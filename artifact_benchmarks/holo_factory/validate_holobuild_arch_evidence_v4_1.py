from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


FACTORY = Path(__file__).resolve().parent
SCHEMA_PATH = FACTORY / "schemas/holo_build_arch_evidence_schema.json"
POLICY_PATH = FACTORY / "architecture_policies/holobuild_patent_alignment_policy_v4_1.json"

PROVIDER_CALLS = 0
LIVE_ARTIFACTS_GENERATED = 0
SCORES_GENERATED = 0

TURN_REQUIRED = {
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

FINAL_REQUIRED = {
    "synthesis_trigger",
    "final_artifact_hash",
    "final_artifact_path",
    "final_state_object_hash",
    "final_artifact_registry_hash",
    "architecture_evidence_visible_to_judges",
}

JUDGE_ALLOWLIST = {
    "anonymous_artifact",
    "source_packet",
    "task_brief",
    "domain_card",
    "frozen_rubric",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def schema_required(schema: dict[str, Any], path: list[str]) -> set[str]:
    node: Any = schema
    for key in path:
        node = node[key]
    return set(node.get("required") or [])


def main() -> int:
    errors: list[str] = []
    require(SCHEMA_PATH.exists(), errors, f"missing schema: {SCHEMA_PATH}")
    require(POLICY_PATH.exists(), errors, f"missing policy: {POLICY_PATH}")

    if errors:
        print(json.dumps({"status": "HOLOBUILD_ARCH_EVIDENCE_V4_1_VALIDATION_FAIL", "provider_calls": 0, "errors": errors}, indent=2))
        return 1

    schema = read_json(SCHEMA_PATH)
    policy = read_json(POLICY_PATH)

    require(schema.get("properties", {}).get("architecture_evidence_visible_to_judges", {}).get("const") is False, errors, "schema does not force architecture_evidence_visible_to_judges=false")
    require(schema.get("properties", {}).get("architecture_policy_id", {}).get("const") == "HOLOBUILD_PATENT_ALIGNMENT_POLICY_V4_1", errors, "schema policy id mismatch")
    require(set(policy.get("required_run_metadata_per_turn") or []) >= TURN_REQUIRED, errors, "policy missing required per-turn metadata")
    require(set(policy.get("required_final_metadata") or []) >= FINAL_REQUIRED, errors, "policy missing required final metadata")

    turn_required = schema_required(schema, ["properties", "turns", "items"])
    final_required = schema_required(schema, ["properties", "final"])
    require(turn_required >= TURN_REQUIRED, errors, "schema missing required per-turn metadata")
    require(final_required >= FINAL_REQUIRED, errors, "schema missing required final metadata")

    require(policy.get("provider_calls") == 0, errors, "policy provider_calls is not 0")
    require(policy.get("architecture_evidence_visible_to_judges") is False, errors, "policy exposes architecture evidence to judges")
    require(policy.get("architecture_evidence_visible_to_model_prompts") is False, errors, "policy exposes architecture evidence to prompts")
    require(policy.get("architecture_evidence_visible_to_browser_packets") is False, errors, "policy exposes architecture evidence to browser packets")
    require(policy.get("architecture_evidence_visible_to_public_artifacts") is False, errors, "policy exposes architecture evidence to public artifacts")
    require(policy.get("architecture_evidence_visible_to_benchmark_source_packets") is False, errors, "policy exposes architecture evidence to source packets")
    require(set(policy.get("judge_visible_allowed_fields") or []) == JUDGE_ALLOWLIST, errors, "judge allowlist mismatch")

    readiness = policy.get("fail_closed_readiness") or {}
    require(readiness.get("holo_build_artifact_proof_credit_requires_valid_architecture_evidence") is True, errors, "proof credit does not require architecture evidence")
    require(readiness.get("proof_credit_allowed_if_required_architecture_evidence_missing") is False, errors, "policy allows proof credit when evidence is missing")
    require(readiness.get("diagnostic_only_if_required_architecture_evidence_missing") is True, errors, "policy does not mark missing evidence diagnostic-only")

    result = {
        "status": "HOLOBUILD_ARCH_EVIDENCE_V4_1_VALIDATION_PASS" if not errors else "HOLOBUILD_ARCH_EVIDENCE_V4_1_VALIDATION_FAIL",
        "provider_calls": PROVIDER_CALLS,
        "live_artifacts_generated": LIVE_ARTIFACTS_GENERATED,
        "scores_generated": SCORES_GENERATED,
        "architecture_evidence_visible_to_judges": False,
        "judge_visible_allowed_fields": sorted(JUDGE_ALLOWLIST),
        "schema_hash": sha256(SCHEMA_PATH),
        "policy_hash": sha256(POLICY_PATH),
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
