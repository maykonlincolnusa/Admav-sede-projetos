from __future__ import annotations

from app.agents.devotional import DevotionalAgent
from app.constants import DEFAULT_UNITS
from app.db import MemberRepository
from app.services.communication_service import CommunicationService
from app.services.interaction_service import InteractionService


class DevotionalService:
    def __init__(
        self,
        *,
        devotional_agent: DevotionalAgent,
        member_repository: MemberRepository,
        communication_service: CommunicationService,
        interaction_service: InteractionService,
    ) -> None:
        self._devotional_agent = devotional_agent
        self._member_repository = member_repository
        self._communication_service = communication_service
        self._interaction_service = interaction_service

    async def send(self, unit: str | None = None) -> list[dict[str, object]]:
        units = [unit] if unit else list(DEFAULT_UNITS)
        deliveries: list[dict[str, object]] = []
        for current_unit in units:
            content = await self._devotional_agent.compose(current_unit)
            members = await self._member_repository.list_by_unit(current_unit)
            for member in members:
                await self._communication_service.send_message(
                    phone=str(member["phone"]),
                    message=content,
                    unit=current_unit,
                )
                await self._interaction_service.register(
                    member_id=str(member["id"]),
                    message="AUTO_DEVOTIONAL",
                    response=content,
                    metadata={"agent": "DevotionalAgent", "unit": current_unit},
                )
            deliveries.append(
                {
                    "unit": current_unit,
                    "recipients": len(members),
                    "content": content,
                }
            )
        return deliveries
