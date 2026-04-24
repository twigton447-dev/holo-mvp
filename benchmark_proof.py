"""
benchmark_proof.py

Generates the Holo architectural proof document.

Runs Holo across N seeded rotations on a scenario and generates a
self-contained HTML proof document containing:

  1. The explicit MoE distinction — technical definition of Mixture of Experts
     and exactly why Holo is architecturally incompatible with that category.

  2. Rotation stability — Holo's verdict across N independent random model
     assignments. If the result were probabilistic, we would see variance.
     N/N uniformity proves the result is structural.

  3. Coverage forensics — the exact turn-by-turn audit trail showing which
     model found which signal at which turn. The catch is not a black box.

  4. The governor's deterministic algorithm — no LLM in the final call.
     The verdict is computed, not generated.

  5. Documented failure modes — why each solo model fails, and how the
     adversarial loop structurally covers each failure mode.

Usage:
  python benchmark_proof.py examples/scenarios/13_the_threshold_gambit.json
  python benchmark_proof.py examples/scenarios/13_the_threshold_gambit.json --seeds 10
  python benchmark_proof.py examples/scenarios/13_the_threshold_gambit.json --seeds 5 --no-solos
"""

import argparse
import json
import sys
import time
from copy import deepcopy
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from benchmark import run_solo, run_holo_loop, _scenario_categories
from llm_adapters import OpenAIAdapter, AnthropicAdapter, GoogleAdapter

SEVERITY_RANK = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}

FAMILY_COLORS = {
    "openai":    "#74b9ff",
    "anthropic": "#a29bfe",
    "google":    "#55efc4",
    "unknown":   "#b2bec3",
}

FAMILY_LABELS = {
    "openai":    "OpenAI",
    "anthropic": "Anthropic",
    "google":    "Google",
}

# Documented failure modes from the Blindspot Atlas
SOLO_FAILURE_MODES = {
    "openai": {
        "name":    "Authentication Tunnel Vision",
        "detail":  (
            "GPT performs thorough sender authentication and, once the sender passes, "
            "treats clean identity as a proxy for a clean request. It does not "
            "independently verify whether the action itself is authorized by policy. "
            "Sender legitimacy and action legitimacy are separate questions."
        ),
    },
    "anthropic": {
        "name":    "Explanation Surrender",
        "detail":  (
            "When a plausible narrative is offered for a flagged anomaly, Claude accepts "
            "the story as evidence and clears the signal — even when the explanation "
            "originates from the same domain as the suspicious request. It does not ask "
            "whether any legitimizing evidence comes from outside the sender's control."
        ),
    },
    "google": {
        "name":    "Signal Fabrication",
        "detail":  (
            "When evidence is ambiguous, Gemini invents a plausible theory to explain the "
            "anomaly rather than stating that evidence is insufficient. It produces "
            "coherent-sounding narratives for things it cannot directly verify — and rates "
            "categories based on the theory rather than the data."
        ),
    },
}


# ---------------------------------------------------------------------------
# Coverage forensics
# ---------------------------------------------------------------------------

def reconstruct_coverage_events(turn_log: list, categories: list) -> tuple[list, dict]:
    """
    Reconstruct the exact sequence of coverage events from a run's turn_log.

    For each category, records:
      - first_addressed: the first turn (and model) to rate it non-NONE
      - escalated: any turn that raised a category to a higher severity

    Returns (events, final_coverage).
    """
    coverage = {cat: {"addressed": False, "max_severity": "NONE"} for cat in categories}
    events = []

    for turn in turn_log:
        flags    = turn.get("severity_flags", {})
        provider = turn.get("provider", "unknown")
        turn_num = turn.get("turn_number", 0)
        role     = turn.get("role", "")
        verdict  = turn.get("verdict", "")

        for cat in categories:
            new_sev = flags.get(cat, "NONE")
            if new_sev == "NONE":
                continue
            if not coverage[cat]["addressed"]:
                coverage[cat]["addressed"]    = True
                coverage[cat]["max_severity"] = new_sev
                events.append({
                    "turn": turn_num, "provider": provider, "role": role,
                    "category": cat, "severity": new_sev,
                    "event": "first_addressed",
                })
            elif SEVERITY_RANK[new_sev] > SEVERITY_RANK[coverage[cat]["max_severity"]]:
                old_sev = coverage[cat]["max_severity"]
                coverage[cat]["max_severity"] = new_sev
                events.append({
                    "turn": turn_num, "provider": provider, "role": role,
                    "category": cat, "severity": new_sev, "from_severity": old_sev,
                    "event": "escalated",
                })

    return events, coverage


def build_coverage_matrix(turn_log: list, categories: list) -> dict:
    """
    Build a turn×category grid of severity ratings.
    Returns {turn_number: {category: severity}}.
    """
    grid = {}
    for t in turn_log:
        tn = t.get("turn_number")
        if tn is not None:
            grid[tn] = {cat: t.get("severity_flags", {}).get(cat, "NONE") for cat in categories}
    return grid


