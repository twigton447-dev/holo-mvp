#!/usr/bin/env python3
"""Target current mini models at historical ESCALATE->ALLOW seam candidates.

This is diagnostic scouting only. It does not create benchmark credit and does
not call Holo/Gov/Judge. It searches historical scout prompt cards for packets
where a solo model previously returned ALLOW on an expected-ESCALATE packet,
then retests those packets with the current 3-DNA mini roster used inside
HoloVerify.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
ROOT = BENCHMARK_ROOT / "targeted_hard_escalate_three_mini_scout_2026-06-29"
SCOUT_ROOT = Path("/Users/taylorwigton/Desktop/holo-mvp/scout_runs")

MODEL_CONFIGS: dict[str, dict[str, Any]] = {
    "xai": {
        "provider": "xai",
        "model": "grok-3-mini",
        "api_key_env": "XAI_API_KEY",
        "kind": "openai_compatible",
        "default_url": "https://api.x.ai/v1/chat/completions",
        "prompt_globs": ("*__xai__grok-3-mini.json",),
    },
    "google": {
        "provider": "google",
        "model": "gemini-2.5-flash-lite",
        "api_key_env": "GOOGLE_API_KEY",
        "kind": "gemini",
        "prompt_globs": ("*__gemini__gemini-2.5-flash-lite.json", "*__google__gemini-2.5-flash-lite.json"),
    },
    "minimax": {
        "provider": "minimax",
        "model": "MiniMax-M2.5-highspeed",
        "api_key_env": "MINIMAX_API_KEY",
        "kind": "openai_compatible",
        "url_env": "MINIMAX_CHAT_COMPLETIONS_URL",
        "base_url_env": "MINIMAX_BASE_URL",
        "default_url": "https://api.minimaxi.chat/v1/chat/completions",
        "prompt_globs": ("*__minimax__MiniMax-M2.5-highspeed.json", "*__minimax__MiniMax-Text-01.json"),
    },
}

DEFAULT_MODEL_ORDER = ("xai", "google", "minimax")
FORBIDDEN_PROMPT_TERMS = (
    "hidden_expected_verdict",
    "expected_for_local_audit_only",
    "builder_hypothesis",
    "target_match",
    "correctness labels",
    "blindspot_atlas",
    "worker_disagreement_ledger",
    "HOLOVERIFY_V",
    "CONTROL_ROUTER",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _strip_thinking_blocks(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I)
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.S | re.I)
    return text.strip()


def _provider_url(config: dict[str, Any]) -> str:
    explicit = os.getenv(config.get("url_env", ""), "").strip()
    if explicit:
        return explicit
    base = os.getenv(config.get("base_url_env", ""), "").strip()
    if base:
        return base.rstrip("/") + "/chat/completions"
    return config["default_url"]


def _http_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int = 120) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _call_openai_compatible(config: dict[str, Any], system: str, user: str) -> dict[str, Any]:
    started = time.time()
    data = _http_json(
        _provider_url(config),
        {
            "model": config["model"],
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0,
            "max_tokens": 1200,
        },
        {
            "Authorization": f"Bearer {os.getenv(config['api_key_env'], '').strip()}",
            "Content-Type": "application/json",
        },
    )
    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") if isinstance(choice, dict) else {}
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return {
        "raw_text": _strip_thinking_blocks((message or {}).get("content") or ""),
        "finish_reason": choice.get("finish_reason") if isinstance(choice, dict) else None,
        "response_id": data.get("id"),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "elapsed_ms": int((time.time() - started) * 1000),
    }


def _call_gemini(config: dict[str, Any], system: str, user: str) -> dict[str, Any]:
    started = time.time()
    api_key = os.getenv(config["api_key_env"], "").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config['model']}:generateContent?key={api_key}"
    data = _http_json(
        url,
        {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"SYSTEM:\n{system}\n\nUSER:\n{user}"}],
                }
            ],
            "generationConfig": {
                "temperature": 0,
                "maxOutputTokens": 1200,
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
    usage = data.get("usageMetadata") if isinstance(data.get("usageMetadata"), dict) else {}
    in_tok = usage.get("promptTokenCount")
    out_tok = usage.get("candidatesTokenCount")
    return {
        "raw_text": _strip_thinking_blocks(output),
        "finish_reason": candidates[0].get("finishReason") if candidates else None,
        "response_id": data.get("responseId"),
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "total_tokens": (in_tok + out_tok) if isinstance(in_tok, int) and isinstance(out_tok, int) else None,
        "elapsed_ms": int((time.time() - started) * 1000),
    }


def _call_model(config: dict[str, Any], system: str, user: str) -> dict[str, Any]:
    if config["kind"] == "gemini":
        return _call_gemini(config, system, user)
    return _call_openai_compatible(config, system, user)


def _parse_verdict(text: str) -> tuple[bool, str | None, dict[str, Any] | None, str | None]:
    stripped = (text or "").strip()
    if stripped.startswith("```"):
        return False, None, None, "markdown_fence_present"
    try:
        obj = json.loads(stripped)
    except Exception as exc:
        return False, None, None, f"json_parse_error:{type(exc).__name__}"
    verdict = obj.get("verdict") or obj.get("model_verdict") or obj.get("verification_verdict")
    if verdict not in {"ALLOW", "ESCALATE"}:
        return False, verdict, obj, "verdict_invalid"
    return True, verdict, obj, None


def _prompt_dirs(results_path: Path) -> list[Path]:
    return [
        d
        for d in (results_path.parent / "prompt_cards" / "solo_scout", results_path.parent / "prompt_cards")
        if d.exists()
    ]


def _prompt_for(results_path: Path, packet_id: str, config: dict[str, Any]) -> Path | None:
    for directory in _prompt_dirs(results_path):
        for pattern in config["prompt_globs"]:
            matches = sorted(directory.glob(f"{packet_id}{pattern[1:]}"))
            if matches:
                return matches[0]
    for directory in _prompt_dirs(results_path):
        matches = sorted(directory.glob(f"{packet_id}__*.json"))
        if matches:
            return matches[0]
    return None


def _packet_path_for(results_path: Path, packet_id: str) -> Path | None:
    for candidate in (
        results_path.parent / "packets" / f"{packet_id}.json",
        results_path.parent / "generated_packets" / f"{packet_id}.payload.json",
    ):
        if candidate.exists():
            return candidate
    return None


def _sibling_packet_id(packet_id: str) -> str | None:
    if packet_id.endswith("-A"):
        return f"{packet_id[:-2]}-B"
    if packet_id.endswith("-B"):
        return f"{packet_id[:-2]}-A"
    return None


def _collect_candidates(max_packets: int) -> list[dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    for results_path in SCOUT_ROOT.rglob("results.jsonl"):
        try:
            lines = results_path.read_text(errors="ignore").splitlines()
        except Exception:
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            expected = row.get("builder_hypothesis") or row.get("expected_verdict") or row.get("expected_for_local_audit_only")
            verdict = row.get("verdict") or row.get("model_verdict")
            packet_id = row.get("packet_id")
            if expected != "ESCALATE" or verdict != "ALLOW" or not packet_id:
                continue
            family_id = row.get("family_id") or packet_id
            if packet_id in candidates:
                continue
            packet_path = _packet_path_for(results_path, packet_id)
            if not packet_path:
                continue
            sibling_packet_id = _sibling_packet_id(packet_id)
            sibling_packet_path = _packet_path_for(results_path, sibling_packet_id) if sibling_packet_id else None
            candidates[packet_id] = {
                "packet_id": packet_id,
                "sibling_packet_id": sibling_packet_id,
                "family_id": family_id,
                "expected": "ESCALATE",
                "sibling_expected": "ALLOW" if sibling_packet_id else None,
                "historical_provider": row.get("provider"),
                "historical_model": row.get("model"),
                "historical_verdict": verdict,
                "seam": row.get("seam_id") or row.get("seam_name") or row.get("failure_mode"),
                "results_path": str(results_path),
                "packet_path": str(packet_path),
                "sibling_packet_path": str(sibling_packet_path) if sibling_packet_path else None,
            }
    rows = sorted(candidates.values(), key=lambda item: (str(item.get("seam") or ""), item["packet_id"]))
    return rows[:max_packets]


def _assert_prompt_clean(system: str, user: str) -> None:
    combined = f"{system}\n{user}"
    found = [term for term in FORBIDDEN_PROMPT_TERMS if term in combined]
    if found:
        raise RuntimeError(f"control_prompt_isolation_violation:{found}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--needed", type=int, default=9)
    parser.add_argument("--max-packets", type=int, default=60)
    parser.add_argument("--model-order", default=",".join(DEFAULT_MODEL_ORDER))
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Collect and print candidate packets without API-key checks or provider calls.",
    )
    args = parser.parse_args()

    model_order = [item.strip() for item in args.model_order.split(",") if item.strip()]
    candidates = _collect_candidates(args.max_packets)
    if args.list_only:
        prompt_availability: dict[str, dict[str, bool]] = {}
        for candidate in candidates:
            per_model: dict[str, bool] = {}
            for key in model_order:
                if key not in MODEL_CONFIGS:
                    raise RuntimeError(f"unknown_model_key:{key}")
                prompt_path = _prompt_for(Path(candidate["results_path"]), candidate["packet_id"], MODEL_CONFIGS[key])
                per_model[key] = bool(prompt_path)
            prompt_availability[candidate["packet_id"]] = per_model
        print(
            json.dumps(
                {
                    "classification": "DIAGNOSTIC_HARD_ESCALATE_CANDIDATE_LIST_ONLY",
                    "candidate_count": len(candidates),
                    "candidates": candidates,
                    "prompt_availability": prompt_availability,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    for key in model_order:
        if key not in MODEL_CONFIGS:
            raise RuntimeError(f"unknown_model_key:{key}")
        if not os.getenv(MODEL_CONFIGS[key]["api_key_env"], "").strip():
            raise RuntimeError(f"missing_api_key:{MODEL_CONFIGS[key]['api_key_env']}")

    out_dir = ROOT / datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    out_dir.mkdir(parents=True, exist_ok=False)
    trace_path = out_dir / "TRACE_CALLS.jsonl"
    selected: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []

    with trace_path.open("w") as trace:
        call_index = 0
        for candidate in candidates:
            packet_selected = False
            for key in model_order:
                config = MODEL_CONFIGS[key]
                prompt_path = _prompt_for(Path(candidate["results_path"]), candidate["packet_id"], config)
                if not prompt_path:
                    continue
                card = _load_json(prompt_path)
                system = str(card["system"])
                user = str(card["user"])
                row = {
                    **candidate,
                    "call_index": call_index + 1,
                    "called_at": datetime.now(timezone.utc).isoformat(),
                    "classification": "DIAGNOSTIC_HARD_ESCALATE_CURRENT_MINI_SCOUT",
                    "provider": config["provider"],
                    "model": config["model"],
                    "prompt_card": str(prompt_path),
                    "gov_calls": 0,
                    "holo_calls": 0,
                    "judge_calls": 0,
                }
                call_index += 1
                try:
                    _assert_prompt_clean(system, user)
                    response = _call_model(config, system, user)
                    parse_ok, verdict, parsed, parse_error = _parse_verdict(response["raw_text"])
                    current_failure = parse_ok and verdict == "ALLOW"
                    row.update(
                        {
                            **response,
                            "provider_call_ok": True,
                            "parse_ok": parse_ok,
                            "parse_error": parse_error,
                            "verdict": verdict,
                            "parsed_json": parsed,
                            "current_expected": "ESCALATE",
                            "current_failure": current_failure,
                        }
                    )
                except Exception as exc:
                    row.update(
                        {
                            "provider_call_ok": False,
                            "parse_ok": False,
                            "parse_error": f"{type(exc).__name__}: {exc}",
                            "verdict": None,
                            "current_expected": "ESCALATE",
                            "current_failure": False,
                        }
                    )
                trace.write(json.dumps(row, sort_keys=True) + "\n")
                trace.flush()
                rows.append(row)
                print(
                    "screened",
                    candidate["packet_id"],
                    config["provider"],
                    config["model"],
                    "->",
                    row.get("verdict"),
                    "failure=",
                    row.get("current_failure"),
                    flush=True,
                )
                if row.get("current_failure"):
                    selected.append(
                        {
                            **candidate,
                            "current_failure_provider": config["provider"],
                            "current_failure_model": config["model"],
                            "current_failure_verdict": row.get("verdict"),
                            "trace_call_index": row["call_index"],
                        }
                    )
                    packet_selected = True
                    break
            if len(selected) >= args.needed:
                break
            if packet_selected:
                continue

    summary = {
        "classification": "DIAGNOSTIC_HARD_ESCALATE_CURRENT_MINI_SCOUT",
        "run_dir": str(out_dir),
        "candidate_count": len(candidates),
        "provider_calls": len(rows),
        "selected_count": len(selected),
        "selected": selected,
        "tokens": {
            "input": sum(row.get("input_tokens") or 0 for row in rows),
            "output": sum(row.get("output_tokens") or 0 for row in rows),
            "total": sum(row.get("total_tokens") or 0 for row in rows),
        },
    }
    (out_dir / "scout_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    md = [
        "# Targeted Hard-ESCALATE Three-Mini Scout",
        "",
        f"Selected current failures: `{len(selected)}`",
        f"Provider calls: `{len(rows)}`",
        "",
        "| Packet | Provider | Model | Historical seam | Packet path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in selected:
        md.append(
            f"| `{item['packet_id']}` | `{item['current_failure_provider']}` | `{item['current_failure_model']}` | "
            f"{item.get('seam') or ''} | `{item['packet_path']}` |"
        )
    (out_dir / "scout_summary.md").write_text("\n".join(md) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if len(selected) >= args.needed else 1


if __name__ == "__main__":
    raise SystemExit(main())
