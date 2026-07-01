"""
chat_engine.py

Holo chat mode -- rotating serial analyst conversation engine.

Every response comes from one selected analyst provider.
The Governor is a separate controller/check layer; it does not produce a
second visible answer.
All providers speak as Holo using the unified persona prompt.
"""

import logging
import json
import os
import random
import re as _re
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any

from holo_context import (
    HoloContextBuilder,
    build_capsule_context_block,
    build_context_budget_ledger,
    build_life_context_block,
    build_runtime_identity_block,
    estimate_context_tokens,
)
from holo_governed_shadow import (
    GOVERNED_SHADOW_ENV,
    GOVERNED_SHADOW_VERSION,
    ROSTER as GOVERNED_SHADOW_ROSTER,
    governed_shadow_enabled,
    run_governed_shadow,
)
from holo_router import HoloRouter, PreviousRoute, RouteDecision
from holo_state import GovArcState, HoloState, RequiredTools
from holo_trace import HoloTraceRecord, log_trace
from holo_release import release_info
from llm_adapters import (
    HOLO_CHAT_SYSTEM_PROMPT,
    GovernorAdapter,
    load_adapters,
)
from project_brain import ProjectBrain
import web_search

logger = logging.getLogger("holo.chat")

# In-memory session store.
# Replace with Redis for multi-instance or persistent deployments.
_sessions: Dict[str, "ChatSession"] = {}


# ---------------------------------------------------------------------------
# Session model
# ---------------------------------------------------------------------------

@dataclass
class ChatSession:
    session_id: str
    history: List[Dict[str, str]] = field(default_factory=list)
    rotation_index: int = 0      # round-robin analyst cursor
    turn_count: int = 0
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)

    # Governor rotation state
    # Governor locks to one provider for 7–11 turns, then rotates when the
    # thread is healthy and no work is mid-resolution.
    governor_provider: Optional[str] = None
    governor_locked_since: int = 0
    governor_rotation_threshold: int = field(
        default_factory=lambda: random.randint(7, 11)
    )
    holo4dna_previous_route: Optional[PreviousRoute] = None
    gov_arc_state: GovArcState = field(default_factory=GovArcState)
    rolling_summary: Optional[str] = None
    continuity_ledger: Dict[str, List[str]] = field(default_factory=dict)
    critical_constraints: List[str] = field(default_factory=list)
    handoff_artifact_saved: bool = False
    handoff_suggested: bool = False
    autocompact_attempted: bool = False
    autocompact_count: int = 0
    last_autocompact_turn: int = 0
    handoff_artifact_count: int = 0
    last_handoff_artifact_turn: int = 0

    @property
    def thread_health_score(self) -> int:
        """
        Continuity health is based on explicit degradation signals, not raw
        thread length. Long threads are handled by bounded context assembly,
        rolling summaries, and handoff artifacts; they are not automatically
        unhealthy unless the carried frame starts to drift.
        """
        score, _reasons = self._thread_health_assessment()
        return score

    @property
    def thread_health_reasons(self) -> list[str]:
        _score, reasons = self._thread_health_assessment()
        return reasons

    def _thread_health_assessment(self) -> tuple[int, list[str]]:
        score = 100
        reasons: list[str] = []
        ledger = _normalized_continuity_ledger(self.continuity_ledger)
        arc = self.gov_arc_state or GovArcState()

        def penalize(points: int, reason: str) -> None:
            nonlocal score
            score = max(0, score - points)
            if reason not in reasons:
                reasons.append(reason)

        joined_regressions = " ".join(ledger.get("regressed") or []).lower()
        joined_missing = " ".join(ledger.get("still_missing") or []).lower()
        joined_open = " ".join(ledger.get("open_issues") or []).lower()
        joined_user = " ".join(ledger.get("user_continuity") or []).lower()
        joined_all = " ".join((joined_regressions, joined_missing, joined_open, joined_user))

        hard_drift_terms = (
            "capsule boundary",
            "boundary violation",
            "goal drift",
            "wrong goal",
            "lost goal",
            "stale decision",
            "stale summary",
            "full memory claim",
            "raw memory leak",
        )
        if any(term in joined_all for term in hard_drift_terms):
            penalize(85, "continuity_degradation_signal")

        if ledger.get("regressed"):
            penalize(35, "regression_recorded")
        if "stale" in joined_missing or "drift" in joined_missing:
            penalize(35, "stale_or_drift_missing_item")
        if arc.confidence == "low":
            penalize(25, "low_governor_continuity_confidence")
        if self.turn_count >= 2 and not (arc.user_goal or joined_user):
            penalize(20, "missing_live_goal_evidence")
        if self.turn_count >= 3 and not (arc.current_directive or arc.settled_decisions or ledger.get("repaired")):
            penalize(20, "missing_recent_decision_evidence")

        return score, reasons

    @property
    def thread_health_level(self) -> str:
        score = self.thread_health_score
        if score >= 61:
            return "GREEN"
        elif score >= 21:
            return "YELLOW"
        return "RED"

    @property
    def thread_status(self) -> str:
        reasons = set(self.thread_health_reasons)
        score = self.thread_health_score
        if "continuity_degradation_signal" in reasons or score <= 20:
            return "ROTATION_RECOMMENDED"
        elif score <= 60:
            return "CLEANUP_RECOMMENDED"
        return "HEALTHY"

    @property
    def user_alert(self) -> str:
        status = self.thread_status
        if status == "HEALTHY":
            return "NONE"
        return status


# ---------------------------------------------------------------------------
# Governor rotation helpers
# ---------------------------------------------------------------------------

LOCKED_ARCHITECTURE_MANIFEST = Path(__file__).resolve().parent / "holo_profiles" / "locked_architecture_profiles.json"
DEFAULT_LOCKED_ARCHITECTURE_PROFILE = "frontier_holo_optimized_opus_gpt55_v1"
SUPPORTED_POOL_STRATEGIES = {"frontier_ordered_full_registry"}
BALANCED_RUNTIME_PROFILE = "balanced"
DEFAULT_THREAD_HANDOFF_MIN_TURNS = 40
DEFAULT_AUTOCOMPACT_MIN_TURNS = 24
DEFAULT_AUTOCOMPACT_INTERVAL_TURNS = 10
DEFAULT_ADAPTER_HISTORY_MESSAGES = 8
DEFAULT_ADAPTER_HISTORY_CHARS = 8000
DEFAULT_ADAPTER_HISTORY_MESSAGE_CHARS = 1800
DEFAULT_GOVERNOR_CONTEXT_ITEMS = 16
DEFAULT_GOVERNOR_CONTEXT_VALUE_CHARS = 360
DEFAULT_CONTEXT_WARNING_TOKENS = 20000
DEFAULT_CONTEXT_HARD_LIMIT_TOKENS = 30000

_BALANCED_USER_POWER_TERMS = (
    "frontier",
    "power mode",
    "deep mode",
    "smarter",
    "not as smart",
    "amp this up",
)

_BALANCED_COMPLEXITY_TERMS = (
    "architecture",
    "doctrine",
    "under the hood",
    "strategy",
    "strategic",
    "complex",
    "hard problem",
    "deep reasoning",
    "tradeoff",
    "adversarial",
    "debug",
    "diagnose",
    "legal",
    "medical",
    "financial",
    "high stakes",
)

_BALANCED_CREATIVE_STRATEGY_TERMS = (
    "inspire",
    "inspiring",
    "creative",
    "vision",
    "hopeful",
    "pragmatic",
    "doctrine",
    "manifesto",
)

_BALANCED_GOV_ESCALATION_TERMS = (
    "pressure point",
    "live tension",
    "high stakes",
    "deep reasoning",
    "strategic",
    "hard part",
    "precision",
    "confront",
    "unresolved",
    "challenge",
)

# Local, non-authoritative pricing estimates. Only include model prices when we
# are comfortable showing a rough estimate; otherwise the UI reports unknown.
_STATIC_CHAT_PRICING_USD_PER_M_TOKEN: dict[tuple[str, str], tuple[float, float]] = {
    ("openai", "gpt-4o-mini"): (0.15, 0.60),
}

THREAD_HANDOFF_MESSAGE = "This thread is getting long. Start a fresh thread to keep Holo sharp."


@dataclass(frozen=True)
class ResolvedArchitectureProfile:
    profile_id: str
    profile_version: str
    status: str
    runtime_class: str
    builder_alignment: str
    registry_mode: str
    governor_lane: str
    runtime_behavior: str
    pool_strategy: str
    active_provider_order: tuple[str, ...]
    governor_provider: Optional[str]
    manifest_path: str
    manifest_version: str
    source: str = "locked_manifest"
    selector_source: str = "default_locked_profile"

    @property
    def architecture_profile(self) -> str:
        return self.profile_id

    @property
    def alignment_profile(self) -> str:
        return self.builder_alignment

    @property
    def registry_profile(self) -> str:
        return self.registry_mode

    def locked_value(self) -> dict[str, str]:
        return {
            "architecture_profile": self.architecture_profile,
            "alignment_profile": self.alignment_profile,
            "registry_profile": self.registry_profile,
            "governor_lane": self.governor_lane,
        }


def _selected_architecture_profile_id(env: dict[str, str] | None = None) -> tuple[str, str]:
    return DEFAULT_LOCKED_ARCHITECTURE_PROFILE, "locked_constant"


def _load_locked_architecture_manifest(path: Optional[Path] = None) -> dict[str, Any]:
    path = path or LOCKED_ARCHITECTURE_MANIFEST
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Locked architecture manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Locked architecture manifest is invalid JSON: {path}") from exc
    if manifest.get("schema_version") != "holo.architecture_profiles.v1":
        raise RuntimeError("Locked architecture manifest schema_version is invalid.")
    if not isinstance(manifest.get("profiles"), dict):
        raise RuntimeError("Locked architecture manifest has no profiles mapping.")
    return manifest


def _validate_locked_architecture_profile(profile_id: str, profile: dict[str, Any]) -> None:
    required = {
        "profile_id": profile_id,
        "status": "locked",
        "runtime_behavior": "manifest_controls_runtime_selection",
        "runtime_class": "frontier_holo_optimized",
        "builder_alignment": "patent_aligned_v4",
        "registry_mode": "full_registry",
        "governor_lane": "HoloGov-B",
    }
    for key, expected in required.items():
        if profile.get(key) != expected:
            raise RuntimeError(
                f"Locked architecture profile {profile_id!r} has invalid {key}: "
                f"{profile.get(key)!r}"
            )
    if profile.get("pool_strategy") not in SUPPORTED_POOL_STRATEGIES:
        raise RuntimeError(
            f"Locked architecture profile {profile_id!r} has unsupported pool_strategy: "
            f"{profile.get('pool_strategy')!r}"
        )
    provider_order = profile.get("active_provider_order")
    if not isinstance(provider_order, list) or not all(isinstance(item, str) and item.strip() for item in provider_order):
        raise RuntimeError(f"Locked architecture profile {profile_id!r} must define active_provider_order.")


def _holochat_runtime_profile(
    profile_id: Optional[str] = None,
    *,
    selector_source: Optional[str] = None,
) -> ResolvedArchitectureProfile:
    if profile_id is None:
        profile_id, selector_source = _selected_architecture_profile_id()
    else:
        profile_id = str(profile_id).strip()
        selector_source = selector_source or "explicit_manifest_profile_id"
    manifest = _load_locked_architecture_manifest()
    profiles = manifest["profiles"]
    if profile_id not in profiles:
        raise RuntimeError(
            f"HoloChat architecture profile {profile_id!r} is not present in "
            f"{LOCKED_ARCHITECTURE_MANIFEST.relative_to(Path(__file__).resolve().parent)}"
        )
    profile = profiles[profile_id]
    _validate_locked_architecture_profile(profile_id, profile)
    return ResolvedArchitectureProfile(
        profile_id=profile["profile_id"],
        profile_version=str(profile.get("profile_version", "")),
        status=profile["status"],
        runtime_class=profile["runtime_class"],
        builder_alignment=profile["builder_alignment"],
        registry_mode=profile["registry_mode"],
        governor_lane=profile["governor_lane"],
        runtime_behavior=profile["runtime_behavior"],
        pool_strategy=profile["pool_strategy"],
        active_provider_order=tuple(item.strip().lower() for item in profile["active_provider_order"]),
        governor_provider=(str(profile.get("governor_provider") or "").strip().lower() or None),
        manifest_path=str(LOCKED_ARCHITECTURE_MANIFEST),
        manifest_version=str(manifest.get("manifest_version", "")),
        selector_source=selector_source,
    )


def _positive_int_env(name: str, default: int, *, minimum: int = 0) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return max(minimum, int(raw))
    except ValueError:
        return default


def _adapter_history_message_limit() -> int:
    return _positive_int_env(
        "HOLOCHAT_ADAPTER_HISTORY_MESSAGES",
        DEFAULT_ADAPTER_HISTORY_MESSAGES,
        minimum=0,
    )


def _adapter_history_char_limit() -> int:
    return _positive_int_env(
        "HOLOCHAT_ADAPTER_HISTORY_CHARS",
        DEFAULT_ADAPTER_HISTORY_CHARS,
        minimum=1000,
    )


def _adapter_history_message_char_limit() -> int:
    return _positive_int_env(
        "HOLOCHAT_ADAPTER_HISTORY_MESSAGE_CHARS",
        DEFAULT_ADAPTER_HISTORY_MESSAGE_CHARS,
        minimum=400,
    )


def _bounded_adapter_history(
    history: list[dict[str, str]],
    *,
    max_messages: Optional[int] = None,
    max_chars: Optional[int] = None,
    message_char_limit: Optional[int] = None,
) -> list[dict[str, str]]:
    """
    Keep the raw transcript in session storage, but never send the full thread
    to providers. Long-term continuity is carried by Holo state + memory blocks.
    """
    if not history:
        return []
    message_limit = _adapter_history_message_limit() if max_messages is None else max(0, max_messages)
    char_limit = _adapter_history_char_limit() if max_chars is None else max(0, max_chars)
    per_message_limit = (
        _adapter_history_message_char_limit()
        if message_char_limit is None
        else max(1, message_char_limit)
    )
    if message_limit <= 0 or char_limit <= 0:
        return []

    selected: list[dict[str, str]] = []
    used_chars = 0
    for message in reversed(history[-message_limit:]):
        role = str(message.get("role") or "unknown")
        if role not in {"system", "user", "assistant", "tool"}:
            role = "unknown"
        content = _compact_text(message.get("content"), limit=per_message_limit)
        if not content:
            continue
        entry_chars = len(role) + len(content) + 2
        if selected and used_chars + entry_chars > char_limit:
            break
        if used_chars + entry_chars > char_limit:
            content = _compact_text(content, limit=max(1, char_limit - len(role) - 2))
            entry_chars = len(role) + len(content) + 2
        selected.append({"role": role, "content": content})
        used_chars += entry_chars
        if used_chars >= char_limit:
            break
    return list(reversed(selected))


def _bounded_consolidation_history(history: list[dict[str, str]]) -> list[dict[str, str]]:
    return _bounded_adapter_history(
        history,
        max_messages=24,
        max_chars=18000,
        message_char_limit=1200,
    )


