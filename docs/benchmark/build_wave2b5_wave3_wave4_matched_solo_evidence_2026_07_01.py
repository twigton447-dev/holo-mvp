#!/usr/bin/env python3
"""Build matched solo-control evidence for Wave2 Batch005 plus Wave3/Wave4.

This is a no-provider evidence compiler. It extracts only the solo one-shot
rows that correspond to Holo target-batch packets already frozen on disk.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
OUT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE2B5_WAVE3_WAVE4_MATCHED_SOLO_EVIDENCE_2026_07_01.json"
OUT_MD = BENCHMARK_ROOT / "HOLOVERIFY_WAVE2B5_WAVE3_WAVE4_MATCHED_SOLO_EVIDENCE_2026_07_01.md"

MATCHED_SCOPES = [
    {
        "scope_id": "WAVE2_BATCH005",
        "description": "Wave2 target batch 005",
        "registration": BENCHMARK_ROOT
        / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
        / "holo_target_batches"
        / "wave2_holo_target_batch_005"
        / "WAVE2_HOLO_TARGET_BATCH_005_REGISTRATION_2026_07_01.json",
        "holo_results": BENCHMARK_ROOT
        / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
        / "holo_target_batches"
        / "wave2_holo_target_batch_005"
        / "live_runs"
        / "run_20260701T141727Z"
        / "live_results.json",
        "holo_trace": BENCHMARK_ROOT
        / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
        / "holo_target_batches"
        / "wave2_holo_target_batch_005"
        / "live_runs"
        / "run_20260701T141727Z"
        / "TRACE_CALLS.jsonl",
        "solo_traces": [
            BENCHMARK_ROOT
            / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
            / "solo_triage_3mini"
            / "wave2_workforce_solo_triage_clean_001"
            / "run_20260701T022623Z"
            / "SOLO_TRIAGE_TRACE.jsonl",
            BENCHMARK_ROOT
            / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
            / "solo_triage_3mini"
            / "wave2_data_privacy_solo_triage_clean_001"
            / "run_20260701T024118Z"
            / "SOLO_TRIAGE_TRACE.jsonl",
            BENCHMARK_ROOT
            / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
            / "solo_triage_3mini"
            / "wave2_finance_close_solo_triage_clean_001"
            / "run_20260701T030250Z"
            / "SOLO_TRIAGE_TRACE.jsonl",
        ],
    },
    {
        "scope_id": "WAVE3_BATCH001",
        "description": "Wave3 target batch 001",
        "registration": BENCHMARK_ROOT
        / "holoverify_replication_packet_freeze_wave3_wave4_2026-07-01"
        / "holo_target_batches"
        / "wave3_holo_target_batch_001"
        / "WAVE3_HOLO_TARGET_BATCH_001_REGISTRATION_2026_07_01.json",
        "holo_results": BENCHMARK_ROOT
        / "holoverify_replication_packet_freeze_wave3_wave4_2026-07-01"
        / "holo_target_batches"
        / "wave3_holo_target_batch_001"
        / "live_runs"
        / "run_20260701T163353Z"
        / "live_results.json",
        "holo_trace": BENCHMARK_ROOT
        / "holoverify_replication_packet_freeze_wave3_wave4_2026-07-01"
        / "holo_target_batches"
        / "wave3_holo_target_batch_001"
        / "live_runs"
        / "run_20260701T163353Z"
        / "TRACE_CALLS.jsonl",
        "solo_traces": [
            BENCHMARK_ROOT
            / "holoverify_replication_packet_freeze_wave3_wave4_2026-07-01"
            / "solo_triage_3mini"
            / "wave3_solo_triage"
            / "run_20260701T133544Z"
            / "SOLO_TRIAGE_TRACE.jsonl"
        ],
    },
    {
        "scope_id": "WAVE4_BATCH001",
        "description": "Wave4 target batch 001",
        "registration": BENCHMARK_ROOT
        / "holoverify_replication_packet_freeze_wave3_wave4_2026-07-01"
        / "holo_target_batches"
        / "wave4_holo_target_batch_001"
        / "WAVE4_HOLO_TARGET_BATCH_001_REGISTRATION_2026_07_01.json",
        "holo_results": BENCHMARK_ROOT
        / "holoverify_replication_packet_freeze_wave3_wave4_2026-07-01"
        / "holo_target_batches"
        / "wave4_holo_target_batch_001"
        / "live_runs"
        / "run_20260701T163526Z"
        / "live_results.json",
        "holo_trace": BENCHMARK_ROOT
        / "holoverify_replication_packet_freeze_wave3_wave4_2026-07-01"
        / "holo_target_batches"
        / "wave4_holo_target_batch_001"
        / "live_runs"
        / "run_20260701T163526Z"
        / "TRACE_CALLS.jsonl",
        "solo_traces": [
            BENCHMARK_ROOT
            / "holoverify_replication_packet_freeze_wave3_wave4_2026-07-01"
            / "solo_triage_3mini"
            / "wave4_solo_triage"
            / "run_20260701T151059Z"
            / "SOLO_TRIAGE_TRACE.jsonl"
        ],
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def rel(path: Path) -> str:
    return str(path.relative_to(BENCHMARK_ROOT))


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise RuntimeError(reason)


def sanitized_solo_row(row: dict[str, Any]) -> dict[str, Any]:
    gate = row.get("gate_result") or {}
    return {
        "packet_id": row.get("packet_id"),
        "pair_id": row.get("pair_id"),
        "family_id": row.get("family_id"),
        "domain": row.get("domain"),
        "sibling_id": row.get("sibling_id"),
        "target_bucket": row.get("target_bucket"),
        "target_sibling": row.get("target_sibling"),
        "packet_truth": row.get("packet_truth_for_local_audit_only"),
        "model_key": row.get("model_key"),
        "provider": row.get("provider"),
        "model": row.get("model"),
        "dna": row.get("dna"),
        "provider_call_ok": row.get("provider_call_ok"),
        "parse_ok": row.get("parse_ok"),
        "local_verdict": row.get("local_verdict"),
        "verdict_correct": row.get("local_verdict_matches_packet_truth"),
        "admissible": row.get("admissible"),
        "solo_label": row.get("solo_label"),
        "gate_failures": gate.get("failures") or [],
        "input_tokens": row.get("input_tokens") or 0,
        "output_tokens": row.get("output_tokens") or 0,
        "total_tokens": row.get("total_tokens") or 0,
        "prompt_hash_matches_freeze": row.get("prompt_hash_matches_freeze"),
        "prompt_leakage_hits": row.get("prompt_leakage_hits") or [],
        "gov_context_in_prompt": row.get("gov_context_in_prompt"),
        "holo_state_in_prompt": row.get("holo_state_in_prompt"),
        "artifact_registry_in_prompt": row.get("artifact_registry_in_prompt"),
        "judge_calls": row.get("judge_calls"),
        "source_trace_call_index": row.get("call_index"),
    }


def packet_truth_by_id(records: list[dict[str, Any]]) -> dict[str, str]:
    return {row["packet_id"]: row["packet_truth"] for row in records}


def pair_class(rows: list[dict[str, Any]]) -> str:
    if len(rows) != 6:
        return "INVALID_PAIR_TRACE"
    labels = [row.get("solo_label") for row in rows]
    not_knew = sum(label != "KNEW" for label in labels)
    wrong = sum(label == "WRONG_VERDICT" for label in labels)
    if not_knew == 6:
        return "ALL_SIX_SOLO_COLLAPSE"
    if not_knew >= 4 or wrong >= 3:
        return "STRONG_SOLO_COLLAPSE"
    if not_knew:
        return "MIXED_SEAM"
    return "NO_SOLO_SEAM"


def compare_scope(scope: dict[str, Any]) -> dict[str, Any]:
    registration = read_json(scope["registration"])
    holo = read_json(scope["holo_results"])
    selected_records = registration["selected_records"]
    selected_packet_ids = {row["packet_id"] for row in selected_records}
    selected_pair_ids = {row["pair_id"] for row in selected_records}
    truth_by_packet = packet_truth_by_id(selected_records)

    require(holo.get("readiness_passed") is True, f"holo_readiness_not_passed:{scope['scope_id']}")
    require(holo.get("judge_calls") == 0, f"holo_judges_present:{scope['scope_id']}")
    require(not holo.get("provider_failures"), f"holo_provider_failures:{scope['scope_id']}")
    require(holo.get("packet_count") == len(selected_packet_ids), f"holo_packet_count_mismatch:{scope['scope_id']}")
    require(holo.get("packet_correct") == len(selected_packet_ids), f"holo_packet_correct_mismatch:{scope['scope_id']}")
    require(holo.get("valid_pairs") == len(selected_pair_ids), f"holo_pair_count_mismatch:{scope['scope_id']}")
    require((holo.get("no_leakage_audit") or {}).get("status") == "PASS", f"holo_leakage_not_pass:{scope['scope_id']}")
    require(sha256_file(scope["holo_trace"]) == holo.get("trace_hash"), f"holo_trace_hash_mismatch:{scope['scope_id']}")

    holo_packet_results = {row["packet_id"]: row for row in holo["packet_results"]}
    require(selected_packet_ids == set(holo_packet_results), f"holo_packet_set_mismatch:{scope['scope_id']}")

    solo_source_refs = []
    solo_rows_all: list[dict[str, Any]] = []
    for trace in scope["solo_traces"]:
        rows = read_jsonl(trace)
        solo_rows_all.extend(rows)
        solo_source_refs.append(
            {
                "trace_ref": rel(trace),
                "trace_sha256": sha256_file(trace),
                "rows": len(rows),
                "unique_packets": len({row.get("packet_id") for row in rows}),
            }
        )
    solo_rows = [row for row in solo_rows_all if row.get("packet_id") in selected_packet_ids]
    by_packet: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in solo_rows:
        by_packet[row["packet_id"]].append(row)

    missing = sorted(selected_packet_ids - set(by_packet))
    require(not missing, f"solo_missing_packets:{scope['scope_id']}:{missing[:5]}")
    for packet_id, rows in by_packet.items():
        require(len(rows) == 3, f"solo_packet_call_count_mismatch:{scope['scope_id']}:{packet_id}:{len(rows)}")
        require({row["model_key"] for row in rows} == {"xai", "openai_weak", "minimax"}, f"solo_model_set_mismatch:{packet_id}")
        for row in rows:
            require(row.get("provider_call_ok") is True, f"solo_provider_failure:{packet_id}:{row.get('model')}")
            require(row.get("prompt_hash_matches_freeze") is True, f"solo_prompt_hash_mismatch:{packet_id}")
            require(not row.get("prompt_leakage_hits"), f"solo_prompt_leakage:{packet_id}")
            require(row.get("gov_context_in_prompt") is False, f"solo_gov_context_leak:{packet_id}")
            require(row.get("holo_state_in_prompt") is False, f"solo_state_leak:{packet_id}")
            require(row.get("artifact_registry_in_prompt") is False, f"solo_artifact_registry_leak:{packet_id}")
            require(row.get("judge_calls") == 0, f"solo_judge_call:{packet_id}")
            require(row.get("packet_truth_for_local_audit_only") == truth_by_packet[packet_id], f"solo_truth_mismatch:{packet_id}")

    comparison_rows = []
    for record in sorted(selected_records, key=lambda row: (row["family_id"], row["pair_id"], row["sibling_id"])):
        packet_id = record["packet_id"]
        holo_packet = holo_packet_results[packet_id]
        solo_outcomes = [sanitized_solo_row(row) for row in sorted(by_packet[packet_id], key=lambda item: item["model_key"])]
        comparison_rows.append(
            {
                "scope_id": scope["scope_id"],
                "family_id": record["family_id"],
                "domain": record["domain"],
                "pair_id": record["pair_id"],
                "packet_id": packet_id,
                "sibling_id": record["sibling_id"],
                "target_bucket": record["target_bucket"],
                "target_sibling": record["target_sibling"],
                "packet_truth": record["packet_truth"],
                "packet_sha256": record["packet_sha256"],
                "prompt_sha256": record["prompt_sha256"],
                "holo_final_verdict": holo_packet["final_verdict"],
                "holo_final_admissible": holo_packet["final_admissible"],
                "holo_final_correct": holo_packet["final_verdict"] == record["packet_truth"],
                "holo_final_selector": holo_packet.get("final_selector"),
                "holo_intra_single_dna_miss_count": len(holo_packet.get("intra_holo_single_dna_miss_evidence") or []),
                "holo_valid_rescue_evidence_present": holo_packet.get("valid_rescue_evidence_present"),
                "solo_outcomes": solo_outcomes,
                "solo_not_knew_count": sum(row["solo_label"] != "KNEW" for row in solo_outcomes),
                "solo_wrong_verdict_count": sum(row["solo_label"] == "WRONG_VERDICT" for row in solo_outcomes),
                "solo_parse_fail_count": sum(row["solo_label"] == "PARSE_FAIL" for row in solo_outcomes),
                "solo_structural_or_evidence_fail_count": sum(row["solo_label"] == "STRUCTURAL_OR_EVIDENCE_FAIL" for row in solo_outcomes),
                "solo_any_failure": any(row["solo_label"] != "KNEW" for row in solo_outcomes),
                "solo_all_three_failed": all(row["solo_label"] != "KNEW" for row in solo_outcomes),
            }
        )

    pair_rows = []
    grouped_packets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in comparison_rows:
        grouped_packets[row["pair_id"]].append(row)
    for pair_id, packets in sorted(grouped_packets.items()):
        solo_pair_rows = [outcome for packet in packets for outcome in packet["solo_outcomes"]]
        pair_rows.append(
            {
                "scope_id": scope["scope_id"],
                "pair_id": pair_id,
                "family_id": packets[0]["family_id"],
                "domain": packets[0]["domain"],
                "target_bucket": packets[0]["target_bucket"],
                "packets": [packet["packet_id"] for packet in sorted(packets, key=lambda item: item["sibling_id"])],
                "packet_truths": {packet["packet_id"]: packet["packet_truth"] for packet in packets},
                "holo_both_correct": all(packet["holo_final_correct"] for packet in packets),
                "holo_both_admissible": all(packet["holo_final_admissible"] for packet in packets),
                "solo_not_knew_count": sum(row.get("solo_label") != "KNEW" for row in solo_pair_rows),
                "solo_wrong_verdict_count": sum(row.get("solo_label") == "WRONG_VERDICT" for row in solo_pair_rows),
                "solo_parse_fail_count": sum(row.get("solo_label") == "PARSE_FAIL" for row in solo_pair_rows),
                "solo_pair_class": pair_class(solo_pair_rows),
            }
        )

    model_counter: dict[str, Counter[str]] = defaultdict(Counter)
    model_tokens: dict[str, Counter[str]] = defaultdict(Counter)
    for row in solo_rows:
        model = f"{row['provider']}/{row['model']}"
        model_counter[model][row["solo_label"]] += 1
        model_counter[model]["calls"] += 1
        if row.get("local_verdict_matches_packet_truth"):
            model_counter[model]["verdict_correct"] += 1
        if row.get("admissible"):
            model_counter[model]["admissible"] += 1
        for key in ("input_tokens", "output_tokens", "total_tokens"):
            model_tokens[model][key] += row.get(key) or 0

    solo_totals = Counter()
    for row in solo_rows:
        solo_totals["input_tokens"] += row.get("input_tokens") or 0
        solo_totals["output_tokens"] += row.get("output_tokens") or 0
        solo_totals["total_tokens"] += row.get("total_tokens") or 0

    labels = Counter(row["solo_label"] for row in solo_rows)
    pair_classes = Counter(row["solo_pair_class"] for row in pair_rows)
    return {
        "scope_id": scope["scope_id"],
        "description": scope["description"],
        "registration_ref": rel(scope["registration"]),
        "registration_sha256": sha256_file(scope["registration"]),
        "holo_results_ref": rel(scope["holo_results"]),
        "holo_results_sha256": sha256_file(scope["holo_results"]),
        "holo_trace_ref": rel(scope["holo_trace"]),
        "holo_trace_sha256": sha256_file(scope["holo_trace"]),
        "solo_source_traces": solo_source_refs,
        "freeze_root_hash": registration["freeze_root_hash"],
        "packet_count": len(selected_packet_ids),
        "pair_count": len(selected_pair_ids),
        "solo_provider_calls_matched": len(solo_rows),
        "holo_provider_calls": holo["provider_calls"],
        "holo_worker_calls": holo["worker_calls"],
        "holo_gov_calls": holo["gov_calls"],
        "judge_calls": 0,
        "holo_tokens": holo["totals"],
        "solo_tokens_matched": dict(solo_totals),
        "solo_label_counts": dict(labels),
        "solo_pair_class_counts": dict(pair_classes),
        "solo_by_model": {
            model: {**dict(model_counter[model]), "tokens": dict(model_tokens[model])}
            for model in sorted(model_counter)
        },
        "holo_packet_correct": holo["packet_correct"],
        "holo_valid_pairs": holo["valid_pairs"],
        "holo_no_leakage_status": (holo.get("no_leakage_audit") or {}).get("status"),
        "intermediate_holo_single_dna_misses": sum(row["holo_intra_single_dna_miss_count"] for row in comparison_rows),
        "comparison_rows": comparison_rows,
        "pair_rows": pair_rows,
        "assertions": {
            "holo_readiness_passed": "PASS",
            "holo_packet_identity_matches_registration": "PASS",
            "holo_all_selected_packets_correct": "PASS",
            "solo_all_selected_packets_covered": "PASS",
            "solo_three_models_per_packet": "PASS",
            "solo_no_gov_context": "PASS",
            "solo_no_holo_state": "PASS",
            "solo_no_artifact_registry": "PASS",
            "solo_no_judges": "PASS",
            "no_prompt_leakage": "PASS",
        },
    }


def build() -> dict[str, Any]:
    scopes = [compare_scope(scope) for scope in MATCHED_SCOPES]
    total_packets = sum(scope["packet_count"] for scope in scopes)
    total_pairs = sum(scope["pair_count"] for scope in scopes)
    total_solo_calls = sum(scope["solo_provider_calls_matched"] for scope in scopes)
    total_holo_calls = sum(scope["holo_provider_calls"] for scope in scopes)
    total_holo_tokens = Counter()
    total_solo_tokens = Counter()
    solo_label_counts = Counter()
    solo_pair_class_counts = Counter()
    model_counts: dict[str, Counter[str]] = defaultdict(Counter)
    model_tokens: dict[str, Counter[str]] = defaultdict(Counter)
    rows = []
    pair_rows = []
    for scope in scopes:
        total_holo_tokens.update(scope["holo_tokens"])
        total_solo_tokens.update(scope["solo_tokens_matched"])
        solo_label_counts.update(scope["solo_label_counts"])
        solo_pair_class_counts.update(scope["solo_pair_class_counts"])
        rows.extend(scope["comparison_rows"])
        pair_rows.extend(scope["pair_rows"])
        for model, stats in scope["solo_by_model"].items():
            for key, value in stats.items():
                if key == "tokens":
                    for token_key, token_value in value.items():
                        model_tokens[model][token_key] += token_value
                else:
                    model_counts[model][key] += value

    rootless = {
        "classification": "HOLOVERIFY_WAVE2B5_WAVE3_WAVE4_MATCHED_SOLO_EVIDENCE",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_boundary": (
            "Matched-control extraction over already completed solo traces. "
            "No new provider calls are made by this compiler."
        ),
        "scopes": scopes,
        "totals": {
            "packet_count": total_packets,
            "pair_count": total_pairs,
            "solo_provider_calls_matched": total_solo_calls,
            "holo_provider_calls": total_holo_calls,
            "holo_worker_calls": sum(scope["holo_worker_calls"] for scope in scopes),
            "holo_gov_calls": sum(scope["holo_gov_calls"] for scope in scopes),
            "judge_calls": 0,
            "holo_tokens": dict(total_holo_tokens),
            "solo_tokens_matched": dict(total_solo_tokens),
            "holo_to_solo_token_ratio": round(
                total_holo_tokens["total_tokens"] / total_solo_tokens["total_tokens"], 6
            )
            if total_solo_tokens["total_tokens"]
            else None,
            "solo_label_counts": dict(solo_label_counts),
            "solo_pair_class_counts": dict(solo_pair_class_counts),
            "holo_packet_correct": sum(scope["holo_packet_correct"] for scope in scopes),
            "holo_valid_pairs": sum(scope["holo_valid_pairs"] for scope in scopes),
            "intermediate_holo_single_dna_misses": sum(
                scope["intermediate_holo_single_dna_misses"] for scope in scopes
            ),
        },
        "solo_by_model": {
            model: {**dict(model_counts[model]), "tokens": dict(model_tokens[model])}
            for model in sorted(model_counts)
        },
        "pair_rows": pair_rows,
        "comparison_rows": rows,
        "assertions": {
            "matched_packets": "PASS" if total_packets == 100 else "FAIL",
            "matched_pairs": "PASS" if total_pairs == 50 else "FAIL",
            "matched_solo_calls": "PASS" if total_solo_calls == 300 else "FAIL",
            "holo_calls": "PASS" if total_holo_calls == 500 else "FAIL",
            "holo_packets_correct": "PASS" if sum(scope["holo_packet_correct"] for scope in scopes) == 100 else "FAIL",
            "holo_pairs_valid": "PASS" if sum(scope["holo_valid_pairs"] for scope in scopes) == 50 else "FAIL",
            "no_judges": "PASS",
            "no_new_provider_calls_by_compiler": "PASS",
            "external_solo_and_intra_holo_evidence_separated": "PASS",
        },
    }
    root_signature = sha256_text(canonical_json(rootless))
    return {**rootless, "root_signature": root_signature}


def render_md(report: dict[str, Any]) -> str:
    totals = report["totals"]
    lines = [
        "# HoloVerify Matched Solo Evidence: Wave2 Batch005 + Wave3/Wave4",
        "",
        f"Classification: `{report['classification']}`",
        f"Root signature: `{report['root_signature']}`",
        "",
        "This package extracts matched solo-control rows from already completed solo traces.",
        "It does not run providers, does not run Holo, and does not run judges.",
        "",
        "## Summary",
        "",
        f"- Holo packets: `{totals['holo_packet_correct']}` / `{totals['packet_count']}` correct.",
        f"- Holo pairs: `{totals['holo_valid_pairs']}` / `{totals['pair_count']}` valid.",
        f"- Matched solo calls: `{totals['solo_provider_calls_matched']}` across the same `{totals['packet_count']}` packets.",
        f"- Holo provider calls represented: `{totals['holo_provider_calls']}`.",
        f"- Judges: `{totals['judge_calls']}`.",
        f"- Holo tokens: `{totals['holo_tokens']['total_tokens']}` total.",
        f"- Matched solo tokens: `{totals['solo_tokens_matched']['total_tokens']}` total.",
        f"- Holo/solo token ratio: `{totals['holo_to_solo_token_ratio']}`.",
        f"- Intermediate Holo single-DNA misses corrected or absorbed by the architecture: `{totals['intermediate_holo_single_dna_misses']}`.",
        "",
        "## Solo Outcome Counts",
        "",
        "| Label | Count |",
        "| --- | ---: |",
    ]
    for label, count in sorted(totals["solo_label_counts"].items()):
        lines.append(f"| `{label}` | {count} |")
    lines.extend(
        [
            "",
            "## Pair Classes",
            "",
            "| Class | Pairs |",
            "| --- | ---: |",
        ]
    )
    for label, count in sorted(totals["solo_pair_class_counts"].items()):
        lines.append(f"| `{label}` | {count} |")
    lines.extend(
        [
            "",
            "## Model Totals",
            "",
            "| Model | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Structural/Evidence Fail | Verdict Correct | Tokens |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for model, stats in report["solo_by_model"].items():
        calls = stats.get("calls", 0)
        knew = stats.get("KNEW", 0)
        not_knew = calls - knew
        lines.append(
            f"| `{model}` | {calls} | {knew} | {not_knew} | {stats.get('WRONG_VERDICT', 0)} | "
            f"{stats.get('PARSE_FAIL', 0)} | {stats.get('STRUCTURAL_OR_EVIDENCE_FAIL', 0)} | "
            f"{stats.get('verdict_correct', 0)} | {stats['tokens'].get('total_tokens', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Scope Totals",
            "",
            "| Scope | Packets | Pairs | Holo Calls | Solo Calls | Holo Correct | Holo Valid Pairs | All-Six Collapse | Strong Collapse | Mixed | No Seam |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for scope in report["scopes"]:
        classes = scope["solo_pair_class_counts"]
        lines.append(
            f"| `{scope['scope_id']}` | {scope['packet_count']} | {scope['pair_count']} | "
            f"{scope['holo_provider_calls']} | {scope['solo_provider_calls_matched']} | "
            f"{scope['holo_packet_correct']} | {scope['holo_valid_pairs']} | "
            f"{classes.get('ALL_SIX_SOLO_COLLAPSE', 0)} | {classes.get('STRONG_SOLO_COLLAPSE', 0)} | "
            f"{classes.get('MIXED_SEAM', 0)} | {classes.get('NO_SOLO_SEAM', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Conservative Claim Boundary",
            "",
            "This proves matched-control evidence for these 100 already Holo-passed packets only.",
            "It does not claim universal model superiority, and it keeps external solo misses separate from intermediate Holo worker misses.",
            "",
            "## Assertions",
            "",
            "| Assertion | Status |",
            "| --- | --- |",
        ]
    )
    for key, value in report["assertions"].items():
        lines.append(f"| `{key}` | `{value}` |")
    return "\n".join(lines) + "\n"


def main() -> int:
    report = build()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(render_md(report))
    print(json.dumps({"status": "PASS", "json": rel(OUT_JSON), "md": rel(OUT_MD), "root_signature": report["root_signature"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
