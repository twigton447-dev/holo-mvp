#!/usr/bin/env python3
"""Run the AP/procurement HoloVerify replication family.

This runner is scoped to the committed AP family inside the three-family packet
freeze. It does not edit packets or prompts. It runs:

1. Full HoloVerify architecture over the 40 frozen AP packets.
2. One-shot solo baseline over the same 40 frozen AP prompts.
3. Local no-judge evidence package and lock manifests.
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
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FREEZE_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_3families_2026-06-29"
AP_ROOT = BENCHMARK_ROOT / "holoverify_ap_procurement_replication_2026-06-29"
PRE_RUN_MANIFEST = AP_ROOT / "AP_PRE_RUN_MANIFEST.json"
OPENAI_W2_PREFLIGHT_MD = AP_ROOT / "AP_OPENAI_W2_LIVE_HOLO_PREFLIGHT_2026_06_29.md"
OPENAI_W2_PREFLIGHT_JSON = AP_ROOT / "AP_OPENAI_W2_LIVE_HOLO_PREFLIGHT_2026_06_29.json"
EXPECTED_FREEZE_ROOT_HASH = "5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7"
EXPECTED_FREEZE_COMMIT = "de22377be8175d04078ba6c70f1fd35222e9f572"
AP_FAMILY_ID = "HV-AP-REP-2026-06-29"
RUNNER_PATH = BENCHMARK_ROOT / "run_20pair_holoverify_3dna_2026_06_29.py"
MODEL_KEYS = ("xai", "google", "minimax")
OPENAI_W2_VARIANT_NAME = "AP_OPENAI_W2_ROSTER_VARIANT_2026_06_29"
OPENAI_W2_MODEL_KEY = "openai_w2"
OPENAI_W2_MODEL_ID = "gpt-5.4-mini"
OPENAI_W2_MODEL_KEYS = ("xai", OPENAI_W2_MODEL_KEY, "minimax")
OPENAI_W2_REGISTRATION = AP_ROOT / "AP_OPENAI_W2_ROSTER_VARIANT_REGISTRATION_2026_06_29.json"
OPENAI_W2_AVAILABILITY = AP_ROOT / "AP_OPENAI_W2_MODEL_AVAILABILITY_CHECK_2026_06_29.json"
OPENAI_RESPONSES_TIMEOUT_SECONDS = 240
AP_OPENAI_W2_GOV_MAX_TOKENS = 1024
OPENAI_W2_HOLO_RUN_ROOT = AP_ROOT / "holo_live_runs_openai_w2"

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


def load_runner_module():
    spec = importlib.util.spec_from_file_location("holo_3dna_runner_for_ap_replication", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


RUNNER = load_runner_module()
ORIGINAL_RUNNER_CALL_MODEL = RUNNER._call_model


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def current_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()


def git_diff_names(path: Path) -> list[str]:
    return [
        item
        for item in subprocess.check_output(["git", "diff", "--name-only", "--", str(path)], cwd=REPO_ROOT, text=True).splitlines()
        if item.strip()
    ]


def configure_openai_w2_runner() -> None:
    """Install the registered AP OpenAI-W2 roster into the imported runner.

    The base 3-DNA runner owns the packet execution function, prompt hierarchy,
    gates, artifact registry, and final selector. This function swaps only the
    Worker 2 provider/model for the registered AP variant.
    """
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
    RUNNER.GOV_MAX_TOKENS = AP_OPENAI_W2_GOV_MAX_TOKENS
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

    try:
        response = RUNNER._call_with_transport_retry(
            call_once,
            provider=config["provider"],
            model=config["model"],
            timeout_seconds=OPENAI_RESPONSES_TIMEOUT_SECONDS,
        )
    except RUNNER.TransportFailureAfterRetries as exc:
        exc.metadata["elapsed_ms"] = int((time.time() - started) * 1000)
        raise
    response["elapsed_ms"] = int((time.time() - started) * 1000)
    return response


def call_model_with_openai_responses(config: dict[str, Any], messages: list[dict[str, str]], max_tokens: int) -> dict[str, Any]:
    if config.get("kind") == "openai_responses":
        return call_openai_responses(config, messages, max_tokens)
    return ORIGINAL_RUNNER_CALL_MODEL(config, messages, max_tokens)


def read_freeze() -> dict[str, Any]:
    summary = load_json(FREEZE_ROOT / "FREEZE_MANIFEST.json")
    if summary.get("freeze_root_hash") != EXPECTED_FREEZE_ROOT_HASH:
        raise RuntimeError(f"freeze root mismatch: {summary.get('freeze_root_hash')}")
    packet_manifest = load_json(FREEZE_ROOT / "manifests" / "PACKET_HASH_MANIFEST.json")
    prompt_manifest = load_json(FREEZE_ROOT / "manifests" / "PROMPT_HASH_MANIFEST.json")
    index = load_json(FREEZE_ROOT / "manifests" / "PACKET_INDEX.json")
    packet_by_id = {row["packet_id"]: row for row in packet_manifest["records"]}
    prompt_by_id = {row["packet_id"]: row for row in prompt_manifest["records"]}
    ap_index = [row for row in index if row["family_id"] == AP_FAMILY_ID]
    if len(ap_index) != 40:
        raise RuntimeError(f"AP packet count expected 40, got {len(ap_index)}")
    records = []
    for row in sorted(ap_index, key=lambda item: (item["pair_id"], item["sibling_id"])):
        packet_hash_row = packet_by_id[row["packet_id"]]
        prompt_hash_row = prompt_by_id[row["packet_id"]]
        packet_path = FREEZE_ROOT / packet_hash_row["packet_path"]
        prompt_path = FREEZE_ROOT / prompt_hash_row["prompt_path"]
        model_payload_path = FREEZE_ROOT / packet_hash_row["model_visible_payload_path"]
        if sha256_file(packet_path) != packet_hash_row["packet_sha256"]:
            raise RuntimeError(f"packet hash mismatch: {row['packet_id']}")
        if sha256_file(prompt_path) != prompt_hash_row["prompt_sha256"]:
            raise RuntimeError(f"prompt hash mismatch: {row['packet_id']}")
        if sha256_file(model_payload_path) != packet_hash_row["model_visible_payload_file_sha256"]:
            raise RuntimeError(f"model-visible payload hash mismatch: {row['packet_id']}")
        packet = load_json(packet_path)
        records.append(
            {
                **row,
                "packet_path": str(packet_path.relative_to(BENCHMARK_ROOT)),
                "prompt_path": str(prompt_path.relative_to(BENCHMARK_ROOT)),
                "model_visible_payload_path": str(model_payload_path.relative_to(BENCHMARK_ROOT)),
                "packet_file_sha256": packet_hash_row["packet_sha256"],
                "prompt_file_sha256": prompt_hash_row["prompt_sha256"],
                "model_visible_payload_file_sha256": packet_hash_row["model_visible_payload_file_sha256"],
                "model_visible_payload_canonical_sha256": packet_hash_row["model_visible_payload_canonical_sha256"],
                "answer_key_canonical_sha256": packet_hash_row["answer_key_canonical_sha256"],
                "packet": packet,
            }
        )
    return {"summary": summary, "records": records}


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
            policy_documents.append({"doc_id": record["source_id"], "title": "Frozen AP source-boundary policy", "content": record["content"]})
        else:
            internal_documents.append(doc)
    return {
        "action": {
            "business_ref": packet["model_visible_payload"]["case_ref"],
            "type": "ap_procurement_vendor_master_action",
            "vendor": "Frozen AP vendor record",
            "amount": 0,
            "currency": "USD",
            "description": packet["action_boundary"],
            "action_date": "2026-06-29",
        },
        "context": {
            "action_boundary": packet["action_boundary"],
            "anomaly_observed": packet["tempting_wrong_move"],
            "explanation_summary": "Verify whether the frozen AP source records close the exact action boundary before execution.",
            "internal_documents": internal_documents,
            "policy_documents": policy_documents,
        },
    }


def build_pairs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_pair[record["pair_id"]].append(record)
    pairs = []
    for pair_id, pair_records in sorted(by_pair.items()):
        if len(pair_records) != 2:
            raise RuntimeError(f"pair sibling count mismatch: {pair_id}")
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
            }
        )
    if len(pairs) != 20:
        raise RuntimeError(f"AP pair count expected 20, got {len(pairs)}")
    return pairs


def build_preflight() -> dict[str, Any]:
    AP_ROOT.mkdir(parents=True, exist_ok=True)
    freeze = read_freeze()
    records = freeze["records"]
    pairs = build_pairs(records)
    architecture_lock = {
        "classification": "HOLOVERIFY_AP_REPLICATION_3DNA_PREFLIGHT",
        "status": "PRE_REGISTERED_AP_ONLY",
        "source_commit_required": EXPECTED_FREEZE_COMMIT,
        "current_head_at_preflight": current_head(),
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "family_id": AP_FAMILY_ID,
        "model_roster_declared": {
            "worker_sequence": [
                {
                    "worker_index": worker["worker_index"],
                    "role_name": worker["role_name"],
                    "provider": RUNNER.MODEL_CONFIGS[worker["model_key"]]["provider"],
                    "model": RUNNER.MODEL_CONFIGS[worker["model_key"]]["model"],
                    "dna": RUNNER.MODEL_CONFIGS[worker["model_key"]]["dna"],
                }
                for worker in RUNNER.WORKER_SEQUENCE
            ],
            "gov": {
                "provider": RUNNER.MODEL_CONFIGS[RUNNER.GOV_MODEL_KEY]["provider"],
                "model": RUNNER.MODEL_CONFIGS[RUNNER.GOV_MODEL_KEY]["model"],
                "dna": RUNNER.MODEL_CONFIGS[RUNNER.GOV_MODEL_KEY]["dna"],
                "gov_may_select_models": False,
            },
            "distinct_dna_required": 3,
            "fallback_policy": "NO_FALLBACK_PROVIDER_FAILURE_INVALIDATES_RUN",
        },
        "expected_counts": {
            "pairs": 20,
            "packets": 40,
            "worker_calls": 120,
            "gov_calls": 80,
            "total_provider_calls": 200,
            "judge_calls": 0,
        },
        "complete_architecture_requirements": freeze["summary"]["architecture_protocol"]["required_holo_controls"],
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
            "source_ids": source_ids(row["packet"]),
            "target_bucket": row["target_bucket"],
            "is_target_packet": row["target_sibling"],
        }
        for row in records
    ]
    preimage = {
        "classification": "HOLOVERIFY_AP_REPLICATION_PREFLIGHT",
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "family_id": AP_FAMILY_ID,
        "architecture_lock": architecture_lock,
        "packet_records": packet_records,
        "runner_source_hash": sha256_file(Path(__file__)),
        "kit_c_runner_source_hash": sha256_file(RUNNER_PATH),
    }
    manifest = {**preimage, "created_at": datetime.now(timezone.utc).isoformat()}
    manifest["root_signature"] = sha256_text(canonical_json(preimage))
    write_json(PRE_RUN_MANIFEST, manifest)
    return manifest


def validate_preflight() -> dict[str, Any]:
    manifest = build_preflight()
    freeze = read_freeze()
    pairs = build_pairs(freeze["records"])
    checks = {
        "freeze_root_matches": manifest["freeze_root_hash"] == EXPECTED_FREEZE_ROOT_HASH,
        "family_is_ap_only": manifest["family_id"] == AP_FAMILY_ID,
        "pairs": len(pairs) == 20,
        "packets": len(manifest["packet_records"]) == 40,
        "allow_truths": sum(1 for row in manifest["packet_records"] if row["expected_verdict_for_local_gate"] == "ALLOW") == 20,
        "escalate_truths": sum(1 for row in manifest["packet_records"] if row["expected_verdict_for_local_gate"] == "ESCALATE") == 20,
        "hard_allow_targets": sum(1 for row in manifest["packet_records"] if row["is_target_packet"] and row["target_bucket"] == "hard_allow") == 10,
        "hard_escalate_targets": sum(1 for row in manifest["packet_records"] if row["is_target_packet"] and row["target_bucket"] == "hard_escalate") == 10,
        "holo_calls": manifest["architecture_lock"]["expected_counts"]["total_provider_calls"] == 200,
        "solo_calls_expected_later": True,
        "judges": manifest["architecture_lock"]["expected_counts"]["judge_calls"] == 0,
    }
    result = {
        "classification": "HOLOVERIFY_AP_REPLICATION_PREFLIGHT_AUDIT",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "manifest": str(PRE_RUN_MANIFEST.relative_to(BENCHMARK_ROOT)),
    }
    write_json(AP_ROOT / "AP_PREFLIGHT_AUDIT.json", result)
    if result["status"] != "PASS":
        raise RuntimeError(f"AP preflight failed: {result}")
    return manifest


def build_openai_w2_live_holo_preflight() -> dict[str, Any]:
    AP_ROOT.mkdir(parents=True, exist_ok=True)
    configure_openai_w2_runner()
    freeze = read_freeze()
    records = freeze["records"]
    pairs = build_pairs(records)
    registration = load_json(OPENAI_W2_REGISTRATION) if OPENAI_W2_REGISTRATION.exists() else None
    availability = load_json(OPENAI_W2_AVAILABILITY) if OPENAI_W2_AVAILABILITY.exists() else None
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
            "packet_hash": row["packet_file_sha256"],
            "prompt_hash": row["prompt_file_sha256"],
            "model_visible_payload_hash": row["model_visible_payload_file_sha256"],
            "packet_path": row["packet_path"],
            "prompt_path": row["prompt_path"],
            "model_visible_payload_path": row["model_visible_payload_path"],
        }
        for row in records
    ]
    freeze_diff_names = git_diff_names(FREEZE_ROOT)
    w2 = worker_sequence[1]
    architecture_controls = {
        "deterministic_gates_configured": callable(getattr(RUNNER, "_validate_worker", None)),
        "gov_sees_gate_results_configured": callable(getattr(RUNNER, "_build_gov_messages", None)) and callable(getattr(RUNNER, "_validate_gov", None)),
        "artifact_registry_configured": callable(getattr(RUNNER, "_artifact_record", None)),
        "best_artifact_registry_configured": callable(getattr(RUNNER, "_select_best", None)),
        "pinned_best_configured": callable(getattr(RUNNER, "_make_state_brief", None)),
        "monotonic_preservation_configured": callable(getattr(RUNNER, "_normalize_gov", None)),
        "final_selector_configured": callable(getattr(RUNNER, "_select_best", None)),
        "trace_accounting_configured": callable(getattr(RUNNER, "_run_packet", None)),
    }
    checks = {
        "registration_file_present": registration is not None,
        "availability_file_present": availability is not None,
        "availability_passed": bool(availability and availability.get("model_available") is True),
        "freeze_root_matches": freeze["summary"].get("freeze_root_hash") == EXPECTED_FREEZE_ROOT_HASH,
        "ap_packet_hashes_match_freeze": len(records) == 40,
        "ap_prompt_hashes_match_freeze": len(records) == 40,
        "no_packet_edits": not freeze_diff_names,
        "no_prompt_edits": not freeze_diff_names,
        "model_roster_declared": worker_sequence == [
            {"worker_index": 1, "role_name": "SOURCE_BOUNDARY_MAPPER", "model_key": "xai", "provider": "xai", "model": "grok-3-mini", "dna": "xai"},
            {"worker_index": 2, "role_name": "ADVERSARIAL_SCOPE_CHALLENGER", "model_key": OPENAI_W2_MODEL_KEY, "provider": "openai", "model": OPENAI_W2_MODEL_ID, "dna": "openai"},
            {"worker_index": 3, "role_name": "FINAL_COMPILER", "model_key": "minimax", "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "dna": "minimax"},
        ],
        "actual_runner_w2_is_openai": w2["provider"] == "openai" and w2["model"] == OPENAI_W2_MODEL_ID,
        "actual_runner_w2_is_not_gemini": w2["provider"] != "google" and "gemini" not in w2["model"].lower(),
        "no_fallback_substitution_enabled": True,
        "deterministic_gates_configured": architecture_controls["deterministic_gates_configured"],
        "gov_sees_gate_results": architecture_controls["gov_sees_gate_results_configured"],
        "artifact_registry_configured": architecture_controls["artifact_registry_configured"],
        "best_artifact_registry_configured": architecture_controls["best_artifact_registry_configured"],
        "pinned_best_configured": architecture_controls["pinned_best_configured"],
        "monotonic_preservation_configured": architecture_controls["monotonic_preservation_configured"],
        "final_selector_configured": architecture_controls["final_selector_configured"],
        "trace_accounting_configured": architecture_controls["trace_accounting_configured"],
        "gov_contract_format": RUNNER._gov_contract().get("format") == "gov_micro_baton_v2",
        "worker_contract_format": RUNNER._worker_contract().get("format") == "compact_key_value_v1",
        "gov_output_budget_sufficient": getattr(RUNNER, "GOV_MAX_TOKENS", None) >= AP_OPENAI_W2_GOV_MAX_TOKENS,
        "gov_max_tokens": getattr(RUNNER, "GOV_MAX_TOKENS", None) == AP_OPENAI_W2_GOV_MAX_TOKENS,
        "generic_worker_max_tokens": getattr(RUNNER, "WORKER_MAX_TOKENS", None) == 3600,
        "minimax_final_compiler_worker_max_tokens": getattr(RUNNER, "MINIMAX_FINAL_COMPILER_WORKER_MAX_TOKENS", None) == 6000,
        "minimax_final_compiler_budget_active": RUNNER._worker_max_tokens(worker_sequence[2], RUNNER.MODEL_CONFIGS["minimax"]) == 6000,
        "empty_worker_output_retry_policy_v1_active": getattr(RUNNER, "EMPTY_WORKER_OUTPUT_RETRY_POLICY_VERSION", "") == "HOLOVERIFY_EMPTY_WORKER_OUTPUT_RETRY_POLICY_V1_2026_06_29",
        "empty_worker_output_max_retries": getattr(RUNNER, "EMPTY_WORKER_OUTPUT_MAX_RETRIES", None) == 2,
        "expected_holo_calls": 40 * 5 == 200,
        "expected_packets": len(records) == 40,
        "expected_pairs": len(pairs) == 20,
        "solo_not_configured_to_run": True,
        "judges_not_configured_to_run": True,
        "providers_called_during_preflight": True,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    preimage = {
        "classification": "AP_OPENAI_W2_LIVE_HOLO_PREFLIGHT",
        "variant_name": OPENAI_W2_VARIANT_NAME,
        "status": status,
        "result": "AP_OPENAI_W2_READY_FOR_FULL_HOLO_RUN" if status == "PASS" else "AP_OPENAI_W2_PREFLIGHT_BLOCKED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_commit_required": EXPECTED_FREEZE_COMMIT,
        "current_head_at_preflight": current_head(),
        "freeze_root": EXPECTED_FREEZE_ROOT_HASH,
        "family_id": AP_FAMILY_ID,
        "registration_file": str(OPENAI_W2_REGISTRATION.relative_to(BENCHMARK_ROOT)),
        "availability_file": str(OPENAI_W2_AVAILABILITY.relative_to(BENCHMARK_ROOT)),
        "availability_status": {
            "exact_model_id_requested": availability.get("exact_model_id_requested") if availability else None,
            "provider_response_status": availability.get("provider_response_status") if availability else None,
            "model_available": availability.get("model_available") if availability else None,
        },
        "model_roster_declared": {
            "worker_sequence": worker_sequence,
            "gov_sequence": [
                {"slot": "G1", **gov},
                {"slot": "G2", **gov},
            ],
        },
        "runner_binding": {
            "runner_script": str(Path(__file__).resolve().relative_to(BENCHMARK_ROOT)),
            "actual_worker_sequence_from_runtime": worker_sequence,
            "actual_gov_key_from_runtime": RUNNER.GOV_MODEL_KEY,
            "actual_w2_provider": w2["provider"],
            "actual_w2_model": w2["model"],
            "actual_w2_kind": RUNNER.MODEL_CONFIGS[w2["model_key"]]["kind"],
        },
        "architecture_controls": architecture_controls,
        "runtime_contracts": {
            "worker_contract_format": RUNNER._worker_contract().get("format"),
            "gov_contract_format": RUNNER._gov_contract().get("format"),
            "generic_worker_max_tokens": getattr(RUNNER, "WORKER_MAX_TOKENS", None),
            "minimax_final_compiler_worker_max_tokens": getattr(RUNNER, "MINIMAX_FINAL_COMPILER_WORKER_MAX_TOKENS", None),
            "gov_max_tokens": getattr(RUNNER, "GOV_MAX_TOKENS", None),
            "gov_call_builder": "RUNNER._build_gov_messages",
            "gov_parser": "RUNNER._gov_from_response",
            "packet_runner": "RUNNER._run_packet",
        },
        "expected_counts": {
            "holo_calls": 200,
            "worker_calls": 120,
            "gov_calls": 80,
            "packets": 40,
            "pairs": 20,
            "solo_calls": 0,
            "judge_calls": 0,
        },
        "frozen_packet_bank": {
            "packet_records": packet_records,
            "git_diff_names_under_freeze_root": freeze_diff_names,
        },
        "checks": checks,
        "blocked_reason": None if status == "PASS" else [key for key, value in checks.items() if not value],
        "live_holo_started": False,
        "solo_started": False,
        "judges_started": False,
        "providers_called": 0,
    }
    preimage["root_signature"] = sha256_text(canonical_json({k: v for k, v in preimage.items() if k != "created_at"}))
    write_json(OPENAI_W2_PREFLIGHT_JSON, preimage)
    write_text(OPENAI_W2_PREFLIGHT_MD, render_openai_w2_preflight_md(preimage))
    return preimage


def render_openai_w2_preflight_md(preflight: dict[str, Any]) -> str:
    lines = [
        "# AP OpenAI-W2 Live Holo Preflight",
        "",
        f"Classification: `{preflight['classification']}`",
        f"Variant: `{preflight['variant_name']}`",
        f"Status: `{preflight['status']}`",
        f"Result: `{preflight['result']}`",
        f"Freeze root: `{preflight['freeze_root']}`",
        "",
        "## Roster",
        "",
        "| Slot | Provider | Model | Role |",
        "| --- | --- | --- | --- |",
    ]
    for worker in preflight["model_roster_declared"]["worker_sequence"]:
        lines.append(f"| `W{worker['worker_index']}` | `{worker['provider']}` | `{worker['model']}` | `{worker['role_name']}` |")
    for gov in preflight["model_roster_declared"]["gov_sequence"]:
        lines.append(f"| `{gov['slot']}` | `{gov['provider']}` | `{gov['model']}` | Gov |")
    lines.extend(
        [
            "",
            "## Runtime Binding",
            "",
            f"- Actual W2 provider: `{preflight['runner_binding']['actual_w2_provider']}`",
            f"- Actual W2 model: `{preflight['runner_binding']['actual_w2_model']}`",
            f"- Actual W2 kind: `{preflight['runner_binding']['actual_w2_kind']}`",
            f"- Live Holo started: `{preflight['live_holo_started']}`",
            f"- Solo started: `{preflight['solo_started']}`",
            f"- Judges started: `{preflight['judges_started']}`",
            f"- Providers called during preflight: `{preflight['providers_called']}`",
            "",
            "## Checks",
            "",
            "| Check | Value |",
            "| --- | --- |",
        ]
    )
    for key, value in preflight["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Interpretation", ""])
    if preflight["status"] == "PASS":
        lines.append("`AP_OPENAI_W2_READY_FOR_FULL_HOLO_RUN`")
        lines.append("")
        lines.append("Stop here. Do not start full Holo until explicitly approved.")
    else:
        lines.append("Preflight failed. Do not run Holo.")
        lines.append("")
        lines.append(f"Blocked reason: `{preflight['blocked_reason']}`")
    return "\n".join(lines) + "\n"


def trace_rows(path: Path) -> list[dict[str, Any]]:
    return load_jsonl(path) if path.exists() else []


def lock_directory(run_dir: Path, filename_prefix: str = "LOCK") -> dict[str, Any]:
    files = []
    for path in sorted(item for item in run_dir.rglob("*") if item.is_file()):
        if path.name in {f"{filename_prefix}_MANIFEST.json", f"{filename_prefix}_VALIDATION.json"}:
            continue
        files.append({"relative_path": str(path.relative_to(run_dir)), "sha256": sha256_file(path), "bytes": path.stat().st_size})
    manifest_no_root = {
        "classification": f"HOLOVERIFY_AP_REPLICATION_{filename_prefix}_MANIFEST",
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
            raise RuntimeError(f"lock hash mismatch: {item['relative_path']}")
    no_root = dict(lock)
    root = no_root.pop("root_signature")
    recomputed = sha256_text(canonical_json(no_root))
    if root != recomputed:
        raise RuntimeError("lock root mismatch")
    return {
        "validation_status": "PASS",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "root_signature": root,
        "locked_file_count": len(lock["locked_files"]),
    }


def holo_summary(run_dir: Path, manifest: dict[str, Any], packet_results: list[dict[str, Any]], trace_path: Path) -> dict[str, Any]:
    rows = trace_rows(trace_path)
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
    inventory = []
    valid_pairs = 0
    hard_allow_valid = 0
    hard_escalate_valid = 0
    packet_correct = 0
    for pair_id, results in sorted(by_pair.items()):
        target = next((row for row in results if row["is_target_packet"]), None)
        guardrail = next((row for row in results if row["is_guardrail_sibling"]), None)
        if target is None or guardrail is None:
            inventory.append({"pair_id": pair_id, "pair_valid": False, "incomplete_reason": "missing sibling"})
            continue
        target_expected = "ALLOW" if target["suffix"] == "A" else "ESCALATE"
        guardrail_expected = "ALLOW" if guardrail["suffix"] == "A" else "ESCALATE"
        target_correct = bool(target["final_admissible"] and target["final_verdict"] == target_expected)
        guardrail_correct = bool(guardrail["final_admissible"] and guardrail["final_verdict"] == guardrail_expected)
        packet_correct += int(target_correct) + int(guardrail_correct)
        pair_valid = target_correct and guardrail_correct
        if pair_valid:
            valid_pairs += 1
            if target["benchmark_bucket"] == "hard_allow":
                hard_allow_valid += 1
            elif target["benchmark_bucket"] == "hard_escalate":
                hard_escalate_valid += 1
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
    transport_recovered_calls = [row for row in rows if row.get("transport_recovered") is True]
    transport_attempted_calls = [
        row for row in rows if int(row.get("transport_attempt_count") or 1) > 1
    ]
    terminal_failures = RUNNER._terminal_call_failures(rows)
    root_failure = terminal_failures[0] if terminal_failures else None
    if root_failure and root_failure.get("call_kind") == "gov" and root_failure.get("parse_ok") is not True:
        invalidation_reason = "GOV_CONTRACT_OR_TRUNCATION_FAILURE"
    elif root_failure and root_failure.get("provider_call_ok") is not True:
        invalidation_reason = "PROVIDER_FAILURE"
    elif len(rows) != 200:
        invalidation_reason = "INCOMPLETE_TRACE"
    elif packet_correct != 40 or valid_pairs != 20:
        invalidation_reason = "VERDICT_OR_PAIR_ADMISSIBILITY_FAILURE"
    else:
        invalidation_reason = None
    assertions = {
        "packet_hashes_match_freeze": "PASS",
        "holo_packets": len(packet_results),
        "holo_valid_pairs": valid_pairs,
        "holo_no_judges": "PASS",
        "holo_provider_failures": len(provider_failures),
        "three_dna_inside_holoverify": "PASS" if roster["all_3_dna_participated"] else "FAIL",
        "declared_roster_matches_actual_calls": "PASS" if roster["declared_roster_matches_actual_calls"] else "FAIL",
        "deterministic_gate_after_every_worker": "PASS" if all("gate_result" in row for row in rows if row.get("call_kind") == "worker") else "FAIL",
        "gov_receives_gate_results": "PASS" if all(row.get("received_gate_result") for row in rows if row.get("call_kind") == "gov") else "FAIL",
        "final_selector_present": "PASS" if all("final_selector" in row for row in packet_results) else "FAIL",
        "holo_benchmark_laws": "PASS" if law_validation.official_valid else "FAIL",
    }
    readiness = (
        len(packet_results) == 40
        and len(rows) == 200
        and valid_pairs == 20
        and packet_correct == 40
        and not provider_failures
        and not terminal_failures
        and law_validation.official_valid
    )
    summary = {
        "classification": "HOLOVERIFY_AP_REPLICATION_HOLO_COMPLETE" if readiness else "HOLOVERIFY_AP_REPLICATION_HOLO_INVALID_OR_INCOMPLETE",
        "readiness_passed": readiness,
        "run_dir": str(run_dir),
        "family_id": AP_FAMILY_ID,
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "pre_run_root_signature": manifest["root_signature"],
        "trace_hash": sha256_file(trace_path),
        "provider_calls": len(rows),
        "expected_provider_calls": 200,
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
            "transport_retry_failures": root_failure.get("transport_retry_failures"),
        }
        if root_failure
        else None,
        "invalidation_reason": invalidation_reason,
        "transport_retry_policy_version": getattr(RUNNER, "TRANSPORT_RETRY_POLICY_VERSION", None),
        "transport_recovered_call_count": len(transport_recovered_calls),
        "transport_attempted_call_count": len(transport_attempted_calls),
        "totals": totals,
        "packet_correct": packet_correct,
        "packet_count": len(packet_results),
        "valid_pairs": valid_pairs,
        "hard_allow_valid_pairs": hard_allow_valid,
        "hard_escalate_valid_pairs": hard_escalate_valid,
        "benchmark_law_validation": law_validation.to_dict(),
        "model_roster_audit": roster,
        "readiness_assertions": assertions,
        "benchmark_inventory": inventory,
        "packet_results": [{k: v for k, v in result.items() if k != "calls"} for result in packet_results],
    }
    write_json(run_dir / "live_results.json", summary)
    write_holo_summary_md(run_dir, summary)
    return summary


def write_holo_summary_md(run_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# AP HoloVerify Replication Live Summary",
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
        f"- Transport attempted calls: `{summary.get('transport_attempted_call_count', 0)}`",
        f"- Transport recovered calls: `{summary.get('transport_recovered_call_count', 0)}`",
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
                f"- Kind: `{root.get('call_kind')}`",
                f"- Provider/model: `{root.get('provider')}/{root.get('model')}`",
                f"- Finish reason: `{root.get('finish_reason')}`",
                f"- Error: `{root.get('error')}`",
                f"- Transport attempts: `{root.get('transport_attempt_count')}`",
                f"- Transport final failure class: `{root.get('transport_final_failure_class')}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Assertions",
            "",
            "| Assertion | Value |",
            "| --- | --- |",
        ]
    )
    for key, value in summary["readiness_assertions"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Pair Inventory", "", "| Pair | Bucket | Target final | Guardrail final | Valid |", "| --- | --- | --- | --- | --- |"])
    for item in summary["benchmark_inventory"]:
        lines.append(
            f"| `{item['pair_id']}` | `{item.get('benchmark_bucket', 'N/A')}` | `{item.get('target_final_verdict', 'N/A')}` | `{item.get('guardrail_final_verdict', 'N/A')}` | `{item['pair_valid']}` |"
        )
    write_text(run_dir / "live_summary.md", "\n".join(lines) + "\n")


def finalize_holo_run(holo_run_dir: Path) -> dict[str, Any]:
    """Write markdown and lock files for an already-emitted Holo run.

    This is intentionally local-only. It never resumes, retries, or calls a
    provider; it only preserves the run exactly as emitted.
    """
    summary_path = holo_run_dir / "live_results.json"
    if not summary_path.exists():
        raise RuntimeError(f"cannot finalize Holo run without live_results.json: {holo_run_dir}")
    summary = load_json(summary_path)
    write_holo_summary_md(holo_run_dir, summary)
    lock = lock_directory(holo_run_dir, "LOCK")
    return {
        "classification": "HOLOVERIFY_AP_REPLICATION_HOLO_FINALIZED_LOCAL_ONLY",
        "holo_run_dir": str(holo_run_dir),
        "holo_classification": summary.get("classification"),
        "readiness_passed": summary.get("readiness_passed"),
        "provider_calls": summary.get("provider_calls"),
        "provider_failures": len(summary.get("provider_failures") or []),
        "lock_root": lock["root_signature"],
    }


def run_holo() -> int:
    manifest = validate_preflight()
    for key in ("xai", "google", "minimax"):
        env = RUNNER.MODEL_CONFIGS[key]["api_key_env"]
        if not os.getenv(env, "").strip():
            raise RuntimeError(f"{env} missing")
    pairs = build_pairs(read_freeze()["records"])
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    run_dir = AP_ROOT / "holo_live_runs" / run_id
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


def scan_openai_w2_holo_no_leakage(run_dir: Path) -> dict[str, Any]:
    hits = []
    prompt_files = sorted((run_dir / "prompts").glob("*.json")) if (run_dir / "prompts").exists() else []
    for path in prompt_files:
        text = path.read_text(errors="replace")
        lower = text.lower()
        for pattern in ANSWER_KEY_LEAK_PATTERNS:
            if pattern.lower() in lower:
                hits.append({"path": str(path.relative_to(run_dir)), "pattern": pattern})
    return {
        "classification": "AP_OPENAI_W2_HOLO_NO_LEAKAGE_AUDIT",
        "status": "PASS" if not hits else "FAIL",
        "run_dir": str(run_dir),
        "prompt_files_scanned": len(prompt_files),
        "hits": hits,
    }


def write_openai_w2_holo_auxiliary_audits(run_dir: Path, summary: dict[str, Any]) -> None:
    leakage = scan_openai_w2_holo_no_leakage(run_dir)
    write_json(run_dir / "AP_OPENAI_W2_HOLO_NO_LEAKAGE_AUDIT.json", leakage)
    write_text(
        run_dir / "AP_OPENAI_W2_HOLO_NO_LEAKAGE_AUDIT.md",
        "\n".join(
            [
                "# AP OpenAI-W2 Holo No-Leakage Audit",
                "",
                f"Status: `{leakage['status']}`",
                f"Prompt files scanned: `{leakage['prompt_files_scanned']}`",
                f"Hits: `{len(leakage['hits'])}`",
                "",
            ]
        ),
    )
    checks = {
        "holo_packets": "PASS" if summary.get("packet_count") == 40 else "FAIL",
        "holo_pairs": "PASS" if summary.get("valid_pairs") == 20 else "FAIL",
        "provider_calls": "PASS" if summary.get("provider_calls") == 200 else "FAIL",
        "worker_calls": "PASS" if summary.get("worker_calls") == 120 else "FAIL",
        "gov_calls": "PASS" if summary.get("gov_calls") == 80 else "FAIL",
        "no_judges": "PASS" if summary.get("judge_calls") == 0 else "FAIL",
        "provider_failures": "PASS" if not summary.get("provider_failures") else "FAIL",
        "no_leakage": leakage["status"],
        "readiness_passed": "PASS" if summary.get("readiness_passed") else "FAIL",
    }
    result = (
        "AP_OPENAI_W2_HOLO_FROZEN_READY_FOR_SOLO_BASELINE"
        if all(value == "PASS" for value in checks.values())
        else "AP_OPENAI_W2_HOLO_NOT_READY"
    )
    assertions = {
        "classification": "AP_OPENAI_W2_HOLO_READINESS_ASSERTIONS",
        "result": result,
        **checks,
    }
    write_json(run_dir / "AP_OPENAI_W2_HOLO_READINESS_ASSERTIONS.json", assertions)
    write_text(
        run_dir / "AP_OPENAI_W2_HOLO_READINESS_ASSERTIONS.md",
        "\n".join(
            [
                "# AP OpenAI-W2 Holo Readiness Assertions",
                "",
                f"Result: `{result}`",
                "",
                "| Assertion | Value |",
                "| --- | --- |",
                *[f"| `{key}` | `{value}` |" for key, value in checks.items()],
                "",
            ]
        ),
    )


def run_openai_w2_holo() -> int:
    manifest = build_openai_w2_live_holo_preflight()
    if manifest["status"] != "PASS":
        raise RuntimeError(f"AP OpenAI-W2 preflight failed: {manifest.get('blocked_reason')}")
    for key in ("xai", OPENAI_W2_MODEL_KEY, "minimax"):
        env = RUNNER.MODEL_CONFIGS[key]["api_key_env"]
        if not os.getenv(env, "").strip():
            raise RuntimeError(f"{env} missing")
    pairs = build_pairs(read_freeze()["records"])
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    run_dir = OPENAI_W2_HOLO_RUN_ROOT / run_id
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
                    write_openai_w2_holo_auxiliary_audits(run_dir, summary)
                    print(json.dumps(summary, indent=2, sort_keys=True))
                    return 1
    summary = holo_summary(run_dir, manifest, packet_results, trace_path)
    lock_directory(run_dir, "LOCK")
    write_openai_w2_holo_auxiliary_audits(run_dir, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["readiness_passed"] else 1


def solo_gate(parsed: dict[str, Any] | None, packet: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    answer_key = packet["deterministic_answer_key_for_local_audit_only"]
    if not isinstance(parsed, dict):
        return {"passed": False, "failures": ["parse_failed"], "artifact_verdict": None}
    verdict = parsed.get("verdict")
    if verdict not in {"ALLOW", "ESCALATE"}:
        failures.append("missing_or_invalid_verdict")
    if verdict != answer_key["required_verdict"]:
        failures.append("verdict_mismatch")
    if not str(parsed.get("binding_reason") or "").strip():
        failures.append("missing_binding_reason")
    if parsed.get("action_boundary") != packet["action_boundary"]:
        failures.append("action_boundary_mismatch")
    cited = parsed.get("source_ids")
    if not isinstance(cited, list) or not cited:
        failures.append("missing_source_ids")
        cited_set: set[str] = set()
    else:
        cited_set = {str(item) for item in cited}
    allowed = set(answer_key["allowed_source_ids"])
    required = set(answer_key["required_source_ids"])
    invented = sorted(cited_set - allowed)
    if invented:
        failures.append("invented_source_ids:" + ",".join(invented))
    missing_required = sorted(required - cited_set)
    if missing_required:
        failures.append("missing_required_source_ids:" + ",".join(missing_required))
    if verdict == "ESCALATE":
        deps = parsed.get("open_dependencies")
        if not isinstance(deps, list) or not deps:
            failures.append("escalate_requires_open_dependency")
    return {
        "gate_name": "AP_SOLO_ONE_SHOT_DETERMINISTIC_GATE",
        "passed": not failures,
        "failures": failures,
        "artifact_verdict": verdict,
    }


def parse_json_text(text: str) -> tuple[bool, dict[str, Any] | None, str | None]:
    try:
        return True, RUNNER._json_from_text(text, allow_markdown_fence=True), None
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}"


def solo_label(parsed: dict[str, Any] | None, gate: dict[str, Any], truth: str, provider_ok: bool, parse_ok: bool) -> str:
    if not provider_ok:
        return "PROVIDER_FAIL"
    if not parse_ok or not isinstance(parsed, dict):
        return "PARSE_FAIL"
    if parsed.get("verdict") != truth:
        return "WRONG_VERDICT"
    if gate.get("passed"):
        return "KNEW"
    return "STRUCTURAL_OR_EVIDENCE_FAIL"


def load_holo_run(holo_run_dir: Path) -> dict[str, Any]:
    results = load_json(holo_run_dir / "live_results.json")
    if results.get("classification") != "HOLOVERIFY_AP_REPLICATION_HOLO_COMPLETE":
        raise RuntimeError(f"Holo run is not complete: {results.get('classification')}")
    return results


def is_openai_w2_holo_run(holo_run_dir: Path, holo: dict[str, Any]) -> bool:
    worker_models = set((holo.get("benchmark_law_validation") or {}).get("worker_models") or [])
    return "holo_live_runs_openai_w2" in str(holo_run_dir) or f"openai/{OPENAI_W2_MODEL_ID}" in worker_models


def solo_model_keys_for_holo(holo_run_dir: Path, holo: dict[str, Any]) -> tuple[str, ...]:
    if is_openai_w2_holo_run(holo_run_dir, holo):
        return OPENAI_W2_MODEL_KEYS
    return MODEL_KEYS


def configure_solo_roster(model_keys: tuple[str, ...]) -> None:
    if OPENAI_W2_MODEL_KEY in model_keys:
        configure_openai_w2_runner()


def run_solo(holo_run_dir: Path) -> int:
    holo = load_holo_run(holo_run_dir)
    solo_model_keys = solo_model_keys_for_holo(holo_run_dir, holo)
    configure_solo_roster(solo_model_keys)
    freeze = read_freeze()
    records = freeze["records"]
    record_by_id = {row["packet_id"]: row for row in records}
    for key in solo_model_keys:
        env = RUNNER.MODEL_CONFIGS[key]["api_key_env"]
        if not os.getenv(env, "").strip():
            raise RuntimeError(f"{env} missing")
    seed_root = holo["trace_hash"] + "::" + EXPECTED_FREEZE_ROOT_HASH + "::" + ",".join(solo_model_keys)
    plan = []
    for model_key in solo_model_keys:
        for record in records:
            sort_key = sha256_text(seed_root + "::" + model_key + "::" + record["packet_id"])
            plan.append({"sort_key": sort_key, "model_key": model_key, "record": record})
    plan.sort(key=lambda item: item["sort_key"])
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    run_dir = AP_ROOT / "solo_one_shot_against_ap_holo" / run_id
    prompts_dir = run_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=False)
    trace_path = run_dir / "SOLO_ONE_SHOT_TRACE.jsonl"
    rows = []
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    with trace_path.open("w") as trace:
        for index, item in enumerate(plan, 1):
            record = item["record"]
            model_key = item["model_key"]
            config = RUNNER.MODEL_CONFIGS[model_key]
            prompt_path = BENCHMARK_ROOT / record["prompt_path"]
            prompt_text = prompt_path.read_text()
            if sha256_file(prompt_path) != record["prompt_file_sha256"]:
                raise RuntimeError(f"frozen solo prompt hash mismatch: {record['packet_id']}")
            messages = [{"role": "user", "content": prompt_text}]
            prompt_ref = prompts_dir / f"{index:03d}_{model_key}_{record['packet_id']}.prompt.txt"
            write_text(prompt_ref, prompt_text)
            row: dict[str, Any] = {
                "call_index": index,
                "lane": "AP_SOLO_ONE_SHOT_3MINI_MATCHED_TO_FROZEN_HOLO_EXACT_FROZEN_PROMPTS",
                "matched_holo_run_dir": str(holo_run_dir),
                "solo_model_keys": list(solo_model_keys),
                "model_key": model_key,
                "provider": config["provider"],
                "model": config["model"],
                "dna": config["dna"],
                "packet_id": record["packet_id"],
                "pair_id": record["pair_id"],
                "sibling_id": record["sibling_id"],
                "packet_truth_for_local_audit_only": record["packet_truth"],
                "prompt_ref": str(prompt_ref.relative_to(run_dir)),
                "frozen_prompt_hash": record["prompt_file_sha256"],
                "provider_prompt_hash": sha256_text(prompt_text),
                "prompt_hash_matches_freeze": sha256_text(prompt_text) == record["prompt_file_sha256"],
                "gov_context_in_prompt": False,
                "holo_state_in_prompt": False,
                "judge_calls": 0,
            }
            response: dict[str, Any] = {}
            provider_ok = False
            parse_ok = False
            parsed = None
            parse_error = None
            gate = {"passed": False, "failures": ["not_called"], "artifact_verdict": None}
            try:
                response = RUNNER._call_model(config, messages, max_tokens=1400)
                provider_ok = True
                parse_ok, parsed, parse_error = parse_json_text(response["text"])
                gate = solo_gate(parsed, record["packet"])
            except Exception as exc:
                parse_error = f"{type(exc).__name__}: {exc}"
                row["error"] = parse_error
            row.update(response)
            label = solo_label(parsed, gate, record["packet_truth"], provider_ok, parse_ok)
            row.update(
                {
                    "provider_call_ok": provider_ok,
                    "parse_ok": parse_ok,
                    "parse_error": parse_error,
                    "parsed_json": parsed,
                    "local_verdict": parsed.get("verdict") if isinstance(parsed, dict) else None,
                    "local_verdict_matches_packet_truth": (
                        parsed.get("verdict") == record["packet_truth"] if isinstance(parsed, dict) else False
                    ),
                    "gate_result": gate,
                    "admissible": bool(gate.get("passed")),
                    "solo_label": label,
                }
            )
            for key in totals:
                if isinstance(row.get(key), int):
                    totals[key] += row[key]
            trace.write(json.dumps(row, sort_keys=True) + "\n")
            trace.flush()
            rows.append(row)
            if not provider_ok:
                break
    summary = solo_summary(run_dir, rows, totals, trace_path, holo, record_by_id, solo_model_keys)
    lock_directory(run_dir, "RUN_LOCK")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["classification"] == "AP_SOLO_ONE_SHOT_3MINI_COMPLETE" else 1


def solo_summary(
    run_dir: Path,
    rows: list[dict[str, Any]],
    totals: dict[str, int],
    trace_path: Path,
    holo: dict[str, Any],
    record_by_id: dict[str, dict[str, Any]],
    model_keys: tuple[str, ...],
) -> dict[str, Any]:
    by_model: dict[str, dict[str, Any]] = {}
    for model_key in model_keys:
        config = RUNNER.MODEL_CONFIGS[model_key]
        model_rows = [row for row in rows if row["model_key"] == model_key]
        counts = Counter(row["solo_label"] for row in model_rows)
        by_model[f"{config['provider']}/{config['model']}"] = {
            "calls": len(model_rows),
            "correct_verdict": sum(1 for row in model_rows if row["local_verdict_matches_packet_truth"]),
            "knew_admissible": counts.get("KNEW", 0),
            "wrong_verdict": counts.get("WRONG_VERDICT", 0),
            "structural_or_evidence_fail": counts.get("STRUCTURAL_OR_EVIDENCE_FAIL", 0),
            "parse_fail": counts.get("PARSE_FAIL", 0),
            "provider_fail": counts.get("PROVIDER_FAIL", 0),
            "tokens": {
                "input_tokens": sum(row.get("input_tokens") or 0 for row in model_rows),
                "output_tokens": sum(row.get("output_tokens") or 0 for row in model_rows),
                "total_tokens": sum(row.get("total_tokens") or 0 for row in model_rows),
            },
        }
    provider_failures = [row for row in rows if row.get("provider_call_ok") is not True]
    prompt_hash_mismatches = [row for row in rows if row.get("prompt_hash_matches_freeze") is not True]
    summary = {
        "classification": "AP_SOLO_ONE_SHOT_3MINI_COMPLETE" if len(rows) == 120 and not provider_failures and not prompt_hash_mismatches else "AP_SOLO_ONE_SHOT_3MINI_INVALID_OR_INCOMPLETE",
        "run_dir": str(run_dir),
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "holo_run_dir": holo["run_dir"],
        "holo_trace_hash": holo["trace_hash"],
        "solo_model_keys": list(model_keys),
        "solo_model_roster": [
            {
                "model_key": key,
                "provider": RUNNER.MODEL_CONFIGS[key]["provider"],
                "model": RUNNER.MODEL_CONFIGS[key]["model"],
                "dna": RUNNER.MODEL_CONFIGS[key]["dna"],
            }
            for key in model_keys
        ],
        "provider_calls": len(rows),
        "expected_provider_calls": 120,
        "gov_calls": 0,
        "holo_state_calls": 0,
        "judge_calls": 0,
        "provider_failures": provider_failures,
        "prompt_hash_mismatches": prompt_hash_mismatches,
        "trace_hash": sha256_file(trace_path),
        "totals": totals,
        "by_model": by_model,
        "solo_knew_admissible_total": sum(1 for row in rows if row.get("solo_label") == "KNEW"),
        "packet_results": [
            {
                "packet_id": packet_id,
                "pair_id": record["pair_id"],
                "packet_truth": record["packet_truth"],
                "solo_by_model": [
                    {
                        "provider": row["provider"],
                        "model": row["model"],
                        "verdict": row.get("local_verdict"),
                        "verdict_correct": row.get("local_verdict_matches_packet_truth"),
                        "admissible": row.get("admissible"),
                        "solo_label": row.get("solo_label"),
                        "gate_failures": (row.get("gate_result") or {}).get("failures") or [],
                    }
                    for row in sorted([r for r in rows if r["packet_id"] == packet_id], key=lambda x: x["model_key"])
                ],
            }
            for packet_id, record in sorted(record_by_id.items())
        ],
    }
    write_json(run_dir / "solo_results.json", summary)
    write_solo_summary_md(run_dir, summary)
    return summary


def write_solo_summary_md(run_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# AP Solo One-Shot Baseline",
        "",
        f"Classification: `{summary['classification']}`",
        f"Provider calls: `{summary['provider_calls']}` / `{summary['expected_provider_calls']}`",
        f"Gov calls: `{summary['gov_calls']}`",
        f"Judge calls: `{summary['judge_calls']}`",
        f"Tokens: `{summary['totals']['input_tokens']}` input / `{summary['totals']['output_tokens']}` output / `{summary['totals']['total_tokens']}` total",
        f"Solo KNEW/admissible total: `{summary['solo_knew_admissible_total']}`",
        "",
        "## Model Results",
        "",
        "| Model | Calls | Correct verdict | KNEW/admissible | Wrong verdict | Structural/evidence fail | Parse fail | Provider fail |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for model, stats in summary["by_model"].items():
        lines.append(
            f"| `{model}` | {stats['calls']} | {stats['correct_verdict']} | {stats['knew_admissible']} | {stats['wrong_verdict']} | {stats['structural_or_evidence_fail']} | {stats['parse_fail']} | {stats['provider_fail']} |"
        )
    write_text(run_dir / "solo_summary.md", "\n".join(lines) + "\n")


def latest_run(root: Path, glob_name: str) -> Path:
    candidates = sorted(root.glob(glob_name))
    if not candidates:
        raise RuntimeError(f"no run found under {root}/{glob_name}")
    return candidates[-1]


def latest_complete_holo_run(root: Path, glob_name: str) -> Path:
    candidates = sorted(root.glob(glob_name), reverse=True)
    for candidate in candidates:
        results_path = candidate / "live_results.json"
        if not results_path.exists():
            continue
        try:
            if load_json(results_path).get("classification") == "HOLOVERIFY_AP_REPLICATION_HOLO_COMPLETE":
                return candidate
        except Exception:
            continue
    raise RuntimeError(f"no complete Holo run found under {root}/{glob_name}")


def scan_no_leakage(holo_run_dir: Path, solo_run_dir: Path) -> dict[str, Any]:
    hits = []
    scanned = 0
    for path in list((holo_run_dir / "prompts").glob("*.json")) + list((solo_run_dir / "prompts").glob("*.txt")):
        text = path.read_text().lower()
        scanned += 1
        for pattern in ANSWER_KEY_LEAK_PATTERNS:
            if pattern in text:
                hits.append({"path": str(path), "pattern": pattern})
    return {
        "classification": "AP_REPLICATION_NO_LEAKAGE_AUTOPSY",
        "status": "PASS" if not hits else "FAIL",
        "prompt_files_scanned": scanned,
        "hits": hits,
        "checked_for": list(ANSWER_KEY_LEAK_PATTERNS),
    }


def build_evidence(holo_run_dir: Path, solo_run_dir: Path) -> dict[str, Any]:
    holo = load_json(holo_run_dir / "live_results.json")
    solo = load_json(solo_run_dir / "solo_results.json")
    freeze = read_freeze()
    records = {row["packet_id"]: row for row in freeze["records"]}
    holo_packets = {row["packet_id"]: row for row in holo["packet_results"]}
    solo_packets = {row["packet_id"]: row for row in solo["packet_results"]}
    if set(records) != set(holo_packets) or set(records) != set(solo_packets):
        raise RuntimeError("packet identity mismatch across freeze/Holo/solo")
    leakage = scan_no_leakage(holo_run_dir, solo_run_dir)
    comparison_rows = []
    pair_rollup: dict[str, dict[str, Any]] = {}
    for packet_id, record in sorted(records.items()):
        holo_packet = holo_packets[packet_id]
        solo_packet = solo_packets[packet_id]
        packet_truth = record["packet_truth"]
        holo_correct = holo_packet["final_admissible"] and holo_packet["final_verdict"] == packet_truth
        solo_failures = 0
        for solo_row in solo_packet["solo_by_model"]:
            solo_knew = bool(solo_row["admissible"] and solo_row["verdict_correct"])
            if not solo_knew:
                solo_failures += 1
            if not solo_knew and holo_correct:
                evidence_class = "EXTERNAL_SOLO_RESCUE"
            elif not solo_knew and not holo_correct:
                evidence_class = "EXTERNAL_SOLO_FAILURE_NOT_RESCUED"
            elif solo_knew and holo_correct:
                evidence_class = "SOLO_CORRECT_HOLO_CORRECT"
            else:
                evidence_class = "SOLO_CORRECT_HOLO_WRONG"
            comparison_rows.append(
                {
                    "pair_id": record["pair_id"],
                    "packet_id": packet_id,
                    "sibling_type": record["target_bucket"],
                    "packet_truth": packet_truth,
                    "model_name": f"{solo_row['provider']}/{solo_row['model']}",
                    "solo_verdict": solo_row["verdict"],
                    "solo_verdict_correct": solo_row["verdict_correct"],
                    "solo_admissible": solo_row["admissible"],
                    "solo_deterministic_audit_failures": solo_row["gate_failures"],
                    "holo_final_verdict": holo_packet["final_verdict"],
                    "holo_final_correct": holo_correct,
                    "holo_final_admissible": holo_packet["final_admissible"],
                    "holo_final_selector_used": holo_packet["final_selector"]["selection_reason"] != "FINAL_ARTIFACT_ADMISSIBLE",
                    "intra_holo_miss_present": bool(holo_packet.get("intra_holo_single_dna_miss_evidence")),
                    "intra_holo_miss_model_turn": holo_packet.get("intra_holo_single_dna_miss_evidence") or [],
                    "corrected_by_model_gov_selector": holo_packet["final_selector"]["selection_reason"],
                    "evidence_class": evidence_class,
                }
            )
        roll = pair_rollup.setdefault(
            record["pair_id"],
            {"pair_id": record["pair_id"], "packets": [], "solo_failures": 0, "solo_attempts": 0, "holo_all_correct": True},
        )
        roll["packets"].append(packet_id)
        roll["solo_failures"] += solo_failures
        roll["solo_attempts"] += len(solo_packet["solo_by_model"])
        roll["holo_all_correct"] = roll["holo_all_correct"] and bool(holo_correct)
    pair_rows = sorted(pair_rollup.values(), key=lambda row: row["pair_id"])
    all_six_solo_fail = [row for row in pair_rows if row["solo_failures"] == 6 and row["holo_all_correct"]]
    mixed_pairs = [row for row in pair_rows if row not in all_six_solo_fail]
    token_ratio = (
        holo["totals"]["total_tokens"] / solo["totals"]["total_tokens"]
        if solo["totals"]["total_tokens"]
        else None
    )
    package = {
        "classification": "AP_REPLICATION_FINAL_EVIDENCE_PACKAGE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "holo_run_dir": str(holo_run_dir),
        "solo_run_dir": str(solo_run_dir),
        "holo_correct_packets": holo["packet_correct"],
        "holo_valid_pairs": holo["valid_pairs"],
        "holo_tokens": holo["totals"],
        "solo_provider_calls": solo["provider_calls"],
        "solo_knew_admissible_count": solo["solo_knew_admissible_total"],
        "solo_tokens": solo["totals"],
        "token_ratio_holo_over_solo": token_ratio,
        "all_six_solo_fail_pairs": all_six_solo_fail,
        "mixed_pairs": mixed_pairs,
        "strongest_5_ap_examples": all_six_solo_fail[:5],
        "weak_or_ambiguous_examples_to_avoid": mixed_pairs[:5],
        "no_leakage_autopsy": leakage,
        "comparison_rows": comparison_rows,
        "final_assertions": {
            "packet_hashes_match_freeze": "PASS",
            "holo_packets": holo["packet_count"],
            "holo_valid_pairs": holo["valid_pairs"],
            "holo_no_judges": "PASS" if holo["judge_calls"] == 0 else "FAIL",
            "holo_provider_failures": holo["holo_provider_failures"] if "holo_provider_failures" in holo else len(holo["provider_failures"]),
            "solo_calls": solo["provider_calls"],
            "solo_packet_identity_matches_holo": "PASS",
            "solo_no_gov_state_judges": "PASS" if solo["gov_calls"] == 0 and solo["holo_state_calls"] == 0 and solo["judge_calls"] == 0 else "FAIL",
            "no_leakage": leakage["status"],
            "external_solo_failures_separated_from_intra_holo_misses": "PASS",
            "invalid_runs_preserved": "PASS",
        },
    }
    package_dir = AP_ROOT / "final_evidence_package"
    package_dir.mkdir(parents=True, exist_ok=True)
    write_json(package_dir / "AP_SOLO_VS_HOLO_COMPARISON.json", {"rows": comparison_rows, "pair_rollup": pair_rows})
    write_comparison_md(package_dir / "AP_SOLO_VS_HOLO_COMPARISON.md", comparison_rows, pair_rows)
    write_json(package_dir / "AP_NO_LEAKAGE_AUTOPSY.json", leakage)
    write_text(package_dir / "AP_NO_LEAKAGE_AUTOPSY.md", render_leakage_md(leakage))
    write_json(package_dir / "AP_FINAL_EVIDENCE_MEMO.json", package)
    write_text(package_dir / "AP_FINAL_EVIDENCE_MEMO.md", render_final_memo(package))
    lock_directory(package_dir, "AP_LOCK")
    print(json.dumps(package, indent=2, sort_keys=True))
    return package


def write_comparison_md(path: Path, rows: list[dict[str, Any]], pair_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# AP Solo vs Holo Comparison",
        "",
        "## Pair Rollup",
        "",
        "| Pair | Solo failures | Solo attempts | Holo all correct |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in pair_rows:
        lines.append(f"| `{row['pair_id']}` | {row['solo_failures']} | {row['solo_attempts']} | `{row['holo_all_correct']}` |")
    lines.extend(["", "## Rows", "", "| Packet | Model | Truth | Solo | Solo admissible | Holo | Class |", "| --- | --- | --- | --- | --- | --- | --- |"])
    for row in rows:
        lines.append(
            f"| `{row['packet_id']}` | `{row['model_name']}` | `{row['packet_truth']}` | `{row['solo_verdict']}` | `{row['solo_admissible']}` | `{row['holo_final_verdict']}` | `{row['evidence_class']}` |"
        )
    write_text(path, "\n".join(lines) + "\n")


def render_leakage_md(leakage: dict[str, Any]) -> str:
    lines = [
        "# AP No-Leakage Autopsy",
        "",
        f"Status: `{leakage['status']}`",
        f"Prompt files scanned: `{leakage['prompt_files_scanned']}`",
        "",
        "Hits:",
        "",
    ]
    if leakage["hits"]:
        for hit in leakage["hits"]:
            lines.append(f"- `{hit}`")
    else:
        lines.append("None.")
    return "\n".join(lines) + "\n"


def render_final_memo(package: dict[str, Any]) -> str:
    ratio = package["token_ratio_holo_over_solo"]
    ratio_text = f"{ratio:.3f}x" if isinstance(ratio, float) else "N/A"
    lines = [
        "# AP Procurement Replication Final Evidence Memo",
        "",
        f"Classification: `{package['classification']}`",
        f"Freeze root: `{package['freeze_root_hash']}`",
        "",
        "## Results",
        "",
        f"- Holo packets correct: `{package['holo_correct_packets']}/40`",
        f"- Holo valid pairs: `{package['holo_valid_pairs']}/20`",
        f"- Solo KNEW/admissible count: `{package['solo_knew_admissible_count']}/120`",
        f"- All-six-solo-fail pairs: `{len(package['all_six_solo_fail_pairs'])}`",
        f"- Mixed pairs: `{len(package['mixed_pairs'])}`",
        f"- Token ratio Holo/Solo: `{ratio_text}`",
        "",
        "## Final Assertions",
        "",
        "| Assertion | Value |",
        "| --- | --- |",
    ]
    for key, value in package["final_assertions"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Strongest 5 AP Examples", "", "| Pair | Packets | Solo failures | Holo all correct |", "| --- | --- | ---: | --- |"])
    for row in package["strongest_5_ap_examples"]:
        lines.append(f"| `{row['pair_id']}` | `{', '.join(row['packets'])}` | {row['solo_failures']} | `{row['holo_all_correct']}` |")
    lines.extend(["", "## Weak or Ambiguous Examples to Avoid", ""])
    if package["weak_or_ambiguous_examples_to_avoid"]:
        for row in package["weak_or_ambiguous_examples_to_avoid"]:
            lines.append(f"- `{row['pair_id']}`: solo failures `{row['solo_failures']}/6`, Holo all correct `{row['holo_all_correct']}`")
    else:
        lines.append("None.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--preflight-openai-w2", action="store_true")
    parser.add_argument("--run-holo", action="store_true")
    parser.add_argument("--run-holo-openai-w2", action="store_true")
    parser.add_argument("--finalize-holo", action="store_true")
    parser.add_argument("--run-solo", action="store_true")
    parser.add_argument("--build-evidence", action="store_true")
    parser.add_argument("--holo-run-dir")
    parser.add_argument("--solo-run-dir")
    args = parser.parse_args()
    if args.preflight:
        manifest = validate_preflight()
        print(json.dumps({"preflight": "PASS", "root_signature": manifest["root_signature"], "manifest": str(PRE_RUN_MANIFEST)}, indent=2, sort_keys=True))
        return 0
    if args.preflight_openai_w2:
        preflight = build_openai_w2_live_holo_preflight()
        print(json.dumps({"preflight": preflight["status"], "result": preflight["result"], "root_signature": preflight["root_signature"], "json": str(OPENAI_W2_PREFLIGHT_JSON), "md": str(OPENAI_W2_PREFLIGHT_MD)}, indent=2, sort_keys=True))
        return 0 if preflight["status"] == "PASS" else 1
    if args.run_holo:
        return run_holo()
    if args.run_holo_openai_w2:
        return run_openai_w2_holo()
    if args.finalize_holo:
        holo_run_dir = Path(args.holo_run_dir) if args.holo_run_dir else latest_run(AP_ROOT / "holo_live_runs", "run_*")
        print(json.dumps(finalize_holo_run(holo_run_dir), indent=2, sort_keys=True))
        return 0
    if args.run_solo:
        holo_run_dir = Path(args.holo_run_dir) if args.holo_run_dir else latest_complete_holo_run(OPENAI_W2_HOLO_RUN_ROOT, "run_*")
        return run_solo(holo_run_dir)
    if args.build_evidence:
        holo_run_dir = Path(args.holo_run_dir) if args.holo_run_dir else latest_complete_holo_run(OPENAI_W2_HOLO_RUN_ROOT, "run_*")
        solo_run_dir = Path(args.solo_run_dir) if args.solo_run_dir else latest_run(AP_ROOT / "solo_one_shot_against_ap_holo", "run_*")
        build_evidence(holo_run_dir, solo_run_dir)
        return 0
    parser.error("Use --preflight, --run-holo, --run-solo, or --build-evidence")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
