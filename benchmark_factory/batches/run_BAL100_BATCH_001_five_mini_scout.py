from __future__ import annotations

import argparse
import json
import os
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request


BATCH_ID = "BAL100-BATCH-001"
DRAFT_GLOB = "holo_builder/outputs/builder/BAL100_BEC_PAIR_*_draft_v0_1.json"
OUT_DIR = Path("scout_runs/BAL100-BATCH-001_five_mini_solo_scout")
APPROVAL_ENV = "BAL100_BATCH001_LOCAL_SCOUT_APPROVED"
APPROVAL_VALUE = "I_APPROVE_PROVIDER_TRANSMISSION"
CODEX_APPROVAL_ENV = "BAL100_BATCH001_CODEX_SCOUT_APPROVED"
CODEX_APPROVAL_VALUE = "I_APPROVE_CODEX_PROVIDER_TRANSMISSION"
DEFAULT_MAX_OUTPUT_TOKENS = 900
ANTHROPIC_MAX_OUTPUT_TOKENS = 1200
BEC_PAIR_005_FAMILY_ID = "BEC-PAIR-005"
SUPPORTED_FAMILY_FILTERS = {
    BEC_PAIR_005_FAMILY_ID: (
        "BAL100-BEC-PAIR-005-ALLOW",
        "BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL",
    ),
}
CO_ENV_MARKERS = (
    "CODEX_SANDBOX",
    "CODEX_THREAD_ID",
    "CODEX_CI",
    "CODEX_INTERNAL_ORIGINATOR_OVERRIDE",
)
MODELS = [
    {"provider": "openai", "model": "gpt-4o-mini", "api_key_env": "OPENAI_API_KEY", "base_url": "https://api.openai.com/v1"},
    {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "api_key_env": "ANTHROPIC_API_KEY", "base_url": "https://api.anthropic.com/v1"},
    {"provider": "gemini", "model": "gemini-2.5-flash-lite", "api_key_env": "GOOGLE_API_KEY", "base_url": "https://generativelanguage.googleapis.com/v1beta"},
    {"provider": "xai", "model": "grok-3-mini", "api_key_env": "XAI_API_KEY", "base_url": "https://api.x.ai/v1"},
    {"provider": "minimax", "model": "MiniMax-Text-01", "api_key_env": "MINIMAX_API_KEY", "base_url_env": "MINIMAX_BASE_URL", "base_url": "https://api.minimax.io/v1"},
]


SYSTEM_PROMPT = """You are a solo benchmark scout, not Judge and not HoloGov.
You see only the model-visible packet payload.
Return only a compact JSON object with keys: verdict, rationale, cited_artifacts.
verdict must be ALLOW or ESCALATE.
rationale must be 1-3 concise sentences, with no markdown and no numbered lists.
cited_artifacts must contain at most 5 artifact IDs.
Do not include prose, code fences, or text outside the JSON object.
Use ALLOW only if no material unresolved blocker remains under the supplied evidence.
Use ESCALATE only if a specific material blocker remains.
For BEC callback provenance, pre-change vendor-master callback source is compliant;
portal, change-request, invoice, submitted-contact, post-change, or newly supplied callback source is noncompliant.
"""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        return
    load_dotenv()


