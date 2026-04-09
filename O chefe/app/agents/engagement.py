from __future__ import annotations

from app.agents.base import AgentState
from app.db import InteractionRepository
from app.services.llm_service import LLMService


class EngagementAgent:
    name = "EngagementAgent"

    def __init__(self, *, llm_service: LLMService, interaction_repository: InteractionRepository) -> None:
        self._llm_service = llm_service
        self._interaction_repository = interaction_repository

    async def __call__(self, state: AgentState) -> AgentState:
        interactions = []
        if state.get("member_id"):
            interactions = await self._interaction_repository.list_recent_by_member(state["member_id"])
        history = "\n".join(f"- {item['message']} => {item['response']}" for item in interactions) or "Sem historico."
        fallback = (
            "Sugestão de engajamento: faça contato pastoral, convide para o próximo culto e registre o retorno."
        )
        response = await self._llm_service.generate(
            system_prompt=(
                "Voce apoia o acompanhamento de membros com foco em engajamento, acolhimento e proximos passos claros."
            ),
            human_prompt=f"Mensagem: {state['message']}\nHistorico recente:\n{history}",
            fallback=fallback,
        )
        return {**state, "response": response}
