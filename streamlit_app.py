"""Holo V1 MVP -- Streamlit Frontend.

Two-tab layout:
  Tab 1 - New Evaluation: demo scenario dropdown, form, live results
  Tab 2 - History: summary stats + evaluation log table

Run: streamlit run streamlit_app.py
Requires: FastAPI backend running on http://localhost:8000
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import requests
import streamlit as st

# ============================================================
# Configuration
# ============================================================

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_KEY = os.environ.get("HOLO_API_KEY", "demo")
SCENARIOS_DIR = Path(__file__).parent / "examples" / "scenarios"

# ============================================================
# Page Config (must be first Streamlit call)
# ============================================================

st.set_page_config(
    page_title="Holo Trust Layer",
    page_icon="\u2B21",  # hexagon
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Custom CSS + PWA Meta
# ============================================================

st.markdown("""
<style>
    /* ---- CSS Variables ---- */
    :root {
        --brass: #C9A84C;
        --brass-light: #E0C97A;
        --brass-dark: #9B7E2E;
        --allow-green: #2ECC71;
        --escalate-red: #E74C3C;
        --bg-card: #16181D;
        --border-subtle: #2A2D35;
    }

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background-color: #0a0c10;
        border-right: 1px solid var(--border-subtle);
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--brass);
        letter-spacing: 0.15em;
    }

    /* ---- Verdict Banners ---- */
    .verdict-allow {
        background: linear-gradient(135deg, #0d2818 0%, #1a4731 50%, #0d2818 100%);
        color: var(--allow-green);
        padding: 1.8rem 1rem;
        border-radius: 12px;
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 0.2em;
        border: 2px solid var(--allow-green);
        margin: 1rem 0 1.5rem 0;
        text-shadow: 0 0 20px rgba(46, 204, 113, 0.3);
    }
    .verdict-escalate {
        background: linear-gradient(135deg, #2a0a10 0%, #4a1520 50%, #2a0a10 100%);
        color: var(--escalate-red);
        padding: 1.8rem 1rem;
        border-radius: 12px;
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 0.2em;
        border: 2px solid var(--escalate-red);
        margin: 1rem 0 1.5rem 0;
        text-shadow: 0 0 20px rgba(231, 76, 60, 0.3);
    }

    /* ---- Risk Heatmap Cells ---- */
    .risk-cell {
        padding: 0.75rem 0.5rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 0.6rem;
        border: 1px solid var(--border-subtle);
    }
    .risk-cell .risk-label {
        font-size: 0.75rem;
        color: #888;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .risk-cell .risk-value {
        font-size: 1.1rem;
        font-weight: 700;
    }
    .risk-low {
        background-color: #0d2818;
        border-color: #1a4731;
    }
    .risk-low .risk-value { color: var(--allow-green); }
    .risk-medium {
        background-color: #2a2210;
        border-color: #4a3f1a;
    }
    .risk-medium .risk-value { color: var(--brass); }
    .risk-high {
        background-color: #2a0a10;
        border-color: #4a1520;
    }
    .risk-high .risk-value { color: var(--escalate-red); }
    .risk-none {
        background-color: var(--bg-card);
    }
    .risk-none .risk-value { color: #555; }

    /* ---- Stat Cards ---- */
    .stat-card {
        background-color: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 1.2rem 0.8rem;
        text-align: center;
    }
    .stat-card .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--brass);
        line-height: 1.2;
    }
    .stat-card .stat-label {
        color: #777;
        font-size: 0.8rem;
        margin-top: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ---- Section Headers ---- */
    .section-header {
        color: var(--brass);
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        border-bottom: 1px solid var(--border-subtle);
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }

    /* ---- Convergence Pill ---- */
    .converge-pill {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .converge-yes {
        background-color: #1a4731;
        color: var(--allow-green);
        border: 1px solid var(--allow-green);
    }
    .converge-no {
        background-color: #2a2210;
        color: var(--brass);
        border: 1px solid var(--brass-dark);
    }

    /* ---- Mobile Responsiveness ---- */
    @media (max-width: 768px) {
        .verdict-allow, .verdict-escalate {
            font-size: 1.5rem;
            padding: 1.2rem 0.8rem;
            letter-spacing: 0.1em;
        }
        .stat-card .stat-value { font-size: 1.4rem; }
        .risk-cell .risk-value { font-size: 0.95rem; }
    }

    /* ---- Hide Streamlit Hamburger & Footer ---- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ---- Slightly tighten default padding ---- */
    .block-container { padding-top: 2rem; }
</style>

<!-- PWA Manifest + Mobile Meta -->
<link rel="manifest" href="data:application/json;base64,eyJuYW1lIjoiSG9sbyBUcnVzdCBMYXllciIsInNob3J0X25hbWUiOiJIb2xvIiwic3RhcnRfdXJsIjoiLiIsInRoZW1lX2NvbG9yIjoiIzBFMTExNyIsImJhY2tncm91bmRfY29sb3IiOiIjMEUxMTE3IiwiZGlzcGxheSI6InN0YW5kYWxvbmUifQ==">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Holo">
<meta name="theme-color" content="#0E1117">
""", unsafe_allow_html=True)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.markdown("### HOLO")
    st.markdown("*Trust Layer for AI Agents*")
    st.markdown("---")

    # Connection status
    try:
        health = requests.get(f"{API_BASE}/health", timeout=3).json()
        st.markdown(
            f"\u25CF API Connected &nbsp; `v{health.get('version', '?')}`",
        )
    except Exception:
        st.markdown("\u25CB API Disconnected")
        st.caption(f"Expected at {API_BASE}")

    st.markdown("---")
    st.caption("v0.1.0 \u00B7 Patent Pending")


# ============================================================
# Load Demo Scenarios
# ============================================================

@st.cache_data
def load_scenarios() -> dict[str, dict | None]:
    """Load JSON scenario files from examples/scenarios/."""
    scenarios: dict[str, dict | None] = {"-- Select a demo scenario --": None}
    if SCENARIOS_DIR.exists():
        for f in sorted(SCENARIOS_DIR.glob("*.json")):
            try:
                with open(f) as fh:
                    data = json.load(fh)
                label = data.get("name", f.stem)
                expected = data.get("expected_decision", "")
                if expected:
                    label = f"{label}  \u2192  {expected}"
                scenarios[label] = data
            except json.JSONDecodeError:
                pass
    return scenarios


SCENARIOS = load_scenarios()


# ============================================================
# API Helper
# ============================================================

def call_evaluate(payload: dict) -> dict:
    """POST to /v1/evaluate_action and return parsed JSON."""
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    resp = requests.post(
        f"{API_BASE}/v1/evaluate_action",
        json=payload,
        headers=headers,
        timeout=130,
    )
    resp.raise_for_status()
    return resp.json()


def call_history() -> dict:
    """GET /v1/evaluations for the history dashboard."""
    headers = {"x-api-key": API_KEY}
    resp = requests.get(f"{API_BASE}/v1/evaluations", headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


# ============================================================
# Rendering Helpers
# ============================================================

CATEGORY_LABELS = {
    "sender_identity_verification": "Sender Identity",
    "invoice_amount_anomaly": "Invoice Amount",
    "payment_routing_change": "Payment Routing",
    "urgency_pressure_language": "Urgency / Pressure",
    "domain_spoofing_indicators": "Domain Spoofing",
    "approval_chain_compliance": "Approval Chain",
}


def render_verdict(decision: str):
    """Big verdict banner."""
    css_class = "verdict-allow" if decision == "ALLOW" else "verdict-escalate"
    icon = "\u2713" if decision == "ALLOW" else "\u26A0"
    st.markdown(
        f'<div class="{css_class}">{icon} &nbsp; {decision}</div>',
        unsafe_allow_html=True,
    )


def render_risk_heatmap(risk_profile: dict):
    """6-category risk heatmap grid (2 rows of 3)."""
    st.markdown('<div class="section-header">Risk Profile</div>', unsafe_allow_html=True)

    categories = list(risk_profile.items())
    for row_start in (0, 3):
        cols = st.columns(3)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx >= len(categories):
                break
            cat, info = categories[idx]
            sev = info.get("severity")
            addressed = info.get("addressed", False)
            label = CATEGORY_LABELS.get(cat, cat.replace("_", " ").title())

            if not addressed or sev is None:
                css_class = "risk-none"
                display = "N/A"
            else:
                css_class = f"risk-{sev.lower()}"
                display = sev

            with col:
                st.markdown(
                    f'<div class="risk-cell {css_class}">'
                    f'<div class="risk-label">{label}</div>'
                    f'<div class="risk-value">{display}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


def render_round_accordions(round_details: list):
    """Expandable accordion per round showing model, role, findings, severity."""
    st.markdown(
        '<div class="section-header">Round-by-Round Analysis</div>',
        unsafe_allow_html=True,
    )

    for rd in round_details:
        r_num = rd.get("round_number", "?")
        role = rd.get("role", "Unknown")
        provider = rd.get("model_provider", "?")
        model_id = rd.get("model_id", "?")
        verdict = rd.get("verdict", "?")
        reasoning = rd.get("reasoning_summary", "")
        findings = rd.get("findings", [])
        sev_flags = rd.get("severity_flags", {})
        in_tok = rd.get("input_tokens", 0)
        out_tok = rd.get("output_tokens", 0)
        cost = rd.get("cost_usd", 0)
        latency = rd.get("latency_ms", 0)

        verdict_color = "\U0001F7E2" if verdict == "ALLOW" else "\U0001F534"
        header = f"Round {r_num}: {role} ({provider}) {verdict_color} {verdict}"

        with st.expander(header, expanded=False):
            st.markdown(f"**Model:** `{model_id}`")
            st.markdown(f"**Verdict:** {verdict}")

            # Severity flags as inline badges
            if sev_flags:
                badges = []
                for cat, sev in sev_flags.items():
                    short = CATEGORY_LABELS.get(cat, cat)
                    if sev == "HIGH":
                        badges.append(f":red[**{short}: {sev}**]")
                    elif sev == "MEDIUM":
                        badges.append(f":orange[**{short}: {sev}**]")
                    else:
                        badges.append(f":green[{short}: {sev}]")
                st.markdown(" &nbsp;\u00B7&nbsp; ".join(badges))

            st.markdown("---")
            st.markdown(f"**Reasoning:** {reasoning}")

            # Findings
            if findings:
                st.markdown("**Findings:**")
                for f in findings:
                    sev = f.get("severity", "?")
                    cat_label = CATEGORY_LABELS.get(f.get("category", ""), f.get("category", ""))
                    detail = f.get("detail", "")
                    evidence = f.get("evidence", "")
                    if sev == "HIGH":
                        st.markdown(f"- :red[**{sev}**] **{cat_label}**: {detail}")
                    elif sev == "MEDIUM":
                        st.markdown(f"- :orange[**{sev}**] **{cat_label}**: {detail}")
                    else:
                        st.markdown(f"- :green[**{sev}**] **{cat_label}**: {detail}")
                    if evidence:
                        st.caption(f"  Evidence: {evidence}")

            # Metadata footer
            st.caption(
                f"Tokens: {in_tok:,} in / {out_tok:,} out &nbsp;\u00B7&nbsp; "
                f"Cost: ${cost:.4f} &nbsp;\u00B7&nbsp; "
                f"Latency: {latency:,}ms"
            )


def render_convergence(convergence_info: dict):
    """Convergence status pill."""
    converged = convergence_info.get("converged", False)
    total = convergence_info.get("total_rounds", 0)
    conv_round = convergence_info.get("convergence_round")
    deltas = convergence_info.get("deltas", [])

    if converged:
        pill_class = "converge-yes"
        text = f"\u2713 Converged at round {conv_round} of {total}"
    else:
        pill_class = "converge-no"
        text = f"\u2194 Did not converge in {total} round{'s' if total != 1 else ''}"

    st.markdown(
        f'<span class="converge-pill {pill_class}">{text}</span>'
        f' &nbsp; <span style="color:#555;font-size:0.8rem;">deltas: {deltas}</span>',
        unsafe_allow_html=True,
    )


def render_token_summary(token_usage: dict):
    """Token/cost summary row."""
    st.markdown(
        '<div class="section-header">Token Usage & Cost</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Input Tokens", f"{token_usage.get('total_input_tokens', 0):,}")
    with c2:
        st.metric("Output Tokens", f"{token_usage.get('total_output_tokens', 0):,}")
    with c3:
        st.metric("Total Cost", f"${token_usage.get('total_cost_usd', 0):.4f}")


# ============================================================
# Tab 1: New Evaluation
# ============================================================

tab_eval, tab_history = st.tabs(["\u2B21 New Evaluation", "\U0001F4CA History"])

with tab_eval:
    st.markdown("## Evaluate an Action")
    st.caption("Select a demo scenario or build your own payload. Holo runs a multi-model adversarial loop and returns ALLOW or ESCALATE.")

    # ---- Scenario Selector ----
    scenario_name = st.selectbox(
        "Demo Scenario",
        list(SCENARIOS.keys()),
        help="Pre-loaded BEC scenarios for one-click demos.",
    )
    scenario = SCENARIOS.get(scenario_name)

    if scenario:
        st.info(f"\U0001F4CB {scenario.get('description', '')}")

    # ---- Pre-fill form values from scenario ----
    if scenario:
        action_json = json.dumps(scenario["action"], indent=2)
        email_json = json.dumps(scenario["context"]["email_chain"], indent=2)
        vendor_json = json.dumps(
            scenario["context"].get("vendor_record") or {}, indent=2
        )
        sender_json = json.dumps(
            scenario["context"].get("sender_history") or {}, indent=2
        )
        org_text = scenario["context"].get("org_policies", "")
    else:
        action_json = json.dumps(
            {
                "type": "invoice_payment",
                "actor": {
                    "user": {"id": "", "email": "", "name": "", "role": ""},
                    "agent": {"id": "", "name": "", "type": ""},
                },
                "parameters": {
                    "amount": 0,
                    "currency": "USD",
                    "recipient_account": "",
                    "routing_number": "",
                    "invoice_id": "",
                    "due_date": "",
                    "vendor_name": "",
                    "payment_method": "",
                    "is_new_account": False,
                },
            },
            indent=2,
        )
        email_json = "[]"
        vendor_json = "{}"
        sender_json = "{}"
        org_text = ""

    # ---- Form Fields ----

    st.markdown(
        '<div class="section-header">Action Payload</div>',
        unsafe_allow_html=True,
    )
    action_input = st.text_area(
        "Action (JSON)",
        value=action_json,
        height=220,
        help="The proposed action the AI agent wants to execute.",
    )

    st.markdown(
        '<div class="section-header">Email Chain</div>',
        unsafe_allow_html=True,
    )
    email_input = st.text_area(
        "Email Chain (JSON array of message objects)",
        value=email_json,
        height=300,
        help='Array of { "from", "to", "subject", "body", "timestamp", "raw_headers?" }',
    )

    st.markdown(
        '<div class="section-header">Optional Context</div>',
        unsafe_allow_html=True,
    )
    col_v, col_s = st.columns(2)
    with col_v:
        vendor_input = st.text_area(
            "Vendor Record (JSON)",
            value=vendor_json,
            height=160,
            help="Historical vendor data. Leave empty if unavailable.",
        )
    with col_s:
        sender_input = st.text_area(
            "Sender History (JSON)",
            value=sender_json,
            height=160,
            help="What we know about this sender. Leave empty if unavailable.",
        )

    org_input = st.text_area(
        "Org Policies (plain text)",
        value=org_text,
        height=80,
        help="Organization payment approval policies.",
    )

    # ---- Evaluate Button ----

    st.markdown("")  # spacing
    evaluate_clicked = st.button(
        "\u2B21  Evaluate Action",
        type="primary",
        use_container_width=True,
    )

    if evaluate_clicked:
        # Validate inputs
        try:
            action_obj = json.loads(action_input)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON in **Action** field: {e}")
            st.stop()

        try:
            email_obj = json.loads(email_input)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON in **Email Chain** field: {e}")
            st.stop()

        # Build context
        context_obj: dict = {"email_chain": email_obj}

        try:
            vr = json.loads(vendor_input) if vendor_input.strip() else None
            if vr:
                context_obj["vendor_record"] = vr
        except json.JSONDecodeError:
            st.warning("Vendor Record JSON is invalid, skipping.")

        try:
            sh = json.loads(sender_input) if sender_input.strip() else None
            if sh:
                context_obj["sender_history"] = sh
        except json.JSONDecodeError:
            st.warning("Sender History JSON is invalid, skipping.")

        if org_input.strip():
            context_obj["org_policies"] = org_input.strip()

        payload = {"action": action_obj, "context": context_obj}

        # ---- Call API ----
        with st.spinner("Running adversarial challenge loop..."):
            try:
                result = call_evaluate(payload)
            except requests.exceptions.ConnectionError:
                st.error(
                    f"Cannot connect to Holo API at `{API_BASE}`. "
                    f"Is the backend running? (`uvicorn main:app --reload`)"
                )
                st.stop()
            except requests.exceptions.HTTPError as e:
                st.error(f"API error {e.response.status_code}: {e.response.text}")
                st.stop()
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                st.stop()

        # ---- Display Results ----
        st.markdown("---")

        render_verdict(result.get("decision", "ESCALATE"))
        render_risk_heatmap(result.get("risk_profile", {}))
        st.markdown("")
        render_convergence(result.get("convergence_info", {}))
        st.markdown("")
        render_round_accordions(result.get("round_details", []))
        st.markdown("")
        render_token_summary(result.get("token_usage", {}))

        st.markdown("")
        st.markdown(
            f"**Audit ID:** `{result.get('audit_id', 'N/A')}`"
        )


# ============================================================
# Tab 2: History / Dashboard
# ============================================================

with tab_history:
    st.markdown("## Evaluation History")

    try:
        data = call_history()
    except requests.exceptions.ConnectionError:
        st.warning(f"Cannot connect to API at `{API_BASE}`.")
        st.stop()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.warning("Authentication required. Check HOLO_API_KEY in .env.")
        else:
            st.warning(f"API returned {e.response.status_code}.")
        st.stop()
    except Exception as e:
        st.warning(f"Could not load history: {e}")
        st.stop()

    stats = data.get("stats", {})
    evaluations = data.get("evaluations", [])

    # ---- Summary Stat Cards ----
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-value">{stats.get("total", 0)}</div>'
            f'<div class="stat-label">Total Evaluations</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        allow = stats.get("allow_count", 0)
        escalate = stats.get("escalate_count", 0)
        ratio = f"{allow} / {escalate}" if (allow + escalate) > 0 else "0 / 0"
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-value">{ratio}</div>'
            f'<div class="stat-label">Allow / Escalate</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-value">{stats.get("avg_rounds", 0)}</div>'
            f'<div class="stat-label">Avg Rounds</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-value">${stats.get("total_cost", 0):.4f}</div>'
            f'<div class="stat-label">Total Cost</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ---- Evaluation Log ----
    if not evaluations:
        st.info(
            "No evaluations yet. Run one from the **New Evaluation** tab "
            "to see results here."
        )
    else:
        for ev in evaluations:
            decision = ev.get("decision", "?")
            created = str(ev.get("created_at", ""))[:19]
            rounds = ev.get("rounds_completed", "?")
            cost = float(ev.get("total_cost_usd", 0))
            latency = ev.get("total_latency_ms", 0)
            eval_id = ev.get("id", "?")

            verdict_icon = "\U0001F7E2" if decision == "ALLOW" else "\U0001F534"
            header = (
                f"{verdict_icon} **{decision}** &nbsp;\u00B7&nbsp; "
                f"{created} &nbsp;\u00B7&nbsp; "
                f"Rounds: {rounds} &nbsp;\u00B7&nbsp; "
                f"${cost:.4f} &nbsp;\u00B7&nbsp; "
                f"{latency:,}ms"
            )

            with st.expander(header, expanded=False):
                st.caption(f"Audit ID: {eval_id}")

                # Show round details if available
                round_details = ev.get("round_details", [])
                if round_details:
                    if isinstance(round_details, str):
                        try:
                            round_details = json.loads(round_details)
                        except json.JSONDecodeError:
                            round_details = []

                    for rd in round_details:
                        if isinstance(rd, dict):
                            st.markdown(
                                f"**R{rd.get('round_number', '?')}: "
                                f"{rd.get('role', '?')}** "
                                f"({rd.get('model_provider', '?')}) "
                                f"\u2192 {rd.get('verdict', '?')}"
                            )
                            if rd.get("reasoning_summary"):
                                st.caption(rd["reasoning_summary"])
                else:
                    # Fallback: show raw response payload
                    resp_payload = ev.get("response_payload")
                    if resp_payload:
                        if isinstance(resp_payload, str):
                            try:
                                resp_payload = json.loads(resp_payload)
                            except json.JSONDecodeError:
                                pass
                        st.json(resp_payload)
