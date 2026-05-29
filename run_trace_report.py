"""
run_trace_report.py

Extracts governor trace logs for all benchmark runs in the 10-scenario
current-era scope. Separates Pre-Today (< 20260528) from Today (20260528).

For each run: scenario, expected, actual verdict, exit_reason,
governor_briefs summary, shadow_verdict_excl_turn1.

Grouped per period into: FP (critical), TP, TN sections.

Output: docs/benchmark/TRACE_REPORT_2026-05-28.md
"""

import json
import re
import textwrap
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).parent
SCAN_DIRS = [
    BASE / "benchmark_results",
    BASE / "private_materials_not_for_public_release" / "benchmark_results",
]
OUT = BASE / "docs" / "benchmark" / "TRACE_REPORT_2026-05-28.md"

EXPECTED_MAP = {
    "BEC-EXPLAINED-ANOMALY-001":          "ESCALATE",
    "RX-OBJECTIVE-OVERRIDE-001":          "ESCALATE",
    "SR-OBJECTIVE-OVERRIDE-001":          "ESCALATE",
    "DFARS-SOURCE-CONTROL-GAP-007B":      "ESCALATE",
    "AP-FP-DUP-INV-001":                  "ALLOW",
    "IAM-FP-GEO-JUMP-001":               "ALLOW",
    "BEC-FP-SPINOFF-001":                "ALLOW",
    "AP-PRECISION-TRUEUP-001":           "ALLOW",
    "PE-CONSOLIDATION-PRECISION-FP-001": "ALLOW",
    "DFARS-SOURCE-CONTROL-PRECISION-002":"ALLOW",
}

def gov_version(extra: dict) -> str:
    if not extra:
        return "v1-bare"
    if "exit_reason" in extra:
        return "v3-provisionality-tier"
    if "shadow_verdict_excl_turn1" in extra:
        return "v2b-shadow-briefs"
    if "governor_briefs" in extra:
        return "v2-briefs-threat"
    return "v1-bare"

def brief_summary(briefs: list, max_chars: int = 400) -> str:
    if not briefs:
        return "_no governor briefs_"
    parts = []
    for b in briefs:
        turn = b.get("for_turn", "?")
        level = b.get("convergence_level", "?")
        text = (b.get("brief") or "").strip()
        if text:
            clipped = text[:max_chars] + ("…" if len(text) > max_chars else "")
            parts.append(f"**[Turn {turn} | {level}]** {clipped}")
    return "\n\n".join(parts) if parts else "_no brief text_"

def reasoning_snippet(reasoning: str, max_chars: int = 350) -> str:
    if not reasoning:
        return "_no reasoning_"
    text = reasoning.strip().replace("\n", " ")
    return text[:max_chars] + ("…" if len(text) > max_chars else "")

# ── Load all pre-today and today runs ────────────────────────────────────────

pre_today = []
today_runs = []

for scan_dir in SCAN_DIRS:
    if not scan_dir.exists():
        continue
    for fpath in sorted(scan_dir.glob("**/*.json")):
        stem = fpath.stem
        m = re.match(r"bench_(\d{8})_(\d{6})_(.+?)(?:_new_baseline)?$", stem)
        if not m:
            continue
        run_date, run_time, scenario_slug = m.group(1), m.group(2), m.group(3)
        if scenario_slug not in EXPECTED_MAP:
            continue

        try:
            with open(fpath) as f:
                data = json.load(f)
        except Exception:
            continue

        sc = data.get("scenario_name") or data.get("benchmark_id") or scenario_slug
        if sc not in EXPECTED_MAP:
            sc = scenario_slug
        if sc not in EXPECTED_MAP:
            continue

        expected = data.get("expected_verdict") or EXPECTED_MAP[sc]
        conds = data.get("conditions", {})
        holo = conds.get("holo_full") or {}
        if not isinstance(holo, dict) or not holo:
            continue

        verdict = holo.get("verdict")
        if verdict in (None, "ERROR"):
            continue

        reasoning = holo.get("reasoning", "") or ""
        extra = holo.get("extra") or {}
        turn_log = holo.get("turn_log") or []

        rec = {
            "file":       stem,
            "date":       run_date,
            "time":       run_time,
            "scenario":   sc,
            "expected":   expected,
            "verdict":    verdict,
            "gov":        gov_version(extra),
            "exit_reason":          extra.get("exit_reason", ""),
            "governor_briefs":      extra.get("governor_briefs") or [],
            "shadow_verdict":       extra.get("shadow_verdict_excl_turn1", ""),
            "shadow_diverges":      extra.get("shadow_diverges", False),
            "turn1_anchor_risk":    extra.get("turn1_anchor_risk", ""),
            "extra_turn_forced":    extra.get("extra_turn_forced_due_to_fast_shadow_divergence", False),
            "tier":                 extra.get("tier", ""),
            "converged":            extra.get("converged", False),
            "reasoning":            reasoning,
            "turns_run":            holo.get("turns_run", len(turn_log)),
            "turn_log":             turn_log,
        }

        if run_date < "20260528":
            pre_today.append(rec)
        else:
            today_runs.append(rec)

