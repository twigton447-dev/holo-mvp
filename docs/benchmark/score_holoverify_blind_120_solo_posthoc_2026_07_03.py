#!/usr/bin/env python3
"""Post-hoc scorer for the blind-120 same-model solo baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
SCORING_MAP = (
    BENCHMARK_ROOT
    / "holoverify_blind_120_bank_2026_07_03"
    / "holoverify_blind_120_scoring_map_2026_07_03.json"
)
EXPECTED_SCORING_MAP_SHA256 = "b5f3c219c473aa2821540aca7cf84e5fc8d2441f977f69d9df226aad550ed166"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(errors="replace"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(errors="replace").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def score(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    trace_path = run_dir / "TRACE_PROVIDER_CALLS.jsonl"
    runtime_results_path = run_dir / "solo_one_shot_runtime_results.json"
    live_summary_path = run_dir / "solo_one_shot_live_summary.json"
    required = (trace_path, runtime_results_path, live_summary_path)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing required frozen solo trace artifacts: {missing}")

    scoring_map_sha256 = sha256_file(SCORING_MAP)
    if scoring_map_sha256 != EXPECTED_SCORING_MAP_SHA256:
        raise RuntimeError(f"scoring_map_hash_mismatch:{scoring_map_sha256}")

    scoring = load_json(SCORING_MAP)
    truth_by_opaque = {
        row["opaque_runtime_id"]: {
            "truth": row["legacy_truth"],
            "domain": row.get("domain"),
            "pair_id": row.get("pair_id"),
            "legacy_packet_id": row.get("legacy_packet_id"),
        }
        for row in scoring.get("scoring_rows", [])
    }
    runtime = load_json(runtime_results_path)
    provider_rows = load_jsonl(trace_path)

    scored_rows: list[dict[str, Any]] = []
    by_model: dict[str, Counter] = defaultdict(Counter)
    by_domain_model: dict[str, Counter] = defaultdict(Counter)
    packet_to_model_results: dict[str, list[dict[str, Any]]] = defaultdict(list)
    token_totals: dict[str, int] = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    token_totals_by_model: dict[str, dict[str, int]] = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})

    provider_by_call = {row.get("call_number"): row for row in provider_rows}
    for provider in provider_rows:
        model_key = str(provider.get("model_key"))
        for key in token_totals:
            value = provider.get(key)
            if isinstance(value, int):
                token_totals[key] += value
                token_totals_by_model[model_key][key] += value

    for index, row in enumerate(runtime.get("results", []), start=1):
        opaque = row.get("opaque_runtime_id")
        truth_meta = truth_by_opaque.get(opaque, {})
        truth = truth_meta.get("truth")
        verdict = row.get("final_verdict")
        admissible = bool(row.get("admissible"))
        correct = verdict == truth
        knew_admissible = admissible and correct
        if not admissible:
            error_class = "PARSE_OR_ADMISSIBILITY_FAILURE"
        elif verdict not in {"ALLOW", "ESCALATE"}:
            error_class = "UNKNOWN_VERDICT"
        elif correct:
            error_class = "KNEW_ADMISSIBLE"
        elif verdict == "ALLOW" and truth == "ESCALATE":
            error_class = "FALSE_NEGATIVE_ALLOW_ON_ESCALATE"
        elif verdict == "ESCALATE" and truth == "ALLOW":
            error_class = "FALSE_POSITIVE_ESCALATE_ON_ALLOW"
        else:
            error_class = "WRONG_VERDICT"
        model_key = str(row.get("model_key"))
        domain = str(truth_meta.get("domain"))
        scored = {
            "opaque_runtime_id": opaque,
            "domain": truth_meta.get("domain"),
            "pair_id": truth_meta.get("pair_id"),
            "legacy_packet_id": truth_meta.get("legacy_packet_id"),
            "model_key": model_key,
            "provider": row.get("provider"),
            "model": row.get("model"),
            "truth": truth,
            "solo_verdict": verdict,
            "solo_admissible": admissible,
            "solo_correct": correct,
            "solo_knew_admissible": knew_admissible,
            "error_class": error_class,
            "gate_failures": (row.get("gate_result") or {}).get("failures", []),
            "trace_call_number": index,
            "provider_row": provider_by_call.get(index, {}),
        }
        scored_rows.append(scored)
        packet_to_model_results[str(opaque)].append(scored)
        by_model[model_key]["total"] += 1
        by_model[model_key][error_class] += 1
        by_model[model_key]["admissible"] += 1 if admissible else 0
        by_model[model_key]["correct"] += 1 if correct else 0
        by_model[model_key]["knew_admissible"] += 1 if knew_admissible else 0
        by_model[model_key]["false_positive"] += 1 if error_class == "FALSE_POSITIVE_ESCALATE_ON_ALLOW" else 0
        by_model[model_key]["false_negative"] += 1 if error_class == "FALSE_NEGATIVE_ALLOW_ON_ESCALATE" else 0
        domain_key = f"{domain}|{model_key}"
        by_domain_model[domain_key]["total"] += 1
        by_domain_model[domain_key]["knew_admissible"] += 1 if knew_admissible else 0
        by_domain_model[domain_key][error_class] += 1

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

    report = {
        "classification": "HOLOVERIFY_BLIND_120_SOLO_ONE_SHOT_POSTHOC_SCORE_TRACE_BOUND_V1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "scoring_map_loaded_after_trace_hash_binding": True,
        "trace_binding": {
            "trace_provider_calls_sha256": sha256_file(trace_path),
            "runtime_results_sha256": sha256_file(runtime_results_path),
            "live_summary_sha256": sha256_file(live_summary_path),
            "scoring_map_sha256": scoring_map_sha256,
        },
        "packet_count": len(packet_to_model_results),
        "solo_call_count": len(scored_rows),
        "models_per_packet": 3,
        "summary_by_model": {key: dict(counter) for key, counter in by_model.items()},
        "summary_by_domain_model": {key: dict(counter) for key, counter in by_domain_model.items()},
        "packet_collapse_summary": dict(collapse_counts),
        "packet_collapse_rows": sorted(packet_collapse_rows, key=lambda item: str(item["opaque_runtime_id"])),
        "score_rows": scored_rows,
        "token_totals": token_totals,
        "token_totals_by_model": dict(token_totals_by_model),
    }
    write_json(run_dir / "solo_one_shot_posthoc_score_trace_bound_v1.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(score(Path(args.run_dir)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
