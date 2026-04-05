"""
bot.py — Telegram bot for triggering Holo benchmark probe runs remotely.

Commands (send as plain text or /slash command):
  run_probe <scenario> [mode]

  mode options:
    gpt / quick  → solo OpenAI only (default — fastest, ~1-3 min)
    claude       → solo Anthropic only
    gemini       → solo Google only
    holo         → Holo full architecture only
    full         → all 4 conditions (slow, ~10-15 min)

  Examples:
    run_probe BEC-PHANTOM-DEP-003A
    run_probe BEC-PHANTOM-DEP-003A holo
    run_probe 13_the_threshold_gambit gpt-5.4
    /run_probe BEC-SUBTLE-003 claude

Required env vars:
  TELEGRAM_BOT_TOKEN        — from BotFather
  TELEGRAM_ALLOWED_CHAT_ID  — your personal Telegram chat ID (integer)
"""

import asyncio
import csv
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("holo.bot")

BOT_TOKEN       = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_CHAT_ID = int(os.environ["TELEGRAM_ALLOWED_CHAT_ID"])

LOG_FILE = Path("bot_probe_log.csv")


def _log_result(scenario_name: str, mode: str, r: dict):
    """Append probe result to a CSV log file on Railway."""
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario": scenario_name,
        "mode": mode,
        "verdict": r.get("verdict", "ERROR"),
        "expected": r.get("expected", "?"),
        "correct": r.get("correct", "?"),
        "turns": r.get("turns", "?"),
        "elapsed_s": round(r.get("elapsed_s", 0), 1),
        "highs": "|".join(r.get("highs", [])),
        "error": r.get("error") or "",
    }
    write_header = not LOG_FILE.exists()
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)


SCENARIO_DIRS = [
    Path("examples/scenarios"),
    Path("examples/benchmark_library/scenarios"),
]

HELP_TEXT = (
    "Holo Probe Bot\n\n"
    "Usage: run_probe <scenario> [mode]\n\n"
    "Modes:\n"
    "  gpt / quick  — solo OpenAI (default, fastest)\n"
    "  claude       — solo Anthropic\n"
    "  gemini       — solo Google\n"
    "  holo         — Holo full architecture\n"
    "  full         — all 4 conditions (~10-15 min)\n\n"
    "Examples:\n"
    "  run_probe BEC-PHANTOM-DEP-003A\n"
    "  run_probe BEC-PHANTOM-DEP-003A holo\n"
    "  run_probe 13_the_threshold_gambit gpt-5.4"
)


# ---------------------------------------------------------------------------
# Scenario resolution
# ---------------------------------------------------------------------------

def _find_scenario(name: str) -> Path | None:
    """Find a scenario JSON by stem name (case-insensitive)."""
    name_lower = name.lower()
    for d in SCENARIO_DIRS:
        if not d.exists():
            continue
        for f in d.glob("*.json"):
            if f.stem.lower() == name_lower:
                return f
    return None


def _list_scenarios() -> list[str]:
    names = []
    for d in SCENARIO_DIRS:
        if not d.exists():
            continue
        names.extend(f.stem for f in sorted(d.glob("*.json")))
    return names


# ---------------------------------------------------------------------------
# Mode resolution
# ---------------------------------------------------------------------------

def _resolve_mode(mode_str: str) -> str:
    """Normalise the user's mode arg into one of: gpt, claude, gemini, holo, full."""
    m = mode_str.lower().strip()
    if m in ("", "quick", "gpt", "openai") or m.startswith("gpt-"):
        return "gpt"
    if m in ("claude", "anthropic", "sonnet") or m.startswith("claude-"):
        return "claude"
    if m in ("gemini", "google") or m.startswith("gemini-"):
        return "gemini"
    if m in ("holo", "holo_full"):
        return "holo"
    if m == "full":
        return "full"
    raise ValueError(
        f"Unknown mode: '{mode_str}'\n"
        "Valid: gpt (default), claude, gemini, holo, full"
    )


# ---------------------------------------------------------------------------
# Benchmark runner (blocking — called in thread pool)
# ---------------------------------------------------------------------------

