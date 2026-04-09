from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import Settings


class MongoManager:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = AsyncIOMotorClient(settings.mongodb_uri)
        self._database = self._client[settings.mongodb_database]

    @property
    def database(self) -> AsyncIOMotorDatabase:
        return self._database

    async def ping(self) -> None:
        await self._database.command("ping")

    async def close(self) -> None:
        self._client.close()
