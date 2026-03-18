"""
combined_report.py — Holo multi-scenario combined benchmark report.

Produces a single self-contained HTML from all benchmark result JSONs in
benchmark_results/, or from an explicit list of files.

Usage:
  python combined_report.py                          # all JSONs in benchmark_results/
  python combined_report.py f1.json f2.json ...      # specific files
  python combined_report.py --out my_report.html     # custom output path
"""

import argparse
import html
import json
import sys
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────────
# Shared constants (mirrors report.py)
# ─────────────────────────────────────────────────────────────────

SEV_COLOR = {
    "HIGH":   ("#dc2626", "#fef2f2"),
    "MEDIUM": ("#d97706", "#fffbeb"),
    "LOW":    ("#16a34a", "#f0fdf4"),
    "NONE":   ("#6b7280", "#f9fafb"),
    "ERR":    ("#7c3aed", "#f5f3ff"),
}

VERDICT_COLOR = {
    "ESCALATE": ("#dc2626", "#fef2f2"),
    "ALLOW":    ("#16a34a", "#f0fdf4"),
    "ERROR":    ("#7c3aed", "#f5f3ff"),
}

BEC_CATEGORIES = [
    "sender_identity", "invoice_amount", "payment_routing",
    "urgency_pressure", "domain_spoofing", "approval_chain",
]

CAT_LABELS = {
    "sender_identity":  "Sender Identity",
    "invoice_amount":   "Invoice Amount",
    "payment_routing":  "Payment Routing",
    "urgency_pressure": "Urgency / Pressure",
    "domain_spoofing":  "Domain Spoofing",
    "approval_chain":   "Approval Chain",
}

CONDITION_KEYS  = ["solo_openai", "solo_anthropic", "solo_google", "holo_full"]
CONDITION_SHORT = {
    "solo_openai":    "GPT",
    "solo_anthropic": "Claude",
    "solo_google":    "Gemini",
    "holo_full":      "HOLO",
}

ATTACK_TAGS = {
    "11_the_long_game":        "Social Engineering",
    "12_the_override":         "Authority Bypass",
    "13_the_threshold_gambit": "Pattern Detection",
    "14_the_acquisition":      "Legal Entity Change",
    "15_the_night_watch":      "Behavioral Anomaly",
    "16_the_split":            "Financial Control Circumvention",
}

SCENARIO_SUBTITLES = {
    "11_the_long_game":        "A 3-email social engineering sequence plants a new contact before the invoice arrives. Every BEC check passes.",
    "12_the_override":         "The CISO 'pre-authorizes' skipping the PO process. Authority bypass with claimed executive sign-off.",
    "13_the_threshold_gambit": "Three consecutive invoices just under the $50K dual-approval threshold. Pattern invisible per-invoice.",
    "14_the_acquisition":      "Vendor claims a corporate acquisition changed their entity. Vendor record not updated.",
    "15_the_night_watch":      "Invoice sent at 9:47 PM Saturday — first after-hours email in 4 years of weekly business-hours sends.",
    "16_the_split":            "Supplemental $4,800 invoice paid 43 days ago + this $49,750 = $54,550 combined, over the $50K threshold.",
}

# ─────────────────────────────────────────────────────────────────
# HTML helpers
# ─────────────────────────────────────────────────────────────────

def _e(s):
    return html.escape(str(s) if s is not None else "")

def _verdict_badge(v, small=False):
    fg, bg = VERDICT_COLOR.get(v, ("#374151", "#f3f4f6"))
    icon = "⚠" if v == "ESCALATE" else ("✓" if v == "ALLOW" else "✕")
    sz = "11px" if small else "13px"
    pad = "2px 7px" if small else "3px 10px"
    return (
        f'<span style="display:inline-block;padding:{pad};border-radius:4px;'
        f'background:{bg};color:{fg};font-weight:700;font-size:{sz};'
        f'letter-spacing:.4px;">{icon} {_e(v)}</span>'
    )