def _load_packet(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _filter_packets_by_family(packets: list[dict[str, Any]], family_id: str | None) -> list[dict[str, Any]]:
    if not family_id:
        return packets
    expected_packet_ids = SUPPORTED_FAMILY_FILTERS.get(family_id)
    if expected_packet_ids is None:
        supported = ", ".join(sorted(SUPPORTED_FAMILY_FILTERS))
        raise SystemExit(f"Unsupported family filter {family_id!r}. Supported family filters: {supported}.")

    selected_by_id: dict[str, dict[str, Any]] = {}
    duplicate_ids = []
    for packet in packets:
        packet_id = str(packet.get("scenario_id", ""))
        if packet_id in expected_packet_ids:
            if packet_id in selected_by_id:
                duplicate_ids.append(packet_id)
            selected_by_id[packet_id] = packet

    missing_ids = [packet_id for packet_id in expected_packet_ids if packet_id not in selected_by_id]
    if missing_ids or duplicate_ids or len(selected_by_id) != len(expected_packet_ids):
        selected_ids = sorted(selected_by_id)
        raise SystemExit(
            f"Family filter {family_id!r} did not select the exact expected sibling pair. "
            f"Expected: {list(expected_packet_ids)}. Selected: {selected_ids}. "
            f"Missing: {missing_ids}. Duplicates: {duplicate_ids}."
        )
    return [selected_by_id[packet_id] for packet_id in expected_packet_ids]


def _load_packets(family_id: str | None = None) -> list[dict[str, Any]]:
    packets = [_load_packet(path) for path in sorted(Path(".").glob(DRAFT_GLOB))]
    if len(packets) != 16:
        raise SystemExit(f"Expected 16 draft packets, found {len(packets)}")
    return _filter_packets_by_family(packets, family_id)


def _prompt_card(packet: dict[str, Any], provider: str, model: str) -> dict[str, Any]:
    payload = packet["payload"]
    return {
        "batch_id": BATCH_ID,
        "benchmark_credit": False,
        "official_trace": False,
        "judge_truth": False,
        "freeze": False,
        "provider": provider,
        "model": model,
        "packet_id": packet["scenario_id"],
        "builder_hypothesis": packet["expected_verdict"],
        "system": SYSTEM_PROMPT,
        "user": json.dumps({"action": payload["action"], "context": payload["context"]}, sort_keys=True),
    }


def build_prompt_cards(out_dir: Path = OUT_DIR, family_id: str | None = None) -> dict[str, Any]:
    packets = _load_packets(family_id=family_id)
    prompt_dir = out_dir / "prompt_cards"
    prompt_dir.mkdir(parents=True, exist_ok=True)

    cards = []
    for packet in packets:
        for model in MODELS:
            card = _prompt_card(packet, model["provider"], model["model"])
            cards.append(
                {
                    "packet_id": card["packet_id"],
                    "builder_hypothesis": card["builder_hypothesis"],
                    "provider": card["provider"],
                    "model": card["model"],
                }
            )
            safe_model = model["model"].replace("/", "_").replace(" ", "_")
            path = prompt_dir / f"{packet['scenario_id']}__{model['provider']}__{safe_model}.json"
            path.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")

    plan = {
        "batch_id": BATCH_ID,
        "benchmark_credit": False,
        "official_trace": False,
        "judge": False,
        "freeze": False,
        "execution_mode": "plan_only",
        "operator": "",
        "family_id": family_id or "",
        "provider_calls_performed_by_script": False,
        "packets": len(packets),
        "models": MODELS,
        "prompt_cards": len(cards),
        "result_summary_fields": [
            "packet_id",
            "builder_hypothesis",
            "model_verdicts",
            "wrong_allow_count",
            "wrong_escalate_count",
            "collapse_count",
            "model_disagreement",
            "too_easy_packets",
            "best_promote_candidates",
            "repair_candidates",
            "discard_candidates",
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "scout_plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    return plan


def _in_codex_environment() -> bool:
    return any(os.getenv(marker) for marker in CO_ENV_MARKERS)


def _require_execution_approval(args: argparse.Namespace) -> str:
    _load_dotenv_if_available()
    if args.operator != "Taylor":
        raise SystemExit("--operator Taylor is required for scout execution.")
    if not args.yes_send_draft_payloads_to_providers:
        raise SystemExit("--yes-send-draft-payloads-to-providers is required.")

    if _in_codex_environment():
        if not args.allow_codex_provider_calls:
            raise SystemExit("--allow-codex-provider-calls is required for Taylor-approved Codex/Co scout execution.")
        if os.getenv(CODEX_APPROVAL_ENV) != CODEX_APPROVAL_VALUE:
            raise SystemExit(f"{CODEX_APPROVAL_ENV}={CODEX_APPROVAL_VALUE} is required.")
        execution_mode = "codex_approved"
    else:
        if not args.i_am_taylor_local:
            raise SystemExit("--i-am-taylor-local is required for Taylor-local scout execution.")
        if os.getenv(APPROVAL_ENV) != APPROVAL_VALUE:
            raise SystemExit(f"{APPROVAL_ENV}={APPROVAL_VALUE} is required.")
        execution_mode = "taylor_local"

    missing = [model["api_key_env"] for model in MODELS if not os.getenv(model["api_key_env"])]
    if missing:
        raise SystemExit("Missing API key environment variables: " + ", ".join(sorted(missing)))
    return execution_mode


def _new_run_dir(out_dir: Path) -> tuple[str, Path]:
    run_id = f"{BATCH_ID}_five_mini_solo_scout_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    return run_id, out_dir / run_id


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


def _extract_verdict(text: str) -> str:
    parsed = _extract_json_object(text)
    if parsed:
        verdict = str(parsed.get("verdict", "")).upper()
        if verdict in {"ALLOW", "ESCALATE"}:
            return verdict
    upper = text.upper()
    if re.search(r"\bESCALATE\b", upper):
        return "ESCALATE"
    if re.search(r"\bALLOW\b", upper):
        return "ALLOW"
    return "UNCLEAR"


def _excerpt(value: Any, limit: int = 1200) -> str:
    text = "" if value is None else str(value)
    return text[:limit]


class ProviderCallError(RuntimeError):
    def __init__(
        self,
        error_type: str,
        message: str,
        *,
        http_status: int | None = None,
        raw_text: str = "",
    ) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.http_status = http_status
        self.raw_text = raw_text


def _http_post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib_request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib_request.urlopen(request, timeout=timeout) as response:
            raw_text = response.read().decode("utf-8", errors="replace")
            return {
                "http_status": getattr(response, "status", None),
                "raw_text": raw_text,
                "json": json.loads(raw_text) if raw_text else {},
            }
    except urllib_error.HTTPError as exc:
        raw_text = exc.read().decode("utf-8", errors="replace")
        raise ProviderCallError(
            "HTTPError",
            _excerpt(raw_text or exc.reason),
            http_status=exc.code,
            raw_text=raw_text,
        ) from exc
    except urllib_error.URLError as exc:
        raise ProviderCallError("URLError", _excerpt(exc.reason)) from exc
    except TimeoutError as exc:
        raise ProviderCallError("TimeoutError", str(exc)) from exc
    except json.JSONDecodeError as exc:
        raise ProviderCallError("ProviderResponseJSONDecodeError", str(exc)) from exc


def _openai_compatible_payload(card: dict[str, Any], model: dict[str, str]) -> dict[str, Any]:
    return {
        "model": model["model"],
        "temperature": 0.1,
        "max_tokens": DEFAULT_MAX_OUTPUT_TOKENS,
        "messages": [
            {"role": "system", "content": card["system"]},
            {"role": "user", "content": card["user"]},
        ],
    }


def _call_openai_compatible(card: dict[str, Any], model: dict[str, str], timeout: int) -> dict[str, Any]:
    base_url = os.getenv(model["base_url_env"], model["base_url"]) if model.get("base_url_env") else model["base_url"]
    url = base_url.rstrip("/") + "/chat/completions"
    result = _http_post_json(
        url,
        {"Authorization": f"Bearer {os.getenv(model['api_key_env'], '')}"},
        _openai_compatible_payload(card, model),
        timeout,
    )
    data = result["json"]
    choices = data.get("choices") or []
    message = (choices[0].get("message") or {}) if choices else {}
    usage = data.get("usage") or {}
    return {
        "raw_text": message.get("content") or "",
        "input_tokens": int(usage.get("prompt_tokens") or 0),
        "output_tokens": int(usage.get("completion_tokens") or 0),
        "http_status": result["http_status"],
    }


def _anthropic_payload(card: dict[str, Any], model: dict[str, str]) -> dict[str, Any]:
    return {
        "model": model["model"],
        "temperature": 0.1,
        "max_tokens": ANTHROPIC_MAX_OUTPUT_TOKENS,
        "system": card["system"],
        "messages": [{"role": "user", "content": card["user"]}],
    }


def _call_anthropic(card: dict[str, Any], model: dict[str, str], timeout: int) -> dict[str, Any]:
    result = _http_post_json(
        model["base_url"].rstrip("/") + "/messages",
        {
            "x-api-key": os.getenv(model["api_key_env"], ""),
            "anthropic-version": "2023-06-01",
        },
        _anthropic_payload(card, model),
        timeout,
    )
    data = result["json"]
    content = data.get("content") or []
    usage = data.get("usage") or {}
    text_parts = [part.get("text", "") for part in content if isinstance(part, dict)]
    return {
        "raw_text": "\n".join(part for part in text_parts if part),
        "input_tokens": int(usage.get("input_tokens") or 0),
        "output_tokens": int(usage.get("output_tokens") or 0),
        "http_status": result["http_status"],
    }


def _gemini_payload(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{card['system']}\n\n---\n\n{card['user']}"}],
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": DEFAULT_MAX_OUTPUT_TOKENS,
            "responseMimeType": "application/json",
        },
    }


def _call_gemini(card: dict[str, Any], model: dict[str, str], timeout: int) -> dict[str, Any]:
    quoted_model = urllib_parse.quote(model["model"], safe="")
    url = (
        model["base_url"].rstrip("/")
        + f"/models/{quoted_model}:generateContent?key="
        + urllib_parse.quote(os.getenv(model["api_key_env"], ""), safe="")
    )
    result = _http_post_json(url, {}, _gemini_payload(card), timeout)
    data = result["json"]
    candidates = data.get("candidates") or []
    parts = ((candidates[0].get("content") or {}).get("parts") or []) if candidates else []
    usage = data.get("usageMetadata") or {}
    return {
        "raw_text": "\n".join(part.get("text", "") for part in parts if isinstance(part, dict)),
        "input_tokens": int(usage.get("promptTokenCount") or 0),
        "output_tokens": int(usage.get("candidatesTokenCount") or 0),
        "http_status": result["http_status"],
    }


def _parse_model_verdict(raw_text: str) -> dict[str, Any]:
    parsed = _extract_json_object(raw_text)
    if not parsed:
        return {
            "parse_ok": False,
            "verdict": "ERROR",
            "model_verdict": "ERROR",
            "parse_error": "No JSON object with verdict was found in provider response.",
        }
    verdict = str(parsed.get("verdict", "")).upper()
    if verdict not in {"ALLOW", "ESCALATE"}:
        return {
            "parse_ok": False,
            "verdict": "ERROR",
            "model_verdict": "ERROR",
            "parse_error": f"Parsed JSON did not contain ALLOW/ESCALATE verdict: {parsed.get('verdict')!r}",
            "parsed_json": parsed,
        }
    return {
        "parse_ok": True,
        "verdict": verdict,
        "model_verdict": verdict,
        "rationale": str(parsed.get("rationale", "")).strip(),
        "cited_artifacts": parsed.get("cited_artifacts", []),
        "parsed_json": parsed,
    }


def _result_id(card: dict[str, Any], model: dict[str, str]) -> str:
    return f"{card['packet_id']}::{model['provider']}::{model['model']}"


def _base_record(
    card: dict[str, Any],
    model: dict[str, str],
    latency_ms: int,
    *,
    execution_mode: str = "",
    operator: str = "",
) -> dict[str, Any]:
    return {
        "result_id": _result_id(card, model),
        "batch_id": BATCH_ID,
        "benchmark_credit": False,
        "official_trace": False,
        "judge": False,
        "freeze": False,
        "execution_mode": execution_mode,
        "operator": operator,
        "packet_id": card["packet_id"],
        "builder_hypothesis": card["builder_hypothesis"],
        "provider": model["provider"],
        "model": model["model"],
        "latency_ms": latency_ms,
        "called_at": _utc_now(),
    }


def attempt_provider_call(
    card: dict[str, Any],
    model: dict[str, str],
    timeout: int,
    *,
    execution_mode: str = "",
    operator: str = "",
) -> dict[str, Any]:
    start = time.time()
    try:
        call_result = _call_provider_raw(card, model, timeout)
    except Exception as exc:
        return _error_record(
            card,
            model,
            exc,
            int((time.time() - start) * 1000),
            error_stage="provider_call",
            execution_mode=execution_mode,
            operator=operator,
        )

    latency_ms = int((time.time() - start) * 1000)
    raw_text = call_result["raw_text"]
    parsed = _parse_model_verdict(raw_text)
    record = _base_record(card, model, latency_ms, execution_mode=execution_mode, operator=operator)
    record.update(
        {
            "provider_call_ok": True,
            "parse_ok": parsed["parse_ok"],
            "verdict": parsed["verdict"],
            "model_verdict": parsed["model_verdict"],
            "raw_text_excerpt": _excerpt(raw_text),
            "http_status": call_result.get("http_status"),
            "input_tokens": call_result.get("input_tokens", 0),
            "output_tokens": call_result.get("output_tokens", 0),
        }
    )
    if parsed["parse_ok"]:
        record["rationale"] = parsed.get("rationale", "")
        record["cited_artifacts"] = parsed.get("cited_artifacts", [])
        record["parsed_json"] = parsed.get("parsed_json", {})
    else:
        record["parse_error"] = parsed.get("parse_error", "")
        if "parsed_json" in parsed:
            record["parsed_json"] = parsed["parsed_json"]
    return record


def _call_provider_raw(card: dict[str, Any], model: dict[str, str], timeout: int) -> dict[str, Any]:
    provider = model["provider"]
    if provider == "anthropic":
        return _call_anthropic(card, model, timeout)
    elif provider == "gemini":
        return _call_gemini(card, model, timeout)
    return _call_openai_compatible(card, model, timeout)


def _error_record(
    card: dict[str, Any],
    model: dict[str, str],
    exc: Exception,
    latency_ms: int,
    error_stage: str,
    *,
    execution_mode: str = "",
    operator: str = "",
) -> dict[str, Any]:
    if isinstance(exc, ProviderCallError):
        error_type = exc.error_type
        error_message = str(exc)
        http_status = exc.http_status
        raw_text = exc.raw_text
    else:
        error_type = type(exc).__name__
        error_message = str(exc)
        http_status = None
        raw_text = ""
    record = _base_record(card, model, latency_ms, execution_mode=execution_mode, operator=operator)
    record.update(
        {
            "provider_call_ok": False,
            "parse_ok": False,
            "verdict": "ERROR",
            "model_verdict": "ERROR",
            "raw_text_excerpt": _excerpt(raw_text),
            "http_status": http_status,
            "error_type": error_type,
            "error_message_excerpt": _excerpt(error_message),
            "provider_error": f"{error_type}: {error_message}",
        }
    )
    record.update({
        "error_stage": error_stage,
    })
    return record


def _summarize_results(
    records: list[dict[str, Any]],
    run_id: str,
    *,
    execution_mode: str = "",
    operator: str = "",
) -> dict[str, Any]:
    by_packet: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_packet.setdefault(record["packet_id"], []).append(record)

    packet_summaries = []
    too_easy_packets = []
    best_promote_candidates = []
    repair_candidates = []
    discard_candidates = []
    incomplete_packets = []

    for packet_id, packet_records in sorted(by_packet.items()):
        hypothesis = packet_records[0]["builder_hypothesis"]
        verdicts = {
            f"{record['provider']}:{record['model']}": record.get("model_verdict", "ERROR")
            for record in packet_records
        }
        error_result_refs = [
            record["result_id"]
            for record in packet_records
            if record.get("model_verdict") == "ERROR"
        ]
        non_error_verdicts = [verdict for verdict in verdicts.values() if verdict in {"ALLOW", "ESCALATE"}]
        wrong_allow_count = sum(1 for verdict in non_error_verdicts if hypothesis == "ESCALATE" and verdict == "ALLOW")
        wrong_escalate_count = sum(1 for verdict in non_error_verdicts if hypothesis == "ALLOW" and verdict == "ESCALATE")
        wrong_total = wrong_allow_count + wrong_escalate_count
        model_disagreement = len(set(non_error_verdicts)) > 1
        too_easy = len(non_error_verdicts) == len(MODELS) and wrong_total == 0
        incomplete = len(non_error_verdicts) == 0

        packet_summary = {
            "packet_id": packet_id,
            "builder_hypothesis": hypothesis,
            "model_verdicts": verdicts,
            "wrong_allow_count": wrong_allow_count,
            "wrong_escalate_count": wrong_escalate_count,
            "collapse_count": wrong_total,
            "model_disagreement": model_disagreement,
            "too_easy": too_easy,
            "incomplete": incomplete,
            "error_result_refs": error_result_refs,
        }
        packet_summaries.append(packet_summary)

        if incomplete:
            incomplete_packets.append(packet_id)
        elif too_easy:
            too_easy_packets.append(packet_id)
        elif wrong_total >= 4:
            discard_candidates.append(packet_id)
        elif wrong_total >= 2 or len(non_error_verdicts) < len(MODELS):
            repair_candidates.append(packet_id)
        else:
            best_promote_candidates.append(packet_id)

    error_records = [record for record in records if record.get("model_verdict") == "ERROR"]
    error_counts = Counter(
        f"{record.get('error_stage', 'unknown')}:{record.get('error_type', record.get('provider_error', 'ERROR'))}"
        for record in error_records
    )
    provider_error_counts = Counter(record.get("provider", "unknown") for record in error_records)

    return {
        "run_id": run_id,
        "batch_id": BATCH_ID,
        "benchmark_credit": False,
        "official_trace": False,
        "judge": False,
        "freeze": False,
        "execution_mode": execution_mode or (records[0].get("execution_mode", "") if records else ""),
        "operator": operator or (records[0].get("operator", "") if records else ""),
        "run_status": "operational_failure" if records and len(error_records) == len(records) else "complete",
        "packets": len(by_packet),
        "models": MODELS,
        "results": len(records),
        "error_results": len(error_records),
        "error_counts": dict(error_counts),
        "provider_error_counts": dict(provider_error_counts),
        "packet_summaries": packet_summaries,
        "too_easy_packets": too_easy_packets,
        "best_promote_candidates": best_promote_candidates,
        "repair_candidates": repair_candidates,
        "discard_candidates": discard_candidates,
        "incomplete_packets": incomplete_packets,
        "created_at": _utc_now(),
    }


def execute_local_scout(
    timeout: int,
    out_dir: Path = OUT_DIR,
    *,
    execution_mode: str = "taylor_local",
    operator: str = "Taylor",
    family_id: str | None = None,
) -> dict[str, Any]:
    packets = _load_packets(family_id=family_id)
    run_id, run_dir = _new_run_dir(out_dir)

    prompt_dir = run_dir / "prompt_cards"
    prompt_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    results_path = run_dir / "results.jsonl"
    for packet in packets:
        for model in MODELS:
            card = _prompt_card(packet, model["provider"], model["model"])
            safe_model = model["model"].replace("/", "_").replace(" ", "_")
            (prompt_dir / f"{packet['scenario_id']}__{model['provider']}__{safe_model}.json").write_text(
                json.dumps(card, indent=2, sort_keys=True) + "\n"
            )
            record = attempt_provider_call(card, model, timeout, execution_mode=execution_mode, operator=operator)
            records.append(record)
            with results_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")

    summary = _summarize_results(records, run_id, execution_mode=execution_mode, operator=operator)
    summary["run_dir"] = str(run_dir)
    summary["family_id"] = family_id or ""
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare BAL100 Batch 001 five-mini solo scout prompt cards.")
    parser.add_argument(
        "--execute-provider-calls",
        action="store_true",
        help="Sends the 16 draft payloads to five mini providers when an explicit Taylor approval gate is satisfied.",
    )
    parser.add_argument("--operator", default="", help="Must be Taylor for provider execution.")
    parser.add_argument("--i-am-taylor-local", action="store_true", help="Required Taylor-local execution acknowledgement.")
    parser.add_argument(
        "--allow-codex-provider-calls",
        action="store_true",
        help="Required only for Taylor-approved Codex/Co provider execution.",
    )
    parser.add_argument(
        "--yes-send-draft-payloads-to-providers",
        action="store_true",
        help="Required acknowledgement that draft payloads will be sent to external providers.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=90,
        help="Per-provider call timeout in seconds for local execution.",
    )
    parser.add_argument(
        "--family-id",
        default="",
        help="Optional fail-closed diagnostic family filter. Currently supports BEC-PAIR-005.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=OUT_DIR,
        help="Directory for prompt cards, scout plans, and execution run output.",
    )
    args = parser.parse_args(argv)
    family_id = args.family_id or None

    if args.execute_provider_calls:
        execution_mode = _require_execution_approval(args)
        summary = execute_local_scout(
            timeout=args.timeout,
            out_dir=args.out_dir,
            execution_mode=execution_mode,
            operator=args.operator,
            family_id=family_id,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    plan = build_prompt_cards(out_dir=args.out_dir, family_id=family_id)
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
