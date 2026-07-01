#!/usr/bin/env python3
"""Regression checks for the Wave 2 statistical claim guardrail."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILDER_PATH = REPO_ROOT / "docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py"
BATCH005_APPROVAL = (
    REPO_ROOT
    / "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
    / "holo_target_batches/wave2_holo_target_batch_005"
    / "WAVE2_HOLO_TARGET_BATCH_005_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
)


def load_builder() -> Any:
    spec = importlib.util.spec_from_file_location("wave2_statistical_claim_guardrail_builder", BUILDER_PATH)
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
    expected = builder.build_guardrail()
    md = builder.OUT_MD.read_text()

    assert builder.package_sha256(actual) == actual["package_sha256"], actual["package_sha256"]
    assert without_volatile_fields(actual) == without_volatile_fields(expected), "statistical_guardrail_output_is_stale"
    assert actual["status"] == "PASS", actual
    assert actual["generated_without_provider_calls"] is True, actual
    assert actual["summary"]["provider_calls_made_by_guardrail"] == 0, actual["summary"]
    assert actual["summary"]["checks_failed"] == 0, actual["summary"]

    claim = actual["claim_boundary"]
    assert claim["current_claim"] == builder.CURRENT_CLAIM, claim
    assert claim["statistical_proof_claim"] == builder.STATISTICAL_PROOF_CLAIM, claim
    assert "full-family Wave 2 statistical proof complete" in claim["disallowed_current_claims"], claim

    lane = actual["statistical_lane"]
    assert lane["current_scored_pairs"] == 37, lane
    assert lane["current_scored_packets"] == 74, lane
    assert lane["current_per_class_n"] == 37, lane
    assert lane["full_family_pairs"] == 60, lane
    assert lane["per_class_n_after_clean_batch004"] == 37, lane
    assert lane["per_class_n_after_clean_batch004_and_batch005"] == 60, lane

    required_checks = {
        "metrics_claim_boundary_declared",
        "ledger_claim_boundary_declared",
        "current_wave2_holo_metric_rows_are_selected_target_tier",
        "current_selected_target_counts_37_pairs_74_packets",
        "current_per_class_n_below_full_family_n",
        "rule_of_three_threshold_not_met_for_fpr_fnr",
        "after_batch004_still_below_60_per_class",
        "batch004_scored_selected_target_evidence",
        "batch005_needed_for_60_per_class_requires_separate_approval",
        "batch005_has_no_approval_packet",
        "future_planning_rows_present",
        "missing_repo_evidence_not_inferred",
        "provider_boundary_closed",
    }
    passed_checks = {row["check_id"] for row in actual["checks"] if row["passed"]}
    assert required_checks <= passed_checks, sorted(required_checks - passed_checks)
    assert not BATCH005_APPROVAL.exists(), BATCH005_APPROVAL

    metrics = {row["metric"]: row for row in lane["significance_rows"]}
    assert metrics["FNR"]["n"] == 37, metrics
    assert metrics["FPR"]["n"] == 37, metrics
    assert metrics["overall_error"]["n"] == 74, metrics
    assert metrics["operational_non_success"]["n"] == 74, metrics
    assert metrics["FNR"]["zero_error_n_for_95_upper_lt_5pct"] == 60, metrics
    assert metrics["FPR"]["zero_error_n_for_95_upper_lt_5pct"] == 60, metrics

    planning_metrics = {row["metric"] for row in lane["planning_rows"]}
    assert builder.REQUIRED_PLANNING_METRICS <= planning_metrics, planning_metrics
    assert actual["missingness_policy"]["missing_rows"][0]["architecture_packet_correct"] == "MISSING_REPO_EVIDENCE"
    assert "Current claim: `SELECTED_TARGET_EVIDENCE_ONLY_NOT_FULL_FAMILY_STATISTICAL_PROOF`" in md, md
    assert "Do not infer missing repository evidence into proof-credit." in md, md

    print(
        json.dumps(
            {
                "current_claim": claim["current_claim"],
                "provider_calls_made": 0,
                "statistical_guardrail_sha256": actual["package_sha256"],
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
