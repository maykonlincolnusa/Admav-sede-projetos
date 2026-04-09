from __future__ import annotations

from app.core.logging import get_logger


class CommunicationService:
    def __init__(self) -> None:
        self._logger = get_logger(self.__class__.__name__)

    async def send_message(self, *, phone: str, message: str, unit: str) -> dict[str, str]:
        self._logger.info("Mensagem enviada | unit=%s | phone=%s | body=%s", unit, phone, message)
        return {"phone": phone, "status": "sent", "unit": unit}
