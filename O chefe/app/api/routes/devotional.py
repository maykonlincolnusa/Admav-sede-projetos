from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_container
from app.schemas import DevotionalSendRequest, DevotionalSendResponse
from app.services.container import ServiceContainer

router = APIRouter(tags=["devotional"])


@router.post("/devotional/send", response_model=DevotionalSendResponse)
async def send_devotional(
    payload: DevotionalSendRequest,
    container: ServiceContainer = Depends(get_container),
) -> DevotionalSendResponse:
    try:
        deliveries = await container.devotional_service.send(payload.unit.value if payload.unit else None)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to send devotional: {exc}") from exc
    return DevotionalSendResponse.model_validate({"deliveries": deliveries})
