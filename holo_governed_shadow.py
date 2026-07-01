"""Governed shadow loop for HoloChat.

This module ports the HoloVerify-style architecture into HoloChat as metadata
only. It never replaces the visible chat answer; it runs a bounded shadow trace
when explicitly enabled and when a turn looks hard enough to justify the spend.
"""

from __future__ import annotations

import os
import re
import time
import uuid
from dataclasses import dataclass
from typing import Any, Iterable

from holo_state import HoloState
from llm_adapters import OpenAIAdapter, OpenAICompatibleAdapter


GOVERNED_SHADOW_VERSION = "holochat_governed_shadow_v0.1"
GOVERNED_SHADOW_ENV = "HOLOCHAT_GOVERNED_SHADOW"

ROSTER = (
    {"slot": "W1", "role": "worker", "provider": "xai", "model": "grok-3-mini", "worker_role": "SOURCE_BOUNDARY_MAPPER"},
    {"slot": "G1", "role": "gov", "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "gov_role": "CONTROL_ACTUATOR"},
    {"slot": "W2", "role": "worker", "provider": "openai", "model": "gpt-5.4-mini", "worker_role": "ADVERSARIAL_SCOPE_CHALLENGER"},
    {"slot": "G2", "role": "gov", "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "gov_role": "CONTROL_ACTUATOR"},
    {"slot": "W3", "role": "worker", "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "worker_role": "FINAL_COMPILER"},
)

FORBIDDEN_MODEL_SELECTION_KEYS = (
    "selected_model",
    "worker_model",
    "model_choice",
    "provider_choice",
    "next_model",
)

SECRET_MARKERS = (
    "api_key",
    "authorization:",
    "bearer ",
    "password",
    "secret-value",
    "private key",
)

SOURCE_REF_RE = re.compile(r"\b(?:SRC-[A-Z0-9_-]+|doc_id\s*:|\[source\s*:)", re.IGNORECASE)

HARD_CHAT_TERMS = (
    "holo voice",
    "holo feel",
    "classic holo",
    "not like holo",
    "holo",
    "verify",
    "decision",
    "decide",
    "risk",
    "strategy",
    "strategic",
    "argument",
    "architecture",
    "adversarial",
    "proof",
    "audit",
    "governance",
    "policy",
    "legal",
    "medical",
    "financial",
    "high stakes",
    "should we",
    "what should",
)


@dataclass(frozen=True)
class ShadowTrigger:
    should_run: bool
    reason: str


def governed_shadow_enabled(env: dict[str, str] | None = None) -> bool:
    env_map = env if env is not None else os.environ
    return str(env_map.get(GOVERNED_SHADOW_ENV, "")).strip().lower() in {"1", "true", "yes", "on"}


def governed_shadow_trigger(
    user_message: str,
    *,
    thread_health_level: str = "GREEN",
    context_token_estimate: int | None = None,
) -> ShadowTrigger:
    text = " ".join((user_message or "").split())
    lowered = text.lower()
    if not text:
        return ShadowTrigger(False, "empty_message")
    if thread_health_level in {"YELLOW", "RED"}:
        return ShadowTrigger(True, f"thread_health_{thread_health_level.lower()}")
    if context_token_estimate is not None and context_token_estimate >= 12000:
        return ShadowTrigger(True, "context_window_stress")
    if len(text) >= 900:
        return ShadowTrigger(True, "long_multi_part_prompt")
    if text.count("?") >= 3 or len(re.findall(r"(?m)^\s*(?:[-*]|\d+[.)])\s+", text)) >= 3:
        return ShadowTrigger(True, "multi_part_prompt")
    for term in HARD_CHAT_TERMS:
        if term in lowered:
            return ShadowTrigger(True, f"hard_chat_term:{term}")
    return ShadowTrigger(False, "not_hard_chat")


def adapter_identity(adapter: Any) -> tuple[str, str]:
    return (
        str(getattr(adapter, "provider", "")),
        str(getattr(adapter, "model_id", getattr(adapter, "model", ""))),
    )


def roster_metadata() -> list[dict[str, str]]:
    return [dict(item) for item in ROSTER]


def find_roster_adapters(adapters: Iterable[Any]) -> tuple[dict[str, Any], list[str]]:
    pool = list(adapters)
    found: dict[str, Any] = {}
    missing: list[str] = []
    for item in ROSTER:
        key = f"{item['provider']}/{item['model']}"
        match = next((adapter for adapter in pool if adapter_identity(adapter) == (item["provider"], item["model"])), None)
        if match is None:
            match = _instantiate_roster_adapter(item)
            if match is not None:
                pool.append(match)
        if match is None:
            missing.append(key)
        else:
            found[item["slot"]] = match
    return found, missing


def _instantiate_roster_adapter(item: dict[str, str]) -> Any | None:
    provider = item["provider"]
    model = item["model"]
    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY", "").strip():
            return None
        adapter = OpenAIAdapter()
        adapter.model_id = model
        return adapter
    if provider == "xai":
        key = os.getenv("XAI_API_KEY", "").strip()
        if not key:
            return None
        base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1").strip()
        return OpenAICompatibleAdapter(provider, model, key, base_url)
    if provider == "minimax":
        key = os.getenv("MINIMAX_API_KEY", "").strip()
        if not key:
            return None
        base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1").strip()
        return OpenAICompatibleAdapter(provider, model, key, base_url)
    return None


def safe_skip_metadata(*, enabled: bool, trigger: ShadowTrigger, missing_roster: list[str] | None = None) -> dict[str, Any]:
    status = "off"
    if enabled and not trigger.should_run:
        status = "skipped"
    elif enabled and missing_roster:
        status = "skipped"
    return {
        "version": GOVERNED_SHADOW_VERSION,
        "mode": "shadow",
        "enabled": enabled,
        "status": status,
        "triggered": False,
        "trigger_reason": trigger.reason,
        "missing_roster": list(missing_roster or []),
        "roster": roster_metadata(),
        "call_count": 0,
        "expected_call_count": len(ROSTER),
        "visible_answer_replaced": False,
    }


def compact_text(value: Any, *, limit: int = 240) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _safe_memory_items(items: dict[str, Any] | None, *, limit: int = 6) -> list[dict[str, str]]:
    safe: list[dict[str, str]] = []
    for key, value in (items or {}).items():
        joined = f"{key} {value}".lower()
        if any(marker in joined for marker in SECRET_MARKERS):
            continue
        safe.append({"key": compact_text(key, limit=80), "value": compact_text(value, limit=160)})
        if len(safe) >= limit:
            break
    return safe


def build_state_brief(
    *,
    holo_state: HoloState,
    capsule_context: dict[str, Any] | None,
    visible_answer: str,
) -> dict[str, Any]:
    state = holo_state.model_dump(mode="json")
    return {
        "state_id": state.get("state_id"),
        "session_id": state.get("session_id"),
        "turn_number": state.get("turn_number"),
        "user_goal": state.get("user_goal"),
        "latest_input_summary": state.get("latest_input_summary"),
        "critical_constraints": state.get("critical_constraints", [])[:6],
        "rolling_summary": compact_text(state.get("rolling_summary"), limit=1200),
        "continuity_ledger": state.get("continuity_ledger", {}),
        "settled_decisions": state.get("settled_decisions", [])[:8],
        "artifact_registry": state.get("artifact_registry", [])[:8],
        "gov_arc_state": state.get("gov_arc_state", {}),
        "selected_holobrain_memory": _safe_memory_items(capsule_context),
        "visible_answer_summary": compact_text(visible_answer, limit=360),
    }


def initial_baton() -> dict[str, Any]:
    return {
        "route_verdict": "CONTINUE_WORKER",
        "control_action": "MAP_AND_CHALLENGE",
        "must_preserve": ["user goal", "critical constraints", "unresolved dependencies"],
        "must_repair": ["surface blind spots before final answer"],
        "blocked_moves": ["do not silently drop constraints", "do not invent source references"],
        "dependency_ledger": ["verify whether the visible answer missed risks, tradeoffs, or structure"],
        "next_worker_baton": {
            "objective": "Produce a stronger shadow answer candidate.",
            "attack_focus": "reasoning quality and blindspot coverage",
            "required_repairs": ["preserve state brief", "name unresolved dependencies"],
            "monotonic_preservation": [],
        },
        "final_compiler_allowed": False,
    }


def _routing_lens(baton: dict[str, Any]) -> dict[str, Any]:
    return {
        "route_verdict": baton.get("route_verdict"),
        "main_repair_target": _first(baton.get("must_repair"), "reasoning quality"),
        "blocked_move": _first(baton.get("blocked_moves"), "do not drop constraints"),
        "unresolved_dependency": _first(baton.get("dependency_ledger"), "unresolved risks"),
        "current_objective": baton.get("control_action") or "CONTINUE_WORKER",
    }


def _first(value: Any, default: str) -> str:
    if isinstance(value, list) and value:
        return compact_text(value[0], limit=160)
    if isinstance(value, str) and value:
        return compact_text(value, limit=160)
    return default


def build_worker_prompt(
    *,
    run_id: str,
    user_message: str,
    state_brief: dict[str, Any],
    latest_baton: dict[str, Any],
    worker: dict[str, str],
    prior_artifacts: list[dict[str, Any]],
) -> tuple[str, str, dict[str, Any]]:
    prompt_object = {
        "system_role": "You are a HoloChat governed-shadow worker. Preserve state. Obey Gov.",
        "gov_routing_lens": _routing_lens(latest_baton),
        "run_lock": {
            "run_id": run_id,
            "lane": "HOLOCHAT_GOVERNED_SHADOW_REASONING",
            "slot": worker["slot"],
            "role": worker["worker_role"],
            "model": f"{worker['provider']}/{worker['model']}",
            "no_substitutions": True,
        },
        "task_answer_contract": {
            "task": "Produce a stronger private shadow answer candidate for the user turn.",
            "required_sections": ["answer", "risks_or_blindspots", "unresolved_dependencies"],
            "source_rules": ["do not invent source IDs", "do not expose hidden memory", "preserve critical constraints"],
        },
        "source_context": {
            "user_message": compact_text(user_message, limit=2400),
            "selected_memory_only": state_brief.get("selected_holobrain_memory", []),
        },
        "state_brief": state_brief,
        "raw_prior_outputs": [
            {k: item.get(k) for k in ("artifact_id", "worker_role", "summary", "gate_passed", "gate_failures")}
            for item in prior_artifacts[-4:]
        ],
        "full_latest_gov_baton": latest_baton,
        "current_turn_command": (
            "Return a concise shadow candidate. Include explicit unresolved dependencies if any. "
            "Do not include raw prompts, secrets, source IDs you were not given, JSON, or markdown fences."
        ),
    }
    system = (
        "You are a HoloChat governed-shadow worker. "
        "Read the Gov routing lens first, then the state brief, then the full latest Gov baton near the end. "
        "Gov does not choose models; the run lock controls roster order. "
        "Return plain text only for a private shadow trace."
    )
    user = (
        "GOV ROUTING LENS:\n"
        f"{prompt_object['gov_routing_lens']}\n\n"
        "STATE_BRIEF:\n"
        f"{state_brief}\n\n"
        "FULL LATEST GOV BATON:\n"
        f"{latest_baton}\n\n"
        "CURRENT TURN COMMAND:\n"
        f"{prompt_object['current_turn_command']}"
    )
    return system, user, prompt_object


def build_gov_prompt(
    *,
    run_id: str,
    state_brief: dict[str, Any],
    worker_artifact: dict[str, Any],
    gate_result: dict[str, Any],
) -> tuple[str, str, dict[str, Any]]:
    action = "FINAL_COMPILER" if gate_result.get("passed") else "CONTINUE_WORKER"
    repair = "NONE" if gate_result.get("passed") else "GATE_REPAIR"
    selected_lines = [
        f"route_verdict={action}",
        f"control_action={action}",
        "must_preserve=STATE|CONSTRAINTS|BEST_ARTIFACT",
        f"must_repair={repair}",
        "blocked_moves=DROP_CONSTRAINTS|INVENT_SOURCES|REPLACE_VISIBLE_ANSWER",
        "dependency_ledger=UNRESOLVED_IF_ANY",
        f"final_compiler_allowed={'true' if gate_result.get('passed') else 'false'}",
    ]
    prompt_object = {
        "run_id": run_id,
        "worker_artifact": {
            "artifact_id": worker_artifact.get("artifact_id"),
            "worker_role": worker_artifact.get("worker_role"),
            "gate_passed": gate_result.get("passed"),
            "gate_failures": gate_result.get("failures", []),
            "summary": worker_artifact.get("summary"),
        },
        "state_keys": sorted(state_brief.keys()),
        "selected_baton_lines": selected_lines,
        "gov_may_select_models": False,
    }
    system = (
        "You are HoloGov for HoloChat governed-shadow. "
        "Return only the selected baton key=value lines. No prose. No JSON. "
        "You route control actions only and must not choose models."
    )
    user = f"Copy these lines exactly:\n" + "\n".join(selected_lines)
    return system, user, prompt_object


def parse_gov_baton(text: str) -> dict[str, Any]:
    if not text or not text.strip():
        raise ValueError("gov_empty_text")
    if "```" in text:
        raise ValueError("gov_markdown_fence_present")
    parsed: dict[str, Any] = {}
    for line in text.strip().splitlines():
        if "=" not in line:
            raise ValueError("gov_non_key_value_line")
        key, value = line.split("=", 1)
        key = key.strip()
        if key in FORBIDDEN_MODEL_SELECTION_KEYS:
            raise ValueError(f"gov_model_selection_forbidden:{key}")
        parsed[key] = value.strip()
    for forbidden in FORBIDDEN_MODEL_SELECTION_KEYS:
        if forbidden in parsed:
            raise ValueError(f"gov_model_selection_forbidden:{forbidden}")
    return {
        "route_verdict": parsed.get("route_verdict", "CONTINUE_WORKER"),
        "control_action": parsed.get("control_action", "CONTINUE_WORKER"),
        "must_preserve": _split_codes(parsed.get("must_preserve")),
        "must_repair": _split_codes(parsed.get("must_repair")),
        "blocked_moves": _split_codes(parsed.get("blocked_moves")),
        "dependency_ledger": _split_codes(parsed.get("dependency_ledger")),
        "next_worker_baton": {
            "objective": parsed.get("control_action", "CONTINUE_WORKER"),
            "attack_focus": parsed.get("must_repair", "REASONING_QUALITY"),
            "required_repairs": _split_codes(parsed.get("must_repair")),
            "monotonic_preservation": _split_codes(parsed.get("must_preserve")),
        },
        "final_compiler_allowed": str(parsed.get("final_compiler_allowed", "")).lower() == "true",
    }


def _split_codes(value: Any) -> list[str]:
    text = str(value or "").strip()
    if not text or text == "NONE":
        return []
    return [item for item in text.split("|") if item]


def validate_worker_artifact(text: str, state_brief: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    compact = compact_text(text, limit=800)
    lowered = compact.lower()
    if len(compact.split()) < 8:
        failures.append("answer_contract_missing_or_too_short")
    if any(marker in lowered for marker in SECRET_MARKERS):
        failures.append("raw_secret_or_hidden_context_marker")
    if SOURCE_REF_RE.search(compact):
        failures.append("invented_source_reference")
    for constraint in state_brief.get("critical_constraints") or []:
        key_terms = [part.lower() for part in re.findall(r"[A-Za-z0-9]{4,}", str(constraint))[:3]]
        if key_terms and not any(term in lowered for term in key_terms):
            failures.append("critical_constraint_not_preserved")
            break
    unresolved = state_brief.get("continuity_ledger", {}).get("open_issues") or []
    if unresolved and "unresolved" not in lowered and "open" not in lowered and "risk" not in lowered:
        failures.append("unresolved_dependencies_not_flagged")
    return {
        "passed": not failures,
        "failures": failures,
        "checks": {
            "answer_contract_present": "answer_contract_missing_or_too_short" not in failures,
            "no_raw_secret_context": "raw_secret_or_hidden_context_marker" not in failures,
            "no_invented_source_refs": "invented_source_reference" not in failures,
            "critical_constraints_preserved": "critical_constraint_not_preserved" not in failures,
            "unresolved_dependencies_flagged": "unresolved_dependencies_not_flagged" not in failures,
        },
    }


def select_best_artifact(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    admissible = [item for item in artifacts if item.get("gate_result", {}).get("passed")]
    if not admissible:
        return {
            "selected_artifact_id": None,
            "selected_turn": None,
            "selection_reason": "NO_ADMISSIBLE_SHADOW_ARTIFACT",
            "final_regressed": True,
        }
    final = artifacts[-1] if artifacts else None
    selected = final if final and final.get("gate_result", {}).get("passed") else admissible[-1]
    return {
        "selected_artifact_id": selected.get("artifact_id"),
        "selected_turn": selected.get("slot"),
        "selection_reason": "FINAL_ARTIFACT_SELECTED" if selected is final else "BEST_PRIOR_ADMISSIBLE_SELECTED",
        "final_regressed": selected is not final,
    }


def estimate_tokens(text: str) -> int:
    return max(1, (len(text or "") + 3) // 4)


def _safe_error(exc: BaseException) -> dict[str, str]:
    return {"type": type(exc).__name__}


def _call_adapter(adapter: Any, system: str, user: str) -> tuple[str, int, int]:
    text, input_tokens, output_tokens = adapter.chat_call(system, [], user, 0)
    if not isinstance(input_tokens, int) or input_tokens <= 0:
        input_tokens = estimate_tokens(system + "\n" + user)
    if not isinstance(output_tokens, int) or output_tokens <= 0:
        output_tokens = estimate_tokens(text)
    return str(text or ""), input_tokens, output_tokens


def run_governed_shadow(
    *,
    adapters: Iterable[Any],
    user_message: str,
    holo_state: HoloState,
    capsule_context: dict[str, Any] | None,
    visible_answer: str,
    context_token_estimate: int | None = None,
) -> dict[str, Any]:
    enabled = governed_shadow_enabled()
    trigger = governed_shadow_trigger(
        user_message,
        thread_health_level=holo_state.thread_health.level,
        context_token_estimate=context_token_estimate,
    )
    if not enabled or not trigger.should_run:
        return safe_skip_metadata(enabled=enabled, trigger=trigger)

    roster_adapters, missing = find_roster_adapters(adapters)
    if missing:
        return safe_skip_metadata(enabled=enabled, trigger=trigger, missing_roster=missing)

    started = time.time()
    run_id = f"hc_gov_shadow_{uuid.uuid4().hex[:12]}"
    state_brief = build_state_brief(
        holo_state=holo_state,
        capsule_context=capsule_context,
        visible_answer=visible_answer,
    )
    latest_baton = initial_baton()
    call_rows: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    token_totals = {"worker_input": 0, "worker_output": 0, "gov_input": 0, "gov_output": 0}

    for item in ROSTER:
        adapter = roster_adapters[item["slot"]]
        row = {
            "slot": item["slot"],
            "role": item["role"],
            "provider": item["provider"],
            "model": item["model"],
        }
        try:
            if item["role"] == "worker":
                system, user, prompt_object = build_worker_prompt(
                    run_id=run_id,
                    user_message=user_message,
                    state_brief=state_brief,
                    latest_baton=latest_baton,
                    worker=item,
                    prior_artifacts=artifacts,
                )
                text, input_tokens, output_tokens = _call_adapter(adapter, system, user)
                gate = validate_worker_artifact(text, state_brief)
                artifact = {
                    "artifact_id": f"{run_id}_{item['slot']}",
                    "slot": item["slot"],
                    "worker_role": item["worker_role"],
                    "summary": compact_text(text, limit=220),
                    "word_count": len(text.split()),
                    "gate_result": gate,
                }
                artifacts.append(artifact)
                token_totals["worker_input"] += input_tokens
                token_totals["worker_output"] += output_tokens
                row.update(
                    {
                        "provider_call_ok": True,
                        "parse_ok": True,
                        "admissible": gate["passed"],
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "gate_result": gate,
                        "artifact_id": artifact["artifact_id"],
                        "prompt_contract": {
                            "gov_routing_lens_present": "gov_routing_lens" in prompt_object,
                            "state_brief_present": "state_brief" in prompt_object,
                            "full_latest_gov_baton_present": "full_latest_gov_baton" in prompt_object,
                        },
                    }
                )
            else:
                system, user, prompt_object = build_gov_prompt(
                    run_id=run_id,
                    state_brief=state_brief,
                    worker_artifact=artifacts[-1] if artifacts else {},
                    gate_result=artifacts[-1]["gate_result"] if artifacts else {"passed": False, "failures": ["missing_worker"]},
                )
                text, input_tokens, output_tokens = _call_adapter(adapter, system, user)
                latest_baton = parse_gov_baton(text)
                token_totals["gov_input"] += input_tokens
                token_totals["gov_output"] += output_tokens
                row.update(
                    {
                        "provider_call_ok": True,
                        "parse_ok": True,
                        "admissible": True,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "received_gate_result": True,
                        "gov_may_select_models": prompt_object["gov_may_select_models"],
                        "route_verdict": latest_baton.get("route_verdict"),
                    }
                )
        except Exception as exc:
            row.update(
                {
                    "provider_call_ok": False,
                    "parse_ok": False,
                    "admissible": False,
                    "error": _safe_error(exc),
                }
            )
            call_rows.append(row)
            return _summary(
                run_id=run_id,
                status="invalid",
                trigger=trigger,
                call_rows=call_rows,
                artifacts=artifacts,
                token_totals=token_totals,
                started=started,
                invalidation_reason=f"{item['role'].upper()}_FAILURE",
            )
        call_rows.append(row)

    return _summary(
        run_id=run_id,
        status="complete",
        trigger=trigger,
        call_rows=call_rows,
        artifacts=artifacts,
        token_totals=token_totals,
        started=started,
        invalidation_reason=None,
    )


def _summary(
    *,
    run_id: str,
    status: str,
    trigger: ShadowTrigger,
    call_rows: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
    token_totals: dict[str, int],
    started: float,
    invalidation_reason: str | None,
) -> dict[str, Any]:
    worker_total = token_totals["worker_input"] + token_totals["worker_output"]
    gov_total = token_totals["gov_input"] + token_totals["gov_output"]
    total = worker_total + gov_total
    selector = select_best_artifact(artifacts)
    failed = next((row for row in call_rows if row.get("provider_call_ok") is not True or row.get("parse_ok") is not True), None)
    return {
        "version": GOVERNED_SHADOW_VERSION,
        "mode": "shadow",
        "enabled": True,
        "status": status,
        "triggered": True,
        "trigger_reason": trigger.reason,
        "run_id": run_id,
        "roster": roster_metadata(),
        "call_count": len(call_rows),
        "expected_call_count": len(ROSTER),
        "call_sequence": [
            {key: row.get(key) for key in ("slot", "role", "provider", "model", "provider_call_ok", "parse_ok", "admissible")}
            for row in call_rows
        ],
        "gate_results": [
            {
                "slot": row.get("slot"),
                "artifact_id": row.get("artifact_id"),
                "passed": row.get("gate_result", {}).get("passed"),
                "failures": row.get("gate_result", {}).get("failures", []),
            }
            for row in call_rows
            if row.get("role") == "worker"
        ],
        "token_totals": {
            **token_totals,
            "worker_total": worker_total,
            "gov_total": gov_total,
            "total": total,
            "gov_share": round(gov_total / total, 6) if total else None,
        },
        "final_selector": selector,
        "invalidation_reason": invalidation_reason,
        "root_failure": failed,
        "visible_answer_replaced": False,
        "elapsed_ms": int((time.time() - started) * 1000),
        "safe_metadata_only": True,
    }
