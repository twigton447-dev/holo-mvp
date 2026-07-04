#!/usr/bin/env python3
"""Post-hoc scorer for the Tier 3 FN targeted-mining solo scout."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(BENCHMARK_ROOT) not in sys.path:
    sys.path.insert(0, str(BENCHMARK_ROOT))

import score_holoverify_blind_120_solo_posthoc_2026_07_03 as SOLO_SCORE  # noqa: E402


SCORING_MAP = (
    BENCHMARK_ROOT
    / "holoverify_tier3_fn_targeted_mining_scout_2026_07_05"
    / "holoverify_tier3_fn_targeted_mining_scout_scoring_map_2026_07_05.json"
)
EXPECTED_SCORING_MAP_SHA256 = "b0d854409dd480f3cb28dc252d72cf4eb5075b13e7c648705bfae8019beb1315"
ROLLUP_JSON = BENCHMARK_ROOT / "HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT_SOLO_ROLLUP_2026_07_05.json"
ROLLUP_MD = BENCHMARK_ROOT / "HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT_SOLO_ROLLUP_2026_07_05.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(errors="replace"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(errors="replace").splitlines() if line.strip()]


def configure_base() -> None:
    SOLO_SCORE.SCORING_MAP = SCORING_MAP
    SOLO_SCORE.EXPECTED_SCORING_MAP_SHA256 = EXPECTED_SCORING_MAP_SHA256


def normalize_text(value: str) -> str:
    return (
        value.replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
    )


def parse_key_value(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().lower()
        if key:
            parsed[key] = value.strip()
    return parsed


def extract_verdict(text: str, parsed: dict[str, str]) -> str:
    parsed_verdict = parsed.get("verdict", "")
    match = re.search(r"\b(allow|escalate)\b", parsed_verdict, flags=re.I)
    if match:
        return match.group(1).upper()
    match = re.search(r"\bverdict\s*[:=]\s*<?\s*(allow|escalate)\s*>?", text, flags=re.I)
    return match.group(1).upper() if match else ""


def extract_reason(text: str, parsed: dict[str, str]) -> str:
    if parsed.get("reason"):
        return parsed["reason"].strip().strip("<>")
    match = re.search(r"\breason\s*[:=]\s*<?\s*(.+?)\s*>?\s*$", text, flags=re.I | re.S)
    if match:
        return match.group(1).strip()
    verdict_match = re.search(r"\bverdict\s*[:=]\s*<?\s*(?:allow|escalate)\s*>?", text, flags=re.I)
    if verdict_match:
        remainder = text[verdict_match.end() :].strip(" ;,.-\n\t")
        if remainder:
            return remainder
    return ""


def source_refs(payload: dict[str, Any]) -> set[str]:
    refs = {
        str(doc.get("doc_id"))
        for doc in payload.get("documents", [])
        if isinstance(doc, dict) and doc.get("doc_id")
    }
    for doc in payload.get("documents", []):
        if not isinstance(doc, dict):
            continue
        text = normalize_text(str(doc.get("text") or ""))
        refs.update(re.findall(r"\bid=([A-Z0-9][A-Z0-9-]*)", text))
    return refs


def normalize_output_gate(payload: dict[str, Any], text: str) -> dict[str, Any]:
    normalized_text = normalize_text(text)
    parsed = parse_key_value(normalized_text)
    verdict = extract_verdict(normalized_text, parsed)
    reason = extract_reason(normalized_text, parsed)
    allowed = source_refs(payload)
    candidates = set(
        re.findall(
            r"\b(?:SYNTH-NOTICE|REQ-\d{3}|SRC-\d{3})\b",
            normalize_text(reason),
        )
    )
    cited = sorted(candidate for candidate in candidates if candidate in allowed)
    invented = sorted(candidate for candidate in candidates if candidate not in allowed)
    failures: list[str] = []
    if verdict not in {"ALLOW", "ESCALATE"}:
        failures.append("missing_or_invalid_verdict")
    if not reason:
        failures.append("missing_reason")
    if not cited:
        failures.append("missing_source_id_in_reason")
    if invented:
        failures.append("invented_source_id")
    return {
        "gate_name": "TIER3_FN_TARGETED_MINING_SOLO_NORMALIZED_POSTHOC_GATE_V1",
        "parsed": {"verdict": verdict, "reason": reason},
        "passed": not failures,
        "failures": failures,
        "cited_source_ids": cited,
        "invented_source_ids": invented,
    }


def error_class(verdict: str, truth: str | None, admissible: bool) -> str:
    if not admissible:
        return "PARSE_OR_ADMISSIBILITY_FAILURE"
    if verdict not in {"ALLOW", "ESCALATE"}:
        return "UNKNOWN_VERDICT"
    if verdict == truth:
        return "KNEW_ADMISSIBLE"
    if verdict == "ALLOW" and truth == "ESCALATE":
        return "FALSE_NEGATIVE_ALLOW_ON_ESCALATE"
    if verdict == "ESCALATE" and truth == "ALLOW":
        return "FALSE_POSITIVE_ESCALATE_ON_ALLOW"
    return "WRONG_VERDICT"


def recompute_report_with_normalized_gate(report: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    runtime = load_json(run_dir / "solo_one_shot_runtime_results.json")
    manifest = load_json(REPO_ROOT / runtime["runtime_manifest"])
    scoring = load_json(SCORING_MAP)
    payload_ref_by_opaque = {row["opaque_runtime_id"]: row["runtime_payload_ref"] for row in manifest.get("packets", [])}
    truth_by_opaque = {
        row["opaque_runtime_id"]: {
            "truth": row["legacy_truth"],
            "domain": row.get("domain"),
            "pair_id": row.get("pair_id"),
            "legacy_packet_id": row.get("legacy_packet_id"),
        }
        for row in scoring.get("scoring_rows", [])
    }
    runtime_gate_by_key = {
        (row.get("opaque_runtime_id"), row.get("model_key")): row.get("gate_result")
        for row in runtime.get("results", [])
    }
    trace_rows = load_jsonl(run_dir / "TRACE_PROVIDER_CALLS.jsonl")

    score_rows: list[dict[str, Any]] = []
    by_model: dict[str, Counter] = defaultdict(Counter)
    by_domain_model: dict[str, Counter] = defaultdict(Counter)
    packet_to_model_results: dict[str, list[dict[str, Any]]] = defaultdict(list)
    token_totals: dict[str, int] = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    token_totals_by_model: dict[str, dict[str, int]] = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})

    for provider in trace_rows:
        opaque = provider.get("opaque_runtime_id")
        model_key = str(provider.get("model_key"))
        for key in token_totals:
            value = provider.get(key)
            if isinstance(value, int):
                token_totals[key] += value
                token_totals_by_model[model_key][key] += value
        payload = load_json(REPO_ROOT / payload_ref_by_opaque[str(opaque)])
        raw = load_json(run_dir / str(provider.get("raw_output_ref")))
        gate = normalize_output_gate(payload, str(raw.get("text") or ""))
        truth_meta = truth_by_opaque.get(opaque, {})
        truth = truth_meta.get("truth")
        verdict = gate["parsed"].get("verdict")
        admissible = bool(gate.get("passed"))
        cls = error_class(str(verdict), truth, admissible)
        correct = verdict == truth
        knew_admissible = admissible and correct
        row = {
            "opaque_runtime_id": opaque,
            "domain": truth_meta.get("domain"),
            "pair_id": truth_meta.get("pair_id"),
            "legacy_packet_id": truth_meta.get("legacy_packet_id"),
            "model_key": model_key,
            "provider": provider.get("provider"),
            "model": provider.get("model"),
            "truth": truth,
            "solo_verdict": verdict,
            "solo_admissible": admissible,
            "solo_correct": correct,
            "solo_knew_admissible": knew_admissible,
            "error_class": cls,
            "gate_failures": gate.get("failures", []),
            "normalized_gate_result": gate,
            "runtime_gate_result_before_normalization": runtime_gate_by_key.get((opaque, model_key)),
            "trace_call_number": provider.get("call_number"),
            "provider_row": provider,
        }
        score_rows.append(row)
        packet_to_model_results[str(opaque)].append(row)
        by_model[model_key]["total"] += 1
        by_model[model_key][cls] += 1
        by_model[model_key]["admissible"] += 1 if admissible else 0
        by_model[model_key]["correct"] += 1 if correct else 0
        by_model[model_key]["knew_admissible"] += 1 if knew_admissible else 0
        by_model[model_key]["false_positive"] += 1 if cls == "FALSE_POSITIVE_ESCALATE_ON_ALLOW" else 0
        by_model[model_key]["false_negative"] += 1 if cls == "FALSE_NEGATIVE_ALLOW_ON_ESCALATE" else 0
        domain_key = f"{truth_meta.get('domain')}|{model_key}"
        by_domain_model[domain_key]["total"] += 1
        by_domain_model[domain_key]["knew_admissible"] += 1 if knew_admissible else 0
        by_domain_model[domain_key][cls] += 1

    packet_collapse_rows: list[dict[str, Any]] = []
    collapse_counts = Counter()
    for opaque, rows in packet_to_model_results.items():
        failures = [row for row in rows if not row["solo_knew_admissible"]]
        knew = [row for row in rows if row["solo_knew_admissible"]]
        if len(failures) == 3:
            collapse_class = "ALL_THREE_SOLO_COLLAPSE"
        elif len(failures) == 2:
            collapse_class = "TWO_OF_THREE_SOLO_COLLAPSE"
        elif len(failures) == 1:
            collapse_class = "ONE_OF_THREE_SOLO_COLLAPSE"
        else:
            collapse_class = "ALL_THREE_SOLO_KNEW"
        collapse_counts[collapse_class] += 1
        first = rows[0]
        packet_collapse_rows.append(
            {
                "opaque_runtime_id": opaque,
                "domain": first.get("domain"),
                "pair_id": first.get("pair_id"),
                "legacy_packet_id": first.get("legacy_packet_id"),
                "truth": first.get("truth"),
                "collapse_class": collapse_class,
                "solo_knew_count": len(knew),
                "solo_failure_count": len(failures),
                "model_outcomes": [
                    {
                        "model_key": row["model_key"],
                        "solo_verdict": row["solo_verdict"],
                        "solo_admissible": row["solo_admissible"],
                        "solo_knew_admissible": row["solo_knew_admissible"],
                        "error_class": row["error_class"],
                    }
                    for row in rows
                ],
            }
        )

    report["score_rows"] = score_rows
    report["summary_by_model"] = {key: dict(counter) for key, counter in by_model.items()}
    report["summary_by_domain_model"] = {key: dict(counter) for key, counter in by_domain_model.items()}
    report["packet_collapse_summary"] = dict(collapse_counts)
    report["packet_collapse_rows"] = sorted(packet_collapse_rows, key=lambda item: str(item["opaque_runtime_id"]))
    report["token_totals"] = token_totals
    report["token_totals_by_model"] = dict(token_totals_by_model)
    report["normalization_note"] = (
        "Tier3 FN targeted-mining post-hoc scoring normalizes reasonable business-prompt variants such as verdict=<ALLOW>, "
        "verdict=ALLOW reason=..., and cited record IDs present inside source rows."
    )
    return report


def compact_pair_summary(score_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in score_rows:
        by_pair[str(row.get("pair_id"))].append(row)

    pair_rows: list[dict[str, Any]] = []
    summary = Counter()
    for pair_id, rows in sorted(by_pair.items()):
        failures = [row for row in rows if not row.get("solo_knew_admissible")]
        wrong = [
            row
            for row in rows
            if row.get("error_class") in {"FALSE_POSITIVE_ESCALATE_ON_ALLOW", "FALSE_NEGATIVE_ALLOW_ON_ESCALATE", "WRONG_VERDICT"}
        ]
        parse = [row for row in rows if row.get("error_class") == "PARSE_OR_ADMISSIBILITY_FAILURE"]
        fp = [row for row in rows if row.get("error_class") == "FALSE_POSITIVE_ESCALATE_ON_ALLOW"]
        fn = [row for row in rows if row.get("error_class") == "FALSE_NEGATIVE_ALLOW_ON_ESCALATE"]
        if failures:
            summary["pairs_with_any_solo_failure"] += 1
        if wrong:
            summary["pairs_with_wrong_verdict"] += 1
        if fp:
            summary["pairs_with_false_positive"] += 1
        if fn:
            summary["pairs_with_false_negative"] += 1
        if parse and not wrong:
            summary["pairs_parse_only"] += 1
        pair_rows.append(
            {
                "pair_id": pair_id,
                "domain": rows[0].get("domain") if rows else None,
                "solo_calls": len(rows),
                "solo_failure_count": len(failures),
                "wrong_verdict_count": len(wrong),
                "parse_or_admissibility_count": len(parse),
                "false_positive_count": len(fp),
                "false_negative_count": len(fn),
                "legacy_packets": sorted({str(row.get("legacy_packet_id")) for row in rows}),
                "failing_models": sorted({str(row.get("model_key")) for row in failures}),
                "error_classes": dict(Counter(str(row.get("error_class")) for row in rows)),
            }
        )
    summary["pair_count"] = len(by_pair)
    return {"summary": dict(summary), "pairs": pair_rows}


def build_markdown(report: dict[str, Any], rollup: dict[str, Any]) -> str:
    lines = [
        "# HoloVerify Tier 3 FN Targeted Mining Solo Scout Live Rollup",
        "",
        "Status: `SOLO_SCOUT_SCORED_POSTHOC`",
        "",
        f"- Run dir: `{rollup['run_dir']}`",
        f"- Packets: `{report.get('packet_count')}`",
        f"- Solo calls: `{report.get('solo_call_count')}`",
        f"- Models per packet: `{report.get('models_per_packet')}`",
        f"- Scoring map loaded after trace hash binding: `{report.get('scoring_map_loaded_after_trace_hash_binding')}`",
        f"- Trace hash: `{report.get('trace_binding', {}).get('trace_provider_calls_sha256')}`",
        f"- Scoring map hash: `{report.get('trace_binding', {}).get('scoring_map_sha256')}`",
        "",
        "## Scoring Note",
        "",
        report.get("normalization_note", ""),
        "",
        "## Aggregate",
        "",
        "```json",
        json.dumps(rollup["aggregate"], indent=2, sort_keys=True),
        "```",
        "",
        "## Model Summary",
        "",
        "```json",
        json.dumps(report.get("summary_by_model", {}), indent=2, sort_keys=True),
        "```",
        "",
        "## Pair Summary",
        "",
        "```json",
        json.dumps(rollup["pair_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Claim Boundary",
        "",
        "Solo-failure discovery only. No Holo, no Gov, no judges, and no public benchmark claim.",
    ]
    return "\n".join(lines) + "\n"


def score(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    configure_base()
    scoring_hash = sha256_file(SCORING_MAP)
    if scoring_hash != EXPECTED_SCORING_MAP_SHA256:
        raise RuntimeError(f"scoring_map_hash_mismatch:{scoring_hash}")

    report = SOLO_SCORE.score(run_dir)
    report = recompute_report_with_normalized_gate(report, run_dir)
    report["classification"] = "HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT_SOLO_POSTHOC_SCORE_V1"
    report["solo_failure_factory_batch"] = "TIER3_FN_TARGETED_MINING_SCOUT"
    report["scoring_map"] = str(SCORING_MAP.relative_to(REPO_ROOT))
    report["scoring_map_sha256_expected"] = EXPECTED_SCORING_MAP_SHA256

    out_json = run_dir / "tier3_fn_targeted_mining_scout_solo_posthoc_score.json"
    write_json(out_json, report)

    aggregate = Counter()
    for row in report.get("score_rows", []):
        aggregate["solo_calls"] += 1
        aggregate[str(row.get("error_class"))] += 1
        aggregate["knew_admissible"] += 1 if row.get("solo_knew_admissible") else 0
        aggregate["correct"] += 1 if row.get("solo_correct") else 0
        aggregate["admissible"] += 1 if row.get("solo_admissible") else 0
        aggregate["false_positive"] += 1 if row.get("error_class") == "FALSE_POSITIVE_ESCALATE_ON_ALLOW" else 0
        aggregate["false_negative"] += 1 if row.get("error_class") == "FALSE_NEGATIVE_ALLOW_ON_ESCALATE" else 0
        aggregate["parse_or_admissibility_failure"] += 1 if row.get("error_class") == "PARSE_OR_ADMISSIBILITY_FAILURE" else 0

    pair_summary = compact_pair_summary(list(report.get("score_rows", [])))
    rollup = {
        "classification": "HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT_SOLO_ROLLUP_V1",
        "status": "SOLO_SCOUT_SCORED_POSTHOC",
        "run_dir": str(run_dir.resolve()),
        "score_ref": str(out_json.resolve()),
        "packet_count": report.get("packet_count"),
        "solo_call_count": report.get("solo_call_count"),
        "models_per_packet": report.get("models_per_packet"),
        "trace_binding": report.get("trace_binding"),
        "summary_by_model": report.get("summary_by_model"),
        "summary_by_domain_model": report.get("summary_by_domain_model"),
        "packet_collapse_summary": report.get("packet_collapse_summary"),
        "aggregate": dict(aggregate),
        "pair_summary": pair_summary,
        "token_totals": report.get("token_totals"),
        "token_totals_by_model": report.get("token_totals_by_model"),
        "normalization_note": report.get("normalization_note"),
        "claim_boundary": "Solo-failure discovery only. No Holo, no Gov, no judges, no public benchmark claim.",
    }
    write_json(ROLLUP_JSON, rollup)
    ROLLUP_MD.write_text(build_markdown(report, rollup))

    score_md = run_dir / "tier3_fn_targeted_mining_scout_solo_posthoc_score.md"
    score_md.write_text(build_markdown(report, rollup))

    return rollup


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(score(Path(args.run_dir)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
