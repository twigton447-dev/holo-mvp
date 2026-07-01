#!/usr/bin/env python3
"""Build the no-provider Wave 2 domain control room."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path("docs/benchmark")
FREEZE_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
BATCHES_ROOT = FREEZE_ROOT / "holo_target_batches"
LEDGER = BENCHMARK_ROOT / "holoverify_domain_consolidation_ledger_2026_07_01/HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.json"
ORDERING = BENCHMARK_ROOT / "holoverify_domain_consolidation_ledger_2026_07_01/WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.json"
READINESS = BENCHMARK_ROOT / "wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json"
COMBINED_MEMO_001_003 = BATCHES_ROOT / "WAVE2_HOLO_TARGET_BATCH_001_002_003_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
COMBINED_MEMO_001_004 = BATCHES_ROOT / "WAVE2_HOLO_TARGET_BATCH_001_002_003_004_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
COMBINED_MEMO = COMBINED_MEMO_001_004 if COMBINED_MEMO_001_004.exists() else COMBINED_MEMO_001_003
METRICS_PACKAGE = BENCHMARK_ROOT / "compiled_holoverify_holobuild_metrics_2026_07_01/compiled_metrics_package.json"
BATCH004_APPROVAL = (
    BATCHES_ROOT
    / "wave2_holo_target_batch_004"
    / "WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
)
BATCH004_APPROVAL_MD = BATCH004_APPROVAL.with_suffix(".md")
BATCH005_APPROVAL = (
    BATCHES_ROOT
    / "wave2_holo_target_batch_005"
    / "WAVE2_HOLO_TARGET_BATCH_005_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
)
OUT_ROOT = BENCHMARK_ROOT / "wave2_domain_control_room_2026_07_01"
OUT_JSON = OUT_ROOT / "WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.json"
OUT_MD = OUT_ROOT / "WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.md"
EXPECTED_BATCH005_LOCK_BLOCKERS = [
    "batch_004_comparison_exists",
    "batch_004_combined_memo_exists",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


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


def package_sha256_no_newline(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    return sha256_text(json.dumps(body, indent=2, sort_keys=True))


def package_hash_valid(data: dict[str, Any]) -> bool:
    declared = data.get("package_sha256")
    return declared in {package_sha256(data), package_sha256_no_newline(data)}


def check(checks: list[dict[str, Any]], check_id: str, passed: bool, evidence: Any) -> None:
    checks.append({"check_id": check_id, "evidence": evidence, "passed": bool(passed)})


def batch_live_preflight_path(batch_number: int) -> Path:
    suffix = f"{batch_number:03d}"
    batch_id = f"WAVE2_HOLO_TARGET_BATCH_{suffix}"
    return BATCHES_ROOT / f"wave2_holo_target_batch_{suffix}" / f"{batch_id}_LIVE_PREFLIGHT_2026_07_01.json"


def batch_registration_path(batch_number: int) -> Path:
    suffix = f"{batch_number:03d}"
    batch_id = f"WAVE2_HOLO_TARGET_BATCH_{suffix}"
    return BATCHES_ROOT / f"wave2_holo_target_batch_{suffix}" / f"{batch_id}_REGISTRATION_2026_07_01.json"


def approval_run_command(approval_packet: dict[str, Any]) -> str:
    command = approval_packet["provider_boundary"]["run_command_after_approval"]
    return command.replace("APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET", approval_packet["package_sha256"])


def source_row(path: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "classification": data.get("classification"),
        "package_hash_valid": package_hash_valid(data) if data.get("package_sha256") else None,
        "package_sha256": data.get("package_sha256"),
        "path": str(path),
        "status": data.get("status"),
    }


def batch_state(batch_number: int) -> dict[str, Any]:
    registration = read_json(batch_registration_path(batch_number))
    live_preflight = read_json(batch_live_preflight_path(batch_number))
    expected_counts = registration["expected_counts"]
    return {
        "batch_id": registration["batch_id"],
        "expected_counts": expected_counts,
        "live_execution_gate": live_preflight.get("live_execution_gate", {}),
        "live_holo_started": live_preflight.get("live_holo_started"),
        "live_preflight_path": str(batch_live_preflight_path(batch_number)),
        "live_preflight_root_signature": live_preflight.get("root_signature"),
        "live_preflight_status": live_preflight.get("status"),
        "packet_count": registration["packet_count"],
        "pair_count": registration["pair_count"],
        "providers_called": live_preflight.get("providers_called"),
        "selected_pair_ids": registration.get("selected_pair_ids", []),
        "selection_mode": live_preflight.get("selection_mode"),
        "solo_started": live_preflight.get("solo_started"),
        "judges_started": live_preflight.get("judges_started"),
    }


def build_control_room() -> dict[str, Any]:
    ledger = read_json(LEDGER)
    ordering = read_json(ORDERING)
    readiness = read_json(READINESS)
    combined = read_json(COMBINED_MEMO)
    metrics = read_json(METRICS_PACKAGE)
    approval = read_json(BATCH004_APPROVAL)
    approval_md = BATCH004_APPROVAL_MD.read_text()
    batch004 = batch_state(4)
    batch005 = batch_state(5)
    wave2 = ledger["wave2"]
    selected = wave2["selected_target_holo"]
    statistical = wave2["statistical_lane"]
    gate_state = ordering.get("gate_state", {})
    checks: list[dict[str, Any]] = []
    source_hash_validity = {
        "batch004_approval_packet": package_hash_valid(approval),
        "combined_memo": package_hash_valid(combined) if combined.get("package_sha256") else None,
        "ledger": package_hash_valid(ledger),
        "metrics_package": package_hash_valid(metrics) if metrics.get("package_sha256") else None,
        "ordering": package_hash_valid(ordering),
        "readiness": package_hash_valid(readiness),
    }
    batch004_run_command = approval_run_command(approval)

    check(checks, "ledger_generated_without_provider_calls", ledger.get("generated_without_provider_calls") is True, ledger.get("generated_without_provider_calls"))
    check(checks, "ordering_pass", ordering.get("status") == "PASS", ordering.get("status"))
    check(checks, "readiness_pass", readiness.get("status") == "PASS", readiness.get("status"))
    check(checks, "readiness_no_failed_checks", readiness.get("summary", {}).get("checks_failed") == 0, readiness.get("summary"))
    check(checks, "declared_source_package_hashes_valid", all(value is not False for value in source_hash_validity.values()), source_hash_validity)
    check(checks, "current_phase_post_batch004_evidence_locked", gate_state.get("current_phase") == "POST_BATCH_004_EVIDENCE_LOCKED", gate_state)
    check(checks, "next_allowed_live_batch005", gate_state.get("next_allowed_live_batch") == "WAVE2_HOLO_TARGET_BATCH_005", gate_state)
    check(checks, "compiled_metrics_no_provider", metrics.get("generated_without_provider_calls") is True, metrics.get("generated_without_provider_calls"))
    check(checks, "combined_memo_no_provider", combined.get("no_provider_calls_for_this_package") is True, combined.get("no_provider_calls_for_this_package"))
    check(checks, "combined_memo_no_judges", combined.get("no_judge_calls_for_this_package") is True, combined.get("no_judge_calls_for_this_package"))
    check(checks, "batch004_approval_packet_preserved", approval.get("status") in {"READY_FOR_EXPLICIT_PROVIDER_APPROVAL", "NOT_READY"}, approval.get("status"))
    check(checks, "batch004_approval_does_not_self_grant", approval.get("approval_granted_by_this_packet") is False, approval.get("approval_granted_by_this_packet"))
    check(checks, "batch004_approval_hash_valid", package_hash_valid(approval), approval.get("package_sha256"))
    check(checks, "batch004_approval_markdown_matches_packet_state", f"Package SHA-256: `{approval.get('package_sha256')}`" in approval_md, approval.get("package_sha256"))
    check(
        checks,
        "batch004_run_command_not_current_permission",
        approval.get("approval_granted_by_this_packet") is False,
        {"approval_status": approval.get("status"), "historical_command": batch004_run_command},
    )
    check(checks, "batch004_live_gate_pass", batch004["live_execution_gate"].get("status") == "PASS", batch004["live_execution_gate"])
    check(checks, "batch004_no_provider_calls_started", batch004["providers_called"] == 0 and not batch004["live_holo_started"], batch004)
    check(checks, "batch004_expected_provider_calls_100", batch004["expected_counts"].get("total_provider_calls") == 100, batch004["expected_counts"])
    check(checks, "batch004_selected_target_count_10", batch004["pair_count"] == 10 and batch004["packet_count"] == 20, batch004)
    check(
        checks,
        "batch005_gate_expected_evidence_unlocked_state",
        gate_state.get("batch_005_gate") == "EVIDENCE_UNLOCKED_PENDING_EXPLICIT_PROVIDER_APPROVAL",
        gate_state,
    )
    check(checks, "batch005_live_gate_pass", batch005["live_execution_gate"].get("status") == "PASS", batch005["live_execution_gate"])
    check(
        checks,
        "batch005_lock_blockers_cleared",
        batch005["live_execution_gate"].get("blocked_reason") is None,
        batch005["live_execution_gate"].get("blocked_reason"),
    )
    check(checks, "batch005_no_provider_calls_started", batch005["providers_called"] == 0 and not batch005["live_holo_started"], batch005)
    check(checks, "batch005_expected_provider_calls_230", batch005["expected_counts"].get("total_provider_calls") == 230, batch005["expected_counts"])
    check(checks, "batch005_remainder_count_23", batch005["pair_count"] == 23 and batch005["packet_count"] == 46, batch005)
    check(checks, "batch005_has_no_approval_packet", not BATCH005_APPROVAL.exists(), str(BATCH005_APPROVAL))
    check(checks, "current_scored_pairs_37", selected.get("scored_pairs") == 37, selected)
    check(checks, "selected_target_lane_closes_after_batch004", selected.get("remaining_selected_targets_after_staged") == 0, selected.get("remaining_selected_targets_after_staged"))
    check(checks, "full_family_remainder_staged_to_60", statistical.get("after_batch_004_and_remainder_stage_per_class_n") == 60, statistical)
    check(checks, "full_family_no_unstaged_pairs_after_batch005", statistical.get("full_family_pairs_unstaged_after_future_stage") == 0, statistical.get("full_family_pairs_unstaged_after_future_stage"))
    check(
        checks,
        "domain_rows_all_staged_after_batch005",
        all(row.get("full_family_pairs_unstaged_after_future_stage") == 0 for row in wave2["domain_rows"]),
        wave2["domain_rows"],
    )

    status = "PASS" if all(row["passed"] for row in checks) else "FAIL"
    report = {
        "checks": checks,
        "classification": "WAVE2_DOMAIN_CONTROL_ROOM_NO_PROVIDER_2026_07_01",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "current_state": {
            "current_phase": gate_state.get("current_phase"),
            "next_allowed_live_batch": gate_state.get("next_allowed_live_batch"),
            "batch005_gate": gate_state.get("batch_005_gate"),
            "scored_batches": selected.get("scored_batches"),
            "current_scored_pairs": selected.get("scored_pairs"),
            "current_scored_packets": selected.get("scored_packets"),
            "current_correct_admissible_packets": selected.get("scored_packets_correct_admissible"),
            "selected_target_pair_pool": selected.get("selected_target_pair_pool"),
            "selected_targets_remaining_after_batch004_staging": selected.get("remaining_selected_targets_after_staged"),
            "full_family_pairs": statistical.get("full_family_pairs"),
            "current_per_class_n": statistical.get("current_per_class_n"),
            "per_class_n_after_clean_batch004": statistical.get("after_batch_004_live_per_class_n"),
            "per_class_n_after_clean_batch004_and_batch005": statistical.get("after_batch_004_and_remainder_stage_per_class_n"),
            "pairs_needed_for_60_per_class_now": statistical.get("current_pairs_needed_for_60_per_class"),
            "pairs_needed_for_60_per_class_after_batch004": statistical.get("after_batch_004_live_pairs_needed_for_60_per_class"),
        },
        "domain_rows": [
            {
                "domain": row["domain"],
                "family_id": row["family_id"],
                "frozen_pairs": row["frozen_pairs"],
                "scored_holo_target_pairs": row["scored_holo_target_pairs"],
                "staged_holo_target_pairs": row["staged_holo_target_pairs"],
                "staged_full_family_remainder_pairs": row["staged_full_family_remainder_pairs"],
                "unstaged_full_family_pairs_after_batch005": row["full_family_pairs_unstaged_after_future_stage"],
                "status": row["status"],
            }
            for row in wave2["domain_rows"]
        ],
        "generated_without_provider_calls": True,
        "gates": {
            "batch004": {
                **batch004,
                "approval_packet_path": str(BATCH004_APPROVAL),
                "approval_packet_sha256": approval.get("package_sha256"),
                "approval_status": approval.get("status"),
                "approval_granted_by_packet": approval.get("approval_granted_by_this_packet"),
                "required_approval_statement": approval.get("approval_statement_required"),
                "run_command_after_explicit_approval": batch004_run_command,
                "state": "HISTORICAL_BATCH004_APPROVAL_PACKET_BATCH004_ALREADY_PROMOTED",
            },
            "batch005": {
                **batch005,
                "required_before_live": batch005["live_execution_gate"].get("required_before_live", []),
                "state": "EVIDENCE_UNLOCKED_PENDING_SEPARATE_PROVIDER_APPROVAL_PACKET",
            },
        },
        "next_actions": [
            {
                "action": "run_full_no_provider_refresh",
                "command": "python3 -B docs/benchmark/run_wave2_domain_no_provider_refresh_2026_07_01.py",
                "provider_calls": 0,
            },
            {
                "action": "validate_no_provider_control_room",
                "command": "python3 -B docs/benchmark/validate_wave2_no_provider_control_room_2026_07_01.py",
                "provider_calls": 0,
            },
            {
                "action": "build_statistical_claim_guardrail_after_control_room",
                "command": "python3 -B docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py",
                "provider_calls": 0,
            },
            {
                "action": "build_preservation_manifest_after_refresh",
                "command": "python3 -B docs/benchmark/build_wave2_domain_preservation_manifest_2026_07_01.py",
                "provider_calls": 0,
            },
            {
                "action": "build_selective_staging_plan_after_preservation",
                "command": "python3 -B docs/benchmark/build_wave2_domain_selective_staging_plan_2026_07_01.py",
                "provider_calls": 0,
            },
            {
                "action": "build_operator_handoff_after_staging_plan",
                "command": "python3 -B docs/benchmark/build_wave2_domain_operator_handoff_2026_07_01.py",
                "provider_calls": 0,
            },
            {
                "action": "refresh_no_provider_verifiers",
                "commands": [
                    "python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py",
                    "python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py",
                    "python3 -B docs/benchmark/build_wave2_batch004_provider_approval_packet_2026_07_01.py",
                    "python3 -B docs/benchmark/build_wave2_domain_control_room_2026_07_01.py",
                    "python3 -B docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py",
                ],
                "provider_calls": 0,
            },
            {
                "action": "batch004_live_complete_and_promoted",
                "command": approval_run_command(approval),
                "expected_provider_calls": batch004["expected_counts"]["total_provider_calls"],
                "provider_calls_allowed_by_this_artifact": False,
            },
            {
                "action": "post_batch004_promotion_after_clean_live",
                "commands": [
                    "python3 -B docs/benchmark/build_wave2_holo_target_batch_comparison_2026_07_01.py --batch-number 4",
                    "python3 -B docs/benchmark/build_wave2_holo_target_combined_evidence_2026_07_01.py --batches 1 2 3 4",
                    "python3 -B docs/benchmark/compile_holoverify_holobuild_metrics_2026_07_01.py",
                    "node docs/benchmark/build_holoverify_holobuild_metrics_workbook_2026_07_01.mjs",
                    "python3 -B docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py",
                    "python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py",
                    "python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py",
                    "python3 -B docs/benchmark/build_wave2_domain_control_room_2026_07_01.py",
                    "python3 -B docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py",
                ],
                "provider_calls": 0,
            },
            {
                "action": "batch005_requires_separate_future_approval",
                "blocked_by": batch005["live_execution_gate"].get("blocked_reason"),
                "expected_provider_calls_after_future_separate_approval": batch005["expected_counts"]["total_provider_calls"],
            },
        ],
        "package_sha256": "",
        "source_paths": {
            "batch004_approval_packet": str(BATCH004_APPROVAL),
            "batch004_live_preflight": str(batch_live_preflight_path(4)),
            "batch005_live_preflight": str(batch_live_preflight_path(5)),
            "combined_memo": str(COMBINED_MEMO),
            "ledger": str(LEDGER),
            "metrics_package": str(METRICS_PACKAGE),
            "ordering": str(ORDERING),
            "readiness": str(READINESS),
        },
        "sources": {
            "batch004_approval_packet": source_row(BATCH004_APPROVAL, approval),
            "combined_memo": source_row(COMBINED_MEMO, combined),
            "ledger": source_row(LEDGER, ledger),
            "metrics_package": source_row(METRICS_PACKAGE, metrics),
            "ordering": source_row(ORDERING, ordering),
            "readiness": source_row(READINESS, readiness),
        },
        "status": status,
        "stop_rules": [
            "This artifact does not approve provider calls.",
            "Run Batch 004 only after the exact approval statement and exact approval packet SHA are supplied.",
            "Do not run Batch 005 until a separate Batch 005 approval packet and explicit approval exist.",
            "Do not run solo or judge lanes from this control-room lane.",
            "Preserve selected-target evidence separately from full-family statistical proof until Batch 005 has live evidence.",
        ],
        "summary": {
            "checks_failed": sum(1 for row in checks if not row["passed"]),
            "checks_passed": sum(1 for row in checks if row["passed"]),
            "checks_total": len(checks),
            "provider_calls_made_by_builder": 0,
        },
    }
    report["package_sha256"] = package_sha256(report)
    return report


def render_md(report: dict[str, Any]) -> str:
    state = report["current_state"]
    b4 = report["gates"]["batch004"]
    b5 = report["gates"]["batch005"]
    lines = [
        "# Wave 2 Domain Control Room",
        "",
        f"Status: `{report['status']}`",
        f"Package SHA-256: `{report['package_sha256']}`",
        f"Generated without provider calls: `{report['generated_without_provider_calls']}`",
        "",
        "## Current State",
        "",
        "| Item | Value |",
        "| --- | --- |",
        f"| Current phase | `{state['current_phase']}` |",
        f"| Next allowed live batch | `{state['next_allowed_live_batch']}` |",
        f"| Scored batches | `{state['scored_batches']}` |",
        f"| Current scored pairs | `{state['current_scored_pairs']}` |",
        f"| Current scored packets correct/admissible | `{state['current_correct_admissible_packets']}/{state['current_scored_packets']}` |",
        f"| Selected-target pool | `{state['selected_target_pair_pool']}` pairs |",
        f"| Per-class n now | `{state['current_per_class_n']}` |",
        f"| Per-class n after clean Batch004 | `{state['per_class_n_after_clean_batch004']}` |",
        f"| Per-class n after clean Batch004+Batch005 | `{state['per_class_n_after_clean_batch004_and_batch005']}` |",
        f"| Pairs still needed for 60/class now | `{state['pairs_needed_for_60_per_class_now']}` |",
        f"| Pairs still needed for 60/class after Batch004 | `{state['pairs_needed_for_60_per_class_after_batch004']}` |",
        "",
        "## Domain Map",
        "",
        "| Domain | Frozen pairs | Scored target | Batch004 target staged | Batch005 remainder staged | Unstaged after Batch005 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["domain_rows"]:
        lines.append(
            f"| {row['domain']} | `{row['frozen_pairs']}` | `{row['scored_holo_target_pairs']}` | "
            f"`{row['staged_holo_target_pairs']}` | `{row['staged_full_family_remainder_pairs']}` | "
            f"`{row['unstaged_full_family_pairs_after_batch005']}` |"
        )
    lines.extend(
        [
            "",
            "## Gates",
            "",
            "| Gate | State | Pairs | Packets | Expected provider calls | Live gate |",
            "| --- | --- | ---: | ---: | ---: | --- |",
            f"| Batch004 | `{b4['state']}` | `{b4['pair_count']}` | `{b4['packet_count']}` | `{b4['expected_counts']['total_provider_calls']}` | `{b4['live_execution_gate'].get('status')}` |",
            f"| Batch005 | `{b5['state']}` | `{b5['pair_count']}` | `{b5['packet_count']}` | `{b5['expected_counts']['total_provider_calls']}` | `{b5['live_execution_gate'].get('status')}` |",
            "",
            "## Batch004 Approval",
            "",
            f"Approval packet status: `{b4['approval_status']}`",
            f"Approval granted by packet: `{b4['approval_granted_by_packet']}`",
            f"Approval packet SHA-256: `{b4['approval_packet_sha256']}`",
            "",
            "Required approval statement:",
            "",
            f"`{b4['required_approval_statement']}`",
            "",
            "Run command after explicit approval:",
            "",
            "```bash",
            b4["run_command_after_explicit_approval"],
            "```",
            "",
            "## Next Actions",
            "",
        ]
    )
    for idx, action in enumerate(report["next_actions"], start=1):
        lines.append(f"{idx}. `{action['action']}`")
        if "command" in action:
            lines.extend(["", "```bash", action["command"], "```", ""])
        if "commands" in action:
            lines.append("")
            lines.append("```bash")
            lines.extend(action["commands"])
            lines.append("```")
            lines.append("")
        if "blocked_by" in action:
            lines.append(f"   Blocked by: `{action['blocked_by']}`")
    lines.extend(
        [
            "",
            "## Stop Rules",
            "",
        ]
    )
    lines.extend(f"- {rule}" for rule in report["stop_rules"])
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Result |",
            "| --- | --- |",
        ]
    )
    for row in report["checks"]:
        lines.append(f"| `{row['check_id']}` | `{'PASS' if row['passed'] else 'FAIL'}` |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    report = build_control_room()
    write_json(OUT_JSON, report)
    write_text(OUT_MD, render_md(report))
    print(
        json.dumps(
            {
                "status": report["status"],
                "json": str(OUT_JSON),
                "md": str(OUT_MD),
                "package_sha256": report["package_sha256"],
                "checks_failed": report["summary"]["checks_failed"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
