import re
from pathlib import Path

from openai import OpenAI

from app.config import settings
from app.secrets import resolve_secret
from app.services.ai_guard_service import guard


class AIService:
    _valid_groups = {"youth", "adult", "senior"}

    def __init__(self):
        api_key = resolve_secret("OPENAI_API_KEY", settings.openai_api_key)
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.style_context = self._load_style_context()

    def _load_style_context(self) -> str:
        path = Path(settings.style_examples_file)
        lines: list[str] = []

        if path.exists():
            for raw in path.read_text(encoding="utf-8").splitlines():
                text = raw.strip()
                if not text or text.startswith("#"):
                    continue
                if text.startswith("-"):
                    text = text.lstrip("-").strip()
                lines.append(text)

        base_lines = [
            f"Assinatura institucional: '{settings.church_signature_phrase}'.",
            f"Tom de familia da fe: acolhimento, comunhao, convite para culto, {settings.nucleus_name} e oracao.",
            "Giria evangelica natural e moderada: 'paz do Senhor', 'gloria a Deus', 'tamo junto em oracao'.",
            "Humor leve e santo: sem sarcasmo com dor, sem desrespeito, sem exagero.",
            "Objetivo: engajar e reter a pessoa na comunidade, reforcando comunhao, culto e servico.",
        ]

        combined = base_lines + lines[:20]
        return "\n".join(f"- {item}" for item in combined)

    def _normalize_group(self, age_group: str | None) -> str:
        if age_group in self._valid_groups:
            return age_group
        return "adult"

    def _audience_guidance(self, age_group: str) -> str:
        if age_group == "youth":
            return (
                "Publico jovem: linguagem leve, dinamica e encorajadora. "
                "Pode usar uma giria evangelica extra, humor curto e convite para comunhao."
            )
        if age_group == "senior":
            return (
                "Publico idoso: linguagem respeitosa e calma, com carinho pastoral. "
                "Evite excesso de girias e use clareza, honra e cuidado."
            )
        return (
            "Publico adulto: linguagem equilibrada, objetiva e acolhedora, "
            "com aplicacao pratica para rotina, familia e trabalho."
        )

    def _normalize_address(self, address_term: str | None) -> str:
        term = (address_term or "").strip().lower()
        if term not in {"chefe", "chefa"}:
            return "chefe"
        return term

    def _ensure_address(self, text: str, address_term: str | None) -> str:
        if not text:
            return text
        term = self._normalize_address(address_term)
        if re.search(r"\bchefe\b|\bchefa\b", text, flags=re.IGNORECASE):
            return text
        return f"{term.capitalize()}, {text}"

    def _fallback_reply(self, member_name: str, age_group: str = "adult", address_term: str | None = None) -> str:
        age_group = self._normalize_group(age_group)
        term = self._normalize_address(address_term)
        if age_group == "youth":
            return (
                f"Paz do Senhor, {term} {member_name}! Mensagem recebida, gloria a Deus. "
                "Bora caminhar firme com Jesus essa semana. Tamo junto em oracao e comunhao. "
                "Base biblica: Jeremias 29:11."
            )
        if age_group == "senior":
            return (
                f"Paz do Senhor, {term} {member_name}. Recebemos sua mensagem com carinho. "
                "Estamos em oracao por voce. Leia Filipenses 4:6-7 e descanse no Senhor. "
                "Base biblica: Filipenses 4:6-7."
            )
        return (
            f"Paz do Senhor, {term} {member_name}! Recebi sua mensagem direitinho, gloria a Deus. "
            "Tamo junto em oracao, sem vacilar. Aqui e uma igreja que ama voce. "
            "Leia Filipenses 4:6-7 e deixa o coracao descansar no Pai. Base biblica: Filipenses 4:6-7."
        )

    def _fallback_good_news(self, age_group: str, address_term: str | None = None) -> str:
        age_group = self._normalize_group(age_group)
        term = self._normalize_address(address_term)
        if age_group == "youth":
            return (
                f"{term.capitalize()}, boas noticias, juventude: Deus nao desistiu de voce nem por um minuto. "
                "Fica firme em Jeremias 29:11 e bora viver proposito. Base biblica: Jeremias 29:11."
            )
        if age_group == "senior":
            return (
                f"{term.capitalize()}, boas noticias: o Senhor permanece fiel em todas as fases da vida. "
                "Medite em Isaias 46:4 e descanse no cuidado de Deus. Base biblica: Isaias 46:4."
            )
        return (
            f"{term.capitalize()}, boas noticias: Deus te ama e cuida de voce. "
            "Medite em Joao 3:16. Estamos com voce em oracao. Base biblica: Joao 3:16."
        )

    def _fallback_weekly_devotional(self, age_group: str, address_term: str | None = None) -> str:
        age_group = self._normalize_group(age_group)
        term = self._normalize_address(address_term)
        if age_group == "youth":
            return (
                f"{term.capitalize()}, devocional da semana: 1 Timoteo 4:12. "
                "Ninguem despreze sua juventude. Seja exemplo na palavra, no amor e na fe. "
                "Pratica: separe 10 minutos por dia para Palavra e oracao. "
                "Base biblica: 1 Timoteo 4:12."
            )
        if age_group == "senior":
            return (
                f"{term.capitalize()}, devocional da semana: Salmo 92:14. "
                "Na velhice ainda darao frutos. O Senhor fortalece e sustenta seus servos. "
                "Pratica: ore por sua familia e compartilhe um versiculo com alguem. "
                "Base biblica: Salmo 92:14."
            )
        return (
            f"{term.capitalize()}, devocional da semana: Salmo 46:1. "
            "Deus e nosso refugio e fortaleza. Quando bater a luta, lembra: o General nao perde batalha. "
            "Ora, confia e segue firme, porque o ceu nao trabalha com derrota final para quem permanece em Cristo. "
            "Estamos com voce, porque somos uma igreja que ama voce. Base biblica: Salmo 46:1."
        )

    def reply_to_member(
        self,
        member_name: str,
        incoming_message: str,
        age_group: str = "adult",
        extra_guidance: str | None = None,
        address_term: str | None = None,
    ) -> str:
        age_group = self._normalize_group(age_group)
        clean_message = guard.sanitize_user_input(incoming_message)
        address_term = self._normalize_address(address_term)
        if guard.is_prompt_injection(clean_message):
            return "Recebi sua mensagem. Para sua seguranca, nao consigo processar esse formato. Pode reformular em linguagem simples?"
        if not self.client:
            return guard.sanitize_output(self._fallback_reply(member_name, age_group, address_term))

        try:
            response = self.client.responses.create(
                model=settings.openai_model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "Voce e um assistente pastoral de uma igreja evangelica. "
                            "Fale em portugues, com tom acolhedor, respeitoso e biblico, respostas curtas. "
                            "Use humor leve e saudavel quando apropriado, sem debochar da fe nem da dor da pessoa. "
                            "Pode usar girias evangelicas naturais (ex.: 'gloria a Deus', 'tamo junto em oracao', "
                            "'paz do Senhor', 'varao/varoa' com bom senso), sem exagero. "
                            "Nao invente promessas nem orientacoes medicas/juridicas. "
                            "Sempre incentive contato com a lideranca da igreja quando necessario.\n\n"
                            f"Sempre trate a pessoa como '{address_term}' de forma respeitosa.\n"
                            "Busque engajar e reter a pessoa na comunidade, convidando para cultos, grupos e comunhao.\n"
                            "Sempre inclua uma base biblica com referencia (ex.: 'Base biblica: Filipenses 4:6-7').\n\n"
                            "Adequacao por publico:\n"
                            f"{self._audience_guidance(age_group)}\n\n"
                            "Base de estilo para esta igreja:\n"
                            f"{self.style_context}\n\n"
                            f"{extra_guidance or ''}"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Faixa etaria do membro: {age_group}\n"
                            f"Membro: {member_name}\n"
                            f"Tratamento preferido: {address_term}\n"
                            f"Mensagem recebida: {clean_message}\n"
                            "Responda com no maximo 120 palavras."
                        ),
                    },
                ],
                max_output_tokens=220,
            )
            text = (response.output_text or "").strip()
            fallback = self._fallback_reply(member_name, age_group, address_term)
            final_text = text if text else fallback
            return guard.sanitize_output(self._ensure_address(final_text, address_term))
        except Exception:
            return guard.sanitize_output(self._fallback_reply(member_name, age_group, address_term))

    def good_news_message(
        self,
        age_group: str = "adult",
        extra_guidance: str | None = None,
        address_term: str | None = None,
    ) -> str:
        age_group = self._normalize_group(age_group)
        address_term = self._normalize_address(address_term)
        if not self.client:
            return guard.sanitize_output(self._fallback_good_news(age_group, address_term))

        try:
            response = self.client.responses.create(
                model=settings.openai_model,
                input=(
                    "Escreva uma mensagem biblica curta de boas noticias (40-70 palavras). "
                    "Fale em portugues com respeito, humor leve e girias evangelicas naturais sem exagero. "
                    f"Comece chamando a pessoa de '{address_term}'. "
                    "Inclua base biblica com referencia ao final. "
                    f"Publico alvo: {age_group}. "
                    f"Adequacao por publico: {self._audience_guidance(age_group)}. "
                    f"Base de voz:\n{self.style_context}\n\n"
                    f"{extra_guidance or ''}"
                ),
                max_output_tokens=180,
            )
            text = (response.output_text or "").strip()
            if text:
                return guard.sanitize_output(self._ensure_address(text, address_term))
        except Exception:
            pass
        return guard.sanitize_output(self._fallback_good_news(age_group, address_term))

    def weekly_devotional(
        self,
        age_group: str = "adult",
        extra_guidance: str | None = None,
        address_term: str | None = None,
    ) -> str:
        age_group = self._normalize_group(age_group)
        address_term = self._normalize_address(address_term)
        if not self.client:
            return guard.sanitize_output(self._fallback_weekly_devotional(age_group, address_term))
        try:
            response = self.client.responses.create(
                model=settings.openai_model,
                input=(
                    "Escreva um devocional semanal cristao em portugues com 90 a 140 palavras, "
                    "incluindo 1 versiculo biblico e uma aplicacao pratica. "
                    "Estilo: respeitoso, biblico, com humor leve e girias evangelicas naturais sem exagero. "
                    f"Comece chamando a pessoa de '{address_term}'. "
                    "Inclua base biblica com referencia ao final. "
                    f"Publico alvo: {age_group}. "
                    f"Adequacao por publico: {self._audience_guidance(age_group)}. "
                    f"Use como base de voz:\n{self.style_context}\n\n"
                    f"{extra_guidance or ''}"
                ),
                max_output_tokens=260,
            )
            text = (response.output_text or "").strip()
            fallback = self._fallback_weekly_devotional(age_group, address_term)
            final_text = text if text else fallback
            return guard.sanitize_output(self._ensure_address(final_text, address_term))
        except Exception:
            return guard.sanitize_output(self._fallback_weekly_devotional(age_group, address_term))
