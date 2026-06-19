from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKET_DIR = Path(__file__).resolve().parent
RUNS_DIR = PACKET_DIR / "runs"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_run_dir() -> Path:
    candidates = [
        path
        for path in RUNS_DIR.iterdir()
        if path.is_dir() and (path / "run_manifest.json").exists()
    ]
    if not candidates:
        raise SystemExit(f"No run manifests found under {RUNS_DIR}")
    return max(candidates, key=lambda path: (path / "run_manifest.json").stat().st_mtime)


def summarize_judges(summary_path: Path | None) -> dict[str, Any] | None:
    if not summary_path or not summary_path.exists():
        return None
    summary = read_json(summary_path)
    pair_rows = []
    all_validation_flags: list[dict[str, Any]] = []
    for pair in summary.get("pair_summaries", []):
        pair_rows.append(
            {
                "solo_condition": pair.get("solo_condition"),
                "holo_mean": pair.get("holo_mean"),
                "solo_mean": pair.get("solo_mean"),
                "gap_holo_minus_solo": pair.get("gap_holo_minus_solo"),
                "primary_holo_mean": pair.get("primary_holo_mean"),
                "primary_solo_mean": pair.get("primary_solo_mean"),
                "primary_gap_holo_minus_solo": pair.get("primary_gap_holo_minus_solo"),
                "primary_judge_observations": pair.get("primary_judge_observations"),
            }
        )
        for row in pair.get("judge_rows", []):
            flags = row.get("validation_flags") or []
            if flags:
                all_validation_flags.append(
                    {
                        "solo_condition": pair.get("solo_condition"),
                        "judge_id": row.get("judge_id"),
                        "judge_provider": row.get("judge_provider"),
                        "validation_flags": flags,
                    }
                )
    return {
        "overall": summary.get("overall"),
        "primary_no_self_dna": summary.get("primary_no_self_dna"),
        "pair_summaries": pair_rows,
        "criterion_gap_holo_minus_solo": summary.get("criterion_gap_holo_minus_solo"),
        "judge_validation_flags": all_validation_flags,
    }


def summarize_condition(condition: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "condition": condition,
        "provider_model": payload.get("provider_model"),
        "final_artifact_path": payload.get("final_artifact_path"),
        "final_sha256": payload.get("final_sha256"),
        "final_word_count": payload.get("final_word_count"),
        "word_count_in_band": payload.get("word_count_in_band"),
        "selected_turn": payload.get("selected_turn"),
        "valid_final": (payload.get("artifact_validity_report") or {}).get("valid"),
        "validity_flags": (payload.get("artifact_validity_report") or {}).get("flags"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest", action="store_true", help="Inspect the latest run folder.")
    parser.add_argument("--run-id", help="Inspect a specific run id.")
    args = parser.parse_args()
    if bool(args.latest) == bool(args.run_id):
        parser.error("Choose exactly one of --latest or --run-id")

    run_dir = latest_run_dir() if args.latest else RUNS_DIR / str(args.run_id)
    manifest_path = run_dir / "run_manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Missing run manifest: {manifest_path}")
    manifest = read_json(manifest_path)

    summary_path = None
    if manifest.get("judge_summary_path"):
        summary_path = Path(manifest["judge_summary_path"])
    elif (run_dir / "judge_score_summary_all_pairs.json").exists():
        summary_path = run_dir / "judge_score_summary_all_pairs.json"

    conditions = {
        name: summarize_condition(name, payload)
        for name, payload in sorted((manifest.get("condition_results") or {}).items())
        if isinstance(payload, dict)
    }

    output = {
        "run_id": manifest.get("run_id", run_dir.name),
        "status": manifest.get("status"),
        "benchmark_credit": manifest.get("benchmark_credit"),
        "public_claim": manifest.get("public_claim"),
        "run_manifest": str(manifest_path),
        "hash_lock_id": (read_json(PACKET_DIR / "hash_lock.json")).get("hash_lock_id")
        if (PACKET_DIR / "hash_lock.json").exists()
        else None,
        "conditions": conditions,
        "provider_call_count": manifest.get("provider_call_count"),
        "total_input_tokens": manifest.get("total_input_tokens"),
        "total_output_tokens": manifest.get("total_output_tokens"),
        "total_latency_ms": manifest.get("total_latency_ms"),
        "counts": manifest.get("counts"),
        "turn_judge_packet_count": manifest.get("turn_judge_packet_count"),
        "turn_judge_status": manifest.get("turn_judge_status"),
        "failures": manifest.get("failures"),
        "overall_gap_holo_minus_solo": manifest.get("overall_gap_holo_minus_solo"),
        "judge_summary_path": str(summary_path) if summary_path else None,
        "judge_summary": summarize_judges(summary_path),
        "error": manifest.get("error"),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
