#!/usr/bin/env python3
"""Hash-lock a Solo-vs-full-Holo KNEW benchmark run directory."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
DEFAULT_RUN_DIR = (
    BENCHMARK_ROOT
    / "hard_allow_fp_5pair_solo_fullholo_knew_benchmark_2026-06-28"
    / "run_20260629T000225Z"
)
EXCLUDED_NAMES = {"RUN_LOCK_MANIFEST.json", "RUN_LOCK_VALIDATION.json"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def locked_files(run_dir: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for path in sorted(item for item in run_dir.rglob("*") if item.is_file()):
        if path.name in EXCLUDED_NAMES:
            continue
        rel = path.relative_to(run_dir)
        files.append(
            {
                "relative_path": str(rel),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )
    return files


def build_lock(run_dir: Path) -> dict[str, Any]:
    benchmark_results = json.loads((run_dir / "benchmark_results.json").read_text())
    solo_results = json.loads((run_dir / "solo_one_shot_results.json").read_text())
    judge_dirs = [path for path in (run_dir / "judges").glob("*") if path.is_dir()] if (run_dir / "judges").exists() else []
    manifest_no_root = {
        "classification": "SOLO_FULLHOLO_KNEW_BENCHMARK_RUN_HASH_LOCK",
        "status": "FROZEN_HASH_LOCKED_PENDING_EXTERNAL_JUDGES"
        if benchmark_results.get("status") != "COMPLETE_WITH_VALID_JUDGES"
        else "FROZEN_HASH_LOCKED_WITH_VALID_JUDGES",
        "benchmark_locked": benchmark_results.get("status") == "COMPLETE_WITH_VALID_JUDGES",
        "hash_locked": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "freeze_root_signature": benchmark_results["freeze_root_signature"],
        "scope": {
            "packet_count": benchmark_results["packet_count"],
            "holo_full_trace_source": benchmark_results["holo_full_trace_source"],
            "holo_full_provider_calls_from_freeze": benchmark_results["holo_full_provider_calls_from_freeze"],
            "solo_one_shot_provider_calls": benchmark_results["solo_one_shot_provider_calls"],
            "knew_only_pass_rule": "Only KNEW passes. LUCKY, WRONG, and CONFUSED fail.",
        },
        "results": {
            "solo_local_knew_passes": benchmark_results["solo_local_knew_passes"],
            "holo_local_knew_passes": benchmark_results["holo_local_knew_passes"],
            "solo_trace_hash": benchmark_results["solo_one_shot_trace_hash"],
            "solo_tokens": solo_results["totals"],
            "judge_status": benchmark_results["status"],
            "judge_count": len(judge_dirs),
        },
        "required_status_invariants": [
            "no Solo rerun after SOLO_ONE_SHOT_TRACE.jsonl is locked",
            "no Holo rerun; Holo traces are sourced from the frozen full-architecture bundle",
            "KNEW is the only passing label",
            "external judges must use judge-only continuation and must not rerun Solo or Holo",
            "after external judges complete, rerun this lock script to include judge outputs",
        ],
        "locked_files": locked_files(run_dir),
    }
    root_signature = sha256_bytes(canonical_json(manifest_no_root).encode("utf-8"))
    manifest = {**manifest_no_root, "root_signature": root_signature}
    (run_dir / "RUN_LOCK_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def validate_lock(run_dir: Path) -> dict[str, Any]:
    manifest = json.loads((run_dir / "RUN_LOCK_MANIFEST.json").read_text())
    for item in manifest["locked_files"]:
        path = run_dir / item["relative_path"]
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"hash mismatch: {item['relative_path']}")
    manifest_no_root = dict(manifest)
    root = manifest_no_root.pop("root_signature")
    recomputed = sha256_bytes(canonical_json(manifest_no_root).encode("utf-8"))
    if recomputed != root:
        raise RuntimeError(f"root mismatch: {recomputed} != {root}")
    validation = {
        "validation_status": "PASS",
        "root_signature": root,
        "locked_file_count": len(manifest["locked_files"]),
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "status": manifest["status"],
        "benchmark_locked": manifest["benchmark_locked"],
    }
    (run_dir / "RUN_LOCK_VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    return validation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    if not args.validate_only:
        manifest = build_lock(run_dir)
        print(json.dumps({"build": "ok", "root_signature": manifest["root_signature"], "run_dir": str(run_dir)}, indent=2, sort_keys=True))
    validation = validate_lock(run_dir)
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
