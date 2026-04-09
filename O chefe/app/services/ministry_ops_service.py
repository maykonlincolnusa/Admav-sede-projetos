import json
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    CasadosParaSempreEvent,
    CasadosParaSempreRegistration,
    Contribution,
    CourseEnrollment,
    CoursePayment,
    ChurchCourse,
    Member,
    MissionTask,
    SecretariatRequest,
)
from app.providers.calling import get_calling_provider
from app.providers.messaging import get_messaging_provider
from app.services.ai_service import AIService
from app.services.agent_service import ChurchAgentService
from app.services.casados_service import CasadosParaSempreService
from app.services.department_coordination_service import DepartmentCoordinationService
from app.services.media_content_service import MediaContentService
from app.services.ml_service import CommunityMLService


class MinistryOpsService:
    def __init__(self, db: Session):
        self.db = db

    def _as_json(self, value: dict[str, Any] | None) -> str | None:
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=True)

    def _from_json(self, value: str | None) -> dict[str, Any] | None:
        if not value:
            return None
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None

    def create_secretariat_request(self, payload) -> SecretariatRequest:
        req = SecretariatRequest(
            member_id=payload.member_id,
            category=payload.category,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
        )
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def list_secretariat_requests(self, status: str | None = None) -> list[SecretariatRequest]:
        query = self.db.query(SecretariatRequest).order_by(SecretariatRequest.created_at.desc())
        if status:
            query = query.filter(SecretariatRequest.status == status)
        return query.all()

    def update_secretariat_request(self, request_id: int, payload) -> SecretariatRequest:
        req = self.db.query(SecretariatRequest).filter(SecretariatRequest.id == request_id).first()
        if not req:
            raise ValueError("Solicitacao da secretaria nao encontrada.")
        updates = payload.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(req, key, value)
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def create_course(self, payload) -> ChurchCourse:
        course = ChurchCourse(
            name=payload.name,
            description=payload.description,
            fee_amount=payload.fee_amount,
            is_active=payload.is_active,
        )
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def list_courses(self, active_only: bool = False) -> list[ChurchCourse]:
        query = self.db.query(ChurchCourse).order_by(ChurchCourse.created_at.desc())
        if active_only:
            query = query.filter(ChurchCourse.is_active.is_(True))
        return query.all()

    def create_enrollment(self, payload) -> CourseEnrollment:
        member = self.db.query(Member).filter(Member.id == payload.member_id).first()
        if not member:
            raise ValueError("Membro nao encontrado.")
        course = self.db.query(ChurchCourse).filter(ChurchCourse.id == payload.course_id).first()
        if not course:
            raise ValueError("Curso nao encontrado.")
        existing = (
            self.db.query(CourseEnrollment)
            .filter(CourseEnrollment.member_id == payload.member_id, CourseEnrollment.course_id == payload.course_id)
            .first()
        )
        if existing:
            raise ValueError("Membro ja matriculado neste curso.")
        enroll = CourseEnrollment(course_id=payload.course_id, member_id=payload.member_id)
        self.db.add(enroll)
        self.db.commit()
        self.db.refresh(enroll)
        return enroll

    def list_enrollments(self, course_id: int | None = None) -> list[CourseEnrollment]:
        query = self.db.query(CourseEnrollment).order_by(CourseEnrollment.enrolled_at.desc())
        if course_id:
            query = query.filter(CourseEnrollment.course_id == course_id)
        return query.all()

    def update_enrollment(self, enrollment_id: int, payload) -> CourseEnrollment:
        enrollment = self.db.query(CourseEnrollment).filter(CourseEnrollment.id == enrollment_id).first()
        if not enrollment:
            raise ValueError("Matricula nao encontrada.")
        enrollment.status = payload.status
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def create_course_payment(self, payload) -> CoursePayment:
        enrollment = self.db.query(CourseEnrollment).filter(CourseEnrollment.id == payload.enrollment_id).first()
        if not enrollment:
            raise ValueError("Matricula nao encontrada.")
        payment = CoursePayment(
            enrollment_id=payload.enrollment_id,
            amount=payload.amount,
            currency=payload.currency,
            method=payload.method,
            reference=payload.reference,
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def list_course_payments(self, status: str | None = None) -> list[CoursePayment]:
        query = self.db.query(CoursePayment).order_by(CoursePayment.created_at.desc())
        if status:
            query = query.filter(CoursePayment.status == status)
        return query.all()

    def update_course_payment(self, payment_id: int, payload) -> CoursePayment:
        payment = self.db.query(CoursePayment).filter(CoursePayment.id == payment_id).first()
        if not payment:
            raise ValueError("Pagamento de curso nao encontrado.")
        updates = payload.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(payment, key, value)
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def create_contribution(self, payload) -> Contribution:
        if payload.member_id:
            member = self.db.query(Member).filter(Member.id == payload.member_id).first()
            if not member:
                raise ValueError("Membro nao encontrado.")
        contribution = Contribution(
            member_id=payload.member_id,
            kind=payload.kind,
            amount=payload.amount,
            currency=payload.currency,
            method=payload.method,
            reference=payload.reference,
            note=payload.note,
        )
        self.db.add(contribution)
        self.db.commit()
        self.db.refresh(contribution)
        return contribution

    def list_contributions(self, kind: str | None = None) -> list[Contribution]:
        query = self.db.query(Contribution).order_by(Contribution.contributed_at.desc())
        if kind:
            query = query.filter(Contribution.kind == kind)
        return query.all()

    def contribution_summary(self) -> dict[str, Any]:
        rows = (
            self.db.query(Contribution.kind, func.count(Contribution.id), func.sum(Contribution.amount))
            .group_by(Contribution.kind)
            .all()
        )
        total = self.db.query(func.sum(Contribution.amount)).scalar() or 0
        by_kind: dict[str, dict[str, int]] = {}
        for kind, count, amount in rows:
            by_kind[kind] = {"count": int(count or 0), "amount": int(amount or 0)}
        return {"total_amount": int(total), "by_kind": by_kind}

    def dashboard_metrics(self, lookback_days: int = 30) -> dict[str, Any]:
        days = max(1, min(int(lookback_days), 365))
        since = datetime.utcnow() - timedelta(days=days)

        members_total = self.db.query(func.count(Member.id)).scalar() or 0
        active_members = self.db.query(func.count(Member.id)).filter(Member.is_active.is_(True)).scalar() or 0

        age_rows = self.db.query(Member.age_group, func.count(Member.id)).group_by(Member.age_group).all()
        channel_rows = self.db.query(Member.preferred_channel, func.count(Member.id)).group_by(Member.preferred_channel).all()

        secretariat_rows = (
            self.db.query(SecretariatRequest.status, func.count(SecretariatRequest.id))
            .group_by(SecretariatRequest.status)
            .all()
        )

        courses_total = self.db.query(func.count(ChurchCourse.id)).scalar() or 0
        courses_active = self.db.query(func.count(ChurchCourse.id)).filter(ChurchCourse.is_active.is_(True)).scalar() or 0

        enrollment_rows = (
            self.db.query(CourseEnrollment.status, func.count(CourseEnrollment.id))
            .group_by(CourseEnrollment.status)
            .all()
        )

        payment_rows = (
            self.db.query(CoursePayment.status, func.count(CoursePayment.id), func.sum(CoursePayment.amount))
            .group_by(CoursePayment.status)
            .all()
        )

        contributions_total = self.db.query(func.sum(Contribution.amount)).scalar() or 0
        contributions_window = (
            self.db.query(func.sum(Contribution.amount))
            .filter(Contribution.contributed_at >= since)
            .scalar()
            or 0
        )
        contributions_rows = (
            self.db.query(Contribution.kind, func.count(Contribution.id), func.sum(Contribution.amount))
            .filter(Contribution.contributed_at >= since)
            .group_by(Contribution.kind)
            .all()
        )

        tasks_rows = self.db.query(MissionTask.status, func.count(MissionTask.id)).group_by(MissionTask.status).all()
        tasks_window = (
            self.db.query(func.count(MissionTask.id))
            .filter(MissionTask.created_at >= since)
            .scalar()
            or 0
        )

        ml_summary = CommunityMLService().summary(self.db)
        dept_service = DepartmentCoordinationService(self.db)
        dept_data = dept_service.get_departments()
        dept_items = dept_data.get("departments", [])
        missing_links = 0
        for dept in dept_items:
            links = dept.get("social_links") or {}
            for platform in ("instagram", "facebook", "tiktok", "youtube"):
                if not links.get(platform):
                    missing_links += 1

        payments_by_status = {}
        for status, count, amount in payment_rows:
            payments_by_status[status] = {"count": int(count or 0), "amount": int(amount or 0)}

        casados_rows = (
            self.db.query(CasadosParaSempreRegistration.status, func.count(CasadosParaSempreRegistration.id))
            .group_by(CasadosParaSempreRegistration.status)
            .all()
        )
        casados_event = (
            self.db.query(CasadosParaSempreEvent)
            .filter(CasadosParaSempreEvent.is_active.is_(True))
            .order_by(CasadosParaSempreEvent.event_at.asc())
            .first()
        )

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "lookback_days": days,
            "members": {
                "total": int(members_total),
                "active": int(active_members),
                "by_age_group": {str(k): int(v) for k, v in age_rows},
                "by_channel": {str(k): int(v) for k, v in channel_rows},
            },
            "secretariat": {
                "by_status": {str(k): int(v) for k, v in secretariat_rows},
            },
            "courses": {
                "total": int(courses_total),
                "active": int(courses_active),
                "enrollments_by_status": {str(k): int(v) for k, v in enrollment_rows},
                "payments_by_status": payments_by_status,
            },
            "finance": {
                "contributions_total_amount": int(contributions_total),
                "contributions_amount_last_window": int(contributions_window),
                "contributions_last_window_by_kind": {
                    str(kind): {"count": int(count or 0), "amount": int(amount or 0)}
                    for kind, count, amount in contributions_rows
                },
            },
            "operations": {
                "tasks_created_last_window": int(tasks_window),
                "tasks_by_status": {str(k): int(v) for k, v in tasks_rows},
            },
            "departments": {
                "total": len(dept_items),
                "missing_social_links_total": int(missing_links),
            },
            "casados_para_sempre": {
                "registrations_by_status": {str(k): int(v) for k, v in casados_rows},
                "active_event_at": casados_event.event_at.isoformat() if casados_event else None,
                "active_event_location": casados_event.location if casados_event else None,
            },
            "ml": ml_summary,
        }

    def create_task(self, payload) -> MissionTask:
        task = MissionTask(
            task_type=payload.task_type,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            payload_json=self._as_json(payload.payload),
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list_tasks(self, status: str | None = None) -> list[MissionTask]:
        query = self.db.query(MissionTask).order_by(MissionTask.created_at.desc())
        if status:
            query = query.filter(MissionTask.status == status)
        return query.all()

    def update_task(self, task_id: int, payload) -> MissionTask:
        task = self.db.query(MissionTask).filter(MissionTask.id == task_id).first()
        if not task:
            raise ValueError("Tarefa nao encontrada.")
        updates = payload.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(task, key, value)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def serialize_task(self, task: MissionTask) -> dict[str, Any]:
        return {
            "id": task.id,
            "task_type": task.task_type,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "payload": self._from_json(task.payload_json),
            "result": self._from_json(task.result_json),
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        }

    def _agent(self) -> ChurchAgentService:
        return ChurchAgentService(
            db=self.db,
            ai_service=AIService(),
            messaging_provider=get_messaging_provider(),
            calling_provider=get_calling_provider(),
            ml_service=CommunityMLService(),
        )

    def execute_task(self, task_id: int) -> MissionTask:
        task = self.db.query(MissionTask).filter(MissionTask.id == task_id).first()
        if not task:
            raise ValueError("Tarefa nao encontrada.")

        payload = self._from_json(task.payload_json) or {}
        task.status = "in_progress"
        self.db.add(task)
        self.db.commit()

        result: dict[str, Any]
        try:
            agent = self._agent()
            if task.task_type == "send_weekly_devotional":
                total = agent.send_weekly_devotional(channel=payload.get("channel", "whatsapp"))
                result = {"sent": total}
            elif task.task_type == "send_good_news":
                total = agent.send_good_news(
                    custom_message=payload.get("message"),
                    channel=payload.get("channel"),
                )
                result = {"sent": total}
            elif task.task_type == "train_ml":
                result = CommunityMLService().train(self.db)
            elif task.task_type == "generate_media_plan":
                result = MediaContentService(self.db).generate_plan_from_payload(payload)
            elif task.task_type == "run_department_week_plan":
                result = DepartmentCoordinationService(self.db).execute_week_plan(
                    send_messages=bool(payload.get("send_messages", True)),
                    create_media_tasks=bool(payload.get("create_media_tasks", True)),
                )
            elif task.task_type == "send_casados_reminders":
                result = CasadosParaSempreService(self.db).send_event_reminders()
            else:
                result = {
                    "info": (
                        "Tarefa registrada para operacao manual ou integracao futura. "
                        "Tipos automaticos atuais: send_weekly_devotional, send_good_news, train_ml, "
                        "generate_media_plan, run_department_week_plan, send_casados_reminders."
                    )
                }
            task.status = "done"
            task.result_json = self._as_json(result)
        except Exception as exc:
            task.status = "failed"
            task.result_json = self._as_json({"error": str(exc)})

        task.updated_at = datetime.utcnow()
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