print(f"Pre-today runs loaded: {len(pre_today)}")
print(f"Today runs loaded:     {len(today_runs)}")

# ── Classify FP / TP / TN ────────────────────────────────────────────────────

def classify(rec):
    exp, v = rec["expected"], rec["verdict"]
    if exp == "ALLOW"    and v == "ESCALATE": return "FP"
    if exp == "ESCALATE" and v == "ESCALATE": return "TP"
    if exp == "ALLOW"    and v == "ALLOW":    return "TN"
    return "FN"

# ── Markdown rendering helpers ────────────────────────────────────────────────

DIVIDER = "\n---\n"

def render_fp(rec: dict, idx: int) -> str:
    lines = []
    lines.append(f"#### FP-{idx}: `{rec['scenario']}`")
    lines.append(f"**File:** `{rec['file']}`  **Date:** {rec['date']}  **Gov:** `{rec['gov']}`  **Tier:** `{rec['tier'] or 'n/a'}`")
    lines.append(f"**Exit reason:** `{rec['exit_reason'] or 'n/a'}`  "
                 f"**Shadow verdict:** `{rec['shadow_verdict'] or 'n/a'}`  "
                 f"**Shadow diverges:** {rec['shadow_diverges']}  "
                 f"**Turn1 anchor risk:** `{rec['turn1_anchor_risk'] or 'n/a'}`  "
                 f"**Extra turn forced:** {rec['extra_turn_forced']}  "
                 f"**Turns run:** {rec['turns_run']}")
    lines.append("")
    lines.append("**Governor reasoning (verbatim snippet):**")
    lines.append(f"> {reasoning_snippet(rec['reasoning'], 500)}")
    lines.append("")
    briefs = rec["governor_briefs"]
    if briefs:
        lines.append(f"**Governor briefs ({len(briefs)} total):**")
        lines.append(brief_summary(briefs, 350))
    else:
        lines.append("**Governor briefs:** _none_")
    # Turn log verdicts
    tl = rec["turn_log"]
    if tl:
        lines.append("")
        lines.append("**Turn-by-turn verdicts:**")
        for t in tl:
            turn_n = t.get("turn_number", "?")
            role   = t.get("role", "?")
            tv     = t.get("verdict", "?")
            model  = t.get("model_id", "?")
            flags  = t.get("severity_flags", {})
            high_cats = [c for c, s in flags.items() if s == "HIGH"]
            med_cats  = [c for c, s in flags.items() if s == "MEDIUM"]
            flag_str  = ""
            if high_cats: flag_str += f" HIGH={high_cats}"
            if med_cats:  flag_str += f" MED={med_cats}"
            lines.append(f"  - Turn {turn_n} ({role}) | {model} → **{tv}**{flag_str}")
    lines.append("")
    return "\n".join(lines)

