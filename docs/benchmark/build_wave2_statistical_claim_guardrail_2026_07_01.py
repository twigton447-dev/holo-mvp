#!/usr/bin/env python3
"""Build a no-provider guardrail for Wave 2 statistical claim boundaries."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = REPO_ROOT / "docs/benchmark"
METRICS_ROOT = BENCHMARK_ROOT / "compiled_holoverify_holobuild_metrics_2026_07_01"
CONTROL_ROOT = BENCHMARK_ROOT / "wave2_domain_control_room_2026_07_01"
FREEZE_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
BATCHES_ROOT = FREEZE_ROOT / "holo_target_batches"

METRICS_PACKAGE = METRICS_ROOT / "compiled_metrics_package.json"
METRIC_SUMMARY_CSV = METRICS_ROOT / "holoverify_metric_summary.csv"
SIGNIFICANCE_PLANNER_CSV = METRICS_ROOT / "significance_planner.csv"
LEDGER = BENCHMARK_ROOT / "holoverify_domain_consolidation_ledger_2026_07_01/HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.json"
CONTROL_ROOM = CONTROL_ROOT / "WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.json"
READINESS = BENCHMARK_ROOT / "wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json"
BATCH004_APPROVAL = (
    BATCHES_ROOT
    / "wave2_holo_target_batch_004"
    / "WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
)
BATCH005_APPROVAL = (
    BATCHES_ROOT
    / "wave2_holo_target_batch_005"
    / "WAVE2_HOLO_TARGET_BATCH_005_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
)
OUT_JSON = CONTROL_ROOT / "WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.json"
OUT_MD = CONTROL_ROOT / "WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.md"

WAVE2_FAMILY = "Wave 2 / HR-Data Privacy-Finance Targeted Holo Runs"
WAVE2_HOLO_TIER = "wave2_selected_target_batches_complete"
WAVE2_SOLO_TIER = "wave2_selected_target_solo_triage_exact_roster"
CURRENT_CLAIM = "SELECTED_TARGET_EVIDENCE_ONLY_NOT_FULL_FAMILY_STATISTICAL_PROOF"
STATISTICAL_PROOF_CLAIM = "NOT_ACHIEVED_BATCH005_NOT_RUN"
REQUIRED_PLANNING_METRICS = {
    "detect_error_drop_20%_to_5%",
    "detect_error_drop_15%_to_5%",
    "detect_error_drop_10%_to_2%",
    "detect_error_drop_8%_to_1%",
}
REQUIRED_WAVE2_METRICS = {"FNR", "FPR", "overall_error", "operational_non_success"}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def sha256_text(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def package_sha256(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    return sha256_text(json.dumps(body, indent=2, sort_keys=True) + "\n")


def int_value(value: Any) -> int:
    if value in (None, ""):
        return 0
    return int(str(value))


def check(checks: list[dict[str, Any]], check_id: str, passed: bool, evidence: Any) -> None:
    checks.append({"check_id": check_id, "evidence": evidence, "passed": bool(passed)})


def wave2_holo_planner_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("evidence_family") == WAVE2_FAMILY
        and row.get("system") == "HoloVerify governed architecture"
        and row.get("model") == "3DNA governed roster"
        and row.get("evidence_tier") == WAVE2_HOLO_TIER
        and row.get("metric_scope") == "audit_grade_knew_or_admissible"
    ]


def wave2_metric_summary_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("evidence_family") == WAVE2_FAMILY
        and row.get("system") == "HoloVerify governed architecture"
        and row.get("model") == "3DNA governed roster"
        and row.get("evidence_tier") == WAVE2_HOLO_TIER
    ]


def planning_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("evidence_family") == "Future replication planning"]


def missingness_rows(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in ledger.get("compiled_evidence_families", [])
        if int_value(row.get("architecture_packet_correct_missing_rows")) > 0
    ]


def compact_metric_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for row in rows:
        compact.append(
            {
                "evidence_tier": row.get("evidence_tier"),
                "metric": row.get("metric"),
                "metric_scope": row.get("metric_scope"),
                "model": row.get("model"),
                "n": int_value(row.get("n")),
                "observed_errors": int_value(row.get("observed_errors")),
                "observed_rate": row.get("observed_rate"),
                "system": row.get("system"),
                "wilson_95_high": row.get("wilson_95_high"),
                "zero_error_n_for_95_upper_lt_5pct": int_value(row.get("if_zero_errors_n_for_95_upper_lt_5pct")),
            }
        )
    return compact


def compact_planning_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    return [
        {
            "metric": row.get("metric"),
            "metric_scope": row.get("metric_scope"),
            "n_per_arm": int_value(row.get("n")),
            "note": row.get("note"),
        }
        for row in rows
    ]


def build_guardrail() -> dict[str, Any]:
    metrics = read_json(METRICS_PACKAGE)
    metric_summary_rows = read_csv(METRIC_SUMMARY_CSV)
    significance_rows = read_csv(SIGNIFICANCE_PLANNER_CSV)
    ledger = read_json(LEDGER)
    control = read_json(CONTROL_ROOM)
    readiness = read_json(READINESS)
    approval = read_json(BATCH004_APPROVAL)

    wave2 = ledger["wave2"]
    selected = wave2["selected_target_holo"]
    statistical = wave2["statistical_lane"]
    current = control["current_state"]
    batch004 = control["gates"]["batch004"]
    batch005 = control["gates"]["batch005"]
    holo_metric_rows = wave2_holo_planner_rows(significance_rows)
    holo_metric_by_name = {row["metric"]: row for row in holo_metric_rows}
    summary_rows = wave2_metric_summary_rows(metric_summary_rows)
    planning = planning_rows(significance_rows)
    planning_by_metric = {row["metric"]: row for row in planning}
    missing_rows = missingness_rows(ledger)
    checks: list[dict[str, Any]] = []

    wave2_boundary = "Wave 2 target batches are selected-target evidence over three domains, not a full-family or per-domain statistical proof."
    ledger_boundary = "Wave 2 selected-target evidence is separated from full-family statistical proof."
    check(
        checks,
        "metrics_generated_without_provider_calls",
        metrics.get("generated_without_provider_calls") is True,
        metrics.get("generated_without_provider_calls"),
    )
    check(checks, "metrics_claim_boundary_declared", wave2_boundary in metrics.get("claim_boundaries", []), metrics.get("claim_boundaries", []))
    check(
        checks,
        "ledger_claim_boundary_declared",
        any(ledger_boundary in boundary for boundary in ledger.get("claim_boundaries", [])),
        ledger.get("claim_boundaries", []),
    )
    check(
        checks,
        "current_wave2_holo_metric_rows_are_selected_target_tier",
        len(holo_metric_rows) == 4 and set(holo_metric_by_name) == REQUIRED_WAVE2_METRICS,
        compact_metric_rows(holo_metric_rows),
    )
    check(
        checks,
        "current_selected_target_counts_37_pairs_74_packets",
        selected.get("scored_pairs") == 37
        and selected.get("scored_packets") == 74
        and selected.get("scored_packets_correct_admissible") == 74
        and current.get("current_scored_pairs") == 37
        and current.get("current_scored_packets") == 74,
        {"control_room": current, "ledger_selected_target": selected},
    )
    check(
        checks,
        "current_per_class_n_below_full_family_n",
        statistical.get("current_per_class_n") == 37
        and statistical.get("full_family_pairs") == 60
        and statistical.get("current_pairs_needed_for_60_per_class") == 23,
        statistical,
    )
    check(
        checks,
        "rule_of_three_threshold_not_met_for_fpr_fnr",
        all(
            int_value(holo_metric_by_name.get(metric, {}).get("n")) == 37
            and int_value(holo_metric_by_name.get(metric, {}).get("if_zero_errors_n_for_95_upper_lt_5pct")) == 60
            and int_value(holo_metric_by_name.get(metric, {}).get("observed_errors")) == 0
            for metric in ("FNR", "FPR")
        ),
        compact_metric_rows([holo_metric_by_name.get("FNR", {}), holo_metric_by_name.get("FPR", {})]),
    )
    check(
        checks,
        "after_batch004_still_below_60_per_class",
        statistical.get("after_batch_004_live_per_class_n") == 37
        and statistical.get("after_batch_004_live_pairs_needed_for_60_per_class") == 23,
        statistical,
    )
    check(
        checks,
        "batch004_scored_selected_target_evidence",
        batch004.get("state") == "HISTORICAL_BATCH004_APPROVAL_PACKET_BATCH004_ALREADY_PROMOTED"
        and statistical.get("current_per_class_n") == 37,
        {
            "batch004_state": batch004.get("state"),
            "current_per_class_n": statistical.get("current_per_class_n"),
        },
    )
    check(
        checks,
        "batch005_needed_for_60_per_class_requires_separate_approval",
        batch005.get("live_execution_gate", {}).get("status") == "PASS"
        and batch005.get("providers_called") == 0
        and statistical.get("after_batch_004_and_remainder_stage_per_class_n") == 60
        and readiness.get("summary", {}).get("ready_for_batch005_provider_approval") is True,
        {
            "batch005_gate": batch005.get("live_execution_gate"),
            "per_class_n_after_batch004_and_batch005": statistical.get("after_batch_004_and_remainder_stage_per_class_n"),
            "ready_for_batch005_provider_approval": readiness.get("summary", {}).get("ready_for_batch005_provider_approval"),
        },
    )
    check(checks, "batch005_has_no_approval_packet", not BATCH005_APPROVAL.exists(), str(BATCH005_APPROVAL.relative_to(REPO_ROOT)))
    check(
        checks,
        "domain_rows_are_not_current_per_domain_statistical_proofs",
        all(
            row.get("scored_holo_target_pairs", 0) < row.get("frozen_pairs", 0)
            and row.get("staged_full_family_remainder_pairs", 0) > 0
            and row.get("full_family_pairs_unstaged_after_future_stage") == 0
            for row in wave2.get("domain_rows", [])
        ),
        wave2.get("domain_rows", []),
    )
    check(
        checks,
        "future_planning_rows_present",
        REQUIRED_PLANNING_METRICS <= set(planning_by_metric),
        compact_planning_rows([planning_by_metric.get(metric, {}) for metric in sorted(REQUIRED_PLANNING_METRICS)]),
    )
    check(
        checks,
        "missing_repo_evidence_not_inferred",
        all(row.get("architecture_packet_correct") == "MISSING_REPO_EVIDENCE" for row in missing_rows),
        missing_rows,
    )
    check(
        checks,
        "provider_boundary_closed",
        control.get("summary", {}).get("provider_calls_made_by_builder") == 0
        and approval.get("approval_granted_by_this_packet") is False
        and batch004.get("providers_called") == 0
        and batch005.get("providers_called") == 0,
        {
            "approval_granted_by_this_packet": approval.get("approval_granted_by_this_packet"),
            "batch004_providers_called": batch004.get("providers_called"),
            "batch005_providers_called": batch005.get("providers_called"),
            "control_room_provider_calls": control.get("summary", {}).get("provider_calls_made_by_builder"),
        },
    )

    status = "PASS" if all(row["passed"] for row in checks) else "FAIL"
    report = {
        "checks": checks,
        "claim_boundary": {
            "allowed_current_claims": [
                "Batch001-004 selected-target Wave 2 Holo evidence: 37 pairs / 74 packets / 74 correct admissible packets.",
                "Planning-only statistical lane: 60 per-class target is identified, not currently achieved.",
                "Batch005 is evidence-unlocked but not live evidence until a separate approval packet and clean live run exist.",
            ],
            "current_claim": CURRENT_CLAIM,
            "disallowed_current_claims": [
                "all-domain live proof complete",
                "full-family Wave 2 statistical proof complete",
                "per-domain statistical proof complete",
                "Batch005 live evidence counted before explicit provider approval and clean live results",
            ],
            "statistical_proof_claim": STATISTICAL_PROOF_CLAIM,
        },
        "classification": "WAVE2_STATISTICAL_CLAIM_GUARDRAIL_NO_PROVIDER_2026_07_01",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_without_provider_calls": True,
        "missingness_policy": {
            "missing_rows": missing_rows,
            "rule": "Rows with missing file-backed packet-correct evidence must remain MISSING_REPO_EVIDENCE and must not be inferred into proof-credit.",
        },
        "package_sha256": "",
        "source_paths": {
            "batch004_approval_packet": str(BATCH004_APPROVAL.relative_to(REPO_ROOT)),
            "control_room": str(CONTROL_ROOM.relative_to(REPO_ROOT)),
            "domain_ledger": str(LEDGER.relative_to(REPO_ROOT)),
            "metric_summary_csv": str(METRIC_SUMMARY_CSV.relative_to(REPO_ROOT)),
            "metrics_package": str(METRICS_PACKAGE.relative_to(REPO_ROOT)),
            "readiness": str(READINESS.relative_to(REPO_ROOT)),
            "significance_planner_csv": str(SIGNIFICANCE_PLANNER_CSV.relative_to(REPO_ROOT)),
        },
        "statistical_lane": {
            "batch004_expected_provider_calls_if_approved": batch004.get("expected_counts", {}).get("total_provider_calls"),
            "batch005_expected_provider_calls_after_future_approval": batch005.get("expected_counts", {}).get("total_provider_calls"),
            "current_pairs_needed_for_60_per_class": statistical.get("current_pairs_needed_for_60_per_class"),
            "current_per_class_n": statistical.get("current_per_class_n"),
            "current_scored_pairs": selected.get("scored_pairs"),
            "current_scored_packets": selected.get("scored_packets"),
            "full_family_pairs": statistical.get("full_family_pairs"),
            "holo_metric_summary_rows": summary_rows,
            "per_class_n_after_clean_batch004": statistical.get("after_batch_004_live_per_class_n"),
            "per_class_n_after_clean_batch004_and_batch005": statistical.get(
                "after_batch_004_and_remainder_stage_per_class_n"
            ),
            "planning_rows": compact_planning_rows([planning_by_metric[metric] for metric in sorted(REQUIRED_PLANNING_METRICS)]),
            "significance_rows": compact_metric_rows(holo_metric_rows),
        },
        "status": status,
        "stop_rules": [
            "This guardrail does not approve provider calls.",
            "Do not call current Wave 2 selected-target evidence full-family statistical proof.",
            "Batch004 selected-target evidence is already promoted in this package.",
            "Do not count Batch005 as live evidence until a separate approval exists and a clean live run completes.",
            "Do not infer missing repository evidence into proof-credit.",
        ],
        "summary": {
            "checks_failed": sum(1 for row in checks if not row["passed"]),
            "checks_passed": sum(1 for row in checks if row["passed"]),
            "checks_total": len(checks),
            "provider_calls_made_by_guardrail": 0,
        },
    }
    report["package_sha256"] = package_sha256(report)
    return report


def render_md(report: dict[str, Any]) -> str:
    claim = report["claim_boundary"]
    lane = report["statistical_lane"]
    lines = [
        "# Wave 2 Statistical Claim Guardrail",
        "",
        f"Status: `{report['status']}`",
        f"Package SHA-256: `{report['package_sha256']}`",
        f"Generated without provider calls: `{report['generated_without_provider_calls']}`",
        "",
        "## Claim Boundary",
        "",
        f"Current claim: `{claim['current_claim']}`",
        f"Statistical proof claim: `{claim['statistical_proof_claim']}`",
        "",
        "## Statistical Lane",
        "",
        "| Item | Value |",
        "| --- | ---: |",
        f"| Current scored pairs | `{lane['current_scored_pairs']}` |",
        f"| Current scored packets | `{lane['current_scored_packets']}` |",
        f"| Current per-class n | `{lane['current_per_class_n']}` |",
        f"| Full-family pairs | `{lane['full_family_pairs']}` |",
        f"| Pairs needed for 60/class now | `{lane['current_pairs_needed_for_60_per_class']}` |",
        f"| Per-class n after clean Batch004 | `{lane['per_class_n_after_clean_batch004']}` |",
        f"| Per-class n after clean Batch004+Batch005 | `{lane['per_class_n_after_clean_batch004_and_batch005']}` |",
        "",
        "## Wave 2 Holo Significance Rows",
        "",
        "| Metric | n | Observed errors | Wilson 95 high | Zero-error n for <5% upper |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in lane["significance_rows"]:
        lines.append(
            f"| `{row['metric']}` | `{row['n']}` | `{row['observed_errors']}` | "
            f"`{row['wilson_95_high']}` | `{row['zero_error_n_for_95_upper_lt_5pct']}` |"
        )
    lines.extend(["", "## Checks", "", "| Check | Result |", "| --- | --- |"])
    for row in report["checks"]:
        lines.append(f"| `{row['check_id']}` | `{'PASS' if row['passed'] else 'FAIL'}` |")
    lines.extend(["", "## Stop Rules", ""])
    lines.extend(f"- {rule}" for rule in report["stop_rules"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    report = build_guardrail()
    write_json(OUT_JSON, report)
    write_text(OUT_MD, render_md(report))
    print(
        json.dumps(
            {
                "current_claim": report["claim_boundary"]["current_claim"],
                "json": str(OUT_JSON.relative_to(REPO_ROOT)),
                "md": str(OUT_MD.relative_to(REPO_ROOT)),
                "package_sha256": report["package_sha256"],
                "provider_calls_made": 0,
                "status": report["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
