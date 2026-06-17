"""Deterministic HoloContext builder seam for HoloChat 4DNA."""

from __future__ import annotations

import hashlib
import json
import os
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
    context_budget: "ContextBudgetLedger"


class ContextBudgetRow(BaseModel):
    block_name: str
    included: bool
    char_count: int
    token_estimate: int
    source_type: str
    reason: str | None = None


class ContextBudgetLedger(BaseModel):
    rows: list[ContextBudgetRow] = Field(default_factory=list)
    total_chars: int = 0
    total_token_estimate: int = 0
    largest_blocks: list[dict[str, Any]] = Field(default_factory=list)
    budget_status: str = "not_measured"
    budget_limit_tokens: int | None = None


def estimate_context_tokens(text: str | None) -> int:
    char_count = len(text or "")
    if char_count == 0:
        return 0
    return (char_count + 3) // 4


def _budget_limit_from_env(budget_limit_tokens: int | None = None) -> int | None:
    if budget_limit_tokens is not None:
        return budget_limit_tokens if budget_limit_tokens > 0 else None
    raw = os.getenv("HOLOCHAT_CONTEXT_BUDGET_TOKENS", "").strip()
    if not raw:
        return None
    try:
        parsed = int(raw)
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def _budget_status(total_token_estimate: int, budget_limit_tokens: int | None) -> str:
    if total_token_estimate <= 0:
        return "not_measured"
    if budget_limit_tokens is None:
        return "within_budget"
    if total_token_estimate > budget_limit_tokens:
        return "over_budget"
    if total_token_estimate >= int(budget_limit_tokens * 0.8):
        return "near_budget"
    return "within_budget"


