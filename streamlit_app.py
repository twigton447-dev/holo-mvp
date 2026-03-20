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
    /* ---- Google Fonts ---- */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

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

    /* ---- Base Typography ---- */
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }
    code, pre, .stTextArea textarea, .stCode {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem !important;
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

    /* ---- Sidebar Brand Block ---- */
    .sidebar-brand {
        padding: 0.5rem 0 1rem 0;
    }
    .sidebar-brand .brand-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: 0.25em;
        color: var(--brass);
        text-shadow: 0 0 30px rgba(201, 168, 76, 0.4);
        display: block;
        line-height: 1;
    }
    .sidebar-brand .brand-sub {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #666;
        margin-top: 0.4rem;
        display: block;
    }
    .sidebar-brand .brand-tagline {
        font-size: 0.78rem;
        color: #888;
        font-style: italic;
        margin-top: 0.6rem;
        display: block;
        line-height: 1.4;
    }

    /* ---- Status Indicator ---- */
    .status-online {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.78rem;
        color: var(--allow-green);
        font-weight: 500;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--allow-green);
        box-shadow: 0 0 6px var(--allow-green);
        animation: pulse-dot 2s infinite;
        display: inline-block;
    }
    .status-offline {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.78rem;
        color: #666;
    }
    .status-dot-off {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #444;
        display: inline-block;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    /* ---- Page Hero ---- */
    .page-hero {
        padding: 1.5rem 0 0.5rem 0;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 1.5rem;
    }
    .page-hero h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin: 0 0 0.4rem 0;
        line-height: 1.1;
        background: linear-gradient(90deg, var(--brass-light) 0%, var(--brass) 60%, var(--brass-dark) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .page-hero .hero-sub {
        font-size: 0.9rem;
        color: #888;
        line-height: 1.5;
        max-width: 680px;
        font-weight: 400;
    }
    .page-hero .hero-sub strong {
        color: #aaa;
        font-weight: 600;
    }

    /* ---- Verdict Banners ---- */
    @keyframes verdict-glow-allow {
        0%, 100% { box-shadow: 0 0 20px rgba(46, 204, 113, 0.2), inset 0 0 30px rgba(46, 204, 113, 0.05); }
        50% { box-shadow: 0 0 40px rgba(46, 204, 113, 0.4), inset 0 0 50px rgba(46, 204, 113, 0.1); }
    }
    @keyframes verdict-glow-escalate {
        0%, 100% { box-shadow: 0 0 20px rgba(231, 76, 60, 0.2), inset 0 0 30px rgba(231, 76, 60, 0.05); }
        50% { box-shadow: 0 0 40px rgba(231, 76, 60, 0.4), inset 0 0 50px rgba(231, 76, 60, 0.1); }
    }
    .verdict-allow {
        background: linear-gradient(135deg, #0d2818 0%, #1a4731 50%, #0d2818 100%);
        color: var(--allow-green);
        padding: 2rem 1rem;
        border-radius: 12px;
        text-align: center;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        letter-spacing: 0.25em;
        border: 2px solid var(--allow-green);
        margin: 1rem 0 0.5rem 0;
        text-shadow: 0 0 20px rgba(46, 204, 113, 0.4);
        animation: verdict-glow-allow 3s ease-in-out infinite;
    }
    .verdict-allow .verdict-sub {
        display: block;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.2em;
        color: rgba(46, 204, 113, 0.65);
        margin-top: 0.4rem;
        text-transform: uppercase;
    }
    .verdict-escalate {
        background: linear-gradient(135deg, #2a0a10 0%, #4a1520 50%, #2a0a10 100%);
        color: var(--escalate-red);
        padding: 2rem 1rem;
        border-radius: 12px;
        text-align: center;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        letter-spacing: 0.25em;
        border: 2px solid var(--escalate-red);
        margin: 1rem 0 0.5rem 0;
        text-shadow: 0 0 20px rgba(231, 76, 60, 0.4);
        animation: verdict-glow-escalate 2s ease-in-out infinite;
    }
    .verdict-escalate .verdict-sub {
        display: block;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.2em;
        color: rgba(231, 76, 60, 0.65);
        margin-top: 0.4rem;
        text-transform: uppercase;
    }

    /* ---- Risk Heatmap Cells ---- */
    .risk-cell {
        padding: 0.85rem 0.5rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 0.6rem;
        border: 1px solid var(--border-subtle);
        transition: transform 0.15s ease;
    }
    .risk-cell:hover { transform: translateY(-1px); }
    .risk-cell .risk-label {
        font-size: 0.68rem;
        color: #777;
        margin-bottom: 0.35rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }
    .risk-cell .risk-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.05em;
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
    .risk-none .risk-value { color: #444; }

    /* ---- Stat Cards ---- */
    .stat-card {
        background: linear-gradient(160deg, #18191f 0%, var(--bg-card) 100%);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1.4rem 0.8rem;
        text-align: center;
        transition: border-color 0.2s ease;
    }
    .stat-card:hover { border-color: var(--brass-dark); }
    .stat-card .stat-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--brass);
        line-height: 1.1;
    }
    .stat-card .stat-label {
        color: #666;
        font-size: 0.72rem;
        margin-top: 0.35rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
    }

    /* ---- Section Headers ---- */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        color: var(--brass);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        padding-bottom: 0.5rem;
        margin: 1.8rem 0 1rem 0;
        border-bottom: 1px solid var(--border-subtle);
    }
    .section-header::before {
        content: '';
        display: inline-block;
        width: 3px;
        height: 12px;
        background: var(--brass);
        border-radius: 2px;
        box-shadow: 0 0 8px rgba(201, 168, 76, 0.5);
    }

    /* ---- Convergence Pill ---- */
    .converge-pill {
        display: inline-block;
        padding: 0.4rem 1.1rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        font-family: 'Space Grotesk', sans-serif;
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

    /* ---- Results Banner Label ---- */
    .results-label {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #555;
        text-align: center;
        margin: 0.5rem 0 0 0;
    }

    /* ---- History Section Header ---- */
    .history-hero {
        padding: 1rem 0 1.2rem 0;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 1.5rem;
    }
    .history-hero h2 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        color: var(--brass);
        margin: 0 0 0.3rem 0;
    }
    .history-hero .history-sub {
        font-size: 0.82rem;
        color: #666;
    }

    /* ---- Mobile Responsiveness ---- */
    @media (max-width: 768px) {
        .verdict-allow, .verdict-escalate {
            font-size: 1.6rem;
            padding: 1.5rem 0.8rem;
            letter-spacing: 0.12em;
        }
        .stat-card .stat-value { font-size: 1.5rem; }
        .risk-cell .risk-value { font-size: 0.95rem; }
        .page-hero h1 { font-size: 1.5rem; }
    }

    /* ---- Hide Streamlit Hamburger & Footer ---- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ---- Tighten default padding ---- */
    .block-container { padding-top: 1.5rem; }

    /* ---- Tab styling ---- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        border-bottom: 1px solid var(--border-subtle);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        padding: 0.6rem 1.2rem;
    }

    /* ---- Follow-up Cards ---- */
    .followup-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #555;
        margin: 2rem 0 0.8rem 0;
    }
    .followup-header span {
        flex: 1;
        height: 1px;
        background: var(--border-subtle);
    }

    /* ---- Chat Response Area ---- */
    .holo-response {
        background: linear-gradient(160deg, #0f1118 0%, #13151c 100%);
        border: 1px solid var(--border-subtle);
        border-left: 3px solid var(--brass);
        border-radius: 0 10px 10px 0;
        padding: 1.2rem 1.4rem;
        margin: 1rem 0;
        font-size: 0.9rem;
        line-height: 1.7;
        color: #d0d0d0;
    }
    .holo-response .holo-response-label {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: var(--brass);
        margin-bottom: 0.6rem;
        display: block;
    }
    .chat-thread {
        margin-top: 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
    }
    .chat-user-msg {
        align-self: flex-end;
        background: #1e2028;
        border: 1px solid var(--border-subtle);
        border-radius: 12px 12px 2px 12px;
        padding: 0.7rem 1rem;
        max-width: 80%;
        font-size: 0.85rem;
        color: #aaa;
        font-style: italic;
    }

    /* ---- Capsule Identity Card ---- */
    .capsule-card {
        background: linear-gradient(160deg, #0f1014 0%, #13151a 100%);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 0.9rem 0.85rem;
        margin: 0.5rem 0;
    }
    .capsule-card .capsule-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.9rem;
        font-weight: 600;
        color: #ddd;
        display: block;
        margin-bottom: 0.15rem;
    }
    .capsule-card .capsule-email {
        font-size: 0.72rem;
        color: #555;
        display: block;
        margin-bottom: 0.5rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .capsule-card .capsule-meta {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .mode-pill {
        display: inline-block;
        padding: 0.18rem 0.6rem;
        border-radius: 10px;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .mode-personal {
        background: #1a1f2e;
        color: #6688cc;
        border: 1px solid #2a3550;
    }
    .mode-work {
        background: #1a2a1a;
        color: #55aa66;
        border: 1px solid #2a4a2a;
    }
    .capsule-id-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem;
        color: #3a3d45;
    }

    /* ---- Sign-in section ---- */
    .signin-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #555;
        margin-bottom: 0.6rem;
        display: block;
    }
    .signin-note {
        font-size: 0.72rem;
        color: #444;
        line-height: 1.4;
        margin-bottom: 0.8rem;
    }
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

# Initialize capsule session state before sidebar renders
for _k, _v in {
    "capsule_token": None,
    "capsule_id": None,
    "capsule_email": None,
    "capsule_name": None,
    "capsule_mode": None,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <span class="brand-name">⬡ HOLO</span>
        <span class="brand-sub">Protect &nbsp;·&nbsp; Trust Layer</span>
        <span class="brand-tagline">Multi-model adversarial council<br>for high-stakes agentic actions</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # ---- Connection status ----
    try:
        health = requests.get(f"{API_BASE}/health", timeout=3).json()
        version = health.get('version', '?')
        st.markdown(
            f'<div class="status-online"><span class="status-dot"></span> API Online &nbsp;'
            f'<code style="font-size:0.7rem;color:#555;">v{version}</code></div>',
            unsafe_allow_html=True,
        )
    except Exception:
        st.markdown(
            f'<div class="status-offline"><span class="status-dot-off"></span> API Offline</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"Expected at {API_BASE}")

    st.markdown("---")

    # ---- Capsule Identity ----
    if st.session_state.capsule_token:
        # Signed in — show identity card
        mode = st.session_state.capsule_mode or "personal"
        mode_class = f"mode-{mode}"
        cid = st.session_state.capsule_id or ""
        st.markdown(
            f'<div class="capsule-card">'
            f'<span class="capsule-name">{st.session_state.capsule_name}</span>'
            f'<span class="capsule-email">{st.session_state.capsule_email}</span>'
            f'<div class="capsule-meta">'
            f'<span class="mode-pill {mode_class}">{mode}</span>'
            f'<span class="capsule-id-tag">{cid[:8]}…</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button("Sign out", key="signout_btn", use_container_width=True):
            for _k in ("capsule_token", "capsule_id", "capsule_email",
                       "capsule_name", "capsule_mode"):
                st.session_state[_k] = None
            st.rerun()
    else:
        # Not signed in — show sign-in form
        st.markdown(
            '<span class="signin-header">Sign in to Holo</span>'
            '<p class="signin-note">Your Capsule ID links chat sessions to persistent memory — '
            'so context compounds over time.</p>',
            unsafe_allow_html=True,
        )
        with st.form("capsule_signin", clear_on_submit=False):
            signin_email = st.text_input("Email", placeholder="you@example.com")
            signin_name  = st.text_input("Name",  placeholder="Your name")
            submitted    = st.form_submit_button("⬡  Activate Capsule", use_container_width=True)

        if submitted:
            if not signin_email or "@" not in signin_email:
                st.error("Enter a valid email.")
            else:
                try:
                    result = call_email_signin(signin_email, signin_name)
                    st.session_state.capsule_token = result["capsule_token"]
                    st.session_state.capsule_id    = result["capsule_id"]
                    st.session_state.capsule_email = result["email"]
                    st.session_state.capsule_name  = result["name"]
                    st.session_state.capsule_mode  = result.get("mode", "personal")
                    st.rerun()
                except Exception as e:
                    st.error(f"Sign-in failed: {e}")

    st.markdown("---")
    st.markdown(
        '<span style="font-size:0.7rem;color:#444;letter-spacing:0.08em;">v0.1.0 &nbsp;·&nbsp; Patent Pending</span>',
        unsafe_allow_html=True,
    )


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


def call_email_signin(email: str, name: str) -> dict:
    """POST to /auth/email and return capsule info."""
    resp = requests.post(
        f"{API_BASE}/auth/email",
        json={"email": email, "name": name},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def call_chat(message: str, session_id: str | None = None,
              capsule_token: str | None = None) -> dict:
    """POST to /v1/chat and return parsed JSON."""
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    if capsule_token:
        headers["Authorization"] = f"Bearer {capsule_token}"
    payload: dict = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    resp = requests.post(
        f"{API_BASE}/v1/chat",
        json=payload,
        headers=headers,
        timeout=60,
    )
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
    icon = "✓" if decision == "ALLOW" else "⚠"
    sub = "Action cleared by adversarial council" if decision == "ALLOW" else "Human review required — threat detected"
    st.markdown(
        f'<div class="{css_class}">{icon} &nbsp; {decision}'
        f'<span class="verdict-sub">{sub}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="results-label">Adversarial Council Verdict</div>', unsafe_allow_html=True)


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


def generate_follow_ups(result: dict) -> list[dict]:
    """Generate 3 contextual follow-up prompts based on the evaluation result."""
    decision = result.get("decision", "ESCALATE")
    risk_profile = result.get("risk_profile", {})
    decision_reason = result.get("decision_reason", "")

    high_cats = [k for k, v in risk_profile.items() if v.get("severity") == "HIGH"]
    medium_cats = [k for k, v in risk_profile.items() if v.get("severity") == "MEDIUM"]
    top_cat = high_cats[0] if high_cats else (medium_cats[0] if medium_cats else None)
    top_label = CATEGORY_LABELS.get(top_cat, top_cat.replace("_", " ").title()) if top_cat else "the primary signal"

    # Build a shared context prefix for every message
    high_labels = [CATEGORY_LABELS.get(c, c) for c in high_cats]
    ctx = (
        f"Context: A Holo adversarial council just evaluated an invoice payment transaction "
        f"and returned verdict: {decision}. "
        + (f"High-severity findings: {', '.join(high_labels)}. " if high_labels else "")
        + (f"Decision reason: {decision_reason}. " if decision_reason else "")
    )

    prompts = []

    # 1 — Dig into the primary finding
    if decision == "ESCALATE":
        prompts.append({
            "label": "Primary Threat",
            "title": f"Why did {top_label} drive escalation?",
            "hint": "The council's detailed reasoning on the highest-risk signal.",
            "message": (
                f"{ctx} Walk me through exactly what the adversarial council detected "
                f"in {top_label} and why it was severe enough to escalate."
            ),
        })
    else:
        prompts.append({
            "label": "Clearance Path",
            "title": "What specifically cleared this transaction?",
            "hint": "Understand the signals the council verified before allowing.",
            "message": (
                f"{ctx} What were the specific signals the council verified, "
                f"and what evidence would have been enough to tip it toward escalation?"
            ),
        })

    # 2 — Counterfactual
    if decision == "ESCALATE":
        prompts.append({
            "label": "Counterfactual",
            "title": "What would have cleared this transaction?",
            "hint": "The verification path or evidence that changes the verdict.",
            "message": (
                f"{ctx} What specific evidence, verification steps, or contextual signals — "
                f"if present — would have allowed the council to approve this transaction?"
            ),
        })
    else:
        prompts.append({
            "label": "Attack Surface",
            "title": "How could a bad actor weaponize this pattern?",
            "hint": "Map the threat model behind this transaction type.",
            "message": (
                f"{ctx} Describe how a sophisticated attacker might craft a similar transaction "
                f"to evade detection — what attack variations exist, and how subtle can they get?"
            ),
        })

    # 3 — Controls and prevention
    prompts.append({
        "label": "Prevention",
        "title": "What controls stop this at scale?",
        "hint": "Turn council findings into policy — what should your org implement?",
        "message": (
            f"{ctx} Based on this evaluation, what internal controls, approval policies, "
            f"or verification gates should an organization put in place to catch this class "
            f"of {'attack' if decision == 'ESCALATE' else 'risk'} before it reaches the agent layer?"
        ),
    })

    return prompts


def render_follow_ups(result: dict):
    """3 contextual follow-up prompt cards that call /v1/chat when clicked."""
    st.markdown(
        '<div class="followup-header">⬡ &nbsp; Go Deeper<span></span></div>',
        unsafe_allow_html=True,
    )

    prompts = generate_follow_ups(result)
    cols = st.columns(3)

    for i, (col, p) in enumerate(zip(cols, prompts)):
        with col:
            clicked = st.button(
                f"**{p['label']}**\n\n{p['title']}\n\n_{p['hint']}_",
                key=f"followup_{i}",
                use_container_width=True,
            )
            if clicked:
                st.session_state.active_followup = i
                st.session_state.pending_chat_message = p["message"]
                st.session_state.pending_chat_display = p["title"]

    # Fire the chat call if a follow-up was just triggered
    if st.session_state.get("pending_chat_message"):
        msg = st.session_state.pop("pending_chat_message")
        display = st.session_state.pop("pending_chat_display", msg)
        with st.spinner("Holo is thinking..."):
            try:
                chat_result = call_chat(
                    msg,
                    st.session_state.get("chat_session_id"),
                    capsule_token=st.session_state.get("capsule_token"),
                )
                st.session_state.chat_session_id = chat_result.get("session_id")
                st.session_state.chat_history.append({
                    "display": display,
                    "response": chat_result.get("response", ""),
                })
            except Exception as e:
                st.error(f"Chat error: {e}")

    # Render chat thread
    if st.session_state.get("chat_history"):
        st.markdown('<div class="chat-thread">', unsafe_allow_html=True)
        for turn in st.session_state.chat_history:
            st.markdown(
                f'<div class="chat-user-msg">{turn["display"]}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="holo-response">'
                f'<span class="holo-response-label">⬡ Holo</span>'
                f'{turn["response"]}'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Allow freeform follow-up
        st.markdown(
            '<div class="section-header">Continue the conversation</div>',
            unsafe_allow_html=True,
        )
        user_msg = st.text_input(
            "Ask Holo anything about this evaluation",
            key="freeform_chat_input",
            label_visibility="collapsed",
            placeholder="Ask anything about this evaluation...",
        )
        if st.button("Send", key="freeform_chat_send"):
            if user_msg.strip():
                with st.spinner("Holo is thinking..."):
                    try:
                        chat_result = call_chat(
                            user_msg,
                            st.session_state.get("chat_session_id"),
                            capsule_token=st.session_state.get("capsule_token"),
                        )
                        st.session_state.chat_session_id = chat_result.get("session_id")
                        st.session_state.chat_history.append({
                            "display": user_msg,
                            "response": chat_result.get("response", ""),
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"Chat error: {e}")


# ============================================================
# Tab 1: New Evaluation
# ============================================================

tab_eval, tab_history = st.tabs(["\u2B21 New Evaluation", "\U0001F4CA History"])

with tab_eval:
    # Session state for persistent results + chat
    for _key in ("eval_result", "chat_session_id", "chat_history", "active_followup"):
        if _key not in st.session_state:
            st.session_state[_key] = None if _key != "chat_history" else []

    st.markdown("""
    <div class="page-hero">
        <h1>Evaluate an Action</h1>
        <p class="hero-sub">
            Select a scenario or build your own payload.
            Holo runs a <strong>multi-model adversarial council</strong> — three frontier models, compounding postmortems,
            convergence detection — and returns a final verdict: <strong>ALLOW</strong> or <strong>ESCALATE</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

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
        "⬡  Run Adversarial Evaluation",
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

        # Store result in session state so it persists across re-runs (e.g. follow-up clicks)
        st.session_state.eval_result = result
        st.session_state.chat_session_id = None
        st.session_state.chat_history = []
        st.session_state.active_followup = None

    # ---- Display Results (from session state, persists across button clicks) ----
    if st.session_state.eval_result:
        result = st.session_state.eval_result
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
            f'<span style="font-size:0.75rem;color:#444;font-family:\'JetBrains Mono\',monospace;">'
            f'Audit ID: {result.get("audit_id", "N/A")}</span>',
            unsafe_allow_html=True,
        )

        render_follow_ups(result)


# ============================================================
# Tab 2: History / Dashboard
# ============================================================

with tab_history:
    st.markdown("""
    <div class="history-hero">
        <h2>Evaluation History</h2>
        <span class="history-sub">All past adversarial evaluations — auditable, compounding, permanent.</span>
    </div>
    """, unsafe_allow_html=True)

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
