#!/usr/bin/env python3
"""Regression checks for the Wave 2 domain operator handoff."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILDER_PATH = REPO_ROOT / "docs/benchmark/build_wave2_domain_operator_handoff_2026_07_01.py"
BATCH005_APPROVAL = (
    REPO_ROOT
    / "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
    / "holo_target_batches/wave2_holo_target_batch_005"
    / "WAVE2_HOLO_TARGET_BATCH_005_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
)


def load_builder() -> Any:
    spec = importlib.util.spec_from_file_location("wave2_domain_operator_handoff_builder", BUILDER_PATH)
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
    expected = builder.build_handoff()
    md = builder.OUT_MD.read_text()

    assert builder.package_sha256(actual) == actual["package_sha256"], actual["package_sha256"]
    assert without_volatile_fields(actual) == without_volatile_fields(expected), "operator_handoff_output_is_stale"
    assert actual["status"] == "PASS", actual
    assert actual["generated_without_provider_calls"] is True, actual
    assert actual["summary"]["provider_calls_made_by_handoff"] == 0, actual["summary"]
    assert actual["summary"]["checks_failed"] == 0, actual["summary"]

    state = actual["current_state"]
    assert state["all_domain_live_proof"] == "NOT_COMPLETE_PROVIDER_APPROVAL_REQUIRED", state
    assert state["current_scored_pairs"] == 27, state
    assert state["current_scored_packets"] == 54, state
    assert state["current_per_class_n"] == 27, state
    assert state["next_allowed_live_batch"] == "WAVE2_HOLO_TARGET_BATCH_004", state
    assert state["per_class_n_after_clean_batch004"] == 37, state
    assert state["per_class_n_after_clean_batch004_and_batch005"] == 60, state

    by_action = {row["action"]: row for row in actual["operator_path"]}
    batch004 = by_action["run_batch004_only_after_explicit_provider_approval"]
    assert batch004["expected_provider_calls"] == 100, batch004
    assert batch004["provider_calls_allowed_by_this_handoff"] is False, batch004
    assert f"--approval-packet-sha256 {batch004['approval_packet_sha256']}" in batch004[
        "command_after_approval"
    ], batch004
    assert batch004["approval_statement_required"] in batch004["command_after_approval"], batch004

    batch005 = by_action["batch005_requires_separate_future_approval"]
    assert batch005["expected_provider_calls_after_future_approval"] == 230, batch005
    assert batch005["provider_calls_allowed_by_this_handoff"] is False, batch005
    assert not BATCH005_APPROVAL.exists(), BATCH005_APPROVAL

    required_checks = {
        "batch004_approval_packet_current",
        "batch004_is_only_next_live_gate",
        "batch005_remains_locked_without_approval_packet",
        "control_room_pass",
        "preservation_and_staging_orderly",
        "provider_boundary_closed_by_handoff",
        "readiness_pass",
        "statistical_guardrail_pass",
    }
    passed_checks = {row["check_id"] for row in actual["checks"] if row["passed"]}
    assert required_checks <= passed_checks, sorted(required_checks - passed_checks)

    assert "Current claim: `SELECTED_TARGET_EVIDENCE_ONLY_NOT_FULL_FAMILY_STATISTICAL_PROOF`" in md, md
    assert "NOT_COMPLETE_PROVIDER_APPROVAL_REQUIRED" in md, md
    assert "Do not run Batch005 in the Batch004 approval window." in md, md
    assert "Do not use git add . or git add -A" in md, md

    print(
        json.dumps(
            {
                "current_claim": actual["current_claim"],
                "operator_handoff_sha256": actual["package_sha256"],
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
