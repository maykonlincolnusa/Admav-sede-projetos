from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    message: str
    member_id: str | None
    member: dict[str, Any] | None
    unit: str | None
    intent: str
    response: str
    context_docs: list[dict[str, Any]]
    metadata: dict[str, Any]
