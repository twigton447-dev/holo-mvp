from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FACTORY_DIR = Path(__file__).resolve().parent
DEFAULT_PACKET_DIR = FACTORY_DIR / "mini_scouts/d5_medtech_capacity_strain_001"
ARCH_SCHEMA_PATH = FACTORY_DIR / "schemas/holo_build_arch_evidence_schema.json"
ARCH_POLICY_PATH = FACTORY_DIR / "architecture_policies/holobuild_patent_alignment_policy_v4_1.json"

RUNNER_ID = "d5_medtech_capacity_strain_001_live_adapter_v4_1"
LIVE_APPROVAL_ENV = "HOLO_ALLOW_LIVE"
PROVIDER_CALLS = 0
LIVE_ARTIFACTS_GENERATED = 0
SCORES_GENERATED = 0

VALID_CONDITIONS = ("holo_build_arch", "solo_openai_gpt_5_5")
CONDITION_LABELS = {
    "holo_build_arch": "HoloBuild architecture condition",
    "solo_openai_gpt_5_5": "GPT-5.5 solo condition",
}
REQUIRED_PACKET_FILES = (
    "task_brief.md",
    "source_packet.json",
    "source_packet.md",
    "packet_lock.json",
    "freeze_manifest.json",
    "deterministic_gate_policy.json",
)


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def require_packet(packet_dir: Path) -> dict[str, Any]:
    missing = [name for name in REQUIRED_PACKET_FILES if not (packet_dir / name).exists()]
    if missing:
        raise SystemExit(
            json.dumps(
                {
                    "status": "D5_MINI_SCOUT_RUNNER_FAIL",
                    "error": "missing_packet_files",
                    "missing": missing,
                    "provider_calls": PROVIDER_CALLS,
                },
                indent=2,
            )
        )

    lock = read_json(packet_dir / "packet_lock.json")
    locked_files = lock.get("locked_files") or {}
    hash_errors: list[str] = []
    for rel, expected in locked_files.items():
        path = packet_dir / rel
        if not path.exists():
            hash_errors.append(f"missing locked file: {rel}")
        elif sha_file(path) != expected:
            hash_errors.append(f"locked file hash mismatch: {rel}")

    if hash_errors:
        raise SystemExit(
            json.dumps(
                {
                    "status": "D5_MINI_SCOUT_RUNNER_FAIL",
                    "error": "packet_lock_validation_failed",
                    "errors": hash_errors,
                    "provider_calls": PROVIDER_CALLS,
                },
                indent=2,
            )
        )
    return lock


def load_word_gate(packet_dir: Path) -> dict[str, Any]:
    gate = read_json(packet_dir / "deterministic_gate_policy.json")
    word_gate = gate["layer_1_deterministic_gate"]["artifact_body_word_count"]
    return {
        "min": int(word_gate["min"]),
        "max": int(word_gate["max"]),
        "scope": word_gate["scope"],
        "failure_result": word_gate["failure_result"],
    }


def deterministic_gate_precheck(packet_dir: Path, condition: str, artifact_text: str | None = None) -> dict[str, Any]:
    word_gate = load_word_gate(packet_dir)
    text = artifact_text or ""
    count = word_count(text)
    artifact_present = artifact_text is not None
    in_band = word_gate["min"] <= count <= word_gate["max"] if artifact_present else None
    return {
        "runner_id": RUNNER_ID,
        "condition": condition,
        "provider_calls": PROVIDER_CALLS,
        "artifact_present": artifact_present,
        "artifact_body_word_count": count if artifact_present else None,
        "word_count_gate": word_gate,
        "deterministic_gate_status": "not_evaluated_no_provider_smoke" if not artifact_present else ("pass" if in_band else "fail"),
        "proof_credit_eligible_if_failed": False,
        "notes": [
            "Layer 1 is admission-only.",
            "No proof credit is available if the word-count gate fails.",
        ],
    }


def visible_surface_boundary() -> dict[str, Any]:
    return {
        "model_prompts_include_architecture_evidence": False,
        "browser_packets_include_architecture_evidence": False,
        "judge_packets_include_architecture_evidence": False,
        "public_artifacts_include_architecture_evidence": False,
        "benchmark_source_packets_include_architecture_evidence": False,
        "judge_visible_allowed_fields": [
            "anonymous_artifact",
            "source_packet",
            "task_brief",
            "domain_card",
            "frozen_rubric",
        ],
    }


def proof_credit_readiness() -> dict[str, Any]:
    return {
        "fail_closed_if_architecture_evidence_missing": True,
        "proof_credit_allowed_if_architecture_evidence_missing": False,
        "diagnostic_only_if_architecture_evidence_missing": True,
        "required_evidence_validation_status": "validated",
    }


