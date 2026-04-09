import json
from datetime import date, datetime, timedelta
from typing import Any

from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.services.ai_service import AIService
from app.services.ml_service import CommunityMLService
from app.services.social_links_service import SocialLinksService


class MediaContentService:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.ai = AIService()
        self.ml = CommunityMLService()
        self.social = SocialLinksService()

    def _extract_json(self, raw: str) -> dict[str, Any] | None:
        text = (raw or "").strip()
        if not text:
            return None
        first = text.find("{")
        last = text.rfind("}")
        if first < 0 or last <= first:
            return None
        chunk = text[first : last + 1]
        try:
            parsed = json.loads(chunk)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None

    def _context(self) -> str:
        links = self.social.get_links()
        ml_summary = self.ml.summary(self.db)
        return (
            f"Igreja: {settings.nucleus_name}\n"
            f"Assinatura: {settings.church_signature_phrase}\n"
            f"Estilo base:\n{self.ai.style_context}\n\n"
            f"Redes oficiais:\n{json.dumps(links, ensure_ascii=True)}\n\n"
            f"Resumo de engajamento:\n{json.dumps(ml_summary, ensure_ascii=True)}\n"
        )

    def _fallback_plan(self, week_focus: str, objective: str, posts_per_platform: int, include_youth_focus: bool) -> dict[str, Any]:
        pillars = [
            "Devocional curto com aplicacao pratica",
            "Convite para culto/celula e comunhao",
            "Testemunho real de transformacao",
            "Ensino biblico objetivo para a semana",
        ]
        if include_youth_focus:
            pillars.append("Quadro juventude com linguagem dinamica e desafio de fe")

        platforms: dict[str, list[dict[str, str]]] = {}
        for platform in ("instagram", "facebook", "tiktok", "youtube"):
            ideas: list[dict[str, str]] = []
            for idx in range(posts_per_platform):
                ideas.append(
                    {
                        "title": f"{platform.title()} #{idx + 1} - {week_focus}",
                        "format": "reel curto" if platform in {"instagram", "tiktok"} else "post/video",
                        "idea": (
                            f"Mensagem focada em {week_focus}, conectando com {objective}, "
                            f"com chamada para participar do {settings.nucleus_name}."
                        ),
                        "cta": "Compartilhe e marque alguem que precisa dessa palavra.",
                    }
                )
            platforms[platform] = ideas

        return {
            "nucleus": settings.nucleus_name,
            "week_focus": week_focus,
            "objective": objective,
            "pillars": pillars,
            "platforms": platforms,
            "notes": [
                "Priorizar autenticidade e testemunhos reais.",
                "Sempre incluir chamada para culto e comunhao.",
                "Manter identidade pastoral: humor leve, respeito e base biblica.",
            ],
        }

    def generate_plan(self, payload) -> dict[str, Any]:
        if not self.client:
            return self._fallback_plan(
                week_focus=payload.week_focus,
                objective=payload.objective,
                posts_per_platform=payload.posts_per_platform,
                include_youth_focus=payload.include_youth_focus,
            )

        prompt = (
            "Voce e estrategista de conteudo cristao para a equipe de midia de igreja.\n"
            "Gere um plano semanal para Instagram, Facebook, TikTok e YouTube.\n"
            "Retorne JSON valido com chaves: week_focus, objective, pillars, platforms, notes.\n"
            "Em platforms: objeto com as 4 redes, cada uma com lista de ideias contendo title, format, idea, cta.\n"
            f"Posts por rede: {payload.posts_per_platform}.\n"
            f"Foco da semana: {payload.week_focus}.\n"
            f"Objetivo: {payload.objective}.\n"
            f"Incluir foco juventude: {payload.include_youth_focus}.\n\n"
            f"Contexto:\n{self._context()}"
        )
        try:
            response = self.client.responses.create(
                model=settings.openai_model,
                input=prompt,
                max_output_tokens=900,
            )
            parsed = self._extract_json(response.output_text or "")
            if parsed:
                parsed["nucleus"] = settings.nucleus_name
                return parsed
        except Exception:
            pass
        return self._fallback_plan(
            week_focus=payload.week_focus,
            objective=payload.objective,
            posts_per_platform=payload.posts_per_platform,
            include_youth_focus=payload.include_youth_focus,
        )

    def _fallback_caption(self, payload) -> dict[str, str]:
        verse_line = f" | Versiculo: {payload.verse}" if payload.verse else ""
        cta = payload.cta or "Comente 'eu creio' e compartilhe com alguem."
        caption = (
            f"Paz do Senhor, familia {settings.nucleus_name}! Hoje o tema e {payload.theme}. "
            f"Deus segue cuidando de cada detalhe da nossa jornada.{verse_line} "
            f"Tamo junto em oracao e comunhao. {cta}"
        )
        return {"platform": payload.platform, "caption": caption}

    def generate_caption(self, payload) -> dict[str, str]:
        if not self.client:
            return self._fallback_caption(payload)
        prompt = (
            "Crie uma legenda cristaa para rede social em portugues do Brasil, com linguagem pastoral, "
            "respeitosa, humor leve e girias evangelicas naturais sem exagero.\n"
            f"Plataforma: {payload.platform}\n"
            f"Tema: {payload.theme}\n"
            f"Publico: {payload.audience}\n"
            f"Versiculo opcional: {payload.verse or ''}\n"
            f"CTA opcional: {payload.cta or ''}\n"
            "Tamanho: ate 90 palavras.\n"
            "Retorne texto puro.\n\n"
            f"Contexto:\n{self._context()}"
        )
        try:
            response = self.client.responses.create(
                model=settings.openai_model,
                input=prompt,
                max_output_tokens=220,
            )
            text = (response.output_text or "").strip()
            if text:
                return {"platform": payload.platform, "caption": text}
        except Exception:
            pass
        return self._fallback_caption(payload)

    def _fallback_calendar(self, start: date, days: int, objective: str) -> dict[str, Any]:
        sequence = ["instagram", "tiktok", "facebook", "youtube", "instagram", "tiktok", "youtube"]
        themes = [
            "devocional de 60 segundos",
            "convite para culto",
            "testemunho de fe",
            "mensagem pastoral",
            "juventude e proposito",
            "oracao da semana",
            "resumo do culto",
        ]
        items = []
        for i in range(days):
            d = start + timedelta(days=i)
            platform = sequence[i % len(sequence)]
            theme = themes[i % len(themes)]
            items.append(
                {
                    "date": d.isoformat(),
                    "platform": platform,
                    "theme": theme,
                    "goal": objective,
                    "format": "video curto" if platform in {"instagram", "tiktok"} else "post/video",
                }
            )
        return {"nucleus": settings.nucleus_name, "objective": objective, "items": items}

    def generate_calendar(self, payload) -> dict[str, Any]:
        start = payload.start_date or date.today()
        if not self.client:
            return self._fallback_calendar(start=start, days=payload.days, objective=payload.objective)

        prompt = (
            "Monte um calendario de conteudo para igreja em JSON valido.\n"
            "Retorne objeto com chaves: objective, items.\n"
            "items deve ser lista com: date (YYYY-MM-DD), platform, theme, goal, format.\n"
            f"Data inicial: {start.isoformat()}.\n"
            f"Quantidade de dias: {payload.days}.\n"
            f"Objetivo: {payload.objective}.\n\n"
            f"Contexto:\n{self._context()}"
        )
        try:
            response = self.client.responses.create(
                model=settings.openai_model,
                input=prompt,
                max_output_tokens=900,
            )
            parsed = self._extract_json(response.output_text or "")
            if parsed and isinstance(parsed.get("items"), list):
                parsed["nucleus"] = settings.nucleus_name
                return parsed
        except Exception:
            pass
        return self._fallback_calendar(start=start, days=payload.days, objective=payload.objective)

    def generate_plan_from_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        class _P:
            week_focus = payload.get("week_focus", "esperanca e comunhao")
            objective = payload.get("objective", "edificar a igreja e alcancar novas pessoas")
            posts_per_platform = int(payload.get("posts_per_platform", 2))
            include_youth_focus = bool(payload.get("include_youth_focus", True))

        return self.generate_plan(_P())
