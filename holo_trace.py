"""Safe HoloTrace metadata records for HoloChat 4DNA."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


SECRET_MARKERS = ("api_key", "apikey", "authorization", "bearer", "password", "secret", "token")


def stable_context_hash(system_prompt: str, user_message: str) -> str:
    payload = json.dumps(
        {"system_prompt": system_prompt, "user_message": user_message},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def redact_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if any(marker in lowered for marker in SECRET_MARKERS):
                redacted[str(key)] = "[REDACTED]"
            else:
                redacted[str(key)] = redact_secrets(item)
        return redacted
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    if isinstance(value, str) and any(marker in value.lower() for marker in SECRET_MARKERS):
        return "[REDACTED]"
    return value


class HoloTraceRecord(BaseModel):
    session_id: str
    turn_number: int
    holo_state_id: str
    holo_state_schema_version: str
    dna_profile: str
    shadow_route: bool = False
    runtime_analyst_provider: str | None = None
    runtime_analyst_model: str | None = None
    selected_council_provider: str
    selected_council_model: str
    selected_hologov_provider: str
    selected_hologov_model: str
    assigned_role: str
    route_reason: str
    searched: bool = False
    search_query: str | None = None
    thread_health: dict[str, Any] = Field(default_factory=dict)
    memory_extraction_attempted: bool = False
    memory_writes_count: int = 0
    context_packet_hash: str
    context_blocks: list[str] = Field(default_factory=list)
    fallback_used: bool = False
    fallback_reason: str | None = None
    dna_degraded: bool = False
    extra_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def safe_dict(self) -> dict[str, Any]:
        return redact_secrets(self.model_dump(mode="json"))

    def to_json(self) -> str:
        return json.dumps(self.safe_dict(), sort_keys=True, separators=(",", ":"))


class HoloSearchTraceRecord(BaseModel):
    session_id: str
    turn_number: int
    query: str
    provider: str = "tavily"
    message_id: str | None = None
    result_count: int = 0
    compact_result_summary: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def log_trace(record: HoloTraceRecord, logger: logging.Logger | None = None) -> None:
    sink = logger or logging.getLogger("holo.trace")
    sink.info("holochat_trace=%s", record.to_json())


def save_search_trace(persistence: Any, record: HoloSearchTraceRecord) -> bool:
    """Persist search trace when a compatible seam exists; otherwise no-op."""
    if persistence is None:
        return False
    if hasattr(persistence, "save_search_trace"):
        persistence.save_search_trace(record.model_dump(mode="json"))
        return True
    client = getattr(persistence, "_client", None)
    if client is None:
        return False
    try:
        client.table("holo_search_traces").insert(record.model_dump(mode="json")).execute()
        return True
    except Exception:
        logging.getLogger("holo.trace").debug("HoloSearch trace persistence unavailable", exc_info=True)
        return False
