from __future__ import annotations

from app.agents.welcome import WelcomeAgent
from app.db import MemberRepository
from app.services.communication_service import CommunicationService
from app.services.interaction_service import InteractionService


class MemberService:
    def __init__(
        self,
        *,
        member_repository: MemberRepository,
        welcome_agent: WelcomeAgent,
        communication_service: CommunicationService,
        interaction_service: InteractionService,
    ) -> None:
        self._member_repository = member_repository
        self._welcome_agent = welcome_agent
        self._communication_service = communication_service
        self._interaction_service = interaction_service

    async def create_member(self, payload: dict[str, object]) -> dict[str, object]:
        member = await self._member_repository.create(payload)
        welcome_message = await self._welcome_agent.compose_message(
            member_name=str(member["name"]),
            unit=str(member["unit"]),
        )
        await self._communication_service.send_message(
            phone=str(member["phone"]),
            message=welcome_message,
            unit=str(member["unit"]),
        )
        await self._interaction_service.register(
            member_id=str(member["id"]),
            message="AUTO_WELCOME",
            response=welcome_message,
            metadata={"agent": "WelcomeAgent"},
        )
        refreshed_member = await self._member_repository.get_by_id(str(member["id"]))
        return refreshed_member or member

    async def list_members(self) -> list[dict[str, object]]:
        return await self._member_repository.list_all()