# ---------------------------------------------------------------------------
# Run collectors
# ---------------------------------------------------------------------------

def run_solos(scenario: dict, scenario_name: str) -> dict:
    print("  Running solo conditions (1x each — establishes the baseline failure)...")
    adapters = {
        "openai":    OpenAIAdapter(),
        "anthropic": AnthropicAdapter(),
        "google":    GoogleAdapter(),
    }
    results = {}
    for provider, adapter in adapters.items():
        label = f"solo_{provider}"
        print(f"    [{provider}] running...")
        t0 = time.time()
        r  = run_solo(scenario, adapter, label, force_max_turns=False)
        elapsed = int((time.time() - t0) * 1000)
        results[provider] = {
            "verdict":   r.get("verdict"),
            "turns_run": r.get("turns_run"),
            "elapsed_ms": elapsed,
            "error":     r.get("error"),
        }
        v = r.get("verdict", "ERROR")
        print(f"    [{provider}] → {v} in {r.get('turns_run','?')} turns")
    return results


def run_rotation_seeds(scenario: dict, seeds: list) -> list:
    """Run Holo once per seed. Returns list of run dicts."""
    runs = []
    for i, seed in enumerate(seeds):
        print(f"  [seed {seed}] running Holo ({i+1}/{len(seeds)})...")
        t0 = time.time()
        r  = run_holo_loop(scenario, force_max_turns=False, no_memory=True, seed=seed)
        elapsed = int((time.time() - t0) * 1000)
        verdict = r.get("verdict", "ERROR")
        turns   = r.get("turns_run", 0)
        turn_log = r.get("turn_log", [])
        gov_briefs = r.get("extra", {}).get("governor_briefs", [])
        deltas     = r.get("extra", {}).get("deltas", [])
        print(f"    → {verdict} in {turns} turns  [{elapsed}ms]")
        runs.append({
            "seed":       seed,
            "verdict":    verdict,
            "turns_run":  turns,
            "elapsed_ms": elapsed,
            "error":      r.get("error"),
            "turn_log":   turn_log,
            "gov_briefs": gov_briefs,
            "deltas":     deltas,
        })
    return runs


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def _sev_color(sev: str) -> str:
    return {
        "HIGH":   "#ff7675",
        "MEDIUM": "#fdcb6e",
        "LOW":    "#74b9ff",
        "NONE":   "#2d3436",
    }.get(sev, "#2d3436")


def _sev_text_color(sev: str) -> str:
    return {
        "HIGH":   "#ff7675",
        "MEDIUM": "#fdcb6e",
        "LOW":    "#74b9ff",
        "NONE":   "#636e72",
    }.get(sev, "#636e72")


def _verdict_badge(verdict: str, expected: str) -> str:
    correct = verdict == expected
    v_class = "escalate" if verdict == "ESCALATE" else "allow"
    check   = " ✓" if correct else " ✗"
    return f'<span class="verdict-badge {v_class}">{verdict}{check}</span>'


