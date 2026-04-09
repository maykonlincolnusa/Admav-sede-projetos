from __future__ import annotations

import re

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.config import Settings


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model = self._build_model()

    def _build_model(self):
        provider = self._settings.llm_provider.lower()

        if provider == "google" and self._settings.google_api_key:
            return ChatGoogleGenerativeAI(
                google_api_key=self._settings.google_api_key,
                model=self._settings.google_chat_model,
                temperature=0.2,
            )

        if provider == "openai" and self._settings.openai_api_key:
            return ChatOpenAI(
                api_key=self._settings.openai_api_key,
                model=self._settings.openai_chat_model,
                temperature=0.2,
            )

        return None

    async def classify_intent(self, message: str) -> str:
        if self._model is None:
            return self._fallback_intent(message)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "Classifique a intencao da mensagem em apenas um destes rótulos: "
                        "cadastro, welcome, devotional, rag, engagement, secretary. "
                        "Retorne somente o rótulo."
                    ),
                ),
                ("human", "{message}"),
            ]
        )
        chain = prompt | self._model | StrOutputParser()
        response = (await chain.ainvoke({"message": message})).strip().lower()
        return response if response in {"cadastro", "welcome", "devotional", "rag", "engagement", "secretary"} else "rag"

    async def generate(self, *, system_prompt: str, human_prompt: str, fallback: str) -> str:
        if self._model is None:
            return fallback

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{human_prompt}"),
            ]
        )
        chain = prompt | self._model | StrOutputParser()
        result = await chain.ainvoke({"human_prompt": human_prompt})
        return result.strip() or fallback

    def _fallback_intent(self, message: str) -> str:
        normalized = re.sub(r"\s+", " ", message.lower()).strip()
        if any(token in normalized for token in ("cadastro", "registr", "membro novo")):
            return "cadastro"
        if any(token in normalized for token in ("boas-vindas", "bem-vindo", "recepc")):
            return "welcome"
        if any(token in normalized for token in ("devoc", "vers", "reflex", "prega")):
            return "devotional"
        if any(token in normalized for token in ("visita", "engaj", "acompanh", "sumiu", "retenc")):
            return "engagement"
        if any(token in normalized for token in ("secretaria", "documento", "culto", "horario", "agenda")):
            return "secretary"
        return "rag"
