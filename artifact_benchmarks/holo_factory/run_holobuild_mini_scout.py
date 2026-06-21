from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_holo_factory_suite import PROVIDER_ENV, ProviderCallError, call_provider, provider_model

FACTORY_DIR = Path(__file__).resolve().parent
REPO_ROOT = FACTORY_DIR.parents[1]
DEFAULT_SUITE_MANIFEST = FACTORY_DIR / "mini_scouts/TEN_DOMAIN_PACKET_SUITE_MANIFEST.json"
CONFIG_DIR = FACTORY_DIR / "configs"
D3_SUCCESS_TEMPLATE_LOCK = CONFIG_DIR / "holo_session_template_d3_success_v1.lock.json"
LIVE_APPROVAL_ENV = "HOLO_ALLOW_LIVE"
PROOF_ELIGIBLE_HOLO_MODE = "patent_aligned_v4"
LEGACY_HOLO_MODES = {"diagnostic_v3", "full_gov_v4"}
HOLO_MODES = ("diagnostic_v3", "full_gov_v4", "patent_aligned_v4")
HOLO_CONTEXT_PROFILES = ("full_registry", "latest_only")
DEFAULT_HOLO_CONTEXT_PROFILE = "full_registry"
MAX_HOLO_FINAL_REPAIR_ATTEMPTS = 1
DEFAULT_TURN_MAX_TOKENS = 3800
FINAL_SYNTHESIS_MAX_TOKENS = 6000
FINAL_REPAIR_MAX_TOKENS = 5200
HOLO_SESSION_TEMPLATES = ("random", "d3_success_v1")
D3_SUCCESS_HOLO_TURN_MODELS = (
    "google:gemini-3.1-pro-preview",
    "openai:gpt-5.5",
    "anthropic:claude-opus-4-8",
    "google:gemini-3.1-pro-preview",
    "openai:gpt-5.5",
    "anthropic:claude-opus-4-8",
)
D3_SUCCESS_GOV_MODEL = "openai:gpt-5.5"
VALID_CONDITIONS = (
    "HoloFull",
    "HoloMini",
    "SoloFull",
    "SoloMini",
    "holo_build_arch",
    "solo_openai_gpt_5_5",
    "frontier_solo_v1",
    "frontier_holo_v1",
    "mini_solo_v1",
    "mini_holo_v1",
)
FINAL_WORD_MIN = 900
FINAL_WORD_MAX = 1300
FINAL_WORD_TARGET = 1250
FINAL_WORD_PERSUASIVE_MAX = 1500
FINAL_WORD_EXTREME_MAX = 1800
HOLOGOV_C_TENURE_MIN = 7
HOLOGOV_C_TENURE_MAX = 11
PROVIDER_CALLS = 0
ACCEPTED_PROVIDER_CALLS = 0
FAILED_PROVIDER_CALLS = 0
SCORES_GENERATED = 0

SOLO_TURNS = (
    ("initial_decision_brief_draft", "Write an initial decision-grade crisis/action brief draft. This is not final."),
    ("assumption_and_evidence_attack", "Attack the prior draft for unsupported assumptions, weak evidence, missing calculations, source quality flattening, and missing risks."),
    ("contradiction_uncertainty_source_fidelity_pass", "Revise for contradictory evidence, uncertainty, stale or weak source handling, and source-fidelity problems."),
    ("options_risks_operational_usefulness_pass", "Revise for practical options, risks of acting, risks of waiting, stop/go triggers, and operational usefulness for leadership."),
    ("claim_discipline_overclaim_reduction_pass", "Cut unsupported claims, reduce overclaiming, tighten source citations, and prepare a concise final version."),
    ("final_synthesis_900_1500_words", "Return only the final decision-grade crisis/action brief, 900-1,500 body words, target 1,250; use any words over 1,300 only when they materially improve argument power."),
)
HOLO_TURNS = (
    ("initial_decision_brief_drafter", "anthropic:claude-opus-4-8", "Draft a source-grounded initial decision frame covering what is happening, why it matters, and the main options. This is not final."),
    ("assumption_and_evidence_attacker", "google:gemini-3.1-pro-preview", "Attack assumptions, weak evidence, stale claims, missing calculations, and unsupported causal links."),
    ("contradiction_uncertainty_source_fidelity_reviewer", "openai:gpt-5.5", "Stress-test contradictory evidence, source fidelity, source-status boundaries, and uncertainty handling."),
    ("options_operational_usefulness_reviewer", "anthropic:claude-opus-4-8", "Stress-test practical options, risks of acting, risks of waiting, operating gates, and usefulness for leadership."),
    ("claim_discipline_overclaim_reducer", "google:gemini-3.1-pro-preview", "Reduce unsupported claims, identify overclaim risks, and prepare final-brief constraints."),
    ("final_synthesis_author", "openai:gpt-5.5", "Return only the final decision-grade crisis/action brief, 900-1,500 body words, target 1,250; use any words over 1,300 only when they materially improve argument power."),
)
V6_1_ARGUMENT_POWER_GUIDANCE = (
    "Optimize for the locked v6.1 scoring protocol: not just safe compliance, but stronger thinking. "
    "After source fidelity, action-boundary safety, and claim discipline are preserved, argument strength and persuasion are the decisive top-band discriminator. "
    "A merely safe, complete, or well-cited artifact is not enough; the final artifact must be the more convincing and more powerful decision argument. "
    "The final brief must have a sharp central thesis, clean evidence-to-decision argument, persuasive uncertainty handling, "
    "non-generic insights, source synthesis, practical judgment, and explicit handling of the best counterargument. "
    "Do not make the brief longer to sound stronger; use the clean 900-1,300 band when possible and the 1,500-word persuasive ceiling only for decision-useful argument power."
)
FINAL_SYNTHESIS_TRIGGER_TAXONOMY = (
    "In the final synthesis, convert the recommendation into an executable trigger taxonomy: broad-action go/no-go, "
    "narrow/conditional go, hold/escalate, revoke/rollback/stop, and post-action review or follow-up where relevant. "
    "Use packet-specific names when the packet supplies required practical response options."
)
FINAL_REQUIRED_SECTION_PATTERNS = {
    "bottom_line": re.compile(r"(?im)^#{1,3}\s*(?:\d+\.\s*)?(?:bottom line|recommendation|bottom-line)"),
    "risks_of_acting": re.compile(r"(?im)^#{1,3}\s*(?:\d+\.\s*)?risks?\s+of\s+acting"),
    "risks_of_waiting": re.compile(r"(?im)^#{1,3}\s*(?:\d+\.\s*)?risks?\s+of\s+waiting"),
    "next_steps": re.compile(r"(?im)^#{1,3}\s*(?:\d+\.\s*)?(?:recommended\s+)?next\s+steps|trigger\s+taxonomy"),
    "claim_boundaries": re.compile(r"(?im)^#{1,3}\s*(?:\d+\.\s*)?(?:claim\s+boundaries|disclaimer|claim\s+boundaries\s*/\s*disclaimer)"),
}
FINAL_CLEAN_ENDING_RE = re.compile(r"[.!?][\"')\]]*$")
SOURCE_ID_RE = re.compile(r"\bS\d+_[A-Z0-9_]+\b")
ACTIVE_SCORING_LOCK_PATH = FACTORY_DIR / "scoring_policies/ACTIVE_SCORING_PROTOCOL.lock.json"
HARD_FORBIDDEN_JUDGE_VISIBLE_PATTERNS = {
    "holo_label": re.compile(r"\bholo(build|gov|full|mini|_build_arch)?\b", re.IGNORECASE),
    "gpt_label": re.compile(r"\bgpt[-_ ]?5(?:\.5)?\b", re.IGNORECASE),
    "provider_model": re.compile(r"\bprovider_model\b", re.IGNORECASE),
    "token_burn": re.compile(r"\b(token_burn|input_tokens|output_tokens|total_tokens)\b", re.IGNORECASE),
    "architecture_evidence": re.compile(r"\barchitecture_evidence\b", re.IGNORECASE),
    "arch_evidence": re.compile(r"\barch_evidence\b", re.IGNORECASE),
    "run_id": re.compile(r"\brun_id\b", re.IGNORECASE),
    "state_object": re.compile(r"\bstate_object\b", re.IGNORECASE),
    "baton_pass": re.compile(r"\bbaton_pass\b", re.IGNORECASE),
    "artifact_registry": re.compile(r"\bartifact_registry\b", re.IGNORECASE),
}
CONTEXT_SENSITIVE_JUDGE_VISIBLE_PATTERNS = {
    "condition_metadata": re.compile(
        r"\b(condition_id|benchmark_condition|condition_family|holo_condition|solo_condition|generation_condition|condition_manifest|condition_type|model_condition)\b",
        re.IGNORECASE,
    ),
    "internal_metadata": re.compile(
        r"\b(internal_generation|internal_state|internal_label|internal_scaffold|internal_process|internal_run|internal_metadata|builder_internal)\b",
        re.IGNORECASE,
    ),
}


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def active_scoring_protocol() -> dict[str, Any]:
    if not ACTIVE_SCORING_LOCK_PATH.exists():
        return {
            "active_scoring_protocol_id": "unified_artifact_scoring_protocol_v6_structural_epistemic",
            "lock_path": repo_rel(ACTIVE_SCORING_LOCK_PATH),
            "lock_missing": True,
        }
    lock = read_json(ACTIVE_SCORING_LOCK_PATH)
    return {
        "active_scoring_protocol_id": lock.get("active_scoring_protocol_id"),
        "protocol_path": lock.get("protocol_path"),
        "protocol_hash": lock.get("protocol_hash"),
        "schema_path": lock.get("schema_path"),
        "schema_hash": lock.get("schema_hash"),
        "lock_path": lock.get("lock_path"),
        "lock_hash": lock.get("lock_hash"),
    }


def repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def architecture_evidence_summary(evidence_turns: list[dict[str, Any]], precheck: dict[str, Any], holo_mode: str) -> dict[str, Any]:
    role_failures = [
        {"turn": item.get("turn"), "role_compliance": item.get("role_compliance")}
        for item in evidence_turns
        if (item.get("role_compliance") or {}).get("status") != "pass"
    ]
    state_failures = [
        {"turn": item.get("turn"), "state_audit": item.get("state_audit")}
        for item in evidence_turns
        if (item.get("state_audit") or {}).get("status") != "pass"
    ]
    prompt_hash_missing = [
        item.get("turn")
        for item in evidence_turns
        if not item.get("prompt_card_hash")
    ]
    final_completeness_failures = [
        {"turn": item.get("turn"), "final_artifact_completeness": (item.get("role_compliance") or {}).get("final_artifact_completeness")}
        for item in evidence_turns
        if ((item.get("role_compliance") or {}).get("final_artifact_completeness") or {}).get("status") == "fail"
    ]
    deterministic_gate_pass = precheck.get("deterministic_gate_status") in {"pass", "pass_with_word_overage_penalty"}
    proof_eligible = (
        holo_mode == PROOF_ELIGIBLE_HOLO_MODE
        and deterministic_gate_pass
        and not role_failures
        and not state_failures
        and not prompt_hash_missing
        and not final_completeness_failures
    )
    return {
        "proof_credit_eligible": proof_eligible,
        "deterministic_gate_pass": deterministic_gate_pass,
        "role_compliance_all_pass": not role_failures,
        "state_audit_all_pass": not state_failures,
        "prompt_card_hashes_present": not prompt_hash_missing,
        "final_artifact_completeness_pass": not final_completeness_failures,
        "role_compliance_failures": role_failures,
        "state_audit_failures": state_failures,
        "prompt_hash_missing_turns": prompt_hash_missing,
        "final_artifact_completeness_failures": final_completeness_failures,
    }


def scan_judge_visible_text(text: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for label, pattern in HARD_FORBIDDEN_JUDGE_VISIBLE_PATTERNS.items():
        if pattern.search(text):
            findings.append({"term_class": "hard_forbidden", "term": label})
    for label, pattern in CONTEXT_SENSITIVE_JUDGE_VISIBLE_PATTERNS.items():
        if pattern.search(text):
            findings.append({"term_class": "context_sensitive_process_metadata", "term": label})
    return findings


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def final_artifact_completeness(output_text: str, output_meta: dict[str, Any] | None = None) -> dict[str, Any]:
    stripped = output_text.strip()
    failures: list[str] = []
    if not stripped:
        failures.append("empty_final_artifact")

    clean_ending = bool(FINAL_CLEAN_ENDING_RE.search(stripped))
    if not clean_ending:
        failures.append("unclean_or_mid_sentence_ending")

    section_presence = {
        name: bool(pattern.search(stripped))
        for name, pattern in FINAL_REQUIRED_SECTION_PATTERNS.items()
    }
    missing_sections = [name for name, present in section_presence.items() if not present]
    failures.extend(f"missing_final_section:{name}" for name in missing_sections)

    claim_boundary_tail_words = 0
    claim_boundary_match = FINAL_REQUIRED_SECTION_PATTERNS["claim_boundaries"].search(stripped)
    if claim_boundary_match:
        claim_boundary_tail = stripped[claim_boundary_match.end():]
        claim_boundary_tail_words = word_count(claim_boundary_tail)
        if claim_boundary_tail_words < 20:
            failures.append("claim_boundary_section_too_short_or_truncated")

    output_tokens = int((output_meta or {}).get("output_tokens") or 0)
    max_tokens_requested = int((output_meta or {}).get("max_tokens_requested") or 0)
    hit_requested_token_ceiling = bool(output_tokens and max_tokens_requested and output_tokens >= max_tokens_requested)
    if hit_requested_token_ceiling and not clean_ending:
        failures.append("provider_output_hit_max_tokens_with_unclean_ending")

    return {
        "status": "pass" if not failures else "fail",
        "clean_ending": clean_ending,
        "section_presence": section_presence,
        "missing_sections": missing_sections,
        "claim_boundary_tail_words": claim_boundary_tail_words,
        "output_tokens": output_tokens,
        "max_tokens_requested": max_tokens_requested,
        "hit_requested_token_ceiling": hit_requested_token_ceiling,
        "failures": failures,
    }


def excerpt(text: str, limit: int = 900) -> str:
    return re.sub(r"\s+", " ", text).strip()[:limit]


def stable_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def load_suite_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "suite_manifest_missing", "path": str(path), "provider_calls": 0}, indent=2))
    return read_json(path)


def suite_entries_by_packet(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out = {}
    for entry in manifest.get("domains", []):
        p = (REPO_ROOT / entry["packet_dir"]).resolve()
        out[str(p)] = entry
    return out


def resolve_packet_dir(args: argparse.Namespace, manifest: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    entries = manifest.get("domains", [])
    if args.domain:
        matches = [item for item in entries if item.get("domain_id") == args.domain]
        if not matches:
            valid = [item.get("domain_id") for item in entries]
            raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "unknown_domain", "domain": args.domain, "valid_domains": valid, "provider_calls": 0}, indent=2))
        entry = matches[0]
        packet_dir = (REPO_ROOT / entry["packet_dir"]).resolve()
    elif args.packet_dir:
        packet_dir = Path(args.packet_dir)
        if not packet_dir.is_absolute():
            packet_dir = REPO_ROOT / packet_dir
        packet_dir = packet_dir.resolve()
        by_packet = suite_entries_by_packet(manifest)
        entry = by_packet.get(str(packet_dir))
        if entry is None:
            raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "packet_dir_not_in_ten_domain_manifest", "packet_dir": str(packet_dir), "provider_calls": 0}, indent=2))
    else:
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "packet_dir_or_domain_required", "provider_calls": 0}, indent=2))
    return packet_dir, entry


def validate_packet_against_manifest(packet_dir: Path, entry: dict[str, Any]) -> dict[str, Any]:
    required = [
        "task_brief.md",
        "source_packet.json",
        "source_packet.md",
        "source_manifest.json",
        "deterministic_gate_policy.json",
        "blind_packet_manifest.json",
        "contamination_scan_config.json",
        "packet_lock.json",
        "freeze_manifest.json",
        "validate_packet_no_provider.py",
    ]
    missing = [name for name in required if not (packet_dir / name).exists()]
    if missing:
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "missing_packet_files", "missing": missing, "packet_dir": str(packet_dir), "provider_calls": 0}, indent=2))
    lock = read_json(packet_dir / "packet_lock.json")
    hash_errors: list[str] = []
    for rel, expected_hash in (lock.get("locked_files") or {}).items():
        candidate = packet_dir / rel
        if not candidate.exists():
            hash_errors.append(f"missing locked file: {rel}")
        elif sha_file(candidate) != expected_hash:
            hash_errors.append(f"locked file hash mismatch: {rel}")
    checks = {
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "packet_lock_hash": sha_file(packet_dir / "packet_lock.json"),
        "freeze_manifest_hash": sha_file(packet_dir / "freeze_manifest.json"),
    }
    for key, actual in checks.items():
        expected = entry.get(key)
        if expected and actual != expected:
            hash_errors.append(f"manifest {key} mismatch: expected {expected} actual {actual}")
    if hash_errors:
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "packet_manifest_validation_failed", "errors": hash_errors, "provider_calls": 0}, indent=2))
    return {"lock": lock, "hashes": checks}


def load_configs() -> dict[str, dict[str, Any]]:
    configs: dict[str, dict[str, Any]] = {}
    for path in sorted(CONFIG_DIR.glob("*.json")):
        cfg = read_json(path)
        configs[cfg["config_id"]] = cfg
        for alias in cfg.get("condition_aliases", []):
            configs[alias] = cfg
    return configs


