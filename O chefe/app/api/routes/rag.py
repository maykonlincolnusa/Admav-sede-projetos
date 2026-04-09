from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_container
from app.schemas import RagTrainRequest, RagTrainResponse
from app.services.container import ServiceContainer

router = APIRouter(tags=["rag"])


@router.post("/rag/train", response_model=RagTrainResponse)
async def train_rag(
    payload: RagTrainRequest,
    container: ServiceContainer = Depends(get_container),
) -> RagTrainResponse:
    try:
        inserted_count = await container.rag_service.train(
            [document.model_dump(mode="json") for document in payload.documents]
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to train RAG: {exc}") from exc
    return RagTrainResponse(inserted_count=inserted_count)
