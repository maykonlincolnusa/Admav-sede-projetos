from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import ChurchAgendaEvent


class AgendaService:
    def __init__(self, db: Session):
        self.db = db

    def list_events(
        self,
        active_only: bool = True,
        category: str | None = None,
        limit: int = 50,
    ) -> list[ChurchAgendaEvent]:
        query = self.db.query(ChurchAgendaEvent).order_by(ChurchAgendaEvent.starts_at.asc())
        if active_only:
            query = query.filter(ChurchAgendaEvent.is_active.is_(True))
        if category:
            query = query.filter(ChurchAgendaEvent.category == category)
        return query.limit(max(1, min(int(limit), 200))).all()

    def upcoming(self, days: int = 30, limit: int = 10) -> list[ChurchAgendaEvent]:
        window_days = max(1, min(int(days), 365))
        now = datetime.utcnow()
        until = now + timedelta(days=window_days)
        return (
            self.db.query(ChurchAgendaEvent)
            .filter(
                ChurchAgendaEvent.is_active.is_(True),
                ChurchAgendaEvent.starts_at >= now,
                ChurchAgendaEvent.starts_at <= until,
            )
            .order_by(ChurchAgendaEvent.starts_at.asc())
            .limit(max(1, min(int(limit), 50)))
            .all()
        )

    def create_event(self, payload) -> ChurchAgendaEvent:
        event = ChurchAgendaEvent(
            title=payload.title,
            category=payload.category,
            starts_at=payload.starts_at,
            location=payload.location,
            department_key=payload.department_key,
            notes=payload.notes,
            is_active=payload.is_active,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def update_event(self, event_id: int, payload) -> ChurchAgendaEvent:
        event = self.db.query(ChurchAgendaEvent).filter(ChurchAgendaEvent.id == event_id).first()
        if not event:
            raise ValueError("Evento da agenda nao encontrado.")

        updates = payload.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(event, key, value)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def disable_event(self, event_id: int) -> ChurchAgendaEvent:
        event = self.db.query(ChurchAgendaEvent).filter(ChurchAgendaEvent.id == event_id).first()
        if not event:
            raise ValueError("Evento da agenda nao encontrado.")
        event.is_active = False
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