def config_for_condition(condition: str, configs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if condition not in configs:
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "unknown_condition_or_config", "condition": condition, "provider_calls": 0}, indent=2))
    return configs[condition]


def enforce_live_guard(live: bool) -> None:
    if not live:
        return
    if os.getenv(LIVE_APPROVAL_ENV) != "1":
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_LIVE_FAIL_CLOSED", "reason": f"live mode requires {LIVE_APPROVAL_ENV}=1 in addition to --live", "provider_calls": 0}, indent=2))


def enforce_holo_mode_guard(holo_mode: str, diagnostic_legacy_holo_mode: bool) -> None:
    if holo_mode in LEGACY_HOLO_MODES and not diagnostic_legacy_holo_mode:
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "legacy_holo_mode_requires_explicit_diagnostic_flag", "holo_mode": holo_mode, "required_flag": "--diagnostic-legacy-holo-mode", "provider_calls": 0}, indent=2))


def provider_models_for_config(config: dict[str, Any], holo_mode: str) -> list[str]:
    if config.get("condition_type") == "solo":
        return [item["provider_model"] for item in config.get("model_pool", []) if item.get("provider_model")]
    if config.get("condition_type") == "holo":
        return unique_provider_models(holo_agent_models(config) + governor_model_pool(config))
    return []


def unique_provider_models(models: list[str]) -> list[str]:
    return list(dict.fromkeys(models))


def holo_agent_models(config: dict[str, Any]) -> list[str]:
    models = unique_provider_models([item["provider_model"] for item in config.get("model_pool", []) if item.get("provider_model")])
    if len(models) != 3:
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
            "reason": "holo_config_requires_three_holo_agent_models",
            "config_id": config.get("config_id"),
            "expected_models": 3,
            "actual_models": len(models),
            "provider_calls": 0,
        }, indent=2))
    return models


def governor_model_pool(config: dict[str, Any]) -> list[str]:
    return unique_provider_models(config.get("governor_model_pool") or holo_agent_models(config))


def session_template_lock_info(template_id: str) -> dict[str, Any] | None:
    if template_id != "d3_success_v1":
        return None
    if not D3_SUCCESS_TEMPLATE_LOCK.exists():
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
            "reason": "holo_session_template_lock_missing",
            "template_id": template_id,
            "expected_lock_path": repo_rel(D3_SUCCESS_TEMPLATE_LOCK),
            "provider_calls": 0,
        }, indent=2))
    lock = read_json(D3_SUCCESS_TEMPLATE_LOCK)
    if lock.get("template_id") != template_id:
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
            "reason": "holo_session_template_lock_id_mismatch",
            "template_id": template_id,
            "lock_template_id": lock.get("template_id"),
            "lock_path": repo_rel(D3_SUCCESS_TEMPLATE_LOCK),
            "provider_calls": 0,
        }, indent=2))
    return {
        "holo_session_template_lock_path": repo_rel(D3_SUCCESS_TEMPLATE_LOCK),
        "holo_session_template_lock_hash": sha_file(D3_SUCCESS_TEMPLATE_LOCK),
    }


def validate_fixed_holo_models(config: dict[str, Any], *, turn_models: tuple[str, ...], governor_model: str) -> None:
    agents = set(holo_agent_models(config))
    gov_pool = set(governor_model_pool(config))
    missing_agents = [model for model in turn_models if model not in agents]
    if missing_agents or governor_model not in gov_pool:
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
            "reason": "fixed_holo_session_template_models_not_in_config_pool",
            "config_id": config.get("config_id"),
            "missing_turn_models": missing_agents,
            "governor_model": governor_model,
            "governor_model_in_pool": governor_model in gov_pool,
            "provider_calls": 0,
        }, indent=2))


def randomized_holo_session_plan(config: dict[str, Any], *, run_id: str, packet_hash: str, turn_count: int, session_template: str = "random") -> dict[str, Any]:
    if session_template == "d3_success_v1":
        if turn_count != len(D3_SUCCESS_HOLO_TURN_MODELS):
            raise SystemExit(json.dumps({
                "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
                "reason": "d3_success_template_turn_count_mismatch",
                "expected_turns": len(D3_SUCCESS_HOLO_TURN_MODELS),
                "actual_turns": turn_count,
                "provider_calls": 0,
            }, indent=2))
        validate_fixed_holo_models(config, turn_models=D3_SUCCESS_HOLO_TURN_MODELS, governor_model=D3_SUCCESS_GOV_MODEL)
        agents = holo_agent_models(config)
        gov_pool = governor_model_pool(config)
        lock_info = session_template_lock_info(session_template) or {}
        return {
            "selection_seed": "d3_success_v1_fixed_template",
            "selection_source": "fixed_successful_d3_holo_choreography",
            **lock_info,
            "run_id": run_id,
            "packet_hash": packet_hash,
            "cohort_name": config.get("cohort_name"),
            "config_id": config.get("config_id"),
            "hologov_profile": config.get("hologov_profile"),
            "holo_session_template": session_template,
            "holo_agent_pool": agents,
            "holo_agent_selection_policy": "fixed_d3_success_v1_turn_order",
            "holo_agent_turn_models": list(D3_SUCCESS_HOLO_TURN_MODELS),
            "hologov_model_pool": gov_pool,
            "hologov_selection_policy": "fixed_d3_success_v1_governor",
            "hologov_tenure_policy": {
                "min_turns": HOLOGOV_C_TENURE_MIN,
                "max_turns": HOLOGOV_C_TENURE_MAX,
                "swap_policy": "disabled_for_fixed_template",
            },
            "hologov_schedule": [
                {
                    "start_turn": 1,
                    "end_turn": turn_count,
                    "selected_tenure_turns": 7,
                    "governor_model": D3_SUCCESS_GOV_MODEL,
                }
            ],
            "final_synthesis_model": D3_SUCCESS_HOLO_TURN_MODELS[-1],
            "final_synthesis_model_policy": "fixed_d3_success_v1_final_writer",
        }
    seed = secrets.token_hex(16)
    rng = random.Random(seed)
    agents = holo_agent_models(config)
    agent_rotation = agents[:]
    rng.shuffle(agent_rotation)
    turn_models = [agent_rotation[index % len(agent_rotation)] for index in range(turn_count)]
    final_synthesis_model = preferred_holo_final_model(config)
    if turn_models:
        turn_models[-1] = final_synthesis_model
    gov_pool = governor_model_pool(config)
    gov_segments: list[dict[str, Any]] = []
    start_turn = 1
    current_model: str | None = None
    while start_turn <= turn_count:
        candidates = [model for model in gov_pool if model != current_model] or gov_pool
        current_model = rng.choice(candidates)
        tenure = rng.randint(HOLOGOV_C_TENURE_MIN, HOLOGOV_C_TENURE_MAX)
        end_turn = min(turn_count, start_turn + tenure - 1)
        gov_segments.append({
            "start_turn": start_turn,
            "end_turn": end_turn,
            "selected_tenure_turns": tenure,
            "governor_model": current_model,
        })
        start_turn = end_turn + 1
    return {
        "selection_seed": seed,
        "selection_source": "python_secrets_token_hex_16",
        "run_id": run_id,
        "packet_hash": packet_hash,
        "cohort_name": config.get("cohort_name"),
        "config_id": config.get("config_id"),
        "hologov_profile": config.get("hologov_profile"),
        "holo_agent_pool": agents,
        "holo_agent_selection_policy": "random_permutation_of_three_agents_repeated_for_turn_budget",
        "holo_agent_turn_models": turn_models,
        "final_synthesis_model": final_synthesis_model,
        "final_synthesis_model_policy": "configured_or_openai_model_from_holo_agent_pool",
        "hologov_model_pool": gov_pool,
        "hologov_selection_policy": "random_governor_from_hologov_model_pool",
        "hologov_tenure_policy": {
            "min_turns": HOLOGOV_C_TENURE_MIN,
            "max_turns": HOLOGOV_C_TENURE_MAX,
            "swap_policy": "after_tenure_select_random_different_model_from_pool_when_possible",
        },
        "hologov_schedule": gov_segments,
    }


def holo_turn_plan(session_plan: dict[str, Any]) -> list[tuple[str, str, str]]:
    models = session_plan.get("holo_agent_turn_models", [])
    if len(models) != len(HOLO_TURNS):
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
            "reason": "holo_session_plan_requires_one_model_per_turn",
            "expected_turns": len(HOLO_TURNS),
            "actual_models": len(models),
            "provider_calls": 0,
        }, indent=2))
    return [(role, models[index], objective) for index, (role, _default_model, objective) in enumerate(HOLO_TURNS)]