def smoke_arch_evidence(packet_dir: Path, run_id: str, condition_dir: Path) -> dict[str, Any]:
    source_packet_hash = sha_file(packet_dir / "source_packet.json")
    task_brief_hash = sha_file(packet_dir / "task_brief.md")
    lock_hash = sha_file(packet_dir / "packet_lock.json")
    state_payload = {
        "run_id": run_id,
        "packet_id": read_json(packet_dir / "source_packet.json")["packet_id"],
        "mode": "no_provider_smoke",
        "critical_constraints": [
            "use only frozen packet sources",
            "main artifact body must be 900-1300 words",
            "architecture evidence is not judge-visible",
        ],
    }
    state_hash = sha_text(json.dumps(state_payload, sort_keys=True))
    registry_entries = [
        {
            "artifact_id": "frozen_source_packet",
            "artifact_type": "source_packet",
            "artifact_hash": source_packet_hash,
            "source_refs": ["source_packet.json"],
        },
        {
            "artifact_id": "frozen_task_brief",
            "artifact_type": "task_brief",
            "artifact_hash": task_brief_hash,
            "source_refs": ["task_brief.md"],
        },
        {
            "artifact_id": "smoke_final_artifact_slot",
            "artifact_type": "reserved_output_path",
            "artifact_hash": sha_text(str(condition_dir / "artifact.md")),
            "source_refs": ["artifact.md"],
        },
    ]
    registry_hash = sha_text(json.dumps(registry_entries, sort_keys=True))
    baton_payload = {
        "run_id": run_id,
        "turn_index": 1,
        "next_model_id": "no_provider_smoke",
        "adversarial_role": "evidence_uncertainty_and_claim_boundary_reviewer",
    }
    baton_hash = sha_text(json.dumps(baton_payload, sort_keys=True))
    final_artifact_hash = sha_text("NO_PROVIDER_SMOKE_FINAL_ARTIFACT_SLOT")
    arch_evidence = {
        "schema_version": "holo_build_arch_evidence_schema_v4_1",
        "architecture_policy_id": "HOLOBUILD_PATENT_ALIGNMENT_POLICY_V4_1",
        "run_id": run_id,
        "domain_id": "D5_healthcare_medtech_evidence_synthesis",
        "condition_type": "holo_build_arch",
        "provider_calls_recorded": PROVIDER_CALLS,
        "architecture_evidence_visible_to_judges": False,
        "visible_surface_boundary": visible_surface_boundary(),
        "proof_credit_readiness": proof_credit_readiness(),
        "turns": [
            {
                "turn_index": 1,
                "state_object_hash": state_hash,
                "state_object_snapshot_path": str(condition_dir / "state_object_turn_001.json"),
                "critical_constraints_preserved": [
                    {
                        "constraint_id": "frozen_source_packet_hash",
                        "status": "preserved",
                        "evidence_hash_or_location": source_packet_hash,
                    },
                    {
                        "constraint_id": "architecture_evidence_hidden_from_judges",
                        "status": "preserved",
                        "evidence_hash_or_location": "visible_surface_boundary.judge_packets_include_architecture_evidence=false",
                    },
                ],
                "settled_decisions_if_present": {
                    "present": True,
                    "settled_decisions": [
                        {
                            "decision_id": "scout_domain_and_packet_locked",
                            "decision_hash_or_location": lock_hash,
                        }
                    ],
                },
                "artifact_registry_entries": registry_entries,
                "artifact_registry_hash": registry_hash,
                "pinned_source_hashes": [source_packet_hash, task_brief_hash, lock_hash],
                "pinned_artifact_hashes": [final_artifact_hash],
                "retrieve_by_id_or_source_reference_behavior": {
                    "required": True,
                    "observed": True,
                    "evidence_hash_or_location": "source_packet.sources[].source_id",
                },
                "token_budget_partial_injection_flags": {
                    "present": True,
                    "token_budget_limit": None,
                    "tokens_used": 0,
                    "partial_injection_used": False,
                    "partial_injection_reason": None,
                },
                "baton_pass": {
                    "baton_pass_hash": baton_hash,
                    "baton_pass_path": str(condition_dir / "baton_pass_turn_001.json"),
                    "next_model_id": "no_provider_smoke",
                    "adversarial_role": "evidence_uncertainty_and_claim_boundary_reviewer",
                },
                "selected_model": {
                    "provider": "no_provider_smoke",
                    "exact_model_id": "no_provider_smoke",
                    "endpoint": "none",
                },
                "adversarial_role": "evidence_uncertainty_and_claim_boundary_reviewer",
                "role_compliance_result": {
                    "status": "not_checked",
                    "evidence_hash_or_location": "no_provider_smoke_no_model_turn",
                },
                "state_audit_constraint_preservation_result": {
                    "state_audit_status": "pass",
                    "constraint_preservation_status": "pass",
                    "evidence_hash_or_location": state_hash,
                },
                "synthesis_trigger": {
                    "triggered": True,
                    "reason": "no_provider_smoke_wires_final_artifact_slot",
                },
            }
        ],
        "final": {
            "synthesis_trigger": "no_provider_smoke_wires_final_artifact_slot",
            "final_artifact_hash": final_artifact_hash,
            "final_artifact_path": str(condition_dir / "artifact.md"),
            "final_state_object_hash": state_hash,
            "final_artifact_registry_hash": registry_hash,
            "architecture_evidence_visible_to_judges": False,
        },
    }
    write_json(condition_dir / "state_object_turn_001.json", state_payload)
    write_json(condition_dir / "baton_pass_turn_001.json", baton_payload)
    return arch_evidence


