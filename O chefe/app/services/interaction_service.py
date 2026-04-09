from __future__ import annotations

from typing import Any

from app.db import InteractionRepository, MemberRepository


class InteractionService:
    def __init__(
        self,
        *,
        interaction_repository: InteractionRepository,
        member_repository: MemberRepository,
    ) -> None:
        self._interaction_repository = interaction_repository
        self._member_repository = member_repository

    async def register(
        self,
        *,
        member_id: str | None,
        message: str,
        response: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        interaction = await self._interaction_repository.create(
            member_id=member_id,
            message=message,
            response=response,
            metadata=metadata,
        )
        if member_id:
            await self._member_repository.append_interaction(
                member_id,
                {
                    "interaction_id": interaction["id"],
                    "message": message,
                    "response": response,
                    "timestamp": interaction["timestamp"],
                },
            )
        return interaction
