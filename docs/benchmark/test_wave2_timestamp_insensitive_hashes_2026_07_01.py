#!/usr/bin/env python3
"""Verify Wave 2 no-provider package hashes ignore generation timestamps."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = REPO_ROOT / "docs/benchmark"
BATCHES_ROOT = (
    BENCHMARK_ROOT
    / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
    / "holo_target_batches"
)


def load_module(label: str, relpath: str) -> Any:
    path = REPO_ROOT / relpath
    spec = importlib.util.spec_from_file_location(label, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could_not_load:{relpath}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(relpath: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / relpath).read_text())


def mutate_timestamp(data: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(data)
    mutated["created_at_utc"] = "2099-01-01T00:00:00+00:00"
    return mutated


def assert_timestamp_insensitive(label: str, data: dict[str, Any], hash_fn: Any) -> None:
    declared = data["package_sha256"]
    mutated = mutate_timestamp(data)
    assert hash_fn(data) == declared, label
    assert hash_fn(mutated) == declared, label


def main() -> int:
    os.chdir(REPO_ROOT)
    approval_builder = load_module(
        "approval_builder",
        "docs/benchmark/build_wave2_batch004_provider_approval_packet_2026_07_01.py",
    )
    runner = load_module("wave2_runner", "docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py")
    control_builder = load_module(
        "control_builder",
        "docs/benchmark/build_wave2_domain_control_room_2026_07_01.py",
    )
    ledger_builder = load_module(
        "ledger_builder",
        "docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py",
    )
    ordering_builder = load_module(
        "ordering_builder",
        "docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py",
    )
    readiness_builder = load_module(
        "readiness_builder",
        "docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py",
    )
    validation_builder = load_module(
        "validation_builder",
        "docs/benchmark/validate_wave2_no_provider_control_room_2026_07_01.py",
    )
    preservation_builder = load_module(
        "preservation_builder",
        "docs/benchmark/build_wave2_domain_preservation_manifest_2026_07_01.py",
    )
    completion_audit_builder = load_module(
        "completion_audit_builder",
        "docs/benchmark/build_wave2_domain_completion_audit_2026_07_01.py",
    )
    selective_staging_builder = load_module(
        "selective_staging_builder",
        "docs/benchmark/build_wave2_domain_selective_staging_plan_2026_07_01.py",
    )
    operator_handoff_builder = load_module(
        "operator_handoff_builder",
        "docs/benchmark/build_wave2_domain_operator_handoff_2026_07_01.py",
    )
    statistical_guardrail_builder = load_module(
        "statistical_guardrail_builder",
        "docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py",
    )

    approval = read_json(
        "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
        "/holo_target_batches/wave2_holo_target_batch_004"
        "/WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
    )
    control = read_json("docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.json")
    ledger = read_json(
        "docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01"
        "/HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.json"
    )
    ordering = read_json(
        "docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01"
        "/WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.json"
    )
    readiness = read_json(
        "docs/benchmark/wave2_domain_completion_readiness_2026_07_01"
        "/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json"
    )
    validation = read_json(
        "docs/benchmark/wave2_domain_control_room_2026_07_01"
        "/WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01.json"
    )
    preservation = read_json(
        "docs/benchmark/wave2_domain_control_room_2026_07_01"
        "/WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.json"
    )
    completion_audit = read_json(
        "docs/benchmark/wave2_domain_control_room_2026_07_01"
        "/WAVE2_DOMAIN_COMPLETION_AUDIT_2026_07_01.json"
    )
    selective_staging = read_json(
        "docs/benchmark/wave2_domain_control_room_2026_07_01"
        "/WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.json"
    )
    operator_handoff = read_json(
        "docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_OPERATOR_HANDOFF_2026_07_01.json"
    )
    statistical_guardrail = read_json(
        "docs/benchmark/wave2_domain_control_room_2026_07_01"
        "/WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.json"
    )

    assert_timestamp_insensitive("approval_builder", approval, approval_builder.package_sha256)
    assert_timestamp_insensitive("runner_approval_gate", approval, runner.package_sha256)
    assert_timestamp_insensitive("control_room", control, control_builder.package_sha256)
    assert_timestamp_insensitive("ledger", ledger, ledger_builder.sha256_json)
    assert_timestamp_insensitive("ordering", ordering, ordering_builder.sha256_json)
    assert_timestamp_insensitive("readiness", readiness, readiness_builder.package_sha256)
    assert_timestamp_insensitive("validation", validation, validation_builder.package_sha256)
    assert_timestamp_insensitive("preservation", preservation, preservation_builder.package_sha256)
    assert_timestamp_insensitive("completion_audit", completion_audit, completion_audit_builder.package_sha256)
    assert_timestamp_insensitive("selective_staging", selective_staging, selective_staging_builder.package_sha256)
    assert_timestamp_insensitive("operator_handoff", operator_handoff, operator_handoff_builder.package_sha256)
    assert_timestamp_insensitive(
        "statistical_guardrail",
        statistical_guardrail,
        statistical_guardrail_builder.package_sha256,
    )

    assert control["current_state"]["next_allowed_live_batch"] == "WAVE2_HOLO_TARGET_BATCH_005"
    assert not (
        BATCHES_ROOT
        / "wave2_holo_target_batch_005"
        / "WAVE2_HOLO_TARGET_BATCH_005_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
    ).exists()

    print(
        json.dumps(
            {
                "approval_packet_sha256": approval["package_sha256"],
                "checked_artifacts": [
                    "approval_builder",
                    "runner_approval_gate",
                    "control_room",
                    "ledger",
                    "ordering",
                    "readiness",
                    "validation",
                    "preservation",
                    "completion_audit",
                    "selective_staging",
                    "operator_handoff",
                    "statistical_guardrail",
                ],
                "provider_calls_made": 0,
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
