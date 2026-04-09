from __future__ import annotations

from app.agents.base import AgentState
from app.db import MemberRepository
from app.rag import RAGService
from app.services.llm_service import LLMService


class OrchestratorAgent:
    name = "OrchestratorAgent"

    def __init__(
        self,
        *,
        llm_service: LLMService,
        member_repository: MemberRepository,
        rag_service: RAGService,
    ) -> None:
        self._llm_service = llm_service
        self._member_repository = member_repository
        self._rag_service = rag_service

    async def __call__(self, state: AgentState) -> AgentState:
        member = None
        if state.get("member_id"):
            member = await self._member_repository.get_by_id(state["member_id"])

        resolved_unit = state.get("unit") or (member or {}).get("unit")
        context_docs = await self._rag_service.search(state["message"], resolved_unit, limit=3)
        intent = await self._llm_service.classify_intent(state["message"])
        return {
            **state,
            "member": member,
            "unit": resolved_unit,
            "intent": intent,
            "context_docs": context_docs,
        }
