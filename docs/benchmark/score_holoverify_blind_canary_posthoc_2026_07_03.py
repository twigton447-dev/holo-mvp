#!/usr/bin/env python3
"""Post-hoc scorer for the HoloVerify blind canary.

This script intentionally lives outside the live provider wrapper. The live
wrapper freezes runtime traces only; this scorer may be run after trace freeze
to load the hidden scoring map and bind the score artifact to exact trace
hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
SCORING_MAP = BENCHMARK_ROOT / "holoverify_blind_canary_scoring_map_2026_07_02.json"
EXPECTED_SCORING_MAP_SHA256 = "5bb6fea5c3f2d72ae0b092eb168aeebc6ab4dcd6bc897b784c563dc455822c2b"


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


def posthoc_score(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    trace_calls = run_dir / "TRACE_CALLS.jsonl"
    provider_trace = run_dir / "TRACE_PROVIDER_CALLS.jsonl"
    runtime_results = run_dir / "blind_canary_runtime_results.json"
    summary_path = run_dir / "blind_canary_live_summary.json"
    required = (trace_calls, provider_trace, runtime_results, summary_path)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing required frozen trace artifacts: {missing}")

    trace_hashes = {
        "trace_calls_sha256": sha256_file(trace_calls),
        "trace_provider_calls_sha256": sha256_file(provider_trace),
        "runtime_results_sha256": sha256_file(runtime_results),
        "live_summary_sha256": sha256_file(summary_path),
    }

    scoring_map_sha256 = sha256_file(SCORING_MAP)
    if scoring_map_sha256 != EXPECTED_SCORING_MAP_SHA256:
        raise RuntimeError(f"scoring_map_hash_mismatch:{scoring_map_sha256}")

    scoring = load_json(SCORING_MAP)
    runtime_result = load_json(runtime_results)
    provider_rows = load_jsonl(provider_trace)
    truth_by_opaque = {
        row["opaque_runtime_id"]: row["legacy_truth"]
        for row in scoring.get("scoring_rows", [])
    }

    scored_rows: list[dict[str, Any]] = []
    correct = 0
    for row in runtime_result.get("results", []):
        packet_id = row.get("packet_id")
        verdict = (row.get("final") or {}).get("verdict")
        truth = truth_by_opaque.get(packet_id)
        is_correct = verdict == truth
        correct += 1 if is_correct else 0
        scored_rows.append(
            {
                "opaque_runtime_id": packet_id,
                "final_verdict": verdict,
                "posthoc_truth": truth,
                "correct": is_correct,
            }
        )

    token_totals: dict[str, int] = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    provider_token_totals: dict[str, dict[str, int]] = {}
    for row in provider_rows:
        provider = str(row.get("provider"))
        bucket = provider_token_totals.setdefault(provider, {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
        for key in token_totals:
            value = row.get(key)
            if isinstance(value, int):
                token_totals[key] += value
                bucket[key] += value

    report = {
        "classification": "HOLOVERIFY_BLIND_CANARY_POSTHOC_SCORE_TRACE_BOUND_V1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "scoring_map_loaded_after_trace_hash_binding": True,
        "trace_binding": {
            **trace_hashes,
            "scoring_map_sha256": scoring_map_sha256,
        },
        "packet_count": len(scored_rows),
        "correct_count": correct,
        "incorrect_count": len(scored_rows) - correct,
        "score_rows": scored_rows,
        "token_totals": token_totals,
        "provider_token_totals": provider_token_totals,
    }
    write_json(run_dir / "blind_canary_posthoc_score_trace_bound_v1.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(posthoc_score(Path(args.run_dir)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
