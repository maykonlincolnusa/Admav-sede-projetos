import json
import re
import secrets
import unicodedata
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.models import ChurchCourse, ConversationSession, InteractionLog, Member, SecretariatRequest
from app.providers.calling import CallingProvider
from app.providers.messaging import MessagingProvider
from app.schemas import AgendaEventCreate, CasadosEventCreate, DepartmentUpdate, SocialLinksUpdate
from app.services.agenda_service import AgendaService
from app.services.ai_service import AIService
from app.services.ai_guard_service import guard
from app.services.biblical_base import ensure_biblical_base
from app.services.casados_service import CasadosParaSempreService
from app.services.department_coordination_service import DepartmentCoordinationService
from app.services.ml_service import CommunityMLService
from app.services.social_links_service import SocialLinksService
from app.security_audit import write_security_event


class ChurchAgentService:
    day_label = {
        "mon": "Segunda",
        "tue": "Terca",
        "wed": "Quarta",
        "thu": "Quinta",
        "fri": "Sexta",
        "sat": "Sabado",
        "sun": "Domingo",
    }
    day_order = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    female_names = {
        "ana",
        "beatriz",
        "bruna",
        "carla",
        "carolina",
        "camila",
        "daniela",
        "elaine",
        "fernanda",
        "gabriela",
        "helena",
        "isabela",
        "isabella",
        "julia",
        "juliana",
        "laura",
        "lara",
        "larissa",
        "leticia",
        "lucia",
        "luciana",
        "luana",
        "maria",
        "mariana",
        "patricia",
        "paula",
        "priscila",
        "rafaela",
        "raquel",
        "renata",
        "sara",
        "sarah",
        "simone",
        "thais",
        "valeria",
        "vitoria",
        "yasmin",
    }
    male_names = {
        "alex",
        "alexandre",
        "andre",
        "antonio",
        "bruno",
        "caio",
        "carlos",
        "daniel",
        "davi",
        "eduardo",
        "felipe",
        "filipe",
        "gabriel",
        "gustavo",
        "henrique",
        "igor",
        "joao",
        "jose",
        "julio",
        "leonardo",
        "lucas",
        "luis",
        "luiz",
        "marcos",
        "mateus",
        "murilo",
        "paulo",
        "pedro",
        "rafael",
        "ricardo",
        "rodrigo",
        "sergio",
        "thiago",
        "tiago",
        "vitor",
        "victor",
        "vinicius",
    }
    male_end_a_names = {"luca", "juca", "noa"}

    def __init__(
        self,
        db: Session,
        ai_service: AIService,
        messaging_provider: MessagingProvider,
        calling_provider: CallingProvider,
        ml_service: CommunityMLService | None = None,
    ):
        self.db = db
        self.ai_service = ai_service
        self.messaging_provider = messaging_provider
        self.calling_provider = calling_provider
        self.ml_service = ml_service or CommunityMLService()

    def create_member(
        self, name: str, phone: str, email: str | None, preferred_channel: str, age_group: str = "adult"
    ) -> Member:
        existing = self.db.query(Member).filter(Member.phone == phone).first()
        if existing:
            raise ValueError("Ja existe membro com este telefone.")
        member = Member(
            name=name,
            phone=phone,
            email=email,
            preferred_channel=preferred_channel,
            age_group=age_group,
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def _normalize_channel(self, channel: str | None, member: Member | None = None) -> str:
        candidate = channel or (member.preferred_channel if member else None) or "whatsapp"
        return candidate if candidate in {"sms", "whatsapp"} else "whatsapp"

    def update_member_age_group(self, member_id: int, age_group: str) -> Member:
        member = self.db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise ValueError("Membro nao encontrado.")
        member.age_group = age_group
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def update_member_channel(self, member_id: int, preferred_channel: str) -> Member:
        member = self.db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise ValueError("Membro nao encontrado.")
        member.preferred_channel = self._normalize_channel(preferred_channel, member)
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def list_members(self) -> list[Member]:
        return self.db.query(Member).order_by(Member.name.asc()).all()

    def _normalize_text(self, text: str) -> str:
        return (text or "").strip().lower()

    def _strip_accents(self, text: str) -> str:
        if not text:
            return ""
        normalized = unicodedata.normalize("NFD", text)
        return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")

    def _first_name(self, name: str | None) -> str | None:
        if not name:
            return None
        parts = str(name).strip().split()
        if not parts:
            return None
        return parts[0]

    def _infer_address_from_name(self, name: str | None) -> str | None:
        first = self._first_name(name)
        if not first:
            return None
        normalized = self._strip_accents(first).lower()
        if normalized in self.male_names:
            return "chefe"
        if normalized in self.female_names:
            return "chefa"
        if normalized.endswith("a") and normalized not in self.male_end_a_names:
            return "chefa"
        if normalized.endswith("o"):
            return "chefe"
        return None

    def _extract_address_preference(self, message: str) -> str | None:
        if not message:
            return None
        normalized = self._normalize_text(message)
        if re.search(r"\b(me chama|me chame|pode me chamar|me trate|me trata|pode me tratar)\b.*\bchefa\b", normalized):
            return "chefa"
        if re.search(r"\b(me chama|me chame|pode me chamar|me trate|me trata|pode me tratar)\b.*\bchefe\b", normalized):
            return "chefe"
        if re.search(r"\bsou\s+chefa\b", normalized):
            return "chefa"
        if re.search(r"\bsou\s+chefe\b", normalized):
            return "chefe"
        if re.search(r"\b(sou|sou uma|sou do sexo|sou mulher|sou menina|sou moca|feminino)\b", normalized):
            return "chefa"
        if re.search(r"\b(sou|sou um|sou do sexo|sou homem|sou menino|sou rapaz|masculino)\b", normalized):
            return "chefe"
        return None

    def _capture_address_preference(self, session: ConversationSession, message: str) -> None:
        pref = self._extract_address_preference(message)
        if not pref:
            return
        self._update_session(session, extra_state={"address_term": pref, "address_source": "explicit"})

    def _address_term_for(self, session: ConversationSession | None, member: Member | None) -> str:
        if session:
            term = self._session_state(session).get("address_term")
            if term in {"chefe", "chefa"}:
                return term
        inferred = self._infer_address_from_name(member.name if member else None)
        return inferred or "chefe"

    def _address_prefix(self, session: ConversationSession | None, member: Member | None) -> str:
        term = self._address_term_for(session, member)
        return f"{term.capitalize()},"

    def _ensure_address_in_text(self, text: str, address_term: str) -> str:
        if not text:
            return text
        if re.search(r"\bchefe\b|\bchefa\b", text, flags=re.IGNORECASE):
            return text
        return f"{address_term.capitalize()}, {text}"

    def _greeting(self, session: ConversationSession | None, member: Member | None) -> str:
        term = self._address_term_for(session, member)
        name = self._first_name(member.name) if member else None
        if name:
            return f"Paz do Senhor, {term} {name}!"
        return f"Paz do Senhor, {term}!"

    def _normalize_phone(self, phone: str) -> str:
        digits = re.sub(r"\D+", "", phone or "")
        if phone and phone.strip().startswith("+"):
            return f"+{digits}"
        return digits

    def _admin_numbers(self) -> set[str]:
        raw = (settings.admin_whatsapp_numbers or "").strip()
        if not raw:
            return set()
        values = [piece.strip() for piece in raw.replace(";", ",").split(",")]
        return {self._normalize_phone(item) for item in values if item}

    def _is_admin_phone(self, phone: str) -> bool:
        allowed = self._admin_numbers()
        if not allowed:
            return False
        return self._normalize_phone(phone) in allowed

    def _admin_password(self) -> str:
        return (settings.admin_command_password or "").strip()

    def _admin_lock_message(self, session: ConversationSession) -> str | None:
        state = self._session_state(session)
        locked_until_text = str(state.get("admin_locked_until") or "").strip()
        if not locked_until_text:
            return None
        try:
            locked_until = datetime.fromisoformat(locked_until_text)
        except Exception:
            self._update_session(session, extra_state={"admin_locked_until": "", "admin_failed_attempts": 0})
            return None

        now = datetime.utcnow()
        if locked_until <= now:
            self._update_session(session, extra_state={"admin_locked_until": "", "admin_failed_attempts": 0})
            return None

        return f"Acesso admin temporariamente bloqueado ate {locked_until.strftime('%d/%m/%Y %H:%M')} UTC."

    def _register_admin_failure(self, session: ConversationSession) -> str:
        max_attempts = max(1, int(settings.admin_password_max_attempts))
        lock_minutes = max(1, int(settings.admin_password_lock_minutes))
        state = self._session_state(session)
        current = int(state.get("admin_failed_attempts") or 0) + 1

        if current >= max_attempts:
            locked_until = datetime.utcnow() + timedelta(minutes=lock_minutes)
            self._update_session(
                session,
                extra_state={
                    "admin_failed_attempts": 0,
                    "admin_locked_until": locked_until.isoformat(),
                },
            )
            return f"Muitas tentativas invalidas. Admin bloqueado por {lock_minutes} minutos."

        self._update_session(session, extra_state={"admin_failed_attempts": current})
        remaining = max_attempts - current
        return f"Senha admin invalida. Tentativas restantes: {remaining}."

    def _is_admin_authenticated(self, session: ConversationSession) -> bool:
        state = self._session_state(session)
        until_text = str(state.get("admin_auth_until") or "").strip()
        if not until_text:
            return False
        try:
            until = datetime.fromisoformat(until_text)
            return until > datetime.utcnow()
        except Exception:
            return False

    def _set_admin_authenticated(self, session: ConversationSession) -> ConversationSession:
        ttl = max(1, int(settings.admin_session_ttl_minutes))
        until = datetime.utcnow() + timedelta(minutes=ttl)
        return self._update_session(
            session=session,
            step="await_menu_choice",
            extra_state={
                "admin_auth_until": until.isoformat(),
                "admin_failed_attempts": 0,
                "admin_locked_until": "",
            },
        )

    def _clear_admin_authenticated(self, session: ConversationSession) -> ConversationSession:
        return self._update_session(
            session=session,
            step="await_menu_choice",
            extra_state={"admin_auth_until": "", "admin_failed_attempts": 0, "admin_locked_until": ""},
        )

    def _parse_datetime(self, text: str) -> datetime | None:
        value = (text or "").strip()
        formats = ("%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%dT%H:%M")
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None

    def _admin_help_text(self) -> str:
        prefix = settings.admin_command_prefix.strip() or "admin"
        return (
            "Comandos admin (WhatsApp):\n"
            f"- {prefix} senha <sua_senha>\n"
            f"- {prefix} logout\n"
            f"- {prefix} help\n"
            f"- {prefix} agenda add|weekly|2026-03-10 19:30|Culto Especial|Sede|Noite de oracao\n"
            f"- {prefix} agenda add|monthly|2026-03-30 20:00|Santa Ceia|Sede|Ultima segunda do mes\n"
            f"- {prefix} agenda add|quarterly|2026-06-15 19:00|Conferencia Trimestral|Sede|Tema do trimestre\n"
            f"- {prefix} agenda list\n"
            f"- {prefix} agenda off|12\n"
            f"- {prefix} dept set|level_up|sat|20:00\n"
            f"- {prefix} casados set|2026-04-20 19:30|ADMAV Sede|Turma de abril\n"
            f"- {prefix} social set|instagram|https://...\n"
            f"- {prefix} finance set|pix|06.251.957/0001-97|cnpj|ADMAV Sede|Dizimo e oferta\n"
        )

    def _handle_admin_command(self, phone: str, message: str, session: ConversationSession) -> str | None:
        normalized = self._normalize_text(message)
        prefix = (settings.admin_command_prefix or "admin").strip().lower()

        is_admin_intent = normalized.startswith(f"{prefix} ") or normalized == prefix or normalized in {
            "admin",
            "ajuda admin",
            "help admin",
        }
        if not is_admin_intent:
            return None

        if not self._is_admin_phone(phone):
            return "Esse comando e restrito a administracao da igreja."

        content = message.strip()
        if content.lower().startswith(prefix):
            content = content[len(prefix) :].strip()
        if not content:
            return "Comando admin bloqueado. Envie: admin senha <sua_senha>"

        lowered = content.lower()
        lock_message = self._admin_lock_message(session)
        if lock_message:
            return lock_message

        if lowered.startswith("senha "):
            given_password = content[6:].strip()
            expected_password = self._admin_password()
            if not expected_password:
                return "Senha admin nao configurada no sistema."
            if not secrets.compare_digest(given_password, expected_password):
                return self._register_admin_failure(session)
            self._set_admin_authenticated(session)
            ttl = max(1, int(settings.admin_session_ttl_minutes))
            return f"Acesso admin liberado por {ttl} minutos. Envie: {prefix} help"

        if lowered in {"logout", "sair", "exit"}:
            self._clear_admin_authenticated(session)
            return "Sessao admin encerrada com sucesso."

        if not self._is_admin_authenticated(session):
            return "Comando admin bloqueado. Envie: admin senha <sua_senha>"

        if lowered in {"help", "ajuda"} or normalized in {"admin", "ajuda admin", "help admin"}:
            return self._admin_help_text()

        if lowered.startswith("agenda add|"):
            parts = [p.strip() for p in content[11:].split("|")]
            if len(parts) < 4:
                return "Formato: admin agenda add|categoria|YYYY-MM-DD HH:MM|titulo|local(opcional)|notas(opcional)"
            category = parts[0].lower()
            starts_at = self._parse_datetime(parts[1])
            title = parts[2]
            location = parts[3] if len(parts) >= 4 else None
            notes = parts[4] if len(parts) >= 5 else None

            if category not in {"weekly", "monthly", "quarterly", "special"}:
                return "Categoria invalida. Use: weekly, monthly, quarterly ou special."
            if starts_at is None:
                return "Data invalida. Use YYYY-MM-DD HH:MM (ex.: 2026-03-10 19:30)."
            payload = AgendaEventCreate(
                title=title,
                category=category,
                starts_at=starts_at,
                location=location,
                notes=notes,
                is_active=True,
            )
            event = AgendaService(self.db).create_event(payload)
            summary = (
                f"Agenda atualizada: {event.title} em {event.starts_at.strftime('%d/%m/%Y %H:%M')} ({event.category})."
            )
            result = self._broadcast_admin_update(summary)
            return f"{summary} Notificacao enviada para {result['sent']} membro(s)."

        if lowered == "agenda list":
            events = AgendaService(self.db).list_events(active_only=True, category=None, limit=12)
            if not events:
                return "Agenda ativa vazia no momento."
            lines = ["Agenda ativa:"]
            for event in events:
                lines.append(
                    f"- #{event.id} [{event.category}] {event.starts_at.strftime('%d/%m/%Y %H:%M')} - {event.title}"
                )
            return "\n".join(lines)

        if lowered.startswith("agenda off|"):
            event_id_text = content[11:].strip()
            if not event_id_text.isdigit():
                return "Formato: admin agenda off|ID"
            try:
                event = AgendaService(self.db).disable_event(int(event_id_text))
                summary = f"Agenda atualizada: evento {event.title} foi desativado."
                result = self._broadcast_admin_update(summary)
                return f"Evento #{event.id} desativado com sucesso. Notificacao enviada para {result['sent']} membro(s)."
            except ValueError as exc:
                return str(exc)

        if lowered.startswith("dept set|"):
            parts = [p.strip() for p in content[9:].split("|")]
            if len(parts) < 3:
                return "Formato: admin dept set|department_key|day(mon..sun)|HH:MM"
            department_key = parts[0]
            day = parts[1].lower()
            meeting_time = parts[2]
            if day not in self.day_order:
                return "Dia invalido. Use: mon, tue, wed, thu, fri, sat, sun."
            if not re.match(r"^\d{2}:\d{2}$", meeting_time):
                return "Hora invalida. Use HH:MM (ex.: 19:30)."
            try:
                DepartmentCoordinationService(self.db).update_department(
                    department_key=department_key,
                    payload=DepartmentUpdate(meeting_day=day, meeting_time=meeting_time),
                )
                summary = (
                    f"Horario atualizado: departamento {department_key} agora acontece "
                    f"{self.day_label.get(day, day)} {meeting_time}."
                )
                result = self._broadcast_admin_update(summary)
                return f"{summary} Notificacao enviada para {result['sent']} membro(s)."
            except ValueError as exc:
                return str(exc)

        if lowered.startswith("casados set|"):
            parts = [p.strip() for p in content[12:].split("|")]
            if len(parts) < 2:
                return "Formato: admin casados set|YYYY-MM-DD HH:MM|Local|Notas(opcional)"
            starts_at = self._parse_datetime(parts[0])
            if starts_at is None:
                return "Data invalida para Casados. Use YYYY-MM-DD HH:MM."
            location = parts[1]
            notes = parts[2] if len(parts) >= 3 else None
            payload = CasadosEventCreate(
                title="Casados para Sempre",
                event_at=starts_at,
                location=location,
                notes=notes,
                is_active=True,
            )
            event = CasadosParaSempreService(self.db, messaging_provider=self.messaging_provider).upsert_event(payload)
            summary = f"Casados para Sempre atualizado: {event.event_at.strftime('%d/%m/%Y %H:%M')} em {event.location}."
            result = self._broadcast_admin_update(summary)
            return f"{summary} Notificacao enviada para {result['sent']} membro(s)."

        if lowered.startswith("social set|"):
            parts = [p.strip() for p in content[11:].split("|")]
            if len(parts) < 2:
                return "Formato: admin social set|instagram|https://..."
            network = parts[0].lower()
            url = parts[1]
            if network not in {"instagram", "facebook", "tiktok", "youtube"}:
                return "Rede invalida. Use: instagram, facebook, tiktok ou youtube."
            payload = SocialLinksUpdate(**{network: url})
            SocialLinksService().upsert_links(payload)
            summary = f"Rede social oficial atualizada ({network})."
            result = self._broadcast_admin_update(summary)
            return f"{summary} Notificacao enviada para {result['sent']} membro(s)."

        if lowered.startswith("finance set|"):
            parts = [p.strip() for p in content[12:].split("|")]
            if len(parts) < 2:
                return "Formato: admin finance set|pix|CHAVE|tipo(opcional)|titular(opcional)|nota(opcional)"
            field = parts[0].lower()
            if field != "pix":
                return "No momento, apenas 'pix' e suportado em finance set."
            pix_key = parts[1]
            pix_type = parts[2] if len(parts) >= 3 else None
            holder_name = parts[3] if len(parts) >= 4 else None
            note = parts[4] if len(parts) >= 5 else None
            payload = SocialLinksUpdate(
                finance={
                    "pix_key": pix_key,
                    "pix_type": pix_type,
                    "holder_name": holder_name,
                    "note": note,
                }
            )
            SocialLinksService().upsert_links(payload)
            summary = f"Dados financeiros atualizados (PIX: {pix_key})."
            result = self._broadcast_admin_update(summary)
            return f"{summary} Notificacao enviada para {result['sent']} membro(s)."

        return "Comando admin nao reconhecido. Envie: admin help"

    def _sanitize_log_content(self, content: str) -> str:
        text = content or ""
        text = re.sub(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b", "[REDACTED_CNPJ]", text)
        text = re.sub(r"(?i)(admin senha\s+)(\S+)", r"\1[REDACTED]", text)
        return text

    def _log(self, member_id: int | None, interaction_type: str, direction: str, content: str, status: str = "ok") -> None:
        safe_content = self._sanitize_log_content(content)
        entry = InteractionLog(
            member_id=member_id,
            interaction_type=interaction_type,
            direction=direction,
            content=safe_content,
            status=status,
        )
        self.db.add(entry)
        self.db.commit()

    def _dispatch_reply(self, phone: str, member: Member | None, interaction_type: str, reply: str) -> None:
        response_channel = "whatsapp" if member is None else self._normalize_channel(None, member)
        try:
            provider_id = self.messaging_provider.send_message(phone, reply, channel=response_channel)
            self._log(
                member.id if member else None,
                interaction_type,
                "outgoing",
                f"{reply} [channel:{response_channel}] [provider:{provider_id}]",
            )
        except Exception as exc:
            self._log(
                member.id if member else None,
                interaction_type,
                "outgoing",
                reply,
                status=f"error: {exc}",
            )

    def _broadcast_admin_update(self, summary: str) -> dict[str, int]:
        members = self.db.query(Member).filter(Member.is_active.is_(True)).all()
        sent = 0
        errors = 0
        body = ensure_biblical_base(f"Atualizacao oficial ADMAV Sede: {summary}")
        for member in members:
            channel = self._normalize_channel(None, member)
            try:
                provider_id = self.messaging_provider.send_message(member.phone, body, channel=channel)
                self._log(
                    member.id,
                    "admin_update_broadcast",
                    "outgoing",
                    f"{body} [channel:{channel}] [provider:{provider_id}]",
                )
                sent += 1
            except Exception as exc:
                self._log(member.id, "admin_update_broadcast", "outgoing", body, status=f"error: {exc}")
                errors += 1
        return {"sent": sent, "errors": errors}

    def _get_or_create_session(self, phone: str, member: Member | None) -> ConversationSession:
        session = self.db.query(ConversationSession).filter(ConversationSession.phone == phone).first()
        if not session:
            session = ConversationSession(
                phone=phone,
                member_id=member.id if member else None,
                current_step="menu",
                state_json=None,
                last_menu_at=None,
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            return session

        if member and session.member_id != member.id:
            session.member_id = member.id
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
        return session

    def _session_state(self, session: ConversationSession) -> dict:
        if not session.state_json:
            return {}
        try:
            parsed = json.loads(session.state_json)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}

    def _update_session(
        self,
        session: ConversationSession,
        step: str | None = None,
        extra_state: dict | None = None,
        mark_menu: bool = False,
    ) -> ConversationSession:
        if step:
            session.current_step = step
        state = self._session_state(session)
        if extra_state:
            state.update(extra_state)
        session.state_json = json.dumps(state, ensure_ascii=True) if state else None
        if mark_menu:
            session.last_menu_at = datetime.utcnow()
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def _is_menu_trigger(self, normalized: str) -> bool:
        return normalized in {
            "menu",
            "inicio",
            "iniciar",
            "comecar",
            "start",
            "0",
            "oi",
            "ola",
            "bom dia",
            "boa tarde",
            "boa noite",
        }

    def _format_branch(self, branch: dict) -> str:
        name = branch.get("name") or branch.get("key") or "Filial"
        lines = [f"{name}:"]
        if branch.get("instagram"):
            lines.append(f"Instagram: {branch['instagram']}")
        if branch.get("facebook"):
            lines.append(f"Facebook: {branch['facebook']}")
        if branch.get("tiktok"):
            lines.append(f"TikTok: {branch['tiktok']}")
        if branch.get("youtube"):
            lines.append(f"YouTube: {branch['youtube']}")
        if branch.get("visit_note"):
            lines.append(f"Obs: {branch['visit_note']}")
        return "\n".join(lines)

    def _format_leader(self, leader: dict) -> str:
        role = leader.get("role") or "Lideranca"
        name = leader.get("name") or "Contato"
        lines = [f"{role} - {name}:"]
        if leader.get("instagram"):
            lines.append(f"Instagram: {leader['instagram']}")
        if leader.get("facebook"):
            lines.append(f"Facebook: {leader['facebook']}")
        if leader.get("tiktok"):
            lines.append(f"TikTok: {leader['tiktok']}")
        if leader.get("youtube"):
            lines.append(f"YouTube: {leader['youtube']}")
        return "\n".join(lines)

    def _leadership_reply(self, message: str, session: ConversationSession | None, member: Member | None) -> str | None:
        normalized = self._normalize_text(message)
        leadership_keywords = (
            "pastor",
            "pastora",
            "presidente",
            "rogerio",
            "rogerio barros",
            "amanda",
            "amanda barros",
            "instagram do pastor",
            "instagram da pastora",
            "lideranca",
        )
        if not any(keyword in normalized for keyword in leadership_keywords):
            return None

        links = SocialLinksService().get_links()
        leadership = links.get("leadership") or []
        if not leadership:
            return f"{self._address_prefix(session, member)} Ainda nao cadastramos as redes da lideranca aqui no sistema."

        lines = [f"{self._address_prefix(session, member)} Seguem as redes da lideranca:"]
        for leader in leadership:
            lines.append("")
            lines.append(self._format_leader(leader))
        return "\n".join(lines)

    def _visit_reply(self, message: str, session: ConversationSession | None, member: Member | None) -> str | None:
        normalized = self._normalize_text(message)
        visit_keywords = (
            "visita",
            "visitar",
            "filial",
            "campo grande",
            "recreio",
            "onde fica",
            "endereco",
            "endereco da igreja",
        )
        if not any(keyword in normalized for keyword in visit_keywords):
            return None

        links = SocialLinksService().get_links()
        branches = links.get("branches") or []
        base_lines = [
            f"{self._address_prefix(session, member)} Que alegria receber seu interesse em visitar a igreja.",
            "Nucleo ADMAV Sede (redes oficiais):",
        ]
        if links.get("instagram"):
            base_lines.append(f"Instagram: {links['instagram']}")
        if links.get("facebook"):
            base_lines.append(f"Facebook: {links['facebook']}")
        if links.get("youtube"):
            base_lines.append(f"YouTube: {links['youtube']}")
        if links.get("tiktok"):
            base_lines.append(f"TikTok: {links['tiktok']}")

        if "recreio" in normalized:
            for branch in branches:
                key_value = self._normalize_text(str(branch.get("key") or ""))
                name_value = self._normalize_text(str(branch.get("name") or ""))
                if "recreio" in key_value or "recreio" in name_value:
                    return (
                        f"{self._address_prefix(session, member)} Para visita no Recreio, segue a filial:\n"
                        f"{self._format_branch(branch)}\n\n"
                        "Se quiser, tambem te passo os horarios dos cultos."
                    )

        if "campo grande" in normalized:
            for branch in branches:
                key_value = self._normalize_text(str(branch.get("key") or ""))
                name_value = self._normalize_text(str(branch.get("name") or ""))
                if "campo grande" in key_value or "campo grande" in name_value:
                    return (
                        f"{self._address_prefix(session, member)} Para visita em Campo Grande, segue a filial:\n"
                        f"{self._format_branch(branch)}\n\n"
                        "Se quiser, tambem te passo os horarios dos cultos."
                    )

        if branches:
            branch_blocks = [self._format_branch(branch) for branch in branches]
            base_lines.append("")
            base_lines.append("Filiais para visita:")
            base_lines.extend(branch_blocks)
        base_lines.append("")
        base_lines.append("Me diga se voce quer visitar Sede, Recreio ou Campo Grande que te ajudo no proximo passo.")
        return "\n".join(base_lines)

    def _departments_reply(self, session: ConversationSession | None, member: Member | None) -> str:
        structure = DepartmentCoordinationService(self.db).get_departments()
        departments = structure.get("departments") if isinstance(structure, dict) else []
        if not departments:
            return (
                f"{self._address_prefix(session, member)} No momento estamos atualizando os horarios "
                "dos departamentos. Posso te conectar com a secretaria."
            )

        ordered = sorted(
            departments,
            key=lambda item: (
                self.day_order.get(str(item.get("meeting_day") or "").lower(), 99),
                str(item.get("meeting_time") or ""),
            ),
        )
        lines = [f"{self._address_prefix(session, member)} Horarios dos cultos e departamentos:"]
        for dept in ordered:
            day = self.day_label.get(str(dept.get("meeting_day") or "").lower(), str(dept.get("meeting_day") or "-"))
            time = dept.get("meeting_time") or "--:--"
            lines.append(f"- {dept.get('name')}: {day} {time}")

        upcoming = AgendaService(self.db).upcoming(days=45, limit=5)
        if upcoming:
            lines.append("")
            lines.append("Proximos eventos da agenda:")
            for event in upcoming:
                lines.append(
                    f"- [{event.category}] {event.starts_at.strftime('%d/%m/%Y %H:%M')} - {event.title}"
                    + (f" ({event.location})" if event.location else "")
                )
        lines.append("")
        lines.append("Se quiser, te indico o melhor encontro para adolescentes, jovens, adultos ou idosos.")
        return "\n".join(lines)

    def _courses_reply(self, session: ConversationSession | None, member: Member | None) -> str:
        courses = (
            self.db.query(ChurchCourse)
            .filter(ChurchCourse.is_active.is_(True))
            .order_by(ChurchCourse.name.asc())
            .all()
        )
        if not courses:
            return (
                f"{self._address_prefix(session, member)} No momento nao temos cursos ativos cadastrados. "
                "Posso abrir uma solicitacao para a secretaria."
            )

        lines = [f"{self._address_prefix(session, member)} Cursos ativos da igreja:"]
        for course in courses:
            fee_label = "gratuito" if int(course.fee_amount or 0) == 0 else f"R$ {int(course.fee_amount)}"
            lines.append(f"- {course.name} ({fee_label})")
        lines.append("")
        lines.append("Para inscricao, me diga o nome do curso e seu nome completo.")
        return "\n".join(lines)

    def _social_links_reply(self, session: ConversationSession | None, member: Member | None) -> str:
        links = SocialLinksService().get_links()
        lines = [f"{self._address_prefix(session, member)} Redes oficiais da ADMAV Sede:"]
        if links.get("instagram"):
            lines.append(f"- Instagram: {links['instagram']}")
        if links.get("facebook"):
            lines.append(f"- Facebook: {links['facebook']}")
        if links.get("youtube"):
            lines.append(f"- YouTube: {links['youtube']}")
        if links.get("tiktok"):
            lines.append(f"- TikTok: {links['tiktok']}")

        branches = links.get("branches") or []
        if branches:
            lines.append("")
            lines.append("Filiais:")
            for branch in branches:
                name = branch.get("name") or branch.get("key") or "Filial"
                branch_instagram = branch.get("instagram")
                branch_youtube = branch.get("youtube")
                summary = f"- {name}"
                if branch_instagram:
                    summary += f" | Instagram: {branch_instagram}"
                if branch_youtube:
                    summary += f" | YouTube: {branch_youtube}"
                lines.append(summary)
        finance = links.get("finance") or {}
        if finance.get("pix_key"):
            pix_type = (finance.get("pix_type") or "chave").upper()
            lines.append("")
            lines.append(f"PIX ADMAV Sede ({pix_type}): {finance.get('pix_key')}")
        return "\n".join(lines)

    def _finance_reply(self, session: ConversationSession | None, member: Member | None) -> str:
        links = SocialLinksService().get_links()
        finance = links.get("finance") or {}
        pix_key = finance.get("pix_key")
        if not pix_key:
            return (
                f"{self._address_prefix(session, member)} Para dizimo e oferta, posso te orientar e abrir "
                "atendimento financeiro com a secretaria. Se deseja isso agora, responda: quero contribuir."
            )

        pix_type = (finance.get("pix_type") or "chave").upper()
        holder_name = finance.get("holder_name")
        note = finance.get("note")
        lines = [
            f"{self._address_prefix(session, member)} Contribuicao - ADMAV Sede",
            f"PIX ({pix_type}): {pix_key}",
        ]
        if holder_name:
            lines.append(f"Titular: {holder_name}")
        if note:
            lines.append(f"Obs: {note}")
        lines.append("")
        lines.append("Se quiser acompanhamento da secretaria, responda: quero contribuir.")
        return "\n".join(lines)

    def _menu_text(self, session: ConversationSession | None, member: Member | None) -> str:
        greeting = self._greeting(session, member)
        return (
            f"{greeting} Sou o assistente virtual do Nucleo ADMAV Sede. "
            "Tamo junto para te ajudar com alegria e respeito.\n\n"
            "Digite o numero da opcao:\n"
            "1. Horarios de cultos e departamentos\n"
            "2. Endereco e visita (Sede, Recreio, Campo Grande)\n"
            "3. Inscricao no Casados para Sempre\n"
            "4. Pedido de oracao e aconselhamento\n"
            "5. Secretaria (cadastro, documentos, suporte)\n"
            "6. Dizimo e oferta\n"
            "7. Cursos da igreja\n"
            "8. Redes da lideranca pastoral\n"
            "9. Redes sociais oficiais\n"
            "0. Ver menu novamente\n\n"
            "Se preferir, pode escrever sua duvida direto.\n"
            "Se quiser ajustar o tratamento, me diga: pode me chamar de chefe/chefa."
        )

    def _menu_choice_from_text(self, normalized: str) -> str | None:
        match = re.match(r"^\s*(\d{1,2})\b", normalized)
        if match and match.group(1) in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}:
            return match.group(1)

        mapping = {
            "1": ("culto", "horario", "departamento", "intercessao", "domingo", "level teen", "level up", "nucleo"),
            "2": ("visita", "filial", "endereco", "recreio", "campo grande"),
            "3": ("casados", "casados para sempre"),
            "4": ("oracao", "aconselhamento", "ajuda espiritual", "pedido de oracao"),
            "5": ("secretaria", "declaracao", "documento", "cadastro"),
            "6": ("dizimo", "oferta", "contribuicao", "pix"),
            "7": ("curso", "matricula", "inscricao"),
            "8": ("pastor", "pastora", "lideranca"),
            "9": ("instagram", "facebook", "youtube", "tiktok", "rede social"),
            "0": ("menu", "inicio", "comecar"),
        }
        for choice, keywords in mapping.items():
            if any(keyword in normalized for keyword in keywords):
                return choice
        return None

    def _handle_pending_step(
        self,
        session: ConversationSession,
        member: Member | None,
        phone: str,
        normalized: str,
        message: str,
    ) -> tuple[str, str] | None:
        if session.current_step == "await_prayer_request":
            if self._is_menu_trigger(normalized):
                self._update_session(session, step="await_menu_choice", mark_menu=True)
                return ("guided_menu", self._menu_text(session, member))
            if len(message.strip()) < 6:
                return (
                    "menu_pending_oracao",
                    f"{self._address_prefix(session, member)} Pode me contar um pouco mais do pedido de oracao para eu encaminhar certinho?",
                )

            req = self._open_secretariat_request(
                member=member,
                category="oracao",
                title="Pedido de oracao recebido via WhatsApp",
                description=f"Telefone: {phone}\nMensagem: {message.strip()}",
                priority="normal",
            )
            self._update_session(session, step="await_menu_choice", extra_state={"last_ticket": req.id})
            return (
                "menu_pending_oracao",
                (
                    f"{self._address_prefix(session, member)} Pedido recebido, gloria a Deus. Protocolo #{req.id}. "
                    "Nossa equipe vai interceder e te acompanhar. Se quiser, digite 0 para voltar ao menu."
                ),
            )

        if session.current_step == "await_secretariat_request":
            if self._is_menu_trigger(normalized):
                self._update_session(session, step="await_menu_choice", mark_menu=True)
                return ("guided_menu", self._menu_text(session, member))
            if len(message.strip()) < 6:
                return (
                    "menu_pending_secretaria",
                    f"{self._address_prefix(session, member)} Me manda mais detalhes para eu abrir sua solicitacao da secretaria corretamente.",
                )

            req = self._open_secretariat_request(
                member=member,
                category="secretaria",
                title="Solicitacao de secretaria via WhatsApp",
                description=f"Telefone: {phone}\nMensagem: {message.strip()}",
                priority="normal",
            )
            self._update_session(session, step="await_menu_choice", extra_state={"last_ticket": req.id})
            return (
                "menu_pending_secretaria",
                (
                    f"{self._address_prefix(session, member)} Solicitacao aberta com sucesso. Protocolo #{req.id}. "
                    "A secretaria vai retornar em breve. Para mais opcoes, digite 0."
                ),
            )

        return None

    def _open_secretariat_request(
        self,
        member: Member | None,
        category: str,
        title: str,
        description: str,
        priority: str = "normal",
    ) -> SecretariatRequest:
        req = SecretariatRequest(
            member_id=member.id if member else None,
            category=category,
            title=title,
            description=description,
            priority=priority,
        )
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def _handle_menu_choice(
        self,
        choice: str,
        session: ConversationSession,
        member: Member | None,
        phone: str,
    ) -> str:
        if choice == "0":
            self._update_session(session, step="await_menu_choice", mark_menu=True)
            return self._menu_text(session, member)

        if choice == "1":
            self._update_session(session, step="await_menu_choice", extra_state={"last_choice": "1"})
            return self._departments_reply(session, member)

        if choice == "2":
            self._update_session(session, step="await_menu_choice", extra_state={"last_choice": "2"})
            return self._visit_reply("visita", session, member) or (
                f"{self._address_prefix(session, member)} Estamos organizando as informacoes de visita. "
                "Ja te conecto com a secretaria."
            )

        if choice == "3":
            self._update_session(session, step="await_menu_choice", extra_state={"last_choice": "3"})
            casados_service = CasadosParaSempreService(self.db, messaging_provider=self.messaging_provider)
            handled, reply = casados_service.handle_whatsapp_registration(
                phone=phone,
                message="casados para sempre",
                member=member,
            )
            if handled and reply:
                return reply
            return "No momento nao consegui iniciar o fluxo do Casados para Sempre. Tente novamente em instantes."

        if choice == "4":
            self._update_session(session, step="await_prayer_request", extra_state={"last_choice": "4"})
            return (
                f"{self._address_prefix(session, member)} Me envie seu pedido de oracao em uma mensagem. "
                "Vamos caminhar com voce em oracao."
            )

        if choice == "5":
            self._update_session(session, step="await_secretariat_request", extra_state={"last_choice": "5"})
            return (
                f"{self._address_prefix(session, member)} Me descreva sua necessidade da secretaria em uma mensagem "
                "que eu abro o atendimento agora."
            )

        if choice == "6":
            self._update_session(session, step="await_menu_choice", extra_state={"last_choice": "6"})
            return self._finance_reply(session, member)

        if choice == "7":
            self._update_session(session, step="await_menu_choice", extra_state={"last_choice": "7"})
            return self._courses_reply(session, member)

        if choice == "8":
            self._update_session(session, step="await_menu_choice", extra_state={"last_choice": "8"})
            return self._leadership_reply("pastor", session, member) or (
                f"{self._address_prefix(session, member)} Ainda nao temos redes da lideranca cadastradas."
            )

        if choice == "9":
            self._update_session(session, step="await_menu_choice", extra_state={"last_choice": "9"})
            return self._social_links_reply(session, member)

        self._update_session(session, step="await_menu_choice")
        return self._menu_text(session, member)

    def send_good_news(self, custom_message: str | None = None, channel: str | None = None) -> int:
        members = self.db.query(Member).filter(Member.is_active.is_(True)).all()
        sent = 0
        by_group_messages: dict[tuple[str, str, str], str] = {}
        for member in members:
            message = custom_message or "Boas noticias: Deus te ama e cuida de voce. Estamos com voce em oracao."
            recommended = self.ml_service.recommended_channel(member)
            message_channel = self._normalize_channel(channel or recommended, member)
            ml_hint = self.ml_service.communication_hint(member) or ""
            try:
                if custom_message:
                    address_term = self._infer_address_from_name(member.name) or "chefe"
                    message = self._ensure_address_in_text(custom_message, address_term)
                else:
                    address_term = self._infer_address_from_name(member.name) or "chefe"
                    group_key = (member.age_group or "adult", ml_hint, address_term)
                    if group_key not in by_group_messages:
                        by_group_messages[group_key] = self.ai_service.good_news_message(
                            age_group=group_key[0],
                            extra_guidance=ml_hint,
                            address_term=address_term,
                        )
                    message = by_group_messages[group_key]
                message = ensure_biblical_base(message)
                provider_id = self.messaging_provider.send_message(member.phone, message, channel=message_channel)
                self._log(
                    member.id,
                    "good_news",
                    "outgoing",
                    f"{message} [channel:{message_channel}] [provider:{provider_id}]",
                )
                sent += 1
            except Exception as exc:
                self._log(member.id, "good_news", "outgoing", message, status=f"error: {exc}")
        return sent

    def send_weekly_devotional(self, channel: str | None = None) -> int:
        members = self.db.query(Member).filter(Member.is_active.is_(True)).all()
        sent = 0
        by_group_devotional: dict[tuple[str, str, str], str] = {}
        for member in members:
            devotional_text = "Devocional da semana: Deus e fiel e permanece conosco."
            recommended = self.ml_service.recommended_channel(member)
            message_channel = self._normalize_channel(channel or recommended, member)
            ml_hint = self.ml_service.communication_hint(member) or ""
            try:
                address_term = self._infer_address_from_name(member.name) or "chefe"
                group_key = (member.age_group or "adult", ml_hint, address_term)
                if group_key not in by_group_devotional:
                    by_group_devotional[group_key] = self.ai_service.weekly_devotional(
                        age_group=group_key[0],
                        extra_guidance=ml_hint,
                        address_term=address_term,
                    )
                devotional_text = by_group_devotional[group_key]
                devotional_text = ensure_biblical_base(devotional_text)
                provider_id = self.messaging_provider.send_message(
                    member.phone,
                    devotional_text,
                    channel=message_channel,
                )
                self._log(
                    member.id,
                    "weekly_devotional",
                    "outgoing",
                    f"{devotional_text} [channel:{message_channel}] [provider:{provider_id}]",
                )
                sent += 1
            except Exception as exc:
                self._log(member.id, "weekly_devotional", "outgoing", devotional_text, status=f"error: {exc}")
        return sent

    def process_incoming_message(self, phone: str, message: str) -> str:
        member = self.db.query(Member).filter(Member.phone == phone).first()
        session = self._get_or_create_session(phone=phone, member=member)
        safe_message = guard.sanitize_user_input(message)
        self._log(member.id if member else None, "inbound_message", "incoming", safe_message)
        normalized = self._normalize_text(safe_message)
        self._capture_address_preference(session, safe_message)
        address_term = self._address_term_for(session, member)
        address_prefix = self._address_prefix(session, member)

        def finalize(text: str) -> str:
            return ensure_biblical_base(text)

        if guard.is_rate_limited(phone):
            write_security_event(
                event_type="agent_user_rate_limited",
                severity="warning",
                actor=phone,
                details={"channel": "whatsapp"},
            )
            reply = f"{address_prefix} Muitas mensagens em pouco tempo. Aguarde um instante e tente novamente."
            reply = finalize(reply)
            self._dispatch_reply(phone, member, "rate_limited", reply)
            return reply

        if guard.is_prompt_injection(safe_message):
            write_security_event(
                event_type="prompt_injection_detected",
                severity="warning",
                actor=phone,
                details={"message": safe_message[:120]},
            )
            reply = (
                f"{address_prefix} Por seguranca, nao consegui processar esse formato de mensagem. "
                "Pode reenviar de forma simples?"
            )
            reply = finalize(reply)
            self._dispatch_reply(phone, member, "prompt_injection_block", reply)
            return reply

        admin_reply = self._handle_admin_command(phone=phone, message=safe_message, session=session)
        if admin_reply is not None:
            admin_reply = finalize(admin_reply)
            self._update_session(session, step="await_menu_choice")
            self._dispatch_reply(phone, member, "admin_command", admin_reply)
            return admin_reply

        if self._is_menu_trigger(normalized):
            self._update_session(session, step="await_menu_choice", mark_menu=True)
            reply = self._menu_text(session, member)
            reply = finalize(reply)
            self._dispatch_reply(phone, member, "guided_menu", reply)
            return reply

        casados_service = CasadosParaSempreService(self.db, messaging_provider=self.messaging_provider)
        handled, casados_reply = casados_service.handle_whatsapp_registration(phone=phone, message=safe_message, member=member)
        if handled:
            casados_reply = self._ensure_address_in_text(casados_reply, address_term)
            casados_reply = finalize(casados_reply)
            self._update_session(session, step="await_menu_choice", extra_state={"last_choice": "3"})
            self._dispatch_reply(phone, member, "casados_flow_reply", casados_reply)
            return casados_reply

        visit_reply = self._visit_reply(safe_message, session, member)
        if visit_reply:
            self._update_session(session, step="await_menu_choice", extra_state={"last_choice": "2"})
            visit_reply = finalize(visit_reply)
            self._dispatch_reply(phone, member, "visit_info", visit_reply)
            return visit_reply

        leadership_reply = self._leadership_reply(safe_message, session, member)
        if leadership_reply:
            self._update_session(session, step="await_menu_choice", extra_state={"last_choice": "8"})
            leadership_reply = finalize(leadership_reply)
            self._dispatch_reply(phone, member, "leadership_social_info", leadership_reply)
            return leadership_reply

        pending_result = self._handle_pending_step(
            session=session,
            member=member,
            phone=phone,
            normalized=normalized,
            message=safe_message,
        )
        if pending_result:
            interaction_type, pending_reply = pending_result
            pending_reply = finalize(pending_reply)
            self._dispatch_reply(phone, member, interaction_type, pending_reply)
            return pending_reply

        if "quero contribuir" in normalized:
            req = self._open_secretariat_request(
                member=member,
                category="financeiro",
                title="Solicitacao financeira via WhatsApp",
                description=f"Telefone: {phone}\nMensagem: {safe_message.strip()}",
                priority="normal",
            )
            self._update_session(session, step="await_menu_choice", extra_state={"last_ticket": req.id, "last_choice": "6"})
            finance = SocialLinksService().get_links().get("finance") or {}
            pix_key = finance.get("pix_key")
            pix_type = (finance.get("pix_type") or "chave").upper() if pix_key else None
            pix_chunk = f" PIX ({pix_type}): {pix_key}." if pix_key else ""
            reply = (
                f"{address_prefix} Perfeito! Atendimento financeiro aberto, protocolo #{req.id}."
                f"{pix_chunk} A secretaria vai te enviar as orientacoes de dizimo/oferta. Digite 0 para voltar ao menu."
            )
            reply = finalize(reply)
            self._dispatch_reply(phone, member, "menu_finance_request", reply)
            return reply

        choice = self._menu_choice_from_text(normalized)
        if choice is not None:
            reply = self._handle_menu_choice(choice=choice, session=session, member=member, phone=phone)
            reply = finalize(reply)
            self._dispatch_reply(phone, member, "guided_menu_choice", reply)
            return reply

        if session.last_menu_at is None:
            self._update_session(session, step="await_menu_choice", mark_menu=True)
            reply = self._menu_text(session, member)
            reply = finalize(reply)
            self._dispatch_reply(phone, member, "guided_menu", reply)
            return reply

        if not member:
            reply = f"{address_prefix} Posso te guiar rapidinho pelo menu. Digite 0 para ver as opcoes de atendimento da igreja."
            reply = finalize(reply)
            self._dispatch_reply(phone, member, "guided_menu_prompt", reply)
            return reply

        ml_hint = self.ml_service.communication_hint(member)
        reply = self.ai_service.reply_to_member(
            member_name=member.name,
            incoming_message=safe_message,
            age_group=member.age_group,
            extra_guidance=ml_hint,
            address_term=address_term,
        )
        reply = finalize(reply)
        self._dispatch_reply(phone, member, "inbound_reply", reply)
        return reply

    def call_member(self, member_id: int, custom_message: str | None = None) -> str:
        member = self.db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise ValueError("Membro nao encontrado.")

        address_term = self._infer_address_from_name(member.name) or "chefe"
        spoken_text = custom_message or (
            f"Ola {address_term} {member.name}. Aqui e da igreja para lembrar que voce e importante para nos. "
            "Que Deus te abencoe nesta semana."
        )
        spoken_text = ensure_biblical_base(spoken_text)
        call_id = self.calling_provider.make_call(member.phone, spoken_text)
        self._log(member.id, "phone_call", "outgoing", f"{spoken_text} [provider:{call_id}]")
        return call_id
