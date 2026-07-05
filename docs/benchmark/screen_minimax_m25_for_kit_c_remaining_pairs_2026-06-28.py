#!/usr/bin/env python3
"""Screen current MiniMax M2.5 for remaining Kit C source-boundary pairs.

This is a diagnostic scout. It does not create benchmark credit. It searches
existing A/B prompt-card families, runs current MiniMax raw Solo on both
siblings, and stops after finding the requested number of new families where
Solo misses at least one sibling.
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


ROOT = Path(__file__).resolve().parent / "kit_c_remaining_pair_screen_minimax_m25_2026-06-28"
SCOUT_ROOT = Path("/Users/taylorwigton/Desktop/holo-mvp/scout_runs")
MODEL = "MiniMax-M2.5-highspeed"
EXCLUDE_FAMILIES = {
    "BAL100-BEC-SUBTLE-CLOSEOUT-021",
    "BAL100-BEC-SUBTLE-CLOSEOUT-022",
    "BAL100-BEC-SUBTLE-CLOSEOUT-019",
    "BAL100-BEC-SUBTLE-CLOSEOUT-020",
    "BAL100-HB004-DEP-001",
    "BAL100-HB004-DEP-002",
    "BAL100-HB004-DEP-003",
    "BAL100-HB004-DEP-004",
    "BAL100-HB004-DEP-005",
    "BAL100-HB004-DEP-006",
    "BAL100-HB004-DEP-007",
    "BAL100-HB004-DEP-008",
    "BAL100-BEC-QUIET-MISMATCH-025",
    "BAL100-HB004-TIME-001",
}
FORBIDDEN_CONTROL_TERMS = (
    "blindspot",
    "worker_disagreement_ledger",
    "HOLOVERIFY_V",
    "CONTROL_ROUTER",
    "hidden_expected_verdict",
    "expected_for_local_audit_only",
    "correctness labels",
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
    with urllib.request.urlopen(req, timeout=75) as response:
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


def _prompt_candidates(results_path: Path, packet_id: str) -> list[Path]:
    paths: list[Path] = []
    for subdir in ("prompt_cards/solo_scout", "prompt_cards"):
        directory = results_path.parent / subdir
        if directory.exists():
            paths.extend(directory.glob(f"{packet_id}__minimax__*.json"))
    return sorted(paths, key=lambda p: ("reasoning_extraction" in str(p), len(str(p))))


def _family_priority(family_id: str, seam: str, mismatch_count: int) -> tuple[int, str]:
    score = 100
    if mismatch_count:
        score -= 50
    if "SUBTLE-CLOSEOUT" in family_id:
        score -= 20
    if "DEP" in family_id:
        score -= 15
    if "TIME" in family_id:
        score -= 10
    if "QUIET" in family_id:
        score -= 10
    if seam:
        score -= 5
    return score, family_id


def _collect_families() -> list[dict[str, Any]]:
    families: dict[str, dict[str, Any]] = {}
    for results_path in SCOUT_ROOT.glob("*/results.jsonl"):
        for line in results_path.read_text(errors="ignore").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            packet_id = row.get("packet_id")
            family_id = row.get("family_id") or packet_id
            if not packet_id or not family_id or family_id in EXCLUDE_FAMILIES:
                continue
            expected = row.get("builder_hypothesis") or row.get("expected_verdict")
            if expected not in {"ALLOW", "ESCALATE"}:
                continue
            prompts = _prompt_candidates(results_path, packet_id)
            if not prompts:
                continue
            fam = families.setdefault(
                family_id,
                {
                    "family_id": family_id,
                    "seam": row.get("seam_name") or row.get("seam_id") or row.get("failure_mode") or "",
                    "results_path": str(results_path),
                    "packets": {},
                    "historical_minimax_mismatch_count": 0,
                },
            )
            existing = fam["packets"].setdefault(
                packet_id,
                {
                    "packet_id": packet_id,
                    "expected": expected,
                    "prompt_card": str(prompts[0]),
                },
            )
            if row.get("provider") == "minimax" and row.get("provider_call_ok") is True and row.get("parse_ok") is True:
                verdict = row.get("verdict") or row.get("model_verdict")
                if verdict != expected:
                    fam["historical_minimax_mismatch_count"] += 1
                    existing["historical_minimax_verdict"] = verdict
    complete = []
    for fam in families.values():
        exps = {p["expected"] for p in fam["packets"].values()}
        if {"ALLOW", "ESCALATE"}.issubset(exps):
            fam["priority"] = _family_priority(
                fam["family_id"],
                fam["seam"],
                fam["historical_minimax_mismatch_count"],
            )
            complete.append(fam)
    return sorted(complete, key=lambda f: f["priority"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--needed", type=int, default=8)
    parser.add_argument("--max-families", type=int, default=20)
    args = parser.parse_args()
    if not os.getenv("MINIMAX_API_KEY", "").strip():
        raise RuntimeError("MINIMAX_API_KEY missing")
    out_dir = ROOT / datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    out_dir.mkdir(parents=True, exist_ok=False)
    trace_path = out_dir / "CONTROL_SCREEN_TRACE.jsonl"
    selected: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    families = _collect_families()[: args.max_families]
    with trace_path.open("w") as trace:
        for fam in families:
            family_rows = []
            for packet in sorted(fam["packets"].values(), key=lambda p: (p["expected"] != "ALLOW", p["packet_id"])):
                card = _load_json(Path(packet["prompt_card"]))
                row = {
                    "call_index": len(rows) + 1,
                    "called_at": datetime.now(timezone.utc).isoformat(),
                    "screen_type": "CURRENT_MINIMAX_M25_RAW_CONTROL_PAIR_SCREEN",
                    "provider": "minimax",
                    "model": MODEL,
                    "family_id": fam["family_id"],
                    "packet_id": packet["packet_id"],
                    "expected_for_local_audit_only": packet["expected"],
                    "prompt_card": packet["prompt_card"],
                    "results_path": fam["results_path"],
                    "seam": fam["seam"],
                }
                try:
                    response = _call_minimax(card["system"], card["user"])
                    parse_ok, verdict, parsed, parse_error = _parse_verdict(response["raw_text"])
                    row.update(
                        {
                            **response,
                            "provider_call_ok": True,
                            "parse_ok": parse_ok,
                            "parse_error": parse_error,
                            "verdict": verdict,
                            "parsed_json": parsed,
                            "target_match": parse_ok and verdict == packet["expected"],
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
                    trace.write(json.dumps(row) + "\n")
                    rows.append(row)
                    break
                trace.write(json.dumps(row) + "\n")
                rows.append(row)
                family_rows.append(row)
            else:
                print(
                    "screened",
                    fam["family_id"],
                    [(r["expected_for_local_audit_only"], r.get("verdict"), r.get("target_match")) for r in family_rows],
                    flush=True,
                )
                if family_rows and any(r.get("target_match") is False and r.get("parse_ok") is True for r in family_rows):
                    selected.append(
                        {
                            "family_id": fam["family_id"],
                            "seam": fam["seam"],
                            "results_path": fam["results_path"],
                            "packets": [
                                {
                                    "packet_id": r["packet_id"],
                                    "expected": r["expected_for_local_audit_only"],
                                    "verdict": r.get("verdict"),
                                    "target_match": r.get("target_match"),
                                    "prompt_card": r["prompt_card"],
                                    "input_tokens": r.get("input_tokens"),
                                    "output_tokens": r.get("output_tokens"),
                                    "total_tokens": r.get("total_tokens"),
                                }
                                for r in family_rows
                            ],
                        }
                    )
                    if len(selected) >= args.needed:
                        break
                continue
            break
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for row in rows:
        for key in totals:
            if isinstance(row.get(key), int):
                totals[key] += row[key]
    summary = {
        "classification": "KIT_C_REMAINING_PAIR_SCREEN_COMPLETE",
        "run_dir": str(out_dir),
        "provider_calls": len(rows),
        "needed": args.needed,
        "selected_count": len(selected),
        "selected": selected,
        "tokens": totals,
    }
    (out_dir / "screen_summary.json").write_text(json.dumps(summary, indent=2))
    md = [
        "# MiniMax M2.5 Kit C Remaining Pair Screen",
        "",
        f"Classification: `{summary['classification']}`",
        f"Selected: `{len(selected)}` / `{args.needed}`",
        f"Provider calls: `{len(rows)}`",
        f"Tokens: `{totals['input_tokens']}` input / `{totals['output_tokens']}` output / `{totals['total_tokens']}` total",
        "",
        "| Family | Seam | Packet verdicts |",
        "| --- | --- | --- |",
    ]
    for item in selected:
        verdicts = ", ".join(
            f"{p['packet_id']} {p['expected']}->{p['verdict']}" for p in item["packets"]
        )
        md.append(f"| `{item['family_id']}` | {item['seam']} | {verdicts} |")
    (out_dir / "screen_summary.md").write_text("\n".join(md) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if selected else 1


if __name__ == "__main__":
    raise SystemExit(main())
