from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import Settings
from app.core.logging import get_logger
from app.services.devotional_service import DevotionalService


class SchedulerManager:
    def __init__(self, *, settings: Settings, devotional_service: DevotionalService) -> None:
        self._logger = get_logger(self.__class__.__name__)
        self._settings = settings
        self._devotional_service = devotional_service
        self._scheduler = AsyncIOScheduler(timezone=settings.timezone)

    def start(self) -> None:
        if self._scheduler.running:
            return
        self._scheduler.add_job(
            self._run_devotional_job,
            CronTrigger(
                day_of_week=self._settings.scheduler_devotional_days,
                hour=self._settings.scheduler_devotional_hour,
                minute=self._settings.scheduler_devotional_minute,
            ),
            id="automatic-devotional",
            replace_existing=True,
        )
        self._scheduler.start()
        self._logger.info("Scheduler iniciado para devocionais automáticos.")

    def shutdown(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            self._logger.info("Scheduler finalizado.")

    async def _run_devotional_job(self) -> None:
        self._logger.info("Executando job automático de devocional.")
        await self._devotional_service.send()