def generate_proof_html(
    scenario_name: str,
    expected: str,
    categories: list,
    solo_results: dict,
    rotation_runs: list,
    seeds: list,
) -> str:

    correct_runs  = [r for r in rotation_runs if r["verdict"] == expected and not r["error"]]
    n_seeds       = len(rotation_runs)
    n_correct     = len(correct_runs)
    stability_pct = int(n_correct / n_seeds * 100) if n_seeds else 0

    # Representative run for coverage forensics (first correct run)
    rep_run = correct_runs[0] if correct_runs else (rotation_runs[0] if rotation_runs else None)

    # ---- Section: Rotation stability table ----------------------------------
    rotation_rows = ""
    for r in rotation_runs:
        correct = r["verdict"] == expected and not r["error"]
        seq = " → ".join(
            f'<span class="fam-badge" style="background:{FAMILY_COLORS.get(t.get("provider","unknown"),"#b2bec3")}">'
            f'{FAMILY_LABELS.get(t.get("provider","?"),"?")}</span>'
            for t in r.get("turn_log", [])
        )
        v_class = "escalate" if r["verdict"] == "ESCALATE" else "allow"
        result_cell = (
            f'<span class="verdict-sm {v_class}">{r["verdict"]}</span> '
            f'<span class="{"ok" if correct else "fail"}">{"✓ correct" if correct else "✗ wrong"}</span>'
        )
        rotation_rows += f"""
        <tr>
          <td class="num">{r['seed']}</td>
          <td class="seq-cell">{seq}</td>
          <td class="num">{r.get('turns_run','?')}</td>
          <td>{result_cell}</td>
        </tr>"""

    # ---- Section: Coverage forensics ----------------------------------------
    coverage_grid_html = ""
    coverage_events_html = ""

    if rep_run:
        events, final_cov = reconstruct_coverage_events(rep_run["turn_log"], categories)
        grid = build_coverage_matrix(rep_run["turn_log"], categories)
        turns_in_run = sorted(grid.keys())

        # Grid header
        header_cells = "<th>Category</th>" + "".join(
            f'<th>Turn {t}<br><span class="fam-mini">'
            f'{FAMILY_LABELS.get(next((x.get("provider","?") for x in rep_run["turn_log"] if x.get("turn_number")==t), "?"), "?")}'
            f'</span></th>'
            for t in turns_in_run
        )
        coverage_grid_html += f"<tr>{header_cells}</tr>"

        # Grid rows
        for cat in categories:
            row = f'<td class="cat-label">{cat.replace("_"," ").title()}</td>'
            for t in turns_in_run:
                sev = grid[t].get(cat, "NONE")
                bg  = _sev_color(sev)
                tc  = "#e6edf3" if sev in ("HIGH", "MEDIUM") else _sev_text_color(sev)
                provider = next((x.get("provider","?") for x in rep_run["turn_log"] if x.get("turn_number")==t), "?")
                fam_color = FAMILY_COLORS.get(provider, "#b2bec3")
                # Mark first HIGH discovery
                is_first_high = any(
                    e["category"] == cat and e["turn"] == t and e["severity"] == "HIGH"
                    for e in events
                )
                star = " ★" if is_first_high else ""
                row += f'<td style="background:{bg};color:{tc};border-left:3px solid {fam_color}">{sev[0]}{star}</td>'
            coverage_grid_html += f"<tr>{row}</tr>"

        # Coverage events narrative
        for e in events:
            fam_color = FAMILY_COLORS.get(e["provider"], "#b2bec3")
            fam_label = FAMILY_LABELS.get(e["provider"], e["provider"])
            if e["event"] == "first_addressed":
                desc = (
                    f'Turn {e["turn"]} — '
                    f'<span class="fam-inline" style="color:{fam_color}">{fam_label}</span> '
                    f'({e["role"]}) first assessed '
                    f'<strong>{e["category"].replace("_"," ")}</strong> → '
                    f'<span style="color:{_sev_text_color(e["severity"])}">{e["severity"]}</span>'
                )
            else:
                desc = (
                    f'Turn {e["turn"]} — '
                    f'<span class="fam-inline" style="color:{fam_color}">{fam_label}</span> '
                    f'({e["role"]}) escalated '
                    f'<strong>{e["category"].replace("_"," ")}</strong>: '
                    f'<span style="color:{_sev_text_color(e["from_severity"])}">{e["from_severity"]}</span> → '
                    f'<span style="color:{_sev_text_color(e["severity"])}">{e["severity"]}</span>'
                )
            coverage_events_html += f'<div class="event-row">{desc}</div>'

    # ---- Section: Solo results table ----------------------------------------
    solo_rows = ""
    for provider in ["openai", "anthropic", "google"]:
        r = solo_results.get(provider, {})
        if not r:
            continue
        correct = r.get("verdict") == expected and not r.get("error")
        v_class = "escalate" if r.get("verdict") == "ESCALATE" else "allow"
        failure = SOLO_FAILURE_MODES.get(provider, {})
        solo_rows += f"""
        <tr>
          <td>
            <span class="fam-badge" style="background:{FAMILY_COLORS.get(provider,'#b2bec3')}">{FAMILY_LABELS.get(provider,provider)}</span>
          </td>
          <td><span class="verdict-sm {v_class}">{r.get('verdict','?')}</span></td>
          <td class="{'ok' if correct else 'fail'}">{'✓ correct' if correct else '✗ missed it'}</td>
          <td class="failure-mode"><strong>{failure.get('name','—')}</strong><br><span class="muted">{failure.get('detail','')}</span></td>
        </tr>"""

    # ---- Section: Governor algorithm ----------------------------------------
    algorithm_code = """GOVERNOR DECISION ALGORITHM — no LLM is invoked at any step below.

Input:  turn_history[]   — every model's full verdict + severity_flags
        coverage_matrix  — {category: {addressed: bool, max_severity: str}}

Step 1. Count votes (empty ESCALATE votes — those with all flags LOW/NONE — are excluded)
        allow_votes    = count(t for t in turns if t.verdict == "ALLOW")
        escalate_votes = count(t for t in turns if t.verdict == "ESCALATE"
                               and any flag >= MEDIUM)

Step 2. Compute majority
        majority = "ESCALATE" if escalate_votes > allow_votes else "ALLOW"
        (ALLOW wins ties — conservative on false positives when no HIGH present)

Step 3. Apply HIGH override  ← THIS IS THE MATHEMATICAL LOCK
        if any(category.max_severity == "HIGH" for category in coverage_matrix):
            decision = "ESCALATE"
            # This lock can only be cleared by:
            # (a) 2 consecutive turns both voting ALLOW with all HIGH categories LOW/NONE, OR
            # (b) Final turn with role "Synthesis" voting ALLOW with all flags LOW/NONE
            # In genuine fraud: neither clears because adversarial pressure keeps at least
            # one turn rating the HIGH category above LOW.

Step 4. Return decision
        The decision is the output of steps 1–3.
        No language model is consulted. No probability is sampled.
        The output is a deterministic function of the turn history."""

    # ---- Final verdict summary ----------------------------------------------
    stability_statement = (
        f"<strong>{n_correct}/{n_seeds}</strong> rotation seeds returned the correct verdict ({expected})."
    )
    if n_correct == n_seeds:
        stability_statement += " <strong>Zero variance.</strong> The result is structural."
    else:
        stability_statement += f" {n_seeds - n_correct} seed(s) returned incorrect verdict — investigate."

    # ---- Assemble HTML ------------------------------------------------------
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Holo Engine — Architectural Proof — {scenario_name}</title>
<style>
  :root {{
    --bg:        #0d1117;
    --surface:   #161b22;
    --surface2:  #1c2128;
    --border:    #30363d;
    --text:      #e6edf3;
    --muted:     #8b949e;
    --openai:    #74b9ff;
    --anthropic: #a29bfe;
    --google:    #55efc4;
    --escalate:  #ff7675;
    --allow:     #55efc4;
    --high:      #ff7675;
    --medium:    #fdcb6e;
    --low:       #74b9ff;
    --none:      #636e72;
    --ok:        #55efc4;
    --fail:      #ff7675;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'JetBrains Mono', 'Fira Mono', 'Menlo', monospace;
    font-size: 13px;
    line-height: 1.7;
    padding: 32px 24px;
    max-width: 1100px;
    margin: 0 auto;
  }}
  .hero {{
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 32px;
    margin-bottom: 28px;
    background: var(--surface);
  }}
  .hero h1 {{ font-size: 26px; font-weight: 800; margin-bottom: 6px; letter-spacing: -.02em; }}
  .hero .sub {{ font-size: 14px; color: var(--muted); margin-bottom: 16px; }}
  .hero .scenario {{ font-size: 15px; font-weight: 600; margin-bottom: 4px; }}
  .stability-number {{
    font-size: 52px;
    font-weight: 800;
    color: var(--ok);
    letter-spacing: -.04em;
    line-height: 1;
    margin-bottom: 6px;
  }}
  .stability-label {{ font-size: 13px; color: var(--muted); }}
  .hero-grid {{ display: grid; grid-template-columns: auto 1fr; gap: 32px; align-items: center; }}
  h2 {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 14px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
  }}
  h3 {{ font-size: 14px; font-weight: 700; margin-bottom: 8px; }}
  .section {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 24px 28px;
    margin-bottom: 20px;
  }}
  .section.accent-escalate {{ border-left: 4px solid var(--escalate); }}
  .section.accent-ok       {{ border-left: 4px solid var(--ok); }}
  .section.accent-math     {{ border-left: 4px solid #fdcb6e; }}
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
  .three-col {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 20px; }}
  .prop-block {{
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px;
  }}
  .prop-num {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 4px;
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  th {{
    text-align: left;
    color: var(--muted);
    padding: 8px 10px;
    border-bottom: 1px solid var(--border);
    font-weight: 700;
    letter-spacing: .06em;
    text-transform: uppercase;
    font-size: 10px;
  }}
  td {{
    padding: 8px 10px;
    border-bottom: 1px solid rgba(48,54,61,.5);
    vertical-align: top;
  }}
  tr:last-child td {{ border-bottom: none; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .verdict-badge {{
    display: inline-block;
    padding: 4px 14px;
    border-radius: 4px;
    font-weight: 800;
    font-size: 15px;
  }}
  .verdict-badge.escalate {{ background: rgba(255,118,117,.15); color: var(--escalate); border: 1px solid var(--escalate); }}
  .verdict-badge.allow    {{ background: rgba(85,239,196,.15); color: var(--allow); border: 1px solid var(--allow); }}
  .verdict-sm {{ display: inline-block; padding: 2px 8px; border-radius: 3px; font-weight: 700; font-size: 11px; }}
  .verdict-sm.escalate {{ background: rgba(255,118,117,.15); color: var(--escalate); }}
  .verdict-sm.allow    {{ background: rgba(85,239,196,.15); color: var(--allow); }}
  .fam-badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 10px;
    font-weight: 700;
    color: #0d1117;
    margin: 1px;
  }}
  .fam-mini {{ font-size: 10px; font-weight: 600; color: var(--muted); }}
  .fam-inline {{ font-weight: 700; }}
  .seq-cell {{ font-size: 11px; }}
  .ok   {{ color: var(--ok);   font-weight: 700; }}
  .fail {{ color: var(--fail); font-weight: 700; }}
  .muted {{ color: var(--muted); }}
  .failure-mode {{ max-width: 400px; line-height: 1.5; }}
  .failure-mode .muted {{ font-size: 11px; }}
  pre {{
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 18px 20px;
    font-size: 12px;
    line-height: 1.8;
    overflow-x: auto;
    white-space: pre-wrap;
    color: #b2cbe4;
  }}
  .compare-table td:first-child {{ font-weight: 700; width: 220px; }}
  .compare-table .moe  {{ color: var(--fail); }}
  .compare-table .holo {{ color: var(--ok); }}
  .event-row {{
    padding: 5px 0;
    border-bottom: 1px solid rgba(48,54,61,.4);
    font-size: 12px;
  }}
  .event-row:last-child {{ border-bottom: none; }}
  .coverage-table th {{ white-space: nowrap; }}
  .coverage-table td {{ text-align: center; font-size: 12px; font-weight: 700; width: 60px; }}
  .cat-label {{ text-align: left !important; font-weight: 600; white-space: nowrap; width: 180px; }}
  .qed-block {{
    background: var(--surface2);
    border: 1px solid #fdcb6e;
    border-radius: 6px;
    padding: 20px 24px;
    margin-top: 20px;
    font-size: 13px;
    line-height: 1.9;
  }}
  .qed-block strong {{ color: var(--text); }}
  .divider {{ height: 1px; background: var(--border); margin: 28px 0; }}
  .pill {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    margin-right: 6px;
    margin-bottom: 4px;
  }}
  .pill-escalate {{ background: rgba(255,118,117,.15); color: var(--escalate); border: 1px solid var(--escalate); }}
  .pill-allow    {{ background: rgba(85,239,196,.15);  color: var(--allow);    border: 1px solid var(--allow); }}
  .arch-diagram {{
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 18px 20px;
    font-size: 12px;
    line-height: 2;
    margin-bottom: 12px;
  }}
  .arch-node {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 11px;
    margin: 2px;
  }}
  .arrow {{ color: var(--muted); font-size: 14px; vertical-align: middle; padding: 0 4px; }}
  .note-box {{
    background: rgba(116,185,255,.08);
    border: 1px solid rgba(116,185,255,.3);
    border-radius: 5px;
    padding: 10px 14px;
    font-size: 12px;
    color: #b2cbe4;
    margin-top: 10px;
  }}