def validate_smoke_arch_evidence(evidence: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_top = {
        "schema_version",
        "architecture_policy_id",
        "run_id",
        "domain_id",
        "condition_type",
        "provider_calls_recorded",
        "architecture_evidence_visible_to_judges",
        "visible_surface_boundary",
        "proof_credit_readiness",
        "turns",
        "final",
    }
    missing = sorted(required_top - set(evidence))
    if missing:
        errors.append(f"arch evidence missing top-level fields: {missing}")
    if evidence.get("architecture_evidence_visible_to_judges") is not False:
        errors.append("arch evidence is judge-visible")
    if evidence.get("condition_type") != "holo_build_arch":
        errors.append("arch evidence condition_type mismatch")
    turns = evidence.get("turns") or []
    if not turns:
        errors.append("arch evidence has no turns")
    else:
        turn = turns[0]
        required_turn = {
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
        }
        missing_turn = sorted(required_turn - set(turn))
        if missing_turn:
            errors.append(f"arch evidence missing per-turn fields: {missing_turn}")
    final = evidence.get("final") or {}
    if final.get("architecture_evidence_visible_to_judges") is not False:
        errors.append("final arch evidence visibility is not false")
    return errors


def write_condition_smoke(packet_dir: Path, run_id: str, condition: str) -> dict[str, Any]:
    run_dir = packet_dir / "runs" / run_id
    condition_dir = run_dir / condition
    condition_dir.mkdir(parents=True, exist_ok=True)
    lock = read_json(packet_dir / "packet_lock.json")
    source_packet_hash = sha_file(packet_dir / "source_packet.json")
    gate = deterministic_gate_precheck(packet_dir, condition)
    metadata = {
        "runner_id": RUNNER_ID,
        "run_id": run_id,
        "condition": condition,
        "condition_label": CONDITION_LABELS[condition],
        "status": "planned_no_provider_smoke",
        "created_at_utc": utc_iso(),
        "provider_calls": PROVIDER_CALLS,
        "live_artifacts_generated": LIVE_ARTIFACTS_GENERATED,
        "scores_generated": SCORES_GENERATED,
        "packet_dir": str(packet_dir),
        "packet_id": lock["packet_id"],
        "packet_hash": source_packet_hash,
        "frozen_task_brief_hash": sha_file(packet_dir / "task_brief.md"),
        "frozen_source_packet_hash": source_packet_hash,
        "artifact_path": str(condition_dir / "artifact.md"),
        "artifact_written": False,
        "deterministic_gate_precheck_path": str(condition_dir / "deterministic_gate_precheck.json"),
        "architecture_evidence_path": str(condition_dir / "arch_evidence.json") if condition == "holo_build_arch" else None,
    }
    write_json(condition_dir / "deterministic_gate_precheck.json", gate)
    write_json(condition_dir / "artifact_metadata.json", metadata)

    arch_status = "not_applicable"
    arch_errors: list[str] = []
    if condition == "holo_build_arch":
        evidence = smoke_arch_evidence(packet_dir, run_id, condition_dir)
        arch_errors = validate_smoke_arch_evidence(evidence)
        arch_status = "wired_and_schema_shape_valid" if not arch_errors else "invalid"
        write_json(condition_dir / "arch_evidence.json", evidence)

    result = {
        "condition": condition,
        "condition_dir": str(condition_dir),
        "packet_hash": source_packet_hash,
        "deterministic_gate_precheck": gate["deterministic_gate_status"],
        "artifact_slots_wired": ["artifact.md", "artifact_metadata.json", "deterministic_gate_precheck.json"],
        "architecture_evidence_status": arch_status,
        "architecture_evidence_errors": arch_errors,
        "provider_calls": PROVIDER_CALLS,
    }
    return result


def update_run_manifest(packet_dir: Path, run_id: str, condition_results: list[dict[str, Any]]) -> dict[str, Any]:
    run_dir = packet_dir / "runs" / run_id
    manifest_path = run_dir / "run_manifest.json"
    previous: dict[str, Any] = {}
    if manifest_path.exists():
        previous = read_json(manifest_path)
    existing = {item["condition"]: item for item in previous.get("conditions", [])}
    for item in condition_results:
        existing[item["condition"]] = item
    manifest = {
        "runner_id": RUNNER_ID,
        "run_id": run_id,
        "status": "NO_PROVIDER_SMOKE_READY",
        "updated_at_utc": utc_iso(),
        "packet_dir": str(packet_dir),
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "conditions": [existing[key] for key in VALID_CONDITIONS if key in existing],
        "provider_calls": PROVIDER_CALLS,
        "live_artifacts_generated": LIVE_ARTIFACTS_GENERATED,
        "scores_generated": SCORES_GENERATED,
        "live_mode_fail_closed": True,
        "live_requires_flag": "--live",
        "live_requires_env": f"{LIVE_APPROVAL_ENV}=1",
    }
    write_json(manifest_path, manifest)
    return manifest


def run_no_provider_smoke(packet_dir: Path, run_id: str, conditions: list[str]) -> int:
    require_packet(packet_dir)
    results = [write_condition_smoke(packet_dir, run_id, condition) for condition in conditions]
    manifest = update_run_manifest(packet_dir, run_id, results)
    status = "D5_MINI_SCOUT_RUNNER_NO_PROVIDER_SMOKE_PASS"
    if any(item.get("architecture_evidence_errors") for item in results):
        status = "D5_MINI_SCOUT_RUNNER_NO_PROVIDER_SMOKE_FAIL"
    print(
        json.dumps(
            {
                "status": status,
                "runner_id": RUNNER_ID,
                "run_id": run_id,
                "packet_hash": manifest["packet_hash"],
                "conditions": results,
                "run_manifest": str(packet_dir / "runs" / run_id / "run_manifest.json"),
                "provider_calls": PROVIDER_CALLS,
                "live_artifacts_generated": LIVE_ARTIFACTS_GENERATED,
                "scores_generated": SCORES_GENERATED,
                "live_mode_fail_closed": True,
                "live_requires": ["--live", f"{LIVE_APPROVAL_ENV}=1"],
            },
            indent=2,
        )
    )
    return 0 if status.endswith("_PASS") else 1


def run_live_guarded(packet_dir: Path, run_id: str, conditions: list[str], timeout: int) -> int:
    require_packet(packet_dir)
    if os.getenv(LIVE_APPROVAL_ENV) != "1":
        print(
            json.dumps(
                {
                    "status": "D5_MINI_SCOUT_LIVE_FAIL_CLOSED",
                    "reason": f"live mode requires {LIVE_APPROVAL_ENV}=1 in addition to --live",
                    "provider_calls": PROVIDER_CALLS,
                },
                indent=2,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "status": "D5_MINI_SCOUT_LIVE_WIRING_PRESENT_PROVIDER_CALLS_NOT_IMPLEMENTED_IN_THIS_LANE",
                "reason": "This adapter is deliberately wired fail-closed until the separate provider-generation lane is approved.",
                "run_id": run_id,
                "conditions": conditions,
                "timeout": timeout,
                "packet_hash": sha_file(packet_dir / "source_packet.json"),
                "provider_calls": PROVIDER_CALLS,
            },
            indent=2,
        )
    )
    return 3


def main() -> int:
    parser = argparse.ArgumentParser(description="D5 mini scout HoloBuild vs GPT-5.5 adapter.")
    parser.add_argument("--packet-dir", default=str(DEFAULT_PACKET_DIR))
    parser.add_argument("--condition", action="append", choices=VALID_CONDITIONS, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--no-provider-smoke", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    packet_dir = Path(args.packet_dir).resolve()
    conditions = list(dict.fromkeys(args.condition))
    if args.live:
        return run_live_guarded(packet_dir, args.run_id, conditions, args.timeout)
    return run_no_provider_smoke(packet_dir, args.run_id, conditions)


if __name__ == "__main__":
    raise SystemExit(main())
