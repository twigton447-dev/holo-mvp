"""
run_with_trace.py — Run a single benchmark scenario and save a full reasoning trace.

Usage:
  python run_with_trace.py examples/scenarios/11_the_long_game.json

Outputs:
  - Summary table printed to console (same as benchmark.py)
  - Full turn-by-turn reasoning trace saved to traces/<scenario_name>_trace.md
  - Raw result JSON saved to traces/<scenario_name>_result.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from benchmark import run_benchmark

SEV_ORDER = ["HIGH", "MEDIUM", "LOW", "NONE"]

def _sev_bar(flags: dict) -> str:
    cats = {
        "sender_identity":  "SndId",
        "invoice_amount":   "InvAmt",
        "payment_routing":  "PayRt",
        "urgency_pressure": "Urgcy",
        "domain_spoofing":  "DomSpf",
        "approval_chain":   "ApprCh",
    }
    parts = [f"{abbr}={flags.get(cat,'NONE')[0]}" for cat, abbr in cats.items()]
    return "  ".join(parts)


def _md_turn(turn: dict, idx: int) -> str:
    lines = []
    verdict = turn.get("verdict", "?")
    role    = turn.get("role", "?")
    provider = turn.get("provider", "?")
    reasoning = turn.get("reasoning", "").strip()
    flags   = turn.get("severity_flags", {})

    lines.append(f"### Turn {idx} — {provider.upper()} · {role}")
    lines.append(f"**Verdict:** `{verdict}`  ")
    lines.append(f"**Risk flags:** `{_sev_bar(flags)}`")
    lines.append("")

    if reasoning:
        lines.append("**Reasoning:**")
        lines.append("")
        lines.append(reasoning)
        lines.append("")

    findings = turn.get("findings", [])
    if findings:
        lines.append("**Findings:**")
        lines.append("")
        for f in findings:
            sev  = f.get("severity", "?")
            cat  = f.get("category", "?")
            ev   = f.get("evidence", "")
            det  = f.get("detail", "")
            marker = "🔴" if sev == "HIGH" else ("🟡" if sev == "MEDIUM" else ("🟢" if sev == "LOW" else "⚪"))
            lines.append(f"- {marker} **{sev}** `{cat}`")
            if ev:
                lines.append(f"  - *Evidence:* {ev}")
            if det:
                lines.append(f"  - *Detail:* {det}")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def _md_condition(name: str, cond: dict, expected: str) -> str:
    lines = []
    verdict = cond.get("verdict", "ERROR")
    correct = "YES ✓" if verdict == expected else "NO ✗"
    turns   = cond.get("turns_run", 0)
    elapsed = cond.get("elapsed_ms", 0)
    model   = cond.get("model", "?")
    extra   = cond.get("extra", {})
    converged = extra.get("converged", False)
    deltas    = extra.get("deltas", [])
    in_tok  = cond.get("total_tokens", {}).get("input", 0)
    out_tok = cond.get("total_tokens", {}).get("output", 0)

    lines.append(f"## {name}")
    lines.append("")
    lines.append(f"| | |")
    lines.append(f"|---|---|")
    lines.append(f"| **Model** | `{model}` |")
    lines.append(f"| **Verdict** | `{verdict}` |")
    lines.append(f"| **Correct** | {correct} |")
    lines.append(f"| **Turns run** | {turns} |")
    lines.append(f"| **Converged** | {converged} |")
    lines.append(f"| **Delta sequence** | `{deltas}` |")
    lines.append(f"| **Elapsed** | {elapsed:,} ms |")
    lines.append(f"| **Tokens** | {in_tok:,} in / {out_tok:,} out |")
    lines.append("")

    if cond.get("error"):
        lines.append(f"> ❌ ERROR: {cond['error']}")
        lines.append("")
        return "\n".join(lines)

    turn_log = cond.get("turn_log", [])
    if turn_log:
        lines.append(f"### Turn-by-Turn Reasoning")
        lines.append("")
        for i, turn in enumerate(turn_log, 1):
            lines.append(_md_turn(turn, i))

    return "\n".join(lines)


def generate_trace(result: dict, out_dir: Path) -> Path:
    scenario  = result["scenario_name"]
    expected  = result["expected_verdict"]
    ts        = result.get("timestamp", datetime.utcnow().isoformat() + "Z")
    conditions = result["conditions"]
    models    = result.get("models", {})

    md = []
    md.append(f"# Benchmark Trace — {scenario}")
    md.append("")
    md.append(f"**Run at:** {ts}  ")
    md.append(f"**Expected verdict:** `{expected}`  ")
    md.append(f"**Max turns:** {result.get('max_turns', 10)}  ")
    md.append(f"**Models:** GPT `{models.get('openai','?')}` · Claude `{models.get('anthropic','?')}` · Gemini `{models.get('google','?')}`")
    md.append("")
    md.append("---")
    md.append("")

    # Summary gate
    rows = [
        ("Solo GPT",    conditions["solo_openai"]),
        ("Solo Claude", conditions["solo_anthropic"]),
        ("Solo Gemini", conditions["solo_google"]),
        ("Holo Full",   conditions["holo_full"]),
    ]
    md.append("## Summary")
    md.append("")
    md.append("| Condition | Verdict | Correct | Turns | Converged | Elapsed |")
    md.append("|---|---|---|---|---|---|")
    for label, cond in rows:
        v = cond.get("verdict", "ERROR")
        correct = "YES ✓" if v == expected else "NO ✗"
        turns   = cond.get("turns_run", 0)
        extra   = cond.get("extra", {})
        conv    = extra.get("converged", False)
        elapsed = cond.get("elapsed_ms", 0)
        md.append(f"| {label} | `{v}` | {correct} | {turns} | {conv} | {elapsed:,} ms |")
    md.append("")
    md.append("---")
    md.append("")

    # Full condition traces
    md.append(_md_condition("Condition 1 — Solo GPT",    conditions["solo_openai"],    expected))
    md.append(_md_condition("Condition 2 — Solo Claude", conditions["solo_anthropic"], expected))
    md.append(_md_condition("Condition 3 — Solo Gemini", conditions["solo_google"],    expected))
    md.append(_md_condition("Condition 4 — Holo Full",   conditions["holo_full"],      expected))

    out_dir.mkdir(exist_ok=True)
    md_path   = out_dir / f"{scenario}_trace.md"
    json_path = out_dir / f"{scenario}_result.json"

    md_path.write_text("\n".join(md), encoding="utf-8")
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return md_path, json_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_with_trace.py <scenario.json>")
        sys.exit(1)

    scenario_path = sys.argv[1]
    result = run_benchmark(scenario_path)

    out_dir = Path("traces")
    md_path, json_path = generate_trace(result, out_dir)

    print(f"\n  Trace saved : {md_path}")
    print(f"  JSON saved  : {json_path}")


if __name__ == "__main__":
    main()
