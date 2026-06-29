#!/usr/bin/env python3
"""Hash-freeze the completed HoloVerify 20-pair / 3-DNA run.

The freeze is a file-backed evidence bundle for downstream solo one-shot
comparison. It does not rerun providers and does not mutate the completed run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
HOLO_ROOT = BENCHMARK_ROOT / "holoverify_20pair_3dna_2026-06-29"
DEFAULT_RUN_DIR = HOLO_ROOT / "live_runs" / "run_20260629T052822Z"
DEFAULT_FREEZE_ROOT = HOLO_ROOT / "frozen_complete_run_20260629T052822Z"
LOCK_FILENAMES = {"LOCK_MANIFEST.json", "LOCK_VALIDATION.json", "LOCK_SUMMARY.md"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def copy_file(source: Path, dest: Path, freeze_root: Path) -> dict[str, Any]:
    if not source.exists():
        raise FileNotFoundError(source)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return {
        "relative_path": str(dest.relative_to(freeze_root)),
        "source_path": str(source),
        "sha256": sha256_file(dest),
        "bytes": dest.stat().st_size,
    }


def validate_completed_run(run_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    live_results = json.loads((run_dir / "live_results.json").read_text())
    required_assertions = {
        "hard_allow_valid_pairs": 10,
        "hard_escalate_valid_pairs": 10,
        "total_valid_pairs": 20,
        "three_dna_inside_holoverify": "PASS",
        "declared_roster_matches_actual_calls": "PASS",
        "complete_governance_enforcement": "PASS",
        "deterministic_gate_after_every_worker": "PASS",
        "gov_receives_gate_results": "PASS",
        "artifact_registry_present": "PASS",
        "best_artifact_registry_present": "PASS",
        "pinned_best_artifact_present": "PASS",
        "monotonic_preservation_enforced": "PASS",
        "final_selector_present": "PASS",
        "guardrail_sibling_correct_for_all_pairs": "PASS",
        "external_and_intra_holo_evidence_separated": "PASS",
        "invalid_runs_preserved": "PASS",
    }
    if live_results.get("classification") != "HOLOVERIFY_20PAIR_3DNA_COMPLETE":
        raise RuntimeError(f"unexpected classification: {live_results.get('classification')}")
    if live_results.get("readiness_passed") is not True:
        raise RuntimeError("readiness_passed is not true")
    if live_results.get("benchmark_valid") is not True or live_results.get("score_valid") is not True:
        raise RuntimeError("benchmark_valid/score_valid are not true")
    if live_results.get("provider_calls") != 200 or live_results.get("worker_calls") != 120 or live_results.get("gov_calls") != 80:
        raise RuntimeError("provider call counts do not match 200/120/80")
    if live_results.get("judge_calls") != 0:
        raise RuntimeError("judge_calls must be 0")
    if live_results.get("provider_failures"):
        raise RuntimeError("provider failures present")
    if live_results.get("pre_run_root_signature") != manifest.get("root_signature"):
        raise RuntimeError("pre-run root signature mismatch")
    assertions = live_results.get("readiness_assertions") or {}
    for key, expected in required_assertions.items():
        if assertions.get(key) != expected:
            raise RuntimeError(f"assertion {key} expected {expected}, got {assertions.get(key)}")
    trace_path = run_dir / "TRACE_CALLS.jsonl"
    trace_rows = [line for line in trace_path.read_text().splitlines() if line.strip()]
    if len(trace_rows) != 200:
        raise RuntimeError(f"TRACE_CALLS row count expected 200, got {len(trace_rows)}")
    if sha256_file(trace_path) != live_results.get("trace_hash"):
        raise RuntimeError("trace hash mismatch")
    return live_results


def build_freeze(run_dir: Path, freeze_root: Path, *, force: bool = False) -> dict[str, Any]:
    if freeze_root.exists():
        if not force:
            raise RuntimeError(f"freeze already exists: {freeze_root}")
        shutil.rmtree(freeze_root)
    freeze_root.mkdir(parents=True)

    manifest_source = HOLO_ROOT / "PRE_RUN_MANIFEST.json"
    manifest = json.loads(manifest_source.read_text())
    live_results = validate_completed_run(run_dir, manifest)

    copied_files: list[dict[str, Any]] = []
    copied_files.append(copy_file(manifest_source, freeze_root / "evidence" / "PRE_RUN_MANIFEST.json", freeze_root))
    copied_files.append(copy_file(run_dir / "live_results.json", freeze_root / "evidence" / "holo_run" / "live_results.json", freeze_root))
    copied_files.append(copy_file(run_dir / "live_summary.md", freeze_root / "evidence" / "holo_run" / "live_summary.md", freeze_root))
    copied_files.append(copy_file(run_dir / "TRACE_CALLS.jsonl", freeze_root / "evidence" / "holo_run" / "TRACE_CALLS.jsonl", freeze_root))
    copied_files.append(copy_file(BENCHMARK_ROOT / "run_20pair_holoverify_3dna_2026_06_29.py", freeze_root / "evidence" / "source" / "run_20pair_holoverify_3dna_2026_06_29.py", freeze_root))
    copied_files.append(copy_file(REPO_ROOT / "holo_architecture_invariants.py", freeze_root / "evidence" / "source" / "holo_architecture_invariants.py", freeze_root))
    copied_files.append(copy_file(BENCHMARK_ROOT / "three_mini_seam_scout_2026-06-29" / "AGGREGATE_20_BALANCED_3DNA_CURRENT_FAILURE_CANDIDATES.json", freeze_root / "evidence" / "source" / "AGGREGATE_20_BALANCED_3DNA_CURRENT_FAILURE_CANDIDATES.json", freeze_root))

    packet_records: list[dict[str, Any]] = []
    packet_results_by_id = {row["packet_id"]: row for row in live_results["packet_results"]}
    for record in manifest["packet_records"]:
        packet_id = record["packet_id"]
        payload_source = HOLO_ROOT / record["payload_path"]
        payload_copy = copy_file(payload_source, freeze_root / "payloads" / f"{packet_id}.payload.json", freeze_root)
        copied_files.append(payload_copy)
        packet_result = packet_results_by_id.get(packet_id)
        if not packet_result:
            raise RuntimeError(f"missing packet result: {packet_id}")
        packet_records.append(
            {
                "pair_id": record["pair_id"],
                "packet_id": packet_id,
                "suffix": record["suffix"],
                "expected_verdict_for_local_audit": record["expected_verdict_for_local_gate"],
                "benchmark_bucket": record["benchmark_bucket"],
                "is_target_packet": record["is_target_packet"],
                "payload_ref": payload_copy["relative_path"],
                "payload_sha256": payload_copy["sha256"],
                "payload_canonical_sha256": record["payload_hash"],
                "source_ids": record["source_ids"],
                "knew_terms": record["knew_terms"],
                "holo_final_verdict": packet_result["final_verdict"],
                "holo_final_binding": packet_result["final_binding"],
                "holo_final_admissible": packet_result["final_admissible"],
                "holo_selected_artifact_id": packet_result["final_selector"]["selected_artifact_id"],
                "holo_selection_reason": packet_result["final_selector"]["selection_reason"],
                "external_solo_failure_evidence": packet_result.get("external_solo_failure_evidence") or [],
                "intra_holo_single_dna_miss_evidence": packet_result.get("intra_holo_single_dna_miss_evidence") or [],
            }
        )

    invalid_runs = []
    for run_name in ("run_20260629T042132Z", "run_20260629T044805Z", "run_20260629T050310Z", "run_20260629T052724Z"):
        invalid_dir = HOLO_ROOT / "live_runs" / run_name
        if not invalid_dir.exists():
            continue
        invalid_files = []
        for filename in ("live_results.json", "live_summary.md", "TRACE_CALLS.jsonl"):
            path = invalid_dir / filename
            if path.exists():
                item = copy_file(path, freeze_root / "evidence" / "preserved_invalid_runs" / run_name / filename, freeze_root)
                copied_files.append(item)
                invalid_files.append(item)
        classification = None
        if (invalid_dir / "live_results.json").exists():
            classification = json.loads((invalid_dir / "live_results.json").read_text()).get("classification")
        invalid_runs.append({"run_id": run_name, "classification": classification, "files": invalid_files})

    copied_files = sorted(copied_files, key=lambda item: item["relative_path"])
    manifest_no_root = {
        "classification": "HOLOVERIFY_20PAIR_3DNA_COMPLETE_HASH_FREEZE",
        "status": "FROZEN_FOR_SOLO_ONE_SHOT_BASELINE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "freeze_root": str(freeze_root),
        "source_run_dir": str(run_dir),
        "pre_run_root_signature": live_results["pre_run_root_signature"],
        "holo_trace_hash": live_results["trace_hash"],
        "holo_results_hash": sha256_file(run_dir / "live_results.json"),
        "holo_summary_hash": sha256_file(run_dir / "live_summary.md"),
        "scope": {
            "pairs": 20,
            "packets": 40,
            "holo_provider_calls": 200,
            "holo_worker_calls": 120,
            "holo_gov_calls": 80,
            "judge_calls": 0,
            "solo_rerun_calls_inside_holo": 0,
            "worker_dna": ["xai", "google", "minimax"],
            "gov_model": "minimax/MiniMax-M2.5-highspeed",
        },
        "holo_readiness_assertions": live_results["readiness_assertions"],
        "holo_token_totals": live_results["totals"],
        "packet_records": packet_records,
        "preserved_invalid_runs": invalid_runs,
        "locked_files": copied_files,
        "downstream_rules": [
            "Solo prompts must be built only from payload source context and the neutral answer contract.",
            "Solo prompts must not include Holo traces, Gov batons, readiness assertions, expected verdicts, target/guardrail labels, benchmark buckets, or failure evidence.",
            "Benchmark business_ref values may be scrubbed from solo prompts to prevent A/B suffix leakage; source document contents and doc_ids remain unchanged.",
            "No fallback substitution is allowed for provider failures.",
        ],
    }
    root_signature = sha256_text(canonical_json(manifest_no_root))
    lock = {**manifest_no_root, "root_signature": root_signature}
    (freeze_root / "LOCK_MANIFEST.json").write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n")
    write_summary(freeze_root, lock)
    return lock


def validate_freeze(freeze_root: Path) -> dict[str, Any]:
    lock = json.loads((freeze_root / "LOCK_MANIFEST.json").read_text())
    for item in lock["locked_files"]:
        path = freeze_root / item["relative_path"]
        if not path.exists():
            raise RuntimeError(f"missing locked file: {item['relative_path']}")
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"hash mismatch: {item['relative_path']}")
    lock_without_root = dict(lock)
    root = lock_without_root.pop("root_signature")
    recomputed = sha256_text(canonical_json(lock_without_root))
    if recomputed != root:
        raise RuntimeError(f"root mismatch: {recomputed} != {root}")
    validation = {
        "validation_status": "PASS",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "root_signature": root,
        "locked_file_count": len(lock["locked_files"]),
        "packet_count": len(lock["packet_records"]),
        "holo_trace_hash": lock["holo_trace_hash"],
    }
    (freeze_root / "LOCK_VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    return validation


def write_summary(freeze_root: Path, lock: dict[str, Any]) -> None:
    lines = [
        "# HoloVerify 20-Pair / 3-DNA Freeze",
        "",
        f"Classification: `{lock['classification']}`",
        f"Status: `{lock['status']}`",
        f"Root signature: `{lock['root_signature']}`",
        f"Source run: `{lock['source_run_dir']}`",
        f"Holo trace hash: `{lock['holo_trace_hash']}`",
        "",
        "## Scope",
        "",
        f"- Pairs: `{lock['scope']['pairs']}`",
        f"- Packets: `{lock['scope']['packets']}`",
        f"- Holo provider calls: `{lock['scope']['holo_provider_calls']}`",
        f"- Worker calls: `{lock['scope']['holo_worker_calls']}`",
        f"- Gov calls: `{lock['scope']['holo_gov_calls']}`",
        f"- Judge calls: `{lock['scope']['judge_calls']}`",
        f"- Worker DNA: `{', '.join(lock['scope']['worker_dna'])}`",
        f"- Gov model: `{lock['scope']['gov_model']}`",
        "",
        "## Assertions",
        "",
        "| Assertion | Value |",
        "| --- | --- |",
    ]
    for key, value in lock["holo_readiness_assertions"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Packets", "", "| Packet | Expected For Local Audit | Holo Final | Selection |", "| --- | --- | --- | --- |"])
    for record in lock["packet_records"]:
        lines.append(
            f"| `{record['packet_id']}` | `{record['expected_verdict_for_local_audit']}` | `{record['holo_final_verdict']}` | `{record['holo_selection_reason']}` |"
        )
    (freeze_root / "LOCK_SUMMARY.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    parser.add_argument("--freeze-root", default=str(DEFAULT_FREEZE_ROOT))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    freeze_root = Path(args.freeze_root)
    if not args.validate_only:
        lock = build_freeze(Path(args.run_dir), freeze_root, force=args.force)
        print(json.dumps({"build": "ok", "freeze_root": str(freeze_root), "root_signature": lock["root_signature"]}, indent=2, sort_keys=True))
    validation = validate_freeze(freeze_root)
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
