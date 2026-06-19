from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

PACKET_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKET_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT))
from artifact_benchmarks.harness.judge_consistency import score_verdict_consistency_flags

PROVIDERS = {
    "openai": {
        "model": "gpt-5.5",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
    },
    "anthropic": {
        "model": "claude-opus-4-8",
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": "https://api.anthropic.com/v1",
    },
    "google": {
        "model": "gemini-3.1-pro-preview",
        "api_key_env": "GOOGLE_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
    },
    "xai": {
        "model": "grok-4.3",
        "api_key_env": "XAI_API_KEY",
        "base_url": "https://api.x.ai/v1",
    },
}

SOLO_CONDITIONS = {
    "solo_openai": "openai:gpt-5.5",
    "solo_anthropic": "anthropic:claude-opus-4-8",
    "solo_google": "google:gemini-3.1-pro-preview",
}

FINAL_MIN_WORDS = 2800
FINAL_TARGET_MAX_WORDS = 3400
FINAL_MAX_WORDS = 3600
STATE_OBJECT_VERSION = "patent_grade_holo_state_v1"
MAX_PRIOR_ARTIFACT_CHARS = 18000
HC_STATE_AUTHORITY_RULE = (
    "Only HC may mutate benchmark architecture/state. HoloAgents may write artifacts; "
    "Gov may baton, gate, and summarize; durable architecture updates enter through "
    "HC via ROLLING_SUMMARY."
)


class ProviderCallError(RuntimeError):
    def __init__(
        self,
        provider: str,
        error_type: str,
        message: str,
        *,
        http_status: int | None = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.error_type = error_type
        self.http_status = http_status


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    return sha_text(read_text(path))


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def excerpt(text: Any, limit: int = 500) -> str:
    cleaned = re.sub(r"\s+", " ", str(text)).strip()
    return cleaned[:limit]


def env_status() -> dict[str, str]:
    return {
        cfg["api_key_env"]: ("PRESENT" if os.getenv(cfg["api_key_env"]) else "MISSING")
        for cfg in PROVIDERS.values()
    }


def provider_model(provider_model: str) -> tuple[str, str]:
    provider, model = provider_model.split(":", 1)
    return provider, model


def solo_provider_for_condition(condition: str) -> str | None:
    provider_model_name = SOLO_CONDITIONS.get(condition)
    if not provider_model_name:
        return None
    provider, _ = provider_model(provider_model_name)
    return provider


def turn_prompt_parity_contract(role_flow: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "turn": int(item["turn"]),
            "role": item["role"],
            "turn_instruction_sha256": sha_text(item["instruction"]),
            "same_base_turn_prompt_for_solo_and_holo": True,
            "holo_extra_context": "Gov Baton Pass plus STATE_OBJECT plus pinned artifacts.",
        }
        for item in role_flow["turns"]
    ]


def load_routing_config(routing_config_id: str | None) -> dict[str, Any]:
    suite = read_json(PACKET_DIR / "holo_routing_configs.json")
    selected = routing_config_id or suite["default_routing_config_id"]
    for config in suite["routing_configs"]:
        if config["routing_config_id"] == selected:
            return config
    valid = ", ".join(config["routing_config_id"] for config in suite["routing_configs"])
    raise RuntimeError(f"unknown_routing_config:{selected}; valid={valid}")


def apply_holo_routing_config(role_flow: dict[str, Any], routing_config: dict[str, Any]) -> dict[str, Any]:
    turns = role_flow["turns"]
    rotation = routing_config["analyst_rotation"]
    if len(rotation) != len(turns):
        raise RuntimeError("routing_config_must_have_one_model_per_turn")
    routed = json.loads(json.dumps(role_flow))
    for idx, provider_model_name in enumerate(rotation):
        routed["turns"][idx]["provider_model"] = provider_model_name
    routed["routing_config_id"] = routing_config["routing_config_id"]
    routed["routing_config_label"] = routing_config.get("label")
    return routed


def packet_hashes() -> dict[str, str]:
    files = {
        "source_pack": "source_pack.json",
        "report_brief": "report_brief.json",
        "gov_protocol": "gov_technical_probe_protocol.json",
        "role_flow": "finance_algo_adversarial_role_flow.json",
        "routing_configs": "holo_routing_configs.json",
        "judge_rubric": "judge_rubric_8criteria.json",
        "judge_panel": "judge_panel_frontier_blind.json",
        "run_prompt": "holo_frontier_run_prompt.md",
        "judge_brief": "judge_brief.md",
    }
    return {key: sha_file(PACKET_DIR / name) for key, name in files.items()}


def model_visible_report_brief() -> dict[str, Any]:
    brief = read_json(PACKET_DIR / "report_brief.json")
    return {
        "brief_id": brief["brief_id"],
        "created_at_utc": brief["created_at_utc"],
        "domain": brief["domain"],
        "audience": brief["audience"],
        "task": brief["task"],
        "deliverable_requirements": brief["deliverable_requirements"],
    }