def preferred_holo_final_model(config: dict[str, Any]) -> str:
    models = holo_agent_models(config)
    configured = config.get("final_synthesis_model")
    if configured:
        if configured not in models:
            raise SystemExit(json.dumps({
                "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
                "reason": "final_synthesis_model_not_in_holo_agent_pool",
                "config_id": config.get("config_id"),
                "final_synthesis_model": configured,
                "holo_agent_pool": models,
                "provider_calls": 0,
            }, indent=2))
        return configured
    for model in models:
        if model.startswith("openai:"):
            return model
    return models[-1]


def ensure_provider_env(models: list[str]) -> None:
    missing: dict[str, str] = {}
    for provider_model_name in models:
        provider, _model = provider_model(provider_model_name)
        env_name = PROVIDER_ENV.get(provider)
        if not env_name:
            missing[provider_model_name] = "unknown_provider"
        elif not os.getenv(env_name):
            missing[provider_model_name] = env_name
    if missing:
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_LIVE_FAIL_CLOSED", "reason": "missing_provider_environment", "missing": missing, "provider_calls": 0}, indent=2))


def source_ids(source_packet: dict[str, Any]) -> set[str]:
    return {src.get("source_id") for src in source_packet.get("sources", []) if src.get("source_id")}


def required_practical_response_options(source_packet: dict[str, Any]) -> list[str]:
    options = source_packet.get("practical_response_options_required")
    if isinstance(options, list):
        return [str(item) for item in options if str(item).strip()]
    return []


def load_packet_surfaces(packet_dir: Path) -> dict[str, Any]:
    return {
        "task_brief": (packet_dir / "task_brief.md").read_text(encoding="utf-8"),
        "source_packet_md": (packet_dir / "source_packet.md").read_text(encoding="utf-8"),
        "source_packet_json": read_json(packet_dir / "source_packet.json"),
        "deterministic_gate_policy": read_json(packet_dir / "deterministic_gate_policy.json"),
    }


def build_base_system() -> str:
    return (
        "You are producing a decision-grade crisis/action brief from a frozen benchmark packet. "
        "Use only the provided task brief and frozen source packet. Do not browse. Do not infer model identity. "
        "Separate facts from inference, preserve source boundaries, compare options, and include risks of acting and waiting. "
        "The clean final artifact band is 900-1,300 words, but the persuasive ceiling is 1,500 words when the extra space materially improves the argument. "
        "Target about 1,250 words. Under v6.1, words over 1,300 receive a scoring penalty rather than automatic failure; do not exceed 1,500 unless explicitly instructed. "
        f"{V6_1_ARGUMENT_POWER_GUIDANCE}"
    )


def packet_context(task_brief: str, source_packet_md: str) -> str:
    return (
        "FROZEN TASK BRIEF\n"
        "=================\n"
        f"{task_brief}\n\n"
        "FROZEN SOURCE PACKET\n"
        "====================\n"
        f"{source_packet_md}\n"
    )


def call_model(provider_model_name: str, *, system: str, user: str, max_tokens: int, timeout: int) -> dict[str, Any]:
    global PROVIDER_CALLS, ACCEPTED_PROVIDER_CALLS, FAILED_PROVIDER_CALLS
    provider, model = provider_model(provider_model_name)
    PROVIDER_CALLS += 1
    try:
        out = call_provider(provider, system=system, user=user, max_tokens=max_tokens, timeout=timeout, model_override=model)
    except ProviderCallError:
        FAILED_PROVIDER_CALLS += 1
        raise
    ACCEPTED_PROVIDER_CALLS += 1
    out["provider_model"] = provider_model_name
    return out


def deterministic_gate_precheck(packet_dir: Path, artifact_text: str) -> dict[str, Any]:
    gate = read_json(packet_dir / "deterministic_gate_policy.json")
    word_gate = gate.get("layer_1_deterministic_gate", {}).get("artifact_body_word_count", {})
    minimum = int(word_gate.get("min", FINAL_WORD_MIN))
    maximum = int(word_gate.get("max", FINAL_WORD_MAX))
    count = word_count(artifact_text)
    overage_words = max(0, count - maximum)
    word_count_penalty_points = round(overage_words * 0.03, 4)
    if minimum <= count <= maximum:
        status = "pass"
        proof_eligible_if_failed = False
    elif maximum < count <= FINAL_WORD_PERSUASIVE_MAX:
        status = "pass_with_word_overage_penalty"
        proof_eligible_if_failed = True
    else:
        status = "fail"
        proof_eligible_if_failed = False
    return {
        "artifact_body_word_count": count,
        "word_count_gate": word_gate,
        "clean_word_count_max": maximum,
        "persuasive_word_count_max": FINAL_WORD_PERSUASIVE_MAX,
        "extreme_word_count_max": FINAL_WORD_EXTREME_MAX,
        "word_count_overage_words": overage_words,
        "word_count_penalty_points": word_count_penalty_points,
        "deterministic_gate_status": status,
        "proof_credit_eligible_if_failed": proof_eligible_if_failed,
        "word_count_policy_note": "Over clean max is scoring-penalized under v6.1 up to the persuasive ceiling; under minimum or above persuasive ceiling remains fail-closed.",
        "provider_calls": PROVIDER_CALLS,
    }


def run_dir_for(packet_dir: Path, run_id: str) -> Path:
    return packet_dir / "runs" / run_id


def condition_dir_for(packet_dir: Path, run_id: str, condition: str) -> Path:
    return run_dir_for(packet_dir, run_id) / condition


def write_prompt_and_output(condition_dir: Path, turn_index: int, prompt_text: str, output: dict[str, Any]) -> dict[str, str]:
    prompt_path = condition_dir / "prompt_cards" / f"turn_{turn_index:03d}.md"
    output_path = condition_dir / "raw_outputs" / f"turn_{turn_index:03d}.json"
    write_text(prompt_path, prompt_text)
    write_json(output_path, output)
    return {"prompt_path": repo_rel(prompt_path), "prompt_hash": sha_file(prompt_path), "raw_output_path": repo_rel(output_path), "raw_output_hash": sha_file(output_path)}


def write_named_prompt_and_output(condition_dir: Path, name: str, prompt_text: str, output: dict[str, Any]) -> dict[str, str]:
    prompt_path = condition_dir / "prompt_cards" / f"{name}.md"
    output_path = condition_dir / "raw_outputs" / f"{name}.json"
    write_text(prompt_path, prompt_text)
    write_json(output_path, output)
    return {"prompt_path": repo_rel(prompt_path), "prompt_hash": sha_file(prompt_path), "raw_output_path": repo_rel(output_path), "raw_output_hash": sha_file(output_path)}


def run_solo(packet_dir: Path, run_id: str, config: dict[str, Any], timeout: int) -> dict[str, Any]:
    condition = "solo_openai_gpt_5_5" if "solo_openai_gpt_5_5" in config.get("condition_aliases", []) else config["config_id"]
    condition_dir = condition_dir_for(packet_dir, run_id, condition)
    surfaces = load_packet_surfaces(packet_dir)
    model = config["model_pool"][0]["provider_model"]
    prior = ""
    turn_records = []
    base = packet_context(surfaces["task_brief"], surfaces["source_packet_md"])
    for index, (role, objective) in enumerate(SOLO_TURNS, start=1):
        final_instruction = "Return only the final artifact." if index == len(SOLO_TURNS) else "Return a draft, critique, or revision notes for the next pass."
        user = f"{base}\n\nTURN ROLE: {role}\nTURN OBJECTIVE: {objective}\n{final_instruction}\n\nPRIOR DRAFT OR NOTES\n====================\n{prior or '[none]'}\n"
        prompt_text = f"SYSTEM:\n{build_base_system()}\n\nUSER:\n{user}"
        out = call_model(model, system=build_base_system(), user=user, max_tokens=3600, timeout=timeout)
        io = write_prompt_and_output(condition_dir, index, prompt_text, out)
        prior = out["text"].strip()
        turn_records.append({"turn": index, "role": role, "model": model, "input_tokens": out.get("input_tokens"), "output_tokens": out.get("output_tokens"), **io})
    artifact_text = prior
    artifact_path = condition_dir / "artifact.md"
    write_text(artifact_path, artifact_text)
    precheck = deterministic_gate_precheck(packet_dir, artifact_text)
    write_json(condition_dir / "deterministic_gate_precheck.json", precheck)
    metadata = {
        "condition": condition,
        "config_id": config["config_id"],
        "cohort_name": config.get("cohort_name"),
        "condition_type": "solo",
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "artifact_path": repo_rel(artifact_path),
        "artifact_hash": sha_file(artifact_path),
        "turns": turn_records,
        "provider_calls": len(turn_records),
        "input_tokens": sum(int(item.get("input_tokens") or 0) for item in turn_records),
        "output_tokens": sum(int(item.get("output_tokens") or 0) for item in turn_records),
        "proof_credit_eligible": False,
        "baseline_eligible": True,
        "scores_generated": 0,
    }
    write_json(condition_dir / "artifact_metadata.json", metadata)
    return metadata


