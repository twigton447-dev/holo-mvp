"""
run_fp_traces.py

Extracts complete verbatim governor traces for every FP run
(expected ALLOW, got ESCALATE) across all current-era scenarios.

No truncation on reasoning or briefs. Full turn-by-turn severity flags.
Full coverage matrix. Grouped by scenario so the pattern is visible.

Output: docs/benchmark/FP_TRACES_2026-05-28.md
"""

import json
import re
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).parent
SCAN_DIRS = [
    BASE / "benchmark_results",
    BASE / "private_materials_not_for_public_release" / "benchmark_results",
]
OUT = BASE / "docs" / "benchmark" / "FP_TRACES_2026-05-28.md"

ALLOW_SCENARIOS = {
    "AP-FP-DUP-INV-001",
    "IAM-FP-GEO-JUMP-001",
    "BEC-FP-SPINOFF-001",
    "AP-PRECISION-TRUEUP-001",
    "PE-CONSOLIDATION-PRECISION-FP-001",
    "DFARS-SOURCE-CONTROL-PRECISION-002",
}

def gov_version(extra: dict) -> str:
    if not extra:                                return "v1-bare"
    if "exit_reason" in extra:                   return "v3"
    if "shadow_verdict_excl_turn1" in extra:     return "v2b"
    if "governor_briefs" in extra:               return "v2"
    return "v1-bare"

def sev_bar(flags: dict) -> str:
    """One-line severity summary ordered HIGH→MEDIUM→LOW."""
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "NONE": 3}
    pairs = sorted(flags.items(), key=lambda x: order.get(x[1], 9))
    return "  ".join(f"{c}={s}" for c, s in pairs) if pairs else "(none)"

# ── Load all FP runs ──────────────────────────────────────────────────────────

fp_runs = []

for scan_dir in SCAN_DIRS:
    if not scan_dir.exists():
        continue
    for fpath in sorted(scan_dir.glob("**/*.json")):
        stem = fpath.stem
        m = re.match(r"bench_(\d{8})_(\d{6})_(.+?)(?:_new_baseline)?$", stem)
        if not m:
            continue
        run_date, run_time, slug = m.group(1), m.group(2), m.group(3)
        if slug not in ALLOW_SCENARIOS:
            continue
        try:
            with open(fpath) as f:
                data = json.load(f)
        except Exception:
            continue
        if "conditions" not in data:
            continue

        sc = data.get("scenario_name") or data.get("benchmark_id") or slug
        if sc not in ALLOW_SCENARIOS:
            sc = slug
        if sc not in ALLOW_SCENARIOS:
            continue

        expected = data.get("expected_verdict", "ALLOW")
        holo = (data.get("conditions") or {}).get("holo_full") or {}
        if not isinstance(holo, dict):
            continue

        verdict = holo.get("verdict")
        if verdict != "ESCALATE":          # only FPs
            continue

        extra      = holo.get("extra") or {}
        turn_log   = holo.get("turn_log") or []
        reasoning  = holo.get("reasoning", "") or ""

        period = "pre-today" if run_date < "20260528" else "today"

        fp_runs.append({
            "file":           stem,
            "date":           run_date,
            "time":           run_time,
            "period":         period,
            "scenario":       sc,
            "gov":            gov_version(extra),
            "turns_run":      holo.get("turns_run", len(turn_log)),
            "reasoning":      reasoning,
            "exit_reason":    extra.get("exit_reason", ""),
            "shadow_verdict": extra.get("shadow_verdict_excl_turn1", ""),
            "shadow_diverges":extra.get("shadow_diverges", False),
            "turn1_anchor":   extra.get("turn1_anchor_risk", ""),
            "extra_turn":     extra.get("extra_turn_forced_due_to_fast_shadow_divergence", False),
            "tier":           extra.get("tier", ""),
            "converged":      extra.get("converged", False),
            "coverage_matrix":extra.get("coverage_matrix", {}),
            "governor_briefs":extra.get("governor_briefs") or [],
            "threat_hyp":     extra.get("threat_hypothesis", ""),
            "turn_log":       turn_log,
        })

# Group by scenario, then by period
by_sc = defaultdict(lambda: {"pre-today": [], "today": []})
for r in fp_runs:
    by_sc[r["scenario"]][r["period"]].append(r)

sc_order = [
    "BEC-FP-SPINOFF-001",
    "AP-FP-DUP-INV-001",
    "IAM-FP-GEO-JUMP-001",
    "AP-PRECISION-TRUEUP-001",
    "PE-CONSOLIDATION-PRECISION-FP-001",
    "DFARS-SOURCE-CONTROL-PRECISION-002",
]

print(f"Total FP runs extracted: {len(fp_runs)}")
for sc in sc_order:
    pre = len(by_sc[sc]["pre-today"])
    tod = len(by_sc[sc]["today"])
    print(f"  {sc}: pre={pre}  today={tod}")

# ── Render ────────────────────────────────────────────────────────────────────