def _sev_badge(s, small=False):
    fg, bg = SEV_COLOR.get(s, ("#374151", "#f3f4f6"))
    sz = "11px" if small else "12px"
    return (
        f'<span style="display:inline-block;padding:2px 7px;border-radius:3px;'
        f'background:{bg};color:{fg};font-weight:600;font-size:{sz};">{_e(s)}</span>'
    )

def _tag(text, color="#3b82f6"):
    return (
        f'<span style="display:inline-block;padding:2px 9px;border-radius:12px;'
        f'background:{color}18;color:{color};font-weight:600;font-size:11px;'
        f'border:1px solid {color}40;">{_e(text)}</span>'
    )

# ─────────────────────────────────────────────────────────────────
# Data helpers
# ─────────────────────────────────────────────────────────────────

def _cond(r, key):
    return r.get("conditions", {}).get(key, {})

def _verdict(r, key):
    return _cond(r, key).get("verdict", "ERROR")

def _turns(r, key):
    return _cond(r, key).get("turns_run", 0)

def _correct(r, key):
    return _verdict(r, key) == r.get("expected_verdict", "")

def _solo_keys(r):
    return [k for k in CONDITION_KEYS if k != "holo_full"]

def _scenario_label(name):
    # "11_the_long_game" -> "The Long Game"
    parts = name.split("_")
    # drop leading number
    if parts and parts[0].isdigit():
        parts = parts[1:]
    return " ".join(p.capitalize() for p in parts)

# ─────────────────────────────────────────────────────────────────
# Scorecard (top section)
# ─────────────────────────────────────────────────────────────────

def _build_scorecard(results):
    total = len(results)
    holo_correct = sum(1 for r in results if _correct(r, "holo_full"))
    solo_correct_any = sum(1 for r in results if any(_correct(r, k) for k in _solo_keys(r)))
    all_solo_missed = sum(1 for r in results if not any(_correct(r, k) for k in _solo_keys(r)))

    # per-model stats
    model_stats = {}
    for key in CONDITION_KEYS:
        correct = sum(1 for r in results if _correct(r, key))
        model_stats[key] = correct

    # stat boxes
    def stat_box(value, label, color="#1e293b"):
        return f"""
<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:20px 24px;text-align:center;flex:1;min-width:140px;">
  <div style="font-size:36px;font-weight:800;color:{color};">{value}</div>
  <div style="font-size:12px;color:#6b7280;margin-top:4px;line-height:1.4;">{label}</div>
</div>"""

    boxes = (
        stat_box(f"{holo_correct}/{total}", "HOLO Correct", "#16a34a") +
        stat_box(f"{all_solo_missed}/{total}", "Scenarios where<br>all solos missed", "#dc2626") +
        stat_box(f"{model_stats['solo_openai']}/{total}", "GPT Correct", "#6b7280") +
        stat_box(f"{model_stats['solo_anthropic']}/{total}", "Claude Correct", "#6b7280") +
        stat_box(f"{model_stats['solo_google']}/{total}", "Gemini Correct", "#6b7280")
    )

    proof_count = sum(1 for r in results if _correct(r, "holo_full") and not any(_correct(r, k) for k in _solo_keys(r)))

    banner = f"""
<div style="background:#fef2f2;border:2px solid #dc2626;border-radius:10px;padding:20px 24px;margin-top:20px;">
  <div style="font-size:16px;font-weight:800;color:#dc2626;margin-bottom:8px;">★ ARCHITECTURE PROOF</div>
  <div style="font-size:14px;color:#374151;line-height:1.7;">
    On <strong>{proof_count} of {total} scenarios</strong>, every solo model missed the threat — GPT, Claude, and Gemini all returned ALLOW
    with up to 10 turns each, convergence detection active, and the full adversarial role sequence.
    Holo caught all {holo_correct}. The irreducible variable is structural independence: three different frontier models
    per turn, no shared reasoning context, adversarial roles injected fresh each turn, governed by shared canonical state.
  </div>
</div>"""

    content = f"""
<div style="display:flex;gap:14px;flex-wrap:wrap;">{boxes}</div>
{banner}"""
    return _collapsible("Architecture Proof — All Scenarios", content, collapsed=False, accent="#dc2626")