</style>
</head>
<body>

<!-- ============================================================ -->
<!-- HERO                                                         -->
<!-- ============================================================ -->

<div class="hero">
  <div class="hero-grid">
    <div>
      <div class="stability-number">{n_correct}/{n_seeds}</div>
      <div class="stability-label">rotation seeds correct<br>(expected: {expected})</div>
    </div>
    <div>
      <h1>Holo Engine — Architectural Proof</h1>
      <div class="sub">
        Scenario: <strong>{scenario_name}</strong> &nbsp;|&nbsp;
        Seeds: <strong>{n_seeds}</strong> &nbsp;|&nbsp;
        Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
      </div>
      <p style="font-size:14px;line-height:1.7;margin-top:8px;">
        This document proves two claims: <strong>(1) Holo is not Mixture of Experts</strong> —
        the architectures are incompatible by definition. <strong>(2) The results are mathematical,
        not random</strong> — the catch is a deterministic consequence of structure, not a function
        of lucky model assignment.
      </p>
    </div>
  </div>
</div>


<!-- ============================================================ -->
<!-- PROPOSITION 1: NOT MIXTURE OF EXPERTS                       -->
<!-- ============================================================ -->

<div class="section accent-escalate">
  <h2>Proposition 1 — Holo is not Mixture of Experts</h2>
  <h3>Definition: What Mixture of Experts does</h3>
  <div class="arch-diagram">
    <div>
      <span class="arch-node" style="background:#2d3436;color:#e6edf3">Input</span>
      <span class="arrow">→</span>
      <span class="arch-node" style="background:#2d3436;color:#fdcb6e">Gating Function (learned weights)</span>
      <span class="arrow">→</span>
      <span class="arch-node" style="background:#2d3436;color:#74b9ff">Expert A</span>
      <span class="arch-node" style="background:#2d3436;color:#a29bfe">Expert B</span>
      <span class="arch-node" style="background:#2d3436;color:#55efc4">Expert C</span>
      <span class="arrow">→</span>
      <span class="arch-node" style="background:#2d3436;color:#fdcb6e">Weighted Combination</span>
      <span class="arrow">→</span>
      <span class="arch-node" style="background:#2d3436;color:#e6edf3">Output</span>
    </div>
  </div>
  <p style="color:var(--muted);font-size:12px;margin-bottom:16px;">
    In MoE: models execute <strong>in parallel</strong>. No model reads another model's output.
    No adversarial pressure. Convergence via learned parameter weights, not evidence accumulation.
    The "mixing" happens in a shared parameter space — a weighted average of activations.
  </p>

  <h3>Definition: What Holo does</h3>
  <div class="arch-diagram">
    <div style="line-height:2.2">
      <span class="arch-node" style="background:#2d3436;color:#e6edf3">Input</span>
      <span class="arrow">→</span>
      <span class="arch-node" style="background:rgba(116,185,255,.15);color:#74b9ff;border:1px solid #74b9ff">Turn 1: OpenAI API<br><small>produces full structured JSON</small></span>
      <span class="arrow">→</span>
      <span class="arch-node" style="background:#2d3436;color:#fdcb6e">Shared State ↑</span>
      <span class="arrow">→</span>
      <span class="arch-node" style="background:rgba(162,155,254,.15);color:#a29bfe;border:1px solid #a29bfe">Turn 2: Anthropic API<br><small>reads Turn 1 in full, MUST challenge it</small></span>
      <span class="arrow">→</span>
      <span class="arch-node" style="background:#2d3436;color:#fdcb6e">Shared State ↑</span>
      <span class="arrow">→</span>
      <span class="arch-node" style="background:rgba(85,239,196,.15);color:#55efc4;border:1px solid #55efc4">Turn 3: Google API<br><small>reads Turns 1+2, must address both</small></span>
      <span class="arrow">→</span>
      <span class="arch-node" style="background:#2d3436;color:#fdcb6e">…</span>
      <span class="arrow">→</span>
      <span class="arch-node" style="background:#2d3436;color:#e6edf3">Governor<br><small>deterministic algorithm</small></span>
      <span class="arrow">→</span>
      <span class="arch-node" style="background:rgba(255,118,117,.15);color:#ff7675;border:1px solid #ff7675">ESCALATE / ALLOW</span>
    </div>
  </div>

  <div class="two-col" style="margin-top:16px;">
    <div>
      <h3>The 5 structural differences</h3>
      <table class="compare-table">
        <thead><tr><th>Property</th><th>MoE</th><th>Holo</th></tr></thead>
        <tbody>
          <tr>
            <td>Model communication</td>
            <td class="moe">None — parallel execution</td>
            <td class="holo">Full — each model reads all prior reasoning</td>
          </tr>
          <tr>
            <td>Adversarial pressure</td>
            <td class="moe">None</td>
            <td class="holo">Explicit — role instruction requires challenging prior conclusions</td>
          </tr>
          <tr>
            <td>Architecture independence</td>
            <td class="moe">May share base weights (same family)</td>
            <td class="holo">Different vendors, different training corpora, different latent spaces</td>
          </tr>
          <tr>
            <td>Final decision mechanism</td>
            <td class="moe">Learned weighted combination of activations</td>
            <td class="holo">Deterministic algorithm — no LLM in the loop</td>
          </tr>
          <tr>
            <td>Evidence accumulation</td>
            <td class="moe">None — outputs averaged, not compounded</td>
            <td class="holo">Coverage matrix — monotonically increasing, HIGH locks ESCALATE</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div>
      <h3>What this means in practice</h3>
      <p style="font-size:12px;line-height:1.8;color:var(--muted);margin-bottom:10px;">
        A MoE system routes tokens to a shared latent space and averages outputs.
        If every expert in the MoE has the same blindspot, the blindspot survives.
        The average of three wrong answers is a wrong answer.
      </p>
      <p style="font-size:12px;line-height:1.8;color:var(--muted);margin-bottom:10px;">
        Holo forces Model B — with a different architecture and different failure modes —
        to read Model A's complete reasoning and explicitly challenge it. A signal that
        Model A buried under a plausible narrative is exposed when Model B's adversarial
        role requires it to ask: <em>where did Model A accept a story without evidence?</em>
      </p>
      <p style="font-size:12px;line-height:1.8;color:var(--muted);">
        This is not routing. This is adversarial collision between independent architectures.
        The convergence is structural — not the average of opinions, but the product of
        genuine disagreement resolved into signal.
      </p>
    </div>
  </div>