def _adapter_history_budget_content(
    adapter_history: list[dict[str, str]],
    *,
    total_history_messages: int,
) -> str:
    lines = [
        f"{message.get('role', 'unknown')}: {message.get('content', '')}"
        for message in adapter_history
    ]
    omitted = max(0, total_history_messages - len(adapter_history))
    if omitted:
        lines.insert(0, f"[context_budget] omitted {omitted} older raw history message(s); use HOLO STATE OBJECT and memory blocks for continuity.")
    return "\n".join(lines)


def _provider_history_metadata(
    adapter_history: list[dict[str, str]],
    *,
    total_history_messages: int,
) -> dict[str, Any]:
    char_count = sum(
        len(str(message.get("role", ""))) + len(str(message.get("content", ""))) + 2
        for message in adapter_history
    )
    return {
        "adapter_history_messages": len(adapter_history),
        "adapter_history_total_messages": max(0, total_history_messages),
        "adapter_history_omitted_messages": max(0, total_history_messages - len(adapter_history)),
        "adapter_history_chars": char_count,
        "adapter_history_char_cap": _adapter_history_char_limit(),
        "adapter_history_message_cap": _adapter_history_message_limit(),
        "adapter_history_message_char_cap": _adapter_history_message_char_limit(),
    }


def _governor_capsule_context(context: dict[str, Any]) -> dict[str, str]:
    if not context:
        return {}
    item_limit = _positive_int_env(
        "HOLOCHAT_GOV_CONTEXT_ITEMS",
        DEFAULT_GOVERNOR_CONTEXT_ITEMS,
        minimum=1,
    )
    value_limit = _positive_int_env(
        "HOLOCHAT_GOV_CONTEXT_VALUE_CHARS",
        DEFAULT_GOVERNOR_CONTEXT_VALUE_CHARS,
        minimum=80,
    )
    safe: dict[str, str] = {}
    for key, value in list(context.items()):
        key_text = str(key)
        if key_text.startswith("_"):
            continue
        safe[key_text] = _compact_text(value, limit=value_limit)
        if len(safe) >= item_limit:
            break
    return safe


def _context_warning_token_limit() -> int:
    return _positive_int_env(
        "HOLOCHAT_CONTEXT_WARNING_TOKENS",
        DEFAULT_CONTEXT_WARNING_TOKENS,
        minimum=1000,
    )


def _context_hard_token_limit() -> int:
    return _positive_int_env(
        "HOLOCHAT_CONTEXT_HARD_LIMIT_TOKENS",
        DEFAULT_CONTEXT_HARD_LIMIT_TOKENS,
        minimum=1000,
    )


def _enforce_runtime_context_budget(context_budget: dict[str, Any]) -> None:
    total = _safe_positive_int(context_budget.get("total_token_estimate"))
    hard_limit = _context_hard_token_limit()
    if total > hard_limit:
        raise RuntimeError("HoloChat context budget exceeded safe limit before provider call.")


def _holochat_ordered_pool(
    active_pool: list[Any],
    bench_pool: list[Any],
    providers: tuple[str, ...],
) -> tuple[list[Any], list[Any]]:
    combined = [*active_pool, *bench_pool]
    by_provider = {
        str(getattr(adapter, "provider", "") or "").strip().lower(): adapter
        for adapter in combined
    }
    ordered = [by_provider[provider] for provider in providers if provider in by_provider]
    missing = [provider for provider in providers if provider not in by_provider]
    if missing:
        raise RuntimeError(
            "HoloChat provider rotation is missing configured provider(s): "
            + ", ".join(missing)
            + ". Check the matching API keys and model registry entries."
        )
    selected = {id(adapter) for adapter in ordered}
    remaining = [adapter for adapter in combined if id(adapter) not in selected]
    return ordered, remaining


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = (text or "").lower()
    return any(term in lowered for term in terms)


_NATIVE_PDF_PROVIDER_NAMES = {"anthropic", "google", "gemini"}


def _has_pdf_attachments(images: Optional[List[Dict[str, Any]]]) -> bool:
    return any(item.get("mimeType") == "application/pdf" for item in (images or []))


def _adapter_accepts_native_pdf(adapter: Any) -> bool:
    provider = str(getattr(adapter, "provider", "") or "").strip().lower()
    return provider in _NATIVE_PDF_PROVIDER_NAMES


def _adapter_candidate_order_for_attachments(
    adapters: list[Any],
    selected: Any,
    images: Optional[List[Dict[str, Any]]],
) -> list[Any]:
    order = _adapter_candidate_order(adapters, selected)
    if not _has_pdf_attachments(images):
        return order
    pdf_capable = [adapter for adapter in order if _adapter_accepts_native_pdf(adapter)]
    return pdf_capable or order


def _balanced_frontier_assist_reason(
    *,
    user_message: str,
    tenor: Optional[str],
) -> Optional[str]:
    """Return a safe reason when Balanced should use a frontier assist analyst."""
    if _contains_any(user_message, _BALANCED_USER_POWER_TERMS):
        return "user_requested_power_lane"
    if _contains_any(user_message, _BALANCED_COMPLEXITY_TERMS):
        return "complexity_or_high_stakes"
    if _contains_any(user_message, _BALANCED_CREATIVE_STRATEGY_TERMS):
        return "creative_strategy_depth"
    if tenor and _contains_any(tenor, _BALANCED_GOV_ESCALATION_TERMS):
        return "governor_escalated_depth"
    return None


def _select_frontier_assist_adapter(
    bench_pool: list[Any],
    *,
    initial_adapter: Any,
    governor: Any,
) -> Optional[Any]:
    if not bench_pool:
        return None
    blocked = {
        getattr(initial_adapter, "provider", None),
        getattr(governor, "provider", None) if governor is not None else None,
    }
    candidates = [adapter for adapter in bench_pool if getattr(adapter, "provider", None) not in blocked]
    if not candidates:
        candidates = [adapter for adapter in bench_pool if adapter is not initial_adapter]
    if not candidates:
        candidates = bench_pool
    return random.choice(candidates)


def _frontier_assist_metadata(
    *,
    enabled: bool,
    reason: Optional[str] = None,
    selected_adapter: Optional[Any] = None,
) -> dict[str, Any]:
    return {
        "enabled": bool(enabled),
        "triggered": bool(reason and selected_adapter),
        "reason": reason if reason and selected_adapter else ("not_triggered" if enabled else "off"),
        "source": "balanced_runtime" if enabled else "off",
        "selected": _adapter_identity_dict(selected_adapter) if selected_adapter is not None else None,
    }


def _timer_start() -> float:
    return time.perf_counter()


def _elapsed_timer_ms(start: float) -> int:
    return max(0, int((time.perf_counter() - start) * 1000))


def _add_timing(timings: dict[str, int], key: str, start: float) -> None:
    timings[key] = int(timings.get(key, 0)) + _elapsed_timer_ms(start)


def _timing_breakdown_metadata(
    timings: dict[str, int],
    *,
    turn_started_at: float,
) -> dict[str, Any]:
    values = {
        "memory_context_ms": int(timings.get("memory_context_ms", 0)),
        "governor_pre_ms": int(timings.get("governor_pre_ms", 0)),
        "web_search_ms": int(timings.get("web_search_ms", 0)),
        "context_assembly_ms": int(timings.get("context_assembly_ms", 0)),
        "analyst_ms": int(timings.get("analyst_ms", 0)),
        "governor_post_ms": int(timings.get("governor_post_ms", 0)),
        "persistence_ms": int(timings.get("persistence_ms", 0)),
        "total_server_ms": _elapsed_timer_ms(turn_started_at),
    }
    owner_scores = {
        "memory": values["memory_context_ms"] + values["context_assembly_ms"],
        "governor": values["governor_pre_ms"] + values["governor_post_ms"],
        "web": values["web_search_ms"],
        "analyst": values["analyst_ms"],
        "persistence": values["persistence_ms"],
    }
    primary_owner = max(owner_scores, key=owner_scores.get)
    values.update(
        {
            "primary_time_owner": primary_owner,
            "primary_time_owner_ms": owner_scores[primary_owner],
            "note": "Safe stage timings only; browser pacing and network transit are not included.",
        }
    )
    return values


def _thread_handoff_min_turns() -> int:
    raw = os.getenv("HOLOCHAT_HANDOFF_MIN_TURNS", "").strip()
    if not raw:
        return DEFAULT_THREAD_HANDOFF_MIN_TURNS
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_THREAD_HANDOFF_MIN_TURNS


def _autocompact_min_turns() -> int:
    raw = os.getenv("HOLOCHAT_AUTOCOMPACT_MIN_TURNS", "").strip()
    if not raw:
        return DEFAULT_AUTOCOMPACT_MIN_TURNS
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_AUTOCOMPACT_MIN_TURNS


def _autocompact_interval_turns() -> int:
    raw = os.getenv("HOLOCHAT_AUTOCOMPACT_INTERVAL_TURNS", "").strip()
    if not raw:
        return DEFAULT_AUTOCOMPACT_INTERVAL_TURNS
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_AUTOCOMPACT_INTERVAL_TURNS


def _thread_handoff_ready(session: "ChatSession") -> bool:
    if session.thread_health_level != "RED":
        return False
    return session.turn_count >= _thread_handoff_min_turns()


def _handoff_for_context_window(session: "ChatSession") -> Optional[dict[str, Any]]:
    """Return one visible fresh-thread prompt per session/context window."""
    if not _thread_handoff_ready(session) or session.handoff_suggested:
        return None
    session.handoff_suggested = True
    arc = session.gov_arc_state
    return {
        "suggested": True,
        "message": THREAD_HANDOFF_MESSAGE,
        "new_thread": "/chat",
        "arc": {
            "topic": _compact_text(arc.current_topic or "", limit=160),
            "goal": _compact_text(arc.user_goal or arc.current_directive or "", limit=220),
            "tension": _compact_text(arc.current_tension or "", limit=220),
            "next_paths": [_compact_text(path, limit=180) for path in arc.next_paths[:3]],
        },
    }


def _safe_handoff_transition(value: Any) -> Optional[dict[str, Any]]:
    """Keep fresh-thread continuity to synthesized, bounded handoff fields."""
    if not isinstance(value, dict):
        return None
    next_paths = value.get("next_paths")
    safe_paths = []
    if isinstance(next_paths, list):
        safe_paths = [
            _compact_text(path, limit=200)
            for path in next_paths[:3]
            if _compact_text(path, limit=200)
        ]
    safe = {
        "source": "thread_handoff",
        "topic": _compact_text(value.get("topic"), limit=180),
        "goal": _compact_text(value.get("goal"), limit=240),
        "tension": _compact_text(value.get("tension"), limit=240),
        "next_paths": safe_paths,
        "at": _compact_text(value.get("at"), limit=40),
    }
    if not any((safe["topic"], safe["goal"], safe["tension"], safe["next_paths"])):
        return None
    return safe


def _thread_handoff_transition_block(transition: Optional[dict[str, Any]]) -> str:
    safe = _safe_handoff_transition(transition)
    if not safe:
        return ""
    lines = [
        "THREAD HANDOFF SEED (private continuity context for this fresh thread):",
        "  source: thread_handoff",
    ]
    if safe.get("topic"):
        lines.append(f"  prior_topic: {safe['topic']}")
    if safe.get("goal"):
        lines.append(f"  prior_goal: {safe['goal']}")
    if safe.get("tension"):
        lines.append(f"  unresolved_tension: {safe['tension']}")
    if safe.get("next_paths"):
        lines.append("  useful_next_paths:")
        for path in safe["next_paths"][:3]:
            lines.append(f"    - {path}")
    lines.append(
        "  instruction: Use this as a compact synthesis from the previous thread. "
        "Do not claim full memory or perfect continuity; orient the next answer to this arc."
    )
    return "\n".join(lines)


def _apply_handoff_transition_to_session(
    session: "ChatSession",
    transition: Optional[dict[str, Any]],
) -> Optional[dict[str, Any]]:
    safe = _safe_handoff_transition(transition)
    if not safe or session.turn_count != 0:
        return None
    previous = session.gov_arc_state or GovArcState()
    session.gov_arc_state = GovArcState(
        current_topic=safe.get("topic") or previous.current_topic,
        topic_shift_reason="fresh_thread_handoff",
        user_goal=safe.get("goal") or previous.user_goal or safe.get("topic") or None,
        current_tension=safe.get("tension") or previous.current_tension,
        unresolved_questions=previous.unresolved_questions[:5],
        settled_decisions=previous.settled_decisions[:5],
        last_gov_read=(
            "Gov is starting a fresh thread from a compact handoff seed, "
            "selected memory, and current user input."
        ),
        current_directive=previous.current_directive,
        next_paths=(safe.get("next_paths") or previous.next_paths)[:3],
        web_decision=previous.web_decision,
        memory_write_summary=previous.memory_write_summary,
        handoff_recommendation="accepted",
        confidence="medium",
    )
    return safe


def _claim_autocompact_for_context_window(
    session: "ChatSession",
    *,
    capsule_id: Optional[str],
    incognito: bool,
) -> bool:
    """Allow spaced background compaction without repeatedly nudging the user."""
    if not capsule_id or incognito or session.thread_health_level != "RED":
        return False
    if session.turn_count < _autocompact_min_turns():
        return False
    if (
        session.last_autocompact_turn
        and session.turn_count - session.last_autocompact_turn < _autocompact_interval_turns()
    ):
        return False
    session.autocompact_attempted = True
    session.autocompact_count += 1
    session.last_autocompact_turn = session.turn_count
    return True


def _adapter_pool_metadata(adapters: list[Any]) -> list[dict[str, Optional[str]]]:
    return [_adapter_identity_dict(adapter) for adapter in adapters]


def _governor_turn_metadata(governor: Any, *, checked_this_turn: bool) -> dict[str, Any]:
    provider = getattr(governor, "provider", None) if governor is not None else None
    model = getattr(governor, "model_id", getattr(governor, "model", None)) if governor is not None else None
    present = governor is not None
    return {
        "governor_present": present,
        "governor_checked_this_turn": bool(present and checked_this_turn),
        "governor_mode": "active" if present else "off",
        "governor_provider": provider,
        "governor_model": model,
        "governor_status": "checked_this_turn" if present and checked_this_turn else "not_checked",
        "governor_role": "controller_check_layer" if present else "off",
    }


def _governor_trace_metadata(
    *,
    web_trace: Optional[dict[str, Any]],
    incognito: bool,
    memory_extraction_attempted: bool,
    memory_writes_count: int,
    thread_health_level: str,
    conversation_paths_count: int = 0,
) -> dict[str, Any]:
    web_status = (web_trace or {}).get("status") or "off"
    memory_status = "skipped_incognito" if incognito else (
        "checked" if memory_extraction_attempted else "not_available"
    )
    return {
        "temperature": "checked",
        "web_decision": web_status,
        "web_search": web_trace or _web_trace(None, source="none", results=None),
        "claim_check": "checked",
        "memory_extraction": memory_status,
        "memory_writes_count": _safe_positive_int(memory_writes_count),
        "conversation_paths": "generated" if conversation_paths_count else "skipped",
        "conversation_paths_count": _safe_positive_int(conversation_paths_count),
        "thread_health": thread_health_level,
    }


def _safe_positive_int(value: Any) -> int:
    try:
        parsed = int(value or 0)
    except (TypeError, ValueError):
        return 0
    return max(0, parsed)


