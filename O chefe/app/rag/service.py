from __future__ import annotations

from datetime import datetime, timezone
from math import sqrt
from typing import Any

from app.config import Settings
from app.db import KnowledgeBaseRepository
from app.rag.embeddings import EmbeddingService


class RAGService:
    def __init__(
        self,
        *,
        settings: Settings,
        repository: KnowledgeBaseRepository,
        embedding_service: EmbeddingService,
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._embedding_service = embedding_service

    async def train(self, documents: list[dict[str, Any]]) -> int:
        contents = [document["content"] for document in documents]
        vectors = await self._embedding_service.embed_documents(contents)
        payloads: list[dict[str, Any]] = []
        for document, vector in zip(documents, vectors, strict=True):
            payloads.append(
                {
                    "type": document["type"],
                    "content": document["content"],
                    "embedding": vector,
                    "unit": document.get("unit"),
                    "created_at": datetime.now(timezone.utc),
                }
            )
        return await self._repository.insert_many(payloads)

    async def search(self, query: str, unit: str | None, limit: int | None = None) -> list[dict[str, Any]]:
        query_vector = await self._embedding_service.embed_query(query)
        candidates = await self._repository.find_candidates(unit)
        scored: list[dict[str, Any]] = []
        for candidate in candidates:
            embedding = candidate.get("embedding") or []
            if not embedding:
                continue
            score = self._cosine_similarity(query_vector, embedding)
            scored.append({**candidate, "score": score})
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[: limit or self._settings.default_search_k]

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        dot_product = sum(a * b for a, b in zip(left, right, strict=False))
        left_norm = sqrt(sum(value * value for value in left))
        right_norm = sqrt(sum(value * value for value in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot_product / (left_norm * right_norm)
