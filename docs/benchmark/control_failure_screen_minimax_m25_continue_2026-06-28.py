#!/usr/bin/env python3
"""Continue raw MiniMax M2.5 control-only screening over historical failures."""

from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent / "control_failure_screen_minimax_m25_2026-06-28"
MODEL = "MiniMax-M2.5-highspeed"
ALREADY_TESTED = {
    "BAL100-HB004-TIME-002-B",
    "BAL100-HB004-TIME-001-B",
    "BAL100-HB004-TIME-003-B",
    "BAL100-BEC-SUBTLE-CLOSEOUT-019-B",
    "BAL100-BEC-SUBTLE-CLOSEOUT-021-A",
    "BAL100-BEC-SUBTLE-CLOSEOUT-020-A",
    "BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL",
    "BAL100-BEC-QUIET-MISMATCH-025-B",
}
FORBIDDEN_CONTROL_TERMS = (
    "blindspot",
    "worker_disagreement_ledger",
    "frozen_active",
    "Gov does not choose models",
    "HOLOVERIFY_V",
    "CONTROL_ROUTER",
    "hidden_expected_verdict",
    "expected_for_local_audit_only",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _strip_thinking_blocks(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I)
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.S | re.I)
    return text.strip()


def _chat_completions_url() -> str:
    explicit = os.getenv("MINIMAX_CHAT_COMPLETIONS_URL", "").strip()
    if explicit:
        return explicit
    base = os.getenv("MINIMAX_BASE_URL", "").strip()
    if base:
        return base.rstrip("/") + "/chat/completions"
    return "https://api.minimaxi.chat/v1/chat/completions"


