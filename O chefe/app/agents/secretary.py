from __future__ import annotations

from app.agents.base import AgentState
from app.services.llm_service import LLMService


class SecretaryAgent:
    name = "SecretaryAgent"

    def __init__(self, llm_service: LLMService) -> None:
        self._llm_service = llm_service

    async def __call__(self, state: AgentState) -> AgentState:
        context = "\n\n".join(document["content"] for document in state.get("context_docs", [])) or "Sem contexto."
        fallback = (
            "A secretaria pode responder com base na memória cadastrada da igreja. "
            "Treine a base RAG com horários, endereços e comunicados oficiais."
        )
        response = await self._llm_service.generate(
            system_prompt=(
                "Voce atua como secretaria da igreja, com respostas claras, formais e objetivas."
            ),
            human_prompt=f"Pergunta: {state['message']}\nContexto oficial:\n{context}",
            fallback=fallback,
        )
        return {**state, "response": response}
