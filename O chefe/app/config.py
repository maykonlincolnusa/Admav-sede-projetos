from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants import DEFAULT_UNITS


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ADMAV AI CHURCH SYSTEM"
    app_env: str = "development"
    api_prefix: str = ""
    log_level: str = "INFO"
    timezone: str = "America/Sao_Paulo"
    expose_docs: bool = True
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "admav_ai_church"
    mongodb_members_collection: str = "members"
    mongodb_knowledge_collection: str = "knowledge_base"
    mongodb_interactions_collection: str = "interactions"

    llm_provider: str = "google"
    google_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GOOGLE_API_KEY", "GEMINI_API_KEY"),
    )
    google_chat_model: str = "gemini-2.5-flash"
    google_embedding_model: str = "gemini-embedding-001"

    openai_api_key: str | None = None
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_provider: str = "google"
    huggingface_embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    scheduler_devotional_days: str = "mon,wed,fri"
    scheduler_devotional_hour: int = 7
    scheduler_devotional_minute: int = 0
    default_search_k: int = 4

    church_units: list[str] = Field(default_factory=lambda: list(DEFAULT_UNITS))


@lru_cache
def get_settings() -> Settings:
    return Settings()