def _run_probe_sync(scenario_path: Path, mode: str) -> dict:
    """
    Run one probe condition synchronously. Returns a result dict.
    Called from run_in_executor so it won't block the event loop.
    """
    import benchmark as bm
    from llm_adapters import OpenAIAdapter, AnthropicAdapter, GoogleAdapter

    scenario = json.loads(scenario_path.read_text())
    expected  = scenario.get("expected_verdict", "UNKNOWN").upper()
    start     = time.time()

    if mode == "gpt":
        adapter = OpenAIAdapter()
        r = bm.run_solo(scenario, adapter, "solo_openai")
        elapsed = time.time() - start
        return _format_solo(r, expected, elapsed)

    elif mode == "claude":
        adapter = AnthropicAdapter()
        r = bm.run_solo(scenario, adapter, "solo_anthropic")
        elapsed = time.time() - start
        return _format_solo(r, expected, elapsed)

    elif mode == "gemini":
        adapter = GoogleAdapter()
        r = bm.run_solo(scenario, adapter, "solo_google")
        elapsed = time.time() - start
        return _format_solo(r, expected, elapsed)

    elif mode == "holo":
        r = bm.run_holo_loop(scenario)
        elapsed = time.time() - start
        return _format_solo(r, expected, elapsed)

    elif mode == "full":
        result  = bm.run_benchmark(str(scenario_path))
        elapsed = time.time() - start
        return _format_full(result, elapsed)

    else:
        raise ValueError(f"Unknown mode: {mode}")


def _format_solo(r: dict, expected: str, elapsed: float) -> dict:
    verdict  = r.get("verdict", "ERROR")
    turns    = r.get("turns_run", "?")
    model    = r.get("model", "?")
    correct  = "✓" if verdict == expected else "✗"
    highs    = [
        cat for cat, sev in r.get("severity_flags", {}).items()
        if sev == "HIGH"
    ]
    mediums  = [
        cat for cat, sev in r.get("severity_flags", {}).items()
        if sev == "MEDIUM"
    ]
    error    = r.get("error")

    # Decision reason — governor's plain-English explanation of why it decided
    decision_reason = r.get("reasoning") or r.get("decision_reason") or ""

    # Turn audit — compact per-turn summary (holo mode only)
    turn_log = r.get("turn_log", [])
    turn_lines = []
    for t in turn_log:
        role    = (t.get("role") or "?")[:18]
        prov    = (t.get("provider") or "?")[:8]
        v       = t.get("verdict", "?")
        flags   = t.get("severity_flags", {})
        highs_t = [c[:3].upper() for c, s in flags.items() if s == "HIGH"]
        meds_t  = [c[:3].upper() for c, s in flags.items() if s == "MEDIUM"]
        flag_str = ""
        if highs_t:
            flag_str += f" H:{','.join(highs_t)}"
        if meds_t:
            flag_str += f" M:{','.join(meds_t)}"
        turn_lines.append(f"  T{t.get('turn_number','?')} {prov:<8} {role:<18} {v}{flag_str}")

    return {
        "mode":            model,
        "verdict":         verdict,
        "expected":        expected,
        "correct":         correct,
        "turns":           turns,
        "elapsed_s":       elapsed,
        "highs":           highs,
        "mediums":         mediums,
        "decision_reason": decision_reason,
        "turn_lines":      turn_lines,
        "tokens":          r.get("total_tokens", {}),
        "summary":         None,
        "error":           error,
    }


def _format_full(result: dict, elapsed: float) -> dict:
    conds    = result["conditions"]
    expected = result["expected_verdict"]
    models   = result.get("models", {})
    lines    = []
    for label, key, model_key in [
        ("Solo GPT",    "solo_openai",    "openai"),
        ("Solo Claude", "solo_anthropic", "anthropic"),
        ("Solo Gemini", "solo_google",    "google"),
        ("Holo Full",   "holo_full",      None),
    ]:
        c = conds.get(key)
        if c is None:
            continue
        v  = c.get("verdict", "ERROR")
        t  = c.get("turns_run", "?")
        ok = "✓" if v == expected else "✗"
        lines.append(f"  {label:<12} {v:<10} {ok}  ({t} turns)")

    holo = conds.get("holo_full") or {}

    # Holo turn audit for full mode
    turn_log   = holo.get("turn_log", [])
    turn_lines = []
    for t in turn_log:
        role    = (t.get("role") or "?")[:18]
        prov    = (t.get("provider") or "?")[:8]
        v       = t.get("verdict", "?")
        flags   = t.get("severity_flags", {})
        highs_t = [c[:3].upper() for c, s in flags.items() if s == "HIGH"]
        meds_t  = [c[:3].upper() for c, s in flags.items() if s == "MEDIUM"]
        flag_str = ""
        if highs_t:
            flag_str += f" H:{','.join(highs_t)}"
        if meds_t:
            flag_str += f" M:{','.join(meds_t)}"
        turn_lines.append(f"  T{t.get('turn_number','?')} {prov:<8} {role:<18} {v}{flag_str}")

    holo_highs = [
        cat for cat, sev in holo.get("severity_flags", {}).items()
        if sev == "HIGH"
    ]
    holo_mediums = [
        cat for cat, sev in holo.get("severity_flags", {}).items()
        if sev == "MEDIUM"
    ]

    return {
        "mode":            "full benchmark",
        "verdict":         holo.get("verdict", "—"),
        "expected":        expected,
        "correct":         "✓" if holo.get("verdict") == expected else "✗",
        "turns":           "—",
        "elapsed_s":       elapsed,
        "highs":           holo_highs,
        "mediums":         holo_mediums,
        "decision_reason": holo.get("reasoning", ""),
        "turn_lines":      turn_lines,
        "tokens":          holo.get("total_tokens", {}),
        "summary":         "\n".join(lines),
        "error":           holo.get("error"),
    }


