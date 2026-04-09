import base64
import hashlib
import hmac
import json
import os
import struct
import time
from dataclasses import dataclass
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import AuthUser
from app.secrets import resolve_secret
from app.security_audit import write_security_event

bearer_scheme = HTTPBearer(auto_error=False)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("utf-8"))


def _jwt_secret() -> str:
    secret = resolve_secret("JWT_SECRET_KEY", settings.jwt_secret_key)
    if not secret:
        raise HTTPException(status_code=503, detail="JWT secret nao configurado.")
    return secret


def create_access_token(payload: dict, expires_minutes: int | None = None) -> tuple[str, int]:
    expires = max(1, int(expires_minutes or settings.access_token_expire_minutes))
    now = int(time.time())
    exp = now + (expires * 60)
    token_payload = dict(payload)
    token_payload.update({"iat": now, "exp": exp})

    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    segments = [
        _b64url_encode(json.dumps(header, separators=(",", ":"), ensure_ascii=True).encode("utf-8")),
        _b64url_encode(json.dumps(token_payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")),
    ]
    signing_input = ".".join(segments).encode("utf-8")
    signature = hmac.new(_jwt_secret().encode("utf-8"), signing_input, hashlib.sha256).digest()
    token = ".".join([segments[0], segments[1], _b64url_encode(signature)])
    return token, expires * 60


def decode_access_token(token: str) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("token malformed")
        signing_input = f"{parts[0]}.{parts[1]}".encode("utf-8")
        given_sig = _b64url_decode(parts[2])
        expected = hmac.new(_jwt_secret().encode("utf-8"), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(given_sig, expected):
            raise ValueError("invalid signature")

        payload = json.loads(_b64url_decode(parts[1]).decode("utf-8"))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("expired")
        return payload
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Token invalido.") from exc


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"pbkdf2_sha256${_b64url_encode(salt)}${_b64url_encode(derived)}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        _, salt_enc, hash_enc = password_hash.split("$", 2)
        salt = _b64url_decode(salt_enc)
        expected = _b64url_decode(hash_enc)
        derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
        return hmac.compare_digest(derived, expected)
    except Exception:
        return False


def _normalize_totp_secret(secret: str) -> bytes:
    value = (secret or "").strip().replace(" ", "").upper()
    padding = "=" * (-len(value) % 8)
    return base64.b32decode(value + padding, casefold=True)


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    if not secret or not code:
        return False
    digits = "".join(ch for ch in code if ch.isdigit())
    if len(digits) < 6:
        return False

    key = _normalize_totp_secret(secret)
    step = 30
    now_counter = int(time.time() // step)

    for offset in range(-window, window + 1):
        counter = now_counter + offset
        msg = struct.pack(">Q", counter)
        digest = hmac.new(key, msg, hashlib.sha1).digest()
        pos = digest[-1] & 0x0F
        binary = ((digest[pos] & 0x7F) << 24) | ((digest[pos + 1] & 0xFF) << 16) | ((digest[pos + 2] & 0xFF) << 8) | (
            digest[pos + 3] & 0xFF
        )
        expected = str(binary % 1_000_000).zfill(6)
        if hmac.compare_digest(expected, digits[-6:]):
            return True
    return False


def create_auth_user(
    db: Session,
    username: str,
    password: str,
    role: str = "viewer",
    is_active: bool = True,
    mfa_enabled: bool = True,
    mfa_secret: str | None = None,
) -> AuthUser:
    existing = db.query(AuthUser).filter(AuthUser.username == username).first()
    if existing:
        raise ValueError("Usuario ja existe.")

    user = AuthUser(
        username=username.strip(),
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
        mfa_enabled=mfa_enabled,
        mfa_secret=mfa_secret,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    write_security_event(
        event_type="auth_user_created",
        actor=username,
        details={"role": role, "mfa_enabled": mfa_enabled},
    )
    return user


def authenticate_user(db: Session, username: str, password: str, mfa_code: str | None = None) -> AuthUser:
    user = db.query(AuthUser).filter(AuthUser.username == username.strip()).first()
    if not user or not user.is_active:
        write_security_event(event_type="auth_login_failed", severity="warning", actor=username, details={"reason": "user_not_found"})
        raise HTTPException(status_code=401, detail="Credenciais invalidas.")

    if not verify_password(password, user.password_hash):
        write_security_event(event_type="auth_login_failed", severity="warning", actor=username, details={"reason": "bad_password"})
        raise HTTPException(status_code=401, detail="Credenciais invalidas.")

    if user.mfa_enabled:
        if not mfa_code or not verify_totp(user.mfa_secret or "", mfa_code):
            write_security_event(event_type="auth_login_failed", severity="warning", actor=username, details={"reason": "mfa_invalid"})
            raise HTTPException(status_code=401, detail="MFA invalido.")

    write_security_event(event_type="auth_login_success", actor=username, details={"role": user.role})
    return user


@dataclass
class Principal:
    user_id: int
    username: str
    role: str
    mfa: bool
    claims: dict


def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Principal:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente.")

    claims = decode_access_token(credentials.credentials)
    user_id = int(claims.get("uid", 0))
    username = str(claims.get("sub") or "")
    role = str(claims.get("role") or "viewer")
    mfa = bool(claims.get("mfa", False))

    user = db.query(AuthUser).filter(AuthUser.id == user_id, AuthUser.is_active.is_(True)).first()
    if not user or user.username != username:
        raise HTTPException(status_code=401, detail="Usuario invalido.")

    return Principal(user_id=user_id, username=username, role=role, mfa=mfa, claims=claims)


def require_roles(*roles: str, mfa_required: bool = False) -> Callable:
    allowed = set(roles)

    def dependency(principal: Principal = Depends(get_current_principal)) -> Principal:
        if allowed and principal.role not in allowed:
            raise HTTPException(status_code=403, detail="Permissao insuficiente.")
        if mfa_required and not principal.mfa:
            raise HTTPException(status_code=403, detail="MFA obrigatorio para este recurso.")
        return principal

    return dependency
