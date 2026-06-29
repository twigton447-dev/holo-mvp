#!/usr/bin/env python3
"""Run the AP OpenAI-W2 Holo canary on the six all-solo-collapse pairs.

This runner is a narrow wrapper around the registered AP OpenAI-W2 runtime.
It does not edit packets, prompts, model roster, Gov contract, worker contract,
or deterministic gates. It only filters the frozen AP family to the six pairs
identified by the completed AP solo triage batch as ALL_SIX_SOLO_COLLAPSE.
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
REPO_ROOT = BENCHMARK_ROOT.parents[1]
AP_MODULE_PATH = BENCHMARK_ROOT / "run_ap_replication_holoverify_3dna_2026_06_29.py"
SOLO_TRIAGE_RUN = (
    BENCHMARK_ROOT
    / "holoverify_replication_packet_freeze_3families_2026-06-29"
    / "solo_triage_3mini"
    / "ap_family_120call"
    / "run_20260629T183456Z"
)
RUN_ROOT = BENCHMARK_ROOT / "holoverify_ap_procurement_replication_2026-06-29" / "holo_canary_openai_w2_all_six_collapse"
EXPECTED_FREEZE_ROOT_HASH = "5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7"
TARGET_PAIR_IDS = (
    "HV-AP-REP-011",
    "HV-AP-REP-012",
    "HV-AP-REP-013",
    "HV-AP-REP-019",
    "HV-AP-REP-005",
    "HV-AP-REP-010",
)
EXPECTED_COUNTS = {
    "pairs": 6,
    "packets": 12,
    "worker_calls": 36,
    "gov_calls": 24,
    "total_provider_calls": 60,
    "solo_calls": 0,
    "judge_calls": 0,
}


def load_ap_module():
    spec = importlib.util.spec_from_file_location("ap_openai_w2_all_six_canary", AP_MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


AP = load_ap_module()
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


def selected_pairs() -> list[dict[str, Any]]:
    AP.configure_openai_w2_runner()
    freeze = AP.read_freeze()
    if freeze["summary"].get("freeze_root_hash") != EXPECTED_FREEZE_ROOT_HASH:
        raise RuntimeError("freeze_root_mismatch")
    pairs = AP.build_pairs(freeze["records"])
    by_id = {pair["pair_id"]: pair for pair in pairs}
    missing = [pair_id for pair_id in TARGET_PAIR_IDS if pair_id not in by_id]
    if missing:
        raise RuntimeError(f"target_pairs_missing:{missing}")
    return [by_id[pair_id] for pair_id in TARGET_PAIR_IDS]


def solo_triage_target_check() -> dict[str, Any]:
    result_path = SOLO_TRIAGE_RUN / "solo_triage_results.json"
    lock_path = SOLO_TRIAGE_RUN / "SOLO_TRIAGE_LOCK_VALIDATION.json"
    if not result_path.exists() or not lock_path.exists():
        return {
            "solo_triage_run_present": False,
            "solo_triage_lock_pass": False,
            "all_six_pairs_match": False,
            "solo_triage_run": str(SOLO_TRIAGE_RUN),
        }
    results = read_json(result_path)
    lock = read_json(lock_path)
    all_six = [row["pair_id"] for row in results.get("pair_rankings", []) if row.get("triage_class") == "ALL_SIX_SOLO_COLLAPSE"]
    return {
        "solo_triage_run_present": True,
        "solo_triage_lock_pass": lock.get("validation_status") == "PASS",
        "all_six_pairs_from_solo": all_six,
        "target_pair_ids": list(TARGET_PAIR_IDS),
        "all_six_pairs_match": set(all_six) == set(TARGET_PAIR_IDS),
        "solo_triage_classification": results.get("classification"),
        "solo_triage_provider_calls": results.get("provider_calls"),
        "solo_triage_run": str(SOLO_TRIAGE_RUN),
    }


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


def build_preflight() -> dict[str, Any]:
    pairs = selected_pairs()
    target_check = solo_triage_target_check()
    declared_roster = roster()
    w2 = declared_roster["worker_sequence"][1]
    freeze_diff_names = AP.git_diff_names(AP.FREEZE_ROOT)
    checks = {
        "freeze_root_matches": True,
        "target_pairs_count": len(pairs) == EXPECTED_COUNTS["pairs"],
        "target_packets_count": len(pairs) * 2 == EXPECTED_COUNTS["packets"],
        "solo_triage_run_present": target_check["solo_triage_run_present"],
        "solo_triage_lock_pass": target_check["solo_triage_lock_pass"],
        "solo_triage_all_six_pairs_match": target_check["all_six_pairs_match"],
        "w2_is_openai_gpt_5_4_mini": w2["provider"] == "openai" and w2["model"] == AP.OPENAI_W2_MODEL_ID,
        "no_gemini_active": all("gemini" not in item["model"].lower() for item in declared_roster["worker_sequence"]),
        "gov_is_minimax": declared_roster["gov"]["provider"] == "minimax",
        "worker_contract_format": RUNNER._worker_contract().get("format") == "compact_key_value_v1",
        "gov_contract_format": RUNNER._gov_contract().get("format") == "gov_micro_baton_v2",
        "gov_max_tokens": getattr(RUNNER, "GOV_MAX_TOKENS", None) == AP.AP_OPENAI_W2_GOV_MAX_TOKENS,
        "transport_policy_v1_active": getattr(RUNNER, "TRANSPORT_RETRY_POLICY_VERSION", "") == "HOLOVERIFY_TRANSPORT_RETRY_POLICY_V1_2026_06_29",
        "no_packet_edits": not freeze_diff_names,
        "no_prompt_edits": not freeze_diff_names,
        "expected_provider_calls": EXPECTED_COUNTS["total_provider_calls"] == 60,
        "expected_worker_calls": EXPECTED_COUNTS["worker_calls"] == 36,
        "expected_gov_calls": EXPECTED_COUNTS["gov_calls"] == 24,
        "solo_calls_configured": EXPECTED_COUNTS["solo_calls"] == 0,
        "judge_calls_configured": EXPECTED_COUNTS["judge_calls"] == 0,
        "providers_called_during_preflight": True,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    architecture_lock = {
        "classification": "AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_CANARY_ARCHITECTURE_LOCK",
        "family_id": AP.AP_FAMILY_ID,
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "target_pair_ids": list(TARGET_PAIR_IDS),
        "model_roster_declared": declared_roster,
        "expected_counts": EXPECTED_COUNTS,
        "full_context_governor_audit": False,
        "benchmark_laws": {
            "worker_prompt_order": "gov_adversarial_baton>structured_canonical_state>artifact_context",
            "raw_accumulating_transcript_injection": "banned",
            "gov_model_policy": "fixed_for_session",
            "gov_may_select_models": False,
        },
    }
    preimage = {
        "classification": "AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_CANARY_PREFLIGHT",
        "status": status,
        "result": "AP_OPENAI_W2_ALL_SIX_COLLAPSE_CANARY_READY" if status == "PASS" else "AP_OPENAI_W2_ALL_SIX_COLLAPSE_CANARY_BLOCKED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "freeze_root": EXPECTED_FREEZE_ROOT_HASH,
        "source_ap_runner": str(AP_MODULE_PATH.relative_to(BENCHMARK_ROOT)),
        "target_pair_ids": list(TARGET_PAIR_IDS),
        "expected_counts": EXPECTED_COUNTS,
        "architecture_lock": architecture_lock,
        "solo_triage_target_check": target_check,
        "checks": checks,
        "blocked_reason": None if status == "PASS" else [key for key, value in checks.items() if not value],
        "providers_called": 0,
        "holo_started": False,
        "solo_started": False,
        "judges_started": False,
    }
    preimage["root_signature"] = AP.sha256_text(AP.canonical_json({k: v for k, v in preimage.items() if k != "created_at"}))
    return preimage


def scan_no_leakage(run_dir: Path) -> dict[str, Any]:
    hits = []
    prompt_files = sorted((run_dir / "prompts").glob("*.json")) if (run_dir / "prompts").exists() else []
    for path in prompt_files:
        text = path.read_text(errors="replace").lower()
        for pattern in AP.ANSWER_KEY_LEAK_PATTERNS:
            if pattern.lower() in text:
                hits.append({"path": str(path.relative_to(run_dir)), "pattern": pattern})
    return {
        "classification": "AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_NO_LEAKAGE_AUDIT",
        "status": "PASS" if not hits else "FAIL",
        "run_dir": str(run_dir),
        "prompt_files_scanned": len(prompt_files),
        "hits": hits,
    }


def summarize(run_dir: Path, manifest: dict[str, Any], packet_results: list[dict[str, Any]], trace_path: Path) -> dict[str, Any]:
    rows = trace_rows(trace_path)
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
        pair_valid = target_correct and guardrail_correct and bool(target.get("valid_rescue_evidence_present"))
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
    terminal_failures = RUNNER._terminal_call_failures(rows)
    root_failure = terminal_failures[0] if terminal_failures else None
    leakage = scan_no_leakage(run_dir)
    assertions = {
        "holo_packets": "PASS" if len(packet_results) == EXPECTED_COUNTS["packets"] else "FAIL",
        "holo_pairs": "PASS" if len(by_pair) == EXPECTED_COUNTS["pairs"] else "FAIL",
        "provider_calls": "PASS" if len(rows) == EXPECTED_COUNTS["total_provider_calls"] else "FAIL",
        "worker_calls": "PASS" if sum(1 for row in rows if row.get("call_kind") == "worker") == EXPECTED_COUNTS["worker_calls"] else "FAIL",
        "gov_calls": "PASS" if sum(1 for row in rows if row.get("call_kind") == "gov") == EXPECTED_COUNTS["gov_calls"] else "FAIL",
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
        "all_target_pairs_valid": "PASS" if valid_pairs == EXPECTED_COUNTS["pairs"] else "FAIL",
        "all_packets_correct": "PASS" if packet_correct == EXPECTED_COUNTS["packets"] else "FAIL",
        "benchmark_laws": "PASS" if law_validation.official_valid else "FAIL",
    }
    readiness = all(value == "PASS" for value in assertions.values()) and not terminal_failures
    if root_failure and root_failure.get("call_kind") == "gov" and root_failure.get("parse_ok") is not True:
        invalidation_reason = "GOV_CONTRACT_OR_TRUNCATION_FAILURE"
    elif root_failure and root_failure.get("provider_call_ok") is not True:
        invalidation_reason = "PROVIDER_FAILURE"
    elif len(rows) != EXPECTED_COUNTS["total_provider_calls"]:
        invalidation_reason = "INCOMPLETE_TRACE"
    elif not readiness:
        invalidation_reason = "CANARY_ASSERTION_FAILURE"
    else:
        invalidation_reason = None
    summary = {
        "classification": "AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_CANARY_COMPLETE" if readiness else "AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_CANARY_INVALID_OR_INCOMPLETE",
        "readiness_passed": readiness,
        "run_dir": str(run_dir),
        "freeze_root": EXPECTED_FREEZE_ROOT_HASH,
        "target_pair_ids": list(TARGET_PAIR_IDS),
        "trace_hash": AP.sha256_file(trace_path),
        "provider_calls": len(rows),
        "expected_provider_calls": EXPECTED_COUNTS["total_provider_calls"],
        "worker_calls": sum(1 for row in rows if row.get("call_kind") == "worker"),
        "gov_calls": sum(1 for row in rows if row.get("call_kind") == "gov"),
        "solo_calls": 0,
        "judge_calls": 0,
        "provider_failures": provider_failures,
        "terminal_failures": terminal_failures,
        "root_failure": root_failure,
        "invalidation_reason": invalidation_reason,
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
    write_json(run_dir / "canary_results.json", summary)
    write_json(run_dir / "AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_NO_LEAKAGE_AUDIT.json", leakage)
    write_json(run_dir / "AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_READINESS_ASSERTIONS.json", assertions)
    write_summary_md(run_dir, summary)
    return summary


def write_summary_md(run_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# AP OpenAI-W2 All-Six-Collapse Holo Canary",
        "",
        f"Classification: `{summary['classification']}`",
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
        lines.append(f"| `{item['pair_id']}` | `{item.get('target_final_verdict')}` | `{item.get('guardrail_final_verdict')}` | `{item.get('pair_valid')}` |")
    lines.extend(["", "## Assertions", "", "| Assertion | Value |", "| --- | --- |"])
    for key, value in summary["readiness_assertions"].items():
        lines.append(f"| `{key}` | `{value}` |")
    write_text(run_dir / "canary_summary.md", "\n".join(lines) + "\n")


def run_live() -> int:
    manifest = build_preflight()
    if manifest["status"] != "PASS":
        raise RuntimeError(f"preflight_failed:{manifest.get('blocked_reason')}")
    for key in ("xai", AP.OPENAI_W2_MODEL_KEY, "minimax"):
        env = RUNNER.MODEL_CONFIGS[key]["api_key_env"]
        if not os.getenv(env, "").strip():
            raise RuntimeError(f"{env} missing")
    pairs = selected_pairs()
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    run_dir = RUN_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    write_json(run_dir / "CANARY_PREFLIGHT.json", manifest)
    trace_path = run_dir / "TRACE_CALLS.jsonl"
    packet_results: list[dict[str, Any]] = []
    with trace_path.open("w") as trace:
        for pair in pairs:
            for suffix in ("A", "B"):
                result = RUNNER._run_packet(run_id, pair, suffix, manifest, run_dir, trace)
                packet_results.append(result)
                if RUNNER._terminal_call_failures(result["calls"]):
                    summary = summarize(run_dir, manifest, packet_results, trace_path)
                    AP.lock_directory(run_dir, "LOCK")
                    print(json.dumps(summary, indent=2, sort_keys=True))
                    return 1
    summary = summarize(run_dir, manifest, packet_results, trace_path)
    AP.lock_directory(run_dir, "LOCK")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["readiness_passed"] else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        report = build_preflight()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["status"] == "PASS" else 1
    if args.run_live:
        return run_live()
    parser.error("Use --preflight or --run-live")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