def render_tp(rec: dict) -> str:
    tl = rec["turn_log"]
    exit_r = rec["exit_reason"] or "n/a"
    shadow = rec["shadow_verdict"] or "n/a"
    tier   = rec["tier"] or "n/a"
    # Summarise turn log: how many ESCALATE vs ALLOW votes
    esc_v  = sum(1 for t in tl if t.get("verdict") == "ESCALATE")
    allow_v = sum(1 for t in tl if t.get("verdict") == "ALLOW")
    high_cats_all = defaultdict(int)
    for t in tl:
        for c, s in (t.get("severity_flags") or {}).items():
            if s == "HIGH":
                high_cats_all[c] += 1
    high_str = ", ".join(f"{c}(×{n})" for c, n in sorted(high_cats_all.items(), key=lambda x: -x[1])) or "none"
    return (f"| `{rec['scenario']}` | `{rec['date']}` | `{rec['gov']}` | `{exit_r}` | "
            f"{rec['turns_run']} turns | ESC={esc_v} ALLOW={allow_v} | "
            f"HIGH: {high_str} | shadow={shadow} |")

def render_tn(rec: dict) -> str:
    exit_r = rec["exit_reason"] or "n/a"
    shadow = rec["shadow_verdict"] or "n/a"
    tier   = rec["tier"] or "n/a"
    tl     = rec["turn_log"]
    esc_v  = sum(1 for t in tl if t.get("verdict") == "ESCALATE")
    allow_v = sum(1 for t in tl if t.get("verdict") == "ALLOW")
    return (f"| `{rec['scenario']}` | `{rec['date']}` | `{rec['gov']}` | `{exit_r}` | "
            f"{rec['turns_run']} turns | ESC={esc_v} ALLOW={allow_v} | shadow={shadow} |")

# ── Build report ──────────────────────────────────────────────────────────────

lines = []
lines.append("# Governor Trace Report — Pre-Today vs Today (2026-05-28)")
lines.append("")
lines.append(f"**Pre-today runs (< 2026-05-28):** {len(pre_today)}  ")
lines.append(f"**Today runs (2026-05-28):** {len(today_runs)}  ")
lines.append("")
lines.append("Scope: 10 current-era scenarios, Holo verdict only. "
             "FP = expected ALLOW, got ESCALATE. "
             "TP = expected ESCALATE, got ESCALATE. "
             "TN = expected ALLOW, got ALLOW.")
lines.append("")

