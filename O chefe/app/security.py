import hashlib
import hmac
import secrets
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.secrets import resolve_secret
from app.security_audit import write_security_event


def _parse_csv(value: str | None) -> list[str]:
    raw = (value or "").strip()
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _path_matches(path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if pattern.endswith("*"):
            if path.startswith(pattern[:-1]):
                return True
        elif path == pattern:
            return True
    return False


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none';")
        if request.url.scheme == "https":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.enabled = bool(settings.rate_limit_enabled)
        self.limit = max(1, int(settings.rate_limit_requests))
        self.window_seconds = max(1, int(settings.rate_limit_window_seconds))
        self.exempt_paths = _parse_csv(settings.security_exempt_paths)
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)

        path = request.url.path
        if _path_matches(path, self.exempt_paths):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"{client_ip}:{path}"
        now = time.time()

        with self._lock:
            queue = self._hits[key]
            cutoff = now - self.window_seconds
            while queue and queue[0] < cutoff:
                queue.popleft()
            if len(queue) >= self.limit:
                write_security_event(
                    event_type="rate_limit_exceeded",
                    severity="warning",
                    ip_address=client_ip,
                    path=path,
                    details={"window_seconds": self.window_seconds, "limit": self.limit},
                )
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Muitas requisicoes. Tente novamente em instantes."},
                )
            queue.append(now)

        return await call_next(request)


class ApiKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.require_api_key = bool(settings.require_api_key)
        self.api_key_header = (settings.api_key_header_name or "X-API-Key").strip()
        self.exempt_paths = _parse_csv(settings.security_exempt_paths)

    async def dispatch(self, request: Request, call_next):
        if not self.require_api_key:
            return await call_next(request)

        path = request.url.path
        if _path_matches(path, self.exempt_paths):
            return await call_next(request)

        expected_api_key = (resolve_secret("API_KEY", settings.api_key) or "").strip()
        if not expected_api_key:
            return JSONResponse(
                status_code=503,
                content={"detail": "Servidor sem API key configurada."},
            )

        incoming = request.headers.get(self.api_key_header)
        if not incoming or not secrets.compare_digest(incoming, expected_api_key):
            write_security_event(
                event_type="api_key_invalid",
                severity="warning",
                ip_address=request.client.host if request.client else None,
                path=path,
            )
            return JSONResponse(status_code=401, content={"detail": "Nao autorizado."})

        return await call_next(request)


async def verify_webhook_signature(request: Request) -> None:
    if not settings.require_webhook_signature:
        return

    secret = (resolve_secret("WEBHOOK_SECRET", settings.webhook_secret) or "").strip()
    if not secret:
        raise HTTPException(status_code=503, detail="Webhook secret nao configurado.")

    signature_header = (settings.webhook_signature_header or "X-Webhook-Signature").strip()
    timestamp_header = (settings.webhook_timestamp_header or "X-Webhook-Timestamp").strip()

    signature = (request.headers.get(signature_header) or "").strip()
    timestamp = (request.headers.get(timestamp_header) or "").strip()

    if not signature or not timestamp:
        write_security_event(
            event_type="webhook_signature_missing",
            severity="warning",
            ip_address=request.client.host if request.client else None,
            path=request.url.path,
        )
        raise HTTPException(status_code=401, detail="Assinatura do webhook ausente.")

    if signature.lower().startswith("sha256="):
        signature = signature.split("=", 1)[1].strip()

    try:
        ts = int(timestamp)
    except ValueError as exc:
        write_security_event(
            event_type="webhook_timestamp_invalid",
            severity="warning",
            ip_address=request.client.host if request.client else None,
            path=request.url.path,
        )
        raise HTTPException(status_code=401, detail="Timestamp de webhook invalido.") from exc

    now = int(time.time())
    max_age = max(1, int(settings.webhook_max_age_seconds))
    if abs(now - ts) > max_age:
        write_security_event(
            event_type="webhook_expired",
            severity="warning",
            ip_address=request.client.host if request.client else None,
            path=request.url.path,
            details={"max_age": max_age, "ts": ts},
        )
        raise HTTPException(status_code=401, detail="Webhook expirado.")

    body = await request.body()
    payload = f"{timestamp}.{body.decode('utf-8')}".encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    if not secrets.compare_digest(signature, expected):
        write_security_event(
            event_type="webhook_signature_invalid",
            severity="warning",
            ip_address=request.client.host if request.client else None,
            path=request.url.path,
        )
        raise HTTPException(status_code=401, detail="Assinatura do webhook invalida.")
