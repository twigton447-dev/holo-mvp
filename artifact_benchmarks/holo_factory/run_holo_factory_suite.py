from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request


FACTORY_DIR = Path(__file__).resolve().parent
BENCH_ROOT = FACTORY_DIR.parent
DOMAINS_ROOT = BENCH_ROOT / "domains"
DEFAULT_SPEC = FACTORY_DIR / "domain_specs" / "current_geopolitical_suite_v001.json"
SUITE_RUNS_ROOT = FACTORY_DIR / "suite_runs"
FINANCE_PACKET_DIR = BENCH_ROOT / "current_event_finance_algo_execution_20260618"
ROUTING_CONFIGS = FINANCE_PACKET_DIR / "holo_routing_configs.json"
SOLO_SWEEP = FINANCE_PACKET_DIR / "solo_model_sweep.json"
JUDGE_PANEL = FINANCE_PACKET_DIR / "judge_panel_frontier_blind.json"
LEADERBOARD_JUDGE_PANEL_ID = "d1_hb_hv_leaderboard_matrix_two_judge_v1"
LEADERBOARD_JUDGE_IDS = ("judge_frontier_01", "judge_frontier_03")

sys.path.insert(0, str(BENCH_ROOT / "harness"))
from proof_credit_rules import (  # noqa: E402
    annotate_judge_credit,
    generation_dna_from_provider_models,
    judge_visible_packet,
)


PROVIDER_ENV = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "xai": "XAI_API_KEY",
    "minimax": "MINIMAX_API_KEY",
}


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
    "minimax": {
        "model": "MiniMax-M2.5-highspeed",
        "api_key_env": "MINIMAX_API_KEY",
        "base_url": "https://api.minimax.io/v1",
        "base_url_env": "MINIMAX_BASE_URL",
    },
}


COHORT_DEFAULTS = {
    "frontier": {
        "cohort_id": "frontier_fixed_v1",
        "routing_config_id": "order_a_current",
        "solo_suite_id": "frontier_baseline",
        "holo_condition_id": "holo_frontier_fixed_v1",
        "claim_scope": "primary frontier v1 lane",
    },
    "mini": {
        "cohort_id": "mini_fixed_v1",
        "routing_config_id": "mini_order_a_openai_bookend",
        "solo_suite_id": "mini_baseline",
        "holo_condition_id": "holo_mini_fixed_v1",
        "claim_scope": "primary mini v1 lane",
    },
}


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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def excerpt(value: Any, limit: int = 700) -> str:
    return re.sub(r"\s+", " ", str(value)).strip()[:limit]


def provider_model(provider_model_name: str) -> tuple[str, str]:
    provider, model = provider_model_name.split(":", 1)
    return provider, model


def env_status() -> dict[str, str]:
    return {name: ("PRESENT" if os.getenv(name) else "MISSING") for name in PROVIDER_ENV.values()}


def base_url_for_provider(provider: str) -> str:
    cfg = PROVIDERS[provider]
    env_name = cfg.get("base_url_env")
    return os.getenv(env_name) if env_name and os.getenv(env_name) else cfg["base_url"]


