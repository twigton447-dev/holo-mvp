#!/usr/bin/env python3
"""Verify the Wave 2 domain execution order without running providers."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FREEZE_ROOT = Path("docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01")
BATCHES_ROOT = FREEZE_ROOT / "holo_target_batches"
OUT_ROOT = Path("docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01")
OUT_JSON = OUT_ROOT / "WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.json"
OUT_MD = OUT_ROOT / "WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.md"

FREEZE_MANIFEST = FREEZE_ROOT / "FREEZE_MANIFEST.json"
PACKET_INDEX = FREEZE_ROOT / "manifests/PACKET_INDEX.json"
TARGET_SELECTION = FREEZE_ROOT / "solo_triage_3mini/WAVE2_HOLO_TARGET_SELECTION_FROM_SOLO_TRIAGE_2026_07_01.json"
COMBINED_MEMO_001_003 = BATCHES_ROOT / "WAVE2_HOLO_TARGET_BATCH_001_002_003_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
COMBINED_MEMO_001_004 = BATCHES_ROOT / "WAVE2_HOLO_TARGET_BATCH_001_002_003_004_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
COMBINED_MEMO = COMBINED_MEMO_001_004 if COMBINED_MEMO_001_004.exists() else COMBINED_MEMO_001_003
DOMAIN_LEDGER = OUT_ROOT / "HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def sha256_json(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    return hashlib.sha256(json.dumps(body, indent=2, sort_keys=True).encode()).hexdigest()


def batch_id(batch_number: int) -> str:
    return f"WAVE2_HOLO_TARGET_BATCH_{batch_number:03d}"


def batch_dir(batch_number: int) -> Path:
    return BATCHES_ROOT / f"wave2_holo_target_batch_{batch_number:03d}"


def batch_file(batch_number: int, suffix: str) -> Path:
    return batch_dir(batch_number) / f"{batch_id(batch_number)}_{suffix}_2026_07_01.json"


def comparison_path(batch_number: int) -> Path:
    return batch_file(batch_number, "SOLO_VS_HOLO_COMPARISON")


def completed_comparison_batches() -> list[int]:
    completed = []
    for path in sorted(BATCHES_ROOT.glob("wave2_holo_target_batch_*/WAVE2_HOLO_TARGET_BATCH_*_SOLO_VS_HOLO_COMPARISON_2026_07_01.json")):
        match = re.search(r"wave2_holo_target_batch_(\d{3})/", str(path))
        if match:
            completed.append(int(match.group(1)))
    return completed


def packet_pairs() -> dict[str, dict[str, Any]]:
    pairs: dict[str, dict[str, Any]] = {}
    for packet in read_json(PACKET_INDEX):
        row = pairs.setdefault(
            packet["pair_id"],
            {
                "domain": packet["domain"],
                "family_id": packet["family_id"],
                "packet_ids": [],
                "pair_id": packet["pair_id"],
                "target_bucket": packet["target_bucket"],
                "truths": Counter(),
            },
        )
        row["packet_ids"].append(packet["packet_id"])
        row["truths"][packet["packet_truth"]] += 1
    for row in pairs.values():
        row["packet_ids"] = sorted(row["packet_ids"])
        row["truths"] = dict(sorted(row["truths"].items()))
    return pairs


def pair_ids_from_comparison(batch_number: int) -> list[str]:
    comparison = read_json(comparison_path(batch_number))
    return [row["pair_id"] for row in comparison.get("pair_rows", [])]


def load_batch_state(batch_number: int) -> dict[str, Any]:
    registration_path = batch_file(batch_number, "REGISTRATION")
    staging_preflight_path = batch_file(batch_number, "PREFLIGHT")
    live_preflight_path = batch_file(batch_number, "LIVE_PREFLIGHT")
    registration = read_json(registration_path)
    staging_preflight = read_json(staging_preflight_path)
    live_preflight = read_json(live_preflight_path)
    raw_mode = registration.get("selection_mode")
    return {
        "batch_id": registration["batch_id"],
        "effective_selection_mode": raw_mode or "target-selection",
        "expected_counts": registration["expected_counts"],
        "judges_started": live_preflight.get("judges_started", False),
        "live_holo_started": live_preflight.get("live_holo_started", False),
        "live_execution_gate": live_preflight.get("live_execution_gate", {}),
        "live_preflight_path": str(live_preflight_path),
        "live_preflight_root_signature": live_preflight.get("root_signature"),
        "live_preflight_status": live_preflight.get("status"),
        "providers_called": live_preflight.get("providers_called", 0),
        "raw_selection_mode": raw_mode,
        "registration_path": str(registration_path),
        "selected_pair_ids": registration.get("selected_pair_ids", []),
        "solo_started": live_preflight.get("solo_started", False),
        "staging_preflight_path": str(staging_preflight_path),
        "staging_preflight_status": staging_preflight.get("status"),
        "staging_ready_for_live_holo": staging_preflight.get("ready_for_live_holo", False),
    }


def check_hex_sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def build_verification() -> dict[str, Any]:
    freeze_manifest = read_json(FREEZE_MANIFEST)
    target_selection = read_json(TARGET_SELECTION)
    combined_memo = read_json(COMBINED_MEMO)
    domain_ledger = read_json(DOMAIN_LEDGER)
    pairs_by_id = packet_pairs()

    completed_batches = completed_comparison_batches()
    completed_pair_ids = {
        pair_id
        for batch_number in completed_batches
        for pair_id in pair_ids_from_comparison(batch_number)
    }
    target_pair_ids = [row["pair_id"] for row in target_selection.get("all_top_targets", [])]
    remaining_target_pair_ids = [pair_id for pair_id in target_pair_ids if pair_id not in completed_pair_ids]
    full_family_remainder_pair_ids = [
        pair_id for pair_id in sorted(pairs_by_id) if pair_id not in set(target_pair_ids)
    ]

    batch_004 = load_batch_state(4)
    batch_005 = load_batch_state(5)
    statistical = domain_ledger["wave2"]["statistical_lane"]
    selected = domain_ledger["wave2"]["selected_target_holo"]
    combined_metrics = combined_memo.get("combined_metrics") or combined_memo.get("summary_metrics", {})
    batch004_comparison_pair_ids = pair_ids_from_comparison(4) if comparison_path(4).exists() else []

    checks = {
        "freeze_scope_60_pairs_120_packets": freeze_manifest["scope"]["pairs"] == 60
        and freeze_manifest["scope"]["packets"] == 120,
        "target_selection_has_37_pairs": len(target_pair_ids) == 37,
        "completed_comparison_batches_are_001_002_003_004": completed_batches == [1, 2, 3, 4],
        "combined_memo_no_provider": combined_memo.get("no_provider_calls_for_this_package") is True,
        "domain_ledger_no_provider": domain_ledger.get("generated_without_provider_calls") is True,
        "scored_pairs_37_packets_74": combined_metrics.get("holo_pairs") == 37
        and combined_metrics.get("holo_packets") == 74
        and combined_metrics.get("holo_packets_correct_admissible") == 74,
        "batch_004_comparison_present": comparison_path(4).exists(),
        "batch_004_effective_selection_mode_target_selection": batch_004["effective_selection_mode"] == "target-selection",
        "batch_004_selected_pairs_match_scored_comparison": set(batch_004["selected_pair_ids"])
        == set(batch004_comparison_pair_ids),
        "batch_004_expected_counts_10_pairs_20_packets_100_calls": batch_004["expected_counts"].get("pairs") == 10
        and batch_004["expected_counts"].get("packets") == 20
        and batch_004["expected_counts"].get("total_provider_calls") == 100
        and batch_004["expected_counts"].get("solo_calls") == 0
        and batch_004["expected_counts"].get("judge_calls") == 0,
        "batch_004_preflights_passed": batch_004["staging_preflight_status"] == "PASS"
        and batch_004["live_preflight_status"] == "PASS"
        and batch_004["staging_ready_for_live_holo"] is True,
        "batch_004_live_execution_gate_pass": batch_004["live_execution_gate"].get("status") == "PASS",
        "batch_004_not_started": batch_004["providers_called"] == 0
        and batch_004["live_holo_started"] is False
        and batch_004["solo_started"] is False
        and batch_004["judges_started"] is False,
        "batch_004_root_signature_present": check_hex_sha(batch_004["live_preflight_root_signature"]),
        "batch_005_comparison_absent": not comparison_path(5).exists(),
        "batch_005_selection_mode_full_family_remainder": batch_005["effective_selection_mode"] == "full-family-remainder",
        "batch_005_selected_pairs_match_full_family_remainder": batch_005["selected_pair_ids"]
        == full_family_remainder_pair_ids,
        "batch_005_no_selected_target_overlap": set(batch_005["selected_pair_ids"]).isdisjoint(target_pair_ids),
        "batch_005_expected_counts_23_pairs_46_packets_230_calls": batch_005["expected_counts"].get("pairs") == 23
        and batch_005["expected_counts"].get("packets") == 46
        and batch_005["expected_counts"].get("total_provider_calls") == 230
        and batch_005["expected_counts"].get("solo_calls") == 0
        and batch_005["expected_counts"].get("judge_calls") == 0,
        "batch_005_preflights_passed": batch_005["staging_preflight_status"] == "PASS"
        and batch_005["live_preflight_status"] == "PASS"
        and batch_005["staging_ready_for_live_holo"] is True,
        "batch_005_live_execution_gate_pass_after_batch004_promotion": batch_005["live_execution_gate"].get("status")
        == "PASS"
        and batch_005["live_execution_gate"].get("blocked_reason") is None,
        "batch_005_not_started": batch_005["providers_called"] == 0
        and batch_005["live_holo_started"] is False
        and batch_005["solo_started"] is False
        and batch_005["judges_started"] is False,
        "batch_005_root_signature_present": check_hex_sha(batch_005["live_preflight_root_signature"]),
        "ledger_selected_targets_fully_scored": selected["scored_pairs"] == 37
        and selected["scored_packets"] == 74
        and selected["remaining_selected_targets_after_staged"] == 0,
        "ledger_statistical_lane_37_37_60": statistical["current_per_class_n"] == 37
        and statistical["after_batch_004_live_per_class_n"] == 37
        and statistical["after_batch_004_and_remainder_stage_per_class_n"] == 60,
        "ledger_full_family_remainder_fully_staged_not_scored": statistical[
            "full_family_remainder_staged_pairs"
        ]
        == 23
        and statistical["full_family_pairs_unstaged_after_future_stage"] == 0,
    }

    gate_state = {
        "current_phase": "POST_BATCH_004_EVIDENCE_LOCKED",
        "next_allowed_live_batch": "WAVE2_HOLO_TARGET_BATCH_005",
        "batch_005_gate": "EVIDENCE_UNLOCKED_PENDING_EXPLICIT_PROVIDER_APPROVAL",
        "provider_calls_allowed_by_this_verifier": False,
    }
    verification = {
        "batch_004": batch_004,
        "batch_005": batch_005,
        "checks": checks,
        "classification": "WAVE2_DOMAIN_ORDERING_VERIFICATION_NO_PROVIDER_2026_07_01",
        "completed_comparison_batches": completed_batches,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "full_family_remainder_pair_count": len(full_family_remainder_pair_ids),
        "full_family_remainder_pair_ids": full_family_remainder_pair_ids,
        "gate_state": gate_state,
        "generated_without_provider_calls": True,
        "remaining_target_pair_count": len(remaining_target_pair_ids),
        "remaining_target_pair_ids": remaining_target_pair_ids,
        "scored_pair_count": len(completed_pair_ids),
        "source_paths": {
            "combined_memo": str(COMBINED_MEMO),
            "domain_ledger": str(DOMAIN_LEDGER),
            "freeze_manifest": str(FREEZE_MANIFEST),
            "packet_index": str(PACKET_INDEX),
            "target_selection": str(TARGET_SELECTION),
        },
        "status": "PASS" if all(checks.values()) else "FAIL",
        "target_pair_count": len(target_pair_ids),
    }
    verification["package_sha256"] = sha256_json(verification)
    return verification


def render_markdown(verification: dict[str, Any]) -> str:
    checks = verification["checks"]
    batch_004 = verification["batch_004"]
    batch_005 = verification["batch_005"]
    lines = [
        "# Wave 2 Domain Ordering Verification",
        "",
        f"Classification: `{verification['classification']}`",
        f"Status: `{verification['status']}`",
        f"Package SHA-256: `{verification['package_sha256']}`",
        f"Generated without provider calls: `{verification['generated_without_provider_calls']}`",
        "",
        "## Gate State",
        "",
        f"Current phase: `{verification['gate_state']['current_phase']}`",
        f"Next allowed live batch: `{verification['gate_state']['next_allowed_live_batch']}`",
        f"Batch 005 gate: `{verification['gate_state']['batch_005_gate']}`",
        "",
        "## Counts",
        "",
        "| Item | Value |",
        "| --- | ---: |",
        f"| Completed comparison batches | `{', '.join(f'{item:03d}' for item in verification['completed_comparison_batches'])}` |",
        f"| Scored pairs | `{verification['scored_pair_count']}` |",
        f"| Target pair pool | `{verification['target_pair_count']}` |",
        f"| Remaining selected-target pairs | `{verification['remaining_target_pair_count']}` |",
        f"| Full-family remainder pairs | `{verification['full_family_remainder_pair_count']}` |",
        "",
        "## Batch Gates",
        "",
        "| Batch | Mode | Pairs | Packets | Provider calls if live | Providers called | Live started | Preflight | Live gate |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
        (
            f"| `{batch_004['batch_id']}` | `{batch_004['effective_selection_mode']}` | "
            f"`{batch_004['expected_counts']['pairs']}` | `{batch_004['expected_counts']['packets']}` | "
            f"`{batch_004['expected_counts']['total_provider_calls']}` | `{batch_004['providers_called']}` | "
            f"`{batch_004['live_holo_started']}` | `{batch_004['live_preflight_status']}` | "
            f"`{batch_004['live_execution_gate'].get('status')}` |"
        ),
        (
            f"| `{batch_005['batch_id']}` | `{batch_005['effective_selection_mode']}` | "
            f"`{batch_005['expected_counts']['pairs']}` | `{batch_005['expected_counts']['packets']}` | "
            f"`{batch_005['expected_counts']['total_provider_calls']}` | `{batch_005['providers_called']}` | "
            f"`{batch_005['live_holo_started']}` | `{batch_005['live_preflight_status']}` | "
            f"`{batch_005['live_execution_gate'].get('status')}` |"
        ),
        "",
        "## Checks",
        "",
        "| Check | Result |",
        "| --- | --- |",
    ]
    for key, value in checks.items():
        lines.append(f"| `{key}` | `{value}` |")

    lines += [
        "",
        "## Next Gates",
        "",
        "1. Batch 004 live Holo evidence has been promoted into the selected-target comparison and combined memo.",
        "2. Batch 005 is the next eligible live lane, but it still requires a separate provider approval packet and explicit approval.",
        "3. Batch 005 remains full-family remainder only; it is not selected-target evidence and is not scored proof while staged.",
        "",
        "## Root Signatures",
        "",
        f"- Batch 004 live preflight: `{batch_004['live_preflight_root_signature']}`",
        f"- Batch 005 live preflight: `{batch_005['live_preflight_root_signature']}`",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    verification = build_verification()
    write_json(OUT_JSON, verification)
    OUT_MD.write_text(render_markdown(verification))
    print(
        json.dumps(
            {
                "status": verification["status"],
                "json": str(OUT_JSON),
                "md": str(OUT_MD),
                "package_sha256": verification["package_sha256"],
                "next_allowed_live_batch": verification["gate_state"]["next_allowed_live_batch"],
                "batch_005_gate": verification["gate_state"]["batch_005_gate"],
            },
            indent=2,
        )
    )
    return 0 if verification["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
