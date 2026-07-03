#!/usr/bin/env python3
"""Post-hoc scorer for the blind-120 11-packet workers-only ablation."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
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
    worker_trace_path = run_dir / "TRACE_WORKER_ROWS.jsonl"
    runtime_results_path = run_dir / "workers_only_11pkt_runtime_results.json"
    live_summary_path = run_dir / "workers_only_11pkt_live_summary.json"
    required = (trace_path, worker_trace_path, runtime_results_path, live_summary_path)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing required frozen workers-only trace artifacts: {missing}")

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
    worker_rows = load_jsonl(worker_trace_path)

    scored_rows: list[dict[str, Any]] = []
    correct = 0
    failure_class_counts: Counter[str] = Counter()
    token_totals: dict[str, int] = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    token_totals_by_model: dict[str, dict[str, int]] = {}
    for provider in provider_rows:
        model_key = str(provider.get("model_key"))
        bucket = token_totals_by_model.setdefault(model_key, {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
        for key in token_totals:
            value = provider.get(key)
            if isinstance(value, int):
                token_totals[key] += value
                bucket[key] += value

    for row in runtime.get("results", []):
        opaque = row.get("opaque_runtime_id")
        truth_meta = truth_by_opaque.get(opaque, {})
        truth = truth_meta.get("truth")
        verdict = row.get("final_verdict")
        admissible = bool(row.get("final_admissible"))
        correct_row = admissible and verdict == truth
        correct += 1 if correct_row else 0
        if not admissible:
            failure_class = "PARSE_OR_ADMISSIBILITY_FAILURE"
        elif verdict == truth:
            failure_class = "KNEW_ADMISSIBLE"
        elif verdict == "ESCALATE" and truth == "ALLOW":
            failure_class = "FALSE_POSITIVE_ESCALATE_ON_ALLOW"
        elif verdict == "ALLOW" and truth == "ESCALATE":
            failure_class = "FALSE_NEGATIVE_ALLOW_ON_ESCALATE"
        else:
            failure_class = "WRONG_VERDICT"
        failure_class_counts[failure_class] += 1
        scored_rows.append(
            {
                "opaque_runtime_id": opaque,
                "domain": truth_meta.get("domain"),
                "pair_id": truth_meta.get("pair_id"),
                "legacy_packet_id": truth_meta.get("legacy_packet_id"),
                "truth": truth,
                "final_verdict": verdict,
                "final_admissible": admissible,
                "correct": correct_row,
                "failure_class": failure_class,
                "final_worker_role": row.get("final_worker_role"),
                "final_selection_policy": row.get("final_selection_policy"),
            }
        )

    report = {
        "classification": "HOLOVERIFY_BLIND_120_11PKT_WORKERS_ONLY_POSTHOC_SCORE_TRACE_BOUND_V1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "scoring_map_loaded_after_trace_hash_binding": True,
        "trace_binding": {
            "trace_provider_calls_sha256": sha256_file(trace_path),
            "trace_worker_rows_sha256": sha256_file(worker_trace_path),
            "runtime_results_sha256": sha256_file(runtime_results_path),
            "live_summary_sha256": sha256_file(live_summary_path),
            "scoring_map_sha256": scoring_map_sha256,
        },
        "packet_count": len(scored_rows),
        "correct_count": correct,
        "incorrect_count": len(scored_rows) - correct,
        "failure_class_counts": dict(failure_class_counts),
        "score_rows": scored_rows,
        "worker_row_count": len(worker_rows),
        "provider_call_count": len(provider_rows),
        "token_totals": token_totals,
        "token_totals_by_model": token_totals_by_model,
        "claim_boundary": {
            "fresh_public_claims_allowed": False,
            "ablation_evidence_only": True,
            "false_negative_claim_allowed": False,
            "truth_side": "ALLOW_ONLY_TARGET_SET"
        },
    }
    write_json(run_dir / "workers_only_11pkt_posthoc_score_trace_bound_v1.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(score(Path(args.run_dir)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
