from __future__ import annotations

import asyncio

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from app.config import Settings


class EmbeddingService:
    def __init__(self, settings: Settings) -> None:
        provider = settings.embedding_provider.lower()
        if provider == "google" and settings.google_api_key:
            self._embeddings = GoogleGenerativeAIEmbeddings(
                google_api_key=settings.google_api_key,
                model=settings.google_embedding_model,
            )
        elif provider == "openai" and settings.openai_api_key:
            self._embeddings = OpenAIEmbeddings(
                api_key=settings.openai_api_key,
                model=settings.openai_embedding_model,
            )
        else:
            self._embeddings = HuggingFaceEmbeddings(model_name=settings.huggingface_embedding_model)

    async def embed_query(self, text: str) -> list[float]:
        return await asyncio.to_thread(self._embeddings.embed_query, text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return await asyncio.to_thread(self._embeddings.embed_documents, texts)