def http_post_json(
    *,
    provider: str,
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib_request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib_request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return {"http_status": getattr(response, "status", None), "json": json.loads(raw) if raw else {}}
    except urllib_error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise ProviderCallError(provider, "HTTPError", excerpt(raw or exc.reason), http_status=exc.code) from exc
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
    model_override: str | None = None,
) -> dict[str, Any]:
    cfg = PROVIDERS[provider]
    model = model_override or cfg["model"]
    attempt = 0
    current_max_tokens = max_tokens
    last_out: dict[str, Any] | None = None
    while attempt < 2:
        started = time.monotonic()
        if provider == "anthropic":
            result = http_post_json(
                provider=provider,
                url=base_url_for_provider(provider).rstrip("/") + "/messages",
                headers={
                    "x-api-key": os.getenv(cfg["api_key_env"], ""),
                    "anthropic-version": "2023-06-01",
                },
                payload={
                    "model": model,
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
                    base_url_for_provider(provider).rstrip("/")
                    + f"/models/{model}:generateContent"
                    + "?key="
                    + os.getenv(cfg["api_key_env"], "")
                ),
                headers={},
                payload={
                    "contents": [{"parts": [{"text": "SYSTEM:\n" + system + "\n\nUSER:\n" + user}]}],
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": current_max_tokens},
                },
                timeout=timeout,
            )
            data = result["json"]
            candidates = data.get("candidates") or []
            parts: list[str] = []
            if candidates:
                for part in (candidates[0].get("content") or {}).get("parts") or []:
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
            payload: dict[str, Any] = {
                "model": model,
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
                url=base_url_for_provider(provider).rstrip("/") + "/chat/completions",
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
        current_max_tokens = min(current_max_tokens + 1800, 12000)
    raise ProviderCallError(provider, "EmptyVisibleText", f"{provider}:{model} returned empty visible text twice")


def load_suite_order(spec_path: Path) -> list[str]:
    suite = read_json(spec_path)
    return [item["domain_id"] for item in suite["domains"]]


def domain_path(domain_id: str, version: str = "v001") -> Path:
    return DOMAINS_ROOT / domain_id / version


def select_domain_ids(selectors: list[str], spec_path: Path) -> list[str]:
    available = load_suite_order(spec_path)
    if selectors == ["all"]:
        return available
    selected: list[str] = []
    for selector in selectors:
        if selector == "all":
            for domain_id in available:
                if domain_id not in selected:
                    selected.append(domain_id)
            continue
        if selector not in available:
            valid = ", ".join(available)
            raise RuntimeError(f"unknown_domain:{selector}; valid={valid}")
        if selector not in selected:
            selected.append(selector)
    return selected


def select_cohorts(selector: str) -> list[str]:
    if selector == "both":
        return ["frontier", "mini"]
    if selector not in COHORT_DEFAULTS:
        valid = ", ".join(["both", *COHORT_DEFAULTS])
        raise RuntimeError(f"unknown_cohort:{selector}; valid={valid}")
    return [selector]


def load_routing_config(routing_config_id: str) -> dict[str, Any]:
    suite = read_json(ROUTING_CONFIGS)
    for config in suite["routing_configs"]:
        if config["routing_config_id"] == routing_config_id:
            loaded = dict(config)
            loaded["_fixed_governor_model"] = suite.get("fixed_governor_model")
            return loaded
    valid = ", ".join(config["routing_config_id"] for config in suite["routing_configs"])
    raise RuntimeError(f"unknown_routing_config:{routing_config_id}; valid={valid}")


def governor_model_for_route(route: dict[str, Any]) -> str:
    model = route.get("governor_model") or route.get("_fixed_governor_model")
    if not model:
        raise RuntimeError(f"missing_governor_model_for_route:{route.get('routing_config_id')}")
    return model


def load_solo_suite(solo_suite_id: str) -> dict[str, str]:
    suites = read_json(SOLO_SWEEP)
    suite = suites.get("solo_suites", {}).get(solo_suite_id)
    if not suite:
        valid = ", ".join(sorted(suites.get("solo_suites", {})))
        raise RuntimeError(f"unknown_solo_suite:{solo_suite_id}; valid={valid}")
    return dict(suite["conditions"])


def load_judge_panel() -> dict[str, Any]:
    return read_json(JUDGE_PANEL)


def load_leaderboard_judge_panel() -> dict[str, Any]:
    panel = load_judge_panel()
    judges_by_id = {judge["judge_id"]: judge for judge in panel.get("judge_models", [])}
    missing = [judge_id for judge_id in LEADERBOARD_JUDGE_IDS if judge_id not in judges_by_id]
    if missing:
        raise RuntimeError(f"missing_leaderboard_judges:{','.join(missing)}")
    return {
        **panel,
        "judge_panel_id": LEADERBOARD_JUDGE_PANEL_ID,
        "source_judge_panel_id": panel.get("judge_panel_id"),
        "judge_count": len(LEADERBOARD_JUDGE_IDS),
        "judge_models": [judges_by_id[judge_id] for judge_id in LEADERBOARD_JUDGE_IDS],
        "score_packet_mode": "single_artifact_leaderboard",
        "score_label": "tier_champion_headline_two_judge",
        "active_leaderboard_matrix": True,
        "quarantined_from_headline": ["judge_frontier_04"],
        "supporting_audit_only": [
            judge_id
            for judge_id in judges_by_id
            if judge_id not in set(LEADERBOARD_JUDGE_IDS)
        ],
    }


def kit_paths(path: Path) -> dict[str, Path]:
    return {
        "brief": path / "brief.md",
        "source_pack": path / "source_pack.json",
        "role_flow": path / "role_flow.json",
        "gov_protocol": path / "gov_protocol.json",
        "hidden_failure_targets": path / "hidden_failure_targets.json",
        "rubric": path / "rubric.json",
        "judge_brief": path / "judge_brief.md",
        "claim_boundaries": path / "claim_boundaries.md",
        "packet_manifest": path / "packet_manifest.json",
        "hash_lock": path / "hash_lock.json",
    }


def verify_hash_lock(path: Path) -> dict[str, Any]:
    lock_path = path / "hash_lock.json"
    if not lock_path.exists():
        return {"ok": False, "failures": ["missing_hash_lock"], "files_checked": 0}
    lock = read_json(lock_path)
    failures: list[str] = []
    files_checked = 0
    for rel, expected in sorted(lock.get("files", {}).items()):
        file_path = path / rel
        if not file_path.exists():
            failures.append(f"missing_locked_file:{rel}")
            continue
        files_checked += 1
        got = sha_file(file_path)
        if got != expected:
            failures.append(f"hash_mismatch:{rel}:{expected[:12]}:{got[:12]}")
    return {
        "ok": not failures,
        "failures": failures,
        "files_checked": files_checked,
        "hash_lock_id": lock.get("hash_lock_id"),
        "status": lock.get("status"),
        "benchmark_credit": lock.get("benchmark_credit"),
    }


def validate_domain_kit(domain_id: str) -> dict[str, Any]:
    path = domain_path(domain_id)
    paths = kit_paths(path)
    failures: list[str] = []
    for label, file_path in paths.items():
        if not file_path.exists():
            failures.append(f"missing:{label}:{file_path.name}")
    if failures:
        return {"domain_id": domain_id, "path": str(path), "ok": False, "failures": failures}

    manifest = read_json(paths["packet_manifest"])
    source_pack = read_json(paths["source_pack"])
    role_flow = read_json(paths["role_flow"])
    gov_protocol = read_json(paths["gov_protocol"])
    rubric = read_json(paths["rubric"])
    hidden = read_json(paths["hidden_failure_targets"])
    hash_report = verify_hash_lock(path)

    if manifest.get("domain_id") != domain_id:
        failures.append("manifest_domain_id_mismatch")
    if manifest.get("status") != "frozen_candidate_not_benchmark_credit":
        failures.append(f"manifest_not_frozen_candidate:{manifest.get('status')}")
    if manifest.get("benchmark_credit") is not False:
        failures.append("manifest_benchmark_credit_not_false")
    if source_pack.get("internet_policy") != "Do not browse. Use only this packet.":
        failures.append("source_pack_internet_policy_not_locked_no_browse")
    if len(role_flow.get("turns", [])) != 6:
        failures.append("role_flow_not_six_turns")
    if not role_flow.get("same_base_turn_prompt_for_solo_and_holo"):
        failures.append("turn_prompt_parity_not_declared")
    if not gov_protocol.get("gov_is_fixed_for_session"):
        failures.append("gov_not_fixed_for_session")
    if len(rubric.get("criteria", [])) != 8:
        failures.append("rubric_not_8_criteria")
    if sum(item.get("weight", 0) for item in rubric.get("criteria", [])) != 100:
        failures.append("rubric_weights_not_100")
    if len(hidden.get("targets", [])) < 5:
        failures.append("too_few_hidden_failure_targets")
    if not hash_report["ok"]:
        failures.extend(hash_report["failures"])

    return {
        "domain_id": domain_id,
        "path": str(path),
        "ok": not failures,
        "failures": failures,
        "hash_lock": hash_report,
        "word_band": manifest.get("word_band"),
    }


def required_envs_for_plan(cohorts: list[str]) -> list[str]:
    judge_panel = load_leaderboard_judge_panel()
    providers: set[str] = set()
    for cohort in cohorts:
        defaults = COHORT_DEFAULTS[cohort]
        route = load_routing_config(defaults["routing_config_id"])
        solo_conditions = load_solo_suite(defaults["solo_suite_id"])
        for provider_model_name in route["analyst_rotation"]:
            providers.add(provider_model(provider_model_name)[0])
        providers.add(provider_model(governor_model_for_route(route))[0])
        for provider_model_name in solo_conditions.values():
            providers.add(provider_model(provider_model_name)[0])
    for judge in judge_panel["judge_models"]:
        providers.add(judge["provider"])
    return sorted(PROVIDER_ENV[provider] for provider in providers)


def build_cohort_plan(cohort: str) -> dict[str, Any]:
    defaults = COHORT_DEFAULTS[cohort]
    route = load_routing_config(defaults["routing_config_id"])
    solo_conditions = load_solo_suite(defaults["solo_suite_id"])
    return {
        "cohort": cohort,
        "cohort_id": defaults["cohort_id"],
        "claim_scope": defaults["claim_scope"],
        "routing_config_id": defaults["routing_config_id"],
        "routing_config_label": route.get("label"),
        "governor_model": governor_model_for_route(route),
        "analyst_rotation": route["analyst_rotation"],
        "holo_condition_id": defaults["holo_condition_id"],
        "solo_suite_id": defaults["solo_suite_id"],
        "solo_conditions": solo_conditions,
        "turn_budget": len(route["analyst_rotation"]),
    }


def turn_prompt_parity(role_flow: dict[str, Any], route: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for index, turn in enumerate(role_flow["turns"]):
        rows.append(
            {
                "turn": turn["turn"],
                "role": turn["role"],
                "turn_instruction_sha256": sha_text(turn["instruction"]),
                "same_base_turn_prompt_for_solo_and_holo": True,
                "holo_analyst_model": route["analyst_rotation"][index],
                "holo_extra_context": "Gov baton, repair ledger, rolling state, prior artifacts, and validity gates.",
            }
        )
    return rows


def flip(run_id: str, key: str) -> bool:
    digest = hashlib.sha256(f"{run_id}:{key}".encode("utf-8")).hexdigest()
    return int(digest[:2], 16) % 2 == 0


def source_id_tokens(source_pack: dict[str, Any]) -> list[str]:
    tokens: list[str] = []
    for entry in source_pack.get("source_entries", []):
        full_id = entry.get("id")
        if not full_id:
            continue
        tokens.append(f"[{full_id}]")
        tokens.append(f"[{full_id.split('_', 1)[0]}]")
    return sorted(set(tokens))


def source_ids_in_text(text: str) -> list[str]:
    matches = re.findall(r"[\[(](S\d+(?:_[A-Za-z0-9_]+)?)[\])]", text)
    return sorted({f"[{match}]" for match in matches})


def required_sections_present(text: str, required_sections: list[str]) -> dict[str, bool]:
    def normalize(value: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()

    lowered = normalize(text)
    return {section: normalize(section) in lowered for section in required_sections}


def clean_ending(text: str) -> bool:
    stripped = text.strip()
    stripped = re.sub(r"[*_~`]+$", "", stripped).strip()
    return bool(stripped) and stripped[-1] in ".!?)]\"'"


def validity_report(text: str, kit: dict[str, Any]) -> dict[str, Any]:
    manifest = kit["manifest"]
    gov_protocol = kit["gov_protocol"]
    source_pack = kit["source_pack"]
    word_band = gov_protocol.get("validity_gate", {}).get("word_band") or manifest.get("word_band") or {}
    min_words = int(word_band.get("min", 0))
    max_words = int(word_band.get("max", word_band.get("hard_max", 10**9)))
    required_sections = list(gov_protocol.get("validity_gate", {}).get("required_sections_must_be_present", []))
    required_disclaimer = gov_protocol.get("validity_gate", {}).get("required_disclaimer", "")
    sections = required_sections_present(text, required_sections)
    sources = source_ids_in_text(text)
    allowed_sources = set(source_id_tokens(source_pack))
    flags: list[str] = []
    wc = word_count(text)
    if min_words and not (min_words <= wc <= max_words):
        flags.append(f"word_count_out_of_band:{wc}")
    if not clean_ending(text):
        flags.append("unclean_ending")
    missing_sections = [section for section, present in sections.items() if not present]
    for section in missing_sections:
        flags.append(f"missing_required_section:{section}")
    if required_disclaimer and required_disclaimer.lower() not in text.lower():
        flags.append("missing_required_disclaimer")
    unknown_sources = sorted(set(sources) - allowed_sources)
    if unknown_sources:
        flags.append("unknown_source_ids:" + ",".join(unknown_sources))
    if not sources:
        flags.append("missing_source_ids")
    residue_terms = [
        "document x",
        "document y",
        "anonymization map",
        "benchmark_credit",
        "provider calls",
        "draft_not_frozen",
        "hologov mission packet",
        "previous draft state",
        "condition type:",
        "model slot:",
        "not benchmark credit",
        "to be continued",
    ]
    residue = [term for term in residue_terms if term in text.lower()]
    if residue:
        flags.append("internal_process_residue:" + ",".join(residue))
    return {
        "valid": not flags,
        "flags": flags,
        "word_count": wc,
        "word_count_in_band": bool(min_words and min_words <= wc <= max_words),
        "clean_ending": clean_ending(text),
        "required_sections_present": sections,
        "source_ids": sources,
    }


def load_kit(domain_id: str) -> dict[str, Any]:
    path = domain_path(domain_id)
    return {
        "domain_id": domain_id,
        "path": path,
        "brief": (path / "brief.md").read_text(encoding="utf-8"),
        "source_pack": read_json(path / "source_pack.json"),
        "role_flow": read_json(path / "role_flow.json"),
        "gov_protocol": read_json(path / "gov_protocol.json"),
        "hidden_failure_targets": read_json(path / "hidden_failure_targets.json"),
        "rubric": read_json(path / "rubric.json"),
        "judge_brief": (path / "judge_brief.md").read_text(encoding="utf-8"),
        "claim_boundaries": (path / "claim_boundaries.md").read_text(encoding="utf-8"),
        "manifest": read_json(path / "packet_manifest.json"),
        "hash_lock": read_json(path / "hash_lock.json"),
    }


def read_kit_dataset_and_exhibit_payload(kit: dict[str, Any]) -> dict[str, Any]:
    path = kit["path"]
    datasets = []
    for item in kit["source_pack"].get("datasets", []):
        rel = Path("datasets") / item["filename"]
        datasets.append(
            {
                "filename": item["filename"],
                "description": item.get("description", ""),
                "text": (path / rel).read_text(encoding="utf-8") if (path / rel).exists() else "",
            }
        )
    exhibits = []
    for item in kit["source_pack"].get("exhibits", []):
        rel = Path("exhibits") / item["filename"]
        exhibits.append(
            {
                "filename": item["filename"],
                "title": item.get("title", ""),
                "text": (path / rel).read_text(encoding="utf-8") if (path / rel).exists() else "",
            }
        )
    return {"datasets": datasets, "exhibits": exhibits}


INTERNAL_PACKET_KEYS = {"status", "benchmark_credit", "public_claim"}


def scrub_internal_packet_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: scrub_internal_packet_json(item) for key, item in value.items() if key not in INTERNAL_PACKET_KEYS}
    if isinstance(value, list):
        return [scrub_internal_packet_json(item) for item in value]
    if isinstance(value, str):
        return value.replace("draft_not_frozen", "").replace("benchmark_credit", "")
    return value


def scrub_internal_packet_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        lower = line.lower()
        if lower.strip().startswith("status:"):
            continue
        if "draft_not_frozen" in lower or "benchmark_credit" in lower:
            continue
        if "holo" in lower or "gov" in lower:
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def frozen_packet_payload(kit: dict[str, Any], cohort_plan: dict[str, Any], *, mode: str = "holo") -> str:
    if mode == "solo":
        gate = kit["gov_protocol"]["validity_gate"]
        payload = {
            "packet_manifest": scrub_internal_packet_json(kit["manifest"]),
            "hash_lock_id": kit["hash_lock"].get("hash_lock_id"),
            "brief_md": scrub_internal_packet_text(kit["brief"]),
            "source_pack": scrub_internal_packet_json(kit["source_pack"]),
            "datasets_and_exhibits": read_kit_dataset_and_exhibit_payload(kit),
            "role_flow": kit["role_flow"],
            "required_sections": gate.get("required_sections_must_be_present", []),
            "required_disclaimer": gate.get("required_disclaimer", ""),
            "word_band": gate.get("word_band", {}),
            "hidden_failure_targets": kit["hidden_failure_targets"],
            "rubric": scrub_internal_packet_json(kit["rubric"]),
        }
        return json.dumps(payload, indent=2, sort_keys=False)

    payload = {
        "packet_manifest": kit["manifest"],
        "hash_lock_id": kit["hash_lock"].get("hash_lock_id"),
        "cohort_plan": cohort_plan,
        "brief_md": kit["brief"],
        "source_pack": kit["source_pack"],
        "datasets_and_exhibits": read_kit_dataset_and_exhibit_payload(kit),
        "role_flow": kit["role_flow"],
        "gov_protocol": kit["gov_protocol"],
        "hidden_failure_targets": kit["hidden_failure_targets"],
        "rubric": kit["rubric"],
        "claim_boundaries": kit["claim_boundaries"],
    }
    return json.dumps(payload, indent=2, sort_keys=False)


def markdown_system(role: str) -> str:
    return (
        f"You are a benchmark participant acting as {role}. "
        "Use only the frozen packet provided by the user. Do not browse. "
        "Do not mention model identity, benchmark mechanics, hidden labels, or internal process. "
        "Return Markdown only."
    )


def gov_system() -> str:
    return (
        "You are fixed HoloGov for a HoloBuild artifact benchmark. "
        "Use only the frozen packet and prior artifacts. Do not browse. "
        "Your job is to create a compact but forceful mission packet for the next HoloAgent. "
        "Return Markdown only."
    )


def judge_system(judge_id: str) -> str:
    return (
        f"You are {judge_id}, a blind judge for a controlled artifact benchmark. "
        "Do not browse. You are scoring one anonymous artifact at a time. "
        "You are not told which system, model, condition, or cohort generated it. "
        "Score only against the brief, frozen source pack, datasets, exhibits, rubric, and single blind artifact. "
        "Return strict JSON only."
    )


def turn_word_target(kit: dict[str, Any], turn: int) -> str:
    band = kit["manifest"]["word_band"]
    if turn >= 5:
        return f"{band['min']}-{band['max']} validator-counted words; target about {band['target']} validator-counted words"
    return "enough detail to advance the draft without pretending this is final"


def final_turn_validity_guard(kit: dict[str, Any], turn: int) -> str:
    if turn < 5:
        return ""
    gate = kit["gov_protocol"]["validity_gate"]
    sections = "\n".join(f"- {section}" for section in gate.get("required_sections_must_be_present", []))
    return f"""

Final-turn validity gate:
- The final deliverable must be within the stated validator-counted word band. Do not include a self-reported word count.
- Include every required section exactly enough for deterministic matching:
{sections}
- Include the required disclaimer verbatim: {gate.get('required_disclaimer', '')}
- End as a clean client artifact with normal punctuation.
- Do not include delivery metadata or process residue such as Document Status, Word Count, Turn, Role, model slot, benchmark_credit, or internal scaffold text.
"""


def prior_artifact_block(previous_artifacts: list[dict[str, Any]]) -> str:
    if not previous_artifacts:
        return "No prior artifact. This is Turn 1."
    blocks = []
    for item in previous_artifacts:
        blocks.append(
            f"## Prior Turn {item['turn']} - {item['role']}\n"
            f"model_slot: {item.get('model', '')}\n"
            f"artifact_sha256: {sha_text(item['text'])}\n\n"
            f"{item['text']}"
        )
    return "\n\n".join(blocks)


def live_state_object(
    *,
    kit: dict[str, Any],
    cohort_plan: dict[str, Any],
    turn: int,
    role_item: dict[str, Any],
    previous_artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "state_object_kind": "BUILD_STATE_OBJECT",
        "state_object_version": "holo_factory_build_state_v1",
        "domain_id": kit["domain_id"],
        "packet_id": kit["manifest"]["packet_id"],
        "hash_lock_id": kit["hash_lock"]["hash_lock_id"],
        "cohort": cohort_plan["cohort"],
        "routing_config_id": cohort_plan["routing_config_id"],
        "governor_model": cohort_plan["governor_model"],
        "turn": turn,
        "role": role_item["role"],
        "fixed_v1_law": {
            "randomized_holoagents": False,
            "randomized_hologov": False,
            "same_base_turn_prompt_for_solo_and_holo": True,
        },
        "repair_ledger": [
            {
                "turn": item["turn"],
                "role": item["role"],
                "artifact_sha256": sha_text(item["text"]),
                "word_count": word_count(item["text"]),
            }
            for item in previous_artifacts
        ],
        "standing_hidden_failure_probes": kit["gov_protocol"].get("standing_hidden_failure_probes", []),
        "domain_probe_bank": kit["gov_protocol"].get("domain_probe_bank", []),
        "validity_gate": kit["gov_protocol"].get("validity_gate", {}),
    }


def solo_live_prompt(
    *,
    kit: dict[str, Any],
    payload: str,
    condition: str,
    model: str,
    turn: int,
    role_item: dict[str, Any],
    previous_text: str | None,
) -> str:
    previous_block = previous_text or "No prior draft. This is Turn 1."
    return f"""Frozen benchmark packet:

{payload}

Turn: {turn} of 6
Role: {role_item['role']}
Turn instruction: {role_item['instruction']}
Target length: {turn_word_target(kit, turn)}.
{final_turn_validity_guard(kit, turn)}

Previous draft state:
{previous_block}

Write the best possible updated artifact for this turn. Preserve useful prior content, repair weaknesses, cite source IDs inline, respect all required sections and disclaimers, and do not browse.
"""


def gov_live_prompt(
    *,
    kit: dict[str, Any],
    payload: str,
    turn: int,
    role_item: dict[str, Any],
    previous_artifacts: list[dict[str, Any]],
    state_object: dict[str, Any],
) -> str:
    return f"""Canonical BUILD_STATE_OBJECT:

```json
{json.dumps(state_object, indent=2)}
```

Frozen benchmark packet:

{payload}

Holo turn to prepare: {turn} of 6
Next role: {role_item['role']}
Next instruction: {role_item['instruction']}

Prior artifacts:
{prior_artifact_block(previous_artifacts)}

Create the Turn {turn} HoloGov mission packet. Include:
- current_best_state
- new_learnings_from_prior_turns
- repair_ledger
- open_issue -> repaired -> regressed -> still_missing tracking
- highest_value_flaw
- source_context_anchors
- hidden_failure_probes
- domain_probe_questions
- math_and_dataset_checks
- compliance_and_boundary_checks
- next_role_objective
- constraints_and_do_not_do
- convergence_target

Be technical and specific. Ask hard practitioner-grade questions. Do not write the final artifact yourself. Do not browse.
"""


def holo_live_prompt(
    *,
    kit: dict[str, Any],
    payload: str,
    turn: int,
    role_item: dict[str, Any],
    previous_artifacts: list[dict[str, Any]],
    state_object: dict[str, Any],
    mission: str | None,
) -> str:
    mission_block = mission or "No Gov mission for Turn 1. Build the first serious complete draft."
    return f"""HoloGov mission packet:

{mission_block}

Canonical BUILD_STATE_OBJECT:

```json
{json.dumps(state_object, indent=2)}
```

Pinned prior artifacts:
{prior_artifact_block(previous_artifacts)}

Frozen benchmark packet:

{payload}

Holo condition: fixed-route multi-model adversarial build with fixed Gov mission packets.
Turn: {turn} of 6
Role: {role_item['role']}
Turn instruction: {role_item['instruction']}
Target length: {turn_word_target(kit, turn)}.
{final_turn_validity_guard(kit, turn)}

Write the best possible updated artifact for this turn. Answer or resolve Gov's probes, preserve the strongest prior material, repair regressions, cite source IDs inline, respect the word band, and produce the best possible final artifact on Turn 6. Do not browse.
"""


def selector_live_prompt(*, kit: dict[str, Any], turn5: str, turn6: str, validity: dict[str, Any]) -> str:
    return f"""You are selecting the strongest valid final artifact.

Domain: {kit['domain_id']}
Required disclaimer: {kit['gov_protocol']['validity_gate']['required_disclaimer']}

Candidate validity reports:
```json
{json.dumps(validity, indent=2)}
```

Turn 5 candidate:
{turn5}

Turn 6 candidate:
{turn6}

Return strict JSON with:
{{
  "selected_artifact": "turn_5" | "turn_6" | "no_valid_candidate",
  "quality_rationale": "brief explanation",
  "validity_rationale": "brief explanation",
  "regression_notes": ["..."],
  "final_selection_confidence_1_5": 1
}}

The candidate validity reports are authoritative. Validity comes before quality. If one candidate is valid and the other is invalid, select the valid candidate. If both candidates are invalid, return "no_valid_candidate". Do not browse.
"""


def deterministic_final_selection(candidate_validity: dict[str, Any], requested: str | None) -> tuple[str, list[str]]:
    notes: list[str] = []
    turn5_valid = bool((candidate_validity.get("turn_5") or {}).get("valid"))
    turn6_valid = bool((candidate_validity.get("turn_6") or {}).get("valid"))
    if turn6_valid and not turn5_valid:
        if requested != "turn_6":
            notes.append("deterministic_override_selected_only_valid_turn_6")
        return "turn_6", notes
    if turn5_valid and not turn6_valid:
        if requested != "turn_5":
            notes.append("deterministic_override_selected_only_valid_turn_5")
        return "turn_5", notes
    if not turn5_valid and not turn6_valid:
        notes.append("no_valid_candidate_fail_closed")
        return "no_valid_candidate", notes
    if requested in {"turn_5", "turn_6"}:
        return requested, notes
    notes.append("invalid_selector_choice_defaulted_turn_6")
    return "turn_6", notes


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(stripped[start : end + 1])


def save_prompt_card(
    run_root: Path,
    *,
    rel: str,
    provider: str,
    model: str,
    system: str,
    user: str,
    call_type: str,
) -> Path:
    path = run_root / "prompt_cards" / f"{rel}.json"
    write_json(
        path,
        {
            "provider": provider,
            "model": model,
            "call_type": call_type,
            "system_sha256": sha_text(system),
            "user_sha256": sha_text(user),
            "system": system,
            "user": user,
        },
    )
    return path


def save_live_call(
    *,
    run_root: Path,
    trace_rel: str,
    prompt_card_path: Path,
    artifact_path: Path | None,
    artifact_text: str,
    call_type: str,
    condition: str,
    provider: str,
    model: str,
    role: str,
    turn: int | None,
    result: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    trace = {
        "call_type": call_type,
        "condition": condition,
        "provider": provider,
        "model": model,
        "role": role,
        "turn": turn,
        "prompt_card_path": str(prompt_card_path.relative_to(run_root)),
        "artifact_path": str(artifact_path.relative_to(run_root)) if artifact_path else None,
        "artifact_sha256": sha_text(artifact_text) if artifact_text else None,
        "word_count": word_count(artifact_text) if artifact_text else 0,
        "input_tokens": result.get("input_tokens", 0),
        "output_tokens": result.get("output_tokens", 0),
        "latency_ms": result.get("latency_ms", 0),
        "http_status": result.get("http_status"),
        "response_id": result.get("response_id", ""),
        "empty_visible_retry_count": result.get("empty_visible_retry_count", 0),
        "created_at_utc": utc_iso(),
        "extra": extra or {},
    }
    write_json(run_root / "traces" / f"{trace_rel}.json", trace)
    return trace


def call_and_save_live(
    *,
    run_root: Path,
    provider_model_name: str,
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
    provider, model = provider_model(provider_model_name)
    prompt_card = save_prompt_card(
        run_root,
        rel=prompt_rel,
        provider=provider,
        model=model,
        system=system,
        user=user,
        call_type=call_type,
    )
    result = call_provider(provider, system=system, user=user, max_tokens=max_tokens, timeout=timeout, model_override=model)
    text = result["text"].strip() + "\n"
    if artifact_path:
        write_text(artifact_path, text)
    trace = save_live_call(
        run_root=run_root,
        trace_rel=trace_rel,
        prompt_card_path=prompt_card,
        artifact_path=artifact_path,
        artifact_text=text,
        call_type=call_type,
        condition=condition,
        provider=provider,
        model=model,
        role=role,
        turn=turn,
        result=result,
        extra=extra,
    )
    return text, trace


def existing_live_artifact(run_root: Path, artifact_path: Path, trace_rel: str) -> tuple[str, dict[str, Any]] | None:
    trace_path = run_root / "traces" / f"{trace_rel}.json"
    if artifact_path.exists() and trace_path.exists():
        return artifact_path.read_text(encoding="utf-8"), read_json(trace_path)
    return None


def run_live_solo_condition(
    *,
    run_root: Path,
    run_id: str,
    kit: dict[str, Any],
    cohort_plan: dict[str, Any],
    condition: str,
    provider_model_name: str,
    timeout: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = run_root / "condition_manifests" / kit["domain_id"] / cohort_plan["cohort"] / f"{condition}.json"
    if manifest_path.exists():
        return read_json(manifest_path), []
    payload = frozen_packet_payload(kit, cohort_plan, mode="solo")
    previous_text: str | None = None
    traces: list[dict[str, Any]] = []
    final_text = ""
    for role_item in kit["role_flow"]["turns"]:
        turn = int(role_item["turn"])
        artifact_path = run_root / "artifacts" / kit["domain_id"] / cohort_plan["cohort"] / condition / f"turn_{turn}.md"
        trace_rel = f"{kit['domain_id']}/{cohort_plan['cohort']}/{condition}/turn_{turn}"
        cached = existing_live_artifact(run_root, artifact_path, trace_rel)
        if cached:
            text, trace = cached
            traces.append(trace)
        else:
            text, trace = call_and_save_live(
                run_root=run_root,
                provider_model_name=provider_model_name,
                system=markdown_system(role_item["role"]),
                user=solo_live_prompt(
                    kit=kit,
                    payload=payload,
                    condition=condition,
                    model=provider_model_name,
                    turn=turn,
                    role_item=role_item,
                    previous_text=previous_text,
                ),
                max_tokens=9000 if turn >= 5 else 6000,
                timeout=timeout,
                call_type="solo_turn",
                condition=condition,
                role=role_item["role"],
                turn=turn,
                prompt_rel=f"{kit['domain_id']}/{cohort_plan['cohort']}/{condition}/turn_{turn}",
                trace_rel=trace_rel,
                artifact_path=artifact_path,
                extra={"run_id": run_id, "domain_id": kit["domain_id"], "cohort": cohort_plan["cohort"]},
            )
            traces.append(trace)
        previous_text = text
        if turn == 6:
            final_text = text
    final_path = run_root / "artifacts" / kit["domain_id"] / cohort_plan["cohort"] / condition / "final.md"
    write_text(final_path, final_text)
    validity = validity_report(final_text, kit)
    result = {
        "run_id": run_id,
        "domain_id": kit["domain_id"],
        "cohort": cohort_plan["cohort"],
        "condition": condition,
        "provider_model": provider_model_name,
        "status": "valid_final" if validity["valid"] else "invalid_final",
        "final_artifact_path": str(final_path),
        "final_sha256": sha_text(final_text),
        "final_word_count": word_count(final_text),
        "artifact_validity_report": validity,
        "turn_count": 6,
        "input_tokens": sum(int(t.get("input_tokens", 0)) for t in traces),
        "output_tokens": sum(int(t.get("output_tokens", 0)) for t in traces),
        "latency_ms": sum(int(t.get("latency_ms", 0)) for t in traces),
    }
    write_json(manifest_path, result)
    return result, traces


def select_condition_ids(cohort_plan: dict[str, Any], raw_conditions: list[str] | None) -> list[str]:
    valid = [cohort_plan["holo_condition_id"], *cohort_plan["solo_conditions"].keys()]
    if not raw_conditions:
        return valid
    selected: list[str] = []
    unknown: list[str] = []
    for condition in raw_conditions:
        if condition not in valid:
            unknown.append(condition)
        elif condition not in selected:
            selected.append(condition)
    if unknown:
        raise RuntimeError(f"unknown_conditions:{unknown}; valid={valid}")
    return selected


def run_live_holo_condition(
    *,
    run_root: Path,
    run_id: str,
    kit: dict[str, Any],
    cohort_plan: dict[str, Any],
    timeout: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    condition = cohort_plan["holo_condition_id"]
    manifest_path = run_root / "condition_manifests" / kit["domain_id"] / cohort_plan["cohort"] / f"{condition}.json"
    if manifest_path.exists():
        return read_json(manifest_path), []
    payload = frozen_packet_payload(kit, cohort_plan)
    route = load_routing_config(cohort_plan["routing_config_id"])
    previous_artifacts: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    turn_texts: dict[int, str] = {}
    mission_text: str | None = None
    for role_item in kit["role_flow"]["turns"]:
        turn = int(role_item["turn"])
        analyst_model = route["analyst_rotation"][turn - 1]
        state_object = live_state_object(
            kit=kit,
            cohort_plan=cohort_plan,
            turn=turn,
            role_item=role_item,
            previous_artifacts=previous_artifacts,
        )
        write_json(
            run_root / "state_objects" / kit["domain_id"] / cohort_plan["cohort"] / condition / f"turn_{turn}.json",
            state_object,
        )
        if turn > 1:
            mission_path = (
                run_root
                / "mission_packets"
                / kit["domain_id"]
                / cohort_plan["cohort"]
                / condition
                / f"turn_{turn}_mission.md"
            )
            trace_rel = f"{kit['domain_id']}/{cohort_plan['cohort']}/{condition}/gov_turn_{turn}"
            cached = existing_live_artifact(run_root, mission_path, trace_rel)
            if cached:
                mission_text, trace = cached
                traces.append(trace)
            else:
                mission_text, trace = call_and_save_live(
                    run_root=run_root,
                    provider_model_name=cohort_plan["governor_model"],
                    system=gov_system(),
                    user=gov_live_prompt(
                        kit=kit,
                        payload=payload,
                        turn=turn,
                        role_item=role_item,
                        previous_artifacts=previous_artifacts,
                        state_object=state_object,
                    ),
                    max_tokens=3200,
                    timeout=timeout,
                    call_type="holo_gov_mission_packet",
                    condition=condition,
                    role="HoloGov mission packet",
                    turn=turn,
                    prompt_rel=f"{kit['domain_id']}/{cohort_plan['cohort']}/{condition}/gov_turn_{turn}",
                    trace_rel=trace_rel,
                    artifact_path=mission_path,
                    extra={"run_id": run_id, "domain_id": kit["domain_id"], "cohort": cohort_plan["cohort"]},
                )
                traces.append(trace)
        artifact_path = run_root / "artifacts" / kit["domain_id"] / cohort_plan["cohort"] / condition / f"turn_{turn}.md"
        trace_rel = f"{kit['domain_id']}/{cohort_plan['cohort']}/{condition}/turn_{turn}"
        cached = existing_live_artifact(run_root, artifact_path, trace_rel)
        if cached:
            text, trace = cached
            traces.append(trace)
        else:
            text, trace = call_and_save_live(
                run_root=run_root,
                provider_model_name=analyst_model,
                system=markdown_system(role_item["role"]),
                user=holo_live_prompt(
                    kit=kit,
                    payload=payload,
                    turn=turn,
                    role_item=role_item,
                    previous_artifacts=previous_artifacts,
                    state_object=state_object,
                    mission=mission_text,
                ),
                max_tokens=9000 if turn >= 5 else 6000,
                timeout=timeout,
                call_type="holo_analyst_turn",
                condition=condition,
                role=role_item["role"],
                turn=turn,
                prompt_rel=f"{kit['domain_id']}/{cohort_plan['cohort']}/{condition}/turn_{turn}",
                trace_rel=trace_rel,
                artifact_path=artifact_path,
                extra={"run_id": run_id, "domain_id": kit["domain_id"], "cohort": cohort_plan["cohort"]},
            )
            traces.append(trace)
        turn_texts[turn] = text
        previous_artifacts.append(
            {
                "turn": turn,
                "role": role_item["role"],
                "model": analyst_model,
                "text": text,
            }
        )

    candidate_validity = {
        "turn_5": validity_report(turn_texts.get(5, ""), kit),
        "turn_6": validity_report(turn_texts.get(6, ""), kit),
    }
    selector_path = run_root / "final_selection" / kit["domain_id"] / cohort_plan["cohort"] / f"{condition}.json"
    selector_trace_rel = f"{kit['domain_id']}/{cohort_plan['cohort']}/{condition}/post_turn_6_selector"
    selector_cached = selector_path.exists() and (run_root / "traces" / f"{selector_trace_rel}.json").exists()
    if selector_cached:
        selector_payload = read_json(selector_path)
        traces.append(read_json(run_root / "traces" / f"{selector_trace_rel}.json"))
    else:
        selector_text, selector_trace = call_and_save_live(
            run_root=run_root,
            provider_model_name=cohort_plan["governor_model"],
            system="You are HoloGov final selector. Return strict JSON only.",
            user=selector_live_prompt(
                kit=kit,
                turn5=turn_texts.get(5, ""),
                turn6=turn_texts.get(6, ""),
                validity=candidate_validity,
            ),
            max_tokens=2000,
            timeout=timeout,
            call_type="holo_gov_final_selector",
            condition=condition,
            role="HoloGov final selector",
            turn=None,
            prompt_rel=f"{kit['domain_id']}/{cohort_plan['cohort']}/{condition}/post_turn_6_selector",
            trace_rel=selector_trace_rel,
            artifact_path=None,
            extra={"run_id": run_id, "domain_id": kit["domain_id"], "cohort": cohort_plan["cohort"]},
        )
        try:
            parsed = extract_json_object(selector_text)
        except Exception as exc:
            parsed = {
                "selected_artifact": "no_valid_candidate",
                "quality_rationale": "Selector JSON parse failed; defaulted to Turn 6.",
                "validity_rationale": excerpt(exc),
                "regression_notes": ["selector_parse_failure"],
                "final_selection_confidence_1_5": 1,
            }
        selected = parsed.get("selected_artifact")
        if selected not in {"turn_5", "turn_6", "no_valid_candidate"}:
            selected = "no_valid_candidate"
            parsed.setdefault("regression_notes", []).append("invalid_selected_artifact_fail_closed")
        selected, deterministic_notes = deterministic_final_selection(candidate_validity, selected)
        if deterministic_notes:
            parsed.setdefault("regression_notes", []).extend(deterministic_notes)
            parsed["selected_artifact"] = selected
        selector_payload = {
            "selector_model": cohort_plan["governor_model"],
            "parsed": parsed,
            "selected_artifact": selected,
            "candidate_validity": candidate_validity,
        }
        write_json(selector_path, selector_payload)
        traces.append(selector_trace)

    selected, deterministic_notes = deterministic_final_selection(candidate_validity, selector_payload.get("selected_artifact"))
    if deterministic_notes:
        selector_payload.setdefault("parsed", {}).setdefault("regression_notes", []).extend(deterministic_notes)
        selector_payload["selected_artifact"] = selected
        write_json(selector_path, selector_payload)
    selected_turn = 5 if selected == "turn_5" else 6
    final_text = turn_texts[selected_turn]
    final_path = run_root / "artifacts" / kit["domain_id"] / cohort_plan["cohort"] / condition / "final.md"
    write_text(final_path, final_text)
    validity = validity_report(final_text, kit)
    result = {
        "run_id": run_id,
        "domain_id": kit["domain_id"],
        "cohort": cohort_plan["cohort"],
        "condition": condition,
        "provider_model": "fixed_holo_route",
        "governor_model": cohort_plan["governor_model"],
        "analyst_rotation": route["analyst_rotation"],
        "status": "valid_final" if validity["valid"] else "invalid_final",
        "final_artifact_path": str(final_path),
        "final_sha256": sha_text(final_text),
        "final_word_count": word_count(final_text),
        "artifact_validity_report": validity,
        "selected_turn": selected_turn,
        "deterministic_final_selection": selected,
        "final_selection_fail_closed": selected == "no_valid_candidate",
        "selector_path": str(selector_path),
        "turn_count": 6,
        "input_tokens": sum(int(t.get("input_tokens", 0)) for t in traces),
        "output_tokens": sum(int(t.get("output_tokens", 0)) for t in traces),
        "latency_ms": sum(int(t.get("latency_ms", 0)) for t in traces),
    }
    write_json(manifest_path, result)
    return result, traces


def live_single_artifact_judge_prompt(*, packet: dict[str, Any], judge_id: str) -> str:
    visible_packet = judge_visible_packet(packet)
    criteria_example = [
        {"criterion_id": item["id"], "score_1_5": 3, "score_1_10": 6, "notes": "reason"}
        for item in packet["rubric"]["criteria"]
    ]
    return f"""Judge packet:

{json.dumps(visible_packet, indent=2)}

Anonymous artifact:
{packet['artifact']['text']}

You are scoring this single anonymous artifact only.
Do not compare it to another artifact.
Do not rank artifacts.
Do not infer whether it is Holo, solo, mini, frontier, or which model produced it.

Return strict JSON only:
{{
  "judge_id": "{judge_id}",
  "blindness_confirmation": "I was not told whether this artifact is Holo, solo, mini, frontier, or which model generated it.",
  "artifact": {{
    "anonymous_label": "{packet['artifact']['anonymous_label']}",
    "summary_description": "...",
    "criterion_scores": {json.dumps(criteria_example)},
    "weighted_score_1_10": 0,
    "top_3_strengths": ["..."],
    "top_3_weaknesses_or_hidden_failures": ["..."],
    "unsupported_or_stale_claims": ["..."],
    "math_or_dataset_logic_issues": ["..."],
    "source_grounding_notes": "..."
  }},
  "validation_flags": []
}}
"""


def weighted_score(document: dict[str, Any], rubric: dict[str, Any]) -> float:
    weights = {item["id"]: float(item["weight"]) for item in rubric["criteria"]}
    rows = {item["criterion_id"]: item for item in document.get("criterion_scores", [])}
    total = 0.0
    for cid, weight in weights.items():
        total += float(rows[cid]["score_1_10"]) * weight / 100.0
    return round(total, 3)


def load_pair_map(run_root: Path) -> dict[str, dict[str, Any]]:
    maps = sorted((run_root / "sealed").glob("*anonymization_map.json"))
    if not maps:
        return {}
    sealed = read_json(maps[0])
    return {item.get("judge_packet_id"): item for item in sealed.get("pairs", [])}


def load_artifact_map(run_root: Path) -> dict[str, dict[str, Any]]:
    maps = sorted((run_root / "sealed").glob("*anonymization_map.json"))
    if not maps:
        return {}
    sealed = read_json(maps[0])
    return {item.get("judge_packet_id"): item for item in sealed.get("artifacts", [])}


def architecture_credit_for_condition(condition: str, cohort_plan: dict[str, Any]) -> dict[str, Any]:
    if condition != cohort_plan.get("holo_condition_id"):
        return {
            "architecture_credit_label": "solo_baseline",
            "scoreboard_eligible": True,
            "pre_holo_arch": False,
        }
    if condition in {"holo_frontier_fixed_v1", "holo_mini_fixed_v1"}:
        return {
            "architecture_credit_label": "current_context_governor_fixed_v1",
            "scoreboard_eligible": True,
            "pre_holo_arch": False,
        }
    return {
        "architecture_credit_label": "audit_only_pre_holo_arch",
        "scoreboard_eligible": False,
        "pre_holo_arch": True,
    }


def generation_dna_for_condition(*, cohort_plan: dict[str, Any], condition: str) -> dict[str, Any]:
    if condition == cohort_plan.get("holo_condition_id"):
        models = [str(item) for item in cohort_plan.get("analyst_rotation", []) if item]
        if cohort_plan.get("governor_model"):
            models.append(str(cohort_plan["governor_model"]))
        dna = generation_dna_from_provider_models(models)
        dna.update(
            {
                "artifact_condition": condition,
                "artifact_family": "holo",
                "holo_provider_models": sorted(set(models)),
                "solo_provider_model": "",
            }
        )
        return dna
    solo_model = (cohort_plan.get("solo_conditions") or {}).get(condition)
    dna = generation_dna_from_provider_models([str(solo_model)] if solo_model else [])
    dna.update(
        {
            "artifact_condition": condition,
            "artifact_family": "solo",
            "holo_provider_models": [],
            "solo_provider_model": solo_model or "",
        }
    )
    return dna


def score_final_judge_packets(*, run_root: Path, timeout: int) -> tuple[int, list[dict[str, Any]]]:
    judge_panel = load_leaderboard_judge_panel()
    artifact_map = load_artifact_map(run_root)
    scored = 0
    traces: list[dict[str, Any]] = []
    for packet_path in sorted((run_root / "judge_packets" / "final_single").glob("*/*/*.json")):
        packet = read_json(packet_path)
        artifact_record = artifact_map.get(packet["judge_packet_id"], {})
        if not artifact_record.get("scoreboard_eligible", False):
            continue
        generation_dna = artifact_record.get("generation_dna")
        for judge in judge_panel["judge_models"]:
            credit = annotate_judge_credit(judge, generation_dna)
            judge_id = judge["judge_id"]
            provider_model_name = f"{judge['provider']}:{judge['model']}"
            score_path = run_root / "judge_scores" / packet["judge_packet_id"] / f"{judge_id}.json"
            if score_path.exists():
                continue
            raw, trace = call_and_save_live(
                run_root=run_root,
                provider_model_name=provider_model_name,
                system=judge_system(judge_id),
                user=live_single_artifact_judge_prompt(packet=packet, judge_id=judge_id),
                max_tokens=7500,
                timeout=timeout,
                call_type="blind_single_artifact_final_judge",
                condition=packet["judge_packet_id"],
                role="Blind single-artifact final judge",
                turn=None,
                prompt_rel=f"judges/{packet['judge_packet_id']}/{judge_id}",
                trace_rel=f"judges/{packet['judge_packet_id']}/{judge_id}",
                artifact_path=None,
                extra={"judge_packet_id": packet["judge_packet_id"]},
            )
            parsed = extract_json_object(raw)
            parsed["artifact"]["weighted_score_1_10"] = weighted_score(parsed["artifact"], packet["rubric"])
            parsed["_harness"] = {
                "judge_provider": judge["provider"],
                "judge_model": judge["model"],
                "judge_packet_id": packet["judge_packet_id"],
                "score_packet_mode": "single_artifact_leaderboard",
                "architecture_credit_label": artifact_record.get("architecture_credit_label"),
                "scoreboard_eligible": artifact_record.get("scoreboard_eligible"),
                **credit,
            }
            write_json(score_path, parsed)
            scored += 1
            traces.append(trace)
    return scored, traces


def smoke_artifact_text(
    *,
    kit: dict[str, Any],
    cohort: str,
    condition: str,
    model: str,
    turn: int,
    role: str,
    is_holo: bool,
) -> str:
    required_sections = kit["gov_protocol"]["validity_gate"]["required_sections_must_be_present"]
    source_tokens = source_id_tokens(kit["source_pack"])[:8]
    source_line = " ".join(source_tokens)
    title = kit["manifest"]["packet_id"]
    condition_type = "Holo fixed-route condition" if is_holo else "Solo baseline condition"
    sections = "\n\n".join(
        f"## {section.title()}\n"
        f"Smoke placeholder for `{section}`. The live run must fill this section with source-grounded, "
        f"domain-specific reasoning using the frozen packet only. Source anchors: {source_line}."
        for section in required_sections
    )
    return (
        f"# {title} - Turn {turn} Smoke Artifact\n\n"
        f"Cohort: `{cohort}`\n\n"
        f"Condition: `{condition}`\n\n"
        f"Model slot: `{model}`\n\n"
        f"Role: `{role}`\n\n"
        f"Condition type: {condition_type}.\n\n"
        f"This file is a no-provider smoke placeholder. It is not benchmark credit and it is not a scored "
        f"deliverable. It exists to test full-domain automation, trace layout, packet loading, blind packet "
        f"assembly, and deterministic gates before live calls are allowed.\n\n"
        f"{sections}\n\n"
        f"## Disclaimer\n"
        f"{kit['gov_protocol']['validity_gate']['required_disclaimer']}\n"
    )


def write_artifact_and_trace(
    *,
    run_root: Path,
    run_id: str,
    kit: dict[str, Any],
    cohort_plan: dict[str, Any],
    condition: str,
    model: str,
    turn: int,
    role: str,
    is_holo: bool,
) -> dict[str, Any]:
    cohort = cohort_plan["cohort"]
    text = smoke_artifact_text(
        kit=kit,
        cohort=cohort,
        condition=condition,
        model=model,
        turn=turn,
        role=role,
        is_holo=is_holo,
    )
    artifact_path = run_root / "artifacts" / kit["domain_id"] / cohort / condition / f"turn_{turn}.md"
    write_text(artifact_path, text)
    validity = validity_report(text, kit)
    trace = {
        "run_id": run_id,
        "domain_id": kit["domain_id"],
        "cohort": cohort,
        "condition": condition,
        "model": model,
        "turn": turn,
        "role": role,
        "is_holo": is_holo,
        "provider_calls": 0,
        "benchmark_credit": False,
        "artifact_path": str(artifact_path.relative_to(run_root)),
        "artifact_sha256": sha_text(text),
        "word_count": validity["word_count"],
        "validity": validity,
    }
    trace_path = run_root / "traces" / kit["domain_id"] / cohort / condition / f"turn_{turn}.json"
    write_json(trace_path, trace)
    return trace


def build_judge_packet(
    **_: Any,
) -> dict[str, Any]:
    raise RuntimeError("legacy_pairwise_judge_packets_disabled_use_single_artifact_leaderboard")


def build_artifact_score_packet(
    *,
    run_root: Path,
    kit: dict[str, Any],
    cohort_plan: dict[str, Any],
    condition: str,
    turn: int,
    packet_kind: str,
    sealed: dict[str, Any],
) -> dict[str, Any] | None:
    cohort = cohort_plan["cohort"]
    if packet_kind == "final":
        final_path = run_root / "artifacts" / kit["domain_id"] / cohort / condition / "final.md"
        artifact_path = final_path if final_path.exists() else (
            run_root / "artifacts" / kit["domain_id"] / cohort / condition / f"turn_{turn}.md"
        )
    else:
        artifact_path = run_root / "artifacts" / kit["domain_id"] / cohort / condition / f"turn_{turn}.md"
    if not artifact_path.exists():
        return None

    artifact_text = artifact_path.read_text(encoding="utf-8")
    artifact_validity = validity_report(artifact_text, kit)
    artifact_index = len(sealed.setdefault("artifacts", [])) + 1
    packet_id = f"packet_{artifact_index:04d}"
    anonymous_label = f"Artifact {artifact_index:04d}"
    architecture_credit = architecture_credit_for_condition(condition, cohort_plan)
    scoreboard_eligible = bool(architecture_credit.get("scoreboard_eligible")) and (
        packet_kind != "final" or bool(artifact_validity.get("valid"))
    )
    generation_dna = generation_dna_for_condition(cohort_plan=cohort_plan, condition=condition)
    packet = {
        "judge_packet_id": packet_id,
        "score_packet_mode": "single_artifact_leaderboard",
        "packet_kind": packet_kind,
        "blind": True,
        "benchmark_credit": False,
        "provider_calls": 0,
        "turn": turn,
        "brief": kit["brief"],
        "source_pack": kit["source_pack"],
        "datasets": kit["source_pack"].get("datasets", []),
        "exhibits": kit["source_pack"].get("exhibits", []),
        "judge_brief": kit["judge_brief"],
        "rubric": kit["rubric"],
        "artifact": {
            "anonymous_label": anonymous_label,
            "text": artifact_text,
        },
        "judge_instructions": {
            "do_not_browse": True,
            "do_not_infer_model_identity": True,
            "score_single_artifact_only": True,
            "do_not_compare_to_another_artifact": True,
            "do_not_rank_artifacts": True,
            "required_summary_description": True,
            "required_rationales": True,
        },
    }
    if packet_kind == "final":
        out_path = run_root / "judge_packets" / "final_single" / kit["domain_id"] / cohort / f"{packet_id}.json"
    else:
        out_path = run_root / "judge_packets" / "turn_single" / kit["domain_id"] / cohort / f"{packet_id}.json"
    write_json(out_path, packet)
    sealed["artifacts"].append(
        {
            "judge_packet_id": packet_id,
            "score_packet_mode": "single_artifact_leaderboard",
            "packet_kind": packet_kind,
            "domain_id": kit["domain_id"],
            "cohort": cohort,
            "turn": turn,
            "anonymous_label": anonymous_label,
            "condition": condition,
            "artifact_path": str(artifact_path.relative_to(run_root)),
            "artifact_sha256": sha_text(artifact_text),
            "artifact_validity": artifact_validity,
            "generation_dna": generation_dna,
            **architecture_credit,
            "scoreboard_eligible": scoreboard_eligible,
            "diagnostic_only_reason": None if scoreboard_eligible else "invalid_final_artifact" if packet_kind == "final" else "not_scoreboard_eligible",
        }
    )
    return {"packet_id": packet_id, "path": str(out_path.relative_to(run_root)), **architecture_credit}


def no_provider_smoke(args: argparse.Namespace) -> int:
    domain_ids = select_domain_ids(args.domains, args.spec)
    cohorts = select_cohorts(args.cohort)
    validation = [validate_domain_kit(domain_id) for domain_id in domain_ids]
    failures = [item for item in validation if not item["ok"]]
    if failures:
        payload = {
            "status": "HOLO_FACTORY_NO_PROVIDER_SMOKE_BLOCKED_INVALID_KITS",
            "run_id": None,
            "benchmark_credit": False,
            "failures": failures,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    run_id = args.run_id or f"holo_factory_no_provider_smoke_{utc_stamp()}"
    run_root = SUITE_RUNS_ROOT / run_id
    judge_panel = load_leaderboard_judge_panel()
    cohort_plans = [build_cohort_plan(cohort) for cohort in cohorts]
    sealed: dict[str, Any] = {
        "run_id": run_id,
        "blind": True,
        "score_packet_mode": "single_artifact_leaderboard",
        "artifacts": [],
        "pairs": [],
    }
    trace_count = 0
    final_packet_count = 0
    turn_packet_count = 0

    preflight_payload = {
        "status": "PREFLIGHT_PASS",
        "created_at_utc": utc_iso(),
        "provider_calls": 0,
        "benchmark_credit": False,
        "domain_ids": domain_ids,
        "cohorts": cohort_plans,
        "judge_panel": judge_panel["judge_models"],
        "provider_env": env_status(),
        "required_provider_env": required_envs_for_plan(cohorts),
        "domain_validation": validation,
        "live_execution": "disabled",
    }
    write_json(run_root / "preflight.json", preflight_payload)

    for domain_id in domain_ids:
        kit = load_kit(domain_id)
        for cohort_plan in cohort_plans:
            route = load_routing_config(cohort_plan["routing_config_id"])
            role_flow = kit["role_flow"]
            holo_condition = cohort_plan["holo_condition_id"]
            solo_conditions = cohort_plan["solo_conditions"]
            selected_conditions = select_condition_ids(cohort_plan, args.conditions)
            for turn in role_flow["turns"]:
                turn_index = int(turn["turn"]) - 1
                if holo_condition in selected_conditions:
                    trace = write_artifact_and_trace(
                        run_root=run_root,
                        run_id=run_id,
                        kit=kit,
                        cohort_plan=cohort_plan,
                        condition=holo_condition,
                        model=route["analyst_rotation"][turn_index],
                        turn=int(turn["turn"]),
                        role=turn["role"],
                        is_holo=True,
                    )
                    trace_count += 1
                for solo_condition, solo_model in solo_conditions.items():
                    if solo_condition not in selected_conditions:
                        continue
                    trace = write_artifact_and_trace(
                        run_root=run_root,
                        run_id=run_id,
                        kit=kit,
                        cohort_plan=cohort_plan,
                        condition=solo_condition,
                        model=solo_model,
                        turn=int(turn["turn"]),
                        role=turn["role"],
                        is_holo=False,
                    )
                    trace_count += 1

            for condition in selected_conditions:
                packet = build_artifact_score_packet(
                    run_root=run_root,
                    kit=kit,
                    cohort_plan=cohort_plan,
                    condition=condition,
                    turn=6,
                    packet_kind="final",
                    sealed=sealed,
                )
                if packet:
                    final_packet_count += 1
                for turn in range(1, 7):
                    packet = build_artifact_score_packet(
                        run_root=run_root,
                        kit=kit,
                        cohort_plan=cohort_plan,
                        condition=condition,
                        turn=turn,
                        packet_kind="turn",
                        sealed=sealed,
                    )
                    if packet:
                        turn_packet_count += 1

            write_json(
                run_root / "contracts" / domain_id / cohort_plan["cohort"] / "turn_prompt_parity.json",
                turn_prompt_parity(role_flow, route),
            )

    write_json(run_root / "sealed" / f"{run_id}_anonymization_map.json", sealed)
    manifest = {
        "run_id": run_id,
        "status": "HOLO_FACTORY_NO_PROVIDER_SMOKE_PASS",
        "created_at_utc": utc_iso(),
        "benchmark_credit": False,
        "public_claim": False,
        "provider_calls": 0,
        "domains": domain_ids,
        "cohorts": cohort_plans,
        "fixed_v1_law": {
            "randomized_holoagents": False,
            "randomized_hologov": False,
            "frontier_route": COHORT_DEFAULTS["frontier"]["routing_config_id"],
            "mini_route": COHORT_DEFAULTS["mini"]["routing_config_id"],
            "phase_2_ablation_deferred": True,
        },
        "artifact_count": trace_count,
        "trace_count": trace_count,
        "final_judge_packet_count": final_packet_count,
        "turn_judge_packet_count": turn_packet_count,
        "sealed_artifact_count": len(sealed["artifacts"]),
        "sealed_pair_count": len(sealed["pairs"]),
        "preflight": "preflight.json",
        "anonymization_map": f"sealed/{run_id}_anonymization_map.json",
        "domain_validation": validation,
        "notes": [
            "No provider calls were made.",
            "Smoke artifacts are placeholders and are not benchmark-credit outputs.",
            "Live execution remains gated behind a future explicit --run-live implementation and user approval.",
        ],
    }
    write_json(run_root / "suite_run_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def preflight(args: argparse.Namespace) -> int:
    domain_ids = select_domain_ids(args.domains, args.spec)
    cohorts = select_cohorts(args.cohort)
    validation = [validate_domain_kit(domain_id) for domain_id in domain_ids]
    ok = all(item["ok"] for item in validation)
    payload = {
        "status": "PREFLIGHT_PASS" if ok else "PREFLIGHT_INVALID_KITS",
        "provider_calls": 0,
        "benchmark_credit": False,
        "domain_ids": domain_ids,
        "cohorts": [build_cohort_plan(cohort) for cohort in cohorts],
        "judge_panel": load_leaderboard_judge_panel()["judge_models"],
        "provider_env": env_status(),
        "required_provider_env": required_envs_for_plan(cohorts),
        "domain_validation": validation,
        "live_calls_default": "disabled",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if ok else 2


def list_domains(args: argparse.Namespace) -> int:
    domain_ids = select_domain_ids(["all"], args.spec)
    print(json.dumps({"suite": str(args.spec), "domains": domain_ids}, indent=2))
    return 0


def run_live(args: argparse.Namespace) -> int:
    domain_ids = select_domain_ids(args.domains, args.spec)
    cohorts = select_cohorts(args.cohort)
    validation = [validate_domain_kit(domain_id) for domain_id in domain_ids]
    failures = [item for item in validation if not item["ok"]]
    if failures:
        payload = {
            "status": "HOLO_FACTORY_LIVE_BLOCKED_INVALID_KITS",
            "run_id": None,
            "benchmark_credit": False,
            "provider_calls": 0,
            "failures": failures,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    required_env = required_envs_for_plan(cohorts)
    status = env_status()
    missing_env = [name for name in required_env if status.get(name) != "PRESENT"]
    if missing_env:
        payload = {
            "status": "HOLO_FACTORY_LIVE_BLOCKED_MISSING_ENV",
            "run_id": None,
            "benchmark_credit": False,
            "provider_calls": 0,
            "missing_required_provider_env": missing_env,
            "provider_env": status,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    run_id = args.run_id or f"holo_factory_live_{utc_stamp()}"
    run_root = SUITE_RUNS_ROOT / run_id
    cohort_plans = [build_cohort_plan(cohort) for cohort in cohorts]
    sealed: dict[str, Any] = {
        "run_id": run_id,
        "blind": True,
        "score_packet_mode": "single_artifact_leaderboard",
        "artifacts": [],
        "pairs": [],
    }
    all_traces: list[dict[str, Any]] = []
    condition_results: list[dict[str, Any]] = []
    final_packet_count = 0
    turn_packet_count = 0
    errors: list[dict[str, Any]] = []

    preflight_payload = {
        "status": "PREFLIGHT_PASS",
        "created_at_utc": utc_iso(),
        "provider_calls": "live",
        "benchmark_credit": False,
        "domain_ids": domain_ids,
        "cohorts": cohort_plans,
        "judge_panel": load_leaderboard_judge_panel()["judge_models"],
        "provider_env": status,
        "required_provider_env": required_env,
        "domain_validation": validation,
        "score_final_judges": bool(args.score_final_judges),
    }
    write_json(run_root / "preflight.json", preflight_payload)

    for domain_id in domain_ids:
        kit = load_kit(domain_id)
        for cohort_plan in cohort_plans:
            route = load_routing_config(cohort_plan["routing_config_id"])
            selected_conditions = select_condition_ids(cohort_plan, args.conditions)
            write_json(
                run_root / "contracts" / domain_id / cohort_plan["cohort"] / "turn_prompt_parity.json",
                turn_prompt_parity(kit["role_flow"], route),
            )
            if cohort_plan["holo_condition_id"] in selected_conditions:
                try:
                    holo_result, traces = run_live_holo_condition(
                        run_root=run_root,
                        run_id=run_id,
                        kit=kit,
                        cohort_plan=cohort_plan,
                        timeout=args.timeout,
                    )
                    all_traces.extend(traces)
                    condition_results.append(holo_result)
                except Exception as exc:
                    error_row = {
                        "domain_id": domain_id,
                        "cohort": cohort_plan["cohort"],
                        "condition": cohort_plan["holo_condition_id"],
                        "error_type": exc.__class__.__name__,
                        "http_status": getattr(exc, "http_status", None),
                        "message": excerpt(exc),
                    }
                    errors.append(error_row)
                    write_json(
                        run_root
                        / "condition_manifests"
                        / domain_id
                        / cohort_plan["cohort"]
                        / f"{cohort_plan['holo_condition_id']}.json",
                        {**error_row, "status": "generation_error"},
                    )
                    if not args.continue_on_error:
                        break
            for solo_condition, solo_model in cohort_plan["solo_conditions"].items():
                if solo_condition not in selected_conditions:
                    continue
                try:
                    solo_result, traces = run_live_solo_condition(
                        run_root=run_root,
                        run_id=run_id,
                        kit=kit,
                        cohort_plan=cohort_plan,
                        condition=solo_condition,
                        provider_model_name=solo_model,
                        timeout=args.timeout,
                    )
                    all_traces.extend(traces)
                    condition_results.append(solo_result)
                except Exception as exc:
                    error_row = {
                        "domain_id": domain_id,
                        "cohort": cohort_plan["cohort"],
                        "condition": solo_condition,
                        "provider_model": solo_model,
                        "error_type": exc.__class__.__name__,
                        "http_status": getattr(exc, "http_status", None),
                        "message": excerpt(exc),
                    }
                    errors.append(error_row)
                    write_json(
                        run_root / "condition_manifests" / domain_id / cohort_plan["cohort"] / f"{solo_condition}.json",
                        {**error_row, "status": "generation_error"},
                    )
                    if not args.continue_on_error:
                        break
            if errors and not args.continue_on_error:
                break
            for condition in selected_conditions:
                condition_manifest = (
                    run_root / "condition_manifests" / domain_id / cohort_plan["cohort"] / f"{condition}.json"
                )
                if not condition_manifest.exists():
                    continue
                if read_json(condition_manifest).get("status") == "generation_error":
                    continue
                packet = build_artifact_score_packet(
                    run_root=run_root,
                    kit=kit,
                    cohort_plan=cohort_plan,
                    condition=condition,
                    turn=6,
                    packet_kind="final",
                    sealed=sealed,
                )
                if packet:
                    final_packet_count += 1
                for turn in range(1, 7):
                    packet = build_artifact_score_packet(
                        run_root=run_root,
                        kit=kit,
                        cohort_plan=cohort_plan,
                        condition=condition,
                        turn=turn,
                        packet_kind="turn",
                        sealed=sealed,
                    )
                    if packet:
                        turn_packet_count += 1
        if errors and not args.continue_on_error:
            break

    write_json(run_root / "sealed" / f"{run_id}_anonymization_map.json", sealed)
    judge_score_count = 0
    if args.score_final_judges and not errors:
        judge_score_count, judge_traces = score_final_judge_packets(run_root=run_root, timeout=args.timeout)
        all_traces.extend(judge_traces)

    token_input = sum(int(trace.get("input_tokens", 0)) for trace in all_traces)
    token_output = sum(int(trace.get("output_tokens", 0)) for trace in all_traces)
    latency_ms = sum(int(trace.get("latency_ms", 0)) for trace in all_traces)
    manifest = {
        "run_id": run_id,
        "status": "HOLO_FACTORY_LIVE_COMPLETE" if not errors else "HOLO_FACTORY_LIVE_ERROR",
        "created_at_utc": utc_iso(),
        "benchmark_credit": False,
        "public_claim": False,
        "domains": domain_ids,
        "cohorts": cohort_plans,
        "fixed_v1_law": {
            "randomized_holoagents": False,
            "randomized_hologov": False,
            "frontier_route": COHORT_DEFAULTS["frontier"]["routing_config_id"],
            "mini_route": COHORT_DEFAULTS["mini"]["routing_config_id"],
            "phase_2_ablation_deferred": True,
        },
        "condition_count": len(condition_results),
        "provider_call_trace_count": len(all_traces),
        "input_tokens": token_input,
        "output_tokens": token_output,
        "total_tokens": token_input + token_output,
        "latency_ms": latency_ms,
        "final_judge_packet_count": final_packet_count,
        "turn_judge_packet_count": turn_packet_count,
        "judge_score_count": judge_score_count,
        "sealed_artifact_count": len(sealed["artifacts"]),
        "sealed_pair_count": len(sealed["pairs"]),
        "errors": errors,
        "preflight": "preflight.json",
        "anonymization_map": f"sealed/{run_id}_anonymization_map.json",
        "domain_validation": validation,
        "notes": [
            "Live generation sends frozen packets and generated artifacts to external providers.",
            "benchmark_credit remains false until artifacts, traces, judging, and rollups are reviewed and promoted.",
            "Final judge scoring only runs when --score-final-judges is set.",
        ],
    }
    write_json(run_root / "suite_run_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Sequential HoloFactory suite runner.")
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--domains", nargs="+", default=["all"], help="Domain ids or all.")
    parser.add_argument("--cohort", default="both", choices=["frontier", "mini", "both"])
    parser.add_argument(
        "--conditions",
        nargs="+",
        help="Optional condition IDs to run within the selected cohort, for example holo_frontier_fixed_v1 solo_openai.",
    )
    parser.add_argument("--run-id")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--no-provider-smoke", action="store_true")
    parser.add_argument("--run-live", action="store_true", help="Run live generation. Sends frozen packets/artifacts to providers.")
    parser.add_argument("--score-final-judges", action="store_true", help="After live generation, score final blind packets.")
    parser.add_argument("--continue-on-error", action="store_true", help="Continue later conditions after provider/model failures.")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    modes = [args.list, args.preflight, args.no_provider_smoke, args.run_live]
    if sum(bool(item) for item in modes) != 1:
        parser.print_help()
        print("\nChoose exactly one mode.")
        return 2
    if args.list:
        return list_domains(args)
    if args.preflight:
        return preflight(args)
    if args.no_provider_smoke:
        return no_provider_smoke(args)
    return run_live(args)


if __name__ == "__main__":
    raise SystemExit(main())