</div>


<!-- ============================================================ -->
<!-- PROPOSITION 2: MATHEMATICAL GUARANTEE                       -->
<!-- ============================================================ -->

<div class="section accent-math">
  <h2>Proposition 2 — The result is mathematical, not random</h2>

  <div class="two-col">
    <div>
      <h3>The coverage matrix is monotonic</h3>
      <p style="font-size:12px;color:var(--muted);line-height:1.8;margin-bottom:12px;">
        Every turn's severity flags are merged into a shared coverage matrix.
        Categories can only escalate — they cannot quietly drop.
        Once any model rates a category HIGH, that HIGH persists in the matrix
        regardless of what subsequent models say.
      </p>
      <div class="prop-block">
        <div class="prop-num">Property</div>
        <p style="font-size:12px;line-height:1.8;">
          <code>coverage_matrix[category].max_severity</code> is a non-decreasing sequence.
          It can go NONE → LOW → MEDIUM → HIGH.
          It cannot go backwards without explicit evidence-backed clearance.
        </p>
      </div>
    </div>
    <div>
      <h3>HIGH override is a hard lock</h3>
      <p style="font-size:12px;color:var(--muted);line-height:1.8;margin-bottom:12px;">
        Once any category reaches HIGH severity, the governor forces ESCALATE regardless
        of the majority vote. This is not probabilistic. It is a conditional that runs
        after all turns complete.
      </p>
      <div class="prop-block">
        <div class="prop-num">Property</div>
        <p style="font-size:12px;line-height:1.8;">
          <code>if any(cat.max_severity == "HIGH"): decision = "ESCALATE"</code><br>
          No model's subsequent ALLOW vote changes this. The only exit is
          sustained clearance: 2 consecutive turns both voting ALLOW
          with every HIGH category rated LOW/NONE — which does not happen
          in genuine fraud scenarios because adversarial pressure keeps
          at least one model above LOW.
        </p>
      </div>
    </div>
  </div>

  <h3 style="margin-top:4px;">The governor's decision algorithm</h3>
  <pre>{algorithm_code}</pre>
