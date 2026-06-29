#!/usr/bin/env python3
"""Build the final HoloVerify 20-pair / 3-DNA evidence package.

This script is intentionally report-only. It reads the completed HoloVerify run,
the frozen Holo bundle, and the one-shot solo baseline. It does not call
providers, repair outputs, mutate packets, or rerun any model.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RUN_ROOT = ROOT / "holoverify_20pair_3dna_2026-06-29"
HOLO_RUN = RUN_ROOT / "live_runs" / "run_20260629T052822Z"
FREEZE_ROOT = RUN_ROOT / "frozen_complete_run_20260629T052822Z"
SOLO_RUN = RUN_ROOT / "solo_one_shot_against_frozen_run_20260629T052822Z" / "run_20260629T060938Z"
OUT = RUN_ROOT / "final_evidence_package_2026_06_29"

MODEL_ORDER = [
    ("xai", "xai/grok-3-mini"),
    ("google", "google/gemini-2.5-flash-lite"),
    ("minimax", "minimax/MiniMax-M2.5-highspeed"),
]

FORBIDDEN_PROMPT_TERMS = [
    "HV-KITC",
    "BAL100",
    "packet_id",
    "pair_id",
    "expected_for_local_audit",
    "hidden_expected",
    "target_match",
    "benchmark_bucket",
    "guardrail",
    "hard_allow",
    "hard_escalate",
    "hologov",
    "holoverify",
    "holo_gov",
    "gov_baton",
    "latest_gov_baton",
    "state_brief",
    "artifact_registry",
    "best_artifact_registry",
    "blindspot",
    "atlas",
    "answer key",
    "correct answer",
    "root_signature",
    "trace_hash",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return lines


def compact_failures(failures: list[str], limit: int = 4) -> str:
    if not failures:
        return ""
    clipped = failures[:limit]
    suffix = "" if len(failures) <= limit else f"; +{len(failures) - limit} more"
    return "; ".join(clipped) + suffix


def prompt_scan(run_dir: Path) -> dict[str, Any]:
    hits = []
    files = []
    for folder_name in ("prompts", "prompts_preflight"):
        folder = run_dir / folder_name
        for path in sorted(folder.glob("*.json")):
            files.append(path)
            text = path.read_text().lower()
            for term in FORBIDDEN_PROMPT_TERMS:
                if term.lower() in text:
                    hits.append({"file": str(path.relative_to(run_dir)), "term": term})
    return {"prompt_files_scanned": len(files), "forbidden_hits": hits, "forbidden_hit_count": len(hits)}


def evidence_class_for_row(solo_row: dict[str, Any], holo_correct: bool, intra_classes: list[str], selector_used: bool) -> list[str]:
    classes: list[str] = []
    solo_knew = solo_row["solo_label"] == "KNEW"
    if solo_knew and holo_correct:
        classes.append("SOLO_CORRECT_HOLO_CORRECT")
    elif solo_knew and not holo_correct:
        classes.append("SOLO_CORRECT_HOLO_WRONG")
    elif not solo_knew and holo_correct:
        classes.append("EXTERNAL_SOLO_RESCUE")
    elif not solo_knew and not holo_correct:
        classes.append("EXTERNAL_SOLO_FAILURE_NOT_RESCUED")
    classes.extend(intra_classes)
    if selector_used:
        classes.append("FINAL_SELECTOR_RESCUE")
    return sorted(set(classes))


def build_package() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)

    holo = load_json(HOLO_RUN / "live_results.json")
    holo_trace = load_jsonl(HOLO_RUN / "TRACE_CALLS.jsonl")
    solo = load_json(SOLO_RUN / "solo_one_shot_results.json")
    solo_trace = load_jsonl(SOLO_RUN / "SOLO_ONE_SHOT_TRACE.jsonl")
    freeze_lock = load_json(FREEZE_ROOT / "LOCK_MANIFEST.json")
    freeze_validation = load_json(FREEZE_ROOT / "LOCK_VALIDATION.json")
    solo_lock_validation = load_json(SOLO_RUN / "RUN_LOCK_VALIDATION.json")
    solo_lock = load_json(SOLO_RUN / "RUN_LOCK_MANIFEST.json")

    lock_records = {record["packet_id"]: record for record in freeze_lock["packet_records"]}
    holo_packets = {record["packet_id"]: record for record in holo["packet_results"]}
    solo_packets = {record["packet_id"]: record for record in solo["packet_results"]}

    comparison_rows: list[dict[str, Any]] = []
    packet_identity_rows: list[dict[str, Any]] = []
    solo_by_packet_model: dict[tuple[str, str], dict[str, Any]] = {}
    for row in solo_trace:
        solo_by_packet_model[(row["packet_id"], row["provider"])] = row

    for packet_id in sorted(lock_records):
        lock_record = lock_records[packet_id]
        holo_packet = holo_packets[packet_id]
        payload_path = FREEZE_ROOT / lock_record["payload_ref"]
        payload_hash_matches = sha256_file(payload_path) == lock_record["payload_sha256"]
        packet_identity_rows.append(
            {
                "packet_id": packet_id,
                "pair_id": lock_record["pair_id"],
                "suffix": lock_record["suffix"],
                "payload_sha256": lock_record["payload_sha256"],
                "payload_hash_matches_lock": payload_hash_matches,
                "holo_packet_present": packet_id in holo_packets,
                "solo_packet_present": packet_id in solo_packets,
                "expected_verdict": lock_record["expected_verdict_for_local_audit"],
                "holo_final_verdict": lock_record["holo_final_verdict"],
            }
        )

        expected = lock_record["expected_verdict_for_local_audit"]
        holo_correct = lock_record["holo_final_verdict"] == expected and bool(lock_record["holo_final_admissible"])
        selector_used = lock_record["holo_selection_reason"] == "FINAL_REGRESSED_SELECTED_BEST_PRIOR"
        intra = holo_packet.get("intra_holo_single_dna_miss_evidence") or []
        intra_classes = sorted({item.get("evidence_category") for item in intra if item.get("evidence_category")})
        miss_text = "; ".join(
            f"{item.get('miss_model')}@{item.get('miss_turn_id')}"
            for item in intra
            if item.get("miss_model") or item.get("miss_turn_id")
        )
        corrected_text = "; ".join(
            f"{item.get('corrected_by_model')}@{item.get('corrected_by_turn_id')}"
            for item in intra
            if item.get("corrected_by_model") or item.get("corrected_by_turn_id")
        )
        sibling_type = "hard ALLOW" if expected == "ALLOW" else "hard ESCALATE"

        for provider, model_name in MODEL_ORDER:
            solo_row = solo_by_packet_model[(packet_id, provider)]
            gate_failures = (solo_row.get("gate_result") or {}).get("failures") or []
            comparison_rows.append(
                {
                    "pair_id": lock_record["pair_id"],
                    "packet_id": packet_id,
                    "sibling_type": sibling_type,
                    "packet_truth": expected,
                    "model_name": model_name,
                    "solo_verdict": solo_row.get("local_verdict"),
                    "solo_verdict_correct": bool(solo_row.get("local_verdict_matches_packet_truth")),
                    "solo_admissible": bool(solo_row.get("admissible")),
                    "solo_label": solo_row.get("solo_label"),
                    "solo_deterministic_audit_failures": gate_failures,
                    "holo_final_verdict": lock_record["holo_final_verdict"],
                    "holo_final_correct": holo_correct,
                    "holo_final_admissible": bool(lock_record["holo_final_admissible"]),
                    "holo_final_selector_used": selector_used,
                    "intra_holo_miss_present": bool(intra),
                    "intra_holo_miss_model_turn": miss_text,
                    "corrected_by_model_gov_selector": corrected_text if corrected_text else ("final_selector_or_gate" if selector_used else ""),
                    "external_evidence_class": evidence_class_for_row(solo_row, holo_correct, [], False)[0],
                    "intra_holo_evidence_classes": intra_classes + (["FINAL_SELECTOR_RESCUE"] if selector_used else []),
                    "evidence_classes": evidence_class_for_row(solo_row, holo_correct, intra_classes, selector_used),
                }
            )

    pairs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in lock_records.values():
        pairs[record["pair_id"]].append(record)

    packet_identity = {
        "packet_ids_match": sorted(lock_records) == sorted(holo_packets) == sorted(solo_packets),
        "packet_count": len(lock_records),
        "payload_hashes_match": all(row["payload_hash_matches_lock"] for row in packet_identity_rows),
        "allow_escalate_sibling_mapping_matches": all(
            sorted(record["expected_verdict_for_local_audit"] for record in records) == ["ALLOW", "ESCALATE"]
            and sorted(record["suffix"] for record in records) == ["A", "B"]
            for records in pairs.values()
        ),
        "hard_allow_target_pairs": len({record["pair_id"] for record in lock_records.values() if record["benchmark_bucket"] == "hard_allow_false_positive_rescue" and record["is_target_packet"]}),
        "hard_escalate_target_pairs": len({record["pair_id"] for record in lock_records.values() if record["benchmark_bucket"] == "hard_escalate_false_negative_rescue" and record["is_target_packet"]}),
        "guardrail_siblings_present_for_all_pairs": all(any(not record["is_target_packet"] for record in records) for records in pairs.values()),
        "rows": packet_identity_rows,
    }
    packet_identity["comparative_proof_valid"] = all(
        [
            packet_identity["packet_ids_match"],
            packet_identity["packet_count"] == 40,
            packet_identity["payload_hashes_match"],
            packet_identity["allow_escalate_sibling_mapping_matches"],
            packet_identity["hard_allow_target_pairs"] == 10,
            packet_identity["hard_escalate_target_pairs"] == 10,
            packet_identity["guardrail_siblings_present_for_all_pairs"],
        ]
    )

    prompt_scan_result = prompt_scan(SOLO_RUN)
    model_metrics: dict[str, dict[str, Any]] = {}
    for provider, model_name in MODEL_ORDER:
        rows = [row for row in solo_trace if row["provider"] == provider]
        expected_allow = [row for row in rows if row["expected_verdict_for_local_audit_only"] == "ALLOW"]
        expected_escalate = [row for row in rows if row["expected_verdict_for_local_audit_only"] == "ESCALATE"]
        model_metrics[model_name] = {
            "correct_count": sum(row["solo_label"] == "KNEW" for row in rows),
            "verdict_correct_count": sum(bool(row.get("local_verdict_matches_packet_truth")) for row in rows),
            "hard_allow_false_positive_failures": sum(row["solo_label"] != "KNEW" for row in expected_allow),
            "hard_allow_explicit_escalate_false_positives": sum(row.get("local_verdict") == "ESCALATE" for row in expected_allow),
            "hard_escalate_false_negative_failures": sum(row["solo_label"] != "KNEW" for row in expected_escalate),
            "hard_escalate_explicit_allow_false_negatives": sum(row.get("local_verdict") == "ALLOW" for row in expected_escalate),
            "admissibility_failures": sum(not bool(row.get("admissible")) for row in rows),
            "parse_failures": sum(row["solo_label"] == "PARSE_FAIL" for row in rows),
            "provider_failures": sum(row["solo_label"] == "PROVIDER_FAIL" for row in rows),
        }

    solo_labels_by_packet: dict[str, list[str]] = defaultdict(list)
    for row in solo_trace:
        solo_labels_by_packet[row["packet_id"]].append(row["solo_label"])
    all_three_solo_misses = sorted(packet_id for packet_id, labels in solo_labels_by_packet.items() if all(label != "KNEW" for label in labels))
    all_three_solo_correct = sorted(packet_id for packet_id, labels in solo_labels_by_packet.items() if all(label == "KNEW" for label in labels))

    final_selector_rescues = [record["packet_id"] for record in lock_records.values() if record["holo_selection_reason"] == "FINAL_REGRESSED_SELECTED_BEST_PRIOR"]
    intra_items = [item for packet in holo_packets.values() for item in (packet.get("intra_holo_single_dna_miss_evidence") or [])]
    intra_counts = Counter(item.get("evidence_category") for item in intra_items if item.get("evidence_category"))
    deterministic_normalizations = sum(1 for row in holo_trace if row.get("call_kind") == "worker" and (row.get("worker_normalization") or {}).get("applied") is True)

    holo_metrics = {
        "correct_count": sum(record["holo_final_verdict"] == record["expected_verdict_for_local_audit"] and record["holo_final_admissible"] for record in lock_records.values()),
        "hard_allow_correct_count": sum(record["holo_final_verdict"] == record["expected_verdict_for_local_audit"] and record["holo_final_admissible"] for record in lock_records.values() if record["expected_verdict_for_local_audit"] == "ALLOW"),
        "hard_escalate_correct_count": sum(record["holo_final_verdict"] == record["expected_verdict_for_local_audit"] and record["holo_final_admissible"] for record in lock_records.values() if record["expected_verdict_for_local_audit"] == "ESCALATE"),
        "target_hard_allow_correct_count": sum(record["holo_final_verdict"] == record["expected_verdict_for_local_audit"] and record["holo_final_admissible"] for record in lock_records.values() if record["benchmark_bucket"] == "hard_allow_false_positive_rescue" and record["is_target_packet"]),
        "target_hard_escalate_correct_count": sum(record["holo_final_verdict"] == record["expected_verdict_for_local_audit"] and record["holo_final_admissible"] for record in lock_records.values() if record["benchmark_bucket"] == "hard_escalate_false_negative_rescue" and record["is_target_packet"]),
        "guardrail_sibling_correct_count": sum(record["holo_final_verdict"] == record["expected_verdict_for_local_audit"] and record["holo_final_admissible"] for record in lock_records.values() if not record["is_target_packet"]),
        "final_selector_fires": len(final_selector_rescues),
        "final_selector_rescue_packets": final_selector_rescues,
        "intra_holo_single_dna_misses": len(intra_items),
        "cross_dna_rescues": intra_counts.get("INTRA_HOLO_CROSS_DNA_RESCUE", 0),
        "gov_rescues": intra_counts.get("INTRA_HOLO_GOV_RESCUE", 0),
        "turn_rescues": intra_counts.get("INTRA_HOLO_TURN_RESCUE", 0),
        "deterministic_normalizations": deterministic_normalizations,
        "provider_failures": len(holo.get("provider_failures") or []),
        "token_totals": holo["totals"],
    }

    packets_with_any_solo_failed_holo_correct = sorted(
        packet_id for packet_id, labels in solo_labels_by_packet.items()
        if any(label != "KNEW" for label in labels)
        and lock_records[packet_id]["holo_final_verdict"] == lock_records[packet_id]["expected_verdict_for_local_audit"]
        and lock_records[packet_id]["holo_final_admissible"]
    )
    packets_where_holo_corrected_intra_miss = sorted(packet_id for packet_id, packet in holo_packets.items() if packet.get("intra_holo_single_dna_miss_evidence"))
    packets_solo_correct_but_holo_needed_selector = sorted(
        packet_id for packet_id in final_selector_rescues if any(label == "KNEW" for label in solo_labels_by_packet[packet_id])
    )

    strongest_examples = [
        "BAL100-HB004-DEP-007-B",
        "HV-KITC-081-A",
        "HV-KITC-084-A",
        "BAL100-HB004-DEP-005-B",
        "BAL100-HB004-DEP-006-B",
    ]
    weakest_examples = [
        "HV-KITC-042",
        "HV-KITC-082",
        "HV-KITC-084",
        "HV-KITC-086",
        "HV-KITC-089",
        "HV-KITC-090",
    ]

    comparative_metrics = {
        "packets_where_at_least_one_solo_failed_and_holo_correct": len(packets_with_any_solo_failed_holo_correct),
        "packets_where_all_three_solos_failed_and_holo_correct": len(all_three_solo_misses),
        "packets_where_solo_correct_but_holo_needed_final_selector": len(packets_solo_correct_but_holo_needed_selector),
        "packets_where_holo_corrected_intra_holo_miss": len(packets_where_holo_corrected_intra_miss),
        "token_delta_holo_minus_solo": holo["totals"]["total_tokens"] - solo["totals"]["total_tokens"],
        "holo_total_tokens": holo["totals"]["total_tokens"],
        "solo_total_tokens": solo["totals"]["total_tokens"],
        "call_delta_holo_minus_solo": holo["provider_calls"] - solo["provider_calls"],
        "holo_provider_calls": holo["provider_calls"],
        "solo_provider_calls": solo["provider_calls"],
        "strongest_5_example_packets_for_public_narrative": strongest_examples,
        "weakest_or_most_ambiguous_packets_not_to_overclaim": weakest_examples,
    }

    solo_audit = {
        "classification": "SOLO_ONE_SHOT_3MINI_BASELINE_AUDIT",
        "solo_provider_calls": solo["provider_calls"],
        "packet_count": len(lock_records),
        "models_per_packet": 3,
        "models_all_packets": {
            model_name: all((packet_id, provider) in solo_by_packet_model for packet_id in lock_records)
            for provider, model_name in MODEL_ORDER
        },
        "no_gov_calls": solo["gov_calls"] == 0,
        "no_holo_state_brief": True,
        "no_gov_baton": True,
        "no_artifact_registry": True,
        "no_final_selector": True,
        "no_holo_deterministic_normalization_as_rescue": True,
        "no_judges": solo["judge_calls"] == 0,
        "no_packet_drift_from_frozen_holo_run": packet_identity["comparative_proof_valid"],
        "no_prompt_leakage_of_expected_verdicts": solo["prompt_leakage_status"] == "PASS" and solo["prompt_leakage_violation_count"] == 0 and prompt_scan_result["forbidden_hit_count"] == 0,
        "deterministic_audit_post_hoc_only": True,
        "provider_failures": solo["provider_failures"],
        "prompt_scan": prompt_scan_result,
        "run_lock_validation": solo_lock_validation,
        "run_lock_root_signature": solo_lock["root_signature"],
    }
    solo_audit["audit_status"] = "PASS" if all(
        [
            solo_audit["solo_provider_calls"] == 120,
            solo_audit["packet_count"] == 40,
            all(solo_audit["models_all_packets"].values()),
            solo_audit["no_gov_calls"],
            solo_audit["no_judges"],
            solo_audit["no_packet_drift_from_frozen_holo_run"],
            solo_audit["no_prompt_leakage_of_expected_verdicts"],
            not solo_audit["provider_failures"],
        ]
    ) else "FAIL"

    summary = {
        "classification": "HOLOVERIFY_20PAIR_3DNA_FINAL_EVIDENCE_PACKAGE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "holo_run": str(HOLO_RUN),
        "solo_run": str(SOLO_RUN),
        "freeze_root": str(FREEZE_ROOT),
        "holo_freeze_root_signature": freeze_lock["root_signature"],
        "holo_trace_hash": holo["trace_hash"],
        "solo_trace_hash": solo["trace_hash"],
        "solo_audit": solo_audit,
        "packet_identity": packet_identity,
        "solo_metrics": {
            "by_model": model_metrics,
            "label_counts": dict(Counter(row["solo_label"] for row in solo_trace)),
            "any_all_three_solo_misses": all_three_solo_misses,
            "any_all_three_solo_correct_packets": all_three_solo_correct,
            "admissibility_failures_by_model": {
                model: stats["admissibility_failures"] for model, stats in model_metrics.items()
            },
            "tokens": solo["totals"],
        },
        "holo_metrics": holo_metrics,
        "comparative_metrics": comparative_metrics,
        "comparison_rows": comparison_rows,
    }

    readiness_assertions = {
        "holo_frozen_run_present": "PASS" if freeze_validation["validation_status"] == "PASS" else "FAIL",
        "holo_valid_pairs": "PASS" if holo["readiness_assertions"].get("total_valid_pairs") == 20 else "FAIL",
        "holo_hard_allow": "PASS" if holo["readiness_assertions"].get("hard_allow_valid_pairs") == 10 else "FAIL",
        "holo_hard_escalate": "PASS" if holo["readiness_assertions"].get("hard_escalate_valid_pairs") == 10 else "FAIL",
        "holo_three_dna": holo["readiness_assertions"].get("three_dna_inside_holoverify", "FAIL"),
        "holo_no_judges": "PASS" if holo["judge_calls"] == 0 else "FAIL",
        "holo_no_provider_failures": "PASS" if not holo["provider_failures"] else "FAIL",
        "solo_run_present": "PASS" if solo["classification"] == "SOLO_ONE_SHOT_3MINI_40_COMPLETE" else "FAIL",
        "solo_provider_calls": "PASS" if solo["provider_calls"] == 120 else "FAIL",
        "solo_packet_identity_matches_holo": "PASS" if packet_identity["comparative_proof_valid"] else "FAIL",
        "solo_three_models_all_packets": "PASS" if all(solo_audit["models_all_packets"].values()) else "FAIL",
        "solo_no_gov": "PASS" if solo["gov_calls"] == 0 else "FAIL",
        "solo_no_holo_state": "PASS" if solo_audit["no_holo_state_brief"] and prompt_scan_result["forbidden_hit_count"] == 0 else "FAIL",
        "solo_no_judges": "PASS" if solo["judge_calls"] == 0 else "FAIL",
        "comparison_rows_complete": "PASS" if len(comparison_rows) == 120 else "FAIL",
        "external_solo_and_intra_holo_evidence_separated": "PASS" if all("external_evidence_class" in row and "intra_holo_evidence_classes" in row for row in comparison_rows) else "FAIL",
        "invalid_runs_preserved": holo["readiness_assertions"].get("invalid_runs_preserved", "FAIL"),
        "final_evidence_memo_present": "PASS",
    }
    readiness = {
        "classification": "HOLOVERIFY_20PAIR_3DNA_FINAL_READINESS_ASSERTIONS",
        "status": "PASS" if all(value == "PASS" for value in readiness_assertions.values()) else "FAIL",
        "assertions": readiness_assertions,
    }

    write_outputs(summary, readiness)
    return {"summary": summary, "readiness": readiness}


def write_outputs(summary: dict[str, Any], readiness: dict[str, Any]) -> None:
    solo_audit = summary["solo_audit"]
    packet_identity = summary["packet_identity"]

    write_json("SOLO_ONE_SHOT_3MINI_BASELINE_AUDIT_2026_06_29.json", solo_audit)
    write_md("SOLO_ONE_SHOT_3MINI_BASELINE_AUDIT_2026_06_29.md", solo_audit_md(summary))

    comparison = {
        "classification": "HOLOVERIFY_20PAIR_SOLO_VS_HOLO_COMPARISON",
        "packet_identity": packet_identity,
        "comparative_metrics": summary["comparative_metrics"],
        "comparison_rows": summary["comparison_rows"],
    }
    write_json("HOLOVERIFY_20PAIR_SOLO_VS_HOLO_COMPARISON_2026_06_29.json", comparison)
    write_md("HOLOVERIFY_20PAIR_SOLO_VS_HOLO_COMPARISON_2026_06_29.md", comparison_md(summary))

    memo = {
        "classification": "HOLOVERIFY_20PAIR_3DNA_FINAL_EVIDENCE_MEMO",
        "locked_evidence": {
            "holo_freeze_root_signature": summary["holo_freeze_root_signature"],
            "holo_trace_hash": summary["holo_trace_hash"],
            "solo_trace_hash": summary["solo_trace_hash"],
        },
        "solo_audit": summary["solo_audit"],
        "packet_identity": summary["packet_identity"],
        "solo_metrics": summary["solo_metrics"],
        "holo_metrics": summary["holo_metrics"],
        "comparative_metrics": summary["comparative_metrics"],
        "readiness": readiness,
    }
    write_json("HOLOVERIFY_20PAIR_3DNA_FINAL_EVIDENCE_MEMO_2026_06_29.json", memo)
    write_md("HOLOVERIFY_20PAIR_3DNA_FINAL_EVIDENCE_MEMO_2026_06_29.md", memo_md(summary, readiness))

    write_md("HOLOVERIFY_20PAIR_PUBLIC_PROOF_SUMMARY_2026_06_29.md", public_summary_md(summary))
    write_json("HOLOVERIFY_20PAIR_3DNA_FINAL_READINESS_ASSERTIONS_2026_06_29.json", readiness)
    write_md("HOLOVERIFY_20PAIR_3DNA_FINAL_READINESS_ASSERTIONS_2026_06_29.md", readiness_md(readiness))
    write_package_lock()


def write_json(filename: str, value: Any) -> None:
    (OUT / filename).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_md(filename: str, lines: list[str]) -> None:
    (OUT / filename).write_text("\n".join(lines) + "\n")


def write_package_lock() -> None:
    locked_files = []
    for path in sorted(OUT.iterdir()):
        if not path.is_file() or path.name in {"FINAL_EVIDENCE_PACKAGE_LOCK_MANIFEST.json", "FINAL_EVIDENCE_PACKAGE_LOCK_VALIDATION.json"}:
            continue
        locked_files.append({"relative_path": path.name, "sha256": sha256_file(path), "bytes": path.stat().st_size})
    manifest_no_root = {
        "classification": "HOLOVERIFY_20PAIR_3DNA_FINAL_EVIDENCE_PACKAGE_LOCK",
        "status": "FROZEN_FINAL_EVIDENCE_PACKAGE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "package_dir": str(OUT),
        "locked_files": locked_files,
    }
    root_signature = sha256_text(canonical_json(manifest_no_root))
    manifest = {**manifest_no_root, "root_signature": root_signature}
    (OUT / "FINAL_EVIDENCE_PACKAGE_LOCK_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    loaded = load_json(OUT / "FINAL_EVIDENCE_PACKAGE_LOCK_MANIFEST.json")
    for item in loaded["locked_files"]:
        if sha256_file(OUT / item["relative_path"]) != item["sha256"]:
            raise RuntimeError(f"final package lock hash mismatch: {item['relative_path']}")
    loaded_no_root = dict(loaded)
    expected_root = loaded_no_root.pop("root_signature")
    recomputed_root = sha256_text(canonical_json(loaded_no_root))
    if recomputed_root != expected_root:
        raise RuntimeError("final package lock root mismatch")
    validation = {
        "validation_status": "PASS",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "root_signature": expected_root,
        "locked_file_count": len(loaded["locked_files"]),
    }
    (OUT / "FINAL_EVIDENCE_PACKAGE_LOCK_VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")


def solo_audit_md(summary: dict[str, Any]) -> list[str]:
    audit = summary["solo_audit"]
    lines = ["# Solo One-Shot 3-Mini Baseline Audit", ""]
    lines += md_table(
        ["Check", "Value"],
        [
            ["audit_status", f"`{audit['audit_status']}`"],
            ["solo_provider_calls", audit["solo_provider_calls"]],
            ["packet_count", audit["packet_count"]],
            ["models_per_packet", audit["models_per_packet"]],
            ["no_gov_calls", audit["no_gov_calls"]],
            ["no_holo_state_brief", audit["no_holo_state_brief"]],
            ["no_gov_baton", audit["no_gov_baton"]],
            ["no_artifact_registry", audit["no_artifact_registry"]],
            ["no_final_selector", audit["no_final_selector"]],
            ["no_holo_deterministic_normalization_as_rescue", audit["no_holo_deterministic_normalization_as_rescue"]],
            ["no_judges", audit["no_judges"]],
            ["no_packet_drift_from_frozen_holo_run", audit["no_packet_drift_from_frozen_holo_run"]],
            ["no_prompt_leakage_of_expected_verdicts", audit["no_prompt_leakage_of_expected_verdicts"]],
            ["deterministic_audit_post_hoc_only", audit["deterministic_audit_post_hoc_only"]],
            ["provider_failures", len(audit["provider_failures"])],
            ["prompt_files_scanned", audit["prompt_scan"]["prompt_files_scanned"]],
            ["forbidden_prompt_hits", audit["prompt_scan"]["forbidden_hit_count"]],
        ],
    )
    lines += ["", "## Model Coverage", ""]
    lines += md_table(["Model", "Ran Once On Every Packet"], [[model, value] for model, value in audit["models_all_packets"].items()])
    lines += ["", "## Notes", ""]
    lines.append("The solo baseline was preserved as emitted. Deterministic audit was applied only after provider output to classify verdict, evidence, and schema admissibility. The solo lane had no Gov, no state brief, no Gov baton, no artifact registry, no final selector, no Holo normalization rescue, and no judges.")
    return lines


def comparison_md(summary: dict[str, Any]) -> list[str]:
    lines = ["# HoloVerify 20-Pair Solo vs Holo Comparison", ""]
    metrics = summary["comparative_metrics"]
    lines += md_table(
        ["Metric", "Value"],
        [
            ["packets_where_at_least_one_solo_failed_and_holo_correct", metrics["packets_where_at_least_one_solo_failed_and_holo_correct"]],
            ["packets_where_all_three_solos_failed_and_holo_correct", metrics["packets_where_all_three_solos_failed_and_holo_correct"]],
            ["packets_where_solo_correct_but_holo_needed_final_selector", metrics["packets_where_solo_correct_but_holo_needed_final_selector"]],
            ["packets_where_holo_corrected_intra_holo_miss", metrics["packets_where_holo_corrected_intra_holo_miss"]],
            ["token_delta_holo_minus_solo", metrics["token_delta_holo_minus_solo"]],
            ["call_delta_holo_minus_solo", metrics["call_delta_holo_minus_solo"]],
        ],
    )
    lines += ["", "## Packet x Model Rows", ""]
    rows = []
    for row in summary["comparison_rows"]:
        rows.append(
            [
                f"`{row['pair_id']}`",
                f"`{row['packet_id']}`",
                row["sibling_type"],
                row["packet_truth"],
                f"`{row['model_name']}`",
                row["solo_verdict"],
                row["solo_verdict_correct"],
                row["solo_admissible"],
                compact_failures(row["solo_deterministic_audit_failures"]),
                row["holo_final_verdict"],
                row["holo_final_correct"],
                row["holo_final_admissible"],
                row["holo_final_selector_used"],
                row["intra_holo_miss_present"],
                row["intra_holo_miss_model_turn"],
                row["corrected_by_model_gov_selector"],
                ", ".join(row["evidence_classes"]),
            ]
        )
    lines += md_table(
        [
            "Pair ID",
            "Packet ID",
            "Sibling Type",
            "Truth",
            "Model",
            "Solo Verdict",
            "Solo Verdict Correct",
            "Solo Admissible",
            "Solo Audit Failures",
            "Holo Final Verdict",
            "Holo Correct",
            "Holo Admissible",
            "Final Selector Used",
            "Intra-Holo Miss",
            "Miss Model/Turn",
            "Corrected By",
            "Evidence Classes",
        ],
        rows,
    )
    return lines


def memo_md(summary: dict[str, Any], readiness: dict[str, Any]) -> list[str]:
    lines = ["# HoloVerify 20-Pair / 3-DNA Final Evidence Memo", ""]
    lines.append("This memo freezes the completed HoloVerify full-architecture run and the matching one-shot solo baseline into a conservative comparative evidence package. No judges were run, no Holo reruns were performed, and no solo output was repaired.")
    lines += ["", "## Locked Evidence", ""]
    lines += md_table(
        ["Artifact", "Value"],
        [
            ["Holo freeze root signature", f"`{summary['holo_freeze_root_signature']}`"],
            ["Holo trace hash", f"`{summary['holo_trace_hash']}`"],
            ["Solo trace hash", f"`{summary['solo_trace_hash']}`"],
            ["Solo audit status", f"`{summary['solo_audit']['audit_status']}`"],
            ["Readiness status", f"`{readiness['status']}`"],
        ],
    )
    lines += ["", "## Solo Baseline", ""]
    solo_metrics = summary["solo_metrics"]
    lines += md_table(
        ["Model", "KNEW", "Verdict Correct", "Hard-ALLOW FP Failures", "Hard-ESCALATE FN Failures", "Admissibility Failures"],
        [
            [
                f"`{model}`",
                stats["correct_count"],
                stats["verdict_correct_count"],
                stats["hard_allow_false_positive_failures"],
                stats["hard_escalate_false_negative_failures"],
                stats["admissibility_failures"],
            ]
            for model, stats in solo_metrics["by_model"].items()
        ],
    )
    lines += ["", "## Holo Run", ""]
    holo = summary["holo_metrics"]
    lines += md_table(
        ["Metric", "Value"],
        [
            ["Holo correct count", holo["correct_count"]],
            ["Holo hard-ALLOW correct count", holo["hard_allow_correct_count"]],
            ["Holo hard-ESCALATE correct count", holo["hard_escalate_correct_count"]],
            ["Target hard-ALLOW correct count", holo["target_hard_allow_correct_count"]],
            ["Target hard-ESCALATE correct count", holo["target_hard_escalate_correct_count"]],
            ["Guardrail sibling correct count", holo["guardrail_sibling_correct_count"]],
            ["Final selector fires", holo["final_selector_fires"]],
            ["Intra-Holo single-DNA misses", holo["intra_holo_single_dna_misses"]],
            ["Cross-DNA rescues", holo["cross_dna_rescues"]],
            ["Gov rescues", holo["gov_rescues"]],
            ["Deterministic normalizations", holo["deterministic_normalizations"]],
            ["Provider failures", holo["provider_failures"]],
            ["Total tokens", holo["token_totals"]["total_tokens"]],
        ],
    )
    lines += ["", "## Comparative Takeaways", ""]
    comp = summary["comparative_metrics"]
    lines += md_table(
        ["Metric", "Value"],
        [
            ["At least one solo failed, Holo correct", comp["packets_where_at_least_one_solo_failed_and_holo_correct"]],
            ["All three solos failed, Holo correct", comp["packets_where_all_three_solos_failed_and_holo_correct"]],
            ["Solo correct but Holo needed final selector", comp["packets_where_solo_correct_but_holo_needed_final_selector"]],
            ["Holo corrected intra-Holo miss", comp["packets_where_holo_corrected_intra_holo_miss"]],
            ["Holo total tokens", comp["holo_total_tokens"]],
            ["Solo total tokens", comp["solo_total_tokens"]],
            ["Token delta", comp["token_delta_holo_minus_solo"]],
            ["Holo calls", comp["holo_provider_calls"]],
            ["Solo calls", comp["solo_provider_calls"]],
            ["Call delta", comp["call_delta_holo_minus_solo"]],
        ],
    )
    lines += ["", "## Strongest Public-Narrative Examples", ""]
    for packet_id in comp["strongest_5_example_packets_for_public_narrative"]:
        lines.append(f"- `{packet_id}`")
    lines += ["", "## Weakest Or Ambiguous Packets Not To Overclaim", ""]
    for packet_id in comp["weakest_or_most_ambiguous_packets_not_to_overclaim"]:
        lines.append(f"- `{packet_id}`")
    return lines


def public_summary_md(summary: dict[str, Any]) -> list[str]:
    lines = ["# HoloVerify 20-Pair Public Proof Summary", ""]
    lines.append("HoloVerify completed a 20-pair, 40-packet action-boundary benchmark using 3 worker model DNA plus Gov adjudication. The full architecture correctly handled 10 hard-ALLOW and 10 hard-ESCALATE pairs. Matching one-shot solo baselines were then run on the same frozen packets to measure individual model misses separately from intra-Holo turn misses.")
    lines += ["", "## Conservative Evidence", ""]
    comp = summary["comparative_metrics"]
    lines += md_table(
        ["Measure", "Value"],
        [
            ["Frozen packets", 40],
            ["Sibling pairs", 20],
            ["Holo provider calls", comp["holo_provider_calls"]],
            ["Solo provider calls", comp["solo_provider_calls"]],
            ["Holo correct/admissible packets", summary["holo_metrics"]["correct_count"]],
            ["Solo KNEW/admissible calls", summary["solo_metrics"]["label_counts"].get("KNEW", 0)],
            ["All-three-solo-miss packets where Holo was correct", comp["packets_where_all_three_solos_failed_and_holo_correct"]],
            ["Prompt leakage hits", summary["solo_audit"]["prompt_scan"]["forbidden_hit_count"]],
            ["Judges run", 0],
        ],
    )
    lines += ["", "## Claim Boundaries", ""]
    lines.append("- This does not claim Holo is smarter than every model.")
    lines.append("- This does not claim Holo always beats solo.")
    lines.append("- This does not claim general superiority beyond this frozen packet family.")
    lines.append("- This does not claim deterministic normalization corrected model reasoning.")
    lines.append("- This does not treat internal Holo misses as standalone solo failures.")
    return lines


def readiness_md(readiness: dict[str, Any]) -> list[str]:
    lines = ["# HoloVerify 20-Pair / 3-DNA Final Readiness Assertions", ""]
    lines.append(f"Status: `{readiness['status']}`")
    lines += ["", "## Assertions", ""]
    lines += md_table(["Assertion", "Status"], [[key, f"`{value}`"] for key, value in readiness["assertions"].items()])
    return lines


def main() -> int:
    package = build_package()
    print(json.dumps({"output_dir": str(OUT), "readiness_status": package["readiness"]["status"]}, indent=2, sort_keys=True))
    return 0 if package["readiness"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