# ─────────────────────────────────────────────────────────────────
# Master matrix
# ─────────────────────────────────────────────────────────────────

def _build_matrix(results):
    header_cells = '<th style="padding:10px 14px;text-align:left;">Scenario</th><th style="padding:10px 14px;">Attack Type</th>'
    for key in CONDITION_KEYS:
        label = CONDITION_SHORT[key]
        is_holo = key == "holo_full"
        weight = "800" if is_holo else "600"
        header_cells += f'<th style="padding:10px 14px;text-align:center;font-weight:{weight};">{_e(label)}</th>'

    rows = ""
    for r in results:
        name = r.get("scenario_name", "unknown")
        label = _scenario_label(name)
        tag_text = ATTACK_TAGS.get(name, "")
        tag_html = _tag(tag_text, "#6366f1") if tag_text else ""
        expected = r.get("expected_verdict", "ESCALATE")

        cells = f'<td style="padding:10px 14px;font-weight:600;">{_e(label)}</td>'
        cells += f'<td style="padding:10px 14px;">{tag_html}</td>'
        for key in CONDITION_KEYS:
            verdict = _verdict(r, key)
            correct = _correct(r, key)
            turns   = _turns(r, key)
            is_holo = key == "holo_full"
            bg = "#fffdf0" if is_holo else "white"
            miss = "" if correct else '<span style="font-size:10px;color:#dc2626;margin-left:4px;">✗</span>'
            cells += f'<td style="padding:10px 14px;text-align:center;background:{bg};">{_verdict_badge(verdict, small=True)}{miss}<br><span style="font-size:11px;color:#9ca3af;">{turns} turns</span></td>'

        rows += f"<tr style='border-bottom:1px solid #f1f5f9;'>{cells}</tr>"

    table = f"""
<table style="width:100%;border-collapse:collapse;font-size:13px;">
  <thead>
    <tr style="background:#f3f4f6;">{header_cells}</tr>
  </thead>
  <tbody>{rows}</tbody>
</table>"""
    return _collapsible("Scenario × Condition Matrix", table, collapsed=False)


# ─────────────────────────────────────────────────────────────────
# Per-scenario cards
# ─────────────────────────────────────────────────────────────────