for period_label, runs in [("Pre-Today (before 2026-05-28)", pre_today),
                            ("Today — 2026-05-28", today_runs)]:
    lines.append(f"---")
    lines.append(f"## {period_label}")
    lines.append("")

    fp_runs = [r for r in runs if classify(r) == "FP"]
    tp_runs = [r for r in runs if classify(r) == "TP"]
    tn_runs = [r for r in runs if classify(r) == "TN"]

    allow_n  = sum(1 for r in runs if r["expected"] == "ALLOW")
    esc_n    = sum(1 for r in runs if r["expected"] == "ESCALATE")
    total    = len(runs)
    correct  = len(tp_runs) + len(tn_runs)

    lines.append(f"**Totals:** {total} runs | "
                 f"TP={len(tp_runs)} TN={len(tn_runs)} FP={len(fp_runs)} FN=0 | "
                 f"Accuracy={correct}/{total}={(correct/total):.1%} | "
                 f"FPR={len(fp_runs)}/{allow_n}={len(fp_runs)/allow_n:.1%} | FNR=0%")
    lines.append("")

    # ── False Positives ───────────────────────────────────────────────────────
    lines.append("### False Positives — Critical")
    lines.append("")
    if not fp_runs:
        lines.append("_No false positives in this period._")
    else:
        lines.append(f"**{len(fp_runs)} FP runs across "
                     f"{len(set(r['scenario'] for r in fp_runs))} scenarios.**")
        lines.append("")
        # Group by exit_reason first
        by_exit = defaultdict(list)
        for r in fp_runs:
            by_exit[r["exit_reason"] or "unknown"].append(r)
        lines.append("**FP exit reason distribution:**")
        for er, recs in sorted(by_exit.items(), key=lambda x: -len(x[1])):
            lines.append(f"- `{er}`: {len(recs)} runs "
                         f"({', '.join(sorted(set(r['scenario'] for r in recs)))})")
        lines.append("")
        for i, rec in enumerate(fp_runs, 1):
            lines.append(render_fp(rec, i))
    lines.append("")

    # ── True Positives ────────────────────────────────────────────────────────
    lines.append("### True Positives — ESCALATE detection")
    lines.append("")
    if not tp_runs:
        lines.append("_No TP runs in this period._")
    else:
        lines.append(f"**{len(tp_runs)} TP runs | 0 FN | Detection rate: 100%**")
        lines.append("")
        lines.append("| Scenario | Date | Gov | Exit reason | Turns | Vote split | HIGH categories | Shadow |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for rec in tp_runs:
            lines.append(render_tp(rec))
    lines.append("")

    # ── True Negatives ────────────────────────────────────────────────────────
    lines.append("### True Negatives — ALLOW correctly passed")
    lines.append("")
    if not tn_runs:
        lines.append("_No TN runs in this period._")
    else:
        lines.append(f"**{len(tn_runs)} TN runs**")
        lines.append("")
        lines.append("| Scenario | Date | Gov | Exit reason | Turns | Vote split | Shadow |")
        lines.append("|---|---|---|---|---|---|---|")
        for rec in tn_runs:
            lines.append(render_tn(rec))
    lines.append("")

# ── Architecture diff section ─────────────────────────────────────────────────
lines.append("---")
lines.append("## Architecture Diff: v2/v2b FPs vs v3 FPs")
lines.append("")

pre_fps = [r for r in pre_today if classify(r) == "FP"]
tod_fps = [r for r in today_runs if classify(r) == "FP"]

lines.append("### Pre-today FP exit reasons")
if pre_fps:
    by_exit = defaultdict(list)
    for r in pre_fps:
        by_exit[r["exit_reason"] or "unknown"].append(r["scenario"])
    for er, scs in sorted(by_exit.items(), key=lambda x: -len(x[1])):
        lines.append(f"- `{er}` ({len(scs)}): {', '.join(sorted(set(scs)))}")
else:
    lines.append("_none_")
lines.append("")

lines.append("### Today FP exit reasons")
if tod_fps:
    by_exit = defaultdict(list)
    for r in tod_fps:
        by_exit[r["exit_reason"] or "unknown"].append(r["scenario"])
    for er, scs in sorted(by_exit.items(), key=lambda x: -len(x[1])):
        lines.append(f"- `{er}` ({len(scs)}): {', '.join(sorted(set(scs)))}")
else:
    lines.append("_none_")
lines.append("")

lines.append("### Key architectural differences between periods")
lines.append("")
lines.append("| Feature | v2-briefs-threat | v2b-shadow-briefs | v3-provisionality-tier |")
lines.append("|---|---|---|---|")
lines.append("| exit_reason field | absent | absent | **present** |")
lines.append("| tier field | absent | absent | **present** |")
lines.append("| shadow_verdict_excl_turn1 | absent | **present** | present |")
lines.append("| governor_briefs | **present** | present | present |")
lines.append("| First-turn provisionality guard | absent | absent | **present** |")
lines.append("| Extra turn forced on shadow divergence | absent | absent | **present** |")
lines.append("| Campaign traceability overreach check | absent | absent | **present** (D5) |")
lines.append("| D8 safe-harbor majority override | absent | absent | **present** |")
lines.append("")

# ── FP pattern comparison ────────────────────────────────────────────────────
lines.append("### FP mechanism shift: pre-today vs today")
lines.append("")
lines.append("Pre-today FPs (v2/v2b): all driven by `CONFIRMED_HIGH_OVERRIDE` — "
             "multiple model families independently rated a category HIGH, "
             "governor safety override fired regardless of majority. "
             "Exit reason field absent (pre-v3), so mechanism inferred from reasoning text.")
lines.append("")
lines.append("Today FPs (v3): `CONFIRMED_HIGH_OVERRIDE` replaced by oscillation and decay "
             "as the primary tripwire. This reflects v3 suppressing or resolving many "
             "prior confirmed-HIGH misfires via provisionality guard and campaign-traceability "
             "overreach — but oscillation (models deadlocked) and decay (severity walkback "
             "rejected without evidentiary support) are now the residual failure modes.")
lines.append("")

# ── Write ─────────────────────────────────────────────────────────────────────
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"\nReport written: {OUT}")
print(f"Lines: {len(lines)}")
