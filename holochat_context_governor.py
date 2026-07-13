"""Deterministic HoloChat Context Governor continuity helpers.

This layer maintains the durable HoloChat State Object. It does not call
providers and does not turn HoloChat into the HoloBuild artifact factory.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import ValidationError

from holochat_constitution import HOLOCHAT_CONSTITUTIONAL_TONE_LAW, HOLOCHAT_OPERATING_OBJECTIVE
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
DEFAULT_HOLOBRAIN_INJECTION_CHAR_LIMIT = 2400


class HoloBrainInjectionMode(str, Enum):
    NONE = "NONE"
    HASHES_ONLY = "HASHES_ONLY"
    ARTIFACT_REFS = "ARTIFACT_REFS"
    BATON_ONLY = "BATON_ONLY"
    ROLLING_SUMMARY = "ROLLING_SUMMARY"
    FULL_RESEED = "FULL_RESEED"


@dataclass(frozen=True)
class HoloBrainInjectionPlan:
    mode: HoloBrainInjectionMode
    payload: str
    reason: str
    state_hash: str | None = None
    char_count: int = 0
    token_estimate: int = 0


@dataclass(frozen=True)
class GovAdvisorAdmission:
    admitted: bool
    value: Any = None
    reason: str = ""
    repaired: bool = False
    blocked_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class GovTurnPolicy:
    tier: str
    reasons: tuple[str, ...]
    advisor_allowed: bool
    fallback_allowed: bool


@dataclass(frozen=True)
class GovTurnPlan:
    turn_id: str
    user_id: str | None
    route: str
    visible_worker_role: str
    worker_provider_selection: dict[str, Any]
    advisor_provider_selection: dict[str, Any]
    intelligence_tier: str
    selected_context_ids: tuple[str, ...]
    dropped_context_ids: tuple[str, ...]
    context_drop_reasons: dict[str, str]
    memory_admissions: tuple[dict[str, Any], ...]
    memory_rejections: tuple[dict[str, Any], ...]
    artifact_refs: tuple[dict[str, Any], ...]
    pinned_artifacts: tuple[dict[str, Any], ...]
    tool_authorization: dict[str, Any]
    search_authorization: dict[str, Any]
    voice_tone_constraints: tuple[str, ...]
    persona_identity_constraints: tuple[str, ...]
    contradiction_repairs: tuple[dict[str, Any], ...]
    state_corrections: tuple[dict[str, Any], ...]
    fallback_eligibility: dict[str, Any]
    release_constraints: tuple[str, ...]
    worker_prompt_baton: str
    telemetry: dict[str, Any]
    kernel_validation_result: dict[str, Any]

    def model_dump(self) -> dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "user_id": self.user_id,
            "route": self.route,
            "visible_worker_role": self.visible_worker_role,
            "worker_provider_selection": self.worker_provider_selection,
            "advisor_provider_selection": self.advisor_provider_selection,
            "intelligence_tier": self.intelligence_tier,
            "selected_context_ids": list(self.selected_context_ids),
            "dropped_context_ids": list(self.dropped_context_ids),
            "context_drop_reasons": self.context_drop_reasons,
            "memory_admissions": list(self.memory_admissions),
            "memory_rejections": list(self.memory_rejections),
            "artifact_refs": list(self.artifact_refs),
            "pinned_artifacts": list(self.pinned_artifacts),
            "tool_authorization": self.tool_authorization,
            "search_authorization": self.search_authorization,
            "voice_tone_constraints": list(self.voice_tone_constraints),
            "persona_identity_constraints": list(self.persona_identity_constraints),
            "contradiction_repairs": list(self.contradiction_repairs),
            "state_corrections": list(self.state_corrections),
            "fallback_eligibility": self.fallback_eligibility,
            "release_constraints": list(self.release_constraints),
            "worker_prompt_baton": self.worker_prompt_baton,
            "telemetry": self.telemetry,
            "kernel_validation_result": self.kernel_validation_result,
        }


@dataclass(frozen=True)
class GovVisibleReleaseDecision:
    release: bool
    text: str
    reason: str
    repaired: bool = False


FALLBACK_ONLY_ADVISOR_PROVIDERS = {"minimax"}
_RUPTURE_RE = re.compile(
    r"(?i)\b("
    r"you sound cold|sound cold|you sound like a dick|acting like a dick|"
    r"not acting right|not like you|too sterile|too robotic|you are scolding|"
    r"that was curt|you feel off|you lost the thread"
    r")\b"
)
_SCOLDING_DIRECTIVE_RE = re.compile(
    r"(?i)\b("
    r"scold|gotcha|sterile|curt|cold|lecture|punish|shame|dismiss|"
    r"prosecute|cross-examine|corner|humiliate|patronize|condescend|"
    r"call (?:him|her|them|the user|the person) out|be harsh|make (?:him|her|them|the user|the person) admit"
    r")\b"
)
_HOSTILE_POSTURE_RE = re.compile(
    r"(?i)("
    r"\byou (?:clearly|obviously|just) (?:failed|ignored|refused|don't understand)\b|"
    r"\bthis is on you\b|"
    r"\byou need to admit\b|"
    r"\bface the consequence\b|"
    r"\bmake (?:him|her|them|the user|the person) look at it\b|"
    r"\bstop making excuses\b|"
    r"\byou are being\b"
    r")"
)
_VISIBLE_HOSTILE_POSTURE_RE = re.compile(
    r"(?i)("
    r"\byou (?:clearly|obviously|just) (?:failed|ignored|refused|don't understand)\b|"
    r"\bthis is on you\b|"
    r"\byou need to admit\b|"
    r"\bface the consequence\b|"
    r"\bmake (?:him|her|them|the user|the person) look at it\b|"
    r"\bstop making excuses\b|"
    r"\byou(?:'re| are)(?: being)? (?:ridiculous|evasive|lazy|dishonest|irrational|manipulative)\b|"
    r"\b(?:let me|i will|i am going to|i'm going to) "
    r"(?:scold|lecture|punish|shame|cross-examine|corner|humiliate|patronize|condescend)\b"
    r")"
)
_HIGH_TIER_RE = re.compile(
    r"(?i)\b("
    r"safety|unsafe|harm|medical|legal|financial|crisis|emergency|credential|"
    r"password|secret|api key|memory|remember|forget|persona|voice|relationship|"
    r"you sound|not acting right|tool|search|send|delete|deploy|purchase|pay|"
    r"provider|governor|state|conflict|uncertain|product critical"
    r")\b"
)
_LOW_TIER_RE = re.compile(r"(?i)^\s*(hi|hey|thanks|thank you|ok|okay|lol|nice)\s*[.!?]*\s*$")
_ADVISOR_SECRET_OR_CONTROL_RE = re.compile(
    r"(?i)\b(system prompt|ignore previous|developer message|api[_ -]?key|token|secret|password|bearer)\b"
)
_VISIBLE_STERILE_RE = re.compile(
    r"(?i)^\s*(no\.?|incorrect\.?|you are wrong\.?|that is false\.?|can't help\.?)\s*$"
)

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


def _estimate_tokens(text: str | None) -> int:
    if not text:
        return 0
    return (len(text) + 3) // 4


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


def _provider_name(selection: dict[str, Any] | None) -> str:
    if not isinstance(selection, dict):
        return ""
    return str(selection.get("provider") or "").strip().lower()


def _safe_tuple(items: list[Any] | tuple[Any, ...] | None, *, limit: int = 32) -> tuple[str, ...]:
    out: list[str] = []
    for item in items or []:
        text = sanitize_text(item, limit=120)
        if text and text not in out:
            out.append(text)
        if len(out) >= limit:
            break
    return tuple(out)


def _safe_dict(value: dict[str, Any] | None, *, key_limit: int = 60, value_limit: int = 220) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for raw_key, raw_value in (value or {}).items():
        key = sanitize_text(raw_key, limit=key_limit)
        if not key:
            continue
        if isinstance(raw_value, bool) or raw_value is None:
            clean[key] = raw_value
        elif isinstance(raw_value, (int, float)):
            clean[key] = raw_value
        elif isinstance(raw_value, (list, tuple)):
            clean[key] = [sanitize_text(item, limit=value_limit) for item in raw_value if sanitize_text(item, limit=value_limit)]
        elif isinstance(raw_value, dict):
            clean[key] = _safe_dict(raw_value, key_limit=key_limit, value_limit=value_limit)
        else:
            clean[key] = sanitize_text(raw_value, limit=value_limit)
    return clean


def _safe_records(items: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None, *, limit: int = 16) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        clean = _safe_dict(item)
        if clean:
            records.append(clean)
        if len(records) >= limit:
            break
    return tuple(records)


def validate_gov_turn_plan(plan: GovTurnPlan) -> dict[str, Any]:
    failures: list[str] = []
    if not plan.turn_id:
        failures.append("missing_turn_id")
    if not plan.route:
        failures.append("missing_route")
    if not plan.visible_worker_role:
        failures.append("missing_visible_worker_role")
    if not plan.worker_provider_selection:
        failures.append("missing_worker_provider_selection")
    if not plan.release_constraints:
        failures.append("missing_release_constraints")
    if not plan.worker_prompt_baton:
        failures.append("missing_worker_prompt_baton")
    if not plan.kernel_validation_result:
        # Placeholder is allowed during construction; final plans replace it.
        pass

    advisor_provider = _provider_name(plan.advisor_provider_selection)
    worker_provider = _provider_name(plan.worker_provider_selection)
    advisor_fallback = bool(plan.fallback_eligibility.get("advisor_fallback_allowed"))
    worker_fallback_active = bool(plan.fallback_eligibility.get("worker_fallback_active"))
    if advisor_provider in FALLBACK_ONLY_ADVISOR_PROVIDERS and not advisor_fallback:
        failures.append("minimax_advisor_without_fallback_eligibility")
    if worker_provider in FALLBACK_ONLY_ADVISOR_PROVIDERS and not worker_fallback_active:
        failures.append("minimax_worker_without_active_fallback")

    baton_lower = plan.worker_prompt_baton.lower()
    if "raw_advisor" in baton_lower or "surface_thought" in baton_lower:
        failures.append("raw_advisor_material_in_worker_baton")
    if _ADVISOR_SECRET_OR_CONTROL_RE.search(plan.worker_prompt_baton):
        failures.append("secret_or_control_text_in_worker_baton")
    if not any("visible release" in item.lower() for item in plan.release_constraints):
        failures.append("missing_visible_release_constraint")
    if not any("no scold" in item.lower() or "no-scold" in item.lower() for item in plan.voice_tone_constraints):
        failures.append("missing_constitutional_tone_constraint")
    if not any("serve the user's best interests" in item.lower() for item in plan.persona_identity_constraints):
        failures.append("missing_operating_objective_constraint")

    return {
        "passed": not failures,
        "failures": failures,
        "validator": "deterministic_holochat_gov_kernel_v0",
    }


def build_gov_turn_plan(
    *,
    turn_id: Any,
    user_id: Any = None,
    route: Any,
    visible_worker_role: Any = "visible_worker",
    worker_provider_selection: dict[str, Any] | None,
    advisor_provider_selection: dict[str, Any] | None,
    turn_policy: GovTurnPolicy,
    selected_context_ids: list[Any] | tuple[Any, ...] | None = None,
    dropped_context_ids: list[Any] | tuple[Any, ...] | None = None,
    context_drop_reasons: dict[str, Any] | None = None,
    memory_admissions: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    memory_rejections: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    artifact_refs: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    pinned_artifacts: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    tool_authorization: dict[str, Any] | None = None,
    search_authorization: dict[str, Any] | None = None,
    voice_tone_constraints: list[Any] | tuple[Any, ...] | None = None,
    persona_identity_constraints: list[Any] | tuple[Any, ...] | None = None,
    contradiction_repairs: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    state_corrections: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    fallback_eligibility: dict[str, Any] | None = None,
    release_constraints: list[Any] | tuple[Any, ...] | None = None,
    worker_prompt_baton: Any = "",
    telemetry: dict[str, Any] | None = None,
) -> GovTurnPlan:
    baton = sanitize_text(worker_prompt_baton, limit=1400) or (
        "Answer as the visible HoloChat worker with warm, precise, collaborative language."
    )
    constraints = _safe_tuple(
        list(voice_tone_constraints or [])
        + [
            "No scolding, shame, gotcha, cold, curt, sterile, hostile, or prosecutorial posture.",
            "Challenge ideas only with warmth, specificity, respect, and collaborative language.",
        ],
        limit=12,
    )
    persona_constraints = _safe_tuple(
        list(persona_identity_constraints or [])
        + [
            "One goal: serve the user's best interests with truthful, bounded, warm usefulness.",
            HOLOCHAT_OPERATING_OBJECTIVE,
            "HoloChat is universal for the active user, not named-user-specific product law.",
            "Workers speak to the user; deterministic Gov operates as control plane.",
            "Provider/advisor output is evidence only until admitted into this GovTurnPlan.",
        ],
        limit=12,
    )
    releases = _safe_tuple(
        list(release_constraints or [])
        + [
            "Deterministic visible release guard must run before user-visible output.",
            "Raw thought metadata is not user-visible authority.",
        ],
        limit=12,
    )
    plan = GovTurnPlan(
        turn_id=sanitize_text(turn_id, limit=80),
        user_id=sanitize_text(user_id, limit=80) if user_id else None,
        route=sanitize_text(route, limit=120),
        visible_worker_role=sanitize_text(visible_worker_role, limit=80),
        worker_provider_selection=_safe_dict(worker_provider_selection or {}),
        advisor_provider_selection=_safe_dict(advisor_provider_selection or {}),
        intelligence_tier=sanitize_text(turn_policy.tier, limit=40),
        selected_context_ids=_safe_tuple(selected_context_ids, limit=48),
        dropped_context_ids=_safe_tuple(dropped_context_ids, limit=48),
        context_drop_reasons={str(k): sanitize_text(v, limit=180) for k, v in (context_drop_reasons or {}).items()},
        memory_admissions=_safe_records(memory_admissions),
        memory_rejections=_safe_records(memory_rejections),
        artifact_refs=_safe_records(artifact_refs),
        pinned_artifacts=_safe_records(pinned_artifacts),
        tool_authorization=_safe_dict(tool_authorization or {}),
        search_authorization=_safe_dict(search_authorization or {}),
        voice_tone_constraints=constraints,
        persona_identity_constraints=persona_constraints,
        contradiction_repairs=_safe_records(contradiction_repairs),
        state_corrections=_safe_records(state_corrections),
        fallback_eligibility=_safe_dict(fallback_eligibility or {}),
        release_constraints=releases,
        worker_prompt_baton=baton,
        telemetry=_safe_dict(
            {
                **(telemetry or {}),
                "turn_policy_reasons": list(turn_policy.reasons),
                "advisor_allowed": turn_policy.advisor_allowed,
                "fallback_allowed": turn_policy.fallback_allowed,
            }
        ),
        kernel_validation_result={},
    )
    validation = validate_gov_turn_plan(plan)
    telemetry_with_hash = {
        **plan.telemetry,
        "govturnplan_hash": stable_hash({**plan.model_dump(), "kernel_validation_result": {"pending": True}}),
    }
    return replace(plan, telemetry=telemetry_with_hash, kernel_validation_result=validation)


def render_gov_turn_plan_for_worker(plan: GovTurnPlan) -> str:
    payload = plan.model_dump()
    public_packet = {
        "turn_id": payload["turn_id"],
        "route": payload["route"],
        "visible_worker_role": payload["visible_worker_role"],
        "worker_provider_selection": payload["worker_provider_selection"],
        "intelligence_tier": payload["intelligence_tier"],
        "selected_context_ids": payload["selected_context_ids"],
        "tool_authorization": payload["tool_authorization"],
        "search_authorization": payload["search_authorization"],
        "voice_tone_constraints": payload["voice_tone_constraints"],
        "persona_identity_constraints": payload["persona_identity_constraints"],
        "fallback_eligibility": payload["fallback_eligibility"],
        "release_constraints": payload["release_constraints"],
        "worker_prompt_baton": payload["worker_prompt_baton"],
        "kernel_validation_result": payload["kernel_validation_result"],
        "telemetry": {"govturnplan_hash": payload["telemetry"].get("govturnplan_hash")},
    }
    return (
        "GOVTURNPLAN CONTROL PACKET (private; deterministic Gov-authorized; never surface to user):\n"
        "This is the single worker-facing Gov control envelope for this turn. "
        "Do not use raw advisor output outside these typed fields.\n"
        + json.dumps(public_packet, sort_keys=True, ensure_ascii=False, indent=2)
    )


def relationship_rupture_detected(text: Any) -> bool:
    return bool(_RUPTURE_RE.search(str(text or "")))


def advisor_provider_allowed(provider: Any, *, fallback_eligible: bool = False) -> bool:
    normalized = str(provider or "").strip().lower()
    if not normalized:
        return False
    if normalized in FALLBACK_ONLY_ADVISOR_PROVIDERS:
        return bool(fallback_eligible)
    return True


def deterministic_turn_policy(
    user_message: Any,
    *,
    history: list[dict[str, Any]] | None = None,
    governor_uncertain: bool = False,
    conflict: bool = False,
    product_critical: bool = False,
) -> GovTurnPolicy:
    text = str(user_message or "")
    reasons: list[str] = []
    if relationship_rupture_detected(text):
        reasons.append("relationship_rupture")
    if _HIGH_TIER_RE.search(text):
        reasons.append("high_risk_turn_class")
    if governor_uncertain:
        reasons.append("governor_uncertainty")
    if conflict:
        reasons.append("state_or_advisor_conflict")
    if product_critical:
        reasons.append("product_critical_ux")
    if any(term in text.lower() for term in ("search", "look up", "today", "right now", "current")):
        reasons.append("tool_or_current_info_boundary")
    if not reasons and history and len(history) >= 12:
        reasons.append("long_thread_state_risk")

    if reasons:
        tier = "max" if any(reason in reasons for reason in ("relationship_rupture", "governor_uncertainty", "state_or_advisor_conflict")) else "high"
        return GovTurnPolicy(tier=tier, reasons=tuple(reasons), advisor_allowed=True, fallback_allowed=False)
    if _LOW_TIER_RE.match(text):
        return GovTurnPolicy(tier="fast", reasons=("routine_low_risk",), advisor_allowed=False, fallback_allowed=False)
    return GovTurnPolicy(tier="standard", reasons=("normal_turn",), advisor_allowed=True, fallback_allowed=False)


def _warm_relationship_repair_directive() -> str:
    return (
        HOLOCHAT_CONSTITUTIONAL_TONE_LAW
        + "\n"
        "Relationship repair mode: answer warmly, own any tone mismatch without defensiveness, "
        "stay concrete, avoid scolding or trap framing, and help the user feel met before moving on."
    )


def admit_advisor_prompt_directive(
    proposal: Any,
    *,
    user_message: Any = "",
) -> GovAdvisorAdmission:
    text = sanitize_text(proposal, limit=700)
    if relationship_rupture_detected(user_message):
        return GovAdvisorAdmission(
            admitted=True,
            value=_warm_relationship_repair_directive(),
            reason="deterministic_relationship_repair_overrode_advisor_directive",
            repaired=True,
            blocked_terms=tuple(_SCOLDING_DIRECTIVE_RE.findall(text)),
        )
    if not text:
        return GovAdvisorAdmission(admitted=False, value="", reason="empty_advisor_directive")
    blocked = tuple(term if isinstance(term, str) else str(term) for term in _SCOLDING_DIRECTIVE_RE.findall(text))
    hostile = bool(_HOSTILE_POSTURE_RE.search(text))
    if blocked or hostile or _ADVISOR_SECRET_OR_CONTROL_RE.search(text):
        return GovAdvisorAdmission(
            admitted=True,
            value=_warm_relationship_repair_directive(),
            reason="deterministic_gov_repaired_unsafe_advisor_directive",
            repaired=True,
            blocked_terms=blocked,
        )
    return GovAdvisorAdmission(
        admitted=True,
        value=text,
        reason="deterministic_gov_admitted_sanitized_advisor_directive",
    )


def admit_advisor_search_query(user_message: Any, advisor_query: Any) -> GovAdvisorAdmission:
    query = sanitize_text(advisor_query, limit=180)
    if not query:
        return GovAdvisorAdmission(admitted=False, value=None, reason="empty_advisor_search_query")
    text = str(user_message or "").lower()
    current_markers = (
        "today",
        "right now",
        "current",
        "latest",
        "recent",
        "this week",
        "news",
        "weather",
        "stock",
        "price",
        "score",
        "look up",
        "search",
    )
    if any(marker in text for marker in current_markers):
        return GovAdvisorAdmission(admitted=True, value=query, reason="deterministic_gov_authorized_current_info_search")
    return GovAdvisorAdmission(admitted=False, value=None, reason="deterministic_gov_denied_advisor_search")


def admit_advisor_claim_corrections(
    flagged_claims: list[dict[str, Any]] | None,
) -> GovAdvisorAdmission:
    admitted: list[str] = []
    blocked: list[str] = []
    for item in flagged_claims or []:
        claim = sanitize_text(item.get("claim"), limit=220) if isinstance(item, dict) else ""
        correction = sanitize_text(item.get("correction"), limit=260) if isinstance(item, dict) else ""
        if not claim or not correction:
            blocked.append("missing_claim_or_correction")
            continue
        if (
            _ADVISOR_SECRET_OR_CONTROL_RE.search(correction)
            or _SCOLDING_DIRECTIVE_RE.search(correction)
            or _HOSTILE_POSTURE_RE.search(correction)
        ):
            blocked.append("unsafe_correction")
            continue
        admitted.append(correction)
    return GovAdvisorAdmission(
        admitted=bool(admitted),
        value=admitted,
        reason="deterministic_gov_admitted_claim_corrections" if admitted else "no_admissible_claim_corrections",
        blocked_terms=tuple(blocked),
    )


def admit_advisor_memory_updates(updates: dict[str, Any] | None) -> GovAdvisorAdmission:
    admitted: dict[str, str] = {}
    blocked: list[str] = []
    for raw_key, raw_value in (updates or {}).items():
        key = sanitize_text(raw_key, limit=60).lower().replace(" ", "_").replace("-", "_")
        value = sanitize_text(raw_value, limit=500)
        if not key or key in {"none", "key"}:
            blocked.append("invalid_key")
            continue
        if not value.startswith("[FACT]"):
            blocked.append(key)
            continue
        if _ADVISOR_SECRET_OR_CONTROL_RE.search(value):
            blocked.append(key)
            continue
        admitted[key] = value
    return GovAdvisorAdmission(
        admitted=bool(admitted),
        value=admitted,
        reason="deterministic_gov_admitted_explicit_fact_memory_updates" if admitted else "no_admissible_memory_updates",
        blocked_terms=tuple(blocked),
    )


def admit_advisor_consolidation(result: dict[str, Any] | None) -> GovAdvisorAdmission:
    if not isinstance(result, dict):
        return GovAdvisorAdmission(admitted=False, value={}, reason="invalid_consolidation_shape")
    session_note = result.get("session_note") if isinstance(result.get("session_note"), dict) else {}
    life_context = []
    for entry in result.get("life_context") or []:
        if not isinstance(entry, dict):
            continue
        value = sanitize_text(entry.get("value"), limit=700)
        if not value or _ADVISOR_SECRET_OR_CONTROL_RE.search(value):
            continue
        clean = dict(entry)
        clean["value"] = value
        life_context.append(clean)
    clean_note = {
        sanitize_text(key, limit=80): sanitize_text(value, limit=600)
        for key, value in session_note.items()
        if sanitize_text(key, limit=80)
    }
    return GovAdvisorAdmission(
        admitted=bool(clean_note or life_context),
        value={"session_note": clean_note, "life_context": life_context},
        reason="deterministic_gov_admitted_sanitized_consolidation",
    )


def admit_advisor_thread_name(name: Any) -> GovAdvisorAdmission:
    text = sanitize_text(name, limit=60)
    if not text or _ADVISOR_SECRET_OR_CONTROL_RE.search(text):
        return GovAdvisorAdmission(admitted=False, value="", reason="thread_name_not_admitted")
    return GovAdvisorAdmission(admitted=True, value=text, reason="deterministic_gov_admitted_thread_name")


def admit_advisor_surface_thought(thought: Any) -> GovAdvisorAdmission:
    if not thought:
        return GovAdvisorAdmission(admitted=False, value=None, reason="empty_surface_thought")
    if isinstance(thought, dict):
        text = sanitize_text(thought.get("text"), limit=120)
        color = sanitize_text(thought.get("color"), limit=24).lower() or "blue"
    else:
        text = sanitize_text(thought, limit=120)
        color = "blue"
    if not text:
        return GovAdvisorAdmission(admitted=False, value=None, reason="empty_surface_thought_text")
    if (
        _SCOLDING_DIRECTIVE_RE.search(text)
        or _HOSTILE_POSTURE_RE.search(text)
        or _ADVISOR_SECRET_OR_CONTROL_RE.search(text)
    ):
        return GovAdvisorAdmission(admitted=False, value=None, reason="surface_thought_blocked_by_constitution")
    if color not in {"blue", "yellow", "red", "green", "purple", "orange"}:
        color = "blue"
    return GovAdvisorAdmission(
        admitted=True,
        value={"text": text, "color": color},
        reason="deterministic_gov_admitted_surface_thought",
    )


def deterministic_visible_release(
    user_message: Any,
    response_text: Any,
) -> GovVisibleReleaseDecision:
    text = str(response_text or "")
    if (
        _VISIBLE_STERILE_RE.match(text)
        or _VISIBLE_HOSTILE_POSTURE_RE.search(text)
    ):
        return GovVisibleReleaseDecision(
            release=True,
            text=(
                "Let me keep this warm and useful. "
                + (
                    "You're right to call out the tone. "
                    if relationship_rupture_detected(user_message)
                    else ""
                )
                + "I should help you see the point without making you feel prosecuted."
            ),
            reason="deterministic_constitutional_tone_repair_before_visible_release",
            repaired=True,
        )
    if _ADVISOR_SECRET_OR_CONTROL_RE.search(text):
        return GovVisibleReleaseDecision(
            release=False,
            text="I need to repair that response before showing it.",
            reason="visible_output_blocked_for_secret_or_control_text",
            repaired=True,
        )
    return GovVisibleReleaseDecision(release=True, text=text, reason="visible_output_admitted")


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
    content = artifact.get("content")
    content_hash = artifact.get("content_hash") or artifact.get("hash")
    if not content_hash and content:
        content_hash = stable_hash(content)
    if not artifact_id and not path and not content_hash:
        return None
    ref = {
        "artifact_id": sanitize_text(artifact_id, limit=120) or None,
        "path": sanitize_text(path, limit=260) or None,
        "hash": sanitize_text(content_hash, limit=96) or None,
        "title": sanitize_text(artifact.get("title"), limit=140) or None,
        "type": sanitize_text(artifact.get("type") or artifact.get("artifact_type"), limit=80) or None,
        "status": sanitize_text(artifact.get("status"), limit=80) or None,
        "summary": sanitize_text(
            artifact.get("summary") or artifact.get("description"),
            limit=180,
        ) or None,
    }
    if ref["artifact_id"] and not ref["status"]:
        ref["status"] = "available_by_id"
    return {key: value for key, value in ref.items() if value}


def _near_context_budget(context_budget: dict[str, Any] | None) -> bool:
    budget = context_budget or {}
    if str(budget.get("budget_status") or "").lower() in {"over_budget", "near_budget", "warning"}:
        return True
    limit = budget.get("budget_limit_tokens")
    estimate = budget.get("total_token_estimate")
    try:
        return bool(limit and estimate and int(estimate) >= int(limit) * 0.8)
    except (TypeError, ValueError):
        return False


def _trusted_state(state: HoloState | None) -> bool:
    return bool(state and state.state_audit and state.state_audit.trusted)


def _state_hash(state: HoloState | None) -> str | None:
    if not state:
        return None
    if state.state_audit and state.state_audit.state_hash:
        return state.state_audit.state_hash
    canonical = state.canonical_object()
    canonical.pop("STATE_AUDIT", None)
    return stable_hash(canonical)


def select_holobrain_injection_mode(
    state: HoloState | None,
    thread_status: str | None,
    context_budget: dict[str, Any] | None,
    fresh_thread: bool,
    recovery_needed: bool,
    topic_shift: bool,
    artifact_needed: bool,
) -> HoloBrainInjectionMode:
    """Deterministically choose how much HoloBrain state may enter context."""
    if not state:
        return HoloBrainInjectionMode.NONE

    if not _trusted_state(state):
        return HoloBrainInjectionMode.HASHES_ONLY if _state_hash(state) else HoloBrainInjectionMode.NONE

    if _near_context_budget(context_budget):
        return HoloBrainInjectionMode.HASHES_ONLY if _state_hash(state) else HoloBrainInjectionMode.NONE

    status = str(thread_status or "").lower()
    unrelated_shift = topic_shift and any(
        marker in status
        for marker in ("unrelated", "different project", "new topic", "new project")
    )
    same_project_discontinuity = topic_shift and any(
        marker in status
        for marker in ("same project", "same-project", "continuity", "discontinuity", "active project")
    )

    if unrelated_shift:
        return HoloBrainInjectionMode.HASHES_ONLY
    if recovery_needed:
        return HoloBrainInjectionMode.FULL_RESEED
    if fresh_thread:
        return HoloBrainInjectionMode.FULL_RESEED
    if same_project_discontinuity:
        return HoloBrainInjectionMode.ROLLING_SUMMARY
    if topic_shift:
        return HoloBrainInjectionMode.HASHES_ONLY
    if artifact_needed:
        return HoloBrainInjectionMode.ARTIFACT_REFS
    return HoloBrainInjectionMode.BATON_ONLY


def _constrain_payload(text: str, *, max_chars: int) -> str:
    redacted = redact_secrets(text)
    if len(redacted) <= max_chars:
        return redacted
    suffix = "\n  [truncated: HoloBrain injection exceeded configured limit]"
    return redacted[: max(0, max_chars - len(suffix))].rstrip() + suffix


def _audit_hash_lines(state: HoloState) -> list[str]:
    audit = state.state_audit
    return [
        f"  state_id: {sanitize_text(state.state_id, limit=96)}",
        f"  state_hash: {sanitize_text(audit.state_hash or _state_hash(state), limit=96)}",
        f"  summary_hash: {sanitize_text(audit.summary_hash, limit=96)}",
        f"  baton_hash: {sanitize_text(audit.baton_hash, limit=96)}",
        f"  artifact_registry_hash: {sanitize_text(audit.artifact_registry_hash, limit=96)}",
        f"  state_audit_trusted: {str(bool(audit.trusted)).lower()}",
    ]


def _artifact_ref_line(ref: dict[str, Any]) -> str:
    parts = [
        f"id={sanitize_text(ref.get('artifact_id'), limit=80)}" if ref.get("artifact_id") else None,
        f"title={sanitize_text(ref.get('title'), limit=100)}" if ref.get("title") else None,
        f"type={sanitize_text(ref.get('type'), limit=40)}" if ref.get("type") else None,
        f"hash={sanitize_text(ref.get('hash'), limit=80)}" if ref.get("hash") else None,
        f"status={sanitize_text(ref.get('status'), limit=60)}" if ref.get("status") else None,
        f"summary={sanitize_text(ref.get('summary'), limit=140)}" if ref.get("summary") else None,
    ]
    return " | ".join(part for part in parts if part)


def build_holobrain_injection_payload(
    state: HoloState | None,
    mode: HoloBrainInjectionMode,
    *,
    max_chars: int | None = None,
) -> str:
    if not state or mode == HoloBrainInjectionMode.NONE:
        return ""

    limit = max_chars or _int_env(
        "HOLOCHAT_HOLOBRAIN_INJECTION_MAX_CHARS",
        DEFAULT_HOLOBRAIN_INJECTION_CHAR_LIMIT,
    )
    if mode == HoloBrainInjectionMode.FULL_RESEED:
        return generate_auto_reseed_payload(state, max_chars=limit)

    canonical = state.canonical_object()
    baton = canonical.get("BATON_PASS") or {}
    artifacts = canonical.get("ARTIFACTS_REGISTRY") or []

    if mode == HoloBrainInjectionMode.HASHES_ONLY:
        lines = [
            "HOLOGOV-C HOLOBRAIN STATE HASHES (private; do not surface):",
            "  injection_mode: HASHES_ONLY",
            *_audit_hash_lines(state),
            "  instruction: Continue from current user input. Do not infer private state beyond these hashes.",
        ]
        return _constrain_payload("\n".join(lines), max_chars=limit)

    if mode == HoloBrainInjectionMode.ARTIFACT_REFS:
        lines = [
            "HOLOGOV-C HOLOBRAIN ARTIFACT REFS (private; refs only; do not surface):",
            "  injection_mode: ARTIFACT_REFS",
            *_audit_hash_lines(state),
            "  artifacts:",
        ]
        for ref in artifacts[:10]:
            line = _artifact_ref_line(ref)
            if line:
                lines.append(f"    - {line}")
        if not artifacts:
            lines.append("    - None captured.")
        lines.append("  instruction: Use refs only. Retrieve full artifact body only when specifically needed.")
        return _constrain_payload("\n".join(lines), max_chars=limit)

    if mode == HoloBrainInjectionMode.BATON_ONLY:
        lines = [
            "HOLOGOV-C HOLOBRAIN BATON (private; do not surface):",
            "  injection_mode: BATON_ONLY",
            *_audit_hash_lines(state),
            f"  current_task: {sanitize_text(baton.get('current_task'), limit=220)}",
            f"  next_action: {sanitize_text(baton.get('next_action'), limit=220)}",
        ]
        constraints = baton.get("constraints_for_next_assistant") or []
        if constraints:
            lines.append("  constraints:")
            lines.extend(f"    - {sanitize_text(item, limit=180)}" for item in constraints[:6])
        tensions = baton.get("unresolved_tensions") or []
        if tensions:
            lines.append("  unresolved_tensions:")
            lines.extend(f"    - {sanitize_text(item, limit=180)}" for item in tensions[:6])
        artifact_ids = baton.get("relevant_artifact_ids") or []
        if artifact_ids:
            lines.append("  relevant_artifact_ids:")
            lines.extend(f"    - {sanitize_text(item, limit=80)}" for item in artifact_ids[:8])
        return _constrain_payload("\n".join(lines), max_chars=limit)

    if mode == HoloBrainInjectionMode.ROLLING_SUMMARY:
        lines = [
            "HOLOGOV-C HOLOBRAIN ROLLING SUMMARY (private; do not surface):",
            "  injection_mode: ROLLING_SUMMARY",
            *_audit_hash_lines(state),
            f"  user_goal: {sanitize_text(canonical.get('USER_GOAL'), limit=220)}",
            f"  rolling_summary: {sanitize_text(canonical.get('ROLLING_SUMMARY'), limit=700)}",
            f"  next_action: {sanitize_text(baton.get('next_action'), limit=220)}",
        ]
        constraints = canonical.get("CRITICAL_CONSTRAINTS") or []
        if constraints:
            lines.append("  critical_constraints:")
            lines.extend(f"    - {sanitize_text(item, limit=180)}" for item in constraints[:6])
        settled = canonical.get("SETTLED_DECISIONS") or []
        if settled:
            lines.append("  settled_decisions:")
            lines.extend(f"    - {sanitize_text(item, limit=180)}" for item in settled[:6])
        return _constrain_payload("\n".join(lines), max_chars=limit)

    return ""


def build_holobrain_injection_plan(
    state: HoloState | None,
    *,
    thread_status: str | None,
    context_budget: dict[str, Any] | None,
    fresh_thread: bool,
    recovery_needed: bool,
    topic_shift: bool,
    artifact_needed: bool,
    max_chars: int | None = None,
) -> HoloBrainInjectionPlan:
    mode = select_holobrain_injection_mode(
        state,
        thread_status,
        context_budget,
        fresh_thread,
        recovery_needed,
        topic_shift,
        artifact_needed,
    )
    payload = build_holobrain_injection_payload(state, mode, max_chars=max_chars)
    reason = "no_state_available"
    if state:
        reason = {
            HoloBrainInjectionMode.NONE: "no_private_holobrain_injection",
            HoloBrainInjectionMode.HASHES_ONLY: (
                "fail_closed_or_budget_pressure"
                if (not _trusted_state(state) or _near_context_budget(context_budget))
                else "topic_shift_without_continuity_admission"
            ),
            HoloBrainInjectionMode.ARTIFACT_REFS: "artifact_refs_requested",
            HoloBrainInjectionMode.BATON_ONLY: "normal_continuation",
            HoloBrainInjectionMode.ROLLING_SUMMARY: "same_project_context_discontinuity",
            HoloBrainInjectionMode.FULL_RESEED: "fresh_thread_or_recovery",
        }[mode]
    return HoloBrainInjectionPlan(
        mode=mode,
        payload=payload,
        reason=reason,
        state_hash=_state_hash(state),
        char_count=len(payload),
        token_estimate=_estimate_tokens(payload),
    )


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


def retrieve_holobrain_artifact_body(
    brain: Any,
    capsule_id: str | None,
    artifact_id: str | None,
    *,
    full_body_needed: bool,
) -> str | None:
    """Retrieve full artifact content only under explicit caller demand."""
    if not full_body_needed or not brain or not capsule_id or not artifact_id:
        return None
    getter = getattr(brain, "get_artifact", None)
    if not getter:
        return None
    artifact = getter(capsule_id, artifact_id)
    if not isinstance(artifact, dict):
        return None
    return artifact.get("content")


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
    if previous_state and not has_meaningful_holobrain_delta(
        previous_state,
        state,
        include_rolling_summary=False,
    ):
        state.rolling_summary = previous_state.rolling_summary
    reseed = generate_auto_reseed_payload(state)
    state.state_audit = audit_state_object(
        state,
        latest_user_input=user_message,
        reseed_payload=reseed,
        extra_notes=[audit_note],
    )
    return state


def _baton_signature(baton: BatonPass) -> dict[str, Any]:
    data = baton.model_dump(mode="json")
    return {
        "current_task": data.get("current_task"),
        "next_action": data.get("next_action"),
        "focus_areas": data.get("focus_areas", []),
        "unresolved_tensions": data.get("unresolved_tensions", []),
        "relevant_artifact_ids": data.get("relevant_artifact_ids", []),
        "constraints_for_next_assistant": data.get("constraints_for_next_assistant", []),
        "required_tools": data.get("required_tools", []),
    }


def _gov_arc_signature(gov_arc: GovArcState) -> dict[str, Any]:
    data = gov_arc.model_dump(mode="json")
    return {
        "current_tension": data.get("current_tension"),
        "unresolved_questions": data.get("unresolved_questions", []),
        "settled_decisions": data.get("settled_decisions", []),
        "next_paths": data.get("next_paths", []),
        "handoff_recommendation": data.get("handoff_recommendation"),
    }


def _durable_state_signature(
    state: HoloState | None,
    *,
    include_rolling_summary: bool,
) -> dict[str, Any] | None:
    if not state:
        return None
    signature = {
        "user_goal": state.user_goal,
        "critical_constraints": state.critical_constraints,
        "settled_decisions": state.settled_decisions,
        "artifact_registry": state.artifact_registry,
        "required_tools": [
            tool.value if isinstance(tool, RequiredTools) else str(tool)
            for tool in state.required_tools
        ],
        "baton_pass": _baton_signature(state.baton_pass),
        "gov_arc_state": _gov_arc_signature(state.gov_arc_state),
    }
    if include_rolling_summary:
        signature["rolling_summary"] = state.rolling_summary
    return signature


def has_meaningful_holobrain_delta(
    previous_state: HoloState | None,
    candidate_state: HoloState | None,
    *,
    include_rolling_summary: bool = True,
) -> bool:
    """Return true only when durable HoloBrain state materially changed."""
    if not candidate_state:
        return False
    if not previous_state:
        return bool(
            candidate_state.user_goal
            or candidate_state.critical_constraints
            or candidate_state.settled_decisions
            or candidate_state.artifact_registry
            or candidate_state.rolling_summary
            or candidate_state.baton_pass.current_task
            or candidate_state.baton_pass.next_action
        )
    return _durable_state_signature(
        previous_state,
        include_rolling_summary=include_rolling_summary,
    ) != _durable_state_signature(
        candidate_state,
        include_rolling_summary=include_rolling_summary,
    )


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
