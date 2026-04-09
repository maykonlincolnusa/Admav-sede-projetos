from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.constants import DEFAULT_UNITS


class ChurchUnit(str, Enum):
    admav_sede = DEFAULT_UNITS[0]
    admav_freguesia = DEFAULT_UNITS[1]
    admav_colonia = DEFAULT_UNITS[2]
    mav_recreio = DEFAULT_UNITS[3]
    admav_campo_grande = DEFAULT_UNITS[4]
    admav_praca_seca = DEFAULT_UNITS[5]


class InteractionSnippet(BaseModel):
    interaction_id: str | None = None
    message: str
    response: str
    timestamp: datetime


class MemberCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=8, max_length=30)
    email: EmailStr | None = None
    birth_date: date | None = None
    marital_status: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=200)
    unit: ChurchUnit
    tags: list[str] = Field(default_factory=list)


class MemberRead(BaseModel):
    id: str
    name: str
    phone: str
    email: EmailStr | None = None
    birth_date: date | None = None
    marital_status: str | None = None
    address: str | None = None
    unit: str
    created_at: datetime
    tags: list[str] = Field(default_factory=list)
    interactions: list[InteractionSnippet] = Field(default_factory=list)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=4000)
    member_id: str | None = None
    unit: ChurchUnit | None = None


class ChatResponse(BaseModel):
    intent: str
    agent: str
    response: str
    unit: str | None = None
    context_docs: list[str] = Field(default_factory=list)


class KnowledgeDocumentIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(min_length=2, max_length=50)
    content: str = Field(min_length=5, max_length=10000)
    unit: ChurchUnit | None = None


class RagTrainRequest(BaseModel):
    documents: list[KnowledgeDocumentIn] = Field(min_length=1)


class RagTrainResponse(BaseModel):
    inserted_count: int


class DevotionalSendRequest(BaseModel):
    unit: ChurchUnit | None = None


class DevotionalDelivery(BaseModel):
    unit: str
    recipients: int
    content: str


class DevotionalSendResponse(BaseModel):
    deliveries: list[DevotionalDelivery]


class HealthResponse(BaseModel):
    status: str
    app: str