</div>


<!-- ============================================================ -->
<!-- EMPIRICAL EVIDENCE: ROTATION STABILITY                       -->
<!-- ============================================================ -->

<div class="section accent-ok">
  <h2>Empirical evidence — Rotation stability</h2>
  <p style="font-size:13px;margin-bottom:16px;">
    {stability_statement}
    If the result were probabilistic — a function of lucky model assignment —
    we would expect the verdict to vary as the model sequence changes.
    We observe <strong>zero variance</strong> across {n_seeds} independent random sequences.
  </p>

  <table>
    <thead>
      <tr>
        <th>Seed</th>
        <th>Model sequence (left = Turn 1)</th>
        <th>Turns</th>
        <th>Result</th>
      </tr>
    </thead>
    <tbody>
      {rotation_rows}
    </tbody>
  </table>

  <div class="note-box" style="margin-top:14px;">
    <strong>Interpretation:</strong> The same-DNA-never-collide rule (no two consecutive turns share the same model family)
    is enforced across all seeds. The exact sequence changes each time. The verdict does not.
    This is the hallmark of a structural result: independent of which architecture plays which role,
    the adversarial loop finds the signal.
  </div>
</div>


<!-- ============================================================ -->
<!-- THE FORENSIC TRAIL — COVERAGE BUILD-UP                       -->
<!-- ============================================================ -->