def role_compliance(role: str, output_text: str, final: bool, output_meta: dict[str, Any] | None = None) -> dict[str, Any]:
    lowered = output_text.lower()
    praise_only = len(re.findall(r"\b(strong|excellent|good|solid)\b", lowered)) >= 3 and not re.search(r"\b(missing|unsupported|risk|weak|contradict|uncertain|revise|option)\b", lowered)
    role_behaviors: dict[str, dict[str, str]] = {
        "initial_decision_brief_drafter": {
            "decision_frame": r"\b(recommend|decision|bottom line|do not|approve|deny|block|escalate|conditional)",
            "options": r"\b(option|path|alternative|fallback|response)",
            "source_grounding": r"\b(source|packet|case fact|frozen|evidence|supports|does not show|not provided)",
        },
        "assumption_and_evidence_attacker": {
            "assumption_attack": r"\b(assumption|assumes|overstate|not shown|does not show|not prove|inference|unsupported)",
            "weak_or_missing_support": r"\b(weak|missing|lacks|incomplete|not provided|no evidence|not establish|does not prove)",
            "revision_pressure": r"\b(final should|should not|tighten|revise|frame|avoid|must include)",
        },
        "contradiction_uncertainty_source_fidelity_reviewer": {
            "contradiction_or_tension": r"\b(contradict|conflict|tension|however|but|although)",
            "uncertainty": r"\b(uncertain|uncertainty|not shown|not provided|cannot conclude|does not prove|unknown)",
            "source_fidelity": r"\b(source|source id|packet|cited|frozen|stale|weak)",
        },
        "options_operational_usefulness_reviewer": {
            "options": r"\b(option|path|trigger|go|no-go|hold|escalate|fallback|response)",
            "risk": r"\b(risk|exposure|failure|harm|cost)",
            "waiting_or_sequence": r"\b(wait|waiting|sequence|window|timeline|next step|within)",
        },
        "claim_discipline_overclaim_reducer": {
            "overclaim_reduction": r"\b(overclaim|avoid|reduce|replace|bounded|tighten|soften|do not assert|should not imply)",
            "unsupported_or_not_proven": r"\b(unsupported|not shown|not provided|does not prove|no evidence|not establish|cannot conclude)",
            "claim_boundary": r"\b(claim|boundary|source-supported|packet supports|final language|recommended final)",
        },
        "final_synthesis_author": {
            "options": r"\b(option|trigger|go|no-go|hold|escalate|fallback|response)",
            "risk": r"\b(risk|exposure|failure|harm|waiting|acting)",
            "claim_boundary": r"\b(claim|boundary|does not prove|not shown|not provided|disclaimer|uncertainty)",
        },
    }
    expected_behaviors = role_behaviors.get(role, {})
    missing_terms = [name for name, pattern in expected_behaviors.items() if not re.search(pattern, lowered)]
    result = {
        "status": "pass" if not praise_only and not missing_terms else "fail",
        "praise_only": praise_only,
        "missing_role_behaviors": missing_terms,
    }
    if final:
        wc = word_count(output_text)
        result["final_word_count"] = wc
        if FINAL_WORD_MIN <= wc <= FINAL_WORD_MAX:
            result["final_word_band_status"] = "pass"
        elif FINAL_WORD_MAX < wc <= FINAL_WORD_PERSUASIVE_MAX:
            result["final_word_band_status"] = "pass_with_word_overage_penalty"
            result["word_count_penalty_points"] = round((wc - FINAL_WORD_MAX) * 0.03, 4)
        else:
            result["final_word_band_status"] = "fail"
        completeness = final_artifact_completeness(output_text, output_meta)
        result["final_artifact_completeness"] = completeness
        if completeness["status"] != "pass":
            result["status"] = "fail"
    return result


def state_audit(output_text: str, state: dict[str, Any], allowed_source_ids: set[str], packet_hash: str, registry: dict[str, Any]) -> dict[str, Any]:
    cited = set(SOURCE_ID_RE.findall(output_text))
    invented = sorted(cited - allowed_source_ids)
    checks = {
        "critical_constraints_present": bool(state.get("CRITICAL_CONSTRAINTS")),
        "packet_hash_preserved": state.get("PACKET_HASH") == packet_hash,
        "invented_source_ids": invented,
        "artifact_registry_present": bool(registry.get("artifacts")),
        "source_boundaries_preserved": "browse" not in output_text.lower(),
    }
    checks["status"] = "pass" if checks["critical_constraints_present"] and checks["packet_hash_preserved"] and not invented and checks["artifact_registry_present"] and checks["source_boundaries_preserved"] else "fail"
    return checks


def retrieved_content_for(ids: list[str], registry: dict[str, Any]) -> str:
    chunks = []
    for artifact_id in ids:
        item = registry.get("artifacts", {}).get(artifact_id)
        if not item:
            chunks.append(f"[MISSING REGISTRY ARTIFACT: {artifact_id}]")
            continue
        chunks.append(f"ARTIFACT_ID: {artifact_id}\nSTATUS: {item.get('status')}\nSHA256: {item.get('hash')}\nCONTENT:\n{item.get('content', '')}")
    return "\n\n---\n\n".join(chunks)


def build_context_governor_instructions(hologov_profile: str | None, context_profile: str) -> str:
    profile = hologov_profile or "HoloGov-C"
    return (
        f"CONTEXT GOVERNOR PROFILE: {profile}\n"
        f"HOLO CONTEXT PROFILE: {context_profile}\n"
        "Maintain the canonical STATE_OBJECT before and after each model turn. "
        "Preserve critical constraints, packet hash, source boundaries, settled decisions, unresolved tensions, and the Artifact Registry. "
        "Generate the BATON_PASS for the selected model and adversarial role. "
        "Require retrieve-by-ID behavior from the Artifact Registry before generation. "
        "After each output, audit role compliance, source-boundary preservation, invented source IDs, packet-hash preservation, and final word-band status when applicable. "
        "Do not decide from model fluency; preserve claim discipline and action-boundary uncertainty."
    )


def gov_notes_for_turn(index: int, role: str, final: bool, retrieved_ids: list[str], state: dict[str, Any], registry: dict[str, Any], context_profile: str) -> list[str]:
    notes = [
        "Governor-controlled state is authoritative for this turn.",
        f"Turn {index} role is {role}; enforce the role-specific behavior rather than generic praise or summary.",
        f"Retrieved artifact IDs are Gov-selected from the Artifact Registry: {', '.join(retrieved_ids)}.",
        f"Holo context profile is {context_profile}; full_registry means all prior registered turn artifacts are retrieved, not only the latest note.",
        "Preserve the frozen packet source boundary; do not browse and do not invent approvals, clearances, or source IDs.",
        "If citing source IDs, copy exact source_id strings from the frozen source packet; do not abbreviate or rename them.",
        "Keep risks of acting, risks of waiting, practical options, and claim boundaries visible.",
        V6_1_ARGUMENT_POWER_GUIDANCE,
    ]
    required_options = state.get("REQUIRED_PRACTICAL_RESPONSE_OPTIONS") or []
    if required_options:
        notes.append("Packet required practical response options must be preserved as exact option labels, then explained in plain English.")
        notes.append("Required option labels: " + "; ".join(str(item) for item in required_options))
    if state.get("SETTLED_DECISIONS"):
        notes.append("Do not contradict settled decisions unless explicitly identifying a source-grounded reason to reopen them.")
    if final:
        notes.append("Final synthesis clean band is 900-1,300 body words, target 1,250; persuasive ceiling is 1,500 when extra words materially improve argument power.")
        notes.append("Words over 1,300 carry a v6.1 scoring penalty, so use overage only for better thesis, trigger taxonomy, counterargument handling, or insight density.")
        notes.append(FINAL_SYNTHESIS_TRIGGER_TAXONOMY)
        notes.append("Final synthesis must explicitly handle the strongest counterargument and explain why the recommended path is still better or conditional.")
    else:
        notes.append("This is an intermediate registered artifact; produce role-specific draft, critique, or constraints for the next turn.")
    notes.append(f"Registry currently contains {len(registry.get('artifacts', {}))} artifacts; all retrieved content must be traceable to registry IDs and hashes.")
    return notes


def retrieved_ids_for_holo_turn(registry: dict[str, Any], context_profile: str) -> list[str]:
    retrieved_ids = ["TASK_BRIEF", "SOURCE_PACKET_MD"]
    prior_ids = [key for key in registry["artifacts"] if key.startswith("TURN_")]
    if not prior_ids:
        return retrieved_ids
    if context_profile == "latest_only":
        return retrieved_ids + [prior_ids[-1]]
    if context_profile == "full_registry":
        return retrieved_ids + prior_ids
    raise ValueError(f"unsupported Holo context profile: {context_profile}")


