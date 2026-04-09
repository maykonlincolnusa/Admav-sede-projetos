from __future__ import annotations

from app.agents.base import AgentState
from app.rag import RAGService
from app.services.llm_service import LLMService


class RAGAgent:
    name = "RAGAgent"

    def __init__(self, *, rag_service: RAGService, llm_service: LLMService) -> None:
        self._rag_service = rag_service
        self._llm_service = llm_service

    async def __call__(self, state: AgentState) -> AgentState:
        unit = state.get("unit")
        context_docs = state.get("context_docs") or await self._rag_service.search(state["message"], unit)
        context = "\n\n".join(document["content"] for document in context_docs) or "Sem contexto adicional."
        fallback = (
            "Com base na memória da igreja, encontrei estas referências:\n"
            f"{context}"
        )
        response = await self._llm_service.generate(
            system_prompt=(
                "Responda perguntas usando apenas o contexto recuperado da base da igreja. "
                "Se o contexto for insuficiente, diga isso de forma transparente."
            ),
            human_prompt=f"Pergunta: {state['message']}\n\nContexto:\n{context}",
            fallback=fallback,
        )
        return {**state, "context_docs": context_docs, "response": response}
