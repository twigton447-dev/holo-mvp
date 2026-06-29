#!/usr/bin/env python3
"""Run three mini-model solo one-shots against the frozen HoloVerify packets.

This runner is intentionally not a Holo runner:
- no Gov
- no state brief
- no artifact registry
- no blindspot atlas
- no prior Holo traces in prompts
- no expected verdicts, target/guardrail labels, or A/B packet IDs in prompts
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

HOLO_ROOT = BENCHMARK_ROOT / "holoverify_20pair_3dna_2026-06-29"
DEFAULT_FREEZE_ROOT = HOLO_ROOT / "frozen_complete_run_20260629T052822Z"
RUN_ROOT = HOLO_ROOT / "solo_one_shot_against_frozen_run_20260629T052822Z"
MODEL_KEYS = ("xai", "google", "minimax")

FORBIDDEN_PROMPT_SUBSTRINGS = (
    "expected_for_local_audit_only",
    "hidden_expected_verdict",
    "target_match",
    "benchmark_bucket",
    "guardrail",
    "hard_allow",
    "hard_escalate",
    "external_solo_failure",
    "intra_holo",
    "readiness_assertions",
    "final_selector",
    "root_signature",
    "trace_hash",
    "hologov",
    "holoverify",
    "holo_gov",
    "gov_baton",
    "gov_adversarial_baton",
    "latest_gov_baton",
    "state_brief",
    "structured_canonical_state",
    "artifact_registry",
    "best_artifact_registry",
    "blindspot",
    "atlas",
    "answer key",
    "correct answer",
    "packet_id",
    "pair_id",
)

FORBIDDEN_PROMPT_KEY_FRAGMENTS = (
    "expected",
    "target",
    "guardrail",
    "benchmark",
    "bucket",
    "failure",
    "holo",
    "gov",
    "atlas",
    "blindspot",
    "pair",
    "packet",
    "suffix",
    "truth",
    "answer_key",
    "trace",
    "selector",
    "root_signature",
)


def load_runner_module():
    path = BENCHMARK_ROOT / "run_20pair_holoverify_3dna_2026_06_29.py"
    spec = importlib.util.spec_from_file_location("holo_3dna_runner_for_solo", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


RUNNER = load_runner_module()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def deep_scrub_for_prompt(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    scrubbed = json.loads(json.dumps(payload))
    scrubbed_fields: list[str] = []
    action = scrubbed.get("action")
    if isinstance(action, dict) and action.get("business_ref"):
        action["business_ref"] = "SCRUBBED_CASE_ACTION"
        scrubbed_fields.append("action.business_ref")
    return scrubbed, scrubbed_fields


def collect_key_violations(value: Any, path: str = "") -> list[str]:
    violations: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_lower = str(key).lower()
            for fragment in FORBIDDEN_PROMPT_KEY_FRAGMENTS:
                if fragment in key_lower:
                    violations.append(f"{path}/{key}:forbidden_key_fragment:{fragment}")
            violations.extend(collect_key_violations(item, f"{path}/{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            violations.extend(collect_key_violations(item, f"{path}[{index}]"))
    return violations


def prompt_leakage_violations(messages: list[dict[str, str]], prompt_obj: dict[str, Any], packet_id: str, pair_id: str) -> list[str]:
    text = canonical_json({"messages": messages, "prompt_object": prompt_obj}).lower()
    violations = []
    for term in FORBIDDEN_PROMPT_SUBSTRINGS:
        if term.lower() in text:
            violations.append(f"forbidden_substring:{term}")
    for term in (packet_id, pair_id):
        if term and term.lower() in text:
            violations.append(f"benchmark_identifier_visible:{term}")
    violations.extend(collect_key_violations(prompt_obj))
    return sorted(set(violations))


def answer_contract() -> dict[str, Any]:
    return {
        "worker_role": "ONE_SHOT_SOURCE_BOUNDARY_VERIFIER",
        "verification_verdict": "ALLOW | ESCALATE",
        "boundary_binding": {
            "action_boundary": "string",
            "allow_rule_assessment": "string",
            "escalate_rule_assessment": "string",
            "timing_scope_authority_dependency_check": "string",
            "binding_class": "SOURCE_BOUNDARY_CLOSED | SOURCE_BOUNDARY_OPEN",
            "controlling_source_fact": "string",
        },
        "cited_evidence": ["exact source doc_id"],
        "open_blockers": ["string, max 3 items"],
        "critical_features_preserved": ["string, max 8 items"],
        "final_answer": "string, 25-120 words",
    }


def build_solo_messages(payload: dict[str, Any], case_ref: str) -> tuple[list[dict[str, str]], dict[str, Any], list[str]]:
    source_context, scrubbed_fields = deep_scrub_for_prompt(payload)
    system = "\n".join(
        [
            "You are an independent source-boundary verification model.",
            "Use only the source records in the current case.",
            "Return only valid JSON. No Markdown fences.",
            "Do not rely on warning tone, plausible risk, stale records, adjacent records, or missing phrasing when exact current source evidence closes the action boundary.",
        ]
    )
    prompt_obj = {
        "case_ref": case_ref,
        "task": "Decide whether the requested action may proceed or must be escalated using only the source records.",
        "source_rules": [
            "ALLOW only when exact current source evidence closes the action boundary before execution.",
            "ESCALATE when a narrow source-record defect remains open before execution.",
            "Cite exact doc_id values from the current case only.",
            "Do not invent source IDs.",
        ],
        "answer_contract": answer_contract(),
        "source_context": source_context,
    }
    return [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(prompt_obj, separators=(",", ":"), sort_keys=True)}], prompt_obj, scrubbed_fields


def load_freeze(freeze_root: Path) -> dict[str, Any]:
    lock = json.loads((freeze_root / "LOCK_MANIFEST.json").read_text())
    validation = json.loads((freeze_root / "LOCK_VALIDATION.json").read_text())
    if validation.get("validation_status") != "PASS":
        raise RuntimeError("freeze validation is not PASS")
    if validation.get("root_signature") != lock.get("root_signature"):
        raise RuntimeError("freeze validation root mismatch")
    for item in lock["locked_files"]:
        path = freeze_root / item["relative_path"]
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"freeze hash mismatch: {item['relative_path']}")
    return lock


def load_packets(freeze_root: Path, lock: dict[str, Any]) -> list[dict[str, Any]]:
    packets = []
    for record in lock["packet_records"]:
        payload_path = freeze_root / record["payload_ref"]
        payload = json.loads(payload_path.read_text())
        if sha256_file(payload_path) != record["payload_sha256"]:
            raise RuntimeError(f"payload file hash mismatch: {record['packet_id']}")
        packets.append({**record, "payload": payload})
    if len(packets) != 40:
        raise RuntimeError(f"expected 40 frozen packets, got {len(packets)}")
    return packets


def spec_for_packet(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "boundary": (packet["payload"].get("context") or {}).get("action_boundary"),
        "knew_terms": {packet["suffix"]: packet.get("knew_terms") or []},
    }


def parse_solo_text(text: str) -> tuple[bool, dict[str, Any] | None, str | None]:
    try:
        return True, RUNNER._json_from_text(text, allow_markdown_fence=True), None
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}"


def solo_label(parsed: dict[str, Any] | None, gate: dict[str, Any] | None, expected: str, parse_ok: bool, provider_ok: bool) -> str:
    if not provider_ok:
        return "PROVIDER_FAIL"
    if not parse_ok or not isinstance(parsed, dict):
        return "PARSE_FAIL"
    verdict = parsed.get("verification_verdict")
    if verdict != expected:
        return "WRONG_VERDICT"
    if gate and gate.get("passed"):
        return "KNEW"
    return "STRUCTURAL_OR_EVIDENCE_FAIL"


def build_call_plan(lock: dict[str, Any], packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plan = []
    for model_key in MODEL_KEYS:
        for packet in packets:
            seed = sha256_text(lock["root_signature"] + "::" + model_key + "::" + packet["packet_id"])
            plan.append({"sort_key": seed, "model_key": model_key, "packet": packet})
    return sorted(plan, key=lambda item: item["sort_key"])


def write_preflight(run_dir: Path, freeze_root: Path, lock: dict[str, Any], call_plan: list[dict[str, Any]]) -> dict[str, Any]:
    prompts_dir = run_dir / "prompts_preflight"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    audit_rows = []
    for index, item in enumerate(call_plan, 1):
        packet = item["packet"]
        case_ref = "CASE_" + sha256_text(lock["root_signature"] + "::" + str(index) + "::" + item["model_key"])[:12]
        messages, prompt_obj, scrubbed_fields = build_solo_messages(packet["payload"], case_ref)
        violations = prompt_leakage_violations(messages, prompt_obj, packet["packet_id"], packet["pair_id"])
        prompt_hash = sha256_text(canonical_json({"messages": messages, "prompt_object": prompt_obj}))
        prompt_ref = prompts_dir / f"{index:03d}_{item['model_key']}.json"
        prompt_ref.write_text(json.dumps({"messages": messages, "prompt_object": prompt_obj}, indent=2, sort_keys=True) + "\n")
        audit_rows.append(
            {
                "call_index": index,
                "model_key": item["model_key"],
                "provider": RUNNER.MODEL_CONFIGS[item["model_key"]]["provider"],
                "model": RUNNER.MODEL_CONFIGS[item["model_key"]]["model"],
                "packet_id_for_local_audit_only": packet["packet_id"],
                "pair_id_for_local_audit_only": packet["pair_id"],
                "prompt_ref": str(prompt_ref.relative_to(run_dir)),
                "prompt_hash": prompt_hash,
                "scrubbed_fields": scrubbed_fields,
                "leakage_violations": violations,
                "prompt_contains_expected_verdict": False,
                "prompt_contains_holo_or_gov_state": False,
            }
        )
    violation_count = sum(len(row["leakage_violations"]) for row in audit_rows)
    preflight = {
        "classification": "SOLO_ONE_SHOT_3MINI_PREFLIGHT",
        "freeze_root": str(freeze_root),
        "freeze_root_signature": lock["root_signature"],
        "expected_provider_calls": len(call_plan),
        "models": [
            {
                "model_key": key,
                "provider": RUNNER.MODEL_CONFIGS[key]["provider"],
                "model": RUNNER.MODEL_CONFIGS[key]["model"],
                "dna": RUNNER.MODEL_CONFIGS[key]["dna"],
            }
            for key in MODEL_KEYS
        ],
        "prompt_leakage_status": "PASS" if violation_count == 0 else "FAIL",
        "prompt_leakage_violation_count": violation_count,
        "scrub_policy": {
            "scrubbed_prompt_fields": ["action.business_ref"],
            "reason": "business_ref contains benchmark packet IDs with A/B suffixes; frozen payload files preserve original values for audit.",
            "source_document_contents_changed": False,
            "source_doc_ids_changed": False,
        },
        "audit_rows": audit_rows,
    }
    (run_dir / "SOLO_PREFLIGHT.json").write_text(json.dumps(preflight, indent=2, sort_keys=True) + "\n")
    if violation_count:
        raise RuntimeError(f"prompt leakage violations present: {violation_count}")
    return preflight


def run_live(freeze_root: Path) -> int:
    lock = load_freeze(freeze_root)
    packets = load_packets(freeze_root, lock)
    for key in MODEL_KEYS:
        env = RUNNER.MODEL_CONFIGS[key]["api_key_env"]
        if not os.getenv(env, "").strip():
            raise RuntimeError(f"{env} missing")
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    run_dir = RUN_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    call_plan = build_call_plan(lock, packets)
    preflight = write_preflight(run_dir, freeze_root, lock, call_plan)
    prompts_dir = run_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    trace_path = run_dir / "SOLO_ONE_SHOT_TRACE.jsonl"
    rows: list[dict[str, Any]] = []
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    with trace_path.open("w") as trace:
        for index, item in enumerate(call_plan, 1):
            packet = item["packet"]
            model_key = item["model_key"]
            config = RUNNER.MODEL_CONFIGS[model_key]
            case_ref = "CASE_" + sha256_text(lock["root_signature"] + "::" + str(index) + "::" + model_key)[:12]
            messages, prompt_obj, scrubbed_fields = build_solo_messages(packet["payload"], case_ref)
            violations = prompt_leakage_violations(messages, prompt_obj, packet["packet_id"], packet["pair_id"])
            if violations:
                raise RuntimeError(f"prompt leakage before call {index}: {violations}")
            prompt_ref = prompts_dir / f"{index:03d}_{model_key}.json"
            prompt_ref.write_text(json.dumps({"messages": messages, "prompt_object": prompt_obj}, indent=2, sort_keys=True) + "\n")
            row: dict[str, Any] = {
                "call_index": index,
                "lane": "SOLO_ONE_SHOT_3MINI_EXACT_FROZEN_PACKETS",
                "model_key": model_key,
                "provider": config["provider"],
                "model": config["model"],
                "dna": config["dna"],
                "packet_id": packet["packet_id"],
                "pair_id": packet["pair_id"],
                "suffix": packet["suffix"],
                "expected_verdict_for_local_audit_only": packet["expected_verdict_for_local_audit"],
                "freeze_root_signature": lock["root_signature"],
                "prompt_ref": str(prompt_ref.relative_to(run_dir)),
                "prompt_hash": sha256_text(canonical_json({"messages": messages, "prompt_object": prompt_obj})),
                "prompt_leakage_violations": [],
                "prompt_scrubbed_fields": scrubbed_fields,
                "holo_or_gov_context_in_prompt": False,
                "expected_verdict_in_prompt": False,
                "solo_normalization_applied": False,
            }
            response: dict[str, Any] = {}
            provider_ok = False
            parse_ok = False
            parsed = None
            gate = None
            try:
                response = RUNNER._call_model(config, messages, max_tokens=RUNNER.WORKER_MAX_TOKENS)
                provider_ok = True
                parse_ok, parsed, parse_error = parse_solo_text(response["text"])
                if parse_ok and isinstance(parsed, dict):
                    valid_ids = RUNNER._source_ids(packet["payload"])
                    gate = RUNNER._validate_worker(parsed, spec_for_packet(packet), packet["suffix"], valid_ids)
                else:
                    gate = {
                        "gate_name": "HOLOVERIFY_SOLO_ONE_SHOT_DETERMINISTIC_GATE",
                        "passed": False,
                        "failures": [parse_error or "parse_failed"],
                        "artifact_verdict": None,
                        "artifact_binding": None,
                    }
            except Exception as exc:
                parse_error = f"{type(exc).__name__}: {exc}"
                row["error"] = parse_error
            row.update(response)
            label = solo_label(parsed, gate, packet["expected_verdict_for_local_audit"], parse_ok, provider_ok)
            row.update(
                {
                    "provider_call_ok": provider_ok,
                    "parse_ok": parse_ok,
                    "parse_error": parse_error,
                    "parsed_json": parsed,
                    "local_verdict": parsed.get("verification_verdict") if isinstance(parsed, dict) else None,
                    "local_verdict_matches_packet_truth": (
                        parsed.get("verification_verdict") == packet["expected_verdict_for_local_audit"]
                        if isinstance(parsed, dict)
                        else False
                    ),
                    "gate_result": gate,
                    "admissible": bool(gate and gate.get("passed")),
                    "solo_label": label,
                    "holo_final_verdict": packet["holo_final_verdict"],
                    "holo_final_admissible": packet["holo_final_admissible"],
                    "holo_selection_reason": packet["holo_selection_reason"],
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
    summary = summarize(run_dir, lock, preflight, rows, totals, trace_path)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["classification"] == "SOLO_ONE_SHOT_3MINI_40_COMPLETE" else 1


def summarize(run_dir: Path, lock: dict[str, Any], preflight: dict[str, Any], rows: list[dict[str, Any]], totals: dict[str, int], trace_path: Path) -> dict[str, Any]:
    by_model: dict[str, dict[str, Any]] = {}
    for key in MODEL_KEYS:
        config = RUNNER.MODEL_CONFIGS[key]
        model_label = f"{config['provider']}/{config['model']}"
        model_rows = [row for row in rows if row.get("model_key") == key]
        counts = Counter(row.get("solo_label") for row in model_rows)
        by_model[model_label] = {
            "calls": len(model_rows),
            "expected_calls": 40,
            "verdict_correct": sum(1 for row in model_rows if row.get("local_verdict_matches_packet_truth") is True),
            "admissible_knew": counts.get("KNEW", 0),
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
    packet_rows = defaultdict(list)
    for row in rows:
        packet_rows[row["packet_id"]].append(row)
    packet_results = []
    for record in lock["packet_records"]:
        model_rows = packet_rows.get(record["packet_id"], [])
        packet_results.append(
            {
                "packet_id": record["packet_id"],
                "pair_id": record["pair_id"],
                "suffix": record["suffix"],
                "expected_verdict_for_local_audit": record["expected_verdict_for_local_audit"],
                "holo_final_verdict": record["holo_final_verdict"],
                "holo_final_admissible": record["holo_final_admissible"],
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
                    for row in sorted(model_rows, key=lambda item: item["model_key"])
                ],
            }
        )
    provider_failures = [row for row in rows if row.get("provider_call_ok") is not True]
    leakage_violations = [row for row in rows if row.get("prompt_leakage_violations")]
    complete = len(rows) == 120 and not provider_failures
    summary = {
        "classification": "SOLO_ONE_SHOT_3MINI_40_COMPLETE" if complete else "SOLO_ONE_SHOT_3MINI_INCOMPLETE_OR_PROVIDER_FAILURE",
        "run_dir": str(run_dir),
        "freeze_root_signature": lock["root_signature"],
        "holo_run_source": lock["source_run_dir"],
        "holo_trace_hash": lock["holo_trace_hash"],
        "provider_calls": len(rows),
        "expected_provider_calls": 120,
        "judge_calls": 0,
        "gov_calls": 0,
        "holo_calls": 0,
        "provider_failures": [
            {
                "call_index": row.get("call_index"),
                "packet_id": row.get("packet_id"),
                "provider": row.get("provider"),
                "model": row.get("model"),
                "error": row.get("error") or row.get("parse_error"),
            }
            for row in provider_failures
        ],
        "totals": totals,
        "trace_hash": sha256_file(trace_path),
        "prompt_leakage_status": "PASS" if preflight["prompt_leakage_status"] == "PASS" and not leakage_violations else "FAIL",
        "prompt_leakage_violation_count": preflight["prompt_leakage_violation_count"] + sum(len(row["prompt_leakage_violations"]) for row in leakage_violations),
        "leakage_controls": {
            "prompt_contains_expected_verdict": False,
            "prompt_contains_holo_or_gov_state": False,
            "prompt_contains_packet_id_or_pair_id": False,
            "prompt_contains_target_or_guardrail_label": False,
            "scrubbed_business_ref": True,
            "source_document_contents_changed": False,
            "source_doc_ids_changed": False,
        },
        "holo_reference": {
            "classification": "HOLOVERIFY_20PAIR_3DNA_COMPLETE",
            "packet_count": 40,
            "final_admissible_packets": sum(1 for record in lock["packet_records"] if record["holo_final_admissible"]),
            "valid_pairs": 20,
            "provider_calls": lock["scope"]["holo_provider_calls"],
            "tokens": lock["holo_token_totals"],
        },
        "by_model": by_model,
        "packet_results": packet_results,
    }
    (run_dir / "solo_one_shot_results.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    write_analysis(run_dir, summary)
    write_run_lock(run_dir, summary)
    return summary


def write_analysis(run_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Solo One-Shot Against Frozen HoloVerify 20-Pair / 3-DNA Packets",
        "",
        f"Classification: `{summary['classification']}`",
        f"Freeze root signature: `{summary['freeze_root_signature']}`",
        f"Holo trace hash: `{summary['holo_trace_hash']}`",
        f"Prompt leakage status: `{summary['prompt_leakage_status']}`",
        f"Provider calls: `{summary['provider_calls']}` / `{summary['expected_provider_calls']}`",
        f"Tokens: `{summary['totals']['input_tokens']}` input / `{summary['totals']['output_tokens']}` output / `{summary['totals']['total_tokens']}` total",
        "",
        "## Leakage Controls",
        "",
        "| Control | Value |",
        "| --- | --- |",
    ]
    for key, value in summary["leakage_controls"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Model Results", "", "| Model | Calls | Verdict Correct | KNEW/Admissible | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"])
    for model, stats in summary["by_model"].items():
        lines.append(
            f"| `{model}` | {stats['calls']} | {stats['verdict_correct']} | {stats['admissible_knew']} | {stats['wrong_verdict']} | {stats['structural_or_evidence_fail']} | {stats['parse_fail']} | {stats['provider_fail']} |"
        )
    lines.extend(["", "## Holo Reference", ""])
    holo = summary["holo_reference"]
    lines.extend(
        [
            f"- Holo classification: `{holo['classification']}`",
            f"- Holo final admissible packets: `{holo['final_admissible_packets']}/{holo['packet_count']}`",
            f"- Holo valid pairs: `{holo['valid_pairs']}`",
            f"- Holo provider calls: `{holo['provider_calls']}`",
            f"- Holo tokens: `{holo['tokens']['input_tokens']}` input / `{holo['tokens']['output_tokens']}` output / `{holo['tokens']['total_tokens']}` total",
        ]
    )
    lines.extend(["", "## Packet Matrix", "", "| Packet | Expected | Holo | xAI | Gemini | MiniMax |", "| --- | --- | --- | --- | --- | --- |"])
    for packet in summary["packet_results"]:
        cells = {}
        for row in packet["solo_by_model"]:
            label = f"{row['verdict']}:{row['solo_label']}"
            key = "xAI" if row["provider"] == "xai" else "Gemini" if row["provider"] == "google" else "MiniMax"
            cells[key] = label
        lines.append(
            f"| `{packet['packet_id']}` | `{packet['expected_verdict_for_local_audit']}` | `{packet['holo_final_verdict']}` | `{cells.get('xAI')}` | `{cells.get('Gemini')}` | `{cells.get('MiniMax')}` |"
        )
    (run_dir / "solo_analysis.md").write_text("\n".join(lines) + "\n")


def locked_files(run_dir: Path) -> list[dict[str, Any]]:
    files = []
    for path in sorted(item for item in run_dir.rglob("*") if item.is_file()):
        if path.name in {"RUN_LOCK_MANIFEST.json", "RUN_LOCK_VALIDATION.json"}:
            continue
        files.append({"relative_path": str(path.relative_to(run_dir)), "sha256": sha256_file(path), "bytes": path.stat().st_size})
    return files


def write_run_lock(run_dir: Path, summary: dict[str, Any]) -> None:
    manifest_no_root = {
        "classification": "SOLO_ONE_SHOT_3MINI_AGAINST_FROZEN_HOLOVERIFY_HASH_LOCK",
        "status": "FROZEN_SOLO_BASELINE_COMPLETE" if summary["classification"] == "SOLO_ONE_SHOT_3MINI_40_COMPLETE" else "FROZEN_SOLO_BASELINE_INCOMPLETE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "freeze_root_signature": summary["freeze_root_signature"],
        "trace_hash": summary["trace_hash"],
        "prompt_leakage_status": summary["prompt_leakage_status"],
        "provider_calls": summary["provider_calls"],
        "expected_provider_calls": summary["expected_provider_calls"],
        "locked_files": locked_files(run_dir),
    }
    root_signature = sha256_text(canonical_json(manifest_no_root))
    lock = {**manifest_no_root, "root_signature": root_signature}
    (run_dir / "RUN_LOCK_MANIFEST.json").write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n")
    validation = validate_run_lock(run_dir)
    (run_dir / "RUN_LOCK_VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")


def validate_run_lock(run_dir: Path) -> dict[str, Any]:
    lock = json.loads((run_dir / "RUN_LOCK_MANIFEST.json").read_text())
    for item in lock["locked_files"]:
        path = run_dir / item["relative_path"]
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"run lock hash mismatch: {item['relative_path']}")
    lock_no_root = dict(lock)
    root = lock_no_root.pop("root_signature")
    recomputed = sha256_text(canonical_json(lock_no_root))
    if recomputed != root:
        raise RuntimeError(f"run lock root mismatch: {recomputed} != {root}")
    return {
        "validation_status": "PASS",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "root_signature": root,
        "locked_file_count": len(lock["locked_files"]),
    }


def preflight_only(freeze_root: Path) -> int:
    lock = load_freeze(freeze_root)
    packets = load_packets(freeze_root, lock)
    run_dir = RUN_ROOT / "preflight_latest"
    if run_dir.exists():
        raise RuntimeError(f"preflight dir already exists; remove or inspect it first: {run_dir}")
    run_dir.mkdir(parents=True)
    call_plan = build_call_plan(lock, packets)
    preflight = write_preflight(run_dir, freeze_root, lock, call_plan)
    print(json.dumps({"preflight": "ok", "run_dir": str(run_dir), "expected_provider_calls": len(call_plan), "prompt_leakage_status": preflight["prompt_leakage_status"]}, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-root", default=str(DEFAULT_FREEZE_ROOT))
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    args = parser.parse_args()
    freeze_root = Path(args.freeze_root)
    if args.preflight_only:
        return preflight_only(freeze_root)
    if args.run_live:
        return run_live(freeze_root)
    parser.error("Use --preflight-only or --run-live")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