def run_holo(packet_dir: Path, run_id: str, config: dict[str, Any], timeout: int, holo_mode: str, holo_context_profile: str, holo_session_template: str) -> dict[str, Any]:
    condition = "holo_build_arch" if "holo_build_arch" in config.get("condition_aliases", []) else config["config_id"]
    condition_dir = condition_dir_for(packet_dir, run_id, condition)
    surfaces = load_packet_surfaces(packet_dir)
    packet_hash = sha_file(packet_dir / "source_packet.json")
    session_plan = randomized_holo_session_plan(config, run_id=run_id, packet_hash=packet_hash, turn_count=len(HOLO_TURNS), session_template=holo_session_template)
    turn_plan = holo_turn_plan(session_plan)
    allowed_ids = source_ids(surfaces["source_packet_json"])
    required_options = required_practical_response_options(surfaces["source_packet_json"])
    registry = {
        "artifacts": {
            "TASK_BRIEF": {"status": "PINNED", "hash": sha_text(surfaces["task_brief"]), "source_reference": repo_rel(packet_dir / "task_brief.md"), "content": surfaces["task_brief"]},
            "SOURCE_PACKET_MD": {"status": "PINNED", "hash": sha_text(surfaces["source_packet_md"]), "source_reference": repo_rel(packet_dir / "source_packet.md"), "content": surfaces["source_packet_md"]},
        }
    }
    context_governor_instructions = build_context_governor_instructions(config.get("hologov_profile"), holo_context_profile)
    state = {
        "USER_GOAL": "Produce a decision-grade crisis/action brief from the frozen packet.",
        "LATEST_INPUT_SUMMARY": surfaces["source_packet_json"].get("decision_question") or surfaces["source_packet_json"].get("crisis_frame"),
        "CRITICAL_CONSTRAINTS": [
            "Use only the frozen task brief and source packet; no browsing.",
            "Final artifact body must be 900-1,300 words, target 1,100.",
            "Separate source facts from inference and preserve claim boundaries.",
            "No proof credit if deterministic gate fails.",
            "Full-architecture Holo context must retrieve pinned sources and registered prior artifacts by ID before every generation turn.",
            "Optimize the final artifact for v6.1 Structural/Epistemic + Argument Power scoring, including a sharp thesis, trigger taxonomy, counterargument handling, and high insight density.",
            "If the packet supplies required practical response options, preserve the exact option labels in the final artifact and explain them.",
        ],
        "PACKET_HASH": packet_hash,
        "ROLLING_SUMMARY": "No model turns completed yet.",
        "SETTLED_DECISIONS": [],
        "ARTIFACTS_REGISTRY": {"artifact_ids": list(registry["artifacts"].keys())},
        "REQUIRED_TOOLS": [],
        "REQUIRED_PRACTICAL_RESPONSE_OPTIONS": required_options,
        "BATON_PASS": {},
        "GOV_NOTES": [
            "Context Governor initialized the canonical state and pinned frozen task/source packet artifacts.",
            "Architecture evidence is internal only and must never be included in judge-visible packets.",
            "Argument power is a first-class quality target: the final artifact should be the strongest usable decision argument, not merely a safe source summary.",
        ],
    }
    evidence_turns = []
    turn_records = []
    final_repair_attempts: list[dict[str, Any]] = []
    final_text = ""
    for index, (role, model, objective) in enumerate(turn_plan, start=1):
        final = index == len(turn_plan)
        retrieved_ids = retrieved_ids_for_holo_turn(registry, holo_context_profile)
        gov_notes = gov_notes_for_turn(index, role, final, retrieved_ids, state, registry, holo_context_profile)
        baton = {
            "next_model": model,
            "adversarial_role": role,
            "focus_area": objective,
            "unresolved_tensions": ["source support", "risks of acting", "risks of waiting", "claim boundaries"],
            "retrieved_artifact_ids": retrieved_ids,
            "required_output_behavior": "final artifact only" if final else "role-specific draft or critique for registry update",
            "holo_context_profile": holo_context_profile,
            "gov_notes": gov_notes,
        }
        state["BATON_PASS"] = baton
        state["GOV_NOTES"] = gov_notes
        state["ARTIFACTS_REGISTRY"] = {"artifact_ids": list(registry["artifacts"].keys())}
        state_json = stable_json(state)
        baton_json = stable_json(baton)
        registry_json = stable_json({k: {kk: vv for kk, vv in v.items() if kk != "content"} for k, v in registry["artifacts"].items()})
        gov_notes_json = stable_json(gov_notes)
        retrieved = retrieved_content_for(retrieved_ids, registry)
        required_options_text = "\n".join(f"- {option}" for option in required_options) if required_options else "[none supplied]"
        user = (
            "CONTEXT_GOVERNOR_INSTRUCTIONS\n=============================\n"
            f"{context_governor_instructions}\n\nCONTEXT_GOVERNOR_INSTRUCTIONS_SHA256: {sha_text(context_governor_instructions)}\n\n"
            "CANONICAL STATE_OBJECT\n======================\n"
            f"{state_json}\n\nSTATE_OBJECT_SHA256: {sha_text(state_json)}\n\n"
            "GOV_NOTES\n=========\n"
            f"{gov_notes_json}\n\nGOV_NOTES_SHA256: {sha_text(gov_notes_json)}\n\n"
            "BATON_PASS\n==========\n"
            f"{baton_json}\n\nBATON_PASS_SHA256: {sha_text(baton_json)}\n\n"
            "ARTIFACTS_REGISTRY\n==================\n"
            f"{registry_json}\n\nARTIFACTS_REGISTRY_SHA256: {sha_text(registry_json)}\n\n"
            "RETRIEVED PINNED SOURCES AND ARTIFACTS\n======================================\n"
            f"{retrieved}\n\n"
            "ADVERSARIAL ROLE INSTRUCTION\n============================\n"
            f"Role: {role}\nObjective: {objective}\n"
        )
        if final:
            user += (
                "\nFINAL SYNTHESIS QUALITY BAR\n===========================\n"
                "Return only the final decision-grade crisis/action brief. Clean body word band is 900-1,300; persuasive ceiling is 1,500; target about 1,250. "
                "Words over 1,300 carry a v6.1 scoring penalty, so use them only when they materially improve argument strength, persuasion, trigger taxonomy, or insight density. "
                "If over 1,500, revise shorter before final answer.\n"
                f"{V6_1_ARGUMENT_POWER_GUIDANCE}\n"
                f"{FINAL_SYNTHESIS_TRIGGER_TAXONOMY}\n"
                "Include the strongest counterargument or temptation for the opposite action, then explain why the recommended path is safer, stronger, or conditional.\n"
                "Use exact source IDs when citing frozen sources. Do not abbreviate source IDs.\n"
                "Preserve claim boundaries, but do not let cautious wording make the brief generic or weak.\n"
                "If the packet supplies required practical response options, include the exact option labels below and then explain them:\n"
                f"{required_options_text}\n"
            )
        prompt_text = f"SYSTEM:\n{build_base_system()}\n\nUSER:\n{user}"
        max_tokens = FINAL_SYNTHESIS_MAX_TOKENS if final else DEFAULT_TURN_MAX_TOKENS
        out = call_model(model, system=build_base_system(), user=user, max_tokens=max_tokens, timeout=timeout)
        io = write_prompt_and_output(condition_dir, index, prompt_text, out)
        output_text = out["text"].strip()
        artifact_source_io = io
        artifact_output_meta = out
        repair_turn_records: list[dict[str, Any]] = []
        turn_repair_attempts: list[dict[str, Any]] = []
        if final:
            initial_final_word_count = word_count(output_text)
            initial_completeness = final_artifact_completeness(output_text, out)
            final_quality_failures = []
            if not (FINAL_WORD_MIN <= initial_final_word_count <= FINAL_WORD_PERSUASIVE_MAX):
                final_quality_failures.append("word_band_failure")
            final_quality_failures.extend(initial_completeness["failures"])
            if final_quality_failures:
                for repair_attempt in range(1, MAX_HOLO_FINAL_REPAIR_ATTEMPTS + 1):
                    repair_user = (
                        "FINAL_ARTIFACT_COMPLETENESS_REPAIR\n"
                        "==================================\n"
                        "The final synthesis output failed final artifact quality checks. "
                        "Return only a corrected final decision-grade crisis/action brief, 900-1,500 body words, target 1,250. "
                        "Words over 1,300 are allowed only when they materially improve argument strength, persuasion, trigger taxonomy, or insight density. "
                        "Do not add commentary about this repair. Use only the frozen packet and registered artifacts below. "
                        "Preserve source boundaries, calculations, practical options, risks of acting, risks of waiting, next steps, and claim boundaries. "
                        "The final answer must end cleanly with a complete sentence and a complete claim-boundary/disclaimer section.\n\n"
                        f"{V6_1_ARGUMENT_POWER_GUIDANCE}\n"
                        f"{FINAL_SYNTHESIS_TRIGGER_TAXONOMY}\n"
                        "Keep exact required practical response option labels if supplied, and retain the strongest counterargument handling.\n\n"
                        f"FAILED_FINAL_WORD_COUNT: {initial_final_word_count}\n\n"
                        f"FINAL_QUALITY_FAILURES: {stable_json(final_quality_failures)}\n\n"
                        f"FINAL_COMPLETENESS_AUDIT: {stable_json(initial_completeness)}\n\n"
                        "CONTEXT_GOVERNOR_INSTRUCTIONS\n=============================\n"
                        f"{context_governor_instructions}\n\n"
                        "CANONICAL STATE_OBJECT\n======================\n"
                        f"{state_json}\n\nSTATE_OBJECT_SHA256: {sha_text(state_json)}\n\n"
                        "GOV_NOTES\n=========\n"
                        f"{gov_notes_json}\n\nGOV_NOTES_SHA256: {sha_text(gov_notes_json)}\n\n"
                        "BATON_PASS\n==========\n"
                        f"{baton_json}\n\nBATON_PASS_SHA256: {sha_text(baton_json)}\n\n"
                        "ARTIFACTS_REGISTRY\n==================\n"
                        f"{registry_json}\n\nARTIFACTS_REGISTRY_SHA256: {sha_text(registry_json)}\n\n"
                        "RETRIEVED PINNED SOURCES AND ARTIFACTS\n======================================\n"
                        f"{retrieved}\n\n"
                        "REQUIRED PRACTICAL RESPONSE OPTION LABELS\n=========================================\n"
                        f"{required_options_text}\n\n"
                        "FAILED FINAL OUTPUT TO REPAIR\n=============================\n"
                        f"{output_text}\n"
                    )
                    repair_prompt_text = f"SYSTEM:\n{build_base_system()}\n\nUSER:\n{repair_user}"
                    repair_out = call_model(model, system=build_base_system(), user=repair_user, max_tokens=FINAL_REPAIR_MAX_TOKENS, timeout=timeout)
                    repair_io = write_named_prompt_and_output(condition_dir, f"turn_{index:03d}_final_repair_{repair_attempt:03d}", repair_prompt_text, repair_out)
                    repaired_text = repair_out["text"].strip()
                    repaired_word_count = word_count(repaired_text)
                    repaired_completeness = final_artifact_completeness(repaired_text, repair_out)
                    repair_record = {
                        "attempt": repair_attempt,
                        "model": model,
                        "previous_word_count": initial_final_word_count,
                        "previous_final_completeness": initial_completeness,
                        "repaired_word_count": repaired_word_count,
                        "repaired_final_completeness": repaired_completeness,
                        "accepted": FINAL_WORD_MIN <= repaired_word_count <= FINAL_WORD_PERSUASIVE_MAX and repaired_completeness["status"] == "pass",
                        **repair_io,
                    }
                    turn_repair_attempts.append(repair_record)
                    final_repair_attempts.append(repair_record)
                    repair_turn_records.append({
                        "turn": f"{index}_final_repair_{repair_attempt}",
                        "role": "final_word_band_repair",
                        "model": model,
                        "input_tokens": repair_out.get("input_tokens"),
                        "output_tokens": repair_out.get("output_tokens"),
                        **repair_io,
                    })
                    output_text = repaired_text
                    artifact_source_io = repair_io
                    artifact_output_meta = repair_out
                    if repair_record["accepted"]:
                        break
        artifact_id = "FINAL_ARTIFACT" if final else f"TURN_{index:03d}_{role.upper()}"
        registry["artifacts"][artifact_id] = {
            "status": "PINNED" if final else "INTERMEDIATE",
            "hash": sha_text(output_text),
            "source_reference": artifact_source_io["raw_output_path"],
            "content": output_text,
        }
        compliance = role_compliance(role, output_text, final, artifact_output_meta)
        audit = state_audit(output_text, state, allowed_ids, packet_hash, registry)
        state["ROLLING_SUMMARY"] = excerpt(output_text, 650)
        if final:
            state["SETTLED_DECISIONS"].append("final_artifact_synthesized")
            final_text = output_text
        evidence_turns.append({
            "turn": index,
            "model": model,
            "holo_context_profile": holo_context_profile,
            "context_governor_instructions_hash": sha_text(context_governor_instructions),
            "gov_notes_hash": sha_text(gov_notes_json),
            "state_object_hash": sha_text(state_json),
            "baton_pass_hash": sha_text(baton_json),
            "artifact_registry_hash": sha_text(registry_json),
            "prompt_card_hash": io["prompt_hash"],
            "retrieved_artifact_ids": retrieved_ids,
            "retrieved_content_hash": sha_text(retrieved),
            "role_compliance": compliance,
            "state_audit": audit,
            "final_repair_attempts": turn_repair_attempts,
        })
        turn_records.append({"turn": index, "role": role, "model": model, "input_tokens": out.get("input_tokens"), "output_tokens": out.get("output_tokens"), **io})
        turn_records.extend(repair_turn_records)
    artifact_path = condition_dir / "artifact.md"
    write_text(artifact_path, final_text)
    precheck = deterministic_gate_precheck(packet_dir, final_text)
    write_json(condition_dir / "deterministic_gate_precheck.json", precheck)
    arch_validation = architecture_evidence_summary(evidence_turns, precheck, holo_mode)
    arch_evidence = {
        "architecture_mode": holo_mode,
        "holo_context_profile": holo_context_profile,
        "architecture_evidence_visible_to_judges": False,
        "context_governor_type": "internal_deterministic_state_management_layer",
        "context_governor_instructions_hash": sha_text(context_governor_instructions),
        "hologov_profile": config.get("hologov_profile"),
        "holo_session_plan": session_plan,
        "packet_hash": packet_hash,
        "turns": evidence_turns,
        "final_artifact_hash": sha_file(artifact_path),
        "architecture_evidence_validation": arch_validation,
        "proof_credit_architecture_status": "eligible_if_all_turn_audits_pass_and_deterministic_gate_passes" if arch_validation["proof_credit_eligible"] else "not_proof_eligible_due_failed_architecture_or_gate_check",
        "provider_calls": len(turn_records),
        "final_repair_attempts": final_repair_attempts,
    }
    write_json(condition_dir / "arch_evidence.json", arch_evidence)
    metadata = {
        "condition": condition,
        "config_id": config["config_id"],
        "cohort_name": config.get("cohort_name"),
        "condition_type": "holo",
        "holo_mode": holo_mode,
        "holo_context_profile": holo_context_profile,
        "hologov_profile": config.get("hologov_profile"),
        "holo_session_plan": session_plan,
        "holo_mode_status": "proof_eligible_if_evidence_validates" if holo_mode == PROOF_ELIGIBLE_HOLO_MODE else "diagnostic_only_no_proof_credit",
        "packet_hash": packet_hash,
        "artifact_path": repo_rel(artifact_path),
        "artifact_hash": sha_file(artifact_path),
        "arch_evidence_path": repo_rel(condition_dir / "arch_evidence.json"),
        "turns": turn_records,
        "provider_calls": len(turn_records),
        "repair_calls": len(final_repair_attempts),
        "input_tokens": sum(int(item.get("input_tokens") or 0) for item in turn_records),
        "output_tokens": sum(int(item.get("output_tokens") or 0) for item in turn_records),
        "final_repair_attempts": final_repair_attempts,
        "architecture_evidence_validation": arch_validation,
        "proof_credit_eligible": arch_validation["proof_credit_eligible"],
        "scores_generated": 0,
    }
    write_json(condition_dir / "artifact_metadata.json", metadata)
    return metadata


