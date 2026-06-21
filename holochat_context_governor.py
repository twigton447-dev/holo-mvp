"""Deterministic HoloChat Context Governor continuity helpers.

This layer maintains the durable HoloChat State Object. It does not call
providers and does not turn HoloChat into the HoloBuild artifact factory.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from typing import Any

from pydantic import ValidationError

from holo_state import BatonPass, GovArcState, HoloState, RequiredTools, StateAudit


HOLOCHAT_STATE_CONTEXT_KEY = "_holochat_state_object"
REQUIRED_STATE_FIELDS = (
    "USER_GOAL",
    "LATEST_INPUT_SUMMARY",
    "CRITICAL_CONSTRAINTS",
    "ROLLING_SUMMARY",
    "SETTLED_DECISIONS",
    "ARTIFACTS_REGISTRY",
    "REQUIRED_TOOLS",
    "BATON_PASS",
)
DEFAULT_RESEED_CHAR_LIMIT = 3600
DEFAULT_ROLLING_SUMMARY_LIMIT = 1800

_SECRET_ENV_RE = re.compile(
    r"\b([A-Z][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD)[A-Z0-9_]*)\s*=\s*([^\s,;]+)"
)
_SECRET_KV_RE = re.compile(
    r"(?i)\b(api[_-]?key|token|secret|password|authorization|bearer)\s*[:=]\s*([^\s,;]+)"
)
_OPENAI_STYLE_SECRET_RE = re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_\-=]{12,}")
_CONSTRAINT_TERMS = (
    "do not",
    "don't",
    "never",
    "must",
    "only",
    "no provider",
    "no push",
    "no app mutation",
    "stop after",
    "hard rule",
    "important scope",
    "without losing",
)
_DECISION_TERMS = (
    "approved",
    "safe to proceed",
    "created",
    "committed",
    "decided",
    "selected",
    "using",
)


def stable_hash(value: Any) -> str:
    if isinstance(value, str):
        payload = value
    else:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return max(1, int(raw))
    except ValueError:
        return default


def redact_secrets(value: Any) -> str:
    text = str(value or "")
    text = _SECRET_ENV_RE.sub(lambda match: f"{match.group(1)}=[REDACTED]", text)
    text = _SECRET_KV_RE.sub(lambda match: f"{match.group(1)}=[REDACTED]", text)
    return _OPENAI_STYLE_SECRET_RE.sub("[REDACTED_SECRET]", text)


def sanitize_text(value: Any, *, limit: int = 320) -> str:
    text = " ".join(redact_secrets(value).split())
    if len(text) > limit:
        return text[: max(0, limit - 3)].rstrip() + "..."
    return text


def _unique_compact(items: list[str], *, limit: int, item_limit: int = 240) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        compact = sanitize_text(item, limit=item_limit)
        if not compact:
            continue
        key = compact.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(compact)
        if len(out) >= limit:
            break
    return out


def extract_constraints(text: str) -> list[str]:
    candidates: list[str] = []
    for raw_line in str(text or "").splitlines():
        clean_line = raw_line.strip().lstrip("*-0123456789. ")
        for part in re.split(r"(?<=[.!?])\s+", clean_line):
            line = sanitize_text(part, limit=260)
            lowered = line.lower()
            if line and any(term in lowered for term in _CONSTRAINT_TERMS):
                candidates.append(line)
    return _unique_compact(candidates, limit=12)


def extract_settled_decisions(*texts: str) -> list[str]:
    candidates: list[str] = []
    for text in texts:
        for raw_line in str(text or "").splitlines():
            line = sanitize_text(raw_line.strip().lstrip("*-0123456789. "), limit=260)
            lowered = line.lower()
            if line and any(term in lowered for term in _DECISION_TERMS):
                candidates.append(line)
    return _unique_compact(candidates, limit=12)


def load_state_from_capsule_context(capsule_context: dict[str, Any] | None) -> HoloState | None:
    raw = (capsule_context or {}).get(HOLOCHAT_STATE_CONTEXT_KEY)
    if not raw:
        return None
    try:
        if isinstance(raw, str):
            return HoloState.model_validate_json(raw)
        return HoloState.model_validate(raw)
    except (ValidationError, ValueError, TypeError):
        return None


def state_context_value(state: HoloState) -> str:
    return state.model_dump_json()


def artifact_reference(artifact: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(artifact, dict):
        return None
    artifact_id = artifact.get("artifact_id") or artifact.get("id")
    path = artifact.get("path")
    content_hash = artifact.get("content_hash") or artifact.get("hash")
    if not artifact_id and not path and not content_hash:
        return None
    ref = {
        "artifact_id": sanitize_text(artifact_id, limit=120) or None,
        "path": sanitize_text(path, limit=260) or None,
        "hash": sanitize_text(content_hash, limit=96) or None,
        "title": sanitize_text(artifact.get("title"), limit=140) or None,
        "type": sanitize_text(artifact.get("type") or artifact.get("artifact_type"), limit=80) or None,
        "status": sanitize_text(artifact.get("status"), limit=80) or None,
    }
    if ref["artifact_id"] and not ref["status"]:
        ref["status"] = "available_by_id"
    return {key: value for key, value in ref.items() if value}


def merge_artifact_registry(
    previous: list[dict[str, Any]] | None,
    additions: list[dict[str, Any]] | None,
    *,
    limit: int = 30,
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in list(previous or []) + list(additions or []):
        ref = artifact_reference(item)
        if not ref:
            continue
        key = ref.get("artifact_id") or ref.get("path") or ref.get("hash") or json.dumps(ref, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        merged.append(ref)
        if len(merged) >= limit:
            break
    return merged


def should_auto_compact(
    *,
    context_budget: dict[str, Any] | None,
    thread_health_level: str,
    thread_health_score: int,
) -> bool:
    budget = context_budget or {}
    if str(budget.get("budget_status") or "").lower() in {"over_budget", "near_budget", "warning"}:
        return True
    limit = budget.get("budget_limit_tokens")
    estimate = budget.get("total_token_estimate")
    try:
        if limit and estimate and int(estimate) >= int(limit) * 0.8:
            return True
    except (TypeError, ValueError):
        pass
    return str(thread_health_level).upper() == "RED" or int(thread_health_score or 0) <= 20


def update_rolling_summary(
    previous_summary: str | None,
    *,
    latest_input_summary: str,
    response_summary: str | None = None,
    limit: int | None = None,
) -> str:
    char_limit = limit or _int_env("HOLOCHAT_ROLLING_SUMMARY_CHARS", DEFAULT_ROLLING_SUMMARY_LIMIT)
    parts = []
    previous = sanitize_text(previous_summary, limit=char_limit)
    if previous:
        parts.append(previous)
    latest = sanitize_text(latest_input_summary, limit=360)
    if latest:
        parts.append(f"Latest user turn: {latest}")
    response = sanitize_text(response_summary, limit=360)
    if response:
        parts.append(f"Latest Holo response: {response}")
    summary = " | ".join(parts)
    if len(summary) > char_limit:
        return summary[-char_limit:].lstrip(" |")
    return summary


def build_baton_pass(
    *,
    current_task: str | None,
    next_action: str | None,
    unresolved_tensions: list[str],
    artifact_registry: list[dict[str, Any]],
    constraints: list[str],
    required_tools: list[RequiredTools],
) -> BatonPass:
    artifact_ids = [
        ref["artifact_id"]
        for ref in artifact_registry
        if isinstance(ref, dict) and ref.get("artifact_id")
    ][:8]
    focus = [item for item in (current_task, next_action) if item]
    return BatonPass(
        current_task=sanitize_text(current_task, limit=240) or None,
        next_action=sanitize_text(next_action, limit=240) or None,
        focus_areas=_unique_compact(focus, limit=4),
        unresolved_tensions=_unique_compact(unresolved_tensions, limit=8),
        relevant_artifact_ids=artifact_ids,
        constraints_for_next_assistant=_unique_compact(constraints, limit=10),
        required_tools=required_tools,
        route_reason="holochat_context_governor_continuity",
        mode="serial",
    )


def build_holochat_state(
    *,
    session_id: str,
    turn_number: int,
    user_message: str,
    response_text: str | None = None,
    capsule_id: str | None = None,
    previous_state: HoloState | None = None,
    artifacts_saved: list[dict[str, Any]] | None = None,
    required_tools: list[RequiredTools] | None = None,
    gov_arc_state: GovArcState | None = None,
    thread_health_score: int = 100,
    thread_status: str | None = None,
    auto_compact: bool = False,
) -> HoloState:
    latest = sanitize_text(user_message, limit=360)
    previous_constraints = list(previous_state.critical_constraints if previous_state else [])
    constraints = _unique_compact(previous_constraints + extract_constraints(user_message), limit=14)
    previous_decisions = list(previous_state.settled_decisions if previous_state else [])
    settled = _unique_compact(
        previous_decisions + extract_settled_decisions(user_message, response_text or ""),
        limit=14,
    )
    registry = merge_artifact_registry(
        previous_state.artifact_registry if previous_state else [],
        artifacts_saved or [],
    )
    tools = required_tools or [RequiredTools.NONE]
    goal = previous_state.user_goal if previous_state else None
    lowered_latest = latest.lower()
    if not goal or "new lane" in lowered_latest or "new goal" in lowered_latest:
        goal = latest
    next_action = None
    if gov_arc_state and gov_arc_state.next_paths:
        next_action = gov_arc_state.next_paths[0]
    if not next_action:
        next_action = "Continue from the latest user request using the durable HoloChat state object."
    tensions = []
    if previous_state and previous_state.baton_pass.unresolved_tensions:
        tensions.extend(previous_state.baton_pass.unresolved_tensions)
    if gov_arc_state and gov_arc_state.current_tension:
        tensions.append(gov_arc_state.current_tension)
    baton = build_baton_pass(
        current_task=goal,
        next_action=next_action,
        unresolved_tensions=tensions,
        artifact_registry=registry,
        constraints=constraints,
        required_tools=tools,
    )
    rolling = update_rolling_summary(
        previous_state.rolling_summary if previous_state else None,
        latest_input_summary=latest,
        response_summary=response_text,
    )
    audit_note = "auto_compact_triggered" if auto_compact else "rolling_update"
    state = HoloState(
        session_id=session_id,
        capsule_id=capsule_id,
        turn_number=turn_number,
        user_goal=goal,
        latest_input_summary=latest,
        critical_constraints=constraints,
        rolling_summary=rolling,
        settled_decisions=settled,
        artifact_registry=registry,
        required_tools=tools,
        baton_pass=baton,
        gov_arc_state=gov_arc_state or (previous_state.gov_arc_state if previous_state else GovArcState(current_topic=latest)),
        thread_health=HoloState.from_chat_turn(
            session_id=session_id,
            capsule_id=capsule_id,
            turn_number=turn_number,
            user_message=user_message,
            thread_health_score=thread_health_score,
            thread_status=thread_status,
        ).thread_health,
    )
    reseed = generate_auto_reseed_payload(state)
    state.state_audit = audit_state_object(
        state,
        latest_user_input=user_message,
        reseed_payload=reseed,
        extra_notes=[audit_note],
    )
    return state


def generate_auto_reseed_payload(state: HoloState, *, max_chars: int | None = None) -> str:
    limit = max_chars or _int_env("HOLOCHAT_RESEED_MAX_CHARS", DEFAULT_RESEED_CHAR_LIMIT)
    canonical = state.canonical_object()
    canonical_for_hash = dict(canonical)
    canonical_for_hash.pop("STATE_AUDIT", None)
    baton = canonical.get("BATON_PASS") or {}
    artifacts = canonical.get("ARTIFACTS_REGISTRY") or []
    lines = [
        "HOLOCHAT AUTO-RESEED (private continuity context; do not surface unless asked):",
        f"  state_id: {state.state_id}",
        f"  user_goal: {sanitize_text(canonical.get('USER_GOAL'), limit=260)}",
        f"  latest_input_summary: {sanitize_text(canonical.get('LATEST_INPUT_SUMMARY'), limit=260)}",
        f"  rolling_summary: {sanitize_text(canonical.get('ROLLING_SUMMARY'), limit=900)}",
        "  critical_constraints:",
    ]
    constraints = canonical.get("CRITICAL_CONSTRAINTS") or []
    lines.extend(f"    - {sanitize_text(item, limit=220)}" for item in constraints[:8])
    if not constraints:
        lines.append("    - None captured.")
    lines.append("  settled_decisions:")
    settled = canonical.get("SETTLED_DECISIONS") or []
    lines.extend(f"    - {sanitize_text(item, limit=220)}" for item in settled[:8])
    if not settled:
        lines.append("    - None captured.")
    lines.append("  active_artifacts:")
    for artifact in artifacts[:8]:
        label = artifact.get("artifact_id") or artifact.get("path") or artifact.get("hash")
        title = artifact.get("title")
        status = artifact.get("status", "referenced")
        lines.append(f"    - {sanitize_text(label, limit=120)} | {sanitize_text(title, limit=120)} | {status}")
    if not artifacts:
        lines.append("    - None captured.")
    lines.extend(
        [
            "  baton_pass:",
            f"    current_task: {sanitize_text(baton.get('current_task'), limit=240)}",
            f"    next_action: {sanitize_text(baton.get('next_action'), limit=240)}",
        ]
    )
    tensions = baton.get("unresolved_tensions") or []
    if tensions:
        lines.append("    unresolved_tensions:")
        lines.extend(f"      - {sanitize_text(item, limit=220)}" for item in tensions[:6])
    if baton.get("relevant_artifact_ids"):
        lines.append("    relevant_artifact_ids:")
        lines.extend(f"      - {sanitize_text(item, limit=120)}" for item in baton["relevant_artifact_ids"][:8])
    lines.append("  instruction: Continue from this structured state. Retrieve scoped artifacts by ID only when needed.")
    payload = redact_secrets("\n".join(lines))
    if len(payload) > limit:
        payload = payload[: max(0, limit - 80)].rstrip() + "\n  [truncated: reseed exceeded configured limit]"
    return payload


def audit_state_object(
    state: HoloState,
    *,
    latest_user_input: str | None = None,
    reseed_payload: str | None = None,
    extra_notes: list[str] | None = None,
) -> StateAudit:
    canonical = state.canonical_object()
    canonical_for_hash = dict(canonical)
    canonical_for_hash.pop("STATE_AUDIT", None)
    missing = [field for field in REQUIRED_STATE_FIELDS if field not in canonical]
    artifact_refs = canonical.get("ARTIFACTS_REGISTRY") or []
    missing_refs = [
        json.dumps(ref, sort_keys=True)
        for ref in artifact_refs
        if isinstance(ref, dict) and not (ref.get("artifact_id") or ref.get("path") or ref.get("hash"))
    ]
    reseed = reseed_payload or generate_auto_reseed_payload(state)
    contradiction_warnings: list[str] = []
    latest = sanitize_text(latest_user_input, limit=220).lower()
    if latest and ("new lane" in latest or "new goal" in latest):
        goal = sanitize_text(canonical.get("USER_GOAL"), limit=220).lower()
        if goal and latest[:80] not in goal:
            contradiction_warnings.append("latest_user_intent_may_override_stored_goal")
    overlarge = len(reseed) > _int_env("HOLOCHAT_RESEED_MAX_CHARS", DEFAULT_RESEED_CHAR_LIMIT)
    trusted = not (missing or missing_refs or overlarge)
    notes = list(extra_notes or [])
    if missing:
        notes.append("missing_required_fields")
    if overlarge:
        notes.append("overlarge_reseed")
    if contradiction_warnings:
        notes.append("latest_user_intent_review_needed")
    return StateAudit(
        trusted=trusted,
        critical_constraints_preserved=bool(canonical.get("CRITICAL_CONSTRAINTS") is not None),
        pinned_artifacts_preserved=not missing_refs,
        settled_decisions_preserved=bool(canonical.get("SETTLED_DECISIONS") is not None),
        missing_required_fields=missing,
        overlarge_reseed=overlarge,
        missing_artifact_references=missing_refs,
        contradiction_warnings=contradiction_warnings,
        state_hash=stable_hash(canonical_for_hash),
        summary_hash=stable_hash(canonical.get("ROLLING_SUMMARY") or ""),
        baton_hash=stable_hash(canonical.get("BATON_PASS") or {}),
        artifact_registry_hash=stable_hash(artifact_refs),
        reseed_hash=stable_hash(reseed),
        reseed_chars=len(reseed),
        notes=notes,
    )


def audit_canonical_state_object(state_object: dict[str, Any]) -> StateAudit:
    missing = [field for field in REQUIRED_STATE_FIELDS if field not in (state_object or {})]
    trusted = not missing
    state_for_hash = dict(state_object or {})
    state_for_hash.pop("STATE_AUDIT", None)
    return StateAudit(
        trusted=trusted,
        missing_required_fields=missing,
        state_hash=stable_hash(state_for_hash),
        summary_hash=stable_hash((state_object or {}).get("ROLLING_SUMMARY") or ""),
        baton_hash=stable_hash((state_object or {}).get("BATON_PASS") or {}),
        artifact_registry_hash=stable_hash((state_object or {}).get("ARTIFACTS_REGISTRY") or []),
        notes=["missing_required_fields"] if missing else [],
    )
