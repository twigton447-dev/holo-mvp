#!/usr/bin/env python3
"""Find a current MiniMax M2.5 raw-control failure before any Gov/Holo run."""

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
ROOT.mkdir(parents=True, exist_ok=True)

CANDIDATES = [
    {
        "packet_id": "BAL100-HB004-TIME-002-B",
        "expected": "ESCALATE",
        "seam": "TIMING_WINDOW_EXACTNESS",
        "prompt_card": "/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-004_holobuilder_scaleout_plan_20260618T231804Z/prompt_cards/solo_scout/BAL100-HB004-TIME-002-B__minimax__MiniMax-Text-01.json",
    },
    {
        "packet_id": "BAL100-HB004-TIME-001-B",
        "expected": "ESCALATE",
        "seam": "TIMING_WINDOW_EXACTNESS",
        "prompt_card": "/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-004_holobuilder_scaleout_plan_20260618T231804Z/prompt_cards/solo_scout/BAL100-HB004-TIME-001-B__minimax__MiniMax-Text-01.json",
    },
    {
        "packet_id": "BAL100-HB004-TIME-003-B",
        "expected": "ESCALATE",
        "seam": "TIMING_WINDOW_EXACTNESS",
        "prompt_card": "/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-004_holobuilder_scaleout_plan_20260618T231804Z/prompt_cards/solo_scout/BAL100-HB004-TIME-003-B__minimax__MiniMax-Text-01.json",
    },
    {
        "packet_id": "BAL100-BEC-SUBTLE-CLOSEOUT-019-B",
        "expected": "ESCALATE",
        "seam": "SUBTLE_ACTION_BOUNDARY",
        "prompt_card": "/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-003_bounded_scout/prompt_cards/BAL100-BEC-SUBTLE-CLOSEOUT-019-B__minimax__MiniMax-Text-01.json",
    },
    {
        "packet_id": "BAL100-BEC-SUBTLE-CLOSEOUT-020-A",
        "expected": "ALLOW",
        "seam": "SUBTLE_ACTION_BOUNDARY_PRECISION",
        "prompt_card": "/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-003_targeted_post_repair_rescout/prompt_cards/BAL100-BEC-SUBTLE-CLOSEOUT-020-A__minimax__MiniMax-Text-01.json",
    },
    {
        "packet_id": "BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL",
        "expected": "ESCALATE",
        "seam": "CALLBACK_PROVENANCE",
        "prompt_card": "/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-001_BEC-PAIR-005_diagnostic_rescout/BAL100-BATCH-001_five_mini_solo_scout_20260618T153412Z/prompt_cards/BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL__minimax__MiniMax-Text-01.json",
    },
    {
        "packet_id": "BAL100-BEC-QUIET-MISMATCH-025-B",
        "expected": "ESCALATE",
        "seam": "DEPENDENCY_CLOSURE_EXACTNESS_RAW_CONTROL",
        "prompt_card": "/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-004_selected_repair_rescout_live_20260618T2208Z/prompt_cards/solo_scout/BAL100-BEC-QUIET-MISMATCH-025-B__minimax__MiniMax-Text-01.json",
    },
]

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


def _call_minimax(model: str, system: str, user: str) -> dict[str, Any]:
    combined = f"{system}\n{user}"
    found = [term for term in FORBIDDEN_CONTROL_TERMS if term in combined]
    if found:
        raise RuntimeError(f"control prompt isolation violation: {found}")
    started = time.time()
    payload = {
        "model": model,
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
        body = response.read().decode("utf-8", errors="replace")
    data = json.loads(body)
    elapsed_ms = int((time.time() - started) * 1000)
    choices = data.get("choices") or [{}]
    message = choices[0].get("message") if isinstance(choices[0], dict) else {}
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return {
        "raw_text": _strip_thinking_blocks((message or {}).get("content") or ""),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "elapsed_ms": elapsed_ms,
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


def main() -> int:
    if not os.getenv("MINIMAX_API_KEY", "").strip():
        raise RuntimeError("MINIMAX_API_KEY missing")
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    out_dir = ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=False)
    trace_path = out_dir / "CONTROL_SCREEN_TRACE.jsonl"
    model = "MiniMax-M2.5-highspeed"
    rows: list[dict[str, Any]] = []
    found_failure = False
    with trace_path.open("w") as trace:
        for index, candidate in enumerate(CANDIDATES, 1):
            card = _load_json(Path(candidate["prompt_card"]))
            system = card["system"]
            user = card["user"]
            row = {
                "call_index": index,
                "called_at": datetime.now(timezone.utc).isoformat(),
                "screen_type": "RAW_CONTROL_ONLY_NO_GOV_NO_HOLO",
                "provider": "minimax",
                "model": model,
                "packet_id": candidate["packet_id"],
                "seam": candidate["seam"],
                "expected_for_local_audit_only": candidate["expected"],
                "prompt_card": candidate["prompt_card"],
                "control_prompt_inputs": ["historical_prompt_card.system", "historical_prompt_card.user"],
                "control_forbidden_inputs": ["blindspot_atlas", "worker_ledger", "gov_doctrine", "repair_schema"],
                "prompt_chars": {"system": len(system), "user": len(user)},
            }
            try:
                response = _call_minimax(model, system, user)
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
                found_failure = True
                break

    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for row in rows:
        for key in totals:
            value = row.get(key)
            if isinstance(value, int):
                totals[key] += value
    summary = {
        "classification": "CONTROL_FAILURE_FOUND" if found_failure else "NO_CONTROL_FAILURE_FOUND_IN_SCREEN",
        "run_dir": str(out_dir),
        "provider_calls": len(rows),
        "gov_calls": 0,
        "holo_calls": 0,
        "judge_calls": 0,
        "tokens": totals,
        "first_failure": next((r for r in rows if r.get("control_failed")), None),
        "rows": [
            {
                "call_index": r.get("call_index"),
                "packet_id": r.get("packet_id"),
                "seam": r.get("seam"),
                "expected": r.get("expected_for_local_audit_only"),
                "verdict": r.get("verdict"),
                "control_failed": r.get("control_failed"),
                "provider_call_ok": r.get("provider_call_ok"),
                "parse_ok": r.get("parse_ok"),
                "error": r.get("error") or r.get("parse_error"),
                "input_tokens": r.get("input_tokens"),
                "output_tokens": r.get("output_tokens"),
                "total_tokens": r.get("total_tokens"),
            }
            for r in rows
        ],
    }
    (out_dir / "control_screen_summary.json").write_text(json.dumps(summary, indent=2))
    md = [
        "# MiniMax M2.5 Raw Control Failure Screen",
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
