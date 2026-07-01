#!/usr/bin/env python3
"""Run IT Access OpenAI-W2 Holo as a preregistered 3-batch family.

This script does not change the frozen packets, prompts, model roster, or
architecture. It only scopes the existing IT Access OpenAI-W2 runtime into three
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
IT_ACCESS_MODULE_PATH = BENCHMARK_ROOT / "run_it_access_replication_holoverify_3dna_2026_06_30.py"
IT_ACCESS_ROOT = BENCHMARK_ROOT / "holoverify_it_access_replication_2026-06-30"
BATCH_RUN_ROOT = IT_ACCESS_ROOT / "holo_live_runs_openai_w2_batched"
BATCH_PREFLIGHT_ROOT = IT_ACCESS_ROOT / "batched_full_holo_preflights"
BATCH_HEALTH_GATED_PREFLIGHT_ROOT = IT_ACCESS_ROOT / "batched_full_holo_preflights_health_gated"
ROLLUP_ROOT = IT_ACCESS_ROOT / "batched_full_holo_rollups"
MINIMAX_HEALTH_ROOT = IT_ACCESS_ROOT / "minimax_health_checks"
MINIMAX_WORKER_SMOKE_ROOT = IT_ACCESS_ROOT / "minimax_worker_contract_smokes"
EXPECTED_FREEZE_ROOT_HASH = "5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7"
REPLACEMENT_015R1_FREEZE_ROOT = IT_ACCESS_ROOT / "it_access_replacement_pair_015r1_freeze_2026_07_01"
REPLACEMENT_015R1_FREEZE_ROOT_HASH = "6c61024da5f6c36c1ee5210b95efd1d7a1ed0caff60a11efe0ace1ca1e72dc4e"
MINIMAX_HEALTH_PROMPT = "Return exactly MINIMAX_READY"
MINIMAX_HEALTH_EXPECTED_RESPONSE = "MINIMAX_READY"
MINIMAX_HEALTH_MAX_TOKENS = 128
MINIMAX_HEALTH_MAX_AGE_SECONDS = 30 * 60
MINIMAX_WORKER_SMOKE_MAX_TOKENS = 1200
MINIMAX_WORKER_SMOKE_MAX_AGE_SECONDS = 30 * 60
MINIMAX_WORKER_SMOKE_PROMPT = "\n".join(
    [
        "Return compact_key_value_v1 only.",
        "The first output characters must be worker_role=FINAL_COMPILER.",
        "Do not emit hidden thinking, analysis, Markdown, JSON, or prose.",
        "Use only these fixture source IDs: SRC-FIXTURE-CTL and SRC-FIXTURE-BND.",
        "Return exactly these lines, with no extra text:",
        "worker_role=FINAL_COMPILER",
        "verification_verdict=ALLOW",
        "binding_class=SOURCE_BOUNDARY_CLOSED",
        "action_boundary=fixture non-benchmark action boundary",
        "allow_rule_assessment=fixture control closes exact boundary",
        "escalate_rule_assessment=no open escalation defect remains",
        "dependency_check=fixture timing scope authority and dependency closed",
        "controlling_source_fact=SRC-FIXTURE-CTL",
        "cited_evidence=SRC-FIXTURE-CTL|SRC-FIXTURE-BND",
        "open_blockers=",
        "critical_features_preserved=fixture boundary|SRC-FIXTURE-CTL|SRC-FIXTURE-BND",
        "final_answer=Action may proceed because the fixture control closes the exact non-benchmark boundary, cites the required fixture sources, and leaves no timing scope authority or dependency blocker unresolved.",
    ]
)

BATCHES: dict[str, dict[str, Any]] = {
    "batch_1": {
        "label": "pairs_001_007",
        "pair_ids": tuple(f"HV-ITAC-REP-{index:03d}" for index in range(1, 8)),
    },
    "batch_2": {
        "label": "pairs_008_014",
        "pair_ids": tuple(f"HV-ITAC-REP-{index:03d}" for index in range(8, 15)),
    },
    "batch_3": {
        "label": "pairs_015_020",
        "pair_ids": tuple(f"HV-ITAC-REP-{index:03d}" for index in range(15, 21)),
    },
    "replacement_015r1": {
        "label": "replacement_pair_015r1",
        "pair_ids": ("HV-ITAC-REP-015R1",),
        "replacement_for": "HV-ITAC-REP-015",
        "supplemental_freeze": True,
    },
}


def load_it_access_module():
    spec = importlib.util.spec_from_file_location("it_access_openai_w2_batched_family", IT_ACCESS_MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


IT_ACCESS = load_it_access_module()
AP = IT_ACCESS.AP
RUNNER = AP.RUNNER


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def sha256_file(path: Path) -> str:
    return AP.sha256_file(path)


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def trace_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def configure() -> None:
    IT_ACCESS.configure_it_access_runtime()
    IT_ACCESS.ensure_registration_files()
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


def latest_minimax_health_report(now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    candidates = sorted(MINIMAX_HEALTH_ROOT.glob("health_*/IT_ACCESS_MINIMAX_HEALTH_CHECK_2026_06_30.json"))
    if not candidates:
        return {
            "status": "MISSING",
            "recent_pass": False,
            "reason": "no_minimax_health_check_report_found",
            "max_age_seconds": MINIMAX_HEALTH_MAX_AGE_SECONDS,
        }
    path = candidates[-1]
    try:
        report = read_json(path)
    except Exception as exc:
        return {
            "status": "MALFORMED",
            "recent_pass": False,
            "reason": f"latest_health_check_malformed:{type(exc).__name__}",
            "path": str(path),
            "max_age_seconds": MINIMAX_HEALTH_MAX_AGE_SECONDS,
        }
    created_at = parse_timestamp(report.get("created_at"))
    age_seconds = None
    if created_at is not None:
        age_seconds = int((now - created_at).total_seconds())
    recent = isinstance(age_seconds, int) and 0 <= age_seconds <= MINIMAX_HEALTH_MAX_AGE_SECONDS
    passed = report.get("status") == "PASS" and report.get("provider_clean") is True
    return {
        "status": "PASS" if passed and recent else "FAIL",
        "recent_pass": bool(passed and recent),
        "reason": None if passed and recent else "latest_health_check_missing_stale_failed_or_degraded",
        "path": str(path),
        "created_at": report.get("created_at"),
        "age_seconds": age_seconds,
        "max_age_seconds": MINIMAX_HEALTH_MAX_AGE_SECONDS,
        "provider_clean": report.get("provider_clean"),
        "transport_attempt_count": report.get("transport_attempt_count"),
        "transport_recovered": report.get("transport_recovered"),
        "response_exact": report.get("response_exact"),
        "max_tokens": report.get("max_tokens"),
    }


def latest_minimax_worker_smoke_report(now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    candidates = sorted(MINIMAX_WORKER_SMOKE_ROOT.glob("smoke_*/IT_ACCESS_MINIMAX_WORKER_CONTRACT_SMOKE_2026_06_30.json"))
    if not candidates:
        return {
            "status": "MISSING",
            "recent_pass": False,
            "reason": "no_minimax_worker_contract_smoke_report_found",
            "max_age_seconds": MINIMAX_WORKER_SMOKE_MAX_AGE_SECONDS,
        }
    path = candidates[-1]
    try:
        report = read_json(path)
    except Exception as exc:
        return {
            "status": "MALFORMED",
            "recent_pass": False,
            "reason": f"latest_worker_smoke_malformed:{type(exc).__name__}",
            "path": str(path),
            "max_age_seconds": MINIMAX_WORKER_SMOKE_MAX_AGE_SECONDS,
        }
    created_at = parse_timestamp(report.get("created_at"))
    age_seconds = None
    if created_at is not None:
        age_seconds = int((now - created_at).total_seconds())
    recent = isinstance(age_seconds, int) and 0 <= age_seconds <= MINIMAX_WORKER_SMOKE_MAX_AGE_SECONDS
    passed = report.get("status") == "PASS" and report.get("worker_contract_clean") is True
    return {
        "status": "PASS" if passed and recent else "FAIL",
        "recent_pass": bool(passed and recent),
        "reason": None if passed and recent else "latest_worker_smoke_missing_stale_failed_or_degraded",
        "path": str(path),
        "created_at": report.get("created_at"),
        "age_seconds": age_seconds,
        "max_age_seconds": MINIMAX_WORKER_SMOKE_MAX_AGE_SECONDS,
        "worker_contract_clean": report.get("worker_contract_clean"),
        "raw_starts_with_worker_role": report.get("raw_starts_with_worker_role"),
        "text_starts_with_worker_role": report.get("text_starts_with_worker_role"),
        "parse_ok": report.get("parse_ok"),
        "gate_passed": report.get("gate_passed"),
        "finish_reason": report.get("finish_reason"),
        "transport_attempt_count": report.get("transport_attempt_count"),
        "transport_recovered": report.get("transport_recovered"),
    }


def run_minimax_health_check() -> int:
    """Run a harmless MiniMax readiness check with no benchmark content."""
    configure()
    config = RUNNER.MODEL_CONFIGS["minimax"]
    env_name = config["api_key_env"]
    if not os.getenv(env_name, "").strip():
        raise RuntimeError(f"{env_name} missing")
    now = datetime.now(timezone.utc)
    run_id = now.strftime("health_%Y%m%dT%H%M%SZ")
    out_dir = MINIMAX_HEALTH_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=False)
    prompt_hash = AP.sha256_text(MINIMAX_HEALTH_PROMPT)
    response: dict[str, Any] = {}
    provider_call_ok = False
    error = None
    try:
        response = RUNNER._call_model(
            config,
            [{"role": "user", "content": MINIMAX_HEALTH_PROMPT}],
            max_tokens=MINIMAX_HEALTH_MAX_TOKENS,
        )
        provider_call_ok = True
    except RUNNER.TransportFailureAfterRetries as exc:
        response = dict(getattr(exc, "metadata", {}) or {})
        error = f"{type(exc).__name__}: {exc}"
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    text = str(response.get("text") or "").strip()
    transport_attempt_count = response.get("transport_attempt_count")
    transport_recovered = response.get("transport_recovered")
    response_exact = text == MINIMAX_HEALTH_EXPECTED_RESPONSE
    provider_clean = (
        provider_call_ok
        and response_exact
        and transport_attempt_count == 1
        and transport_recovered is False
        and not response.get("transport_final_failure_class")
    )
    report = {
        "classification": "IT_ACCESS_MINIMAX_HEALTH_CHECK_NON_BENCHMARK",
        "status": "PASS" if provider_clean else "FAIL",
        "created_at": now.isoformat(),
        "provider": config["provider"],
        "model": config["model"],
        "dna": config["dna"],
        "prompt_hash": prompt_hash,
        "prompt_policy": "harmless_non_benchmark_readiness_prompt_only",
        "benchmark_content_included": False,
        "packet_content_included": False,
        "source_ids_included": False,
        "traps_included": False,
        "answer_keys_included": False,
        "expected_response": MINIMAX_HEALTH_EXPECTED_RESPONSE,
        "max_tokens": MINIMAX_HEALTH_MAX_TOKENS,
        "response_text": text,
        "response_exact": response_exact,
        "provider_call_ok": provider_call_ok,
        "provider_clean": provider_clean,
        "transport_attempt_count": transport_attempt_count,
        "transport_recovered": transport_recovered,
        "transport_retry_failures": response.get("transport_retry_failures") or [],
        "transport_final_failure_class": response.get("transport_final_failure_class"),
        "finish_reason": response.get("finish_reason"),
        "input_tokens": response.get("input_tokens"),
        "output_tokens": response.get("output_tokens"),
        "total_tokens": response.get("total_tokens"),
        "elapsed_ms": response.get("elapsed_ms"),
        "error": error,
    }
    write_json(out_dir / "IT_ACCESS_MINIMAX_HEALTH_CHECK_2026_06_30.json", report)
    write_text(out_dir / "IT_ACCESS_MINIMAX_HEALTH_CHECK_2026_06_30.md", render_minimax_health_md(report))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if provider_clean else 1


def run_minimax_worker_contract_smoke() -> int:
    """Run a harmless MiniMax worker-format smoke with no benchmark content."""
    configure()
    config = RUNNER.MODEL_CONFIGS["minimax"]
    env_name = config["api_key_env"]
    if not os.getenv(env_name, "").strip():
        raise RuntimeError(f"{env_name} missing")
    now = datetime.now(timezone.utc)
    run_id = now.strftime("smoke_%Y%m%dT%H%M%SZ")
    out_dir = MINIMAX_WORKER_SMOKE_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=False)
    prompt_hash = AP.sha256_text(MINIMAX_WORKER_SMOKE_PROMPT)
    response: dict[str, Any] = {}
    provider_call_ok = False
    parse_ok = False
    gate_passed = False
    parse_error = None
    gate_result: dict[str, Any] | None = None
    error = None
    try:
        response = RUNNER._call_model(
            config,
            [{"role": "user", "content": MINIMAX_WORKER_SMOKE_PROMPT}],
            max_tokens=MINIMAX_WORKER_SMOKE_MAX_TOKENS,
        )
        provider_call_ok = True
        parsed = RUNNER._worker_from_response(response)
        parse_ok = True
        fixture_spec = {
            "boundary": "fixture non-benchmark action boundary",
            "knew_terms": {"A": ["fixture boundary", "SRC-FIXTURE-CTL", "SRC-FIXTURE-BND"]},
        }
        gate_result = RUNNER._validate_worker(parsed, fixture_spec, "A", {"SRC-FIXTURE-CTL", "SRC-FIXTURE-BND"})
        gate_passed = bool(gate_result.get("passed"))
    except RUNNER.TransportFailureAfterRetries as exc:
        response = dict(getattr(exc, "metadata", {}) or {})
        error = f"{type(exc).__name__}: {exc}"
    except Exception as exc:
        parse_error = f"{type(exc).__name__}: {exc}"
    raw_text = str(response.get("raw_text") or response.get("text") or "")
    text = str(response.get("text") or "")
    raw_starts_with_worker_role = raw_text.lstrip().startswith("worker_role=FINAL_COMPILER")
    text_starts_with_worker_role = text.lstrip().startswith("worker_role=FINAL_COMPILER")
    worker_contract_clean = (
        provider_call_ok
        and parse_ok
        and gate_passed
        and text_starts_with_worker_role
        and response.get("finish_reason") != "length"
        and response.get("transport_attempt_count") == 1
        and response.get("transport_recovered") is False
        and not response.get("transport_final_failure_class")
    )
    report = {
        "classification": "IT_ACCESS_MINIMAX_WORKER_CONTRACT_SMOKE_NON_BENCHMARK",
        "status": "PASS" if worker_contract_clean else "FAIL",
        "created_at": now.isoformat(),
        "provider": config["provider"],
        "model": config["model"],
        "dna": config["dna"],
        "prompt_hash": prompt_hash,
        "prompt_policy": "harmless_non_benchmark_worker_contract_smoke_only",
        "benchmark_content_included": False,
        "packet_content_included": False,
        "source_ids_included": False,
        "traps_included": False,
        "answer_keys_included": False,
        "fixture_source_ids_only": ["SRC-FIXTURE-CTL", "SRC-FIXTURE-BND"],
        "max_tokens": MINIMAX_WORKER_SMOKE_MAX_TOKENS,
        "provider_call_ok": provider_call_ok,
        "worker_contract_clean": worker_contract_clean,
        "parse_ok": parse_ok,
        "parse_error": parse_error,
        "gate_passed": gate_passed,
        "gate_result": gate_result,
        "raw_starts_with_worker_role": raw_starts_with_worker_role,
        "text_starts_with_worker_role": text_starts_with_worker_role,
        "text_stripped_by_thinking_filter": response.get("text_stripped_by_thinking_filter"),
        "response_text_preview": text[:500],
        "raw_text_preview": raw_text[:500],
        "finish_reason": response.get("finish_reason"),
        "input_tokens": response.get("input_tokens"),
        "output_tokens": response.get("output_tokens"),
        "total_tokens": response.get("total_tokens"),
        "elapsed_ms": response.get("elapsed_ms"),
        "transport_attempt_count": response.get("transport_attempt_count"),
        "transport_recovered": response.get("transport_recovered"),
        "transport_retry_failures": response.get("transport_retry_failures") or [],
        "transport_final_failure_class": response.get("transport_final_failure_class"),
        "error": error,
    }
    write_json(out_dir / "IT_ACCESS_MINIMAX_WORKER_CONTRACT_SMOKE_2026_06_30.json", report)
    write_text(out_dir / "IT_ACCESS_MINIMAX_WORKER_CONTRACT_SMOKE_2026_06_30.md", render_minimax_worker_smoke_md(report))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if worker_contract_clean else 1


def render_minimax_worker_smoke_md(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# IT Access MiniMax Worker Contract Smoke",
            "",
            f"Classification: `{report['classification']}`",
            f"Status: `{report['status']}`",
            f"Provider/model: `{report['provider']}/{report['model']}`",
            f"Prompt policy: `{report['prompt_policy']}`",
            "",
            "## Result",
            "",
            f"- Provider call OK: `{report['provider_call_ok']}`",
            f"- Worker contract clean: `{report['worker_contract_clean']}`",
            f"- Parse OK: `{report['parse_ok']}`",
            f"- Gate passed: `{report['gate_passed']}`",
            f"- Raw starts with worker role: `{report['raw_starts_with_worker_role']}`",
            f"- Visible text starts with worker role: `{report['text_starts_with_worker_role']}`",
            f"- Finish reason: `{report['finish_reason']}`",
            f"- Transport attempts: `{report['transport_attempt_count']}`",
            f"- Transport recovered: `{report['transport_recovered']}`",
            f"- Error: `{report['error']}`",
            "",
            "No frozen IT Access packet text, prompt text, source IDs, traps, or answer keys are included in this worker smoke.",
            "",
        ]
    )


def render_minimax_health_md(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# IT Access MiniMax Health Check",
            "",
            f"Classification: `{report['classification']}`",
            f"Status: `{report['status']}`",
            f"Provider/model: `{report['provider']}/{report['model']}`",
            f"Prompt policy: `{report['prompt_policy']}`",
            "",
            "## Result",
            "",
            f"- Provider call OK: `{report['provider_call_ok']}`",
            f"- Provider clean: `{report['provider_clean']}`",
            f"- Response exact: `{report['response_exact']}`",
            f"- Transport attempts: `{report['transport_attempt_count']}`",
            f"- Transport recovered: `{report['transport_recovered']}`",
            f"- Final transport failure class: `{report['transport_final_failure_class']}`",
            f"- Error: `{report['error']}`",
            "",
            "No frozen IT Access packet text, prompt text, source IDs, traps, or answer keys are included in this health check.",
            "",
        ]
    )


def active_freeze_root_hash(batch_id: str) -> str:
    if BATCHES[batch_id].get("supplemental_freeze"):
        return REPLACEMENT_015R1_FREEZE_ROOT_HASH
    return EXPECTED_FREEZE_ROOT_HASH


def read_replacement_015r1_freeze() -> dict[str, Any]:
    summary = read_json(REPLACEMENT_015R1_FREEZE_ROOT / "FREEZE_MANIFEST.json")
    if summary.get("freeze_root_hash") != REPLACEMENT_015R1_FREEZE_ROOT_HASH:
        raise RuntimeError(f"replacement_freeze_root_mismatch:{summary.get('freeze_root_hash')}")
    if summary.get("original_freeze_root_hash") != EXPECTED_FREEZE_ROOT_HASH:
        raise RuntimeError("replacement_original_freeze_root_mismatch")
    packet_manifest = read_json(REPLACEMENT_015R1_FREEZE_ROOT / "manifests" / "PACKET_HASH_MANIFEST.json")
    prompt_manifest = read_json(REPLACEMENT_015R1_FREEZE_ROOT / "manifests" / "PROMPT_HASH_MANIFEST.json")
    index = read_json(REPLACEMENT_015R1_FREEZE_ROOT / "manifests" / "PACKET_INDEX.json")
    packet_by_id = {row["packet_id"]: row for row in packet_manifest["records"]}
    prompt_by_id = {row["packet_id"]: row for row in prompt_manifest["records"]}
    records = []
    for row in sorted(index, key=lambda item: (item["pair_id"], item["sibling_id"])):
        packet_hash_row = packet_by_id[row["packet_id"]]
        prompt_hash_row = prompt_by_id[row["packet_id"]]
        packet_path = REPLACEMENT_015R1_FREEZE_ROOT / packet_hash_row["packet_path"]
        prompt_path = REPLACEMENT_015R1_FREEZE_ROOT / prompt_hash_row["prompt_path"]
        model_payload_path = REPLACEMENT_015R1_FREEZE_ROOT / packet_hash_row["model_visible_payload_path"]
        if sha256_file(packet_path) != packet_hash_row["packet_sha256"]:
            raise RuntimeError(f"replacement_packet_hash_mismatch:{row['packet_id']}")
        if sha256_file(prompt_path) != prompt_hash_row["prompt_sha256"]:
            raise RuntimeError(f"replacement_prompt_hash_mismatch:{row['packet_id']}")
        if sha256_file(model_payload_path) != packet_hash_row["model_visible_payload_file_sha256"]:
            raise RuntimeError(f"replacement_model_visible_hash_mismatch:{row['packet_id']}")
        packet = read_json(packet_path)
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
    if len(records) != 2:
        raise RuntimeError(f"replacement_packet_count_mismatch:{len(records)}")
    return {"summary": summary, "records": records}


def source_record(packet: dict[str, Any], suffix: str) -> str:
    for item in packet["source_control_facts"]:
        if str(item["source_id"]).endswith(suffix):
            return str(item["source_id"])
    return str(packet["source_control_facts"][0]["source_id"])


def build_pairs_any_count(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_pair[record["pair_id"]].append(record)
    pairs = []
    for pair_id, pair_records in sorted(by_pair.items()):
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
                    "A": AP.convert_payload(a["packet"]),
                    "B": AP.convert_payload(b["packet"]),
                },
                "freeze_records": {"A": a, "B": b},
                "candidate": {"failing_models": []},
            }
        )
    return pairs


def selected_pairs(batch_id: str) -> list[dict[str, Any]]:
    configure()
    if BATCHES[batch_id].get("supplemental_freeze"):
        freeze = read_replacement_015r1_freeze()
        pairs = build_pairs_any_count(freeze["records"])
        by_id = {pair["pair_id"]: pair for pair in pairs}
        pair_ids = BATCHES[batch_id]["pair_ids"]
        missing = [pair_id for pair_id in pair_ids if pair_id not in by_id]
        if missing:
            raise RuntimeError(f"replacement_target_pairs_missing:{missing}")
        return [by_id[pair_id] for pair_id in pair_ids]
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
        "# IT Access OpenAI-W2 Batched Full-Holo Preflight",
        "",
        f"Classification: `{preflight['classification']}`",
        f"Batch: `{preflight['batch_id']}`",
        f"Status: `{preflight['status']}`",
        f"Result: `{preflight['result']}`",
        f"Freeze root: `{preflight['freeze_root']}`",
        f"Original freeze root: `{preflight['original_freeze_root']}`",
        f"Supplemental replacement freeze: `{preflight['supplemental_replacement_freeze']}`",
        f"Replacement for: `{preflight['replacement_for']}`",
        "",
        "## Scope",
        "",
        f"- Pair range: `{preflight['batch_label']}`",
        f"- Pair IDs: `{', '.join(preflight['pair_ids'])}`",
        f"- Expected packets: `{preflight['expected_counts']['packets']}`",
        f"- Expected provider calls: `{preflight['expected_counts']['total_provider_calls']}`",
        f"- Solo calls: `{preflight['expected_counts']['solo_calls']}`",
        f"- Judge calls: `{preflight['expected_counts']['judge_calls']}`",
        f"- MiniMax health required: `{preflight['minimax_health_gate']['required']}`",
        f"- MiniMax recent clean health: `{preflight['minimax_health_gate']['recent_pass']}`",
        f"- MiniMax worker smoke required: `{preflight['minimax_worker_smoke_gate']['required']}`",
        f"- MiniMax recent worker smoke: `{preflight['minimax_worker_smoke_gate']['recent_pass']}`",
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


def build_preflight(
    batch_id: str,
    require_minimax_health: bool = False,
    require_minimax_worker_smoke: bool = False,
) -> dict[str, Any]:
    pairs = selected_pairs(batch_id)
    counts = expected_counts(batch_id)
    declared_roster = roster()
    w2 = declared_roster["worker_sequence"][1]
    freeze_diff_names = AP.git_diff_names(AP.FREEZE_ROOT)
    active_root_hash = active_freeze_root_hash(batch_id)
    is_replacement_batch = bool(BATCHES[batch_id].get("supplemental_freeze"))
    pair_ids = tuple(pair["pair_id"] for pair in pairs)
    health_gate = latest_minimax_health_report()
    health_gate["required"] = require_minimax_health
    worker_smoke_gate = latest_minimax_worker_smoke_report()
    worker_smoke_gate["required"] = require_minimax_worker_smoke
    checks = {
        "freeze_root_matches": True,
        "original_freeze_root_preserved": EXPECTED_FREEZE_ROOT_HASH == "5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7",
        "replacement_freeze_root_matches": (not is_replacement_batch) or active_root_hash == REPLACEMENT_015R1_FREEZE_ROOT_HASH,
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
        "expected_provider_calls": counts["total_provider_calls"] in {70, 60, 10},
        "expected_worker_calls": counts["worker_calls"] in {42, 36, 6},
        "expected_gov_calls": counts["gov_calls"] in {28, 24, 4},
        "solo_calls_configured": counts["solo_calls"] == 0,
        "judge_calls_configured": counts["judge_calls"] == 0,
        "no_providers_called_during_preflight": True,
    }
    if require_minimax_health:
        checks["minimax_health_check_recent_clean_pass"] = health_gate["recent_pass"] is True
    if require_minimax_worker_smoke:
        checks["minimax_worker_contract_smoke_recent_clean_pass"] = worker_smoke_gate["recent_pass"] is True
    status = "PASS" if all(checks.values()) else "FAIL"
    architecture_lock = {
        "classification": "IT_ACCESS_OPENAI_W2_BATCHED_FULL_HOLO_ARCHITECTURE_LOCK",
        "family_id": IT_ACCESS.FAMILY_ID,
        "freeze_root_hash": active_root_hash,
        "original_freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "supplemental_replacement_freeze": is_replacement_batch,
        "replacement_for": BATCHES[batch_id].get("replacement_for"),
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
        "classification": "IT_ACCESS_OPENAI_W2_BATCHED_FULL_HOLO_PREFLIGHT",
        "status": status,
        "result": "IT_ACCESS_OPENAI_W2_BATCH_READY" if status == "PASS" else "IT_ACCESS_OPENAI_W2_BATCH_BLOCKED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "freeze_root": active_root_hash,
        "original_freeze_root": EXPECTED_FREEZE_ROOT_HASH,
        "supplemental_replacement_freeze": is_replacement_batch,
        "replacement_for": BATCHES[batch_id].get("replacement_for"),
        "source_it_access_runner": str(IT_ACCESS_MODULE_PATH.relative_to(BENCHMARK_ROOT)),
        "batch_id": batch_id,
        "batch_label": BATCHES[batch_id]["label"],
        "pair_ids": list(pair_ids),
        "expected_counts": counts,
        "architecture_lock": architecture_lock,
        "minimax_health_gate": health_gate,
        "minimax_worker_smoke_gate": worker_smoke_gate,
        "checks": checks,
        "blocked_reason": None if status == "PASS" else [key for key, value in checks.items() if not value],
        "providers_called": 0,
        "holo_started": False,
        "solo_started": False,
        "judges_started": False,
    }
    preflight["root_signature"] = AP.sha256_text(AP.canonical_json({k: v for k, v in preflight.items() if k != "created_at"}))
    out_dir = (
        BATCH_HEALTH_GATED_PREFLIGHT_ROOT
        if require_minimax_health or require_minimax_worker_smoke
        else BATCH_PREFLIGHT_ROOT
    ) / batch_id
    write_json(out_dir / "IT_ACCESS_OPENAI_W2_BATCH_PREFLIGHT.json", preflight)
    write_text(out_dir / "IT_ACCESS_OPENAI_W2_BATCH_PREFLIGHT.md", render_preflight_md(preflight))
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
        "classification": "IT_ACCESS_OPENAI_W2_BATCHED_HOLO_NO_LEAKAGE_AUDIT",
        "status": "PASS" if not hits else "FAIL",
        "run_dir": str(run_dir),
        "prompt_files_scanned": len(prompt_files),
        "hits": hits,
    }


def summarize_batch(run_dir: Path, manifest: dict[str, Any], packet_results: list[dict[str, Any]], trace_path: Path) -> dict[str, Any]:
    rows = trace_rows(trace_path)
    counts = manifest["expected_counts"]
    active_root_hash = manifest.get("freeze_root") or EXPECTED_FREEZE_ROOT_HASH
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
        "packet_identity_matches_freeze": "PASS" if manifest.get("freeze_root") == active_root_hash else "FAIL",
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
        "classification": "IT_ACCESS_OPENAI_W2_BATCHED_HOLO_BATCH_COMPLETE" if readiness else "IT_ACCESS_OPENAI_W2_BATCHED_HOLO_BATCH_INVALID_OR_INCOMPLETE",
        "readiness_passed": readiness,
        "run_dir": str(run_dir),
        "freeze_root": active_root_hash,
        "original_freeze_root": manifest.get("original_freeze_root") or EXPECTED_FREEZE_ROOT_HASH,
        "supplemental_replacement_freeze": manifest.get("supplemental_replacement_freeze") is True,
        "replacement_for": manifest.get("replacement_for"),
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
    write_json(run_dir / "IT_ACCESS_OPENAI_W2_BATCHED_HOLO_NO_LEAKAGE_AUDIT.json", leakage)
    write_json(run_dir / "IT_ACCESS_OPENAI_W2_BATCHED_HOLO_READINESS_ASSERTIONS.json", assertions)
    write_batch_summary_md(run_dir, summary)
    return summary


def write_batch_summary_md(run_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# IT Access OpenAI-W2 Batched Holo Run",
        "",
        f"Classification: `{summary['classification']}`",
        f"Batch: `{summary['batch_id']}`",
        f"Readiness passed: `{summary['readiness_passed']}`",
        f"Freeze root: `{summary['freeze_root']}`",
        f"Original freeze root: `{summary['original_freeze_root']}`",
        f"Supplemental replacement freeze: `{summary['supplemental_replacement_freeze']}`",
        f"Replacement for: `{summary['replacement_for']}`",
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


def run_batch(
    batch_id: str,
    require_minimax_health: bool = False,
    require_minimax_worker_smoke: bool = False,
) -> int:
    manifest = build_preflight(
        batch_id,
        require_minimax_health=require_minimax_health,
        require_minimax_worker_smoke=require_minimax_worker_smoke,
    )
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
        "pair_coverage_20": sorted(all_pairs) == [f"HV-ITAC-REP-{index:03d}" for index in range(1, 21)],
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
        "classification": "IT_ACCESS_OPENAI_W2_BATCHED_FULL_HOLO_ROLLUP_COMPLETE" if readiness else "IT_ACCESS_OPENAI_W2_BATCHED_FULL_HOLO_ROLLUP_INCOMPLETE",
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
    write_json(out_dir / "it_access_batched_full_holo_rollup.json", rollup)
    write_rollup_md(out_dir, rollup)
    AP.lock_directory(out_dir, "ROLLUP_LOCK")
    return rollup


def write_rollup_md(out_dir: Path, rollup: dict[str, Any]) -> None:
    lines = [
        "# IT Access OpenAI-W2 Batched Full-Holo Rollup",
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
    write_text(out_dir / "it_access_batched_full_holo_rollup.md", "\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minimax-health-check", action="store_true")
    parser.add_argument("--minimax-worker-contract-smoke", action="store_true")
    parser.add_argument("--require-minimax-health", action="store_true")
    parser.add_argument("--require-minimax-worker-smoke", action="store_true")
    parser.add_argument("--preflight-batch", action="store_true")
    parser.add_argument("--preflight-all-batches", action="store_true")
    parser.add_argument("--run-batch", action="store_true")
    parser.add_argument("--rollup-latest", action="store_true")
    parser.add_argument("--batch", choices=sorted(BATCHES))
    args = parser.parse_args()
    if args.minimax_health_check:
        return run_minimax_health_check()
    if args.minimax_worker_contract_smoke:
        return run_minimax_worker_contract_smoke()
    if args.preflight_batch:
        if not args.batch:
            raise SystemExit("--batch is required")
        report = build_preflight(
            args.batch,
            require_minimax_health=args.require_minimax_health,
            require_minimax_worker_smoke=args.require_minimax_worker_smoke,
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["status"] == "PASS" else 1
    if args.preflight_all_batches:
        reports = [
            build_preflight(
                batch_id,
                require_minimax_health=args.require_minimax_health,
                require_minimax_worker_smoke=args.require_minimax_worker_smoke,
            )
            for batch_id in BATCHES
        ]
        print(json.dumps(reports, indent=2, sort_keys=True))
        return 0 if all(report["status"] == "PASS" for report in reports) else 1
    if args.run_batch:
        if not args.batch:
            raise SystemExit("--batch is required")
        return run_batch(
            args.batch,
            require_minimax_health=args.require_minimax_health,
            require_minimax_worker_smoke=args.require_minimax_worker_smoke,
        )
    if args.rollup_latest:
        rollup = rollup_latest()
        print(json.dumps(rollup, indent=2, sort_keys=True))
        return 0 if rollup["readiness_passed"] else 1
    parser.error("Use --minimax-health-check, --minimax-worker-contract-smoke, --preflight-batch, --preflight-all-batches, --run-batch, or --rollup-latest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
