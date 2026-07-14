"""
chat_engine.py

Holo chat mode — rotating serial analyst conversation engine.

Every response comes from one selected analyst provider.
The Governor is a separate controller/check layer selected away from
the analyst on the same turn; it does not produce a second visible answer.
All providers speak as Holo using the unified persona prompt.
"""

import logging
import inspect
import os
import random
import re as _re
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from holo_context import (
    HoloContextBuilder,
    build_capsule_context_block,
    build_context_budget_ledger,
    build_life_context_block,
    build_runtime_identity_block,
    estimate_context_tokens,
)
from holo_router import HoloRouter, PreviousRoute, RouteDecision
from holochat_context_governor import (
    HOLOCHAT_STATE_CONTEXT_KEY,
    HoloBrainInjectionMode,
    HoloBrainInjectionPlan,
    GovTurnPlan,
    admit_advisor_claim_corrections,
    admit_advisor_consolidation,
    admit_advisor_memory_updates,
    admit_advisor_prompt_directive,
    admit_advisor_search_query,
    admit_advisor_surface_thought,
    admit_advisor_thread_name,
    build_holobrain_injection_plan,
    build_holochat_state,
    build_gov_turn_plan,
    deterministic_turn_policy,
    deterministic_visible_release,
    has_meaningful_holobrain_delta,
    load_state_from_capsule_context,
    project_gov_narrative_packet_for_worker,
    render_gov_turn_plan_for_worker,
    should_auto_compact,
    stable_hash,
    state_context_value,
)
from holochat_constitution import constitutional_prompt_block
from holochat_evidence import (
    admit_web_citations,
    build_worker_context_receipt,
    merge_episode_context,
    render_web_evidence,
)
from holochat_memory_steward import (
    CheckpointPolicy,
    EventKind as MemoryEventKind,
    LifecycleEvent as MemoryLifecycleEvent,
    LifecycleKind as MemoryLifecycleKind,
    MemoryProposal,
    MemoryStewardState,
    PersistenceAcknowledgement,
    ProposalKind as MemoryProposalKind,
    Provenance as MemoryProvenance,
    TurnInput as MemoryTurnInput,
    acknowledge_checkpoint,
    apply_exchange,
    apply_lifecycle_event,
    checkpoint_payload,
    initial_state as initial_memory_steward_state,
    restore_state as restore_memory_steward_state,
)
from holo_state import GovArcState, HoloState, RequiredTools
from holo_trace import HoloTraceRecord, log_trace
from llm_adapters import (
    HOLO_CHAT_SYSTEM_PROMPT,
    GovernorAdapter,
    load_adapters,
    load_fast_adapters,
    load_holochat_governor_adapters,
)
from project_brain import ProjectBrain
import web_search

logger = logging.getLogger("holo.chat")

# In-memory session store.
# Replace with Redis for multi-instance or persistent deployments.
_sessions: Dict[str, "ChatSession"] = {}
_memory_steward_lock = threading.RLock()


# ---------------------------------------------------------------------------
# Session model
# ---------------------------------------------------------------------------

class SessionOwnershipError(Exception):
    """Raised when a caller attempts to use a chat session it does not own."""


@dataclass
class ChatSession:
    session_id: str
    # Set only when the session is created. It is the in-process companion to
    # the durable holo_chat_sessions.capsule_id ownership binding.
    owner_capsule_id: Optional[str] = None
    owner_scope_id: Optional[str] = None
    incognito: bool = False
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
    holochat_state: Optional[HoloState] = None
    handoff_artifact_saved: bool = False
    handoff_suggested: bool = False
    autocompact_attempted: bool = False
    auto_reseed_applied: bool = False
    auto_reseed_hash: Optional[str] = None
    retrieved_episodes: list[dict[str, Any]] = field(default_factory=list)
    web_evidence_bundle: dict[str, Any] = field(default_factory=dict)
    episode_retrieval_trace: dict[str, Any] = field(default_factory=dict)
    worker_context_receipt: dict[str, Any] = field(default_factory=dict)
    memory_steward_state: Optional[MemoryStewardState] = None
    memory_steward_trace: dict[str, Any] = field(default_factory=dict)
    memory_steward_open_checked: bool = False
    memory_steward_persistence_blocked: bool = False

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {"owner_capsule_id", "owner_scope_id", "incognito"} and name in self.__dict__:
            raise AttributeError(f"{name} is immutable after session creation")
        super().__setattr__(name, value)

    @property
    def thread_health_score(self) -> int:
        """
        Measure actual context pressure, not conversation age. A long coherent
        relationship is healthy until the ordered transcript approaches the
        configured provider-history budget.
        """
        total_chars = sum(len(m["content"]) for m in self.history)
        capacity = max(1, _adapter_history_char_limit())
        soft_limit = int(capacity * 0.65)
        if total_chars <= soft_limit:
            return 100
        if total_chars <= capacity:
            pressure = (total_chars - soft_limit) / max(1, capacity - soft_limit)
            return max(20, int(round(100 - (pressure * 80))))
        overflow = (total_chars - capacity) / capacity
        return max(0, int(round(20 - (overflow * 20))))

    @property
    def thread_health_reasons(self) -> list[str]:
        """Legacy debug reasons.

        New telemetry consumers should prefer thread_health_metrics and
        thread_health_flags so numeric values remain parseable.
        """
        reasons: list[str] = []
        metrics = self.thread_health_metrics
        if metrics["turn_count"]:
            reasons.append(f"turn_count:{metrics['turn_count']}")
        if metrics["raw_history_chars"]:
            reasons.append(f"raw_history_chars:{metrics['raw_history_chars']}")
        reasons.extend(self.thread_health_flags)
        return reasons

    @property
    def thread_health_metrics(self) -> dict[str, int]:
        return {
            "turn_count": self.turn_count,
            "raw_history_chars": sum(len(m["content"]) for m in self.history),
        }

    @property
    def thread_health_flags(self) -> list[str]:
        flags: list[str] = []
        metrics = self.thread_health_metrics
        if self.thread_health_level == "YELLOW":
            flags.append("context_pressure_warning")
        elif self.thread_health_level == "RED":
            flags.append("context_pressure_critical")
        if self.thread_health_level == "RED":
            flags.append("internal_autocompact_required")
        if metrics["raw_history_chars"] > DEFAULT_ADAPTER_HISTORY_CHARS:
            flags.append("provider_history_bounded")
        return flags

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
        score = self.thread_health_score
        if score <= 20:
            return "AUTOCOMPACT_REQUIRED"
        elif score <= 60:
            return "CONTEXT_PRESSURE"
        return "HEALTHY"

    @property
    def user_alert(self) -> str:
        # Context pressure is an internal runtime responsibility. Do not make
        # the user manage HoloChat's context window.
        return "NONE"


# ---------------------------------------------------------------------------
# Governor rotation helpers
# ---------------------------------------------------------------------------

CANONICAL_RUNTIME_PROFILE = "holochat_canonical"
DEFAULT_RUNTIME_PROFILE = CANONICAL_RUNTIME_PROFILE
LEGACY_CANONICAL_RUNTIME_PROFILES = {CANONICAL_RUNTIME_PROFILE, "mini_only"}
BALANCED_RUNTIME_PROFILE = "balanced"
FRONTIER_RUNTIME_PROFILES = {"frontier_active", "legacy_frontier"}
DEFAULT_HOLOCHAT_MODEL_PROVIDERS = ("openai", "xai")
FALLBACK_HOLOCHAT_MODEL_PROVIDERS: set[str] = set()
DISABLED_HOLOCHAT_MODEL_PROVIDERS = {"minimax"}
HOLOCHAT_MODEL_TIER_ENV = "HOLOCHAT_MODEL_TIER"
# Visible intelligence stays frontier by default. Cost containment now belongs
# in the private HoloGov provider seat, not in the worker rotation.
DEFAULT_HOLOCHAT_MODEL_TIER = "frontier"
HOLOCHAT_MODEL_BY_TIER = {
    "economy": {
        "openai": "gpt-5.4-mini",
        "xai": "grok-4.3",
    },
    "frontier": {
        "openai": "gpt-5.5",
        "xai": "grok-4.3",
    },
}
# Compatibility name for code/tests that refer to the intended frontier law.
CANONICAL_HOLOCHAT_MODEL_BY_PROVIDER = HOLOCHAT_MODEL_BY_TIER["frontier"]
CANONICAL_HOLOCHAT_GOV_PROVIDER = "minimax"
CANONICAL_HOLOCHAT_GOV_PROVIDERS = (CANONICAL_HOLOCHAT_GOV_PROVIDER,)
DEFAULT_THREAD_HANDOFF_MIN_TURNS = 24
THREAD_HANDOFF_FORCE_SCORE = 5
# Preserve the original HoloChat behavior for normal-length threads: workers and
# HoloGov receive the ordered conversation from the beginning. These are safety
# rails for genuinely long threads, not an early-compaction policy.
DEFAULT_ADAPTER_HISTORY_MESSAGES = 120
DEFAULT_ADAPTER_HISTORY_CHARS = 160_000
DEFAULT_ADAPTER_HISTORY_MESSAGE_CHARS = 20_000
MATERIAL_HISTORY_BOUNDING_CHARS = 200
HOLOCHAT_MEMORY_PACK_VERSION = "holochat_recovery_pack_v0.1"

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

# Local, non-authoritative pricing estimates. Values are standard input/output
# USD per 1M tokens from official provider pricing pages on the version date.
# They are estimates only; cached, long-context, priority, tool, and regional
# charges may differ from this simple turn estimate.
_STATIC_CHAT_PRICING_VERSION = "official_public_pricing_2026-07-14"
_STATIC_CHAT_PRICING_USD_PER_M_TOKEN: dict[tuple[str, str], tuple[float, float]] = {
    ("openai", "gpt-5.5"): (5.00, 30.00),
    ("openai", "gpt-5.4-mini"): (0.75, 4.50),
    ("xai", "grok-4.3"): (1.25, 2.50),
    ("minimax", "MiniMax-M2.7-highspeed"): (0.60, 2.40),
}

THREAD_HANDOFF_MESSAGE = "This thread is getting long. Start a fresh thread to keep Holo sharp."


