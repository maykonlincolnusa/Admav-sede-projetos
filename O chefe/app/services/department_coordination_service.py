import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.config import settings
from app.models import InteractionLog, Member, MissionTask, SecretariatRequest
from app.providers.messaging import get_messaging_provider
from app.services.biblical_base import ensure_biblical_base


class DepartmentCoordinationService:
    day_map = {
        "mon": ("segunda", 0),
        "tue": ("terca", 1),
        "wed": ("quarta", 2),
        "thu": ("quinta", 3),
        "fri": ("sexta", 4),
        "sat": ("sabado", 5),
        "sun": ("domingo", 6),
    }
    social_keys = ("instagram", "facebook", "tiktok", "youtube")

    def __init__(self, db: Session):
        self.db = db
        self.path = Path(settings.department_structure_file)

    def _default_structure(self) -> dict[str, Any]:
        return {
            "departments": [
                {
                    "key": "terca_intercessao",
                    "name": "Terca da Intercessao",
                    "audience": "todos",
                    "meeting_day": "tue",
                    "meeting_time": "19:30",
                    "description": "Culto de intercessao e clamor.",
                    "leader_name": None,
                    "leader_phone": None,
                    "social_links": {k: None for k in self.social_keys},
                },
                {
                    "key": "domingo_manha",
                    "name": "Culto de Domingo de Manha",
                    "audience": "todos",
                    "meeting_day": "sun",
                    "meeting_time": "09:00",
                    "description": "Culto de celebracao e palavra.",
                    "leader_name": None,
                    "leader_phone": None,
                    "social_links": {k: None for k in self.social_keys},
                },
                {
                    "key": "level_teen",
                    "name": "Level Teen",
                    "audience": "adolescentes",
                    "meeting_day": "sat",
                    "meeting_time": "18:00",
                    "description": "Ministerio de adolescentes.",
                    "leader_name": None,
                    "leader_phone": None,
                    "social_links": {k: None for k in self.social_keys},
                },
                {
                    "key": "level_up",
                    "name": "Level Up",
                    "audience": "jovens",
                    "meeting_day": "sat",
                    "meeting_time": "20:00",
                    "description": "Ministerio de jovens.",
                    "leader_name": None,
                    "leader_phone": None,
                    "social_links": {k: None for k in self.social_keys},
                },
                {
                    "key": "nucleo_conexao",
                    "name": "Nucleo - Grupos de Conexao",
                    "audience": "todos",
                    "meeting_day": "wed",
                    "meeting_time": "20:00",
                    "description": "Grupos de conexao e comunhao nos lares.",
                    "leader_name": None,
                    "leader_phone": None,
                    "social_links": {k: None for k in self.social_keys},
                },
            ],
            "updated_at": None,
        }

    def _normalize_department(self, dept: dict[str, Any]) -> dict[str, Any]:
        normalized = {
            "key": str(dept.get("key") or "").strip(),
            "name": str(dept.get("name") or "").strip(),
            "audience": str(dept.get("audience") or "todos").strip().lower(),
            "meeting_day": str(dept.get("meeting_day") or "sun").strip().lower(),
            "meeting_time": str(dept.get("meeting_time") or "19:00").strip(),
            "description": dept.get("description"),
            "leader_name": dept.get("leader_name"),
            "leader_phone": dept.get("leader_phone"),
            "social_links": {},
        }
        social = dept.get("social_links") or {}
        for key in self.social_keys:
            normalized["social_links"][key] = social.get(key)
        if normalized["meeting_day"] not in self.day_map:
            normalized["meeting_day"] = "sun"
        if not normalized["audience"]:
            normalized["audience"] = "todos"
        return normalized

    def _load_structure(self) -> dict[str, Any]:
        if not self.path.exists():
            return self._default_structure()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            data = self._default_structure()
        departments = data.get("departments") or []
        normalized = [self._normalize_department(d) for d in departments if (d.get("key") or "").strip()]
        return {
            "departments": normalized,
            "updated_at": data.get("updated_at"),
        }

    def _save_structure(self, data: dict[str, Any]) -> None:
        data["updated_at"] = datetime.utcnow().isoformat()
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=True), encoding="utf-8")

    def get_departments(self) -> dict[str, Any]:
        return self._load_structure()

    def update_department(self, department_key: str, payload) -> dict[str, Any]:
        data = self._load_structure()
        target = None
        for dept in data["departments"]:
            if dept["key"] == department_key:
                target = dept
                break
        if not target:
            raise ValueError("Departamento nao encontrado.")

        updates = payload.model_dump(exclude_unset=True)
        for field in ("name", "audience", "meeting_day", "meeting_time", "description", "leader_name", "leader_phone"):
            if field in updates:
                target[field] = updates[field]

        for social_key in self.social_keys:
            if social_key in updates:
                link = updates[social_key]
                target["social_links"][social_key] = link.strip() if isinstance(link, str) and link.strip() else None

        updated = self._normalize_department(target)
        for idx, dept in enumerate(data["departments"]):
            if dept["key"] == department_key:
                data["departments"][idx] = updated
                break

        self._save_structure(data)
        return updated

    def _next_occurrence(self, weekday_code: str, start_date: date) -> date:
        target_idx = self.day_map.get(weekday_code, ("domingo", 6))[1]
        delta = (target_idx - start_date.weekday()) % 7
        return start_date + timedelta(days=delta)

    def weekly_plan(self, start_date: date | None = None) -> dict[str, Any]:
        start = start_date or date.today()
        data = self._load_structure()
        items = []
        for dept in data["departments"]:
            next_day = self._next_occurrence(dept["meeting_day"], start)
            day_name = self.day_map.get(dept["meeting_day"], ("domingo", 6))[0]
            social_links = dept.get("social_links") or {}
            available = [k for k in self.social_keys if social_links.get(k)]
            missing = [k for k in self.social_keys if not social_links.get(k)]
            items.append(
                {
                    "department_key": dept["key"],
                    "department_name": dept["name"],
                    "audience": dept["audience"],
                    "meeting": {
                        "date": next_day.isoformat(),
                        "day_name": day_name,
                        "time": dept["meeting_time"],
                        "description": dept.get("description"),
                    },
                    "social_links_available": available,
                    "social_links_missing": missing,
                    "actions": [
                        "send_whatsapp_reminder",
                        "create_social_post_tasks",
                        "open_secretariat_request_for_missing_networks",
                    ],
                }
            )
        return {
            "nucleus": settings.nucleus_name,
            "start_date": start.isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "departments": items,
        }

    def _target_members(self, audience: str) -> list[Member]:
        query = self.db.query(Member).filter(Member.is_active.is_(True))
        aud = (audience or "todos").lower()
        if aud in {"adolescentes", "jovens"}:
            query = query.filter(Member.age_group == "youth")
        elif aud == "adultos":
            query = query.filter(Member.age_group == "adult")
        elif aud == "idosos":
            query = query.filter(Member.age_group == "senior")
        return query.all()

    def _message_for_department(self, dept_item: dict[str, Any]) -> str:
        meeting = dept_item["meeting"]
        body = (
            f"Paz do Senhor! Aviso do {dept_item['department_name']} no {settings.nucleus_name}: "
            f"encontro {meeting['day_name']} ({meeting['date']}) as {meeting['time']}. "
            "Esperamos voce para comunhao e crescimento espiritual. Tamo junto em oracao."
        )
        return ensure_biblical_base(body)

    def _upsert_missing_network_request(self, dept_name: str, platform: str) -> None:
        title = f"Cadastrar rede {platform} do departamento {dept_name}"
        existing = (
            self.db.query(SecretariatRequest)
            .filter(
                SecretariatRequest.title == title,
                SecretariatRequest.status.in_(["open", "in_progress"]),
            )
            .first()
        )
        if existing:
            return
        req = SecretariatRequest(
            category="media",
            title=title,
            description=(
                f"Falta o link oficial de {platform} para o departamento {dept_name}. "
                "Atualizar em /departments/{department_key} para liberar automacoes completas."
            ),
            priority="high",
            status="open",
        )
        self.db.add(req)
        self.db.commit()

    def _create_social_task(self, dept_item: dict[str, Any], platform: str) -> bool:
        title = f"Publicar convite - {dept_item['department_name']} ({platform})"
        duplicate = (
            self.db.query(MissionTask)
            .filter(
                MissionTask.task_type == "department_social_post",
                MissionTask.title == title,
                MissionTask.status.in_(["pending", "in_progress"]),
            )
            .first()
        )
        if duplicate:
            return False

        link = None
        for d in self._load_structure()["departments"]:
            if d["key"] == dept_item["department_key"]:
                link = (d.get("social_links") or {}).get(platform)
                break
        task = MissionTask(
            task_type="department_social_post",
            title=title,
            description="Post de convite do departamento conforme calendario semanal.",
            status="pending",
            priority="normal",
            payload_json=json.dumps(
                {
                    "department_key": dept_item["department_key"],
                    "department_name": dept_item["department_name"],
                    "platform": platform,
                    "network_link": link,
                    "meeting": dept_item["meeting"],
                },
                ensure_ascii=True,
            ),
        )
        self.db.add(task)
        self.db.commit()
        return True

    def execute_week_plan(
        self,
        start_date: date | None = None,
        send_messages: bool = True,
        create_media_tasks: bool = True,
    ) -> dict[str, Any]:
        plan = self.weekly_plan(start_date=start_date)
        provider = get_messaging_provider()
        sent = 0
        errors = 0
        tasks_created = 0
        missing_requests_opened = 0

        for dept_item in plan["departments"]:
            if send_messages:
                body = self._message_for_department(dept_item)
                members = self._target_members(dept_item["audience"])
                for member in members:
                    channel = member.preferred_channel if member.preferred_channel in {"sms", "whatsapp"} else "whatsapp"
                    try:
                        sid = provider.send_message(member.phone, body, channel=channel)
                        self.db.add(
                            InteractionLog(
                                member_id=member.id,
                                interaction_type="department_notice",
                                direction="outgoing",
                                content=f"{body} [department:{dept_item['department_key']}] [channel:{channel}] [provider:{sid}]",
                                status="ok",
                            )
                        )
                        self.db.commit()
                        sent += 1
                    except Exception as exc:
                        self.db.add(
                            InteractionLog(
                                member_id=member.id,
                                interaction_type="department_notice",
                                direction="outgoing",
                                content=f"{body} [department:{dept_item['department_key']}]",
                                status=f"error: {exc}",
                            )
                        )
                        self.db.commit()
                        errors += 1

            if create_media_tasks:
                for platform in dept_item["social_links_available"]:
                    created = self._create_social_task(dept_item, platform)
                    if created:
                        tasks_created += 1
                for platform in dept_item["social_links_missing"]:
                    before = (
                        self.db.query(SecretariatRequest)
                        .filter(
                            SecretariatRequest.title == f"Cadastrar rede {platform} do departamento {dept_item['department_name']}",
                            SecretariatRequest.status.in_(["open", "in_progress"]),
                        )
                        .count()
                    )
                    self._upsert_missing_network_request(dept_item["department_name"], platform)
                    after = (
                        self.db.query(SecretariatRequest)
                        .filter(
                            SecretariatRequest.title == f"Cadastrar rede {platform} do departamento {dept_item['department_name']}",
                            SecretariatRequest.status.in_(["open", "in_progress"]),
                        )
                        .count()
                    )
                    if after > before:
                        missing_requests_opened += 1

        return {
            "plan_generated_for": plan["start_date"],
            "departments": len(plan["departments"]),
            "messages_sent": sent,
            "message_errors": errors,
            "media_tasks_created": tasks_created,
            "missing_network_requests_opened": missing_requests_opened,
        }
