import json
from datetime import datetime

from app.config import settings
from app.db import SessionLocal
from app.models import SecurityAuditEvent


def write_security_event(
    event_type: str,
    severity: str = "info",
    actor: str | None = None,
    ip_address: str | None = None,
    path: str | None = None,
    details: dict | None = None,
) -> None:
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "severity": severity,
        "event_type": event_type,
        "actor": actor,
        "ip": ip_address,
        "path": path,
        "details": details or {},
    }

    db = SessionLocal()
    try:
        db.add(
            SecurityAuditEvent(
                severity=severity,
                event_type=event_type,
                actor=actor,
                ip_address=ip_address,
                path=path,
                details_json=json.dumps(details or {}, ensure_ascii=True),
            )
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

    # fallback line for SIEM/file shippers
    if settings.security_audit_stdout:
        print(f"[SECURITY] {json.dumps(entry, ensure_ascii=True)}")