def _call_minimax(system: str, user: str) -> dict[str, Any]:
    combined = f"{system}\n{user}"
    found = [term for term in FORBIDDEN_CONTROL_TERMS if term in combined]
    if found:
        raise RuntimeError(f"control prompt isolation violation: {found}")
    started = time.time()
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0,
        "max_tokens": 1200,
    }
    req = urllib.request.Request(
        _chat_completions_url(),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {os.getenv('MINIMAX_API_KEY', '').strip()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8", errors="replace"))
    choices = data.get("choices") or [{}]
    message = choices[0].get("message") if isinstance(choices[0], dict) else {}
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return {
        "raw_text": _strip_thinking_blocks((message or {}).get("content") or ""),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "elapsed_ms": int((time.time() - started) * 1000),
    }


def _parse_verdict(text: str) -> tuple[bool, str | None, dict[str, Any] | None, str | None]:
    stripped = text.strip()
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


def _prompt_candidates_for(results_path: Path, packet_id: str) -> list[Path]:
    paths: list[Path] = []
    for subdir in ("prompt_cards/solo_scout", "prompt_cards"):
        directory = results_path.parent / subdir
        if directory.exists():
            paths.extend(directory.glob(f"{packet_id}__minimax__*.json"))
    return sorted(paths, key=lambda p: ("reasoning_extraction" in str(p), len(str(p))))


def _candidate_score(packet_id: str, expected: str, seam: str) -> int:
    score = 50
    if expected == "ALLOW":
        score -= 40
    if "CALLBACK" in packet_id:
        score -= 25
    if "SUBTLE" in packet_id:
        score -= 20
    if "DEP" in packet_id or "025" in packet_id:
        score += 20
    if seam == "DEP_CLOSURE_EXACTNESS":
        score += 15
    return score


def _collect_candidates(limit: int = 25) -> list[dict[str, Any]]:
    collected: dict[str, dict[str, Any]] = {}
    for results_path in Path("/Users/taylorwigton/Desktop/holo-mvp/scout_runs").rglob("results.jsonl"):
        try:
            lines = results_path.read_text(errors="ignore").splitlines()
        except Exception:
            continue
        for line in lines:
            if not line.strip() or "minimax" not in line.lower():
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("provider") != "minimax":
                continue
            packet_id = obj.get("packet_id")
            if not packet_id or packet_id in ALREADY_TESTED or packet_id in collected:
                continue
            expected = obj.get("builder_hypothesis") or obj.get("expected_verdict")
            historical = obj.get("verdict") or obj.get("model_verdict")
            if not expected or not historical or expected == historical or historical == "ERROR":
                continue
            prompts = _prompt_candidates_for(results_path, packet_id)
            if not prompts:
                continue
            seam = obj.get("seam_id") or obj.get("seam_name") or obj.get("failure_mode") or ""
            collected[packet_id] = {
                "packet_id": packet_id,
                "expected": expected,
                "historical_minimax_verdict": historical,
                "seam": seam,
                "prompt_card": str(prompts[0]),
                "results_path": str(results_path),
                "score": _candidate_score(packet_id, expected, str(seam)),
            }
    return sorted(collected.values(), key=lambda c: (c["score"], c["packet_id"]))[:limit]


def main() -> int:
    if not os.getenv("MINIMAX_API_KEY", "").strip():
        raise RuntimeError("MINIMAX_API_KEY missing")
    out_dir = ROOT / ("run_continue_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    out_dir.mkdir(parents=True, exist_ok=False)
    trace_path = out_dir / "CONTROL_SCREEN_TRACE.jsonl"
    rows: list[dict[str, Any]] = []
    found_failure: dict[str, Any] | None = None
    candidates = _collect_candidates()

    with trace_path.open("w") as trace:
        for call_index, candidate in enumerate(candidates, 1):
            card = _load_json(Path(candidate["prompt_card"]))
            row = {
                "call_index": call_index,
                "called_at": datetime.now(timezone.utc).isoformat(),
                "screen_type": "RAW_CONTROL_ONLY_NO_GOV_NO_HOLO_CONTINUATION",
                "provider": "minimax",
                "model": MODEL,
                "packet_id": candidate["packet_id"],
                "seam": candidate["seam"],
                "expected_for_local_audit_only": candidate["expected"],
                "historical_minimax_verdict": candidate["historical_minimax_verdict"],
                "prompt_card": candidate["prompt_card"],
                "results_path": candidate["results_path"],
                "control_prompt_inputs": [
                    "historical_prompt_card.system",
                    "historical_prompt_card.user",
                ],
                "control_forbidden_inputs": [
                    "blindspot_atlas",
                    "worker_ledger",
                    "gov_doctrine",
                    "repair_schema",
                ],
                "prompt_chars": {
                    "system": len(card["system"]),
                    "user": len(card["user"]),
                },
            }
            try:
                response = _call_minimax(card["system"], card["user"])
                parse_ok, verdict, parsed, parse_error = _parse_verdict(response["raw_text"])
                control_failed = parse_ok and verdict != candidate["expected"]
                row.update(
                    {
                        **response,
                        "provider_call_ok": True,
                        "parse_ok": parse_ok,
                        "parse_error": parse_error,
                        "verdict": verdict,
                        "parsed_json": parsed,
                        "control_failed": control_failed,
                    }
                )
            except Exception as exc:
                row.update(
                    {
                        "provider_call_ok": False,
                        "parse_ok": False,
                        "error": f"{type(exc).__name__}: {exc}",
                        "control_failed": False,
                    }
                )
                trace.write(json.dumps(row) + "\n")
                rows.append(row)
                break
            trace.write(json.dumps(row) + "\n")
            rows.append(row)
            if row["control_failed"]:
                found_failure = row
                break

    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for row in rows:
        for key in totals:
            value = row.get(key)
            if isinstance(value, int):
                totals[key] += value
    summary = {
        "classification": "CONTROL_FAILURE_FOUND"
        if found_failure
        else "NO_CONTROL_FAILURE_FOUND_IN_CONTINUATION_SCREEN",
        "run_dir": str(out_dir),
        "provider_calls": len(rows),
        "gov_calls": 0,
        "holo_calls": 0,
        "judge_calls": 0,
        "tokens": totals,
        "first_failure": found_failure,
        "rows": [
            {
                "call_index": row.get("call_index"),
                "packet_id": row.get("packet_id"),
                "seam": row.get("seam"),
                "expected": row.get("expected_for_local_audit_only"),
                "verdict": row.get("verdict"),
                "control_failed": row.get("control_failed"),
                "provider_call_ok": row.get("provider_call_ok"),
                "parse_ok": row.get("parse_ok"),
                "error": row.get("error") or row.get("parse_error"),
                "input_tokens": row.get("input_tokens"),
                "output_tokens": row.get("output_tokens"),
                "total_tokens": row.get("total_tokens"),
            }
            for row in rows
        ],
    }
    (out_dir / "control_screen_summary.json").write_text(json.dumps(summary, indent=2))
    md = [
        "# MiniMax M2.5 Raw Control Failure Continuation Screen",
        "",
        f"Classification: `{summary['classification']}`",
        "",
        "No Gov, Holo, worker, atlas, or judge calls were made.",
        "",
        f"Provider calls: {len(rows)}",
        f"Tokens: {totals['input_tokens']} input / {totals['output_tokens']} output / {totals['total_tokens']} total",
        "",
        "| Call | Packet | Seam | Expected | Verdict | Control Failed |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for row in summary["rows"]:
        md.append(
            f"| {row['call_index']} | `{row['packet_id']}` | `{row['seam']}` | `{row['expected']}` | `{row['verdict']}` | {row['control_failed']} |"
        )
    (out_dir / "control_screen_summary.md").write_text("\n".join(md) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if found_failure else 2


if __name__ == "__main__":
    raise SystemExit(main())