_CURRENT_INFO_RE = _re.compile(
    r"\b("
    r"today|tonight|currently|current|latest|recent|right now|now|new|news|"
    r"price|prices|stock|stocks|weather|forecast|score|scores|schedule|"
    r"ceo|president|released|available|outage|down|online|updated"
    r")\b",
    _re.IGNORECASE,
)


def _compact_text(value: Any, *, limit: int = 160) -> str:
    text = " ".join(str(value or "").strip().split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _deterministic_search_query(user_message: str) -> Optional[str]:
    text = (user_message or "").strip()
    if not text or not _CURRENT_INFO_RE.search(text):
        return None
    return _compact_text(text, limit=180)


def _resolve_search_query(user_message: str, governor_query: Optional[str]) -> tuple[Optional[str], str, str]:
    gov_query = _compact_text(governor_query, limit=180) if governor_query else ""
    if gov_query:
        return gov_query, "governor", "search_requested_by_governor"
    forced = _deterministic_search_query(user_message)
    if forced:
        return forced, "deterministic", "forced_currentness_trigger"
    return None, "none", "not_needed"


def _web_result_count(results: Optional[str]) -> int:
    if not results:
        return 0
    count = len(_re.findall(r"(?m)^Source:\s+", results))
    return count or 1


def _web_trace(
    query: Optional[str],
    *,
    source: str,
    results: Optional[str],
) -> dict[str, Any]:
    attempted = bool(query)
    result_count = _web_result_count(results)
    configured = bool(os.getenv("TAVILY_API_KEY"))
    if not attempted:
        status = "off"
        unavailable_reason = None
    elif results:
        status = "checked"
        unavailable_reason = None
    elif not configured:
        status = "unavailable"
        unavailable_reason = "missing_config"
    else:
        status = "unavailable"
        unavailable_reason = "no_results_or_search_failed"
    return {
        "decision": "search_requested" if attempted else "not_needed",
        "source": source,
        "attempted": attempted,
        "provider": "tavily",
        "status": status,
        "result_count": result_count,
        "unavailable_reason": unavailable_reason,
    }


def _run_web_search_for_turn(user_message: str, governor_query: Optional[str]) -> tuple[Optional[str], Optional[str], dict[str, Any]]:
    search_query, source, decision = _resolve_search_query(user_message, governor_query)
    results = web_search.search(search_query) if search_query else None
    trace = _web_trace(search_query, source=source, results=results)
    trace["decision"] = decision
    return search_query, results, trace


def _gov_arc_state_block(arc_state: GovArcState) -> str:
    data = arc_state.model_dump(mode="json")
    lines = ["GOV ARC STATE (Holo-owned continuity object; private, do not surface):"]
    for key in (
        "current_topic",
        "topic_shift_reason",
        "user_goal",
        "current_tension",
        "last_gov_read",
        "current_directive",
        "web_decision",
        "memory_write_summary",
        "handoff_recommendation",
        "confidence",
    ):
        value = data.get(key)
        if value:
            lines.append(f"  {key}: {_compact_text(value, limit=220)}")
    for key in ("unresolved_questions", "settled_decisions", "next_paths"):
        values = data.get(key) or []
        if values:
            lines.append(f"  {key}:")
            for item in values[:5]:
                lines.append(f"    - {_compact_text(item, limit=180)}")
    return "\n".join(lines)


_PATENT_ROLE_SEQUENCE = (
    "DIRECT_SYNTHESIS",
    "ASSUMPTION_ATTACK",
    "EVIDENCE_PRESSURE",
    "EDGE_CASE_SCAN",
    "ACTIONABILITY_AUDIT",
    "SYNTHESIS",
)

_CONTINUITY_LEDGER_KEYS = (
    "open_issues",
    "repaired",
    "regressed",
    "still_missing",
    "user_continuity",
    "pinned_artifacts",
)


def _conversation_role_for_turn(turn_count: int) -> str:
    if turn_count <= 1:
        return _PATENT_ROLE_SEQUENCE[0]
    return _PATENT_ROLE_SEQUENCE[(turn_count - 1) % len(_PATENT_ROLE_SEQUENCE)]


def _rolling_summary_from_history(history: list[dict[str, str]], *, limit: int = 1800) -> str:
    if not history:
        return ""
    lines = []
    for item in history[-12:]:
        role = "USER" if item.get("role") == "user" else "HOLO"
        content = _compact_text(item.get("content"), limit=220)
        if content:
            lines.append(f"{role}: {content}")
    text = "\n".join(lines)
    if len(text) <= limit:
        return text
    return text[-limit:].lstrip()


def _empty_continuity_ledger() -> dict[str, list[str]]:
    return {key: [] for key in _CONTINUITY_LEDGER_KEYS}


def _clean_ledger_items(values: list[Any], *, limit: int = 5, item_limit: int = 180) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _compact_text(value, limit=item_limit)
        if not item or item in seen:
            continue
        seen.add(item)
        cleaned.append(item)
        if len(cleaned) >= limit:
            break
    return cleaned


def _normalized_continuity_ledger(
    ledger: Optional[dict[str, list[str]]],
) -> dict[str, list[str]]:
    normalized = _empty_continuity_ledger()
    for key in _CONTINUITY_LEDGER_KEYS:
        normalized[key] = _clean_ledger_items(list((ledger or {}).get(key) or []))
    return normalized


def _continuity_ledger_from_history(history: list[dict[str, str]]) -> dict[str, list[str]]:
    ledger = _empty_continuity_ledger()
    if not history:
        return ledger
    last_user = next((m.get("content") for m in reversed(history) if m.get("role") == "user"), "")
    last_holo = next((m.get("content") for m in reversed(history) if m.get("role") == "assistant"), "")
    if last_user:
        ledger["user_continuity"] = [f"restored latest user need: {_compact_text(last_user, limit=180)}"]
    if last_holo:
        ledger["repaired"] = [f"restored latest Holo response: {_compact_text(last_holo, limit=180)}"]
    return ledger


def _update_rolling_summary_after_turn(
    session: "ChatSession",
    *,
    user_message: str,
    response_text: str,
) -> str:
    previous = session.rolling_summary or _rolling_summary_from_history(session.history[:-2])
    latest = (
        f"USER: {_compact_text(user_message, limit=260)}\n"
        f"HOLO: {_compact_text(response_text, limit=360)}"
    )
    combined = "\n".join(part for part in (previous, latest) if part)
    session.rolling_summary = combined[-1800:].lstrip()
    return session.rolling_summary


def _update_continuity_ledger_after_turn(
    session: "ChatSession",
    *,
    user_message: str,
    response_text: str,
    conversation_paths: Optional[list[str]] = None,
    artifacts_saved: Optional[list[dict[str, Any]]] = None,
    flagged_claims: Optional[list[dict[str, Any]]] = None,
    memory_writes_count: int = 0,
) -> dict[str, list[str]]:
    previous = _normalized_continuity_ledger(session.continuity_ledger)
    arc = session.gov_arc_state or GovArcState()
    open_candidates = [
        *(conversation_paths or []),
        *(arc.unresolved_questions or []),
        *(previous.get("open_issues") or []),
    ]
    repaired_candidates = [
        f"addressed latest turn: {_compact_text(response_text, limit=220)}",
        *(previous.get("repaired") or []),
    ]
    regression_candidates = list(previous.get("regressed") or [])
    for claim in flagged_claims or []:
        correction = claim.get("correction") if isinstance(claim, dict) else None
        if correction:
            regression_candidates.insert(0, f"claim corrected: {correction}")
    still_missing_candidates = list(previous.get("still_missing") or [])
    if session.thread_health_level != "GREEN":
        still_missing_candidates.insert(0, f"thread health {session.thread_health_level}: keep continuity compressed and explicit")
    user_candidates = [
        f"latest user need: {_compact_text(user_message, limit=220)}",
        *([f"current goal: {_compact_text(arc.user_goal, limit=180)}"] if arc.user_goal else []),
        *([f"current tension: {_compact_text(arc.current_tension, limit=180)}"] if arc.current_tension else []),
        *(previous.get("user_continuity") or []),
    ]
    artifact_candidates = list(previous.get("pinned_artifacts") or [])
    if session.handoff_artifact_count:
        artifact_candidates.insert(0, f"thread_handoff_artifacts: {session.handoff_artifact_count}")
    for artifact in artifacts_saved or []:
        if isinstance(artifact, dict):
            label = artifact.get("title") or artifact.get("name") or artifact.get("artifact_id") or artifact.get("id")
            if label:
                artifact_candidates.insert(0, f"saved artifact: {label}")
    if memory_writes_count:
        repaired_candidates.insert(0, f"memory updated: {memory_writes_count} write(s)")
    ledger = {
        "open_issues": _clean_ledger_items(open_candidates),
        "repaired": _clean_ledger_items(repaired_candidates),
        "regressed": _clean_ledger_items(regression_candidates),
        "still_missing": _clean_ledger_items(still_missing_candidates),
        "user_continuity": _clean_ledger_items(user_candidates),
        "pinned_artifacts": _clean_ledger_items(artifact_candidates),
    }
    session.continuity_ledger = ledger
    return ledger


def _patent_state_block(
    session: "ChatSession",
    *,
    user_message: str,
    required_tools: list[RequiredTools],
) -> str:
    arc = session.gov_arc_state or GovArcState()
    rolling = session.rolling_summary or _rolling_summary_from_history(session.history)
    role = _conversation_role_for_turn(session.turn_count)
    focus = [
        item
        for item in (
            arc.current_tension,
            arc.current_directive,
            arc.current_topic,
        )
        if item
    ][:3]
    lines = [
        "HOLO STATE OBJECT (private; patent-aligned continuity state; never surface directly):",
        f"  USER_GOAL: {_compact_text(arc.user_goal or arc.current_topic or user_message, limit=220)}",
        f"  LATEST_INPUT_SUMMARY: {_compact_text(user_message, limit=220)}",
        "  ROLLING_SUMMARY:",
    ]
    if rolling:
        for line in rolling.splitlines()[-10:]:
            lines.append(f"    {line}")
    else:
        lines.append("    none yet")
    if session.critical_constraints:
        lines.append("  CRITICAL_CONSTRAINTS:")
        for item in session.critical_constraints[:6]:
            lines.append(f"    - {_compact_text(item, limit=180)}")
    if arc.settled_decisions:
        lines.append("  SETTLED_DECISIONS:")
        for item in arc.settled_decisions[:6]:
            lines.append(f"    - {_compact_text(item, limit=180)}")
    ledger = _normalized_continuity_ledger(session.continuity_ledger)
    if any(ledger.values()):
        lines.append("  CONTINUITY_LEDGER:")
        for key in _CONTINUITY_LEDGER_KEYS:
            values = ledger.get(key) or []
            if not values:
                continue
            lines.append(f"    {key}:")
            for item in values[:5]:
                lines.append(f"      - {_compact_text(item, limit=180)}")
    lines.extend(
        [
            "  ARTIFACTS_REGISTRY:",
            f"    - thread_handoff_artifacts: {session.handoff_artifact_count}",
            "  REQUIRED_TOOLS: " + ", ".join(tool.value for tool in required_tools),
            "  BATON_PASS:",
            "    next_model_policy: serial_distinct_model_when_available",
            f"    assigned_role: {role}",
            "    instruction: Treat prior output as an external hypothesis, preserve what is true, challenge what is soft, and surface the highest-value next insight.",
        ]
    )
    if focus:
        lines.append("    focus_areas:")
        for item in focus:
            lines.append(f"      - {_compact_text(item, limit=180)}")
    if arc.unresolved_questions:
        lines.append("    unresolved_tensions:")
        for item in arc.unresolved_questions[:5]:
            lines.append(f"      - {_compact_text(item, limit=180)}")
    return "\n".join(lines)


def _update_gov_arc_state(
    session: "ChatSession",
    *,
    user_message: str,
    tenor: Optional[str],
    web_trace: dict[str, Any],
    conversation_paths: Optional[list[str]] = None,
    memory_writes_count: int = 0,
    handoff: Optional[dict[str, Any]] = None,
) -> GovArcState:
    previous = session.gov_arc_state or GovArcState()
    topic = _compact_text(user_message, limit=90) or previous.current_topic
    topic_shift_reason = previous.topic_shift_reason
    if previous.current_topic and topic and topic != previous.current_topic:
        topic_shift_reason = "latest_user_turn_shifted_focus"
    directive = _compact_text(tenor, limit=220) if tenor else previous.current_directive
    web_status = (web_trace or {}).get("status") or "off"
    web_source = (web_trace or {}).get("source") or "none"
    next_paths = [
        _compact_text(path, limit=120)
        for path in (conversation_paths or previous.next_paths or [])
        if _compact_text(path, limit=120)
    ][:3]
    arc = GovArcState(
        current_topic=topic,
        topic_shift_reason=topic_shift_reason,
        user_goal=previous.user_goal or topic,
        current_tension=previous.current_tension,
        unresolved_questions=previous.unresolved_questions[:5],
        settled_decisions=previous.settled_decisions[:5],
        last_gov_read=(
            f"Gov reconstructed the turn from Holo-owned state, recent history, "
            f"selected context, and a {web_status} web decision."
        ),
        current_directive=directive,
        next_paths=next_paths,
        web_decision=f"{web_status} via {web_source}",
        memory_write_summary=f"{_safe_positive_int(memory_writes_count)} writes this turn",
        handoff_recommendation="suggested" if handoff else None,
        confidence="medium" if session.thread_health_level == "GREEN" else "low",
    )
    session.gov_arc_state = arc
    return arc


def _thread_handoff_markdown(
    *,
    session: "ChatSession",
    consolidation: dict[str, Any],
    gov_arc_state: GovArcState,
) -> str:
    session_note = (consolidation or {}).get("session_note") or {}
    life_context = (consolidation or {}).get("life_context") or []
    open_threads = session_note.get("open_threads") or gov_arc_state.unresolved_questions or []
    next_paths = gov_arc_state.next_paths or []
    lines = [
        "# Thread Handoff",
        "",
        "This is a synthesized reseed artifact for the next HoloChat thread. "
        "It is tethered to the source chat session, while the raw chat remains available separately.",
        "",
        "## What Changed",
        _compact_text(session_note.get("what_changed") or "No durable change captured.", limit=600),
        "",
        "## What Surfaced",
        _compact_text(session_note.get("what_surfaced") or "No surfaced insight captured.", limit=600),
        "",
        "## Open Threads",
    ]
    if open_threads:
        lines.extend(f"- {_compact_text(item, limit=240)}" for item in open_threads[:8])
    else:
        lines.append("- None captured.")
    lines.extend(["", "## Gov Read", _compact_text(session_note.get("captain_note") or gov_arc_state.last_gov_read or "", limit=700)])
    if life_context:
        lines.extend(["", "## Memory Nutrients"])
        for entry in life_context[:8]:
            key = _compact_text(entry.get("key", "memory"), limit=80)
            value = _compact_text(entry.get("value", ""), limit=260)
            if value:
                lines.append(f"- {key}: {value}")
    if next_paths:
        lines.extend(["", "## Suggested Next Paths"])
        lines.extend(f"- {_compact_text(path, limit=180)}" for path in next_paths[:3])
    lines.extend(
        [
            "",
            "## Source",
            "Raw chat remains the source record. This artifact is a clean synthesis for retrieval and carry-forward.",
            "",
        ]
    )
    return "\n".join(lines)


def _save_thread_handoff_artifact(
    brain: Any,
    *,
    capsule_id: Optional[str],
    session: "ChatSession",
    consolidation: dict[str, Any],
) -> Optional[str]:
    if not capsule_id:
        return None
    if session.last_handoff_artifact_turn == session.turn_count:
        return None
    markdown = _thread_handoff_markdown(
        session=session,
        consolidation=consolidation,
        gov_arc_state=session.gov_arc_state,
    )
    artifact_id = brain.save_artifact(
        capsule_id=capsule_id,
        session_id=session.session_id,
        turn_number=session.turn_count,
        title="Thread handoff reseed",
        content=markdown,
        artifact_type="thread_handoff_md",
    )
    if artifact_id:
        session.handoff_artifact_saved = True
        session.handoff_artifact_count += 1
        session.last_handoff_artifact_turn = session.turn_count
    return artifact_id


def _context_budget_input_estimate(context_budget: Optional[dict[str, Any]]) -> int:
    if not isinstance(context_budget, dict):
        return 0
    return _safe_positive_int(context_budget.get("total_token_estimate"))


def _estimated_output_tokens(response_text: str, provider_output_tokens: Any) -> tuple[int, str]:
    output_tokens = _safe_positive_int(provider_output_tokens)
    if output_tokens:
        return output_tokens, "provider_usage"
    return estimate_context_tokens(response_text), "estimated_chars"


def _estimated_input_tokens(
    context_budget: Optional[dict[str, Any]],
    provider_input_tokens: Any,
) -> tuple[int, str]:
    budget_tokens = _context_budget_input_estimate(context_budget)
    if budget_tokens:
        return budget_tokens, "context_budget_estimate"
    input_tokens = _safe_positive_int(provider_input_tokens)
    if input_tokens:
        return input_tokens, "provider_usage"
    return 0, "unavailable"


def _estimate_turn_cost_usd(
    provider: Optional[str],
    model: Optional[str],
    input_tokens: int,
    output_tokens: int,
) -> tuple[Optional[float], str]:
    key = ((provider or "").strip().lower(), (model or "").strip())
    pricing = _STATIC_CHAT_PRICING_USD_PER_M_TOKEN.get(key)
    if not pricing:
        return None, "unknown_pricing"
    input_per_m, output_per_m = pricing
    estimated = ((input_tokens / 1_000_000) * input_per_m) + (
        (output_tokens / 1_000_000) * output_per_m
    )
    return round(estimated, 6), "static_pricing_estimate"


def _turn_usage_metadata(
    *,
    analyst_adapter: Any,
    context_budget: Optional[dict[str, Any]],
    response_text: str,
    provider_input_tokens: Any,
    provider_output_tokens: Any,
    latency_ms: Any,
) -> dict[str, Any]:
    input_estimate, input_source = _estimated_input_tokens(
        context_budget,
        provider_input_tokens,
    )
    output_estimate, output_source = _estimated_output_tokens(
        response_text,
        provider_output_tokens,
    )
    total_estimate = input_estimate + output_estimate
    selected = _adapter_identity_dict(analyst_adapter)
    estimated_cost, cost_source = _estimate_turn_cost_usd(
        selected.get("provider"),
        selected.get("model"),
        input_estimate,
        output_estimate,
    )
    return {
        "input_token_estimate": input_estimate,
        "output_token_estimate": output_estimate,
        "total_token_estimate": total_estimate,
        "input_token_source": input_source,
        "output_token_source": output_source,
        "latency_ms": _safe_positive_int(latency_ms),
        "estimated_cost_usd": estimated_cost,
        "cost_source": cost_source,
        "cost_is_estimate": True,
        "pricing_note": "Exact provider billing may differ.",
    }


def _turn_runtime_metadata(
    runtime_info: dict[str, Any],
    *,
    analyst_adapter: Any,
    governor: Any,
    governor_checked_this_turn: bool,
    provider_history: Optional[dict[str, Any]] = None,
    usage: Optional[dict[str, Any]] = None,
    failover: Optional[dict[str, Any]] = None,
    governor_trace: Optional[dict[str, Any]] = None,
    gov_arc_state: Optional[GovArcState] = None,
    frontier_assist: Optional[dict[str, Any]] = None,
    timing_breakdown: Optional[dict[str, Any]] = None,
    handoff_transition: Optional[dict[str, Any]] = None,
    session: Optional[ChatSession] = None,
    governed_shadow: Optional[dict[str, Any]] = None,
    holo_voice_diagnostics: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    metadata = dict(runtime_info or {})
    selected = _adapter_identity_dict(analyst_adapter)
    handoff_seed_present = bool(_safe_handoff_transition(handoff_transition))
    autocompact_count = _safe_positive_int(getattr(session, "autocompact_count", 0))
    last_autocompact_turn = _safe_positive_int(getattr(session, "last_autocompact_turn", 0))
    reseed_artifact_count = _safe_positive_int(getattr(session, "handoff_artifact_count", 0))
    last_reseed_turn = _safe_positive_int(getattr(session, "last_handoff_artifact_turn", 0))
    continuity_ledger = _normalized_continuity_ledger(
        getattr(session, "continuity_ledger", {}) if session is not None else {}
    )
    metadata.update(
        {
            "analyst_pool_role": "analyst",
            "analyst_call_mode": "serial_one_per_turn",
            "selection_mode": "round_robin",
            "selected_analyst": selected,
            "selected_provider": selected.get("provider"),
            "selected_model": selected.get("model"),
            "active_pool_count": len(metadata.get("active_pool") or []),
            "context_delivery_mode": "capped_ranked_prompt_slice",
            "durable_memory_store": "HoloBrain/capsule",
            "memory_delivery_mode": "rolling_summary_selected_context",
            "pinned_artifact_policy": "refs_by_default_full_fidelity_when_selected",
            "analyst_receives_full_memory": False,
            "context_budget_warning_tokens": _context_warning_token_limit(),
            "context_budget_hard_limit_tokens": _context_hard_token_limit(),
            "structured_state_object_mode": "active_prompt",
            "gov_arc_state_mode": "active_prompt",
            "baton_pass_mode": "active_prompt",
            "holo4dna_mode": "enabled"
            if _holo4dna_enabled()
            else ("shadow" if _holo4dna_shadow_enabled() else "off"),
            "reseed_present": handoff_seed_present,
            "reseed_mode": "thread_handoff_seed" if handoff_seed_present else "off",
            "thread_handoff_seed_present": handoff_seed_present,
            "autoreseed_enabled": True,
            "auto_compact_enabled": True,
            "auto_compact_min_turns": _autocompact_min_turns(),
            "auto_compact_interval_turns": _autocompact_interval_turns(),
            "rolling_summary_mode": "active_prompt_sliding_window",
            "continuity_ledger_mode": "active_prompt_structured_private",
            "continuity_ledger_counts": {
                key: len(continuity_ledger.get(key) or [])
                for key in _CONTINUITY_LEDGER_KEYS
            },
            "auto_compact_count": autocompact_count,
            "last_auto_compact_turn": last_autocompact_turn or None,
            "reseed_artifact_count": reseed_artifact_count,
            "last_reseed_turn": last_reseed_turn or None,
            "visible_handoff_min_turns": _thread_handoff_min_turns(),
            "visible_handoff_suggested": bool(getattr(session, "handoff_suggested", False)),
        }
    )
    if usage is not None:
        metadata["usage"] = usage
    if provider_history is not None:
        metadata.update(provider_history)
    if failover is not None:
        metadata["failover"] = failover
    if governor_trace is not None:
        metadata["governor_trace"] = governor_trace
    if gov_arc_state is not None:
        metadata["gov_arc_state"] = gov_arc_state.model_dump(mode="json")
    if frontier_assist is not None:
        metadata["frontier_assist"] = frontier_assist
    if timing_breakdown is not None:
        metadata["timing_breakdown"] = timing_breakdown
    if governed_shadow is not None:
        metadata["governed_shadow"] = governed_shadow
    if holo_voice_diagnostics is not None:
        metadata["holo_voice_diagnostics"] = holo_voice_diagnostics
    metadata.update(
        _governor_turn_metadata(
            governor,
            checked_this_turn=governor_checked_this_turn,
        )
    )
    return metadata


def _holo_voice_diagnostics(
    *,
    session: ChatSession,
    analyst_adapter: Any,
    capsule_id: Optional[str],
    incognito: bool,
    capsule_context: dict[str, Any],
    life_context: list[dict[str, Any]],
    last_session: Optional[dict[str, Any]],
    tenor: Optional[str],
    patent_state: str,
    runtime_identity: str,
    system_prompt: str,
    context_budget: Optional[dict[str, Any]],
    provider_history: Optional[dict[str, Any]],
    governed_shadow: Optional[dict[str, Any]],
) -> dict[str, Any]:
    capsule_attached = bool(capsule_id and not incognito)
    ledger = _normalized_continuity_ledger(session.continuity_ledger)
    safe_capsule_keys = [
        str(key)
        for key in (capsule_context or {}).keys()
        if not str(key).startswith("_")
    ]
    selected_gov_context = _governor_capsule_context(capsule_context)
    block_presence = {
        "runtime_identity": "HOLOCHAT RUNTIME IDENTITY:" in (system_prompt or ""),
        "holo_state_object": "HOLO STATE OBJECT" in (system_prompt or ""),
        "gov_arc_state": "GOV ARC STATE" in (system_prompt or ""),
        "captain_brief": bool(tenor) and "CAPTAIN BRIEF" in (system_prompt or ""),
        "life_context": bool(life_context),
        "last_session": bool(last_session),
        "capsule_context": bool(capsule_context),
        "patent_state_nonempty": bool((patent_state or "").strip()),
    }
    risk_flags: list[str] = []
    if incognito:
        risk_flags.append("incognito_memory_stripped")
    elif not capsule_attached:
        risk_flags.append("capsule_not_attached")
    elif not capsule_context:
        risk_flags.append("capsule_context_empty")
    if not block_presence["runtime_identity"]:
        risk_flags.append("runtime_identity_missing")
    if not incognito and not block_presence["holo_state_object"]:
        risk_flags.append("holo_state_object_missing")
    if not incognito and not block_presence["gov_arc_state"]:
        risk_flags.append("gov_arc_state_missing")
    if not incognito and not block_presence["captain_brief"]:
        risk_flags.append("captain_brief_absent")
    if not session.rolling_summary and session.turn_count >= 2:
        risk_flags.append("rolling_summary_absent_after_first_turn")
    omitted = _safe_positive_int((provider_history or {}).get("adapter_history_omitted_messages"))
    if omitted:
        risk_flags.append("adapter_history_truncated")
    if (governed_shadow or {}).get("status") in {None, "off", "skipped"}:
        risk_flags.append("governed_shadow_not_active")

    return {
        "version": "holo_voice_diagnostics_v0.1",
        "status": "attention" if risk_flags else "ok",
        "risk_flags": risk_flags,
        "selected_analyst": _adapter_identity_dict(analyst_adapter),
        "capsule_attached": capsule_attached,
        "incognito": bool(incognito),
        "capsule_context_count": len(safe_capsule_keys),
        "selected_gov_context_count": len(selected_gov_context),
        "life_context_count": len(life_context or []),
        "last_session_present": bool(last_session),
        "rolling_summary_present": bool(session.rolling_summary),
        "critical_constraints_count": len(session.critical_constraints or []),
        "continuity_ledger_counts": {
            key: len(ledger.get(key) or [])
            for key in _CONTINUITY_LEDGER_KEYS
        },
        "block_presence": block_presence,
        "captain_brief_present": block_presence["captain_brief"],
        "context_token_estimate": _safe_positive_int((context_budget or {}).get("total_token_estimate")),
        "adapter_history_messages": _safe_positive_int((provider_history or {}).get("adapter_history_messages")),
        "adapter_history_omitted_messages": omitted,
        "governed_shadow_status": (governed_shadow or {}).get("status", "unknown"),
        "safe_metadata_only": True,
    }


def _run_governed_shadow_for_turn(
    engine: "HoloChatEngine",
    *,
    session: ChatSession,
    user_message: str,
    response_text: str,
    capsule_id: Optional[str],
    capsule_context: dict[str, Any],
    context_budget: Optional[dict[str, Any]],
    search_query: Optional[str],
    search_results: Optional[str],
    incognito: bool,
) -> dict[str, Any]:
    try:
        holo_state = HoloState.from_chat_turn(
            session_id=session.session_id,
            turn_number=session.turn_count,
            user_message=user_message,
            capsule_id=None if incognito else capsule_id,
            user_goal=session.gov_arc_state.user_goal,
            critical_constraints=session.critical_constraints,
            rolling_summary=session.rolling_summary or _rolling_summary_from_history(session.history),
            continuity_ledger=_normalized_continuity_ledger(session.continuity_ledger),
            settled_decisions=session.gov_arc_state.settled_decisions,
            thread_health_score=session.thread_health_score,
            thread_status=session.thread_status,
            required_tools=_required_tools_for_turn(search_query, search_results),
            gov_arc_state=session.gov_arc_state,
        )
        return run_governed_shadow(
            adapters=[*(getattr(engine, "_adapters", []) or []), *(getattr(engine, "_bench", []) or [])],
            user_message=user_message,
            holo_state=holo_state,
            capsule_context={} if incognito else (capsule_context or {}),
            visible_answer=response_text,
            context_token_estimate=(context_budget or {}).get("total_token_estimate"),
        )
    except Exception as exc:
        return {
            "version": "holochat_governed_shadow_v0.1",
            "mode": "shadow",
            "enabled": True,
            "status": "invalid",
            "triggered": False,
            "trigger_reason": "shadow_runtime_exception",
            "call_count": 0,
            "expected_call_count": 5,
            "invalidation_reason": "SHADOW_RUNTIME_EXCEPTION",
            "root_failure": {"type": type(exc).__name__},
            "visible_answer_replaced": False,
            "safe_metadata_only": True,
        }


def _runtime_metadata(
    runtime_profile: str | ResolvedArchitectureProfile,
    active_pool: list[Any],
    bench_pool: list[Any],
) -> dict[str, Any]:
    resolved_profile = runtime_profile if isinstance(runtime_profile, ResolvedArchitectureProfile) else None
    runtime_profile_id = (
        resolved_profile.profile_id
        if resolved_profile is not None
        else str(runtime_profile)
    )
    runtime_class = (
        resolved_profile.runtime_class
        if resolved_profile is not None
        else str(runtime_profile)
    )
    mini_only = runtime_class == "mini_only"
    balanced = runtime_class == BALANCED_RUNTIME_PROFILE
    frontier_assist_enabled = balanced and bool(bench_pool)
    metadata = {
        "release": release_info(),
        "runtime_profile": runtime_profile_id,
        "active_pool": _adapter_pool_metadata(active_pool),
        "bench_pool": _adapter_pool_metadata(bench_pool),
        "frontier_enabled": not mini_only,
        "frontier_assist_enabled": frontier_assist_enabled,
        "fallback_policy": (
            "no_frontier_fallback"
            if mini_only
            else ("gov_triggered_frontier_assist" if balanced else "bench_failover_enabled")
        ),
        "serial_call": True,
        "parallel_fanout": False,
    }
    if resolved_profile is not None:
        metadata.update(
            {
                "architecture_profile": resolved_profile.architecture_profile,
                "alignment_profile": resolved_profile.alignment_profile,
                "registry_profile": resolved_profile.registry_profile,
                "governor_lane": resolved_profile.governor_lane,
                "runtime_class": resolved_profile.runtime_class,
                "architecture_profile_source": resolved_profile.source,
                "architecture_manifest_path": resolved_profile.manifest_path,
                "architecture_manifest_version": resolved_profile.manifest_version,
                "architecture_selector_source": resolved_profile.selector_source,
                "architecture_profile_status": resolved_profile.status,
                "architecture_profile_locked": resolved_profile.status == "locked",
                "architecture_override_policy": "manifest_named_profile_only",
                "runtime_behavior": resolved_profile.runtime_behavior,
                "pool_strategy": resolved_profile.pool_strategy,
                "configured_active_provider_order": list(resolved_profile.active_provider_order),
            }
        )
    return metadata


def _select_runtime_pools(
    profile: Optional[str] = None,
    *,
    fast_loader=None,
    frontier_loader=None,
) -> tuple[ResolvedArchitectureProfile, list[Any], list[Any]]:
    if profile is not None:
        if not isinstance(profile, str):
            raise RuntimeError("HoloChat runtime profile override must be a manifest profile id.")
        if profile.strip() != DEFAULT_LOCKED_ARCHITECTURE_PROFILE:
            raise RuntimeError(
                "HoloChat runtime profile override is disabled; "
                f"only {DEFAULT_LOCKED_ARCHITECTURE_PROFILE!r} may be resolved."
            )
        resolved_profile = _holochat_runtime_profile(
            profile,
            selector_source="locked_explicit_constant",
        )
    else:
        resolved_profile = _holochat_runtime_profile()
    frontier_loader = frontier_loader or load_adapters

    if resolved_profile.pool_strategy == "frontier_ordered_full_registry":
        active_pool, bench_pool = frontier_loader()
        active_pool, bench_pool = _holochat_ordered_pool(
            active_pool,
            bench_pool,
            resolved_profile.active_provider_order,
        )
        if not active_pool:
            raise RuntimeError("HoloChat frontier runtime has no active adapters.")
        return resolved_profile, active_pool, bench_pool

    raise RuntimeError(
        f"Unsupported locked architecture pool_strategy: {resolved_profile.pool_strategy}"
    )


def _is_mid_resolution(last_assistant_message: str) -> bool:
    """
    Heuristic: return True if the last assistant message looks like it's in
    the middle of a multi-step task or numbered walkthrough.
    Prevents Governor rotation mid-way through active work.
    """
    if not last_assistant_message:
        return False
    text = last_assistant_message
    has_numbered_steps = bool(_re.search(r'^\s*[1-9]\.\s', text, _re.MULTILINE))
    continuation_phrases = [
        "next step", "step 1", "step 2", "step 3", "step 4", "step 5",
        "continuing from", "part 1", "part 2",
        "to summarize what we've covered so far",
        "here's what we have so far",
    ]
    has_continuation = any(phrase in text.lower() for phrase in continuation_phrases)
    return has_numbered_steps or has_continuation


def _should_rotate_governor(session: "ChatSession") -> bool:
    """
    Returns True if the Governor should rotate to a fresh provider.

    ALL conditions must be true:
      - At least governor_rotation_threshold turns since last rotation
      - Thread health is GREEN or YELLOW (not RED — don't destabilize a late thread)
      - No active work appears to be mid-resolution
    """
    if session.governor_provider is None:
        return True  # first turn — must lock

    turns_since = session.turn_count - session.governor_locked_since
    if turns_since < session.governor_rotation_threshold:
        return False

    if session.thread_health_level == "RED":
        return False

    last_assistant = next(
        (m["content"] for m in reversed(session.history) if m["role"] == "assistant"),
        ""
    )
    if _is_mid_resolution(last_assistant):
        return False

    return True


# ---------------------------------------------------------------------------
# Chat engine
# ---------------------------------------------------------------------------

class HoloChatEngine:
    """
    Manages the round-robin multi-model chat loop.
    One instance per application; sessions are keyed by session_id.
    """

    def __init__(self):
        self._resolved_architecture_profile, self._adapters, self._bench = _select_runtime_pools()
        self._runtime_profile = self._resolved_architecture_profile.profile_id
        self._runtime_info = _runtime_metadata(
            self._resolved_architecture_profile,
            self._adapters,
            self._bench,
        )
        governor_provider = self._resolved_architecture_profile.governor_provider
        self._governor = GovernorAdapter(
            self._adapters,
            fixed_governor=governor_provider,
        ) # separate controller; not another analyst answer
        if governor_provider:
            self._governor.lock_to_provider(governor_provider)
        self._brain    = ProjectBrain()
        self._holo_context_builder = HoloContextBuilder()
        self._holo_router = None
        logger.info(
            f"HoloChatEngine initialized. Runtime profile: {self._runtime_profile} | Active: "
            + ", ".join(a.provider for a in self._adapters)
            + (" | Bench: " + ", ".join(a.provider for a in self._bench) if self._bench else "")
            + " | GovernorAdapter ready"
        )

    def runtime_status(self) -> dict[str, Any]:
        """Return safe, user-visible runtime identity and model-roster state."""
        profile = getattr(self, "_resolved_architecture_profile", None)
        runtime_info = dict(getattr(self, "_runtime_info", {}) or {})
        active_pool = _adapter_pool_metadata(getattr(self, "_adapters", []) or [])
        bench_pool = _adapter_pool_metadata(getattr(self, "_bench", []) or [])
        governor = getattr(self, "_governor", None)
        governor_meta = _governor_turn_metadata(governor, checked_this_turn=False)
        return {
            "status": "initialized",
            "release": release_info(),
            "visible_chat_lane": {
                "runtime_profile": getattr(profile, "profile_id", runtime_info.get("runtime_profile")),
                "runtime_class": getattr(profile, "runtime_class", runtime_info.get("runtime_class")),
                "architecture_profile_status": getattr(profile, "status", runtime_info.get("architecture_profile_status")),
                "architecture_manifest_version": getattr(profile, "manifest_version", runtime_info.get("architecture_manifest_version")),
                "architecture_manifest_path": getattr(profile, "manifest_path", runtime_info.get("architecture_manifest_path")),
                "runtime_behavior": getattr(profile, "runtime_behavior", runtime_info.get("runtime_behavior")),
                "pool_strategy": getattr(profile, "pool_strategy", runtime_info.get("pool_strategy")),
                "model_selection": "fixed_manifest_order",
                "gov_can_choose_models": False,
                "analyst_rotation_order": active_pool,
                "bench_pool": bench_pool,
                "selection_mode": "round_robin",
                "visible_answer_mode": "one_selected_analyst_per_turn",
            },
            "governor": {
                "role": "controller_check_layer",
                "configured_provider": getattr(profile, "governor_provider", None),
                "loaded_provider": governor_meta.get("governor_provider"),
                "loaded_model": governor_meta.get("governor_model"),
                "status": "configured" if governor_meta.get("governor_present") else "off",
                "visible_answer_producer": False,
            },
            "governed_shadow_lane": {
                "version": GOVERNED_SHADOW_VERSION,
                "enabled": governed_shadow_enabled(),
                "env_var": GOVERNED_SHADOW_ENV,
                "trigger_policy": "hard_chat_or_thread_health_only",
                "visible_answer_replaced": False,
                "expected_call_sequence": [dict(item) for item in GOVERNED_SHADOW_ROSTER],
                "model_selection": "fixed_roster_order",
                "gov_can_choose_models": False,
            },
            "state_and_memory": {
                "context_delivery_mode": runtime_info.get("context_delivery_mode", "capped_ranked_prompt_slice"),
                "memory_delivery_mode": runtime_info.get("memory_delivery_mode", "rolling_summary_selected_context"),
                "structured_state_object_mode": runtime_info.get("structured_state_object_mode", "active_prompt"),
                "baton_pass_mode": runtime_info.get("baton_pass_mode", "active_prompt"),
                "rolling_summary_mode": runtime_info.get("rolling_summary_mode", "active_prompt_sliding_window"),
                "continuity_ledger_mode": runtime_info.get("continuity_ledger_mode", "active_prompt_structured_private"),
                "analyst_receives_full_memory": runtime_info.get("analyst_receives_full_memory", False),
                "durable_memory_store": runtime_info.get("durable_memory_store", "HoloBrain/capsule"),
            },
            "safety": {
                "raw_prompts_exposed": False,
                "raw_memory_exposed": False,
                "provider_error_bodies_exposed": False,
                "api_keys_exposed": False,
            },
        }

    def get_or_create_session(self, session_id: Optional[str] = None) -> ChatSession:
        if session_id and session_id in _sessions:
            return _sessions[session_id]
        new_id  = session_id or str(uuid.uuid4())
        session = ChatSession(session_id=new_id)

        # Restore history from Supabase if the session_id is known but not in memory
        # (e.g. after a server restart)
        if session_id:
            prior = self._brain.load_chat_history(session_id)
            if prior:
                session.history      = prior
                session.turn_count   = sum(1 for m in prior if m["role"] == "user")
                session.rotation_index = session.turn_count % len(self._adapters)
                session.rolling_summary = _rolling_summary_from_history(prior)
                session.continuity_ledger = _continuity_ledger_from_history(prior)
                logger.info(f"Restored session {session_id[:8]} from brain ({session.turn_count} turns).")

        _sessions[new_id] = session
        logger.info(f"Chat session ready: {new_id[:8]}")
        return session

    def send_message(self, session_id: str, user_message: str,
                     capsule_id: Optional[str] = None,
                     images: Optional[List[Dict[str, Any]]] = None,
                     incognito: bool = False,
                     handoff_transition: Optional[dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process one user message. Returns Holo's response + metadata.
        The caller should use session_id from the returned dict for follow-up turns.

        incognito=True: blind mode — no capsule context, no Governor memory, no life portrait
        injected. Base system prompt only. Used for unbiased evaluation runs.
        """
        session             = self.get_or_create_session(session_id)
        session.last_active = time.time()
        turn_started_at = _timer_start()
        timings: dict[str, int] = {}

        # Incognito: strip all memory — only base system prompt reaches the model
        memory_timer = _timer_start()
        if incognito:
            capsule_context = {}
            life_context    = []
            last_session    = None
        else:
            capsule_context = self._brain.get_capsule_context(capsule_id) if capsule_id else {}
            life_context    = self._brain.load_life_context(capsule_id) if capsule_id else []
            last_session    = self._brain.load_last_consolidation(capsule_id) if capsule_id and session.turn_count == 0 else None
        _add_timing(timings, "memory_context_ms", memory_timer)

        active_handoff_transition = None if incognito else _apply_handoff_transition_to_session(
            session,
            handoff_transition,
        )

        # Rotate through the active mini pool so every configured analyst gets turns.
        adapter = _select_analyst_adapter(session, self._adapters)
        initial_adapter = adapter
        session.turn_count     += 1
        adapter_history = _bounded_adapter_history(session.history)
        provider_history_stats = _provider_history_metadata(
            adapter_history,
            total_history_messages=len(session.history),
        )
        governor_context = _governor_capsule_context(capsule_context)

        gov_pre_timer = _timer_start()
        # Governor rotation policy:
        # Lock to one provider for 7–11 turns. Rotate only when the thread is
        # healthy and no active work is mid-resolution. The no-same-family rule
        # is enforced by prepare_for_turn() on every rotation.
        if _should_rotate_governor(session):
            self._governor.prepare_for_turn(adapter)
            session.governor_provider        = self._governor.provider
            session.governor_locked_since    = session.turn_count
            session.governor_rotation_threshold = random.randint(7, 11)
            if session.turn_count > 1:
                logger.info(
                    f"Governor rotated → {session.governor_provider} "
                    f"(next rotation in {session.governor_rotation_threshold} turns)"
                )
        else:
            self._governor.lock_to_provider(session.governor_provider)

        # Governor runs the instruments: temperature + search decision
        temperature  = self._governor.assess_chat_temperature(user_message, adapter_history)
        governor_search_query = self._governor.should_search(user_message, adapter_history)

        # Governor thinks about the human — skipped in incognito (would introduce bias)
        thought = None if incognito else self._governor.surface_thought(adapter_history, governor_context, baton_pass=_health_context(session))
        tenor   = None if incognito else self._governor.assess_tenor(adapter_history, governor_context, turn_count=session.turn_count, analyst_provider=adapter.provider)
        _add_timing(timings, "governor_pre_ms", gov_pre_timer)

        web_timer = _timer_start()
        search_query, search_results, web_trace = _run_web_search_for_turn(user_message, governor_search_query)
        _add_timing(timings, "web_search_ms", web_timer)
        search_attempted = bool(search_query)
        search_succeeded = bool(search_results)
        web_status = web_trace["status"]
        _update_gov_arc_state(
            session,
            user_message=user_message,
            tenor=tenor,
            web_trace=web_trace,
        )
        required_tools = _required_tools_for_turn(search_query, search_results)
        patent_state = "" if incognito else _patent_state_block(
            session,
            user_message=user_message,
            required_tools=required_tools,
        )

        frontier_assist_enabled = (
            getattr(
                getattr(self, "_resolved_architecture_profile", None),
                "runtime_class",
                getattr(self, "_runtime_profile", ""),
            ) == BALANCED_RUNTIME_PROFILE
            and bool(self._bench)
            and not incognito
        )
        frontier_assist_reason = (
            _balanced_frontier_assist_reason(user_message=user_message, tenor=tenor)
            if frontier_assist_enabled
            else None
        )
        frontier_assist_adapter = (
            _select_frontier_assist_adapter(
                self._bench,
                initial_adapter=initial_adapter,
                governor=self._governor,
            )
            if frontier_assist_reason
            else None
        )
        if frontier_assist_adapter is not None:
            adapter = frontier_assist_adapter
        frontier_assist = _frontier_assist_metadata(
            enabled=frontier_assist_enabled,
            reason=frontier_assist_reason,
            selected_adapter=frontier_assist_adapter,
        )

        context_timer = _timer_start()
        # Build enriched message — search results injected for the model only,
        # not stored in history (history stays clean with the original message)
        enriched_message = user_message
        if search_results:
            enriched_message = (
                f"{user_message}\n\n"
                f"[BACKGROUND CONTEXT: The following search results were retrieved to help you answer. "
                f"Use them silently — do not mention, quote, or reference that a search was performed. "
                f"If the results are irrelevant to the question, ignore them entirely.]\n\n"
                f"{search_results}"
            )
            logger.info(f"  Search query: '{search_query}'")

        logger.info(
            f"Chat turn {session.turn_count} | session={session.session_id[:8]} | "
            f"analyst={adapter.provider} | governor={self._governor.provider} | temp={temperature:.2f}"
            + (" | INCOGNITO" if incognito else "")
        )

        runtime_identity = build_runtime_identity_block(
            getattr(self, "_runtime_info", {}),
            capsule_attached=bool(capsule_id and not incognito),
        )

        # Inject runtime identity + thread-health context + portrait + working memory + Governor brief.
        # Incognito: keeps runtime identity but strips memory context.
        system_prompt = HOLO_CHAT_SYSTEM_PROMPT + "\n\n" + runtime_identity
        if not incognito:
            system_prompt += (
                "\n\n" + _health_context(session)
                + "\n\n" + patent_state
                + "\n\n" + _gov_arc_state_block(session.gov_arc_state)
                + ("\n\n" + _thread_handoff_transition_block(active_handoff_transition) if active_handoff_transition else "")
                + ("\n\n" + _life_context_block(life_context) if life_context else "")
                + ("\n\n" + _last_session_block(last_session) if last_session else "")
                + ("\n\n" + _capsule_context_block(capsule_context) if capsule_context else "")
                + ("\n\nCAPTAIN BRIEF — READ + DIRECTIVE (private, never surface to user):\n" + tenor if tenor else "")
            )

        context_budget = _runtime_context_budget(
            session=session,
            adapter_history=adapter_history,
            user_message=user_message,
            capsule_context=capsule_context,
            life_context=life_context,
            last_session=last_session,
            tenor=tenor,
            search_results=search_results,
            images=images,
            incognito=incognito,
            runtime_identity=runtime_identity,
            handoff_transition=active_handoff_transition,
            patent_state=patent_state,
        )
        _enforce_runtime_context_budget(context_budget)

        holo4dna_shadow = None
        if _holo4dna_shadow_enabled():
            try:
                if self._holo_router is None:
                    self._holo_router = HoloRouter(self._adapters)
                holo4dna_shadow = _build_holo4dna_shadow_turn(
                    session=session,
                    capsule_id=capsule_id,
                    user_message=user_message,
                    runtime_adapter=adapter,
                    router=self._holo_router,
                    context_builder=self._holo_context_builder,
                    previous_route=session.holo4dna_previous_route,
                    recent_history=adapter_history,
                    capsule_context=capsule_context,
                    life_context=life_context,
                    last_session=last_session,
                    search_query=search_query,
                    search_results=search_results,
                    incognito=incognito,
                    runtime_info=getattr(self, "_runtime_info", {}),
                    capsule_attached=bool(capsule_id and not incognito),
                )
                session.holo4dna_previous_route = holo4dna_shadow.previous_route
            except Exception as exc:
                logger.warning("HoloChat 4DNA shadow trace failed: %s", exc)
        _add_timing(timings, "context_assembly_ms", context_timer)

        # Call the adapter. If the selected mini is down, skip forward through
        # the active pool before falling back to any bench pool in non-mini profiles.
        analyst_timer = _timer_start()
        failover_attempts: list[dict[str, Optional[str]]] = []
        last_err: Optional[Exception] = None
        response_text = ""
        in_tok = out_tok = 0
        candidate_order = _adapter_candidate_order_for_attachments(self._adapters, adapter, images)
        for candidate in candidate_order:
            try:
                response_text, in_tok, out_tok = candidate.chat_call(
                    system_prompt, adapter_history, enriched_message, temperature,
                    images=images or None,
                )
                adapter = candidate
                break
            except Exception as exc:
                failover_attempts.append(_safe_adapter_error(candidate, exc))
                last_err = exc
                logger.warning(
                    "Analyst %s/%s failed with %s; trying next available analyst",
                    getattr(candidate, "provider", "unknown"),
                    getattr(candidate, "model_id", getattr(candidate, "model", "unknown")),
                    exc.__class__.__name__,
                )
        else:
            bench_candidates = [b for b in self._bench if b.provider != initial_adapter.provider]
            if _has_pdf_attachments(images):
                pdf_bench_candidates = [b for b in bench_candidates if _adapter_accepts_native_pdf(b)]
                bench_candidates = pdf_bench_candidates or bench_candidates
            if not bench_candidates:
                if last_err is not None:
                    raise last_err
                raise RuntimeError("HoloChat runtime has no available analyst adapters.")
            fallback = random.choice(bench_candidates)
            try:
                response_text, in_tok, out_tok = fallback.chat_call(
                    system_prompt, adapter_history, enriched_message, temperature,
                    images=images or None,
                )
                adapter = fallback
            except Exception as exc:
                failover_attempts.append(_safe_adapter_error(fallback, exc))
                raise
        elapsed_ms = _elapsed_timer_ms(analyst_timer)
        _add_timing(timings, "analyst_ms", analyst_timer)
        failover = _analyst_failover_metadata(
            initial_adapter=initial_adapter,
            final_adapter=adapter,
            attempts=failover_attempts,
            policy=(
                "balanced_frontier_assist_then_next_mini"
                if frontier_assist.get("triggered")
                else "try_next_active_mini_then_bench"
            ),
        )

        if holo4dna_shadow is not None:
            actual_analyst = _adapter_identity_dict(adapter)
            recorded_analyst = holo4dna_shadow.metadata["route"]["runtime_analyst"]
            if actual_analyst != recorded_analyst:
                holo4dna_shadow.metadata["route"]["runtime_analyst_after_failover"] = actual_analyst
                holo4dna_shadow.trace.extra_metadata["runtime_analyst_after_failover"] = actual_analyst

        gov_post_timer = _timer_start()
        # Hallucination check — Governor scans for specific low-confidence claims
        # and verifies them against live search. Silent on clean responses.
        response_text, flagged_claims = self._governor.verify_claims(
            response_text, web_search.search
        )
        if flagged_claims:
            corrections = [f["correction"] for f in flagged_claims if f.get("correction")]
            if corrections:
                # Quietly inline the correction so the user gets accurate information
                note = " · ".join(corrections)
                response_text += f"\n\n*One thing worth correcting: {note}*"

        path_generator = getattr(self._governor, "generate_conversation_paths", None)
        conversation_paths = []
        if path_generator and not incognito:
            conversation_paths = path_generator(
                history=adapter_history,
                capsule_context=governor_context,
                user_message=user_message,
                response_text=response_text,
                tenor=tenor or "",
                thread_health_level=session.thread_health_level,
                gov_arc_state=session.gov_arc_state.model_dump(mode="json"),
            )
        _add_timing(timings, "governor_post_ms", gov_post_timer)

        # Extract and save any HTML artifacts — after claims check, before history commit
        artifacts_saved = []
        if capsule_id and not incognito:
            artifacts_saved = _extract_and_save_artifacts(
                self._brain, response_text, capsule_id, session.session_id, session.turn_count
            )

        # Commit both turns to history
        session.history.append({"role": "user",      "content": user_message})
        session.history.append({"role": "assistant",  "content": response_text})
        if not incognito:
            _update_rolling_summary_after_turn(
                session,
                user_message=user_message,
                response_text=response_text,
            )

        # Link session to capsule on first turn — skipped in incognito
        if capsule_id and session.turn_count == 1 and not incognito:
            self._brain.set_capsule_context(capsule_id, "last_session_id", session.session_id)
            self._brain.append_session_history(capsule_id, session.session_id, user_message)

        # Governor learns — extract any new facts about the user and persist them
        # Skipped in incognito: blind sessions must not pollute the capsule portrait
        memory_extraction_attempted = False
        memory_writes_count = 0
        if capsule_id and not incognito:
            memory_extraction_attempted = True
            gov_post_timer = _timer_start()
            updates = self._governor.extract_context_updates(session.history, governor_context)
            for key, value in updates.items():
                self._brain.set_capsule_context(capsule_id, key, value)
            memory_writes_count = len(updates)
            _add_timing(timings, "governor_post_ms", gov_post_timer)
            if updates:
                logger.info(f"Capsule context updated for {capsule_id[:8]}: {list(updates.keys())}")

        if not incognito:
            _update_continuity_ledger_after_turn(
                session,
                user_message=user_message,
                response_text=response_text,
                conversation_paths=conversation_paths,
                artifacts_saved=artifacts_saved,
                flagged_claims=flagged_claims,
                memory_writes_count=memory_writes_count,
            )

        # Governor consolidates — skipped in incognito
        if _claim_autocompact_for_context_window(
            session,
            capsule_id=capsule_id,
            incognito=incognito,
        ):
            def _consolidate():
                try:
                    result = self._governor.consolidate_session(
                        _bounded_consolidation_history(session.history),
                        governor_context,
                        session.session_id,
                    )
                    if result.get("session_note"):
                        self._brain.save_consolidation(
                            capsule_id, session.session_id, result["session_note"]
                        )
                    if result.get("life_context"):
                        self._brain.upsert_life_context(capsule_id, result["life_context"])
                    _save_thread_handoff_artifact(
                        self._brain,
                        capsule_id=capsule_id,
                        session=session,
                        consolidation=result,
                    )
                    logger.info(
                        f"Consolidation complete for {capsule_id[:8]}: "
                        f"{len(result.get('life_context', []))} life_context entries written."
                    )
                except Exception as e:
                    logger.warning(f"Consolidation failed: {e}")
            threading.Thread(target=_consolidate, daemon=True).start()

        # Governor names the thread after turn 2 — enough context to know the topic
        if capsule_id and session.turn_count == 2 and not incognito:
            _hist = list(session.history)
            _sid  = session.session_id
            _cid  = capsule_id
            def _name_thread():
                try:
                    name = self._governor.name_session(_hist)
                    if name:
                        self._brain.update_session_name(_cid, _sid, name)
                except Exception as e:
                    logger.warning(f"Thread naming failed: {e}")
            threading.Thread(target=_name_thread, daemon=True).start()

        # Persist to Supabase — capsule_id links session to user permanently
        persistence_timer = _timer_start()
        self._brain.save_chat_turn(
            session_id    = session.session_id,
            turn_number   = session.turn_count,
            user_message  = user_message,
            holo_response = response_text,
            provider      = adapter.provider,
            temperature   = temperature,
            capsule_id    = capsule_id,
        )
        _add_timing(timings, "persistence_ms", persistence_timer)

        if holo4dna_shadow is not None:
            holo4dna_shadow.trace.memory_extraction_attempted = memory_extraction_attempted
            holo4dna_shadow.trace.memory_writes_count = memory_writes_count
            log_trace(holo4dna_shadow.trace, logger=logger)

        # Signal a thread handoff when health is RED
        handoff = _handoff_for_context_window(session)

        _update_gov_arc_state(
            session,
            user_message=user_message,
            tenor=tenor,
            web_trace=web_trace,
            conversation_paths=conversation_paths,
            memory_writes_count=memory_writes_count,
            handoff=handoff,
        )

        usage = _turn_usage_metadata(
            analyst_adapter=adapter,
            context_budget=context_budget,
            response_text=response_text,
            provider_input_tokens=in_tok,
            provider_output_tokens=out_tok,
            latency_ms=elapsed_ms,
        )
        governed_shadow = _run_governed_shadow_for_turn(
            self,
            session=session,
            user_message=user_message,
            response_text=response_text,
            capsule_id=capsule_id,
            capsule_context=capsule_context,
            context_budget=context_budget,
            search_query=search_query,
            search_results=search_results,
            incognito=incognito,
        )
        holo_voice_diagnostics = _holo_voice_diagnostics(
            session=session,
            analyst_adapter=adapter,
            capsule_id=capsule_id,
            incognito=incognito,
            capsule_context=capsule_context,
            life_context=life_context,
            last_session=last_session,
            tenor=tenor,
            patent_state=patent_state,
            runtime_identity=runtime_identity,
            system_prompt=system_prompt,
            context_budget=context_budget,
            provider_history=provider_history_stats,
            governed_shadow=governed_shadow,
        )
        resolved_runtime_profile = getattr(self, "_resolved_architecture_profile", None) or _holochat_runtime_profile()
        runtime_info = getattr(self, "_runtime_info", None) or _runtime_metadata(
            resolved_runtime_profile,
            self._adapters,
            self._bench,
        )
        runtime = _turn_runtime_metadata(
            runtime_info,
            analyst_adapter=adapter,
            governor=self._governor,
            governor_checked_this_turn=True,
            usage=usage,
            provider_history=provider_history_stats,
            failover=failover,
            governor_trace=_governor_trace_metadata(
                web_trace=web_trace,
                incognito=incognito,
                memory_extraction_attempted=memory_extraction_attempted,
                memory_writes_count=memory_writes_count,
                conversation_paths_count=len(conversation_paths),
                thread_health_level=session.thread_health_level,
            ),
            gov_arc_state=session.gov_arc_state,
            frontier_assist=frontier_assist,
            timing_breakdown=_timing_breakdown_metadata(
                timings,
                turn_started_at=turn_started_at,
            ),
            handoff_transition=active_handoff_transition,
            session=session,
            governed_shadow=governed_shadow,
            holo_voice_diagnostics=holo_voice_diagnostics,
        )

        return {
            "session_id":          session.session_id,
            "response":            response_text,
            "turn_number":         session.turn_count,
            "thread_health_score": session.thread_health_score,
            "thread_health_level": session.thread_health_level,
            "elapsed_ms":          elapsed_ms,
            "tokens":              {"input": in_tok, "output": out_tok},
            "thought":             thought,
            "handoff":             handoff,
            "incognito":           incognito,
            "context_budget":      context_budget,
            "searched":            search_succeeded,
            "search_query":        search_query if search_succeeded else None,
            "web_status":          web_status,
            "_provider":           adapter.provider,
            "_governor":           session.governor_provider,
            "_governor_turns_held": session.turn_count - session.governor_locked_since,
            "_temperature":        temperature,
            "artifacts":           artifacts_saved,
            "usage":               usage,
            "runtime":             runtime,
            "conversation_paths":   conversation_paths,
            **({"holo4dna": holo4dna_shadow.metadata} if holo4dna_shadow else {}),
        }

    def stream_message(self, session_id: str, user_message: str,
                       capsule_id: Optional[str] = None,
                       images: Optional[List[Dict[str, Any]]] = None,
                       incognito: bool = False,
                       handoff_transition: Optional[dict[str, Any]] = None):
        """
        Generator variant of send_message.

        Yields strings (text chunks) while the analyst streams its response,
        then yields a single sentinel dict with metadata once streaming is complete:
          {"done": True, "session_id": ..., "turn_number": ..., "thought": ...,
           "thread_health_level": ..., "thread_health_score": ..., "searched": bool,
           "artifacts": [...], "handoff": ...}

        The Governor's pre-turn work (temperature, search decision, tenor) runs
        synchronously before streaming starts. Post-turn work (context extraction,
        consolidation, thread naming, Supabase persist) runs in a background thread
        after the stream completes so the caller never blocks on it.
        """
        session             = self.get_or_create_session(session_id)
        session.last_active = time.time()
        turn_started_at = _timer_start()
        timings: dict[str, int] = {}

        memory_timer = _timer_start()
        if incognito:
            capsule_context = {}
            life_context    = []
            last_session    = None
        else:
            capsule_context = self._brain.get_capsule_context(capsule_id) if capsule_id else {}
            life_context    = self._brain.load_life_context(capsule_id) if capsule_id else []
            last_session    = self._brain.load_last_consolidation(capsule_id) if capsule_id and session.turn_count == 0 else None
        _add_timing(timings, "memory_context_ms", memory_timer)

        active_handoff_transition = None if incognito else _apply_handoff_transition_to_session(
            session,
            handoff_transition,
        )

        adapter = _select_analyst_adapter(session, self._adapters)
        initial_adapter = adapter
        session.turn_count     += 1
        adapter_history = _bounded_adapter_history(session.history)
        provider_history_stats = _provider_history_metadata(
            adapter_history,
            total_history_messages=len(session.history),
        )
        governor_context = _governor_capsule_context(capsule_context)

        gov_pre_timer = _timer_start()
        if _should_rotate_governor(session):
            self._governor.prepare_for_turn(adapter)
            session.governor_provider             = self._governor.provider
            session.governor_locked_since         = session.turn_count
            session.governor_rotation_threshold   = random.randint(7, 11)
        else:
            self._governor.lock_to_provider(session.governor_provider)

        temperature  = self._governor.assess_chat_temperature(user_message, adapter_history)
        governor_search_query = self._governor.should_search(user_message, adapter_history)
        thought      = None if incognito else self._governor.surface_thought(adapter_history, governor_context, baton_pass=_health_context(session))
        tenor        = None if incognito else self._governor.assess_tenor(adapter_history, governor_context, turn_count=session.turn_count, analyst_provider=adapter.provider)
        _add_timing(timings, "governor_pre_ms", gov_pre_timer)

        web_timer = _timer_start()
        search_query, search_results, web_trace = _run_web_search_for_turn(user_message, governor_search_query)
        _add_timing(timings, "web_search_ms", web_timer)
        search_attempted = bool(search_query)
        searched = bool(search_results)
        web_status = web_trace["status"]
        _update_gov_arc_state(
            session,
            user_message=user_message,
            tenor=tenor,
            web_trace=web_trace,
        )
        required_tools = _required_tools_for_turn(search_query, search_results)
        patent_state = "" if incognito else _patent_state_block(
            session,
            user_message=user_message,
            required_tools=required_tools,
        )

        frontier_assist_enabled = (
            getattr(
                getattr(self, "_resolved_architecture_profile", None),
                "runtime_class",
                getattr(self, "_runtime_profile", ""),
            ) == BALANCED_RUNTIME_PROFILE
            and bool(self._bench)
            and not incognito
        )
        frontier_assist_reason = (
            _balanced_frontier_assist_reason(user_message=user_message, tenor=tenor)
            if frontier_assist_enabled
            else None
        )
        frontier_assist_adapter = (
            _select_frontier_assist_adapter(
                self._bench,
                initial_adapter=initial_adapter,
                governor=self._governor,
            )
            if frontier_assist_reason
            else None
        )
        if frontier_assist_adapter is not None:
            adapter = frontier_assist_adapter
        frontier_assist = _frontier_assist_metadata(
            enabled=frontier_assist_enabled,
            reason=frontier_assist_reason,
            selected_adapter=frontier_assist_adapter,
        )

        context_timer = _timer_start()
        enriched_message = user_message
        if search_results:
            enriched_message = (
                f"{user_message}\n\n"
                f"[BACKGROUND CONTEXT: The following search results were retrieved to help you answer. "
                f"Use them silently — do not mention, quote, or reference that a search was performed. "
                f"If the results are irrelevant to the question, ignore them entirely.]\n\n"
                f"{search_results}"
            )

        runtime_identity = build_runtime_identity_block(
            getattr(self, "_runtime_info", {}),
            capsule_attached=bool(capsule_id and not incognito),
        )

        system_prompt = HOLO_CHAT_SYSTEM_PROMPT + "\n\n" + runtime_identity
        if not incognito:
            system_prompt += (
                "\n\n" + _health_context(session)
                + "\n\n" + patent_state
                + "\n\n" + _gov_arc_state_block(session.gov_arc_state)
                + ("\n\n" + _thread_handoff_transition_block(active_handoff_transition) if active_handoff_transition else "")
                + ("\n\n" + _life_context_block(life_context) if life_context else "")
                + ("\n\n" + _last_session_block(last_session) if last_session else "")
                + ("\n\n" + _capsule_context_block(capsule_context) if capsule_context else "")
                + ("\n\nCAPTAIN BRIEF — READ + DIRECTIVE (private, never surface to user):\n" + tenor if tenor else "")
            )

        context_budget = _runtime_context_budget(
            session=session,
            adapter_history=adapter_history,
            user_message=user_message,
            capsule_context=capsule_context,
            life_context=life_context,
            last_session=last_session,
            tenor=tenor,
            search_results=search_results,
            images=images,
            incognito=incognito,
            runtime_identity=runtime_identity,
            handoff_transition=active_handoff_transition,
            patent_state=patent_state,
        )
        _enforce_runtime_context_budget(context_budget)

        holo4dna_shadow = None
        if _holo4dna_shadow_enabled():
            try:
                if self._holo_router is None:
                    self._holo_router = HoloRouter(self._adapters)
                holo4dna_shadow = _build_holo4dna_shadow_turn(
                    session=session,
                    capsule_id=capsule_id,
                    user_message=user_message,
                    runtime_adapter=adapter,
                    router=self._holo_router,
                    context_builder=self._holo_context_builder,
                    previous_route=session.holo4dna_previous_route,
                    recent_history=adapter_history,
                    capsule_context=capsule_context,
                    life_context=life_context,
                    last_session=last_session,
                    search_query=search_query,
                    search_results=search_results,
                    incognito=incognito,
                    runtime_info=getattr(self, "_runtime_info", {}),
                    capsule_attached=bool(capsule_id and not incognito),
                )
                session.holo4dna_previous_route = holo4dna_shadow.previous_route
            except Exception as exc:
                logger.warning("HoloChat 4DNA stream shadow trace failed: %s", exc)
        _add_timing(timings, "context_assembly_ms", context_timer)

        # Signal search before tokens arrive so the UI can show the indicator
        if search_attempted:
            yield {"searching": True}

        # Stream analyst response token by token. If a provider fails before it
        # emits content, skip to the next active mini instead of ending the turn.
        accumulated = []
        in_tok = out_tok = 0
        analyst_timer = _timer_start()
        failover_attempts: list[dict[str, Optional[str]]] = []
        last_err: Optional[Exception] = None
        stream_completed = False
        candidate_order = _adapter_candidate_order_for_attachments(self._adapters, adapter, images)
        for candidate in candidate_order:
            candidate_chunks: list[str] = []
            emitted = False
            try:
                for chunk in candidate.stream_chat_call(
                    system_prompt, adapter_history, enriched_message, temperature, images=images or None
                ):
                    if isinstance(chunk, dict) and chunk.get("done"):
                        in_tok  = chunk.get("in_tok", 0)
                        out_tok = chunk.get("out_tok", 0)
                    else:
                        emitted = True
                        candidate_chunks.append(chunk)
                        yield chunk
                accumulated.extend(candidate_chunks)
                adapter = candidate
                stream_completed = True
                break
            except Exception as exc:
                if emitted:
                    raise
                failover_attempts.append(_safe_adapter_error(candidate, exc))
                last_err = exc
                logger.warning(
                    "Streaming analyst %s/%s failed with %s before output; trying next available analyst",
                    getattr(candidate, "provider", "unknown"),
                    getattr(candidate, "model_id", getattr(candidate, "model", "unknown")),
                    exc.__class__.__name__,
                )
        if not stream_completed:
            if last_err is not None:
                raise last_err
            raise RuntimeError("HoloChat runtime has no available streaming analyst adapters.")

        response_text = "".join(accumulated)
        elapsed_ms = _elapsed_timer_ms(analyst_timer)
        _add_timing(timings, "analyst_ms", analyst_timer)
        failover = _analyst_failover_metadata(
            initial_adapter=initial_adapter,
            final_adapter=adapter,
            attempts=failover_attempts,
            policy=(
                "balanced_frontier_assist_then_next_mini"
                if frontier_assist.get("triggered")
                else "try_next_active_mini"
            ),
        )

        if holo4dna_shadow is not None:
            actual_analyst = _adapter_identity_dict(adapter)
            recorded_analyst = holo4dna_shadow.metadata["route"]["runtime_analyst"]
            if actual_analyst != recorded_analyst:
                holo4dna_shadow.metadata["route"]["runtime_analyst_after_failover"] = actual_analyst
                holo4dna_shadow.trace.extra_metadata["runtime_analyst_after_failover"] = actual_analyst

        gov_post_timer = _timer_start()
        # Post-stream: claims check (may append a correction to response_text)
        response_text, flagged_claims = self._governor.verify_claims(response_text, web_search.search)
        if flagged_claims:
            corrections = [f["correction"] for f in flagged_claims if f.get("correction")]
            if corrections:
                note = " · ".join(corrections)
                correction_text = f"\n\n*One thing worth correcting: {note}*"
                response_text  += correction_text
                yield correction_text

        path_generator = getattr(self._governor, "generate_conversation_paths", None)
        conversation_paths = []
        if path_generator and not incognito:
            conversation_paths = path_generator(
                history=adapter_history,
                capsule_context=governor_context,
                user_message=user_message,
                response_text=response_text,
                tenor=tenor or "",
                thread_health_level=session.thread_health_level,
                gov_arc_state=session.gov_arc_state.model_dump(mode="json"),
            )
        _add_timing(timings, "governor_post_ms", gov_post_timer)

        # Commit history
        session.history.append({"role": "user",      "content": user_message})
        session.history.append({"role": "assistant",  "content": response_text})
        if not incognito:
            _update_rolling_summary_after_turn(
                session,
                user_message=user_message,
                response_text=response_text,
            )

        # Extract artifacts
        artifacts_saved = []
        if capsule_id and not incognito:
            artifacts_saved = _extract_and_save_artifacts(
                self._brain, response_text, capsule_id, session.session_id, session.turn_count
            )

        if not incognito:
            _update_continuity_ledger_after_turn(
                session,
                user_message=user_message,
                response_text=response_text,
                conversation_paths=conversation_paths,
                artifacts_saved=artifacts_saved,
                flagged_claims=flagged_claims,
                memory_writes_count=0,
            )

        # Link session on first turn
        if capsule_id and session.turn_count == 1 and not incognito:
            self._brain.set_capsule_context(capsule_id, "last_session_id", session.session_id)
            self._brain.append_session_history(capsule_id, session.session_id, user_message)

        # Background: context extraction, consolidation, thread naming, Supabase persist
        def _post_stream():
            try:
                if capsule_id and not incognito:
                    updates = self._governor.extract_context_updates(session.history, governor_context)
                    for key, value in updates.items():
                        self._brain.set_capsule_context(capsule_id, key, value)
                    if _claim_autocompact_for_context_window(
                        session,
                        capsule_id=capsule_id,
                        incognito=incognito,
                    ):
                        result = self._governor.consolidate_session(
                            _bounded_consolidation_history(session.history),
                            governor_context,
                            session.session_id,
                        )
                        if result.get("session_note"):
                            self._brain.save_consolidation(capsule_id, session.session_id, result["session_note"])
                        if result.get("life_context"):
                            self._brain.upsert_life_context(capsule_id, result["life_context"])
                        _save_thread_handoff_artifact(
                            self._brain,
                            capsule_id=capsule_id,
                            session=session,
                            consolidation=result,
                        )
                    if session.turn_count == 2:
                        name = self._governor.name_session(list(session.history))
                        if name:
                            self._brain.update_session_name(capsule_id, session.session_id, name)
                self._brain.save_chat_turn(
                    session_id    = session.session_id,
                    turn_number   = session.turn_count,
                    user_message  = user_message,
                    holo_response = response_text,
                    provider      = adapter.provider,
                    temperature   = temperature,
                    capsule_id    = capsule_id,
                )
            except Exception as e:
                logger.warning(f"Post-stream background task failed: {e}")

        threading.Thread(target=_post_stream, daemon=True).start()

        if holo4dna_shadow is not None:
            holo4dna_shadow.trace.memory_extraction_attempted = bool(capsule_id and not incognito)
            log_trace(holo4dna_shadow.trace, logger=logger)

        handoff = _handoff_for_context_window(session)

        _update_gov_arc_state(
            session,
            user_message=user_message,
            tenor=tenor,
            web_trace=web_trace,
            conversation_paths=conversation_paths,
            memory_writes_count=0,
            handoff=handoff,
        )

        usage = _turn_usage_metadata(
            analyst_adapter=adapter,
            context_budget=context_budget,
            response_text=response_text,
            provider_input_tokens=in_tok,
            provider_output_tokens=out_tok,
            latency_ms=elapsed_ms,
        )
        governed_shadow = _run_governed_shadow_for_turn(
            self,
            session=session,
            user_message=user_message,
            response_text=response_text,
            capsule_id=capsule_id,
            capsule_context=capsule_context,
            context_budget=context_budget,
            search_query=search_query,
            search_results=search_results,
            incognito=incognito,
        )
        holo_voice_diagnostics = _holo_voice_diagnostics(
            session=session,
            analyst_adapter=adapter,
            capsule_id=capsule_id,
            incognito=incognito,
            capsule_context=capsule_context,
            life_context=life_context,
            last_session=last_session,
            tenor=tenor,
            patent_state=patent_state,
            runtime_identity=runtime_identity,
            system_prompt=system_prompt,
            context_budget=context_budget,
            provider_history=provider_history_stats,
            governed_shadow=governed_shadow,
        )
        resolved_runtime_profile = getattr(self, "_resolved_architecture_profile", None) or _holochat_runtime_profile()
        runtime_info = getattr(self, "_runtime_info", None) or _runtime_metadata(
            resolved_runtime_profile,
            self._adapters,
            self._bench,
        )
        runtime = _turn_runtime_metadata(
            runtime_info,
            analyst_adapter=adapter,
            governor=self._governor,
            governor_checked_this_turn=True,
            usage=usage,
            provider_history=provider_history_stats,
            failover=failover,
            governor_trace=_governor_trace_metadata(
                web_trace=web_trace,
                incognito=incognito,
                memory_extraction_attempted=bool(capsule_id and not incognito),
                memory_writes_count=0,
                conversation_paths_count=len(conversation_paths),
                thread_health_level=session.thread_health_level,
            ),
            gov_arc_state=session.gov_arc_state,
            frontier_assist=frontier_assist,
            timing_breakdown=_timing_breakdown_metadata(
                timings,
                turn_started_at=turn_started_at,
            ),
            handoff_transition=active_handoff_transition,
            session=session,
            governed_shadow=governed_shadow,
            holo_voice_diagnostics=holo_voice_diagnostics,
        )

        yield {
            "done":                True,
            "session_id":          session.session_id,
            "response":            response_text,
            "turn_number":         session.turn_count,
            "thread_health_score": session.thread_health_score,
            "thread_health_level": session.thread_health_level,
            "elapsed_ms":          elapsed_ms,
            "tokens":              {"input": in_tok, "output": out_tok},
            "thought":             thought,
            "searched":            searched,
            "search_query":        search_query if searched else None,
            "web_status":          web_status,
            "context_budget":      context_budget,
            "artifacts":           artifacts_saved,
            "handoff":             handoff,
            "incognito":           incognito,
            "_provider":           adapter.provider,
            "_temperature":        temperature,
            "usage":               usage,
            "runtime":             runtime,
            "conversation_paths":   conversation_paths,
            **({"holo4dna": holo4dna_shadow.metadata} if holo4dna_shadow else {}),
        }

    def get_history(self, session_id: str) -> Optional[List[Dict[str, str]]]:
        session = _sessions.get(session_id)
        return session.history if session else None

    def clear_session(self, session_id: str) -> bool:
        if session_id in _sessions:
            del _sessions[session_id]
            return True
        return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Holo4DnaShadowTurn:
    metadata: dict[str, Any]
    previous_route: PreviousRoute
    trace: HoloTraceRecord


def _env_flag(name: str) -> bool:
    return str(os.getenv(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def _holo4dna_shadow_enabled() -> bool:
    return _env_flag("HOLOCHAT_4DNA_SHADOW") or _env_flag("HOLOCHAT_4DNA_ENABLED")


def _holo4dna_enabled() -> bool:
    return _env_flag("HOLOCHAT_4DNA_ENABLED")


def _adapter_identity_dict(adapter: Any) -> dict[str, Optional[str]]:
    return {
        "provider": getattr(adapter, "provider", None),
        "model": getattr(adapter, "model_id", getattr(adapter, "model", None)),
    }


def _select_analyst_adapter(session: ChatSession, adapters: list[Any]) -> Any:
    if not adapters:
        raise RuntimeError("HoloChat runtime has no analyst adapters.")
    adapter = adapters[session.rotation_index % len(adapters)]
    session.rotation_index += 1
    return adapter


def _adapter_candidate_order(adapters: list[Any], selected: Any) -> list[Any]:
    if not adapters:
        return []
    try:
        selected_index = next(
            idx for idx, adapter in enumerate(adapters) if adapter is selected
        )
    except StopIteration:
        return [selected, *[adapter for adapter in adapters if adapter is not selected]]
    return adapters[selected_index:] + adapters[:selected_index]


def _safe_adapter_error(adapter: Any, exc: Exception) -> dict[str, Optional[str]]:
    details = _adapter_identity_dict(adapter)
    details["error_type"] = exc.__class__.__name__
    return details


def _analyst_failover_metadata(
    *,
    initial_adapter: Any,
    final_adapter: Any,
    attempts: list[dict[str, Optional[str]]],
    policy: str,
) -> dict[str, Any]:
    return {
        "policy": policy,
        "attempted": bool(attempts),
        "count": len(attempts),
        "initial": _adapter_identity_dict(initial_adapter),
        "final": _adapter_identity_dict(final_adapter),
        "skipped": attempts,
    }


def _required_tools_for_turn(search_query: Optional[str], search_results: Optional[str]) -> List[RequiredTools]:
    if search_query or search_results:
        return [RequiredTools.WEB_SEARCH]
    return [RequiredTools.NONE]


def _runtime_context_budget(
    *,
    session: ChatSession,
    adapter_history: Optional[list[dict[str, str]]] = None,
    user_message: str,
    capsule_context: dict,
    life_context: list,
    last_session: Optional[dict],
    tenor: Optional[str],
    search_results: Optional[str],
    images: Optional[List[Dict[str, Any]]],
    incognito: bool,
    runtime_identity: str,
    handoff_transition: Optional[dict[str, Any]] = None,
    patent_state: Optional[str] = None,
) -> dict[str, Any]:
    provider_history = adapter_history if adapter_history is not None else session.history
    blocks: list[dict[str, Any]] = [
        {
            "block_name": "base_holochat_prompt",
            "content": HOLO_CHAT_SYSTEM_PROMPT,
            "included": True,
            "source_type": "system",
        },
        {
            "block_name": "runtime_identity",
            "content": runtime_identity,
            "included": True,
            "source_type": "system",
        },
        {
            "block_name": "recent_session_history",
            "content": _adapter_history_budget_content(
                provider_history,
                total_history_messages=len(session.history),
            ),
            "included": bool(provider_history),
            "source_type": "history",
            "reason": "bounded adapter history argument" if provider_history else "empty",
        },
        {
            "block_name": "user_message",
            "content": user_message,
            "included": True,
            "source_type": "user",
        },
    ]

    if incognito:
        blocks.extend(
            [
                {
                    "block_name": "thread_health",
                    "content": "",
                    "included": False,
                    "source_type": "system",
                    "reason": "incognito mode",
                },
                {
                    "block_name": "holo_state_object",
                    "content": "",
                    "included": False,
                    "source_type": "governor",
                    "reason": "incognito mode",
                },
                {
                    "block_name": "thread_handoff_seed",
                    "content": "",
                    "included": False,
                    "source_type": "system",
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
                {
                    "block_name": "capsule_context",
                    "content": "",
                    "included": False,
                    "source_type": "memory",
                    "reason": "incognito mode",
                },
                {
                    "block_name": "captain_brief",
                    "content": "",
                    "included": False,
                    "source_type": "governor",
                    "reason": "incognito mode",
                },
            ]
        )
    else:
        blocks.append(
            {
                "block_name": "thread_health",
                "content": _health_context(session),
                "included": True,
                "source_type": "system",
            }
        )
        blocks.append(
            {
                "block_name": "holo_state_object",
                "content": patent_state or "",
                "included": bool(patent_state),
                "source_type": "governor",
                "reason": "empty" if not patent_state else None,
            }
        )
        blocks.append(
            {
                "block_name": "thread_handoff_seed",
                "content": _thread_handoff_transition_block(handoff_transition),
                "included": bool(handoff_transition),
                "source_type": "system",
                "reason": "empty" if not handoff_transition else None,
            }
        )
        blocks.append(
            {
                "block_name": "life_context",
                "content": _life_context_block(life_context) if life_context else "",
                "included": bool(life_context),
                "source_type": "memory",
                "reason": "empty" if not life_context else None,
            }
        )
        blocks.append(
            {
                "block_name": "latest_consolidation",
                "content": _last_session_block(last_session) if last_session else "",
                "included": bool(last_session),
                "source_type": "memory",
                "reason": "empty" if not last_session else None,
            }
        )
        blocks.append(
            {
                "block_name": "capsule_context",
                "content": _capsule_context_block(capsule_context) if capsule_context else "",
                "included": bool(capsule_context),
                "source_type": "memory",
                "reason": "empty" if not capsule_context else None,
            }
        )
        blocks.append(
            {
                "block_name": "captain_brief",
                "content": f"CAPTAIN BRIEF — READ + DIRECTIVE (private, never surface to user):\n{tenor}" if tenor else "",
                "included": bool(tenor),
                "source_type": "governor",
                "reason": "empty" if not tenor else None,
            }
        )

    blocks.append(
        {
            "block_name": "web_results",
            "content": (
                "\n\n"
                "[BACKGROUND CONTEXT: The following search results were retrieved to help you answer. "
                "Use them silently — do not mention, quote, or reference that a search was performed. "
                "If the results are irrelevant to the question, ignore them entirely.]\n\n"
                f"{search_results}"
            ) if search_results else "",
            "included": bool(search_results),
            "source_type": "search",
            "reason": "no web results" if not search_results else None,
        }
    )
    blocks.append(
        {
            "block_name": "image_attachments",
            "content": "",
            "included": bool(images),
            "source_type": "artifact",
            "reason": f"{len(images or [])} image attachment(s) passed separately; binary not counted",
        }
    )

    return build_context_budget_ledger(
        blocks,
        budget_limit_tokens=_context_warning_token_limit(),
    ).model_dump(mode="json")


def _memory_presence_summary(
    *,
    capsule_context: dict,
    life_context: list,
    last_session: Optional[dict],
    incognito: bool,
) -> dict[str, Any]:
    if incognito:
        return {"source": "HoloBrain", "incognito": True, "memory_in_prompt": False}
    return {
        "source": "HoloBrain",
        "incognito": False,
        "memory_in_prompt": bool(capsule_context or life_context or last_session),
        "capsule_context_keys": len(capsule_context or {}),
        "life_context_entries": len(life_context or []),
        "latest_consolidation_loaded": bool(last_session),
    }


def _route_decision_metadata(
    route: RouteDecision,
    *,
    runtime_adapter: Any,
    shadow_route: bool,
) -> dict[str, Any]:
    return {
        "shadow_route": shadow_route,
        "runtime_analyst": _adapter_identity_dict(runtime_adapter),
        "shadow_council": {
            "provider": route.council_provider,
            "model": route.council_model,
        },
        "hologov": {
            "provider": route.hologov_provider,
            "model": route.hologov_model,
            "tenure_remaining": route.hologov_tenure_remaining,
            "tenure_window": list(route.hologov_tenure_window),
        },
        "previous_council": {
            "provider": route.previous_council_provider,
            "model": route.previous_council_model,
        },
        "assigned_role": route.assigned_role,
        "route_reason": route.route_reason,
        "fallback_used": route.fallback_used,
        "fallback_reason": route.fallback_reason,
        "dna_degraded": route.dna_degraded,
        "eligible_provider_count": route.eligible_provider_count,
    }


def _thread_health_metadata(holo_state: HoloState) -> dict[str, Any]:
    return holo_state.thread_health.model_dump(mode="json")


def _build_holo4dna_shadow_turn(
    *,
    session: ChatSession,
    capsule_id: Optional[str],
    user_message: str,
    runtime_adapter: Any,
    router: HoloRouter,
    context_builder: HoloContextBuilder,
    previous_route: Optional[PreviousRoute],
    capsule_context: dict,
    life_context: list,
    last_session: Optional[dict],
    search_query: Optional[str],
    search_results: Optional[str],
    incognito: bool,
    runtime_info: dict[str, Any],
    capsule_attached: bool,
    recent_history: Optional[list[dict[str, str]]] = None,
) -> Holo4DnaShadowTurn:
    required_tools = _required_tools_for_turn(search_query, search_results)
    holo_state = HoloState.from_chat_turn(
        session_id=session.session_id,
        capsule_id=capsule_id,
        turn_number=session.turn_count,
        user_message=user_message,
        user_goal=session.gov_arc_state.user_goal,
        critical_constraints=session.critical_constraints,
        rolling_summary=session.rolling_summary or _rolling_summary_from_history(session.history),
        continuity_ledger=_normalized_continuity_ledger(session.continuity_ledger),
        settled_decisions=session.gov_arc_state.settled_decisions,
        thread_health_score=session.thread_health_score,
        thread_status=session.thread_status,
        required_tools=required_tools,
        gov_arc_state=session.gov_arc_state,
    )
    holo_state.memory_candidates.append(
        _memory_presence_summary(
            capsule_context=capsule_context,
            life_context=life_context,
            last_session=last_session,
            incognito=incognito,
        )
    )

    route = router.select_route(holo_state, previous_route=previous_route)
    context_packet = context_builder.build(
        base_system_prompt=HOLO_CHAT_SYSTEM_PROMPT,
        holo_state=holo_state,
        user_message=user_message,
        route_decision=route,
        capsule_context=capsule_context,
        life_context=life_context,
        latest_consolidation=last_session,
        recent_history=recent_history or _bounded_adapter_history(session.history),
        web_results=search_results,
        incognito=incognito,
        runtime_info=runtime_info,
        capsule_attached=capsule_attached,
    )

    route_metadata = _route_decision_metadata(route, runtime_adapter=runtime_adapter, shadow_route=True)
    thread_health = _thread_health_metadata(holo_state)
    metadata = {
        "shadow": True,
        "enabled": _holo4dna_enabled(),
        "state_id": holo_state.state_id,
        "state_schema_version": holo_state.schema_version,
        "dna_profile": route.dna_profile,
        "route": route_metadata,
        "context_hash": context_packet.context_hash,
        "context": {
            "included_blocks": context_packet.metadata.get("included_blocks", []),
            "omitted_blocks": context_packet.metadata.get("omitted_blocks", []),
            "char_count": context_packet.char_count,
            "token_estimate": context_packet.token_estimate,
        },
        "context_budget": context_packet.metadata.get("context_budget"),
        "thread_health": thread_health,
        "gov_arc_state": holo_state.gov_arc_state.model_dump(mode="json"),
        "searched": bool(search_query or search_results),
        "search_query": search_query,
    }

    trace = HoloTraceRecord(
        session_id=session.session_id,
        turn_number=session.turn_count,
        holo_state_id=holo_state.state_id,
        holo_state_schema_version=holo_state.schema_version,
        dna_profile=route.dna_profile,
        shadow_route=True,
        runtime_analyst_provider=metadata["route"]["runtime_analyst"]["provider"],
        runtime_analyst_model=metadata["route"]["runtime_analyst"]["model"],
        selected_council_provider=route.council_provider,
        selected_council_model=route.council_model,
        selected_hologov_provider=route.hologov_provider,
        selected_hologov_model=route.hologov_model,
        assigned_role=route.assigned_role,
        route_reason=route.route_reason,
        searched=bool(search_query or search_results),
        search_query=search_query,
        thread_health=thread_health,
        context_packet_hash=context_packet.context_hash,
        context_blocks=context_packet.metadata.get("included_blocks", []),
        fallback_used=route.fallback_used,
        fallback_reason=route.fallback_reason,
        dna_degraded=route.dna_degraded,
        extra_metadata={
            "context_char_count": context_packet.char_count,
            "context_token_estimate": context_packet.token_estimate,
            "omitted_blocks": context_packet.metadata.get("omitted_blocks", []),
        },
    )
    return Holo4DnaShadowTurn(
        metadata=metadata,
        previous_route=route.as_previous_route(),
        trace=trace,
    )


def _life_context_block(entries: list) -> str:
    """
    Format the Governor's permanent portrait for injection.
    This is the distilled, curated truth — highest priority context.
    """
    return build_life_context_block(
        entries,
        header="WHO THIS PERSON IS (Governor's permanent portrait — distilled across all sessions):",
    )


def _last_session_block(note: dict) -> str:
    """Format the Governor's note from last session — private, never surface."""
    if not note:
        return ""
    lines = ["LAST SESSION NOTE (Governor's private carry-forward — do not mention to user):"]
    if note.get("what_surfaced"):
        lines.append(f"  What surfaced last time: {note['what_surfaced']}")
    if note.get("open_threads"):
        threads = note["open_threads"] if isinstance(note["open_threads"], list) else [note["open_threads"]]
        lines.append(f"  Open threads to pick up: {', '.join(threads)}")
    if note.get("captain_note"):
        lines.append(f"  Captain note: {note['captain_note']}")
    return "\n".join(lines)


def _capsule_context_block(context: dict) -> str:
    """Format capsule context (working memory) for injection into the system prompt."""
    return build_capsule_context_block(
        context,
        header="WORKING MEMORY (facts extracted this and recent sessions — less refined than portrait):",
    )


def _extract_and_save_artifacts(
    brain, response_text: str, capsule_id: str, session_id: str, turn_number: int
) -> list:
    """
    Scan response_text for ```html artifacts, save each to holo_artifacts.
    Returns list of {artifact_id, title, type} dicts for the API response.
    """
    saved = []
    for match in _re.finditer(r'```html\n?([\s\S]*?)```', response_text, _re.IGNORECASE):
        content = match.group(1).strip()
        if not _re.search(r'<!doctype|<html', content, _re.IGNORECASE):
            continue
        title_match = _re.search(r'<title>([^<]*)</title>', content, _re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "Artifact"
        aid = brain.save_artifact(capsule_id, session_id, turn_number, title, content)
        if aid:
            saved.append({"artifact_id": aid, "title": title, "type": "html"})
    return saved


def _health_context(session: ChatSession) -> str:
    """
    Build the BATON_PASS snippet that HOLO_CHAT_SYSTEM_PROMPT references.
    Injected at the end of the system prompt every turn.
    """
    return (
        f"BATON_PASS:\n"
        f"  THREAD_HEALTH_SCORE: {session.thread_health_score}\n"
        f"  THREAD_HEALTH_LEVEL: {session.thread_health_level}\n"
        f"  THREAD_STATUS: {session.thread_status}\n"
        f"  USER_ALERT_RECOMMENDED: {session.user_alert}\n"
        f"  TASK_MODE: DEEP_REASONING"
    )