def condition_public_label(index: int) -> str:
    return f"ARTIFACT_{index:03d}"


def create_blind_export(packet_dir: Path, run_id: str, condition_results: list[dict[str, Any]]) -> dict[str, Any]:
    run_dir = run_dir_for(packet_dir, run_id)
    export_dir = run_dir / "blind_export"
    task_brief = (packet_dir / "task_brief.md").read_text(encoding="utf-8")
    source_packet = read_json(packet_dir / "source_packet.json")
    scoring_protocol = active_scoring_protocol()
    created = []
    internal_map = {}
    for idx, result in enumerate(condition_results, start=1):
        artifact_path = REPO_ROOT / result["artifact_path"]
        if not artifact_path.exists():
            continue
        label = condition_public_label(idx)
        packet = {
            "artifact_label": label,
            "artifact_text": artifact_path.read_text(encoding="utf-8"),
            "task_brief": task_brief,
            "source_packet": source_packet,
            "scoring_protocol": {
                "active_scoring_protocol_id": scoring_protocol.get("active_scoring_protocol_id"),
                "protocol_hash": scoring_protocol.get("protocol_hash"),
                "schema_hash": scoring_protocol.get("schema_hash"),
                "lock_hash": scoring_protocol.get("lock_hash"),
            },
        }
        packet_path = export_dir / f"{label}_blind_packet.json"
        write_json(packet_path, packet)
        created.append({"artifact_label": label, "path": repo_rel(packet_path), "artifact_hash": result.get("artifact_hash")})
        internal_map[label] = {"condition": result.get("condition"), "config_id": result.get("config_id"), "artifact_hash": result.get("artifact_hash")}
    map_path = export_dir / "anonymization_map.internal.json"
    write_json(map_path, internal_map)
    findings = []
    for item in created:
        text = (REPO_ROOT / item["path"]).read_text(encoding="utf-8")
        for finding in scan_judge_visible_text(text):
            findings.append({"path": item["path"], **finding})
    scan = {"status": "PASS" if not findings else "FAIL", "findings": findings}
    write_json(export_dir / "contamination_scan_result.json", scan)
    manifest = {
        "blind_export_id": f"{run_id}_blind_export",
        "created_utc": utc_iso(),
        "judge_visible_packets": created,
        "scoring_protocol": scoring_protocol,
        "internal_mapping_file": repo_rel(map_path),
        "mapping_is_internal_only": True,
        "architecture_evidence_judge_visible": False,
        "contamination_scan_result": scan,
        "provider_calls": 0,
    }
    write_json(export_dir / "blind_export_manifest.json", manifest)
    return {"blind_export_dir": repo_rel(export_dir), "manifest": manifest}


