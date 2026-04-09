from __future__ import annotations

from app.agents.base import AgentState
from app.services.llm_service import LLMService


class CadastroAgent:
    name = "CadastroAgent"

    def __init__(self, llm_service: LLMService) -> None:
        self._llm_service = llm_service

    async def __call__(self, state: AgentState) -> AgentState:
        fallback = (
            "Para cadastrar um membro envie nome, telefone e unidade. "
            "Se preferir pela API, use o endpoint POST /members."
        )
        response = await self._llm_service.generate(
            system_prompt="Voce orienta o cadastro de membros de uma igreja de forma objetiva e acolhedora.",
            human_prompt=(
                f"Mensagem do usuario: {state['message']}\n"
                "Explique os dados obrigatorios para cadastro: nome, telefone e unidade."
            ),
            fallback=fallback,
        )
        return {**state, "response": response}
