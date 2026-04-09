from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_container
from app.schemas import ChatRequest, ChatResponse
from app.services.container import ServiceContainer

router = APIRouter(tags=["chat"])

AGENT_NAME_BY_INTENT = {
    "cadastro": "CadastroAgent",
    "welcome": "WelcomeAgent",
    "devotional": "DevotionalAgent",
    "rag": "RAGAgent",
    "engagement": "EngagementAgent",
    "secretary": "SecretaryAgent",
}


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    container: ServiceContainer = Depends(get_container),
) -> ChatResponse:
    try:
        member = None
        if payload.member_id:
            member = await container.member_repository.get_by_id(payload.member_id)

        resolved_unit = container.unit_resolver_service.resolve(
            payload.message,
            payload.unit.value if payload.unit else None,
            member["unit"] if member else None,
        )
        if resolved_unit is None:
            response = container.unit_resolver_service.menu_text()
            await container.interaction_service.register(
                member_id=payload.member_id,
                message=payload.message,
                response=response,
                metadata={"agent": "OrchestratorAgent", "intent": "unit_selection"},
            )
            return ChatResponse(
                intent="unit_selection",
                agent="OrchestratorAgent",
                response=response,
                unit=None,
                context_docs=[],
            )

        if container.unit_resolver_service.is_unit_only_message(payload.message, resolved_unit):
            response = container.unit_resolver_service.confirmation_text(resolved_unit)
            await container.interaction_service.register(
                member_id=payload.member_id,
                message=payload.message,
                response=response,
                metadata={"agent": "OrchestratorAgent", "intent": "unit_confirmation", "unit": resolved_unit},
            )
            return ChatResponse(
                intent="unit_confirmation",
                agent="OrchestratorAgent",
                response=response,
                unit=resolved_unit,
                context_docs=[],
            )

        state = await container.orchestrator_service.route(
            {
                "message": payload.message,
                "member_id": payload.member_id,
                "unit": resolved_unit,
            }
        )
        await container.interaction_service.register(
            member_id=payload.member_id,
            message=payload.message,
            response=state["response"],
            metadata={"agent": state["intent"], "unit": state.get("unit")},
        )
        return ChatResponse(
            intent=state["intent"],
            agent=AGENT_NAME_BY_INTENT.get(state["intent"], "RAGAgent"),
            response=state["response"],
            unit=state.get("unit"),
            context_docs=[document["content"] for document in state.get("context_docs", [])],
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {exc}") from exc