def _build_scenario_cards(results):
    cards = ""
    for r in results:
        name     = r.get("scenario_name", "unknown")
        label    = _scenario_label(name)
        expected = r.get("expected_verdict", "ESCALATE")
        tag_text = ATTACK_TAGS.get(name, "")
        subtitle = SCENARIO_SUBTITLES.get(name, "")
        models   = r.get("models", {})

        # verdict row
        verdict_cells = ""
        for key in CONDITION_KEYS:
            cond    = _cond(r, key)
            verdict = _verdict(r, key)
            correct = _correct(r, key)
            turns   = _turns(r, key)
            is_holo = key == "holo_full"
            bg      = "#fffdf0" if is_holo else "#f8fafc"
            border  = "2px solid #d97706" if is_holo else "1px solid #e2e8f0"
            model_id = ""
            if key == "solo_openai":
                model_id = models.get("openai", "")
            elif key == "solo_anthropic":
                model_id = models.get("anthropic", "")
            elif key == "solo_google":
                model_id = models.get("google", "")
            else:
                model_id = "3-model council"
            correct_badge = (
                '<span style="font-size:11px;color:#16a34a;font-weight:700;">✓ correct</span>'
                if correct else
                '<span style="font-size:11px;color:#dc2626;font-weight:700;">✗ missed</span>'
            )
            verdict_cells += f"""
<div style="background:{bg};border:{border};border-radius:8px;padding:12px 14px;text-align:center;flex:1;min-width:120px;">
  <div style="font-size:11px;color:#6b7280;margin-bottom:6px;font-weight:600;">{_e(CONDITION_SHORT[key])}</div>
  <div style="margin-bottom:4px;">{_verdict_badge(verdict)}</div>
  <div style="font-size:11px;color:#9ca3af;">{turns} turns</div>
  <div style="margin-top:4px;">{correct_badge}</div>
  <div style="font-size:10px;color:#9ca3af;margin-top:2px;">{_e(model_id[:22])}</div>
</div>"""

        # holo turn trail
        holo_cond = _cond(r, "holo_full")
        trail_rows = ""
        for t in holo_cond.get("turn_log", []):
            tv = t.get("verdict", "?")
            fg, bg_c = VERDICT_COLOR.get(tv, ("#374151", "#f3f4f6"))
            role     = t.get("role", "?")
            provider = t.get("provider", "?").upper()
            tnum     = t.get("turn_number", "?")
            flags    = t.get("severity_flags", {})
            high_cats = [CAT_LABELS.get(c, c) for c, s in flags.items() if s == "HIGH"]
            high_html = ""
            if high_cats:
                high_html = ' &nbsp;' + " ".join(
                    f'<span style="font-size:10px;background:#fef2f2;color:#dc2626;padding:1px 6px;border-radius:3px;font-weight:700;">HIGH: {_e(c)}</span>'
                    for c in high_cats
                )
            trail_rows += f"""
<tr style="border-bottom:1px solid #f1f5f9;">
  <td style="padding:6px 10px;font-size:12px;color:#6b7280;white-space:nowrap;">Turn {tnum}</td>
  <td style="padding:6px 10px;font-size:12px;color:#6b7280;">{_e(provider)}</td>
  <td style="padding:6px 10px;font-size:12px;">{_e(role)}</td>
  <td style="padding:6px 10px;">{_verdict_badge(tv, small=True)}{high_html}</td>
</tr>"""

        trail_html = f"""
<div style="margin-top:16px;">
  <div style="font-size:12px;font-weight:700;color:#d97706;margin-bottom:8px;">HOLO TURN-BY-TURN</div>
  <table style="width:100%;border-collapse:collapse;font-size:12px;">
    <thead><tr style="background:#fffbeb;">
      <th style="padding:6px 10px;text-align:left;color:#6b7280;">Turn</th>
      <th style="padding:6px 10px;text-align:left;color:#6b7280;">Model</th>
      <th style="padding:6px 10px;text-align:left;color:#6b7280;">Role</th>
      <th style="padding:6px 10px;text-align:left;color:#6b7280;">Verdict</th>
    </tr></thead>
    <tbody>{trail_rows}</tbody>
  </table>
</div>""" if trail_rows else ""

        tag_html = _tag(tag_text, "#6366f1") if tag_text else ""
        subtitle_html = f'<div style="color:#6b7280;font-size:13px;margin-top:6px;line-height:1.5;">{_e(subtitle)}</div>' if subtitle else ""

        cards += f"""
<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:16px;overflow:hidden;">
  <div style="background:#f8fafc;padding:16px 20px;border-bottom:1px solid #e2e8f0;">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <span style="font-weight:800;font-size:16px;color:#1e293b;">{_e(label)}</span>
      {tag_html}
    </div>
    {subtitle_html}
  </div>
  <div style="padding:16px 20px;">
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:4px;">
      {verdict_cells}
    </div>
    {trail_html}
  </div>
</div>"""

    return _collapsible("Scenario Breakdown", cards, collapsed=False)


# ─────────────────────────────────────────────────────────────────
# Attack taxonomy summary
# ─────────────────────────────────────────────────────────────────

