#!/usr/bin/env python3
"""Build a no-provider combined evidence memo for Wave 2 Holo target batches."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01")
TARGET_ROOT = ROOT / "holo_target_batches"
SELECTION_PATH = ROOT / "solo_triage_3mini" / "WAVE2_HOLO_TARGET_SELECTION_FROM_SOLO_TRIAGE_2026_07_01.json"
PACKET_INDEX_PATH = ROOT / "manifests" / "PACKET_INDEX.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json_with_hash(path: Path, data: dict) -> str:
    data = dict(data)
    data.pop("package_sha256", None)
    data.pop("created_at_utc", None)
    rendered = json.dumps(data, indent=2, sort_keys=True) + "\n"
    package_sha256 = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    data["created_at_utc"] = datetime.now(timezone.utc).isoformat()
    data["package_sha256"] = package_sha256
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return package_sha256


def batch_comparison_path(batch: int) -> Path:
    batch_id = f"{batch:03d}"
    return (
        TARGET_ROOT
        / f"wave2_holo_target_batch_{batch_id}"
        / f"WAVE2_HOLO_TARGET_BATCH_{batch_id}_SOLO_VS_HOLO_COMPARISON_2026_07_01.json"
    )


def sum_key(dicts: list[dict], key: str) -> int:
    return sum(int(d.get(key, 0) or 0) for d in dicts)


def ratio(num: int, den: int) -> float:
    return round(num / den, 6) if den else 0.0


def display_value(value: Any) -> Any:
    return "MISSING_REPO_EVIDENCE" if value is None else value


def live_preflight_head(batch: int) -> str:
    batch_id = f"{batch:03d}"
    preflight_path = (
        TARGET_ROOT
        / f"wave2_holo_target_batch_{batch_id}"
        / f"WAVE2_HOLO_TARGET_BATCH_{batch_id}_LIVE_PREFLIGHT_2026_07_01.json"
    )
    if not preflight_path.exists():
        return "UNKNOWN"
    data = read_json(preflight_path)
    return data.get("current_head_at_preflight") or data.get("commit") or "UNKNOWN"


def load_staged_batch(batch: int, expected_pair_ids: list[str] | None = None) -> dict | None:
    batch_id = f"{batch:03d}"
    batch_dir = TARGET_ROOT / f"wave2_holo_target_batch_{batch_id}"
    registration_path = batch_dir / f"WAVE2_HOLO_TARGET_BATCH_{batch_id}_REGISTRATION_2026_07_01.json"
    preflight_path = batch_dir / f"WAVE2_HOLO_TARGET_BATCH_{batch_id}_PREFLIGHT_2026_07_01.json"
    live_preflight_path = batch_dir / f"WAVE2_HOLO_TARGET_BATCH_{batch_id}_LIVE_PREFLIGHT_2026_07_01.json"
    if not registration_path.exists() or not preflight_path.exists():
        return None

    registration = read_json(registration_path)
    preflight = read_json(preflight_path)
    live_preflight = read_json(live_preflight_path) if live_preflight_path.exists() else {}
    selected_pair_ids = registration.get("selected_pair_ids", [])
    pair_records = {}
    for row in registration.get("selected_records", []):
        pair_records.setdefault(
            row["pair_id"],
            {
                "domain": row.get("domain"),
                "family_id": row.get("family_id"),
                "pair_id": row.get("pair_id"),
                "target_bucket": row.get("target_bucket"),
                "triage_class": row.get("triage_class"),
                "not_knew_count": row.get("not_knew_count"),
                "wrong_verdict_count": row.get("wrong_verdict_count"),
                "parse_or_provider_fail_count": row.get("parse_or_provider_fail_count"),
                "priority_score": row.get("priority_score"),
            },
        )

    return {
        "batch": batch_id,
        "batch_id": f"WAVE2_HOLO_TARGET_BATCH_{batch_id}",
        "claim_boundary": registration.get(
            "claim_boundary",
            "Staged/preflight evidence only; not counted as Holo result, solo comparison, judge result, or statistical proof.",
        ),
        "expected_counts": registration.get("expected_counts", {}),
        "live_execution_gate": live_preflight.get("live_execution_gate", {}),
        "live_holo_started": live_preflight.get("live_holo_started", False),
        "live_preflight_path": str(live_preflight_path) if live_preflight_path.exists() else None,
        "live_preflight_root_signature": live_preflight.get("root_signature"),
        "providers_called": live_preflight.get("providers_called", 0),
        "ready_for_live_holo": preflight.get("ready_for_live_holo"),
        "selected_pair_ids": selected_pair_ids,
        "selected_pairs": [pair_records[pair_id] for pair_id in selected_pair_ids if pair_id in pair_records],
        "selected_pairs_match_expected_pool": selected_pair_ids == expected_pair_ids if expected_pair_ids is not None else None,
        "selection_mode": registration.get("selection_mode") or "target-selection",
        "selection_mode_defaulted": registration.get("selection_mode") is None,
        "solo_started": live_preflight.get("solo_started", False),
        "judges_started": live_preflight.get("judges_started", False),
        "status": preflight.get("status"),
    }


def remaining_full_family_pairs_after_target_pool() -> list[dict]:
    selection = read_json(SELECTION_PATH)
    target_pair_ids = {row.get("pair_id") for row in selection.get("all_top_targets", [])}
    grouped: dict[str, dict] = {}
    for row in read_json(PACKET_INDEX_PATH):
        pair = grouped.setdefault(
            row["pair_id"],
            {
                "domain": row["domain"],
                "family_id": row["family_id"],
                "packet_ids": [],
                "pair_id": row["pair_id"],
                "target_bucket": row["target_bucket"],
            },
        )
        pair["packet_ids"].append(row["packet_id"])

    remaining = []
    for pair_id, row in sorted(grouped.items()):
        if pair_id in target_pair_ids:
            continue
        row["packet_ids"] = sorted(row["packet_ids"])
        remaining.append(row)
    return remaining


def compact_pair_row(batch: int, row: dict) -> dict:
    outcomes = row.get("six_solo_outcomes") or []

    def count_outcome(name: str) -> int:
        return sum(1 for outcome in outcomes if outcome.get("failure_class") == name)

    knew = row.get("solo_knew_admissible")
    if knew is None and outcomes:
        knew = sum(1 for outcome in outcomes if outcome.get("knew_admissible") is True)
    not_knew = row.get("solo_not_knew")
    if not_knew is None:
        not_knew = row.get("solo_not_knew_count_from_selection")
    if not_knew is None and outcomes:
        not_knew = sum(1 for outcome in outcomes if outcome.get("knew_admissible") is not True)
    parse_fail = row.get("solo_parse_fail")
    if parse_fail is None:
        parse_fail = row.get("solo_parse_or_provider_fail_count_from_selection")
    if parse_fail is None and outcomes:
        parse_fail = count_outcome("PARSE_FAIL")
    provider_failures = row.get("solo_provider_failures")
    if provider_failures is None and outcomes:
        provider_failures = count_outcome("PROVIDER_FAILURE")
    wrong_verdict = row.get("solo_wrong_verdict")
    if wrong_verdict is None:
        wrong_verdict = row.get("solo_wrong_verdict_count_from_selection")
    if wrong_verdict is None and outcomes:
        wrong_verdict = count_outcome("WRONG_VERDICT")
    structural = row.get("solo_structural_or_evidence_fail")
    if structural is None and outcomes:
        structural = count_outcome("STRUCTURAL_OR_EVIDENCE_FAIL")

    return {
        "batch": f"{batch:03d}",
        "domain": row.get("domain"),
        "evidence_class": row.get("evidence_class"),
        "family_id": row.get("family_id"),
        "holo_guardrail": {
            "expected": row.get("holo_guardrail_expected"),
            "final_correct": row.get("holo_guardrail_final_correct"),
            "final_verdict": row.get("holo_guardrail_final_verdict"),
            "packet_id": row.get("holo_guardrail_packet_id"),
        },
        "holo_pair_valid": row.get("holo_pair_valid"),
        "holo_target": {
            "expected": row.get("holo_target_expected"),
            "final_correct": row.get("holo_target_final_correct"),
            "final_verdict": row.get("holo_target_final_verdict"),
            "packet_id": row.get("holo_target_packet_id"),
        },
        "pair_id": row.get("pair_id"),
        "target_bucket": row.get("target_bucket"),
        "triage_class": row.get("triage_class"),
        "solo": {
            "knew_admissible": int(knew or 0),
            "not_knew": int(not_knew or 0),
            "parse_fail": int(parse_fail or 0),
            "provider_failures": int(provider_failures or 0),
            "structural_or_evidence_fail": int(structural or 0),
            "wrong_verdict": int(wrong_verdict or 0),
        },
    }


def build_combined(batches: list[int]) -> dict:
    comparisons = [(batch, read_json(batch_comparison_path(batch))) for batch in batches]
    summaries = [data["summary_metrics"] for _, data in comparisons]
    solo_tokens = [data["solo_tokens_on_selected_packets"] for _, data in comparisons]
    holo_tokens = [data["holo_tokens"] for _, data in comparisons]
    pair_rows = [
        compact_pair_row(batch, row)
        for batch, data in comparisons
        for row in data.get("pair_rows", [])
    ]

    selected_solo_attempts = sum_key(solo_tokens, "attempts")
    selected_solo_total = sum_key(solo_tokens, "total_tokens")
    selected_solo_input = sum_key(solo_tokens, "input_tokens")
    selected_solo_output = sum_key(solo_tokens, "output_tokens")
    holo_total = sum_key(holo_tokens, "total_tokens")
    holo_gov = sum_key(holo_tokens, "gov_total_tokens")
    holo_worker = sum_key(holo_tokens, "worker_total_tokens")

    combined_metrics = {
        "all_six_solo_collapse_pairs": sum_key(summaries, "all_six_solo_collapse_pairs"),
        "batch_count": len(batches),
        "gov_share_of_holo_tokens": ratio(holo_gov, holo_total),
        "holo_gov_tokens": holo_gov,
        "holo_input_tokens": sum_key(holo_tokens, "input_tokens"),
        "holo_intra_worker_misses_corrected": sum_key(summaries, "holo_intra_worker_misses_corrected"),
        "holo_output_tokens": sum_key(holo_tokens, "output_tokens"),
        "holo_packets": sum_key(summaries, "holo_final_packet_count"),
        "holo_packets_correct_admissible": sum_key(summaries, "holo_final_packets_correct_admissible"),
        "holo_pairs": sum_key(summaries, "holo_pair_count"),
        "holo_parse_failures": sum_key(summaries, "holo_parse_failures"),
        "holo_provider_failures": sum_key(summaries, "holo_provider_failures"),
        "holo_total_tokens": holo_total,
        "holo_valid_pairs": sum_key(summaries, "holo_valid_pairs"),
        "holo_worker_tokens": holo_worker,
        "selected_solo_attempts": selected_solo_attempts,
        "selected_solo_input_tokens": selected_solo_input,
        "selected_solo_output_tokens": selected_solo_output,
        "selected_solo_total_tokens": selected_solo_total,
        "solo_knew_admissible": sum_key(solo_tokens, "knew_admissible"),
        "solo_knew_admissible_rate": ratio(sum_key(solo_tokens, "knew_admissible"), selected_solo_attempts),
        "solo_not_knew": sum_key(solo_tokens, "not_knew"),
        "solo_not_knew_rate": ratio(sum_key(solo_tokens, "not_knew"), selected_solo_attempts),
        "solo_parse_fail": sum_key(solo_tokens, "parse_fail"),
        "solo_provider_failures": sum_key(solo_tokens, "provider_failures"),
        "solo_structural_or_evidence_fail": sum_key(solo_tokens, "structural_or_evidence_fail"),
        "solo_wrong_verdict": sum_key(solo_tokens, "wrong_verdict"),
        "strong_solo_collapse_pairs": sum_key(summaries, "strong_solo_collapse_pairs"),
        "non_target_full_family_completion_pairs": sum_key(summaries, "non_target_full_family_completion_pairs"),
        "token_ratio_holo_vs_selected_solo": ratio(holo_total, selected_solo_total),
    }

    family_counts: dict[str, dict] = defaultdict(lambda: {
        "holo_correct_admissible_packets": 0,
        "packets": 0,
        "pairs": 0,
        "solo_attempts": 0,
        "solo_knew": 0,
        "solo_not_knew": 0,
        "solo_parse_fail": 0,
        "solo_structural_or_evidence_fail": 0,
        "solo_wrong_verdict": 0,
    })
    for row in pair_rows:
        family = family_counts[row["family_id"]]
        family["pairs"] += 1
        family["packets"] += 2
        family["holo_correct_admissible_packets"] += int(bool(row["holo_target"]["final_correct"])) + int(bool(row["holo_guardrail"]["final_correct"]))
        family["solo_attempts"] += 6
        family["solo_knew"] += int(row["solo"].get("knew_admissible") or 0)
        family["solo_not_knew"] += int(row["solo"].get("not_knew") or 0)
        family["solo_parse_fail"] += int(row["solo"].get("parse_fail") or 0)
        family["solo_structural_or_evidence_fail"] += int(row["solo"].get("structural_or_evidence_fail") or 0)
        family["solo_wrong_verdict"] += int(row["solo"].get("wrong_verdict") or 0)

    selection = read_json(SELECTION_PATH)
    run_pairs = {row["pair_id"] for row in pair_rows}
    remaining = [target for target in selection.get("all_top_targets", []) if target.get("pair_id") not in run_pairs]
    remaining_full_family = remaining_full_family_pairs_after_target_pool()
    staged_next = load_staged_batch(max(batches) + 1, [row.get("pair_id") for row in remaining])
    if staged_next and staged_next.get("selection_mode") != "target-selection":
        staged_next = None
    staged_full_family = load_staged_batch(5, [row["pair_id"] for row in remaining_full_family])
    if staged_full_family and staged_full_family.get("selection_mode") != "full-family-remainder":
        staged_full_family = None

    batch_summaries = []
    for batch, data in comparisons:
        metrics = data["summary_metrics"]
        solo = data["solo_tokens_on_selected_packets"]
        batch_summaries.append({
            "batch": f"{batch:03d}",
            "classification": data.get("classification"),
            "holo_packets": metrics.get("holo_final_packet_count"),
            "holo_packets_correct_admissible": metrics.get("holo_final_packets_correct_admissible"),
            "holo_valid_pairs": metrics.get("holo_valid_pairs"),
            "pair_count": metrics.get("holo_pair_count"),
            "package_sha256": data.get("package_sha256"),
            "preflight_head": live_preflight_head(batch),
            "holo_intra_worker_misses_corrected": metrics.get("holo_intra_worker_misses_corrected"),
            "solo_knew": solo.get("knew_admissible"),
            "solo_not_knew": solo.get("not_knew"),
            "solo_parse_fail": solo.get("parse_fail"),
            "solo_structural_or_evidence_fail": solo.get("structural_or_evidence_fail"),
            "solo_wrong_verdict": solo.get("wrong_verdict"),
            "token_ratio_holo_vs_selected_solo": metrics.get("token_ratio_holo_vs_selected_solo"),
        })

    batch_label = ", ".join(f"{batch:03d}" for batch in batches)
    if staged_next:
        next_valid_step = f"Run explicitly approved live Holo execution for {staged_next['batch_id']}. Do not run solo or judges first."
    elif remaining:
        next_valid_step = "Stage the next selected-target batch from the remaining target pool. Do not run providers until explicitly approved."
    elif staged_full_family:
        next_valid_step = (
            f"After selected-target promotion is complete, run explicitly approved live Holo execution for "
            f"{staged_full_family['batch_id']}. Keep it under full-family statistical language."
        )
    else:
        next_valid_step = "No selected-target staging gap is visible. Keep provider work closed until an explicit live gate is opened."

    return {
        "batch_summaries": batch_summaries,
        "claim_boundaries": [
            f"This memo covers only Wave 2 Holo target Batches {batch_label}, not the entire Wave 2 frozen packet bank.",
            f"Holo solved all selected target packets run in these batches: {combined_metrics['holo_packets_correct_admissible']}/{combined_metrics['holo_packets']} packets and {combined_metrics['holo_valid_pairs']}/{combined_metrics['holo_pairs']} sibling pairs.",
            f"The matched solo one-shot results on the same selected packets were unreliable: {combined_metrics['solo_not_knew']}/{combined_metrics['selected_solo_attempts']} attempts were not KNEW/admissible.",
            "Selected-target evidence remains separate from full-family statistical proof until the non-target remainder has live Holo evidence.",
            "Any staged selected-target or full-family remainder section is preflight-only and excluded from scored totals.",
            "Token ratio is operational bookkeeping only. It is not a proof claim because solo was one-shot while Holo used governed multi-turn architecture.",
            "No judges are included in this package. No new provider calls were made to create this combined memo.",
            "Internal Holo worker misses are separated from external solo failures. They show governance correction, not standalone solo failure.",
        ],
        "classification": "WAVE2_HOLO_TARGET_BATCH_001_002_003_COMBINED_EVIDENCE_MEMO_NO_PROVIDER",
        "combined_metrics": combined_metrics,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "family_counts": dict(sorted(family_counts.items())),
        "intra_holo_worker_misses_corrected": [
            miss
            for _, data in comparisons
            for miss in data.get("intra_holo_worker_misses_corrected", [])
        ],
        "full_family_remainder_after_target_pool": remaining_full_family,
        "next_valid_step": next_valid_step,
        "no_judge_calls_for_this_package": True,
        "no_provider_calls_for_this_package": True,
        "pair_rows": pair_rows,
        "remaining_target_pool": {
            "pairs_already_run_in_batch_set": len(run_pairs),
            "remaining_top_targets": len(remaining),
            "total_top_targets_from_solo_triage": len(selection.get("all_top_targets", [])),
            "next_batch_preview_pair_count": min(10, len(remaining)),
            "next_batch_preview_pairs": remaining[:10],
        },
        "staged_full_family_remainder_batch": staged_full_family,
        "staged_next_target_batch": staged_next,
        "source_batch_comparison_paths": {
            f"batch_{batch:03d}": str(batch_comparison_path(batch))
            for batch in batches
        },
        "source_selection_path": str(SELECTION_PATH),
        "source_selection_sha256": selection.get("package_sha256"),
    }


def combined_md(data: dict) -> str:
    metrics = data["combined_metrics"]
    batch_label = "+".join(batch["batch"] for batch in data["batch_summaries"])
    batch_words = ", ".join(f"Batch {batch['batch']}" for batch in data["batch_summaries"])
    lines = [
        f"# Wave 2 Holo Target Batch {batch_label} Combined Evidence Memo",
        "",
        f"Classification: `{data['classification']}`",
        f"Package SHA-256: `{data['package_sha256']}`",
        "",
        "## Scope",
        "",
        f"This is a no-provider combined memo over the Wave 2 Holo target {batch_words} evidence. It does not add judge calls, provider calls, packet edits, prompt edits, or new scoring rules.",
        "",
        "## Combined Result",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Batches included | `{metrics['batch_count']}` |",
        f"| Holo sibling pairs | `{metrics['holo_pairs']}` |",
        f"| Holo packets | `{metrics['holo_packets']}` |",
        f"| Holo packets correct/admissible | `{metrics['holo_packets_correct_admissible']}` |",
        f"| Holo valid pairs | `{metrics['holo_valid_pairs']}` |",
        f"| Holo provider failures | `{metrics['holo_provider_failures']}` |",
        f"| Holo parse failures | `{metrics['holo_parse_failures']}` |",
        f"| Selected solo attempts | `{metrics['selected_solo_attempts']}` |",
        f"| Solo KNEW/admissible | `{metrics['solo_knew_admissible']}` |",
        f"| Solo not KNEW | `{metrics['solo_not_knew']}` |",
        f"| Solo wrong verdicts | `{metrics['solo_wrong_verdict']}` |",
        f"| Solo parse fails | `{metrics['solo_parse_fail']}` |",
        f"| Solo structural/evidence fails | `{metrics['solo_structural_or_evidence_fail']}` |",
        f"| All-six solo-collapse pairs | `{metrics['all_six_solo_collapse_pairs']}` |",
        f"| Strong solo-collapse pairs | `{metrics['strong_solo_collapse_pairs']}` |",
        f"| Non-target full-family completion pairs | `{metrics['non_target_full_family_completion_pairs']}` |",
        f"| Intra-Holo worker misses corrected | `{metrics['holo_intra_worker_misses_corrected']}` |",
        f"| Solo not KNEW rate | `{metrics['solo_not_knew_rate']}` |",
        f"| Holo vs selected solo token ratio | `{metrics['token_ratio_holo_vs_selected_solo']}` |",
        f"| Gov share of Holo tokens | `{metrics['gov_share_of_holo_tokens']}` |",
        "",
        "## Batch Comparison",
        "",
        "| Batch | Holo packets | Holo valid pairs | Solo KNEW | Solo not KNEW | Wrong verdicts | Parse fails | Structural/evidence fails | Intra-Holo corrections | Token ratio |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for batch in data["batch_summaries"]:
        lines.append(
            f"| {batch['batch']} | `{batch['holo_packets_correct_admissible']}/{batch['holo_packets']}` | "
            f"`{batch['holo_valid_pairs']}/{batch['pair_count']}` | `{batch['solo_knew']}` | `{batch['solo_not_knew']}` | "
            f"`{batch['solo_wrong_verdict']}` | `{batch['solo_parse_fail']}` | `{batch['solo_structural_or_evidence_fail']}` | "
            f"`{batch['holo_intra_worker_misses_corrected']}` | "
            f"`{batch['token_ratio_holo_vs_selected_solo']}` |"
        )
    lines.extend([
        "",
        "## Claim Boundaries",
        "",
    ])
    for boundary in data["claim_boundaries"]:
        lines.append(f"- {boundary}")
    lines.extend([
        "",
        "## Family Breakdown",
        "",
        "| Family | Pairs | Packets | Holo correct/admissible packets | Solo attempts | Solo KNEW | Solo not KNEW | Wrong verdicts | Parse fails | Structural/evidence fails |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for family_id, counts in data["family_counts"].items():
        lines.append(
            f"| `{family_id}` | `{counts['pairs']}` | `{counts['packets']}` | `{counts['holo_correct_admissible_packets']}` | "
            f"`{counts['solo_attempts']}` | `{counts['solo_knew']}` | `{counts['solo_not_knew']}` | "
            f"`{counts['solo_wrong_verdict']}` | `{counts['solo_parse_fail']}` | `{counts['solo_structural_or_evidence_fail']}` |"
        )
    lines.extend([
        "",
        "## Pair Rows",
        "",
        "| Batch | Family | Pair | Bucket | Triage class | Solo not KNEW | Solo wrong verdicts | Holo target | Holo guardrail | Evidence class |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ])
    for row in data["pair_rows"]:
        target = row["holo_target"]
        guardrail = row["holo_guardrail"]
        solo = row["solo"]
        lines.append(
            f"| `{row['batch']}` | `{row['family_id']}` | `{row['pair_id']}` | `{row['target_bucket']}` | `{row['triage_class']}` | "
            f"`{solo['not_knew']}` | `{solo['wrong_verdict']}` | "
            f"`{target['packet_id']} {target['expected']}->{target['final_verdict']}` | "
            f"`{guardrail['packet_id']} {guardrail['expected']}->{guardrail['final_verdict']}` | `{row['evidence_class']}` |"
        )
    remaining = data["remaining_target_pool"]
    lines.extend([
        "",
        "## Remaining Target Pool",
        "",
        f"Solo triage produced `{remaining['total_top_targets_from_solo_triage']}` top targets. These batches have run `{remaining['pairs_already_run_in_batch_set']}` pairs, leaving `{remaining['remaining_top_targets']}` target pairs.",
    ])

    staged = data.get("staged_next_target_batch")
    if staged:
        counts = staged["expected_counts"]
        lines.extend([
            "",
            "## Staged Final Target Batch",
            "",
            f"Batch: `{staged['batch_id']}`",
            f"Selection mode: `{staged['selection_mode']}`",
            f"Selection mode defaulted: `{staged['selection_mode_defaulted']}`",
            f"Status: `{staged['status']}`",
            f"Ready for live Holo: `{staged['ready_for_live_holo']}`",
            f"Selected pairs match expected target pool: `{staged['selected_pairs_match_expected_pool']}`",
            f"Providers called: `{staged['providers_called']}`",
            f"Live Holo started: `{staged['live_holo_started']}`",
            f"Live execution gate: `{staged['live_execution_gate'].get('status', 'MISSING_REPO_EVIDENCE')}`",
            f"Solo started: `{staged['solo_started']}`",
            f"Judges started: `{staged['judges_started']}`",
            f"Expected live provider calls: `{counts.get('total_provider_calls')}` (`{counts.get('worker_calls')}` worker, `{counts.get('gov_calls')}` Gov)",
            f"Expected solo calls: `{counts.get('solo_calls')}`",
            f"Expected judge calls: `{counts.get('judge_calls')}`",
            f"Live preflight root signature: `{staged['live_preflight_root_signature']}`",
            "",
            f"Claim boundary: {staged['claim_boundary']}",
            "",
            "| Priority | Family | Pair | Class | Bucket | Not KNEW | Wrong verdicts | Parse/provider fails |",
            "| ---: | --- | --- | --- | --- | ---: | ---: | ---: |",
        ])
        for row in staged["selected_pairs"]:
            lines.append(
                f"| `{display_value(row['priority_score'])}` | `{row['family_id']}` | `{row['pair_id']}` | "
                f"`{row['triage_class']}` | `{row['target_bucket']}` | `{display_value(row['not_knew_count'])}` | "
                f"`{display_value(row['wrong_verdict_count'])}` | `{display_value(row['parse_or_provider_fail_count'])}` |"
            )

    full_family = data.get("full_family_remainder_after_target_pool", [])
    lines.extend([
        "",
        "## Full-Family Remainder After Target Pool",
        "",
        "These pairs are outside the selected-target pool and are needed only for full 60-pair Wave 2 coverage.",
        "",
        f"Remaining non-target full-family pairs: `{len(full_family)}`.",
    ])
    if full_family:
        lines.extend([
            "",
            "| Family | Pair | Bucket | Packets |",
            "| --- | --- | --- | --- |",
        ])
        for row in full_family:
            lines.append(
                f"| `{row['family_id']}` | `{row['pair_id']}` | `{row['target_bucket']}` | `{', '.join(row['packet_ids'])}` |"
            )

    staged_full = data.get("staged_full_family_remainder_batch")
    if staged_full:
        counts = staged_full["expected_counts"]
        lines.extend([
            "",
            "## Staged Full-Family Remainder Batch",
            "",
            f"Batch: `{staged_full['batch_id']}`",
            f"Selection mode: `{staged_full['selection_mode']}`",
            f"Selection mode defaulted: `{staged_full['selection_mode_defaulted']}`",
            f"Status: `{staged_full['status']}`",
            f"Ready for live Holo: `{staged_full['ready_for_live_holo']}`",
            f"Selected pairs match remaining full-family backlog: `{staged_full['selected_pairs_match_expected_pool']}`",
            f"Providers called: `{staged_full['providers_called']}`",
            f"Live Holo started: `{staged_full['live_holo_started']}`",
            f"Live execution gate: `{staged_full['live_execution_gate'].get('status', 'MISSING_REPO_EVIDENCE')}`",
            f"Solo started: `{staged_full['solo_started']}`",
            f"Judges started: `{staged_full['judges_started']}`",
            f"Expected live provider calls: `{counts.get('total_provider_calls')}` (`{counts.get('worker_calls')}` worker, `{counts.get('gov_calls')}` Gov)",
            f"Expected solo calls: `{counts.get('solo_calls')}`",
            f"Expected judge calls: `{counts.get('judge_calls')}`",
            f"Live preflight root signature: `{staged_full['live_preflight_root_signature']}`",
            "",
            f"Claim boundary: {staged_full['claim_boundary']}",
            "",
            "| Priority | Family | Pair | Class | Bucket | Not KNEW | Wrong verdicts | Parse/provider fails |",
            "| ---: | --- | --- | --- | --- | ---: | ---: | ---: |",
        ])
        for row in staged_full["selected_pairs"]:
            lines.append(
                f"| `{display_value(row['priority_score'])}` | `{row['family_id']}` | `{row['pair_id']}` | "
                f"`{row['triage_class']}` | `{row['target_bucket']}` | `{display_value(row['not_knew_count'])}` | "
                f"`{display_value(row['wrong_verdict_count'])}` | `{display_value(row['parse_or_provider_fail_count'])}` |"
            )

    lines.extend([
        "",
        "## Next Valid Step",
        "",
        data["next_valid_step"],
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batches", nargs="+", type=int, default=[1, 2, 3])
    args = parser.parse_args()

    data = build_combined(args.batches)
    suffix = "_".join(f"{batch:03d}" for batch in args.batches)
    json_path = TARGET_ROOT / f"WAVE2_HOLO_TARGET_BATCH_{suffix}_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
    md_path = TARGET_ROOT / f"WAVE2_HOLO_TARGET_BATCH_{suffix}_COMBINED_EVIDENCE_MEMO_2026_07_01.md"
    package_sha256 = write_json_with_hash(json_path, data)
    final_data = read_json(json_path)
    md_path.write_text(combined_md(final_data))
    print(json.dumps({
        "status": "PASS",
        "json": str(json_path),
        "md": str(md_path),
        "package_sha256": package_sha256,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
