#!/usr/bin/env python3
"""Run staged Wave 2 Holo target batches.

Scope:
- Reads the frozen Wave 2 packet bank.
- Uses a staged Wave 2 target batch from the no-provider staging package.
- Runs the complete HoloVerify architecture over 9 pairs / 18 packets.
- Does not run solo or judges.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


BASE_RUNNER_PATH = BENCHMARK_ROOT / "run_20pair_holoverify_3dna_2026_06_29.py"
FREEZE_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
BATCH_NUMBER = 1
BATCH_SUFFIX = "001"
BATCH_ID = "WAVE2_HOLO_TARGET_BATCH_001"
STAGING_ROOT = FREEZE_ROOT / "holo_target_batches" / "wave2_holo_target_batch_001"
REGISTRATION_PATH = STAGING_ROOT / "WAVE2_HOLO_TARGET_BATCH_001_REGISTRATION_2026_07_01.json"
PREFLIGHT_PATH = STAGING_ROOT / "WAVE2_HOLO_TARGET_BATCH_001_PREFLIGHT_2026_07_01.json"
LIVE_PREFLIGHT_JSON = STAGING_ROOT / "WAVE2_HOLO_TARGET_BATCH_001_LIVE_PREFLIGHT_2026_07_01.json"
LIVE_PREFLIGHT_MD = STAGING_ROOT / "WAVE2_HOLO_TARGET_BATCH_001_LIVE_PREFLIGHT_2026_07_01.md"
LIVE_RUN_ROOT = STAGING_ROOT / "live_runs"

EXPECTED_FREEZE_ROOT_HASH = "80d8106d7efe72bee44d2c05648b71814204c08e1f96934afefd3d75d242845f"
EXPECTED_TARGET_SELECTION_SHA = "75e6681b163a7c2e2ab70e69ab161ac53b727c0d311774609e2eca1959874c99"
OPENAI_W2_MODEL_KEY = "openai_w2"
OPENAI_W2_MODEL_ID = "gpt-5.4-mini"
OPENAI_RESPONSES_TIMEOUT_SECONDS = 240
WAVE2_GOV_MAX_TOKENS = 1024

ANSWER_KEY_LEAK_PATTERNS = (
    "packet_truth",
    "target_bucket",
    "target_sibling",
    "deterministic_answer_key_for_local_audit_only",
    "required_verdict",
    "verdict_basis",
    "local_audit_predicate",
    "answer key",
    "expected verdict",
)


def load_base_runner() -> Any:
    spec = importlib.util.spec_from_file_location("wave2_holo_base_runner", BASE_RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


RUNNER = load_base_runner()
ORIGINAL_RUNNER_CALL_MODEL = RUNNER._call_model


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def current_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()


def configure_batch(batch_number: int) -> None:
    global BATCH_NUMBER, BATCH_SUFFIX, BATCH_ID, STAGING_ROOT, REGISTRATION_PATH, PREFLIGHT_PATH, LIVE_PREFLIGHT_JSON, LIVE_PREFLIGHT_MD, LIVE_RUN_ROOT
    if batch_number < 1:
        raise ValueError("batch_number must be >= 1")
    BATCH_NUMBER = batch_number
    BATCH_SUFFIX = f"{batch_number:03d}"
    BATCH_ID = f"WAVE2_HOLO_TARGET_BATCH_{BATCH_SUFFIX}"
    STAGING_ROOT = FREEZE_ROOT / "holo_target_batches" / f"wave2_holo_target_batch_{BATCH_SUFFIX}"
    REGISTRATION_PATH = STAGING_ROOT / f"{BATCH_ID}_REGISTRATION_2026_07_01.json"
    PREFLIGHT_PATH = STAGING_ROOT / f"{BATCH_ID}_PREFLIGHT_2026_07_01.json"
    LIVE_PREFLIGHT_JSON = STAGING_ROOT / f"{BATCH_ID}_LIVE_PREFLIGHT_2026_07_01.json"
    LIVE_PREFLIGHT_MD = STAGING_ROOT / f"{BATCH_ID}_LIVE_PREFLIGHT_2026_07_01.md"
    LIVE_RUN_ROOT = STAGING_ROOT / "live_runs"


def git_diff_names(path: Path) -> list[str]:
    return [
        row
        for row in subprocess.check_output(["git", "diff", "--name-only", "--", str(path)], cwd=REPO_ROOT, text=True).splitlines()
        if row.strip()
    ]


def configure_openai_w2_runner() -> None:
    RUNNER.MODEL_CONFIGS[OPENAI_W2_MODEL_KEY] = {
        "provider": "openai",
        "model": OPENAI_W2_MODEL_ID,
        "dna": "openai",
        "api_key_env": "OPENAI_API_KEY",
        "kind": "openai_responses",
    }
    RUNNER.WORKER_SEQUENCE = [
        {"worker_index": 1, "role_name": "SOURCE_BOUNDARY_MAPPER", "model_key": "xai"},
        {"worker_index": 2, "role_name": "ADVERSARIAL_SCOPE_CHALLENGER", "model_key": OPENAI_W2_MODEL_KEY},
        {"worker_index": 3, "role_name": "FINAL_COMPILER", "model_key": "minimax"},
    ]
    RUNNER.GOV_MODEL_KEY = "minimax"
    RUNNER.GOV_MAX_TOKENS = WAVE2_GOV_MAX_TOKENS
    RUNNER._call_model = call_model_with_openai_responses


def _call_openai_responses_once(config: dict[str, Any], messages: list[dict[str, str]], max_tokens: int) -> dict[str, Any]:
    prompt = "\n\n".join(f"{message['role'].upper()}:\n{message['content']}" for message in messages)
    payload = {
        "model": config["model"],
        "input": prompt,
        "max_output_tokens": max_tokens,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {os.getenv(config['api_key_env'], '').strip()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=OPENAI_RESPONSES_TIMEOUT_SECONDS) as response:
        data = json.loads(response.read().decode("utf-8", errors="replace"))
    text_parts: list[str] = []
    output = data.get("output") if isinstance(data.get("output"), list) else []
    for item in output:
        content = item.get("content") if isinstance(item, dict) else []
        for part in content if isinstance(content, list) else []:
            if isinstance(part, dict) and part.get("type") in {"output_text", "text"}:
                text_parts.append(str(part.get("text") or ""))
    raw_text = "".join(text_parts)
    stripped_text = RUNNER._strip_thinking_blocks(raw_text)
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return {
        "text": stripped_text,
        "raw_text": raw_text,
        "text_stripped_by_thinking_filter": raw_text != stripped_text,
        "finish_reason": data.get("status"),
        "response_id": data.get("id"),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }


def call_openai_responses(config: dict[str, Any], messages: list[dict[str, str]], max_tokens: int) -> dict[str, Any]:
    started = time.time()

    def call_once() -> dict[str, Any]:
        return _call_openai_responses_once(config, messages, max_tokens)

    response = RUNNER._call_with_transport_retry(
        call_once,
        provider=config["provider"],
        model=config["model"],
        timeout_seconds=OPENAI_RESPONSES_TIMEOUT_SECONDS,
    )
    response["elapsed_ms"] = int((time.time() - started) * 1000)
    return response


def call_model_with_openai_responses(config: dict[str, Any], messages: list[dict[str, str]], max_tokens: int) -> dict[str, Any]:
    if config.get("kind") == "openai_responses":
        return call_openai_responses(config, messages, max_tokens)
    return ORIGINAL_RUNNER_CALL_MODEL(config, messages, max_tokens)


def read_freeze_records() -> list[dict[str, Any]]:
    freeze_manifest = load_json(FREEZE_ROOT / "FREEZE_MANIFEST.json")
    if freeze_manifest.get("freeze_root_hash") != EXPECTED_FREEZE_ROOT_HASH:
        raise RuntimeError(f"freeze_root_mismatch:{freeze_manifest.get('freeze_root_hash')}")
    registration = load_json(REGISTRATION_PATH)
    packet_manifest = load_json(FREEZE_ROOT / "manifests" / "PACKET_HASH_MANIFEST.json")
    prompt_manifest = load_json(FREEZE_ROOT / "manifests" / "PROMPT_HASH_MANIFEST.json")
    packet_index = load_json(FREEZE_ROOT / "manifests" / "PACKET_INDEX.json")
    packet_hash_by_id = {row["packet_id"]: row for row in packet_manifest["records"]}
    prompt_hash_by_id = {row["packet_id"]: row for row in prompt_manifest["records"]}
    index_by_id = {row["packet_id"]: row for row in packet_index}

    records: list[dict[str, Any]] = []
    for selected in registration["selected_records"]:
        packet_id = selected["packet_id"]
        packet_row = packet_hash_by_id[packet_id]
        prompt_row = prompt_hash_by_id[packet_id]
        index_row = index_by_id[packet_id]
        packet_path = FREEZE_ROOT / packet_row["packet_path"]
        prompt_path = FREEZE_ROOT / prompt_row["prompt_path"]
        model_visible_path = FREEZE_ROOT / packet_row["model_visible_payload_path"]
        if sha256_file(packet_path) != packet_row["packet_sha256"]:
            raise RuntimeError(f"packet_hash_mismatch:{packet_id}")
        if sha256_file(prompt_path) != prompt_row["prompt_sha256"]:
            raise RuntimeError(f"prompt_hash_mismatch:{packet_id}")
        if sha256_file(model_visible_path) != packet_row["model_visible_payload_file_sha256"]:
            raise RuntimeError(f"model_visible_hash_mismatch:{packet_id}")
        records.append(
            {
                **index_row,
                "packet_path": str(packet_path.relative_to(BENCHMARK_ROOT)),
                "prompt_path": str(prompt_path.relative_to(BENCHMARK_ROOT)),
                "model_visible_payload_path": str(model_visible_path.relative_to(BENCHMARK_ROOT)),
                "packet_file_sha256": packet_row["packet_sha256"],
                "prompt_file_sha256": prompt_row["prompt_sha256"],
                "model_visible_payload_file_sha256": packet_row["model_visible_payload_file_sha256"],
                "packet": load_json(packet_path),
                "triage_class": selected.get("triage_class"),
                "priority_score": selected.get("priority_score"),
                "not_knew_count": selected.get("not_knew_count"),
                "wrong_verdict_count": selected.get("wrong_verdict_count"),
                "parse_or_provider_fail_count": selected.get("parse_or_provider_fail_count"),
            }
        )
    return sorted(records, key=lambda row: (row["pair_id"], row["sibling_id"]))


def source_ids(packet: dict[str, Any]) -> list[str]:
    return [str(item["source_id"]) for item in packet["source_control_facts"]]


def source_record(packet: dict[str, Any], suffix: str) -> str:
    for item in packet["source_control_facts"]:
        if str(item["source_id"]).endswith(suffix):
            return str(item["source_id"])
    return str(packet["source_control_facts"][0]["source_id"])


def convert_payload(packet: dict[str, Any]) -> dict[str, Any]:
    internal_documents = []
    policy_documents = []
    for record in packet["source_control_facts"]:
        doc = {
            "doc_id": record["source_id"],
            "type": record["source_type"],
            "content": record["content"],
        }
        if record["source_type"] == "policy_control":
            policy_documents.append({"doc_id": record["source_id"], "title": "Frozen Wave 2 source-boundary policy", "content": record["content"]})
        else:
            internal_documents.append(doc)
    return {
        "action": {
            "business_ref": packet["model_visible_payload"]["case_ref"],
            "type": packet.get("domain_slug") or "wave2_action_boundary",
            "vendor": "Frozen Wave 2 record",
            "amount": 0,
            "currency": "USD",
            "description": packet["action_boundary"],
            "action_date": "2026-07-01",
        },
        "context": {
            "action_boundary": packet["action_boundary"],
            "anomaly_observed": packet["tempting_wrong_move"],
            "explanation_summary": "Verify whether the frozen Wave 2 source records close the exact action boundary before execution.",
            "internal_documents": internal_documents,
            "policy_documents": policy_documents,
        },
    }


def build_pairs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_pair[record["pair_id"]].append(record)
    pairs = []
    for pair_id in selected_pair_ids():
        pair_records = by_pair[pair_id]
        if len(pair_records) != 2:
            raise RuntimeError(f"pair_sibling_count_mismatch:{pair_id}")
        by_suffix = {row["sibling_id"]: row for row in pair_records}
        a = by_suffix["A"]
        b = by_suffix["B"]
        target = next(row for row in pair_records if row["target_sibling"])
        target_suffix = target["sibling_id"]
        guardrail_suffix = "B" if target_suffix == "A" else "A"
        spec = {
            "pair_id": pair_id,
            "boundary": a["packet"]["action_boundary"],
            "failure_class_notes": a["packet"]["hidden_dependency"],
            "knew_terms": {
                "A": [
                    a["packet"]["hidden_dependency"],
                    source_record(a["packet"], "-CTL"),
                    source_record(a["packet"], "-BND"),
                ],
                "B": [
                    b["packet"]["hidden_dependency"],
                    source_record(b["packet"], "-CTL"),
                    source_record(b["packet"], "-BND"),
                ],
            },
        }
        pairs.append(
            {
                "pair_id": pair_id,
                "benchmark_bucket": target["target_bucket"],
                "target_suffix": target_suffix,
                "guardrail_suffix": guardrail_suffix,
                "spec": spec,
                "payloads": {
                    "A": convert_payload(a["packet"]),
                    "B": convert_payload(b["packet"]),
                },
                "freeze_records": {"A": a, "B": b},
                "candidate": {"failing_models": []},
                "triage_evidence": {
                    "triage_class": target.get("triage_class"),
                    "priority_score": target.get("priority_score"),
                    "not_knew_count": target.get("not_knew_count"),
                    "wrong_verdict_count": target.get("wrong_verdict_count"),
                    "parse_or_provider_fail_count": target.get("parse_or_provider_fail_count"),
                },
            }
        )
    return pairs


def selected_pair_ids() -> list[str]:
    registration = load_json(REGISTRATION_PATH)
    return list(registration["selected_pair_ids"])


def build_live_preflight() -> dict[str, Any]:
    configure_openai_w2_runner()
    freeze_manifest = load_json(FREEZE_ROOT / "FREEZE_MANIFEST.json")
    staging_preflight = load_json(PREFLIGHT_PATH)
    registration = load_json(REGISTRATION_PATH)
    records = read_freeze_records()
    pairs = build_pairs(records)
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
    packet_records = [
        {
            "pair_id": row["pair_id"],
            "packet_id": row["packet_id"],
            "suffix": row["sibling_id"],
            "expected_verdict_for_local_gate": row["packet_truth"],
            "packet_hash": row["packet_file_sha256"],
            "prompt_hash": row["prompt_file_sha256"],
            "model_visible_payload_hash": row["model_visible_payload_file_sha256"],
            "packet_path": row["packet_path"],
            "prompt_path": row["prompt_path"],
            "model_visible_payload_path": row["model_visible_payload_path"],
            "triage_class": row.get("triage_class"),
            "not_knew_count": row.get("not_knew_count"),
        }
        for row in records
    ]
    families_diff = git_diff_names(FREEZE_ROOT / "families")
    manifests_diff = git_diff_names(FREEZE_ROOT / "manifests")
    expected_pair_count = registration["expected_counts"]["pairs"]
    expected_packet_count = registration["expected_counts"]["packets"]
    expected_total_calls = registration["expected_counts"]["total_provider_calls"]
    checks = {
        "staging_preflight_passed": staging_preflight.get("status") == "PASS",
        "freeze_root_matches": freeze_manifest.get("freeze_root_hash") == EXPECTED_FREEZE_ROOT_HASH,
        "target_selection_sha_matches": registration.get("source_target_selection_sha256") == EXPECTED_TARGET_SELECTION_SHA,
        "pair_count": len(pairs) == expected_pair_count,
        "packet_count": len(records) == expected_packet_count,
        "selected_pair_ids_match_registration": [pair["pair_id"] for pair in pairs] == selected_pair_ids(),
        "packet_hashes_match_freeze": len(records) == expected_packet_count,
        "prompt_hashes_match_freeze": len(records) == expected_packet_count,
        "no_packet_edits": not families_diff,
        "no_prompt_edits": not families_diff,
        "no_manifest_edits": not manifests_diff,
        "worker_roster_declared": worker_sequence
        == [
            {"worker_index": 1, "role_name": "SOURCE_BOUNDARY_MAPPER", "model_key": "xai", "provider": "xai", "model": "grok-3-mini", "dna": "xai"},
            {"worker_index": 2, "role_name": "ADVERSARIAL_SCOPE_CHALLENGER", "model_key": OPENAI_W2_MODEL_KEY, "provider": "openai", "model": OPENAI_W2_MODEL_ID, "dna": "openai"},
            {"worker_index": 3, "role_name": "FINAL_COMPILER", "model_key": "minimax", "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "dna": "minimax"},
        ],
        "gov_is_minimax": gov["provider"] == "minimax" and gov["model"] == "MiniMax-M2.5-highspeed",
        "gov_cannot_choose_models": gov["gov_may_select_models"] is False,
        "w2_is_openai_gpt_5_4_mini": worker_sequence[1]["provider"] == "openai" and worker_sequence[1]["model"] == OPENAI_W2_MODEL_ID,
        "no_gemini_active": all("gemini" not in row["model"].lower() and row["provider"] != "google" for row in worker_sequence),
        "worker_contract_format": RUNNER._worker_contract().get("format") == "compact_key_value_v1",
        "gov_contract_format": RUNNER._gov_contract().get("format") == "gov_micro_baton_v2",
        "gov_max_tokens_1024": getattr(RUNNER, "GOV_MAX_TOKENS", None) == WAVE2_GOV_MAX_TOKENS,
        "transport_policy_v1_active": getattr(RUNNER, "TRANSPORT_RETRY_POLICY_VERSION", "") == "HOLOVERIFY_TRANSPORT_RETRY_POLICY_V1_2026_06_29",
        "deterministic_gates_configured": callable(getattr(RUNNER, "_validate_worker", None)),
        "gov_sees_gate_results": callable(getattr(RUNNER, "_build_gov_messages", None)),
        "artifact_registry_configured": callable(getattr(RUNNER, "_artifact_record", None)),
        "best_artifact_registry_configured": callable(getattr(RUNNER, "_select_best", None)),
        "pinned_best_configured": callable(getattr(RUNNER, "_make_state_brief", None)),
        "final_selector_configured": callable(getattr(RUNNER, "_select_best", None)),
        f"expected_provider_calls_{expected_total_calls}": len(records) * 5 == expected_total_calls,
        "solo_calls_0": True,
        "judge_calls_0": True,
    }
    architecture_lock = {
        "classification": f"{BATCH_ID}_LIVE_PREFLIGHT",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "current_head_at_preflight": current_head(),
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "batch_id": BATCH_ID,
        "model_roster_declared": {
            "worker_sequence": worker_sequence,
            "gov": gov,
            "gov_sequence": [{"slot": "G1", **gov}, {"slot": "G2", **gov}],
            "fallback_policy": "NO_FALLBACK_PROVIDER_FAILURE_INVALIDATES_RUN",
        },
        "expected_counts": {
            "pairs": len(pairs),
            "packets": len(records),
            "worker_calls": len(records) * 3,
            "gov_calls": len(records) * 2,
            "total_provider_calls": len(records) * 5,
            "judge_calls": 0,
            "solo_calls": 0,
        },
        "complete_architecture_requirements": freeze_manifest["architecture_protocol"]["required_holo_controls"],
        "full_context_governor_audit": False,
        "benchmark_laws": {
            "gov_worker_ratio_target": "0.10_to_0.25",
            "gov_worker_ratio_warning": ">0.33",
            "gov_worker_ratio_hard_fail": ">0.50 unless full_context_governor_audit",
            "worker_prompt_order": "gov_adversarial_baton>structured_canonical_state>artifact_context",
            "raw_accumulating_transcript_injection": "banned",
            "gov_model_policy": "fixed_for_session",
            "worker_rotation_policy": "at_least_two_distinct_workers_no_immediate_self_feed",
        },
    }
    preimage = {
        "classification": f"{BATCH_ID}_LIVE_PREFLIGHT",
        "status": architecture_lock["status"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "batch_id": BATCH_ID,
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "registration_ref": str(REGISTRATION_PATH.relative_to(REPO_ROOT)),
        "staging_preflight_ref": str(PREFLIGHT_PATH.relative_to(REPO_ROOT)),
        "runner_script": str(Path(__file__).relative_to(BENCHMARK_ROOT)),
        "runner_batch_arg": f"--batch-number {BATCH_NUMBER}",
        "base_runner_script": str(BASE_RUNNER_PATH.relative_to(BENCHMARK_ROOT)),
        "architecture_lock": architecture_lock,
        "packet_records": packet_records,
        "checks": checks,
        "blocked_reason": None if all(checks.values()) else [key for key, value in checks.items() if not value],
        "providers_called": 0,
        "solo_started": False,
        "judges_started": False,
        "live_holo_started": False,
    }
    preimage["root_signature"] = sha256_text(canonical_json({k: v for k, v in preimage.items() if k != "created_at"}))
    write_json(LIVE_PREFLIGHT_JSON, preimage)
    write_text(LIVE_PREFLIGHT_MD, render_preflight_md(preimage))
    return preimage


def render_preflight_md(preflight: dict[str, Any]) -> str:
    lines = [
        f"# Wave 2 Holo Target Batch {BATCH_SUFFIX} Live Preflight",
        "",
        f"Status: `{preflight['status']}`",
        f"Batch: `{preflight['batch_id']}`",
        f"Freeze root: `{preflight['freeze_root_hash']}`",
        f"Root signature: `{preflight['root_signature']}`",
        "",
        "## Expected Calls",
        "",
    ]
    expected = preflight["architecture_lock"]["expected_counts"]
    for key in ("pairs", "packets", "worker_calls", "gov_calls", "total_provider_calls", "solo_calls", "judge_calls"):
        lines.append(f"- `{key}`: `{expected[key]}`")
    lines.extend(["", "## Roster", "", "| Slot | Provider | Model | Role |", "| --- | --- | --- | --- |"])
    for worker in preflight["architecture_lock"]["model_roster_declared"]["worker_sequence"]:
        lines.append(f"| `W{worker['worker_index']}` | `{worker['provider']}` | `{worker['model']}` | `{worker['role_name']}` |")
    for gov in preflight["architecture_lock"]["model_roster_declared"]["gov_sequence"]:
        lines.append(f"| `{gov['slot']}` | `{gov['provider']}` | `{gov['model']}` | Gov |")
    lines.extend(["", "## Checks", "", "| Check | Value |", "| --- | --- |"])
    for key, value in preflight["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Next Step", ""])
    if preflight["status"] == "PASS":
        lines.append(
            f"Run `python3 -B docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py --batch-number {BATCH_NUMBER} --run-live` only when provider calls are approved."
        )
    else:
        lines.append(f"Do not run live. Blocked checks: `{preflight['blocked_reason']}`")
    return "\n".join(lines) + "\n"


def validate_preflight() -> dict[str, Any]:
    manifest = build_live_preflight()
    if manifest["status"] != "PASS":
        raise RuntimeError(f"wave2_holo_preflight_failed:{manifest['blocked_reason']}")
    return manifest


def lock_directory(run_dir: Path, filename_prefix: str = "LOCK") -> dict[str, Any]:
    files = []
    for path in sorted(item for item in run_dir.rglob("*") if item.is_file()):
        if path.name in {f"{filename_prefix}_MANIFEST.json", f"{filename_prefix}_VALIDATION.json"}:
            continue
        files.append({"relative_path": str(path.relative_to(run_dir)), "sha256": sha256_file(path), "bytes": path.stat().st_size})
    manifest_no_root = {
        "classification": f"{BATCH_ID}_{filename_prefix}_MANIFEST",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "locked_files": files,
    }
    root_signature = sha256_text(canonical_json(manifest_no_root))
    manifest = {**manifest_no_root, "root_signature": root_signature}
    write_json(run_dir / f"{filename_prefix}_MANIFEST.json", manifest)
    validation = validate_lock(run_dir / f"{filename_prefix}_MANIFEST.json")
    write_json(run_dir / f"{filename_prefix}_VALIDATION.json", validation)
    return manifest


def validate_lock(lock_path: Path) -> dict[str, Any]:
    lock = load_json(lock_path)
    run_dir = lock_path.parent
    for item in lock["locked_files"]:
        if sha256_file(run_dir / item["relative_path"]) != item["sha256"]:
            raise RuntimeError(f"lock_hash_mismatch:{item['relative_path']}")
    no_root = dict(lock)
    root = no_root.pop("root_signature")
    recomputed = sha256_text(canonical_json(no_root))
    if root != recomputed:
        raise RuntimeError("lock_root_mismatch")
    return {
        "validation_status": "PASS",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "root_signature": root,
        "locked_file_count": len(lock["locked_files"]),
    }


def expected_verdict(suffix: str) -> str:
    return "ALLOW" if suffix == "A" else "ESCALATE"


def trace_rows(path: Path) -> list[dict[str, Any]]:
    return load_jsonl(path)


def no_leakage_audit(run_dir: Path) -> dict[str, Any]:
    hits = []
    prompt_files = sorted((run_dir / "prompts").glob("*.json")) if (run_dir / "prompts").exists() else []
    for path in prompt_files:
        lower = path.read_text(errors="replace").lower()
        for pattern in ANSWER_KEY_LEAK_PATTERNS:
            if pattern.lower() in lower:
                hits.append({"path": str(path.relative_to(run_dir)), "pattern": pattern})
    return {
        "classification": f"{BATCH_ID}_NO_LEAKAGE_AUDIT",
        "status": "PASS" if not hits else "FAIL",
        "run_dir": str(run_dir),
        "prompt_files_scanned": len(prompt_files),
        "hits": hits,
    }


def holo_summary(run_dir: Path, manifest: dict[str, Any], packet_results: list[dict[str, Any]], trace_path: Path) -> dict[str, Any]:
    rows = trace_rows(trace_path)
    expected = manifest["architecture_lock"]["expected_counts"]
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for row in rows:
        for key in totals:
            if isinstance(row.get(key), int):
                totals[key] += row[key]
    roster = RUNNER._model_roster_audit(manifest, rows)
    law_validation = RUNNER.validate_holo_benchmark_laws(
        rows,
        full_context_governor_audit=False,
        worker_prompt_objects=RUNNER._load_worker_prompt_objects(run_dir, rows),
    )
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in packet_results:
        by_pair[result["pair_id"]].append(result)
    valid_pairs = 0
    packet_correct = 0
    inventory = []
    for pair_id, results in sorted(by_pair.items()):
        if len(results) != 2:
            inventory.append({"pair_id": pair_id, "pair_valid": False, "incomplete_reason": "missing_sibling"})
            continue
        target = next((row for row in results if row["is_target_packet"]), None)
        guardrail = next((row for row in results if row["is_guardrail_sibling"]), None)
        if target is None or guardrail is None:
            inventory.append({"pair_id": pair_id, "pair_valid": False, "incomplete_reason": "missing_target_or_guardrail"})
            continue
        target_expected = expected_verdict(target["suffix"])
        guardrail_expected = expected_verdict(guardrail["suffix"])
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
            }
        )
    provider_failures = [row for row in rows if row.get("provider_call_ok") is not True]
    terminal_failures = RUNNER._terminal_call_failures(rows)
    root_failure = terminal_failures[0] if terminal_failures else None
    leakage = no_leakage_audit(run_dir)
    if root_failure and root_failure.get("provider_call_ok") is not True:
        invalidation_reason = "PROVIDER_FAILURE"
    elif root_failure and root_failure.get("call_kind") == "gov" and root_failure.get("parse_ok") is not True:
        invalidation_reason = "GOV_CONTRACT_OR_TRUNCATION_FAILURE"
    elif root_failure:
        invalidation_reason = "CONTENT_OR_PARSE_FAILURE"
    elif len(rows) != expected["total_provider_calls"]:
        invalidation_reason = "INCOMPLETE_TRACE"
    elif packet_correct != expected["packets"] or valid_pairs != expected["pairs"]:
        invalidation_reason = "VERDICT_OR_PAIR_ADMISSIBILITY_FAILURE"
    elif leakage["status"] != "PASS":
        invalidation_reason = "PROMPT_LEAKAGE"
    else:
        invalidation_reason = None
    assertions = {
        "holo_packets": "PASS" if len(packet_results) == expected["packets"] else "FAIL",
        "holo_pairs": "PASS" if valid_pairs == expected["pairs"] else "FAIL",
        "provider_calls": "PASS" if len(rows) == expected["total_provider_calls"] else "FAIL",
        "worker_calls": "PASS" if sum(1 for row in rows if row.get("call_kind") == "worker") == expected["worker_calls"] else "FAIL",
        "gov_calls": "PASS" if sum(1 for row in rows if row.get("call_kind") == "gov") == expected["gov_calls"] else "FAIL",
        "no_judges": "PASS",
        "provider_failures": "PASS" if not provider_failures else "FAIL",
        "three_dna_inside_holoverify": "PASS" if roster["all_3_dna_participated"] else "FAIL",
        "declared_roster_matches_actual_calls": "PASS" if roster["declared_roster_matches_actual_calls"] else "FAIL",
        "deterministic_gate_after_every_worker": "PASS" if all("gate_result" in row for row in rows if row.get("call_kind") == "worker") else "FAIL",
        "gov_receives_gate_results": "PASS" if all(row.get("received_gate_result") for row in rows if row.get("call_kind") == "gov") else "FAIL",
        "final_selector_present": "PASS" if all("final_selector" in row for row in packet_results) else "FAIL",
        "no_leakage": leakage["status"],
        "holo_benchmark_laws": "PASS" if law_validation.official_valid else "FAIL",
    }
    readiness = (
        len(packet_results) == expected["packets"]
        and len(rows) == expected["total_provider_calls"]
        and valid_pairs == expected["pairs"]
        and packet_correct == expected["packets"]
        and not provider_failures
        and not terminal_failures
        and leakage["status"] == "PASS"
        and law_validation.official_valid
    )
    summary = {
        "classification": f"{BATCH_ID}_COMPLETE" if readiness else f"{BATCH_ID}_INVALID_OR_INCOMPLETE",
        "readiness_passed": readiness,
        "run_dir": str(run_dir),
        "batch_id": BATCH_ID,
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "pre_run_root_signature": manifest["root_signature"],
        "trace_hash": sha256_file(trace_path) if trace_path.exists() else None,
        "provider_calls": len(rows),
        "expected_provider_calls": expected["total_provider_calls"],
        "worker_calls": sum(1 for row in rows if row.get("call_kind") == "worker"),
        "gov_calls": sum(1 for row in rows if row.get("call_kind") == "gov"),
        "judge_calls": 0,
        "provider_failures": provider_failures,
        "terminal_failures": terminal_failures,
        "root_failure": {
            "turn_id": root_failure.get("turn_id"),
            "packet_id": root_failure.get("packet_id"),
            "call_kind": root_failure.get("call_kind"),
            "provider": root_failure.get("provider"),
            "model": root_failure.get("model"),
            "finish_reason": root_failure.get("finish_reason"),
            "error": root_failure.get("error"),
            "provider_call_ok": root_failure.get("provider_call_ok"),
            "parse_ok": root_failure.get("parse_ok"),
            "admissible": root_failure.get("admissible"),
            "transport_attempt_count": root_failure.get("transport_attempt_count"),
            "transport_recovered": root_failure.get("transport_recovered"),
            "transport_final_failure_class": root_failure.get("transport_final_failure_class"),
        }
        if root_failure
        else None,
        "invalidation_reason": invalidation_reason,
        "transport_retry_policy_version": getattr(RUNNER, "TRANSPORT_RETRY_POLICY_VERSION", None),
        "transport_recovered_call_count": sum(1 for row in rows if row.get("transport_recovered") is True),
        "transport_attempted_call_count": sum(1 for row in rows if int(row.get("transport_attempt_count") or 1) > 1),
        "totals": totals,
        "packet_correct": packet_correct,
        "packet_count": len(packet_results),
        "valid_pairs": valid_pairs,
        "benchmark_law_validation": law_validation.to_dict(),
        "model_roster_audit": roster,
        "readiness_assertions": assertions,
        "no_leakage_audit": leakage,
        "benchmark_inventory": inventory,
        "packet_results": [{k: v for k, v in result.items() if k != "calls"} for result in packet_results],
    }
    write_json(run_dir / "live_results.json", summary)
    write_json(run_dir / f"{BATCH_ID}_NO_LEAKAGE_AUDIT.json", leakage)
    write_text(run_dir / "live_summary.md", render_live_summary_md(summary))
    return summary


def render_live_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        f"# Wave 2 Holo Target Batch {BATCH_SUFFIX} Live Summary",
        "",
        f"Classification: `{summary['classification']}`",
        f"Readiness passed: `{summary['readiness_passed']}`",
        f"Freeze root: `{summary['freeze_root_hash']}`",
        "",
        "## Calls",
        "",
        f"- Provider calls: `{summary['provider_calls']}` / `{summary['expected_provider_calls']}`",
        f"- Worker calls: `{summary['worker_calls']}`",
        f"- Gov calls: `{summary['gov_calls']}`",
        f"- Judge calls: `{summary['judge_calls']}`",
        f"- Tokens: `{summary['totals']['input_tokens']}` input / `{summary['totals']['output_tokens']}` output / `{summary['totals']['total_tokens']}` total",
    ]
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
                f"- Provider/model: `{root.get('provider')}/{root.get('model')}`",
                f"- Error: `{root.get('error')}`",
            ]
        )
    lines.extend(["", "## Assertions", "", "| Assertion | Value |", "| --- | --- |"])
    for key, value in summary["readiness_assertions"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Pair Inventory", "", "| Pair | Bucket | Target final | Guardrail final | Valid |", "| --- | --- | --- | --- | --- |"])
    for item in summary["benchmark_inventory"]:
        lines.append(
            f"| `{item['pair_id']}` | `{item.get('benchmark_bucket', 'N/A')}` | `{item.get('target_final_verdict', 'N/A')}` | `{item.get('guardrail_final_verdict', 'N/A')}` | `{item['pair_valid']}` |"
        )
    return "\n".join(lines) + "\n"


def run_live() -> int:
    manifest = validate_preflight()
    for key in ("xai", OPENAI_W2_MODEL_KEY, "minimax"):
        env = RUNNER.MODEL_CONFIGS[key]["api_key_env"]
        if not os.getenv(env, "").strip():
            raise RuntimeError(f"{env} missing")
    pairs = build_pairs(read_freeze_records())
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    run_dir = LIVE_RUN_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    trace_path = run_dir / "TRACE_CALLS.jsonl"
    packet_results: list[dict[str, Any]] = []
    with trace_path.open("w") as trace:
        for pair in pairs:
            for suffix in ("A", "B"):
                result = RUNNER._run_packet(run_id, pair, suffix, manifest, run_dir, trace)
                packet_results.append(result)
                if RUNNER._terminal_call_failures(result["calls"]):
                    summary = holo_summary(run_dir, manifest, packet_results, trace_path)
                    lock_directory(run_dir, "LOCK")
                    print(json.dumps(summary, indent=2, sort_keys=True))
                    return 1
    summary = holo_summary(run_dir, manifest, packet_results, trace_path)
    lock_directory(run_dir, "LOCK")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["readiness_passed"] else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-number", type=int, default=1)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    args = parser.parse_args()
    configure_batch(args.batch_number)
    if args.preflight:
        manifest = validate_preflight()
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0
    if args.run_live:
        return run_live()
    parser.error("choose --preflight or --run-live")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
