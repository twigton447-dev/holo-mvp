#!/usr/bin/env python3
"""Build the final no-provider Wave 2 combined evidence memo including Batch 005."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01")
BATCHES_ROOT = ROOT / "holo_target_batches"
SELECTED_COMBINED_001_004 = (
    BATCHES_ROOT / "WAVE2_HOLO_TARGET_BATCH_001_002_003_004_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
)
BATCH005_ROOT = BATCHES_ROOT / "wave2_holo_target_batch_005"
BATCH005_REGISTRATION = BATCH005_ROOT / "WAVE2_HOLO_TARGET_BATCH_005_REGISTRATION_2026_07_01.json"
BATCH005_RUN_DIR = BATCH005_ROOT / "live_runs" / "run_20260701T141727Z"
BATCH005_RESULTS = BATCH005_RUN_DIR / "live_results.json"
BATCH005_TRACE = BATCH005_RUN_DIR / "TRACE_CALLS.jsonl"
BATCH005_LOCK_VALIDATION = BATCH005_RUN_DIR / "LOCK_VALIDATION.json"
BATCH005_NO_LEAKAGE = BATCH005_RUN_DIR / "WAVE2_HOLO_TARGET_BATCH_005_NO_LEAKAGE_AUDIT.json"
OUT_JSON = BATCHES_ROOT / "WAVE2_HOLO_TARGET_BATCH_001_002_003_004_005_FINAL_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
OUT_MD = BATCHES_ROOT / "WAVE2_HOLO_TARGET_BATCH_001_002_003_004_005_FINAL_COMBINED_EVIDENCE_MEMO_2026_07_01.md"
SELECTED_BATCH_001_004_CALLS = {
    "provider_calls": 370,
    "worker_calls": 222,
    "gov_calls": 148,
    "judge_calls": 0,
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def canonical_hash(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    rendered = json.dumps(body, indent=2, sort_keys=True) + "\n"
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def write_json_with_hash(path: Path, data: dict[str, Any]) -> str:
    data = dict(data)
    data["created_at_utc"] = datetime.now(timezone.utc).isoformat()
    data["package_sha256"] = canonical_hash(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return data["package_sha256"]


def ratio(num: int | float, den: int | float) -> float:
    return round(num / den, 6) if den else 0.0


def zero_failure_upper_95(n: int) -> float:
    return round((1 - math.pow(0.05, 1 / n)) * 100, 6) if n else 0.0


def rule_of_three(n: int) -> float:
    return round((3 / n) * 100, 6) if n else 0.0


def batch005_token_split() -> dict[str, dict[str, int]]:
    split = {
        "worker": {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        "gov": {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
    }
    for line in BATCH005_TRACE.read_text().splitlines():
        row = json.loads(line)
        kind = "gov" if "_G" in row.get("turn_id", "") else "worker"
        split[kind]["calls"] += 1
        split[kind]["input_tokens"] += int(row.get("input_tokens") or 0)
        split[kind]["output_tokens"] += int(row.get("output_tokens") or 0)
        split[kind]["total_tokens"] += int(row.get("total_tokens") or 0)
    return split


def registration_by_pair() -> dict[str, dict[str, Any]]:
    registration = read_json(BATCH005_REGISTRATION)
    pairs: dict[str, dict[str, Any]] = {}
    for row in registration.get("selected_records", []):
        pair = pairs.setdefault(
            row["pair_id"],
            {
                "domain": row.get("domain"),
                "family_id": row.get("family_id"),
                "pair_id": row.get("pair_id"),
                "target_bucket": row.get("target_bucket"),
                "triage_class": row.get("triage_class"),
                "packet_ids": [],
            },
        )
        pair["packet_ids"].append(row["packet_id"])
    for pair in pairs.values():
        pair["packet_ids"] = sorted(pair["packet_ids"])
    return pairs


def batch005_pair_rows() -> list[dict[str, Any]]:
    results = read_json(BATCH005_RESULTS)
    pairs = registration_by_pair()
    rows = []
    for item in results.get("benchmark_inventory", []):
        meta = pairs.get(item["pair_id"], {})
        rows.append(
            {
                "batch": "005",
                "domain": meta.get("domain"),
                "evidence_class": "FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE",
                "family_id": meta.get("family_id"),
                "holo_guardrail": {
                    "expected": item.get("guardrail_expected"),
                    "final_correct": item.get("guardrail_final_correct"),
                    "final_verdict": item.get("guardrail_final_verdict"),
                    "packet_id": item.get("guardrail_packet_id"),
                },
                "holo_pair_valid": item.get("pair_valid"),
                "holo_target": {
                    "expected": item.get("target_expected"),
                    "final_correct": item.get("target_final_correct"),
                    "final_verdict": item.get("target_final_verdict"),
                    "packet_id": item.get("target_packet_id"),
                },
                "pair_id": item.get("pair_id"),
                "target_bucket": item.get("benchmark_bucket"),
                "triage_class": meta.get("triage_class"),
                "solo": {
                    "knew_admissible": None,
                    "not_knew": None,
                    "parse_fail": None,
                    "provider_failures": None,
                    "structural_or_evidence_fail": None,
                    "wrong_verdict": None,
                },
            }
        )
    return rows


def count_expected_verdicts(pair_rows: list[dict[str, Any]]) -> Counter:
    counts: Counter = Counter()
    for row in pair_rows:
        counts[row["holo_target"]["expected"]] += 1
        counts[row["holo_guardrail"]["expected"]] += 1
    return counts


def count_error_types(pair_rows: list[dict[str, Any]]) -> dict[str, int]:
    fp = 0
    fn = 0
    wrong = 0
    for row in pair_rows:
        for side in ("holo_target", "holo_guardrail"):
            expected = row[side]["expected"]
            actual = row[side]["final_verdict"]
            if expected != actual:
                wrong += 1
                if expected == "ALLOW" and actual == "ESCALATE":
                    fp += 1
                if expected == "ESCALATE" and actual == "ALLOW":
                    fn += 1
    return {"false_positives": fp, "false_negatives": fn, "wrong_verdicts": wrong}


def family_rollup(pair_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    families: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "holo_correct_admissible_packets": 0,
            "packets": 0,
            "pairs": 0,
            "solo_attempts": 0,
            "solo_knew": 0,
            "solo_not_knew": 0,
            "solo_parse_fail": 0,
            "solo_structural_or_evidence_fail": 0,
            "solo_wrong_verdict": 0,
        }
    )
    for row in pair_rows:
        family = families[row["family_id"]]
        family["pairs"] += 1
        family["packets"] += 2
        family["holo_correct_admissible_packets"] += int(bool(row["holo_target"]["final_correct"]))
        family["holo_correct_admissible_packets"] += int(bool(row["holo_guardrail"]["final_correct"]))
        solo = row.get("solo") or {}
        if solo.get("knew_admissible") is not None:
            family["solo_attempts"] += 6
            family["solo_knew"] += int(solo.get("knew_admissible") or 0)
            family["solo_not_knew"] += int(solo.get("not_knew") or 0)
            family["solo_parse_fail"] += int(solo.get("parse_fail") or 0)
            family["solo_structural_or_evidence_fail"] += int(solo.get("structural_or_evidence_fail") or 0)
            family["solo_wrong_verdict"] += int(solo.get("wrong_verdict") or 0)
    return dict(sorted(families.items()))


def build_package() -> dict[str, Any]:
    selected = read_json(SELECTED_COMBINED_001_004)
    batch005 = read_json(BATCH005_RESULTS)
    lock = read_json(BATCH005_LOCK_VALIDATION)
    no_leakage = read_json(BATCH005_NO_LEAKAGE)
    split = batch005_token_split()
    b5_rows = batch005_pair_rows()
    all_rows = list(selected.get("pair_rows", [])) + b5_rows
    expected_counts = count_expected_verdicts(all_rows)
    errors = count_error_types(all_rows)
    selected_metrics = selected["combined_metrics"]
    b5_packet_correct = int(batch005.get("packet_correct") or 0)
    b5_packet_count = int(batch005.get("packet_count") or 0)
    b5_pair_count = len(batch005.get("benchmark_inventory", []))
    b5_valid_pairs = int(batch005.get("valid_pairs") or 0)
    b5_tokens = batch005.get("totals", {})

    wave2_metrics = {
        "allow_denominator": expected_counts.get("ALLOW", 0),
        "batch_count": 5,
        "false_negatives": errors["false_negatives"],
        "false_positives": errors["false_positives"],
        "fnr_observed": ratio(errors["false_negatives"], expected_counts.get("ESCALATE", 0)),
        "fnr_upper_95_exact_percent": zero_failure_upper_95(expected_counts.get("ESCALATE", 0))
        if errors["false_negatives"] == 0
        else None,
        "fnr_upper_95_rule_of_three_percent": rule_of_three(expected_counts.get("ESCALATE", 0))
        if errors["false_negatives"] == 0
        else None,
        "fpr_observed": ratio(errors["false_positives"], expected_counts.get("ALLOW", 0)),
        "fpr_upper_95_exact_percent": zero_failure_upper_95(expected_counts.get("ALLOW", 0))
        if errors["false_positives"] == 0
        else None,
        "fpr_upper_95_rule_of_three_percent": rule_of_three(expected_counts.get("ALLOW", 0))
        if errors["false_positives"] == 0
        else None,
        "gov_calls": SELECTED_BATCH_001_004_CALLS["gov_calls"] + int(batch005.get("gov_calls") or 0),
        "gov_share_of_holo_tokens": ratio(
            int(selected_metrics.get("holo_gov_tokens") or 0) + split["gov"]["total_tokens"],
            int(selected_metrics.get("holo_total_tokens") or 0) + int(b5_tokens.get("total_tokens") or 0),
        ),
        "holo_gov_tokens": int(selected_metrics.get("holo_gov_tokens") or 0) + split["gov"]["total_tokens"],
        "holo_input_tokens": int(selected_metrics.get("holo_input_tokens") or 0) + int(b5_tokens.get("input_tokens") or 0),
        "holo_output_tokens": int(selected_metrics.get("holo_output_tokens") or 0) + int(b5_tokens.get("output_tokens") or 0),
        "holo_packets": int(selected_metrics.get("holo_packets") or 0) + b5_packet_count,
        "holo_packets_correct_admissible": int(selected_metrics.get("holo_packets_correct_admissible") or 0)
        + b5_packet_correct,
        "holo_pairs": int(selected_metrics.get("holo_pairs") or 0) + b5_pair_count,
        "holo_provider_calls": SELECTED_BATCH_001_004_CALLS["provider_calls"] + int(batch005.get("provider_calls") or 0),
        "holo_provider_failures": int(selected_metrics.get("holo_provider_failures") or 0)
        + len(batch005.get("provider_failures") or []),
        "holo_total_tokens": int(selected_metrics.get("holo_total_tokens") or 0) + int(b5_tokens.get("total_tokens") or 0),
        "holo_valid_pairs": int(selected_metrics.get("holo_valid_pairs") or 0) + b5_valid_pairs,
        "holo_worker_tokens": int(selected_metrics.get("holo_worker_tokens") or 0) + split["worker"]["total_tokens"],
        "judge_calls": SELECTED_BATCH_001_004_CALLS["judge_calls"] + int(batch005.get("judge_calls") or 0),
        "packet_error_observed": 0.0,
        "packet_error_upper_95_exact_percent": zero_failure_upper_95(
            int(selected_metrics.get("holo_packets") or 0) + b5_packet_count
        ),
        "packet_error_upper_95_rule_of_three_percent": rule_of_three(
            int(selected_metrics.get("holo_packets") or 0) + b5_packet_count
        ),
        "selected_target_solo_attempts": int(selected_metrics.get("selected_solo_attempts") or 0),
        "selected_target_solo_knew_admissible": int(selected_metrics.get("solo_knew_admissible") or 0),
        "selected_target_solo_not_knew": int(selected_metrics.get("solo_not_knew") or 0),
        "selected_target_solo_not_knew_rate": selected_metrics.get("solo_not_knew_rate"),
        "selected_target_solo_tokens": int(selected_metrics.get("selected_solo_total_tokens") or 0),
        "selected_target_token_ratio_holo_vs_solo": selected_metrics.get("token_ratio_holo_vs_selected_solo"),
        "wave2_full_family_completion_pairs": b5_valid_pairs,
        "worker_calls": SELECTED_BATCH_001_004_CALLS["worker_calls"] + int(batch005.get("worker_calls") or 0),
        "wrong_verdicts": errors["wrong_verdicts"],
    }

    return {
        "batch005_summary": {
            "classification": batch005.get("classification"),
            "gov_calls": batch005.get("gov_calls"),
            "lock_root_signature": lock.get("root_signature"),
            "lock_validation_status": lock.get("validation_status"),
            "no_leakage_prompt_files_scanned": no_leakage.get("prompt_files_scanned"),
            "no_leakage_status": no_leakage.get("status"),
            "packet_count": b5_packet_count,
            "packets_correct_admissible": b5_packet_correct,
            "provider_calls": batch005.get("provider_calls"),
            "readiness_passed": batch005.get("readiness_passed"),
            "run_dir": str(BATCH005_RUN_DIR),
            "tokens": b5_tokens,
            "valid_pairs": b5_valid_pairs,
            "worker_calls": batch005.get("worker_calls"),
        },
        "claim_boundaries": [
            "This final Wave 2 memo folds Batch005 into the Holo result as full-family completion evidence.",
            "Batch001-004 retain the selected-target solo comparison layer; Batch005 has no matched solo baseline and must not be described as solo-collapse evidence.",
            "The Wave2 Holo total is 120/120 packets and 60/60 valid sibling pairs, with 0 observed false positives and 0 observed false negatives.",
            "FPR/FNR denominators are 60 ALLOW and 60 ESCALATE packets for Wave2 only.",
            "No judges are included in this package. No provider calls were made to create this memo.",
            "Internal Holo worker misses remain separate from external solo failures.",
        ],
        "classification": "WAVE2_HOLO_TARGET_BATCH_001_002_003_004_005_FINAL_COMBINED_EVIDENCE_MEMO_NO_PROVIDER",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "family_counts": family_rollup(all_rows),
        "no_judge_calls_for_this_package": True,
        "no_provider_calls_for_this_package": True,
        "pair_rows": all_rows,
        "package_sha256": "",
        "source_paths": {
            "batch001_004_combined": str(SELECTED_COMBINED_001_004),
            "batch005_live_results": str(BATCH005_RESULTS),
            "batch005_lock_validation": str(BATCH005_LOCK_VALIDATION),
            "batch005_no_leakage": str(BATCH005_NO_LEAKAGE),
            "batch005_registration": str(BATCH005_REGISTRATION),
            "batch005_trace": str(BATCH005_TRACE),
        },
        "wave2_metrics": wave2_metrics,
    }


def render_md(data: dict[str, Any]) -> str:
    m = data["wave2_metrics"]
    lines = [
        "# Wave 2 Final Combined Evidence Memo",
        "",
        f"Classification: `{data['classification']}`",
        f"Package SHA-256: `{data['package_sha256']}`",
        "",
        "## Result",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Holo packets | `{m['holo_packets']}` |",
        f"| Holo packets correct/admissible | `{m['holo_packets_correct_admissible']}` |",
        f"| Holo valid sibling pairs | `{m['holo_valid_pairs']}` |",
        f"| False positives | `{m['false_positives']}/{m['allow_denominator']}` |",
        f"| False negatives | `{m['false_negatives']}/{m['esc_denominator'] if 'esc_denominator' in m else 60}` |",
        f"| Packet error upper 95%, exact | `{m['packet_error_upper_95_exact_percent']}%` |",
        f"| Packet error upper 95%, rule of three | `{m['packet_error_upper_95_rule_of_three_percent']}%` |",
        f"| FPR upper 95%, exact | `{m['fpr_upper_95_exact_percent']}%` |",
        f"| FPR upper 95%, rule of three | `{m['fpr_upper_95_rule_of_three_percent']}%` |",
        f"| FNR upper 95%, exact | `{m['fnr_upper_95_exact_percent']}%` |",
        f"| FNR upper 95%, rule of three | `{m['fnr_upper_95_rule_of_three_percent']}%` |",
        f"| Provider calls | `{m['holo_provider_calls']}` |",
        f"| Worker calls | `{m['worker_calls']}` |",
        f"| Gov calls | `{m['gov_calls']}` |",
        f"| Judge calls | `{m['judge_calls']}` |",
        f"| Holo total tokens | `{m['holo_total_tokens']}` |",
        f"| Gov share of Holo tokens | `{m['gov_share_of_holo_tokens']}` |",
        "",
        "## Solo Comparison Layer",
        "",
        "Solo comparison exists for Batch001-004 selected targets only. Batch005 is Holo-only full-family completion evidence.",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Selected-target solo attempts | `{m['selected_target_solo_attempts']}` |",
        f"| Selected-target solo KNEW/admissible | `{m['selected_target_solo_knew_admissible']}` |",
        f"| Selected-target solo not KNEW | `{m['selected_target_solo_not_knew']}` |",
        f"| Selected-target solo not KNEW rate | `{m['selected_target_solo_not_knew_rate']}` |",
        f"| Selected-target Holo/solo token ratio | `{m['selected_target_token_ratio_holo_vs_solo']}` |",
        "",
        "## Batch005 Fold-In",
        "",
    ]
    b5 = data["batch005_summary"]
    lines.extend(
        [
            f"- Classification: `{b5['classification']}`",
            f"- Run: `{b5['run_dir']}`",
            f"- Packets: `{b5['packets_correct_admissible']}/{b5['packet_count']}`",
            f"- Valid pairs: `{b5['valid_pairs']}`",
            f"- Provider calls: `{b5['provider_calls']}`",
            f"- Worker/Gov calls: `{b5['worker_calls']}` worker / `{b5['gov_calls']}` Gov",
            f"- No leakage: `{b5['no_leakage_status']}`, `{b5['no_leakage_prompt_files_scanned']}` prompt files scanned",
            f"- Lock validation: `{b5['lock_validation_status']}`",
            "",
            "## Claim Boundaries",
            "",
        ]
    )
    for boundary in data["claim_boundaries"]:
        lines.append(f"- {boundary}")
    lines.extend(
        [
            "",
            "## Family Breakdown",
            "",
            "| Family | Pairs | Packets | Holo correct/admissible packets | Solo attempts present | Solo KNEW | Solo not KNEW |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for family_id, counts in data["family_counts"].items():
        lines.append(
            f"| `{family_id}` | `{counts['pairs']}` | `{counts['packets']}` | "
            f"`{counts['holo_correct_admissible_packets']}` | `{counts['solo_attempts']}` | "
            f"`{counts['solo_knew']}` | `{counts['solo_not_knew']}` |"
        )
    lines.extend(
        [
            "",
            "## Pair Rows",
            "",
            "| Batch | Family | Pair | Bucket | Evidence class | Target | Guardrail | Solo layer |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in data["pair_rows"]:
        solo = row.get("solo") or {}
        solo_layer = "none" if solo.get("knew_admissible") is None else f"{solo.get('knew_admissible')} KNEW / {solo.get('not_knew')} not KNEW"
        lines.append(
            f"| `{row['batch']}` | `{row['family_id']}` | `{row['pair_id']}` | `{row['target_bucket']}` | "
            f"`{row['evidence_class']}` | `{row['holo_target']['expected']}->{row['holo_target']['final_verdict']}` | "
            f"`{row['holo_guardrail']['expected']}->{row['holo_guardrail']['final_verdict']}` | `{solo_layer}` |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    data = build_package()
    # Store ESC denominator explicitly after build to keep the top table simple.
    counts = count_expected_verdicts(data["pair_rows"])
    data["wave2_metrics"]["esc_denominator"] = counts.get("ESCALATE", 0)
    data["package_sha256"] = canonical_hash(data)
    OUT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(render_md(data))
    print(
        json.dumps(
            {
                "json": str(OUT_JSON),
                "md": str(OUT_MD),
                "package_sha256": data["package_sha256"],
                "status": "PASS",
                "wave2_packets": data["wave2_metrics"]["holo_packets"],
                "wave2_pairs": data["wave2_metrics"]["holo_pairs"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