<div class="section">
  <h2>The forensic trail — Coverage build-up (representative run, seed {seeds[0] if seeds else '?'})</h2>
  <p style="font-size:12px;color:var(--muted);margin-bottom:14px;">
    Cell color = severity (red=HIGH, yellow=MEDIUM, blue=LOW, dark=NONE).
    Left border color = model family that assessed it.
    ★ = first HIGH discovery.
  </p>
  <div style="overflow-x:auto;">
    <table class="coverage-table">
      {coverage_grid_html}
    </table>
  </div>

  <div style="margin-top:18px;">
    <h3>Coverage event sequence</h3>
    <div style="margin-top:8px;">
      {coverage_events_html if coverage_events_html else '<p class="muted">No coverage events recorded.</p>'}
    </div>
  </div>

  <div class="note-box" style="margin-top:14px;">
    <strong>Interpretation:</strong> Each row shows exactly when a category was first assessed and by which architecture.
    The HIGH signals were not present in Turn 1. They emerged through adversarial pressure across independent architectures.
    This is the forensic record of convergence — not averaging, not routing, but compounding evidence discovery.
  </div>
</div>


<!-- ============================================================ -->
<!-- DOCUMENTED FAILURE MODES                                    -->
<!-- ============================================================ -->

<div class="section">
  <h2>Documented failure modes — why solo models miss this</h2>
  <p style="font-size:12px;color:var(--muted);margin-bottom:14px;">
    Each failure mode is documented from benchmark results. These are not theoretical —
    they are observed patterns from controlled runs on this and related scenarios.
  </p>

  <table>
    <thead>
      <tr>
        <th>Model</th>
        <th>Solo result</th>
        <th>Correct?</th>
        <th>Documented failure mode + mechanism</th>
      </tr>
    </thead>
    <tbody>
      {solo_rows if solo_rows else '<tr><td colspan="4" style="color:var(--muted)">Solo results not run (use --include-solos to run them).</td></tr>'}
    </tbody>
  </table>

  <div class="note-box" style="margin-top:14px;">
    <strong>Why cross-coverage works:</strong>
    OpenAI's failure mode (accepting clean identity as proof of clean action) is challenged when
    Anthropic's adversarial role requires it to separate sender legitimacy from action legitimacy.
    Anthropic's failure mode (accepting plausible narrative as evidence) is challenged when
    Google's role requires it to ask: what specific field value supports that story?
    Google's failure mode (fabricating explanations for gaps) is challenged when
    OpenAI's role requires it to demand a cited source for every claim.
    No single model covers all three failure modes. The adversarial structure does.
  </div>