# ---------------------------------------------------------------------------
# Message builder
# ---------------------------------------------------------------------------

def _build_reply(scenario_name: str, r: dict) -> str:
    elapsed   = r["elapsed_s"]
    elapsed_s = (
        f"{int(elapsed // 60)}m {int(elapsed % 60)}s"
        if elapsed >= 60
        else f"{elapsed:.1f}s"
    )

    if r.get("error"):
        return (
            f"ERROR — {scenario_name}\n"
            f"Condition: {r['mode']}\n"
            f"{r['error']}"
        )

    lines = [
        f"Scenario: {scenario_name}",
        f"Condition: {r['mode']}",
        f"Expected:  {r['expected']}",
        f"Verdict:   {r['verdict']} {r['correct']}",
    ]

    if r["turns"] != "—":
        lines.append(f"Turns:     {r['turns']}")

    if r.get("highs"):
        lines.append(f"HIGH:      {', '.join(r['highs'])}")
    if r.get("mediums"):
        lines.append(f"MEDIUM:    {', '.join(r['mediums'])}")

    # Per-condition summary (full mode)
    if r.get("summary"):
        lines.append("")
        lines.append(r["summary"])

    # Holo turn-by-turn audit
    if r.get("turn_lines"):
        lines.append("")
        lines.append("Turn trace:")
        lines.extend(r["turn_lines"])

    # Governor decision reason
    if r.get("decision_reason"):
        lines.append("")
        lines.append(f"Why: {r['decision_reason']}")

    # Token burn
    tokens = r.get("tokens", {})
    if tokens:
        inp = tokens.get("input", 0)
        out = tokens.get("output", 0)
        lines.append(f"\nTokens:    {inp:,} in / {out:,} out")

    lines.append(f"Elapsed:   {elapsed_s}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Telegram handlers
# ---------------------------------------------------------------------------

def _is_authorized(update: Update) -> bool:
    return update.effective_chat.id == ALLOWED_CHAT_ID


async def handle_run_probe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_authorized(update):
        logger.warning("Rejected message from chat_id=%s", update.effective_chat.id)
        return

    text = (update.message.text or "").strip()

    # Strip leading command prefix
    for prefix in ("/run_probe", "run_probe"):
        if text.lower().startswith(prefix):
            text = text[len(prefix):].strip()
            break

    parts = text.split()

    if not parts:
        await update.message.reply_text(HELP_TEXT)
        return

    scenario_name = parts[0]
    mode_str      = parts[1] if len(parts) > 1 else "gpt"

    # Resolve mode
    try:
        mode = _resolve_mode(mode_str)
    except ValueError as e:
        await update.message.reply_text(str(e))
        return

    # Find scenario file
    scenario_path = _find_scenario(scenario_name)
    if scenario_path is None:
        await update.message.reply_text(
            f"Scenario not found: {scenario_name}\n\n"
            f"Available:\n" + "\n".join(f"  {s}" for s in _list_scenarios()[:20])
        )
        return

    mode_label = "full benchmark (all 4 conditions)" if mode == "full" else f"solo {mode}"
    await update.message.reply_text(
        f"Running {scenario_name} [{mode_label}]...\n"
        f"(full = ~10-15 min, single condition = ~1-3 min)"
        if mode == "full"
        else f"Running {scenario_name} [{mode_label}]..."
    )

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            None, _run_probe_sync, scenario_path, mode
        )
    except Exception as e:
        logger.exception("Benchmark run failed")
        await update.message.reply_text(f"Run failed: {e}")
        return

    _log_result(scenario_name, mode, result)
    await update.message.reply_text(_build_reply(scenario_name, result))


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_authorized(update):
        return
    await update.message.reply_text(HELP_TEXT)


async def handle_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_authorized(update):
        return
    names = _list_scenarios()
    await update.message.reply_text(
        f"Available scenarios ({len(names)}):\n\n"
        + "\n".join(f"  {n}" for n in names)
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # /run_probe command
    app.add_handler(CommandHandler("run_probe", handle_run_probe))
    # plain "run_probe ..." message
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r"(?i)^run_probe\b"),
            handle_run_probe,
        )
    )
    # /help and /list
    app.add_handler(CommandHandler("help", handle_help))
    app.add_handler(CommandHandler("list", handle_list))

    logger.info("Holo probe bot starting (polling mode)...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
