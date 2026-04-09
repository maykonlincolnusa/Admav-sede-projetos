from __future__ import annotations

from app.agents.base import AgentState
from app.services.llm_service import LLMService


class WelcomeAgent:
    name = "WelcomeAgent"

    def __init__(self, llm_service: LLMService) -> None:
        self._llm_service = llm_service

    async def __call__(self, state: AgentState) -> AgentState:
        member_name = (state.get("member") or {}).get("name", "irmão(ã)")
        unit = state.get("unit") or (state.get("member") or {}).get("unit", "igreja")
        fallback = (
            f"Paz do Senhor, {member_name}!\n\n"
            f"Que alegria ter você na {unit}...\n"
            "Você é muito bem-vindo!\n"
            "Esperamos você no próximo culto 🙌"
        )
        response = await self._llm_service.generate(
            system_prompt=(
                "Escreva mensagens de boas-vindas acolhedoras, pastorais e simples para novos membros."
            ),
            human_prompt=(
                f"Crie uma mensagem para {member_name} na unidade {unit} usando o tom acolhedor e pastoral."
            ),
            fallback=fallback,
        )
        return {**state, "response": response}

    async def compose_message(self, *, member_name: str, unit: str) -> str:
        state: AgentState = {"message": "boas-vindas", "unit": unit, "member": {"name": member_name, "unit": unit}}
        result = await self.__call__(state)
        return result["response"]
