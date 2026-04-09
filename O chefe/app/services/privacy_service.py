from datetime import datetime

from sqlalchemy.orm import Session

from app.models import InteractionLog, Member, PrivacyRequestLog


class PrivacyService:
    def __init__(self, db: Session):
        self.db = db

    def grant_consent(self, member_id: int, basis: str, requested_by: str | None = None, note: str | None = None) -> Member:
        member = self.db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise ValueError("Membro nao encontrado.")

        member.consent_given = True
        member.consent_basis = basis
        member.consent_at = datetime.utcnow()
        self.db.add(member)
        self.db.add(
            PrivacyRequestLog(
                member_id=member.id,
                action="consent",
                basis=basis,
                requested_by=requested_by,
                note=note,
            )
        )
        self.db.commit()
        self.db.refresh(member)
        return member

    def forget_member(self, member_id: int, reason: str, requested_by: str | None = None) -> Member:
        member = self.db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise ValueError("Membro nao encontrado.")

        member.name = f"ANONYMIZED-{member.id}"
        member.email = None
        member.phone = f"anon-{member.id}"
        member.is_active = False
        member.consent_given = False
        member.deleted_at = datetime.utcnow()
        member.pseudonymized_at = datetime.utcnow()
        self.db.add(member)

        logs = self.db.query(InteractionLog).filter(InteractionLog.member_id == member.id).all()
        for item in logs:
            item.content = "[ANONYMIZED]"
            self.db.add(item)

        self.db.add(
            PrivacyRequestLog(
                member_id=member.id,
                action="forget",
                basis="direito_ao_esquecimento",
                requested_by=requested_by,
                note=reason,
            )
        )

        self.db.commit()
        self.db.refresh(member)
        return member

    def export_member_summary(self, member_id: int) -> dict:
        member = self.db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise ValueError("Membro nao encontrado.")

        interactions = (
            self.db.query(InteractionLog)
            .filter(InteractionLog.member_id == member.id)
            .order_by(InteractionLog.created_at.desc())
            .limit(200)
            .all()
        )
        privacy_logs = (
            self.db.query(PrivacyRequestLog)
            .filter(PrivacyRequestLog.member_id == member.id)
            .order_by(PrivacyRequestLog.created_at.desc())
            .all()
        )
        return {
            "member": {
                "id": member.id,
                "name": member.name,
                "phone": member.phone,
                "email": member.email,
                "consent_given": member.consent_given,
                "consent_basis": member.consent_basis,
                "consent_at": member.consent_at.isoformat() if member.consent_at else None,
                "deleted_at": member.deleted_at.isoformat() if member.deleted_at else None,
            },
            "interactions_count": len(interactions),
            "privacy_history": [
                {
                    "action": item.action,
                    "basis": item.basis,
                    "requested_by": item.requested_by,
                    "note": item.note,
                    "created_at": item.created_at.isoformat(),
                }
                for item in privacy_logs
            ],
        }