def _build_taxonomy(results):
    rows = ""
    for r in results:
        name     = r.get("scenario_name", "unknown")
        label    = _scenario_label(name)
        tag_text = ATTACK_TAGS.get(name, "—")
        subtitle = SCENARIO_SUBTITLES.get(name, "")
        proof    = _correct(r, "holo_full") and not any(_correct(r, k) for k in _solo_keys(r))
        proof_html = '<span style="color:#dc2626;font-weight:700;font-size:11px;">★ ALL SOLO MISSED</span>' if proof else ""
        rows += f"""
<tr style="border-bottom:1px solid #f1f5f9;">
  <td style="padding:10px 14px;font-weight:600;">{_e(label)}</td>
  <td style="padding:10px 14px;">{_tag(tag_text, '#6366f1')}</td>
  <td style="padding:10px 14px;font-size:13px;color:#374151;">{_e(subtitle)}</td>
  <td style="padding:10px 14px;">{proof_html}</td>
</tr>"""

    table = f"""
<table style="width:100%;border-collapse:collapse;font-size:13px;">
  <thead>
    <tr style="background:#f3f4f6;">
      <th style="padding:10px 14px;text-align:left;">Scenario</th>
      <th style="padding:10px 14px;text-align:left;">Attack Type</th>
      <th style="padding:10px 14px;text-align:left;">What Makes It Hard</th>
      <th style="padding:10px 14px;text-align:left;">Result</th>
    </tr>
  </thead>
  <tbody>{rows}</tbody>
</table>"""
    return _collapsible("BEC Attack Taxonomy", table, collapsed=False)


# ─────────────────────────────────────────────────────────────────
# Methodology (collapsed)
# ─────────────────────────────────────────────────────────────────

def _build_methodology():
    content = """
<div style="font-size:14px;line-height:1.8;color:#374151;">

<h3 style="color:#1e293b;margin:0 0 12px;">What Holo Is</h3>
<p>Holo is a multi-model adversarial council for evaluating Business Email Compromise risk.
Every evaluation cycles three frontier AI models — OpenAI, Anthropic, and Google — through
a sequence of adversarial analyst roles. No single model decides. The Context Governor holds
shared canonical state, detects convergence, and applies the final verdict rule.</p>

<h3 style="color:#1e293b;margin:16px 0 12px;">The Benchmark Design</h3>
<p>Each solo condition runs the <strong>identical role sequence</strong> as Holo — same adversarial prompts,
same turn structure, same scoring rubric. The <strong>only variable</strong> is structural independence:
solo conditions use the same model for all turns; Holo uses a different frontier model for each turn.</p>

<p>This is an apples-to-apples comparison. Solo Turn 2 reads Solo Turn 1's output and is explicitly
prompted to challenge it — exactly as Holo Turn 2 does. The difference is that a model
challenging its <em>own</em> prior reasoning is anchored to that reasoning. A different model has no anchor.</p>

<h3 style="color:#1e293b;margin:16px 0 12px;">Equal Turn Budget</h3>
<p>All conditions — solo and Holo alike — share the same 10-turn budget with identical convergence
detection: exit early when delta = 0 for two consecutive turns after the minimum of 3 turns.
If a solo model converges at turn 5 with ALLOW and Holo converges at turn 4 with ESCALATE,
the solo model had <em>more</em> turns, not fewer. The turn count in results reflects actual turns run.</p>

<h3 style="color:#1e293b;margin:16px 0 12px;">Verdict Logic</h3>
<ol style="padding-left:20px;">
  <li>Any HIGH-severity finding forces ESCALATE unless a Synthesis turn explicitly clears it.</li>
  <li>Majority vote across all turns (ESCALATE wins ties).</li>
  <li>Oscillation or decay detected → ESCALATE.</li>
</ol>

</div>"""
    return _collapsible("Methodology", content, collapsed=True)


# ─────────────────────────────────────────────────────────────────
# Collapsible section wrapper
# ─────────────────────────────────────────────────────────────────

_section_counter = [0]

def _collapsible(title, content, collapsed=False, accent=None):
    _section_counter[0] += 1
    sid = f"sec{_section_counter[0]}"
    display = "none" if collapsed else "block"
    hint = "▶ expand" if collapsed else "▼ collapse"
    border = f"border-left:4px solid {accent};" if accent else ""
    return f"""
<div class="section" style="{border}">
  <div class="section-header" onclick="toggle('{sid}')">
    <span class="section-title">{_e(title)}</span>
    <span class="toggle-hint" id="hint_{sid}">{hint}</span>
  </div>
  <div id="{sid}" style="display:{display};">
    <div style="padding:20px;">{content}</div>
  </div>
</div>"""