SEP = "\n" + "─" * 80 + "\n"

def render_run(r: dict, run_idx: int) -> list[str]:
    lines = []
    period_tag = "PRE-TODAY" if r["period"] == "pre-today" else "TODAY"
    lines.append(f"### Run {run_idx} | {period_tag} | `{r['date']}_{r['time']}` | gov=`{r['gov']}` | tier=`{r['tier'] or 'n/a'}`")
    lines.append("")
    lines.append(f"**exit_reason:** `{r['exit_reason'] or 'n/a'}`  "
                 f"**converged:** {r['converged']}  "
                 f"**turns_run:** {r['turns_run']}  "
                 f"**shadow:** `{r['shadow_verdict'] or 'n/a'}` (diverges={r['shadow_diverges']})  "
                 f"**turn1_anchor_risk:** `{r['turn1_anchor'] or 'n/a'}`  "
                 f"**extra_turn_forced:** {r['extra_turn']}")
    lines.append("")

    # Coverage matrix
    cov = r["coverage_matrix"]
    if cov:
        lines.append("**Coverage matrix at verdict:**")
        order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "NONE": 3}
        pairs = sorted(
            ((cat, v.get("max_severity", v) if isinstance(v, dict) else v)
             for cat, v in cov.items()),
            key=lambda x: order.get(x[1], 9)
        )
        for cat, sev in pairs:
            marker = " ◄" if sev in ("HIGH", "MEDIUM") else ""
            lines.append(f"  `{cat}`: {sev}{marker}")
        lines.append("")

    # Governor final reasoning (verbatim)
    lines.append("**Governor final reasoning (verbatim):**")
    lines.append("```")
    lines.append(r["reasoning"].strip() if r["reasoning"] else "(empty)")
    lines.append("```")
    lines.append("")

    # Threat hypothesis (if present)
    if r["threat_hyp"]:
        lines.append("**Threat hypothesis:**")
        lines.append("```")
        lines.append(r["threat_hyp"].strip())
        lines.append("```")
        lines.append("")

    # Turn log
    tl = r["turn_log"]
    if tl:
        lines.append(f"**Turn log ({len(tl)} turns):**")
        lines.append("")
        for t in tl:
            turn_n = t.get("turn_number", "?")
            role   = t.get("role", "?")
            model  = t.get("model_id", "?")
            tv     = t.get("verdict", "?")
            flags  = t.get("severity_flags") or {}
            treason= (t.get("reasoning") or "").strip()

            lines.append(f"#### Turn {turn_n} — {role}")
            lines.append(f"**model:** `{model}`  **verdict:** `{tv}`")
            if flags:
                lines.append(f"**severity flags:** {sev_bar(flags)}")
            lines.append("")
            if treason:
                lines.append("**reasoning:**")
                lines.append("```")
                lines.append(treason)
                lines.append("```")
            lines.append("")
    else:
        lines.append("_No turn log available._")
        lines.append("")

    # Governor briefs
    briefs = r["governor_briefs"]
    if briefs:
        lines.append(f"**Governor briefs ({len(briefs)}):**")
        lines.append("")
        for b in briefs:
            turn_for     = b.get("for_turn", "?")
            provider_for = b.get("for_provider", b.get("provider", ""))
            level        = b.get("convergence_level", "?")
            text         = (b.get("brief") or "").strip()
            lines.append(f"##### Brief → Turn {turn_for}"
                         + (f" ({provider_for})" if provider_for else "")
                         + f" | level={level}")
            lines.append("```")
            lines.append(text if text else "(empty)")
            lines.append("```")
            lines.append("")
    else:
        lines.append("_No governor briefs._")
        lines.append("")

    return lines

out_lines = []
out_lines.append("# FP Traces — Complete Verbatim Governor Logs")
out_lines.append("")
out_lines.append(f"**Total FP runs:** {len(fp_runs)}  ")
out_lines.append("**Scope:** All expected-ALLOW scenarios that returned ESCALATE.  ")
out_lines.append("**Sections:** One section per scenario. Within each: pre-today runs first, then today's.")
out_lines.append("")
out_lines.append("---")
out_lines.append("")

for sc in sc_order:
    sc_data = by_sc[sc]
    pre  = sc_data["pre-today"]
    tod  = sc_data["today"]
    total_fps = len(pre) + len(tod)
    if total_fps == 0:
        continue

    out_lines.append(f"## {sc}")
    out_lines.append("")
    out_lines.append(f"**Total FP runs: {total_fps}** ({len(pre)} pre-today, {len(tod)} today)")
    out_lines.append("")

    all_runs = pre + tod
    for i, r in enumerate(all_runs, 1):
        out_lines.extend(render_run(r, i))
        out_lines.append("---")
        out_lines.append("")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(out_lines), encoding="utf-8")
size_kb = OUT.stat().st_size // 1024
print(f"\nWritten: {OUT}  ({size_kb} KB, {len(out_lines)} lines)")
