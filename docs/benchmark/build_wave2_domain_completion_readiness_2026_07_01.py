#!/usr/bin/env python3
"""Build a no-provider Wave 2 domain completion readiness report."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FREEZE_ROOT = Path("docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01")
BATCHES_ROOT = FREEZE_ROOT / "holo_target_batches"
OUT_ROOT = Path("docs/benchmark/wave2_domain_completion_readiness_2026_07_01")
OUT_JSON = OUT_ROOT / "WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json"
OUT_MD = OUT_ROOT / "WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.md"

PACKET_INDEX = FREEZE_ROOT / "manifests/PACKET_INDEX.json"
TARGET_SELECTION = FREEZE_ROOT / "solo_triage_3mini/WAVE2_HOLO_TARGET_SELECTION_FROM_SOLO_TRIAGE_2026_07_01.json"
COMBINED_MEMO_001_003 = BATCHES_ROOT / "WAVE2_HOLO_TARGET_BATCH_001_002_003_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
COMBINED_MEMO_001_004 = BATCHES_ROOT / "WAVE2_HOLO_TARGET_BATCH_001_002_003_004_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
COMBINED_MEMO = COMBINED_MEMO_001_004 if COMBINED_MEMO_001_004.exists() else COMBINED_MEMO_001_003
COMPILED_PACKAGE = Path("docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/compiled_metrics_package.json")
LEDGER = Path("docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.json")
ORDERING_VERIFICATION = Path(
    "docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.json"
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def package_sha256(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    rendered = json.dumps(body, indent=2, sort_keys=True) + "\n"
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def package_sha256_no_newline(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    rendered = json.dumps(body, indent=2, sort_keys=True)
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def batch_live_approval_command(batch_number: int) -> str:
    batch_id = f"WAVE2_HOLO_TARGET_BATCH_{batch_number:03d}"
    statement = (
        f"I explicitly approve provider calls for {batch_id} only, exactly as scoped in "
        f"{batch_id}_PROVIDER_APPROVAL_PACKET_2026_07_01."
    )
    return (
        f"python3 -B docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py --batch-number {batch_number} --run-live "
        "--approval-packet-sha256 APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET "
        f"--approval-statement {json.dumps(statement)}"
    )


def batch_dir(batch_number: int) -> Path:
    return BATCHES_ROOT / f"wave2_holo_target_batch_{batch_number:03d}"


def batch_paths(batch_number: int) -> dict[str, Path]:
    bid = f"WAVE2_HOLO_TARGET_BATCH_{batch_number:03d}"
    root = batch_dir(batch_number)
    return {
        "registration": root / f"{bid}_REGISTRATION_2026_07_01.json",
        "preflight": root / f"{bid}_PREFLIGHT_2026_07_01.json",
        "live_preflight": root / f"{bid}_LIVE_PREFLIGHT_2026_07_01.json",
        "comparison": root / f"{bid}_SOLO_VS_HOLO_COMPARISON_2026_07_01.json",
    }


def selected_mode(registration: dict[str, Any], batch_number: int) -> str:
    return registration.get("selection_mode") or ("target-selection" if batch_number == 4 else "")


def expected_counts(pair_count: int) -> dict[str, int]:
    packet_count = pair_count * 2
    return {
        "gov_calls": packet_count * 2,
        "judge_calls": 0,
        "packets": packet_count,
        "pairs": pair_count,
        "solo_calls": 0,
        "total_provider_calls": packet_count * 5,
        "worker_calls": packet_count * 3,
    }


def check(checks: list[dict[str, Any]], check_id: str, passed: bool, evidence: Any) -> None:
    checks.append({"check_id": check_id, "passed": bool(passed), "evidence": evidence})


def pair_index_rows() -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in read_json(PACKET_INDEX):
        pair = grouped.setdefault(
            row["pair_id"],
            {
                "family_id": row["family_id"],
                "packet_ids": [],
                "pair_id": row["pair_id"],
                "target_bucket": row["target_bucket"],
            },
        )
        pair["packet_ids"].append(row["packet_id"])
    for row in grouped.values():
        row["packet_ids"] = sorted(row["packet_ids"])
    return grouped


def load_batch_stage(batch_number: int) -> dict[str, Any]:
    paths = batch_paths(batch_number)
    registration = read_json(paths["registration"])
    preflight = read_json(paths["preflight"])
    live_preflight = read_json(paths["live_preflight"])
    return {
        "batch_number": batch_number,
        "batch_id": registration["batch_id"],
        "claim_boundary": registration.get("claim_boundary", ""),
        "expected_counts": registration["expected_counts"],
        "live_execution_gate": live_preflight.get("live_execution_gate", {}),
        "live_holo_started": live_preflight.get("live_holo_started"),
        "live_preflight_root_signature": live_preflight.get("root_signature"),
        "live_preflight_status": live_preflight.get("status"),
        "paths": {key: str(value) for key, value in paths.items() if key != "comparison" or value.exists()},
        "preflight_ready_for_live_holo": preflight.get("ready_for_live_holo"),
        "preflight_status": preflight.get("status"),
        "providers_called": live_preflight.get("providers_called"),
        "selected_pair_ids": registration.get("selected_pair_ids", []),
        "selection_mode": selected_mode(registration, batch_number),
        "selection_mode_defaulted": registration.get("selection_mode") is None,
        "solo_started": live_preflight.get("solo_started"),
        "judges_started": live_preflight.get("judges_started"),
    }


def build_report() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    target_selection = read_json(TARGET_SELECTION)
    target_pair_ids = [row["pair_id"] for row in target_selection.get("all_top_targets", [])]
    target_pair_set = set(target_pair_ids)
    packet_pairs = pair_index_rows()
    full_family_remainder_ids = [pair_id for pair_id in sorted(packet_pairs) if pair_id not in target_pair_set]

    combined = read_json(COMBINED_MEMO)
    batch004_comparison = read_json(batch_paths(4)["comparison"]) if batch_paths(4)["comparison"].exists() else {}
    compiled = read_json(COMPILED_PACKAGE)
    ledger = read_json(LEDGER)
    wave2 = ledger["wave2"]
    statistical = wave2["statistical_lane"]
    selected = wave2["selected_target_holo"]

    check(checks, "combined_memo_hash_matches_file", combined.get("package_sha256") == package_sha256(combined), combined.get("package_sha256"))
    check(checks, "ledger_hash_matches_file", ledger.get("package_sha256") == package_sha256_no_newline(ledger), ledger.get("package_sha256"))
    check(checks, "compiled_metrics_no_provider", compiled.get("generated_without_provider_calls") is True, compiled.get("generated_without_provider_calls"))
    check(checks, "combined_memo_no_provider", combined.get("no_provider_calls_for_this_package") is True, combined.get("no_provider_calls_for_this_package"))
    check(checks, "combined_memo_no_judges", combined.get("no_judge_calls_for_this_package") is True, combined.get("no_judge_calls_for_this_package"))
    check(checks, "wave2_freeze_full_60_pairs", wave2["freeze"]["scope"].get("pairs") == 60, wave2["freeze"]["scope"])
    check(checks, "solo_triage_target_pool_37", selected.get("selected_target_pair_pool") == 37, selected.get("selected_target_pair_pool"))
    check(checks, "scored_batches_001_004", selected.get("scored_batches") == "001-004", selected.get("scored_batches"))
    check(checks, "current_scored_pairs_37", selected.get("scored_pairs") == 37, selected.get("scored_pairs"))
    check(checks, "current_holo_packets_74_of_74", selected.get("scored_packets") == 74 and selected.get("scored_packets_correct_admissible") == 74, selected)
    check(checks, "statistical_lane_current_37", statistical.get("current_per_class_n") == 37, statistical)
    check(checks, "statistical_lane_after_batch004_37", statistical.get("after_batch_004_live_per_class_n") == 37, statistical)
    check(checks, "statistical_lane_after_batch005_60", statistical.get("after_batch_004_and_remainder_stage_per_class_n") == 60, statistical)

    batch004 = load_batch_stage(4)
    batch004_pair_ids = batch004["selected_pair_ids"]
    scored_batch004_ids = [row["pair_id"] for row in batch004_comparison.get("pair_rows", [])]
    check(checks, "batch004_selection_mode_target", batch004["selection_mode"] == "target-selection", batch004["selection_mode"])
    check(checks, "batch004_pair_count_10", len(batch004_pair_ids) == 10, batch004_pair_ids)
    check(checks, "batch004_pairs_match_scored_comparison", set(batch004_pair_ids) == set(scored_batch004_ids), {"batch004": batch004_pair_ids, "comparison": scored_batch004_ids})
    check(checks, "batch004_expected_counts_100", batch004["expected_counts"] == expected_counts(10), batch004["expected_counts"])
    check(checks, "batch004_preflight_pass", batch004["preflight_status"] == "PASS" and batch004["preflight_ready_for_live_holo"] is True, batch004)
    check(checks, "batch004_live_preflight_no_provider", batch004["live_preflight_status"] == "PASS" and batch004["providers_called"] == 0, batch004)
    check(checks, "batch004_live_execution_gate_pass", batch004["live_execution_gate"].get("status") == "PASS", batch004["live_execution_gate"])
    check(checks, "batch004_no_live_started", not batch004["live_holo_started"] and not batch004["solo_started"] and not batch004["judges_started"], batch004)
    check(checks, "batch004_live_preflight_signature_present", bool(batch004["live_preflight_root_signature"]), batch004["live_preflight_root_signature"])

    batch005 = load_batch_stage(5)
    batch005_pair_ids = batch005["selected_pair_ids"]
    check(checks, "batch005_selection_mode_full_family_remainder", batch005["selection_mode"] == "full-family-remainder", batch005["selection_mode"])
    check(checks, "batch005_pair_count_23", len(batch005_pair_ids) == 23, batch005_pair_ids)
    check(checks, "batch005_no_selected_target_overlap", not (set(batch005_pair_ids) & target_pair_set), sorted(set(batch005_pair_ids) & target_pair_set))
    check(checks, "batch005_pairs_match_full_family_remainder", batch005_pair_ids == full_family_remainder_ids, {"batch005": batch005_pair_ids, "remainder": full_family_remainder_ids})
    check(checks, "batch005_expected_counts_230", batch005["expected_counts"] == expected_counts(23), batch005["expected_counts"])
    check(checks, "batch005_preflight_pass", batch005["preflight_status"] == "PASS" and batch005["preflight_ready_for_live_holo"] is True, batch005)
    check(checks, "batch005_live_preflight_no_provider", batch005["live_preflight_status"] == "PASS" and batch005["providers_called"] == 0, batch005)
    check(
        checks,
        "batch005_live_execution_gate_pass_after_batch004_promotion",
        batch005["live_execution_gate"].get("status") == "PASS"
        and batch005["live_execution_gate"].get("blocked_reason") is None,
        batch005["live_execution_gate"],
    )
    check(checks, "batch005_no_live_started", not batch005["live_holo_started"] and not batch005["solo_started"] and not batch005["judges_started"], batch005)
    check(checks, "batch005_live_preflight_signature_present", bool(batch005["live_preflight_root_signature"]), batch005["live_preflight_root_signature"])
    check(checks, "no_unstaged_full_family_pairs_after_batch005", statistical.get("full_family_pairs_unstaged_after_future_stage") == 0, statistical.get("full_family_pairs_unstaged_after_future_stage"))

    passed = all(row["passed"] for row in checks)
    report = {
        "batch004_gate": batch004,
        "batch005_gate": batch005,
        "checks": checks,
        "classification": "WAVE2_DOMAIN_COMPLETION_READINESS_NO_PROVIDER_2026_07_01",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "current_state": {
            "batch004_live_provider_calls_if_approved": batch004["expected_counts"]["total_provider_calls"],
            "batch005_live_provider_calls_if_approved": batch005["expected_counts"]["total_provider_calls"],
            "current_per_class_n": statistical["current_per_class_n"],
            "current_scored_pairs": statistical["current_scored_pairs"],
            "full_family_pairs": statistical["full_family_pairs"],
            "per_class_n_after_clean_batch004": statistical["after_batch_004_live_per_class_n"],
            "per_class_n_after_clean_batch004_and_batch005": statistical["after_batch_004_and_remainder_stage_per_class_n"],
            "remaining_selected_targets_after_batch004_staging": selected["remaining_selected_targets_after_staged"],
            "unstaged_full_family_pairs_after_batch005_staging": statistical["full_family_pairs_unstaged_after_future_stage"],
        },
        "generated_without_provider_calls": True,
        "next_gates": [
            {
                "gate": "full_no_provider_refresh",
                "status": "AVAILABLE_SINGLE_COMMAND_REFRESH",
                "command": "python3 -B docs/benchmark/run_wave2_domain_no_provider_refresh_2026_07_01.py",
            },
            {
                "gate": "ordering_verification",
                "status": "PASS_REQUIRED_BEFORE_PROVIDER_APPROVAL",
                "command": "python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py",
            },
            {
                "gate": "batch005_approval_packet",
                "status": "NOT_CREATED_SEPARATE_APPROVAL_REQUIRED",
                "command": "create a separate WAVE2_HOLO_TARGET_BATCH_005 provider approval packet before live execution",
            },
            {
                "gate": "domain_control_room",
                "status": "REFRESH_REQUIRED_AFTER_BATCH004_PROMOTION",
                "command": "python3 -B docs/benchmark/build_wave2_domain_control_room_2026_07_01.py",
            },
            {
                "gate": "batch004_live",
                "status": "COMPLETE_AND_PROMOTED",
                "command": batch_live_approval_command(4),
            },
            {
                "gate": "batch004_promotion",
                "status": "WAITING_ON_CLEAN_BATCH004_LIVE",
                "commands": [
                    "python3 -B docs/benchmark/build_wave2_holo_target_batch_comparison_2026_07_01.py --batch-number 4",
                    "python3 -B docs/benchmark/build_wave2_holo_target_combined_evidence_2026_07_01.py --batches 1 2 3 4",
                    "python3 -B docs/benchmark/compile_holoverify_holobuild_metrics_2026_07_01.py",
                    "node docs/benchmark/build_holoverify_holobuild_metrics_workbook_2026_07_01.mjs",
                    "python3 -B docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py",
                    "python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py",
                    "python3 -B docs/benchmark/build_wave2_domain_control_room_2026_07_01.py",
                ],
            },
            {
                "gate": "batch005_full_family_remainder_live",
                "status": "EVIDENCE_UNLOCKED_PENDING_SEPARATE_PROVIDER_APPROVAL",
                "command": batch_live_approval_command(5),
            },
        ],
        "package_sha256": "",
        "source_paths": {
            "combined_memo": str(COMBINED_MEMO),
            "compiled_metrics_package": str(COMPILED_PACKAGE),
            "ledger": str(LEDGER),
            "ordering_verification": str(ORDERING_VERIFICATION),
            "packet_index": str(PACKET_INDEX),
            "target_selection": str(TARGET_SELECTION),
        },
        "status": "PASS" if passed else "FAIL",
        "summary": {
            "checks_failed": sum(1 for row in checks if not row["passed"]),
            "checks_passed": sum(1 for row in checks if row["passed"]),
            "checks_total": len(checks),
            "ready_for_batch004_provider_approval": False,
            "ready_for_batch005_provider_approval": passed,
        },
    }
    report["package_sha256"] = package_sha256(report)
    return report


def render_md(report: dict[str, Any]) -> str:
    state = report["current_state"]
    b4 = report["batch004_gate"]
    b5 = report["batch005_gate"]
    lines = [
        "# Wave 2 Domain Completion Readiness",
        "",
        f"Classification: `{report['classification']}`",
        f"Package SHA-256: `{report['package_sha256']}`",
        f"Status: `{report['status']}`",
        f"Generated without provider calls: `{report['generated_without_provider_calls']}`",
        "",
        "## Current State",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Current scored pairs | `{state['current_scored_pairs']}` |",
        f"| Current per-class n | `{state['current_per_class_n']}/60` |",
        f"| Per-class n after clean Batch 004 | `{state['per_class_n_after_clean_batch004']}/60` |",
        f"| Per-class n after clean Batch 004 and Batch 005 | `{state['per_class_n_after_clean_batch004_and_batch005']}/60` |",
        f"| Remaining selected targets after Batch 004 staging | `{state['remaining_selected_targets_after_batch004_staging']}` |",
        f"| Unstaged full-family pairs after Batch 005 staging | `{state['unstaged_full_family_pairs_after_batch005_staging']}` |",
        "",
        "## Batch Gates",
        "",
        "| Gate | Mode | Pairs | Expected provider calls | Providers called | Live started | Status | Live gate |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | --- |",
        (
            f"| Batch 004 selected target | `{b4['selection_mode']}` | `{len(b4['selected_pair_ids'])}` | "
            f"`{b4['expected_counts']['total_provider_calls']}` | `{b4['providers_called']}` | "
            f"`{b4['live_holo_started']}` | `{b4['preflight_status']}` | "
            f"`{b4['live_execution_gate'].get('status')}` |"
        ),
        (
            f"| Batch 005 full-family remainder | `{b5['selection_mode']}` | `{len(b5['selected_pair_ids'])}` | "
            f"`{b5['expected_counts']['total_provider_calls']}` | `{b5['providers_called']}` | "
            f"`{b5['live_holo_started']}` | `{b5['preflight_status']}` | "
            f"`{b5['live_execution_gate'].get('status')}` |"
        ),
        "",
        "## Next Gates",
        "",
    ]
    for index, gate in enumerate(report["next_gates"], 1):
        lines.append(f"{index}. `{gate['gate']}`: `{gate['status']}`")
        if "command" in gate:
            lines.extend(["", "```bash", gate["command"], "```", ""])
        else:
            lines.extend(["", "```bash", *gate["commands"], "```", ""])

    lines.extend([
        "## Checks",
        "",
        "| Check | Result |",
        "| --- | --- |",
    ])
    for row in report["checks"]:
        lines.append(f"| `{row['check_id']}` | `{'PASS' if row['passed'] else 'FAIL'}` |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    write_json(OUT_JSON, report)
    OUT_MD.write_text(render_md(report))
    print(json.dumps({"status": report["status"], "json": str(OUT_JSON), "md": str(OUT_MD), "package_sha256": report["package_sha256"]}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
