#!/usr/bin/env python3
"""Build a no-provider domain consolidation ledger for the July 2026 benchmark lanes."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FREEZE_ROOT = Path("docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01")
METRICS_ROOT = Path("docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01")
OUT_ROOT = Path("docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01")
OUT_JSON = OUT_ROOT / "HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.json"
OUT_MD = OUT_ROOT / "HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.md"
ORDERING_VERIFICATION = OUT_ROOT / "WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.json"
READINESS_REPORT = Path("docs/benchmark/wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json")

FREEZE_MANIFEST = FREEZE_ROOT / "FREEZE_MANIFEST.json"
PACKET_INDEX = FREEZE_ROOT / "manifests/PACKET_INDEX.json"
SOLO_PACKAGE = FREEZE_ROOT / "solo_triage_3mini/WAVE2_3FAMILY_SOLO_TRIAGE_EVIDENCE_PACKAGE_2026_07_01.json"
TARGET_SELECTION = FREEZE_ROOT / "solo_triage_3mini/WAVE2_HOLO_TARGET_SELECTION_FROM_SOLO_TRIAGE_2026_07_01.json"
COMBINED_MEMO = (
    FREEZE_ROOT
    / "holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
)
BATCH004_APPROVAL_PACKET = (
    FREEZE_ROOT
    / "holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
)
COMPILED_PACKAGE = METRICS_ROOT / "compiled_metrics_package.json"
RUN_SUMMARIES = METRICS_ROOT / "holoverify_run_summaries.csv"
SIGNIFICANCE_PLANNER = METRICS_ROOT / "significance_planner.csv"

WAVE2_FAMILY = "Wave 2 / HR-Data Privacy-Finance Targeted Holo Runs"
WAVE2_HOLO_TIER = "wave2_selected_target_batches_complete"
WAVE2_SOLO_TIER = "wave2_selected_target_solo_triage_exact_roster"
FULL_FAMILY_REMAINDER_BATCH_NUMBER = 5


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def sha256_json(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, indent=2).encode()).hexdigest()


def load_batch004_approval_packet() -> dict[str, Any]:
    if not BATCH004_APPROVAL_PACKET.exists():
        return {
            "approval_granted_by_this_packet": False,
            "approval_statement_required": "MISSING_REPO_EVIDENCE",
            "expected_provider_calls": "MISSING_REPO_EVIDENCE",
            "path": str(BATCH004_APPROVAL_PACKET),
            "run_command_after_approval": "MISSING_REPO_EVIDENCE",
            "status": "MISSING_REPO_EVIDENCE",
        }
    packet = read_json(BATCH004_APPROVAL_PACKET)
    return {
        "approval_granted_by_this_packet": packet.get("approval_granted_by_this_packet"),
        "approval_statement_required": packet.get("approval_statement_required"),
        "expected_provider_calls": packet.get("expected_calls_if_approved", {}).get("total_provider_calls"),
        "path": str(BATCH004_APPROVAL_PACKET),
        "run_command_after_approval": packet.get("provider_boundary", {}).get("run_command_after_approval"),
        "status": packet.get("status"),
    }


def int_value(value: str | int | None) -> int:
    if value in (None, ""):
        return 0
    return int(value)


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


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True).strip()
    except Exception:
        return "UNAVAILABLE"


def packet_index_by_pair(packet_index: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    pairs: dict[str, dict[str, Any]] = {}
    for row in packet_index:
        pair = pairs.setdefault(
            row["pair_id"],
            {
                "domain": row["domain"],
                "family_id": row["family_id"],
                "pair_id": row["pair_id"],
                "packet_ids": [],
                "target_bucket": row["target_bucket"],
                "truths": Counter(),
            },
        )
        pair["packet_ids"].append(row["packet_id"])
        pair["truths"][row["packet_truth"]] += 1
    for row in pairs.values():
        row["packet_ids"] = sorted(row["packet_ids"])
        row["truths"] = dict(sorted(row["truths"].items()))
    return pairs


def family_packet_counts(packet_index: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in packet_index:
        item = rows.setdefault(
            row["family_id"],
            {
                "domain": row["domain"],
                "family_id": row["family_id"],
                "pairs": set(),
                "packets": 0,
                "allow_packets": 0,
                "escalate_packets": 0,
            },
        )
        item["pairs"].add(row["pair_id"])
        item["packets"] += 1
        if row["packet_truth"] == "ALLOW":
            item["allow_packets"] += 1
        elif row["packet_truth"] == "ESCALATE":
            item["escalate_packets"] += 1
    return {
        family_id: {
            **row,
            "pairs": len(row["pairs"]),
        }
        for family_id, row in sorted(rows.items())
    }


def staged_pair_counts(staged_next_batch: dict[str, Any] | None) -> Counter:
    counts: Counter = Counter()
    if not staged_next_batch:
        return counts
    for row in staged_next_batch.get("selected_pairs", []):
        counts[row["family_id"]] += 1
    return counts


def staged_record_pair_counts(staged_batch: dict[str, Any] | None) -> Counter:
    counts: Counter = Counter()
    if not staged_batch:
        return counts
    seen: set[tuple[str, str]] = set()
    for row in staged_batch.get("selected_records", []):
        key = (row["family_id"], row["pair_id"])
        if key in seen:
            continue
        counts[row["family_id"]] += 1
        seen.add(key)
    return counts


def scored_pair_counts(family_breakdown: list[dict[str, Any]]) -> dict[str, int]:
    if isinstance(family_breakdown, dict):
        return {family_id: int(row["pairs"]) for family_id, row in family_breakdown.items()}
    return {row["family_id"]: int(row["pairs"]) for row in family_breakdown}


def remaining_full_family_pairs(
    pairs_by_id: dict[str, dict[str, Any]],
    selected_target_pair_ids: set[str],
) -> list[dict[str, Any]]:
    remaining = []
    for pair_id, row in sorted(pairs_by_id.items()):
        if pair_id in selected_target_pair_ids:
            continue
        remaining.append(
            {
                "domain": row["domain"],
                "family_id": row["family_id"],
                "pair_id": pair_id,
                "packet_ids": row["packet_ids"],
                "target_bucket": row["target_bucket"],
                "truths": row["truths"],
            }
        )
    return remaining


def wave2_significance_rows() -> list[dict[str, Any]]:
    rows = []
    for row in read_csv(SIGNIFICANCE_PLANNER):
        if (
            row["evidence_family"] == WAVE2_FAMILY
            and row["system"] == "HoloVerify governed architecture"
            and row["model"] == "3DNA governed roster"
            and row["metric_scope"] == "audit_grade_knew_or_admissible"
            and row["metric"] in {"FNR", "FPR", "overall_error", "operational_non_success"}
        ):
            rows.append(
                {
                    "metric": row["metric"],
                    "observed_errors": int_value(row["observed_errors"]),
                    "n": int_value(row["n"]),
                    "observed_rate": row["observed_rate"],
                    "wilson_95_high": row["wilson_95_high"],
                    "zero_error_n_for_95_upper_lt_5pct": int_value(
                        row["if_zero_errors_n_for_95_upper_lt_5pct"]
                    ),
                }
            )
    return rows


def staged_batch_paths(batch_number: int) -> dict[str, Path]:
    suffix = f"{batch_number:03d}"
    batch_id = f"WAVE2_HOLO_TARGET_BATCH_{suffix}"
    root = FREEZE_ROOT / "holo_target_batches" / f"wave2_holo_target_batch_{suffix}"
    return {
        "registration": root / f"{batch_id}_REGISTRATION_2026_07_01.json",
        "staging_preflight": root / f"{batch_id}_PREFLIGHT_2026_07_01.json",
        "live_preflight": root / f"{batch_id}_LIVE_PREFLIGHT_2026_07_01.json",
    }


def load_staged_batch(batch_number: int) -> dict[str, Any] | None:
    paths = staged_batch_paths(batch_number)
    if not paths["registration"].exists() or not paths["staging_preflight"].exists():
        return None
    registration = read_json(paths["registration"])
    staging_preflight = read_json(paths["staging_preflight"])
    live_preflight = read_json(paths["live_preflight"]) if paths["live_preflight"].exists() else {}
    return {
        "batch_id": registration["batch_id"],
        "classification": registration["classification"],
        "expected_counts": registration["expected_counts"],
        "judges_started": live_preflight.get("judges_started", False),
        "live_execution_gate": live_preflight.get("live_execution_gate", {}),
        "live_holo_started": live_preflight.get("live_holo_started", False),
        "live_preflight_path": str(paths["live_preflight"]) if paths["live_preflight"].exists() else None,
        "live_preflight_root_signature": live_preflight.get("root_signature"),
        "providers_called": live_preflight.get("providers_called", 0),
        "ready_for_live_holo": staging_preflight["ready_for_live_holo"],
        "registration_path": str(paths["registration"]),
        "selected_pair_ids": registration["selected_pair_ids"],
        "selected_records": registration["selected_records"],
        "selection_mode": registration.get("selection_mode") or "target-selection",
        "solo_started": live_preflight.get("solo_started", False),
        "staging_checks": staging_preflight["checks"],
        "staging_preflight_path": str(paths["staging_preflight"]),
        "status": staging_preflight["status"],
    }


def compiled_evidence_families() -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(RUN_SUMMARIES):
        grouped[row["evidence_family"]].append(row)

    families = []
    for family, rows in sorted(grouped.items()):
        architecture_rows = [
            row
            for row in rows
            if row["system"] == "HoloVerify governed architecture"
            or row["system"].startswith("Full Holo")
            or "HoloBuild" in row["system"]
        ]
        solo_rows = [row for row in rows if "solo" in row["system"].lower()]
        architecture_correct_values = [
            int_value(row["packet_correct"]) for row in architecture_rows if row["packet_correct"] != ""
        ]
        architecture_correct_missing_rows = sum(1 for row in architecture_rows if row["packet_correct"] == "")
        families.append(
            {
                "evidence_family": family,
                "domains": sorted({row["domain"] for row in rows if row["domain"]}),
                "evidence_tiers": sorted({row["evidence_tier"] for row in rows if row["evidence_tier"]}),
                "systems": dict(sorted(Counter(row["system"] for row in rows).items())),
                "row_count": len(rows),
                "architecture_packets": sum(int_value(row["packets"]) for row in architecture_rows),
                "architecture_packet_correct": (
                    sum(architecture_correct_values) if architecture_correct_values else "MISSING_REPO_EVIDENCE"
                ),
                "architecture_packet_correct_missing_rows": architecture_correct_missing_rows,
                "architecture_provider_calls": sum(int_value(row["provider_calls"]) for row in architecture_rows),
                "solo_packets_or_attempts": sum(int_value(row["packets"]) for row in solo_rows),
                "solo_provider_calls": sum(int_value(row["provider_calls"]) for row in solo_rows),
            }
        )
    return families


def build_wave2_status() -> dict[str, Any]:
    freeze_manifest = read_json(FREEZE_MANIFEST)
    packet_index = read_json(PACKET_INDEX)
    solo_package = read_json(SOLO_PACKAGE)
    target_selection = read_json(TARGET_SELECTION)
    combined_memo = read_json(COMBINED_MEMO)

    family_counts = family_packet_counts(packet_index)
    pairs_by_id = packet_index_by_pair(packet_index)
    selected_target_pair_ids = {row["pair_id"] for row in target_selection["all_top_targets"]}
    combined_metrics = combined_memo.get("combined_metrics") or combined_memo.get("summary_metrics", {})
    scored_counts = scored_pair_counts(combined_memo.get("family_counts") or combined_memo["family_breakdown"])
    staged_counts = staged_pair_counts(
        combined_memo.get("staged_next_target_batch") or combined_memo.get("staged_next_batch")
    )
    target_counts = target_selection["domain_target_counts"]
    remaining_pairs = remaining_full_family_pairs(pairs_by_id, selected_target_pair_ids)
    full_family_remainder_stage = load_staged_batch(FULL_FAMILY_REMAINDER_BATCH_NUMBER)
    if full_family_remainder_stage:
        remaining_pair_ids = [row["pair_id"] for row in remaining_pairs]
        full_family_remainder_stage["selected_pairs_match_remaining_full_family_backlog"] = (
            full_family_remainder_stage["selected_pair_ids"] == remaining_pair_ids
        )
        full_family_remainder_stage[
            "claim_boundary"
        ] = "Staged/preflight evidence only; not counted as Holo result, selected-target proof, full-family proof, or statistical proof."
    remainder_staged_counts = staged_record_pair_counts(full_family_remainder_stage)

    domain_rows = []
    for family_id, counts in family_counts.items():
        scored_pairs = scored_counts.get(family_id, 0)
        staged_pairs = staged_counts.get(family_id, 0)
        remainder_staged_pairs = remainder_staged_counts.get(family_id, 0)
        top_targets = target_counts[family_id]["top_targets"]
        unstaged_after_future_stage = counts["pairs"] - scored_pairs - staged_pairs - remainder_staged_pairs
        domain_rows.append(
            {
                "domain": counts["domain"],
                "family_id": family_id,
                "frozen_pairs": counts["pairs"],
                "frozen_packets": counts["packets"],
                "allow_packets": counts["allow_packets"],
                "escalate_packets": counts["escalate_packets"],
                "solo_provider_calls": solo_package["domains"][family_id]["provider_calls"],
                "solo_knew_admissible": solo_package["domains"][family_id]["knew_admissible"],
                "solo_not_knew": solo_package["domains"][family_id]["not_knew"],
                "top_holo_targets": top_targets,
                "scored_holo_target_pairs": scored_pairs,
                "staged_holo_target_pairs": staged_pairs,
                "staged_full_family_remainder_pairs": remainder_staged_pairs,
                "remaining_selected_targets_after_staged": top_targets - scored_pairs - staged_pairs,
                "full_family_pairs_remaining_after_staged_target_lane": counts["pairs"] - scored_pairs - staged_pairs,
                "full_family_pairs_unstaged_after_future_stage": unstaged_after_future_stage,
                "status": (
                    "TARGET_POOL_STAGED_COMPLETE_FULL_FAMILY_REMAINDER_STAGED_NOT_SCORED"
                    if top_targets - scored_pairs - staged_pairs == 0 and unstaged_after_future_stage == 0
                    else
                    "TARGET_POOL_STAGED_COMPLETE_FULL_FAMILY_INCOMPLETE"
                    if top_targets - scored_pairs - staged_pairs == 0
                    else "TARGET_POOL_PARTIAL"
                ),
            }
        )

    staged_next = combined_memo.get("staged_next_target_batch") or combined_memo.get("staged_next_batch") or {}
    selected_target_pairs = len(selected_target_pair_ids)
    scored_pairs = combined_metrics.get("holo_sibling_pairs", combined_metrics.get("holo_pairs", 0))
    staged_pairs = staged_next.get("expected_counts", {}).get("pairs", 0)
    remainder_staged_pairs = (
        full_family_remainder_stage.get("expected_counts", {}).get("pairs", 0) if full_family_remainder_stage else 0
    )
    total_pairs = freeze_manifest["scope"]["pairs"]
    per_class_required_5pct = 60

    return {
        "claim_boundaries": combined_memo["claim_boundaries"]
        + [
            "Batch 004 is staged/preflight-only until an explicitly approved live Holo run exists.",
            "Completing the selected-target pool is not the same as completing all 60 frozen Wave 2 pairs.",
            "The full-family statistical lane requires the remaining non-target pairs after the selected-target lane.",
        ],
        "freeze": {
            "classification": freeze_manifest["classification"],
            "status": freeze_manifest["status"],
            "freeze_root": str(FREEZE_ROOT),
            "freeze_root_hash": freeze_manifest["freeze_root_hash"],
            "scope": freeze_manifest["scope"],
            "final_assertion": freeze_manifest["final_assertion"],
        },
        "solo_triage": {
            "classification": solo_package["classification"],
            "scope": solo_package["scope"],
            "aggregate_totals": solo_package["aggregate_totals"],
            "domain_target_counts": target_counts,
        },
        "selected_target_holo": {
            "scored_batches": "001-003",
            "scored_pairs": scored_pairs,
            "scored_packets": combined_metrics["holo_packets"],
            "scored_packets_correct_admissible": combined_metrics["holo_packets_correct_admissible"],
            "selected_target_pair_pool": selected_target_pairs,
            "staged_next_batch": staged_next,
            "remaining_selected_targets_after_staged": selected_target_pairs - scored_pairs - staged_pairs,
        },
        "statistical_lane": {
            "current_scored_pairs": scored_pairs,
            "current_per_class_n": scored_pairs,
            "current_pairs_needed_for_60_per_class": per_class_required_5pct - scored_pairs,
            "after_batch_004_live_pairs": scored_pairs + staged_pairs,
            "after_batch_004_live_per_class_n": scored_pairs + staged_pairs,
            "after_batch_004_live_pairs_needed_for_60_per_class": per_class_required_5pct
            - (scored_pairs + staged_pairs),
            "full_family_pairs": total_pairs,
            "full_family_packets": freeze_manifest["scope"]["packets"],
            "full_family_pairs_remaining_after_staged_target_lane": total_pairs - scored_pairs - staged_pairs,
            "full_family_remainder_staged_batch": full_family_remainder_stage,
            "full_family_remainder_staged_pairs": remainder_staged_pairs,
            "full_family_pairs_unstaged_after_future_stage": total_pairs
            - scored_pairs
            - staged_pairs
            - remainder_staged_pairs,
            "after_batch_004_and_remainder_stage_live_pairs": scored_pairs + staged_pairs + remainder_staged_pairs,
            "after_batch_004_and_remainder_stage_per_class_n": scored_pairs + staged_pairs + remainder_staged_pairs,
            "after_batch_004_and_remainder_stage_pairs_needed_for_60_per_class": per_class_required_5pct
            - (scored_pairs + staged_pairs + remainder_staged_pairs),
            "significance_rows": wave2_significance_rows(),
        },
        "domain_rows": domain_rows,
        "remaining_full_family_pairs_after_selected_target_lane": remaining_pairs,
    }


def build_ledger() -> dict[str, Any]:
    compiled_package = read_json(COMPILED_PACKAGE)
    ledger = {
        "classification": "HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_NO_PROVIDER_2026_07_01",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_without_provider_calls": True,
        "repo": {
            "branch": git_value("branch", "--show-current"),
            "head": git_value("rev-parse", "HEAD"),
        },
        "source_paths": {
            "compiled_metrics_package": str(COMPILED_PACKAGE),
            "freeze_manifest": str(FREEZE_MANIFEST),
            "packet_index": str(PACKET_INDEX),
            "solo_package": str(SOLO_PACKAGE),
            "target_selection": str(TARGET_SELECTION),
            "combined_memo": str(COMBINED_MEMO),
            "ordering_verification": str(ORDERING_VERIFICATION),
            "readiness_report": str(READINESS_REPORT),
            "batch004_provider_approval_packet": str(BATCH004_APPROVAL_PACKET),
        },
        "approval_packets": {
            "batch004": load_batch004_approval_packet(),
        },
        "claim_boundaries": [
            "This ledger consolidates existing file-backed evidence only; it does not create new benchmark scores.",
            "No provider, solo, judge, or Holo execution is performed by this ledger builder.",
            "Compiled historical families are summarized from the metrics package in this checkout; missing external trees are not inferred.",
            "Wave 2 selected-target evidence is separated from full-family statistical proof.",
        ],
        "compiled_metrics_snapshot": {
            "classification": compiled_package["classification"],
            "packet_row_count": compiled_package["packet_row_count"],
            "metric_summary_count": compiled_package["metric_summary_count"],
            "run_summary_count": compiled_package["run_summary_count"],
            "source_audit_count": compiled_package["source_audit_count"],
            "lock_inventory_count": compiled_package["lock_inventory_count"],
        },
        "compiled_evidence_families": compiled_evidence_families(),
        "wave2": build_wave2_status(),
    }
    ledger["package_sha256"] = sha256_json(ledger)
    return ledger


def md_table(rows: list[list[Any]]) -> list[str]:
    return ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]


def render_markdown(ledger: dict[str, Any]) -> str:
    wave2 = ledger["wave2"]
    statistical = wave2["statistical_lane"]
    selected = wave2["selected_target_holo"]
    approval = ledger.get("approval_packets", {}).get("batch004", {})
    full_stage = statistical.get("full_family_remainder_staged_batch") or {}
    full_stage_pairs = statistical.get("full_family_remainder_staged_pairs", 0)
    full_stage_calls = full_stage.get("expected_counts", {}).get("total_provider_calls", 0)
    full_stage_gate = full_stage.get("live_execution_gate", {}).get("status", "MISSING_REPO_EVIDENCE")
    if full_stage:
        statistical_state = (
            f"`{statistical['current_per_class_n']}/60` current per class; "
            f"`{statistical['after_batch_004_live_per_class_n']}/60` after Batch 004 if clean; "
            f"`{statistical['after_batch_004_and_remainder_stage_per_class_n']}/60` only after Batch 005 if clean"
        )
    else:
        statistical_state = (
            f"`{statistical['current_per_class_n']}/60` current per class; "
            f"`{statistical['after_batch_004_live_per_class_n']}/60` after Batch 004 if clean"
        )
    lines = [
        "# HoloVerify Domain Consolidation Ledger",
        "",
        f"Classification: `{ledger['classification']}`",
        f"Package SHA-256: `{ledger['package_sha256']}`",
        f"Generated without provider calls: `{ledger['generated_without_provider_calls']}`",
        "",
        "## Control Summary",
        "",
        "| Lane | State | Evidence | Next gate |",
        "| --- | --- | --- | --- |",
        (
            "| Compiled metrics snapshot | "
            f"`{ledger['compiled_metrics_snapshot']['run_summary_count']}` run rows, "
            f"`{ledger['compiled_metrics_snapshot']['metric_summary_count']}` metric rows | "
            f"`{ledger['source_paths']['compiled_metrics_package']}` | Keep as current metrics surface |"
        ),
        (
            "| Wave 2 packet freeze | "
            f"`{wave2['freeze']['scope']['pairs']}` pairs / `{wave2['freeze']['scope']['packets']}` packets frozen | "
            f"`{ledger['source_paths']['freeze_manifest']}` | No packet or prompt edits |"
        ),
        (
            "| Wave 2 solo triage | "
            f"`{wave2['solo_triage']['aggregate_totals']['provider_calls']}` calls, "
            f"`{wave2['solo_triage']['aggregate_totals']['top_holo_targets']}` target pairs found | "
            f"`{ledger['source_paths']['solo_package']}` | Do not rerun unless explicitly opened |"
        ),
        (
            "| Wave 2 Holo selected targets | "
            f"`{selected['scored_pairs']}` scored pairs plus "
            f"`{selected['staged_next_batch']['expected_counts']['pairs']}` staged pairs | "
            f"`{ledger['source_paths']['combined_memo']}` | Batch 004 live Holo requires explicit provider approval |"
        ),
        (
            "| Wave 2 full-family remainder | "
            f"`{full_stage_pairs}` future-staged pairs, `{full_stage_calls}` expected provider calls if live, live gate `{full_stage_gate}` | "
            f"`{full_stage.get('live_preflight_path', 'MISSING_REPO_EVIDENCE')}` | "
            "Run only after Batch 004 is live, promoted, and provider-approved |"
            if full_stage
            else "| Wave 2 full-family remainder | `0` staged pairs | `MISSING_REPO_EVIDENCE` | Stage after Batch 004 if statistical proof is the goal |"
        ),
        (
            "| Wave 2 statistical lane | "
            f"{statistical_state} | "
            "`significance_planner.csv` | Keep staged work separate from scored proof until live evidence exists |"
        ),
        (
            "| Wave 2 ordering verifier | "
            "`PASS` required before opening any provider gate | "
            f"`{ledger['source_paths']['ordering_verification']}` | Run immediately before Batch 004 live approval |"
        ),
        (
            "| Batch 004 provider approval packet | "
            f"`{approval.get('status', 'MISSING_REPO_EVIDENCE')}`, `{approval.get('expected_provider_calls', 'MISSING_REPO_EVIDENCE')}` expected calls, "
            f"approval granted `{approval.get('approval_granted_by_this_packet', 'MISSING_REPO_EVIDENCE')}` | "
            f"`{ledger['source_paths']['batch004_provider_approval_packet']}` | Required before Batch 004 live execution |"
        ),
        "",
        "## Wave 2 Domain Status",
        "",
        "| Domain | Frozen pairs | Top targets | Scored target pairs | Staged target pairs | Future full-family staged pairs | Remaining target pairs | Unstaged full-family pairs | Status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in wave2["domain_rows"]:
        lines.append(
            f"| `{row['family_id']}` | `{row['frozen_pairs']}` | `{row['top_holo_targets']}` | "
            f"`{row['scored_holo_target_pairs']}` | `{row['staged_holo_target_pairs']}` | "
            f"`{row['staged_full_family_remainder_pairs']}` | "
            f"`{row['remaining_selected_targets_after_staged']}` | "
            f"`{row['full_family_pairs_unstaged_after_future_stage']}` | `{row['status']}` |"
        )

    lines += [
        "",
        "## Wave 2 Scored Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Scored Holo pairs | `{selected['scored_pairs']}` |",
        f"| Scored Holo packets | `{selected['scored_packets']}` |",
        f"| Scored Holo correct/admissible packets | `{selected['scored_packets_correct_admissible']}` |",
        f"| Selected-target pair pool | `{selected['selected_target_pair_pool']}` |",
        f"| Remaining selected targets after Batch 004 staging | `{selected['remaining_selected_targets_after_staged']}` |",
        f"| Current pairs needed for 60/class | `{statistical['current_pairs_needed_for_60_per_class']}` |",
        f"| Pairs needed for 60/class after clean Batch 004 | `{statistical['after_batch_004_live_pairs_needed_for_60_per_class']}` |",
        f"| Full-family remainder future-staged pairs | `{statistical['full_family_remainder_staged_pairs']}` |",
        f"| Unstaged full-family pairs after future stage | `{statistical['full_family_pairs_unstaged_after_future_stage']}` |",
        f"| Pairs needed for 60/class after clean Batch 004 and Batch 005 | `{statistical['after_batch_004_and_remainder_stage_pairs_needed_for_60_per_class']}` |",
        "",
        "## Significance Planner Extract",
        "",
        "| Metric | Errors | n | 95% Wilson high | Zero-error n for <5% 95% upper bound |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in statistical["significance_rows"]:
        lines.append(
            f"| `{row['metric']}` | `{row['observed_errors']}` | `{row['n']}` | "
            f"`{row['wilson_95_high']}` | `{row['zero_error_n_for_95_upper_lt_5pct']}` |"
        )

    lines += [
        "",
        "## Full-Family Remainder Pairs",
        "",
        "These pairs are not in the 37-pair selected-target pool. They are the exact Wave 2 backlog for full 60-pair coverage across the three new domains; Batch 005 stages them but does not score them.",
        "",
        "| Family | Pair | Bucket | Packets |",
        "| --- | --- | --- | --- |",
    ]
    for row in wave2["remaining_full_family_pairs_after_selected_target_lane"]:
        lines.append(
            f"| `{row['family_id']}` | `{row['pair_id']}` | `{row['target_bucket']}` | "
            f"`{', '.join(row['packet_ids'])}` |"
        )

    lines += [
        "",
        "## Compiled Evidence Families",
        "",
        "| Evidence family | Domains | Architecture packets | Architecture correct | Solo packets/attempts | Tiers |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in ledger["compiled_evidence_families"]:
        domains = "<br>".join(row["domains"]) or "MISSING_REPO_EVIDENCE"
        tiers = "<br>".join(row["evidence_tiers"]) or "MISSING_REPO_EVIDENCE"
        lines.append(
            f"| `{row['evidence_family']}` | {domains} | `{row['architecture_packets']}` | "
            f"`{row['architecture_packet_correct']}` | `{row['solo_packets_or_attempts']}` | {tiers} |"
        )

    staged = selected["staged_next_batch"]
    lines += [
        "",
        "## Next Gates",
        "",
        "0. Re-run the full no-provider refresh before opening any provider-call gate:",
        "",
        "```bash",
        "python3 -B docs/benchmark/run_wave2_domain_no_provider_refresh_2026_07_01.py",
        "```",
        "",
        "Equivalent manual verifier sequence:",
        "",
        "```bash",
        "python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py",
        "python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py",
        "python3 -B docs/benchmark/build_wave2_batch004_provider_approval_packet_2026_07_01.py",
        "python3 -B docs/benchmark/build_wave2_domain_control_room_2026_07_01.py",
        "```",
        "",
        "Required approval statement:",
        "",
        f"`{approval.get('approval_statement_required', 'MISSING_REPO_EVIDENCE')}`",
        "",
        "1. Live Batch 004 only after explicit provider-call approval:",
        "",
        "```bash",
        batch_live_approval_command(4),
        "```",
        "",
        "2. If Batch 004 finishes cleanly, build the comparison and promote only then:",
        "",
        "```bash",
        "python3 -B docs/benchmark/build_wave2_holo_target_batch_comparison_2026_07_01.py --batch-number 4",
        "python3 -B docs/benchmark/build_wave2_holo_target_combined_evidence_2026_07_01.py --batches 1 2 3 4",
        "python3 -B docs/benchmark/compile_holoverify_holobuild_metrics_2026_07_01.py",
        "node docs/benchmark/build_holoverify_holobuild_metrics_workbook_2026_07_01.mjs",
        "python3 -B docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py",
        "python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py",
        "python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py",
        "python3 -B docs/benchmark/build_wave2_domain_control_room_2026_07_01.py",
        "```",
        "",
        "3. Batch 005 full-family remainder is staged/preflighted, but remains locked behind Batch 004 promotion plus explicit provider-call approval:",
        "",
        "```bash",
        batch_live_approval_command(5),
        "```",
        "",
        "4. If Batch 005 finishes cleanly, build its comparison and promote it under full-family statistical language, not selected-target language:",
        "",
        "```bash",
        "python3 -B docs/benchmark/build_wave2_holo_target_batch_comparison_2026_07_01.py --batch-number 5",
        "python3 -B docs/benchmark/build_wave2_holo_target_combined_evidence_2026_07_01.py --batches 1 2 3 4 5",
        "python3 -B docs/benchmark/compile_holoverify_holobuild_metrics_2026_07_01.py",
        "node docs/benchmark/build_holoverify_holobuild_metrics_workbook_2026_07_01.mjs",
        "python3 -B docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py",
        "python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py",
        "python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py",
        "python3 -B docs/benchmark/build_wave2_domain_control_room_2026_07_01.py",
        "```",
        "",
        "## Claim Boundaries",
        "",
    ]
    lines += [f"- {item}" for item in ledger["claim_boundaries"]]
    lines += [f"- {item}" for item in wave2["claim_boundaries"]]
    lines += [
        f"- Batch 004 live preflight root signature: `{staged['live_preflight_root_signature']}`.",
    ]
    if full_stage:
        lines.append(f"- Batch 005 live preflight root signature: `{full_stage['live_preflight_root_signature']}`.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    ledger = build_ledger()
    write_json(OUT_JSON, ledger)
    OUT_MD.write_text(render_markdown(ledger))
    print(
        json.dumps(
            {
                "status": "PASS",
                "json": str(OUT_JSON),
                "md": str(OUT_MD),
                "package_sha256": ledger["package_sha256"],
                "wave2_remaining_full_family_pairs_after_selected_target_lane": len(
                    ledger["wave2"]["remaining_full_family_pairs_after_selected_target_lane"]
                ),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
