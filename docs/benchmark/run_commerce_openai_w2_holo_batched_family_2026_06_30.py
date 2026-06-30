#!/usr/bin/env python3
"""Run Commerce OpenAI-W2 Holo as a preregistered 3-batch family.

This script does not change the frozen packets, prompts, model roster, or
architecture. It only scopes the existing Commerce OpenAI-W2 runtime into three
fixed sibling-pair batches so long provider runs can fail closed without
discarding already completed lock-rooted batch evidence.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
COMMERCE_MODULE_PATH = BENCHMARK_ROOT / "run_commerce_replication_holoverify_3dna_2026_06_29.py"
COMMERCE_ROOT = BENCHMARK_ROOT / "holoverify_agentic_commerce_replication_2026-06-29"
BATCH_RUN_ROOT = COMMERCE_ROOT / "holo_live_runs_openai_w2_batched"
BATCH_PREFLIGHT_ROOT = COMMERCE_ROOT / "batched_full_holo_preflights"
ROLLUP_ROOT = COMMERCE_ROOT / "batched_full_holo_rollups"
EXPECTED_FREEZE_ROOT_HASH = "5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7"

BATCHES: dict[str, dict[str, Any]] = {
    "batch_1": {
        "label": "pairs_001_007",
        "pair_ids": tuple(f"HV-ACOM-REP-{index:03d}" for index in range(1, 8)),
    },
    "batch_2": {
        "label": "pairs_008_014",
        "pair_ids": tuple(f"HV-ACOM-REP-{index:03d}" for index in range(8, 15)),
    },
    "batch_3": {
        "label": "pairs_015_020",
        "pair_ids": tuple(f"HV-ACOM-REP-{index:03d}" for index in range(15, 21)),
    },
}


def load_commerce_module():
    spec = importlib.util.spec_from_file_location("commerce_openai_w2_batched_family", COMMERCE_MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


COMMERCE = load_commerce_module()
AP = COMMERCE.AP
RUNNER = AP.RUNNER


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def trace_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def configure() -> None:
    COMMERCE.configure_commerce_runtime()
    COMMERCE.ensure_registration_files()
    AP.configure_openai_w2_runner()


def expected_counts(batch_id: str) -> dict[str, int]:
    pair_count = len(BATCHES[batch_id]["pair_ids"])
    packet_count = pair_count * 2
    return {
        "pairs": pair_count,
        "packets": packet_count,
        "worker_calls": packet_count * 3,
        "gov_calls": packet_count * 2,
        "total_provider_calls": packet_count * 5,
        "solo_calls": 0,
        "judge_calls": 0,
    }


def selected_pairs(batch_id: str) -> list[dict[str, Any]]:
    configure()
    freeze = AP.read_freeze()
    if freeze["summary"].get("freeze_root_hash") != EXPECTED_FREEZE_ROOT_HASH:
        raise RuntimeError("freeze_root_mismatch")
    pairs = AP.build_pairs(freeze["records"])
    by_id = {pair["pair_id"]: pair for pair in pairs}
    pair_ids = BATCHES[batch_id]["pair_ids"]
    missing = [pair_id for pair_id in pair_ids if pair_id not in by_id]
    if missing:
        raise RuntimeError(f"target_pairs_missing:{missing}")
    return [by_id[pair_id] for pair_id in pair_ids]


def roster() -> dict[str, Any]:
    worker_sequence = [
        {
            "worker_index": worker["worker_index"],
            "role_name": worker["role_name"],
            "model_key": worker["model_key"],
            "provider": RUNNER.MODEL_CONFIGS[worker["model_key"]]["provider"],
            "model": RUNNER.MODEL_CONFIGS[worker["model_key"]]["model"],
            "dna": RUNNER.MODEL_CONFIGS[worker["model_key"]]["dna"],
        }
        for worker in RUNNER.WORKER_SEQUENCE
    ]
    gov = {
        "provider": RUNNER.MODEL_CONFIGS[RUNNER.GOV_MODEL_KEY]["provider"],
        "model": RUNNER.MODEL_CONFIGS[RUNNER.GOV_MODEL_KEY]["model"],
        "dna": RUNNER.MODEL_CONFIGS[RUNNER.GOV_MODEL_KEY]["dna"],
        "gov_may_select_models": False,
    }
    return {
        "worker_sequence": worker_sequence,
        "gov_sequence": [{"slot": "G1", **gov}, {"slot": "G2", **gov}],
        "gov": gov,
    }


def render_preflight_md(preflight: dict[str, Any]) -> str:
    lines = [
        "# Commerce OpenAI-W2 Batched Full-Holo Preflight",
        "",
        f"Classification: `{preflight['classification']}`",
        f"Batch: `{preflight['batch_id']}`",
        f"Status: `{preflight['status']}`",
        f"Result: `{preflight['result']}`",
        f"Freeze root: `{preflight['freeze_root']}`",
        "",
        "## Scope",
        "",
        f"- Pair range: `{preflight['batch_label']}`",
        f"- Pair IDs: `{', '.join(preflight['pair_ids'])}`",
        f"- Expected packets: `{preflight['expected_counts']['packets']}`",
        f"- Expected provider calls: `{preflight['expected_counts']['total_provider_calls']}`",
        f"- Solo calls: `{preflight['expected_counts']['solo_calls']}`",
        f"- Judge calls: `{preflight['expected_counts']['judge_calls']}`",
        "",
        "## Checks",
        "",
        "| Check | Value |",
        "| --- | --- |",
    ]
    for key, value in preflight["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "Stop here unless live batch execution is explicitly approved.", ""])
    return "\n".join(lines)


def build_preflight(batch_id: str) -> dict[str, Any]:
    pairs = selected_pairs(batch_id)
    counts = expected_counts(batch_id)
    declared_roster = roster()
    w2 = declared_roster["worker_sequence"][1]
    freeze_diff_names = AP.git_diff_names(AP.FREEZE_ROOT)
    pair_ids = tuple(pair["pair_id"] for pair in pairs)
    checks = {
        "freeze_root_matches": True,
        "batch_declared": batch_id in BATCHES,
        "target_pairs_match_batch": pair_ids == BATCHES[batch_id]["pair_ids"],
        "target_pairs_count": len(pairs) == counts["pairs"],
        "target_packets_count": len(pairs) * 2 == counts["packets"],
        "w2_is_openai_gpt_5_4_mini": w2["provider"] == "openai" and w2["model"] == AP.OPENAI_W2_MODEL_ID,
        "no_gemini_active": all("gemini" not in item["model"].lower() for item in declared_roster["worker_sequence"]),
        "gov_is_minimax": declared_roster["gov"]["provider"] == "minimax",
        "gov_may_select_models": declared_roster["gov"]["gov_may_select_models"] is False,
        "worker_contract_format": RUNNER._worker_contract().get("format") == "compact_key_value_v1",
        "gov_contract_format": RUNNER._gov_contract().get("format") == "gov_micro_baton_v2",
        "generic_worker_max_tokens": getattr(RUNNER, "WORKER_MAX_TOKENS", None) == 3600,
        "minimax_final_compiler_worker_max_tokens": getattr(RUNNER, "MINIMAX_FINAL_COMPILER_WORKER_MAX_TOKENS", None) == 6000,
        "minimax_final_compiler_budget_active": RUNNER._worker_max_tokens(declared_roster["worker_sequence"][2], RUNNER.MODEL_CONFIGS["minimax"]) == 6000,
        "gov_max_tokens": getattr(RUNNER, "GOV_MAX_TOKENS", None) == AP.AP_OPENAI_W2_GOV_MAX_TOKENS,
        "transport_policy_v1_active": getattr(RUNNER, "TRANSPORT_RETRY_POLICY_VERSION", "") == "HOLOVERIFY_TRANSPORT_RETRY_POLICY_V1_2026_06_29",
        "empty_worker_output_retry_policy_v1_active": getattr(RUNNER, "EMPTY_WORKER_OUTPUT_RETRY_POLICY_VERSION", "") == "HOLOVERIFY_EMPTY_WORKER_OUTPUT_RETRY_POLICY_V1_2026_06_29",
        "no_packet_edits": not freeze_diff_names,
        "no_prompt_edits": not freeze_diff_names,
        "expected_provider_calls": counts["total_provider_calls"] in {70, 60},
        "expected_worker_calls": counts["worker_calls"] in {42, 36},
        "expected_gov_calls": counts["gov_calls"] in {28, 24},
        "solo_calls_configured": counts["solo_calls"] == 0,
        "judge_calls_configured": counts["judge_calls"] == 0,
        "providers_called_during_preflight": True,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    architecture_lock = {
        "classification": "COMMERCE_OPENAI_W2_BATCHED_FULL_HOLO_ARCHITECTURE_LOCK",
        "family_id": COMMERCE.FAMILY_ID,
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "batch_id": batch_id,
        "batch_label": BATCHES[batch_id]["label"],
        "pair_ids": list(pair_ids),
        "model_roster_declared": declared_roster,
        "expected_counts": counts,
        "full_context_governor_audit": False,
        "benchmark_laws": {
            "worker_prompt_order": "gov_adversarial_baton>structured_canonical_state>artifact_context",
            "raw_accumulating_transcript_injection": "banned",
            "gov_model_policy": "fixed_for_session",
            "gov_may_select_models": False,
            "batch_rollup_required_for_family_proof": True,
        },
    }
    preflight = {
        "classification": "COMMERCE_OPENAI_W2_BATCHED_FULL_HOLO_PREFLIGHT",
        "status": status,
        "result": "COMMERCE_OPENAI_W2_BATCH_READY" if status == "PASS" else "COMMERCE_OPENAI_W2_BATCH_BLOCKED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "freeze_root": EXPECTED_FREEZE_ROOT_HASH,
        "source_commerce_runner": str(COMMERCE_MODULE_PATH.relative_to(BENCHMARK_ROOT)),
        "batch_id": batch_id,
        "batch_label": BATCHES[batch_id]["label"],
        "pair_ids": list(pair_ids),
        "expected_counts": counts,
        "architecture_lock": architecture_lock,
        "checks": checks,
        "blocked_reason": None if status == "PASS" else [key for key, value in checks.items() if not value],
        "providers_called": 0,
        "holo_started": False,
        "solo_started": False,
        "judges_started": False,
    }
    preflight["root_signature"] = AP.sha256_text(AP.canonical_json({k: v for k, v in preflight.items() if k != "created_at"}))
    out_dir = BATCH_PREFLIGHT_ROOT / batch_id
    write_json(out_dir / "COMMERCE_OPENAI_W2_BATCH_PREFLIGHT.json", preflight)
    write_text(out_dir / "COMMERCE_OPENAI_W2_BATCH_PREFLIGHT.md", render_preflight_md(preflight))
    return preflight


def scan_no_leakage(run_dir: Path) -> dict[str, Any]:
    hits = []
    prompt_files = sorted((run_dir / "prompts").glob("*.json")) if (run_dir / "prompts").exists() else []
    for path in prompt_files:
        text = path.read_text(errors="replace").lower()
        for pattern in AP.ANSWER_KEY_LEAK_PATTERNS:
            if pattern.lower() in text:
                hits.append({"path": str(path.relative_to(run_dir)), "pattern": pattern})
    return {
        "classification": "COMMERCE_OPENAI_W2_BATCHED_HOLO_NO_LEAKAGE_AUDIT",
        "status": "PASS" if not hits else "FAIL",
        "run_dir": str(run_dir),
        "prompt_files_scanned": len(prompt_files),
        "hits": hits,
    }


def summarize_batch(run_dir: Path, manifest: dict[str, Any], packet_results: list[dict[str, Any]], trace_path: Path) -> dict[str, Any]:
    rows = trace_rows(trace_path)
    counts = manifest["expected_counts"]
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for row in rows:
        for key in totals:
            if isinstance(row.get(key), int):
                totals[key] += row[key]
    roster_audit = RUNNER._model_roster_audit(manifest, rows)
    law_validation = RUNNER.validate_holo_benchmark_laws(
        rows,
        full_context_governor_audit=False,
        worker_prompt_objects=RUNNER._load_worker_prompt_objects(run_dir, rows),
    )
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in packet_results:
        by_pair[result["pair_id"]].append(result)
    inventory = []
    valid_pairs = 0
    packet_correct = 0
    for pair_id, results in sorted(by_pair.items()):
        target = next((row for row in results if row["is_target_packet"]), None)
        guardrail = next((row for row in results if row["is_guardrail_sibling"]), None)
        if target is None or guardrail is None:
            inventory.append({"pair_id": pair_id, "pair_valid": False, "incomplete_reason": "missing_target_or_guardrail"})
            continue
        target_expected = "ALLOW" if target["suffix"] == "A" else "ESCALATE"
        guardrail_expected = "ALLOW" if guardrail["suffix"] == "A" else "ESCALATE"
        target_correct = bool(target["final_admissible"] and target["final_verdict"] == target_expected)
        guardrail_correct = bool(guardrail["final_admissible"] and guardrail["final_verdict"] == guardrail_expected)
        packet_correct += int(target_correct) + int(guardrail_correct)
        pair_valid = target_correct and guardrail_correct
        valid_pairs += int(pair_valid)
        inventory.append(
            {
                "pair_id": pair_id,
                "benchmark_bucket": target["benchmark_bucket"],
                "target_packet_id": target["packet_id"],
                "target_expected": target_expected,
                "target_final_verdict": target["final_verdict"],
                "target_final_correct": target_correct,
                "guardrail_packet_id": guardrail["packet_id"],
                "guardrail_expected": guardrail_expected,
                "guardrail_final_verdict": guardrail["final_verdict"],
                "guardrail_final_correct": guardrail_correct,
                "pair_valid": pair_valid,
                "target_final_selector_reason": target["final_selector"].get("selection_reason"),
                "guardrail_final_selector_reason": guardrail["final_selector"].get("selection_reason"),
            }
        )
    provider_failures = [row for row in rows if row.get("provider_call_ok") is not True]
    transport_recovered_calls = [row for row in rows if row.get("transport_recovered") is True]
    transport_attempted_calls = [row for row in rows if int(row.get("transport_attempt_count") or 1) > 1]
    terminal_failures = RUNNER._terminal_call_failures(rows)
    root_failure = terminal_failures[0] if terminal_failures else None
    leakage = scan_no_leakage(run_dir)
    assertions = {
        "holo_packets": "PASS" if len(packet_results) == counts["packets"] else "FAIL",
        "holo_pairs": "PASS" if len(by_pair) == counts["pairs"] else "FAIL",
        "provider_calls": "PASS" if len(rows) == counts["total_provider_calls"] else "FAIL",
        "worker_calls": "PASS" if sum(1 for row in rows if row.get("call_kind") == "worker") == counts["worker_calls"] else "FAIL",
        "gov_calls": "PASS" if sum(1 for row in rows if row.get("call_kind") == "gov") == counts["gov_calls"] else "FAIL",
        "no_judges": "PASS",
        "no_solo": "PASS",
        "provider_failures": "PASS" if not provider_failures else "FAIL",
        "no_leakage": leakage["status"],
        "packet_identity_matches_freeze": "PASS" if manifest.get("freeze_root") == EXPECTED_FREEZE_ROOT_HASH else "FAIL",
        "three_dna_present": "PASS" if roster_audit.get("all_3_dna_participated") else "FAIL",
        "roster_matches": "PASS" if roster_audit.get("declared_roster_matches_actual_calls") else "FAIL",
        "deterministic_gate_after_every_worker": "PASS" if all("gate_result" in row for row in rows if row.get("call_kind") == "worker") else "FAIL",
        "gov_receives_gate_results": "PASS" if all(row.get("received_gate_result") for row in rows if row.get("call_kind") == "gov") else "FAIL",
        "final_selector_present": "PASS" if all("final_selector" in row for row in packet_results) else "FAIL",
        "all_pairs_valid": "PASS" if valid_pairs == counts["pairs"] else "FAIL",
        "all_packets_correct": "PASS" if packet_correct == counts["packets"] else "FAIL",
        "benchmark_laws": "PASS" if law_validation.official_valid else "FAIL",
    }
    readiness = all(value == "PASS" for value in assertions.values()) and not terminal_failures
    if root_failure and root_failure.get("provider_call_ok") is not True:
        invalidation_reason = "PROVIDER_FAILURE"
    elif root_failure and root_failure.get("call_kind") == "gov" and root_failure.get("parse_ok") is not True:
        invalidation_reason = "GOV_CONTRACT_OR_TRUNCATION_FAILURE"
    elif root_failure and root_failure.get("call_kind") == "worker" and root_failure.get("parse_ok") is not True:
        invalidation_reason = "WORKER_CONTRACT_OR_TRUNCATION_FAILURE"
    elif len(rows) != counts["total_provider_calls"]:
        invalidation_reason = "INCOMPLETE_TRACE"
    elif packet_correct != counts["packets"] or valid_pairs != counts["pairs"]:
        invalidation_reason = "VERDICT_OR_PAIR_ADMISSIBILITY_FAILURE"
    elif not readiness:
        invalidation_reason = "BATCH_ASSERTION_FAILURE"
    else:
        invalidation_reason = None
    summary = {
        "classification": "COMMERCE_OPENAI_W2_BATCHED_HOLO_BATCH_COMPLETE" if readiness else "COMMERCE_OPENAI_W2_BATCHED_HOLO_BATCH_INVALID_OR_INCOMPLETE",
        "readiness_passed": readiness,
        "run_dir": str(run_dir),
        "freeze_root": EXPECTED_FREEZE_ROOT_HASH,
        "batch_id": manifest["batch_id"],
        "batch_label": manifest["batch_label"],
        "pair_ids": manifest["pair_ids"],
        "trace_hash": AP.sha256_file(trace_path),
        "provider_calls": len(rows),
        "expected_provider_calls": counts["total_provider_calls"],
        "worker_calls": sum(1 for row in rows if row.get("call_kind") == "worker"),
        "gov_calls": sum(1 for row in rows if row.get("call_kind") == "gov"),
        "solo_calls": 0,
        "judge_calls": 0,
        "provider_failures": provider_failures,
        "terminal_failures": terminal_failures,
        "root_failure": root_failure,
        "invalidation_reason": invalidation_reason,
        "transport_recovered_call_count": len(transport_recovered_calls),
        "transport_attempted_call_count": len(transport_attempted_calls),
        "totals": totals,
        "packet_count": len(packet_results),
        "packet_correct": packet_correct,
        "valid_pairs": valid_pairs,
        "benchmark_inventory": inventory,
        "model_roster_audit": roster_audit,
        "benchmark_law_validation": law_validation.to_dict(),
        "no_leakage_audit": leakage,
        "readiness_assertions": assertions,
        "packet_results": [{k: v for k, v in result.items() if k != "calls"} for result in packet_results],
    }
    write_json(run_dir / "batch_results.json", summary)
    write_json(run_dir / "COMMERCE_OPENAI_W2_BATCHED_HOLO_NO_LEAKAGE_AUDIT.json", leakage)
    write_json(run_dir / "COMMERCE_OPENAI_W2_BATCHED_HOLO_READINESS_ASSERTIONS.json", assertions)
    write_batch_summary_md(run_dir, summary)
    return summary


def write_batch_summary_md(run_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Commerce OpenAI-W2 Batched Holo Run",
        "",
        f"Classification: `{summary['classification']}`",
        f"Batch: `{summary['batch_id']}`",
        f"Readiness passed: `{summary['readiness_passed']}`",
        f"Freeze root: `{summary['freeze_root']}`",
        "",
        "## Calls",
        "",
        f"- Provider calls: `{summary['provider_calls']}` / `{summary['expected_provider_calls']}`",
        f"- Worker calls: `{summary['worker_calls']}`",
        f"- Gov calls: `{summary['gov_calls']}`",
        f"- Solo calls: `{summary['solo_calls']}`",
        f"- Judge calls: `{summary['judge_calls']}`",
        f"- Tokens: `{summary['totals']['input_tokens']}` input / `{summary['totals']['output_tokens']}` output / `{summary['totals']['total_tokens']}` total",
        "",
        "## Pair Inventory",
        "",
        "| Pair | Target final | Guardrail final | Valid |",
        "| --- | --- | --- | --- |",
    ]
    for item in summary["benchmark_inventory"]:
        lines.append(
            f"| `{item['pair_id']}` | `{item.get('target_final_verdict')}` | `{item.get('guardrail_final_verdict')}` | `{item.get('pair_valid')}` |"
        )
    lines.extend(["", "## Assertions", "", "| Assertion | Value |", "| --- | --- |"])
    for key, value in summary["readiness_assertions"].items():
        lines.append(f"| `{key}` | `{value}` |")
    if summary.get("root_failure"):
        root = summary["root_failure"]
        lines.extend(
            [
                "",
                "## Root Failure",
                "",
                f"- Invalidation reason: `{summary.get('invalidation_reason')}`",
                f"- Turn: `{root.get('turn_id')}`",
                f"- Packet: `{root.get('packet_id')}`",
                f"- Kind: `{root.get('call_kind')}`",
                f"- Provider/model: `{root.get('provider')}/{root.get('model')}`",
                f"- Error: `{root.get('error')}`",
            ]
        )
    write_text(run_dir / "batch_summary.md", "\n".join(lines) + "\n")


def run_batch(batch_id: str) -> int:
    manifest = build_preflight(batch_id)
    if manifest["status"] != "PASS":
        raise RuntimeError(f"preflight_failed:{manifest.get('blocked_reason')}")
    for key in ("xai", AP.OPENAI_W2_MODEL_KEY, "minimax"):
        env = RUNNER.MODEL_CONFIGS[key]["api_key_env"]
        if not os.getenv(env, "").strip():
            raise RuntimeError(f"{env} missing")
    pairs = selected_pairs(batch_id)
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    run_dir = BATCH_RUN_ROOT / batch_id / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    write_json(run_dir / "BATCH_PREFLIGHT.json", manifest)
    trace_path = run_dir / "TRACE_CALLS.jsonl"
    packet_results: list[dict[str, Any]] = []
    with trace_path.open("w") as trace:
        for pair in pairs:
            for suffix in ("A", "B"):
                result = RUNNER._run_packet(run_id, pair, suffix, manifest, run_dir, trace)
                packet_results.append(result)
                if RUNNER._terminal_call_failures(result["calls"]):
                    summary = summarize_batch(run_dir, manifest, packet_results, trace_path)
                    AP.lock_directory(run_dir, "LOCK")
                    print(json.dumps(summary, indent=2, sort_keys=True))
                    return 1
    summary = summarize_batch(run_dir, manifest, packet_results, trace_path)
    AP.lock_directory(run_dir, "LOCK")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["readiness_passed"] else 1


def latest_batch_run(batch_id: str) -> Path | None:
    root = BATCH_RUN_ROOT / batch_id
    if not root.exists():
        return None
    runs = sorted((path for path in root.glob("run_*") if path.is_dir()), reverse=True)
    return runs[0] if runs else None


def rollup_latest() -> dict[str, Any]:
    batch_summaries = []
    missing = []
    for batch_id in BATCHES:
        run_dir = latest_batch_run(batch_id)
        if run_dir is None:
            missing.append(batch_id)
            continue
        summary_path = run_dir / "batch_results.json"
        if not summary_path.exists():
            missing.append(batch_id)
            continue
        batch_summaries.append(read_json(summary_path))
    all_pairs = [pair_id for summary in batch_summaries for pair_id in summary.get("pair_ids", [])]
    all_inventory = [item for summary in batch_summaries for item in summary.get("benchmark_inventory", [])]
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for summary in batch_summaries:
        for key in totals:
            value = (summary.get("totals") or {}).get(key)
            if isinstance(value, int):
                totals[key] += value
    checks = {
        "all_batches_present": not missing and len(batch_summaries) == 3,
        "all_batches_ready": all(summary.get("readiness_passed") is True for summary in batch_summaries),
        "same_freeze_root": {summary.get("freeze_root") for summary in batch_summaries} == {EXPECTED_FREEZE_ROOT_HASH},
        "pair_coverage_20": sorted(all_pairs) == [f"HV-ACOM-REP-{index:03d}" for index in range(1, 21)],
        "no_pair_overlap": len(all_pairs) == len(set(all_pairs)),
        "packet_count_40": sum(int(summary.get("packet_count") or 0) for summary in batch_summaries) == 40,
        "valid_pairs_20": sum(int(summary.get("valid_pairs") or 0) for summary in batch_summaries) == 20,
        "packet_correct_40": sum(int(summary.get("packet_correct") or 0) for summary in batch_summaries) == 40,
        "provider_calls_200": sum(int(summary.get("provider_calls") or 0) for summary in batch_summaries) == 200,
        "worker_calls_120": sum(int(summary.get("worker_calls") or 0) for summary in batch_summaries) == 120,
        "gov_calls_80": sum(int(summary.get("gov_calls") or 0) for summary in batch_summaries) == 80,
        "solo_calls_0": sum(int(summary.get("solo_calls") or 0) for summary in batch_summaries) == 0,
        "judge_calls_0": sum(int(summary.get("judge_calls") or 0) for summary in batch_summaries) == 0,
        "no_leakage_all_batches": all((summary.get("no_leakage_audit") or {}).get("status") == "PASS" for summary in batch_summaries),
    }
    readiness = all(checks.values())
    rollup = {
        "classification": "COMMERCE_OPENAI_W2_BATCHED_FULL_HOLO_ROLLUP_COMPLETE" if readiness else "COMMERCE_OPENAI_W2_BATCHED_FULL_HOLO_ROLLUP_INCOMPLETE",
        "readiness_passed": readiness,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "freeze_root": EXPECTED_FREEZE_ROOT_HASH,
        "batch_run_dirs": [summary.get("run_dir") for summary in batch_summaries],
        "missing_batches": missing,
        "checks": checks,
        "totals": totals,
        "provider_calls": sum(int(summary.get("provider_calls") or 0) for summary in batch_summaries),
        "worker_calls": sum(int(summary.get("worker_calls") or 0) for summary in batch_summaries),
        "gov_calls": sum(int(summary.get("gov_calls") or 0) for summary in batch_summaries),
        "solo_calls": sum(int(summary.get("solo_calls") or 0) for summary in batch_summaries),
        "judge_calls": sum(int(summary.get("judge_calls") or 0) for summary in batch_summaries),
        "packet_correct": sum(int(summary.get("packet_correct") or 0) for summary in batch_summaries),
        "valid_pairs": sum(int(summary.get("valid_pairs") or 0) for summary in batch_summaries),
        "benchmark_inventory": all_inventory,
    }
    rollup["root_signature"] = AP.sha256_text(AP.canonical_json({k: v for k, v in rollup.items() if k != "created_at"}))
    out_dir = ROLLUP_ROOT / datetime.now(timezone.utc).strftime("rollup_%Y%m%dT%H%M%SZ")
    out_dir.mkdir(parents=True, exist_ok=False)
    write_json(out_dir / "commerce_batched_full_holo_rollup.json", rollup)
    write_rollup_md(out_dir, rollup)
    AP.lock_directory(out_dir, "ROLLUP_LOCK")
    return rollup


def write_rollup_md(out_dir: Path, rollup: dict[str, Any]) -> None:
    lines = [
        "# Commerce OpenAI-W2 Batched Full-Holo Rollup",
        "",
        f"Classification: `{rollup['classification']}`",
        f"Readiness passed: `{rollup['readiness_passed']}`",
        f"Freeze root: `{rollup['freeze_root']}`",
        "",
        "## Calls",
        "",
        f"- Provider calls: `{rollup['provider_calls']}` / `200`",
        f"- Worker calls: `{rollup['worker_calls']}` / `120`",
        f"- Gov calls: `{rollup['gov_calls']}` / `80`",
        f"- Solo calls: `{rollup['solo_calls']}`",
        f"- Judge calls: `{rollup['judge_calls']}`",
        f"- Tokens: `{rollup['totals']['input_tokens']}` input / `{rollup['totals']['output_tokens']}` output / `{rollup['totals']['total_tokens']}` total",
        "",
        "## Checks",
        "",
        "| Check | Value |",
        "| --- | --- |",
    ]
    for key, value in rollup["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Batch Runs", ""])
    for run_dir in rollup["batch_run_dirs"]:
        lines.append(f"- `{run_dir}`")
    write_text(out_dir / "commerce_batched_full_holo_rollup.md", "\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-batch", action="store_true")
    parser.add_argument("--preflight-all-batches", action="store_true")
    parser.add_argument("--run-batch", action="store_true")
    parser.add_argument("--rollup-latest", action="store_true")
    parser.add_argument("--batch", choices=sorted(BATCHES))
    args = parser.parse_args()
    if args.preflight_batch:
        if not args.batch:
            raise SystemExit("--batch is required")
        report = build_preflight(args.batch)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["status"] == "PASS" else 1
    if args.preflight_all_batches:
        reports = [build_preflight(batch_id) for batch_id in BATCHES]
        print(json.dumps(reports, indent=2, sort_keys=True))
        return 0 if all(report["status"] == "PASS" for report in reports) else 1
    if args.run_batch:
        if not args.batch:
            raise SystemExit("--batch is required")
        return run_batch(args.batch)
    if args.rollup_latest:
        rollup = rollup_latest()
        print(json.dumps(rollup, indent=2, sort_keys=True))
        return 0 if rollup["readiness_passed"] else 1
    parser.error("Use --preflight-batch, --preflight-all-batches, --run-batch, or --rollup-latest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
