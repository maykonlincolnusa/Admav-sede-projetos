from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING

from app.config import Settings


def serialize_document(document: dict[str, Any] | None) -> dict[str, Any] | None:
    if document is None:
        return None
    serialized = dict(document)
    serialized["id"] = str(serialized.pop("_id"))
    return serialized


class MemberRepository:
    def __init__(self, database: AsyncIOMotorDatabase, settings: Settings) -> None:
        self._collection = database[settings.mongodb_members_collection]

    async def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        document = {
            **payload,
            "created_at": datetime.now(timezone.utc),
            "tags": payload.get("tags", []),
            "interactions": [],
        }
        result = await self._collection.insert_one(document)
        return await self.get_by_id(str(result.inserted_id))

    async def get_by_id(self, member_id: str) -> dict[str, Any] | None:
        if not ObjectId.is_valid(member_id):
            return None
        document = await self._collection.find_one({"_id": ObjectId(member_id)})
        return serialize_document(document)

    async def list_all(self) -> list[dict[str, Any]]:
        cursor = self._collection.find().sort("created_at", DESCENDING)
        return [serialize_document(document) async for document in cursor]

    async def list_by_unit(self, unit: str) -> list[dict[str, Any]]:
        cursor = self._collection.find({"unit": unit}).sort("created_at", DESCENDING)
        return [serialize_document(document) async for document in cursor]

    async def append_interaction(self, member_id: str, interaction: dict[str, Any]) -> None:
        if not ObjectId.is_valid(member_id):
            return
        await self._collection.update_one(
            {"_id": ObjectId(member_id)},
            {
                "$push": {
                    "interactions": {
                        "interaction_id": interaction["interaction_id"],
                        "message": interaction["message"],
                        "response": interaction["response"],
                        "timestamp": interaction["timestamp"],
                    }
                }
            },
        )


class KnowledgeBaseRepository:
    def __init__(self, database: AsyncIOMotorDatabase, settings: Settings) -> None:
        self._collection = database[settings.mongodb_knowledge_collection]

    async def insert_many(self, documents: list[dict[str, Any]]) -> int:
        if not documents:
            return 0
        result = await self._collection.insert_many(documents)
        return len(result.inserted_ids)

    async def find_candidates(self, unit: str | None = None) -> list[dict[str, Any]]:
        criteria: dict[str, Any] = {}
        if unit:
            criteria["$or"] = [{"unit": unit}, {"unit": None}, {"unit": ""}]
        cursor = self._collection.find(criteria).sort("created_at", DESCENDING)
        return [serialize_document(document) async for document in cursor]


class InteractionRepository:
    def __init__(self, database: AsyncIOMotorDatabase, settings: Settings) -> None:
        self._collection = database[settings.mongodb_interactions_collection]

    async def create(
        self,
        *,
        member_id: str | None,
        message: str,
        response: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        document = {
            "member_id": member_id,
            "message": message,
            "response": response,
            "timestamp": datetime.now(timezone.utc),
        }
        result = await self._collection.insert_one(document)
        created = await self._collection.find_one({"_id": result.inserted_id})
        return serialize_document(created)

    async def list_recent_by_member(self, member_id: str, limit: int = 5) -> list[dict[str, Any]]:
        cursor = self._collection.find({"member_id": member_id}).sort("timestamp", DESCENDING).limit(limit)
        return [serialize_document(document) async for document in cursor]
