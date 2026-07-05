#!/usr/bin/env python3
"""Build the five-pair hard-ALLOW false-positive freeze bundle.

This is a local evidence freeze, not public benchmark locking. Official
benchmark locking still requires independent adjudication.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
FREEZE_ROOT = BENCHMARK_ROOT / "hard_allow_fp_5pair_full_arch_freeze_2026-06-28"
EVIDENCE_ROOT = FREEZE_ROOT / "evidence"

PAIRS = [
    {
        "pair_id": "HV-KITC-021",
        "full_arch_dir": BENCHMARK_ROOT / "full_holoverify_arch_kitc_021_2026-06-28",
        "run_id": "run_20260628T233949Z",
        "hard_allow_packet": "BAL100-BEC-SUBTLE-CLOSEOUT-021-A",
        "escalate_packet": "BAL100-BEC-SUBTLE-CLOSEOUT-021-B",
        "expected_allow_binding": "EXACT_HOLD_CLOSEOUT_CLOSED",
        "expected_escalate_binding": "HOLD_CLASS_MISMATCH",
        "failure_class": ["source-boundary hard ALLOW", "FP_EXCEPTION_PATH_FREEZE", "SCOPE_READING"],
    },
    {
        "pair_id": "HV-KITC-022",
        "full_arch_dir": BENCHMARK_ROOT / "full_holoverify_arch_kitc_022_2026-06-28",
        "run_id": "run_20260628T234645Z",
        "hard_allow_packet": "BAL100-BEC-SUBTLE-CLOSEOUT-022-A",
        "escalate_packet": "BAL100-BEC-SUBTLE-CLOSEOUT-022-B",
        "expected_allow_binding": "EXACT_ACTIVATION_DEPENDENCY_CLOSED",
        "expected_escalate_binding": "SITE_AND_USE_CLASS_MISMATCH",
        "failure_class": ["source-boundary hard ALLOW", "FP_EXCEPTION_PATH_FREEZE", "SCOPE_READING"],
        "preserved_invalid_run_id": "run_20260628T234411Z",
        "hardening_note": "Initial replay failed closed because the deterministic gate treated any mention of 18-L as contamination, even when it was only a rejected contrast. The gate now fails 18-L only when it contaminates binding, citation, or open-blocker fields for the hard-ALLOW sibling.",
    },
    {
        "pair_id": "HV-KITC-042",
        "full_arch_dir": BENCHMARK_ROOT / "full_holoverify_arch_kitc_042_2026-06-28",
        "run_id": "run_20260628T233631Z",
        "hard_allow_packet": "HV-KITC-042-A",
        "escalate_packet": "HV-KITC-042-B",
        "expected_allow_binding": "EXACT_EXECUTION_RELEASE_CLOSED",
        "expected_escalate_binding": "EXECUTION_RELEASE_PENDING",
        "failure_class": ["FP_EXCEPTION_PATH_FREEZE", "SCOPE_READING"],
    },
    {
        "pair_id": "HV-KITC-047",
        "full_arch_dir": BENCHMARK_ROOT / "full_holoverify_arch_kitc_047_2026-06-28",
        "run_id": "run_20260628T232707Z",
        "hard_allow_packet": "HV-KITC-047-A",
        "escalate_packet": "HV-KITC-047-B",
        "expected_allow_binding": "EXACT_EXCEPTION_CLOSED",
        "expected_escalate_binding": "CONSIGNEE_ROLE_MISMATCH",
        "failure_class": ["FP_EXCEPTION_PATH_FREEZE", "ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW"],
    },
    {
        "pair_id": "HV-KITC-082",
        "full_arch_dir": BENCHMARK_ROOT / "full_holoverify_arch_kitc_082_2026-06-28",
        "run_id": "run_20260628T232009Z",
        "hard_allow_packet": "HV-KITC-082-A",
        "escalate_packet": "HV-KITC-082-B",
        "expected_allow_binding": "CURRENT_IRB_CONSENT_CLOSED",
        "expected_escalate_binding": "CONSENT_STATUS_PENDING",
        "failure_class": ["FP_EXCEPTION_PATH_FREEZE", "SCOPE_READING", "ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW"],
    },
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def copy_evidence(source: Path, dest: Path) -> dict[str, Any]:
    if not source.exists():
        raise FileNotFoundError(source)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    rel = dest.relative_to(FREEZE_ROOT)
    return {
        "relative_path": str(rel),
        "source_path": str(source),
        "sha256": sha256_file(dest),
        "bytes": dest.stat().st_size,
    }


def selected_artifact_record(run_dir: Path, packet_result: dict[str, Any]) -> tuple[dict[str, Any], Path]:
    selected_id = packet_result["final_selector"]["selected_artifact_id"]
    for artifact in packet_result["artifact_registry"]:
        if artifact["artifact_id"] == selected_id:
            return artifact, run_dir / artifact["full_output_ref"]
    raise RuntimeError(f"selected artifact not found: {selected_id}")


def validate_pair(pair: dict[str, Any], live_results: dict[str, Any]) -> list[dict[str, Any]]:
    if live_results.get("benchmark_locked") is not False:
        raise RuntimeError(f"{pair['pair_id']} benchmark_locked should be false")
    if live_results.get("post_generation_status") != "full_arch_candidate_pair_pending_judge":
        raise RuntimeError(f"{pair['pair_id']} unexpected post_generation_status")
    expected_counts = {
        "provider_calls": 10,
        "worker_calls": 6,
        "holo_gov_calls": 4,
        "solo_rerun_calls": 0,
        "judge_calls": 0,
    }
    for key, expected in expected_counts.items():
        if live_results.get(key) != expected:
            raise RuntimeError(f"{pair['pair_id']} {key} expected {expected}, got {live_results.get(key)}")

    results = {row["packet_id"]: row for row in live_results["packet_results"]}
    allow = results[pair["hard_allow_packet"]]
    escalate = results[pair["escalate_packet"]]
    if allow["final_verdict"] != "ALLOW" or allow["final_binding"] != pair["expected_allow_binding"] or allow["final_admissible"] is not True:
        raise RuntimeError(f"{pair['pair_id']} hard ALLOW sibling failed validation")
    if escalate["final_verdict"] != "ESCALATE" or escalate["final_binding"] != pair["expected_escalate_binding"] or escalate["final_admissible"] is not True:
        raise RuntimeError(f"{pair['pair_id']} ESCALATE sibling failed validation")
    return [allow, escalate]


def build() -> dict[str, Any]:
    if FREEZE_ROOT.exists():
        shutil.rmtree(FREEZE_ROOT)
    EVIDENCE_ROOT.mkdir(parents=True)

    freeze_files: list[dict[str, Any]] = []
    pair_records: list[dict[str, Any]] = []
    totals = {
        "provider_calls": 0,
        "worker_calls": 0,
        "holo_gov_calls": 0,
        "solo_rerun_calls": 0,
        "judge_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }

    for pair in PAIRS:
        pair_dir = pair["full_arch_dir"]
        run_dir = pair_dir / "live_runs" / pair["run_id"]
        live_results_path = run_dir / "live_results.json"
        live_results = json.loads(live_results_path.read_text())
        allow_result, escalate_result = validate_pair(pair, live_results)

        pair_evidence_dir = EVIDENCE_ROOT / pair["pair_id"]
        copied_files = [
            copy_evidence(pair_dir / "PRE_RUN_MANIFEST.json", pair_evidence_dir / "PRE_RUN_MANIFEST.json"),
            copy_evidence(live_results_path, pair_evidence_dir / pair["run_id"] / "live_results.json"),
            copy_evidence(run_dir / "live_summary.md", pair_evidence_dir / pair["run_id"] / "live_summary.md"),
            copy_evidence(run_dir / "TRACE_CALLS.jsonl", pair_evidence_dir / pair["run_id"] / "TRACE_CALLS.jsonl"),
        ]

        packet_records: list[dict[str, Any]] = []
        for kind, packet_result in (("hard_allow", allow_result), ("escalate", escalate_result)):
            artifact_record, artifact_path = selected_artifact_record(run_dir, packet_result)
            payload_path = pair_dir / "frozen_packets" / f"{packet_result['packet_id']}.payload.json"
            payload_copy = copy_evidence(payload_path, pair_evidence_dir / "payloads" / payload_path.name)
            artifact_copy = copy_evidence(artifact_path, pair_evidence_dir / "selected_artifacts" / artifact_path.name)
            copied_files.extend([payload_copy, artifact_copy])
            packet_records.append(
                {
                    "kind": kind,
                    "packet_id": packet_result["packet_id"],
                    "final_verdict": packet_result["final_verdict"],
                    "final_binding": packet_result["final_binding"],
                    "final_admissible": packet_result["final_admissible"],
                    "selected_artifact_id": packet_result["final_selector"]["selected_artifact_id"],
                    "selection_reason": packet_result["final_selector"]["selection_reason"],
                    "payload_hash": payload_copy["sha256"],
                    "selected_artifact_hash": artifact_copy["sha256"],
                    "artifact_gate_passed": artifact_record["gate_passed"],
                    "artifact_gate_failures": artifact_record["gate_failures"],
                }
            )

        invalid_run_record = None
        if pair.get("preserved_invalid_run_id"):
            invalid_run_dir = pair_dir / "live_runs" / pair["preserved_invalid_run_id"]
            invalid_files = [
                copy_evidence(invalid_run_dir / "live_results.json", pair_evidence_dir / pair["preserved_invalid_run_id"] / "live_results.json"),
                copy_evidence(invalid_run_dir / "live_summary.md", pair_evidence_dir / pair["preserved_invalid_run_id"] / "live_summary.md"),
                copy_evidence(invalid_run_dir / "TRACE_CALLS.jsonl", pair_evidence_dir / pair["preserved_invalid_run_id"] / "TRACE_CALLS.jsonl"),
            ]
            copied_files.extend(invalid_files)
            invalid_data = json.loads((invalid_run_dir / "live_results.json").read_text())
            invalid_run_record = {
                "run_id": pair["preserved_invalid_run_id"],
                "classification": invalid_data.get("classification"),
                "post_generation_status": invalid_data.get("post_generation_status"),
                "provider_calls": invalid_data.get("provider_calls"),
                "trace_hash": invalid_data.get("trace_hash"),
                "hardening_note": pair.get("hardening_note"),
            }

        freeze_files.extend(copied_files)
        for key in ("provider_calls", "worker_calls", "holo_gov_calls", "solo_rerun_calls", "judge_calls"):
            totals[key] += live_results[key]
        for key in ("input_tokens", "output_tokens", "total_tokens"):
            totals[key] += live_results["totals"][key]

        pair_records.append(
            {
                "pair_id": pair["pair_id"],
                "run_id": pair["run_id"],
                "status": "FROZEN_PENDING_JUDGE",
                "benchmark_locked": False,
                "failure_class": pair["failure_class"],
                "pre_run_root_signature": live_results["pre_run_root_signature"],
                "trace_hash": live_results["trace_hash"],
                "tokens": live_results["totals"],
                "packets": packet_records,
                "preserved_invalid_run": invalid_run_record,
            }
        )

    freeze_files = sorted(freeze_files, key=lambda row: row["relative_path"])
    manifest_no_root = {
        "classification": "HARD_ALLOW_FP_5PAIR_FULL_ARCH_FREEZE",
        "status": "FROZEN_PENDING_JUDGE_NOT_BENCHMARK_LOCKED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_locked": False,
        "official_judging_status": "PENDING",
        "scope": {
            "goal": "Freeze five hard-ALLOW false-positive rescue pairs with matching ESCALATE siblings.",
            "pair_count": len(pair_records),
            "packet_count": len(pair_records) * 2,
            "hard_allow_siblings": len(pair_records),
            "escalate_siblings": len(pair_records),
            "architecture": "Full HoloVerify architecture: worker turns, state brief, Gov sandwich, per-worker gates, artifact registry, pinned best, final selector, trace/accounting.",
            "not_public_benchmark_locked_until": "independent full-gated adjudication is completed over the frozen traces",
        },
        "required_status_invariants": [
            "each hard-ALLOW sibling final_verdict == ALLOW",
            "each ESCALATE sibling final_verdict == ESCALATE",
            "each selected artifact is admissible",
            "each pair has 10 provider calls, 6 worker calls, 4 real Gov calls, 0 Solo reruns, 0 judge calls",
            "no model fallback or substitution is recorded in the locked live results",
        ],
        "totals": totals,
        "pairs": pair_records,
        "freeze_files": freeze_files,
    }
    root_signature = sha256_bytes(canonical_json(manifest_no_root).encode("utf-8"))
    manifest = {**manifest_no_root, "root_signature": root_signature}
    (FREEZE_ROOT / "LOCK_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    summary_lines = [
        "# Hard ALLOW FP 5-Pair Full-Arch Freeze",
        "",
        "Classification: `HARD_ALLOW_FP_5PAIR_FULL_ARCH_FREEZE`",
        "Status: `FROZEN_PENDING_JUDGE_NOT_BENCHMARK_LOCKED`",
        f"Root signature: `{root_signature}`",
        "",
        "This freezes five hard-ALLOW false-positive rescue pairs and their ESCALATE guardrail siblings.",
        "It is not public benchmark-locked until independent full-gated judging is completed over these frozen traces.",
        "",
        "## Counts",
        "",
        f"- Pairs: `{len(pair_records)}`",
        f"- Packets: `{len(pair_records) * 2}`",
        f"- Hard ALLOW siblings: `{len(pair_records)}`",
        f"- ESCALATE siblings: `{len(pair_records)}`",
        f"- Provider calls: `{totals['provider_calls']}`",
        f"- Worker calls: `{totals['worker_calls']}`",
        f"- Gov calls: `{totals['holo_gov_calls']}`",
        f"- Solo rerun calls: `{totals['solo_rerun_calls']}`",
        f"- Judge calls: `{totals['judge_calls']}`",
        f"- Tokens: `{totals['input_tokens']}` input / `{totals['output_tokens']}` output / `{totals['total_tokens']}` total",
        "",
        "## Locked Pairs",
        "",
        "| Pair | Hard ALLOW sibling | ALLOW binding | ESCALATE sibling | ESCALATE binding | Run |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for pair in pair_records:
        hard = next(row for row in pair["packets"] if row["kind"] == "hard_allow")
        esc = next(row for row in pair["packets"] if row["kind"] == "escalate")
        summary_lines.append(
            f"| `{pair['pair_id']}` | `{hard['packet_id']}` | `{hard['final_binding']}` | `{esc['packet_id']}` | `{esc['final_binding']}` | `{pair['run_id']}` |"
        )
    summary_lines.extend(
        [
            "",
            "## Hardening Evidence",
            "",
            "`HV-KITC-022` preserves invalid run `run_20260628T234411Z` as a gate-hardening trace. It failed closed before the deterministic gate was patched to distinguish rejected contrast text from binding/citation contamination.",
            "",
            "## Validation",
            "",
            "Run `python3 docs/benchmark/build_hard_allow_fp_5pair_freeze_2026_06_28.py --validate-only` to recompute file hashes and the root signature.",
        ]
    )
    (FREEZE_ROOT / "LOCK_SUMMARY.md").write_text("\n".join(summary_lines) + "\n")
    return manifest


def validate() -> dict[str, Any]:
    manifest_path = FREEZE_ROOT / "LOCK_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    root = manifest["root_signature"]
    for item in manifest["freeze_files"]:
        path = FREEZE_ROOT / item["relative_path"]
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"hash mismatch: {item['relative_path']}")
    manifest_no_root = dict(manifest)
    manifest_no_root.pop("root_signature")
    recomputed = sha256_bytes(canonical_json(manifest_no_root).encode("utf-8"))
    if recomputed != root:
        raise RuntimeError(f"root mismatch: {recomputed} != {root}")
    validation = {
        "validation_status": "PASS",
        "root_signature": root,
        "freeze_file_count": len(manifest["freeze_files"]),
        "pair_count": manifest["scope"]["pair_count"],
        "packet_count": manifest["scope"]["packet_count"],
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }
    (FREEZE_ROOT / "LOCK_VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    return validation


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if not args.validate_only:
        manifest = build()
        print(json.dumps({"build": "ok", "freeze_root": str(FREEZE_ROOT), "root_signature": manifest["root_signature"]}, indent=2, sort_keys=True))
    validation = validate()
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
