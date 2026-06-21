from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
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
LIVE_APPROVAL_ENV = "HOLO_ALLOW_LIVE"
PROOF_ELIGIBLE_HOLO_MODE = "patent_aligned_v4"
LEGACY_HOLO_MODES = {"diagnostic_v3", "full_gov_v4"}
HOLO_MODES = ("diagnostic_v3", "full_gov_v4", "patent_aligned_v4")
VALID_CONDITIONS = (
    "holo_build_arch",
    "solo_openai_gpt_5_5",
    "frontier_solo_v1",
    "frontier_holo_v1",
    "mini_solo_v1",
    "mini_holo_v1",
)
FINAL_WORD_MIN = 900
FINAL_WORD_MAX = 1300
FINAL_WORD_TARGET = 1100
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
    ("final_synthesis_900_1300_words", "Return only the final decision-grade crisis/action brief, 900-1,300 body words, target 1,100."),
)
HOLO_TURNS = (
    ("initial_decision_brief_drafter", "anthropic:claude-opus-4-8", "Draft a source-grounded initial decision frame covering what is happening, why it matters, and the main options. This is not final."),
    ("assumption_and_evidence_attacker", "google:gemini-3.1-pro-preview", "Attack assumptions, weak evidence, stale claims, missing calculations, and unsupported causal links."),
    ("contradiction_uncertainty_source_fidelity_reviewer", "openai:gpt-5.5", "Stress-test contradictory evidence, source fidelity, source-status boundaries, and uncertainty handling."),
    ("options_operational_usefulness_reviewer", "anthropic:claude-opus-4-8", "Stress-test practical options, risks of acting, risks of waiting, operating gates, and usefulness for leadership."),
    ("claim_discipline_overclaim_reducer", "google:gemini-3.1-pro-preview", "Reduce unsupported claims, identify overclaim risks, and prepare final-brief constraints."),
    ("final_synthesis_author", "openai:gpt-5.5", "Return only the final decision-grade crisis/action brief, 900-1,300 body words, target 1,100."),
)
SOURCE_ID_RE = re.compile(r"\bS\d+_[A-Z0-9_]+\b")


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


def repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


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
        if holo_mode != PROOF_ELIGIBLE_HOLO_MODE:
            return [item["provider_model"] for item in config.get("model_pool", []) if item.get("provider_model")]
        return [item["provider_model"] for item in config.get("model_pool", []) if item.get("provider_model")]
    return []


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
        "The final artifact body must be 900-1,300 words, target 1,100. If a draft exceeds 1,300 body words, revise shorter before final answer."
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
    return {
        "artifact_body_word_count": count,
        "word_count_gate": word_gate,
        "deterministic_gate_status": "pass" if minimum <= count <= maximum else "fail",
        "proof_credit_eligible_if_failed": False,
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


def role_compliance(role: str, output_text: str, final: bool) -> dict[str, Any]:
    lowered = output_text.lower()
    praise_only = len(re.findall(r"\b(strong|excellent|good|solid)\b", lowered)) >= 3 and not re.search(r"\b(missing|unsupported|risk|weak|contradict|uncertain|revise|option)\b", lowered)
    role_terms = {
        "initial_decision_brief_drafter": ("option", "evidence", "source"),
        "assumption_and_evidence_attacker": ("assumption", "weak", "missing"),
        "contradiction_uncertainty_source_fidelity_reviewer": ("contradict", "uncertain", "source"),
        "options_operational_usefulness_reviewer": ("option", "risk", "wait"),
        "claim_discipline_overclaim_reducer": ("overclaim", "unsupported", "claim"),
        "final_synthesis_author": ("option", "risk", "claim"),
    }.get(role, ())
    missing_terms = [term for term in role_terms if term not in lowered]
    result = {
        "status": "pass" if not praise_only and not missing_terms else "fail",
        "praise_only": praise_only,
        "missing_role_terms": missing_terms,
    }
    if final:
        wc = word_count(output_text)
        result["final_word_count"] = wc
        result["final_word_band_status"] = "pass" if FINAL_WORD_MIN <= wc <= FINAL_WORD_MAX else "fail"
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


def run_holo(packet_dir: Path, run_id: str, config: dict[str, Any], timeout: int, holo_mode: str) -> dict[str, Any]:
    condition = "holo_build_arch" if "holo_build_arch" in config.get("condition_aliases", []) else config["config_id"]
    condition_dir = condition_dir_for(packet_dir, run_id, condition)
    surfaces = load_packet_surfaces(packet_dir)
    packet_hash = sha_file(packet_dir / "source_packet.json")
    allowed_ids = source_ids(surfaces["source_packet_json"])
    registry = {
        "artifacts": {
            "TASK_BRIEF": {"status": "PINNED", "hash": sha_text(surfaces["task_brief"]), "source_reference": repo_rel(packet_dir / "task_brief.md"), "content": surfaces["task_brief"]},
            "SOURCE_PACKET_MD": {"status": "PINNED", "hash": sha_text(surfaces["source_packet_md"]), "source_reference": repo_rel(packet_dir / "source_packet.md"), "content": surfaces["source_packet_md"]},
        }
    }
    state = {
        "USER_GOAL": "Produce a decision-grade crisis/action brief from the frozen packet.",
        "LATEST_INPUT_SUMMARY": surfaces["source_packet_json"].get("decision_question") or surfaces["source_packet_json"].get("crisis_frame"),
        "CRITICAL_CONSTRAINTS": [
            "Use only the frozen task brief and source packet; no browsing.",
            "Final artifact body must be 900-1,300 words, target 1,100.",
            "Separate source facts from inference and preserve claim boundaries.",
            "No proof credit if deterministic gate fails.",
        ],
        "PACKET_HASH": packet_hash,
        "ROLLING_SUMMARY": "No model turns completed yet.",
        "SETTLED_DECISIONS": [],
        "ARTIFACTS_REGISTRY": {"artifact_ids": list(registry["artifacts"].keys())},
        "REQUIRED_TOOLS": [],
        "BATON_PASS": {},
    }
    evidence_turns = []
    turn_records = []
    final_text = ""
    for index, (role, model, objective) in enumerate(HOLO_TURNS, start=1):
        final = index == len(HOLO_TURNS)
        retrieved_ids = ["TASK_BRIEF", "SOURCE_PACKET_MD"]
        prior_ids = [key for key in registry["artifacts"] if key.startswith("TURN_")]
        if prior_ids:
            retrieved_ids.append(prior_ids[-1])
        baton = {
            "next_model": model,
            "adversarial_role": role,
            "focus_area": objective,
            "unresolved_tensions": ["source support", "risks of acting", "risks of waiting", "claim boundaries"],
            "retrieved_artifact_ids": retrieved_ids,
            "required_output_behavior": "final artifact only" if final else "role-specific draft or critique for registry update",
        }
        state["BATON_PASS"] = baton
        state["ARTIFACTS_REGISTRY"] = {"artifact_ids": list(registry["artifacts"].keys())}
        state_json = stable_json(state)
        baton_json = stable_json(baton)
        registry_json = stable_json({k: {kk: vv for kk, vv in v.items() if kk != "content"} for k, v in registry["artifacts"].items()})
        retrieved = retrieved_content_for(retrieved_ids, registry)
        user = (
            "CANONICAL STATE_OBJECT\n======================\n"
            f"{state_json}\n\nSTATE_OBJECT_SHA256: {sha_text(state_json)}\n\n"
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
            user += "Return only the final decision-grade crisis/action brief. Body word count 900-1,300, target 1,100. If too long, revise shorter before final answer.\n"
        prompt_text = f"SYSTEM:\n{build_base_system()}\n\nUSER:\n{user}"
        out = call_model(model, system=build_base_system(), user=user, max_tokens=3800, timeout=timeout)
        io = write_prompt_and_output(condition_dir, index, prompt_text, out)
        output_text = out["text"].strip()
        artifact_id = "FINAL_ARTIFACT" if final else f"TURN_{index:03d}_{role.upper()}"
        registry["artifacts"][artifact_id] = {
            "status": "PINNED" if final else "INTERMEDIATE",
            "hash": sha_text(output_text),
            "source_reference": io["raw_output_path"],
            "content": output_text,
        }
        compliance = role_compliance(role, output_text, final)
        audit = state_audit(output_text, state, allowed_ids, packet_hash, registry)
        state["ROLLING_SUMMARY"] = excerpt(output_text, 650)
        if final:
            state["SETTLED_DECISIONS"].append("final_artifact_synthesized")
            final_text = output_text
        evidence_turns.append({
            "turn": index,
            "model": model,
            "state_object_hash": sha_text(state_json),
            "baton_pass_hash": sha_text(baton_json),
            "artifact_registry_hash": sha_text(registry_json),
            "prompt_card_hash": io["prompt_hash"],
            "retrieved_artifact_ids": retrieved_ids,
            "retrieved_content_hash": sha_text(retrieved),
            "role_compliance": compliance,
            "state_audit": audit,
        })
        turn_records.append({"turn": index, "role": role, "model": model, "input_tokens": out.get("input_tokens"), "output_tokens": out.get("output_tokens"), **io})
    artifact_path = condition_dir / "artifact.md"
    write_text(artifact_path, final_text)
    precheck = deterministic_gate_precheck(packet_dir, final_text)
    write_json(condition_dir / "deterministic_gate_precheck.json", precheck)
    arch_evidence = {
        "architecture_mode": holo_mode,
        "architecture_evidence_visible_to_judges": False,
        "context_governor_type": "internal_deterministic_state_management_layer",
        "packet_hash": packet_hash,
        "turns": evidence_turns,
        "final_artifact_hash": sha_file(artifact_path),
        "proof_credit_architecture_status": "eligible_if_all_turn_audits_pass_and_deterministic_gate_passes" if holo_mode == PROOF_ELIGIBLE_HOLO_MODE else "diagnostic_only_no_proof_credit",
        "provider_calls": len(turn_records),
    }
    write_json(condition_dir / "arch_evidence.json", arch_evidence)
    metadata = {
        "condition": condition,
        "config_id": config["config_id"],
        "condition_type": "holo",
        "holo_mode": holo_mode,
        "holo_mode_status": "proof_eligible_if_evidence_validates" if holo_mode == PROOF_ELIGIBLE_HOLO_MODE else "diagnostic_only_no_proof_credit",
        "packet_hash": packet_hash,
        "artifact_path": repo_rel(artifact_path),
        "artifact_hash": sha_file(artifact_path),
        "arch_evidence_path": repo_rel(condition_dir / "arch_evidence.json"),
        "turns": turn_records,
        "provider_calls": len(turn_records),
        "input_tokens": sum(int(item.get("input_tokens") or 0) for item in turn_records),
        "output_tokens": sum(int(item.get("output_tokens") or 0) for item in turn_records),
        "proof_credit_eligible": holo_mode == PROOF_ELIGIBLE_HOLO_MODE and precheck["deterministic_gate_status"] == "pass",
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
            "scoring_protocol_target": "unified_artifact_scoring_protocol_v5_2_structural_epistemic",
        }
        packet_path = export_dir / f"{label}_blind_packet.json"
        write_json(packet_path, packet)
        created.append({"artifact_label": label, "path": repo_rel(packet_path), "artifact_hash": result.get("artifact_hash")})
        internal_map[label] = {"condition": result.get("condition"), "config_id": result.get("config_id"), "artifact_hash": result.get("artifact_hash")}
    map_path = export_dir / "anonymization_map.internal.json"
    write_json(map_path, internal_map)
    forbidden_keys = ["condition", "provider_model", "token", "architecture_evidence", "arch_evidence", "run_id"]
    findings = []
    for item in created:
        text = (REPO_ROOT / item["path"]).read_text(encoding="utf-8").lower()
        for term in forbidden_keys:
            if term in text:
                findings.append({"path": item["path"], "term": term})
    scan = {"status": "PASS" if not findings else "FAIL", "findings": findings}
    write_json(export_dir / "contamination_scan_result.json", scan)
    manifest = {
        "blind_export_id": f"{run_id}_blind_export",
        "created_utc": utc_iso(),
        "judge_visible_packets": created,
        "internal_mapping_file": repo_rel(map_path),
        "mapping_is_internal_only": True,
        "architecture_evidence_judge_visible": False,
        "contamination_scan_result": scan,
        "provider_calls": 0,
    }
    write_json(export_dir / "blind_export_manifest.json", manifest)
    return {"blind_export_dir": repo_rel(export_dir), "manifest": manifest}


def run_dry(packet_dir: Path, run_id: str, conditions: list[str], configs: dict[str, dict[str, Any]], manifest_entry: dict[str, Any], holo_mode: str) -> int:
    run_dir = run_dir_for(packet_dir, run_id)
    resolved = []
    for condition in conditions:
        cfg = config_for_condition(condition, configs)
        resolved.append({"condition": condition, "config_id": cfg["config_id"], "condition_type": cfg.get("condition_type"), "live_ready": cfg.get("live_ready"), "provider_call_budget": cfg.get("provider_call_budget")})
    payload = {
        "status": "HOLOBUILD_MINI_SCOUT_DRY_RUN_READY",
        "runner_id": "holobuild_generic_mini_scout_runner_v1",
        "run_id": run_id,
        "packet_dir": repo_rel(packet_dir),
        "domain_id": manifest_entry.get("domain_id"),
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "conditions": resolved,
        "holo_mode": holo_mode if any(item["condition_type"] == "holo" for item in resolved) else None,
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


def run_live(packet_dir: Path, run_id: str, conditions: list[str], configs: dict[str, dict[str, Any]], timeout: int, holo_mode: str) -> int:
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
                condition_results.append(run_holo(packet_dir, run_id, cfg, timeout, holo_mode))
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
        return run_live(packet_dir, args.run_id, conditions, configs, args.timeout, args.holo_mode)
    return run_dry(packet_dir, args.run_id, conditions, configs, entry, args.holo_mode)


if __name__ == "__main__":
    raise SystemExit(main())
