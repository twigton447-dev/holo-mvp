from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

FACTORY_DIR = Path(__file__).resolve().parent
REPO_ROOT = FACTORY_DIR.parents[1]
MANIFEST_PATH = FACTORY_DIR / "mini_scouts/TEN_DOMAIN_PACKET_SUITE_MANIFEST.json"
SCORING_LOCK = FACTORY_DIR / "scoring_policies/ACTIVE_SCORING_PROTOCOL.lock.json"
RUNNER_PATH = FACTORY_DIR / "run_holobuild_mini_scout.py"
CONFIG_DIR = FACTORY_DIR / "configs"
D3_SUCCESS_TEMPLATE_LOCK = CONFIG_DIR / "holo_session_template_d3_success_v1.lock.json"
EXPECTED_DOMAINS = {f"D{i}" for i in range(1, 11)}
EXPECTED_MINI_SOLO_MODELS = ["openai:gpt-4o-mini"]
EXPECTED_HOLO_AGENT_MODELS = {
    "frontier_holo_v1": [
        "anthropic:claude-opus-4-8",
        "google:gemini-3.1-pro-preview",
        "openai:gpt-5.5",
    ],
    "mini_holo_v1": [
        "xai:grok-3-mini",
        "minimax:MiniMax-M2.5-highspeed",
        "openai:gpt-4o-mini",
    ],
}
EXPECTED_COHORT_NAMES = {
    "frontier_holo_v1": "HoloFull",
    "frontier_solo_v1": "SoloFull",
    "mini_holo_v1": "HoloMini",
    "mini_solo_v1": "SoloMini",
}
EXPECTED_HOLOGOV_PROFILE = {
    "frontier_holo_v1": "HoloGov-C",
    "mini_holo_v1": "HoloGov-C",
}


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def run_packet_validator(path: Path) -> dict[str, Any]:
    result = subprocess.run([sys.executable, "-B", str(path)], cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    payload: dict[str, Any]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {"status": "PARSE_FAIL", "stdout": result.stdout, "stderr": result.stderr}
    payload["returncode"] = result.returncode
    payload["validator_path"] = repo_rel(path)
    return payload


def provider_models(cfg: dict[str, Any]) -> list[str]:
    return [item["provider_model"] for item in cfg.get("model_pool", []) if item.get("provider_model")]


def governor_models(cfg: dict[str, Any]) -> list[str]:
    return list(cfg.get("governor_model_pool") or [])


def validate_config(cfg: dict[str, Any], errors: list[str]) -> None:
    config_id = cfg.get("config_id")
    models = provider_models(cfg)
    condition_type = cfg.get("condition_type")
    live_ready = cfg.get("live_ready")
    if config_id in EXPECTED_COHORT_NAMES:
        expected_name = EXPECTED_COHORT_NAMES[config_id]
        if cfg.get("cohort_name") != expected_name:
            errors.append(f"{config_id} cohort_name must be {expected_name}")
        if expected_name not in cfg.get("condition_aliases", []):
            errors.append(f"{config_id} condition_aliases must include {expected_name}")
    if config_id in EXPECTED_HOLOGOV_PROFILE:
        expected_profile = EXPECTED_HOLOGOV_PROFILE[config_id]
        if cfg.get("hologov_profile") != expected_profile:
            errors.append(f"{config_id} hologov_profile must be {expected_profile}")
    if config_id in EXPECTED_HOLO_AGENT_MODELS:
        expected_models = EXPECTED_HOLO_AGENT_MODELS[config_id]
        if models != expected_models:
            errors.append(f"{config_id} model_pool must be the three HoloAgent candidates {expected_models}")
        if governor_models(cfg) != expected_models:
            errors.append(f"{config_id} governor_model_pool must match the three HoloAgent candidates")
        if cfg.get("model_selection_policy") != "session_random_three_model_permutation_repeated_for_turn_budget":
            errors.append(f"{config_id} model_selection_policy must be session-randomized")
    if live_ready:
        if cfg.get("provider_call_budget") != 6:
            errors.append(f"{config_id} live_ready requires provider_call_budget=6")
        if condition_type == "holo" and len(models) != 3:
            errors.append(f"{config_id} live_ready holo config requires exactly 3 HoloAgent models")
        if condition_type == "solo" and len(models) != 1:
            errors.append(f"{config_id} live_ready solo config requires exactly 1 provider model")
    if config_id == "mini_holo_v1":
        if cfg.get("architecture_mode") != "patent_aligned_v4":
            errors.append("mini_holo_v1 must use patent_aligned_v4")
        if not live_ready:
            errors.append("mini_holo_v1 must be live_ready")
    if config_id == "mini_solo_v1":
        if models != EXPECTED_MINI_SOLO_MODELS:
            errors.append("mini_solo_v1 model_pool must be openai:gpt-4o-mini")
        if not live_ready:
            errors.append("mini_solo_v1 must be live_ready")


def main() -> int:
    errors: list[str] = []
    if not MANIFEST_PATH.exists():
        errors.append(f"missing suite manifest: {repo_rel(MANIFEST_PATH)}")
        manifest = {"domains": []}
    else:
        manifest = read_json(MANIFEST_PATH)
    entries = manifest.get("domains", [])
    domain_ids = {item.get("domain_id") for item in entries}
    if domain_ids != EXPECTED_DOMAINS:
        errors.append(f"expected D1-D10 domains, got {sorted(domain_ids)}")
    if not RUNNER_PATH.exists():
        errors.append(f"missing runner: {repo_rel(RUNNER_PATH)}")
        runner_text = ""
    else:
        runner_text = RUNNER_PATH.read_text(encoding="utf-8")
        if 'DEFAULT_HOLO_CONTEXT_PROFILE = "full_registry"' not in runner_text:
            errors.append("runner must default proof-eligible Holo context to full_registry")
        if "retrieved_ids_for_holo_turn" not in runner_text:
            errors.append("runner must retrieve Holo pinned artifacts through retrieved_ids_for_holo_turn")
        if '"full_registry"' not in runner_text or '"latest_only"' not in runner_text:
            errors.append("runner must expose full_registry and latest_only Holo context profiles")
        if "CONTEXT_GOVERNOR_INSTRUCTIONS" not in runner_text:
            errors.append("runner must inject CONTEXT_GOVERNOR_INSTRUCTIONS into Holo prompt cards")
        if "GOV_NOTES" not in runner_text:
            errors.append("runner must inject GOV_NOTES into Holo prompt cards and state")
        if "context_governor_instructions_hash" not in runner_text or "gov_notes_hash" not in runner_text:
            errors.append("runner must record Gov instruction and Gov note hashes in architecture evidence")
        if "preferred_holo_final_model" not in runner_text:
            errors.append("runner must pin Holo final synthesis to a preferred final writer model")
        if "MAX_HOLO_FINAL_REPAIR_ATTEMPTS = 1" not in runner_text:
            errors.append("runner must bound Holo final word-band repair to one attempt")
        if "FINAL_SYNTHESIS_MAX_TOKENS = 6000" not in runner_text:
            errors.append("runner must give final synthesis enough token headroom to avoid induced truncation")
        if "final_artifact_completeness" not in runner_text:
            errors.append("runner must audit final artifact completeness and clean ending")
        if "FINAL_ARTIFACT_COMPLETENESS_REPAIR" not in runner_text:
            errors.append("runner must include an auditable final artifact completeness repair prompt")
        if "final_artifact_completeness_pass" not in runner_text:
            errors.append("architecture proof must require final_artifact_completeness_pass")
        if "--holo-session-template" not in runner_text or "d3_success_v1" not in runner_text:
            errors.append("runner must support the locked d3_success_v1 Holo session template")
    if not SCORING_LOCK.exists():
        errors.append(f"missing scoring lock: {repo_rel(SCORING_LOCK)}")
    template_lock_result = None
    if not D3_SUCCESS_TEMPLATE_LOCK.exists():
        errors.append(f"missing D3 success Holo session template lock: {repo_rel(D3_SUCCESS_TEMPLATE_LOCK)}")
    else:
        template_lock = read_json(D3_SUCCESS_TEMPLATE_LOCK)
        expected_turns = [
            "google:gemini-3.1-pro-preview",
            "openai:gpt-5.5",
            "anthropic:claude-opus-4-8",
            "google:gemini-3.1-pro-preview",
            "openai:gpt-5.5",
            "anthropic:claude-opus-4-8",
        ]
        if template_lock.get("template_id") != "d3_success_v1":
            errors.append("D3 success Holo session template lock has wrong template_id")
        if template_lock.get("holo_agent_turn_models") != expected_turns:
            errors.append("D3 success Holo session template lock has wrong turn model order")
        schedule = template_lock.get("hologov_schedule") or []
        if not schedule or schedule[0].get("governor_model") != "openai:gpt-5.5":
            errors.append("D3 success Holo session template lock must use openai:gpt-5.5 governor")
        if template_lock.get("final_synthesis_model") != "anthropic:claude-opus-4-8":
            errors.append("D3 success Holo session template lock must use Anthropic final synthesis")
        template_lock_result = {
            "path": repo_rel(D3_SUCCESS_TEMPLATE_LOCK),
            "hash": sha_file(D3_SUCCESS_TEMPLATE_LOCK),
            "template_id": template_lock.get("template_id"),
            "holo_context_profile_required": template_lock.get("holo_context_profile_required"),
        }
    config_results = {}
    for name in ["frontier_solo_v1.json", "frontier_holo_v1.json", "mini_solo_v1.stub.json", "mini_holo_v1.stub.json"]:
        path = CONFIG_DIR / name
        if not path.exists():
            errors.append(f"missing config: {repo_rel(path)}")
            continue
        cfg = read_json(path)
        validate_config(cfg, errors)
        config_results[cfg["config_id"]] = {
            "path": repo_rel(path),
            "hash": sha_file(path),
            "cohort_name": cfg.get("cohort_name"),
            "live_ready": cfg.get("live_ready"),
            "condition_type": cfg.get("condition_type"),
            "architecture_mode": cfg.get("architecture_mode"),
            "hologov_profile": cfg.get("hologov_profile"),
            "governor_model_pool": governor_models(cfg),
            "proof_credit_eligible": cfg.get("proof_credit_eligible"),
            "provider_call_budget": cfg.get("provider_call_budget"),
            "model_pool": provider_models(cfg),
        }
    holo_cfg = config_results.get("frontier_holo_v1", {})
    if holo_cfg.get("architecture_mode") != "patent_aligned_v4":
        errors.append("frontier_holo_v1 must use patent_aligned_v4")
    packet_results = []
    for item in entries:
        packet_dir = REPO_ROOT / item["packet_dir"]
        for rel in ["packet_lock.json", "freeze_manifest.json", "source_packet.json", "source_manifest.json", "contamination_scan_config.json", "validate_packet_no_provider.py"]:
            if not (packet_dir / rel).exists():
                errors.append(f"{item.get('domain_id')} missing {rel}")
        hash_checks = {
            "packet_hash": sha_file(packet_dir / "source_packet.json") if (packet_dir / "source_packet.json").exists() else None,
            "packet_lock_hash": sha_file(packet_dir / "packet_lock.json") if (packet_dir / "packet_lock.json").exists() else None,
            "freeze_manifest_hash": sha_file(packet_dir / "freeze_manifest.json") if (packet_dir / "freeze_manifest.json").exists() else None,
        }
        for key, actual in hash_checks.items():
            if actual and item.get(key) != actual:
                errors.append(f"{item.get('domain_id')} manifest {key} mismatch")
        validator_path = REPO_ROOT / item["validator_path"]
        validation = run_packet_validator(validator_path) if validator_path.exists() else {"status": "MISSING", "returncode": 1}
        if validation.get("returncode") != 0 or validation.get("provider_calls") != 0:
            errors.append(f"{item.get('domain_id')} packet validator failed or made provider calls")
        packet_results.append({
            "domain_id": item.get("domain_id"),
            "packet_id": item.get("packet_id"),
            "packet_hash": hash_checks["packet_hash"],
            "validation_status": validation.get("status"),
            "provider_calls": validation.get("provider_calls"),
            "validator_returncode": validation.get("returncode"),
        })
    output = {
        "status": "HOLOBUILD_TEN_DOMAIN_SUITE_READY_NO_PROVIDER" if not errors else "HOLOBUILD_TEN_DOMAIN_SUITE_VALIDATION_FAIL",
        "suite_manifest_path": repo_rel(MANIFEST_PATH),
        "suite_manifest_hash": sha_file(MANIFEST_PATH) if MANIFEST_PATH.exists() else None,
        "domain_count": len(entries),
        "packet_results": packet_results,
        "runner_path": repo_rel(RUNNER_PATH),
        "runner_hash": sha_file(RUNNER_PATH) if RUNNER_PATH.exists() else None,
        "holo_context_profile_default": "full_registry",
        "context_governor_prompt_surface_required": True,
        "holo_final_synthesis_policy": "preferred_final_model_with_one_bounded_word_band_repair",
        "d3_success_holo_session_template_lock": template_lock_result,
        "scoring_lock_path": repo_rel(SCORING_LOCK),
        "scoring_lock_hash": sha_file(SCORING_LOCK) if SCORING_LOCK.exists() else None,
        "proof_holo_mode": "patent_aligned_v4",
        "legacy_holo_modes": {
            "diagnostic_v3": "diagnostic_only_no_proof_credit",
            "full_gov_v4": "diagnostic_only_no_proof_credit",
        },
        "configs": config_results,
        "provider_calls": 0,
        "artifact_generation": 0,
        "scoring": 0,
        "judging": 0,
        "unblinding": 0,
        "errors": errors,
    }
    print(json.dumps(output, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
