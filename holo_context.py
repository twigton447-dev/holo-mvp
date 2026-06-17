"""Deterministic HoloContext builder seam for HoloChat 4DNA."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, Field

from holo_router import RouteDecision
from holo_state import HoloState


class ContextPacket(BaseModel):
    system_prompt: str
    user_message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    char_count: int
    token_estimate: int
    context_hash: str


def stable_context_hash(system_prompt: str, user_message: str) -> str:
    payload = json.dumps(
        {"system_prompt": system_prompt, "user_message": user_message},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class HoloContextBuilder:
    """Builds one model-facing packet for the selected council model."""

    def build(
        self,
        *,
        base_system_prompt: str,
        holo_state: HoloState,
        user_message: str,
        route_decision: RouteDecision | None = None,
        capsule_context: dict[str, str] | None = None,
        life_context: list[dict[str, Any]] | None = None,
        latest_consolidation: dict[str, Any] | None = None,
        recent_history: list[dict[str, str]] | None = None,
        web_results: str | None = None,
        incognito: bool = False,
    ) -> ContextPacket:
        included: list[str] = ["base_system_prompt", "holo_state", "baton_pass"]
        omitted: list[str] = []
        blocks = [base_system_prompt.rstrip(), self._state_block(holo_state)]

        if route_decision:
            blocks.append(self._route_block(route_decision))
            included.append("route_decision")

        if recent_history:
            blocks.append(self._history_block(recent_history))
            included.append("recent_history")

        if incognito:
            omitted.extend(["capsule_context", "life_context", "latest_consolidation"])
        else:
            if life_context:
                blocks.append(self._life_context_block(life_context))
                included.append("life_context")
            if latest_consolidation:
                blocks.append(self._latest_consolidation_block(latest_consolidation))
                included.append("latest_consolidation")
            if capsule_context:
                blocks.append(self._capsule_context_block(capsule_context))
                included.append("capsule_context")

        assembled_user = user_message
        if web_results:
            assembled_user = (
                f"{user_message}\n\n"
                "[BACKGROUND CONTEXT: The following HoloSearch results were retrieved "
                "to help answer. Use them silently if relevant.]\n\n"
                f"{web_results}"
            )
            included.append("web_results")
        else:
            omitted.append("web_results")

        system_prompt = "\n\n".join(block for block in blocks if block)
        char_count = len(system_prompt) + len(assembled_user)
        token_estimate = max(1, (char_count + 3) // 4)
        context_hash = stable_context_hash(system_prompt, assembled_user)

        return ContextPacket(
            system_prompt=system_prompt,
            user_message=assembled_user,
            char_count=char_count,
            token_estimate=token_estimate,
            context_hash=context_hash,
            metadata={
                "included_blocks": included,
                "omitted_blocks": omitted,
                "incognito": incognito,
                "state_id": holo_state.state_id,
                "state_schema_version": holo_state.schema_version,
                "required_tools": [tool.value for tool in holo_state.required_tools],
            },
        )

    @staticmethod
    def _state_block(holo_state: HoloState) -> str:
        data = holo_state.model_dump(mode="json")
        compact = {
            "schema_version": data["schema_version"],
            "state_id": data["state_id"],
            "session_id": data["session_id"],
            "turn_number": data["turn_number"],
            "user_goal": data.get("user_goal"),
            "latest_input_summary": data.get("latest_input_summary"),
            "critical_constraints": data.get("critical_constraints", []),
            "rolling_summary": data.get("rolling_summary"),
            "settled_decisions": data.get("settled_decisions", []),
            "artifact_registry": data.get("artifact_registry", []),
            "required_tools": data.get("required_tools", []),
            "thread_health": data.get("thread_health"),
            "state_audit": data.get("state_audit"),
        }
        return "HOLOSTATE v0.1:\n" + json.dumps(compact, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _route_block(route_decision: RouteDecision) -> str:
        return "\n".join(
            [
                "HOLOCOUNCIL ROUTE:",
                f"  assigned_role: {route_decision.assigned_role}",
                f"  council: {route_decision.council_provider}/{route_decision.council_model}",
                f"  HoloGov: {route_decision.hologov_provider}/{route_decision.hologov_model}",
                f"  route_reason: {route_decision.route_reason}",
                "  mode: serial_one_model_at_a_time",
            ]
        )

    @staticmethod
    def _history_block(history: list[dict[str, str]]) -> str:
        lines = ["RECENT SESSION HISTORY:"]
        for message in history[-8:]:
            role = message.get("role", "unknown").upper()
            content = " ".join(str(message.get("content", "")).split())
            lines.append(f"  {role}: {content[:500]}")
        return "\n".join(lines)

    @staticmethod
    def _life_context_block(entries: list[dict[str, Any]]) -> str:
        lines = ["HOLOBRAIN LIFE CONTEXT:"]
        for entry in entries:
            category = entry.get("category", "patterns")
            key = entry.get("key", "")
            value = entry.get("value", "")
            lines.append(f"  [{category}] {key}: {value}")
        return "\n".join(lines)

    @staticmethod
    def _latest_consolidation_block(note: dict[str, Any]) -> str:
        return "HOLOBRAIN LATEST CONSOLIDATION:\n" + json.dumps(
            note,
            sort_keys=True,
            separators=(",", ":"),
        )

    @staticmethod
    def _capsule_context_block(context: dict[str, str]) -> str:
        lines = ["HOLOBRAIN WORKING MEMORY:"]
        for key, value in sorted(context.items()):
            if key.startswith("_"):
                continue
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)