def build_context_budget_ledger(
    blocks: list[dict[str, Any]],
    *,
    budget_limit_tokens: int | None = None,
    largest_count: int = 3,
) -> ContextBudgetLedger:
    rows: list[ContextBudgetRow] = []
    for block in blocks:
        included = bool(block.get("included", True))
        content = str(block.get("content") or "") if included else ""
        char_count = len(content)
        rows.append(
            ContextBudgetRow(
                block_name=str(block.get("block_name", "unknown")),
                included=included,
                char_count=char_count,
                token_estimate=estimate_context_tokens(content),
                source_type=str(block.get("source_type", "unknown")),
                reason=block.get("reason"),
            )
        )

    total_chars = sum(row.char_count for row in rows)
    total_token_estimate = sum(row.token_estimate for row in rows)
    limit = _budget_limit_from_env(budget_limit_tokens)
    largest_blocks = [
        {
            "block_name": row.block_name,
            "source_type": row.source_type,
            "char_count": row.char_count,
            "token_estimate": row.token_estimate,
        }
        for row in sorted(
            (row for row in rows if row.included),
            key=lambda row: (row.token_estimate, row.char_count, row.block_name),
            reverse=True,
        )[:largest_count]
    ]

    return ContextBudgetLedger(
        rows=rows,
        total_chars=total_chars,
        total_token_estimate=total_token_estimate,
        largest_blocks=largest_blocks,
        budget_status=_budget_status(total_token_estimate, limit),
        budget_limit_tokens=limit,
    )


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
        state_block = self._state_block(holo_state)
        block_entries: list[dict[str, Any]] = [
            {
                "block_name": "base_system_prompt",
                "content": base_system_prompt.rstrip(),
                "included": True,
                "source_type": "system",
            },
            {
                "block_name": "holo_state",
                "content": state_block,
                "included": True,
                "source_type": "system",
            },
            {
                "block_name": "baton_pass",
                "content": "",
                "included": True,
                "source_type": "governor",
                "reason": "represented inside HoloState metadata",
            },
        ]
        blocks = [base_system_prompt.rstrip(), state_block]

        if route_decision:
            route_block = self._route_block(route_decision)
            blocks.append(route_block)
            included.append("route_decision")
            block_entries.append(
                {
                    "block_name": "route_decision",
                    "content": route_block,
                    "included": True,
                    "source_type": "governor",
                }
            )

        if recent_history:
            history_block = self._history_block(recent_history)
            blocks.append(history_block)
            included.append("recent_history")
            block_entries.append(
                {
                    "block_name": "recent_history",
                    "content": history_block,
                    "included": True,
                    "source_type": "history",
                }
            )
        else:
            block_entries.append(
                {
                    "block_name": "recent_history",
                    "content": "",
                    "included": False,
                    "source_type": "history",
                    "reason": "no recent history provided",
                }
            )

        if incognito:
            omitted.extend(["capsule_context", "life_context", "latest_consolidation"])
            block_entries.extend(
                [
                    {
                        "block_name": "capsule_context",
                        "content": "",
                        "included": False,
                        "source_type": "memory",
                        "reason": "incognito mode",
                    },
                    {
                        "block_name": "life_context",
                        "content": "",
                        "included": False,
                        "source_type": "memory",
                        "reason": "incognito mode",
                    },
                    {
                        "block_name": "latest_consolidation",
                        "content": "",
                        "included": False,
                        "source_type": "memory",
                        "reason": "incognito mode",
                    },
                ]
            )
        else:
            if life_context:
                life_context_block = self._life_context_block(life_context)
                blocks.append(life_context_block)
                included.append("life_context")
                block_entries.append(
                    {
                        "block_name": "life_context",
                        "content": life_context_block,
                        "included": True,
                        "source_type": "memory",
                    }
                )
            else:
                block_entries.append(
                    {
                        "block_name": "life_context",
                        "content": "",
                        "included": False,
                        "source_type": "memory",
                        "reason": "empty",
                    }
                )
            if latest_consolidation:
                latest_consolidation_block = self._latest_consolidation_block(latest_consolidation)
                blocks.append(latest_consolidation_block)
                included.append("latest_consolidation")
                block_entries.append(
                    {
                        "block_name": "latest_consolidation",
                        "content": latest_consolidation_block,
                        "included": True,
                        "source_type": "memory",
                    }
                )
            else:
                block_entries.append(
                    {
                        "block_name": "latest_consolidation",
                        "content": "",
                        "included": False,
                        "source_type": "memory",
                        "reason": "empty",
                    }
                )
            if capsule_context:
                capsule_context_block = self._capsule_context_block(capsule_context)
                blocks.append(capsule_context_block)
                included.append("capsule_context")
                block_entries.append(
                    {
                        "block_name": "capsule_context",
                        "content": capsule_context_block,
                        "included": True,
                        "source_type": "memory",
                    }
                )
            else:
                block_entries.append(
                    {
                        "block_name": "capsule_context",
                        "content": "",
                        "included": False,
                        "source_type": "memory",
                        "reason": "empty",
                    }
                )

        assembled_user = user_message
        block_entries.append(
            {
                "block_name": "user_message",
                "content": user_message,
                "included": True,
                "source_type": "user",
            }
        )
        if web_results:
            web_results_block = (
                "\n\n"
                "[BACKGROUND CONTEXT: The following HoloSearch results were retrieved "
                "to help answer. Use them silently if relevant.]\n\n"
                f"{web_results}"
            )
            assembled_user = (
                f"{user_message}"
                f"{web_results_block}"
            )
            included.append("web_results")
            block_entries.append(
                {
                    "block_name": "web_results",
                    "content": web_results_block,
                    "included": True,
                    "source_type": "search",
                }
            )
        else:
            omitted.append("web_results")
            block_entries.append(
                {
                    "block_name": "web_results",
                    "content": "",
                    "included": False,
                    "source_type": "search",
                    "reason": "no web results",
                }
            )

        system_prompt = "\n\n".join(block for block in blocks if block)
        char_count = len(system_prompt) + len(assembled_user)
        token_estimate = max(1, (char_count + 3) // 4)
        context_hash = stable_context_hash(system_prompt, assembled_user)
        context_budget = build_context_budget_ledger(block_entries)

        return ContextPacket(
            system_prompt=system_prompt,
            user_message=assembled_user,
            char_count=char_count,
            token_estimate=token_estimate,
            context_hash=context_hash,
            context_budget=context_budget,
            metadata={
                "included_blocks": included,
                "omitted_blocks": omitted,
                "incognito": incognito,
                "state_id": holo_state.state_id,
                "state_schema_version": holo_state.schema_version,
                "required_tools": [tool.value for tool in holo_state.required_tools],
                "context_budget": context_budget.model_dump(mode="json"),
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
