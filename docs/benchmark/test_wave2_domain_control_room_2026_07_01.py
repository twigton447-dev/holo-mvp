#!/usr/bin/env python3
"""Regression checks for the no-provider Wave 2 domain control room."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILDER_PATH = REPO_ROOT / "docs/benchmark/build_wave2_domain_control_room_2026_07_01.py"


def load_builder() -> Any:
    spec = importlib.util.spec_from_file_location("wave2_domain_control_room_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could_not_load_builder:{BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def without_volatile_fields(report: dict[str, Any]) -> dict[str, Any]:
    body = copy.deepcopy(report)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    return body


def main() -> int:
    os.chdir(REPO_ROOT)
    builder = load_builder()
    actual = json.loads(builder.OUT_JSON.read_text())
    expected = builder.build_control_room()
    md = builder.OUT_MD.read_text()

    assert builder.package_hash_valid(actual), actual.get("package_sha256")
    assert without_volatile_fields(actual) == without_volatile_fields(expected), "control_room_output_is_stale"
    assert actual["status"] == "PASS", actual["status"]
    assert actual["summary"]["checks_failed"] == 0, actual["summary"]

    passed_checks = {row["check_id"] for row in actual["checks"] if row["passed"]}
    required_checks = {
        "declared_source_package_hashes_valid",
        "current_phase_pre_batch004_live",
        "next_allowed_live_batch004",
        "batch004_approval_hash_valid",
        "batch004_run_command_embeds_exact_hash_and_statement",
        "batch004_live_gate_pass",
        "batch004_no_provider_calls_started",
        "batch005_gate_expected_locked_state",
        "batch005_live_gate_locked",
        "batch005_lock_blockers_exact",
        "batch005_no_provider_calls_started",
        "batch005_has_no_approval_packet",
        "full_family_remainder_staged_to_60",
        "domain_rows_all_staged_after_batch005",
    }
    missing_checks = sorted(required_checks - passed_checks)
    assert not missing_checks, missing_checks

    current = actual["current_state"]
    assert current["current_phase"] == "PRE_BATCH_004_LIVE", current
    assert current["next_allowed_live_batch"] == "WAVE2_HOLO_TARGET_BATCH_004", current
    assert current["current_scored_pairs"] == 27, current
    assert current["per_class_n_after_clean_batch004"] == 37, current
    assert current["per_class_n_after_clean_batch004_and_batch005"] == 60, current

    batch004 = actual["gates"]["batch004"]
    batch005 = actual["gates"]["batch005"]
    approval_sha = batch004["approval_packet_sha256"]
    run_command = batch004["run_command_after_explicit_approval"]
    assert batch004["approval_status"] == "READY_FOR_EXPLICIT_PROVIDER_APPROVAL", batch004
    assert batch004["approval_granted_by_packet"] is False, batch004
    assert f"--approval-packet-sha256 {approval_sha}" in run_command, run_command
    assert batch004["required_approval_statement"] in run_command, run_command
    assert batch004["expected_counts"]["total_provider_calls"] == 100, batch004
    assert batch004["providers_called"] == 0 and batch004["live_holo_started"] is False, batch004

    assert batch005["live_execution_gate"]["status"] == "LOCKED", batch005
    assert batch005["live_execution_gate"]["blocked_reason"] == builder.EXPECTED_BATCH005_LOCK_BLOCKERS, batch005
    assert batch005["expected_counts"]["total_provider_calls"] == 230, batch005
    assert batch005["providers_called"] == 0 and batch005["live_holo_started"] is False, batch005
    assert not builder.BATCH005_APPROVAL.exists(), builder.BATCH005_APPROVAL

    for row in actual["domain_rows"]:
        staged_total = (
            row["scored_holo_target_pairs"]
            + row["staged_holo_target_pairs"]
            + row["staged_full_family_remainder_pairs"]
            + row["unstaged_full_family_pairs_after_batch005"]
        )
        assert staged_total == row["frozen_pairs"], row
        assert row["unstaged_full_family_pairs_after_batch005"] == 0, row
    assert sum(row["frozen_pairs"] for row in actual["domain_rows"]) == 60, actual["domain_rows"]

    assert f"Package SHA-256: `{actual['package_sha256']}`" in md
    assert run_command in md
    assert "python3 -B docs/benchmark/run_wave2_domain_no_provider_refresh_2026_07_01.py" in md
    assert "python3 -B docs/benchmark/validate_wave2_no_provider_control_room_2026_07_01.py" in md
    assert "python3 -B docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py" in md
    assert "python3 -B docs/benchmark/build_wave2_domain_selective_staging_plan_2026_07_01.py" in md
    assert "python3 -B docs/benchmark/build_wave2_domain_operator_handoff_2026_07_01.py" in md
    assert "Batch005 | `LOCKED_UNTIL_BATCH004_LIVE_COMPARISON_PROMOTION_AND_SEPARATE_APPROVAL`" in md

    print(
        json.dumps(
            {
                "approval_packet_sha256": approval_sha,
                "batch004_expected_provider_calls": batch004["expected_counts"]["total_provider_calls"],
                "batch005_blocked_by": batch005["live_execution_gate"]["blocked_reason"],
                "control_room_package_sha256": actual["package_sha256"],
                "domain_pairs": sum(row["frozen_pairs"] for row in actual["domain_rows"]),
                "provider_calls_made": batch004["providers_called"] + batch005["providers_called"],
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
