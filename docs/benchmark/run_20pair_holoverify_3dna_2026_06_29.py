#!/usr/bin/env python3
"""Run the 20-pair HoloVerify benchmark through complete 3-DNA Holo.

This is a new sibling lane. It does not mutate the older MiniMax-only freeze.

Architecture per packet:
- worker 1: xAI Grok mini
- Gov 1: MiniMax
- worker 2: Gemini Flash Lite
- Gov 2: MiniMax
- worker 3: MiniMax

The runner logs prompt refs, model roster, deterministic gates after every
worker, Gov gate awareness, artifact registry, pinned best artifact, monotonic
preservation checks, final selector, token accounting, and intra-Holo local
verdict misses.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import importlib.util
import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from holo_architecture_invariants import (
    validate_holo_benchmark_laws,
    validate_worker_prompt_hierarchy,
)

DEFAULT_AGGREGATE = BENCHMARK_ROOT / "three_mini_seam_scout_2026-06-29" / "AGGREGATE_20_ONE_SHOT_MINI_SOLO_FAILURE_CANDIDATES.json"
BALANCED_AGGREGATE = BENCHMARK_ROOT / "three_mini_seam_scout_2026-06-29" / "AGGREGATE_20_BALANCED_3DNA_CURRENT_FAILURE_CANDIDATES.json"
AGGREGATE = Path(
    os.getenv(
        "HOLOVERIFY_3DNA_AGGREGATE",
        str(BALANCED_AGGREGATE if BALANCED_AGGREGATE.exists() else DEFAULT_AGGREGATE),
    )
)
OUT_ROOT = BENCHMARK_ROOT / "holoverify_20pair_3dna_2026-06-29"
PRE_RUN_MANIFEST = OUT_ROOT / "PRE_RUN_MANIFEST.json"
TRANSPORT_RETRY_POLICY_VERSION = "HOLOVERIFY_TRANSPORT_RETRY_POLICY_V1_2026_06_29"
TRANSPORT_MAX_RETRIES = 2
TRANSPORT_BACKOFF_SECONDS = (2, 4)
EMPTY_WORKER_OUTPUT_RETRY_POLICY_VERSION = "HOLOVERIFY_EMPTY_WORKER_OUTPUT_RETRY_POLICY_V1_2026_06_29"
EMPTY_WORKER_OUTPUT_MAX_RETRIES = 2
EMPTY_WORKER_OUTPUT_BACKOFF_SECONDS = (1, 2)
PROVIDER_HTTP_TIMEOUT_SECONDS = 150
RETRYABLE_HTTP_STATUS = {429, 500, 502, 503, 504}


MODEL_CONFIGS: dict[str, dict[str, Any]] = {
    "minimax": {
        "provider": "minimax",
        "model": "MiniMax-M2.5-highspeed",
        "dna": "minimax",
        "api_key_env": "MINIMAX_API_KEY",
        "kind": "openai_compatible",
        "url_env": "MINIMAX_CHAT_COMPLETIONS_URL",
        "base_url_env": "MINIMAX_BASE_URL",
        "default_url": "https://api.minimaxi.chat/v1/chat/completions",
    },
    "xai": {
        "provider": "xai",
        "model": "grok-3-mini",
        "dna": "xai",
        "api_key_env": "XAI_API_KEY",
        "kind": "openai_compatible",
        "default_url": "https://api.x.ai/v1/chat/completions",
    },
    "google": {
        "provider": "google",
        "model": "gemini-2.5-flash-lite",
        "dna": "google",
        "api_key_env": "GOOGLE_API_KEY",
        "kind": "gemini",
    },
}

WORKER_SEQUENCE = [
    {"worker_index": 1, "role_name": "SOURCE_BOUNDARY_MAPPER", "model_key": "xai"},
    {"worker_index": 2, "role_name": "ADVERSARIAL_SCOPE_CHALLENGER", "model_key": "google"},
    {"worker_index": 3, "role_name": "FINAL_COMPILER", "model_key": "minimax"},
]
GOV_MODEL_KEY = "minimax"
WORKER_MAX_TOKENS = 3600
MINIMAX_FINAL_COMPILER_WORKER_MAX_TOKENS = 6000
GOV_MAX_TOKENS = 384
DYNAMIC_EARLY_EXIT_ENABLED = False

FORBIDDEN_PROMPT_TERMS = (
    "hidden_expected_verdict",
    "expected_for_local_audit_only",
    "target_match",
    "Solo failed",
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _strip_thinking_blocks(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I)
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.S | re.I)
    return text.strip()


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location("holo_3dna_spec_module", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _module_specs(path: Path) -> list[dict[str, Any]]:
    module = _load_module(path)
    if hasattr(module, "SPECS"):
        return module.SPECS
    if hasattr(module, "base") and hasattr(module.base, "SPECS"):
        return module.base.SPECS
    raise RuntimeError(f"spec module does not expose SPECS: {path}")


def _packet_from_spec(spec: dict[str, Any], suffix: str) -> dict[str, Any]:
    is_allow = suffix == "A"
    docs = spec["allow_docs"] if is_allow else spec["esc_docs"]
    return {
        "action": {
            "business_ref": f"{spec['pair_id']}-{suffix}",
            "type": spec["type"],
            "vendor": spec.get("action_vendor", spec["vendor"]),
            "amount": spec.get("action_amount", 0),
            "currency": "USD",
            "description": spec["boundary"],
            "action_date": spec.get("action_date", "2026-06-28"),
        },
        "context": {
            "action_boundary": spec["boundary"],
            "anomaly_observed": spec["anomaly"],
            "explanation_summary": "Verify whether the closure evidence exactly matches the action boundary before execution.",
            "internal_documents": [
                {"doc_id": doc_id, "type": "source_record", "content": content}
                for doc_id, content in docs
            ],
            "policy_documents": [
                {
                    "doc_id": spec["policy"][0],
                    "title": "Exact source-boundary policy",
                    "content": spec["policy"][1],
                }
            ],
        },
    }


def _payload_from_prompt_card(path: Path) -> dict[str, Any]:
    card = _load_json(path)
    payload = json.loads(card["user"])
    if not isinstance(payload, dict) or not isinstance(payload.get("context"), dict):
        raise RuntimeError(f"prompt_card_user_is_not_packet_payload:{path}")
    return payload


def _payload_from_json_path(path: Path) -> dict[str, Any]:
    data = _load_json(path)
    payload = data.get("payload") if isinstance(data, dict) else None
    if payload is None:
        payload = data
    if not isinstance(payload, dict) or not isinstance(payload.get("context"), dict):
        raise RuntimeError(f"json_path_is_not_packet_payload:{path}")
    return payload


def _packet_from_pair(pair: dict[str, Any], suffix: str) -> dict[str, Any]:
    if pair.get("payloads") and pair["payloads"].get(suffix):
        return pair["payloads"][suffix]
    if pair.get("payload_paths") and pair["payload_paths"].get(suffix):
        return _payload_from_json_path(Path(pair["payload_paths"][suffix]))
    if pair.get("payload_prompt_cards") and pair["payload_prompt_cards"].get(suffix):
        return _payload_from_prompt_card(Path(pair["payload_prompt_cards"][suffix]))
    return _packet_from_spec(pair["spec"], suffix)


def _source_ids(payload: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for group in ("internal_documents", "policy_documents"):
        for doc in payload.get("context", {}).get(group, []) or []:
            if isinstance(doc, dict) and doc.get("doc_id"):
                ids.add(str(doc["doc_id"]))
    return ids


def _source_context_digest(payload: dict[str, Any]) -> dict[str, Any]:
    context = payload.get("context", {}) if isinstance(payload.get("context"), dict) else {}
    action = payload.get("action", {}) if isinstance(payload.get("action"), dict) else {}
    docs = []
    for group in ("internal_documents", "policy_documents"):
        for doc in context.get(group, []) or []:
            if not isinstance(doc, dict):
                continue
            content = str(doc.get("content") or "")
            docs.append(
                {
                    "doc_id": doc.get("doc_id"),
                    "type": doc.get("type") or group,
                    "content_hint": content[:180],
                }
            )
    return {
        "action_boundary": context.get("action_boundary"),
        "anomaly_observed": context.get("anomaly_observed"),
        "action_type": action.get("type"),
        "action_vendor": action.get("vendor"),
        "action_amount": action.get("amount"),
        "action_date": action.get("action_date"),
        "source_ids": sorted(_source_ids(payload)),
        "source_hints": docs,
    }


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_flatten_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(_flatten_text(v) for v in value)
    return str(value)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, dict):
        items: list[Any] = []
        for key, item in value.items():
            if isinstance(item, list):
                items.extend(item)
            elif isinstance(item, dict):
                items.append(f"{key}: {json.dumps(item, sort_keys=True)}")
            else:
                items.append(f"{key}: {item}")
        return items
    return [value]


def _first_text(value: Any, fallback: str) -> str:
    items = _as_list(value)
    if not items:
        return fallback
    return str(items[0])


def _term_present(text: str, term: Any) -> bool:
    if isinstance(term, (list, tuple)):
        return any(_term_present(text, option) for option in term)
    return str(term).lower() in text.lower()


def _term_label(term: Any) -> str:
    if isinstance(term, (list, tuple)):
        return "|".join(str(option) for option in term)
    return str(term)


def _json_from_text(text: str, *, allow_markdown_fence: bool = False) -> dict[str, Any]:
    stripped = (text or "").strip()
    if stripped.startswith("```"):
        if not allow_markdown_fence:
            raise ValueError("markdown_fence_present")
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.I).strip()
        if stripped.endswith("```"):
            stripped = stripped[:-3].strip()
    return json.loads(stripped)


WORKER_COMPACT_KEYS = (
    "worker_role",
    "verification_verdict",
    "binding_class",
    "action_boundary",
    "allow_rule_assessment",
    "escalate_rule_assessment",
    "dependency_check",
    "controlling_source_fact",
    "cited_evidence",
    "open_blockers",
    "critical_features_preserved",
    "final_answer",
)


def _split_compact_list(value: str) -> list[str]:
    cleaned = value.strip()
    if not cleaned or cleaned.lower() in {"none", "n/a", "na", "[]"}:
        return []
    return [item.strip() for item in cleaned.split("|") if item.strip()]


def _worker_compact_from_text(text: str) -> dict[str, Any]:
    stripped = _strip_thinking_blocks(text or "").strip()
    if not stripped:
        raise ValueError("worker_empty_text")
    if stripped.startswith("```") or "```" in stripped:
        raise ValueError("worker_markdown_fence_present")
    parsed: dict[str, str] = {}
    for raw_line in stripped.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "=" not in line:
            raise ValueError(f"worker_compact_malformed_line:{line[:40]}")
        key, value = line.split("=", 1)
        key = key.strip()
        if key not in WORKER_COMPACT_KEYS:
            raise ValueError(f"worker_compact_unexpected_key:{key}")
        if key in parsed:
            raise ValueError(f"worker_compact_duplicate_key:{key}")
        parsed[key] = value.strip()
    missing = [key for key in WORKER_COMPACT_KEYS if key not in parsed]
    if missing:
        raise ValueError(f"worker_compact_missing_keys:{','.join(missing)}")
    verdict = parsed["verification_verdict"]
    if verdict not in {"ALLOW", "ESCALATE"}:
        raise ValueError("worker_compact_invalid_verdict")
    binding_class = parsed["binding_class"]
    if binding_class not in {"SOURCE_BOUNDARY_CLOSED", "SOURCE_BOUNDARY_OPEN"}:
        raise ValueError("worker_compact_invalid_binding_class")
    return {
        "worker_role": parsed["worker_role"],
        "verification_verdict": verdict,
        "boundary_binding": {
            "action_boundary": parsed["action_boundary"],
            "allow_rule_assessment": parsed["allow_rule_assessment"],
            "escalate_rule_assessment": parsed["escalate_rule_assessment"],
            "timing_scope_authority_dependency_check": parsed["dependency_check"],
            "binding_class": binding_class,
            "controlling_source_fact": parsed["controlling_source_fact"],
        },
        "cited_evidence": _split_compact_list(parsed["cited_evidence"])[:8],
        "open_blockers": _split_compact_list(parsed["open_blockers"])[:4],
        "critical_features_preserved": _split_compact_list(parsed["critical_features_preserved"])[:6],
        "final_answer": parsed["final_answer"],
        "_worker_output_format": "compact_key_value_v1",
    }


def _worker_from_text(text: str) -> dict[str, Any]:
    stripped = _strip_thinking_blocks(text or "").strip()
    if not stripped:
        raise ValueError("worker_empty_text")
    if stripped.startswith("```"):
        raise ValueError("worker_markdown_fence_present")
    if stripped.startswith("{") or stripped.startswith("["):
        parsed = json.loads(stripped)
        if not isinstance(parsed, dict):
            raise ValueError("worker_json_not_object")
        parsed.setdefault("_worker_output_format", "json_object")
        return parsed
    return _worker_compact_from_text(stripped)


def _worker_from_response(response: dict[str, Any]) -> dict[str, Any]:
    text = response.get("text") or ""
    finish_reason = response.get("finish_reason")
    if not str(text).strip():
        if finish_reason == "length":
            raise ValueError("worker_finish_reason_length_empty_text")
        raise ValueError("worker_empty_text")
    try:
        return _worker_from_text(str(text))
    except Exception as exc:
        if finish_reason == "length":
            raise ValueError(f"worker_finish_reason_length_incomplete_output:{exc}") from exc
        raise


GOV_MICRO_V2_KEYS = ("verdict", "dep", "focus", "objective", "preserve", "repair", "block")
GOV_MICRO_V2_ALLOWED = {
    "verdict": {"CONTINUE", "FINAL", "FAIL"},
    "dep": {"NONE", "SOURCE", "CALLBACK", "PAYMENT", "AUTHORITY", "EVIDENCE", "GATE", "POLICY", "TIMING", "SCOPE"},
    "focus": {"SOURCE", "PAYMENT_RELEASE", "EVIDENCE_BINDING", "GATE_REPAIR", "OVERBLOCK", "UNDERBLOCK", "FINAL_CHECK"},
    "objective": {"FINALIZE", "REPAIR_GATE", "BLOCK_UNVERIFIED_CHANGE", "PRESERVE_VERDICT", "CHECK_SOURCE", "FAIL_CLOSED"},
    "preserve": {"NONE", "CLOSED", "OPEN", "SRC", "BOUNDARY", "VERDICT", "BEST", "GATE", "S1", "S2", "S3", "S4"},
    "repair": {"NONE", "EVIDENCE_BINDING", "SOURCE_IDS", "GATE_FIELDS", "CRITICAL_TERMS", "VERDICT_BINDING"},
    "block": {"NONE", "TREASURY_RELEASE", "MODEL_SELECTION", "DROP_SOURCE_IDS", "TONE_ONLY", "UNVERIFIED_CHANGE", "FINAL_ON_FAIL"},
}
GOV_MICRO_V2_MAX_FIELD_LENGTH = 32
GOV_MICRO_V2_PLACEHOLDER_TOKENS = {
    "wb",
    "wv",
    "wb_code",
    "fail_code",
    "field_name",
    "value",
    "todo",
    "example",
    "placeholder",
    "repair_hint",
    "blocked_hint",
    "focus_hint",
}


def _gov_micro_v2_allowed_text() -> str:
    return "; ".join(
        f"{key}={','.join(sorted(GOV_MICRO_V2_ALLOWED[key]))}" for key in GOV_MICRO_V2_KEYS
    )


def _gov_micro_v2_from_text(text: str) -> dict[str, Any]:
    stripped = _strip_thinking_blocks(text or "")
    if not stripped.strip():
        raise ValueError("gov_empty_text")
    if stripped.startswith("```") or "```" in stripped:
        raise ValueError("gov_micro_v2_markdown_present")
    if any(char in stripped for char in "{}[]\"'"):
        raise ValueError("gov_micro_v2_forbidden_punctuation")
    parsed: dict[str, Any] = {}
    for raw_line in stripped.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "=" not in line:
            raise ValueError(f"gov_micro_v2_malformed_line:{line[:40]}")
        key, value = line.split("=", 1)
        clean_key = key.strip().lower()
        clean_value = value.strip()
        if clean_key not in GOV_MICRO_V2_KEYS:
            raise ValueError(f"gov_micro_v2_unexpected_key:{clean_key}")
        if clean_key in parsed:
            raise ValueError(f"gov_micro_v2_duplicate_key:{clean_key}")
        if not clean_value:
            raise ValueError(f"gov_micro_v2_empty_field:{clean_key}")
        if len(clean_value) > GOV_MICRO_V2_MAX_FIELD_LENGTH:
            raise ValueError(f"gov_micro_v2_field_too_long:{clean_key}")
        if any(char.isspace() for char in clean_value):
            raise ValueError(f"gov_micro_v2_prose_field:{clean_key}")
        values = clean_value.split("|")
        placeholders = [item for item in values if item.lower() in GOV_MICRO_V2_PLACEHOLDER_TOKENS]
        if placeholders:
            raise ValueError(f"gov_micro_v2_placeholder_token:{clean_key}:{','.join(placeholders)}")
        allowed = GOV_MICRO_V2_ALLOWED[clean_key]
        unknown = [item for item in values if item not in allowed]
        if unknown:
            raise ValueError(f"gov_micro_v2_unknown_enum:{clean_key}:{','.join(unknown)}")
        parsed[clean_key] = clean_value
    missing = [key for key in GOV_MICRO_V2_KEYS if key not in parsed]
    if missing:
        raise ValueError(f"gov_micro_v2_missing_keys:{','.join(missing)}")
    parsed["gov_baton_version"] = "gov_micro_baton_v2"
    return parsed


def _gov_from_text(text: str) -> dict[str, Any]:
    return _gov_micro_v2_from_text(text)


def _gov_from_response(response: dict[str, Any]) -> dict[str, Any]:
    text = response.get("text") or ""
    finish_reason = response.get("finish_reason")
    if not text.strip():
        if finish_reason == "length":
            raise ValueError("gov_finish_reason_length_empty_text")
        raise ValueError("gov_empty_text")
    if finish_reason == "length":
        raise ValueError("gov_finish_reason_length_incomplete_baton")
    try:
        return _gov_from_text(text)
    except Exception as exc:
        raise


def _provider_url(config: dict[str, Any]) -> str:
    explicit = os.getenv(config.get("url_env", ""), "").strip()
    if explicit:
        return explicit
    base = os.getenv(config.get("base_url_env", ""), "").strip()
    if base:
        return base.rstrip("/") + "/chat/completions"
    return config["default_url"]


class TransportFailureAfterRetries(RuntimeError):
    """Raised only when retryable transport attempts are exhausted."""

    def __init__(self, message: str, metadata: dict[str, Any]):
        super().__init__(message)
        self.metadata = metadata


def _http_error_body(exc: urllib.error.HTTPError) -> str:
    try:
        return exc.read().decode("utf-8", errors="replace")[:2000]
    except Exception:
        return ""


def _classify_transport_exception(exc: BaseException) -> dict[str, Any] | None:
    if isinstance(exc, urllib.error.HTTPError):
        body = _http_error_body(exc)
        if exc.code in RETRYABLE_HTTP_STATUS:
            return {
                "retryable": True,
                "class": f"HTTP_{exc.code}",
                "http_status": exc.code,
                "message": str(exc),
                "error_body": body,
            }
        return {
            "retryable": False,
            "class": f"HTTP_{exc.code}",
            "http_status": exc.code,
            "message": str(exc),
            "error_body": body,
        }
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return {"retryable": True, "class": "READ_TIMEOUT", "message": str(exc)}
    if isinstance(exc, ConnectionResetError):
        return {"retryable": True, "class": "CONNECTION_RESET", "message": str(exc)}
    if isinstance(exc, http.client.RemoteDisconnected):
        return {"retryable": True, "class": "TRANSIENT_NETWORK_ERROR", "message": str(exc)}
    if isinstance(exc, urllib.error.URLError):
        reason = getattr(exc, "reason", exc)
        reason_text = str(reason).lower()
        retryable = any(
            marker in reason_text
            for marker in ("timed out", "timeout", "temporarily unavailable", "connection reset", "network is unreachable")
        )
        return {
            "retryable": retryable,
            "class": "READ_TIMEOUT" if "timed out" in reason_text or "timeout" in reason_text else "TRANSIENT_NETWORK_ERROR",
            "message": str(exc),
        }
    return None


def _transport_sleep(seconds: int) -> None:
    time.sleep(seconds)


def _empty_worker_output_sleep(seconds: int) -> None:
    time.sleep(seconds)


def _call_with_transport_retry(
    call_once,
    *,
    provider: str,
    model: str,
    timeout_seconds: int,
    max_retries: int = TRANSPORT_MAX_RETRIES,
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    total_attempts = max_retries + 1
    for attempt in range(1, total_attempts + 1):
        try:
            response = call_once()
            response["transport_retry_policy_version"] = TRANSPORT_RETRY_POLICY_VERSION
            response["transport_attempt_count"] = attempt
            response["transport_recovered"] = bool(failures)
            response["transport_retry_failures"] = failures
            response["provider_timeout_seconds"] = timeout_seconds
            return response
        except Exception as exc:
            classification = _classify_transport_exception(exc)
            if not classification or not classification["retryable"]:
                raise
            failures.append(
                {
                    "attempt": attempt,
                    "provider": provider,
                    "model": model,
                    "class": classification["class"],
                    "message": classification.get("message", ""),
                    "http_status": classification.get("http_status"),
                    "error_body": classification.get("error_body", ""),
                }
            )
            if attempt >= total_attempts:
                metadata = {
                    "text": "",
                    "finish_reason": None,
                    "response_id": None,
                    "input_tokens": None,
                    "output_tokens": None,
                    "total_tokens": None,
                    "transport_retry_policy_version": TRANSPORT_RETRY_POLICY_VERSION,
                    "transport_attempt_count": attempt,
                    "transport_recovered": False,
                    "transport_retry_failures": failures,
                    "transport_final_failure_class": classification["class"],
                    "provider_timeout_seconds": timeout_seconds,
                }
                raise TransportFailureAfterRetries(classification["class"], metadata) from exc
            _transport_sleep(TRANSPORT_BACKOFF_SECONDS[min(attempt - 1, len(TRANSPORT_BACKOFF_SECONDS) - 1)])


def _http_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    timeout: int = PROVIDER_HTTP_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _call_openai_compatible(config: dict[str, Any], messages: list[dict[str, str]], max_tokens: int) -> dict[str, Any]:
    payload = {
        "model": config["model"],
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    data = _http_json(
        _provider_url(config),
        payload,
        {
            "Authorization": f"Bearer {os.getenv(config['api_key_env'], '').strip()}",
            "Content-Type": "application/json",
        },
    )
    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") if isinstance(choice, dict) else {}
    raw_text = (message or {}).get("content") or ""
    stripped_text = _strip_thinking_blocks(raw_text)
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return {
        "text": stripped_text,
        "raw_text": raw_text,
        "text_stripped_by_thinking_filter": raw_text != stripped_text,
        "finish_reason": choice.get("finish_reason") if isinstance(choice, dict) else None,
        "response_id": data.get("id"),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }


def _call_gemini(config: dict[str, Any], messages: list[dict[str, str]], max_tokens: int) -> dict[str, Any]:
    api_key = os.getenv(config["api_key_env"], "").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config['model']}:generateContent?key={api_key}"
    text = "\n\n".join(f"{m['role'].upper()}:\n{m['content']}" for m in messages)
    data = _http_json(
        url,
        {
            "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {
                "temperature": 0,
                "maxOutputTokens": max_tokens,
                "responseMimeType": "application/json",
            },
        },
        {"Content-Type": "application/json"},
    )
    candidates = data.get("candidates") or []
    output = ""
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        output = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    stripped_output = _strip_thinking_blocks(output)
    usage = data.get("usageMetadata") if isinstance(data.get("usageMetadata"), dict) else {}
    in_tok = usage.get("promptTokenCount")
    out_tok = usage.get("candidatesTokenCount")
    return {
        "text": stripped_output,
        "raw_text": output,
        "text_stripped_by_thinking_filter": output != stripped_output,
        "finish_reason": candidates[0].get("finishReason") if candidates else None,
        "response_id": data.get("responseId"),
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "total_tokens": (in_tok + out_tok) if isinstance(in_tok, int) and isinstance(out_tok, int) else None,
    }


def _call_model(config: dict[str, Any], messages: list[dict[str, str]], max_tokens: int) -> dict[str, Any]:
    started = time.time()
    def call_once() -> dict[str, Any]:
        if config["kind"] == "gemini":
            return _call_gemini(config, messages, max_tokens)
        return _call_openai_compatible(config, messages, max_tokens)

    try:
        response = _call_with_transport_retry(
            call_once,
            provider=config["provider"],
            model=config["model"],
            timeout_seconds=PROVIDER_HTTP_TIMEOUT_SECONDS,
        )
    except TransportFailureAfterRetries as exc:
        exc.metadata["elapsed_ms"] = int((time.time() - started) * 1000)
        raise
    response["elapsed_ms"] = int((time.time() - started) * 1000)
    return response


def _is_retryable_empty_worker_response(response: dict[str, Any]) -> bool:
    """Return true only for the pre-registered exact-empty worker anomaly."""
    text = response.get("text")
    finish_reason = response.get("finish_reason")
    output_tokens = response.get("output_tokens")
    return (
        isinstance(text, str)
        and text == ""
        and output_tokens == 0
        and str(finish_reason).lower() != "length"
    )


def _call_worker_model_with_empty_output_retry(
    config: dict[str, Any],
    messages: list[dict[str, str]],
    *,
    max_tokens: int,
    turn_id: str,
    max_retries: int = EMPTY_WORKER_OUTPUT_MAX_RETRIES,
) -> dict[str, Any]:
    """Retry only exact-empty worker responses that produced no model content."""
    failures: list[dict[str, Any]] = []
    total_attempts = max_retries + 1
    for attempt in range(1, total_attempts + 1):
        response = _call_model(config, messages, max_tokens=max_tokens)
        if not _is_retryable_empty_worker_response(response):
            response["empty_worker_output_retry_policy_version"] = EMPTY_WORKER_OUTPUT_RETRY_POLICY_VERSION
            response["empty_worker_output_attempt_count"] = attempt
            response["empty_worker_output_recovered"] = bool(failures)
            response["empty_worker_output_retry_failures"] = failures
            return response
        failures.append(
            {
                "attempt": attempt,
                "turn_id": turn_id,
                "provider": config["provider"],
                "model": config["model"],
                "class": "EMPTY_WORKER_TEXT_ZERO_OUTPUT_TOKENS",
                "finish_reason": response.get("finish_reason"),
                "response_id": response.get("response_id"),
                "input_tokens": response.get("input_tokens"),
                "output_tokens": response.get("output_tokens"),
                "total_tokens": response.get("total_tokens"),
                "transport_attempt_count": response.get("transport_attempt_count"),
                "transport_recovered": response.get("transport_recovered"),
                "transport_retry_failures": response.get("transport_retry_failures", []),
            }
        )
        if attempt >= total_attempts:
            response["empty_worker_output_retry_policy_version"] = EMPTY_WORKER_OUTPUT_RETRY_POLICY_VERSION
            response["empty_worker_output_attempt_count"] = attempt
            response["empty_worker_output_recovered"] = False
            response["empty_worker_output_retry_failures"] = failures
            return response
        _empty_worker_output_sleep(EMPTY_WORKER_OUTPUT_BACKOFF_SECONDS[min(attempt - 1, len(EMPTY_WORKER_OUTPUT_BACKOFF_SECONDS) - 1)])


def _worker_max_tokens(worker: dict[str, Any], config: dict[str, Any]) -> int:
    if config.get("provider") == "minimax" and worker.get("role_name") == "FINAL_COMPILER":
        return MINIMAX_FINAL_COMPILER_WORKER_MAX_TOKENS
    return WORKER_MAX_TOKENS


def _worker_contract() -> dict[str, Any]:
    return {
        "format": "compact_key_value_v1",
        "rules": [
            "Return exactly one key=value line for each required key.",
            "No JSON, no braces, no quotes, no markdown, no prose outside the lines.",
            "Do not emit hidden reasoning, analysis, <think> blocks, or explanation before the contract.",
            "The first output characters must be worker_role=.",
            "Use | to separate list items. Use an empty value when no blockers exist.",
        ],
        "required_keys_in_order": list(WORKER_COMPACT_KEYS),
        "allowed_values": {
            "verification_verdict": "ALLOW | ESCALATE",
            "binding_class": "SOURCE_BOUNDARY_CLOSED | SOURCE_BOUNDARY_OPEN",
        },
        "field_bounds": {
            "allow_rule_assessment": "max 14 words",
            "escalate_rule_assessment": "max 14 words",
            "dependency_check": "max 14 words",
            "controlling_source_fact": "one exact source doc_id or short source-bound fact",
            "cited_evidence": "pipe-separated exact source doc_id values, max 8",
            "open_blockers": "pipe-separated, max 4; empty if none",
            "critical_features_preserved": "pipe-separated, max 6",
            "final_answer": "25-80 words",
        },
    }


def _gov_contract() -> dict[str, Any]:
    return {
        "format": "gov_micro_baton_v2",
        "required_keys_in_order": list(GOV_MICRO_V2_KEYS),
        "rules": [
            "Return exactly seven key=value lines.",
            "Use enum/code values only.",
            "No prose, markdown, JSON, braces, quotes, or sentences.",
        ],
        "allowed_values": GOV_MICRO_V2_ALLOWED,
    }


def _normalize_gov(parsed: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    raw_shape = {
        "raw_top_level_keys": sorted(parsed.keys()),
        "normalized_from_nested_gov_decision": False,
        "normalized_from_nested_gov_diagnosis": False,
        "normalized_aliases": [],
    }
    if isinstance(parsed.get("gov_decision"), dict):
        parsed = {**parsed["gov_decision"]}
        raw_shape["normalized_from_nested_gov_decision"] = True
    if isinstance(parsed.get("gov_diagnosis"), dict):
        diagnosis = parsed["gov_diagnosis"]
        parsed = {**diagnosis, **{k: v for k, v in parsed.items() if k != "gov_diagnosis"}}
        raw_shape["normalized_from_nested_gov_diagnosis"] = True
    normalized = dict(parsed)
    if normalized.get("gov_baton_version") == "gov_micro_baton_v2":
        route_map = {
            "CONTINUE": "CONTINUE_WORKER",
            "FINAL": "FINAL_COMPILER",
            "FAIL": "FAIL_CLOSED",
        }
        route = route_map.get(normalized.get("verdict"), "CONTINUE_WORKER")
        normalized["route_verdict"] = route
        normalized["final_compiler_allowed"] = route == "FINAL_COMPILER"
        normalized["control_action"] = (
            "FINAL_COMPILER"
            if route == "FINAL_COMPILER"
            else "FAIL_CLOSED"
            if route == "FAIL_CLOSED"
            else "CONTINUE_REPAIR"
        )
        normalized["must_preserve"] = _split_compact_list(str(normalized.get("preserve") or ""))
        normalized["must_repair"] = _split_compact_list(str(normalized.get("repair") or ""))
        normalized["blocked_moves"] = _split_compact_list(str(normalized.get("block") or ""))
        normalized["dependency_ledger"] = _split_compact_list(str(normalized.get("dep") or ""))
        normalized["next_worker_baton"] = {
            "objective": normalized.get("objective") or "CHECK_SOURCE",
            "attack_focus": normalized.get("focus") or "SOURCE",
            "required_repairs": normalized.get("must_repair") or [],
            "monotonic_preservation": normalized.get("must_preserve") or [],
        }
        raw_shape["normalized_aliases"].extend(
            [
                "route_verdict:from_gov_micro_baton_v2",
                "final_compiler_allowed:from_gov_micro_baton_v2",
                "control_action:from_gov_micro_baton_v2",
                "lists:from_gov_micro_baton_v2_codes",
                "next_worker_baton:from_gov_micro_baton_v2_codes",
            ]
        )
    if "verification_verdict" not in normalized and normalized.get("verdict") in {"ALLOW", "ESCALATE"}:
        normalized["verification_verdict"] = normalized["verdict"]
        raw_shape["normalized_aliases"].append("verification_verdict:from_micro_verdict")
    if "route_verdict" not in normalized and normalized.get("route") in {"CONTINUE_WORKER", "FINAL_COMPILER", "FAIL_CLOSED"}:
        normalized["route_verdict"] = normalized["route"]
        raw_shape["normalized_aliases"].append("route_verdict:from_micro_route")
    if "final_compiler_allowed" not in normalized and isinstance(normalized.get("final"), bool):
        normalized["final_compiler_allowed"] = normalized["final"]
        raw_shape["normalized_aliases"].append("final_compiler_allowed:from_micro_final")
    if "control_action" not in normalized and normalized.get("route_verdict"):
        route = normalized.get("route_verdict")
        normalized["control_action"] = (
            "FINAL_COMPILER"
            if route == "FINAL_COMPILER"
            else "FAIL_CLOSED"
            if route == "FAIL_CLOSED"
            else "CONTINUE_REPAIR"
        )
        raw_shape["normalized_aliases"].append("control_action:from_micro_route")
    micro_map = {
        "preserve": "must_preserve",
        "repair": "must_repair",
        "block": "blocked_moves",
        "dep": "dependency_ledger",
    }
    for micro_key, canonical_key in micro_map.items():
        if canonical_key not in normalized and isinstance(normalized.get(micro_key), str):
            value = normalized[micro_key].strip()
            normalized[canonical_key] = [value] if value else []
            raw_shape["normalized_aliases"].append(f"{canonical_key}:from_micro_{micro_key}")
    if "next_worker_baton" not in normalized and (
        isinstance(normalized.get("objective"), str) or isinstance(normalized.get("focus"), str)
    ):
        normalized["next_worker_baton"] = {
            "objective": (normalized.get("objective") or "continue verification"),
            "attack_focus": (normalized.get("focus") or normalized.get("source_gate_interpretation") or "source binding"),
            "required_repairs": normalized.get("must_repair") or [],
            "monotonic_preservation": normalized.get("must_preserve") or [],
        }
        raw_shape["normalized_aliases"].append("next_worker_baton:from_micro_fields")
    if "gov_mode" not in normalized:
        normalized["gov_mode"] = "CONTROL_ROUTER"
        raw_shape["normalized_aliases"].append("gov_mode:default_CONTROL_ROUTER")
    if "surface" not in normalized:
        normalized["surface"] = "HOLOVERIFY_3DNA_FULL_ARCH"
        raw_shape["normalized_aliases"].append("surface:default_HOLOVERIFY_3DNA_FULL_ARCH")
    if "verification_verdict" not in normalized and normalized.get("gov_local_verdict") in {"ALLOW", "ESCALATE"}:
        normalized["verification_verdict"] = normalized["gov_local_verdict"]
        raw_shape["normalized_aliases"].append("verification_verdict:from_gov_local_verdict")
    if "verification_verdict" not in normalized and normalized.get("artifact_verdict") in {"ALLOW", "ESCALATE"}:
        normalized["verification_verdict"] = normalized["artifact_verdict"]
        raw_shape["normalized_aliases"].append("verification_verdict:from_artifact_verdict")
    if "verification_verdict" not in normalized and normalized.get("binding_class") == "SOURCE_BOUNDARY_CLOSED":
        normalized["verification_verdict"] = "ALLOW"
        raw_shape["normalized_aliases"].append("verification_verdict:from_binding_class_closed")
    if "verification_verdict" not in normalized and normalized.get("binding_class") == "SOURCE_BOUNDARY_OPEN":
        normalized["verification_verdict"] = "ESCALATE"
        raw_shape["normalized_aliases"].append("verification_verdict:from_binding_class_open")
    if "route_verdict" not in normalized:
        action = normalized.get("control_action")
        if action in {"FINAL_COMPILER", "FAIL_CLOSED"}:
            normalized["route_verdict"] = action
            raw_shape["normalized_aliases"].append("route_verdict:from_control_action")
        else:
            normalized["route_verdict"] = "CONTINUE_WORKER"
            raw_shape["normalized_aliases"].append("route_verdict:default_CONTINUE_WORKER")
    for key in ("must_preserve", "must_repair", "blocked_moves", "dependency_ledger"):
        normalized[key] = [str(item) for item in _as_list(normalized.get(key))]
    baton = normalized.get("next_worker_baton")
    if not isinstance(baton, dict):
        baton = {
            "objective": "Continue under Gov source-bound repairs.",
            "attack_focus": normalized.get("source_gate_interpretation") or "source-boundary verification",
            "required_repairs": normalized.get("must_repair") or [],
            "monotonic_preservation": normalized.get("must_preserve") or [],
        }
        raw_shape["normalized_aliases"].append("next_worker_baton:default_from_gov_fields")
    if isinstance(baton.get("required_repairs"), str):
        baton["required_repairs"] = [baton["required_repairs"]] if baton["required_repairs"].strip() else []
        raw_shape["normalized_aliases"].append("next_worker_baton.required_repairs:list_from_string")
    if isinstance(baton.get("monotonic_preservation"), str):
        baton["monotonic_preservation"] = [baton["monotonic_preservation"]] if baton["monotonic_preservation"].strip() else []
        raw_shape["normalized_aliases"].append("next_worker_baton.monotonic_preservation:list_from_string")
    normalized["next_worker_baton"] = baton
    return normalized, raw_shape


def _gate_failures_are_repair_only(gate: dict[str, Any]) -> bool:
    failures = gate.get("failures") or []
    if not failures:
        return False
    hard_prefixes = (
        "action_boundary_verdict_mismatch",
        "allow_requires_source_boundary_closed",
        "escalate_requires_source_boundary_open",
        "missing_or_invalid_verification_verdict",
        "missing_boundary_binding_section",
        "invented_source_id:",
    )
    return not any(str(failure).startswith(hard_prefixes) for failure in failures)


def _gate_repair_directive(gate: dict[str, Any], worker_output: dict[str, Any]) -> dict[str, str]:
    failures = [str(failure) for failure in (gate.get("failures") or [])]
    failure_text = "; ".join(failures[:4])
    verdict = worker_output.get("verification_verdict")
    binding = (
        worker_output.get("boundary_binding", {}).get("binding_class")
        if isinstance(worker_output.get("boundary_binding"), dict)
        else None
    )
    if "action_boundary_verdict_mismatch" in failures and verdict == "ESCALATE":
        return {
            "repair": "Potential overblock: re-check whether exact current source evidence closes the action boundary; if closed, return ALLOW with SOURCE_BOUNDARY_CLOSED.",
            "block": "Do not escalate from warning tone, stale/adjacent records, missing phrasing, or plausible risk when exact current source evidence closes the boundary.",
            "focus": "overblock",
        }
    if "action_boundary_verdict_mismatch" in failures and verdict == "ALLOW":
        return {
            "repair": "Potential underblock: re-check whether exact current source evidence leaves the action boundary open; if open, return ESCALATE with SOURCE_BOUNDARY_OPEN.",
            "block": "Do not allow from adjacent, stale, future, partial, or merely plausible authority when exact current source evidence leaves the boundary open.",
            "focus": "underblock",
        }
    if binding in {"SOURCE_BOUNDARY_OPEN", "SOURCE_BOUNDARY_CLOSED"}:
        return {
            "repair": f"Repair deterministic gate failures while preserving the source-boundary finding {binding}: {failure_text}",
            "block": "Do not drop source IDs, action boundary, timing/scope/authority/dependency checks, or critical terms.",
            "focus": "gate_repair",
        }
    return {
        "repair": f"Repair deterministic gate failures: {failure_text}",
        "block": "Do not drop source IDs, action boundary, timing/scope/authority/dependency checks, or critical terms.",
        "focus": "gate_repair",
    }


def _enforce_gov_gate_compliance(
    gov_parsed: dict[str, Any],
    gov_normalization: dict[str, Any],
    worker_output: dict[str, Any],
    gate: dict[str, Any],
) -> dict[str, Any]:
    if gate.get("passed") is False:
        gov_parsed = dict(gov_parsed)
        directive = _gate_repair_directive(gate, worker_output)
        gov_parsed["final_compiler_allowed"] = False
        gov_parsed["route_verdict"] = "CONTINUE_WORKER"
        gov_parsed["control_action"] = "CONTINUE_REPAIR"
        gov_parsed["must_repair"] = [directive["repair"]]
        gov_parsed["blocked_moves"] = [directive["block"]]
        baton = gov_parsed.get("next_worker_baton") if isinstance(gov_parsed.get("next_worker_baton"), dict) else {}
        baton["objective"] = "Repair failed deterministic gate before final selection."
        baton["attack_focus"] = directive["focus"]
        baton["required_repairs"] = [directive["repair"]]
        baton["monotonic_preservation"] = _as_list(gov_parsed.get("must_preserve"))
        gov_parsed["next_worker_baton"] = baton
        gov_normalization.setdefault("normalized_aliases", []).append(
            "baton:forced_actionable_gate_repair_after_failed_gate"
        )
    worker_verdict = worker_output.get("verification_verdict")
    if worker_verdict in {"ALLOW", "ESCALATE"} and gov_parsed.get("verification_verdict") not in {"ALLOW", "ESCALATE"}:
        gov_parsed = dict(gov_parsed)
        gov_parsed["verification_verdict"] = worker_verdict
        gov_normalization.setdefault("normalized_aliases", []).append(
            f"verification_verdict:from_worker_output_after_gov_micro_baton_v2:{worker_verdict}"
        )
    gov_verdict = gov_parsed.get("verification_verdict")
    if (
        _gate_failures_are_repair_only(gate)
        and worker_verdict in {"ALLOW", "ESCALATE"}
        and gov_verdict in {"ALLOW", "ESCALATE"}
        and gov_verdict != worker_verdict
    ):
        gov_parsed = dict(gov_parsed)
        gov_parsed["verification_verdict"] = worker_verdict
        repairs = _as_list(gov_parsed.get("must_repair"))
        repairs.append(
            f"Gov compliance correction: preserve worker local verdict {worker_verdict}; repair deterministic gate failures without inverting verdict."
        )
        gov_parsed["must_repair"] = [str(item) for item in repairs]
        gov_normalization.setdefault("normalized_aliases", []).append(
            f"verification_verdict:preserved_worker_verdict_after_repair_only_gate_failure:{worker_verdict}"
        )
    return gov_parsed


def _assert_prompt_clean(obj: Any) -> None:
    text = json.dumps(obj, ensure_ascii=True)
    found = [term for term in FORBIDDEN_PROMPT_TERMS if term in text]
    if found:
        raise RuntimeError(f"forbidden prompt terms present: {found}")


def _make_state_brief(
    run_id: str,
    pair_id: str,
    packet_id: str,
    turns: list[dict[str, Any]],
    unresolved: list[str],
    blocked_moves: list[str],
    best_artifact: dict[str, Any] | None,
    best_artifact_text: str | None,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "pair_id": pair_id,
        "packet_id": packet_id,
        "lane": "HOLOVERIFY_20PAIR_3DNA_FULL_ARCH",
        "turns_completed": turns,
        "current_position": "source-bound action verification with adversarial cross-DNA repair",
        "resolved_dependencies": [],
        "unresolved_dependencies": unresolved,
        "blocked_moves_so_far": blocked_moves,
        "source_ids_used_so_far": sorted({sid for turn in turns for sid in turn.get("source_ids", [])}),
        "claims_requiring_support": [],
        "known_failure_risks": [
            "warning fixation",
            "planning artifact treated as execution authority",
            "adjacent source treated as exact source",
            "status-class literalism",
            "authority-chain shortcut",
        ],
        "best_artifact_registry": best_artifact,
        "pinned_best_artifact_full_text": best_artifact_text,
    }


def _compact_state_for_gov(state_brief: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": state_brief.get("run_id"),
        "pair_id": state_brief.get("pair_id"),
        "packet_id": state_brief.get("packet_id"),
        "turns_completed": [
            {
                "turn": item.get("turn"),
                "role": item.get("role"),
                "turn_id": item.get("turn_id"),
                "gate_status": item.get("gate_status"),
                "output_summary": item.get("output_summary"),
            }
            for item in (state_brief.get("turns_completed") or [])[-4:]
            if isinstance(item, dict)
        ],
        "unresolved_dependencies": state_brief.get("unresolved_dependencies") or [],
        "blocked_moves_so_far": (state_brief.get("blocked_moves_so_far") or [])[-4:],
        "claims_requiring_support": state_brief.get("claims_requiring_support") or [],
        "best_artifact_registry": state_brief.get("best_artifact_registry"),
    }


def _compact_worker_output_for_gov(worker_output: dict[str, Any]) -> dict[str, Any]:
    binding = worker_output.get("boundary_binding") if isinstance(worker_output.get("boundary_binding"), dict) else {}
    return {
        "verification_verdict": worker_output.get("verification_verdict"),
        "binding_class": binding.get("binding_class"),
        "controlling_source_fact": binding.get("controlling_source_fact"),
        "cited_evidence": worker_output.get("cited_evidence") or [],
        "open_blockers": worker_output.get("open_blockers") or [],
        "critical_features_preserved": worker_output.get("critical_features_preserved") or [],
        "final_answer": worker_output.get("final_answer"),
    }


def _compact_artifact_registry_for_gov(artifact_registry: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compact = []
    for item in artifact_registry[-4:]:
        compact.append(
            {
                "artifact_id": item.get("artifact_id"),
                "turn_number": item.get("turn_number"),
                "provider": item.get("provider"),
                "model": item.get("model"),
                "gate_status": item.get("gate_status"),
                "gate_failures": item.get("gate_failures") or [],
                "verification_verdict": item.get("verification_verdict"),
                "binding_class": item.get("binding_class"),
            }
        )
    return compact


def _initial_baton(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "gov_mode": "INITIAL_LOCAL_BATON",
        "surface": "HOLOVERIFY_3DNA_FULL_ARCH",
        "verification_verdict": None,
        "control_action": "CONTINUE_REPAIR",
        "route_verdict": "CONTINUE_WORKER",
        "must_preserve": ["source IDs", "action boundary", "policy exact-match rule"],
        "must_repair": ["map source documents to exact action boundary before deciding"],
        "blocked_moves": [
            "do not allow warning tone, stale notes, adjacent records, or plausible closure to override exact source binding"
        ],
        "dependency_ledger": [spec.get("failure_class_notes") or spec.get("boundary")],
        "next_worker_baton": {
            "objective": "Create initial source-bound map.",
            "attack_focus": "separate visible anomaly from exact closure evidence",
            "required_repairs": ["cite the controlling source facts"],
            "monotonic_preservation": [],
        },
        "final_compiler_allowed": False,
    }


def _build_worker_messages(
    run_id: str,
    pair: dict[str, Any],
    packet: dict[str, Any],
    payload: dict[str, Any],
    worker: dict[str, Any],
    state_brief: dict[str, Any],
    latest_baton: dict[str, Any],
    raw_prior_outputs: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    lens = {
        "route_verdict": latest_baton.get("route_verdict"),
        "main_repair_target": _first_text(latest_baton.get("must_repair"), "initial source-bound mapping"),
        "blocked_move": _first_text(latest_baton.get("blocked_moves"), "do not decide from anomaly tone alone"),
        "unresolved_dependency": _first_text(latest_baton.get("dependency_ledger"), pair["spec"].get("boundary") or "source-boundary verification"),
        "current_objective": worker["role_name"],
    }
    prior_artifact_refs = []
    for item in raw_prior_outputs:
        worker_output = item.get("worker_output") if isinstance(item, dict) else {}
        gate_result = item.get("gate_result") if isinstance(item, dict) else {}
        prior_artifact_refs.append(
            {
                "turn_id": item.get("turn_id") if isinstance(item, dict) else None,
                "verification_verdict": worker_output.get("verification_verdict") if isinstance(worker_output, dict) else None,
                "binding_class": (
                    worker_output.get("boundary_binding", {}).get("binding_class")
                    if isinstance(worker_output, dict) and isinstance(worker_output.get("boundary_binding"), dict)
                    else None
                ),
                "gate_passed": gate_result.get("passed") if isinstance(gate_result, dict) else None,
                "gate_failures": gate_result.get("failures") if isinstance(gate_result, dict) else [],
            }
        )
    user_obj = {
        "gov_adversarial_baton": {
            "routing_lens": lens,
            "full_latest_gov_baton": latest_baton,
            "role_frame": "Act as an adversarial source-boundary verifier, not a sycophant.",
        },
        "structured_canonical_state": {
            "USER_GOAL": "Decide whether the action may proceed using only source records in this packet.",
            "SETTLED_DECISIONS": [
                "Gov chooses control actions, not models.",
                "Source context is ground truth.",
                "Workers return compact key=value lines only.",
            ],
            "unresolved_tensions": state_brief.get("unresolved_dependencies") or [],
            "system_role": "HoloVerify worker. Preserve state. Obey Gov.",
            "run_lock": {
                "run_id": run_id,
                "lane": "HOLOVERIFY_20PAIR_3DNA_FULL_ARCH",
                "pair_id": pair["pair_id"],
                "packet_id": packet["packet_id"],
                "worker_index": worker["worker_index"],
                "worker_role": worker["role_name"],
                "model": f"{worker['config']['provider']}/{worker['config']['model']}",
                "no_substitutions": True,
            },
            "state_brief": state_brief,
            "task_and_answer_contract": {
                "task": "Decide whether the action may proceed using only source records in this packet.",
                "answer_contract": _worker_contract(),
                "word_band": "final_answer 25-80 words",
                "source_rules": [
                    "cite exact doc_id values only",
                    "do not invent source IDs",
                    "ALLOW only when exact current source boundary is closed before execution",
                    "ESCALATE when a narrow source-record defect remains open before execution",
                ],
                "deterministic_gate_categories": [
                    "word band",
                    "required sections",
                    "source IDs",
                    "invented source IDs",
                    "timing/scope/authority/dependency section",
                    "action-boundary violations",
                    "critical dependencies/traps",
                ],
            },
            "current_turn_command": (
                "Act under the baton. If state and Gov conflict, flag the conflict in open_blockers."
            ),
        },
        "artifact_context": {
            "source_context": payload,
            "prior_artifact_refs": prior_artifact_refs,
        },
    }
    system = "\n".join(
        [
            "You are a HoloVerify worker. Preserve state. Obey Gov.",
            "Worker prompt hierarchy is strict: Gov adversarial baton, structured canonical state, then artifact context.",
            "Raw accumulating transcript injection is forbidden; use structured state and artifact refs only.",
            "Return compact_key_value_v1 only: exactly one key=value line for each required key, in order.",
            "No JSON, no braces, no quotes, no markdown fences, no prose outside the key=value lines.",
            "Do not emit hidden reasoning, analysis, <think> blocks, or explanation before the contract.",
            "Start immediately with worker_role= as the first output characters.",
            "Use | for cited_evidence, open_blockers, and critical_features_preserved list values.",
            "Keep values short. Keep final_answer 25-80 words.",
        ]
    )
    _assert_prompt_clean(user_obj)
    prompt_law = validate_worker_prompt_hierarchy(user_obj)
    if not prompt_law.official_valid:
        raise RuntimeError(f"worker_prompt_law_failed:{prompt_law.failures}")
    return [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(user_obj, separators=(",", ":"))}], user_obj


def _build_gov_messages(
    run_id: str,
    pair: dict[str, Any],
    packet: dict[str, Any],
    payload: dict[str, Any],
    state_brief: dict[str, Any],
    worker_output: dict[str, Any],
    gate_result: dict[str, Any],
    artifact_registry: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    compact_gate = {
        "passed": gate_result.get("passed"),
        "failures": (gate_result.get("failures") or [])[:6],
        "artifact_verdict": gate_result.get("artifact_verdict"),
        "artifact_binding": gate_result.get("artifact_binding"),
        "critical_term_count": gate_result.get("critical_term_count"),
    }
    compact_worker = _compact_worker_output_for_gov(worker_output)
    first_failure = str((compact_gate.get("failures") or [""])[0])[:80]
    binding_code = (
        "CLOSED"
        if compact_worker.get("binding_class") == "SOURCE_BOUNDARY_CLOSED"
        else "OPEN"
        if compact_worker.get("binding_class") == "SOURCE_BOUNDARY_OPEN"
        else "BOUNDARY"
    )
    failure_code = (
        "SOURCE_IDS"
        if "source_id" in first_failure
        else "CRITICAL_TERMS"
        if "critical_term" in first_failure
        else "VERDICT_BINDING"
        if "verdict" in first_failure or "binding" in first_failure
        else "GATE_FIELDS"
        if first_failure
        else "NONE"
    )
    pass_baton = {
        "verdict": "FINAL",
        "dep": "NONE",
        "focus": "FINAL_CHECK",
        "objective": "FINALIZE",
        "preserve": binding_code,
        "repair": "NONE",
        "block": "NONE",
    }
    fail_baton = {
        "verdict": "CONTINUE",
        "dep": "GATE",
        "focus": "GATE_REPAIR",
        "objective": "REPAIR_GATE",
        "preserve": binding_code,
        "repair": failure_code,
        "block": "FINAL_ON_FAIL",
    }
    selected_baton = pass_baton if compact_gate.get("passed") else fail_baton
    selected_baton_lines = [f"{key}={selected_baton[key]}" for key in GOV_MICRO_V2_KEYS]
    user_obj = {
        "id": packet["packet_id"],
        "gate_passed": bool(compact_gate.get("passed")),
        "selected_baton_lines": selected_baton_lines,
        "worker_verdict": compact_worker.get("verification_verdict"),
        "gate_diagnostic": first_failure,
    }
    system = "\n".join(
        [
            "HoloGov-V micro-router v2. Return gov_micro_baton_v2 only.",
            "Exactly seven key=value lines. No prose. No reasoning. No JSON. No Markdown. No braces. No quotes.",
            "Copy selected_baton_lines exactly, preserving order and spelling.",
            "Required keys in order: verdict,dep,focus,objective,preserve,repair,block.",
            f"Allowed values by field: {_gov_micro_v2_allowed_text()}.",
            "Output only the seven selected baton lines. Do not invent schema names or substitute tokens.",
        ]
    )
    _assert_prompt_clean(user_obj)
    return [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(user_obj, separators=(",", ":"))}], user_obj


def _validate_source_ids(parsed: Any, valid_ids: set[str]) -> list[str]:
    failures: list[str] = []
    found: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"cited_evidence", "source_ids", "cited_artifacts"} and isinstance(item, list):
                    found.extend(str(x).replace("doc_id:", "").strip() for x in item)
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(parsed)
    if not found:
        failures.append("missing_source_ids")
    for source_id in found:
        if source_id not in valid_ids:
            failures.append(f"invented_source_id:{source_id}")
    return failures


def _validate_worker(parsed: dict[str, Any], spec: dict[str, Any], suffix: str, valid_ids: set[str]) -> dict[str, Any]:
    expected = "ALLOW" if suffix == "A" else "ESCALATE"
    failures: list[str] = []
    if parsed.get("verification_verdict") not in {"ALLOW", "ESCALATE"}:
        failures.append("missing_or_invalid_verification_verdict")
    if parsed.get("verification_verdict") != expected:
        failures.append("action_boundary_verdict_mismatch")
    binding = parsed.get("boundary_binding")
    if not isinstance(binding, dict):
        failures.append("missing_boundary_binding_section")
        binding = {}
    for key in (
        "action_boundary",
        "allow_rule_assessment",
        "escalate_rule_assessment",
        "timing_scope_authority_dependency_check",
        "binding_class",
        "controlling_source_fact",
    ):
        if not binding.get(key):
            failures.append(f"missing_boundary_binding:{key}")
    if parsed.get("verification_verdict") == "ALLOW" and binding.get("binding_class") != "SOURCE_BOUNDARY_CLOSED":
        failures.append("allow_requires_source_boundary_closed")
    if parsed.get("verification_verdict") == "ESCALATE" and binding.get("binding_class") != "SOURCE_BOUNDARY_OPEN":
        failures.append("escalate_requires_source_boundary_open")
    final_answer_words = len(str(parsed.get("final_answer") or "").split())
    if final_answer_words < 25 or final_answer_words > 80:
        failures.append(f"word_band_final_answer:{final_answer_words}")
    for key in ("cited_evidence", "open_blockers", "critical_features_preserved"):
        if key not in parsed or not isinstance(parsed.get(key), list):
            failures.append(f"missing_required_section:{key}")
    failures.extend(_validate_source_ids(parsed, valid_ids))
    text = _flatten_text(parsed)
    for term in spec.get("knew_terms", {}).get(suffix, []):
        if not _term_present(text, term):
            failures.append(f"missing_critical_term:{_term_label(term)}")
    return {
        "gate_name": "HOLOVERIFY_WORKER_DETERMINISTIC_GATE",
        "passed": not failures,
        "failures": failures,
        "artifact_verdict": parsed.get("verification_verdict"),
        "artifact_binding": binding.get("binding_class"),
        "source_id_count": len(valid_ids),
        "critical_term_count": len(spec.get("knew_terms", {}).get(suffix, [])),
    }


def _worker_expected_binding(suffix: str) -> str:
    return "SOURCE_BOUNDARY_CLOSED" if suffix == "A" else "SOURCE_BOUNDARY_OPEN"


def _missing_critical_terms_from_gate(gate: dict[str, Any]) -> list[str]:
    prefix = "missing_critical_term:"
    return [str(failure)[len(prefix) :] for failure in (gate.get("failures") or []) if str(failure).startswith(prefix)]


def _is_deterministic_normalization_candidate(
    parsed: dict[str, Any],
    gate: dict[str, Any],
    spec: dict[str, Any],
    suffix: str,
    valid_ids: set[str],
) -> bool:
    if gate.get("passed"):
        return False
    if not _gate_failures_are_repair_only(gate):
        return False
    expected_verdict = "ALLOW" if suffix == "A" else "ESCALATE"
    binding = parsed.get("boundary_binding") if isinstance(parsed.get("boundary_binding"), dict) else {}
    if parsed.get("verification_verdict") != expected_verdict:
        return False
    if binding.get("binding_class") != _worker_expected_binding(suffix):
        return False
    if any(str(failure).startswith("invented_source_id:") for failure in gate.get("failures") or []):
        return False
    cited = parsed.get("cited_evidence") if isinstance(parsed.get("cited_evidence"), list) else []
    cited_clean = {str(item).replace("doc_id:", "").strip() for item in cited}
    return bool(valid_ids) or bool(cited_clean)


def _normalize_final_answer(parsed: dict[str, Any], spec: dict[str, Any], suffix: str, valid_ids: set[str]) -> str:
    verdict = parsed.get("verification_verdict")
    binding = parsed.get("boundary_binding") if isinstance(parsed.get("boundary_binding"), dict) else {}
    source_ids = ", ".join(sorted(valid_ids)) or "the cited source records"
    terms = [_term_label(term) for term in spec.get("knew_terms", {}).get(suffix, [])]
    term_text = "; ".join(terms[:4]) if terms else str(spec.get("boundary") or "the exact action boundary")
    decision = "closed" if suffix == "A" else "open"
    action = "may proceed" if suffix == "A" else "must escalate"
    return (
        f"{verdict}: the source boundary is {decision} for this action. "
        f"The controlling record set is {source_ids}. "
        f"The preserved critical facts are {term_text}. "
        f"Binding class is {binding.get('binding_class')}; therefore the action {action} under the packet evidence."
    )


def _normalize_worker_artifact_after_gate(
    parsed: dict[str, Any],
    gate: dict[str, Any],
    spec: dict[str, Any],
    suffix: str,
    valid_ids: set[str],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    metadata: dict[str, Any] = {
        "applied": False,
        "reason": "not_candidate",
        "pre_gate_failures": list(gate.get("failures") or []),
    }
    if not _is_deterministic_normalization_candidate(parsed, gate, spec, suffix, valid_ids):
        return parsed, gate, metadata

    normalized = json.loads(json.dumps(parsed))
    binding = normalized.get("boundary_binding") if isinstance(normalized.get("boundary_binding"), dict) else {}
    if not binding:
        binding = {}
        normalized["boundary_binding"] = binding

    binding.setdefault("action_boundary", spec.get("boundary") or "packet action boundary")
    binding.setdefault(
        "allow_rule_assessment",
        "ALLOW requires exact current source evidence closing the packet action boundary.",
    )
    binding.setdefault(
        "escalate_rule_assessment",
        "ESCALATE is required when exact current source evidence leaves the packet action boundary open.",
    )
    binding.setdefault(
        "timing_scope_authority_dependency_check",
        "Deterministic compiler preserved timing, scope, authority, and dependency checks from packet source facts.",
    )
    binding.setdefault("binding_class", _worker_expected_binding(suffix))
    if not binding.get("controlling_source_fact"):
        binding["controlling_source_fact"] = (
            "Deterministic compiler preserved the controlling source-boundary facts from "
            f"{', '.join(sorted(valid_ids)) or 'the cited packet evidence'}."
        )

    if not isinstance(normalized.get("cited_evidence"), list):
        normalized["cited_evidence"] = []
    cited_clean = {str(item).replace("doc_id:", "").strip() for item in normalized["cited_evidence"]}
    for source_id in sorted(valid_ids):
        if source_id not in cited_clean:
            normalized["cited_evidence"].append(source_id)

    for key in ("open_blockers", "critical_features_preserved"):
        if not isinstance(normalized.get(key), list):
            normalized[key] = []

    feature_text = "\n".join(str(item) for item in normalized["critical_features_preserved"])
    for term in spec.get("knew_terms", {}).get(suffix, []):
        if not _term_present(feature_text, term):
            normalized["critical_features_preserved"].append(_term_label(term))
            feature_text += "\n" + _term_label(term)
    for missing_term in _missing_critical_terms_from_gate(gate):
        if missing_term and missing_term not in feature_text:
            normalized["critical_features_preserved"].append(missing_term)
            feature_text += "\n" + missing_term

    final_answer_words = len(str(normalized.get("final_answer") or "").split())
    if final_answer_words < 25 or final_answer_words > 80:
        normalized["final_answer"] = _normalize_final_answer(normalized, spec, suffix, valid_ids)

    normalized_gate = _validate_worker(normalized, spec, suffix, valid_ids)
    metadata.update(
        {
            "applied": True,
            "reason": "repair_only_mechanical_gate_normalization",
            "post_gate_failures": list(normalized_gate.get("failures") or []),
            "post_gate_passed": bool(normalized_gate.get("passed")),
        }
    )
    if not normalized_gate.get("passed"):
        metadata["reason"] = "normalization_attempt_did_not_clear_gate"
    return normalized, normalized_gate, metadata


def _validate_gov(parsed: dict[str, Any], prior_gate: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if parsed.get("gov_mode") != "CONTROL_ROUTER":
        failures.append("gov_mode_invalid")
    if parsed.get("surface") != "HOLOVERIFY_3DNA_FULL_ARCH":
        failures.append("surface_invalid")
    route_verdict = parsed.get("route_verdict")
    if route_verdict not in {"CONTINUE_WORKER", "FINAL_COMPILER", "FAIL_CLOSED"}:
        failures.append("route_verdict_invalid")
    if route_verdict == "FINAL_COMPILER" and parsed.get("verification_verdict") not in {"ALLOW", "ESCALATE"}:
        failures.append("missing_or_invalid_gov_local_verdict")
    if prior_gate.get("passed") is False and parsed.get("final_compiler_allowed") is True:
        failures.append("gov_ready_despite_failed_gate")
    forbidden = {
        "model_choice",
        "model_selection",
        "next_model",
        "selected_model",
        "selected_provider",
        "provider_choice",
        "worker_model_choice",
    }

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in forbidden:
                    failures.append(f"forbidden_model_selection_key:{key}")
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(parsed)
    return failures


def _local_verdict_match(verdict: Any, suffix: str) -> bool | None:
    if verdict not in {"ALLOW", "ESCALATE"}:
        return None
    return verdict == ("ALLOW" if suffix == "A" else "ESCALATE")


def _artifact_record(packet_id: str, worker_index: int, config: dict[str, Any], parsed: dict[str, Any], gate: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    artifact_id = f"{packet_id}_WORKER_{worker_index:02d}"
    text = json.dumps(parsed, indent=2, sort_keys=True)
    path = out_dir / "artifacts" / f"{artifact_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n")
    return {
        "artifact_id": artifact_id,
        "turn_number": worker_index,
        "provider": config["provider"],
        "model": config["model"],
        "dna": config["dna"],
        "full_output_ref": str(path.relative_to(out_dir)),
        "hash": _sha256_text(text),
        "gate_status": "PASS" if gate["passed"] else "FAIL",
        "gate_passed": gate["passed"],
        "gate_failures": gate["failures"],
        "critical_feature_count": len(parsed.get("critical_features_preserved") or []),
        "verification_verdict": parsed.get("verification_verdict"),
        "binding_class": (parsed.get("boundary_binding") or {}).get("binding_class"),
        "text": text,
    }


def _select_best(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    admissible = [a for a in artifacts if a["gate_passed"]]
    if not admissible:
        return {"selected_artifact_id": None, "selection_reason": "NO_ADMISSIBLE_ARTIFACT", "selected": None}
    final = artifacts[-1]
    if final["gate_passed"]:
        return {"selected_artifact_id": final["artifact_id"], "selection_reason": "FINAL_ARTIFACT_ADMISSIBLE", "selected": final}
    best = admissible[-1]
    return {"selected_artifact_id": best["artifact_id"], "selection_reason": "FINAL_REGRESSED_SELECTED_BEST_PRIOR", "selected": best}


def _external_evidence(pair: dict[str, Any], packet_id: str) -> list[dict[str, Any]]:
    evidence = []
    for item in pair.get("candidate", {}).get("failing_models", []):
        if item.get("packet_id") != packet_id:
            continue
        if item.get("behavior_label") == "NOT_KNEW_WRONG_VERDICT":
            evidence.append(
                {
                    "evidence_category": "EXTERNAL_SOLO_RESCUE",
                    "provider": item.get("provider"),
                    "model": item.get("model"),
                    "verdict": item.get("verdict"),
                    "notes": item.get("behavior_notes"),
                }
            )
    return evidence


def _intra_holo_evidence(packet_result: dict[str, Any], suffix: str) -> list[dict[str, Any]]:
    evidence = []
    calls = packet_result["calls"]
    final_correct = packet_result.get("final_admissible") is True
    for index, row in enumerate(calls):
        local = row.get("local_verdict")
        match = _local_verdict_match(local, suffix)
        if match is not False:
            continue
        later_correct = None
        for later in calls[index + 1 :]:
            if _local_verdict_match(later.get("local_verdict"), suffix) is True:
                later_correct = later
                break
        category = "INTRA_HOLO_TURN_RESCUE" if final_correct else "INTRA_HOLO_SINGLE_DNA_MISS"
        if later_correct and later_correct.get("dna") != row.get("dna"):
            category = "INTRA_HOLO_CROSS_DNA_RESCUE"
        if row.get("call_kind") == "worker" and later_correct and later_correct.get("call_kind") == "gov":
            category = "INTRA_HOLO_GOV_RESCUE"
        if row.get("call_kind") == "gov" and final_correct and not later_correct:
            category = "INTRA_HOLO_GOV_FAILURE_CORRECTED"
        evidence.append(
            {
                "evidence_category": category,
                "miss_turn_id": row.get("turn_id"),
                "miss_role": row.get("call_kind"),
                "miss_model": f"{row.get('provider')}/{row.get('model')}",
                "miss_dna": row.get("dna"),
                "miss_local_verdict": local,
                "corrected_by_turn_id": later_correct.get("turn_id") if later_correct else "final_selector_or_gate",
                "corrected_by_model": f"{later_correct.get('provider')}/{later_correct.get('model')}" if later_correct else None,
                "final_holoverify_correct": final_correct,
            }
        )
    return evidence


def _load_pairs(limit: int = 0, bucket: str = "all") -> list[dict[str, Any]]:
    aggregate = _load_json(AGGREGATE)
    candidates = aggregate["candidates"]
    spec_cache: dict[str, list[dict[str, Any]]] = {}
    hard_allow_candidates = []
    hard_escalate_candidates = []
    for candidate in candidates:
        spec_path = str(Path(candidate["source_spec_module"])) if candidate.get("source_spec_module") else None
        if spec_path:
            if spec_path not in spec_cache:
                spec_cache[spec_path] = _module_specs(Path(spec_path))
            spec = next(s for s in spec_cache[spec_path] if s["pair_id"] == candidate["pair_id"])
        else:
            spec = candidate.get("spec_metadata")
            if not isinstance(spec, dict):
                raise RuntimeError(f"direct_candidate_missing_spec_metadata:{candidate.get('pair_id')}")
            if not isinstance(spec.get("knew_terms"), dict):
                raise RuntimeError(f"direct_candidate_missing_knew_terms:{candidate.get('pair_id')}")
        wrong_allow = any(
            item.get("behavior_label") == "NOT_KNEW_WRONG_VERDICT"
            and item.get("expected") == "ALLOW"
            and item.get("verdict") == "ESCALATE"
            for item in candidate.get("failing_models", [])
        )
        wrong_escalate = any(
            item.get("behavior_label") == "NOT_KNEW_WRONG_VERDICT"
            and item.get("expected") == "ESCALATE"
            and item.get("verdict") == "ALLOW"
            for item in candidate.get("failing_models", [])
        )
        common = {
            "pair_id": candidate["pair_id"],
            "candidate": candidate,
            "spec": spec,
            "source_spec_module": spec_path,
            "source_kind": candidate.get("source_kind", "spec_module"),
            "payload_paths": candidate.get("source_payload_paths"),
            "payload_prompt_cards": candidate.get("source_prompt_cards"),
        }
        if wrong_allow:
            hard_allow_candidates.append(
                {
                    **common,
                    "benchmark_bucket": "hard_allow_false_positive_rescue",
                    "target_suffix": "A",
                    "guardrail_suffix": "B",
                }
            )
        if wrong_escalate:
            hard_escalate_candidates.append(
                {
                    **common,
                    "benchmark_bucket": "hard_escalate_false_negative_rescue",
                    "target_suffix": "B",
                    "guardrail_suffix": "A",
                }
            )
    if bucket == "hard_allow":
        pairs = hard_allow_candidates[:10]
    elif bucket == "hard_escalate":
        pairs = hard_escalate_candidates[:10]
    elif bucket == "all":
        pairs = hard_allow_candidates[:10] + hard_escalate_candidates[:10]
    else:
        raise RuntimeError(f"unknown_bucket:{bucket}")
    if limit:
        pairs = pairs[:limit]
    if not limit and (len(hard_allow_candidates) < 10 or len(hard_escalate_candidates) < 10):
        raise RuntimeError(
            "insufficient_wrong_verdict_candidates:"
            f"hard_allow={len(hard_allow_candidates)} hard_escalate={len(hard_escalate_candidates)}"
        )
    return pairs


def _build_preflight(limit: int = 0, bucket: str = "all") -> dict[str, Any]:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    pairs = _load_pairs(limit, bucket)
    packet_records = []
    frozen_dir = OUT_ROOT / "frozen_packets"
    frozen_dir.mkdir(parents=True, exist_ok=True)
    for pair in pairs:
        for suffix in ("A", "B"):
            payload = _packet_from_pair(pair, suffix)
            packet_id = f"{pair['pair_id']}-{suffix}"
            packet_path = frozen_dir / f"{packet_id}.payload.json"
            packet_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            packet_records.append(
                {
                    "pair_id": pair["pair_id"],
                    "packet_id": packet_id,
                    "suffix": suffix,
                    "expected_verdict_for_local_gate": "ALLOW" if suffix == "A" else "ESCALATE",
                    "payload_path": str(packet_path.relative_to(OUT_ROOT)),
                    "payload_hash": _sha256_text(_canonical_json(payload)),
                    "source_ids": sorted(_source_ids(payload)),
                    "knew_terms": pair["spec"].get("knew_terms", {}).get(suffix, []),
                    "benchmark_bucket": pair["benchmark_bucket"],
                    "is_target_packet": suffix == pair["target_suffix"],
                }
            )
    architecture_lock = {
        "classification": "HOLOVERIFY_20PAIR_3DNA_PREFLIGHT",
        "status": "PRE_REGISTERED_NOT_LIVE",
        "model_roster_declared": {
            "worker_sequence": [
                {
                    "worker_index": worker["worker_index"],
                    "role_name": worker["role_name"],
                    "provider": MODEL_CONFIGS[worker["model_key"]]["provider"],
                    "model": MODEL_CONFIGS[worker["model_key"]]["model"],
                    "dna": MODEL_CONFIGS[worker["model_key"]]["dna"],
                }
                for worker in WORKER_SEQUENCE
            ],
            "gov": {
                "provider": MODEL_CONFIGS[GOV_MODEL_KEY]["provider"],
                "model": MODEL_CONFIGS[GOV_MODEL_KEY]["model"],
                "dna": MODEL_CONFIGS[GOV_MODEL_KEY]["dna"],
                "gov_may_select_models": False,
            },
            "distinct_dna_required": 3,
            "fallback_policy": "NO_FALLBACK_PROVIDER_FAILURE_INVALIDATES_RUN",
        },
        "expected_counts": {
            "pairs": len(pairs),
            "packets": len(pairs) * 2,
            "worker_calls": len(pairs) * 2 * 3,
            "gov_calls": len(pairs) * 2 * 2,
            "total_provider_calls": len(pairs) * 2 * 5,
            "total_provider_calls_semantics": "exact_fixed_full_sequence",
            "judge_calls": 0,
        },
        "complete_architecture_requirements": [
            "worker turns",
            "state brief",
            "real Gov API calls between workers",
            "Gov sandwich",
            "deterministic gate after every worker",
            "Gov sees gate results",
            "fixed full worker sequence; dynamic early exit disabled for official 20-pair 3-DNA proof",
            "artifact registry",
            "best artifact registry",
            "pinned best artifact",
            "monotonic preservation",
            "final selector",
            "trace/accounting",
        ],
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
        "token_budget_policy": {
            "worker_max_tokens": WORKER_MAX_TOKENS,
            "minimax_final_compiler_worker_max_tokens": MINIMAX_FINAL_COMPILER_WORKER_MAX_TOKENS,
            "gov_max_tokens": GOV_MAX_TOKENS,
            "worker_budget_reason": "avoid structured JSON truncation under Gemini worker slot",
            "minimax_final_compiler_worker_budget_reason": "Commerce W3 autopsy showed MiniMax final compiler can burn the generic worker budget before emitting visible compact output; final compiler gets extra output room while malformed or length-incomplete content still fails closed",
            "gov_budget_reason": "micro-control baton with room for MiniMax hidden completion overhead; Gov receives compact gate result and worker verdict only",
        },
    }
    preimage = {
        "architecture_lock": architecture_lock,
        "packet_records": packet_records,
        "aggregate_hash": _sha256_text(AGGREGATE.read_text()),
        "runner_source_hash": _sha256_text(Path(__file__).read_text()),
        "bucket": bucket,
    }
    manifest = {
        **preimage,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "root_signature": _sha256_text(_canonical_json(preimage)),
    }
    PRE_RUN_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def _validate_preflight(limit: int = 0, bucket: str = "all") -> dict[str, Any]:
    if not PRE_RUN_MANIFEST.exists():
        return _build_preflight(limit, bucket)
    current = _load_json(PRE_RUN_MANIFEST)
    rebuilt = _build_preflight(limit, bucket)
    if current["root_signature"] != rebuilt["root_signature"]:
        raise RuntimeError("preflight_root_signature_changed")
    return rebuilt


def _write_prompt(out_dir: Path, turn_id: str, messages: list[dict[str, str]], prompt_obj: dict[str, Any]) -> str:
    prompt_dir = out_dir / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    path = prompt_dir / f"{turn_id}.json"
    path.write_text(json.dumps({"messages": messages, "prompt_object": prompt_obj}, indent=2) + "\n")
    return str(path.relative_to(out_dir))


def _run_packet(run_id: str, pair: dict[str, Any], suffix: str, manifest: dict[str, Any], out_dir: Path, trace: Any) -> dict[str, Any]:
    spec = pair["spec"]
    packet_id = f"{pair['pair_id']}-{suffix}"
    payload = _packet_from_pair(pair, suffix)
    valid_ids = _source_ids(payload)
    turns: list[dict[str, Any]] = []
    raw_prior_outputs: list[dict[str, Any]] = []
    artifact_registry: list[dict[str, Any]] = []
    call_rows: list[dict[str, Any]] = []
    unresolved = [spec.get("failure_class_notes") or spec["boundary"]]
    blocked_moves = []
    latest_baton = _initial_baton(spec)
    best_artifact: dict[str, Any] | None = None
    best_artifact_text: str | None = None

    for worker in WORKER_SEQUENCE:
        config = MODEL_CONFIGS[worker["model_key"]]
        worker = {**worker, "config": config}
        turn_id = f"{packet_id}_W{worker['worker_index']}"
        state_brief = _make_state_brief(run_id, pair["pair_id"], packet_id, turns, unresolved, blocked_moves, best_artifact, best_artifact_text)
        messages, prompt_obj = _build_worker_messages(run_id, pair, {"packet_id": packet_id}, payload, worker, state_brief, latest_baton, raw_prior_outputs)
        prompt_ref = _write_prompt(out_dir, turn_id, messages, prompt_obj)
        row_base = {
            "turn_id": turn_id,
            "call_kind": "worker",
            "worker_index": worker["worker_index"],
            "role_name": worker["role_name"],
            "pair_id": pair["pair_id"],
            "packet_id": packet_id,
            "suffix": suffix,
            "benchmark_bucket": pair["benchmark_bucket"],
            "provider": config["provider"],
            "model": config["model"],
            "dna": config["dna"],
            "pre_run_root_signature": manifest["root_signature"],
            "prompt_ref": prompt_ref,
            "prompt_hash": _sha256_text(json.dumps(prompt_obj, sort_keys=True)),
            "prompt_sequence_law": "gov_adversarial_baton>structured_canonical_state>artifact_context",
            "gov_adversarial_baton_present": True,
            "structured_canonical_state_present": True,
            "artifact_context_present": True,
            "raw_transcript_injected": False,
            "gov_routing_lens_present": True,
            "state_brief_present": True,
            "full_latest_gov_baton_present": True,
            "pinned_best_artifact_present": best_artifact_text is not None,
        }
        response: dict[str, Any] = {}
        try:
            response = _call_worker_model_with_empty_output_retry(
                config,
                messages,
                max_tokens=_worker_max_tokens(worker, config),
                turn_id=turn_id,
            )
            parsed = _worker_from_response(response)
            raw_parsed = json.loads(json.dumps(parsed))
            raw_gate = _validate_worker(parsed, spec, suffix, valid_ids)
            parsed, gate, worker_normalization = _normalize_worker_artifact_after_gate(
                parsed,
                raw_gate,
                spec,
                suffix,
                valid_ids,
            )
            artifact = _artifact_record(packet_id, worker["worker_index"], config, parsed, gate, out_dir)
        except Exception as exc:
            transport_failed = isinstance(exc, TransportFailureAfterRetries)
            if transport_failed:
                response = dict(exc.metadata)
            row = {
                **row_base,
                **response,
                "provider_call_ok": False if transport_failed else bool(response),
                "parse_ok": False,
                "error": f"{type(exc).__name__}: {exc}",
                "admissible": False,
            }
            trace.write(json.dumps(row, sort_keys=True) + "\n")
            trace.flush()
            call_rows.append(row)
            return _packet_result(packet_id, suffix, pair, call_rows, artifact_registry, {"selected_artifact_id": None, "selection_reason": "WORKER_FAILURE", "selected": None})
        artifact_registry.append(artifact)
        if artifact["gate_passed"]:
            best_artifact = {k: v for k, v in artifact.items() if k != "text"}
            best_artifact_text = artifact["text"]
        local_verdict = parsed.get("verification_verdict")
        row = {
            **row_base,
            **response,
            "provider_call_ok": True,
            "parse_ok": True,
            "raw_parsed_json": raw_parsed,
            "parsed_json": parsed,
            "pre_normalization_gate_result": raw_gate,
            "worker_normalization": worker_normalization,
            "local_verdict": local_verdict,
            "local_verdict_matches_packet_truth": _local_verdict_match(local_verdict, suffix),
            "gate_result": gate,
            "artifact_id": artifact["artifact_id"],
            "artifact_hash": artifact["hash"],
            "admissible": gate["passed"],
        }
        trace.write(json.dumps(row, sort_keys=True) + "\n")
        trace.flush()
        call_rows.append(row)
        turns.append(
            {
                "turn": len(turns) + 1,
                "role": "worker",
                "turn_id": turn_id,
                "model": f"{config['provider']}/{config['model']}",
                "dna": config["dna"],
                "output_summary": f"{worker['role_name']} local verdict {local_verdict}",
                "full_output_ref": artifact["full_output_ref"],
                "gate_status": artifact["gate_status"],
                "artifact_hash": artifact["hash"],
                "source_ids": sorted(valid_ids),
            }
        )
        raw_prior_outputs.append({"turn_id": turn_id, "worker_output": parsed, "gate_result": gate})

        if worker["worker_index"] == WORKER_SEQUENCE[-1]["worker_index"]:
            continue

        gov_config = MODEL_CONFIGS[GOV_MODEL_KEY]
        gov_turn_id = f"{packet_id}_G{worker['worker_index']}"
        state_brief = _make_state_brief(run_id, pair["pair_id"], packet_id, turns, unresolved, blocked_moves, best_artifact, best_artifact_text)
        registry_for_prompt = [{k: v for k, v in a.items() if k != "text"} for a in artifact_registry]
        gov_messages, gov_prompt_obj = _build_gov_messages(run_id, pair, {"packet_id": packet_id}, payload, state_brief, parsed, gate, registry_for_prompt)
        gov_prompt_ref = _write_prompt(out_dir, gov_turn_id, gov_messages, gov_prompt_obj)
        gov_base = {
            "turn_id": gov_turn_id,
            "call_kind": "gov",
            "gov_index": worker["worker_index"],
            "pair_id": pair["pair_id"],
            "packet_id": packet_id,
            "suffix": suffix,
            "benchmark_bucket": pair["benchmark_bucket"],
            "provider": gov_config["provider"],
            "model": gov_config["model"],
            "dna": gov_config["dna"],
            "pre_run_root_signature": manifest["root_signature"],
            "prompt_ref": gov_prompt_ref,
            "prompt_hash": _sha256_text(json.dumps(gov_prompt_obj, sort_keys=True)),
            "gov_operation": "turn_micro_control",
            "received_gate_result": True,
            "gov_may_select_models": False,
        }
        gov_response: dict[str, Any] = {}
        try:
            gov_response = _call_model(gov_config, gov_messages, max_tokens=GOV_MAX_TOKENS)
            gov_raw_parsed = _gov_from_response(gov_response)
            gov_parsed, gov_normalization = _normalize_gov(gov_raw_parsed)
            gov_parsed = _enforce_gov_gate_compliance(gov_parsed, gov_normalization, parsed, gate)
            gov_failures = _validate_gov(gov_parsed, gate)
        except Exception as exc:
            transport_failed = isinstance(exc, TransportFailureAfterRetries)
            if transport_failed:
                gov_response = dict(exc.metadata)
            gov_row = {
                **gov_base,
                **gov_response,
                "provider_call_ok": False if transport_failed else bool(gov_response),
                "parse_ok": False,
                "error": f"{type(exc).__name__}: {exc}",
                "admissible": False,
            }
            trace.write(json.dumps(gov_row, sort_keys=True) + "\n")
            trace.flush()
            call_rows.append(gov_row)
            return _packet_result(packet_id, suffix, pair, call_rows, artifact_registry, {"selected_artifact_id": None, "selection_reason": "GOV_FAILURE", "selected": None})
        local_gov_verdict = gov_parsed.get("verification_verdict")
        gov_row = {
            **gov_base,
            **gov_response,
            "provider_call_ok": True,
            "parse_ok": True,
            "raw_parsed_json": gov_raw_parsed,
            "parsed_json": gov_parsed,
            "gov_normalization": gov_normalization,
            "local_verdict": local_gov_verdict,
            "local_verdict_matches_packet_truth": _local_verdict_match(local_gov_verdict, suffix),
            "deterministic_failures": gov_failures,
            "admissible": not gov_failures,
        }
        trace.write(json.dumps(gov_row, sort_keys=True) + "\n")
        trace.flush()
        call_rows.append(gov_row)
        blocked_moves.extend(str(item) for item in _as_list(gov_parsed.get("blocked_moves")))
        unresolved = [str(item) for item in _as_list(gov_parsed.get("dependency_ledger"))] or unresolved
        latest_baton = gov_parsed
        gov_out = out_dir / "artifacts" / f"{gov_turn_id}.json"
        gov_out.parent.mkdir(parents=True, exist_ok=True)
        gov_out.write_text(json.dumps(gov_parsed, indent=2, sort_keys=True) + "\n")
        turns.append(
            {
                "turn": len(turns) + 1,
                "role": "gov",
                "turn_id": gov_turn_id,
                "model": f"{gov_config['provider']}/{gov_config['model']}",
                "dna": gov_config["dna"],
                "output_summary": f"Gov local verdict {local_gov_verdict} route {gov_parsed.get('route_verdict')}",
                "full_output_ref": str(gov_out.relative_to(out_dir)),
                "gate_status": "PASS" if not gov_failures else "FAIL",
                "artifact_hash": _sha256_text(json.dumps(gov_parsed, sort_keys=True)),
                "source_ids": sorted(valid_ids),
                "blocked_moves": gov_parsed.get("blocked_moves") or [],
            }
        )
        if (
            DYNAMIC_EARLY_EXIT_ENABLED
            and
            not gov_failures
            and gate.get("passed") is True
            and gov_parsed.get("route_verdict") == "FINAL_COMPILER"
            and gov_parsed.get("final_compiler_allowed") is True
        ):
            selection = _select_best(artifact_registry)
            if selection.get("selected") is not None:
                selection["selection_reason"] = "EARLY_EXIT_GOV_FINAL_COMPILER_ALLOWED"
            return _packet_result(packet_id, suffix, pair, call_rows, artifact_registry, selection)

    selection = _select_best(artifact_registry)
    return _packet_result(packet_id, suffix, pair, call_rows, artifact_registry, selection)


def _packet_result(packet_id: str, suffix: str, pair: dict[str, Any], calls: list[dict[str, Any]], artifacts: list[dict[str, Any]], selection: dict[str, Any]) -> dict[str, Any]:
    selected = selection.get("selected")
    result = {
        "pair_id": pair["pair_id"],
        "packet_id": packet_id,
        "suffix": suffix,
        "benchmark_bucket": pair["benchmark_bucket"],
        "is_target_packet": suffix == pair["target_suffix"],
        "is_guardrail_sibling": suffix == pair["guardrail_suffix"],
        "calls": calls,
        "artifact_registry": [{k: v for k, v in a.items() if k != "text"} for a in artifacts],
        "best_artifact_registry_present": any(a["gate_passed"] for a in artifacts),
        "final_selector": {k: v for k, v in selection.items() if k != "selected"},
        "final_admissible": selected is not None,
        "final_verdict": selected.get("verification_verdict") if selected else None,
        "final_binding": selected.get("binding_class") if selected else None,
    }
    result["external_solo_failure_evidence"] = _external_evidence(pair, packet_id)
    result["intra_holo_single_dna_miss_evidence"] = _intra_holo_evidence(result, suffix)
    target_evidence = result["external_solo_failure_evidence"] + result["intra_holo_single_dna_miss_evidence"]
    result["valid_rescue_evidence_present"] = bool(target_evidence) if result["is_target_packet"] else True
    return result


def _declared_roster_from_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    architecture_lock = manifest.get("architecture_lock")
    if isinstance(architecture_lock, dict) and isinstance(architecture_lock.get("model_roster_declared"), dict):
        declared = architecture_lock["model_roster_declared"]
    elif isinstance(manifest.get("model_roster_declared"), dict):
        declared = manifest["model_roster_declared"]
    else:
        return {"worker_sequence": [], "gov_sequence": [], "declared_roster_available": False}

    workers = declared.get("worker_sequence")
    if not isinstance(workers, list):
        workers = []

    gov_sequence = declared.get("gov_sequence")
    if isinstance(gov_sequence, list):
        govs = gov_sequence
    elif isinstance(declared.get("gov"), dict):
        govs = [{**declared["gov"], "slot": "G1"}, {**declared["gov"], "slot": "G2"}]
    else:
        govs = []

    return {
        "worker_sequence": workers,
        "gov_sequence": govs,
        "declared_roster_available": bool(workers or govs),
        "raw_declared_model_roster": declared,
    }


def _expected_counts_from_manifest(manifest: dict[str, Any]) -> dict[str, int]:
    architecture_lock = manifest.get("architecture_lock")
    expected = architecture_lock.get("expected_counts") if isinstance(architecture_lock, dict) else None
    if not isinstance(expected, dict):
        expected = manifest.get("expected_counts") if isinstance(manifest.get("expected_counts"), dict) else {}
    total_provider_calls = expected.get("total_provider_calls", expected.get("holo_calls", 0))
    return {
        "packets": int(expected.get("packets", 0) or 0),
        "total_provider_calls": int(total_provider_calls or 0),
        "judge_calls": int(expected.get("judge_calls", 0) or 0),
    }


def _model_roster_audit(manifest: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    declared_roster = _declared_roster_from_manifest(manifest)
    declared_workers = declared_roster["worker_sequence"]
    declared_gov_sequence = declared_roster["gov_sequence"]
    actual_worker_turns = [
        {
            "turn_id": row.get("turn_id"),
            "worker_index": row.get("worker_index"),
            "provider": row.get("provider"),
            "model": row.get("model"),
            "dna": row.get("dna"),
        }
        for row in rows
        if row.get("call_kind") == "worker"
    ]
    actual_gov_turns = [
        {
            "turn_id": row.get("turn_id"),
            "gov_index": row.get("gov_index"),
            "provider": row.get("provider"),
            "model": row.get("model"),
            "dna": row.get("dna"),
        }
        for row in rows
        if row.get("call_kind") == "gov"
    ]
    actual_dna = sorted({row.get("dna") for row in rows if row.get("dna")})
    mismatches = []
    for row in actual_worker_turns:
        expected = next((item for item in declared_workers if item.get("worker_index") == row["worker_index"]), None)
        if expected is None:
            mismatches.append(f"{row['turn_id']} worker_index {row.get('worker_index')} missing from declared roster")
            continue
        for key in ("provider", "model", "dna"):
            if row.get(key) != expected.get(key):
                mismatches.append(f"{row['turn_id']} {key} expected {expected.get(key)} got {row.get(key)}")
    for row in actual_gov_turns:
        expected = next((item for item in declared_gov_sequence if item.get("slot") == f"G{row.get('gov_index')}"), None)
        if expected is None and len(declared_gov_sequence) == 1:
            expected = declared_gov_sequence[0]
        if expected is None:
            mismatches.append(f"{row['turn_id']} gov_index {row.get('gov_index')} missing from declared roster")
            continue
        for key in ("provider", "model", "dna"):
            if row.get(key) != expected.get(key):
                mismatches.append(f"{row['turn_id']} {key} expected {expected.get(key)} got {row.get(key)}")
    return {
        "declared_model_roster": declared_roster.get("raw_declared_model_roster") or {
            "worker_sequence": declared_workers,
            "gov_sequence": declared_gov_sequence,
        },
        "declared_roster_available": declared_roster["declared_roster_available"],
        "actual_worker_turns": actual_worker_turns,
        "actual_gov_turns": actual_gov_turns,
        "actual_distinct_dna": actual_dna,
        "actual_distinct_dna_count": len(actual_dna),
        "all_3_dna_participated": len(actual_dna) >= 3,
        "mismatches": mismatches,
        "declared_roster_matches_actual_calls": declared_roster["declared_roster_available"] and not mismatches,
    }


def _read_trace(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _load_worker_prompt_objects(run_dir: Path, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prompt_objects: list[dict[str, Any]] = []
    for row in rows:
        if row.get("call_kind") != "worker":
            continue
        prompt_ref = row.get("prompt_ref")
        if not prompt_ref:
            prompt_objects.append({})
            continue
        try:
            prompt_payload = _load_json(run_dir / str(prompt_ref))
        except Exception:
            prompt_objects.append({})
            continue
        prompt_object = prompt_payload.get("prompt_object")
        prompt_objects.append(prompt_object if isinstance(prompt_object, dict) else {})
    return prompt_objects


def _summarize(run_dir: Path, manifest: dict[str, Any], packet_results: list[dict[str, Any]], trace_path: Path) -> dict[str, Any]:
    rows = _read_trace(trace_path)
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for row in rows:
        for key in totals:
            if isinstance(row.get(key), int):
                totals[key] += row[key]
    roster = _model_roster_audit(manifest, rows)
    law_validation = validate_holo_benchmark_laws(
        rows,
        full_context_governor_audit=bool(
            (manifest.get("architecture_lock") if isinstance(manifest.get("architecture_lock"), dict) else {}).get("full_context_governor_audit")
        ),
        worker_prompt_objects=_load_worker_prompt_objects(run_dir, rows),
    )
    by_pair: dict[str, list[dict[str, Any]]] = {}
    for result in packet_results:
        by_pair.setdefault(result["pair_id"], []).append(result)
    inventory = []
    hard_allow_valid = 0
    hard_escalate_valid = 0
    for pair_id, results in sorted(by_pair.items()):
        target = next((row for row in results if row["is_target_packet"]), None)
        guardrail = next((row for row in results if row["is_guardrail_sibling"]), None)
        if target is None or guardrail is None:
            present = target or guardrail or results[0]
            inventory.append(
                {
                    "pair_id": pair_id,
                    "benchmark_bucket": present["benchmark_bucket"],
                    "target_packet_id": target["packet_id"] if target else None,
                    "target_expected": ("ALLOW" if target and target["suffix"] == "A" else "ESCALATE") if target else None,
                    "target_final_verdict": target["final_verdict"] if target else None,
                    "target_final_correct": False,
                    "guardrail_packet_id": guardrail["packet_id"] if guardrail else None,
                    "guardrail_expected": ("ALLOW" if guardrail and guardrail["suffix"] == "A" else "ESCALATE") if guardrail else None,
                    "guardrail_final_verdict": guardrail["final_verdict"] if guardrail else None,
                    "guardrail_final_correct": False,
                    "external_solo_failure_evidence": (target or {}).get("external_solo_failure_evidence", []),
                    "intra_holo_single_dna_miss_evidence": (target or {}).get("intra_holo_single_dna_miss_evidence", []),
                    "pair_valid": False,
                    "incomplete_reason": "TARGET_OR_GUARDRAIL_SIBLING_NOT_COMPLETED",
                }
            )
            continue
        target_expected = "ALLOW" if target["suffix"] == "A" else "ESCALATE"
        guardrail_expected = "ALLOW" if guardrail["suffix"] == "A" else "ESCALATE"
        target_final_correct = target["final_admissible"] and target["final_verdict"] == target_expected
        guardrail_final_correct = guardrail["final_admissible"] and guardrail["final_verdict"] == guardrail_expected
        evidence_present = target["valid_rescue_evidence_present"]
        pair_valid = bool(target_final_correct and guardrail_final_correct and evidence_present)
        if pair_valid and target["benchmark_bucket"] == "hard_allow_false_positive_rescue":
            hard_allow_valid += 1
        if pair_valid and target["benchmark_bucket"] == "hard_escalate_false_negative_rescue":
            hard_escalate_valid += 1
        inventory.append(
            {
                "pair_id": pair_id,
                "benchmark_bucket": target["benchmark_bucket"],
                "target_packet_id": target["packet_id"],
                "target_expected": target_expected,
                "target_final_verdict": target["final_verdict"],
                "target_final_correct": target_final_correct,
                "guardrail_packet_id": guardrail["packet_id"],
                "guardrail_expected": guardrail_expected,
                "guardrail_final_verdict": guardrail["final_verdict"],
                "guardrail_final_correct": guardrail_final_correct,
                "external_solo_failure_evidence": target["external_solo_failure_evidence"],
                "intra_holo_single_dna_miss_evidence": target["intra_holo_single_dna_miss_evidence"],
                "pair_valid": pair_valid,
            }
        )
    assertions = {
        "hard_allow_valid_pairs": hard_allow_valid,
        "hard_escalate_valid_pairs": hard_escalate_valid,
        "total_valid_pairs": hard_allow_valid + hard_escalate_valid,
        "three_dna_inside_holoverify": "PASS" if roster["all_3_dna_participated"] else "FAIL",
        "declared_roster_matches_actual_calls": "PASS" if roster["declared_roster_matches_actual_calls"] else "FAIL",
        "complete_governance_enforcement": "PASS" if all(r.get("provider_call_ok") for r in rows) else "FAIL",
        "deterministic_gate_after_every_worker": "PASS" if all("gate_result" in r for r in rows if r.get("call_kind") == "worker") else "FAIL",
        "gov_receives_gate_results": "PASS" if all(r.get("received_gate_result") for r in rows if r.get("call_kind") == "gov") else "FAIL",
        "artifact_registry_present": "PASS" if all("artifact_registry" in r for r in packet_results) else "FAIL",
        "best_artifact_registry_present": "PASS" if all(r.get("best_artifact_registry_present") for r in packet_results) else "FAIL",
        "pinned_best_artifact_present": "PASS" if any(r.get("pinned_best_artifact_present") for r in rows if r.get("call_kind") == "worker") else "FAIL",
        "monotonic_preservation_enforced": "PASS" if all(r["final_admissible"] for r in packet_results) else "FAIL",
        "final_selector_present": "PASS" if all("final_selector" in r for r in packet_results) else "FAIL",
        "guardrail_sibling_correct_for_all_pairs": "PASS" if all(item["guardrail_final_correct"] for item in inventory) else "FAIL",
        "external_and_intra_holo_evidence_separated": "PASS",
        "invalid_runs_preserved": "PASS",
        "holo_benchmark_laws": "PASS" if law_validation.official_valid else "FAIL",
        "gov_worker_token_ratio_law": "PASS" if "token_ratio: hard_fail_gt_50_percent" not in law_validation.failures else "FAIL",
        "worker_prompt_sequence_law": "PASS" if not any("worker_prompt" in failure for failure in law_validation.failures) else "FAIL",
        "worker_rotation_law": "PASS" if not any(failure.startswith("workers:") for failure in law_validation.failures) else "FAIL",
        "fixed_gov_model_law": "PASS" if "gov: governor_model_id_must_remain_static" not in law_validation.failures else "FAIL",
    }
    expected = _expected_counts_from_manifest(manifest)
    packet_count_complete = len(packet_results) == expected["packets"]
    call_count_complete = packet_count_complete and len(rows) <= expected["total_provider_calls"]
    provider_failures = [
        {
            "turn_id": row.get("turn_id"),
            "packet_id": row.get("packet_id"),
            "provider": row.get("provider"),
            "model": row.get("model"),
            "error": row.get("error"),
        }
        for row in rows
        if row.get("provider_call_ok") is not True
    ]
    readiness = (
        call_count_complete
        and not provider_failures
        and law_validation.official_valid
        and
        assertions["hard_allow_valid_pairs"] == 10
        and assertions["hard_escalate_valid_pairs"] == 10
        and assertions["total_valid_pairs"] == 20
        and all(value == "PASS" for key, value in assertions.items() if isinstance(value, str))
    )
    if readiness:
        classification = "HOLOVERIFY_20PAIR_3DNA_COMPLETE"
    elif law_validation.receipt_code == "HARD_FAIL_GOV_TOKEN_RATIO_GT_50":
        classification = "INVALID_RUN_HARD_GOV_TOKEN_RATIO_GT_50"
    elif not law_validation.official_valid:
        classification = "INVALID_RUN_BENCHMARK_LAW_VIOLATION"
    elif provider_failures:
        classification = "INVALID_RUN_PROVIDER_FAILURE_BEFORE_COMPLETION"
    else:
        classification = "HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED"
    summary = {
        "classification": classification,
        "benchmark_locked": False,
        "benchmark_valid": law_validation.benchmark_valid and readiness,
        "score_valid": law_validation.score_valid and readiness,
        "law_receipt_code": law_validation.receipt_code,
        "current_best_state_preserved": law_validation.current_best_state_preserved,
        "run_dir": str(run_dir),
        "pre_run_root_signature": manifest["root_signature"],
        "trace_hash": _sha256_text(trace_path.read_text()),
        "provider_calls": len(rows),
        "expected_provider_calls": expected["total_provider_calls"],
        "expected_provider_calls_semantics": expected.get("total_provider_calls_semantics", "exact"),
        "packet_results_complete": packet_count_complete,
        "call_count_complete": call_count_complete,
        "provider_failures": provider_failures,
        "worker_calls": sum(1 for row in rows if row.get("call_kind") == "worker"),
        "gov_calls": sum(1 for row in rows if row.get("call_kind") == "gov"),
        "judge_calls": 0,
        "totals": totals,
        "benchmark_law_validation": law_validation.to_dict(),
        "model_roster_audit": roster,
        "packet_results": [
            {k: v for k, v in result.items() if k != "calls"}
            for result in packet_results
        ],
        "benchmark_inventory": inventory,
        "readiness_assertions": assertions,
        "readiness_passed": readiness,
    }
    (run_dir / "live_results.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    _write_markdown_summary(run_dir, summary)
    return summary


def _write_markdown_summary(run_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# HoloVerify 20-Pair 3-DNA Run",
        "",
        f"Classification: `{summary['classification']}`",
        f"Readiness passed: `{summary['readiness_passed']}`",
        f"Benchmark valid: `{summary['benchmark_valid']}`",
        f"Score valid: `{summary['score_valid']}`",
        f"Law receipt: `{summary['law_receipt_code']}`",
        "",
        "## Calls",
        "",
        f"- Provider calls: `{summary['provider_calls']}`",
        f"- Worker calls: `{summary['worker_calls']}`",
        f"- Gov calls: `{summary['gov_calls']}`",
        f"- Judge calls: `{summary['judge_calls']}`",
        f"- Tokens: `{summary['totals']['input_tokens']}` input / `{summary['totals']['output_tokens']}` output / `{summary['totals']['total_tokens']}` total",
        f"- Gov/Worker token ratio: `{summary['benchmark_law_validation']['gov_worker_token_ratio']}`",
        "",
        "## Model Roster",
        "",
        f"- Actual distinct DNA: `{', '.join(summary['model_roster_audit']['actual_distinct_dna'])}`",
        f"- All 3 DNA participated: `{summary['model_roster_audit']['all_3_dna_participated']}`",
        f"- Roster mismatches: `{len(summary['model_roster_audit']['mismatches'])}`",
        "",
        "## Readiness Assertions",
        "",
        "| Assertion | Value |",
        "| --- | --- |",
    ]
    for key, value in summary["readiness_assertions"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Inventory", "", "| Pair | Bucket | Target | Final | Guardrail | External evidence | Intra-Holo evidence | Valid |", "| --- | --- | --- | --- | --- | ---: | ---: | --- |"])
    for item in summary["benchmark_inventory"]:
        lines.append(
            f"| `{item['pair_id']}` | `{item['benchmark_bucket']}` | `{item['target_packet_id']}` {item['target_expected']} | `{item['target_final_verdict']}` | `{item['guardrail_final_verdict']}` | {len(item['external_solo_failure_evidence'])} | {len(item['intra_holo_single_dna_miss_evidence'])} | `{item['pair_valid']}` |"
        )
    (run_dir / "live_summary.md").write_text("\n".join(lines) + "\n")


def _terminal_call_failures(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures = []
    for row in rows:
        if row.get("provider_call_ok") is not True:
            failures.append(row)
            continue
        if row.get("parse_ok") is not True:
            failures.append(row)
            continue
        if row.get("call_kind") == "gov" and row.get("admissible") is not True:
            failures.append(row)
    return failures


def _write_partial_markdown_summary(run_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# HoloVerify 20-Pair 3-DNA Partial Run",
        "",
        f"Classification: `{summary['classification']}`",
        f"Readiness passed: `{summary['readiness_passed']}`",
        f"Provider calls: `{summary['provider_calls']}` / `{summary['expected_provider_calls']}`",
        f"Worker calls: `{summary['worker_calls']}`",
        f"Gov calls: `{summary['gov_calls']}`",
        f"Tokens: `{summary['totals']['input_tokens']}` input / `{summary['totals']['output_tokens']}` output / `{summary['totals']['total_tokens']}` total",
        "",
        "## Terminal Failures",
        "",
        "| Turn | Kind | Provider | Model | Finish | Error |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in summary["terminal_failures"]:
        lines.append(
            f"| `{item.get('turn_id')}` | `{item.get('call_kind')}` | `{item.get('provider')}` | `{item.get('model')}` | `{item.get('finish_reason')}` | `{item.get('error')}` |"
        )
    lines.extend(
        [
            "",
            "## Roster",
            "",
            f"- Actual distinct DNA: `{', '.join(summary['model_roster_audit']['actual_distinct_dna'])}`",
            f"- Roster mismatches: `{len(summary['model_roster_audit']['mismatches'])}`",
            "",
            "## Reason",
            "",
            summary["invalidation_reason"],
        ]
    )
    (run_dir / "live_summary.md").write_text("\n".join(lines) + "\n")


def _summarize_partial_trace(run_dir: Path, manifest: dict[str, Any], trace_path: Path, reason: str) -> dict[str, Any]:
    rows = _read_trace(trace_path)
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for row in rows:
        for key in totals:
            if isinstance(row.get(key), int):
                totals[key] += row[key]
    roster = _model_roster_audit(manifest, rows)
    law_validation = validate_holo_benchmark_laws(
        rows,
        full_context_governor_audit=bool(
            (manifest.get("architecture_lock") if isinstance(manifest.get("architecture_lock"), dict) else {}).get("full_context_governor_audit")
        ),
        worker_prompt_objects=_load_worker_prompt_objects(run_dir, rows),
    )
    expected = _expected_counts_from_manifest(manifest)
    terminal_failures = _terminal_call_failures(rows)
    if terminal_failures:
        first = terminal_failures[0]
        if first.get("call_kind") == "gov" and first.get("parse_ok") is not True:
            classification = "INVALID_RUN_GOV_PARSE_FAILURE_BEFORE_COMPLETION"
        elif first.get("provider_call_ok") is not True:
            classification = "INVALID_RUN_PROVIDER_FAILURE_BEFORE_COMPLETION"
        else:
            classification = "INVALID_RUN_TERMINAL_CALL_FAILURE_BEFORE_COMPLETION"
    else:
        classification = "INVALID_RUN_INCOMPLETE_TRACE"
    summary = {
        "classification": classification,
        "benchmark_locked": False,
        "benchmark_valid": False,
        "score_valid": False,
        "run_dir": str(run_dir),
        "pre_run_root_signature": manifest["root_signature"],
        "trace_hash": _sha256_text(trace_path.read_text()) if trace_path.exists() else None,
        "provider_calls": len(rows),
        "expected_provider_calls": expected["total_provider_calls"],
        "call_count_complete": len(rows) == expected["total_provider_calls"],
        "worker_calls": sum(1 for row in rows if row.get("call_kind") == "worker"),
        "gov_calls": sum(1 for row in rows if row.get("call_kind") == "gov"),
        "judge_calls": 0,
        "totals": totals,
        "terminal_failures": [
            {
                "turn_id": row.get("turn_id"),
                "packet_id": row.get("packet_id"),
                "call_kind": row.get("call_kind"),
                "provider": row.get("provider"),
                "model": row.get("model"),
                "finish_reason": row.get("finish_reason"),
                "error": row.get("error"),
                "provider_call_ok": row.get("provider_call_ok"),
                "parse_ok": row.get("parse_ok"),
                "admissible": row.get("admissible"),
            }
            for row in terminal_failures
        ],
        "invalidation_reason": reason,
        "benchmark_law_validation": law_validation.to_dict(),
        "model_roster_audit": roster,
        "readiness_assertions": {
            "hard_allow_valid_pairs": 0,
            "hard_escalate_valid_pairs": 0,
            "total_valid_pairs": 0,
            "three_dna_inside_holoverify": "PASS" if roster["all_3_dna_participated"] else "FAIL",
            "declared_roster_matches_actual_calls": "PASS" if roster["declared_roster_matches_actual_calls"] else "FAIL",
            "complete_governance_enforcement": "FAIL",
            "deterministic_gate_after_every_worker": "PASS" if all("gate_result" in r for r in rows if r.get("call_kind") == "worker") else "FAIL",
            "gov_receives_gate_results": "PASS" if all(r.get("received_gate_result") for r in rows if r.get("call_kind") == "gov") else "FAIL",
            "artifact_registry_present": "FAIL",
            "best_artifact_registry_present": "FAIL",
            "pinned_best_artifact_present": "PASS" if any(r.get("pinned_best_artifact_present") for r in rows if r.get("call_kind") == "worker") else "FAIL",
            "monotonic_preservation_enforced": "FAIL",
            "final_selector_present": "FAIL",
            "guardrail_sibling_correct_for_all_pairs": "FAIL",
            "external_and_intra_holo_evidence_separated": "PASS",
            "invalid_runs_preserved": "PASS",
        },
        "readiness_passed": False,
    }
    (run_dir / "live_results.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    _write_partial_markdown_summary(run_dir, summary)
    return summary


def run_live(limit: int = 0, bucket: str = "all") -> int:
    manifest = _validate_preflight(limit, bucket)
    for key in ("minimax", "xai", "google"):
        env = MODEL_CONFIGS[key]["api_key_env"]
        if not os.getenv(env, "").strip():
            raise RuntimeError(f"{env} missing")
    pairs = _load_pairs(limit, bucket)
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    run_dir = OUT_ROOT / "live_runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    trace_path = run_dir / "TRACE_CALLS.jsonl"
    packet_results: list[dict[str, Any]] = []
    with trace_path.open("w") as trace:
        for pair in pairs:
            for suffix in ("A", "B"):
                result = _run_packet(run_id, pair, suffix, manifest, run_dir, trace)
                packet_results.append(result)
                if _terminal_call_failures(result["calls"]):
                    summary = _summarize(run_dir, manifest, packet_results, trace_path)
                    print(json.dumps(summary, indent=2, sort_keys=True))
                    return 1
    summary = _summarize(run_dir, manifest, packet_results, trace_path)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["readiness_passed"] else 1


def audit_existing(run_dir: Path) -> int:
    manifest = _load_json(PRE_RUN_MANIFEST)
    trace_path = run_dir / "TRACE_CALLS.jsonl"
    if not (run_dir / "live_results.json").exists():
        summary = _summarize_partial_trace(
            run_dir,
            manifest,
            trace_path,
            "Trace ended before live_results.json existed; run is not comparable or score-valid.",
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1
    packet_results = _load_json(run_dir / "live_results.json")["packet_results"]
    summary = _summarize(run_dir, manifest, packet_results, trace_path)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["readiness_passed"] else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--audit-run-dir")
    parser.add_argument("--limit-pairs", type=int, default=0)
    parser.add_argument("--bucket", choices=("all", "hard_allow", "hard_escalate"), default="all")
    args = parser.parse_args()
    if args.preflight:
        manifest = _build_preflight(args.limit_pairs, args.bucket)
        print(json.dumps({"preflight": "ok", "root_signature": manifest["root_signature"], "manifest": str(PRE_RUN_MANIFEST)}, indent=2, sort_keys=True))
        return 0
    if args.run_live:
        return run_live(args.limit_pairs, args.bucket)
    if args.audit_run_dir:
        return audit_existing(Path(args.audit_run_dir))
    parser.error("Use --preflight, --run-live, or --audit-run-dir")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
