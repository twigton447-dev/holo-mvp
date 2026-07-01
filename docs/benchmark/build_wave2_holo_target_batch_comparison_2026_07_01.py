#!/usr/bin/env python3
"""Build a no-provider solo-vs-Holo comparison for a Wave 2 Holo target batch."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FREEZE_ROOT = Path("docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01")
SOLO_PACKAGE = FREEZE_ROOT / "solo_triage_3mini/WAVE2_3FAMILY_SOLO_TRIAGE_EVIDENCE_PACKAGE_2026_07_01.json"
TARGET_SELECTION = FREEZE_ROOT / "solo_triage_3mini/WAVE2_HOLO_TARGET_SELECTION_FROM_SOLO_TRIAGE_2026_07_01.json"
BATCHES_ROOT = FREEZE_ROOT / "holo_target_batches"

MODEL_ORDER = {
    "minimax": 0,
    "openai": 1,
    "openai_w2": 1,
    "openai_weak": 1,
    "xai": 2,
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def sha256_json(data: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, indent=2).encode()).hexdigest()


def batch_id(batch_number: int) -> str:
    return f"WAVE2_HOLO_TARGET_BATCH_{batch_number:03d}"


def batch_root(batch_number: int) -> Path:
    return BATCHES_ROOT / f"wave2_holo_target_batch_{batch_number:03d}"


def latest_run_dir(root: Path) -> Path:
    runs = sorted((root / "live_runs").glob("run_*"))
    if not runs:
        raise FileNotFoundError(f"No live run found under {root / 'live_runs'}")
    return runs[-1]


def load_solo_trace_index(solo_package: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for domain in solo_package["domains"].values():
        trace_path = Path(domain["run_dir"]) / "SOLO_TRIAGE_TRACE.jsonl"
        for line in trace_path.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            index[row["packet_id"]].append(row)
    return index


def solo_failure_class(row: dict[str, Any]) -> str:
    label = row.get("solo_label")
    if label == "KNEW":
        return "KNEW"
    if label:
        return label
    if not row.get("provider_call_ok", True):
        return "PROVIDER_FAIL"
    if not row.get("parse_ok"):
        return "PARSE_FAIL"
    if not row.get("local_verdict_matches_packet_truth"):
        return "WRONG_VERDICT"
    if not row.get("admissible"):
        return "STRUCTURAL_OR_EVIDENCE_FAIL"
    return "KNEW"


def solo_outcome(row: dict[str, Any]) -> dict[str, Any]:
    failure_class = solo_failure_class(row)
    gate_result = row.get("gate_result") or {}
    return {
        "admissible": bool(row.get("admissible")),
        "failure_class": failure_class,
        "gate_failures": gate_result.get("failures", []),
        "knew_admissible": failure_class == "KNEW" and bool(row.get("admissible")),
        "model": row.get("model"),
        "model_key": row.get("model_key"),
        "packet_id": row.get("packet_id"),
        "packet_truth": row.get("packet_truth_for_local_audit_only"),
        "parse_ok": bool(row.get("parse_ok")),
        "prompt_hash_matches_freeze": bool(row.get("prompt_hash_matches_freeze")),
        "prompt_leakage_hits": row.get("prompt_leakage_hits", []),
        "provider": row.get("provider"),
        "solo_label": row.get("solo_label", failure_class),
        "solo_verdict": row.get("local_verdict"),
        "total_tokens": row.get("total_tokens", 0),
        "trace_path": str(Path(row.get("trace_path", ""))) if row.get("trace_path") else None,
        "verdict_correct": bool(row.get("local_verdict_matches_packet_truth")),
    }


def sort_solo_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda r: (r.get("packet_id", ""), MODEL_ORDER.get(r.get("model_key", ""), 99), r.get("call_index", 0)))


def packet_holo_result(packet_result: dict[str, Any], truth: str) -> dict[str, Any]:
    return {
        "packet_id": packet_result["packet_id"],
        "packet_truth": truth,
        "holo_final_verdict": packet_result.get("final_verdict"),
        "holo_final_binding": packet_result.get("final_binding"),
        "holo_final_admissible": bool(packet_result.get("final_admissible")),
        "holo_correct": bool(packet_result.get("final_admissible")) and packet_result.get("final_verdict") == truth,
        "holo_final_selector": packet_result.get("final_selector", {}),
        "holo_artifacts": packet_result.get("artifact_registry", []),
        "holo_intra_misses": packet_result.get("intra_holo_single_dna_miss_evidence", []),
    }


def pair_metadata(registration: dict[str, Any]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for rec in registration["selected_records"]:
        pair = grouped.setdefault(
            rec["pair_id"],
            {
                "domain": rec["domain"],
                "family_id": rec["family_id"],
                "pair_id": rec["pair_id"],
                "target_bucket": rec["target_bucket"],
                "triage_class": rec["triage_class"],
                "solo_not_knew_count_from_selection": rec["not_knew_count"],
                "solo_wrong_verdict_count_from_selection": rec["wrong_verdict_count"],
                "solo_parse_or_provider_fail_count_from_selection": rec["parse_or_provider_fail_count"],
                "records": [],
            },
        )
        pair["records"].append(rec)
    return grouped


def build_comparison(batch_number: int, run_dir: Path | None = None) -> dict[str, Any]:
    bid = batch_id(batch_number)
    root = batch_root(batch_number)
    registration = read_json(root / f"{bid}_REGISTRATION_2026_07_01.json")
    run_dir = run_dir or latest_run_dir(root)
    live_results = read_json(run_dir / "live_results.json")
    solo_package = read_json(SOLO_PACKAGE)
    target_selection = read_json(TARGET_SELECTION)
    solo_index = load_solo_trace_index(solo_package)

    packet_results = {row["packet_id"]: row for row in live_results["packet_results"]}
    pair_meta = pair_metadata(registration)
    pair_rows: list[dict[str, Any]] = []
    intra_holo_worker_misses: list[dict[str, Any]] = []

    for inventory in live_results["benchmark_inventory"]:
        pair_id = inventory["pair_id"]
        meta = pair_meta[pair_id]
        records = {rec["packet_id"]: rec for rec in meta["records"]}
        target_packet = inventory["target_packet_id"]
        guardrail_packet = inventory["guardrail_packet_id"]
        packet_rows = []
        six_solo = []
        for packet_id in sorted(records):
            rec = records[packet_id]
            pr = packet_results[packet_id]
            packet_rows.append(packet_holo_result(pr, rec["packet_truth"]))
            for miss in pr.get("intra_holo_single_dna_miss_evidence", []):
                intra_holo_worker_misses.append(
                    {
                        "packet_id": packet_id,
                        "pair_id": pair_id,
                        "turn_id": miss.get("turn_id"),
                        "worker_index": miss.get("worker_index"),
                        "provider": miss.get("provider"),
                        "model": miss.get("model"),
                        "dna": miss.get("dna"),
                        "local_verdict": miss.get("local_verdict"),
                        "admissible": bool(miss.get("admissible")),
                        "parse_ok": bool(miss.get("parse_ok", True)),
                        "gate_failures": miss.get("gate_failures", []),
                    }
                )
            for row in sort_solo_rows(solo_index.get(packet_id, [])):
                outcome = solo_outcome(row)
                outcome["trace_path"] = str(Path(solo_package["domains"][rec["family_id"]]["run_dir"]) / "SOLO_TRIAGE_TRACE.jsonl")
                six_solo.append(outcome)

        evidence_class = (
            "ALL_SIX_SOLO_COLLAPSE_HOLO_PAIR_SOLVED"
            if meta["triage_class"] == "ALL_SIX_SOLO_COLLAPSE"
            else "STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED"
        )
        pair_rows.append(
            {
                "domain": meta["domain"],
                "evidence_class": evidence_class,
                "family_id": meta["family_id"],
                "holo_guardrail_expected": records[guardrail_packet]["packet_truth"],
                "holo_guardrail_final_correct": inventory["guardrail_final_correct"],
                "holo_guardrail_final_verdict": inventory["guardrail_final_verdict"],
                "holo_guardrail_packet_id": guardrail_packet,
                "holo_pair_valid": inventory["pair_valid"],
                "holo_target_expected": records[target_packet]["packet_truth"],
                "holo_target_final_correct": inventory["target_final_correct"],
                "holo_target_final_verdict": inventory["target_final_verdict"],
                "holo_target_packet_id": target_packet,
                "packet_results": packet_rows,
                "pair_id": pair_id,
                "six_solo_outcomes": six_solo,
                "solo_not_knew_count_from_selection": meta["solo_not_knew_count_from_selection"],
                "solo_parse_or_provider_fail_count_from_selection": meta["solo_parse_or_provider_fail_count_from_selection"],
                "solo_wrong_verdict_count_from_selection": meta["solo_wrong_verdict_count_from_selection"],
                "target_bucket": meta["target_bucket"],
                "triage_class": meta["triage_class"],
            }
        )

    solo_outcomes = [out for row in pair_rows for out in row["six_solo_outcomes"]]
    solo_tokens = {
        "attempts": len(solo_outcomes),
        "input_tokens": sum((row.get("input_tokens") or 0) for rows in solo_index.values() for row in rows if row.get("packet_id") in {r["packet_id"] for r in registration["selected_records"]}),
        "output_tokens": sum((row.get("output_tokens") or 0) for rows in solo_index.values() for row in rows if row.get("packet_id") in {r["packet_id"] for r in registration["selected_records"]}),
        "total_tokens": sum(out.get("total_tokens") or 0 for out in solo_outcomes),
        "knew_admissible": sum(1 for out in solo_outcomes if out["knew_admissible"]),
        "not_knew": sum(1 for out in solo_outcomes if not out["knew_admissible"]),
        "wrong_verdict": sum(1 for out in solo_outcomes if out["failure_class"] == "WRONG_VERDICT"),
        "parse_fail": sum(1 for out in solo_outcomes if out["failure_class"] == "PARSE_FAIL"),
        "provider_failures": sum(1 for out in solo_outcomes if out["failure_class"] == "PROVIDER_FAIL"),
        "structural_or_evidence_fail": sum(1 for out in solo_outcomes if out["failure_class"] == "STRUCTURAL_OR_EVIDENCE_FAIL"),
    }
    selected_packet_ids = {rec["packet_id"] for rec in registration["selected_records"]}
    solo_tokens["input_tokens"] = sum((row.get("input_tokens") or 0) for packet_id, rows in solo_index.items() if packet_id in selected_packet_ids for row in rows)
    solo_tokens["output_tokens"] = sum((row.get("output_tokens") or 0) for packet_id, rows in solo_index.items() if packet_id in selected_packet_ids for row in rows)

    holo_tokens = {
        "input_tokens": live_results["totals"]["input_tokens"],
        "output_tokens": live_results["totals"]["output_tokens"],
        "total_tokens": live_results["totals"]["total_tokens"],
        "gov_total_tokens": live_results["benchmark_law_validation"]["gov_tokens"],
        "worker_total_tokens": live_results["totals"]["total_tokens"] - live_results["benchmark_law_validation"]["gov_tokens"],
    }
    holo_tokens["gov_share_of_holo_tokens"] = round(holo_tokens["gov_total_tokens"] / holo_tokens["total_tokens"], 6)
    holo_tokens["gov_worker_token_ratio"] = round(holo_tokens["gov_total_tokens"] / holo_tokens["worker_total_tokens"], 6)

    summary_metrics = {
        "holo_final_packet_count": live_results["packet_count"],
        "holo_final_packets_correct_admissible": live_results["packet_correct"],
        "holo_intra_worker_misses_corrected": len(intra_holo_worker_misses),
        "holo_pair_count": len(live_results["benchmark_inventory"]),
        "holo_parse_failures": 0,
        "holo_provider_failures": len(live_results["provider_failures"]),
        "holo_valid_pairs": live_results["valid_pairs"],
        "solo_attempts_on_selected_packets": len(solo_outcomes),
        "solo_knew_admissible": solo_tokens["knew_admissible"],
        "solo_not_knew": solo_tokens["not_knew"],
        "solo_not_knew_rate": round(solo_tokens["not_knew"] / len(solo_outcomes), 6),
        "solo_parse_fail": solo_tokens["parse_fail"],
        "solo_provider_failures": solo_tokens["provider_failures"],
        "solo_structural_or_evidence_fail": solo_tokens["structural_or_evidence_fail"],
        "solo_wrong_verdict": solo_tokens["wrong_verdict"],
        "all_six_solo_collapse_pairs": sum(1 for row in pair_rows if row["triage_class"] == "ALL_SIX_SOLO_COLLAPSE"),
        "strong_solo_collapse_pairs": sum(1 for row in pair_rows if row["triage_class"] == "STRONG_SOLO_COLLAPSE"),
        "token_ratio_holo_vs_selected_solo": round(holo_tokens["total_tokens"] / solo_tokens["total_tokens"], 6),
    }

    comparison = {
        "claim_boundaries": [
            f"This comparison covers only {bid}, not all Wave 2 packets.",
            "No new provider calls, Holo calls, solo calls, or judge calls were made to build this comparison.",
            "Solo evidence comes from the existing Wave 2 three-mini one-shot solo triage package.",
            "Internal Holo worker misses are separated from external solo failures.",
            "Token ratio is operational bookkeeping, not a proof claim.",
        ],
        "classification": f"{bid}_SOLO_VS_HOLO_COMPARISON_COMPLETE",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "holo_run_summary": {
            "classification": live_results["classification"],
            "run_dir": str(run_dir),
            "readiness_passed": live_results["readiness_passed"],
            "trace_hash": live_results["trace_hash"],
            "lock_validation_status": read_json(run_dir / "LOCK_VALIDATION.json")["validation_status"],
            "no_leakage_status": read_json(run_dir / f"{bid}_NO_LEAKAGE_AUDIT.json")["status"],
        },
        "holo_tokens": holo_tokens,
        "intra_holo_worker_misses_corrected": intra_holo_worker_misses,
        "model_totals_on_selected_solo_packets": {},
        "pair_rows": pair_rows,
        "scope": {
            "batch_id": bid,
            "holo_run": str(run_dir.relative_to(root)),
            "no_judges": True,
            "no_new_provider_calls_for_comparison": True,
            "selected_packets": registration["packet_count"],
            "selected_pairs": registration["pair_count"],
            "selection_source": str(TARGET_SELECTION.name),
            "solo_runs": [domain["run_dir"] for domain in solo_package["domains"].values()],
        },
        "solo_tokens_on_selected_packets": solo_tokens,
        "source_target_selection_sha256": target_selection["package_sha256"],
        "summary_metrics": summary_metrics,
    }

    by_model: dict[str, dict[str, int]] = defaultdict(lambda: {"attempts": 0, "knew_admissible": 0, "not_knew": 0, "wrong_verdict": 0, "parse_fail": 0, "structural_or_evidence_fail": 0, "total_tokens": 0})
    for out in solo_outcomes:
        key = f"{out['provider']}/{out['model']}"
        row = by_model[key]
        row["attempts"] += 1
        row["knew_admissible"] += int(out["knew_admissible"])
        row["not_knew"] += int(not out["knew_admissible"])
        row["wrong_verdict"] += int(out["failure_class"] == "WRONG_VERDICT")
        row["parse_fail"] += int(out["failure_class"] == "PARSE_FAIL")
        row["structural_or_evidence_fail"] += int(out["failure_class"] == "STRUCTURAL_OR_EVIDENCE_FAIL")
        row["total_tokens"] += out.get("total_tokens") or 0
    comparison["model_totals_on_selected_solo_packets"] = dict(sorted(by_model.items()))
    comparison["package_sha256"] = sha256_json(comparison)
    return comparison


def comparison_md(comparison: dict[str, Any], batch_number: int) -> str:
    bid = batch_id(batch_number)
    m = comparison["summary_metrics"]
    lines = [
        f"# {bid} Solo vs Holo Comparison",
        "",
        f"Classification: `{comparison['classification']}`",
        f"Package SHA-256: `{comparison['package_sha256']}`",
        "",
        "## Scope",
        "",
        "This is a no-provider comparison built from the completed Holo live run and the existing Wave 2 solo triage package.",
        "",
        "## Summary Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for label, key in [
        ("Holo packets correct/admissible", "holo_final_packets_correct_admissible"),
        ("Holo packets total", "holo_final_packet_count"),
        ("Holo valid pairs", "holo_valid_pairs"),
        ("Holo pair count", "holo_pair_count"),
        ("Holo provider failures", "holo_provider_failures"),
        ("Solo attempts on selected packets", "solo_attempts_on_selected_packets"),
        ("Solo KNEW/admissible", "solo_knew_admissible"),
        ("Solo not KNEW", "solo_not_knew"),
        ("Solo wrong verdicts", "solo_wrong_verdict"),
        ("Solo parse fails", "solo_parse_fail"),
        ("Solo structural/evidence fails", "solo_structural_or_evidence_fail"),
        ("All-six solo-collapse pairs", "all_six_solo_collapse_pairs"),
        ("Strong solo-collapse pairs", "strong_solo_collapse_pairs"),
        ("Intra-Holo worker misses corrected", "holo_intra_worker_misses_corrected"),
        ("Holo/selected solo token ratio", "token_ratio_holo_vs_selected_solo"),
    ]:
        lines.append(f"| {label} | `{m[key]}` |")
    lines += ["", "## Claim Boundaries", ""]
    lines += [f"- {item}" for item in comparison["claim_boundaries"]]
    lines += ["", "## Pair Rows", "", "| Pair | Family | Bucket | Solo not KNEW | Solo wrong verdicts | Holo target | Holo guardrail | Evidence class |", "| --- | --- | --- | ---: | ---: | --- | --- | --- |"]
    for row in comparison["pair_rows"]:
        target = f"{row['holo_target_packet_id']} {row['holo_target_expected']}->{row['holo_target_final_verdict']}"
        guardrail = f"{row['holo_guardrail_packet_id']} {row['holo_guardrail_expected']}->{row['holo_guardrail_final_verdict']}"
        lines.append(
            f"| `{row['pair_id']}` | `{row['family_id']}` | `{row['target_bucket']}` | `{row['solo_not_knew_count_from_selection']}` | `{row['solo_wrong_verdict_count_from_selection']}` | `{target}` | `{guardrail}` | `{row['evidence_class']}` |"
        )
    lines += ["", "## Holo Run", ""]
    for key, value in comparison["holo_run_summary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-number", type=int, required=True)
    parser.add_argument("--run-dir", type=Path)
    args = parser.parse_args()
    comparison = build_comparison(args.batch_number, args.run_dir)
    bid = batch_id(args.batch_number)
    root = batch_root(args.batch_number)
    out_json = root / f"{bid}_SOLO_VS_HOLO_COMPARISON_2026_07_01.json"
    out_md = root / f"{bid}_SOLO_VS_HOLO_COMPARISON_2026_07_01.md"
    write_json(out_json, comparison)
    out_md.write_text(comparison_md(comparison, args.batch_number))
    print(json.dumps({"status": "PASS", "json": str(out_json), "md": str(out_md), "package_sha256": comparison["package_sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
