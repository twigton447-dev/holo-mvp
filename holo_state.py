"""Canonical HoloChat 4DNA state objects.

This module is intentionally runtime-isolated. It defines the v0.1 HoloState
shape without taking ownership of chat execution, memory persistence, or model
calls. Existing storage remains physically backed by project_brain.py for now;
new architecture code should refer to that surface as HoloBrain.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


SCHEMA_VERSION = "holochat_state_v0.1"


class RequiredTools(str, Enum):
    NONE = "NONE"
    WEB_SEARCH = "WEB_SEARCH"
    INTERNAL_SEARCH = "INTERNAL_SEARCH"


class CouncilRole(str, Enum):
    DIRECT_SYNTHESIS = "DIRECT_SYNTHESIS"
    ASSUMPTION_ATTACK = "ASSUMPTION_ATTACK"
    EVIDENCE_PRESSURE = "EVIDENCE_PRESSURE"
    EDGE_CASE_SCAN = "EDGE_CASE_SCAN"
    ACTIONABILITY_AUDIT = "ACTIONABILITY_AUDIT"
    SYNTHESIS = "SYNTHESIS"


class BatonPass(BaseModel):
    next_model_policy: str = "serial_one_model_at_a_time"
    assigned_role: CouncilRole = CouncilRole.DIRECT_SYNTHESIS
    focus_areas: list[str] = Field(default_factory=list)
    unresolved_tensions: list[str] = Field(default_factory=list)
    required_tools: list[RequiredTools] = Field(default_factory=lambda: [RequiredTools.NONE])
    route_reason: str = "default_direct_synthesis"
    mode: str = "serial"

    @field_validator("required_tools")
    @classmethod
    def _normalize_required_tools(cls, value: list[RequiredTools]) -> list[RequiredTools]:
        if not value:
            return [RequiredTools.NONE]
        if RequiredTools.NONE in value and len(value) > 1:
            return [tool for tool in value if tool != RequiredTools.NONE]
        return value


class ThreadHealth(BaseModel):
    score: int = Field(default=100, ge=0, le=100)
    level: str = "GREEN"
    status: str = "HEALTHY"
    reasons: list[str] = Field(default_factory=list)

    @classmethod
    def from_score(
        cls,
        score: int,
        *,
        status: str | None = None,
        reasons: list[str] | None = None,
    ) -> "ThreadHealth":
        if score >= 61:
            level = "GREEN"
            inferred_status = "HEALTHY"
        elif score >= 21:
            level = "YELLOW"
            inferred_status = "CLEANUP_RECOMMENDED"
        else:
            level = "RED"
            inferred_status = "ROTATION_RECOMMENDED"
        return cls(
            score=score,
            level=level,
            status=status or inferred_status,
            reasons=list(reasons or []),
        )


class StateAudit(BaseModel):
    critical_constraints_preserved: bool = True
    pinned_artifacts_preserved: bool = True
    settled_decisions_preserved: bool = True
    notes: list[str] = Field(default_factory=list)


class HoloState(BaseModel):
    schema_version: str = SCHEMA_VERSION
    state_id: str = Field(default_factory=lambda: f"hstate_{uuid4().hex}")
    session_id: str
    capsule_id: str | None = None
    turn_number: int = Field(default=0, ge=0)
    user_goal: str | None = None
    latest_input_summary: str | None = None
    critical_constraints: list[str] = Field(default_factory=list)
    rolling_summary: str | None = None
    settled_decisions: list[str] = Field(default_factory=list)
    artifact_registry: list[dict[str, Any]] = Field(default_factory=list)
    required_tools: list[RequiredTools] = Field(default_factory=lambda: [RequiredTools.NONE])
    baton_pass: BatonPass = Field(default_factory=BatonPass)
    thread_health: ThreadHealth = Field(default_factory=ThreadHealth)
    memory_candidates: list[dict[str, Any]] = Field(default_factory=list)
    state_audit: StateAudit = Field(default_factory=StateAudit)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("required_tools")
    @classmethod
    def _normalize_required_tools(cls, value: list[RequiredTools]) -> list[RequiredTools]:
        if not value:
            return [RequiredTools.NONE]
        if RequiredTools.NONE in value and len(value) > 1:
            return [tool for tool in value if tool != RequiredTools.NONE]
        return value

    @classmethod
    def from_chat_turn(
        cls,
        *,
        session_id: str,
        turn_number: int,
        user_message: str,
        capsule_id: str | None = None,
        thread_health_score: int = 100,
        thread_status: str | None = None,
        required_tools: list[RequiredTools] | None = None,
        baton_pass: BatonPass | None = None,
    ) -> "HoloState":
        summary = " ".join(user_message.strip().split())
        if len(summary) > 240:
            summary = summary[:237].rstrip() + "..."
        tools = required_tools or [RequiredTools.NONE]
        baton = baton_pass or BatonPass(required_tools=tools)
        return cls(
            session_id=session_id,
            capsule_id=capsule_id,
            turn_number=turn_number,
            latest_input_summary=summary or None,
            required_tools=tools,
            baton_pass=baton,
            thread_health=ThreadHealth.from_score(
                thread_health_score,
                status=thread_status,
                reasons=["imported_from_existing_chat_thread_health"],
            ),
        )