def _truthy_env(name: str) -> bool:
    return str(os.getenv(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def _holochat_allow_noncanonical_policy() -> bool:
    return _truthy_env("HOLOCHAT_ALLOW_NONCANONICAL_POLICY")


def _holochat_experiment_mode() -> bool:
    """Permit explicit runner-selected models without weakening production law."""
    return _truthy_env("HOLOCHAT_EXPERIMENT_MODE") and _holochat_allow_noncanonical_policy()


def _holochat_model_tier() -> str:
    """Select the approved HC cost tier without relaxing provider policy."""
    configured = str(os.getenv(HOLOCHAT_MODEL_TIER_ENV, DEFAULT_HOLOCHAT_MODEL_TIER)).strip().lower()
    if not _holochat_experiment_mode():
        if configured != DEFAULT_HOLOCHAT_MODEL_TIER:
            logger.warning(
                "Ignoring noncanonical %s=%s outside experiment mode; using %s",
                HOLOCHAT_MODEL_TIER_ENV,
                configured,
                DEFAULT_HOLOCHAT_MODEL_TIER,
            )
        return DEFAULT_HOLOCHAT_MODEL_TIER
    if configured in HOLOCHAT_MODEL_BY_TIER:
        return configured
    logger.warning(
        "Unknown %s=%s; using %s",
        HOLOCHAT_MODEL_TIER_ENV,
        configured,
        DEFAULT_HOLOCHAT_MODEL_TIER,
    )
    return DEFAULT_HOLOCHAT_MODEL_TIER


def _single_hologov_call_enabled(runtime_profile: str) -> bool:
    """Canonical HoloChat uses one provider-backed HoloGov compilation per turn."""
    canonical = str(runtime_profile or "").strip().lower() == CANONICAL_RUNTIME_PROFILE
    if canonical and not _holochat_experiment_mode():
        return True
    configured = os.getenv("HOLOCHAT_SINGLE_GOV_CALL")
    if configured is not None:
        return str(configured).strip().lower() in {"1", "true", "yes", "on"}
    return str(runtime_profile or "").strip().lower() == CANONICAL_RUNTIME_PROFILE


def _deterministic_worker_temperature(turn_policy: Any) -> float:
    tier = str(getattr(turn_policy, "tier", "standard") or "standard").lower()
    return {
        "max": 0.25,
        "high": 0.3,
        "standard": 0.5,
        "fast": 0.35,
    }.get(tier, 0.5)


def _holochat_runtime_profile() -> str:
    runtime_profile = (os.getenv("HOLOCHAT_RUNTIME_PROFILE") or DEFAULT_RUNTIME_PROFILE).strip().lower()
    if runtime_profile in LEGACY_CANONICAL_RUNTIME_PROFILES:
        return DEFAULT_RUNTIME_PROFILE
    if runtime_profile != DEFAULT_RUNTIME_PROFILE and not _holochat_experiment_mode():
        logger.warning(
            "HoloChat canonical runtime policy forced %s; ignored HOLOCHAT_RUNTIME_PROFILE=%s",
            DEFAULT_RUNTIME_PROFILE,
            runtime_profile,
        )
        return DEFAULT_RUNTIME_PROFILE
    return runtime_profile


def _holochat_model_providers() -> tuple[str, ...]:
    raw = os.getenv("HOLOCHAT_MODEL_PROVIDERS")
    if raw is None or not _holochat_experiment_mode():
        return DEFAULT_HOLOCHAT_MODEL_PROVIDERS
    providers = tuple(
        provider.strip().lower()
        for provider in raw.split(",")
        if provider.strip()
    )
    return providers or DEFAULT_HOLOCHAT_MODEL_PROVIDERS


def _call_pool_loader(loader: Any, provider_allowlist: tuple[str, ...]) -> Any:
    params = inspect.signature(loader).parameters
    if "provider_allowlist" in params:
        return loader(provider_allowlist=provider_allowlist)
    return loader()


def _normalize_holochat_model_policy(adapters: list[Any]) -> list[Any]:
    if _holochat_experiment_mode():
        logger.warning("HoloChat experiment mode active; using explicit runner model IDs.")
        return adapters
    model_policy = HOLOCHAT_MODEL_BY_TIER[_holochat_model_tier()]
    for adapter in adapters:
        provider = str(getattr(adapter, "provider", "") or "").strip().lower()
        canonical_model = model_policy.get(provider)
        if not canonical_model:
            continue
        current_model = getattr(adapter, "model_id", getattr(adapter, "model", None))
        if current_model != canonical_model:
            logger.warning(
                "HoloChat canonical model policy forced %s/%s; ignored configured model %s",
                provider,
                canonical_model,
                current_model,
            )
            adapter.model_id = canonical_model
            if hasattr(adapter, "model"):
                adapter.model = canonical_model
    return adapters


def _filter_holochat_enabled_adapters(adapters: list[Any]) -> list[Any]:
    return [
        adapter for adapter in adapters
        if str(getattr(adapter, "provider", "") or "").strip().lower()
        not in DISABLED_HOLOCHAT_MODEL_PROVIDERS
    ]


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


def _thread_handoff_ready(session: "ChatSession") -> bool:
    if session.thread_health_level != "RED":
        return False
    return (
        session.turn_count >= _thread_handoff_min_turns()
        or session.thread_health_score <= THREAD_HANDOFF_FORCE_SCORE
    )


def _visible_thread_handoff_enabled() -> bool:
    """Fresh-thread prompts are an opt-in legacy escape hatch, not normal HC flow."""
    return os.getenv("HOLOCHAT_VISIBLE_THREAD_HANDOFF_ENABLED", "0").strip().lower() in {
        "1", "true", "yes", "on",
    }


def _handoff_for_context_window(session: "ChatSession") -> Optional[dict[str, Any]]:
    """Return an opt-in fresh-thread prompt; normal HoloChat threads do not end."""
    if not _visible_thread_handoff_enabled():
        return None
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
            "HoloGov is starting a fresh thread from a compact handoff seed, "
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


def _holochat_state_seed_block(plan: Optional[HoloBrainInjectionPlan]) -> str:
    return plan.payload if plan else ""


def _holochat_state_runtime_metadata(
    state: Optional[HoloState],
    *,
    holobrain_injection_plan: Optional[HoloBrainInjectionPlan] = None,
    holobrain_state_persisted: bool = False,
) -> dict[str, Any]:
    plan = holobrain_injection_plan or HoloBrainInjectionPlan(
        mode=HoloBrainInjectionMode.NONE,
        payload="",
        reason="not_evaluated",
    )
    if not state:
        return {
            "state_object_present": False,
            "state_object_hash": None,
            "rolling_summary_hash": None,
            "baton_hash": None,
            "artifact_registry_hash": None,
            "state_audit_trusted": False,
            "state_audit_warnings": ["state_not_available_yet"],
            "hologov_c_mode": "active",
            "holobrain_injection_mode": plan.mode.value,
            "holobrain_injection_reason": plan.reason,
            "holobrain_injected": False,
            "holobrain_injected_chars": 0,
            "holobrain_injected_token_estimate": 0,
            "holobrain_state_persisted": holobrain_state_persisted,
        }
    audit = state.state_audit
    warnings = list(audit.notes or [])
    warnings.extend(audit.missing_required_fields or [])
    warnings.extend(audit.contradiction_warnings or [])
    if audit.overlarge_reseed:
        warnings.append("overlarge_reseed")
    if audit.missing_artifact_references:
        warnings.append("missing_artifact_references")
    return {
        "state_object_present": True,
        "state_object_id": state.state_id,
        "state_object_hash": audit.state_hash,
        "rolling_summary_hash": audit.summary_hash,
        "baton_hash": audit.baton_hash,
        "artifact_registry_hash": audit.artifact_registry_hash,
        "reseed_hash": audit.reseed_hash,
        "state_audit_trusted": audit.trusted,
        "state_audit_warnings": warnings,
        "artifact_registry_count": len(state.artifact_registry),
        "hologov_c_mode": "active",
        "holobrain_injection_mode": plan.mode.value,
        "holobrain_injection_reason": plan.reason,
        "holobrain_injected": bool(plan.payload),
        "holobrain_injected_chars": plan.char_count,
        "holobrain_injected_token_estimate": plan.token_estimate,
        "holobrain_state_persisted": holobrain_state_persisted,
    }


def _persist_holochat_state(brain: Any, capsule_id: Optional[str], state: Optional[HoloState]) -> None:
    if not capsule_id or not state:
        return
    setter = getattr(brain, "set_capsule_context", None)
    if not setter:
        return
    setter(capsule_id, HOLOCHAT_STATE_CONTEXT_KEY, state_context_value(state))


def _holobrain_recovery_needed(user_message: str) -> bool:
    lowered = (user_message or "").lower()
    return any(
        marker in lowered
        for marker in (
            "recover",
            "reseed",
            "pick up where",
            "restore context",
            "continue from the last thread",
            "continue from prior",
            "lost context",
        )
    )


def _holobrain_topic_shift(user_message: str) -> bool:
    lowered = (user_message or "").lower()
    return any(
        marker in lowered
        for marker in (
            "new topic",
            "unrelated topic",
            "different project",
            "switch topics",
            "new project",
            "context discontinuity",
        )
    )


def _holobrain_artifact_needed(user_message: str) -> bool:
    lowered = (user_message or "").lower()
    artifact_markers = ("artifact", "file", "doc", "document", "html", "packet")
    need_markers = ("open", "retrieve", "pull", "use", "inspect", "show", "refer")
    return any(marker in lowered for marker in artifact_markers) and any(
        marker in lowered for marker in need_markers
    )


def _claim_autocompact_for_context_window(
    session: "ChatSession",
    *,
    capsule_id: Optional[str],
    incognito: bool,
    context_budget: Optional[dict[str, Any]] = None,
) -> bool:
    """Allow one consolidation/reseed attempt per session/context window."""
    if not capsule_id or incognito:
        return False
    compact_ready = _thread_handoff_ready(session)
    if context_budget is not None:
        compact_ready = compact_ready or should_auto_compact(
            context_budget=context_budget,
            thread_health_level=session.thread_health_level,
            thread_health_score=session.thread_health_score,
        )
    if not compact_ready:
        return False
    if (
        _memory_steward_enabled()
        and session.memory_steward_state is not None
        and session.memory_steward_state.pending_checkpoint is not None
    ):
        return False
    if session.autocompact_attempted:
        return False
    session.autocompact_attempted = True
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
        "governor_adapter_role": "provider_advisor_proposal_source" if present else "off",
        "deterministic_gov_kernel": "authority_admission_layer" if present else "off",
    }


def _governor_trace_metadata(
    *,
    web_trace: Optional[dict[str, Any]],
    incognito: bool,
    memory_extraction_attempted: bool,
    memory_writes_count: int,
    thread_health_level: str,
    conversation_paths_count: int = 0,
    single_call_mode: bool = False,
    api_calls_this_turn: int = 0,
) -> dict[str, Any]:
    web_status = (web_trace or {}).get("status") or "off"
    memory_status = "skipped_incognito" if incognito else (
        "checked" if memory_extraction_attempted else "not_available"
    )
    return {
        "temperature": "deterministic_from_turn_policy" if single_call_mode else "checked",
        "web_decision": web_status,
        "web_search": web_trace or _web_trace(None, source="none", results=None),
        "claim_check": "worker_plus_release_guard" if single_call_mode else "checked",
        "memory_extraction": memory_status,
        "memory_writes_count": _safe_positive_int(memory_writes_count),
        "conversation_paths": "generated" if conversation_paths_count else "skipped",
        "conversation_paths_count": _safe_positive_int(conversation_paths_count),
        "thread_health": thread_health_level,
        "single_hologov_call_mode": bool(single_call_mode),
        "hologov_api_calls_this_turn": _safe_positive_int(api_calls_this_turn),
    }


def _governor_api_call_count(governor: Any) -> int:
    getter = getattr(governor, "get_api_call_count", None)
    if not callable(getter):
        return 0
    try:
        return _safe_positive_int(getter())
    except Exception:
        return 0


def _safe_positive_int(value: Any) -> int:
    try:
        parsed = int(value or 0)
    except (TypeError, ValueError):
        return 0
    return max(0, parsed)


def _positive_int_env(name: str, default: int, *, minimum: int = 0) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return max(minimum, int(raw))
    except ValueError:
        return default


def _hologov_control_compilation_enabled() -> bool:
    if not _holochat_experiment_mode():
        return True
    raw = os.getenv(
        "HOLOCHAT_GOV_CONTROL_PACKET_ENABLED",
        os.getenv("HOLOCHAT_DEEP_GOV_ENABLED", "1"),
    )
    return raw.strip().lower() not in {
        "0", "false", "no", "off",
    }


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
    query_text: Optional[str] = None,
) -> list[dict[str, str]]:
    """
    Preserve the complete ordered thread while it fits. Under real pressure,
    retain origins, the newest turns, relevant older material, and explicit
    decisions/corrections. The returned messages remain chronologically ordered.
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

    sanitized: list[dict[str, str]] = []
    for message in history:
        role = str(message.get("role") or "unknown")
        if role not in {"system", "user", "assistant", "tool"}:
            role = "unknown"
        content = _compact_text(message.get("content"), limit=per_message_limit)
        if not content:
            continue
        sanitized.append({"role": role, "content": content})

    if len(sanitized) <= message_limit and _history_char_count(sanitized) <= char_limit:
        return sanitized

    count = len(sanitized)
    # Reserve real space for all three evidence classes. Small test/context
    # windows must not let origins plus recency crowd out a relevant older turn.
    origin_count = min(count, min(6, max(2, message_limit // 10)))
    recent_count = min(count, max(4, min(32, message_limit // 2)))
    origin_indices = list(range(origin_count))
    recent_indices = list(range(max(0, count - recent_count), count))
    protected = set(origin_indices) | set(recent_indices)

    query_terms = {
        term
        for term in _re.findall(r"[a-z0-9][a-z0-9_-]{3,}", (query_text or "").lower())
        if term not in {
            "about", "after", "again", "could", "from", "have", "into", "just",
            "should", "that", "their", "there", "these", "they", "this", "what",
            "when", "where", "which", "with", "would", "your",
        }
    }
    signal_terms = (
        "decided", "decision", "agreed", "must", "never", "remember", "important",
        "correction", "actually", "no longer", "changed", "constraint", "boundary",
        "unresolved", "evidence", "source", "diagnosis", "commitment",
    )
    ranked_middle: list[tuple[int, int]] = []
    for index, message in enumerate(sanitized):
        if index in protected:
            continue
        lowered = message["content"].lower()
        overlap = sum(1 for term in query_terms if term in lowered)
        signal = sum(1 for term in signal_terms if term in lowered)
        role_bonus = 1 if message["role"] == "assistant" else 0
        ranked_middle.append((overlap * 12 + signal * 4 + role_bonus, index))
    ranked_middle.sort(key=lambda item: (item[0], item[1]), reverse=True)

    # Origins first, then reserve relevant older evidence, then fill with the
    # newest turns. Sort only after admission so provider order stays canonical.
    relevance_slots = max(1, message_limit - len(origin_indices) - len(recent_indices))
    relevant_indices = [index for score, index in ranked_middle if score > 0][:relevance_slots]
    priority = origin_indices + relevant_indices + list(reversed(recent_indices))
    priority += [index for _, index in ranked_middle if index not in relevant_indices]
    selected_by_index: dict[int, dict[str, str]] = {}
    used_chars = 0
    for index in priority:
        if index in selected_by_index or len(selected_by_index) >= message_limit:
            continue
        message = sanitized[index]
        entry_chars = len(message["role"]) + len(message["content"]) + 2
        remaining = char_limit - used_chars
        if entry_chars > remaining:
            if remaining < 400:
                continue
            message = {
                "role": message["role"],
                "content": _compact_text(message["content"], limit=max(1, remaining - len(message["role"]) - 2)),
            }
            entry_chars = len(message["role"]) + len(message["content"]) + 2
        selected_by_index[index] = message
        used_chars += entry_chars
        if used_chars >= char_limit:
            break
    return [selected_by_index[index] for index in sorted(selected_by_index)]


def _history_char_count(history: list[dict[str, str]]) -> int:
    return sum(
        len(str(message.get("role", ""))) + len(str(message.get("content", ""))) + 2
        for message in history or []
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
        lines.insert(
            0,
            f"[context_budget] omitted {omitted} raw history message(s) under real context pressure; "
            "origins, relevant older evidence, and recent turns were retained. Use the HoloGov control ledger to navigate gaps.",
        )
    return "\n".join(lines)


def _provider_history_metadata(
    adapter_history: list[dict[str, str]],
    *,
    total_history_messages: int,
    raw_history: list[dict[str, str]],
) -> dict[str, Any]:
    bounded_chars = _history_char_count(adapter_history)
    raw_chars = _history_char_count(raw_history)
    omitted = max(0, total_history_messages - len(adapter_history))
    return {
        "raw_history_messages": max(0, total_history_messages),
        "bounded_history_messages": len(adapter_history),
        "omitted_history_messages": omitted,
        "raw_history_chars": raw_chars,
        "bounded_history_chars": bounded_chars,
        "raw_history_token_estimate": estimate_context_tokens("x" * raw_chars),
        "bounded_history_token_estimate": estimate_context_tokens("x" * bounded_chars),
        "history_message_cap": _adapter_history_message_limit(),
        "history_char_cap": _adapter_history_char_limit(),
        "history_message_char_cap": _adapter_history_message_char_limit(),
        "omitted_history_marker_inserted": bool(omitted),
        "selection_mode": "full_ordered_history" if not omitted else "origin_relevant_recent",
        "ordered_history_preserved": True,
    }


def _thread_health_reasons_for_context_budget(
    session: "ChatSession",
    provider_history_meta: dict[str, Any],
) -> list[str]:
    reasons = [
        reason
        for reason in session.thread_health_reasons
        if reason != "provider_history_bounded"
    ]
    raw_chars = _safe_positive_int(provider_history_meta.get("raw_history_chars"))
    bounded_chars = _safe_positive_int(provider_history_meta.get("bounded_history_chars"))
    provider_history_bounded = (
        _safe_positive_int(provider_history_meta.get("omitted_history_messages")) > 0
        or raw_chars - bounded_chars > MATERIAL_HISTORY_BOUNDING_CHARS
    )
    if provider_history_bounded:
        reasons.append("provider_history_bounded")
    return reasons


def _thread_health_metrics_for_context_budget(
    session: "ChatSession",
    provider_history_meta: dict[str, Any],
) -> dict[str, int]:
    metrics = dict(session.thread_health_metrics)
    metrics.update(
        {
            "bounded_history_chars": _safe_positive_int(provider_history_meta.get("bounded_history_chars")),
            "raw_history_messages": _safe_positive_int(provider_history_meta.get("raw_history_messages")),
            "bounded_history_messages": _safe_positive_int(provider_history_meta.get("bounded_history_messages")),
            "omitted_history_messages": _safe_positive_int(provider_history_meta.get("omitted_history_messages")),
        }
    )
    raw_chars = _safe_positive_int(provider_history_meta.get("raw_history_chars"))
    if raw_chars:
        metrics["raw_history_chars"] = raw_chars
    return metrics


def _thread_health_flags_for_context_budget(
    session: "ChatSession",
    provider_history_meta: dict[str, Any],
) -> list[str]:
    flags = [
        flag
        for flag in session.thread_health_flags
        if flag != "provider_history_bounded"
    ]
    raw_chars = _safe_positive_int(provider_history_meta.get("raw_history_chars"))
    bounded_chars = _safe_positive_int(provider_history_meta.get("bounded_history_chars"))
    provider_history_bounded = (
        _safe_positive_int(provider_history_meta.get("omitted_history_messages")) > 0
        or raw_chars - bounded_chars > MATERIAL_HISTORY_BOUNDING_CHARS
    )
    if provider_history_bounded:
        flags.append("provider_history_bounded")
    return flags


def _holochat_recovery_memory_pack() -> str:
    if _env_flag("HOLOCHAT_MEMORY_PACK_DISABLED"):
        return ""
    return "\n".join(
        [
            f"HOLOBRAIN PINNED MEMORY PACK ({HOLOCHAT_MEMORY_PACK_VERSION}; private, do not surface):",
            "  identity: HoloChat is the local memory-attached chat surface for HoloEngine work.",
            "  recovery_state: After OS recovery, prefer compact HoloBrain state, pinned project anchors, and bounded recent history over raw restored transcript flood.",
            "  user_voice_continuity: Use capsule/HoloBrain-owned voice anchors for the user when supplied; do not hardcode any feedback user into universal behavior.",
            "  voice_anchor: Preserve Holo's one-voice feel; do not let provider rotation, long history, or missing context make the answer bland or amnesic.",
            "  project_priorities: HoloChat context governor, HoloBrain memory fidelity, HoloEngine/HoloVerify boundary clarity, recovery QA, and no-provider verification before live calls.",
        ]
    )


def _captain_brief_block(tenor: Optional[str]) -> str:
    if not tenor:
        return ""
    return (
        "CAPTAIN BRIEF - READ + DIRECTIVE (private, never surface to user):\n"
        + constitutional_prompt_block()
        + "\n\nADMITTED GOV DIRECTIVE:\n"
        + _compact_text(tenor, limit=900)
    )


_EXPLICIT_SEARCH_RE = _re.compile(
    r"\b(search(?:\s+the)?\s+web|web\s+search|browse(?:\s+the)?\s+web|"
    r"look\s+(?:it|this|that)\s+up|find\s+(?:me\s+)?(?:current\s+)?sources?)\b",
    _re.IGNORECASE,
)
_VOLATILE_INFO_RE = _re.compile(
    r"\b("
    r"news|headlines?|price|prices|stock|stocks|weather|forecast|"
    r"score|scores|standings|schedule|ceo|president|prime minister|"
    r"released|release date|availability|outage|service status|updated"
    r")\b",
    _re.IGNORECASE,
)
_CURRENT_FACT_RE = _re.compile(
    r"\b(latest|current|currently|recent|today|tonight|right now)\b"
    r".{0,48}\b(deploy(?:ment)?|status|version|release|update|news|headlines?|"
    r"price|stock|weather|forecast|score|standings|schedule|outage|"
    r"ceo|president|prime minister|availability)\b",
    _re.IGNORECASE,
)


def _compact_text(value: Any, *, limit: int = 160) -> str:
    text = " ".join(str(value or "").strip().split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _deterministic_search_query(user_message: str) -> Optional[str]:
    text = (user_message or "").strip()
    if not text or not (
        _EXPLICIT_SEARCH_RE.search(text)
        or _VOLATILE_INFO_RE.search(text)
        or _CURRENT_FACT_RE.search(text)
    ):
        return None
    return _compact_text(text, limit=180)


def _resolve_search_query(user_message: str, governor_query: Optional[str]) -> tuple[Optional[str], str, str]:
    gov_query = _compact_text(governor_query, limit=180) if governor_query else ""
    if gov_query:
        admission = admit_advisor_search_query(user_message, gov_query)
        if admission.admitted:
            return admission.value, "deterministic_governor", admission.reason
    forced = _deterministic_search_query(user_message)
    if forced:
        return forced, "deterministic", "forced_currentness_trigger"
    return None, "none", "not_needed"


def _web_result_count(results: Optional[str]) -> int:
    if not results:
        return 0
    count = len(_re.findall(r"(?m)^\[S\d+\]\s+", results))
    if not count:
        count = len(_re.findall(r"(?m)^Source:\s+", results))
    return count or 1


def _public_web_sources(bundle: Optional[dict[str, Any]]) -> list[dict[str, Any]]:
    """Expose citation links, never retrieved passages or provider payloads."""
    return [
        {
            key: source.get(key)
            for key in ("source_id", "title", "url", "domain", "published_at")
            if source.get(key) is not None
        }
        for source in (bundle or {}).get("sources") or []
        if isinstance(source, dict)
    ]


def _web_trace(
    query: Optional[str],
    *,
    source: str,
    results: Optional[str],
    run: Optional[web_search.SearchRun] = None,
) -> dict[str, Any]:
    attempted = bool(query)
    if not attempted:
        status = "off"
        unavailable_reason = None
    else:
        status = run.outcome if run is not None else "no_results"
        unavailable_reason = None if status == "checked" else status
    trace = {
        "decision": "search_requested" if attempted else "not_needed",
        "source": source,
        "attempted": attempted,
        "provider": run.provider if run is not None else "tavily",
        "status": status,
        "outcome": status,
        "result_count": run.result_count if run is not None else _web_result_count(results),
        "unavailable_reason": unavailable_reason,
    }
    if run is not None:
        trace.update(run.metadata())
    return trace


def _run_web_search_for_turn(user_message: str, governor_query: Optional[str]) -> tuple[Optional[str], Optional[str], dict[str, Any]]:
    search_query, source, decision = _resolve_search_query(user_message, governor_query)
    run: Optional[web_search.SearchRun] = None
    if search_query:
        run = web_search.run_search(search_query)
    results = run.rendered_text or None if run is not None else None
    trace = _web_trace(search_query, source=source, results=results, run=run)
    evidence_bundle = run.evidence_bundle if run is not None else None
    trace["evidence_bundle"] = evidence_bundle or {}
    trace["evidence_source_ids"] = [
        str(item.get("source_id"))
        for item in (evidence_bundle or {}).get("sources") or []
        if item.get("source_id")
    ]
    trace["evidence_bundle_hash"] = (evidence_bundle or {}).get("bundle_hash")
    trace["decision"] = decision
    return search_query, results, trace


def _retrieve_episode_context(
    brain: Any,
    *,
    capsule_id: Optional[str],
    history: list[dict[str, Any]],
    user_message: str,
    incognito: bool,
    scope_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    if incognito or os.getenv("HOLOCHAT_EXPERIMENT_CONTEXT_MODE") == "control_packet_only":
        return []
    persisted: list[dict[str, Any]] = []
    getter = getattr(brain, "retrieve_relevant_episodes", None)
    if capsule_id and callable(getter):
        try:
            persisted = list(getter(
                capsule_id,
                user_message,
                limit=6,
                token_budget=1600,
                **({"scope_id": scope_id} if scope_id else {}),
            ) or [])
        except Exception as exc:
            logger.warning("HoloBrain episode retrieval failed: %s", exc)
    return merge_episode_context(
        history=history,
        persisted=persisted,
        query=user_message,
        limit=8,
        token_budget=2200,
    )


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
            f"HoloGov reconstructed the turn from Holo-owned state, recent history, "
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
    lines.extend(["", "## HoloGov Read", _compact_text(session_note.get("captain_note") or gov_arc_state.last_gov_read or "", limit=700)])
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
    scope_id: Optional[str] = None,
) -> Optional[str]:
    if not capsule_id or session.handoff_artifact_saved:
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
        **({"scope_id": scope_id} if scope_id else {}),
    )
    if artifact_id:
        session.handoff_artifact_saved = True
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
    input_tokens = _safe_positive_int(provider_input_tokens)
    if input_tokens:
        return input_tokens, "provider_usage"
    if budget_tokens:
        return budget_tokens, "context_budget_estimate"
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


def _holochat_turn_cost_breakdown(
    *,
    worker_usage: Optional[dict[str, Any]],
    gov_turn_plan: Optional[GovTurnPlan],
    failover: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Estimate every model charge in one visible HoloChat turn."""
    worker_usage = dict(worker_usage or {})
    worker_cost = worker_usage.get("estimated_cost_usd")
    control = {}
    if gov_turn_plan is not None:
        control = dict(
            ((gov_turn_plan.telemetry or {}).get("hologov_control_compilation") or {})
        )
    gov_calls: list[dict[str, Any]] = []
    provider = str(control.get("provider") or "").strip().lower()
    model = str(control.get("model") or "").strip()
    input_tokens = _safe_positive_int(control.get("input_tokens"))
    output_tokens = _safe_positive_int(control.get("output_tokens"))
    if provider and model:
        cost, source = _estimate_turn_cost_usd(provider, model, input_tokens, output_tokens)
        gov_calls.append({
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": cost,
            "cost_source": source,
            "call_role": "hologov_fallback" if control.get("gov_fallback") else "hologov_primary",
        })
    fallback = control.get("gov_fallback") or {}
    if fallback.get("active"):
        primary = fallback.get("primary") or {}
        primary_usage = fallback.get("primary_usage") or {}
        primary_provider = str(primary.get("provider") or "").strip().lower()
        primary_model = str(primary.get("model") or "").strip()
        primary_input = _safe_positive_int(primary_usage.get("input_tokens"))
        primary_output = _safe_positive_int(primary_usage.get("output_tokens"))
        if primary_provider and primary_model and (primary_input or primary_output):
            cost, source = _estimate_turn_cost_usd(
                primary_provider,
                primary_model,
                primary_input,
                primary_output,
            )
            gov_calls.insert(0, {
                "provider": primary_provider,
                "model": primary_model,
                "input_tokens": primary_input,
                "output_tokens": primary_output,
                "estimated_cost_usd": cost,
                "cost_source": source,
                "call_role": "hologov_failed_primary",
            })
    gov_costs = [call.get("estimated_cost_usd") for call in gov_calls]
    all_gov_costs_known = bool(gov_calls) and all(value is not None for value in gov_costs)
    known_gov_cost = sum(float(value) for value in gov_costs if value is not None)
    unpriced_failed_attempts = list((failover or {}).get("skipped") or [])
    all_turn_costs_known = all_gov_costs_known and not unpriced_failed_attempts
    return {
        "worker_estimated_cost_usd": worker_cost,
        "hologov_estimated_cost_usd": round(known_gov_cost, 6) if all_gov_costs_known else None,
        "turn_estimated_cost_usd": (
            round(float(worker_cost) + known_gov_cost, 6)
            if worker_cost is not None and all_turn_costs_known
            else None
        ),
        "hologov_calls": gov_calls,
        "unpriced_failed_attempts": unpriced_failed_attempts,
        "estimate": True,
        "pricing_version": _STATIC_CHAT_PRICING_VERSION,
        "pricing_note": "Uses provider-reported tokens when available; exact billing may differ.",
    }


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
    provider_input = _safe_positive_int(provider_input_tokens)
    context_input = _context_budget_input_estimate(context_budget)
    return {
        "input_token_estimate": input_estimate,
        "context_budget_input_token_estimate": context_input,
        "provider_reported_input_tokens": provider_input or None,
        "input_token_reconciliation_delta": (
            provider_input - context_input
            if provider_input and context_input
            else None
        ),
        "output_token_estimate": output_estimate,
        "total_token_estimate": total_estimate,
        "input_token_source": input_source,
        "output_token_source": output_source,
        "latency_ms": _safe_positive_int(latency_ms),
        "estimated_cost_usd": estimated_cost,
        "cost_source": cost_source,
        "cost_is_estimate": True,
        "pricing_version": _STATIC_CHAT_PRICING_VERSION,
        "pricing_note": "Exact provider billing may differ.",
    }


def _turn_runtime_metadata(
    runtime_info: dict[str, Any],
    *,
    analyst_adapter: Any,
    governor: Any,
    governor_checked_this_turn: bool,
    usage: Optional[dict[str, Any]] = None,
    failover: Optional[dict[str, Any]] = None,
    governor_trace: Optional[dict[str, Any]] = None,
    gov_arc_state: Optional[GovArcState] = None,
    frontier_assist: Optional[dict[str, Any]] = None,
    timing_breakdown: Optional[dict[str, Any]] = None,
    context_budget: Optional[dict[str, Any]] = None,
    handoff_transition: Optional[dict[str, Any]] = None,
    holochat_state: Optional[HoloState] = None,
    auto_reseed_present: bool = False,
    holobrain_injection_plan: Optional[HoloBrainInjectionPlan] = None,
    holobrain_state_persisted: bool = False,
    gov_turn_plan: Optional[GovTurnPlan] = None,
    visible_release_decision: Optional[Any] = None,
    web_citation_audit: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    metadata = dict(runtime_info or {})
    selected = _adapter_identity_dict(analyst_adapter)
    handoff_seed_present = bool(_safe_handoff_transition(handoff_transition))
    state_meta = _holochat_state_runtime_metadata(
        holochat_state,
        holobrain_injection_plan=holobrain_injection_plan,
        holobrain_state_persisted=holobrain_state_persisted,
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
            "context_delivery_mode": "ordered_full_history_then_hologov_compaction",
            "lossless_memory_store": "HoloBrain/capsule",
            "analyst_receives_full_memory": False,
            "analyst_receives_ordered_thread_until_pressure": True,
            "structured_state_object_mode": "active",
            "gov_arc_state_mode": "active_private",
            "baton_pass_mode": "active",
            "holo4dna_mode": "enabled"
            if _holo4dna_enabled()
            else ("shadow" if _holo4dna_shadow_enabled() else "off"),
            "reseed_present": bool(handoff_seed_present or auto_reseed_present),
            "reseed_mode": (
                "thread_handoff_seed"
                if handoff_seed_present
                else ("durable_state_auto_reseed" if auto_reseed_present else "off")
            ),
            "thread_handoff_seed_present": handoff_seed_present,
            "durable_state_auto_reseed_present": bool(auto_reseed_present),
            "autoreseed_enabled": True,
            **state_meta,
        }
    )
    if context_budget is not None:
        metadata["context_telemetry"] = {
            "selected_model": selected,
            "gov_model": {
                "provider": getattr(governor, "provider", None) if governor is not None else None,
                "model": getattr(governor, "model_id", getattr(governor, "model", None)) if governor is not None else None,
            },
            "input_token_estimate": _safe_positive_int(context_budget.get("total_token_estimate")),
            "history_context": context_budget.get("history_context", {}),
            "memory_context": context_budget.get("memory_context", {}),
            "holobrain_injection": context_budget.get("holobrain_injection", {}),
            "hologov_packet": context_budget.get("hologov_packet", {}),
            "worker_context_receipt": context_budget.get("worker_context_receipt", {}),
            "thread_health": context_budget.get("thread_health", {}),
        }
    if usage is not None:
        metadata["usage"] = usage
        metadata["cost_breakdown"] = _holochat_turn_cost_breakdown(
            worker_usage=usage,
            gov_turn_plan=gov_turn_plan,
            failover=failover,
        )
    if failover is not None:
        metadata["failover"] = failover
    if governor_trace is not None:
        metadata["governor_trace"] = governor_trace
    if gov_arc_state is not None:
        metadata["gov_arc_state"] = gov_arc_state.model_dump(mode="json")
    if gov_turn_plan is not None:
        metadata["gov_turn_plan"] = gov_turn_plan.model_dump()
    if visible_release_decision is not None:
        metadata["visible_release"] = {
            "release": bool(getattr(visible_release_decision, "release", False)),
            "repaired": bool(getattr(visible_release_decision, "repaired", False)),
            "reason": getattr(visible_release_decision, "reason", None),
        }
    if web_citation_audit is not None:
        metadata["web_citations"] = dict(web_citation_audit)
    if frontier_assist is not None:
        metadata["frontier_assist"] = frontier_assist
    if timing_breakdown is not None:
        metadata["timing_breakdown"] = timing_breakdown
    metadata.update(
        _governor_turn_metadata(
            governor,
            checked_this_turn=governor_checked_this_turn,
        )
    )
    return metadata


def _runtime_metadata(
    runtime_profile: str,
    active_pool: list[Any],
    bench_pool: list[Any],
) -> dict[str, Any]:
    canonical_only = runtime_profile in LEGACY_CANONICAL_RUNTIME_PROFILES
    balanced = runtime_profile == BALANCED_RUNTIME_PROFILE
    frontier_assist_enabled = balanced and bool(bench_pool)
    return {
        "runtime_profile": runtime_profile,
        "model_tier": "experiment" if _holochat_experiment_mode() else _holochat_model_tier(),
        "active_pool": _adapter_pool_metadata(active_pool),
        "bench_pool": _adapter_pool_metadata(bench_pool),
        "frontier_enabled": not canonical_only,
        "frontier_assist_enabled": frontier_assist_enabled,
        "fallback_policy": (
            "canonical_worker_only_no_frontier_fallback"
            if canonical_only
            else ("gov_triggered_frontier_assist" if balanced else "bench_failover_enabled")
        ),
        "serial_call": True,
        "parallel_fanout": False,
    }