def run_dry(packet_dir: Path, run_id: str, conditions: list[str], configs: dict[str, dict[str, Any]], manifest_entry: dict[str, Any], holo_mode: str, holo_context_profile: str, holo_session_template: str) -> int:
    run_dir = run_dir_for(packet_dir, run_id)
    resolved = []
    for condition in conditions:
        cfg = config_for_condition(condition, configs)
        resolved_item = {
            "condition": condition,
            "config_id": cfg["config_id"],
            "cohort_name": cfg.get("cohort_name"),
            "condition_type": cfg.get("condition_type"),
            "hologov_profile": cfg.get("hologov_profile"),
            "hologov_model_pool": cfg.get("governor_model_pool"),
            "live_ready": cfg.get("live_ready"),
            "provider_call_budget": cfg.get("provider_call_budget"),
        }
        if cfg.get("condition_type") == "holo":
            resolved_item["holo_session_plan"] = randomized_holo_session_plan(
                cfg,
                run_id=run_id,
                packet_hash=str(manifest_entry.get("packet_hash")),
                turn_count=len(HOLO_TURNS),
                session_template=holo_session_template,
            )
            resolved_item["holo_context_profile"] = holo_context_profile
            resolved_item["holo_session_template"] = holo_session_template
        resolved.append(resolved_item)
    payload = {
        "status": "HOLOBUILD_MINI_SCOUT_DRY_RUN_READY",
        "runner_id": "holobuild_generic_mini_scout_runner_v1",
        "run_id": run_id,
        "packet_dir": repo_rel(packet_dir),
        "domain_id": manifest_entry.get("domain_id"),
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "conditions": resolved,
        "holo_mode": holo_mode if any(item["condition_type"] == "holo" for item in resolved) else None,
        "holo_context_profile": holo_context_profile if any(item["condition_type"] == "holo" for item in resolved) else None,
        "holo_session_template": holo_session_template if any(item["condition_type"] == "holo" for item in resolved) else None,
        "live_mode_fail_closed": True,
        "live_requires": ["--live", f"{LIVE_APPROVAL_ENV}=1"],
        "provider_calls": 0,
        "live_artifacts_generated": 0,
        "scores_generated": 0,
        "judging_runs": 0,
        "unblinding_runs": 0,
    }
    write_json(run_dir / "generic_runner_dry_run_manifest.json", payload)
    print(json.dumps(payload, indent=2))
    return 0


def run_live(packet_dir: Path, run_id: str, conditions: list[str], configs: dict[str, dict[str, Any]], timeout: int, holo_mode: str, holo_context_profile: str, holo_session_template: str) -> int:
    enforce_live_guard(True)
    condition_results = []
    selected_models = []
    for condition in conditions:
        cfg = config_for_condition(condition, configs)
        if not cfg.get("live_ready"):
            raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_LIVE_FAIL_CLOSED", "reason": "config_not_live_ready", "condition": condition, "config_id": cfg.get("config_id"), "provider_calls": 0}, indent=2))
        selected_models.extend(provider_models_for_config(cfg, holo_mode))
    ensure_provider_env(selected_models)
    try:
        for condition in conditions:
            cfg = config_for_condition(condition, configs)
            if cfg["condition_type"] == "solo":
                condition_results.append(run_solo(packet_dir, run_id, cfg, timeout))
            elif cfg["condition_type"] == "holo":
                condition_results.append(run_holo(packet_dir, run_id, cfg, timeout, holo_mode, holo_context_profile, holo_session_template))
            else:
                raise RuntimeError(f"unsupported condition_type: {cfg['condition_type']}")
    except ProviderCallError as exc:
        failure = {
            "status": "HOLOBUILD_MINI_SCOUT_PROVIDER_ERROR",
            "provider": exc.provider,
            "error_type": exc.error_type,
            "http_status": exc.http_status,
            "message": str(exc),
            "provider_calls": PROVIDER_CALLS,
            "accepted_provider_calls": ACCEPTED_PROVIDER_CALLS,
            "failed_provider_calls": FAILED_PROVIDER_CALLS,
            "scores_generated": SCORES_GENERATED,
        }
        write_json(run_dir_for(packet_dir, run_id) / "run_failure.json", failure)
        print(json.dumps(failure, indent=2))
        return 1
    blind_export = create_blind_export(packet_dir, run_id, condition_results)
    run_manifest = {
        "status": "HOLOBUILD_MINI_SCOUT_LIVE_GENERATION_COMPLETE",
        "runner_id": "holobuild_generic_mini_scout_runner_v1",
        "run_id": run_id,
        "packet_dir": repo_rel(packet_dir),
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "conditions": condition_results,
        "provider_calls": PROVIDER_CALLS,
        "accepted_provider_calls": ACCEPTED_PROVIDER_CALLS,
        "failed_provider_calls": FAILED_PROVIDER_CALLS,
        "scores_generated": SCORES_GENERATED,
        "judging_runs": 0,
        "unblinding_runs": 0,
        "blind_export": blind_export,
        "live_mode_fail_closed": True,
        "live_requires": ["--live", f"{LIVE_APPROVAL_ENV}=1"],
        "holo_context_profile": holo_context_profile if any(result.get("condition_type") == "holo" for result in condition_results) else None,
        "holo_session_template": holo_session_template if any(result.get("condition_type") == "holo" for result in condition_results) else None,
    }
    write_json(run_dir_for(packet_dir, run_id) / "run_manifest.json", run_manifest)
    print(json.dumps(run_manifest, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generic HoloBuild mini-scout runner for frozen D1-D10 packets.")
    parser.add_argument("--suite-manifest", default=str(DEFAULT_SUITE_MANIFEST))
    parser.add_argument("--domain", choices=[f"D{i}" for i in range(1, 11)])
    parser.add_argument("--packet-dir")
    parser.add_argument("--condition", action="append", choices=VALID_CONDITIONS, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--holo-mode", choices=HOLO_MODES, default=PROOF_ELIGIBLE_HOLO_MODE)
    parser.add_argument("--holo-context-profile", choices=HOLO_CONTEXT_PROFILES, default=DEFAULT_HOLO_CONTEXT_PROFILE)
    parser.add_argument("--holo-session-template", choices=HOLO_SESSION_TEMPLATES, default="random")
    parser.add_argument("--diagnostic-legacy-holo-mode", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="No-provider smoke/dry run. Default when --live is absent.")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    enforce_holo_mode_guard(args.holo_mode, args.diagnostic_legacy_holo_mode)
    manifest = load_suite_manifest(Path(args.suite_manifest))
    packet_dir, entry = resolve_packet_dir(args, manifest)
    validate_packet_against_manifest(packet_dir, entry)
    configs = load_configs()
    conditions = list(dict.fromkeys(args.condition))
    if args.live:
        return run_live(packet_dir, args.run_id, conditions, configs, args.timeout, args.holo_mode, args.holo_context_profile, args.holo_session_template)
    return run_dry(packet_dir, args.run_id, conditions, configs, entry, args.holo_mode, args.holo_context_profile, args.holo_session_template)


if __name__ == "__main__":
    raise SystemExit(main())
