#!/usr/bin/env python3
"""Build a no-provider operator handoff for Wave 2 domain completion."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = REPO_ROOT / "docs/benchmark"
CONTROL_ROOT = BENCHMARK_ROOT / "wave2_domain_control_room_2026_07_01"
BATCHES_ROOT = (
    BENCHMARK_ROOT
    / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
    / "holo_target_batches"
)

CONTROL_ROOM = CONTROL_ROOT / "WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.json"
READINESS = (
    BENCHMARK_ROOT
    / "wave2_domain_completion_readiness_2026_07_01"
    / "WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json"
)
STATISTICAL_GUARDRAIL = CONTROL_ROOT / "WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.json"
PRESERVATION = CONTROL_ROOT / "WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.json"
SELECTIVE_STAGING = CONTROL_ROOT / "WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.json"
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

OUT_JSON = CONTROL_ROOT / "WAVE2_DOMAIN_OPERATOR_HANDOFF_2026_07_01.json"
OUT_MD = CONTROL_ROOT / "WAVE2_DOMAIN_OPERATOR_HANDOFF_2026_07_01.md"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def sha256_text(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def package_sha256(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    return sha256_text(json.dumps(body, indent=2, sort_keys=True) + "\n")


def check(checks: list[dict[str, Any]], check_id: str, passed: bool, evidence: Any) -> None:
    checks.append({"check_id": check_id, "evidence": evidence, "passed": bool(passed)})


def build_handoff() -> dict[str, Any]:
    control = read_json(CONTROL_ROOM)
    readiness = read_json(READINESS)
    statistical = read_json(STATISTICAL_GUARDRAIL)
    preservation = read_json(PRESERVATION)
    staging = read_json(SELECTIVE_STAGING)
    approval = read_json(BATCH004_APPROVAL)

    state = control["current_state"]
    batch004 = control["gates"]["batch004"]
    batch005 = control["gates"]["batch005"]
    claim = statistical["claim_boundary"]
    checks: list[dict[str, Any]] = []

    check(checks, "control_room_pass", control.get("status") == "PASS", control.get("package_sha256"))
    check(checks, "readiness_pass", readiness.get("status") == "PASS", readiness.get("package_sha256"))
    check(
        checks,
        "statistical_guardrail_pass",
        statistical.get("status") == "PASS"
        and claim.get("current_claim") == "SELECTED_TARGET_EVIDENCE_ONLY_NOT_FULL_FAMILY_STATISTICAL_PROOF",
        claim,
    )
    check(
        checks,
        "preservation_and_staging_orderly_with_unrelated_dirty_reported",
        preservation.get("status") == "PASS"
        and staging.get("status") == "PASS"
        and staging.get("summary", {}).get("path_count")
        == preservation.get("summary", {}).get("tracked_or_untracked_path_count"),
        {
            "dirty_paths": preservation.get("summary", {}).get("tracked_or_untracked_path_count"),
            "other_dirty_paths": preservation.get("summary", {}).get("other_dirty_path_count"),
            "staging_paths": staging.get("summary", {}).get("path_count"),
        },
    )
    check(
        checks,
        "batch004_is_only_next_live_gate",
        state.get("next_allowed_live_batch") == "WAVE2_HOLO_TARGET_BATCH_005"
        and batch004.get("state") == "HISTORICAL_BATCH004_APPROVAL_PACKET_BATCH004_ALREADY_PROMOTED",
        {
            "batch004_state": batch004.get("state"),
            "next_allowed_live_batch": state.get("next_allowed_live_batch"),
        },
    )
    check(
        checks,
        "batch004_approval_packet_current",
        approval.get("package_sha256") == batch004.get("approval_packet_sha256")
        and approval.get("approval_statement_required") == batch004.get("required_approval_statement")
        and f"--approval-packet-sha256 {approval.get('package_sha256')}"
        in batch004.get("run_command_after_explicit_approval", ""),
        {
            "approval_packet_sha256": approval.get("package_sha256"),
            "required_approval_statement": approval.get("approval_statement_required"),
        },
    )
    check(
        checks,
        "batch005_evidence_unlocked_without_approval_packet",
        batch005.get("live_execution_gate", {}).get("status") == "PASS" and not BATCH005_APPROVAL.exists(),
        {
            "batch005_gate": batch005.get("live_execution_gate"),
            "batch005_approval_packet": str(BATCH005_APPROVAL.relative_to(REPO_ROOT)),
        },
    )
    check(
        checks,
        "provider_boundary_closed_by_handoff",
        control.get("summary", {}).get("provider_calls_made_by_builder") == 0
        and statistical.get("summary", {}).get("provider_calls_made_by_guardrail") == 0
        and staging.get("summary", {}).get("provider_calls_made_by_plan") == 0,
        {
            "control_room_provider_calls": control.get("summary", {}).get("provider_calls_made_by_builder"),
            "statistical_guardrail_provider_calls": statistical.get("summary", {}).get(
                "provider_calls_made_by_guardrail"
            ),
            "staging_plan_provider_calls": staging.get("summary", {}).get("provider_calls_made_by_plan"),
        },
    )

    operator_path = [
        {
            "action": "refresh_no_provider_control_surface",
            "command": "python3 -B docs/benchmark/run_wave2_domain_no_provider_refresh_2026_07_01.py",
            "provider_calls": 0,
            "why": "Regenerates current non-live evidence, metrics, guardrails, preservation, and validation.",
        },
        {
            "action": "review_and_optionally_stage_by_named_groups",
            "artifact": str(SELECTIVE_STAGING.relative_to(REPO_ROOT)),
            "provider_calls": 0,
            "why": "Uses path-limited git add commands; no git add . and no git add -A.",
        },
        {
            "action": "batch004_live_complete_and_promoted",
            "approval_packet_sha256": batch004.get("approval_packet_sha256"),
            "approval_statement_required": batch004.get("required_approval_statement"),
            "command_after_approval": batch004.get("run_command_after_explicit_approval"),
            "expected_provider_calls": batch004.get("expected_counts", {}).get("total_provider_calls"),
            "provider_calls_allowed_by_this_handoff": False,
        },
        {
            "action": "promote_after_clean_batch004_live",
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
            "why": "Promotes clean Batch004 live evidence into comparison, combined evidence, metrics, ledger, and guardrails.",
        },
        {
            "action": "batch005_requires_separate_future_approval",
            "blocked_by": batch005.get("live_execution_gate", {}).get("blocked_reason"),
            "expected_provider_calls_after_future_approval": batch005.get("expected_counts", {}).get(
                "total_provider_calls"
            ),
            "provider_calls_allowed_by_this_handoff": False,
            "reason": "Batch 005 evidence gate is open, but no Batch 005 provider approval packet has been created.",
        },
    ]

    report = {
        "checks": checks,
        "classification": "WAVE2_DOMAIN_OPERATOR_HANDOFF_NO_PROVIDER_2026_07_01",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "current_claim": claim.get("current_claim"),
        "current_state": {
            "all_domain_live_proof": "NOT_COMPLETE_PROVIDER_APPROVAL_REQUIRED",
            "current_scored_pairs": state.get("current_scored_pairs"),
            "current_scored_packets": state.get("current_scored_packets"),
            "current_per_class_n": state.get("current_per_class_n"),
            "next_allowed_live_batch": state.get("next_allowed_live_batch"),
            "per_class_n_after_clean_batch004": state.get("per_class_n_after_clean_batch004"),
            "per_class_n_after_clean_batch004_and_batch005": state.get(
                "per_class_n_after_clean_batch004_and_batch005"
            ),
        },
        "generated_without_provider_calls": True,
        "operator_path": operator_path,
        "package_sha256": "",
        "source_packages": {
            "batch004_approval_packet": approval.get("package_sha256"),
            "control_room": control.get("package_sha256"),
            "preservation_manifest": preservation.get("package_sha256"),
            "readiness": readiness.get("package_sha256"),
            "selective_staging_plan": staging.get("package_sha256"),
            "statistical_guardrail": statistical.get("package_sha256"),
        },
        "status": "PASS" if all(row["passed"] for row in checks) else "FAIL",
        "stop_rules": [
            "This handoff does not approve provider calls.",
            "Do not run Batch004 without the exact approval statement and approval packet SHA.",
            "Do not run Batch005 in the Batch004 approval window.",
            "Do not count staged Batch004 or Batch005 packets as live statistical proof.",
            "Do not use git add . or git add -A for this consolidation set.",
        ],
        "summary": {
            "batch004_expected_provider_calls_if_approved": batch004.get("expected_counts", {}).get(
                "total_provider_calls"
            ),
            "batch005_expected_provider_calls_after_future_approval": batch005.get("expected_counts", {}).get(
                "total_provider_calls"
            ),
            "checks_failed": sum(1 for row in checks if not row["passed"]),
            "checks_passed": sum(1 for row in checks if row["passed"]),
            "checks_total": len(checks),
            "provider_calls_made_by_handoff": 0,
        },
    }
    report["package_sha256"] = package_sha256(report)
    return report


def render_md(report: dict[str, Any]) -> str:
    state = report["current_state"]
    lines = [
        "# Wave 2 Domain Operator Handoff",
        "",
        f"Status: `{report['status']}`",
        f"Package SHA-256: `{report['package_sha256']}`",
        f"Generated without provider calls: `{report['generated_without_provider_calls']}`",
        f"Current claim: `{report['current_claim']}`",
        "",
        "## Current State",
        "",
        "| Item | Value |",
        "| --- | --- |",
        f"| All-domain live proof | `{state['all_domain_live_proof']}` |",
        f"| Current scored pairs | `{state['current_scored_pairs']}` |",
        f"| Current scored packets | `{state['current_scored_packets']}` |",
        f"| Current per-class n | `{state['current_per_class_n']}` |",
        f"| Next allowed live batch | `{state['next_allowed_live_batch']}` |",
        f"| Per-class n after clean Batch004 | `{state['per_class_n_after_clean_batch004']}` |",
        f"| Per-class n after clean Batch004+Batch005 | `{state['per_class_n_after_clean_batch004_and_batch005']}` |",
        "",
        "## Operator Path",
        "",
    ]
    for index, action in enumerate(report["operator_path"], start=1):
        lines.append(f"{index}. `{action['action']}`")
        if "command" in action:
            lines.extend(["", "```bash", action["command"], "```", ""])
        if "command_after_approval" in action:
            lines.extend(["", "```bash", action["command_after_approval"], "```", ""])
        if "commands" in action:
            lines.append("")
            lines.append("```bash")
            lines.extend(action["commands"])
            lines.append("```")
            lines.append("")
        if "approval_packet_sha256" in action:
            lines.append(f"   Approval packet SHA-256: `{action['approval_packet_sha256']}`")
        if "approval_statement_required" in action:
            lines.append(f"   Required statement: `{action['approval_statement_required']}`")
        if "blocked_by" in action:
            lines.append(f"   Blocked by: `{action['blocked_by']}`")
        if "why" in action:
            lines.append(f"   {action['why']}")
        lines.append("")
    lines.extend(["## Checks", "", "| Check | Result |", "| --- | --- |"])
    for row in report["checks"]:
        lines.append(f"| `{row['check_id']}` | `{'PASS' if row['passed'] else 'FAIL'}` |")
    lines.extend(["", "## Stop Rules", ""])
    lines.extend(f"- {rule}" for rule in report["stop_rules"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    report = build_handoff()
    write_json(OUT_JSON, report)
    OUT_MD.write_text(render_md(report))
    print(
        json.dumps(
            {
                "current_claim": report["current_claim"],
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
