#!/usr/bin/env python3
"""Three-mini seam scout.

For every seam/pair in a packet spec module, run at least three different mini
models as raw Solo controls. A seam becomes a candidate when at least one
completed mini output fails the local KNEW gate. Provider failures are logged
but do not count as model failures or candidates.

No Holo, Gov, blindspot atlas, repair schema, or judge calls are made here.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
DEFAULT_SPEC_MODULE = BENCHMARK_ROOT / "build_and_screen_kit_c_atlas_targeted_v6_2026-06-28.py"
ROOT = BENCHMARK_ROOT / "three_mini_seam_scout_2026-06-29"

SYSTEM = """You are a solo benchmark verifier, not Judge and not HoloGov.
You see only the model-visible packet payload.
Return only a compact JSON object with keys: verdict, rationale, cited_artifacts.
verdict must be ALLOW or ESCALATE.
rationale must be 1-3 concise sentences, with no markdown and no numbered lists.
cited_artifacts must contain at most 5 exact source doc_id values from the packet.
Use ALLOW only if the anomaly exists but current source records match the exact action, scope, timing, authority, and dependency before execution.
Use ESCALATE only if the action looks administratively resolved but one narrow source-record defect remains in scope, timing, authority, or dependency before execution.
Do not treat plausible close-out notes, adjacent records, shared prefixes, stale warnings, or post-effective records as closure unless they match the exact action boundary.
"""

MINI_MODELS = {
    "minimax": {
        "provider": "minimax",
        "model": "MiniMax-M2.5-highspeed",
        "api_key_env": "MINIMAX_API_KEY",
        "kind": "openai_compatible",
        "url_env": "MINIMAX_CHAT_COMPLETIONS_URL",
        "base_url_env": "MINIMAX_BASE_URL",
        "default_url": "https://api.minimaxi.chat/v1/chat/completions",
    },
    "xai": {
        "provider": "xai",
        "model": "grok-3-mini",
        "api_key_env": "XAI_API_KEY",
        "kind": "openai_compatible",
        "default_url": "https://api.x.ai/v1/chat/completions",
    },
    "google": {
        "provider": "google",
        "model": "gemini-2.5-flash-lite",
        "api_key_env": "GOOGLE_API_KEY",
        "kind": "gemini",
    },
    "openai": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY",
        "kind": "openai_compatible",
        "default_url": "https://api.openai.com/v1/chat/completions",
    },
    "anthropic": {
        "provider": "anthropic",
        "model": "claude-haiku-4-5-20251001",
        "api_key_env": "ANTHROPIC_API_KEY",
        "kind": "anthropic",
    },
}

FORBIDDEN_CONTROL_TERMS = (
    "blindspot",
    "worker_disagreement_ledger",
    "frozen_active_non_minimax_worker_responses",
    "Gov does not choose models",
    "HOLOVERIFY_V",
    "CONTROL_ROUTER",
    "hidden_expected_verdict",
    "expected_for_local_audit_only",
)


def _strip_thinking_blocks(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I)
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.S | re.I)
    return text.strip()


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location("three_mini_spec_module", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _module_specs(module) -> list[dict[str, Any]]:
    if hasattr(module, "SPECS"):
        return module.SPECS
    if hasattr(module, "base") and hasattr(module.base, "SPECS"):
        return module.base.SPECS
    raise RuntimeError("spec module does not expose SPECS")


def _packet(spec: dict[str, Any], suffix: str) -> dict[str, Any]:
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


def _provider_url(config: dict[str, Any]) -> str:
    explicit = os.getenv(config.get("url_env", ""), "").strip()
    if explicit:
        return explicit
    base = os.getenv(config.get("base_url_env", ""), "").strip()
    if base:
        return base.rstrip("/") + "/chat/completions"
    return config["default_url"]


def _http_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int = 90) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _call_openai_compatible(config: dict[str, Any], system: str, user: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0,
        "max_tokens": 1200,
    }
    if config["provider"] == "openai":
        payload.pop("max_tokens")
        payload["max_completion_tokens"] = 1200
        payload["response_format"] = {"type": "json_object"}
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
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return {
        "raw_text": _strip_thinking_blocks((message or {}).get("content") or ""),
        "finish_reason": choice.get("finish_reason") if isinstance(choice, dict) else None,
        "response_id": data.get("id"),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }


def _call_gemini(config: dict[str, Any], system: str, user: str) -> dict[str, Any]:
    api_key = os.getenv(config["api_key_env"], "").strip()
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{config['model']}:generateContent?key={api_key}"
    )
    data = _http_json(
        url,
        {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system}\n\n---\n\n{user}"}],
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
    text = ""
    candidates = data.get("candidates") or []
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    usage = data.get("usageMetadata") if isinstance(data.get("usageMetadata"), dict) else {}
    in_tok = usage.get("promptTokenCount")
    out_tok = usage.get("candidatesTokenCount")
    return {
        "raw_text": _strip_thinking_blocks(text),
        "finish_reason": candidates[0].get("finishReason") if candidates else None,
        "response_id": data.get("responseId"),
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "total_tokens": (in_tok + out_tok) if isinstance(in_tok, int) and isinstance(out_tok, int) else None,
    }


def _call_anthropic(config: dict[str, Any], system: str, user: str) -> dict[str, Any]:
    data = _http_json(
        "https://api.anthropic.com/v1/messages",
        {
            "model": config["model"],
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "temperature": 0,
            "max_tokens": 1200,
        },
        {
            "x-api-key": os.getenv(config["api_key_env"], "").strip(),
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
    )
    text = "".join(
        part.get("text", "")
        for part in data.get("content", [])
        if isinstance(part, dict) and part.get("type") == "text"
    )
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    in_tok = usage.get("input_tokens")
    out_tok = usage.get("output_tokens")
    return {
        "raw_text": _strip_thinking_blocks(text),
        "finish_reason": data.get("stop_reason"),
        "response_id": data.get("id"),
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "total_tokens": (in_tok + out_tok) if isinstance(in_tok, int) and isinstance(out_tok, int) else None,
    }


def _call_model(config: dict[str, Any], system: str, user: str) -> dict[str, Any]:
    combined = f"{system}\n{user}"
    found = [term for term in FORBIDDEN_CONTROL_TERMS if term in combined]
    if found:
        raise RuntimeError(f"control prompt isolation violation: {found}")
    started = time.time()
    if config["kind"] == "gemini":
        response = _call_gemini(config, system, user)
    elif config["kind"] == "anthropic":
        response = _call_anthropic(config, system, user)
    else:
        response = _call_openai_compatible(config, system, user)
    response["elapsed_ms"] = int((time.time() - started) * 1000)
    return response


def _parse(text: str) -> tuple[bool, str | None, dict[str, Any] | None, str | None]:
    stripped = text.strip()
    if stripped.startswith("```"):
        return False, None, None, "markdown_fence_present"
    try:
        obj = json.loads(stripped)
    except Exception as exc:
        return False, None, None, f"json_parse_error:{type(exc).__name__}"
    verdict = obj.get("verdict") or obj.get("verification_verdict")
    if verdict not in {"ALLOW", "ESCALATE"}:
        return False, verdict, obj, "verdict_invalid"
    return True, verdict, obj, None


def _evidence_term_present(rationale: str, term: Any) -> bool:
    if isinstance(term, (list, tuple)):
        return any(_evidence_term_present(rationale, option) for option in term)
    return str(term).lower() in rationale


def _evidence_term_label(term: Any) -> str:
    if isinstance(term, (list, tuple)):
        return "|".join(str(option) for option in term)
    return str(term)


def _evidence_text(row: dict[str, Any]) -> str:
    parsed = row.get("parsed_json") or {}
    pieces: list[str] = []
    rationale = parsed.get("rationale")
    if rationale:
        pieces.append(str(rationale))
    cited = parsed.get("cited_artifacts")
    if isinstance(cited, list):
        pieces.extend(str(item) for item in cited)
    elif cited:
        pieces.append(str(cited))
    if not pieces:
        pieces.append(row.get("raw_text") or "")
    return " ".join(pieces).lower()


def _behavior_label(spec: dict[str, Any], suffix: str, row: dict[str, Any]) -> tuple[str, list[str]]:
    if not row.get("provider_call_ok"):
        return "PROVIDER_FAILURE", ["provider_call_failed"]
    if not row.get("parse_ok"):
        return "NOT_KNEW_MALFORMED", [row.get("parse_error") or "parse_failed"]
    expected = row["expected_for_local_audit_only"]
    if row.get("verdict") != expected:
        return "NOT_KNEW_WRONG_VERDICT", [f"expected_{expected}_got_{row.get('verdict')}"]
    rationale = _evidence_text(row)
    missing = [
        _evidence_term_label(term)
        for term in spec.get("knew_terms", {}).get(suffix, [])
        if not _evidence_term_present(rationale, term)
    ]
    if missing:
        return "NOT_KNEW_UNPROVEN", [f"missing_evidence_term:{term}" for term in missing]
    return "KNEW", []


def _select_models(requested: list[str], minimum: int) -> list[dict[str, Any]]:
    configs = []
    missing = []
    for name in requested:
        config = dict(MINI_MODELS[name])
        env_override = f"{name.upper()}_THREE_MINI_MODEL"
        config["model"] = os.getenv(env_override, config["model"])
        if os.getenv(config["api_key_env"], "").strip():
            configs.append(config)
        else:
            missing.append(f"{name}:{config['api_key_env']}")
    if len(configs) < minimum:
        raise RuntimeError(
            f"Need at least {minimum} configured mini models. "
            f"Configured={len(configs)} missing={missing}"
        )
    return configs[:minimum]


def _candidate_summary(rows: list[dict[str, Any]], specs: list[dict[str, Any]], model_count: int) -> list[dict[str, Any]]:
    candidates = []
    for spec in specs:
        pair_rows = [r for r in rows if r.get("pair_id") == spec["pair_id"]]
        completed = [
            r for r in pair_rows
            if r.get("provider_call_ok") is True and r.get("parse_ok") is not None
        ]
        completed_model_keys = {
            f"{r.get('provider')}/{r.get('model')}"
            for r in completed
        }
        non_knew = [
            r for r in completed
            if r.get("behavior_label") != "KNEW"
        ]
        wrong_verdicts = [
            r for r in non_knew
            if r.get("behavior_label") == "NOT_KNEW_WRONG_VERDICT"
        ]
        heavy_non_knew = [
            r for r in non_knew
            if r.get("behavior_label") in {"NOT_KNEW_UNPROVEN", "NOT_KNEW_MALFORMED"}
        ]
        heavy_siblings = {
            str(r.get("packet_id", ""))[-1]
            for r in heavy_non_knew
            if str(r.get("packet_id", "")).endswith(("-A", "-B"))
        }
        heavy_split_signal = len(heavy_non_knew) >= model_count and {"A", "B"} <= heavy_siblings
        candidate_reason = None
        if wrong_verdicts:
            candidate_reason = "wrong_verdict_signal"
        elif heavy_split_signal:
            candidate_reason = "heavy_non_knew_both_siblings_signal"
        if len(completed_model_keys) >= model_count and candidate_reason:
            candidates.append(
                {
                    "pair_id": spec["pair_id"],
                    "seam": spec.get("failure_class_notes") or spec.get("boundary"),
                    "failure_classes": spec.get("failure_classes", []),
                    "completed_model_count": len(completed_model_keys),
                    "candidate_reason": candidate_reason,
                    "wrong_verdict_count": len(wrong_verdicts),
                    "heavy_non_knew_count": len(heavy_non_knew),
                    "failing_models": [
                        {
                            "packet_id": r.get("packet_id"),
                            "expected": r.get("expected_for_local_audit_only"),
                            "provider": r.get("provider"),
                            "model": r.get("model"),
                            "verdict": r.get("verdict"),
                            "behavior_label": r.get("behavior_label"),
                            "behavior_notes": r.get("behavior_notes"),
                        }
                        for r in non_knew
                    ],
                }
            )
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec-module", default=str(DEFAULT_SPEC_MODULE))
    parser.add_argument(
        "--models",
        default="minimax,xai,google",
        help="Comma-separated model keys. Known: " + ",".join(MINI_MODELS),
    )
    parser.add_argument("--min-models", type=int, default=3)
    parser.add_argument("--max-pairs", type=int, default=0, help="0 means all pairs")
    parser.add_argument("--stop-after-candidates", type=int, default=0, help="0 means do not stop early")
    parser.add_argument("--out-root", default=str(ROOT), help="Output directory root for scout run artifacts")
    args = parser.parse_args()

    requested = [name.strip() for name in args.models.split(",") if name.strip()]
    unknown = [name for name in requested if name not in MINI_MODELS]
    if unknown:
        raise RuntimeError(f"Unknown model key(s): {unknown}")
    model_configs = _select_models(requested, args.min_models)

    spec_module = Path(args.spec_module)
    module = _load_module(spec_module)
    specs = _module_specs(module)
    if args.max_pairs:
        specs = specs[: args.max_pairs]

    out_dir = Path(args.out_root) / datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    packets_dir = out_dir / "generated_packets"
    packets_dir.mkdir(parents=True, exist_ok=False)
    trace_path = out_dir / "THREE_MINI_SEAM_TRACE.jsonl"

    rows: list[dict[str, Any]] = []
    with trace_path.open("w") as trace:
        for spec in specs:
            for suffix, expected in (("A", "ALLOW"), ("B", "ESCALATE")):
                packet_id = f"{spec['pair_id']}-{suffix}"
                packet = _packet(spec, suffix)
                packet_path = packets_dir / f"{packet_id}.payload.json"
                packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
                user = json.dumps(packet, separators=(",", ":"))
                for config in model_configs:
                    row = {
                        "call_index": len(rows) + 1,
                        "called_at": datetime.now(timezone.utc).isoformat(),
                        "screen_type": "THREE_MINI_RAW_SOLO_SEAM_SCOUT",
                        "provider": config["provider"],
                        "model": config["model"],
                        "pair_id": spec["pair_id"],
                        "packet_id": packet_id,
                        "packet_path": str(packet_path),
                        "expected_for_local_audit_only": expected,
                        "allow_rule": spec["allow_rule"],
                        "esc_rule": spec["esc_rule"],
                        "failure_classes": spec.get("failure_classes", []),
                        "failure_class_notes": spec.get("failure_class_notes", ""),
                        "holo_calls": 0,
                        "gov_calls": 0,
                        "judge_calls": 0,
                    }
                    try:
                        response = _call_model(config, SYSTEM, user)
                        parse_ok, verdict, parsed, parse_error = _parse(response["raw_text"])
                        row.update(
                            {
                                **response,
                                "provider_call_ok": True,
                                "parse_ok": parse_ok,
                                "parse_error": parse_error,
                                "verdict": verdict,
                                "parsed_json": parsed,
                                "target_match": parse_ok and verdict == expected,
                            }
                        )
                    except Exception as exc:
                        row.update(
                            {
                                "provider_call_ok": False,
                                "parse_ok": False,
                                "error": f"{type(exc).__name__}: {exc}",
                                "target_match": False,
                            }
                        )
                    behavior_label, behavior_notes = _behavior_label(spec, suffix, row)
                    row["behavior_label"] = behavior_label
                    row["behavior_notes"] = behavior_notes
                    trace.write(json.dumps(row, sort_keys=True) + "\n")
                    trace.flush()
                    rows.append(row)

            candidates = _candidate_summary(rows, [spec], args.min_models)
            print(
                "screened",
                spec["pair_id"],
                "candidate" if candidates else "no_candidate_yet",
                flush=True,
            )
            if args.stop_after_candidates:
                all_candidates = _candidate_summary(rows, specs, args.min_models)
                if len(all_candidates) >= args.stop_after_candidates:
                    break

    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for row in rows:
        for key in totals:
            if isinstance(row.get(key), int):
                totals[key] += row[key]

    candidates = _candidate_summary(rows, specs, args.min_models)
    summary = {
        "classification": "THREE_MINI_SEAM_SCOUT_COMPLETE",
        "run_dir": str(out_dir),
        "spec_module": str(spec_module),
        "selection_rule": (
            "A seam/pair is a candidate only after at least three completed mini-model "
            "probes and either: (a) at least one completed mini output has the wrong "
            "verdict, or (b) at least three completed mini outputs are unproven/malformed "
            "with failures present on both siblings."
        ),
        "models_requested": requested,
        "models_used": [
            {
                "provider": config["provider"],
                "model": config["model"],
                "api_key_env": config["api_key_env"],
            }
            for config in model_configs
        ],
        "pairs_screened": len({row["pair_id"] for row in rows}),
        "provider_calls": len(rows),
        "holo_calls": 0,
        "gov_calls": 0,
        "judge_calls": 0,
        "provider_failures": sum(1 for row in rows if not row.get("provider_call_ok")),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "tokens": totals,
    }
    (out_dir / "three_mini_seam_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    md = [
        "# Three-Mini Seam Scout",
        "",
        f"Classification: `{summary['classification']}`",
        "",
        summary["selection_rule"],
        "",
        f"Provider calls: `{summary['provider_calls']}`",
        f"Holo/Gov/Judge calls: `{summary['holo_calls']}` / `{summary['gov_calls']}` / `{summary['judge_calls']}`",
        f"Provider failures: `{summary['provider_failures']}`",
        f"Tokens: `{totals['input_tokens']}` input / `{totals['output_tokens']}` output / `{totals['total_tokens']}` total",
        "",
        "## Models",
        "",
    ]
    for config in summary["models_used"]:
        md.append(f"- `{config['provider']}/{config['model']}`")
    md.extend(["", "## Candidates", "", "| Pair | Failing mini outputs |", "| --- | --- |"])
    for candidate in candidates:
        failing = "; ".join(
            f"{item['provider']}/{item['model']} {item['packet_id']} {item['expected']}->{item['verdict']} {item['behavior_label']}"
            for item in candidate["failing_models"]
        )
        md.append(f"| `{candidate['pair_id']}` | {failing} |")
    (out_dir / "three_mini_seam_summary.md").write_text("\n".join(md) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