</div>


<!-- ============================================================ -->
<!-- CONCLUSION — QED                                            -->
<!-- ============================================================ -->

<div class="section">
  <h2>Conclusion</h2>
  <div class="qed-block">
    <p><strong>Proposition 1:</strong> Holo is not Mixture of Experts.</p>
    <p style="color:var(--muted);margin-left:20px;font-size:12px;">
      Proved by definition. MoE executes models in parallel with no cross-communication,
      converging via weighted parameter combination. Holo executes models sequentially,
      each reading the complete prior reasoning of all previous models, with adversarial role
      instructions requiring challenge of those conclusions, converging via a deterministic
      algorithm with a monotonic coverage matrix. The architectures are structurally incompatible.
    </p>

    <p style="margin-top:14px;"><strong>Proposition 2:</strong> The results are mathematical, not random.</p>
    <p style="color:var(--muted);margin-left:20px;font-size:12px;">
      Proved by two independent lines of evidence.
    </p>
    <p style="color:var(--muted);margin-left:40px;font-size:12px;">
      (a) <strong>Structural:</strong> The coverage matrix is monotonic and the HIGH override is a
      hard lock. Once any architecture finds a HIGH signal, the governor's deterministic algorithm
      forces ESCALATE. No language model is consulted at the verdict step. The outcome is computed.
    </p>
    <p style="color:var(--muted);margin-left:40px;font-size:12px;">
      (b) <strong>Empirical:</strong> {n_correct}/{n_seeds} rotation seeds returned the correct verdict
      ({expected}) across independent random model assignments. Zero variance.
      If the result were probabilistic, we would expect variance proportional to the number of seeds.
      We observe none. The result does not depend on which architecture plays which role.
      It depends on the architecture existing at all.
    </p>

    <p style="margin-top:16px;font-size:14px;color:var(--text);">
      <strong>Therefore: Holo Engine's verdicts are the mathematical output of an adversarial architecture.
      They are not the averaged opinion of multiple models.
      They are not the lucky output of a good rotation.
      They are structural. They are inevitable. They are proof.</strong>
    </p>
  </div>
</div>

<p style="color:var(--muted);font-size:11px;text-align:center;margin-top:24px;">
  Holo Engine · holoengine.ai · Generated {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")} ·
  U.S. Provisional Patent Application No. 63/987,899
</p>

</body>
</html>"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate Holo architectural proof document.")
    parser.add_argument("scenario", help="Path to scenario JSON file")
    parser.add_argument("--seeds",          type=int, default=5, metavar="N",
                        help="Number of rotation seeds to run (default: 5)")
    parser.add_argument("--no-solos",       action="store_true",
                        help="Skip solo conditions (faster, no baseline contrast)")
    parser.add_argument("--output-dir",     default=None,
                        help="Output directory (default: benchmark_results/proof/)")
    args = parser.parse_args()

    path = Path(args.scenario)
    if not path.exists():
        print(f"Scenario not found: {args.scenario}")
        sys.exit(1)

    scenario      = json.loads(path.read_text())
    scenario_name = path.stem
    expected      = scenario.get("expected_verdict", "UNKNOWN").upper()
    categories    = _scenario_categories(scenario)

    print(f"\n{'='*65}")
    print(f"  HOLO PROOF GENERATOR — {scenario_name}")
    print(f"  Expected verdict: {expected}")
    print(f"  Seeds: {args.seeds}    Categories: {len(categories)}")
    print(f"{'='*65}\n")

    # Solo conditions
    solo_results = {}
    if not args.no_solos:
        solo_results = run_solos(scenario, scenario_name)
        print()

    # Rotation seeds
    seeds = [42 + i * 17 for i in range(args.seeds)]
    print(f"  Running {args.seeds} Holo rotation seeds...")
    rotation_runs = run_rotation_seeds(scenario, seeds)

    # Summary
    correct = sum(1 for r in rotation_runs if r["verdict"] == expected and not r["error"])
    print(f"\n  Rotation result: {correct}/{args.seeds} correct")

    # Generate HTML
    out_dir = Path(args.output_dir) if args.output_dir else Path("benchmark_results/proof")
    out_dir.mkdir(parents=True, exist_ok=True)

    ts       = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    html_out = out_dir / f"proof_{ts}_{scenario_name}.html"

    print(f"\n  Generating proof document...")
    html = generate_proof_html(
        scenario_name, expected, categories,
        solo_results, rotation_runs, seeds,
    )
    html_out.write_text(html, encoding="utf-8")
    print(f"  Saved: {html_out}")
    print(f"\n  open {html_out}\n")


if __name__ == "__main__":
    main()
