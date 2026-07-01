#!/usr/bin/env python3
"""Build a no-provider combined evidence package for Wave2, Wave3, and Wave4."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OUT_JSON = Path("docs/benchmark/HOLOVERIFY_WAVE2_WAVE3_WAVE4_COMBINED_EVIDENCE_MEMO_2026_07_01.json")
OUT_MD = Path("docs/benchmark/HOLOVERIFY_WAVE2_WAVE3_WAVE4_COMBINED_EVIDENCE_MEMO_2026_07_01.md")
WAVE2_FINAL_JSON = Path(
    "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/"
    "holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_004_005_FINAL_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
)

RUN_SPECS = [
    {
        "wave": "wave2",
        "batch": "001",
        "run_dir": Path(
            "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/"
            "holo_target_batches/wave2_holo_target_batch_001/live_runs/run_20260701T042037Z"
        ),
        "registration": None,
    },
    {
        "wave": "wave2",
        "batch": "002",
        "run_dir": Path(
            "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/"
            "holo_target_batches/wave2_holo_target_batch_002/live_runs/run_20260701T045827Z"
        ),
        "registration": None,
    },
    {
        "wave": "wave2",
        "batch": "003",
        "run_dir": Path(
            "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/"
            "holo_target_batches/wave2_holo_target_batch_003/live_runs/run_20260701T054545Z"
        ),
        "registration": None,
    },
    {
        "wave": "wave2",
        "batch": "004",
        "run_dir": Path(
            "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/"
            "holo_target_batches/wave2_holo_target_batch_004/live_runs/run_20260701T132715Z"
        ),
        "registration": None,
    },
    {
        "wave": "wave2",
        "batch": "005",
        "run_dir": Path(
            "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/"
            "holo_target_batches/wave2_holo_target_batch_005/live_runs/run_20260701T141727Z"
        ),
        "registration": None,
    },
    {
        "wave": "wave3",
        "batch": "001",
        "run_dir": Path(
            "docs/benchmark/holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/"
            "holo_target_batches/wave3_holo_target_batch_001/live_runs/run_20260701T163353Z"
        ),
        "registration": Path(
            "docs/benchmark/holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/"
            "holo_target_batches/wave3_holo_target_batch_001/WAVE3_HOLO_TARGET_BATCH_001_REGISTRATION_2026_07_01.json"
        ),
    },
    {
        "wave": "wave4",
        "batch": "001",
        "run_dir": Path(
            "docs/benchmark/holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/"
            "holo_target_batches/wave4_holo_target_batch_001/live_runs/run_20260701T163526Z"
        ),
        "registration": Path(
            "docs/benchmark/holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/"
            "holo_target_batches/wave4_holo_target_batch_001/WAVE4_HOLO_TARGET_BATCH_001_REGISTRATION_2026_07_01.json"
        ),
    },
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def read_trace(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical_hash(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    rendered = json.dumps(body, indent=2, sort_keys=True) + "\n"
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def ratio(num: int | float, den: int | float) -> float:
    return round(num / den, 6) if den else 0.0


def zero_failure_upper_95(n: int) -> float:
    return round((1 - math.pow(0.05, 1 / n)) * 100, 6) if n else 0.0


def rule_of_three(n: int) -> float:
    return round((3 / n) * 100, 6) if n else 0.0


def leakage_path(run_dir: Path, batch_id: str) -> Path:
    return run_dir / f"{batch_id}_NO_LEAKAGE_AUDIT.json"


def expected_by_packet(results: dict[str, Any]) -> dict[str, dict[str, Any]]:
    expected: dict[str, dict[str, Any]] = {}
    for row in results.get("benchmark_inventory", []):
        expected[row["target_packet_id"]] = {
            "expected": row["target_expected"],
            "final_correct": row["target_final_correct"],
            "final_verdict": row["target_final_verdict"],
            "pair_id": row["pair_id"],
            "side": "target",
        }
        expected[row["guardrail_packet_id"]] = {
            "expected": row["guardrail_expected"],
            "final_correct": row["guardrail_final_correct"],
            "final_verdict": row["guardrail_final_verdict"],
            "pair_id": row["pair_id"],
            "side": "guardrail",
        }
    return expected


def packet_results_by_id(results: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["packet_id"]: row for row in results.get("packet_results", [])}


def trace_token_split(trace: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    split = {
        "worker": {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        "gov": {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
    }
    for row in trace:
        kind = "gov" if row.get("call_kind") == "gov" else "worker"
        split[kind]["calls"] += 1
        split[kind]["input_tokens"] += int(row.get("input_tokens") or 0)
        split[kind]["output_tokens"] += int(row.get("output_tokens") or 0)
        split[kind]["total_tokens"] += int(row.get("total_tokens") or 0)
    return split


def worker_miss_rows(spec: dict[str, Any], results: dict[str, Any], trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expected = expected_by_packet(results)
    packet_results = packet_results_by_id(results)
    rows = []
    for row in trace:
        if row.get("call_kind") != "worker":
            continue
        reasons = []
        if row.get("provider_call_ok") is False:
            reasons.append("provider_fail")
        if row.get("parse_ok") is False:
            reasons.append("parse_fail")
        if row.get("admissible") is False:
            reasons.append("inadmissible")
        if row.get("local_verdict_matches_packet_truth") is False:
            reasons.append("truth_mismatch")
        if not reasons:
            continue
        packet_id = row.get("packet_id")
        final = packet_results.get(packet_id, {})
        truth = expected.get(packet_id, {})
        selector = final.get("final_selector") or {}
        rows.append(
            {
                "wave": spec["wave"],
                "batch": spec["batch"],
                "turn_id": row.get("turn_id"),
                "packet_id": packet_id,
                "pair_id": row.get("pair_id"),
                "model": row.get("model"),
                "worker_index": row.get("worker_index"),
                "reasons": reasons,
                "local_verdict": row.get("local_verdict"),
                "expected_verdict": truth.get("expected"),
                "final_verdict": final.get("final_verdict"),
                "final_admissible": bool(final.get("final_admissible")),
                "final_correct": bool(truth.get("final_correct")),
                "corrected_by_final_architecture": bool(final.get("final_admissible")) and bool(truth.get("final_correct")),
                "gate_failures": row.get("deterministic_failures")
                or (row.get("gate_result") or {}).get("failures")
                or [],
                "final_selector_reason": selector.get("selection_reason"),
                "selected_artifact_id": selector.get("selected_artifact_id"),
            }
        )
    return rows


def registration_lookup(path: Path | None) -> dict[str, dict[str, Any]]:
    if not path:
        return {}
    data = read_json(path)
    by_pair: dict[str, dict[str, Any]] = {}
    for row in data.get("selected_records", []):
        item = by_pair.setdefault(
            row["pair_id"],
            {
                "domain": row.get("domain"),
                "family_id": row.get("family_id"),
                "target_bucket": row.get("target_bucket"),
                "triage_class": row.get("triage_class"),
                "solo_not_knew_total": 0,
                "solo_wrong_verdict_total": 0,
                "solo_parse_or_provider_fail_total": 0,
            },
        )
        item["solo_not_knew_total"] += int(row.get("not_knew_count") or 0)
        item["solo_wrong_verdict_total"] += int(row.get("wrong_verdict_count") or 0)
        item["solo_parse_or_provider_fail_total"] += int(row.get("parse_or_provider_fail_count") or 0)
    return by_pair


def pair_rows_for_run(spec: dict[str, Any], results: dict[str, Any]) -> list[dict[str, Any]]:
    registration = registration_lookup(spec.get("registration"))
    rows = []
    for row in results.get("benchmark_inventory", []):
        meta = registration.get(row["pair_id"], {})
        rows.append(
            {
                "wave": spec["wave"],
                "batch": spec["batch"],
                "domain": meta.get("domain"),
                "family_id": meta.get("family_id"),
                "pair_id": row["pair_id"],
                "target_bucket": row.get("benchmark_bucket"),
                "triage_class": meta.get("triage_class"),
                "evidence_class": "HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE",
                "holo_pair_valid": bool(row.get("pair_valid")),
                "holo_target": {
                    "packet_id": row.get("target_packet_id"),
                    "expected": row.get("target_expected"),
                    "final_verdict": row.get("target_final_verdict"),
                    "final_correct": row.get("target_final_correct"),
                },
                "holo_guardrail": {
                    "packet_id": row.get("guardrail_packet_id"),
                    "expected": row.get("guardrail_expected"),
                    "final_verdict": row.get("guardrail_final_verdict"),
                    "final_correct": row.get("guardrail_final_correct"),
                },
                "solo": {
                    "comparison_scope": "triage_source_only_not_matched_live_baseline",
                    "not_knew_total_from_selection": meta.get("solo_not_knew_total"),
                    "wrong_verdict_total_from_selection": meta.get("solo_wrong_verdict_total"),
                    "parse_or_provider_fail_total_from_selection": meta.get("solo_parse_or_provider_fail_total"),
                },
            }
        )
    return rows


def wave2_pair_rows(wave2_final: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in wave2_final.get("pair_rows", []):
        item = dict(row)
        item["wave"] = "wave2"
        item.setdefault("holo_pair_valid", True)
        rows.append(item)
    return rows


def batch_summary(spec: dict[str, Any]) -> dict[str, Any]:
    run_dir = spec["run_dir"]
    results = read_json(run_dir / "live_results.json")
    trace = read_trace(run_dir / "TRACE_CALLS.jsonl")
    lock = read_json(run_dir / "LOCK_VALIDATION.json")
    leakage = read_json(leakage_path(run_dir, results["batch_id"]))
    split = trace_token_split(trace)
    misses = worker_miss_rows(spec, results, trace)
    packet_results = results.get("packet_results", [])
    final_selector_present = sum(1 for row in packet_results if row.get("final_selector"))
    corrected_misses = [row for row in misses if row["corrected_by_final_architecture"]]
    uncorrected_misses = [row for row in misses if not row["corrected_by_final_architecture"]]
    return {
        "batch_id": results["batch_id"],
        "batch": spec["batch"],
        "classification": results.get("classification"),
        "expected_provider_calls": results.get("expected_provider_calls"),
        "freeze_root_hash": results.get("freeze_root_hash"),
        "gov_calls": results.get("gov_calls"),
        "gov_tokens": split["gov"],
        "holo_worker_misses_corrected": len(corrected_misses),
        "holo_worker_misses_uncorrected": len(uncorrected_misses),
        "input_tokens": (results.get("totals") or {}).get("input_tokens"),
        "invalid_reason": results.get("invalidation_reason"),
        "judge_calls": results.get("judge_calls"),
        "lock_root_signature": lock.get("root_signature"),
        "lock_validation_status": lock.get("validation_status"),
        "no_leakage_prompt_files_scanned": leakage.get("prompt_files_scanned"),
        "no_leakage_status": leakage.get("status"),
        "output_tokens": (results.get("totals") or {}).get("output_tokens"),
        "packet_count": results.get("packet_count"),
        "packets_correct_admissible": results.get("packet_correct"),
        "provider_calls": results.get("provider_calls"),
        "provider_failures": len(results.get("provider_failures") or []),
        "readiness_assertions": results.get("readiness_assertions"),
        "readiness_passed": results.get("readiness_passed"),
        "root_failure": results.get("root_failure"),
        "run_dir": str(run_dir),
        "terminal_failures": len(results.get("terminal_failures") or []),
        "total_tokens": (results.get("totals") or {}).get("total_tokens"),
        "trace_hash": results.get("trace_hash"),
        "valid_pairs": results.get("valid_pairs"),
        "wave": spec["wave"],
        "worker_calls": results.get("worker_calls"),
        "worker_tokens": split["worker"],
        "final_selector_packets": final_selector_present,
        "final_selector_expected_packets": len(packet_results),
    }


def count_expected_verdicts(pair_rows: list[dict[str, Any]]) -> Counter:
    counts: Counter = Counter()
    for row in pair_rows:
        counts[row["holo_target"]["expected"]] += 1
        counts[row["holo_guardrail"]["expected"]] += 1
    return counts


def count_errors(pair_rows: list[dict[str, Any]]) -> dict[str, int]:
    false_positives = 0
    false_negatives = 0
    wrong = 0
    for row in pair_rows:
        for key in ("holo_target", "holo_guardrail"):
            expected = row[key]["expected"]
            actual = row[key]["final_verdict"]
            if expected == actual:
                continue
            wrong += 1
            if expected == "ALLOW" and actual == "ESCALATE":
                false_positives += 1
            if expected == "ESCALATE" and actual == "ALLOW":
                false_negatives += 1
    return {
        "false_negatives": false_negatives,
        "false_positives": false_positives,
        "wrong_verdicts": wrong,
    }


def family_counts(pair_rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    families: dict[str, dict[str, int]] = defaultdict(lambda: {"pairs": 0, "packets": 0, "correct_packets": 0})
    for row in pair_rows:
        family = row.get("family_id") or "UNKNOWN"
        families[family]["pairs"] += 1
        families[family]["packets"] += 2
        families[family]["correct_packets"] += int(bool(row["holo_target"]["final_correct"]))
        families[family]["correct_packets"] += int(bool(row["holo_guardrail"]["final_correct"]))
    return dict(sorted(families.items()))


def build_package() -> dict[str, Any]:
    wave2_final = read_json(WAVE2_FINAL_JSON)
    pair_rows = wave2_pair_rows(wave2_final)
    batch_summaries = []
    worker_misses = []

    for spec in RUN_SPECS:
        results = read_json(spec["run_dir"] / "live_results.json")
        trace = read_trace(spec["run_dir"] / "TRACE_CALLS.jsonl")
        batch_summaries.append(batch_summary(spec))
        worker_misses.extend(worker_miss_rows(spec, results, trace))
        if spec["wave"] in ("wave3", "wave4"):
            pair_rows.extend(pair_rows_for_run(spec, results))

    expected_counts = count_expected_verdicts(pair_rows)
    errors = count_errors(pair_rows)
    corrected = [row for row in worker_misses if row["corrected_by_final_architecture"]]
    uncorrected = [row for row in worker_misses if not row["corrected_by_final_architecture"]]
    total_tokens = sum(int(row.get("total_tokens") or 0) for row in batch_summaries)
    gov_tokens = sum(int(row["gov_tokens"].get("total_tokens") or 0) for row in batch_summaries)
    worker_tokens = sum(int(row["worker_tokens"].get("total_tokens") or 0) for row in batch_summaries)

    metrics = {
        "allow_denominator": expected_counts.get("ALLOW", 0),
        "esc_denominator": expected_counts.get("ESCALATE", 0),
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
        "gov_calls": sum(int(row.get("gov_calls") or 0) for row in batch_summaries),
        "gov_share_of_holo_tokens": ratio(gov_tokens, total_tokens),
        "holo_gov_tokens": gov_tokens,
        "holo_input_tokens": sum(int(row.get("input_tokens") or 0) for row in batch_summaries),
        "holo_output_tokens": sum(int(row.get("output_tokens") or 0) for row in batch_summaries),
        "holo_packets": sum(int(row.get("packet_count") or 0) for row in batch_summaries),
        "holo_packets_correct_admissible": sum(int(row.get("packets_correct_admissible") or 0) for row in batch_summaries),
        "holo_pairs": sum(int(row.get("valid_pairs") or 0) for row in batch_summaries),
        "holo_provider_calls": sum(int(row.get("provider_calls") or 0) for row in batch_summaries),
        "holo_provider_failures": sum(int(row.get("provider_failures") or 0) for row in batch_summaries),
        "holo_total_tokens": total_tokens,
        "holo_valid_pairs": sum(int(row.get("valid_pairs") or 0) for row in batch_summaries),
        "holo_worker_tokens": worker_tokens,
        "judge_calls": sum(int(row.get("judge_calls") or 0) for row in batch_summaries),
        "no_leakage_prompt_files_scanned": sum(int(row.get("no_leakage_prompt_files_scanned") or 0) for row in batch_summaries),
        "packet_error_observed": ratio(errors["wrong_verdicts"], len(pair_rows) * 2),
        "packet_error_upper_95_exact_percent": zero_failure_upper_95(len(pair_rows) * 2)
        if errors["wrong_verdicts"] == 0
        else None,
        "packet_error_upper_95_rule_of_three_percent": rule_of_three(len(pair_rows) * 2)
        if errors["wrong_verdicts"] == 0
        else None,
        "waves": ["wave2", "wave3", "wave4"],
        "worker_calls": sum(int(row.get("worker_calls") or 0) for row in batch_summaries),
        "worker_misses_corrected": len(corrected),
        "worker_misses_uncorrected": len(uncorrected),
        "wrong_verdicts": errors["wrong_verdicts"],
    }

    package = {
        "batch_summaries": batch_summaries,
        "claim_boundaries": [
            "This package combines already-frozen Holo live runs for Wave2, Wave3, and Wave4.",
            "Wave2 includes a selected-target solo comparison layer for Wave2 Batch001-004 only; Wave2 Batch005 and Wave3/Wave4 are Holo completion evidence without matched live solo baselines.",
            "Do not describe Wave3/Wave4 as solo-collapse proof until matched solo baselines are run against those exact packets.",
            "Internal Holo worker misses are reported separately from external solo failures.",
            "No judges are included in this package.",
            "No provider calls were made to create this combined memo.",
        ],
        "classification": "HOLOVERIFY_WAVE2_WAVE3_WAVE4_COMBINED_EVIDENCE_MEMO_NO_PROVIDER",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "family_counts": family_counts(pair_rows),
        "metrics": metrics,
        "next_live_work_recommendation": {
            "recommended": "RUN_MATCHED_SOLO_BASELINES_FOR_WAVE3_WAVE4_AND_WAVE2_BATCH005_BEFORE_PUBLIC_COMPARATIVE_CLAIMS",
            "reason": "The Holo completion layer is now strong; the next proof gap is matched control evidence for the newly proven Holo target packets.",
            "defer": [
                "MORE_HOLO_BATCHES_UNTIL_THIS_COMPARISON_LAYER_IS_CLOSED",
                "PUBLIC_SAFE_BENCHMARK_OR_WHITEPAPER_UPDATE_UNTIL_MATCHED_SOLO_GAPS_ARE_LABELED",
            ],
        },
        "no_judge_calls_for_this_package": True,
        "no_provider_calls_for_this_package": True,
        "package_sha256": "",
        "pair_rows": pair_rows,
        "source_paths": {
            "builder": "docs/benchmark/build_wave2_wave3_wave4_combined_evidence_2026_07_01.py",
            "wave2_final_memo_json": str(WAVE2_FINAL_JSON),
            "run_dirs": [str(spec["run_dir"]) for spec in RUN_SPECS],
        },
        "validation": {
            "all_lock_validations_pass": all(row.get("lock_validation_status") == "PASS" for row in batch_summaries),
            "all_no_leakage_pass": all(row.get("no_leakage_status") == "PASS" for row in batch_summaries),
            "all_readiness_pass": all(row.get("readiness_passed") is True for row in batch_summaries),
            "all_readiness_assertions_pass": all(
                all(value == "PASS" for value in (row.get("readiness_assertions") or {}).values())
                for row in batch_summaries
            ),
            "all_trace_counts_match_expected_calls": all(
                len(read_trace(Path(row["run_dir"]) / "TRACE_CALLS.jsonl")) == int(row["provider_calls"])
                for row in batch_summaries
            ),
            "provider_failures_zero": metrics["holo_provider_failures"] == 0,
            "judge_calls_zero": metrics["judge_calls"] == 0,
            "uncorrected_worker_misses_zero": len(uncorrected) == 0,
        },
        "worker_miss_correction_rows": corrected,
        "worker_miss_uncorrected_rows": uncorrected,
    }
    package["package_sha256"] = canonical_hash(package)
    return package


def render_md(data: dict[str, Any]) -> str:
    m = data["metrics"]
    lines = [
        "# HoloVerify Wave2-Wave4 Combined Evidence Memo",
        "",
        f"Classification: `{data['classification']}`",
        f"Package SHA-256: `{data['package_sha256']}`",
        "",
        "## Combined Result",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Waves | `{', '.join(m['waves'])}` |",
        f"| Holo packets | `{m['holo_packets']}` |",
        f"| Holo packets correct/admissible | `{m['holo_packets_correct_admissible']}` |",
        f"| Holo valid sibling pairs | `{m['holo_valid_pairs']}` |",
        f"| False positives | `{m['false_positives']}/{m['allow_denominator']}` |",
        f"| False negatives | `{m['false_negatives']}/{m['esc_denominator']}` |",
        f"| Provider calls | `{m['holo_provider_calls']}` |",
        f"| Worker calls | `{m['worker_calls']}` |",
        f"| Gov calls | `{m['gov_calls']}` |",
        f"| Judge calls | `{m['judge_calls']}` |",
        f"| Provider failures | `{m['holo_provider_failures']}` |",
        f"| Holo input tokens | `{m['holo_input_tokens']}` |",
        f"| Holo output tokens | `{m['holo_output_tokens']}` |",
        f"| Holo total tokens | `{m['holo_total_tokens']}` |",
        f"| Gov token share | `{m['gov_share_of_holo_tokens']}` |",
        f"| Prompt files scanned for leakage | `{m['no_leakage_prompt_files_scanned']}` |",
        f"| Intermediate worker misses corrected | `{m['worker_misses_corrected']}` |",
        f"| Intermediate worker misses uncorrected | `{m['worker_misses_uncorrected']}` |",
        f"| Packet error upper 95%, exact | `{m['packet_error_upper_95_exact_percent']}%` |",
        f"| Packet error upper 95%, rule of three | `{m['packet_error_upper_95_rule_of_three_percent']}%` |",
        "",
        "## Batch Rollup",
        "",
        "| Wave | Batch | Classification | Packets | Valid pairs | Calls | Worker/Gov | Tokens | No leakage | Worker misses corrected |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for row in data["batch_summaries"]:
        lines.append(
            f"| `{row['wave']}` | `{row['batch']}` | `{row['classification']}` | "
            f"`{row['packets_correct_admissible']}/{row['packet_count']}` | `{row['valid_pairs']}` | "
            f"`{row['provider_calls']}` | `{row['worker_calls']}/{row['gov_calls']}` | "
            f"`{row['total_tokens']}` | `{row['no_leakage_status']}` | `{row['holo_worker_misses_corrected']}` |"
        )
    lines.extend(
        [
            "",
            "## Correction Trail",
            "",
            "These are intra-Holo worker misses, not final Holo failures and not external solo failures.",
            "",
            "| Wave | Batch | Turn | Packet | Model | Reasons | Expected | Local | Final | Selector reason |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in data["worker_miss_correction_rows"]:
        lines.append(
            f"| `{row['wave']}` | `{row['batch']}` | `{row['turn_id']}` | `{row['packet_id']}` | "
            f"`{row['model']}` | `{','.join(row['reasons'])}` | `{row['expected_verdict']}` | "
            f"`{row['local_verdict']}` | `{row['final_verdict']}` | `{row['final_selector_reason']}` |"
        )
    lines.extend(
        [
            "",
            "## Family Breakdown",
            "",
            "| Family | Pairs | Packets | Correct/admissible packets |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for family_id, counts in data["family_counts"].items():
        lines.append(
            f"| `{family_id}` | `{counts['pairs']}` | `{counts['packets']}` | `{counts['correct_packets']}` |"
        )
    lines.extend(
        [
            "",
            "## Pair Rows",
            "",
            "| Wave | Batch | Family | Pair | Bucket | Evidence class | Target | Guardrail |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in data["pair_rows"]:
        lines.append(
            f"| `{row['wave']}` | `{row['batch']}` | `{row.get('family_id')}` | `{row['pair_id']}` | "
            f"`{row['target_bucket']}` | `{row['evidence_class']}` | "
            f"`{row['holo_target']['expected']}->{row['holo_target']['final_verdict']}` | "
            f"`{row['holo_guardrail']['expected']}->{row['holo_guardrail']['final_verdict']}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundaries",
            "",
        ]
    )
    for boundary in data["claim_boundaries"]:
        lines.append(f"- {boundary}")
    recommendation = data["next_live_work_recommendation"]
    lines.extend(
        [
            "",
            "## Next Live Work Recommendation",
            "",
            f"Recommended: `{recommendation['recommended']}`",
            "",
            recommendation["reason"],
            "",
            "Deferred until labels are clean:",
        ]
    )
    for item in recommendation["defer"]:
        lines.append(f"- `{item}`")
    lines.append("")
    return "\n".join(lines)


def validate_package(data: dict[str, Any]) -> None:
    checks = data["validation"]
    failed = [key for key, value in checks.items() if value is not True]
    if failed:
        raise RuntimeError(f"combined_evidence_validation_failed:{failed}")
    metrics = data["metrics"]
    assert metrics["holo_packets"] == metrics["holo_packets_correct_admissible"]
    assert metrics["holo_pairs"] == metrics["holo_valid_pairs"]
    assert metrics["holo_provider_calls"] == metrics["worker_calls"] + metrics["gov_calls"]
    assert metrics["judge_calls"] == 0
    assert metrics["holo_provider_failures"] == 0
    assert metrics["worker_misses_uncorrected"] == 0


def main() -> int:
    data = build_package()
    validate_package(data)
    OUT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(render_md(data))
    print(
        json.dumps(
            {
                "json": str(OUT_JSON),
                "md": str(OUT_MD),
                "package_sha256": data["package_sha256"],
                "status": "PASS",
                "holo_packets": data["metrics"]["holo_packets"],
                "holo_valid_pairs": data["metrics"]["holo_valid_pairs"],
                "provider_calls": data["metrics"]["holo_provider_calls"],
                "worker_misses_corrected": data["metrics"]["worker_misses_corrected"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
