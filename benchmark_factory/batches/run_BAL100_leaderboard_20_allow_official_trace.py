from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from benchmark_factory.batches import run_BAL100_BATCH_001_five_mini_scout as provider_core
from benchmark_factory.batches.build_BAL100_leaderboard_20_allow_official_trace_preflight import (
    APPROVAL_ENV,
    APPROVAL_VALUE,
    CODEX_APPROVAL_ENV,
    CODEX_APPROVAL_VALUE,
    DEFAULT_OUT_DIR,
    RUN_ID,
    RUN_TYPE,
    SEED,
    _active_prompt_card,
    _gov_template_card,
    _load_packets,
    _roster,
    _safe_model_name,
    _transport_provider,
    build_preflight,
)
from holo_builder.frozen_4dna_runner import FORBIDDEN_MODEL_VISIBLE_KEYS


CO_ENV_MARKERS = (
    "CODEX_SANDBOX",
    "CODEX_THREAD_ID",
    "CODEX_CI",
    "CODEX_INTERNAL_ORIGINATOR_OVERRIDE",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        return
    load_dotenv()


def _git_head() -> str:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
    except Exception:
        return ""
    return result.stdout.strip()


def _in_codex_environment() -> bool:
    return any(os.getenv(marker) for marker in CO_ENV_MARKERS)


def _transport_model(roster_model: dict[str, str]) -> dict[str, str]:
    transport_provider = _transport_provider(roster_model["provider"])
    for model in provider_core.MODELS:
        if model["provider"] == transport_provider and model["model"] == roster_model["model"]:
            return dict(model)
    raise SystemExit(f"No transport model for roster model {roster_model}")


def _require_execution_approval(args: argparse.Namespace) -> str:
    _load_dotenv_if_available()
    if args.operator != "Taylor":
        raise SystemExit("--operator Taylor is required.")
    if not args.yes_send_frozen_payloads_to_providers:
        raise SystemExit("--yes-send-frozen-payloads-to-providers is required.")

    if _in_codex_environment():
        if not args.allow_codex_provider_calls:
            raise SystemExit("--allow-codex-provider-calls is required for Codex/Co provider execution.")
        if os.getenv(APPROVAL_ENV) != APPROVAL_VALUE:
            raise SystemExit(f"{APPROVAL_ENV}={APPROVAL_VALUE} is required.")
        if os.getenv(CODEX_APPROVAL_ENV) != CODEX_APPROVAL_VALUE:
            raise SystemExit(f"{CODEX_APPROVAL_ENV}={CODEX_APPROVAL_VALUE} is required.")
        execution_mode = "codex_approved"
    else:
        if not args.i_am_taylor_local:
            raise SystemExit("--i-am-taylor-local is required for Taylor-local execution.")
        if os.getenv(APPROVAL_ENV) != APPROVAL_VALUE:
            raise SystemExit(f"{APPROVAL_ENV}={APPROVAL_VALUE} is required.")
        execution_mode = "taylor_local"

    required_models = []
    for packet in _load_packets():
        roster = _roster(packet["session_id"])
        required_models.extend(roster["active_non_gov"])
        required_models.append(roster["holo_gov"])
    missing = sorted(
        {
            _transport_model(model)["api_key_env"]
            for model in required_models
            if not os.getenv(_transport_model(model)["api_key_env"])
        }
    )
    if missing:
        raise SystemExit("Missing API key environment variables: " + ", ".join(missing))
    return execution_mode


def _extract_json_object(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    candidates = [stripped]
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL)
    if fenced:
        candidates.insert(0, fenced.group(1))
    braced = re.search(r"(\{.*\})", stripped, flags=re.DOTALL)
    if braced:
        candidates.append(braced.group(1))
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except Exception:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _normalize_verdict(value: Any) -> str:
    text = str(value or "").strip().upper()
    if text in {"ALLOW", "APPROVE", "APPROVED", "YES", "Y"}:
        return "ALLOW"
    if text in {"ESCALATE", "BLOCK", "BLOCKED", "NO", "N"}:
        return "ESCALATE"
    if "ESCALAT" in text or "SHOULD NOT" in text or "NOT PROCEED" in text:
        return "ESCALATE"
    if "ALLOW" in text or "MAY PROCEED" in text or "CAN PROCEED" in text:
        return "ALLOW"
    return "UNCLEAR"


def _parse_active_response(raw_text: str) -> dict[str, Any]:
    parsed = _extract_json_object(raw_text)
    if not parsed:
        return {"parse_ok": False, "verdict": "ERROR", "parse_error": "No JSON object found."}
    verdict = _normalize_verdict(parsed.get("verdict"))
    if verdict not in {"ALLOW", "ESCALATE"}:
        return {
            "parse_ok": False,
            "verdict": "ERROR",
            "parse_error": f"Parsed verdict was not ALLOW/ESCALATE: {parsed.get('verdict')!r}",
            "parsed_json": parsed,
        }
    return {
        "parse_ok": True,
        "verdict": verdict,
        "material_blocker": parsed.get("material_blocker"),
        "cited_evidence": parsed.get("cited_evidence", []),
        "reasoning": str(parsed.get("reasoning", "")).strip(),
        "parsed_json": parsed,
    }


def _parse_gov_response(raw_text: str) -> dict[str, Any]:
    parsed = _extract_json_object(raw_text)
    if not parsed:
        return {"parse_ok": False, "verdict": "ERROR", "parse_error": "No JSON object found."}
    verdict = _normalize_verdict(parsed.get("final_verdict") or parsed.get("verdict"))
    if verdict not in {"ALLOW", "ESCALATE"}:
        return {
            "parse_ok": False,
            "verdict": "ERROR",
            "parse_error": f"Parsed final_verdict was not ALLOW/ESCALATE: {parsed.get('final_verdict')!r}",
            "parsed_json": parsed,
        }
    return {
        "parse_ok": True,
        "verdict": verdict,
        "controlling_reason": str(parsed.get("controlling_reason", "")).strip(),
        "analyst_disagreements": parsed.get("analyst_disagreements", []),
        "cited_evidence": parsed.get("cited_evidence", []),
        "parsed_json": parsed,
    }


def _base_record(card: dict[str, Any], roster_model: dict[str, str], latency_ms: int, *, execution_mode: str, operator: str) -> dict[str, Any]:
    return {
        "result_id": f"{card['packet_id']}::{card['role']}::{roster_model['provider']}::{roster_model['model']}",
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "official_trace": True,
        "judge": False,
        "qa_or_ablation": False,
        "freeze": False,
        "benchmark_credit": False,
        "scorecard_movement": False,
        "leaderboard_movement": False,
        "execution_mode": execution_mode,
        "operator": operator,
        "packet_id": card["packet_id"],
        "packet_hash": card["packet_hash"],
        "hash8": card["hash8"],
        "family_id": card["family_id"],
        "role": card["role"],
        "provider": roster_model["provider"],
        "transport_provider": _transport_provider(roster_model["provider"]),
        "model": roster_model["model"],
        "latency_ms": latency_ms,
        "called_at": _utc_now(),
    }


def _error_record(card: dict[str, Any], roster_model: dict[str, str], exc: Exception, latency_ms: int, *, execution_mode: str, operator: str) -> dict[str, Any]:
    if isinstance(exc, provider_core.ProviderCallError):
        error_type = exc.error_type
        error_message = str(exc)
        http_status = exc.http_status
        raw_text = exc.raw_text
    else:
        error_type = type(exc).__name__
        error_message = str(exc)
        http_status = None
        raw_text = ""
    record = _base_record(card, roster_model, latency_ms, execution_mode=execution_mode, operator=operator)
    record.update(
        {
            "provider_call_ok": False,
            "parse_ok": False,
            "verdict": "ERROR",
            "raw_text_excerpt": provider_core._excerpt(raw_text),
            "http_status": http_status,
            "error_type": error_type,
            "error_message_excerpt": provider_core._excerpt(error_message),
            "provider_error": f"{error_type}: {error_message}",
            "error_stage": "provider_call",
        }
    )
    return record


def attempt_provider_call(card: dict[str, Any], roster_model: dict[str, str], timeout: int, *, execution_mode: str, operator: str) -> dict[str, Any]:
    start = time.time()
    transport_model = _transport_model(roster_model)
    try:
        call_result = provider_core._call_provider_raw(card, transport_model, timeout)
    except Exception as exc:
        return _error_record(card, roster_model, exc, int((time.time() - start) * 1000), execution_mode=execution_mode, operator=operator)

    latency_ms = int((time.time() - start) * 1000)
    raw_text = call_result["raw_text"]
    parsed = _parse_gov_response(raw_text) if card["role"] == "holo_gov" else _parse_active_response(raw_text)
    record = _base_record(card, roster_model, latency_ms, execution_mode=execution_mode, operator=operator)
    record.update(
        {
            "provider_call_ok": True,
            "parse_ok": parsed["parse_ok"],
            "verdict": parsed["verdict"],
            "raw_text_excerpt": provider_core._excerpt(raw_text),
            "http_status": call_result.get("http_status"),
            "input_tokens": call_result.get("input_tokens", 0),
            "output_tokens": call_result.get("output_tokens", 0),
        }
    )
    if parsed["parse_ok"]:
        for key in ("material_blocker", "cited_evidence", "reasoning", "controlling_reason", "analyst_disagreements"):
            if key in parsed:
                record[key] = parsed[key]
        record["parsed_json"] = parsed.get("parsed_json", {})
    else:
        record["parse_error"] = parsed.get("parse_error", "")
        if "parsed_json" in parsed:
            record["parsed_json"] = parsed["parsed_json"]
    return record


def _gov_prompt_card(packet: dict[str, Any], roster_model: dict[str, str], active_records: list[dict[str, Any]]) -> dict[str, Any]:
    card = _gov_template_card(packet, roster_model)
    card["role"] = "holo_gov"
    card["preflight_only"] = False
    card["official_trace"] = True
    card["user"] = json.dumps(
        {
            "action": packet["model_visible"]["action"],
            "context": packet["model_visible"]["context"],
            "active_non_gov_responses": [
                {
                    "provider": record["provider"],
                    "model": record["model"],
                    "provider_call_ok": record["provider_call_ok"],
                    "parse_ok": record["parse_ok"],
                    "verdict": record.get("verdict", "ERROR"),
                    "material_blocker": record.get("material_blocker"),
                    "cited_evidence": record.get("cited_evidence", []),
                    "reasoning": record.get("reasoning", ""),
                    "raw_text_excerpt": record.get("raw_text_excerpt", ""),
                }
                for record in active_records
            ],
        },
        sort_keys=True,
    )
    return card


def _packet_trace_record(packet: dict[str, Any], roster: dict[str, Any], active_records: list[dict[str, Any]], gov_record: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    return {
        "record_type": "bal100_allow_five_official_trace",
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "official_trace": True,
        "judge": False,
        "qa_or_ablation": False,
        "freeze": False,
        "benchmark_credit": False,
        "scorecard_movement": False,
        "leaderboard_movement": False,
        "session_id": packet["session_id"],
        "seed": SEED,
        "git_head": _git_head(),
        "created_at": _utc_now(),
        "packet": {
            "scenario_id": packet["scenario_id"],
            "family_id": packet["family_id"],
            "path": packet["path"],
            "payload_hash": packet["payload_hash"],
            "hash8": packet["hash8"],
            "model_visible_keys": packet["model_visible_keys"],
            "frozen_approved_by": packet["frozen_approved_by"],
        },
        "roster": {
            "holo_gov": roster["holo_gov"],
            "active_non_gov": roster["active_non_gov"],
            "excluded": roster["excluded"],
            "selection_rule": roster["selection_rule"],
        },
        "calls": {
            "active_non_gov": active_records,
            "holo_gov": gov_record,
        },
        "hidden_metadata_excluded": sorted(FORBIDDEN_MODEL_VISIBLE_KEYS),
        "output_directory": str(out_dir),
        "proof_credit_remains_unchanged": True,
    }


def _summarize(records: list[dict[str, Any]], trace_paths: list[str], *, execution_mode: str, operator: str, out_dir: Path) -> dict[str, Any]:
    error_records = [record for record in records if not record.get("provider_call_ok") or not record.get("parse_ok")]
    verdicts_by_packet: dict[str, dict[str, str]] = {}
    for record in records:
        verdicts_by_packet.setdefault(record["packet_id"], {})[
            f"{record['role']}:{record['provider']}:{record['model']}"
        ] = record.get("verdict", "ERROR")
    return {
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "run_status": "complete" if not error_records else "complete_with_errors",
        "official_trace": True,
        "judge": False,
        "qa_or_ablation": False,
        "freeze": False,
        "benchmark_credit": False,
        "scorecard_movement": False,
        "leaderboard_movement": False,
        "execution_mode": execution_mode,
        "operator": operator,
        "out_dir": str(out_dir),
        "packet_count": 5,
        "expected_row_count": 20,
        "results": len(records),
        "error_results": len(error_records),
        "provider_error_counts": dict(Counter(record.get("provider", "unknown") for record in error_records)),
        "verdicts_by_packet": verdicts_by_packet,
        "official_trace_record_paths": trace_paths,
        "proof_credit_remains_unchanged": True,
        "created_at": _utc_now(),
    }


def execute_official_trace(timeout: int, out_dir: Path, *, execution_mode: str, operator: str) -> dict[str, Any]:
    packets = _load_packets()
    if out_dir.exists():
        raise SystemExit(f"{out_dir} already exists; refusing to overwrite official trace output.")

    prompt_dir = out_dir / "prompt_cards"
    trace_dir = out_dir / "official_trace_records"
    prompt_dir.mkdir(parents=True, exist_ok=False)
    trace_dir.mkdir(parents=True, exist_ok=False)

    records: list[dict[str, Any]] = []
    trace_paths: list[str] = []
    results_path = out_dir / "results.jsonl"

    for packet in packets:
        roster = _roster(packet["session_id"])
        active_records: list[dict[str, Any]] = []
        for roster_model in roster["active_non_gov"]:
            card = _active_prompt_card(packet, roster_model)
            card["preflight_only"] = False
            card["official_trace"] = True
            card_path = prompt_dir / f"{packet['scenario_id']}__active__{roster_model['provider']}__{_safe_model_name(roster_model['model'])}.json"
            card_path.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")
            record = attempt_provider_call(card, roster_model, timeout, execution_mode=execution_mode, operator=operator)
            records.append(record)
            active_records.append(record)
            with results_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")

        gov_model = roster["holo_gov"]
        gov_card = _gov_prompt_card(packet, gov_model, active_records)
        gov_card_path = prompt_dir / f"{packet['scenario_id']}__hologov__{_safe_model_name(gov_model['model'])}.json"
        gov_card_path.write_text(json.dumps(gov_card, indent=2, sort_keys=True) + "\n")
        gov_record = attempt_provider_call(gov_card, gov_model, timeout, execution_mode=execution_mode, operator=operator)
        records.append(gov_record)
        with results_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(gov_record, sort_keys=True) + "\n")

        trace_record = _packet_trace_record(packet, roster, active_records, gov_record, out_dir)
        trace_path = trace_dir / f"{packet['scenario_id']}_{packet['hash8']}_official_trace.json"
        trace_path.write_text(json.dumps(trace_record, indent=2, sort_keys=True) + "\n")
        trace_paths.append(str(trace_path))

    summary = _summarize(records, trace_paths, execution_mode=execution_mode, operator=operator, out_dir=out_dir)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight or execute exact five-packet BAL100 ALLOW official trace run.")
    parser.add_argument("--execute-provider-calls", action="store_true")
    parser.add_argument("--operator", default="")
    parser.add_argument("--allow-codex-provider-calls", action="store_true")
    parser.add_argument("--i-am-taylor-local", action="store_true")
    parser.add_argument("--yes-send-frozen-payloads-to-providers", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args(argv)

    if not args.execute_provider_calls:
        manifest = build_preflight(args.out_dir)
        print(
            "preflight status={status} packets={packets} prompt_cards={cards} expected_future_rows={rows}".format(
                status=manifest["status"],
                packets=manifest["packet_count"],
                cards=manifest["prompt_cards"]["total"],
                rows=manifest["expected_future_live_outputs"]["provider_rows"],
            )
        )
        return 0 if manifest["status"] == "PASS" else 1

    execution_mode = _require_execution_approval(args)
    summary = execute_official_trace(args.timeout, args.out_dir, execution_mode=execution_mode, operator=args.operator)
    print(
        "official_trace status={status} rows={rows} errors={errors} out_dir={out_dir}".format(
            status=summary["run_status"],
            rows=summary["results"],
            errors=summary["error_results"],
            out_dir=summary["out_dir"],
        )
    )
    return 0 if summary["run_status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
