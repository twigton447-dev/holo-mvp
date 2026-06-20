from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


FACTORY_DIR = Path(__file__).resolve().parent
PACKET_DIR = FACTORY_DIR / "mini_scouts/d5_medtech_capacity_strain_001"
RUNNER_PATH = FACTORY_DIR / "run_d5_mini_scout_live.py"
EXPORTER_PATH = FACTORY_DIR / "export_d5_mini_scout_blind_packets_v4_1.py"
ARCH_SCHEMA_PATH = FACTORY_DIR / "schemas/holo_build_arch_evidence_schema.json"
ARCH_POLICY_PATH = FACTORY_DIR / "architecture_policies/holobuild_patent_alignment_policy_v4_1.json"
SCORING_LOCK_PATH = FACTORY_DIR / "scoring_policies/combined_artifact_scoring_protocol_v4_1.lock.json"

PROVIDER_CALLS = 0
LIVE_ARTIFACTS_GENERATED = 0
SCORES_GENERATED = 0
EXPECTED_PACKET_HASH = "b73292d9d2e4aac5f65a93ae168235d9d581ae17ebaf0a91aa16437018c527aa"
EXPECTED_CONDITIONS = {"holo_build_arch", "solo_openai_gpt_5_5"}
REQUIRED_ARCH_TOKENS = [
    "state_object_hash",
    "state_object_snapshot_path",
    "critical_constraints_preserved",
    "settled_decisions_if_present",
    "artifact_registry_entries",
    "artifact_registry_hash",
    "pinned_source_hashes",
    "pinned_artifact_hashes",
    "retrieve_by_id_or_source_reference_behavior",
    "token_budget_partial_injection_flags",
    "baton_pass",
    "selected_model",
    "adversarial_role",
    "role_compliance_result",
    "state_audit_constraint_preservation_result",
    "synthesis_trigger",
    "final_artifact_hash",
    "architecture_evidence_visible_to_judges",
]
BLIND_EXPORT_FORBIDDEN_TOKENS = [
    "architecture evidence",
    "condition names",
    "generation traces",
    "prior scores",
    "no_architecture_evidence",
    "no_condition_identity",
]


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    require(PACKET_DIR.exists(), errors, f"missing packet dir: {PACKET_DIR}")
    require(RUNNER_PATH.exists(), errors, f"missing runner: {RUNNER_PATH}")
    require(EXPORTER_PATH.exists(), errors, f"missing blind exporter: {EXPORTER_PATH}")
    require(ARCH_SCHEMA_PATH.exists(), errors, f"missing architecture schema: {ARCH_SCHEMA_PATH}")
    require(ARCH_POLICY_PATH.exists(), errors, f"missing architecture policy: {ARCH_POLICY_PATH}")
    require(SCORING_LOCK_PATH.exists(), errors, f"missing scoring lock: {SCORING_LOCK_PATH}")

    if not errors:
        packet_hash = sha_file(PACKET_DIR / "source_packet.json")
        packet = read_json(PACKET_DIR / "source_packet.json")
        gate = read_json(PACKET_DIR / "deterministic_gate_policy.json")
        lock = read_json(PACKET_DIR / "packet_lock.json")
        scoring_lock = read_json(SCORING_LOCK_PATH)
        arch_schema = read_json(ARCH_SCHEMA_PATH)
        arch_policy = read_json(ARCH_POLICY_PATH)
        runner_text = RUNNER_PATH.read_text(encoding="utf-8")
        exporter_text = EXPORTER_PATH.read_text(encoding="utf-8")

        require(packet_hash == EXPECTED_PACKET_HASH, errors, "D5 packet hash mismatch")
        require(packet.get("real_public_sources_only") is True, errors, "packet is not real-public-sources-only")
        require(packet.get("contestants_may_browse") is False, errors, "packet allows contestant browsing")
        require(packet.get("source_count") == 9, errors, "source count mismatch")

        word_gate = gate["layer_1_deterministic_gate"]["artifact_body_word_count"]
        require(word_gate.get("min") == 900 and word_gate.get("max") == 1300, errors, "mini scout word gate mismatch")
        require(word_gate.get("scope") == "main_artifact_body_only", errors, "word gate scope mismatch")
        require("no_proof_credit" in word_gate.get("failure_result", ""), errors, "word gate does not block proof credit")
        require(scoring_lock["word_count_gate"]["mini_test_artifact_body_words"] == {"min": 900, "max": 1300}, errors, "scoring lock mini word gate mismatch")

        locked = lock.get("locked_files") or {}
        require(locked.get("source_packet.json") == EXPECTED_PACKET_HASH, errors, "packet lock does not pin source_packet hash")

        require("--live" in runner_text, errors, "runner missing --live support")
        require("--no-provider-smoke" in runner_text, errors, "runner missing --no-provider-smoke support")
        require("HOLO_ALLOW_LIVE" in runner_text, errors, "runner missing second live approval guard")
        require("D5_MINI_SCOUT_LIVE_FAIL_CLOSED" in runner_text, errors, "runner missing live fail-closed status")
        for condition in EXPECTED_CONDITIONS:
            require(condition in runner_text, errors, f"runner missing condition {condition}")

        for token in REQUIRED_ARCH_TOKENS:
            require(token in runner_text, errors, f"runner missing architecture evidence token: {token}")
        require(arch_schema["properties"]["architecture_evidence_visible_to_judges"]["const"] is False, errors, "architecture schema does not force judge-hidden evidence")
        require(arch_policy["architecture_evidence_visible_to_judges"] is False, errors, "architecture policy exposes evidence to judges")

        for token in BLIND_EXPORT_FORBIDDEN_TOKENS:
            require(token in exporter_text, errors, f"blind exporter missing hidden-field handling: {token}")
        require("neutral_domain_card" in exporter_text, errors, "blind exporter missing neutral domain card")
        require("neutral_rubric" in exporter_text, errors, "blind exporter missing neutral rubric")
        require("scan_text" in exporter_text, errors, "blind exporter missing contamination scan")

        runner_hash = sha_file(RUNNER_PATH)
        exporter_hash = sha_file(EXPORTER_PATH)
        arch_schema_hash = sha_file(ARCH_SCHEMA_PATH)
        arch_policy_hash = sha_file(ARCH_POLICY_PATH)
    else:
        packet_hash = None
        runner_hash = None
        exporter_hash = None
        arch_schema_hash = None
        arch_policy_hash = None

    result = {
        "status": "D5_MINI_SCOUT_READINESS_V4_1_PASS" if not errors else "D5_MINI_SCOUT_READINESS_V4_1_FAIL",
        "provider_calls": PROVIDER_CALLS,
        "live_artifacts_generated": LIVE_ARTIFACTS_GENERATED,
        "scores_generated": SCORES_GENERATED,
        "packet_dir": str(PACKET_DIR),
        "packet_hash": packet_hash,
        "conditions_supported": sorted(EXPECTED_CONDITIONS),
        "live_mode_fail_closed_by_default": True,
        "live_requires": ["--live", "HOLO_ALLOW_LIVE=1"],
        "holobuild_architecture_evidence_path_wired": RUNNER_PATH.exists(),
        "blind_export_path_wired": EXPORTER_PATH.exists(),
        "hashes": {
            "runner": runner_hash,
            "blind_exporter": exporter_hash,
            "architecture_schema": arch_schema_hash,
            "architecture_policy": arch_policy_hash,
        },
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
