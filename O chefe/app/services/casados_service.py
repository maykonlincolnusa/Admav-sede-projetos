from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    CasadosParaSempreEvent,
    CasadosParaSempreRegistration,
    InteractionLog,
    Member,
)
from app.providers.messaging import MessagingProvider, get_messaging_provider
from app.services.biblical_base import ensure_biblical_base


class CasadosParaSempreService:
    intent_keywords = (
        "casados para sempre",
        "inscrever no casados",
        "inscricao casados",
        "inscricao no casados",
    )
    yes_keywords = {"sim", "s", "confirmo", "ok", "confirmar"}
    no_keywords = {"nao", "cancelar", "cancela"}

    def __init__(self, db: Session, messaging_provider: MessagingProvider | None = None):
        self.db = db
        self.messaging_provider = messaging_provider or get_messaging_provider()

    def get_active_event(self) -> CasadosParaSempreEvent | None:
        return (
            self.db.query(CasadosParaSempreEvent)
            .filter(CasadosParaSempreEvent.is_active.is_(True))
            .order_by(CasadosParaSempreEvent.event_at.asc())
            .first()
        )

    def upsert_event(self, payload) -> CasadosParaSempreEvent:
        if payload.is_active:
            self.db.query(CasadosParaSempreEvent).update({CasadosParaSempreEvent.is_active: False})

        event = CasadosParaSempreEvent(
            title=payload.title,
            event_at=payload.event_at,
            location=payload.location,
            notes=payload.notes,
            is_active=payload.is_active,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def update_event(self, event_id: int, payload) -> CasadosParaSempreEvent:
        event = self.db.query(CasadosParaSempreEvent).filter(CasadosParaSempreEvent.id == event_id).first()
        if not event:
            raise ValueError("Evento Casados para Sempre nao encontrado.")

        updates = payload.model_dump(exclude_unset=True)
        if updates.get("is_active") is True:
            self.db.query(CasadosParaSempreEvent).update({CasadosParaSempreEvent.is_active: False})
        for key, value in updates.items():
            setattr(event, key, value)

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_registrations(self, status: str | None = None) -> list[CasadosParaSempreRegistration]:
        query = self.db.query(CasadosParaSempreRegistration).order_by(CasadosParaSempreRegistration.created_at.desc())
        if status:
            query = query.filter(CasadosParaSempreRegistration.status == status)
        return query.all()

    def _normalize(self, text: str) -> str:
        return (text or "").strip().lower()

    def _is_intent(self, text: str) -> bool:
        value = self._normalize(text)
        return any(keyword in value for keyword in self.intent_keywords)

    def _event_block(self) -> str:
        event = self.get_active_event()
        if not event:
            return (
                "Ainda vamos confirmar data/local oficialmente. "
                "Assim que a secretaria fechar, te avisamos aqui."
            )
        return (
            f"Evento: {event.title}\n"
            f"Data/Hora: {event.event_at.strftime('%d/%m/%Y %H:%M')}\n"
            f"Local: {event.location}\n"
            f"Obs: {event.notes or 'Levar caderno e coracao aberto para aprender.'}"
        )

    def _active_registration(self, phone: str) -> CasadosParaSempreRegistration | None:
        return (
            self.db.query(CasadosParaSempreRegistration)
            .filter(
                CasadosParaSempreRegistration.phone == phone,
                CasadosParaSempreRegistration.status == "collecting",
            )
            .order_by(CasadosParaSempreRegistration.created_at.desc())
            .first()
        )

    def _create_registration(self, phone: str, member: Member | None) -> CasadosParaSempreRegistration:
        registration = CasadosParaSempreRegistration(
            member_id=member.id if member else None,
            phone=phone,
            status="collecting",
            current_step="full_name",
        )
        self.db.add(registration)
        self.db.commit()
        self.db.refresh(registration)
        return registration

    def _confirm_text(self, reg: CasadosParaSempreRegistration) -> str:
        return (
            "Perfeito! Confere seus dados:\n"
            f"- Nome: {reg.full_name}\n"
            f"- Conjuge: {reg.spouse_name}\n"
            f"- Cidade: {reg.city}\n"
            f"- Tempo de casados: {reg.years_married}\n\n"
            "Responda *SIM* para confirmar a inscricao ou *NAO* para cancelar."
        )

    def handle_whatsapp_registration(
        self,
        phone: str,
        message: str,
        member: Member | None,
    ) -> tuple[bool, str]:
        text = (message or "").strip()
        normalized = self._normalize(text)
        registration = self._active_registration(phone)
        intent = self._is_intent(text)

        if not registration and not intent:
            return False, ""

        if not registration and intent:
            self._create_registration(phone=phone, member=member)
            return (
                True,
                (
                    "Que alegria receber seu interesse no *Casados para Sempre*! "
                    "Vamos fazer sua inscricao agora. Primeiro, me diga seu *nome completo*."
                ),
            )

        if registration is None:
            return False, ""

        if normalized in {"cancelar", "cancelar inscricao", "parar"}:
            registration.status = "cancelled"
            registration.current_step = "cancelled"
            self.db.add(registration)
            self.db.commit()
            return True, "Inscricao cancelada com sucesso. Se quiser retomar, me chame com: casados para sempre."

        if registration.current_step == "full_name":
            if len(text) < 3:
                return True, "Preciso do seu nome completo para continuar a inscricao."
            registration.full_name = text
            registration.current_step = "spouse_name"
            self.db.add(registration)
            self.db.commit()
            return True, "Perfeito. Agora me informe o *nome do seu conjuge*."

        if registration.current_step == "spouse_name":
            if len(text) < 3:
                return True, "Me passe o nome do conjuge com pelo menos 3 caracteres."
            registration.spouse_name = text
            registration.current_step = "city"
            self.db.add(registration)
            self.db.commit()
            return True, "Obrigado. Qual *cidade/bairro* voces moram?"

        if registration.current_step == "city":
            if len(text) < 2:
                return True, "Me diga sua cidade/bairro para concluir o cadastro."
            registration.city = text
            registration.current_step = "years_married"
            self.db.add(registration)
            self.db.commit()
            return True, "Top! Agora diga o *tempo de casados* (ex.: 2 anos, 10 anos, recem-casados)."

        if registration.current_step == "years_married":
            registration.years_married = text
            registration.current_step = "confirm"
            self.db.add(registration)
            self.db.commit()
            return True, self._confirm_text(registration)

        if registration.current_step == "confirm":
            if normalized in self.yes_keywords:
                registration.status = "confirmed"
                registration.current_step = "done"
                self.db.add(registration)
                self.db.commit()
                return (
                    True,
                    (
                        "Inscricao confirmada com sucesso no *Casados para Sempre*!\n\n"
                        f"{self._event_block()}\n\n"
                        "Vamos te lembrar perto da data. Deus abencoe seu lar!"
                    ),
                )
            if normalized in self.no_keywords:
                registration.status = "cancelled"
                registration.current_step = "cancelled"
                self.db.add(registration)
                self.db.commit()
                return True, "Tudo bem, inscricao cancelada. Se quiser fazer de novo, me chame."
            return True, "Para finalizar, responda *SIM* para confirmar ou *NAO* para cancelar."

        return True, "Estamos concluindo seu cadastro. Se precisar, responda: casados para sempre."

    def send_event_reminders(self) -> dict[str, int]:
        event = self.get_active_event()
        if not event:
            return {"sent": 0, "errors": 0}

        now = datetime.utcnow()
        hours_to_event = (event.event_at - now).total_seconds() / 3600
        if hours_to_event <= 0:
            return {"sent": 0, "errors": 0}

        registrations = (
            self.db.query(CasadosParaSempreRegistration)
            .filter(CasadosParaSempreRegistration.status == "confirmed")
            .all()
        )

        sent = 0
        errors = 0
        for reg in registrations:
            should_send = False
            reminder_type = ""
            if 24 < hours_to_event <= 168 and not reg.reminder_7d_sent:
                should_send = True
                reminder_type = "7d"
            elif 0 < hours_to_event <= 24 and not reg.reminder_1d_sent:
                should_send = True
                reminder_type = "1d"

            if not should_send:
                continue

            member = self.db.query(Member).filter(Member.id == reg.member_id).first() if reg.member_id else None
            channel = member.preferred_channel if member and member.preferred_channel in {"sms", "whatsapp"} else "whatsapp"
            body = (
                f"Lembrete do *{event.title}*!\n"
                f"Data/Hora: {event.event_at.strftime('%d/%m/%Y %H:%M')}\n"
                f"Local: {event.location}\n"
                "Estamos esperando voces. Vai ser bencao para o casamento!"
            )
            body = ensure_biblical_base(body)
            try:
                sid = self.messaging_provider.send_message(reg.phone, body, channel=channel)
                if reminder_type == "7d":
                    reg.reminder_7d_sent = True
                if reminder_type == "1d":
                    reg.reminder_1d_sent = True
                self.db.add(reg)
                self.db.add(
                    InteractionLog(
                        member_id=reg.member_id,
                        interaction_type="casados_reminder",
                        direction="outgoing",
                        content=f"{body} [channel:{channel}] [provider:{sid}]",
                        status="ok",
                    )
                )
                self.db.commit()
                sent += 1
            except Exception as exc:
                self.db.add(
                    InteractionLog(
                        member_id=reg.member_id,
                        interaction_type="casados_reminder",
                        direction="outgoing",
                        content=body,
                        status=f"error: {exc}",
                    )
                )
                self.db.commit()
                errors += 1
        return {"sent": sent, "errors": errors}
