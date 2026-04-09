from __future__ import annotations

from app.agents.base import AgentState
from app.services.llm_service import LLMService


class DevotionalAgent:
    name = "DevotionalAgent"

    def __init__(self, llm_service: LLMService) -> None:
        self._llm_service = llm_service

    async def __call__(self, state: AgentState) -> AgentState:
        unit = state.get("unit") or "igreja"
        fallback = (
            "Versículo: Lamentações 3:22-23\n"
            "Reflexão: As misericórdias do Senhor se renovam a cada manhã e sustentam a igreja em todo tempo.\n"
            "Aplicação: Comece o dia em oração e compartilhe esperança com alguém da sua unidade."
        )
        response = await self._llm_service.generate(
            system_prompt=(
                "Crie devocionais curtos com versiculo, reflexao e aplicacao em portugues, "
                "com linguagem biblica simples e edificante."
            ),
            human_prompt=f"Crie um devocional curto para a unidade {unit}.",
            fallback=fallback,
        )
        return {**state, "response": response}

    async def compose(self, unit: str) -> str:
        result = await self.__call__({"message": "devocional", "unit": unit})
        return result["response"]