def frozen_base_generation_payload() -> str:
    payload = {
        "benchmark_credit": False,
        "public_claim": False,
        "internet_policy": "Do not browse. Use only this frozen packet.",
        "source_pack": read_json(PACKET_DIR / "source_pack.json"),
        "report_brief": model_visible_report_brief(),
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def frozen_holo_generation_payload(*, role_flow: dict[str, Any], routing_config: dict[str, Any]) -> str:
    payload = json.loads(frozen_base_generation_payload())
    payload.update(
        {
            "holo_architecture_mode": STATE_OBJECT_VERSION,
            "holo_architecture_note": (
                "Gov baton first; canonical STATE_OBJECT; pinned artifact registry; "
                "preserved insight ledger; repair ledger; adversarial role; prior artifacts."
            ),
            "gov_technical_probe_protocol": read_json(PACKET_DIR / "gov_technical_probe_protocol.json"),
            "role_flow": role_flow,
            "holo_routing_config": routing_config,
        }
    )
    return json.dumps(payload, indent=2, sort_keys=True)


def frozen_generation_payload(*, role_flow: dict[str, Any], routing_config: dict[str, Any]) -> str:
    return frozen_holo_generation_payload(role_flow=role_flow, routing_config=routing_config)


def frozen_judge_payload() -> str:
    payload = {
        "benchmark_credit": False,
        "public_claim": False,
        "internet_policy": "Do not browse. Use only this frozen packet and blind documents.",
        "source_pack": read_json(PACKET_DIR / "source_pack.json"),
        "report_brief": model_visible_report_brief(),
        "judge_rubric": read_json(PACKET_DIR / "judge_rubric_8criteria.json"),
        "judge_panel": read_json(PACKET_DIR / "judge_panel_frontier_blind.json"),
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def clean_ending(text: str) -> bool:
    stripped = text.strip()
    return bool(stripped) and stripped[-1] in ".!?)]`\"'"


def source_ids_in_text(text: str) -> list[str]:
    return sorted(set(re.findall(r"\[S\d+(?:_[A-Z0-9_]+)?\]", text)))


def allowed_source_ids() -> set[str]:
    source_pack = read_json(PACKET_DIR / "source_pack.json")
    ids = set()
    for entry in source_pack.get("source_entries", []):
        full_id = entry["id"]
        ids.add(f"[{full_id}]")
        ids.add(f"[{full_id.split('_', 1)[0]}]")
    return ids


def has_any(text: str, needles: list[str]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def final_artifact_validity_report(text: str) -> dict[str, Any]:
    wc = word_count(text)
    lowered = text.lower()
    flags: list[str] = []
    if not (FINAL_MIN_WORDS <= wc <= FINAL_MAX_WORDS):
        flags.append(f"final_word_count_out_of_band:{wc}")
    if not clean_ending(text):
        flags.append("final_does_not_end_cleanly")
    tail = text.strip()[-260:].lower()
    if re.search(r"(\n|^)\s*[-*]\s+\S.{0,120}$", text.strip()) and not clean_ending(text):
        flags.append("final_appears_cut_off_mid_bullet")
    if tail.count("(") > tail.count(")") or tail.count("[") > tail.count("]"):
        flags.append("final_tail_has_unbalanced_bracket_or_parenthesis")

    required_topics = {
        "disclaimer_no_investment_advice": ["not investment advice", "not legal", "not a recommendation"],
        "disclaimer_no_live_execution": [
            "does not execute",
            "not a live execution",
            "does not route orders",
            "no live execution",
            "not a live trading",
            "not connected to live brokerage",
            "not an order-routing system",
        ],
        "executive_thesis": ["executive thesis", "thesis"],
        "current_market_setup": ["current market", "market setup", "market regime"],
        "execution_architecture": ["architecture", "execution governor", "control plane"],
        "benchmark_framework": ["implementation shortfall", "arrival price", "benchmark"],
        "portfolio_funding_settlement": ["portfolio", "funding", "settlement"],
        "regulatory_controls_audit": ["controls", "audit", "kill switch", "kill-switch"],
        "model_risk_adversarial": ["model risk", "adversarial", "bias"],
        "implementation_roadmap": ["roadmap", "phase", "implementation"],
        "success_metrics": ["success metrics", "metrics", "kpis", "measurement"],
    }
    for topic, needles in required_topics.items():
        if not has_any(lowered, needles):
            flags.append(f"missing_required_topic:{topic}")

    internal_residue_terms = [
        "state_object",
        "mission packet",
        "baton pass",
        "benchmark_credit",
        "document x",
        "document y",
        "turn_5",
        "turn_6",
        "hologov",
        "holoagent",
    ]
    residue = [term for term in internal_residue_terms if term in lowered]
    if residue:
        flags.append("internal_process_residue:" + ",".join(residue))

    unknown_source_ids = sorted(set(source_ids_in_text(text)) - allowed_source_ids())
    if unknown_source_ids:
        flags.append("unknown_source_ids:" + ",".join(unknown_source_ids))
    if not source_ids_in_text(text):
        flags.append("missing_source_ids")

    return {
        "valid": not flags,
        "flags": flags,
        "word_count": wc,
        "word_count_in_band": FINAL_MIN_WORDS <= wc <= FINAL_MAX_WORDS,
        "clean_ending": clean_ending(text),
        "source_ids": source_ids_in_text(text),
    }


def detect_preserved_insights(previous_artifacts: list[dict[str, str]]) -> list[dict[str, Any]]:
    insight_specs = [
        (
            "arrival_price_spine",
            "Arrival price / implementation shortfall as the benchmark spine",
            ["arrival", "implementation shortfall"],
        ),
        (
            "cost_of_acting_gate",
            "Cost-of-acting / net-benefit gate before changing execution action",
            ["cost of acting", "net-benefit"],
        ),
        (
            "tiered_authority_boundaries",
            "Tiered authority boundaries for automated, confirm, and human-only decisions",
            ["tier a", "tier b", "tier c"],
        ),
        (
            "post_kill_state_machine",
            "Post-kill state machine, re-enable control, and audit aftermath",
            ["post-kill", "state machine"],
        ),
        (
            "offline_champion_challenger_learning",
            "Offline batched learning with champion/challenger validation",
            ["offline", "champion", "challenger"],
        ),
        (
            "fact_vs_inference_labeling",
            "Explicit source fact versus inference labeling",
            ["inference", "source-grounded"],
        ),
        (
            "time_scale_separation",
            "Time-scale separation across event-time, clock-time, and clearing/funding clocks",
            ["time-scale"],
        ),
        (
            "tracking_error_urgency",
            "Portfolio urgency as tracking-error or active-risk reduction versus impact cost",
            ["tracking-error"],
        ),
        (
            "funding_constraint_binds_first",
            "Funding, settlement, and clearing constraints bind before execution micro-optimization",
            ["funding", "settlement", "bind"],
        ),
        (
            "benchmark_divergence_rule",
            "Divergence rule when VWAP improves while arrival/IS worsens",
            ["vwap", "implementation shortfall", "worsen"],
        ),
        (
            "audit_intent_provenance",
            "Audit ledger with order intent provenance and decision reconstruction",
            ["audit", "intent provenance"],
        ),
    ]
    found: list[dict[str, Any]] = []
    for insight_id, label, terms in insight_specs:
        turns = []
        for item in previous_artifacts:
            lowered = item["text"].lower()
            if all(term in lowered for term in terms):
                turns.append(int(item["turn"]))
        if turns:
            found.append(
                {
                    "insight_id": insight_id,
                    "label": label,
                    "evidence_turns": turns,
                    "preservation_rule": "Preserve or explicitly reject with source-grounded rationale.",
                }
            )
    return found


def artifact_registry(previous_artifacts: list[dict[str, str]]) -> list[dict[str, Any]]:
    registry = []
    for item in previous_artifacts:
        text = item["text"].strip() + "\n"
        registry.append(
            {
                "artifact_id": f"turn_{item['turn']}_draft_v1",
                "version": 1,
                "status": "PINNED",
                "turn": int(item["turn"]),
                "role": item["role"],
                "provider_model": item.get("provider_model"),
                "sha256": sha_text(text),
                "word_count": word_count(text),
                "clean_ending": clean_ending(text),
                "source_ids": source_ids_in_text(text),
                "pointer": item.get("path"),
                "description": excerpt(text, 260),
            }
        )
    return registry


def build_state_object(
    *,
    report_brief: dict[str, Any],
    routing_config: dict[str, Any],
    turn: int,
    role_item: dict[str, Any],
    previous_artifacts: list[dict[str, str]],
) -> dict[str, Any]:
    requirements = report_brief["deliverable_requirements"]
    latest = previous_artifacts[-1] if previous_artifacts else None
    latest_flags: list[str] = []
    if latest:
        if not clean_ending(latest["text"]):
            latest_flags.append(f"turn_{latest['turn']}_does_not_end_cleanly")
        if word_count(latest["text"]) < 1200 and int(latest["turn"]) >= 3:
            latest_flags.append(f"turn_{latest['turn']}_likely_incomplete_by_word_count")
    return {
        "state_object_version": STATE_OBJECT_VERSION,
        "USER_GOAL": report_brief["task"],
        "LATEST_INPUT_SUMMARY": f"Prepare Turn {turn} for {role_item['role']}.",
        "CRITICAL_CONSTRAINTS": [
            *requirements["must_not_include"],
            f"Target final length: {requirements['target_length_words'][0]}-{requirements['target_length_words'][1]} words.",
            "Use only frozen source pack facts unless explicitly labeled as inference.",
            "No browsing during generation or judging.",
            HC_STATE_AUTHORITY_RULE,
        ],
        "ROLLING_SUMMARY": [
            {"turn": int(item["turn"]), "role": item["role"], "summary": excerpt(item["text"], 500)}
            for item in previous_artifacts
        ],
        "HC_STATE_AUTHORITY": {
            "architecture_mutation_surface": "HC",
            "mutable_state_surface": "ROLLING_SUMMARY",
            "rule": HC_STATE_AUTHORITY_RULE,
        },
        "SETTLED_DECISIONS": [
            "Fixed Opus Gov for this session.",
            f"Routing config: {routing_config['routing_config_id']}.",
            "Final artifact must be client-shareable and not a live trading or investment recommendation.",
            "Gov must preserve winning insights and track regressions before synthesis.",
        ],
        "ARTIFACTS_REGISTRY": artifact_registry(previous_artifacts),
        "REQUIRED_TOOLS": "NONE",
        "BATON_PASS": {
            "next_turn": turn,
            "next_model_instance": role_item["provider_model"],
            "adversarial_cognitive_role": role_item["role"],
            "role_instruction": role_item["instruction"],
            "specific_focus": "Challenge the current draft as an external hypothesis; preserve only source-grounded improvements.",
            "unresolved_tensions": latest_flags,
        },
        "PRESERVED_INSIGHT_LEDGER": detect_preserved_insights(previous_artifacts),
        "REPAIR_LEDGER": {
            "open_issue": latest_flags,
            "repaired": [],
            "regressed": [],
            "still_missing": [],
        },
    }


def state_object_text(state_object: dict[str, Any]) -> str:
    return json.dumps(state_object, indent=2, sort_keys=False)


def pinned_artifact_text(previous_artifacts: list[dict[str, str]]) -> str:
    if not previous_artifacts:
        return "No prior artifacts. This is Turn 1."
    blocks = []
    for item in previous_artifacts:
        text = item["text"].strip()
        if len(text) > MAX_PRIOR_ARTIFACT_CHARS:
            text = text[:MAX_PRIOR_ARTIFACT_CHARS] + "\n\n[TRUNCATED IN PROMPT: full artifact remains pinned by SHA/path in STATE_OBJECT]"
        blocks.append(
            f"## PINNED artifact turn_{item['turn']}_draft_v1 ({item['role']})\n"
            f"provider_model: {item.get('provider_model')}\n"
            f"sha256: {sha_text(item['text'].strip() + chr(10))}\n\n{text}"
        )
    return "\n\n".join(blocks)


def latest_draft_text(previous_artifacts: list[dict[str, str]]) -> str:
    if not previous_artifacts:
        return "No prior draft. This is Turn 1."
    return previous_artifacts[-1]["text"]


def http_post_json(
    *,
    provider: str,
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib_request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib_request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return {
                "http_status": getattr(response, "status", None),
                "json": json.loads(raw) if raw else {},
            }
    except urllib_error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise ProviderCallError(
            provider,
            "HTTPError",
            excerpt(raw or exc.reason),
            http_status=exc.code,
        ) from exc
    except urllib_error.URLError as exc:
        raise ProviderCallError(provider, "URLError", excerpt(exc.reason)) from exc
    except TimeoutError as exc:
        raise ProviderCallError(provider, "TimeoutError", excerpt(exc)) from exc
    except json.JSONDecodeError as exc:
        raise ProviderCallError(provider, "ProviderResponseJSONDecodeError", excerpt(exc)) from exc


def call_provider(
    provider: str,
    *,
    system: str,
    user: str,
    max_tokens: int,
    timeout: int,
) -> dict[str, Any]:
    cfg = PROVIDERS[provider]
    attempt = 0
    current_max_tokens = max_tokens
    last_out: dict[str, Any] | None = None
    while attempt < 2:
        started = time.monotonic()
        if provider == "anthropic":
            result = http_post_json(
                provider=provider,
                url=cfg["base_url"].rstrip("/") + "/messages",
                headers={
                    "x-api-key": os.getenv(cfg["api_key_env"], ""),
                    "anthropic-version": "2023-06-01",
                },
                payload={
                    "model": cfg["model"],
                    "max_tokens": current_max_tokens,
                    "system": system,
                    "messages": [{"role": "user", "content": user}],
                },
                timeout=timeout,
            )
            data = result["json"]
            blocks = data.get("content") or []
            text = "\n".join(block.get("text", "") for block in blocks if isinstance(block, dict))
            usage = data.get("usage") or {}
            out = {
                "text": text,
                "input_tokens": int(usage.get("input_tokens") or 0),
                "output_tokens": int(usage.get("output_tokens") or 0),
                "http_status": result["http_status"],
                "response_id": data.get("id", ""),
            }
        elif provider == "google":
            result = http_post_json(
                provider=provider,
                url=(
                    cfg["base_url"].rstrip("/")
                    + f"/models/{cfg['model']}:generateContent"
                    + "?key="
                    + os.getenv(cfg["api_key_env"], "")
                ),
                headers={},
                payload={
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": (
                                        "SYSTEM:\n"
                                        + system
                                        + "\n\nUSER:\n"
                                        + user
                                    )
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": current_max_tokens,
                    },
                },
                timeout=timeout,
            )
            data = result["json"]
            candidates = data.get("candidates") or []
            parts = []
            if candidates:
                content = candidates[0].get("content") or {}
                for part in content.get("parts") or []:
                    if isinstance(part, dict) and part.get("text"):
                        parts.append(part["text"])
            usage = data.get("usageMetadata") or {}
            out = {
                "text": "\n".join(parts),
                "input_tokens": int(usage.get("promptTokenCount") or 0),
                "output_tokens": int(usage.get("candidatesTokenCount") or 0),
                "http_status": result["http_status"],
                "response_id": "",
            }
        else:
            payload = {
                "model": cfg["model"],
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            }
            if provider == "openai":
                payload["max_completion_tokens"] = current_max_tokens
            else:
                payload["max_tokens"] = current_max_tokens
            result = http_post_json(
                provider=provider,
                url=cfg["base_url"].rstrip("/") + "/chat/completions",
                headers={"Authorization": "Bearer " + os.getenv(cfg["api_key_env"], "")},
                payload=payload,
                timeout=timeout,
            )
            data = result["json"]
            choices = data.get("choices") or []
            message = choices[0].get("message") if choices else {}
            usage = data.get("usage") or {}
            out = {
                "text": (message or {}).get("content") or "",
                "input_tokens": int(usage.get("prompt_tokens") or 0),
                "output_tokens": int(usage.get("completion_tokens") or 0),
                "http_status": result["http_status"],
                "response_id": data.get("id", ""),
            }
        out["latency_ms"] = int((time.monotonic() - started) * 1000)
        out["empty_visible_retry_count"] = attempt
        out["max_tokens_requested"] = current_max_tokens
        last_out = out
        if out["text"].strip():
            return out
        attempt += 1
        if provider == "openai":
            current_max_tokens = max(current_max_tokens * 2, 11000)
        else:
            current_max_tokens = max(current_max_tokens + 2500, 7000)
    detail = f"provider returned no visible text after retry; last={last_out}"
    raise ProviderCallError(provider, "EmptyVisibleText", detail)


def save_prompt_card(
    run_root: Path,
    *,
    rel: str,
    system: str,
    user: str,
    provider: str,
    model: str,
    call_type: str,
) -> Path:
    path = run_root / "prompt_cards" / f"{rel}.json"
    write_json(
        path,
        {
            "call_type": call_type,
            "provider": provider,
            "model": model,
            "benchmark_credit": False,
            "public_claim": False,
            "system": system,
            "user": user,
        },
    )
    return path


def save_call(
    run_root: Path,
    *,
    trace_rel: str,
    artifact_path: Path | None,
    artifact_text: str | None,
    prompt_card_path: Path,
    call_type: str,
    condition: str,
    provider: str,
    role: str,
    turn: int | None,
    result: dict[str, Any],
    hashes: dict[str, str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if artifact_path is not None and artifact_text is not None:
        write_text(artifact_path, artifact_text.strip() + "\n")
    trace = {
        "call_type": call_type,
        "condition": condition,
        "turn": turn,
        "provider": provider,
        "model": PROVIDERS[provider]["model"],
        "role": role,
        "benchmark_credit": False,
        "public_claim": False,
        "http_status": result.get("http_status"),
        "input_tokens": int(result.get("input_tokens") or 0),
        "output_tokens": int(result.get("output_tokens") or 0),
        "latency_ms": int(result.get("latency_ms") or 0),
        "empty_visible_retry_count": int(result.get("empty_visible_retry_count") or 0),
        "max_tokens_requested": int(result.get("max_tokens_requested") or 0),
        "response_id": result.get("response_id", ""),
        "prompt_card_path": str(prompt_card_path),
        "prompt_card_sha256": sha_file(prompt_card_path),
        "output_sha256": sha_text((artifact_text or result.get("text", "")).strip() + "\n"),
        "artifact_path": str(artifact_path) if artifact_path else None,
        "word_count": word_count((artifact_text or result.get("text", "")).strip()),
        "packet_hashes": hashes,
    }
    if extra:
        trace.update(extra)
    write_json(run_root / "traces" / f"{trace_rel}.json", trace)
    return trace


def markdown_system(role: str) -> str:
    return (
        "You are participating in a controlled HoloBuild artifact benchmark run. "
        "Use only the supplied frozen source pack and prior draft state. Do not browse. "
        "Do not provide investment advice. Do not recommend buying, selling, shorting, "
        "or hedging any named security. Do not claim Holo trades live markets. "
        "Use source IDs inline. Output Markdown only. "
        f"Role: {role}"
    )


def gov_system() -> str:
    return (
        "You are HoloGov in a controlled HoloBuild benchmark run. "
        "Use only the frozen packet, canonical STATE_OBJECT, and pinned artifacts. Do not browse. "
        "Your job is to produce the Baton Pass for the next model: preserve winning insights, "
        "name regressions, update the repair ledger, and ask concrete finance-native probes. "
        f"{HC_STATE_AUTHORITY_RULE} "
        "Output Markdown only."
    )


def selector_system() -> str:
    return (
        "You are HoloGov final selector and synthesis gate. Use only the frozen packet, STATE_OBJECT, "
        "pinned artifacts, and Turn 5/Turn 6 candidate finals. "
        "Do not browse. Return strict JSON only."
    )


def synthesis_system() -> str:
    return (
        "You are HoloGov final synthesis. Use only the frozen packet, STATE_OBJECT, pinned artifacts, "
        "and candidate finals. Do not browse. Produce one complete client-ready final report in Markdown."
    )


def judge_system(judge_id: str) -> str:
    return (
        f"You are {judge_id}, a blind frontier judge for a controlled artifact benchmark. "
        "You must not browse. You are not told which document is Holo or Solo. "
        "You are not told which model generated either document. "
        "Score only against the original brief, frozen source pack, rubric, and blind documents. "
        "Return strict JSON only."
    )


def turn_word_target(turn: int) -> str:
    if turn >= 5:
        return "2,800-3,400 words"
    return "1,800-2,400 words"


def solo_prompt(
    *,
    payload: str,
    condition: str,
    provider_model_name: str,
    turn: int,
    role_item: dict[str, Any],
    previous_text: str | None,
) -> str:
    previous_block = previous_text or "No prior draft. This is Turn 1."
    return f"""Frozen benchmark packet:

{payload}

Condition: {condition}
Solo model: {provider_model_name}
Turn: {turn} of 6
Role for this turn: {role_item['role']}
Turn instruction: {role_item['instruction']}
Target length for this turn: {turn_word_target(turn)}.

Previous draft state:
{previous_block}

Write the best possible updated report draft for this turn. The solo condition uses the same role sequence and same frozen context as Holo, but only this solo model writes the artifact each turn. Preserve useful prior content, repair weaknesses, and improve source-grounded technical depth. Final turns must be client-shareable and within the word band.
"""


def gov_prompt(
    *,
    payload: str,
    turn: int,
    role_item: dict[str, Any],
    previous_artifacts: list[dict[str, str]],
    state_object: dict[str, Any],
) -> str:
    history = "\n\n".join(
        f"## Prior Turn {item['turn']} ({item['role']})\n{item['text']}"
        for item in previous_artifacts
    )
    return f"""Canonical STATE_OBJECT:

```json
{state_object_text(state_object)}
```

Frozen benchmark packet:

{payload}

Holo turn to prepare: {turn} of 6
Next role: {role_item['role']}
Next role instruction: {role_item['instruction']}

Prior artifacts:
{history}

Create the Turn {turn} HoloGov mission packet. It must include:
- updated_state_object_delta
- baton_pass
- preserved_insight_ledger
- repair_ledger
- current_best_state
- new_learnings_from_prior_turns
- highest_value_flaw
- source_context_anchors
- technical_probe_questions
- order_flow_and_microstructure_checks
- benchmark_and_peer_comparison_checks
- portfolio_weight_and_risk_checks
- funding_settlement_and_clearing_checks
- regulatory_control_and_audit_checks
- model_risk_and_bias_checks
- next_role_objective
- constraints_and_do_not_do
- open_tensions
- convergence_target

Make the next model uncomfortable in the useful way: specific, technical, source-grounded, and hard to hand-wave.
Preserve any STATE_OBJECT.PRESERVED_INSIGHT_LEDGER item unless you explicitly reject it with a source-grounded rationale.
Do not mutate architecture directly. If architecture/state needs to change, write the proposed delta for HC to apply through ROLLING_SUMMARY.
"""


def holo_prompt(
    *,
    payload: str,
    turn: int,
    role_item: dict[str, Any],
    previous_artifacts: list[dict[str, str]],
    state_object: dict[str, Any],
    mission: str | None,
) -> str:
    mission_block = mission or "No Gov mission for Turn 1. Build the initial complete draft."
    return f"""HoloGov Baton Pass / Mission Packet:

{mission_block}

Canonical STATE_OBJECT:

```json
{state_object_text(state_object)}
```

Pinned prior artifacts, full-fidelity where budget allows:

{pinned_artifact_text(previous_artifacts)}

Latest draft state:

{latest_draft_text(previous_artifacts)}

Frozen benchmark packet:

{payload}

Holo condition: multi-model adversarial build with HoloGov mission packets.
Turn: {turn} of 6
Role: {role_item['role']}
Turn instruction: {role_item['instruction']}
Target length for this turn: {turn_word_target(turn)}.

Write the best possible updated report draft for this turn. Answer the Gov probes in the artifact or explicitly resolve why a probe does not apply. Preserve the strongest prior content, repair weaknesses, and improve source-grounded technical depth. Final turns must be client-shareable and within the word band.
Treat prior artifacts as external hypotheses, not ground truth. Preserve STATE_OBJECT.PRESERVED_INSIGHT_LEDGER items unless you explicitly reject them with source-grounded rationale.
Do not mutate benchmark architecture. Surface any proposed architecture/state change as an HC rolling-summary delta, not as an agent-level state rewrite.
"""


def word_repair_prompt(*, payload: str, draft: str, condition: str, role: str) -> str:
    current_words = word_count(draft)
    context_block = ""
    if current_words > FINAL_MAX_WORDS:
        repair_instruction = (
            f"The draft is {current_words} words, which is too long for the target band. "
            f"Cut at least {max(300, current_words - 3150)} words if possible. Target 3,050-3,200 words. "
            "Do not add new sections. Compress paragraphs. Remove repetition, throat-clearing, generic explanations, and secondary examples."
        )
    elif current_words < FINAL_MIN_WORDS:
        context_block = f"""Frozen benchmark packet:

{payload}

"""
        repair_instruction = (
            f"The draft is {current_words} words, which is too short. "
            "Expand substantively to at least 2,900 words and target about 3,100 words. "
            "Use this section budget: executive thesis 250 words; current-market setup 350; architecture 500; "
            "benchmark and peer-comparison layer 450; portfolio/funding/settlement layer 450; decision policy 400; "
            "controls/audit/model-risk layer 450; implementation roadmap 300. "
            "Do not stop early. Add concrete finance-native detail from the frozen packet rather than generic filler."
        )
    else:
        repair_instruction = "The draft is already in band; polish lightly while staying in band."
    return f"""{context_block}Condition: {condition}
Role: {role}

The draft below is outside the target final word band of 2,800-3,400 words. Automation accepts a hard tolerance ceiling of 3,600 words for approximate parity.
{repair_instruction}
Surgically edit the draft into the strongest possible client-shareable final report within 2,800-3,400 words if possible, and never over 3,600 words.
Preserve source IDs already present, technical specificity, no-browse discipline, and no-investment-advice constraints.
Do not introduce facts outside the frozen packet. Do not add unsupported source claims. Do not exceed 3,600 words.
If you must choose, prefer concise technical density over breadth.
Output Markdown only.

Draft:
{draft}
"""


def word_append_prompt(*, payload: str, draft: str, condition: str, role: str) -> str:
    current_words = word_count(draft)
    needed = max(650, FINAL_MIN_WORDS - current_words + 250)
    return f"""Frozen benchmark packet:

{payload}

Condition: {condition}
Role: {role}

The current final draft is {current_words} words, below the minimum comparable length.
Write ONLY an expansion addendum of about {needed}-{needed + 250} words that can be appended to the draft.

The addendum must add concrete finance-native depth, not filler. Cover:
- current market regime implications from the source pack,
- execution benchmark conflicts,
- portfolio/funding/settlement constraints,
- controls/audit/model-risk implications.

Use source IDs inline. Do not browse. Do not recommend trades. Do not repeat the whole report.
Output Markdown only.

Current final draft:
{draft}
"""


def final_validity_repair_prompt(
    *,
    payload: str,
    draft: str,
    condition: str,
    role: str,
    report: dict[str, Any],
) -> str:
    return f"""Frozen benchmark packet:

{payload}

Condition: {condition}
Role: {role}

The current final artifact failed deterministic validity checks before judging.

Validity report:
```json
{json.dumps(report, indent=2, sort_keys=False)}
```

Repair only the flagged issues. The repaired final must:
- be complete and end cleanly,
- stay within 2,800-3,400 words if possible and never over 3,600,
- include required disclaimers: no investment advice and no live execution/routing claim,
- include implementation roadmap and success metrics,
- preserve source IDs and use only the frozen source pack,
- remove internal benchmark/process residue such as STATE_OBJECT, mission packet, Document X/Y, or turn labels,
- preserve technical specificity rather than adding filler.

Output the complete repaired final report in Markdown only.

Draft:
{draft}
"""


def maybe_repair_final_validity(
    *,
    run_root: Path,
    hashes: dict[str, str],
    payload: str,
    provider: str,
    condition: str,
    role: str,
    turn: int,
    text: str,
    artifact_path: Path,
    timeout: int,
) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    traces: list[dict[str, Any]] = []
    report = final_artifact_validity_report(text)
    if report["valid"]:
        return text, traces, report
    for attempt in range(1, 3):
        system = markdown_system("Final deterministic validity repair")
        user = final_validity_repair_prompt(
            payload=payload,
            draft=text,
            condition=condition,
            role=role,
            report=report,
        )
        repaired, trace = call_and_save(
            run_root=run_root,
            hashes=hashes,
            provider=provider,
            system=system,
            user=user,
            max_tokens=9000,
            timeout=timeout,
            call_type="final_validity_repair",
            condition=condition,
            role=role,
            turn=turn,
            prompt_rel=f"{condition}/turn_{turn}_final_validity_repair_attempt_{attempt}",
            trace_rel=f"{condition}/turn_{turn}_final_validity_repair_attempt_{attempt}",
            artifact_path=artifact_path,
            extra={"original_validity_report": report, "validity_repair_attempt": attempt},
        )
        text = repaired
        report = final_artifact_validity_report(text)
        trace["repaired_validity_report"] = report
        traces.append(trace)
        if report["valid"]:
            return text, traces, report
    if not report["valid"]:
        raise RuntimeError(
            f"final_artifact_invalid condition={condition} turn={turn} flags={report['flags']}"
        )
    return text, traces, report


def finalize_final_artifact(
    *,
    run_root: Path,
    hashes: dict[str, str],
    payload: str,
    provider: str,
    condition: str,
    role: str,
    turn: int,
    text: str,
    artifact_path: Path,
    timeout: int,
) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    traces: list[dict[str, Any]] = []
    text, word_traces = maybe_repair_final_word_count(
        run_root=run_root,
        hashes=hashes,
        payload=payload,
        provider=provider,
        condition=condition,
        role=role,
        turn=turn,
        text=text,
        artifact_path=artifact_path,
        timeout=timeout,
    )
    traces.extend(word_traces)
    text, validity_traces, report = maybe_repair_final_validity(
        run_root=run_root,
        hashes=hashes,
        payload=payload,
        provider=provider,
        condition=condition,
        role=role,
        turn=turn,
        text=text,
        artifact_path=artifact_path,
        timeout=timeout,
    )
    traces.extend(validity_traces)
    if not report["word_count_in_band"]:
        text, second_word_traces = maybe_repair_final_word_count(
            run_root=run_root,
            hashes=hashes,
            payload=payload,
            provider=provider,
            condition=condition,
            role=role,
            turn=turn,
            text=text,
            artifact_path=artifact_path,
            timeout=timeout,
        )
        traces.extend(second_word_traces)
        report = final_artifact_validity_report(text)
    if not report["valid"]:
        raise RuntimeError(
            f"final_artifact_invalid condition={condition} turn={turn} flags={report['flags']}"
        )
    return text, traces, report


def selector_prompt(*, payload: str, state_object: dict[str, Any], turn5: str, turn6: str) -> str:
    return f"""Frozen benchmark packet:

{payload}

Canonical STATE_OBJECT:

```json
{state_object_text(state_object)}
```

Candidate Turn 5 final:
{turn5}

Candidate Turn 6 final:
{turn6}

Compare Turn 5 and Turn 6 against the brief, source pack, rubric, and word-count band.
Return strict JSON only with this schema:
{{
  "selected_artifact": "turn_5" or "turn_6" or "surgical_synthesis_required",
  "turn_6_degraded": true or false,
  "rationale": "short explanation",
  "strongest_turn_5_elements": ["..."],
  "strongest_turn_6_elements": ["..."],
  "must_preserve_in_synthesis": ["..."],
  "unsupported_claim_flags": ["..."],
  "word_count_notes": "..."
}}
Select surgical_synthesis_required if the strongest Holo result requires merging non-overlapping valid strengths or preserving a ledger insight that one candidate dropped.
"""


def synthesis_prompt(
    *,
    payload: str,
    state_object: dict[str, Any],
    turn5: str,
    turn6: str,
    selector: dict[str, Any],
) -> str:
    return f"""Frozen benchmark packet:

{payload}

Canonical STATE_OBJECT:

```json
{state_object_text(state_object)}
```

HoloGov selector decision:

```json
{json.dumps(selector, indent=2, sort_keys=False)}
```

Candidate Turn 5 final:
{turn5}

Candidate Turn 6 final:
{turn6}

Produce the final Holo synthesis artifact in Markdown.

Rules:
- Use only the frozen source pack and the candidate artifacts.
- Do not browse.
- Preserve STATE_OBJECT.PRESERVED_INSIGHT_LEDGER items unless explicitly rejected with source-grounded rationale.
- Merge the strongest valid elements from Turn 5 and Turn 6.
- Remove process residue, analyst labels, mission-packet language, and internal benchmark commentary.
- Include the required no-investment-advice and no-live-execution disclaimers.
- Stay within 2,800-3,400 words if possible and never over 3,600 words.
- End cleanly.
"""


def judge_prompt(*, payload: str, judge_id: str, pair_id: str, doc_x: str, doc_y: str) -> str:
    rubric = read_json(PACKET_DIR / "judge_rubric_8criteria.json")
    criteria_ids = [item["id"] for item in rubric["criteria"]]
    return f"""Frozen judge packet:

{payload}

Pair ID: {pair_id}
Judge ID: {judge_id}

Document X:
{doc_x}

Document Y:
{doc_y}

You are blind. You are not told which document is Holo or Solo and you are not told the generating model identities.

Return strict JSON only, no markdown, no code fence. Required schema:
{{
  "judge_id": "{judge_id}",
  "blindness_confirmation": "I was not told which document is Holo or Solo and was not told generating model identities.",
  "document_x": {{
    "summary_description": "...",
    "criterion_scores": [
      {{"criterion_id": "{criteria_ids[0]}", "score_1_5": 1-5, "score_1_10": 1-10, "notes": "..."}}
    ],
    "top_3_strengths": ["...", "...", "..."],
    "top_3_weaknesses_or_hidden_failures": ["...", "...", "..."],
    "unsupported_or_stale_claims": ["..."],
    "math_or_benchmark_logic_issues": ["..."],
    "source_grounding_notes": "..."
  }},
  "document_y": {{
    "summary_description": "...",
    "criterion_scores": [
      {{"criterion_id": "{criteria_ids[0]}", "score_1_5": 1-5, "score_1_10": 1-10, "notes": "..."}}
    ],
    "top_3_strengths": ["...", "...", "..."],
    "top_3_weaknesses_or_hidden_failures": ["...", "...", "..."],
    "unsupported_or_stale_claims": ["..."],
    "math_or_benchmark_logic_issues": ["..."],
    "source_grounding_notes": "..."
  }},
  "comparative_verdict": {{
    "stronger_document": "document_x" or "document_y" or "tie",
    "margin_of_difference": "short phrase",
    "why_the_stronger_document_won": "...",
    "where_the_weaker_document_was_closest": "...",
    "judge_confidence_1_5": 1-5
  }},
  "validation_flags": []
}}

You must include exactly these criterion_ids for both documents: {criteria_ids}
"""


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    candidates = [stripped]
    first = stripped.find("{")
    last = stripped.rfind("}")
    if first >= 0 and last > first:
        candidates.append(stripped[first : last + 1])
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue
    raise ValueError("no_valid_json_object")


def weighted_score(doc: dict[str, Any], rubric: dict[str, Any]) -> float:
    scores = doc.get("criterion_scores", [])
    by_id = {item.get("criterion_id"): item for item in scores if isinstance(item, dict)}
    total = sum(float(item["weight"]) for item in rubric["criteria"])
    value = 0.0
    for item in rubric["criteria"]:
        score = float(by_id[item["id"]]["score_1_10"])
        value += score * float(item["weight"])
    return round(value / total, 3)


def ensure_judge_score_shape(score: dict[str, Any]) -> None:
    for doc_key in ["document_x", "document_y"]:
        doc = score.get(doc_key)
        if not isinstance(doc, dict):
            score[doc_key] = {"criterion_scores": []}
        score[doc_key].setdefault("criterion_scores", [])
    score.setdefault("comparative_verdict", {})
    score.setdefault("validation_flags", [])


def validate_judge_score(score: dict[str, Any], rubric: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    ensure_judge_score_shape(score)
    criteria = [item["id"] for item in rubric["criteria"]]
    for doc_key in ["document_x", "document_y"]:
        doc = score.get(doc_key) or {}
        by_id = {item.get("criterion_id"): item for item in doc.get("criterion_scores", []) if isinstance(item, dict)}
        missing = [cid for cid in criteria if cid not in by_id]
        extra = [cid for cid in by_id if cid not in criteria]
        if missing:
            flags.append(f"{doc_key}_missing_criteria:{missing}")
        if extra:
            flags.append(f"{doc_key}_extra_criteria:{extra}")
        for cid in criteria:
            if cid not in by_id:
                continue
            item = by_id[cid]
            try:
                s5 = float(item["score_1_5"])
                s10 = float(item["score_1_10"])
            except Exception:
                flags.append(f"{doc_key}.{cid}_non_numeric_score")
                continue
            if not (1 <= s5 <= 5):
                flags.append(f"{doc_key}.{cid}_score_1_5_out_of_range")
            if not (1 <= s10 <= 10):
                flags.append(f"{doc_key}.{cid}_score_1_10_out_of_range")
            if not str(item.get("notes", "")).strip():
                flags.append(f"{doc_key}.{cid}_missing_notes")
    if not flags:
        score["document_x"]["weighted_score_1_10"] = weighted_score(score["document_x"], rubric)
        score["document_y"]["weighted_score_1_10"] = weighted_score(score["document_y"], rubric)
        flags.extend(score_verdict_consistency_flags(score))
    return flags


def call_and_save(
    *,
    run_root: Path,
    hashes: dict[str, str],
    provider: str,
    system: str,
    user: str,
    max_tokens: int,
    timeout: int,
    call_type: str,
    condition: str,
    role: str,
    turn: int | None,
    prompt_rel: str,
    trace_rel: str,
    artifact_path: Path | None,
    extra: dict[str, Any] | None = None,
) -> tuple[str, dict[str, Any]]:
    prompt_card_path = save_prompt_card(
        run_root,
        rel=prompt_rel,
        system=system,
        user=user,
        provider=provider,
        model=PROVIDERS[provider]["model"],
        call_type=call_type,
    )
    result = call_provider(provider, system=system, user=user, max_tokens=max_tokens, timeout=timeout)
    text = result["text"].strip() + "\n"
    trace = save_call(
        run_root,
        trace_rel=trace_rel,
        artifact_path=artifact_path,
        artifact_text=text,
        prompt_card_path=prompt_card_path,
        call_type=call_type,
        condition=condition,
        provider=provider,
        role=role,
        turn=turn,
        result=result,
        hashes=hashes,
        extra=extra,
    )
    return text, trace


def load_trace(path: Path) -> dict[str, Any]:
    return read_json(path)


def existing_artifact_and_trace(
    *,
    run_root: Path,
    artifact_path: Path,
    trace_rel: str,
) -> tuple[str, dict[str, Any]] | None:
    trace_path = run_root / "traces" / f"{trace_rel}.json"
    if artifact_path.exists() and trace_path.exists():
        return read_text(artifact_path), load_trace(trace_path)
    return None


def existing_condition(
    *,
    run_root: Path,
    condition: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]] | None:
    manifest_path = run_root / "condition_manifests" / f"{condition}.json"
    if not manifest_path.exists():
        return None
    result = read_json(manifest_path)
    if result.get("word_count_in_band") is False:
        return None
    validity = result.get("artifact_validity_report")
    if not validity or validity.get("valid") is not True:
        return None
    traces = [read_json(path) for path in sorted((run_root / "traces" / condition).glob("*.json"))]
    return result, traces


def maybe_repair_final_word_count(
    *,
    run_root: Path,
    hashes: dict[str, str],
    payload: str,
    provider: str,
    condition: str,
    role: str,
    turn: int,
    text: str,
    artifact_path: Path,
    timeout: int,
) -> tuple[str, list[dict[str, Any]]]:
    traces: list[dict[str, Any]] = []
    for attempt in range(1, 4):
        count = word_count(text)
        if FINAL_MIN_WORDS <= count <= FINAL_MAX_WORDS:
            return text, traces
        system = markdown_system("Final word-count repair")
        user = word_repair_prompt(payload=payload, draft=text, condition=condition, role=role)
        repaired, trace = call_and_save(
            run_root=run_root,
            hashes=hashes,
            provider=provider,
            system=system,
            user=user,
            max_tokens=5200 if word_count(text) > FINAL_MAX_WORDS else 9000,
            timeout=timeout,
            call_type="word_count_repair",
            condition=condition,
            role=role,
            turn=turn,
            prompt_rel=f"{condition}/turn_{turn}_word_count_repair_attempt_{attempt}",
            trace_rel=f"{condition}/turn_{turn}_word_count_repair_attempt_{attempt}",
            artifact_path=artifact_path,
            extra={"original_word_count": count, "repair_attempt": attempt},
        )
        trace["repaired_word_count"] = word_count(repaired)
        traces.append(trace)
        text = repaired
    final_count = word_count(text)
    if final_count < FINAL_MIN_WORDS:
        system = markdown_system("Final word-count append expansion")
        user = word_append_prompt(payload=payload, draft=text, condition=condition, role=role)
        prompt_card_path = save_prompt_card(
            run_root,
            rel=f"{condition}/turn_{turn}_word_count_append_expansion",
            system=system,
            user=user,
            provider=provider,
            model=PROVIDERS[provider]["model"],
            call_type="word_count_append_expansion",
        )
        result = call_provider(provider, system=system, user=user, max_tokens=5000, timeout=timeout)
        append_text = result["text"].strip() + "\n"
        append_path = run_root / "artifacts" / condition / f"turn_{turn}_word_count_append.md"
        combined = text.strip() + "\n\n" + append_text
        write_text(append_path, append_text)
        write_text(artifact_path, combined)
        trace = save_call(
            run_root,
            trace_rel=f"{condition}/turn_{turn}_word_count_append_expansion",
            artifact_path=append_path,
            artifact_text=append_text,
            prompt_card_path=prompt_card_path,
            call_type="word_count_append_expansion",
            condition=condition,
            provider=provider,
            role=role,
            turn=turn,
            result=result,
            hashes=hashes,
            extra={
                "original_word_count": final_count,
                "append_word_count": word_count(append_text),
                "combined_word_count": word_count(combined),
                "combined_artifact_path": str(artifact_path),
            },
        )
        traces.append(trace)
        text = combined
        final_count = word_count(text)
    if not (FINAL_MIN_WORDS <= final_count <= FINAL_MAX_WORDS):
        raise RuntimeError(
            f"final_word_count_out_of_band condition={condition} turn={turn} words={final_count}"
        )
    return text, traces


def write_manifest(run_root: Path, payload: dict[str, Any]) -> None:
    write_json(run_root / "run_manifest.json", payload)


def run_solo_condition(
    *,
    run_root: Path,
    hashes: dict[str, str],
    payload: str,
    role_flow: dict[str, Any],
    condition: str,
    provider_model_name: str,
    timeout: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    cached_condition = existing_condition(run_root=run_root, condition=condition)
    if cached_condition:
        return cached_condition
    provider, _model = provider_model(provider_model_name)
    previous: str | None = None
    traces: list[dict[str, Any]] = []
    final_text = ""
    final_path = run_root / "artifacts" / condition / "turn_6.md"
    for role_item in role_flow["turns"]:
        turn = int(role_item["turn"])
        system = markdown_system(role_item["role"])
        user = solo_prompt(
            payload=payload,
            condition=condition,
            provider_model_name=provider_model_name,
            turn=turn,
            role_item=role_item,
            previous_text=previous,
        )
        max_tokens = 7000 if turn >= 5 else 5200
        artifact_path = run_root / "artifacts" / condition / f"turn_{turn}.md"
        cached = existing_artifact_and_trace(
            run_root=run_root,
            artifact_path=artifact_path,
            trace_rel=f"{condition}/turn_{turn}",
        )
        if cached:
            text, trace = cached
            traces.append(trace)
            previous = text
            if turn == 6:
                final_text = text
            continue
        text, trace = call_and_save(
            run_root=run_root,
            hashes=hashes,
            provider=provider,
            system=system,
            user=user,
            max_tokens=max_tokens,
            timeout=timeout,
            call_type="solo_turn",
            condition=condition,
            role=role_item["role"],
            turn=turn,
            prompt_rel=f"{condition}/turn_{turn}",
            trace_rel=f"{condition}/turn_{turn}",
            artifact_path=artifact_path,
        )
        traces.append(trace)
        previous = text
        if turn == 6:
            final_text = text
    final_text, repair_traces, validity_report = finalize_final_artifact(
        run_root=run_root,
        hashes=hashes,
        payload=payload,
        provider=provider,
        condition=condition,
        role="Solo final report",
        turn=6,
        text=final_text,
        artifact_path=final_path,
        timeout=timeout,
    )
    traces.extend(repair_traces)
    result = {
        "condition": condition,
        "provider_model": provider_model_name,
        "final_artifact_path": str(final_path),
        "final_sha256": sha_file(final_path),
        "final_word_count": word_count(final_text),
        "word_count_in_band": FINAL_MIN_WORDS <= word_count(final_text) <= FINAL_MAX_WORDS,
        "artifact_validity_report": validity_report,
        "turn_count": 6,
    }
    write_json(run_root / "condition_manifests" / f"{condition}.json", result)
    return result, traces


def run_holo_condition(
    *,
    run_root: Path,
    hashes: dict[str, str],
    payload: str,
    role_flow: dict[str, Any],
    report_brief: dict[str, Any],
    timeout: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    condition = "holo_frontier_gov"
    cached_condition = existing_condition(run_root=run_root, condition=condition)
    if cached_condition:
        return cached_condition
    previous_text: str | None = None
    previous_artifacts: list[dict[str, str]] = []
    traces: list[dict[str, Any]] = []
    turn_texts: dict[int, str] = {}
    state_objects: dict[int, dict[str, Any]] = {}
    gov_provider_model = report_brief["holo_turn_design"]["governor_model"]
    gov_provider, _ = provider_model(gov_provider_model)
    for role_item in role_flow["turns"]:
        turn = int(role_item["turn"])
        analyst_provider, _ = provider_model(role_item["provider_model"])
        state_object = build_state_object(
            report_brief=report_brief,
            routing_config={
                "routing_config_id": role_flow.get("routing_config_id", "unknown"),
                "routing_config_label": role_flow.get("routing_config_label"),
            },
            turn=turn,
            role_item=role_item,
            previous_artifacts=previous_artifacts,
        )
        state_objects[turn] = state_object
        state_path = run_root / "state_objects" / condition / f"turn_{turn}_state_object.json"
        write_json(state_path, state_object)
        mission_text: str | None = None
        mission_path: Path | None = None
        if turn > 1:
            system = gov_system()
            user = gov_prompt(
                payload=payload,
                turn=turn,
                role_item=role_item,
                previous_artifacts=previous_artifacts,
                state_object=state_object,
            )
            mission_path = run_root / "mission_packets" / condition / f"turn_{turn}_mission.md"
            cached_mission = existing_artifact_and_trace(
                run_root=run_root,
                artifact_path=mission_path,
                trace_rel=f"{condition}/gov_turn_{turn}",
            )
            if cached_mission:
                mission_text, trace = cached_mission
                traces.append(trace)
            else:
                mission_text, trace = call_and_save(
                    run_root=run_root,
                    hashes=hashes,
                    provider=gov_provider,
                    system=system,
                    user=user,
                    max_tokens=2600,
                    timeout=timeout,
                    call_type="holo_gov_mission_packet",
                    condition=condition,
                    role="HoloGov mission packet",
                    turn=turn,
                    prompt_rel=f"{condition}/gov_turn_{turn}",
                    trace_rel=f"{condition}/gov_turn_{turn}",
                    artifact_path=mission_path,
                )
                traces.append(trace)
        system = markdown_system(role_item["role"])
        user = holo_prompt(
            payload=payload,
            turn=turn,
            role_item=role_item,
            previous_artifacts=previous_artifacts,
            state_object=state_object,
            mission=mission_text,
        )
        max_tokens = 7000 if turn >= 5 else 5200
        artifact_path = run_root / "artifacts" / condition / f"turn_{turn}.md"
        cached = existing_artifact_and_trace(
            run_root=run_root,
            artifact_path=artifact_path,
            trace_rel=f"{condition}/turn_{turn}",
        )
        if cached:
            text, trace = cached
            traces.append(trace)
            previous_text = text
            previous_artifacts.append(
                {
                    "turn": str(turn),
                    "role": role_item["role"],
                    "provider_model": role_item["provider_model"],
                    "path": str(artifact_path),
                    "text": text,
                }
            )
            turn_texts[turn] = text
            continue
        text, trace = call_and_save(
            run_root=run_root,
            hashes=hashes,
            provider=analyst_provider,
            system=system,
            user=user,
            max_tokens=max_tokens,
            timeout=timeout,
            call_type="holo_analyst_turn",
            condition=condition,
            role=role_item["role"],
            turn=turn,
            prompt_rel=f"{condition}/turn_{turn}",
            trace_rel=f"{condition}/turn_{turn}",
            artifact_path=artifact_path,
            extra={"mission_path": str(mission_path) if mission_path else None},
        )
        traces.append(trace)
        previous_text = text
        previous_artifacts.append(
            {
                "turn": str(turn),
                "role": role_item["role"],
                "provider_model": role_item["provider_model"],
                "path": str(artifact_path),
                "text": text,
            }
        )
        turn_texts[turn] = text

    for turn in [5, 6]:
        provider, _ = provider_model(role_flow["turns"][turn - 1]["provider_model"])
        repaired, repair_traces, _validity_report = finalize_final_artifact(
            run_root=run_root,
            hashes=hashes,
            payload=payload,
            provider=provider,
            condition=condition,
            role=role_flow["turns"][turn - 1]["role"],
            turn=turn,
            text=turn_texts[turn],
            artifact_path=run_root / "artifacts" / condition / f"turn_{turn}.md",
            timeout=timeout,
        )
        traces.extend(repair_traces)
        turn_texts[turn] = repaired

    selector_provider, _ = provider_model(gov_provider_model)
    system = selector_system()
    final_state_object = build_state_object(
        report_brief=report_brief,
        routing_config={
            "routing_config_id": role_flow.get("routing_config_id", "unknown"),
            "routing_config_label": role_flow.get("routing_config_label"),
        },
        turn=6,
        role_item=role_flow["turns"][-1],
        previous_artifacts=previous_artifacts,
    )
    write_json(run_root / "state_objects" / condition / "final_state_object.json", final_state_object)
    user = selector_prompt(payload=payload, state_object=final_state_object, turn5=turn_texts[5], turn6=turn_texts[6])
    selector_out_path = run_root / "final_selection" / f"{condition}_selector.json"
    final_path = run_root / "artifacts" / condition / "final_selected.md"
    selector_trace_path = run_root / "traces" / condition / "post_turn_6_selector.json"
    if selector_out_path.exists() and final_path.exists() and selector_trace_path.exists():
        selector_payload = read_json(selector_out_path)
        selected_turn_raw = selector_payload["selected_turn"]
        try:
            selected_turn = int(selected_turn_raw)
        except (TypeError, ValueError):
            selected_turn = str(selected_turn_raw)
        selector_trace = read_json(selector_trace_path)
        traces.append(selector_trace)
        final_validity_report = final_artifact_validity_report(read_text(final_path))
    else:
        selector_card = save_prompt_card(
            run_root,
            rel=f"{condition}/post_turn_6_selector",
            system=system,
            user=user,
            provider=selector_provider,
            model=PROVIDERS[selector_provider]["model"],
            call_type="post_turn_6_gov_selector",
        )
        selector_result = call_provider(selector_provider, system=system, user=user, max_tokens=1400, timeout=timeout)
        selector_text = selector_result["text"].strip()
        selector_json = extract_json_object(selector_text)
        selected = selector_json.get("selected_artifact")
        if selected not in {"turn_5", "turn_6", "surgical_synthesis_required"}:
            selected = "turn_6"
            selector_json["selected_artifact"] = selected
            selector_json.setdefault("validation_flags", []).append("invalid_selected_artifact_defaulted_turn_6")
        selected_turn: int | str = 5 if selected == "turn_5" else 6
        if selected == "surgical_synthesis_required":
            synth_system = synthesis_system()
            synth_user = synthesis_prompt(
                payload=payload,
                state_object=final_state_object,
                turn5=turn_texts[5],
                turn6=turn_texts[6],
                selector=selector_json,
            )
            synth_card = save_prompt_card(
                run_root,
                rel=f"{condition}/post_turn_6_synthesis",
                system=synth_system,
                user=synth_user,
                provider=selector_provider,
                model=PROVIDERS[selector_provider]["model"],
                call_type="post_turn_6_gov_synthesis",
            )
            synth_result = call_provider(selector_provider, system=synth_system, user=synth_user, max_tokens=9000, timeout=timeout)
            synth_text = synth_result["text"].strip() + "\n"
            write_text(final_path, synth_text)
            selected_turn = "surgical_synthesis"
            synthesis_trace = save_call(
                run_root,
                trace_rel=f"{condition}/post_turn_6_synthesis",
                artifact_path=final_path,
                artifact_text=synth_text,
                prompt_card_path=synth_card,
                call_type="post_turn_6_gov_synthesis",
                condition=condition,
                provider=selector_provider,
                role="HoloGov final synthesis",
                turn=None,
                result=synth_result,
                hashes=hashes,
            )
            traces.append(synthesis_trace)
        else:
            final_source = run_root / "artifacts" / condition / f"turn_{selected_turn}.md"
            write_text(final_path, read_text(final_source))
        final_text = read_text(final_path)
        final_text, final_validity_traces, final_validity_report = finalize_final_artifact(
            run_root=run_root,
            hashes=hashes,
            payload=payload,
            provider=selector_provider,
            condition=condition,
            role="HoloGov final selected artifact",
            turn=6,
            text=final_text,
            artifact_path=final_path,
            timeout=timeout,
        )
        traces.extend(final_validity_traces)
        selector_payload = {
            "selector_provider": selector_provider,
            "selector_model": PROVIDERS[selector_provider]["model"],
            "raw_output": selector_text,
            "parsed": selector_json,
            "selected_turn": selected_turn,
            "selected_artifact_path": str(final_path),
            "selected_artifact_validity_report": final_validity_report,
            "turn_5_path": str(run_root / "artifacts" / condition / "turn_5.md"),
            "turn_6_path": str(run_root / "artifacts" / condition / "turn_6.md"),
        }
        write_json(selector_out_path, selector_payload)
        selector_trace = save_call(
            run_root,
            trace_rel=f"{condition}/post_turn_6_selector",
            artifact_path=selector_out_path,
            artifact_text=json.dumps(selector_payload, indent=2),
            prompt_card_path=selector_card,
            call_type="post_turn_6_gov_selector",
            condition=condition,
            provider=selector_provider,
            role="HoloGov final selector",
            turn=None,
            result=selector_result,
            hashes=hashes,
        )
        traces.append(selector_trace)
    result = {
        "condition": condition,
        "final_artifact_path": str(final_path),
        "final_sha256": sha_file(final_path),
        "final_word_count": word_count(read_text(final_path)),
        "word_count_in_band": FINAL_MIN_WORDS <= word_count(read_text(final_path)) <= FINAL_MAX_WORDS,
        "artifact_validity_report": final_validity_report,
        "selected_turn": selected_turn,
        "selector_path": str(selector_out_path),
        "turn_count": 6,
    }
    write_json(run_root / "condition_manifests" / f"{condition}.json", result)
    return result, traces


def build_judge_packets(
    *,
    run_root: Path,
    run_id: str,
    condition_results: dict[str, dict[str, Any]],
    solo_conditions: dict[str, str],
) -> list[dict[str, Any]]:
    holo_text = read_text(Path(condition_results["holo_frontier_gov"]["final_artifact_path"]))
    packets: list[dict[str, Any]] = []
    anonymization = {"run_id": run_id, "pairs": []}
    source_pack = read_json(PACKET_DIR / "source_pack.json")
    report_brief = read_json(PACKET_DIR / "report_brief.json")
    rubric = read_json(PACKET_DIR / "judge_rubric_8criteria.json")
    for solo_condition in solo_conditions:
        solo_text = read_text(Path(condition_results[solo_condition]["final_artifact_path"]))
        pair_id = f"{run_id}_{solo_condition}_vs_holo_pair"
        flip = int(hashlib.sha256(pair_id.encode("utf-8")).hexdigest()[:2], 16) % 2 == 0
        if flip:
            doc_x, doc_y = holo_text, solo_text
            x_condition, y_condition = "holo_frontier_gov", solo_condition
        else:
            doc_x, doc_y = solo_text, holo_text
            x_condition, y_condition = solo_condition, "holo_frontier_gov"
        packet = {
            "judge_packet_id": pair_id,
            "blind": True,
            "benchmark_credit": False,
            "public_claim": False,
            "domain": report_brief["domain"],
            "brief": report_brief,
            "source_pack": source_pack,
            "rubric": rubric,
            "documents": {
                "document_x": {"anonymous_id": "Document X", "text": doc_x},
                "document_y": {"anonymous_id": "Document Y", "text": doc_y},
            },
        }
        write_json(run_root / "judge_packets" / f"{pair_id}.json", packet)
        anonymization["pairs"].append(
            {
                "judge_packet_id": pair_id,
                "document_x_condition": x_condition,
                "document_y_condition": y_condition,
            }
        )
        packets.append(packet)
    write_json(run_root / "sealed" / "anonymization_map.json", anonymization)
    return packets


def build_turn_judge_packets(
    *,
    run_root: Path,
    run_id: str,
    role_flow: dict[str, Any],
    solo_conditions: dict[str, str],
) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    anonymization = {"run_id": run_id, "pairs": []}
    source_pack = read_json(PACKET_DIR / "source_pack.json")
    report_brief = read_json(PACKET_DIR / "report_brief.json")
    rubric = read_json(PACKET_DIR / "judge_rubric_8criteria.json")
    for solo_condition in solo_conditions:
        for role_item in role_flow["turns"]:
            turn = int(role_item["turn"])
            solo_path = run_root / "artifacts" / solo_condition / f"turn_{turn}.md"
            holo_path = run_root / "artifacts" / "holo_frontier_gov" / f"turn_{turn}.md"
            if not solo_path.exists() or not holo_path.exists():
                continue
            solo_text = read_text(solo_path)
            holo_text = read_text(holo_path)
            pair_id = f"{run_id}_{solo_condition}_vs_holo_turn_{turn}_pair"
            flip = int(hashlib.sha256(pair_id.encode("utf-8")).hexdigest()[:2], 16) % 2 == 0
            if flip:
                doc_x, doc_y = holo_text, solo_text
                x_condition, y_condition = "holo_frontier_gov", solo_condition
            else:
                doc_x, doc_y = solo_text, holo_text
                x_condition, y_condition = solo_condition, "holo_frontier_gov"
            packet = {
                "judge_packet_id": pair_id,
                "packet_type": "turn_level_diagnostic",
                "blind": True,
                "benchmark_credit": False,
                "public_claim": False,
                "domain": report_brief["domain"],
                "turn": turn,
                "turn_role": role_item["role"],
                "turn_instruction": role_item["instruction"],
                "turn_scoring_note": (
                    "Score each document for this turn's assigned role and its contribution "
                    "to the artifact trajectory. Do not score early critique/repair turns as "
                    "if they must be final board-ready reports."
                ),
                "brief": report_brief,
                "source_pack": source_pack,
                "rubric": rubric,
                "documents": {
                    "document_x": {"anonymous_id": "Document X", "text": doc_x},
                    "document_y": {"anonymous_id": "Document Y", "text": doc_y},
                },
            }
            write_json(run_root / "turn_judge_packets" / f"{pair_id}.json", packet)
            anonymization["pairs"].append(
                {
                    "judge_packet_id": pair_id,
                    "turn": turn,
                    "document_x_condition": x_condition,
                    "document_y_condition": y_condition,
                }
            )
            packets.append(packet)
    write_json(run_root / "sealed" / "turn_anonymization_map.json", anonymization)
    return packets


def judge_pair(
    *,
    run_root: Path,
    hashes: dict[str, str],
    packet: dict[str, Any],
    judge: dict[str, Any],
    judge_payload_text: str,
    timeout: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    provider = judge["provider"]
    judge_id = judge["judge_id"]
    pair_id = packet["judge_packet_id"]
    score_path = run_root / "judge_scores" / pair_id / f"{judge_id}.json"
    trace_path = run_root / "traces" / "judges" / pair_id / f"{judge_id}.json"
    if score_path.exists() and trace_path.exists():
        return read_json(score_path), [read_json(trace_path)]

    system = judge_system(judge_id)
    user = judge_prompt(
        payload=judge_payload_text,
        judge_id=judge_id,
        pair_id=pair_id,
        doc_x=packet["documents"]["document_x"]["text"],
        doc_y=packet["documents"]["document_y"]["text"],
    )
    prompt_rel = f"judges/{pair_id}/{judge_id}"
    prompt_card_path = save_prompt_card(
        run_root,
        rel=prompt_rel,
        system=system,
        user=user,
        provider=provider,
        model=PROVIDERS[provider]["model"],
        call_type="frontier_blind_judge",
    )
    result = call_provider(provider, system=system, user=user, max_tokens=6500, timeout=timeout)
    raw_text = result["text"].strip()
    traces: list[dict[str, Any]] = []
    parse_repair_attempted = False
    try:
        parsed = extract_json_object(raw_text)
    except Exception:
        parse_repair_attempted = True
        repair_system = (
            "You repair malformed judge JSON. Return strict valid JSON only. "
            "Do not change intended scores except to make the schema valid."
        )
        repair_user = f"Repair this malformed judge output into the required JSON schema:\n\n{raw_text}"
        repair_card = save_prompt_card(
            run_root,
            rel=f"judges/{pair_id}/{judge_id}_json_repair",
            system=repair_system,
            user=repair_user,
            provider=provider,
            model=PROVIDERS[provider]["model"],
            call_type="frontier_blind_judge_json_repair",
        )
        repair_result = call_provider(provider, system=repair_system, user=repair_user, max_tokens=5000, timeout=timeout)
        raw_text = repair_result["text"].strip()
        parsed = extract_json_object(raw_text)
        repair_trace = save_call(
            run_root,
            trace_rel=f"judges/{pair_id}/{judge_id}_json_repair",
            artifact_path=None,
            artifact_text=raw_text,
            prompt_card_path=repair_card,
            call_type="frontier_blind_judge_json_repair",
            condition=pair_id,
            provider=provider,
            role="Judge JSON repair",
            turn=None,
            result=repair_result,
            hashes=hashes,
        )
        traces.append(repair_trace)

    rubric = read_json(PACKET_DIR / "judge_rubric_8criteria.json")
    ensure_judge_score_shape(parsed)
    validation_flags = validate_judge_score(parsed, rubric)
    parsed.setdefault("validation_flags", [])
    parsed["validation_flags"].extend(validation_flags)
    for doc_key in ["document_x", "document_y"]:
        if "weighted_score_1_10" in parsed[doc_key]:
            continue
        try:
            parsed[doc_key]["weighted_score_1_10"] = weighted_score(parsed[doc_key], rubric)
        except Exception:
            parsed[doc_key]["weighted_score_1_10"] = None
            parsed["validation_flags"].append(f"{doc_key}_weighted_score_unavailable")
    parsed["_harness"] = {
        "judge_packet_id": pair_id,
        "judge_provider": provider,
        "judge_model": PROVIDERS[provider]["model"],
        "parse_repair_attempted": parse_repair_attempted,
        "raw_output_sha256": sha_text(raw_text),
    }
    write_json(score_path, parsed)
    trace = save_call(
        run_root,
        trace_rel=f"judges/{pair_id}/{judge_id}",
        artifact_path=score_path,
        artifact_text=json.dumps(parsed, indent=2),
        prompt_card_path=prompt_card_path,
        call_type="frontier_blind_judge",
        condition=pair_id,
        provider=provider,
        role="Blind frontier judge",
        turn=None,
        result=result,
        hashes=hashes,
        extra={"validation_flags": validation_flags, "parse_repair_attempted": parse_repair_attempted},
    )
    traces.append(trace)
    return parsed, traces


def aggregate_scores(run_root: Path, packets: list[dict[str, Any]]) -> dict[str, Any]:
    anon = read_json(run_root / "sealed" / "anonymization_map.json")
    mapping = {item["judge_packet_id"]: item for item in anon["pairs"]}
    pair_summaries = []
    overall_holo_scores = []
    overall_solo_scores = []
    primary_overall_holo_scores = []
    primary_overall_solo_scores = []
    skipped_judge_rows = []
    rubric = read_json(PACKET_DIR / "judge_rubric_8criteria.json")
    criteria_ids = [item["id"] for item in rubric["criteria"]]
    criterion_acc: dict[str, list[float]] = {cid: [] for cid in criteria_ids}
    for packet in packets:
        pair_id = packet["judge_packet_id"]
        pair_map = mapping[pair_id]
        solo_condition = pair_map["document_x_condition"] if pair_map["document_x_condition"] != "holo_frontier_gov" else pair_map["document_y_condition"]
        solo_provider = solo_provider_for_condition(solo_condition)
        judge_rows = []
        holo_scores = []
        solo_scores = []
        primary_holo_scores = []
        primary_solo_scores = []
        for score_path in sorted((run_root / "judge_scores" / pair_id).glob("*.json")):
            score = read_json(score_path)
            x_condition = pair_map["document_x_condition"]
            y_condition = pair_map["document_y_condition"]
            judge_provider = score.get("_harness", {}).get("judge_provider")
            self_dna_excluded = bool(solo_provider and judge_provider == solo_provider)
            x_score_raw = score.get("document_x", {}).get("weighted_score_1_10")
            y_score_raw = score.get("document_y", {}).get("weighted_score_1_10")
            if x_score_raw is None or y_score_raw is None:
                skipped_judge_rows.append(
                    {
                        "pair_id": pair_id,
                        "judge_id": score.get("judge_id"),
                        "reason": "missing_weighted_score",
                        "validation_flags": score.get("validation_flags", []),
                    }
                )
                continue
            x_score = float(x_score_raw)
            y_score = float(y_score_raw)
            holo_score = x_score if x_condition == "holo_frontier_gov" else y_score
            solo_score = x_score if x_condition != "holo_frontier_gov" else y_score
            holo_scores.append(holo_score)
            solo_scores.append(solo_score)
            if not self_dna_excluded:
                primary_holo_scores.append(holo_score)
                primary_solo_scores.append(solo_score)
            for cid in criteria_ids:
                try:
                    x_item = next(item for item in score["document_x"]["criterion_scores"] if item["criterion_id"] == cid)
                    y_item = next(item for item in score["document_y"]["criterion_scores"] if item["criterion_id"] == cid)
                except StopIteration:
                    skipped_judge_rows.append(
                        {
                            "pair_id": pair_id,
                            "judge_id": score.get("judge_id"),
                            "criterion_id": cid,
                            "reason": "missing_criterion_score",
                            "validation_flags": score.get("validation_flags", []),
                        }
                    )
                    continue
                h_val = float(x_item["score_1_10"] if x_condition == "holo_frontier_gov" else y_item["score_1_10"])
                s_val = float(x_item["score_1_10"] if x_condition != "holo_frontier_gov" else y_item["score_1_10"])
                criterion_acc[cid].append(h_val - s_val)
            judge_rows.append(
                {
                    "judge_id": score.get("judge_id"),
                    "judge_provider": judge_provider,
                    "holo_score": holo_score,
                    "solo_score": solo_score,
                    "gap_holo_minus_solo": round(holo_score - solo_score, 3),
                    "stronger_document": score.get("comparative_verdict", {}).get("stronger_document"),
                    "validation_flags": score.get("validation_flags", []),
                    "primary_score_included": not self_dna_excluded,
                    "primary_exclusion_reason": "same_provider_as_solo_condition"
                    if self_dna_excluded
                    else "",
                }
            )
        pair_summary = {
            "pair_id": pair_id,
            "solo_condition": solo_condition,
            "holo_mean": round(statistics.mean(holo_scores), 3) if holo_scores else None,
            "solo_mean": round(statistics.mean(solo_scores), 3) if solo_scores else None,
            "gap_holo_minus_solo": round(statistics.mean(holo_scores) - statistics.mean(solo_scores), 3)
            if holo_scores and solo_scores
            else None,
            "primary_holo_mean": round(statistics.mean(primary_holo_scores), 3) if primary_holo_scores else None,
            "primary_solo_mean": round(statistics.mean(primary_solo_scores), 3) if primary_solo_scores else None,
            "primary_gap_holo_minus_solo": round(
                statistics.mean(primary_holo_scores) - statistics.mean(primary_solo_scores), 3
            )
            if primary_holo_scores and primary_solo_scores
            else None,
            "primary_judge_observations": len(primary_holo_scores),
            "primary_exclusion_rule": "exclude judge rows where judge_provider == solo_provider",
            "holo_scores": holo_scores,
            "solo_scores": solo_scores,
            "primary_holo_scores": primary_holo_scores,
            "primary_solo_scores": primary_solo_scores,
            "judge_rows": judge_rows,
        }
        pair_summaries.append(pair_summary)
        overall_holo_scores.extend(holo_scores)
        overall_solo_scores.extend(solo_scores)
        primary_overall_holo_scores.extend(primary_holo_scores)
        primary_overall_solo_scores.extend(primary_solo_scores)
    summary = {
        "status": "judging_complete",
        "benchmark_credit": False,
        "public_claim": False,
        "pair_summaries": pair_summaries,
        "skipped_judge_rows": skipped_judge_rows,
        "overall": {
            "holo_mean": round(statistics.mean(overall_holo_scores), 3) if overall_holo_scores else None,
            "solo_mean": round(statistics.mean(overall_solo_scores), 3) if overall_solo_scores else None,
            "gap_holo_minus_solo": round(statistics.mean(overall_holo_scores) - statistics.mean(overall_solo_scores), 3)
            if overall_holo_scores and overall_solo_scores
            else None,
            "judge_observations": len(overall_holo_scores),
        },
        "primary_no_self_dna": {
            "rule": "exclude judge rows where judge_provider == solo_provider",
            "holo_mean": round(statistics.mean(primary_overall_holo_scores), 3)
            if primary_overall_holo_scores
            else None,
            "solo_mean": round(statistics.mean(primary_overall_solo_scores), 3)
            if primary_overall_solo_scores
            else None,
            "gap_holo_minus_solo": round(
                statistics.mean(primary_overall_holo_scores) - statistics.mean(primary_overall_solo_scores), 3
            )
            if primary_overall_holo_scores and primary_overall_solo_scores
            else None,
            "judge_observations": len(primary_overall_holo_scores),
        },
        "criterion_gap_holo_minus_solo": {
            cid: round(statistics.mean(values), 3) if values else 0 for cid, values in criterion_acc.items()
        },
    }
    write_json(run_root / "judge_score_summary_all_pairs.json", summary)
    lines = [
        "# Finance Algo Execution Benchmark Summary",
        "",
        "Status: judging complete",
        "Benchmark credit: false",
        "Public claim: false",
        "",
        "## Overall",
        "",
        f"- Holo mean: {summary['overall']['holo_mean']}",
        f"- Solo mean: {summary['overall']['solo_mean']}",
        f"- Gap Holo minus Solo: {summary['overall']['gap_holo_minus_solo']}",
        f"- Judge observations: {summary['overall']['judge_observations']}",
        "",
        "## Primary No-Self-DNA Score",
        "",
        f"- Holo mean: {summary['primary_no_self_dna']['holo_mean']}",
        f"- Solo mean: {summary['primary_no_self_dna']['solo_mean']}",
        f"- Gap Holo minus Solo: {summary['primary_no_self_dna']['gap_holo_minus_solo']}",
        f"- Judge observations: {summary['primary_no_self_dna']['judge_observations']}",
        f"- Rule: {summary['primary_no_self_dna']['rule']}",
        "",
        "## Pair Summaries",
        "",
    ]
    for pair in pair_summaries:
        lines.extend(
            [
                f"### {pair['solo_condition']} vs Holo",
                "",
                f"- Holo mean: {pair['holo_mean']}",
                f"- Solo mean: {pair['solo_mean']}",
                f"- Gap: {pair['gap_holo_minus_solo']}",
                f"- Primary no-self-DNA gap: {pair['primary_gap_holo_minus_solo']}",
                f"- Primary judge observations: {pair['primary_judge_observations']}",
                "",
            ]
        )
    lines.extend(["## Criterion Gaps", ""])
    for cid, value in summary["criterion_gap_holo_minus_solo"].items():
        lines.append(f"- {cid}: {value}")
    write_text(run_root / "judge_score_summary_all_pairs.md", "\n".join(lines) + "\n")
    return summary


def run(args: argparse.Namespace) -> int:
    status = env_status()
    missing = [name for name, value in status.items() if value != "PRESENT"]
    if args.preflight:
        solo_condition_count = 1 if args.solo_condition else len(SOLO_CONDITIONS)
        base_role_flow = read_json(PACKET_DIR / "finance_algo_adversarial_role_flow.json")
        routing_config = load_routing_config(args.routing_config)
        role_flow = apply_holo_routing_config(base_role_flow, routing_config)
        judge_panel = read_json(PACKET_DIR / "judge_panel_frontier_blind.json")
        print(
            json.dumps(
                {
                    "status": "PREFLIGHT_PASS" if not missing else "PREFLIGHT_MISSING_ENV",
                    "provider_env": status,
                    "models": {p: cfg["model"] for p, cfg in PROVIDERS.items()},
                    "holo_architecture_mode": STATE_OBJECT_VERSION,
                    "solo_condition_scope": [args.solo_condition] if args.solo_condition else list(SOLO_CONDITIONS),
                    "turn_prompt_parity": turn_prompt_parity_contract(role_flow),
                    "parity_note": "Solo and Holo share the same base turn role/instruction; Holo additionally receives Gov Baton/state/artifacts.",
                    "planned_generation_calls_minimum": (solo_condition_count * 6) + 12,
                    "planned_judge_calls": solo_condition_count * len(judge_panel["judge_models"]),
                    "planned_turn_judge_packets": solo_condition_count * 6,
                    "turn_judging_default": "packets only; live scoring requires a future explicit flag",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0 if not missing else 2
    if missing:
        print(json.dumps({"status": "MISSING_ENV", "provider_env": status}, indent=2, sort_keys=True))
        return 2

    source_pack = read_json(PACKET_DIR / "source_pack.json")
    report_brief = read_json(PACKET_DIR / "report_brief.json")
    base_role_flow = read_json(PACKET_DIR / "finance_algo_adversarial_role_flow.json")
    routing_config = load_routing_config(args.routing_config)
    role_flow = apply_holo_routing_config(base_role_flow, routing_config)
    solo_conditions = (
        {args.solo_condition: SOLO_CONDITIONS[args.solo_condition]}
        if args.solo_condition
        else dict(SOLO_CONDITIONS)
    )
    judge_panel = read_json(PACKET_DIR / "judge_panel_frontier_blind.json")
    rubric = read_json(PACKET_DIR / "judge_rubric_8criteria.json")
    if len(role_flow["turns"]) != 6:
        raise RuntimeError("role_flow_must_have_6_turns")
    if len(judge_panel["judge_models"]) < 4:
        raise RuntimeError("judge_panel_must_have_at_least_4_judges_for_no_self_dna_primary_scoring")
    if sum(item["weight"] for item in rubric["criteria"]) != 100:
        raise RuntimeError("rubric_weights_must_sum_to_100")

    run_id = args.run_id or f"full_frontier_finance_algo_execution_{routing_config['routing_config_id']}_{utc_stamp()}"
    run_root = PACKET_DIR / "runs" / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    solo_payload = frozen_base_generation_payload()
    holo_payload = frozen_holo_generation_payload(role_flow=role_flow, routing_config=routing_config)
    judge_payload_text = frozen_judge_payload()
    hashes = packet_hashes()
    all_traces: list[dict[str, Any]] = []
    condition_results: dict[str, dict[str, Any]] = {}
    manifest: dict[str, Any] = {
        "run_id": run_id,
        "status": "running_generation",
        "created_at_utc": utc_iso(),
        "packet_dir": str(PACKET_DIR),
        "benchmark_credit": False,
        "public_claim": False,
        "provider_env": status,
        "models": {p: cfg["model"] for p, cfg in PROVIDERS.items()},
        "source_pack_id": source_pack["packet_id"],
        "routing_config_id": routing_config["routing_config_id"],
        "routing_config_label": routing_config.get("label"),
        "holo_analyst_rotation": routing_config["analyst_rotation"],
        "holo_governor_model": report_brief["holo_turn_design"]["governor_model"],
        "hashes": hashes,
        "conditions": [*solo_conditions.keys(), "holo_frontier_gov"],
        "solo_condition_scope": list(solo_conditions.keys()),
        "holo_architecture_mode": STATE_OBJECT_VERSION,
        "turn_prompt_parity": turn_prompt_parity_contract(role_flow),
        "parity_note": "Solo and Holo share the same base turn role/instruction; Holo additionally receives Gov Baton/state/artifacts.",
        "judge_panel": judge_panel["judge_panel_id"],
        "condition_results": condition_results,
        "notes": "Full one-domain frontier run. Non-public and benchmark_credit=false until inspected.",
    }
    write_manifest(run_root, manifest)
    try:
        for condition, model_name in solo_conditions.items():
            manifest["status"] = f"running_generation_{condition}"
            write_manifest(run_root, manifest)
            result, traces = run_solo_condition(
                run_root=run_root,
                hashes=hashes,
                payload=solo_payload,
                role_flow=role_flow,
                condition=condition,
                provider_model_name=model_name,
                timeout=args.timeout,
            )
            condition_results[condition] = result
            all_traces.extend(traces)
            manifest["condition_results"] = condition_results
            write_manifest(run_root, manifest)

        manifest["status"] = "running_generation_holo"
        write_manifest(run_root, manifest)
        holo_result, traces = run_holo_condition(
            run_root=run_root,
            hashes=hashes,
            payload=holo_payload,
            role_flow=role_flow,
            report_brief=report_brief,
            timeout=args.timeout,
        )
        condition_results["holo_frontier_gov"] = holo_result
        all_traces.extend(traces)
        manifest["condition_results"] = condition_results
        manifest["status"] = "generation_complete_building_judge_packets"
        write_manifest(run_root, manifest)

        packets = build_judge_packets(
            run_root=run_root,
            run_id=run_id,
            condition_results=condition_results,
            solo_conditions=solo_conditions,
        )
        manifest["judge_packets"] = [packet["judge_packet_id"] for packet in packets]
        turn_packets = build_turn_judge_packets(
            run_root=run_root,
            run_id=run_id,
            role_flow=role_flow,
            solo_conditions=solo_conditions,
        )
        manifest["turn_judge_packets"] = [packet["judge_packet_id"] for packet in turn_packets]
        manifest["turn_judge_packet_count"] = len(turn_packets)
        manifest["turn_judge_status"] = "packets_built_not_scored"
        manifest["status"] = "running_frontier_judges"
        write_manifest(run_root, manifest)

        judge_scores = []
        for packet in packets:
            for judge in judge_panel["judge_models"]:
                score, traces = judge_pair(
                    run_root=run_root,
                    hashes=hashes,
                    packet=packet,
                    judge=judge,
                    judge_payload_text=judge_payload_text,
                    timeout=args.timeout,
                )
                judge_scores.append(
                    {
                        "pair_id": packet["judge_packet_id"],
                        "judge_id": judge["judge_id"],
                        "validation_flags": score.get("validation_flags", []),
                    }
                )
                all_traces.extend(traces)
                manifest["judge_scores_completed"] = judge_scores
                write_manifest(run_root, manifest)

        summary = aggregate_scores(run_root, packets)
        manifest["status"] = "FULL_FRONTIER_FINANCE_E2E_COMPLETE"
        manifest["completed_at_utc"] = utc_iso()
        manifest["provider_call_count"] = len(all_traces)
        manifest["total_input_tokens"] = sum(int(t.get("input_tokens", 0)) for t in all_traces)
        manifest["total_output_tokens"] = sum(int(t.get("output_tokens", 0)) for t in all_traces)
        manifest["total_latency_ms"] = sum(int(t.get("latency_ms", 0)) for t in all_traces)
        manifest["judge_summary_path"] = str(run_root / "judge_score_summary_all_pairs.json")
        manifest["overall_gap_holo_minus_solo"] = summary["overall"]["gap_holo_minus_solo"]
        write_manifest(run_root, manifest)
        print(
            json.dumps(
                {
                    "status": manifest["status"],
                    "run_id": run_id,
                    "provider_call_count": manifest["provider_call_count"],
                    "total_input_tokens": manifest["total_input_tokens"],
                    "total_output_tokens": manifest["total_output_tokens"],
                    "total_latency_ms": manifest["total_latency_ms"],
                    "overall_gap_holo_minus_solo": manifest["overall_gap_holo_minus_solo"],
                    "run_manifest": str(run_root / "run_manifest.json"),
                    "judge_summary": manifest["judge_summary_path"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except Exception as exc:
        error_payload = {
            "status": "FULL_FRONTIER_FINANCE_E2E_ERROR",
            "run_id": run_id,
            "error_type": type(exc).__name__,
            "error_message_excerpt": excerpt(exc),
            "provider": getattr(exc, "provider", None),
            "http_status": getattr(exc, "http_status", None),
            "benchmark_credit": False,
            "public_claim": False,
            "condition_results": condition_results,
        }
        write_json(run_root / "run_error.json", error_payload)
        manifest["status"] = "FULL_FRONTIER_FINANCE_E2E_ERROR"
        manifest["error"] = error_payload
        write_manifest(run_root, manifest)
        print(json.dumps(error_payload, indent=2, sort_keys=True))
        return 3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--run-id")
    parser.add_argument("--timeout", type=int, default=360)
    parser.add_argument("--routing-config", default=None)
    parser.add_argument("--solo-condition", choices=sorted(SOLO_CONDITIONS), default=None)
    args = parser.parse_args()
    if not args.preflight and not args.run_live:
        print(
            json.dumps(
                {
                    "status": "LIVE_RUN_GUARD_REQUIRED",
                    "reason": "This command sends the frozen finance packet and generated artifacts to external model-provider APIs. Re-run with --run-live only from an approved local environment.",
                    "safe_commands": [
                        "python3 run_google_frontier_e2e.py --preflight",
                        "python3 run_google_frontier_e2e.py --no-provider-smoke",
                    ],
                    "live_command": "python3 run_google_frontier_e2e.py --run-live",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
