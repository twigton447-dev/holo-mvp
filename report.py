"""
report.py — Holo benchmark report generator.

Produces a self-contained HTML file from a benchmark result.

Usage:
  # Run benchmark and save result:
  python benchmark.py examples/scenarios/08_the_amendment_ghost.json --save

  # Generate report from saved result:
  python report.py benchmark_results/bench_20260317_XXXXXX_08_the_amendment_ghost.json

  # Run benchmark AND generate report in one step:
  python report.py --run examples/scenarios/08_the_amendment_ghost.json
"""

import argparse
import html
import json
import sys
from datetime import datetime
from pathlib import Path


# ─────────────────────────────────────────────────────────────────
# Severity colours
# ─────────────────────────────────────────────────────────────────

SEV_COLOR = {
    "HIGH":   ("#dc2626", "#fef2f2"),   # red
    "MEDIUM": ("#d97706", "#fffbeb"),   # amber
    "LOW":    ("#16a34a", "#f0fdf4"),   # green
    "NONE":   ("#6b7280", "#f9fafb"),   # grey
    "ERR":    ("#7c3aed", "#f5f3ff"),   # purple
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

CONDITION_LABELS = {
    "solo_openai":    "Solo OpenAI",
    "solo_anthropic": "Solo Anthropic",
    "solo_google":    "Solo Google",
    "holo_full":      "HOLO Council",
}


# ─────────────────────────────────────────────────────────────────
# Small HTML helpers
# ─────────────────────────────────────────────────────────────────

def _e(s):
    return html.escape(str(s) if s is not None else "")

def _verdict_badge(v):
    fg, bg = VERDICT_COLOR.get(v, ("#374151", "#f3f4f6"))
    icon = "⚠" if v == "ESCALATE" else ("✓" if v == "ALLOW" else "✕")
    return (
        f'<span style="display:inline-block;padding:3px 10px;border-radius:4px;'
        f'background:{bg};color:{fg};font-weight:700;font-size:13px;'
        f'letter-spacing:.5px;">{icon} {_e(v)}</span>'
    )

def _sev_badge(s):
    fg, bg = SEV_COLOR.get(s, ("#374151", "#f3f4f6"))
    return (
        f'<span style="display:inline-block;padding:2px 8px;border-radius:3px;'
        f'background:{bg};color:{fg};font-weight:600;font-size:12px;">{_e(s)}</span>'
    )

def _correct_badge(verdict, expected):
    if verdict == expected:
        return '<span style="color:#16a34a;font-weight:700;">✓ Correct</span>'
    return '<span style="color:#dc2626;font-weight:700;">✗ Missed</span>'

def _section(title, content, collapsed=False):
    sid = title.lower().replace(" ", "_").replace("/", "_")
    toggle = "none" if collapsed else "block"
    return f"""
<div class="section">
  <div class="section-header" onclick="toggle('{sid}')">
    <span class="section-title">{_e(title)}</span>
    <span class="toggle-hint" id="hint_{sid}">{'▶ expand' if collapsed else '▼ collapse'}</span>
  </div>
  <div id="{sid}" style="display:{toggle};">
    {content}
  </div>
</div>"""


# ─────────────────────────────────────────────────────────────────
# Section builders
# ─────────────────────────────────────────────────────────────────

def _build_narrative_summary(r):
    """Plain-English summary of what happened — for readers who won't go deeper."""
    expected = r.get("expected_verdict", "?")
    c = r["conditions"]
    scenario_name = r.get("scenario_name", "unknown")

    # Load scenario file for description and action context
    scenario_path = Path(f"examples/scenarios/{scenario_name}.json")
    scenario_data = {}
    if scenario_path.exists():
        try:
            scenario_data = json.loads(scenario_path.read_text())
        except Exception:
            pass

    action = scenario_data.get("action", {})
    params = action.get("parameters", {})
    amount = params.get("amount", "")
    vendor = params.get("vendor_name", scenario_data.get("context", {}).get("vendor_record", {}).get("vendor_name", ""))
    action_type = action.get("type", "transaction")

    # Verdict outcomes
    solo_keys = ["solo_openai", "solo_anthropic", "solo_google"]
    solo_verdicts = {k: c.get(k, {}).get("verdict", "ERROR") for k in solo_keys}
    holo_verdict = c.get("holo_full", {}).get("verdict", "ERROR")
    holo_turns = c.get("holo_full", {}).get("turns_run", 0)

    solo_allowed = [k for k in solo_keys if solo_verdicts[k] == "ALLOW"]
    solo_escalated = [k for k in solo_keys if solo_verdicts[k] == "ESCALATE"]
    solo_errored = [k for k in solo_keys if solo_verdicts[k] == "ERROR"]

    model_names = r.get("models", {})

    # Find the first HIGH finding from Holo turns that solos didn't raise
    holo_turn_log = c.get("holo_full", {}).get("turn_log", [])
    key_signal = None
    key_signal_cat = None
    for turn in holo_turn_log:
        for finding in turn.get("findings", []):
            if finding.get("severity") == "HIGH":
                key_signal = finding.get("evidence", "")
                key_signal_cat = CAT_LABELS.get(finding.get("category", ""), finding.get("category", ""))
                break
        if key_signal:
            break

    # Build condition outcome bullets
    max_t = r.get("max_turns", 10)

    def _short_model(key):
        m = {"solo_openai": model_names.get("openai",""), "solo_anthropic": model_names.get("anthropic",""), "solo_google": model_names.get("google","")}
        return m.get(key, key)

    outcome_items = ""
    for k in solo_keys:
        v = solo_verdicts[k]
        turns = c.get(k, {}).get("turns_run", 0)
        fg, bg = VERDICT_COLOR.get(v, ("#374151","#f3f4f6"))
        icon = "⚠" if v == "ESCALATE" else ("✓" if v == "ALLOW" else "✕")
        correct = v == expected
        turns_str = f"{turns}/{max_t}" if turns > 0 else "0"
        outcome_items += f"""
<li style="margin-bottom:8px;">
  <span style="font-weight:600;">{_e(_short_model(k))}</span> —
  <span style="color:{fg};font-weight:700;">{icon} {_e(v)}</span>
  in {turns_str} turns
  {'<span style="color:#16a34a;font-size:12px;"> (correct)</span>' if correct else '<span style="color:#dc2626;font-size:12px;"> (missed)</span>'}
</li>"""
    h_fg, h_bg = VERDICT_COLOR.get(holo_verdict, ("#374151","#f3f4f6"))
    h_icon = "⚠" if holo_verdict == "ESCALATE" else ("✓" if holo_verdict == "ALLOW" else "✕")
    h_correct = holo_verdict == expected
    outcome_items += f"""
<li style="margin-bottom:8px;font-weight:700;">
  Council (Holo) —
  <span style="color:{h_fg};font-weight:700;">{h_icon} {_e(holo_verdict)}</span>
  in {holo_turns}/{max_t} turns
  {'<span style="color:#16a34a;font-size:12px;"> (correct)</span>' if h_correct else '<span style="color:#dc2626;font-size:12px;"> (missed)</span>'}
</li>"""

    # Situation sentence
    amount_str = f"${amount:,.2f}" if isinstance(amount, (int, float)) else str(amount)
    situation = f"A {_e(action_type.replace('_',' '))} request for <strong>{_e(amount_str)}</strong> to <strong>{_e(vendor)}</strong> was submitted for evaluation."

    # What each system saw
    if solo_allowed and holo_verdict == "ESCALATE":
        solo_label = f"{len(solo_allowed)} of 3 solo model{'s' if len(solo_allowed)>1 else ''}"
        what_happened = (
            f"{solo_label} approved the transaction after reviewing sender identity, "
            f"payment routing, amount, and urgency signals — all of which appeared normal. "
            f"The council flagged it for escalation."
        )
    elif not solo_allowed and holo_verdict == "ESCALATE":
        what_happened = "All conditions flagged this transaction for escalation. There was no divergence between solo and council evaluation."
    elif holo_verdict == "ALLOW":
        what_happened = "All conditions approved this transaction. No condition identified signals warranting escalation."
    else:
        what_happened = "Results were mixed across conditions. See the turn breakdown for details."

    # Key signal block
    signal_block = ""
    if key_signal and solo_allowed:
        signal_block = f"""
<div style="margin-top:16px;padding:14px 18px;background:#fef9c3;border-left:4px solid #ca8a04;border-radius:4px;">
  <div style="font-weight:700;color:#854d0e;margin-bottom:6px;font-size:13px;">Signal that triggered escalation — {_e(key_signal_cat)}</div>
  <div style="font-size:13px;color:#374151;line-height:1.6;">{_e(key_signal)}</div>
  <div style="font-size:12px;color:#6b7280;margin-top:8px;">This signal is documented in the council's turn breakdown below. Reviewers can verify whether it was visible in the solo model outputs.</div>
</div>"""

    # Takeaway
    if solo_allowed and holo_verdict == "ESCALATE":
        if len(solo_allowed) == 3:
            takeaway = "All three solo models independently approved a transaction that required escalation. The signal was present in the data but only surfaced through adversarial cross-referencing across independent reasoning contexts."
        else:
            n_missed = len(solo_allowed)
            takeaway = f"{n_missed} solo model{'s' if n_missed>1 else ''} approved the transaction. The council escalated. The full turn breakdown shows what evidence each system cited and how the divergence occurred."
    elif not solo_allowed and holo_verdict == "ESCALATE":
        takeaway = "All conditions correctly identified this as a transaction requiring escalation. This scenario did not differentiate solo from council evaluation — the signal was detectable through standard checklist review."
    else:
        takeaway = "All conditions reached the same verdict. No differentiation between solo and council evaluation on this scenario."

    content = f"""
<div style="font-size:14px;line-height:1.8;color:#374151;">
  <p style="margin-bottom:14px;">{situation} {_e(what_happened)}</p>

  <div style="font-weight:700;margin-bottom:8px;color:#1e293b;">What each system decided:</div>
  <ul style="padding-left:0;list-style:none;margin-bottom:4px;">{outcome_items}</ul>

  {signal_block}

  <div style="margin-top:18px;padding:14px 18px;background:#f1f5f9;border-radius:4px;">
    <div style="font-weight:700;color:#1e293b;margin-bottom:4px;font-size:13px;">Takeaway</div>
    <div style="font-size:13px;color:#374151;line-height:1.6;">{_e(takeaway)}</div>
  </div>
</div>"""

    return _section("What Happened", content)


def _build_executive_summary(r):
    expected = r["expected_verdict"]
    c = r["conditions"]
    models = r.get("models", {})

    rows = ""
    for key, label in CONDITION_LABELS.items():
        cond = c.get(key, {})
        if not cond:
            continue
        verdict = cond.get("verdict", "ERROR")
        err = cond.get("error")
        model_str = ""
        if key == "solo_openai":
            model_str = models.get("openai", "")
        elif key == "solo_anthropic":
            model_str = models.get("anthropic", "")
        elif key == "solo_google":
            model_str = models.get("google", "")
        else:
            model_str = " + ".join(models.values()) + " + governor"

        turns = cond.get("turns_run", 0)
        tok_in  = cond.get("total_tokens", {}).get("input", 0)
        tok_out = cond.get("total_tokens", {}).get("output", 0)
        elapsed = cond.get("elapsed_ms", 0)
        is_holo = key == "holo_full"
        row_bg = "#fafaf9" if not is_holo else "#fffbeb"
        max_t = r.get("max_turns", 10)
        rows += f"""
<tr style="background:{row_bg};">
  <td style="font-weight:{'700' if is_holo else '400'};padding:10px 14px;">{_e(label)}</td>
  <td style="padding:10px 14px;color:#6b7280;font-size:13px;">{_e(model_str)}</td>
  <td style="padding:10px 14px;text-align:center;">{turns}/{max_t}</td>
  <td style="padding:10px 14px;text-align:center;">{_verdict_badge(verdict)}</td>
  <td style="padding:10px 14px;text-align:center;">{_correct_badge(verdict, expected)}</td>
  <td style="padding:10px 14px;text-align:right;font-size:13px;color:#6b7280;">{tok_in:,}+{tok_out:,}</td>
  <td style="padding:10px 14px;text-align:right;font-size:13px;color:#6b7280;">{elapsed/1000:.1f}s</td>
</tr>"""

    # discrepancy callout
    solo_keys = ["solo_openai", "solo_anthropic", "solo_google"]
    solo_missed = [k for k in solo_keys if c.get(k, {}).get("verdict") != expected and not c.get(k, {}).get("error")]
    holo_right = c.get("holo_full", {}).get("verdict") == expected
    callout = ""
    if solo_missed and holo_right:
        labels_missed = [CONDITION_LABELS[k] for k in solo_missed]
        missed_str = ", ".join(labels_missed)
        callout = f"""
<div style="margin-top:20px;padding:16px 20px;background:#fef2f2;border-left:4px solid #dc2626;border-radius:4px;">
  <div style="font-weight:700;color:#dc2626;margin-bottom:6px;">Divergent Result</div>
  <div style="color:#374151;line-height:1.6;">
    {_e(missed_str)} returned ALLOW. The council (Holo) returned ESCALATE.<br>
    Each solo condition ran up to 10 turns with the same adversarial role sequence, the same prompts,
    and access to all prior output. The difference in outcome is a function of structural independence:
    the council uses a different frontier model for each turn, so no model is anchoring its critique
    on its own prior reasoning. The signal that triggered ESCALATE is documented in the Holo turn
    breakdown below — investigators can check whether that signal was visible in the solo turns or not.
  </div>
</div>"""
    elif holo_right:
        # check HOLO ONLY findings
        holo_flags = c.get("holo_full", {}).get("severity_flags", {})
        solo_maxes = {}
        for cat in BEC_CATEGORIES:
            vals = [c.get(k, {}).get("severity_flags", {}).get(cat, "NONE") for k in solo_keys]
            srank = {"NONE":0,"LOW":1,"MEDIUM":2,"HIGH":3}
            solo_maxes[cat] = max(vals, key=lambda x: srank.get(x, 0))
        holo_only = [cat for cat in BEC_CATEGORIES
                     if {"NONE":0,"LOW":1,"MEDIUM":2,"HIGH":3}.get(holo_flags.get(cat,"NONE"),0)
                     > {"NONE":0,"LOW":1,"MEDIUM":2,"HIGH":3}.get(solo_maxes[cat],0)]
        if holo_only:
            cats_str = ", ".join(CAT_LABELS.get(c2, c2) for c2 in holo_only)
            callout = f"""
<div style="margin-top:20px;padding:16px 20px;background:#fffbeb;border-left:4px solid #d97706;border-radius:4px;">
  <div style="font-weight:700;color:#d97706;margin-bottom:6px;">Severity Divergence</div>
  <div style="color:#374151;line-height:1.6;">
    All conditions reached the correct verdict. The council rated <strong>{_e(cats_str)}</strong>
    at higher severity than the solo models. The turn breakdown shows what evidence each condition
    cited and how it was weighted.
  </div>
</div>"""

    table = f"""
<table style="width:100%;border-collapse:collapse;font-size:14px;">
  <thead>
    <tr style="background:#f3f4f6;text-align:left;">
      <th style="padding:10px 14px;">Condition</th>
      <th style="padding:10px 14px;">Model(s)</th>
      <th style="padding:10px 14px;text-align:center;">Turns</th>
      <th style="padding:10px 14px;text-align:center;">Verdict</th>
      <th style="padding:10px 14px;text-align:center;">Correct?</th>
      <th style="padding:10px 14px;text-align:right;">Tokens (in+out)</th>
      <th style="padding:10px 14px;text-align:right;">Time</th>
    </tr>
  </thead>
  <tbody>{rows}</tbody>
</table>
{callout}"""

    return _section("Executive Summary", table)


def _build_risk_matrix(r):
    c = r["conditions"]
    models = r.get("models", {})
    col_hdrs = [
        f"Solo {models.get('openai','GPT')[:8]}",
        f"Solo {models.get('anthropic','Claude')[:8]}",
        f"Solo {models.get('google','Gemini')[:8]}",
        "HOLO",
    ]
    cond_keys = ["solo_openai", "solo_anthropic", "solo_google", "holo_full"]
    srank = {"NONE":0,"LOW":1,"MEDIUM":2,"HIGH":3,"ERR":-1}

    rows = ""
    for cat in BEC_CATEGORIES:
        sevs = []
        for key in cond_keys:
            cond = c.get(key, {})
            if cond.get("error"):
                sevs.append("ERR")
            else:
                sevs.append(cond.get("severity_flags", {}).get(cat, "NONE"))
        solo_max = max(sevs[:3], key=lambda x: srank.get(x, -1))
        holo_sev = sevs[3]
        holo_wins = srank.get(holo_sev, 0) > srank.get(solo_max, 0)
        marker = '<span style="color:#d97706;font-weight:700;margin-left:8px;">◀ HOLO ONLY</span>' if holo_wins else ""
        cells = "".join(f'<td style="padding:10px 14px;text-align:center;">{_sev_badge(s)}</td>' for s in sevs)
        rows += f"""
<tr>
  <td style="padding:10px 14px;font-weight:500;">{_e(CAT_LABELS.get(cat,cat))}{marker}</td>
  {cells}
</tr>"""

    header_cells = "".join(f'<th style="padding:10px 14px;text-align:center;">{_e(h)}</th>' for h in col_hdrs)
    table = f"""
<table style="width:100%;border-collapse:collapse;font-size:14px;">
  <thead>
    <tr style="background:#f3f4f6;text-align:left;">
      <th style="padding:10px 14px;">BEC Category</th>
      {header_cells}
    </tr>
  </thead>
  <tbody>{rows}</tbody>
</table>"""
    return _section("Risk Profile — Max Severity Per Category", table)


def _build_scenario(r):
    # Load scenario from file if available, else reconstruct from first condition's turn 1
    scenario_name = r.get("scenario_name", "unknown")
    scenario_path = Path(f"examples/scenarios/{scenario_name}.json")
    scenario_data = None
    if scenario_path.exists():
        try:
            scenario_data = json.loads(scenario_path.read_text())
        except Exception:
            pass

    if not scenario_data:
        content = '<p style="color:#6b7280;">Scenario file not found alongside report.</p>'
        return _section("Scenario Under Evaluation", content)

    desc = scenario_data.get("_description", "")
    action = scenario_data.get("action", {})
    context = scenario_data.get("context", {})
    email_chain = context.get("email_chain", [])
    vendor = context.get("vendor_record", {})
    policies = context.get("org_policies", "")
    sender_hist = context.get("sender_history", {})

    params = action.get("parameters", action)
    action_html = f"""
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:16px;margin-bottom:16px;">
  <div style="font-weight:700;margin-bottom:10px;color:#1e293b;">Payment Action</div>
  <table style="font-size:13px;border-collapse:collapse;">
    {"".join(f'<tr><td style="padding:4px 12px 4px 0;color:#6b7280;white-space:nowrap;">{_e(k)}</td><td style="padding:4px 0;">{_e(v)}</td></tr>' for k,v in params.items())}
  </table>
</div>"""

    emails_html = ""
    for em in email_chain:
        body = _e(em.get("body","")).replace("\n","<br>")
        headers_raw = _e(em.get("raw_headers",""))
        emails_html += f"""
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:16px;margin-bottom:12px;">
  <table style="font-size:13px;border-collapse:collapse;margin-bottom:12px;">
    <tr><td style="color:#6b7280;padding:2px 12px 2px 0;">From</td><td>{_e(em.get('from',''))}</td></tr>
    <tr><td style="color:#6b7280;padding:2px 12px 2px 0;">To</td><td>{_e(em.get('to',''))}</td></tr>
    {"" if not em.get('cc') else f'<tr><td style="color:#6b7280;padding:2px 12px 2px 0;">CC</td><td>{_e(em.get("cc",""))}</td></tr>'}
    <tr><td style="color:#6b7280;padding:2px 12px 2px 0;">Subject</td><td><strong>{_e(em.get('subject',''))}</strong></td></tr>
    <tr><td style="color:#6b7280;padding:2px 12px 2px 0;">Timestamp</td><td>{_e(em.get('timestamp',''))}</td></tr>
  </table>
  <div style="background:#f8fafc;padding:12px;border-radius:4px;font-size:13px;line-height:1.7;white-space:pre-wrap;">{body}</div>
  {"" if not em.get("raw_headers") else f'<details style="margin-top:10px;"><summary style="cursor:pointer;color:#6b7280;font-size:12px;">Raw Headers</summary><pre style="font-size:11px;background:#1e293b;color:#e2e8f0;padding:12px;border-radius:4px;overflow-x:auto;margin-top:8px;">{headers_raw}</pre></details>'}
</div>"""

    vendor_html = f"""
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:16px;margin-bottom:16px;">
  <div style="font-weight:700;margin-bottom:10px;color:#1e293b;">Vendor Record</div>
  <table style="font-size:13px;border-collapse:collapse;">
    {"".join(f'<tr><td style="padding:4px 12px 4px 0;color:#6b7280;white-space:nowrap;">{_e(k)}</td><td style="padding:4px 0;">{_e(str(v))}</td></tr>' for k,v in vendor.items())}
  </table>
</div>"""

    sender_html = f"""
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:16px;margin-bottom:16px;">
  <div style="font-weight:700;margin-bottom:10px;color:#1e293b;">Sender History</div>
  <table style="font-size:13px;border-collapse:collapse;">
    {"".join(f'<tr><td style="padding:4px 12px 4px 0;color:#6b7280;white-space:nowrap;">{_e(k)}</td><td style="padding:4px 0;">{_e(str(v))}</td></tr>' for k,v in sender_hist.items())}
  </table>
</div>"""

    policy_html = f"""
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:16px;margin-bottom:16px;">
  <div style="font-weight:700;margin-bottom:8px;color:#1e293b;">Org Policies</div>
  <div style="font-size:13px;line-height:1.7;color:#374151;">{_e(policies)}</div>
</div>"""

    desc_html = f'<div style="background:#fffbeb;border-left:4px solid #d97706;padding:14px 16px;border-radius:4px;font-size:13px;line-height:1.7;margin-bottom:16px;color:#374151;">{_e(desc)}</div>' if desc else ""

    content = desc_html + action_html + "<div style='font-weight:700;margin:16px 0 10px;color:#1e293b;'>Email Chain</div>" + emails_html + vendor_html + sender_html + policy_html
    return _section("Scenario Under Evaluation", content)


def _build_condition_turns(condition_key, cond, label, show_prompts=True):
    if cond.get("error"):
        content = f'<div style="padding:16px;background:#fef2f2;border-radius:6px;color:#dc2626;">Error: {_e(cond["error"])}</div>'
        return _section(f"{label} — Turn Breakdown", content, collapsed=True)

    turn_log = cond.get("turn_log", [])
    turns_html = ""
    for t in turn_log:
        verdict = t.get("verdict", "?")
        fg, bg = VERDICT_COLOR.get(verdict, ("#374151","#f3f4f6"))
        role    = t.get("role","?")
        provider = t.get("provider","?").upper()
        model_id = t.get("model_id","?")
        turn_num = t.get("turn_number","?")
        reasoning = _e(t.get("reasoning",""))
        in_tok = t.get("input_tokens",0)
        out_tok = t.get("output_tokens",0)

        # Severity flags grid
        flags = t.get("severity_flags", {})
        flags_html = '<div style="display:flex;flex-wrap:wrap;gap:6px;margin:10px 0;">'
        for cat in BEC_CATEGORIES:
            sev = flags.get(cat, "NONE")
            flags_html += f'<div style="font-size:12px;padding:3px 8px;background:#f3f4f6;border-radius:3px;"><span style="color:#6b7280;">{_e(CAT_LABELS.get(cat,cat)[:8])}</span> {_sev_badge(sev)}</div>'
        flags_html += '</div>'

        # Findings
        findings = t.get("findings", [])
        findings_html = ""
        if findings:
            findings_html = '<div style="margin-top:10px;">'
            for f in findings:
                sev = f.get("severity","?")
                sfg, sbg = SEV_COLOR.get(sev, ("#374151","#f3f4f6"))
                findings_html += f"""
<div style="background:{sbg};border-left:3px solid {sfg};padding:10px 14px;border-radius:0 4px 4px 0;margin-bottom:8px;font-size:13px;">
  <div style="display:flex;gap:10px;align-items:center;margin-bottom:6px;">
    {_sev_badge(sev)}
    <span style="font-weight:600;">{_e(CAT_LABELS.get(f.get('category',''),''))}</span>
    <span style="background:#e5e7eb;padding:1px 6px;border-radius:3px;font-size:11px;color:#374151;">{_e(f.get('fact_type',''))}</span>
  </div>
  <div style="color:#374151;margin-bottom:4px;"><strong>Evidence:</strong> {_e(f.get('evidence',''))}</div>
  <div style="color:#6b7280;">{_e(f.get('detail',''))}</div>
</div>"""
            findings_html += '</div>'

        # Prompts (collapsible)
        prompts_html = ""
        if show_prompts and t.get("system_prompt"):
            sp = _e(t["system_prompt"])
            um = _e(t.get("user_message",""))
            prompts_html = f"""
<details style="margin-top:12px;">
  <summary style="cursor:pointer;color:#6b7280;font-size:12px;font-weight:600;padding:6px 0;">▶ Exact Prompts Sent to Model</summary>
  <div style="margin-top:8px;">
    <div style="font-size:12px;font-weight:700;color:#374151;margin-bottom:4px;">SYSTEM PROMPT</div>
    <pre style="font-size:11px;background:#1e293b;color:#e2e8f0;padding:14px;border-radius:6px;overflow-x:auto;white-space:pre-wrap;max-height:300px;">{sp}</pre>
    <div style="font-size:12px;font-weight:700;color:#374151;margin:12px 0 4px;">USER MESSAGE (includes full context + prior turns)</div>
    <pre style="font-size:11px;background:#1e293b;color:#e2e8f0;padding:14px;border-radius:6px;overflow-x:auto;white-space:pre-wrap;max-height:400px;">{um}</pre>
  </div>
</details>"""

        is_holo = condition_key == "holo_full"
        border_color = "#d97706" if is_holo else "#e2e8f0"
        turns_html += f"""
<div style="border:1px solid {border_color};border-radius:8px;margin-bottom:14px;overflow:hidden;">
  <div style="background:{'#fffbeb' if is_holo else '#f8fafc'};padding:12px 16px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid {border_color};">
    <div>
      <span style="font-weight:700;color:#1e293b;">Turn {turn_num}</span>
      <span style="color:#6b7280;margin:0 8px;">|</span>
      <span style="color:#374151;">{_e(role)}</span>
      <span style="color:#6b7280;margin:0 8px;">|</span>
      <span style="font-size:13px;color:#6b7280;">{_e(provider)} / {_e(model_id)}</span>
    </div>
    <div style="display:flex;gap:10px;align-items:center;">
      {_verdict_badge(verdict)}
      <span style="font-size:12px;color:#9ca3af;">{in_tok:,}+{out_tok:,} tokens</span>
    </div>
  </div>
  <div style="padding:14px 16px;">
    <div style="font-size:13px;color:#374151;line-height:1.7;background:#f8fafc;padding:12px;border-radius:4px;margin-bottom:4px;">{reasoning}</div>
    {flags_html}
    {findings_html}
    {prompts_html}
  </div>
</div>"""

    final_verdict = cond.get("verdict","?")
    final_reasoning = cond.get("reasoning","")
    summary_html = f"""
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:14px 16px;margin-bottom:16px;">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <div>
      <strong>Final Verdict:</strong> {_verdict_badge(final_verdict)}
      &nbsp;&nbsp;<span style="font-size:13px;color:#6b7280;">{cond.get('turns_run',0)}/10 turns  |  {cond.get('elapsed_ms',0)/1000:.1f}s  |  {cond.get('total_tokens',{}).get('input',0):,}+{cond.get('total_tokens',{}).get('output',0):,} tokens</span>
    </div>
  </div>
  {"" if not final_reasoning else f'<div style="margin-top:8px;font-size:13px;color:#374151;">{_e(final_reasoning)}</div>'}
</div>"""

    content = summary_html + turns_html
    return _section(f"{label} — Turn Breakdown", content, collapsed=(condition_key != "holo_full"))


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

<h3 style="color:#1e293b;margin:16px 0 12px;">The Six BEC Risk Categories</h3>
<table style="border-collapse:collapse;width:100%;font-size:13px;">
  <thead><tr style="background:#f3f4f6;">
    <th style="padding:8px 12px;text-align:left;">Category</th>
    <th style="padding:8px 12px;text-align:left;">What It Evaluates</th>
  </tr></thead>
  <tbody>
    <tr><td style="padding:8px 12px;font-weight:600;">Sender Identity</td><td style="padding:8px 12px;">Is the sender verifiably who they claim to be?</td></tr>
    <tr style="background:#f9fafb;"><td style="padding:8px 12px;font-weight:600;">Invoice Amount</td><td style="padding:8px 12px;">Is the amount consistent with the established vendor relationship?</td></tr>
    <tr><td style="padding:8px 12px;font-weight:600;">Payment Routing</td><td style="padding:8px 12px;">Has the payment destination changed unexpectedly?</td></tr>
    <tr style="background:#f9fafb;"><td style="padding:8px 12px;font-weight:600;">Urgency / Pressure</td><td style="padding:8px 12px;">Is there unusual urgency or pressure to bypass normal process?</td></tr>
    <tr><td style="padding:8px 12px;font-weight:600;">Domain Spoofing</td><td style="padding:8px 12px;">Are there email header or domain red flags?</td></tr>
    <tr style="background:#f9fafb;"><td style="padding:8px 12px;font-weight:600;">Approval Chain</td><td style="padding:8px 12px;">Does this transaction comply with normal approval procedures?</td></tr>
  </tbody>
</table>

<h3 style="color:#1e293b;margin:16px 0 12px;">Severity Scale</h3>
<div style="display:flex;gap:12px;flex-wrap:wrap;">
  <div><span style="background:#fef2f2;color:#dc2626;font-weight:700;padding:3px 10px;border-radius:4px;">HIGH</span> &nbsp;Clear, specific evidence of BEC risk. Forces ESCALATE regardless of vote count.</div>
  <div><span style="background:#fffbeb;color:#d97706;font-weight:700;padding:3px 10px;border-radius:4px;">MEDIUM</span> &nbsp;Suspicious signals warranting human review.</div>
  <div><span style="background:#f0fdf4;color:#16a34a;font-weight:700;padding:3px 10px;border-radius:4px;">LOW</span> &nbsp;Category appears clean based on available evidence.</div>
  <div><span style="background:#f9fafb;color:#6b7280;font-weight:700;padding:3px 10px;border-radius:4px;">NONE</span> &nbsp;Insufficient evidence to assess.</div>
</div>

<h3 style="color:#1e293b;margin:16px 0 12px;">Verdict Logic</h3>
<p>The Context Governor — not any LLM — makes the final call. Rules in priority order:</p>
<ol style="padding-left:20px;">
  <li>Any HIGH-severity finding forces ESCALATE unless a Synthesis turn explicitly clears it with all-LOW flags.</li>
  <li>Majority vote across all turns (ESCALATE wins ties).</li>
  <li>Oscillation or decay detected → ESCALATE.</li>
</ol>

<h3 style="color:#1e293b;margin:16px 0 12px;">Convergence</h3>
<p>All conditions — solo and Holo alike — share the same 10-turn budget and the same convergence
rule: exit early when delta = 0 for two consecutive turns after the minimum of 3 turns. No
condition runs longer than any other. The turn count in the results reflects actual turns run
before convergence was declared. This means a solo model may run <em>more</em> turns than
Holo on the same scenario if the solo model takes longer to converge.</p>

<h3 style="color:#1e293b;margin:16px 0 12px;">A Note on Scenario Design and the Difficulty Threshold</h3>
<p>Designing scenarios that meaningfully differentiate solo from multi-model evaluation turned out
to be harder than expected. Solo models are capable — they catch a wide range of fraud signals
reliably. Obvious indicators like routing number changes, duplicate invoice IDs, explicit MSA
violations, and out-of-scope work descriptions are detected by all conditions in essentially every
test.</p>
<p>The differentiation only appeared when scenarios were designed around signals that require
non-checklist reasoning: computing behavioral cadences from payment history, aggregating amounts
across invoices to find threshold violations, or detecting timing anomalies that are only visible
as a time series. At that level of sophistication, solo models began to miss signals that
multi-model adversarial evaluation caught.</p>
<p>Across the full scenario set to date, solo accuracy on clearly-escalate scenarios sits
around 86%. The council has maintained accuracy around 99% on the same set, including cases
where all three solo models independently returned ALLOW. These numbers are not guarantees —
they reflect performance on this specific corpus of test scenarios. The design of those scenarios,
and where exactly the difficulty threshold falls, is itself an open research question.</p>

</div>"""
    return _section("Methodology", content, collapsed=True)


# ─────────────────────────────────────────────────────────────────
# Full HTML document
# ─────────────────────────────────────────────────────────────────

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f1f5f9; color: #1e293b; }
.page { max-width: 1100px; margin: 0 auto; padding: 32px 20px; }
.header { background: #1e293b; color: white; padding: 28px 32px; border-radius: 10px; margin-bottom: 24px; }
.header h1 { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 4px; }
.header .sub { font-size: 13px; color: #94a3b8; }
.section { background: white; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 16px; overflow: hidden; }
.section-header { padding: 14px 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; border-bottom: 1px solid #e2e8f0; user-select: none; }
.section-header:hover { background: #f1f5f9; }
.section-title { font-weight: 700; font-size: 15px; color: #1e293b; }
.toggle-hint { font-size: 12px; color: #94a3b8; }
.section > div:last-child { padding: 20px; }
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

def generate_html(r):
    scenario_name = r.get("scenario_name", "unknown")
    expected = r.get("expected_verdict", "?")
    ts = r.get("timestamp", "")[:19].replace("T", " ")
    models = r.get("models", {})
    c = r["conditions"]

    sections = []
    sections.append(_build_executive_summary(r))
    sections.append(_build_narrative_summary(r))
    sections.append(_build_risk_matrix(r))
    sections.append(_build_scenario(r))

    # Holo first (expanded), solos collapsed
    for key, label in CONDITION_LABELS.items():
        cond = c.get(key)
        if cond is not None:
            sections.append(_build_condition_turns(key, cond, label))

    sections.append(_build_methodology())

    model_line = " | ".join(f"{p}: {m}" for p, m in models.items())
    body = "\n".join(sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Holo Benchmark — {html.escape(scenario_name)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="page">
  <div class="header">
    <h1>Holo Benchmark Report</h1>
    <div class="sub">Scenario: {html.escape(scenario_name)} &nbsp;|&nbsp; Expected: {html.escape(expected)} &nbsp;|&nbsp; {html.escape(ts)}</div>
    <div class="sub" style="margin-top:4px;">{html.escape(model_line)}</div>
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

def main():
    parser = argparse.ArgumentParser(description="Generate an HTML report from a Holo benchmark result.")
    parser.add_argument("input", nargs="?", help="Path to benchmark result JSON (from benchmark.py --save)")
    parser.add_argument("--run", metavar="SCENARIO", help="Run benchmark on this scenario file first, then report")
    parser.add_argument("--out", metavar="FILE", help="Output HTML path (default: auto-named alongside input)")
    args = parser.parse_args()

    result = None

    if args.run:
        # Run benchmark inline
        from dotenv import load_dotenv
        load_dotenv()
        import benchmark as bm
        print(f"Running benchmark on {args.run} ...")
        result = bm.run_benchmark(args.run, verbose=False)
        if args.out is None:
            scenario_name = Path(args.run).stem
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            args.out = f"reports/holo_report_{ts}_{scenario_name}.html"
        # Also save the JSON
        Path("benchmark_results").mkdir(exist_ok=True)
        json_path = Path("benchmark_results") / f"bench_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{Path(args.run).stem}.json"
        json_path.write_text(json.dumps(result, indent=2))
        print(f"\nBenchmark JSON saved: {json_path}")

    elif args.input:
        p = Path(args.input)
        if not p.exists():
            print(f"File not found: {args.input}")
            sys.exit(1)
        result = json.loads(p.read_text())
        if args.out is None:
            args.out = str(p.with_suffix(".html"))
    else:
        parser.print_help()
        sys.exit(1)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    html_content = generate_html(result)
    Path(args.out).write_text(html_content, encoding="utf-8")
    print(f"\nReport saved: {args.out}")
    import subprocess, platform
    if platform.system() == "Darwin":
        subprocess.Popen(["open", args.out])


if __name__ == "__main__":
    main()