# ─────────────────────────────────────────────────────────────────
# Full HTML document
# ─────────────────────────────────────────────────────────────────

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f1f5f9; color: #1e293b; }
.page { max-width: 1200px; margin: 0 auto; padding: 32px 20px; }
.header { background: #1e293b; color: white; padding: 28px 32px; border-radius: 10px; margin-bottom: 24px; }
.header h1 { font-size: 26px; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 4px; }
.header .sub { font-size: 13px; color: #94a3b8; }
.section { background: white; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 16px; overflow: hidden; }
.section-header { padding: 14px 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; border-bottom: 1px solid #e2e8f0; user-select: none; }
.section-header:hover { background: #f1f5f9; }
.section-title { font-weight: 700; font-size: 15px; color: #1e293b; }
.toggle-hint { font-size: 12px; color: #94a3b8; }
.footer { text-align: center; color: #94a3b8; font-size: 12px; margin-top: 24px; padding: 16px; }
"""

JS = """
function toggle(id) {
  const el = document.getElementById(id);
  const hint = document.getElementById('hint_' + id);
  if (el.style.display === 'none') {
    el.style.display = 'block';
    hint.textContent = '▼ collapse';
  } else {
    el.style.display = 'none';
    hint.textContent = '▶ expand';
  }
}
"""

def generate_combined_html(results):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    n  = len(results)

    # reset section counter for idempotent runs
    _section_counter[0] = 0

    sections = [
        _build_scorecard(results),
        _build_matrix(results),
        _build_taxonomy(results),
        _build_scenario_cards(results),
        _build_methodology(),
    ]

    body = "\n".join(sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Holo — Combined Benchmark Report ({n} Scenarios)</title>
<style>{CSS}</style>
</head>
<body>
<div class="page">
  <div class="header">
    <h1>Holo Benchmark — Combined Report</h1>
    <div class="sub">{n} BEC scenarios &nbsp;|&nbsp; 10-turn equal budget &nbsp;|&nbsp; GPT-5.4 · Claude Sonnet 4.6 · Gemini 3.1 Pro vs. Holo Full Architecture</div>
    <div class="sub" style="margin-top:4px;">Generated {_e(ts)}</div>
  </div>
  {body}
  <div class="footer">Generated by Holo &mdash; Adversarial AI Trust Layer &mdash; Confidential</div>
</div>
<script>{JS}</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────

def _latest_per_scenario(directory):
    """Return the most recent benchmark JSON for each scenario name."""
    d = Path(directory)
    by_scenario = {}
    for p in sorted(d.glob("bench_*.json")):
        parts = p.stem.split("_", 2)  # bench, timestamp, scenario_name
        if len(parts) < 3:
            continue
        scenario = parts[2]
        by_scenario[scenario] = p  # sorted order means last write wins
    return list(by_scenario.values())


def main():
    parser = argparse.ArgumentParser(description="Generate a combined Holo benchmark HTML report.")
    parser.add_argument("files", nargs="*", help="Benchmark result JSON files (default: latest per scenario in benchmark_results/)")
    parser.add_argument("--dir", default="benchmark_results", help="Directory to scan (default: benchmark_results/)")
    parser.add_argument("--out", default=None, help="Output HTML path")
    args = parser.parse_args()

    if args.files:
        paths = [Path(f) for f in args.files]
    else:
        paths = _latest_per_scenario(args.dir)

    if not paths:
        print("No benchmark result files found.")
        sys.exit(1)

    results = []
    for p in paths:
        if not p.exists():
            print(f"Warning: {p} not found, skipping.")
            continue
        try:
            results.append(json.loads(p.read_text()))
        except Exception as e:
            print(f"Warning: could not parse {p}: {e}")

    if not results:
        print("No valid results loaded.")
        sys.exit(1)

    # Sort by scenario name for consistent ordering
    results.sort(key=lambda r: r.get("scenario_name", ""))

    out = args.out or f"benchmark_results/holo_combined_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(generate_combined_html(results), encoding="utf-8")
    print(f"Combined report saved: {out}")

    import subprocess, platform
    if platform.system() == "Darwin":
        subprocess.Popen(["open", out])


if __name__ == "__main__":
    main()
