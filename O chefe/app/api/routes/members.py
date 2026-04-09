from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_container
from app.schemas import MemberCreate, MemberRead
from app.services.container import ServiceContainer

router = APIRouter(tags=["members"])


@router.post("/members", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
async def create_member(
    payload: MemberCreate,
    container: ServiceContainer = Depends(get_container),
) -> MemberRead:
    try:
        member = await container.member_service.create_member(payload.model_dump(mode="json"))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to create member: {exc}") from exc
    return MemberRead.model_validate(member)


@router.get("/members", response_model=list[MemberRead])
async def list_members(container: ServiceContainer = Depends(get_container)) -> list[MemberRead]:
    members = await container.member_service.list_members()
    return [MemberRead.model_validate(member) for member in members]
