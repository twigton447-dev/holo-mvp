#!/usr/bin/env python3
"""Run the HoloVerify blind canary runtime-firewall lane.

This script binds the committed blind runner to the exact 20-packet provider
scope documented in HOLOVERIFY_BLIND_CANARY_LIVE_PROVIDER_SCOPE_2026_07_02.
It does not run solo, judges, or post-hoc scoring before the trace is frozen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
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

import holoverify_blind_runner_v0 as BLIND  # noqa: E402


RUNTIME_MANIFEST = BENCHMARK_ROOT / "holoverify_blind_canary_runtime_manifest_2026_07_02.json"
SCORING_MAP = BENCHMARK_ROOT / "holoverify_blind_canary_scoring_map_2026_07_02.json"
LIVE_ROOT = BENCHMARK_ROOT / "holoverify_blind_canary_live_runs_2026_07_02"

EXPECTED_RUNTIME_MANIFEST_SHA256 = "b80861ab6e407f98d69a7dd268ee102648b0455c19a1823ad0504fb321768bd7"
EXPECTED_SCORING_MAP_SHA256 = "5bb6fea5c3f2d72ae0b092eb168aeebc6ab4dcd6bc897b784c563dc455822c2b"
EXPECTED_PACKET_COUNT = 20
EXPECTED_CALL_COUNT = 100
MAX_OUTPUT_TOKENS = 1024
GOV_MAX_OUTPUT_TOKENS = 512
FINAL_COMPILER_MAX_OUTPUT_TOKENS = 2048
PROVIDER_TIMEOUT_SECONDS = 240
TRANSPORT_MAX_RETRIES = 2
TRANSPORT_BACKOFF_SECONDS = (2, 4)
RETRYABLE_HTTP_STATUS = {429, 500, 502, 503, 504}

EXACT_APPROVAL_SENTENCE = (
    "I approve live provider execution for HOLOVERIFY_BLIND_CANARY_20PKT_RUNTIME_FIREWALL_V0 "
    "using commit 55d5877fe4cd2b4157691bdc54772e5bf09ecf04, runtime manifest "
    "b80861ab6e407f98d69a7dd268ee102648b0455c19a1823ad0504fb321768bd7, and exactly "
    "100 provider calls: W1 xai/grok-3-mini x20, G1 minimax/MiniMax-M2.5-highspeed x20, "
    "W2 openai/gpt-5.4-mini x20, G2 minimax/MiniMax-M2.5-highspeed x20, "
    "W3 minimax/MiniMax-M2.5-highspeed x20. No judges, no solo, no scoring map before "
    "trace freeze, no substitutions, no public claims."
)

def one_packet_approval_sentence(packet_index: int) -> str:
    return (
        "I approve live provider execution for HOLOVERIFY_BLIND_CANARY_1PKT_RUNTIME_FIREWALL_V0 "
        "using the committed blind canary runtime manifest "
        "b80861ab6e407f98d69a7dd268ee102648b0455c19a1823ad0504fb321768bd7, "
        f"opaque packet index {packet_index} only, "
        "and exactly 5 provider calls: W1 xai/grok-3-mini x1, G1 minimax/MiniMax-M2.5-highspeed x1, "
        "W2 openai/gpt-5.4-mini x1, G2 minimax/MiniMax-M2.5-highspeed x1, "
        "W3 minimax/MiniMax-M2.5-highspeed x1. No judges, no solo, no scoring map before "
        "trace freeze, no substitutions, no public claims."
    )


def scoped_approval_sentence(packet_limit: int | None = None, packet_index: int = 1) -> str:
    if packet_limit is None:
        return EXACT_APPROVAL_SENTENCE
    if packet_limit == EXPECTED_PACKET_COUNT and packet_index == 1:
        return EXACT_APPROVAL_SENTENCE
    if packet_limit == 1:
        return one_packet_approval_sentence(packet_index)

    end_index = packet_index + packet_limit - 1
    total_calls = packet_limit * len(CALL_SEQUENCE)
    return (
        f"I approve live provider execution for HOLOVERIFY_BLIND_CANARY_{packet_limit}PKT_RUNTIME_FIREWALL_V0 "
        "using the committed blind canary runtime manifest "
        "b80861ab6e407f98d69a7dd268ee102648b0455c19a1823ad0504fb321768bd7, "
        f"opaque packet indices {packet_index}-{end_index} only, "
        f"and exactly {total_calls} provider calls: W1 xai/grok-3-mini x{packet_limit}, "
        f"G1 minimax/MiniMax-M2.5-highspeed x{packet_limit}, W2 openai/gpt-5.4-mini x{packet_limit}, "
        f"G2 minimax/MiniMax-M2.5-highspeed x{packet_limit}, W3 minimax/MiniMax-M2.5-highspeed x{packet_limit}. "
        "No judges, no solo, no scoring map before trace freeze, no substitutions, no public claims."
    )

FORBIDDEN_RUNTIME_STRINGS = (
    "packet_truth",
    "legacy_truth",
    "legacy_packet_id",
    "sibling_id",
    "target_bucket",
    "answer_key",
    "expected verdict",
    "knew_terms",
    "allow_rule",
    "esc_rule",
)

ROSTER = {
    "W1": {
        "slot": "W1",
        "role": "worker",
        "provider": "xai",
        "model": "grok-3-mini",
        "api_key_env": "XAI_API_KEY",
        "kind": "openai_compatible",
        "url": "https://api.x.ai/v1/chat/completions",
    },
    "G1": {
        "slot": "G1",
        "role": "gov",
        "provider": "minimax",
        "model": "MiniMax-M2.5-highspeed",
        "api_key_env": "MINIMAX_API_KEY",
        "kind": "openai_compatible",
        "url": "https://api.minimax.chat/v1/chat/completions",
    },
    "W2": {
        "slot": "W2",
        "role": "worker",
        "provider": "openai",
        "model": "gpt-5.4-mini",
        "api_key_env": "OPENAI_API_KEY",
        "kind": "openai_responses",
        "url": "https://api.openai.com/v1/responses",
    },
    "G2": {
        "slot": "G2",
        "role": "gov",
        "provider": "minimax",
        "model": "MiniMax-M2.5-highspeed",
        "api_key_env": "MINIMAX_API_KEY",
        "kind": "openai_compatible",
        "url": "https://api.minimax.chat/v1/chat/completions",
    },
    "W3": {
        "slot": "W3",
        "role": "worker",
        "provider": "minimax",
        "model": "MiniMax-M2.5-highspeed",
        "api_key_env": "MINIMAX_API_KEY",
        "kind": "openai_compatible",
        "url": "https://api.minimax.chat/v1/chat/completions",
    },
}

CALL_SEQUENCE = ("W1", "G1", "W2", "G2", "W3")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def current_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(errors="replace"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def strip_thinking_blocks(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I)
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.S | re.I)
    text = re.sub(r"^\s*<think>.*$", "", text, flags=re.S | re.I)
    text = re.sub(r"^\s*<thinking>.*$", "", text, flags=re.S | re.I)
    return text.strip()


def parse_key_value(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key:
            parsed[key] = value.strip()
    return parsed


def validate_live_output_contract(slot: str, response: dict[str, Any]) -> None:
    text = str(response.get("text") or "")
    finish_reason = str(response.get("finish_reason") or "").lower()
    if not text.strip():
        raise BLIND.BlindRunnerContentFailure(f"{slot}_empty_text")
    if finish_reason == "length":
        raise BLIND.BlindRunnerContentFailure(f"{slot}_finish_reason_length")

    parsed = parse_key_value(text)
    if slot.startswith("W"):
        expected_first_line = f"worker_role={slot}"
        if not text.lstrip().startswith(expected_first_line):
            raise BLIND.BlindRunnerContentFailure(f"{slot}_worker_contract_bad_prefix")
        required = (
            "worker_role",
            "verification_verdict",
            "action_boundary",
            "binding_class",
            "cited_evidence",
            "final_answer",
        )
        missing = [key for key in required if not parsed.get(key)]
        if missing:
            raise BLIND.BlindRunnerContentFailure(f"{slot}_worker_contract_missing:{','.join(missing)}")
        if parsed.get("worker_role") != slot:
            raise BLIND.BlindRunnerContentFailure(f"{slot}_worker_contract_bad_role:{parsed.get('worker_role')}")
        if parsed.get("verification_verdict") not in {"ALLOW", "ESCALATE"}:
            raise BLIND.BlindRunnerContentFailure(f"{slot}_worker_contract_bad_verdict:{parsed.get('verification_verdict')}")
        return

    required_gov = ("route_verdict", "repair_target", "blocked_move")
    missing_gov = [key for key in required_gov if not parsed.get(key)]
    if missing_gov:
        raise BLIND.BlindRunnerContentFailure(f"{slot}_gov_contract_missing:{','.join(missing_gov)}")


def env_presence() -> dict[str, str]:
    required = ("XAI_API_KEY", "OPENAI_API_KEY", "MINIMAX_API_KEY")
    return {name: "PRESENT" if os.getenv(name, "").strip() else "MISSING" for name in required}


def minimax_url() -> str:
    explicit = os.getenv("MINIMAX_CHAT_COMPLETIONS_URL", "").strip()
    if explicit:
        return explicit
    base = os.getenv("MINIMAX_BASE_URL", "").strip()
    if base:
        return base.rstrip("/") + "/chat/completions"
    return "https://api.minimax.chat/v1/chat/completions"


def resolved_config(slot: str) -> dict[str, Any]:
    config = dict(ROSTER[slot])
    if config["provider"] == "minimax":
        config["url"] = minimax_url()
    return config


def _http_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=PROVIDER_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _http_error_body(exc: urllib.error.HTTPError) -> str:
    try:
        return exc.read().decode("utf-8", errors="replace")[:2000]
    except Exception:
        return ""


def _classify_transport_exception(exc: BaseException) -> dict[str, Any] | None:
    if isinstance(exc, urllib.error.HTTPError):
        body = _http_error_body(exc)
        status = getattr(exc, "code", None)
        if status in RETRYABLE_HTTP_STATUS:
            return {"class": f"http_{status}", "status": status, "body": body}
        return None
    if isinstance(exc, TimeoutError):
        return {"class": "read_timeout", "status": None, "body": ""}
    if isinstance(exc, urllib.error.URLError):
        reason = str(getattr(exc, "reason", exc)).lower()
        if "timed out" in reason:
            return {"class": "read_timeout", "status": None, "body": ""}
        if "connection reset" in reason or "temporar" in reason:
            return {"class": "transient_network_error", "status": None, "body": ""}
    return None


def call_with_transport_retry(call_once, provider: str, model: str) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    for attempt in range(1, TRANSPORT_MAX_RETRIES + 2):
        try:
            response = call_once()
            response["transport_attempt_count"] = attempt
            response["transport_recovered"] = bool(failures)
            response["transport_retry_failures"] = failures
            return response
        except Exception as exc:
            classification = _classify_transport_exception(exc)
            if classification is None or attempt > TRANSPORT_MAX_RETRIES:
                metadata = {
                    "provider": provider,
                    "model": model,
                    "attempt": attempt,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "retryable": bool(classification),
                    "transport_retry_failures": failures,
                }
                if classification:
                    metadata.update(classification)
                raise RuntimeError(json.dumps(metadata, sort_keys=True)) from exc
            failures.append(
                {
                    "attempt": attempt,
                    "provider": provider,
                    "model": model,
                    "class": classification["class"],
                    "status": classification.get("status"),
                    "body": classification.get("body", ""),
                }
            )
            time.sleep(TRANSPORT_BACKOFF_SECONDS[min(attempt - 1, len(TRANSPORT_BACKOFF_SECONDS) - 1)])
    raise RuntimeError("transport_retry_exhausted")


def max_output_tokens_for_slot(slot: str) -> int:
    if slot.startswith("G"):
        return GOV_MAX_OUTPUT_TOKENS
    if slot == "W3":
        return FINAL_COMPILER_MAX_OUTPUT_TOKENS
    return MAX_OUTPUT_TOKENS


def call_openai_compatible(config: dict[str, Any], messages: list[dict[str, str]], max_tokens: int) -> dict[str, Any]:
    payload = {
        "model": config["model"],
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
    }

    def call_once() -> dict[str, Any]:
        data = _http_json(
            config["url"],
            payload,
            {
                "Authorization": f"Bearer {os.getenv(config['api_key_env'], '').strip()}",
                "Content-Type": "application/json",
            },
        )
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") if isinstance(choice, dict) else {}
        raw_text = (message or {}).get("content") or ""
        text = strip_thinking_blocks(raw_text)
        usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
        return {
            "text": text,
            "raw_text": raw_text,
            "text_stripped_by_thinking_filter": raw_text != text,
            "finish_reason": choice.get("finish_reason") if isinstance(choice, dict) else None,
            "response_id": data.get("id"),
            "input_tokens": usage.get("prompt_tokens"),
            "output_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
        }

    return call_with_transport_retry(call_once, config["provider"], config["model"])


def call_openai_responses(config: dict[str, Any], messages: list[dict[str, str]], max_tokens: int) -> dict[str, Any]:
    prompt = "\n\n".join(f"{message['role'].upper()}:\n{message['content']}" for message in messages)
    payload = {
        "model": config["model"],
        "input": prompt,
        "max_output_tokens": max_tokens,
    }

    def call_once() -> dict[str, Any]:
        data = _http_json(
            config["url"],
            payload,
            {
                "Authorization": f"Bearer {os.getenv(config['api_key_env'], '').strip()}",
                "Content-Type": "application/json",
            },
        )
        text_parts: list[str] = []
        output = data.get("output") if isinstance(data.get("output"), list) else []
        for item in output:
            content = item.get("content") if isinstance(item, dict) else []
            for part in content if isinstance(content, list) else []:
                if isinstance(part, dict) and part.get("type") in {"output_text", "text"}:
                    text_parts.append(str(part.get("text") or ""))
        raw_text = "".join(text_parts)
        text = strip_thinking_blocks(raw_text)
        usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
        return {
            "text": text,
            "raw_text": raw_text,
            "text_stripped_by_thinking_filter": raw_text != text,
            "finish_reason": data.get("status"),
            "response_id": data.get("id"),
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "total_tokens": usage.get("total_tokens"),
        }

    return call_with_transport_retry(call_once, config["provider"], config["model"])


def call_provider(config: dict[str, Any], messages: list[dict[str, str]], max_tokens: int) -> dict[str, Any]:
    if config["kind"] == "openai_responses":
        return call_openai_responses(config, messages, max_tokens)
    return call_openai_compatible(config, messages, max_tokens)


def expected_slot_for_index(index: int) -> str:
    return CALL_SEQUENCE[index % len(CALL_SEQUENCE)]


def assert_message_matches_slot(messages: list[dict[str, str]], slot: str) -> None:
    content = "\n".join(message.get("content", "") for message in messages)
    if slot.startswith("W"):
        if f"role={slot}" not in content:
            raise RuntimeError(f"slot_message_mismatch:{slot}")
    else:
        if "blind Gov actuator" not in content or "SELECTED_GOV_BATON_LINES" not in content:
            raise RuntimeError(f"slot_message_mismatch:{slot}")


def make_mock_transport() -> Any:
    call_index = {"value": 0}

    def transport(messages: list[dict[str, str]]) -> str:
        slot = expected_slot_for_index(call_index["value"])
        call_index["value"] += 1
        assert_message_matches_slot(messages, slot)
        content = "\n".join(message.get("content", "") for message in messages)
        if slot.startswith("G"):
            return "\n".join(
                [
                    "route_verdict=CONTINUE",
                    "repair_target=preserve blind source-grounded reasoning",
                    "blocked_move=do not invent source IDs",
                ]
            )
        ids = re.findall(r"\b([A-Z]{2,}(?:-[A-Z0-9]+)+):", content)
        cited = "|".join(ids[:2] or ["SRC-FIXTURE"])
        return "\n".join(
            [
                f"worker_role={slot}",
                "verification_verdict=ESCALATE",
                "binding_class=SOURCE_BOUNDARY_OPEN",
                "action_boundary=blind runtime firewall fixture boundary",
                f"cited_evidence={cited}",
                "open_blockers=fixture unresolved dependency",
                "final_answer=Fixture output for no-provider prompt leakage preflight only.",
            ]
        )

    return transport


class LiveTransport:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.raw_dir = run_dir / "raw_provider_outputs"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.call_index = 0
        self.provider_rows: list[dict[str, Any]] = []

    def __call__(self, messages: list[dict[str, str]]) -> str:
        slot = expected_slot_for_index(self.call_index)
        assert_message_matches_slot(messages, slot)
        config = resolved_config(slot)
        prompt_text = json.dumps(messages, sort_keys=True, ensure_ascii=True)
        prompt_hash = sha256_text(prompt_text)
        call_number = self.call_index + 1
        max_tokens = max_output_tokens_for_slot(slot)
        self.call_index += 1
        started = time.time()
        response: dict[str, Any] | None = None
        error: str | None = None
        try:
            response = call_provider(config, messages, max_tokens)
            validate_live_output_contract(slot, response)
            return str(response.get("text") or "")
        except Exception as exc:
            error = str(exc)
            raise
        finally:
            elapsed_ms = int((time.time() - started) * 1000)
            text = str((response or {}).get("text") or "")
            raw_text = str((response or {}).get("raw_text") or "")
            raw_ref = self.raw_dir / f"{call_number:03d}_{slot}.json"
            write_json(
                raw_ref,
                {
                    "call_number": call_number,
                    "slot": slot,
                    "provider": config["provider"],
                    "model": config["model"],
                    "prompt_sha256": prompt_hash,
                    "provider_call_ok": response is not None and error is None,
                    "error": error,
                    "response": response,
                    "max_output_tokens": max_tokens,
                    "text": text,
                    "raw_text": raw_text,
                    "text_sha256": sha256_text(text),
                    "raw_text_sha256": sha256_text(raw_text),
                },
            )
            self.provider_rows.append(
                {
                    "call_number": call_number,
                    "slot": slot,
                    "role": config["role"],
                    "provider": config["provider"],
                    "model": config["model"],
                    "prompt_sha256": prompt_hash,
                    "raw_output_ref": str(raw_ref.relative_to(self.run_dir)),
                    "provider_call_ok": response is not None and error is None,
                    "error": error,
                    "max_output_tokens": max_tokens,
                    "finish_reason": (response or {}).get("finish_reason"),
                    "response_id": (response or {}).get("response_id"),
                    "input_tokens": (response or {}).get("input_tokens"),
                    "output_tokens": (response or {}).get("output_tokens"),
                    "total_tokens": (response or {}).get("total_tokens"),
                    "transport_attempt_count": (response or {}).get("transport_attempt_count"),
                    "transport_recovered": (response or {}).get("transport_recovered"),
                    "transport_retry_failures": (response or {}).get("transport_retry_failures", []),
                    "text_sha256": sha256_text(text),
                    "raw_text_sha256": sha256_text(raw_text),
                    "elapsed_ms": elapsed_ms,
                }
            )


def materialize_runtime_subset(run_dir: Path, packet_limit: int | None, packet_index: int = 1) -> Path:
    if packet_limit is None:
        return RUNTIME_MANIFEST
    if packet_limit <= 0:
        raise ValueError("packet_limit must be positive")
    if packet_index <= 0:
        raise ValueError("packet_index must be 1-based and positive")
    source = load_json(RUNTIME_MANIFEST)
    source_packets = list(source.get("packets") or [])
    start = packet_index - 1
    packets = source_packets[start : start + packet_limit]
    if len(packets) != packet_limit:
        raise ValueError(f"packet subset out of range: index={packet_index} limit={packet_limit}")
    subset = {
        **source,
        "packet_count": len(packets),
        "packets": packets,
        "source_runtime_manifest": str(RUNTIME_MANIFEST.relative_to(REPO_ROOT)),
        "source_runtime_manifest_sha256": sha256_file(RUNTIME_MANIFEST),
        "subset_runtime_manifest": True,
        "subset_packet_limit": packet_limit,
        "subset_packet_start_index_1based": packet_index,
        "subset_opaque_runtime_ids": [row.get("opaque_runtime_id") for row in packets],
    }
    path = run_dir / f"runtime_manifest_subset_i{packet_index:03d}_n{packet_limit:03d}.json"
    write_json(path, subset)
    return path


def scan_runtime_inputs(manifest_path: Path, manifest: dict[str, Any]) -> list[str]:
    hits: list[str] = []
    manifest_text = manifest_path.read_text(errors="replace")
    for term in FORBIDDEN_RUNTIME_STRINGS:
        if term.lower() in manifest_text.lower():
            hits.append(f"runtime_manifest:{term}")
    for row in manifest.get("packets", []):
        payload_path = REPO_ROOT / row["runtime_payload_ref"]
        text = payload_path.read_text(errors="replace")
        for term in FORBIDDEN_RUNTIME_STRINGS:
            if term.lower() in text.lower():
                hits.append(f"{payload_path.name}:{term}")
        if re.search(r"\bHV-[A-Z]+-REP-\d{3}-[AB]\b", text):
            hits.append(f"{payload_path.name}:legacy_packet_id_pattern")
    return hits


def prompt_probe_no_leakage(manifest_path: Path, expected_call_count: int, probe_dir: Path) -> list[str]:
    result = BLIND.run_blind_runtime_manifest(str(manifest_path), str(probe_dir), transport=make_mock_transport())
    if result.get("observed_call_count") != expected_call_count:
        return [f"prompt_probe_call_count:{result.get('observed_call_count')}"]
    hits: list[str] = []
    for prompt in (probe_dir).glob("*/prompts/*.json"):
        text = prompt.read_text(errors="replace")
        for term in FORBIDDEN_RUNTIME_STRINGS:
            if term.lower() in text.lower():
                hits.append(f"{prompt.name}:{term}")
        if re.search(r"\bHV-[A-Z]+-REP-\d{3}-[AB]\b", text):
            hits.append(f"{prompt.name}:legacy_packet_id_pattern")
    return hits


def preflight(run_dir: Path, runtime_manifest_path: Path = RUNTIME_MANIFEST) -> dict[str, Any]:
    runtime_hash = sha256_file(runtime_manifest_path)
    source_runtime_hash = sha256_file(RUNTIME_MANIFEST)
    scoring_hash = sha256_file(SCORING_MAP)
    manifest = load_json(runtime_manifest_path)
    packet_refs = [row.get("runtime_payload_ref") for row in manifest.get("packets", [])]
    expected_packet_count = int(manifest.get("packet_count") or len(packet_refs))
    expected_call_count = expected_packet_count * len(CALL_SEQUENCE)
    payload_paths = [REPO_ROOT / str(ref) for ref in packet_refs]
    missing_payloads = [str(path) for path in payload_paths if not path.exists()]
    leakage_hits = scan_runtime_inputs(runtime_manifest_path, manifest)
    probe_hits = prompt_probe_no_leakage(runtime_manifest_path, expected_call_count, run_dir / "preflight_prompt_probe")
    env = env_presence()
    provider_counts = {
        "xai": expected_packet_count,
        "openai": expected_packet_count,
        "minimax": expected_packet_count * 3,
    }
    checks = {
        "source_runtime_manifest_hash": source_runtime_hash == EXPECTED_RUNTIME_MANIFEST_SHA256,
        "scoring_map_hash": scoring_hash == EXPECTED_SCORING_MAP_SHA256,
        "runtime_consumable": manifest.get("runtime_consumable") is True,
        "packet_count": manifest.get("packet_count") == expected_packet_count and len(packet_refs) == expected_packet_count,
        "payloads_present": not missing_payloads,
        "expected_call_count": expected_call_count == expected_packet_count * 5,
        "provider_counts": provider_counts == {"xai": expected_packet_count, "openai": expected_packet_count, "minimax": expected_packet_count * 3},
        "solo_calls_disabled": manifest.get("solo_calls", 0) == 0,
        "judge_calls_disabled": manifest.get("judge_calls", 0) == 0,
        "provider_calls_not_yet_made": True,
        "env_keys_present": all(value == "PRESENT" for value in env.values()),
        "runtime_input_leakage": not leakage_hits,
        "prompt_probe_leakage": not probe_hits,
    }
    report = {
        "classification": "HOLOVERIFY_BLIND_CANARY_LIVE_PREFLIGHT_V0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "current_head": current_head(),
        "runtime_manifest": str(runtime_manifest_path.relative_to(REPO_ROOT)) if runtime_manifest_path.is_relative_to(REPO_ROOT) else str(runtime_manifest_path),
        "runtime_manifest_sha256": runtime_hash,
        "source_runtime_manifest_sha256": source_runtime_hash,
        "scoring_map_sha256_preflight_only": scoring_hash,
        "expected_runtime_manifest_sha256": EXPECTED_RUNTIME_MANIFEST_SHA256,
        "expected_scoring_map_sha256": EXPECTED_SCORING_MAP_SHA256,
        "packets": expected_packet_count,
        "expected_provider_calls": expected_call_count,
        "call_sequence": list(CALL_SEQUENCE),
        "roster": {slot: {k: v for k, v in resolved_config(slot).items() if k != "api_key_env"} for slot in CALL_SEQUENCE},
        "env_presence": env,
        "checks": checks,
        "missing_payloads": missing_payloads,
        "runtime_input_leakage_hits": leakage_hits,
        "prompt_probe_leakage_hits": probe_hits,
        "passed": all(checks.values()),
    }
    write_json(run_dir / "blind_canary_live_preflight.json", report)
    lines = [
        "# HoloVerify Blind Canary Live Preflight",
        "",
        f"- Passed: `{report['passed']}`",
        f"- Runtime manifest hash: `{runtime_hash}`",
        f"- Expected provider calls: `{expected_call_count}`",
        f"- Env keys: `{env}`",
        f"- Leakage hits: `{len(leakage_hits) + len(probe_hits)}`",
        "",
        "No provider calls were made by preflight.",
    ]
    write_text(run_dir / "blind_canary_live_preflight.md", "\n".join(lines) + "\n")
    return report


def write_provider_trace(run_dir: Path, rows: list[dict[str, Any]]) -> None:
    trace_path = run_dir / "TRACE_PROVIDER_CALLS.jsonl"
    with trace_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def posthoc_score(run_dir: Path, runtime_result: dict[str, Any], provider_rows: list[dict[str, Any]]) -> dict[str, Any]:
    scoring = load_json(SCORING_MAP)
    truth_by_opaque = {
        row["opaque_runtime_id"]: row["legacy_truth"]
        for row in scoring.get("scoring_rows", [])
    }
    scored_rows = []
    correct = 0
    for row in runtime_result.get("results", []):
        packet_id = row.get("packet_id")
        verdict = (row.get("final") or {}).get("verdict")
        truth = truth_by_opaque.get(packet_id)
        is_correct = verdict == truth
        correct += 1 if is_correct else 0
        scored_rows.append(
            {
                "opaque_runtime_id": packet_id,
                "final_verdict": verdict,
                "posthoc_truth": truth,
                "correct": is_correct,
            }
        )
    token_totals: dict[str, int] = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    provider_token_totals: dict[str, dict[str, int]] = {}
    for row in provider_rows:
        provider = str(row.get("provider"))
        bucket = provider_token_totals.setdefault(provider, {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
        for key in token_totals:
            value = row.get(key)
            if isinstance(value, int):
                token_totals[key] += value
                bucket[key] += value
    report = {
        "classification": "HOLOVERIFY_BLIND_CANARY_POSTHOC_SCORE_V0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scoring_map_loaded_after_trace_freeze": True,
        "packet_count": len(scored_rows),
        "correct_count": correct,
        "incorrect_count": len(scored_rows) - correct,
        "score_rows": scored_rows,
        "token_totals": token_totals,
        "provider_token_totals": provider_token_totals,
    }
    write_json(run_dir / "blind_canary_posthoc_score.json", report)
    return report


def run_live(approval_statement: str, packet_limit: int | None = None, packet_index: int = 1) -> dict[str, Any]:
    expected_approval = scoped_approval_sentence(packet_limit, packet_index)
    if approval_statement != expected_approval:
        raise RuntimeError("approval_statement_mismatch")

    run_dir = LIVE_ROOT / f"run_{utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=False)
    runtime_manifest_path = materialize_runtime_subset(run_dir, packet_limit, packet_index)
    expected_call_count = int(load_json(runtime_manifest_path).get("packet_count") or 0) * len(CALL_SEQUENCE)
    preflight_report = preflight(run_dir, runtime_manifest_path)
    if not preflight_report.get("passed"):
        raise RuntimeError(f"preflight_failed:{preflight_report.get('checks')}")

    transport = LiveTransport(run_dir)
    trace_frozen = False
    runtime_result: dict[str, Any] | None = None
    posthoc: dict[str, Any] | None = None
    failure: str | None = None
    try:
        runtime_result = BLIND.run_blind_runtime_manifest(str(runtime_manifest_path), str(run_dir), transport=transport)
        write_provider_trace(run_dir, transport.provider_rows)
        trace_frozen = True
        observed = runtime_result.get("observed_call_count")
        if observed != expected_call_count or len(transport.provider_rows) != expected_call_count:
            raise RuntimeError(f"observed_call_count_mismatch:{observed}:{len(transport.provider_rows)}")
        posthoc = posthoc_score(run_dir, runtime_result, transport.provider_rows)
    except Exception as exc:
        failure = str(exc)
        write_provider_trace(run_dir, transport.provider_rows)
        trace_frozen = True
        raise
    finally:
        provider_failures = [row for row in transport.provider_rows if row.get("provider_call_ok") is not True]
        final_verdicts = [
            (row.get("final") or {}).get("verdict")
            for row in (runtime_result or {}).get("results", [])
        ]
        final_verdicts_valid = bool(final_verdicts) and all(verdict in {"ALLOW", "ESCALATE"} for verdict in final_verdicts)
        summary = {
            "classification": "HOLOVERIFY_BLIND_CANARY_LIVE_RUN_SUMMARY_V0",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "run_dir": str(run_dir.relative_to(REPO_ROOT)),
            "current_head": current_head(),
            "runtime_manifest": str(runtime_manifest_path.relative_to(REPO_ROOT)) if runtime_manifest_path.is_relative_to(REPO_ROOT) else str(runtime_manifest_path),
            "runtime_manifest_sha256": sha256_file(runtime_manifest_path),
            "source_runtime_manifest_sha256": sha256_file(RUNTIME_MANIFEST),
            "packet_limit": packet_limit,
            "packet_index": packet_index if packet_limit is not None else None,
            "expected_provider_calls": expected_call_count,
            "observed_provider_calls": len(transport.provider_rows),
            "trace_frozen_before_scoring": trace_frozen,
            "provider_failures": provider_failures,
            "runtime_result_ref": "blind_canary_runtime_results.json" if runtime_result else None,
            "provider_trace_ref": "TRACE_PROVIDER_CALLS.jsonl",
            "posthoc_score_ref": "blind_canary_posthoc_score.json" if posthoc else None,
            "failure": failure,
            "final_verdicts_valid": final_verdicts_valid,
            "passed_runtime_firewall": (
                runtime_result is not None
                and posthoc is not None
                and len(transport.provider_rows) == expected_call_count
                and not provider_failures
                and final_verdicts_valid
            ),
        }
        write_json(run_dir / "blind_canary_live_summary.json", summary)
        lines = [
            "# HoloVerify Blind Canary Live Summary",
            "",
            f"- Runtime firewall passed: `{summary['passed_runtime_firewall']}`",
            f"- Observed provider calls: `{summary['observed_provider_calls']}` / `{expected_call_count}`",
            f"- Provider failures: `{len(provider_failures)}`",
            f"- Trace frozen before scoring: `{trace_frozen}`",
            f"- Failure: `{failure}`",
            "",
            "This run is a blind runtime-firewall test only. It is not an error-rate claim.",
        ]
        write_text(run_dir / "blind_canary_live_summary.md", "\n".join(lines) + "\n")
    return load_json(run_dir / "blind_canary_live_summary.json")


def run_preflight_only(packet_limit: int | None = None, packet_index: int = 1) -> dict[str, Any]:
    run_dir = LIVE_ROOT / f"preflight_{utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=False)
    runtime_manifest_path = materialize_runtime_subset(run_dir, packet_limit, packet_index)
    return preflight(run_dir, runtime_manifest_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--packet-limit", type=int, default=None)
    parser.add_argument("--packet-index", type=int, default=1)
    parser.add_argument("--approval-statement", default="")
    args = parser.parse_args()

    if args.preflight == args.run_live:
        raise SystemExit("choose exactly one of --preflight or --run-live")

    if args.preflight:
        print(json.dumps(run_preflight_only(args.packet_limit, args.packet_index), indent=2, sort_keys=True))
        return 0

    summary = run_live(args.approval_statement, args.packet_limit, args.packet_index)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