def _select_runtime_pools(
    profile: Optional[str] = None,
    *,
    fast_loader=None,
    frontier_loader=None,
) -> tuple[str, list[Any], list[Any]]:
    fast_loader = fast_loader or load_fast_adapters
    frontier_loader = frontier_loader or load_adapters
    runtime_profile = (profile or _holochat_runtime_profile()).strip().lower()
    provider_allowlist = _holochat_model_providers()
    if runtime_profile in LEGACY_CANONICAL_RUNTIME_PROFILES:
        active_pool = _filter_holochat_enabled_adapters(
            _normalize_holochat_model_policy(_call_pool_loader(fast_loader, provider_allowlist))
        )
        active_providers = {str(getattr(adapter, "provider", "")).lower() for adapter in active_pool}
        if active_providers != set(DEFAULT_HOLOCHAT_MODEL_PROVIDERS):
            raise RuntimeError(
                "HoloChat canonical runtime requires both OpenAI and xAI worker adapters; "
                f"available={sorted(active_providers)}; frontier fallback is disabled."
            )
        return runtime_profile, active_pool, []
    if runtime_profile == BALANCED_RUNTIME_PROFILE:
        active_pool = _filter_holochat_enabled_adapters(
            _normalize_holochat_model_policy(_call_pool_loader(fast_loader, provider_allowlist))
        )
        if not active_pool:
            raise RuntimeError("HoloChat balanced runtime has no worker adapters.")
        frontier_active, frontier_bench = _call_pool_loader(
            frontier_loader,
            provider_allowlist,
        )
        frontier_pool = _filter_holochat_enabled_adapters(
            _normalize_holochat_model_policy([*frontier_active, *frontier_bench])
        )
        return runtime_profile, active_pool, frontier_pool
    if runtime_profile in FRONTIER_RUNTIME_PROFILES:
        active_pool, bench_pool = _call_pool_loader(
            frontier_loader,
            provider_allowlist,
        )
        active_pool = _filter_holochat_enabled_adapters(
            _normalize_holochat_model_policy(active_pool)
        )
        bench_pool = _filter_holochat_enabled_adapters(
            _normalize_holochat_model_policy(bench_pool)
        )
        if not active_pool:
            raise RuntimeError("HoloChat frontier runtime has no active adapters.")
        return runtime_profile, active_pool, bench_pool
    raise RuntimeError(f"Unsupported HOLOCHAT_RUNTIME_PROFILE: {runtime_profile}")


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
        self._runtime_profile, self._adapters, self._bench = _select_runtime_pools()
        self._runtime_info = _runtime_metadata(
            self._runtime_profile,
            self._adapters,
            self._bench,
        )
        gov_provider_pool = load_holochat_governor_adapters(
            provider_allowlist=(None if _holochat_experiment_mode() else CANONICAL_HOLOCHAT_GOV_PROVIDERS),
        )
        advisor_pool = gov_provider_pool
        if not advisor_pool:
            raise RuntimeError(
                "HoloChat runtime has no private HoloGov adapter; refusing to reuse a visible worker provider."
            )
        configured_governor = (
            os.getenv("HOLOCHAT_GOV_PROVIDER") or CANONICAL_HOLOCHAT_GOV_PROVIDER
        ).strip().lower() or CANONICAL_HOLOCHAT_GOV_PROVIDER
        fixed_governor = (
            configured_governor
            if _holochat_experiment_mode()
            else CANONICAL_HOLOCHAT_GOV_PROVIDER
        )
        if configured_governor != fixed_governor:
            logger.warning(
                "Ignoring noncanonical HOLOCHAT_GOV_PROVIDER=%s outside experiment mode; using %s",
                configured_governor,
                fixed_governor,
            )
        self._gov_advisor = GovernorAdapter(advisor_pool, fixed_governor=fixed_governor) # provider advisor; deterministic HoloGov admits its proposals
        self._governor = self._gov_advisor  # legacy test/API alias; not canonical authority
        self._runtime_info["hologov_pool"] = _adapter_pool_metadata(advisor_pool)
        self._runtime_info["hologov_policy"] = {
            "primary_provider": fixed_governor,
            "fallback_mode": "local_deterministic_kernel",
            "provider_retry_allowed": False,
            "visible_worker_eligible": False,
            "proposal_authority": "deterministic_kernel_admission_required",
        }
        self._brain    = ProjectBrain()
        self._holo_context_builder = HoloContextBuilder()
        self._holo_router = None
        logger.info(
            f"HoloChatEngine initialized. Runtime profile: {self._runtime_profile} | Active: "
            + ", ".join(a.provider for a in self._adapters)
            + (" | Bench: " + ", ".join(a.provider for a in self._bench) if self._bench else "")
            + " | deterministic HoloGov Kernel ready | GovAdvisor ready"
        )

    def _gov_advisor_adapter(self):
        return getattr(self, "_gov_advisor", None) or getattr(self, "_governor", None)

    @staticmethod
    def _assert_session_owner(
        session: ChatSession,
        capsule_id: Optional[str],
        incognito: bool,
        scope_id: Optional[str] = None,
    ) -> None:
        if (
            session.incognito != incognito
            or session.owner_capsule_id != capsule_id
            or session.owner_scope_id != scope_id
        ):
            raise SessionOwnershipError("Chat session ownership mismatch")

    def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        *,
        capsule_id: Optional[str] = None,
        incognito: bool = False,
        scope_id: Optional[str] = None,
    ) -> ChatSession:
        if session_id and session_id in _sessions:
            session = _sessions[session_id]
            self._assert_session_owner(session, capsule_id, incognito, scope_id)
            return session
        new_id  = session_id or str(uuid.uuid4())
        session = ChatSession(
            session_id=new_id,
            owner_capsule_id=capsule_id,
            owner_scope_id=scope_id,
            incognito=incognito,
        )

        # Restore history from Supabase if the session_id is known but not in memory
        # (e.g. after a server restart)
        if session_id:
            get_stored_session = getattr(self._brain, "get_chat_session", None)
            stored_session = get_stored_session(session_id) if callable(get_stored_session) else None
            if incognito and stored_session is not None:
                raise SessionOwnershipError("Incognito session conflicts with durable session")

        if session_id and not incognito:
            if stored_session:
                durable_owner = stored_session.get("scope_id") if scope_id else stored_session.get("capsule_id")
                if durable_owner != (scope_id or capsule_id):
                    raise SessionOwnershipError("Durable chat session ownership mismatch")
                prior = self._brain.load_chat_history(session_id, **({"scope_id": scope_id} if scope_id else {}))
            elif not callable(getattr(self._brain, "get_chat_session", None)):
                # Backward-compatible no-provider test doubles predate durable
                # session metadata. Production ProjectBrain always has this API.
                prior = self._brain.load_chat_history(session_id)
            else:
                prior = None
            if prior:
                session.history      = prior
                session.turn_count   = sum(1 for m in prior if m["role"] == "user")
                session.rotation_index = session.turn_count % len(_rotation_analyst_adapters(self._adapters))
                if _memory_steward_enabled() and scope_id:
                    load_checkpoint = getattr(self._brain, "load_latest_memory_checkpoint", None)
                    checkpoint = load_checkpoint(
                        session_id=session_id,
                        scope_id=scope_id,
                    ) if callable(load_checkpoint) else None
                    restored_turns = tuple(
                        MemoryTurnInput(
                            message_id=f"{session_id}:restored:{index}",
                            role=message["role"],
                            text=message["content"],
                            input_tokens=estimate_context_tokens(message["content"]),
                        )
                        for index, message in enumerate(prior, start=1)
                        if message.get("role") in {"user", "assistant", "system"}
                    )
                    watermark_sequence = min(
                        int((checkpoint or {}).get("end_sequence") or 0),
                        len(restored_turns),
                    )
                    session.memory_steward_state = restore_memory_steward_state(
                        session_id,
                        "hologov-canonical",
                        restored_turns,
                        watermark_sequence=watermark_sequence,
                        watermark_hash=str((checkpoint or {}).get("transcript_hash") or ""),
                    )
                logger.info(f"Restored session {session_id[:8]} from brain ({session.turn_count} turns).")

        _sessions[new_id] = session
        logger.info(f"Chat session ready: {new_id[:8]}")
        return session

    def send_message(self, session_id: str, user_message: str,
                     capsule_id: Optional[str] = None,
                     scope_id: Optional[str] = None,
                     images: Optional[List[Dict[str, Any]]] = None,
                     incognito: bool = False,
                     handoff_transition: Optional[dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process one user message. Returns Holo's response + metadata.
        The caller should use session_id from the returned dict for follow-up turns.

        incognito=True: blind mode — no capsule context, no Governor memory, no life portrait
        injected. Base system prompt only. Used for unbiased evaluation runs.
        """
        session             = self.get_or_create_session(
            session_id,
            capsule_id=capsule_id,
            incognito=incognito,
            scope_id=scope_id,
        )
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
            raw_capsule_context = self._brain.get_capsule_context(
                capsule_id, **({"scope_id": scope_id} if scope_id else {})
            ) if capsule_id else {}
            capsule_context = _capsule_context_for_depth_preference(raw_capsule_context)
            life_context    = self._brain.load_life_context(
                capsule_id, **({"scope_id": scope_id} if scope_id else {})
            ) if capsule_id else []
            last_session    = self._brain.load_last_consolidation(
                capsule_id, **({"scope_id": scope_id} if scope_id else {})
            ) if capsule_id and session.turn_count == 0 else None
            durable_state   = load_state_from_capsule_context(raw_capsule_context)
            if durable_state and session.holochat_state is None:
                session.holochat_state = durable_state
        session.worker_context_receipt = {}
        session.episode_retrieval_trace = {
            "authorized": bool(capsule_id and not incognito),
            "authority": "deterministic_hologov_preworker_context_operation",
            "capsule_scoped": bool(capsule_id and not incognito),
        }
        session.retrieved_episodes = _retrieve_episode_context(
            self._brain,
            capsule_id=capsule_id,
            history=session.history,
            user_message=user_message,
            incognito=incognito,
            scope_id=scope_id,
        )
        fresh_thread = session.turn_count == 0
        _add_timing(timings, "memory_context_ms", memory_timer)

        auto_reseed_present = False
        holochat_state_block = ""
        holobrain_injection_plan = HoloBrainInjectionPlan(
            mode=HoloBrainInjectionMode.NONE,
            payload="",
            reason="not_evaluated",
        )

        active_handoff_transition = None if incognito else _apply_handoff_transition_to_session(
            session,
            handoff_transition,
        )

        # Rotate through the canonical worker pool so every configured worker gets turns.
        adapter = _select_analyst_adapter(session, self._adapters)
        initial_adapter = adapter
        session.turn_count     += 1
        adapter_history = _bounded_adapter_history(session.history, query_text=user_message)
        gov_advisor = self._gov_advisor_adapter()
        single_hologov_call = _single_hologov_call_enabled(
            getattr(self, "_runtime_profile", "")
        )
        gov_api_calls_before = _governor_api_call_count(gov_advisor)
        turn_policy = deterministic_turn_policy(
            user_message,
            history=session.history,
        )

        gov_pre_timer = _timer_start()
        # Governor rotation policy:
        # Lock to one provider for 7–11 turns. Rotate only when the thread is
        # healthy and no active work is mid-resolution. The no-same-family rule
        # is enforced by prepare_for_turn() on every rotation.
        if _should_rotate_governor(session):
            gov_advisor.prepare_for_turn(adapter)
            session.governor_provider        = gov_advisor.provider
            session.governor_locked_since    = session.turn_count
            session.governor_rotation_threshold = random.randint(7, 11)
            if session.turn_count > 1:
                logger.info(
                    f"HoloGov rotated → {session.governor_provider} "
                    f"(next rotation in {session.governor_rotation_threshold} turns)"
                )
        else:
            gov_advisor.lock_to_provider(session.governor_provider)

        # Canonical HoloChat spends its single HoloGov call on the rich typed
        # packet immediately before the worker. Supporting controls stay local.
        if single_hologov_call:
            temperature = _deterministic_worker_temperature(turn_policy)
            governor_search_query = None
            raw_thought = None
            thought_admission = admit_advisor_surface_thought(None)
            thought = None
            raw_tenor = None
            tenor_admission = None
            tenor = None
        else:
            advisor_temperature = gov_advisor.assess_chat_temperature(user_message, session.history)
            temperature = max(0.2, min(0.9, float(advisor_temperature or 0.5)))
            if turn_policy.tier in {"high", "max"}:
                temperature = min(temperature, 0.35)
            elif turn_policy.tier == "fast":
                temperature = min(temperature, 0.4)
            governor_search_query = gov_advisor.should_search(user_message, session.history)
            raw_thought = None if incognito else gov_advisor.surface_thought(
                session.history,
                capsule_context,
                baton_pass=_health_context(session),
            )
            thought_admission = admit_advisor_surface_thought(raw_thought)
            thought = thought_admission.value if thought_admission.admitted else None
            raw_tenor = None if incognito else gov_advisor.assess_tenor(
                session.history,
                capsule_context,
                turn_count=session.turn_count,
                analyst_provider=adapter.provider,
            )
            tenor_admission = admit_advisor_prompt_directive(
                raw_tenor,
                user_message=user_message,
            ) if raw_tenor or not incognito else None
            tenor = tenor_admission.value if tenor_admission and tenor_admission.admitted else None
        _add_timing(timings, "governor_pre_ms", gov_pre_timer)

        web_timer = _timer_start()
        search_query, search_results, web_trace = _run_web_search_for_turn(user_message, governor_search_query)
        session.web_evidence_bundle = dict(web_trace.pop("evidence_bundle", {}) or {})
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

        frontier_assist_enabled = (
            getattr(self, "_runtime_profile", DEFAULT_RUNTIME_PROFILE) == BALANCED_RUNTIME_PROFILE
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
                governor=gov_advisor,
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
                f"[ADMITTED WEB EVIDENCE: Use only relevant sources below for web-derived claims. "
                f"Cite those claims inline with the supplied [S#] identifiers and never invent a source. "
                f"If the evidence is insufficient or irrelevant, say so plainly.]\n\n"
                f"{search_results}"
            )
            logger.info(f"  Search query: '{search_query}'")

        logger.info(
            f"Chat turn {session.turn_count} | session={session.session_id[:8]} | "
            f"analyst={adapter.provider} | gov_advisor={gov_advisor.provider} | temp={temperature:.2f}"
            + (" | INCOGNITO" if incognito else "")
        )

        runtime_identity = build_runtime_identity_block(
            getattr(self, "_runtime_info", {}),
            capsule_attached=bool(capsule_id and not incognito),
        )

        pre_gate_context_budget = _runtime_context_budget(
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
            holochat_state_block="",
            holobrain_injection_plan=holobrain_injection_plan,
            gov_turn_plan_block="",
        )
        if (
            not incognito
            and session.holochat_state
            and os.getenv("HOLOCHAT_EXPERIMENT_CONTEXT_MODE") != "control_packet_only"
        ):
            holobrain_injection_plan = build_holobrain_injection_plan(
                session.holochat_state,
                thread_status=session.thread_status,
                context_budget=pre_gate_context_budget,
                fresh_thread=fresh_thread,
                recovery_needed=_holobrain_recovery_needed(user_message),
                topic_shift=_holobrain_topic_shift(user_message),
                artifact_needed=_holobrain_artifact_needed(user_message),
            )
            holochat_state_block = _holochat_state_seed_block(holobrain_injection_plan)
            auto_reseed_present = (
                holobrain_injection_plan.mode == HoloBrainInjectionMode.FULL_RESEED
                and bool(holochat_state_block)
            )
            if auto_reseed_present:
                session.auto_reseed_applied = True
                session.auto_reseed_hash = stable_hash(holochat_state_block)

        # Stable worker identity stays small. HoloGov alone reads HoloBrain and
        # state; the candidate-specific GovTurnPlan carries the admitted projection
        # immediately before the visible worker call.
        base_system_prompt = HOLO_CHAT_SYSTEM_PROMPT + "\n\n" + runtime_identity
        if not incognito and active_handoff_transition:
            base_system_prompt += "\n\n" + _thread_handoff_transition_block(active_handoff_transition)
        gov_turn_plan = None
        gov_turn_plan_block = ""
        context_budget = None

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

        # Call the adapter. If the selected worker is down, skip forward through
        # the active pool before falling back to any bench pool in non-canonical profiles.
        analyst_timer = _timer_start()
        failover_attempts: list[dict[str, Optional[str]]] = []
        last_err: Optional[Exception] = None
        response_text = ""
        in_tok = out_tok = 0
        control_compilation_cache: dict[str, Any] = {}
        candidate_order = _adapter_candidate_order_for_attachments(self._adapters, adapter, images)
        for candidate in candidate_order:
            try:
                candidate_plan = _build_worker_gov_turn_plan(
                    session=session,
                    capsule_id=capsule_id,
                    adapter=candidate,
                    gov_advisor=gov_advisor,
                    turn_policy=turn_policy,
                    temperature=temperature,
                    tenor=tenor,
                    tenor_admission=tenor_admission,
                    thought_admission=thought_admission,
                    user_message=user_message,
                    search_query=search_query,
                    search_results=search_results,
                    web_trace=web_trace,
                    capsule_context=capsule_context,
                    life_context=life_context,
                    last_session=last_session,
                    incognito=incognito,
                    active_handoff_transition=active_handoff_transition,
                    holochat_state_block=holochat_state_block,
                    holobrain_injection_plan=holobrain_injection_plan,
                    frontier_assist=frontier_assist,
                    worker_fallback_active=bool(failover_attempts),
                    control_compilation_cache=control_compilation_cache,
                )
                if not candidate_plan.kernel_validation_result.get("passed"):
                    failures = ",".join(candidate_plan.kernel_validation_result.get("failures") or [])
                    raise RuntimeError(f"GovTurnPlan validation failed: {failures}")
                candidate_plan_block = render_gov_turn_plan_for_worker(candidate_plan)
                candidate_system_prompt = base_system_prompt + "\n\n" + candidate_plan_block
                _record_worker_context_delivery(
                    session=session,
                    plan=candidate_plan,
                    system_prompt=candidate_system_prompt,
                    history=adapter_history,
                    user_prompt=enriched_message,
                )
                candidate_context_budget = _runtime_context_budget(
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
                    holochat_state_block=holochat_state_block,
                    holobrain_injection_plan=holobrain_injection_plan,
                    gov_turn_plan_block=candidate_plan_block,
                    gov_turn_plan=candidate_plan,
                )
                response_text, in_tok, out_tok = candidate.chat_call(
                    candidate_system_prompt, adapter_history, enriched_message, temperature,
                    images=images or None,
                )
                adapter = candidate
                gov_turn_plan = candidate_plan
                gov_turn_plan_block = candidate_plan_block
                context_budget = candidate_context_budget
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
                fallback_plan = _build_worker_gov_turn_plan(
                    session=session,
                    capsule_id=capsule_id,
                    adapter=fallback,
                    gov_advisor=gov_advisor,
                    turn_policy=turn_policy,
                    temperature=temperature,
                    tenor=tenor,
                    tenor_admission=tenor_admission,
                    thought_admission=thought_admission,
                    user_message=user_message,
                    search_query=search_query,
                    search_results=search_results,
                    web_trace=web_trace,
                    capsule_context=capsule_context,
                    life_context=life_context,
                    last_session=last_session,
                    incognito=incognito,
                    active_handoff_transition=active_handoff_transition,
                    holochat_state_block=holochat_state_block,
                    holobrain_injection_plan=holobrain_injection_plan,
                    frontier_assist=frontier_assist,
                    worker_fallback_active=True,
                    control_compilation_cache=control_compilation_cache,
                )
                if not fallback_plan.kernel_validation_result.get("passed"):
                    failures = ",".join(fallback_plan.kernel_validation_result.get("failures") or [])
                    raise RuntimeError(f"GovTurnPlan validation failed: {failures}")
                fallback_plan_block = render_gov_turn_plan_for_worker(fallback_plan)
                fallback_system_prompt = base_system_prompt + "\n\n" + fallback_plan_block
                _record_worker_context_delivery(
                    session=session,
                    plan=fallback_plan,
                    system_prompt=fallback_system_prompt,
                    history=adapter_history,
                    user_prompt=enriched_message,
                )
                fallback_context_budget = _runtime_context_budget(
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
                    holochat_state_block=holochat_state_block,
                    holobrain_injection_plan=holobrain_injection_plan,
                    gov_turn_plan_block=fallback_plan_block,
                    gov_turn_plan=fallback_plan,
                )
                response_text, in_tok, out_tok = fallback.chat_call(
                    fallback_system_prompt, adapter_history, enriched_message, temperature,
                    images=images or None,
                )
                adapter = fallback
                gov_turn_plan = fallback_plan
                gov_turn_plan_block = fallback_plan_block
                context_budget = fallback_context_budget
            except Exception as exc:
                failover_attempts.append(_safe_adapter_error(fallback, exc))
                raise
        elapsed_ms = _elapsed_timer_ms(analyst_timer)
        if session.worker_context_receipt:
            session.worker_context_receipt = {
                **session.worker_context_receipt,
                "provider_reported_input_tokens": _safe_positive_int(in_tok),
            }
            context_budget["worker_context_receipt"] = dict(session.worker_context_receipt)
        _add_timing(timings, "analyst_ms", analyst_timer)
        failover = _analyst_failover_metadata(
            initial_adapter=initial_adapter,
            final_adapter=adapter,
            attempts=failover_attempts,
            policy=(
                "balanced_frontier_assist_then_next_canonical_worker"
                if frontier_assist.get("triggered")
                else "try_next_canonical_worker_then_bench"
            ),
        )

        if holo4dna_shadow is not None:
            actual_analyst = _adapter_identity_dict(adapter)
            recorded_analyst = holo4dna_shadow.metadata["route"]["runtime_analyst"]
            if actual_analyst != recorded_analyst:
                holo4dna_shadow.metadata["route"]["runtime_analyst_after_failover"] = actual_analyst
                holo4dna_shadow.trace.extra_metadata["runtime_analyst_after_failover"] = actual_analyst

        gov_post_timer = _timer_start()
        # Canonical mode does not make a hidden post-worker HoloGov call. The
        # worker, admitted web context, and deterministic release gate own release.
        flagged_claims = []
        if not single_hologov_call:
            response_text, flagged_claims = gov_advisor.verify_claims(
                response_text, web_search.search
            )
        if flagged_claims:
            correction_admission = admit_advisor_claim_corrections(flagged_claims)
            corrections = list(correction_admission.value or []) if correction_admission.admitted else []
            if corrections:
                note = " · ".join(corrections)
                response_text += f"\n\n*One thing worth correcting: {note}*"

        release_decision = deterministic_visible_release(user_message, response_text)
        response_text = release_decision.text
        response_text, web_citation_audit = admit_web_citations(
            response_text,
            session.web_evidence_bundle,
        )

        conversation_paths = []
        if not single_hologov_call:
            path_generator = getattr(gov_advisor, "generate_conversation_paths", None)
            if path_generator and not incognito:
                conversation_paths = path_generator(
                    history=session.history,
                    capsule_context=capsule_context,
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
                self._brain, response_text, capsule_id, session.session_id, session.turn_count,
                scope_id=scope_id,
            )

        # Commit both turns to history
        session.history.append({"role": "user",      "content": user_message})
        session.history.append({"role": "assistant",  "content": response_text})

        memory_steward_trace = _advance_memory_steward(
            session=session,
            brain=self._brain,
            capsule_id=capsule_id,
            scope_id=scope_id,
            user_message=user_message,
            response_text=response_text,
            gov_turn_plan=gov_turn_plan,
            context_budget=context_budget,
        )
        context_budget["memory_steward"] = memory_steward_trace

        # Link session to capsule on first turn — skipped in incognito
        if capsule_id and session.turn_count == 1 and not incognito:
            self._brain.set_capsule_context(capsule_id, "last_session_id", session.session_id, **({"scope_id": scope_id} if scope_id else {}))
            self._brain.append_session_history(capsule_id, session.session_id, user_message, **({"scope_id": scope_id} if scope_id else {}))

        # Governor learns — extract any new facts about the user and persist them
        # Skipped in incognito: blind sessions must not pollute the capsule portrait
        memory_extraction_attempted = False
        memory_writes_count = 0
        if capsule_id and not incognito:
            memory_extraction_attempted = True
            gov_post_timer = _timer_start()
            if single_hologov_call:
                updates = _memory_updates_from_hologov_plan(
                    gov_turn_plan,
                    user_message=user_message,
                )
            else:
                proposed_updates = gov_advisor.extract_context_updates(session.history, capsule_context)
                memory_admission = admit_advisor_memory_updates(proposed_updates)
                updates = dict(memory_admission.value or {}) if memory_admission.admitted else {}
            for key, value in updates.items():
                self._brain.set_capsule_context(capsule_id, key, value, **({"scope_id": scope_id} if scope_id else {}))
            memory_writes_count = len(updates)
            _add_timing(timings, "governor_post_ms", gov_post_timer)
            if updates:
                logger.info(f"Capsule context updated for {capsule_id[:8]}: {list(updates.keys())}")

        # Governor consolidates — skipped in incognito
        if _claim_autocompact_for_context_window(
            session,
            capsule_id=capsule_id,
            incognito=incognito,
            context_budget=context_budget,
        ) and not single_hologov_call:
            def _consolidate():
                try:
                    proposed_result = gov_advisor.consolidate_session(
                        session.history, capsule_context, session.session_id
                    )
                    consolidation_admission = admit_advisor_consolidation(proposed_result)
                    result = dict(consolidation_admission.value or {}) if consolidation_admission.admitted else {}
                    if result.get("session_note"):
                        self._brain.save_consolidation(
                            capsule_id, session.session_id, result["session_note"],
                            **({"scope_id": scope_id} if scope_id else {}),
                        )
                    if result.get("life_context"):
                        self._brain.upsert_life_context(capsule_id, result["life_context"], **({"scope_id": scope_id} if scope_id else {}))
                    _save_thread_handoff_artifact(
                        self._brain,
                        capsule_id=capsule_id,
                        session=session,
                        consolidation=result,
                        scope_id=scope_id,
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
            if single_hologov_call:
                packet = (gov_turn_plan.narrative_packet or {}) if gov_turn_plan else {}
                active_topics = packet.get("active_threads") or packet.get("topic_registry") or []
                proposed_name = (
                    _compact_text(active_topics[0].get("subject"), limit=60)
                    if active_topics and isinstance(active_topics[0], dict)
                    else _compact_text(user_message, limit=60)
                )
                name_admission = admit_advisor_thread_name(proposed_name)
                if name_admission.admitted and name_admission.value:
                    self._brain.update_session_name(capsule_id, session.session_id, name_admission.value, **({"scope_id": scope_id} if scope_id else {}))
            else:
                _hist = list(session.history)
                _sid  = session.session_id
                _cid  = capsule_id
                _scope_id = scope_id
                def _name_thread():
                    try:
                        name_admission = admit_advisor_thread_name(gov_advisor.name_session(_hist))
                        if name_admission.admitted and name_admission.value:
                            self._brain.update_session_name(_cid, _sid, name_admission.value, **({"scope_id": _scope_id} if _scope_id else {}))
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
            scope_id      = scope_id,
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
        state_auto_compact = should_auto_compact(
            context_budget=context_budget,
            thread_health_level=session.thread_health_level,
            thread_health_score=session.thread_health_score,
        )
        holobrain_state_persisted = False
        previous_holobrain_state = session.holochat_state
        next_holobrain_state = build_holochat_state(
            session_id=session.session_id,
            capsule_id=None if incognito else capsule_id,
            turn_number=session.turn_count,
            user_message=user_message,
            response_text=response_text,
            previous_state=session.holochat_state,
            artifacts_saved=artifacts_saved,
            required_tools=_required_tools_for_turn(search_query, search_results),
            gov_arc_state=session.gov_arc_state,
            thread_health_score=session.thread_health_score,
            thread_status=session.thread_status,
            auto_compact=state_auto_compact,
            governor_rolling_summary=(
                (gov_turn_plan.narrative_packet or {}).get("rolling_summary")
                if gov_turn_plan is not None
                else None
            ),
            hologov_control_ledger=_hologov_control_ledger_from_plan(
                gov_turn_plan,
                user_message=user_message,
                response_text=response_text,
                worker_identity=_adapter_identity_dict(adapter),
                turn_number=session.turn_count,
                worker_context_receipt=session.worker_context_receipt,
            ),
        )
        session.holochat_state = next_holobrain_state
        if not incognito:
            holobrain_state_persisted = has_meaningful_holobrain_delta(
                previous_holobrain_state,
                next_holobrain_state,
            )
            if holobrain_state_persisted:
                _persist_holochat_state(self._brain, capsule_id, session.holochat_state)

        gov_api_calls_this_turn = max(
            0,
            _governor_api_call_count(gov_advisor) - gov_api_calls_before,
        )
        usage = _turn_usage_metadata(
            analyst_adapter=adapter,
            context_budget=context_budget,
            response_text=response_text,
            provider_input_tokens=in_tok,
            provider_output_tokens=out_tok,
            latency_ms=elapsed_ms,
        )
        runtime = _turn_runtime_metadata(
            getattr(
                self,
                "_runtime_info",
                _runtime_metadata("test_runtime", self._adapters, self._bench),
            ),
            analyst_adapter=adapter,
            governor=gov_advisor,
            governor_checked_this_turn=True,
            usage=usage,
            failover=failover,
            governor_trace=_governor_trace_metadata(
                web_trace=web_trace,
                incognito=incognito,
                memory_extraction_attempted=memory_extraction_attempted,
                memory_writes_count=memory_writes_count,
                conversation_paths_count=len(conversation_paths),
                thread_health_level=session.thread_health_level,
                single_call_mode=single_hologov_call,
                api_calls_this_turn=gov_api_calls_this_turn,
            ),
            gov_arc_state=session.gov_arc_state,
            frontier_assist=frontier_assist,
            timing_breakdown=_timing_breakdown_metadata(
                timings,
                turn_started_at=turn_started_at,
            ),
            context_budget=context_budget,
            handoff_transition=active_handoff_transition,
            holochat_state=session.holochat_state,
            auto_reseed_present=auto_reseed_present,
            holobrain_injection_plan=holobrain_injection_plan,
            holobrain_state_persisted=holobrain_state_persisted,
            gov_turn_plan=gov_turn_plan,
            visible_release_decision=release_decision,
            web_citation_audit=web_citation_audit,
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
            "web_sources":         _public_web_sources(session.web_evidence_bundle),
            "web_citations":       web_citation_audit,
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
                       scope_id: Optional[str] = None,
                       images: Optional[List[Dict[str, Any]]] = None,
                       incognito: bool = False,
                       handoff_transition: Optional[dict[str, Any]] = None):
        """
        Generator variant of send_message.

        Buffers provider stream chunks behind deterministic release guards, then
        yields admitted text and a final sentinel dict once streaming is complete:
          {"done": True, "session_id": ..., "turn_number": ..., "thought": ...,
           "thread_health_level": ..., "thread_health_score": ..., "searched": bool,
           "artifacts": [...], "handoff": ...}

        The Governor's pre-turn work (temperature, search decision, tenor) runs
        synchronously before streaming starts. Post-turn work (context extraction,
        consolidation, thread naming, Supabase persist) runs in a background thread
        after the stream completes so the caller never blocks on it.
        """
        session             = self.get_or_create_session(
            session_id,
            capsule_id=capsule_id,
            incognito=incognito,
            scope_id=scope_id,
        )
        session.last_active = time.time()
        turn_started_at = _timer_start()
        timings: dict[str, int] = {}

        memory_timer = _timer_start()
        if incognito:
            capsule_context = {}
            life_context    = []
            last_session    = None
        else:
            raw_capsule_context = self._brain.get_capsule_context(capsule_id, **({"scope_id": scope_id} if scope_id else {})) if capsule_id else {}
            capsule_context = _capsule_context_for_depth_preference(raw_capsule_context)
            life_context    = self._brain.load_life_context(capsule_id, **({"scope_id": scope_id} if scope_id else {})) if capsule_id else []
            last_session    = self._brain.load_last_consolidation(capsule_id, **({"scope_id": scope_id} if scope_id else {})) if capsule_id and session.turn_count == 0 else None
            durable_state   = load_state_from_capsule_context(raw_capsule_context)
            if durable_state and session.holochat_state is None:
                session.holochat_state = durable_state
        session.worker_context_receipt = {}
        session.episode_retrieval_trace = {
            "authorized": bool(capsule_id and not incognito),
            "authority": "deterministic_hologov_preworker_context_operation",
            "capsule_scoped": bool(capsule_id and not incognito),
        }
        session.retrieved_episodes = _retrieve_episode_context(
            self._brain,
            capsule_id=capsule_id,
            history=session.history,
            user_message=user_message,
            incognito=incognito,
            scope_id=scope_id,
        )
        fresh_thread = session.turn_count == 0
        _add_timing(timings, "memory_context_ms", memory_timer)

        auto_reseed_present = False
        holochat_state_block = ""
        holobrain_injection_plan = HoloBrainInjectionPlan(
            mode=HoloBrainInjectionMode.NONE,
            payload="",
            reason="not_evaluated",
        )

        active_handoff_transition = None if incognito else _apply_handoff_transition_to_session(
            session,
            handoff_transition,
        )

        adapter = _select_analyst_adapter(session, self._adapters)
        initial_adapter = adapter
        session.turn_count     += 1
        adapter_history = _bounded_adapter_history(session.history, query_text=user_message)
        gov_advisor = self._gov_advisor_adapter()
        single_hologov_call = _single_hologov_call_enabled(
            getattr(self, "_runtime_profile", "")
        )
        gov_api_calls_before = _governor_api_call_count(gov_advisor)
        turn_policy = deterministic_turn_policy(
            user_message,
            history=session.history,
        )

        gov_pre_timer = _timer_start()
        if _should_rotate_governor(session):
            gov_advisor.prepare_for_turn(adapter)
            session.governor_provider             = gov_advisor.provider
            session.governor_locked_since         = session.turn_count
            session.governor_rotation_threshold   = random.randint(7, 11)
        else:
            gov_advisor.lock_to_provider(session.governor_provider)

        if single_hologov_call:
            temperature = _deterministic_worker_temperature(turn_policy)
            governor_search_query = None
            raw_thought = None
            thought_admission = admit_advisor_surface_thought(None)
            thought = None
            raw_tenor = None
            tenor_admission = None
            tenor = None
        else:
            advisor_temperature = gov_advisor.assess_chat_temperature(user_message, session.history)
            temperature = max(0.2, min(0.9, float(advisor_temperature or 0.5)))
            if turn_policy.tier in {"high", "max"}:
                temperature = min(temperature, 0.35)
            elif turn_policy.tier == "fast":
                temperature = min(temperature, 0.4)
            governor_search_query = gov_advisor.should_search(user_message, session.history)
            raw_thought = None if incognito else gov_advisor.surface_thought(
                session.history,
                capsule_context,
                baton_pass=_health_context(session),
            )
            thought_admission = admit_advisor_surface_thought(raw_thought)
            thought = thought_admission.value if thought_admission.admitted else None
            raw_tenor = None if incognito else gov_advisor.assess_tenor(
                session.history,
                capsule_context,
                turn_count=session.turn_count,
                analyst_provider=adapter.provider,
            )
            tenor_admission = admit_advisor_prompt_directive(
                raw_tenor,
                user_message=user_message,
            ) if raw_tenor or not incognito else None
            tenor = tenor_admission.value if tenor_admission and tenor_admission.admitted else None
        _add_timing(timings, "governor_pre_ms", gov_pre_timer)

        web_timer = _timer_start()
        search_query, search_results, web_trace = _run_web_search_for_turn(user_message, governor_search_query)
        session.web_evidence_bundle = dict(web_trace.pop("evidence_bundle", {}) or {})
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

        frontier_assist_enabled = (
            getattr(self, "_runtime_profile", DEFAULT_RUNTIME_PROFILE) == BALANCED_RUNTIME_PROFILE
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
                governor=gov_advisor,
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
                f"[ADMITTED WEB EVIDENCE: Use only relevant sources below for web-derived claims. "
                f"Cite those claims inline with the supplied [S#] identifiers and never invent a source. "
                f"If the evidence is insufficient or irrelevant, say so plainly.]\n\n"
                f"{search_results}"
            )

        runtime_identity = build_runtime_identity_block(
            getattr(self, "_runtime_info", {}),
            capsule_attached=bool(capsule_id and not incognito),
        )

        pre_gate_context_budget = _runtime_context_budget(
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
            holochat_state_block="",
            holobrain_injection_plan=holobrain_injection_plan,
            gov_turn_plan_block="",
        )
        if (
            not incognito
            and session.holochat_state
            and os.getenv("HOLOCHAT_EXPERIMENT_CONTEXT_MODE") != "control_packet_only"
        ):
            holobrain_injection_plan = build_holobrain_injection_plan(
                session.holochat_state,
                thread_status=session.thread_status,
                context_budget=pre_gate_context_budget,
                fresh_thread=fresh_thread,
                recovery_needed=_holobrain_recovery_needed(user_message),
                topic_shift=_holobrain_topic_shift(user_message),
                artifact_needed=_holobrain_artifact_needed(user_message),
            )
            holochat_state_block = _holochat_state_seed_block(holobrain_injection_plan)
            auto_reseed_present = (
                holobrain_injection_plan.mode == HoloBrainInjectionMode.FULL_RESEED
                and bool(holochat_state_block)
            )
            if auto_reseed_present:
                session.auto_reseed_applied = True
                session.auto_reseed_hash = stable_hash(holochat_state_block)

        # Build the small stable prompt body once. HoloGov's candidate-specific
        # plan is the only state/memory projection sent to the streaming worker.
        base_system_prompt = HOLO_CHAT_SYSTEM_PROMPT + "\n\n" + runtime_identity
        if not incognito and active_handoff_transition:
            base_system_prompt += "\n\n" + _thread_handoff_transition_block(active_handoff_transition)
        gov_turn_plan = None
        gov_turn_plan_block = ""
        context_budget = None

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

        # Stream from the provider internally, but do not release raw chunks to
        # the UI before deterministic visible-output admission.
        accumulated = []
        in_tok = out_tok = 0
        analyst_timer = _timer_start()
        failover_attempts: list[dict[str, Optional[str]]] = []
        last_err: Optional[Exception] = None
        stream_completed = False
        control_compilation_cache: dict[str, Any] = {}
        candidate_order = _adapter_candidate_order_for_attachments(self._adapters, adapter, images)
        for candidate in candidate_order:
            candidate_chunks: list[str] = []
            emitted = False
            try:
                candidate_plan = _build_worker_gov_turn_plan(
                    session=session,
                    capsule_id=capsule_id,
                    adapter=candidate,
                    gov_advisor=gov_advisor,
                    turn_policy=turn_policy,
                    temperature=temperature,
                    tenor=tenor,
                    tenor_admission=tenor_admission,
                    thought_admission=thought_admission,
                    user_message=user_message,
                    search_query=search_query,
                    search_results=search_results,
                    web_trace=web_trace,
                    capsule_context=capsule_context,
                    life_context=life_context,
                    last_session=last_session,
                    incognito=incognito,
                    active_handoff_transition=active_handoff_transition,
                    holochat_state_block=holochat_state_block,
                    holobrain_injection_plan=holobrain_injection_plan,
                    frontier_assist=frontier_assist,
                    worker_fallback_active=bool(failover_attempts),
                    control_compilation_cache=control_compilation_cache,
                )
                if not candidate_plan.kernel_validation_result.get("passed"):
                    failures = ",".join(candidate_plan.kernel_validation_result.get("failures") or [])
                    raise RuntimeError(f"GovTurnPlan validation failed: {failures}")
                candidate_plan_block = render_gov_turn_plan_for_worker(candidate_plan)
                candidate_system_prompt = base_system_prompt + "\n\n" + candidate_plan_block
                _record_worker_context_delivery(
                    session=session,
                    plan=candidate_plan,
                    system_prompt=candidate_system_prompt,
                    history=adapter_history,
                    user_prompt=enriched_message,
                )
                candidate_context_budget = _runtime_context_budget(
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
                    holochat_state_block=holochat_state_block,
                    holobrain_injection_plan=holobrain_injection_plan,
                    gov_turn_plan_block=candidate_plan_block,
                    gov_turn_plan=candidate_plan,
                )
                for chunk in candidate.stream_chat_call(
                    candidate_system_prompt, adapter_history, enriched_message, temperature, images=images or None
                ):
                    if isinstance(chunk, dict) and chunk.get("done"):
                        in_tok  = chunk.get("in_tok", 0)
                        out_tok = chunk.get("out_tok", 0)
                    else:
                        emitted = True
                        candidate_chunks.append(chunk)
                accumulated.extend(candidate_chunks)
                adapter = candidate
                gov_turn_plan = candidate_plan
                gov_turn_plan_block = candidate_plan_block
                context_budget = candidate_context_budget
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
        if session.worker_context_receipt:
            session.worker_context_receipt = {
                **session.worker_context_receipt,
                "provider_reported_input_tokens": _safe_positive_int(in_tok),
            }
            context_budget["worker_context_receipt"] = dict(session.worker_context_receipt)
        _add_timing(timings, "analyst_ms", analyst_timer)
        failover = _analyst_failover_metadata(
            initial_adapter=initial_adapter,
            final_adapter=adapter,
            attempts=failover_attempts,
            policy=(
                "balanced_frontier_assist_then_next_canonical_worker"
                if frontier_assist.get("triggered")
                else "try_next_canonical_worker"
            ),
        )

        if holo4dna_shadow is not None:
            actual_analyst = _adapter_identity_dict(adapter)
            recorded_analyst = holo4dna_shadow.metadata["route"]["runtime_analyst"]
            if actual_analyst != recorded_analyst:
                holo4dna_shadow.metadata["route"]["runtime_analyst_after_failover"] = actual_analyst
                holo4dna_shadow.trace.extra_metadata["runtime_analyst_after_failover"] = actual_analyst

        gov_post_timer = _timer_start()
        # Canonical streaming uses the same one-call HoloGov contract.
        flagged_claims = []
        if not single_hologov_call:
            response_text, flagged_claims = gov_advisor.verify_claims(response_text, web_search.search)
        if flagged_claims:
            correction_admission = admit_advisor_claim_corrections(flagged_claims)
            corrections = list(correction_admission.value or []) if correction_admission.admitted else []
            if corrections:
                note = " · ".join(corrections)
                response_text += f"\n\n*One thing worth correcting: {note}*"

        release_decision = deterministic_visible_release(user_message, response_text)
        response_text = release_decision.text
        response_text, web_citation_audit = admit_web_citations(
            response_text,
            session.web_evidence_bundle,
        )
        if response_text:
            yield response_text

        conversation_paths = []
        if not single_hologov_call:
            path_generator = getattr(gov_advisor, "generate_conversation_paths", None)
            if path_generator and not incognito:
                conversation_paths = path_generator(
                    history=session.history,
                    capsule_context=capsule_context,
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

        memory_steward_trace = _advance_memory_steward(
            session=session,
            brain=self._brain,
            capsule_id=capsule_id,
            scope_id=scope_id,
            user_message=user_message,
            response_text=response_text,
            gov_turn_plan=gov_turn_plan,
            context_budget=context_budget,
        )
        context_budget["memory_steward"] = memory_steward_trace

        # Extract artifacts
        artifacts_saved = []
        if capsule_id and not incognito:
            artifacts_saved = _extract_and_save_artifacts(
                self._brain, response_text, capsule_id, session.session_id, session.turn_count,
                scope_id=scope_id,
            )

        # Link session on first turn
        if capsule_id and session.turn_count == 1 and not incognito:
            self._brain.set_capsule_context(capsule_id, "last_session_id", session.session_id, **({"scope_id": scope_id} if scope_id else {}))
            self._brain.append_session_history(capsule_id, session.session_id, user_message, **({"scope_id": scope_id} if scope_id else {}))

        admitted_memory_updates = (
            _memory_updates_from_hologov_plan(gov_turn_plan, user_message=user_message)
            if single_hologov_call and capsule_id and not incognito
            else {}
        )

        # Background: persistence only in canonical one-call mode. Legacy modes
        # retain their provider-backed auxiliary behavior for controlled comparison.
        def _post_stream():
            try:
                if capsule_id and not incognito:
                    if single_hologov_call:
                        updates = admitted_memory_updates
                    else:
                        proposed_updates = gov_advisor.extract_context_updates(session.history, capsule_context)
                        memory_admission = admit_advisor_memory_updates(proposed_updates)
                        updates = dict(memory_admission.value or {}) if memory_admission.admitted else {}
                    for key, value in updates.items():
                        self._brain.set_capsule_context(capsule_id, key, value, **({"scope_id": scope_id} if scope_id else {}))
                    if _claim_autocompact_for_context_window(
                        session,
                        capsule_id=capsule_id,
                        incognito=incognito,
                        context_budget=context_budget,
                    ) and not single_hologov_call:
                        proposed_result = gov_advisor.consolidate_session(session.history, capsule_context, session.session_id)
                        consolidation_admission = admit_advisor_consolidation(proposed_result)
                        result = dict(consolidation_admission.value or {}) if consolidation_admission.admitted else {}
                        if result.get("session_note"):
                            self._brain.save_consolidation(capsule_id, session.session_id, result["session_note"], **({"scope_id": scope_id} if scope_id else {}))
                        if result.get("life_context"):
                            self._brain.upsert_life_context(capsule_id, result["life_context"], **({"scope_id": scope_id} if scope_id else {}))
                        _save_thread_handoff_artifact(
                            self._brain,
                            capsule_id=capsule_id,
                            session=session,
                            consolidation=result,
                            scope_id=scope_id,
                        )
                    if session.turn_count == 2:
                        if single_hologov_call:
                            packet = (gov_turn_plan.narrative_packet or {}) if gov_turn_plan else {}
                            active_topics = packet.get("active_threads") or packet.get("topic_registry") or []
                            proposed_name = (
                                _compact_text(active_topics[0].get("subject"), limit=60)
                                if active_topics and isinstance(active_topics[0], dict)
                                else _compact_text(user_message, limit=60)
                            )
                        else:
                            proposed_name = gov_advisor.name_session(list(session.history))
                        name_admission = admit_advisor_thread_name(proposed_name)
                        if name_admission.admitted and name_admission.value:
                            self._brain.update_session_name(capsule_id, session.session_id, name_admission.value, **({"scope_id": scope_id} if scope_id else {}))
                self._brain.save_chat_turn(
                    session_id    = session.session_id,
                    turn_number   = session.turn_count,
                    user_message  = user_message,
                    holo_response = response_text,
                    provider      = adapter.provider,
                    temperature   = temperature,
                    capsule_id    = capsule_id,
                    scope_id      = scope_id,
                )
            except Exception as e:
                logger.warning(f"Post-stream background task failed: {e}")

        threading.Thread(target=_post_stream, daemon=True).start()

        if holo4dna_shadow is not None:
            holo4dna_shadow.trace.memory_extraction_attempted = bool(capsule_id and not incognito)
            holo4dna_shadow.trace.memory_writes_count = len(admitted_memory_updates)
            log_trace(holo4dna_shadow.trace, logger=logger)

        handoff = _handoff_for_context_window(session)

        _update_gov_arc_state(
            session,
            user_message=user_message,
            tenor=tenor,
            web_trace=web_trace,
            conversation_paths=conversation_paths,
            memory_writes_count=len(admitted_memory_updates),
            handoff=handoff,
        )
        state_auto_compact = should_auto_compact(
            context_budget=context_budget,
            thread_health_level=session.thread_health_level,
            thread_health_score=session.thread_health_score,
        )
        holobrain_state_persisted = False
        previous_holobrain_state = session.holochat_state
        next_holobrain_state = build_holochat_state(
            session_id=session.session_id,
            capsule_id=None if incognito else capsule_id,
            turn_number=session.turn_count,
            user_message=user_message,
            response_text=response_text,
            previous_state=session.holochat_state,
            artifacts_saved=artifacts_saved,
            required_tools=_required_tools_for_turn(search_query, search_results),
            gov_arc_state=session.gov_arc_state,
            thread_health_score=session.thread_health_score,
            thread_status=session.thread_status,
            auto_compact=state_auto_compact,
            governor_rolling_summary=(
                (gov_turn_plan.narrative_packet or {}).get("rolling_summary")
                if gov_turn_plan is not None
                else None
            ),
            hologov_control_ledger=_hologov_control_ledger_from_plan(
                gov_turn_plan,
                user_message=user_message,
                response_text=response_text,
                worker_identity=_adapter_identity_dict(adapter),
                turn_number=session.turn_count,
                worker_context_receipt=session.worker_context_receipt,
            ),
        )
        session.holochat_state = next_holobrain_state
        if not incognito:
            holobrain_state_persisted = has_meaningful_holobrain_delta(
                previous_holobrain_state,
                next_holobrain_state,
            )
            if holobrain_state_persisted:
                _persist_holochat_state(self._brain, capsule_id, session.holochat_state)

        gov_api_calls_this_turn = max(
            0,
            _governor_api_call_count(gov_advisor) - gov_api_calls_before,
        )
        usage = _turn_usage_metadata(
            analyst_adapter=adapter,
            context_budget=context_budget,
            response_text=response_text,
            provider_input_tokens=in_tok,
            provider_output_tokens=out_tok,
            latency_ms=elapsed_ms,
        )
        runtime = _turn_runtime_metadata(
            getattr(
                self,
                "_runtime_info",
                _runtime_metadata("test_runtime", self._adapters, self._bench),
            ),
            analyst_adapter=adapter,
            governor=gov_advisor,
            governor_checked_this_turn=True,
            usage=usage,
            failover=failover,
            governor_trace=_governor_trace_metadata(
                web_trace=web_trace,
                incognito=incognito,
                memory_extraction_attempted=bool(capsule_id and not incognito),
                memory_writes_count=len(admitted_memory_updates),
                conversation_paths_count=len(conversation_paths),
                thread_health_level=session.thread_health_level,
                single_call_mode=single_hologov_call,
                api_calls_this_turn=gov_api_calls_this_turn,
            ),
            gov_arc_state=session.gov_arc_state,
            frontier_assist=frontier_assist,
            timing_breakdown=_timing_breakdown_metadata(
                timings,
                turn_started_at=turn_started_at,
            ),
            context_budget=context_budget,
            handoff_transition=active_handoff_transition,
            holochat_state=session.holochat_state,
            auto_reseed_present=auto_reseed_present,
            holobrain_injection_plan=holobrain_injection_plan,
            holobrain_state_persisted=holobrain_state_persisted,
            gov_turn_plan=gov_turn_plan,
            visible_release_decision=release_decision,
            web_citation_audit=web_citation_audit,
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
            "web_sources":         _public_web_sources(session.web_evidence_bundle),
            "web_citations":       web_citation_audit,
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

    def get_history(
        self,
        session_id: str,
        *,
        capsule_id: Optional[str] = None,
        incognito: bool = False,
        scope_id: Optional[str] = None,
    ) -> Optional[List[Dict[str, str]]]:
        session = _sessions.get(session_id)
        if session:
            self._assert_session_owner(session, capsule_id, incognito, scope_id)
        return session.history if session else None

    def clear_session(
        self,
        session_id: str,
        *,
        capsule_id: Optional[str] = None,
        incognito: bool = False,
        scope_id: Optional[str] = None,
    ) -> bool:
        if session_id in _sessions:
            self._assert_session_owner(_sessions[session_id], capsule_id, incognito, scope_id)
            del _sessions[session_id]
            return True
        return False

    def checkpoint_memory_lifecycle(
        self,
        session_id: str,
        lifecycle: str,
        *,
        capsule_id: Optional[str],
        scope_id: Optional[str],
    ) -> dict[str, Any]:
        """Persist an explicit thread lifecycle boundary without a provider call."""
        if not _memory_steward_enabled() or not capsule_id or not scope_id:
            return {"enabled": False, "status": "disabled_or_unscoped"}
        session = self.get_or_create_session(
            session_id,
            capsule_id=capsule_id,
            scope_id=scope_id,
        )
        lifecycle_kind = {
            "thread_open": MemoryLifecycleKind.THREAD_OPEN,
            "thread_fork": MemoryLifecycleKind.THREAD_FORK,
            "idle": MemoryLifecycleKind.IDLE,
            "before_autocompact": MemoryLifecycleKind.BEFORE_AUTOCOMPACT,
        }.get(str(lifecycle or "").strip().lower())
        if lifecycle_kind is None:
            raise ValueError("Unsupported memory lifecycle event")
        return _checkpoint_memory_lifecycle(
            session=session,
            brain=self._brain,
            capsule_id=capsule_id,
            scope_id=scope_id,
            lifecycle_kind=lifecycle_kind,
        )

    def checkpoint_idle_sessions(
        self,
        *,
        idle_seconds: float,
        now: Optional[float] = None,
    ) -> list[dict[str, Any]]:
        """Checkpoint in-memory signed-in sessions after an idle boundary."""
        if not _memory_steward_enabled():
            return []
        cutoff_now = float(now if now is not None else time.time())
        results: list[dict[str, Any]] = []
        for session in list(_sessions.values()):
            if (
                session.incognito
                or not session.owner_capsule_id
                or not session.owner_scope_id
                or cutoff_now - session.last_active < max(1.0, float(idle_seconds))
            ):
                continue
            result = _checkpoint_memory_lifecycle(
                session=session,
                brain=self._brain,
                capsule_id=session.owner_capsule_id,
                scope_id=session.owner_scope_id,
                lifecycle_kind=MemoryLifecycleKind.IDLE,
            )
            if result.get("status") not in {"no_delta", "disabled_or_unscoped"}:
                results.append({"session_id": session.session_id, **result})
        return results


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


def _govturnplan_context_selection(
    *,
    incognito: bool,
    capsule_context: dict,
    life_context: list,
    last_session: Optional[dict],
    handoff_transition: Optional[dict[str, Any]],
    holochat_state_block: Optional[str],
    holobrain_injection_plan: HoloBrainInjectionPlan,
    search_results: Optional[str],
    retrieved_episodes: Optional[list[dict[str, Any]]] = None,
    evidence_bundle: Optional[dict[str, Any]] = None,
) -> tuple[list[str], list[str], dict[str, str], list[dict[str, Any]], list[dict[str, Any]]]:
    selected = ["runtime_identity", "thread_health", "gov_arc_state", "user_message"]
    dropped: list[str] = []
    reasons: dict[str, str] = {}
    memory_admissions: list[dict[str, Any]] = []
    memory_rejections: list[dict[str, Any]] = []

    def mark_context(context_id: str, present: bool, *, reason: str, memory: bool = False) -> None:
        if present and not incognito:
            selected.append(context_id)
            if memory:
                memory_admissions.append({"context_id": context_id, "admission": "selected_for_prompt_by_deterministic_gov"})
        else:
            dropped.append(context_id)
            reasons[context_id] = "incognito_mode" if incognito else reason
            if memory:
                memory_rejections.append({"context_id": context_id, "reason": reasons[context_id]})

    mark_context("holochat_state_object", bool(holochat_state_block), reason="empty", memory=True)
    mark_context("holochat_memory_pack", bool(_holochat_recovery_memory_pack()), reason="disabled", memory=True)
    mark_context("life_context", bool(life_context), reason="empty", memory=True)
    mark_context("latest_consolidation", bool(last_session), reason="empty", memory=True)
    mark_context("capsule_context", bool(capsule_context), reason="empty", memory=True)
    mark_context("thread_handoff_seed", bool(handoff_transition), reason="empty", memory=False)
    for episode in retrieved_episodes or []:
        episode_id = str(episode.get("episode_id") or "").strip()
        if episode_id:
            mark_context(f"episode:{episode_id}", True, reason="not_selected", memory=True)
    for source in (evidence_bundle or {}).get("sources") or []:
        source_id = str(source.get("source_id") or "").strip()
        if source_id:
            selected.append(f"evidence:{source_id}")
    if search_results:
        selected.append("web_results")
    else:
        dropped.append("web_results")
        reasons["web_results"] = "no web results"
    if holobrain_injection_plan.mode != HoloBrainInjectionMode.NONE:
        selected.append(f"holobrain_injection:{holobrain_injection_plan.mode.value}")
    return selected, dropped, reasons, memory_admissions, memory_rejections


def _worker_continuity_baton(
    *,
    session: ChatSession,
    tenor: Optional[str],
    capsule_context: dict,
    life_context: list,
    holobrain_injection_plan: HoloBrainInjectionPlan,
    turn_policy: Any,
    user_message: str,
) -> str:
    provider_history = _bounded_adapter_history(session.history, query_text=user_message)
    history_meta = _provider_history_metadata(
        provider_history,
        total_history_messages=len(session.history),
        raw_history=session.history,
    )
    omitted = _safe_positive_int(history_meta.get("omitted_history_messages"))
    lines = [
        "Answer as the visible HoloChat worker with conversational warmth, truthful precision, and useful forward motion.",
        "One goal: serve the user's best interests; never scold, prosecute, flatter, or fake intimacy.",
        "You are a transient worker entering this turn; treat HoloGov's packet as the canonical state scaffold.",
        "Treat the ordered raw thread as primary conversational evidence; use HoloGov's control ledger to navigate it without flattening it.",
        "HoloGov is the only HoloBrain operator; use only the HoloBrain context HoloGov admitted into this packet.",
    ]
    if tenor:
        if "Relationship repair mode" in tenor:
            repair_directive = tenor[tenor.index("Relationship repair mode") :]
            lines.append(f"Admitted HoloGov tenor for this turn: {_compact_text(repair_directive, limit=360)}")
        else:
            lines.append(f"Admitted HoloGov tenor for this turn: {_compact_text(tenor, limit=360)}")
    if omitted:
        lines.append(
            f"Continuity alert: {omitted} older raw history message(s) are omitted from the provider history; "
            "do not treat the visible recent transcript as complete."
        )
    if holobrain_injection_plan.mode == HoloBrainInjectionMode.ROLLING_SUMMARY:
        lines.append(
            "Use the HoloBrain rolling summary as the conversation spine: preserve the user's arc, current tension, "
            "settled boundaries, and best prior insight across worker rotation."
        )
    elif holobrain_injection_plan.mode == HoloBrainInjectionMode.FULL_RESEED:
        lines.append(
            "Use the HoloBrain auto-reseed as the continuity spine for this turn; it is the compact state bridge."
        )
    elif holobrain_injection_plan.mode == HoloBrainInjectionMode.BATON_ONLY:
        lines.append(
            "Use the HoloBrain baton plus portrait context for continuity; do not over-infer beyond supplied memory."
        )
    if capsule_context or life_context:
        lines.append(
            "User portrait: use HoloBrain capsule/life context as grounding for style, boundaries, and priorities; "
            "never recite private details or turn them into accusatory theory."
        )
    arc = session.gov_arc_state
    if arc.current_tension:
        lines.append(f"Current tension to preserve: {_compact_text(arc.current_tension, limit=220)}")
    if arc.next_paths:
        lines.append(
            "Natural next paths: "
            + "; ".join(_compact_text(path, limit=120) for path in arc.next_paths[:3])
        )
    if getattr(turn_policy, "tier", "") in {"high", "max"}:
        lines.append(
            "High-stakes turn: prefer bounded honesty over certainty theater; ask for missing facts when needed."
        )
    return "\n".join(lines)


def _life_context_portrait_lines(life_context: list, *, limit: int = 8) -> list[str]:
    lines: list[str] = []
    for entry in life_context or []:
        if not isinstance(entry, dict):
            continue
        key = _compact_text(entry.get("key") or entry.get("category") or "context", limit=64)
        if _is_sensitive_holobrain_key(key):
            continue
        value = _compact_text(entry.get("value"), limit=180)
        if value:
            lines.append(f"{key}: {value}")
        if len(lines) >= limit:
            break
    return lines


def _capsule_portrait_lines(capsule_context: dict, *, limit: int = 8) -> list[str]:
    lines: list[str] = []
    for key, value in (capsule_context or {}).items():
        key_text = _compact_text(key, limit=64)
        if _is_sensitive_holobrain_key(key_text):
            continue
        value_text = _compact_text(value, limit=180)
        if key_text and value_text:
            lines.append(f"{key_text}: {value_text}")
        if len(lines) >= limit:
            break
    return lines


_SENSITIVE_HOLOBRAIN_KEY_PARTS = (
    "password", "secret", "token", "api_key", "apikey", "credential",
    "authorization", "bearer", "cookie", "jwt", "hash",
)


def _is_sensitive_holobrain_key(key: Any) -> bool:
    normalized = str(key or "").strip().lower()
    return normalized.startswith("_") or any(part in normalized for part in _SENSITIVE_HOLOBRAIN_KEY_PARTS)


def _holobrain_worker_projection(
    *,
    capsule_context: dict,
    life_context: list,
    last_session: Optional[dict[str, Any]],
    injection_plan: HoloBrainInjectionPlan,
) -> dict[str, Any]:
    """Build the only HoloBrain projection a visible worker may receive."""
    restricted_mode = injection_plan.mode in {
        HoloBrainInjectionMode.NONE,
        HoloBrainInjectionMode.HASHES_ONLY,
        HoloBrainInjectionMode.ARTIFACT_REFS,
    }
    if restricted_mode:
        return {
            "authority": "HoloGov-selected worker projection; no raw HoloBrain library access",
            "injection_mode": injection_plan.mode.value,
            "injection_reason": injection_plan.reason,
            "state_hash": injection_plan.state_hash,
            "durable_context": [],
            "latest_session": {},
            "source_counts": {
                "capsule_keys_available": len(capsule_context or {}),
                "life_entries_available": len(life_context or []),
                "durable_items_admitted": 0,
            },
        }
    portrait: list[str] = []
    for item in _capsule_portrait_lines(capsule_context, limit=10) + _life_context_portrait_lines(life_context, limit=10):
        if item not in portrait:
            portrait.append(item)
    latest: dict[str, Any] = {}
    if isinstance(last_session, dict):
        surfaced = _compact_text(last_session.get("what_surfaced"), limit=700)
        captain_note = _compact_text(last_session.get("captain_note"), limit=500)
        open_threads = last_session.get("open_threads") or []
        if surfaced:
            latest["what_surfaced"] = surfaced
        if captain_note:
            latest["carry_forward"] = captain_note
        if isinstance(open_threads, list):
            latest["open_threads"] = [
                _compact_text(item, limit=240) for item in open_threads[:8] if _compact_text(item, limit=240)
            ]
    return {
        "authority": "HoloGov-selected worker projection; no raw HoloBrain library access",
        "injection_mode": injection_plan.mode.value,
        "injection_reason": injection_plan.reason,
        "durable_context": portrait[:16],
        "latest_session": latest,
        "source_counts": {
            "capsule_keys_available": len(capsule_context or {}),
            "life_entries_available": len(life_context or []),
            "durable_items_admitted": min(16, len(portrait)),
        },
    }


def _memory_lifecycle_status(key: Any, value: Any, *, confidence: Any = None, pruned_at: Any = None) -> str:
    text = f"{key} {value}".lower()
    if pruned_at:
        return "archived"
    if "forgotten" in text or "forget_requested" in text:
        return "forgotten"
    if "contradict" in text or "no longer true" in text or "superseded" in text:
        return "contradicted"
    try:
        score = float(confidence)
    except (TypeError, ValueError):
        score = None
    if score is not None and score < 0.35:
        return "stale"
    if "[inferred]" in text or "inferred" in text:
        return "inferred"
    if "[candidate]" in text or "candidate" in text:
        return "candidate"
    return "active"


def _normalized_memory_value(value: Any) -> str:
    return " ".join(str(value or "").lower().split())[:180]


def _holobrain_stewardship_plan(
    *,
    capsule_context: dict,
    life_context: list,
    last_session: Optional[dict],
    holochat_state: Optional[HoloState],
) -> dict[str, Any]:
    status_counts = {
        "candidate": 0,
        "active": 0,
        "confirmed": 0,
        "inferred": 0,
        "stale": 0,
        "archived": 0,
        "contradicted": 0,
        "forgotten": 0,
    }
    candidates: list[dict[str, Any]] = []
    seen_values: dict[str, str] = {}
    duplicate_pairs: list[dict[str, str]] = []

    def add_record(source: str, key: Any, value: Any, *, confidence: Any = None, pruned_at: Any = None):
        status = _memory_lifecycle_status(key, value, confidence=confidence, pruned_at=pruned_at)
        status_counts[status] = status_counts.get(status, 0) + 1
        normalized = _normalized_memory_value(value)
        key_text = _compact_text(key, limit=80)
        if normalized and normalized in seen_values and len(duplicate_pairs) < 6:
            duplicate_pairs.append({"first": seen_values[normalized], "second": key_text})
        elif normalized:
            seen_values[normalized] = key_text
        if status in {"candidate", "inferred", "stale", "contradicted", "archived", "forgotten"} and len(candidates) < 12:
            candidates.append(
                {
                    "source": source,
                    "key": key_text,
                    "status": status,
                    "confidence": confidence,
                    "reason": _compact_text(value, limit=180),
                }
            )

    for key, value in (capsule_context or {}).items():
        if str(key).startswith("_"):
            continue
        add_record("capsule_context", key, value)

    for entry in life_context or []:
        if not isinstance(entry, dict):
            continue
        add_record(
            "life_context",
            entry.get("key") or entry.get("category") or "memory",
            entry.get("value"),
            confidence=entry.get("confidence"),
            pruned_at=entry.get("pruned_at"),
        )

    actions: list[dict[str, Any]] = []
    if duplicate_pairs:
        actions.append(
            {
                "action": "consolidate_duplicates",
                "count": len(duplicate_pairs),
                "authority": "HoloGov_review_required",
            }
        )
    if status_counts.get("inferred"):
        actions.append(
            {
                "action": "confirm_or_reject_inferred_memory",
                "count": status_counts["inferred"],
                "authority": "HoloGov_review_required",
            }
        )
    if status_counts.get("stale") or status_counts.get("contradicted"):
        actions.append(
            {
                "action": "archive_or_prune_review",
                "count": status_counts.get("stale", 0) + status_counts.get("contradicted", 0),
                "authority": "HoloGov_review_required_kernel_enforced",
            }
        )
    if last_session:
        actions.append(
            {
                "action": "fold_latest_consolidation_into_rolling_summary",
                "count": 1,
                "authority": "HoloGov_review_required",
            }
        )
    if holochat_state and getattr(holochat_state, "rolling_summary", ""):
        actions.append(
            {
                "action": "preserve_iterative_rolling_summary",
                "count": 1,
                "authority": "HoloGov_active_state",
            }
        )

    return {
        "mode": "stewardship_scan_v0",
        "authority": "HoloGov-only; non-destructive until kernel-authorized memory operation",
        "status_counts": status_counts,
        "review_candidates": candidates,
        "duplicate_candidates": duplicate_pairs,
        "actions": actions or [
            {
                "action": "preserve_active_memory",
                "count": status_counts.get("active", 0),
                "authority": "HoloGov_active_state",
            }
        ],
        "raw_library_access_for_worker": False,
    }


_ACCUSATORY_HOLOGOV_RE = _re.compile(
    r"(?i)(?:"
    r"\b(?:the user|this person|they|he|she)\s+(?:is|are|seems?|appears?)\s+"
    r"(?:manipulative|lazy|dishonest|irrational|evasive|delusional|attention[- ]seeking|"
    r"avoidant|defensive|resistant|unaccountable)\b|"
    r"\b(?:the user|this person|they|he|she)\s+(?:keeps?\s+)?"
    r"(?:deflects?|deflecting|avoids? accountability|refuses? to listen|makes? excuses)\b|"
    r"\b(?:you|your)\s+(?:keep\s+)?(?:deflecting|avoiding accountability|making excuses)\b|"
    r"\b(?:your|their) pattern is (?:evasive|avoidant|defensive|manipulative)\b"
    r")"
)


def _merge_hologov_rolling_summary(
    baseline: dict[str, Any],
    candidate: str,
    *,
    limit: int,
) -> str:
    """Keep a bounded deterministic spine when a provider summary omits it."""
    prior = _compact_text(baseline.get("rolling_summary"), limit=1600)
    spine_lines: list[str] = []
    if prior:
        spine_lines.append(f"Origin and prior arc: {prior}")
    for label, field_name, count in (
        ("Settled", "settled_decisions", 4),
        ("Open", "unresolved_questions", 4),
        ("Anchor", "key_anchors", 4),
    ):
        for item in list(baseline.get(field_name) or [])[-count:]:
            text = _compact_text(item, limit=320)
            if text:
                spine_lines.append(f"{label}: {text}")
    for item in list(baseline.get("contradictions") or [])[-3:]:
        if not isinstance(item, dict) or str(item.get("status") or "").lower() == "reconciled":
            continue
        left = _compact_text(item.get("claim_a"), limit=220)
        right = _compact_text(item.get("claim_b"), limit=220)
        if left or right:
            spine_lines.append(f"Unresolved contradiction: {left} / {right}".strip(" /"))
    if not spine_lines:
        return candidate

    candidate_normalized = " ".join(candidate.lower().split())
    missing = [
        line for line in spine_lines
        if " ".join(line.split(":", 1)[-1].lower().split()) not in candidate_normalized
    ]
    if not missing:
        return candidate
    prefix = "CANONICAL SPINE\n" + "\n".join(f"- {line}" for line in missing)
    available = max(0, limit - len(prefix) - 2)
    return prefix + ("\n\n" + candidate[-available:] if available and candidate else "")


def _hologov_state_payload(state: Optional[HoloState]) -> dict[str, Any]:
    if state is None:
        return {}
    try:
        data = state.model_dump(mode="json")
    except TypeError:
        data = state.model_dump()
    # HoloGov already receives the complete ordered transcript and HoloBrain
    # sources separately. Send the canonical control spine, not duplicated audit
    # metadata and artifact payloads.
    return {
        "schema_version": data.get("schema_version"),
        "turn_number": data.get("turn_number"),
        "user_goal": data.get("user_goal"),
        "latest_input_summary": data.get("latest_input_summary"),
        "critical_constraints": list(data.get("critical_constraints") or [])[:14],
        "rolling_summary": _compact_text(data.get("rolling_summary"), limit=10000),
        "settled_decisions": list(data.get("settled_decisions") or [])[:24],
        "hologov_control_ledger": dict(data.get("hologov_control_ledger") or {}),
        "gov_arc_state": dict(data.get("gov_arc_state") or {}),
        "thread_health": dict(data.get("thread_health") or {}),
        "user_portrait": list(data.get("user_portrait") or []),
        "topic_registry": list(data.get("topic_registry") or []),
        "episode_registry": list(data.get("episode_registry") or []),
        "evidence_ledger": list(data.get("evidence_ledger") or []),
        "worker_context_receipt": dict(data.get("worker_context_receipt") or {}),
    }


_TOPIC_ID_RE = _re.compile(r"[^a-z0-9_-]+")
_TOPIC_WORD_RE = _re.compile(r"[a-z0-9][a-z0-9_-]{2,}")
_TOPIC_STOP_WORDS = {
    "about", "after", "again", "also", "because", "could", "from", "have",
    "into", "just", "maybe", "should", "that", "their", "there", "these",
    "they", "this", "what", "when", "where", "which", "with", "would", "your",
}
_TOPIC_STATUSES = {"active", "parked", "resolved", "superseded"}


def _topic_turn_number(value: Any, *, default: int) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return max(0, default)


def _topic_subject_key(subject: Any) -> str:
    return " ".join(_TOPIC_WORD_RE.findall(str(subject or "").lower()))


def _topic_terms(subject: Any) -> set[str]:
    return {
        term
        for term in _TOPIC_WORD_RE.findall(str(subject or "").lower())
        if term not in _TOPIC_STOP_WORDS
    }


def _topic_lane_id(subject: Any, requested_id: Any = None) -> str:
    cleaned = _TOPIC_ID_RE.sub("-", str(requested_id or "").strip().lower()).strip("-_")
    if cleaned:
        return cleaned[:64]
    subject_key = _topic_subject_key(subject) or "conversation"
    return f"topic-{stable_hash(subject_key)[:12]}"


def _fallback_topic_subject(user_message: str) -> str:
    first_sentence = _re.split(r"(?<=[.!?])\s+", _compact_text(user_message, limit=220), maxsplit=1)[0]
    return _compact_text(first_sentence or "Current conversation", limit=120)


def _normalize_topic_registry_record(
    item: dict[str, Any],
    *,
    default_status: str,
    turn_number: int,
) -> dict[str, Any]:
    subject = _compact_text(item.get("subject") or item.get("summary") or "Conversation topic", limit=180)
    status = str(item.get("status") or default_status).strip().lower()
    if status not in _TOPIC_STATUSES:
        status = default_status
    origin_turn = _topic_turn_number(item.get("origin_turn"), default=turn_number)
    last_turn = _topic_turn_number(item.get("last_turn"), default=turn_number)
    source_turns: list[int] = []
    for raw in item.get("source_turn_ids") or item.get("source_turns") or []:
        parsed = _topic_turn_number(raw, default=-1)
        if parsed >= 0 and parsed not in source_turns:
            source_turns.append(parsed)
    record = {
        "id": _topic_lane_id(subject, item.get("id")),
        "subject": subject,
        "status": status,
        "origin_turn": origin_turn,
        "last_turn": max(origin_turn, last_turn),
        "importance": str(item.get("importance") or "medium").strip().lower()[:12],
        "summary": _compact_text(item.get("summary") or subject, limit=700),
        "source_turn_ids": source_turns[-24:],
        "resurface_count": _topic_turn_number(item.get("resurface_count"), default=0),
    }
    reason = _compact_text(item.get("reason") or item.get("park_reason"), limit=260)
    if reason:
        record["park_reason"] = reason
    return record


def _previous_topic_registry(packet: dict[str, Any], *, turn_number: int) -> list[dict[str, Any]]:
    raw_registry = packet.get("topic_registry")
    if isinstance(raw_registry, list) and raw_registry:
        return [
            _normalize_topic_registry_record(item, default_status="parked", turn_number=turn_number)
            for item in raw_registry
            if isinstance(item, dict)
        ]
    records: list[dict[str, Any]] = []
    for field_name, status in (
        ("active_threads", "active"),
        ("parked_threads", "parked"),
        ("resolved_threads", "resolved"),
    ):
        for item in packet.get(field_name) or []:
            if isinstance(item, dict):
                records.append(
                    _normalize_topic_registry_record(item, default_status=status, turn_number=turn_number)
                )
    return records


def _match_previous_topic(
    item: dict[str, Any],
    previous: list[dict[str, Any]],
) -> Optional[dict[str, Any]]:
    requested_id = _topic_lane_id(item.get("subject"), item.get("id"))
    by_id = next((record for record in previous if record.get("id") == requested_id), None)
    if by_id:
        return by_id
    subject_key = _topic_subject_key(item.get("subject"))
    exact = next(
        (record for record in previous if _topic_subject_key(record.get("subject")) == subject_key),
        None,
    )
    if exact:
        return exact
    terms = _topic_terms(item.get("subject"))
    best: tuple[float, Optional[dict[str, Any]]] = (0.0, None)
    for record in previous:
        prior_terms = _topic_terms(record.get("subject"))
        if not terms or not prior_terms:
            continue
        overlap = len(terms & prior_terms) / max(1, len(terms | prior_terms))
        if overlap > best[0]:
            best = (overlap, record)
    return best[1] if best[0] >= 0.6 else None


def _reconcile_topic_registry(
    *,
    baseline: dict[str, Any],
    proposals: dict[str, list[dict[str, Any]]],
    user_message: str,
    turn_number: int,
) -> dict[str, Any]:
    """Preserve topic identity while admitting HoloGov-created lane transitions."""
    previous = _previous_topic_registry(baseline, turn_number=max(0, turn_number - 1))
    registry: dict[str, dict[str, Any]] = {record["id"]: dict(record) for record in previous}
    events: list[dict[str, Any]] = []

    registry_proposals = list(proposals.get("topic_registry") or [])
    for item in registry_proposals:
        status = str(item.get("status") or "parked").lower()
        target = {
            "active": "active_threads",
            "parked": "parked_threads",
            "resolved": "resolved_threads",
            "superseded": "resolved_threads",
        }.get(status, "parked_threads")
        existing = proposals.get(target) or []
        item_id = _topic_lane_id(item.get("subject"), item.get("id"))
        item_subject = _topic_subject_key(item.get("subject"))
        if not any(
            _topic_lane_id(other.get("subject"), other.get("id")) == item_id
            or _topic_subject_key(other.get("subject")) == item_subject
            for other in existing
        ):
            proposals.setdefault(target, []).append(item)

    resurfaced_by_id: dict[str, dict[str, Any]] = {}
    for item in proposals.get("resurfaced_threads") or []:
        prior = _match_previous_topic(item, previous)
        lane_id = prior["id"] if prior else _topic_lane_id(item.get("subject"), item.get("id"))
        active_match = any(
            (_match_previous_topic(active_item, previous) or {}).get("id") == lane_id
            or _topic_lane_id(active_item.get("subject"), active_item.get("id")) == lane_id
            for active_item in (proposals.get("active_threads") or [])
        )
        nonactive_match = any(
            (_match_previous_topic(nonactive_item, previous) or {}).get("id") == lane_id
            or _topic_lane_id(nonactive_item.get("subject"), nonactive_item.get("id")) == lane_id
            for field_name in ("parked_threads", "resolved_threads")
            for nonactive_item in (proposals.get(field_name) or [])
        )
        # Referencing or updating a parked lane is not a resurface. A resurface
        # means the lane actually returns to active attention.
        if nonactive_match and not active_match:
            continue
        resurfaced_by_id[lane_id] = item
        if not active_match:
            active_item = dict(prior or item)
            active_item.update({
                "id": lane_id,
                "subject": item.get("subject") or (prior or {}).get("subject"),
                "status": "active",
                "last_turn": turn_number,
            })
            proposals.setdefault("active_threads", []).append(active_item)

    mentioned: set[str] = set()
    active_ids: set[str] = set()

    def admit(item: dict[str, Any], status: str) -> dict[str, Any]:
        prior = _match_previous_topic(item, previous)
        normalized = _normalize_topic_registry_record(item, default_status=status, turn_number=turn_number)
        if prior:
            normalized["id"] = prior["id"]
            normalized["origin_turn"] = prior.get("origin_turn", normalized["origin_turn"])
            normalized["resurface_count"] = prior.get("resurface_count", 0)
            if not item.get("summary"):
                normalized["summary"] = prior.get("summary") or normalized["summary"]
            normalized["source_turn_ids"] = list(prior.get("source_turn_ids") or [])
        lane_id = normalized["id"]
        prior_status = str((prior or {}).get("status") or "")
        resurface_proposal = resurfaced_by_id.get(lane_id) or {}
        if not prior and resurface_proposal:
            prior_turn = _topic_turn_number(resurface_proposal.get("prior_turn"), default=turn_number)
            normalized["origin_turn"] = min(normalized["origin_turn"], prior_turn)
            if prior_turn not in normalized["source_turn_ids"]:
                normalized["source_turn_ids"].append(prior_turn)
        normalized["status"] = status
        if status == "active":
            normalized["last_turn"] = turn_number
            if turn_number not in normalized["source_turn_ids"]:
                normalized["source_turn_ids"].append(turn_number)
            if prior_status == "parked" or lane_id in resurfaced_by_id:
                normalized["resurface_count"] = int(normalized.get("resurface_count") or 0) + 1
                events.append({
                    "event": "resurfaced",
                    "topic_id": lane_id,
                    "turn": turn_number,
                    "prior_turn": (prior or {}).get(
                        "last_turn",
                        _topic_turn_number(resurface_proposal.get("prior_turn"), default=normalized["origin_turn"]),
                    ),
                })
            elif not prior:
                events.append({"event": "created", "topic_id": lane_id, "turn": turn_number})
            active_ids.add(lane_id)
            normalized.pop("park_reason", None)
        elif status == "parked":
            normalized["last_turn"] = (prior or {}).get("last_turn", normalized["last_turn"])
            normalized["parked_turn"] = turn_number
            if prior_status == "active":
                events.append({"event": "parked", "topic_id": lane_id, "turn": turn_number})
        elif status in {"resolved", "superseded"}:
            normalized["resolved_turn"] = turn_number
            if prior_status != status:
                events.append({"event": status, "topic_id": lane_id, "turn": turn_number})
        normalized["source_turn_ids"] = normalized["source_turn_ids"][-24:]
        registry[lane_id] = normalized
        mentioned.add(lane_id)
        return normalized

    for item in proposals.get("active_threads") or []:
        admit(item, "active")
    for item in proposals.get("parked_threads") or []:
        admit(item, "parked")
    for item in proposals.get("resolved_threads") or []:
        status = str(item.get("status") or "resolved").lower()
        admit(item, status if status in {"resolved", "superseded"} else "resolved")

    has_topic_proposal = any(proposals.get(name) for name in (
        "topic_registry", "active_threads", "parked_threads", "resurfaced_threads", "resolved_threads",
    ))
    if has_topic_proposal and active_ids:
        for prior in previous:
            lane_id = prior["id"]
            if prior.get("status") == "active" and lane_id not in mentioned:
                parked = dict(prior)
                parked["status"] = "parked"
                parked["parked_turn"] = turn_number
                parked["park_reason"] = "Attention shifted to another conversation lane."
                registry[lane_id] = parked
                events.append({"event": "parked", "topic_id": lane_id, "turn": turn_number})

    if not registry:
        subject = _fallback_topic_subject(user_message)
        lane_id = _topic_lane_id(subject)
        registry[lane_id] = {
            "id": lane_id,
            "subject": subject,
            "status": "active",
            "origin_turn": turn_number,
            "last_turn": turn_number,
            "importance": "medium",
            "summary": subject,
            "source_turn_ids": [turn_number],
            "resurface_count": 0,
        }
        events.append({"event": "created", "topic_id": lane_id, "turn": turn_number, "source": "local_fallback"})

    ordered = sorted(
        registry.values(),
        key=lambda record: (
            {"active": 0, "parked": 1, "resolved": 2, "superseded": 3}.get(record.get("status"), 4),
            -int(record.get("last_turn") or 0),
            int(record.get("origin_turn") or 0),
        ),
    )[:64]
    active = [record for record in ordered if record.get("status") == "active"]
    parked = [record for record in ordered if record.get("status") == "parked"]
    resolved = [record for record in ordered if record.get("status") in {"resolved", "superseded"}]
    resurfaced = []
    for event in events:
        if event.get("event") != "resurfaced":
            continue
        record = registry.get(str(event.get("topic_id"))) or {}
        resurfaced.append({
            "id": record.get("id"),
            "subject": record.get("subject"),
            "prior_turn": event.get("prior_turn"),
            "reason": _compact_text(
                (resurfaced_by_id.get(str(record.get("id"))) or {}).get("reason")
                or "The current user message returned to this lane.",
                limit=260,
            ),
        })
    return {
        "topic_registry": ordered,
        "active_threads": active,
        "parked_threads": parked,
        "resolved_threads": resolved,
        "resurfaced_threads": resurfaced,
        "topic_events": events,
    }


def _hologov_control_ledger_from_plan(
    plan: Optional[GovTurnPlan],
    *,
    user_message: str = "",
    response_text: str = "",
    worker_identity: Optional[dict[str, Any]] = None,
    turn_number: int = 0,
    worker_context_receipt: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Persist admitted control state plus the completed visible turn."""
    if plan is None:
        return {}
    packet = plan.narrative_packet or {}
    fields = (
        "conversation_phase",
        "active_threads",
        "parked_threads",
        "resolved_threads",
        "resurfaced_threads",
        "topic_registry",
        "topic_events",
        "worker_contributions",
        "chronological_ledger",
        "settled_decisions",
        "unresolved_questions",
        "contradictions",
        "key_anchors",
        "user_portrait",
        "episode_registry",
        "evidence_ledger",
        "evidence_bundle_hash",
        "worker_context_receipt",
        "context_manifest",
        "worker_assignment",
        "rolling_summary",
    )
    ledger = {field: packet.get(field) for field in fields if packet.get(field) not in (None, "", [], {})}
    if worker_context_receipt:
        ledger["worker_context_receipt"] = dict(worker_context_receipt)

    def append_unique(items: list[Any], value: Any, *, limit: int) -> list[Any]:
        merged = list(items or [])
        if value not in merged:
            merged.append(value)
        if len(merged) <= limit:
            return merged
        # Preserve the origin and the most recent state under long-run pressure.
        return merged[:4] + merged[-(limit - 4):]

    if response_text:
        identity = worker_identity or plan.worker_provider_selection or {}
        worker = "/".join(
            str(identity.get(key) or "").strip()
            for key in ("provider", "model")
            if str(identity.get(key) or "").strip()
        ) or "visible-worker"
        contribution = {
            "turn": int(turn_number or 0),
            "worker": worker,
            "contribution": _compact_text(response_text, limit=900),
            "status": "standing",
        }
        ledger["worker_contributions"] = append_unique(
            list(ledger.get("worker_contributions") or []),
            contribution,
            limit=48,
        )
        chronology = list(ledger.get("chronological_ledger") or [])
        if user_message:
            chronology = append_unique(
                chronology,
                f"Turn {int(turn_number or 0)} user: {_compact_text(user_message, limit=700)}",
                limit=60,
            )
        chronology = append_unique(
            chronology,
            f"Turn {int(turn_number or 0)} {worker}: {_compact_text(response_text, limit=900)}",
            limit=60,
        )
        ledger["chronological_ledger"] = chronology
    return ledger


def _memory_updates_from_hologov_plan(
    plan: Optional[GovTurnPlan],
    *,
    user_message: str,
) -> dict[str, str]:
    """Admit only HoloGov memory proposals grounded in exact current-user evidence."""
    if plan is None:
        return {}
    proposals = (plan.narrative_packet or {}).get("memory_admission_proposals") or []
    if not isinstance(proposals, list):
        return {}
    normalized_user = " ".join(str(user_message or "").casefold().split())
    candidates: dict[str, str] = {}
    for record in proposals[:3]:
        if not isinstance(record, dict):
            continue
        evidence = _compact_text(record.get("evidence"), limit=240)
        normalized_evidence = " ".join(evidence.casefold().split())
        if not normalized_evidence or normalized_evidence not in normalized_user:
            continue
        key = _re.sub(r"[^a-z0-9_]+", "_", str(record.get("key") or "").strip().lower())[:60].strip("_")
        value = _compact_text(record.get("value"), limit=500)
        if not key or not value:
            continue
        if not value.startswith("[FACT]"):
            value = f"[FACT] {value}"
        candidates[key] = value
    admission = admit_advisor_memory_updates(candidates)
    return dict(admission.value or {}) if admission.admitted else {}


_MEMORY_FORGET_RE = _re.compile(r"(?i)\b(?:forget|delete|remove|revoke|do not remember|don't remember)\b")
_MEMORY_CORRECTION_RE = _re.compile(r"(?i)\b(?:correction|actually|that(?:'s| is) wrong|no longer true)\b")
_MEMORY_COMMITMENT_RE = _re.compile(r"(?i)\b(?:i commit|i will|we commit|promise to)\b")
_MEMORY_DECISION_RE = _re.compile(r"(?i)\b(?:i decided|we decided|the decision is|final decision)\b")


def _memory_event_kind(user_message: str) -> MemoryEventKind:
    if _MEMORY_FORGET_RE.search(user_message or ""):
        return MemoryEventKind.FORGET_REQUEST
    if _MEMORY_CORRECTION_RE.search(user_message or ""):
        return MemoryEventKind.CORRECTION
    if _MEMORY_COMMITMENT_RE.search(user_message or ""):
        return MemoryEventKind.COMMITMENT
    if _MEMORY_DECISION_RE.search(user_message or ""):
        return MemoryEventKind.MAJOR_DECISION
    return MemoryEventKind.NORMAL


def _memory_steward_proposals(
    plan: Optional[GovTurnPlan],
    *,
    user_message: str,
    message_id: str,
    user_sequence: int,
) -> tuple[MemoryProposal, ...]:
    provenance = MemoryProvenance(
        message_ids=(message_id,),
        sequence_numbers=(user_sequence,),
        source="user",
        excerpt_hash=stable_hash(user_message),
    )
    proposals: list[MemoryProposal] = []
    updates = _memory_updates_from_hologov_plan(plan, user_message=user_message)
    for key, value in updates.items():
        proposals.append(MemoryProposal(
            proposal_id=f"memory:{stable_hash({'key': key, 'value': value})[:24]}",
            kind=MemoryProposalKind.FACT,
            subject=key,
            value=value,
            provenance=provenance,
            confidence=0.95,
        ))

    raw = (plan.narrative_packet or {}).get("memory_admission_proposals") if plan else []
    for record in raw if isinstance(raw, list) else []:
        if not isinstance(record, dict):
            continue
        operation = str(record.get("operation") or "").lower()
        evidence = _compact_text(record.get("evidence"), limit=240)
        target = _compact_text(record.get("target_memory_id") or record.get("target_key"), limit=160)
        if not evidence or evidence.casefold() not in user_message.casefold() or not target:
            continue
        if operation in {"correct", "correction", "supersede", "replace"}:
            value = _compact_text(record.get("value"), limit=500)
            key = _compact_text(record.get("key") or target, limit=120)
            if not value:
                continue
            proposals.append(MemoryProposal(
                proposal_id=f"supersession:{stable_hash({'target': target, 'value': value, 'evidence': evidence})[:24]}",
                kind=MemoryProposalKind.SUPERSESSION,
                subject=key,
                value=value if value.startswith("[FACT]") else f"[FACT] {value}",
                provenance=provenance,
                confidence=1.0,
                target_memory_id=target,
            ))
            continue
        if operation not in {"forget", "revoke", "delete"}:
            continue
        proposals.append(MemoryProposal(
            proposal_id=f"revocation:{stable_hash({'target': target, 'evidence': evidence})[:24]}",
            kind=MemoryProposalKind.REVOCATION,
            subject=_compact_text(record.get("key") or target, limit=120),
            value="user_requested_deletion",
            provenance=provenance,
            confidence=1.0,
            target_memory_id=target,
        ))
    return tuple(proposals)


def _memory_steward_enabled() -> bool:
    return _truthy_env("HOLOCHAT_MEMORY_STEWARD_ENABLED")


def _checkpoint_memory_lifecycle(
    *,
    session: ChatSession,
    brain: Any,
    capsule_id: str,
    scope_id: str,
    lifecycle_kind: MemoryLifecycleKind,
) -> dict[str, Any]:
    with _memory_steward_lock:
        state = session.memory_steward_state
        if state is None:
            return {"enabled": True, "status": "no_delta", "lifecycle": lifecycle_kind.value}
        transition = apply_lifecycle_event(
            state,
            MemoryLifecycleEvent(lifecycle_kind),
        )
        state = transition.state
        checkpoint = state.pending_checkpoint
        if checkpoint is None:
            session.memory_steward_state = state
            return {"enabled": True, "status": "no_delta", "lifecycle": lifecycle_kind.value}
        if session.memory_steward_persistence_blocked:
            session.memory_steward_state = state
            return {
                "enabled": True,
                "status": "blocked_unresolved_urgent_memory",
                "lifecycle": lifecycle_kind.value,
                "checkpoint_id": checkpoint.checkpoint_id,
            }
        persister = getattr(brain, "persist_memory_checkpoint", None)
        persistence_id = persister(
            capsule_id=capsule_id,
            scope_id=scope_id,
            session_id=session.session_id,
            payload=checkpoint_payload(checkpoint),
        ) if callable(persister) else None
        if persistence_id:
            state = acknowledge_checkpoint(
                state,
                PersistenceAcknowledgement(
                    checkpoint.checkpoint_id,
                    checkpoint.idempotency_key,
                    str(persistence_id),
                    True,
                ),
            ).state
        session.memory_steward_state = state
        return {
            "enabled": True,
            "status": "persisted" if persistence_id else "persistence_failed",
            "lifecycle": lifecycle_kind.value,
            "checkpoint_id": checkpoint.checkpoint_id,
            "watermark_sequence": state.durable.watermark.sequence,
            "pending_checkpoint": state.pending_checkpoint is not None,
        }


def _advance_memory_steward(
    *,
    session: ChatSession,
    brain: Any,
    capsule_id: Optional[str],
    scope_id: Optional[str],
    user_message: str,
    response_text: str,
    gov_turn_plan: Optional[GovTurnPlan],
    context_budget: dict[str, Any],
) -> dict[str, Any]:
    if not _memory_steward_enabled() or not capsule_id or not scope_id:
        return {"enabled": False, "reason": "disabled_or_unscoped"}
    state = session.memory_steward_state or initial_memory_steward_state(
        session.session_id, "hologov-canonical"
    )
    lifecycle_triggers: tuple[Any, ...] = ()
    if not session.memory_steward_open_checked:
        opened = apply_lifecycle_event(
            state,
            MemoryLifecycleEvent(MemoryLifecycleKind.THREAD_OPEN),
        )
        state = opened.state
        lifecycle_triggers = opened.triggers
        session.memory_steward_open_checked = True
    user_sequence = len(state.rolling.transcript) + 1
    user_message_id = f"{session.session_id}:user:{session.turn_count}"
    event_kind = _memory_event_kind(user_message)
    proposals = _memory_steward_proposals(
        gov_turn_plan,
        user_message=user_message,
        message_id=user_message_id,
        user_sequence=user_sequence,
    )
    topic_events = list(((gov_turn_plan.narrative_packet or {}).get("topic_events") or []) if gov_turn_plan else [])
    active_threads = list(((gov_turn_plan.narrative_packet or {}).get("active_threads") or []) if gov_turn_plan else [])
    topic = _compact_text(active_threads[0].get("subject"), limit=120) if active_threads and isinstance(active_threads[0], dict) else None
    transition = apply_exchange(
        state,
        MemoryTurnInput(
            message_id=user_message_id,
            role="user",
            text=user_message,
            input_tokens=estimate_context_tokens(user_message),
            topic=topic,
            topic_transition=bool(topic_events),
            event_kind=event_kind,
            proposals=proposals,
        ),
        MemoryTurnInput(
            message_id=f"{session.session_id}:assistant:{session.turn_count}",
            role="assistant",
            text=response_text,
            input_tokens=estimate_context_tokens(response_text),
            topic=topic,
        ),
        CheckpointPolicy(),
    )
    state = transition.state
    auto_compact_requested = should_auto_compact(
        context_budget=context_budget,
        thread_health_level=session.thread_health_level,
        thread_health_score=session.thread_health_score,
    )
    if auto_compact_requested:
        lifecycle = apply_lifecycle_event(
            state,
            MemoryLifecycleEvent(MemoryLifecycleKind.BEFORE_AUTOCOMPACT),
        )
        state = lifecycle.state
        transition = lifecycle if lifecycle.checkpoint else transition

    checkpoint = state.pending_checkpoint
    persistence_id = None
    unresolved_urgent = (
        event_kind is MemoryEventKind.FORGET_REQUEST
        and not any(proposal.kind is MemoryProposalKind.REVOCATION for proposal in proposals)
    ) or (
        event_kind is MemoryEventKind.CORRECTION
        and not any(
            proposal.kind in {MemoryProposalKind.FACT, MemoryProposalKind.SUPERSESSION}
            for proposal in proposals
        )
    )
    if unresolved_urgent:
        session.memory_steward_persistence_blocked = True
    elif session.memory_steward_persistence_blocked:
        has_explicit_resolution = event_kind in {
            MemoryEventKind.FORGET_REQUEST,
            MemoryEventKind.CORRECTION,
        } and any(
            proposal.kind in {
                MemoryProposalKind.REVOCATION,
                MemoryProposalKind.FACT,
                MemoryProposalKind.SUPERSESSION,
            }
            for proposal in proposals
        )
        session.memory_steward_persistence_blocked = not has_explicit_resolution
    persister = getattr(brain, "persist_memory_checkpoint", None)
    if (
        checkpoint
        and callable(persister)
        and not unresolved_urgent
        and not session.memory_steward_persistence_blocked
    ):
        persistence_id = persister(
            capsule_id=capsule_id,
            scope_id=scope_id,
            session_id=session.session_id,
            payload=checkpoint_payload(checkpoint),
        )
        if persistence_id:
            state = acknowledge_checkpoint(
                state,
                PersistenceAcknowledgement(
                    checkpoint.checkpoint_id,
                    checkpoint.idempotency_key,
                    str(persistence_id),
                    True,
                ),
            ).state
            session.memory_steward_persistence_blocked = False
    session.memory_steward_state = state
    trace = {
        "enabled": True,
        "event_kind": event_kind.value,
        "triggers": [
            trigger.value
            for trigger in dict.fromkeys((*lifecycle_triggers, *transition.triggers))
        ],
        "checkpoint_id": checkpoint.checkpoint_id if checkpoint else None,
        "idempotency_key": checkpoint.idempotency_key if checkpoint else None,
        "persistence_acknowledged": bool(persistence_id),
        "watermark_sequence": state.durable.watermark.sequence,
        "pending_checkpoint": state.pending_checkpoint is not None,
        "autocompact_permitted": not auto_compact_requested or state.pending_checkpoint is None,
        "unresolved_urgent_memory_target": unresolved_urgent,
        "persistence_blocked": session.memory_steward_persistence_blocked,
    }
    session.memory_steward_trace = trace
    return trace


def _admit_hologov_narrative_proposal(
    *,
    baseline: dict[str, Any],
    proposal: dict[str, Any],
    user_message: str,
    turn_number: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Admit narrative intelligence without granting provider control authority."""
    merged = dict(baseline)
    admitted_fields: list[str] = []
    rejected_fields: list[str] = []

    def safe_text(value: Any, *, limit: int) -> str:
        text = _compact_text(value, limit=limit)
        if not text or _ACCUSATORY_HOLOGOV_RE.search(text):
            return ""
        return text

    def safe_list(value: Any, *, item_limit: int, count: int) -> list[str]:
        if not isinstance(value, list):
            return []
        items: list[str] = []
        for item in value[:count]:
            text = safe_text(item, limit=item_limit)
            if text and text not in items:
                items.append(text)
        return items

    phase = safe_text(proposal.get("conversation_phase"), limit=40).lower()
    if phase in {"opening", "exploration", "deepening", "decision", "execution", "reflection", "repair", "mixed"}:
        merged["conversation_phase"] = phase
        admitted_fields.append("conversation_phase")
    elif "conversation_phase" in proposal:
        rejected_fields.append("conversation_phase")

    def safe_records(value: Any, *, fields: tuple[str, ...], count: int) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        records: list[dict[str, Any]] = []
        for item in value[:count]:
            if not isinstance(item, dict):
                continue
            record: dict[str, Any] = {}
            for field_name in fields:
                raw = item.get(field_name)
                if isinstance(raw, list):
                    values = safe_list(raw, item_limit=500, count=12)
                    if values:
                        record[field_name] = values
                else:
                    text = safe_text(raw, limit=900)
                    if text:
                        record[field_name] = text
            if record:
                records.append(record)
        return records

    topic_proposals: dict[str, list[dict[str, Any]]] = {}
    topic_updates = safe_records(
        proposal.get("topic_updates"),
        fields=("id", "subject", "status", "origin_turn", "last_turn", "importance", "summary", "source_turn_ids", "resurface_count", "reason"),
        count=32,
    )
    for record in topic_updates:
        status = str(record.get("status") or "parked").lower()
        target = {
            "active": "active_threads",
            "parked": "parked_threads",
            "resolved": "resolved_threads",
            "superseded": "resolved_threads",
        }.get(status, "parked_threads")
        topic_proposals.setdefault(target, []).append(record)
    if topic_updates:
        admitted_fields.append("topic_updates")
    elif "topic_updates" in proposal:
        rejected_fields.append("topic_updates")
    for field_name, fields, count in (
        ("topic_registry", ("id", "subject", "status", "origin_turn", "last_turn", "importance", "summary", "source_turn_ids", "resurface_count", "reason"), 64),
        ("active_threads", ("id", "subject", "status", "origin_turn", "last_turn", "importance", "summary", "source_turn_ids", "resurface_count"), 24),
        ("parked_threads", ("id", "subject", "status", "origin_turn", "last_turn", "importance", "summary", "source_turn_ids", "resurface_count", "reason"), 48),
        ("resolved_threads", ("id", "subject", "status", "origin_turn", "last_turn", "importance", "summary", "source_turn_ids", "reason"), 48),
        ("resurfaced_threads", ("id", "subject", "prior_turn", "reason"), 24),
    ):
        records = safe_records(proposal.get(field_name), fields=fields, count=count)
        if records:
            topic_proposals[field_name] = records
            admitted_fields.append(field_name)
        elif field_name in proposal:
            rejected_fields.append(field_name)

    topic_baseline = baseline
    if topic_proposals and any(
        event.get("source") == "local_fallback" and _topic_turn_number(event.get("turn"), default=-1) == turn_number
        for event in (baseline.get("topic_events") or [])
        if isinstance(event, dict)
    ):
        topic_baseline = {
            **baseline,
            "topic_registry": [],
            "active_threads": [],
            "parked_threads": [],
            "resolved_threads": [],
            "resurfaced_threads": [],
            "topic_events": [],
        }
    topic_state = _reconcile_topic_registry(
        baseline=topic_baseline,
        proposals=topic_proposals,
        user_message=user_message,
        turn_number=turn_number,
    )
    merged.update(topic_state)
    if "topic_registry" not in admitted_fields:
        admitted_fields.append("topic_registry")

    for field_name, update_field, fields, count in (
        ("worker_contributions", "worker_contribution_updates", ("turn", "worker", "contribution", "status"), 48),
        ("contradictions", "contradiction_updates", ("claim_a", "claim_b", "status", "source_turns"), 24),
    ):
        full_records = safe_records(proposal.get(field_name), fields=fields, count=count)
        updates = safe_records(proposal.get(update_field), fields=fields, count=count)
        records = full_records or updates
        if records:
            existing = [dict(item) for item in (merged.get(field_name) or []) if isinstance(item, dict)]

            def record_key(record: dict[str, Any]) -> str:
                if field_name == "worker_contributions":
                    turn = str(record.get("turn") or "").strip().lower()
                    worker = " ".join(str(record.get("worker") or "").lower().split())
                    return f"{turn}|{worker}" if turn or worker else ""
                claims = sorted(
                    " ".join(str(record.get(name) or "").lower().split())
                    for name in ("claim_a", "claim_b")
                )
                return "|".join(claims) if any(claims) else ""

            index = {
                key: position
                for position, record in enumerate(existing)
                if (key := record_key(record))
            }

            def same_contradiction_lane(left: dict[str, Any], right: dict[str, Any]) -> bool:
                left_turns = {str(item) for item in left.get("source_turns") or []}
                right_turns = {str(item) for item in right.get("source_turns") or []}
                if not left_turns or left_turns != right_turns:
                    return False
                stop_words = {
                    "a", "an", "and", "as", "at", "be", "by", "for", "from", "in", "is",
                    "it", "of", "on", "or", "that", "the", "this", "to", "turn", "was",
                }

                def terms(record: dict[str, Any]) -> set[str]:
                    text = " ".join(str(record.get(name) or "") for name in ("claim_a", "claim_b"))
                    return {
                        token for token in _re.findall(r"[a-z0-9]+", text.lower())
                        if token not in stop_words and len(token) > 1
                    }

                left_terms = terms(left)
                right_terms = terms(right)
                if not left_terms or not right_terms:
                    return False
                return len(left_terms & right_terms) / min(len(left_terms), len(right_terms)) >= 0.35

            for record in records:
                key = record_key(record)
                position = index.get(key) if key else None
                if position is None and field_name == "contradictions":
                    position = next(
                        (
                            candidate_position
                            for candidate_position, candidate in enumerate(existing)
                            if same_contradiction_lane(candidate, record)
                        ),
                        None,
                    )
                if position is not None:
                    current = dict(existing[position])
                    if field_name == "worker_contributions":
                        note = safe_text(record.get("contribution"), limit=700)
                        if note and note != current.get("contribution"):
                            current["hologov_note"] = note
                        if record.get("status"):
                            current["status"] = record["status"]
                    else:
                        if record.get("status"):
                            current["status"] = record["status"]
                        source_turns = list(current.get("source_turns") or [])
                        for source_turn in record.get("source_turns") or []:
                            if source_turn not in source_turns:
                                source_turns.append(source_turn)
                        if source_turns:
                            current["source_turns"] = source_turns[-12:]
                        for claim_field in ("claim_a", "claim_b"):
                            if record.get(claim_field):
                                current[claim_field] = record[claim_field]
                    existing[position] = current
                    updated_key = record_key(current)
                    if updated_key:
                        index[updated_key] = position
                    continue
                existing.append(record)
                if key:
                    index[key] = len(existing) - 1
            merged[field_name] = existing[-count:]
            admitted_fields.append(field_name if full_records else update_field)
        else:
            if field_name in proposal:
                rejected_fields.append(field_name)
            if update_field in proposal:
                rejected_fields.append(update_field)

    memory_proposals = safe_records(
        proposal.get("memory_admission_proposals"),
        fields=("key", "value", "evidence"),
        count=3,
    )
    if memory_proposals:
        merged["memory_admission_proposals"] = memory_proposals
        admitted_fields.append("memory_admission_proposals")
    elif "memory_admission_proposals" in proposal:
        rejected_fields.append("memory_admission_proposals")

    assignment = proposal.get("worker_assignment")
    if isinstance(assignment, dict):
        clean_assignment: dict[str, Any] = {}
        for field_name in ("objective", "completion_signal"):
            text = safe_text(assignment.get(field_name), limit=1600)
            if text:
                clean_assignment[field_name] = text
        for field_name in ("inspect", "build_on", "challenge", "avoid"):
            values = safe_list(assignment.get(field_name), item_limit=500, count=8)
            if values:
                clean_assignment[field_name] = values
        if clean_assignment:
            merged["worker_assignment"] = clean_assignment
            admitted_fields.append("worker_assignment")
        else:
            rejected_fields.append("worker_assignment")

    manifest = proposal.get("context_manifest")
    if isinstance(manifest, dict):
        actual_manifest = dict(merged.get("context_manifest") or {})
        rationale = safe_text(manifest.get("selection_rationale"), limit=1400)
        gaps = safe_list(manifest.get("known_gaps"), item_limit=500, count=8)
        if rationale:
            actual_manifest["hologov_selection_rationale"] = rationale
        if gaps:
            actual_manifest["known_gaps"] = gaps
        if rationale or gaps:
            merged["context_manifest"] = actual_manifest
            admitted_fields.append("context_manifest")

    for field_name, limit in {
        "current_state_of_affairs": 2400,
        "rolling_summary": 10000,
        "narrative_arc": 6000,
        "active_tension": 1800,
    }.items():
        value = safe_text(proposal.get(field_name), limit=limit)
        if value:
            if field_name == "rolling_summary":
                value = _merge_hologov_rolling_summary(merged, value, limit=limit)
            merged[field_name] = value
            admitted_fields.append(field_name)
        elif field_name in proposal:
            rejected_fields.append(field_name)

    for field_name, (item_limit, count) in {
        "user_portrait": (900, 24),
        "settled_decisions": (700, 24),
        "unresolved_questions": (700, 24),
        "key_anchors": (500, 16),
        "confidence_notes": (500, 12),
        "memory_retrieval_requests": (500, 8),
    }.items():
        values = safe_list(proposal.get(field_name), item_limit=item_limit, count=count)
        if values:
            if field_name == "user_portrait":
                existing = [str(item) for item in merged.get(field_name) or []]
                merged[field_name] = (existing + [item for item in values if item not in existing])[-24:]
            else:
                merged[field_name] = values
            admitted_fields.append(field_name)
        elif field_name in proposal:
            rejected_fields.append(field_name)

    for update_field, field_name, item_limit, update_count, total_count in (
        ("user_portrait_updates", "user_portrait", 900, 6, 24),
        ("chronological_ledger_append", "chronological_ledger", 800, 1, 60),
        ("settled_decision_additions", "settled_decisions", 700, 6, 24),
        ("unresolved_question_additions", "unresolved_questions", 700, 6, 24),
        ("key_anchor_additions", "key_anchors", 500, 6, 16),
    ):
        candidate_count = update_count + 3 if field_name == "chronological_ledger" else update_count
        values = safe_list(proposal.get(update_field), item_limit=item_limit, count=candidate_count)
        if field_name == "chronological_ledger":
            current_turn_prefix = _re.compile(rf"^\s*turn\s+{int(turn_number)}\b", _re.IGNORECASE)
            values = [value for value in values if not current_turn_prefix.search(value)][:update_count]
        if values:
            existing = [str(item) for item in merged.get(field_name) or []]
            combined = existing + [item for item in values if item not in existing]
            if field_name == "chronological_ledger" and len(combined) > total_count:
                combined = combined[:4] + combined[-(total_count - 4):]
            else:
                combined = combined[-total_count:]
            merged[field_name] = combined
            admitted_fields.append(update_field)
        elif update_field in proposal:
            rejected_fields.append(update_field)

    resolved_questions = safe_list(proposal.get("resolved_questions"), item_limit=700, count=24)
    if resolved_questions:
        existing = [str(item) for item in merged.get("unresolved_questions") or []]
        resolved_normalized = {" ".join(item.lower().split()) for item in resolved_questions}
        merged["unresolved_questions"] = [
            item for item in existing
            if " ".join(item.lower().split()) not in resolved_normalized
        ]
        admitted_fields.append("resolved_questions")
    elif "resolved_questions" in proposal:
        rejected_fields.append("resolved_questions")

    for field_name, update_field in (
        ("preserve", "preserve_additions"),
        ("reject", "reject_additions"),
    ):
        values = safe_list(proposal.get(field_name), item_limit=700, count=20)
        updates = safe_list(proposal.get(update_field), item_limit=700, count=20)
        existing = [str(item) for item in merged.get(field_name) or []]
        if values:
            merged[field_name] = (existing + [item for item in values if item not in existing])[:28]
            admitted_fields.append(field_name)
        elif updates:
            merged[field_name] = (existing + [item for item in updates if item not in existing])[:28]
            admitted_fields.append(update_field)
        elif field_name in proposal:
            rejected_fields.append(field_name)
        elif update_field in proposal:
            rejected_fields.append(update_field)

    directive = safe_text(proposal.get("next_worker_directive"), limit=5000)
    directive_admission = (
        admit_advisor_prompt_directive(directive, user_message=user_message)
        if directive
        else None
    )
    if directive_admission and directive_admission.admitted:
        merged["next_worker_directive"] = directive_admission.value
        admitted_fields.append("next_worker_directive")
    elif "next_worker_directive" in proposal:
        rejected_fields.append("next_worker_directive")

    for forbidden in ("proposed_answer", "suggested_response", "user_facing_answer", "final_answer"):
        if forbidden in proposal:
            rejected_fields.append(forbidden)

    merged["packet_source"] = "hologov_control_compilation_v3"
    return merged, {
        "admitted": True,
        "admitted_fields": admitted_fields,
        "rejected_fields": rejected_fields,
        "topic_events": list(topic_state.get("topic_events") or []),
        "provider_authority": "conversation_control_proposal_only",
    }


def _gov_narrative_packet(
    *,
    session: ChatSession,
    capsule_context: dict,
    life_context: list,
    last_session: Optional[dict],
    holobrain_injection_plan: HoloBrainInjectionPlan,
    turn_policy: Any,
    user_message: str,
    search_results: Optional[str],
) -> dict[str, Any]:
    provider_history = _bounded_adapter_history(session.history, query_text=user_message)
    history_meta = _provider_history_metadata(
        provider_history,
        total_history_messages=len(session.history),
        raw_history=session.history,
    )
    omitted = _safe_positive_int(history_meta.get("omitted_history_messages"))
    state = session.holochat_state
    arc = session.gov_arc_state
    episodes = [dict(item) for item in (session.retrieved_episodes or []) if isinstance(item, dict)][:8]
    evidence_bundle = dict(session.web_evidence_bundle or {})
    evidence_sources = [
        {
            key: item.get(key)
            for key in ("source_id", "source_key", "title", "url", "domain", "published_at", "content_hash")
            if item.get(key) is not None
        }
        for item in evidence_bundle.get("sources") or []
        if isinstance(item, dict)
    ][:12]
    previous_control = dict(getattr(state, "hologov_control_ledger", {}) or {})
    topic_state = _reconcile_topic_registry(
        baseline=previous_control,
        proposals={},
        user_message=user_message,
        turn_number=session.turn_count,
    )
    preserve = [
        "HoloGov is the continuous conversation accountant and controller; workers are transient and produce the insight.",
        "Treat the ordered raw conversation and prior worker outputs as primary evidence, not disposable noise.",
        "Preserve prior worker gains so the next DNA worker can confirm, challenge, or extend them.",
        "Preserve the user's agency and dignity; do not make the answer about winning compliance.",
        "Preserve truthful warmth: reality first, never cruelty, never fake certainty.",
        "Use the control ledger to navigate gaps when real context pressure requires omission.",
    ]
    if state and state.rolling_summary:
        preserve.append("Carry forward the rolling summary as an iterative control spine, never as a replacement for the ordered conversation.")
    if capsule_context or life_context:
        preserve.append("Use scoped HoloBrain context as secondary grounding for explicit preferences and durable boundaries.")
    if search_results:
        preserve.append("Ground web-derived claims in the admitted evidence ledger and cite only supplied [S#] source IDs.")
    if episodes:
        preserve.append("Use selected episodes as provenance-bearing context; do not treat retrieval rank as truth or expose private retrieval mechanics.")
    reject = [
        "Reject scolding, gotcha framing, shame, sterile disclaimers, and bureaucratic distance.",
        "Reject false memory, hidden-profile theatrics, and claims of knowing private context beyond admitted memory.",
        "Reject overconfident medical, financial, legal, or dependency promises.",
    ]
    directive_parts = [
        "Inspect the ordered conversation and prior worker contributions before answering.",
        "Use this packet as navigation and control structure, never as a replacement for primary conversational evidence.",
        "Build on what prior DNA workers established, challenge weak claims where useful, and add a genuinely new layer.",
        "Answer the live request directly; HoloGov organizes and the worker performs the reasoning.",
    ]
    if omitted:
        directive_parts.append(
            f"{omitted} raw history message(s) are omitted under context pressure; origins, relevant older evidence, and recent turns remain selected."
        )
    if getattr(turn_policy, "tier", "") in {"high", "max"}:
        directive_parts.append("This is high-stakes: prefer precise limits and practical next steps over confidence theater.")
    memory_stewardship = _holobrain_stewardship_plan(
        capsule_context=capsule_context,
        life_context=life_context,
        last_session=last_session,
        holochat_state=state,
    )
    holobrain_projection = _holobrain_worker_projection(
        capsule_context=capsule_context,
        life_context=life_context,
        last_session=last_session,
        injection_plan=holobrain_injection_plan,
    )
    rolling_summary = _compact_text((state.rolling_summary if state else None), limit=16000)
    return {
        "gov_role": "HoloGov maintains conversation structure, provenance, topic lanes, state correctness, context allocation, and worker handoff. HoloGov does not create the answer or the insight.",
        "worker_context_contract": "The worker is a fresh DNA speaker each turn. The ordered raw conversation is primary evidence; this control ledger makes that evidence navigable and preserves recursive gains.",
        "holobrain_operator": "HoloGov is the only runtime role authorized to enter, query, organize, update, prune, archive, or manage HoloBrain. HoloGov and HoloBrain operate as the continuity team.",
        "holobrain_scope": "Workers do not access HoloBrain directly. HoloGov provides the richest lawful admitted HoloBrain projection; the worker must not invent or expose unavailable private memory.",
        "memory_stewardship": memory_stewardship,
        "holobrain_projection": holobrain_projection,
        "packet_source": "deterministic_continuity_fallback_v1",
        "control_health": {
            "status": "degraded",
            "reason": "provider_control_compilation_not_yet_admitted",
        },
        "conversation_phase": previous_control.get("conversation_phase") or "opening",
        "topic_registry": topic_state["topic_registry"],
        "active_threads": topic_state["active_threads"],
        "parked_threads": topic_state["parked_threads"],
        "resolved_threads": topic_state["resolved_threads"],
        "resurfaced_threads": topic_state["resurfaced_threads"],
        "topic_events": topic_state["topic_events"],
        "worker_contributions": previous_control.get("worker_contributions") or [],
        "episode_registry": episodes,
        "evidence_ledger": evidence_sources,
        "evidence_bundle_hash": evidence_bundle.get("bundle_hash"),
        "memory_admission_proposals": [],
        "user_portrait": (_capsule_portrait_lines(capsule_context) + _life_context_portrait_lines(life_context))[:12],
        "current_state_of_affairs": _compact_text(user_message, limit=360),
        "chronological_ledger": list(previous_control.get("chronological_ledger") or [])[:60],
        "rolling_summary": rolling_summary,
        "narrative_arc": _compact_text(rolling_summary or arc.last_gov_read, limit=2400),
        "active_tension": _compact_text(arc.current_tension or arc.topic_shift_reason or "", limit=260),
        "settled_decisions": list(getattr(state, "settled_decisions", []) or [])[:16],
        "unresolved_questions": list(arc.unresolved_questions or [])[:12],
        "contradictions": previous_control.get("contradictions") or [],
        "key_anchors": list(previous_control.get("key_anchors") or [])[:24],
        "confidence_notes": list(previous_control.get("confidence_notes") or [])[:20],
        "memory_retrieval_requests": [],
        "preserve": preserve,
        "reject": reject,
        "context_manifest": {
            "selection_mode": history_meta.get("selection_mode"),
            "ordered_history_preserved": history_meta.get("ordered_history_preserved"),
            "raw_history_messages": history_meta.get("raw_history_messages"),
            "selected_history_messages": history_meta.get("bounded_history_messages"),
            "omitted_history_messages": omitted,
            "selected_episode_ids": [item.get("episode_id") for item in episodes if item.get("episode_id")],
            "episode_retrieval": dict(session.episode_retrieval_trace or {}),
            "evidence_source_ids": [item.get("source_id") for item in evidence_sources if item.get("source_id")],
            "episode_token_estimate": sum(int(item.get("token_estimate") or 0) for item in episodes),
            "evidence_token_estimate": estimate_context_tokens(render_web_evidence(evidence_bundle)),
            "selection_rationale": "Full ordered history while it fits; otherwise preserve origins, relevant older evidence, explicit decisions/corrections, and recent turns.",
        },
        "worker_assignment": {
            "objective": _compact_text(user_message, limit=700),
            "inspect": ["ordered conversation", "selected episodes", "admitted evidence sources", "prior worker contributions", "settled decisions", "open questions"],
            "build_on": ["standing prior insights and evidence"],
            "challenge": ["unsupported or superseded claims"],
            "avoid": ["generic restart", "repeating settled ground", "inventing missing context"],
            "completion_signal": "The response advances the live conversation with one coherent new layer while preserving continuity.",
        },
        "next_worker_directive": " ".join(directive_parts),
        "context_pressure": {
            "raw_history_messages": history_meta.get("raw_history_messages"),
            "bounded_history_messages": history_meta.get("bounded_history_messages"),
            "omitted_history_messages": omitted,
            "holobrain_injection_mode": holobrain_injection_plan.mode.value,
            "holobrain_injection_reason": holobrain_injection_plan.reason,
        },
    }


def _build_worker_gov_turn_plan(
    *,
    session: ChatSession,
    capsule_id: Optional[str],
    adapter: Any,
    gov_advisor: Any,
    turn_policy: Any,
    temperature: float,
    tenor: Optional[str],
    tenor_admission: Any,
    thought_admission: Any,
    user_message: str,
    search_query: Optional[str],
    search_results: Optional[str],
    web_trace: dict[str, Any],
    capsule_context: dict,
    life_context: list,
    last_session: Optional[dict],
    incognito: bool,
    active_handoff_transition: Optional[dict[str, Any]],
    holochat_state_block: Optional[str],
    holobrain_injection_plan: HoloBrainInjectionPlan,
    frontier_assist: dict[str, Any],
    worker_fallback_active: bool = False,
    control_compilation_cache: Optional[dict[str, Any]] = None,
) -> GovTurnPlan:
    selected, dropped, drop_reasons, memory_admissions, memory_rejections = _govturnplan_context_selection(
        incognito=incognito,
        capsule_context=capsule_context,
        life_context=life_context,
        last_session=last_session,
        handoff_transition=active_handoff_transition,
        holochat_state_block=holochat_state_block,
        holobrain_injection_plan=holobrain_injection_plan,
        search_results=search_results,
        retrieved_episodes=list(session.retrieved_episodes or []),
        evidence_bundle=dict(session.web_evidence_bundle or {}),
    )
    contradiction_repairs: list[dict[str, Any]] = []
    if tenor_admission is not None and getattr(tenor_admission, "repaired", False):
        contradiction_repairs.append(
            {
                "surface": "advisor_prompt_directive",
                "reason": getattr(tenor_admission, "reason", "repaired"),
            }
        )
    if thought_admission is not None and not getattr(thought_admission, "admitted", False):
        contradiction_repairs.append(
            {
                "surface": "surface_thought",
                "reason": getattr(thought_admission, "reason", "not_admitted"),
            }
        )
    baton = _worker_continuity_baton(
        session=session,
        tenor=tenor,
        capsule_context=capsule_context,
        life_context=life_context,
        holobrain_injection_plan=holobrain_injection_plan,
        turn_policy=turn_policy,
        user_message=user_message,
    )
    narrative_packet = _gov_narrative_packet(
        session=session,
        capsule_context=capsule_context,
        life_context=life_context,
        last_session=last_session,
        holobrain_injection_plan=holobrain_injection_plan,
        turn_policy=turn_policy,
        user_message=user_message,
        search_results=search_results,
    )
    control_compilation_telemetry: dict[str, Any] = {
        "mode": "local_fallback",
        "reason": "advisor_does_not_support_control_compilation",
    }
    synthesize = getattr(gov_advisor, "compile_holochat_control_packet", None)
    if not callable(synthesize):
        synthesize = getattr(gov_advisor, "synthesize_holochat_turn_packet", None)
    if callable(synthesize) and _hologov_control_compilation_enabled():
        provider_history = _bounded_adapter_history(session.history, query_text=user_message)
        history_metadata = _provider_history_metadata(
            provider_history,
            total_history_messages=len(session.history),
            raw_history=session.history,
        )
        current_worker = _adapter_identity_dict(adapter)
        synthesis = None
        compilation_error_type = None
        failed_call_telemetry: dict[str, Any] = {}
        reused_for_failover = bool(control_compilation_cache and control_compilation_cache.get("attempted"))
        if reused_for_failover:
            synthesis = control_compilation_cache.get("synthesis")
            compilation_error_type = control_compilation_cache.get("error_type")
            failed_call_telemetry = dict(control_compilation_cache.get("failed_call_telemetry") or {})
        else:
            try:
                synthesis_kwargs = {
                    "ordered_history": provider_history,
                    "current_user_message": user_message,
                    "previous_state": _hologov_state_payload(session.holochat_state),
                    "capsule_context": capsule_context,
                    "life_context": life_context,
                    "latest_consolidation": last_session,
                    "worker_identity": current_worker,
                    "turn_policy": {
                        "tier": getattr(turn_policy, "tier", "standard"),
                        "reasons": list(getattr(turn_policy, "reasons", ()) or ()),
                        "fallback_allowed": bool(getattr(turn_policy, "fallback_allowed", False)),
                    },
                    "history_metadata": history_metadata,
                    "turn_number": session.turn_count,
                    "retrieved_episodes": list(session.retrieved_episodes or []),
                    "web_evidence": dict(session.web_evidence_bundle or {}),
                }
                parameters = inspect.signature(synthesize).parameters
                if not any(param.kind == inspect.Parameter.VAR_KEYWORD for param in parameters.values()):
                    synthesis_kwargs = {
                        key: value for key, value in synthesis_kwargs.items()
                        if key in parameters
                    }
                synthesis = synthesize(**synthesis_kwargs)
                if control_compilation_cache is not None:
                    control_compilation_cache.update({
                        "attempted": True,
                        "synthesis": synthesis,
                        "error_type": None,
                        "failed_call_telemetry": {},
                        "compiled_for_worker": current_worker,
                    })
            except Exception as exc:
                logger.warning("HoloGov control compilation failed: %s", exc)
                telemetry_getter = getattr(gov_advisor, "get_last_holochat_control_telemetry", None)
                failed_call_telemetry = telemetry_getter() if callable(telemetry_getter) else {}
                compilation_error_type = exc.__class__.__name__
                if control_compilation_cache is not None:
                    control_compilation_cache.update({
                        "attempted": True,
                        "synthesis": None,
                        "error_type": compilation_error_type,
                        "failed_call_telemetry": failed_call_telemetry,
                        "compiled_for_worker": current_worker,
                    })

        if compilation_error_type:
            control_compilation_telemetry = {
                **failed_call_telemetry,
                "mode": "local_fallback",
                "reason": "control_compilation_error",
                "error_type": compilation_error_type,
                "reused_for_worker_failover": reused_for_failover,
                "compiled_for_worker": (control_compilation_cache or {}).get("compiled_for_worker"),
                "applied_to_worker": current_worker,
            }
        else:
            proposal = synthesis.get("proposal") if isinstance(synthesis, dict) else None
            if isinstance(proposal, dict):
                narrative_packet, admission = _admit_hologov_narrative_proposal(
                    baseline=narrative_packet,
                    proposal=proposal,
                    user_message=user_message,
                    turn_number=session.turn_count,
                )
                control_compilation_telemetry = {
                    **(synthesis.get("telemetry") or {}),
                    "admission": admission,
                    "reused_for_worker_failover": reused_for_failover,
                    "compiled_for_worker": (control_compilation_cache or {}).get("compiled_for_worker") or current_worker,
                    "applied_to_worker": current_worker,
                }
            else:
                control_compilation_telemetry = {
                    **((synthesis.get("telemetry") or {}) if isinstance(synthesis, dict) else {}),
                    "mode": "local_fallback",
                    "reason": "control_compilation_missing_proposal",
                    "reused_for_worker_failover": reused_for_failover,
                    "compiled_for_worker": (control_compilation_cache or {}).get("compiled_for_worker") or current_worker,
                    "applied_to_worker": current_worker,
                }
    elif callable(synthesize):
        control_compilation_telemetry = {
            "mode": "disabled_for_control_run",
            "reason": "HOLOCHAT_GOV_CONTROL_PACKET_ENABLED=false",
        }
    if control_compilation_telemetry.get("mode") == "hologov_control_compilation_v3":
        narrative_packet["control_health"] = {
            "status": "healthy",
            "reason": "bounded_hologov_delta_admitted",
        }
    else:
        narrative_packet["control_health"] = {
            "status": "degraded",
            "reason": control_compilation_telemetry.get("reason") or "control_compilation_unavailable",
        }
    worker_history = _bounded_adapter_history(session.history, query_text=user_message)
    worker_history_metadata = _provider_history_metadata(
        worker_history,
        total_history_messages=len(session.history),
        raw_history=session.history,
    )
    context_receipt = build_worker_context_receipt(
        history_metadata=worker_history_metadata,
        selected_history=worker_history,
        episodes=list(session.retrieved_episodes or []),
        evidence_bundle=dict(session.web_evidence_bundle or {}),
        gov_packet=project_gov_narrative_packet_for_worker(narrative_packet),
    )
    narrative_packet["worker_context_receipt"] = context_receipt
    narrative_packet.setdefault("context_manifest", {})["worker_context_receipt_hash"] = context_receipt["receipt_hash"]
    deep_directive = _compact_text(narrative_packet.get("next_worker_directive"), limit=5000)
    if deep_directive and deep_directive not in baton:
        baton = baton + "\n\nHOLOGOV CONTROL ASSIGNMENT:\n" + deep_directive
    return build_gov_turn_plan(
        turn_id=f"{session.session_id}:{session.turn_count}",
        user_id=stable_hash(capsule_id) if capsule_id and not incognito else None,
        route="Visible Worker -> HoloGov State Update -> GovTurnPlan -> Visible Worker",
        visible_worker_role="holochat_visible_worker",
        worker_provider_selection=_adapter_identity_dict(adapter),
        advisor_provider_selection={
            **_adapter_identity_dict(gov_advisor),
            "role": (
                "hologov_control_proposal_source"
                if _adapter_provider_name(gov_advisor) == "minimax"
                else "gov_advisor_proposal_source"
            ),
            "visible_worker_eligible": False,
            "authority": "proposal_only",
        },
        turn_policy=turn_policy,
        selected_context_ids=selected,
        dropped_context_ids=dropped,
        context_drop_reasons=drop_reasons,
        memory_admissions=memory_admissions,
        memory_rejections=memory_rejections,
        artifact_refs=[],
        pinned_artifacts=[],
        tool_authorization={
            "web_search": bool(search_query or search_results),
            "authorized_tools": [tool.value for tool in _required_tools_for_turn(search_query, search_results)],
            "authorization_source": "deterministic_gov_kernel",
            "holobrain_episode_retrieval": dict(session.episode_retrieval_trace or {}),
        },
        search_authorization={
            "authorized": bool(search_query),
            "query_hash": stable_hash(search_query) if search_query else None,
            "results_present": bool(search_results),
            "decision": web_trace.get("status"),
            "source": web_trace.get("source"),
            "evidence_source_ids": list(web_trace.get("evidence_source_ids") or []),
            "evidence_bundle_hash": web_trace.get("evidence_bundle_hash"),
        },
        voice_tone_constraints=[
            "No scolding, shame, gotcha, cold, curt, sterile, hostile, or prosecutorial posture.",
            "Relationship repair beats cleverness, pressure, or hard-truth performance.",
            "HoloBrain memory grounds continuity; it must never become accusatory theory about the user.",
            "Only HoloGov may operate HoloBrain; visible workers receive admitted HoloBrain projections through GovTurnPlan.",
            "Never expose internal state, GovTurnPlan fields, control schemas, or raw JSON unless the user explicitly requested JSON in their own message.",
        ],
        persona_identity_constraints=[
            "HoloChat is universal for every active user.",
            "HoloGov operates; visible workers speak.",
            "Provider output is subordinate work product until admitted.",
        ],
        contradiction_repairs=contradiction_repairs,
        state_corrections=[],
        fallback_eligibility={
            "worker_fallback_allowed": True,
            "worker_fallback_condition": "primary_provider_failure_only",
            "worker_fallback_active": bool(worker_fallback_active),
            "advisor_fallback_allowed": bool(
                getattr(gov_advisor, "get_gov_fallback_trace", lambda: {})().get("active")
            ),
            "minimax_normal_routing_allowed": False,
        },
        release_constraints=[
            "Deterministic visible release guard must run before user-visible output.",
            "Streaming chunks are buffered until release admission.",
            "Surface thought metadata must be admitted before UI exposure.",
            "Internal control-packet formatting must never leak into visible worker prose.",
        ],
        worker_prompt_baton=baton,
        narrative_packet=narrative_packet,
        telemetry={
            "temperature": round(float(temperature), 3),
            "frontier_assist_triggered": bool((frontier_assist or {}).get("triggered")),
            "incognito": bool(incognito),
            "worker_fallback_active": bool(worker_fallback_active),
            "hologov_control_compilation": control_compilation_telemetry,
        },
    )


def _record_worker_context_delivery(
    *,
    session: ChatSession,
    plan: GovTurnPlan,
    system_prompt: str,
    history: list[dict[str, str]],
    user_prompt: str,
) -> dict[str, Any]:
    packet = project_gov_narrative_packet_for_worker(plan.narrative_packet)
    receipt = build_worker_context_receipt(
        history_metadata=_provider_history_metadata(
            history,
            total_history_messages=len(session.history),
            raw_history=session.history,
        ),
        selected_history=history,
        episodes=list(session.retrieved_episodes or []),
        evidence_bundle=dict(session.web_evidence_bundle or {}),
        gov_packet=packet,
        actual_system_prompt=system_prompt,
        actual_user_prompt=user_prompt,
    )
    session.worker_context_receipt = receipt
    return receipt


def _adapter_provider_name(adapter: Any) -> str:
    return str(getattr(adapter, "provider", "") or "").strip().lower()


def _is_fallback_analyst_adapter(adapter: Any) -> bool:
    return _adapter_provider_name(adapter) in FALLBACK_HOLOCHAT_MODEL_PROVIDERS


def _rotation_analyst_adapters(adapters: list[Any]) -> list[Any]:
    adapters = _filter_holochat_enabled_adapters(adapters)
    primary = [adapter for adapter in adapters if not _is_fallback_analyst_adapter(adapter)]
    return primary or list(adapters)


def _ordered_adapter_pool(pool: list[Any], selected: Any) -> list[Any]:
    if not pool:
        return []
    try:
        selected_index = next(
            idx for idx, adapter in enumerate(pool) if adapter is selected
        )
    except StopIteration:
        return list(pool)
    return pool[selected_index:] + pool[:selected_index]


def _select_analyst_adapter(session: ChatSession, adapters: list[Any]) -> Any:
    if not adapters:
        raise RuntimeError("HoloChat runtime has no analyst adapters.")
    rotation_pool = _rotation_analyst_adapters(adapters)
    if not rotation_pool:
        raise RuntimeError("HoloChat runtime has no analyst adapters.")
    adapter = rotation_pool[session.rotation_index % len(rotation_pool)]
    session.rotation_index += 1
    return adapter


def _adapter_candidate_order(adapters: list[Any], selected: Any) -> list[Any]:
    adapters = _filter_holochat_enabled_adapters(adapters)
    if not adapters:
        return []
    primary = [adapter for adapter in adapters if not _is_fallback_analyst_adapter(adapter)]
    fallback = [adapter for adapter in adapters if _is_fallback_analyst_adapter(adapter)]
    if selected in primary:
        return _ordered_adapter_pool(primary, selected) + fallback
    if selected in fallback:
        return [selected, *_ordered_adapter_pool(primary, selected), *[adapter for adapter in fallback if adapter is not selected]]
    return [selected, *primary, *fallback]


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


def _govturnplan_budget_profile(
    gov_turn_plan: Optional[GovTurnPlan],
    gov_turn_plan_block: Optional[str],
) -> dict[str, Any]:
    if gov_turn_plan is None:
        return {
            "included": False,
            "reason": "not_built",
            "govturnplan_block_token_estimate": estimate_context_tokens(gov_turn_plan_block or ""),
        }
    payload = gov_turn_plan.model_dump()
    narrative_packet = payload.get("narrative_packet") or {}
    telemetry = payload.get("telemetry") or {}
    stewardship = narrative_packet.get("memory_stewardship") or {}
    control_compilation = telemetry.get("hologov_control_compilation") or {}
    holobrain_projection = narrative_packet.get("holobrain_projection") or {}
    return {
        "included": True,
        "packet_source": narrative_packet.get("packet_source"),
        "control_health": narrative_packet.get("control_health") or {},
        "govturnplan_hash": telemetry.get("govturnplan_hash"),
        "govturnplan_block_token_estimate": estimate_context_tokens(gov_turn_plan_block or ""),
        "govturnplan_payload_token_estimate": _safe_positive_int(telemetry.get("govturnplan_payload_token_estimate")),
        "narrative_packet_token_estimate": _safe_positive_int(telemetry.get("narrative_packet_token_estimate")),
        "worker_prompt_baton_token_estimate": _safe_positive_int(telemetry.get("worker_prompt_baton_token_estimate")),
        "user_portrait_items": len(narrative_packet.get("user_portrait") or []),
        "preserve_rules": len(narrative_packet.get("preserve") or []),
        "reject_rules": len(narrative_packet.get("reject") or []),
        "chronological_ledger_items": len(narrative_packet.get("chronological_ledger") or []),
        "topic_registry_count": len(narrative_packet.get("topic_registry") or []),
        "active_thread_count": len(narrative_packet.get("active_threads") or []),
        "parked_thread_count": len(narrative_packet.get("parked_threads") or []),
        "resolved_thread_count": len(narrative_packet.get("resolved_threads") or []),
        "resurfaced_thread_count": len(narrative_packet.get("resurfaced_threads") or []),
        "topic_event_count": len(narrative_packet.get("topic_events") or []),
        "worker_contribution_count": len(narrative_packet.get("worker_contributions") or []),
        "selected_episode_count": len(narrative_packet.get("episode_registry") or []),
        "selected_episode_token_estimate": sum(
            _safe_positive_int(item.get("token_estimate"))
            for item in (narrative_packet.get("episode_registry") or [])
            if isinstance(item, dict)
        ),
        "evidence_source_count": len(narrative_packet.get("evidence_ledger") or []),
        "evidence_token_estimate": _safe_positive_int(
            (narrative_packet.get("context_manifest") or {}).get("evidence_token_estimate")
        ),
        "worker_context_receipt": dict(narrative_packet.get("worker_context_receipt") or {}),
        "contradiction_count": len(narrative_packet.get("contradictions") or []),
        "context_selection_mode": (narrative_packet.get("context_manifest") or {}).get("selection_mode"),
        "rolling_summary_token_estimate": estimate_context_tokens(narrative_packet.get("rolling_summary") or ""),
        "control_compilation": control_compilation,
        "holobrain_projection": {
            "authority": holobrain_projection.get("authority"),
            "injection_mode": holobrain_projection.get("injection_mode"),
            "source_counts": holobrain_projection.get("source_counts") or {},
        },
        "memory_stewardship": {
            "mode": stewardship.get("mode"),
            "authority": stewardship.get("authority"),
            "action_count": len(stewardship.get("actions") or []),
            "review_candidate_count": len(stewardship.get("review_candidates") or []),
            "status_counts": stewardship.get("status_counts") or {},
            "raw_library_access_for_worker": stewardship.get("raw_library_access_for_worker"),
        },
    }


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
    holochat_state_block: Optional[str] = None,
    holobrain_injection_plan: Optional[HoloBrainInjectionPlan] = None,
    gov_turn_plan_block: Optional[str] = None,
    gov_turn_plan: Optional[GovTurnPlan] = None,
) -> dict[str, Any]:
    provider_history = adapter_history if adapter_history is not None else _bounded_adapter_history(
        session.history,
        query_text=user_message,
    )
    provider_history_meta = _provider_history_metadata(
        provider_history,
        total_history_messages=len(session.history),
        raw_history=session.history,
    )
    memory_pack = _holochat_recovery_memory_pack()
    plan = holobrain_injection_plan or HoloBrainInjectionPlan(
        mode=HoloBrainInjectionMode.NONE,
        payload="",
        reason="not_evaluated",
    )
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
            "block_name": "gov_turn_plan",
            "content": gov_turn_plan_block or "",
            "included": bool(gov_turn_plan_block),
            "source_type": "deterministic_gov",
            "reason": "not_built" if not gov_turn_plan_block else None,
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
                    "block_name": "thread_handoff_seed",
                    "content": "",
                    "included": False,
                    "source_type": "system",
                    "reason": "incognito mode",
                },
                {
                    "block_name": "holochat_state_object",
                    "content": "",
                    "included": False,
                    "source_type": "system",
                    "reason": "incognito mode",
                },
                {
                    "block_name": "holochat_memory_pack",
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
                    "reason": "superseded_by_govturnplan_control_plane",
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
                "block_name": "thread_handoff_seed",
                "content": _thread_handoff_transition_block(handoff_transition),
                "included": bool(handoff_transition),
                "source_type": "system",
                "reason": "empty" if not handoff_transition else None,
            }
        )
        blocks.append(
            {
                "block_name": "holochat_state_object",
                "content": holochat_state_block or "",
                "included": bool(holochat_state_block),
                "source_type": "system",
                "reason": "empty" if not holochat_state_block else None,
            }
        )
        blocks.append(
            {
                "block_name": "holochat_memory_pack",
                "content": memory_pack,
                "included": bool(memory_pack),
                "source_type": "memory",
                "reason": "disabled" if not memory_pack else None,
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
                "content": "",
                "included": False,
                "source_type": "governor",
                "reason": "superseded_by_govturnplan_control_plane",
            }
        )

    blocks.append(
        {
            "block_name": "web_results",
            "content": (
                "\n\n"
                "[ADMITTED WEB EVIDENCE: Use only relevant sources below for web-derived claims. "
                "Cite those claims inline with the supplied [S#] identifiers and never invent a source. "
                "If the evidence is insufficient or irrelevant, say so plainly.]\n\n"
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

    if not incognito:
        # These sources are available to HoloGov, but the visible worker receives
        # only the admitted projection inside GovTurnPlan. Keep telemetry aligned
        # with the actual provider prompt instead of double-counting raw memory.
        for block in blocks:
            if block.get("block_name") in {
                "thread_health",
                "holochat_state_object",
                "holochat_memory_pack",
                "life_context",
                "latest_consolidation",
                "capsule_context",
            }:
                block["content"] = ""
                block["included"] = False
                block["reason"] = "projected_through_hologov_govturnplan"

    ledger = build_context_budget_ledger(blocks).model_dump(mode="json")
    rows_by_name = {row.get("block_name"): row for row in ledger.get("rows", [])}
    for row in ledger.get("rows", []):
        if row.get("block_name") == "holochat_state_object":
            row["injection_mode"] = plan.mode.value
            row["injection_reason"] = plan.reason
            row["state_hash"] = plan.state_hash
            row["char_count"] = plan.char_count
            row["token_estimate"] = plan.token_estimate
        if row.get("block_name") == "recent_session_history":
            row.update(provider_history_meta)
    ledger["holobrain_injection"] = {
        "mode": plan.mode.value,
        "reason": plan.reason,
        "state_hash": plan.state_hash,
        "included": bool(plan.payload),
        "char_count": plan.char_count,
        "token_estimate": plan.token_estimate,
    }
    ledger["hologov_packet"] = _govturnplan_budget_profile(gov_turn_plan, gov_turn_plan_block)
    ledger["worker_context_receipt"] = dict(
        session.worker_context_receipt
        or (
            ((gov_turn_plan.narrative_packet or {}).get("worker_context_receipt") or {})
            if gov_turn_plan is not None
            else {}
        )
    )
    ledger["history_context"] = provider_history_meta
    narrative_packet = (gov_turn_plan.narrative_packet or {}) if gov_turn_plan is not None else {}
    holobrain_projection = narrative_packet.get("holobrain_projection") or {}
    ledger["memory_context"] = {
        "memory_pack_version": HOLOCHAT_MEMORY_PACK_VERSION,
        "memory_pack_included": False,
        "life_context_entries_available": len(life_context or []),
        "capsule_context_keys_available": len(capsule_context or {}),
        "life_context_included": bool(rows_by_name.get("life_context", {}).get("included")),
        "capsule_context_included": bool(rows_by_name.get("capsule_context", {}).get("included")),
        "latest_consolidation_included": bool(rows_by_name.get("latest_consolidation", {}).get("included")),
        "life_context_token_estimate": _safe_positive_int(rows_by_name.get("life_context", {}).get("token_estimate")),
        "capsule_context_token_estimate": _safe_positive_int(rows_by_name.get("capsule_context", {}).get("token_estimate")),
        "projected_via_hologov": bool(holobrain_projection),
        "projection_injection_mode": holobrain_projection.get("injection_mode"),
        "projection_durable_items": ((holobrain_projection.get("source_counts") or {}).get("durable_items_admitted")),
        "raw_worker_holobrain_access": False,
        "dropped_memory_blocks": [
            name
            for name in ("life_context", "capsule_context", "latest_consolidation", "holochat_state_object")
            if rows_by_name.get(name) and not rows_by_name[name].get("included")
        ],
    }
    ledger["thread_health"] = {
        "score": session.thread_health_score,
        "level": session.thread_health_level,
        "status": session.thread_status,
        "metrics": _thread_health_metrics_for_context_budget(session, provider_history_meta),
        "flags": _thread_health_flags_for_context_budget(session, provider_history_meta),
        "reasons": _thread_health_reasons_for_context_budget(session, provider_history_meta),
    }
    return ledger


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
) -> Holo4DnaShadowTurn:
    required_tools = _required_tools_for_turn(search_query, search_results)
    holo_state = HoloState.from_chat_turn(
        session_id=session.session_id,
        capsule_id=capsule_id,
        turn_number=session.turn_count,
        user_message=user_message,
        thread_health_score=session.thread_health_score,
        thread_status=session.thread_status,
        thread_health_metrics=session.thread_health_metrics,
        thread_health_flags=session.thread_health_flags,
        thread_health_reasons=session.thread_health_reasons,
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
        recent_history=_bounded_adapter_history(session.history, query_text=user_message),
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


def _capsule_context_for_depth_preference(context: dict) -> dict:
    """Apply the user's onboarding depth choice before prompt injection."""
    if not context:
        return {}
    preference = str(context.get("holo_depth_preference") or "personal").strip().lower()
    if preference not in {"surface", "personal", "deep"}:
        preference = "personal"

    filtered: dict = {}
    for key, value in context.items():
        key_str = str(key)
        if key_str == "holo_seed_deep_v1" and preference != "deep":
            continue
        if key_str == "holo_seed_personal_v1" and preference == "surface":
            continue
        if key_str == "holo_depth_consent_v1":
            continue
        filtered[key] = value
    return filtered


def _extract_and_save_artifacts(
    brain, response_text: str, capsule_id: str, session_id: str, turn_number: int,
    *, scope_id: Optional[str] = None,
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
        aid = brain.save_artifact(
            capsule_id, session_id, turn_number, title, content,
            **({"scope_id": scope_id} if scope_id else {}),
        )
        if aid:
            saved.append({
                "artifact_id": aid,
                "title": title,
                "type": "html",
                "content_hash": stable_hash(content),
                "status": "available_by_id",
            })
    return saved


def _health_context(session: ChatSession) -> str:
    """
    Build the BATON_PASS snippet that HOLO_CHAT_SYSTEM_PROMPT references.
    Injected at the end of the system prompt every turn.
    """
    reasons = ", ".join(session.thread_health_reasons) or "none"
    return (
        f"BATON_PASS:\n"
        f"  THREAD_HEALTH_SCORE: {session.thread_health_score}\n"
        f"  THREAD_HEALTH_LEVEL: {session.thread_health_level}\n"
        f"  THREAD_STATUS: {session.thread_status}\n"
        f"  THREAD_HEALTH_REASONS: {reasons}\n"
        f"  USER_ALERT_RECOMMENDED: {session.user_alert}\n"
        f"  TASK_MODE: DEEP_REASONING"
    )
