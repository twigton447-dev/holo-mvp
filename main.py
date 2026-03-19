"""
main.py

FastAPI application for the Holo trust layer.
This version is wired to the live Context Governor loop.
No mock data. No stub responses.

Startup order:
  1. Load and validate environment variables.
  2. Instantiate the ContextGovernor (which instantiates all three LLM adapters).
  3. Serve requests.

POST /v1/evaluate_action
  - Validates the x-api-key header against HOLO_API_KEY in .env
  - Passes the request body to the ContextGovernor
  - Returns the full evaluation result

Note: Supabase logging is intentionally excluded from this build step.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Logging (set up before importing governor so its logs appear correctly)
# ---------------------------------------------------------------------------

logging.basicConfig(
    level   = getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format  = "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt = "%H:%M:%S",
)
logger = logging.getLogger("holo.main")

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from auth import RateLimiter
from context_governor import ContextGovernor
from chat_engine import HoloChatEngine
from auth_capsule import handle_google_signin, handle_email_signin, get_capsule_from_request, _brain as _capsule_brain

_rate_limiter = RateLimiter()

# Governor is instantiated once at startup and reused for every request.
# This means adapters are initialized once (SDK clients, auth, etc.).
_governor: ContextGovernor | None = None
_chat_engine: Optional[HoloChatEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: validate env and boot the Context Governor."""
    global _governor

    logger.info("Holo API starting up...")

    # 1. Validate required environment variables
    required = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "HOLO_API_KEY",
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(
            f"Startup failed. Missing environment variables: {missing}\n"
            f"Copy .env.example to .env and fill in your keys."
        )

    # 2. Instantiate the Context Governor (loads all three LLM adapters)
    try:
        _governor = ContextGovernor()
        logger.info("Context Governor initialized. Engine is LIVE.")
    except Exception as e:
        raise RuntimeError(f"Context Governor failed to initialize: {e}")

    # 3. Instantiate the Chat Engine (shares the same adapter pool)
    global _chat_engine
    try:
        _chat_engine = HoloChatEngine()
        logger.info("Holo Chat Engine initialized.")
    except Exception as e:
        raise RuntimeError(f"Chat Engine failed to initialize: {e}")

    logger.info("Holo API server ready.")
    yield
    logger.info("Holo API shutting down.")


app = FastAPI(
    title       = "Holo Trust Layer API",
    description = (
        "Adversarial multi-model action evaluation. "
        "Shared-context, compounding postmortems by structurally independent models."
    ),
    version  = "0.1.0",
    lifespan = lifespan,
)

# Serve the chat UI from /frontend — must be mounted before routes
import pathlib
_frontend_dir = pathlib.Path(__file__).parent / "frontend"
if _frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_frontend_dir)), name="static")


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------

def _verify_key(request: Request) -> str:
    """
    Simple API key validation against HOLO_API_KEY in the environment.
    Compares using a constant-time hash comparison to prevent timing attacks.
    """
    provided = request.headers.get("x-api-key", "")
    if not provided:
        raise HTTPException(status_code=401, detail="Missing x-api-key header.")

    expected = os.getenv("HOLO_API_KEY", "")
    if not expected:
        raise HTTPException(status_code=500, detail="Server misconfigured: HOLO_API_KEY not set.")

    # Constant-time comparison — hmac.compare_digest prevents timing attacks
    provided_hash = hashlib.sha256(provided.encode()).digest()
    expected_hash = hashlib.sha256(expected.encode()).digest()
    if not hmac.compare_digest(provided_hash, expected_hash):
        raise HTTPException(status_code=401, detail="Invalid API key.")

    # Rate limiting: 60 requests/minute per key (keyed by SHA256 prefix to avoid
    # storing raw keys in memory)
    key_id = hashlib.sha256(provided.encode()).hexdigest()[:16]
    max_rpm = int(os.getenv("HOLO_MAX_RPM", "60"))
    if not _rate_limiter.check(key_id, max_rpm):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded ({max_rpm} requests/minute).",
        )

    return provided


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Liveness check."""
    return {
        "status":  "ok",
        "version": "0.1.0",
        "engine":  "LIVE" if _governor else "NOT_INITIALIZED",
    }


@app.get("/config")
def get_config():
    """Return public client-side configuration."""
    return {
        "google_client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
    }


@app.post("/v1/evaluate_action")
async def evaluate_action(
    request: Request,
    _key: str = Depends(_verify_key),
):
    """
    Core evaluation endpoint.

    Accepts a structured action + context JSON payload.
    Runs the full multi-model adversarial loop via the Context Governor.
    Returns ALLOW or ESCALATE with the complete turn-by-turn audit trail.

    Required fields:
      action.type              — e.g. "invoice_payment"
      action.actor             — who/what initiated the action
      action.parameters        — action-specific details (amount, account, etc.)
      context.email_chain      — list of email message objects (required)

    Optional context fields:
      context.vendor_record    — historical vendor info
      context.sender_history   — sender reputation data
      context.org_policies     — freetext policy description
    """
    # Parse body
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")

    # Validate minimum required fields
    if "action" not in body:
        raise HTTPException(status_code=400, detail="Missing required field: action")

    context = body.get("context", {})
    if not context or not context.get("email_chain"):
        raise HTTPException(
            status_code=400,
            detail="Missing required field: context.email_chain"
        )

    action_type = body.get("action", {}).get("type", "unknown")
    logger.info(f"Evaluation request received | action_type={action_type}")

    # Run the live loop
    if _governor is None:
        raise HTTPException(status_code=503, detail="Engine not initialized.")

    try:
        result = _governor.evaluate(body)
    except Exception as e:
        logger.error(f"Governor error: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Evaluation engine error. See server logs for details.",
        )

    # Build API response
    response = _build_response(result)
    return JSONResponse(content=response)


@app.post("/auth/google")
async def google_signin(request: Request):
    """
    Exchange a Google Identity Services credential for a Holo capsule token.

    Body: { "credential": "<google_jwt>" }
    Returns: { capsule_token, capsule_id, email, name, avatar_url, mode }
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")

    credential = body.get("credential", "").strip()
    if not credential:
        raise HTTPException(status_code=400, detail="Missing field: credential")

    result = handle_google_signin(credential)
    if not result:
        raise HTTPException(status_code=401, detail="Google sign-in failed. Invalid credential.")

    return JSONResponse(content=result)


@app.post("/auth/email")
async def email_signin(request: Request):
    """
    Sign in with just a name and email — no Google OAuth required.
    Creates or loads a Capsule and returns a Holo capsule token.

    Body: { "email": "...", "name": "..." }
    Returns: { capsule_token, capsule_id, email, name, avatar_url, mode }
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")

    email = body.get("email", "").strip()
    name  = body.get("name", "").strip()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="A valid email is required.")

    result = handle_email_signin(email, name)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create capsule.")

    return JSONResponse(content=result)


@app.get("/auth/me")
async def get_me(request: Request):
    """Return current capsule info from the Authorization: Bearer <token> header."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Invalid or missing capsule token.")
    return JSONResponse(content=capsule)


@app.post("/auth/mode")
async def set_mode(request: Request):
    """Switch the capsule between 'personal' and 'work' modes."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Invalid or missing capsule token.")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")
    mode = body.get("mode", "")
    if mode not in ("personal", "work"):
        raise HTTPException(status_code=400, detail="mode must be 'personal' or 'work'")
    _capsule_brain.set_capsule_mode(capsule["sub"], mode)
    return JSONResponse(content={"capsule_id": capsule["sub"], "mode": mode})


@app.get("/")
def serve_chat_ui():
    """Serve the Holo chat UI."""
    index = _frontend_dir / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"status": "ok", "message": "Holo API running. Frontend not found."}


@app.post("/v1/chat")
async def chat(
    request: Request,
    _key: str = Depends(_verify_key),
):
    """
    Send a message to Holo. Returns Holo's response.

    Body:
      message     — the user's message (required)
      session_id  — continue an existing session (optional; new session created if omitted)
    """
    if _chat_engine is None:
        raise HTTPException(status_code=503, detail="Chat engine not initialized.")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")

    message = body.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Missing required field: message")

    session_id = body.get("session_id")
    images     = body.get("images") or None  # list of {name, data, mimeType} or None

    # Attach capsule identity if a capsule token is provided
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    capsule_id = capsule["sub"] if capsule else None

    try:
        result = _chat_engine.send_message(session_id, message, capsule_id=capsule_id,
                                           images=images)
    except Exception as e:
        logger.error(f"Chat engine error: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Chat engine error. See server logs.")

    return JSONResponse(content={
        "session_id":          result["session_id"],
        "response":            result["response"],
        "turn_number":         result["turn_number"],
        "thread_health_score": result["thread_health_score"],
        "thread_health_level": result["thread_health_level"],
        "elapsed_ms":          result["elapsed_ms"],
        "tokens":              result["tokens"],
        "thought":             result.get("thought"),
    })


@app.get("/v1/chat/{session_id}/history")
async def chat_history(
    session_id: str,
    _key: str = Depends(_verify_key),
):
    """Return the full message history for a session."""
    if _chat_engine is None:
        raise HTTPException(status_code=503, detail="Chat engine not initialized.")
    history = _chat_engine.get_history(session_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return JSONResponse(content={"session_id": session_id, "history": history})


@app.delete("/v1/chat/{session_id}")
async def clear_chat(
    session_id: str,
    _key: str = Depends(_verify_key),
):
    """Clear a chat session and start fresh."""
    if _chat_engine is None:
        raise HTTPException(status_code=503, detail="Chat engine not initialized.")
    cleared = _chat_engine.clear_session(session_id)
    return JSONResponse(content={"cleared": cleared, "session_id": session_id})


# ---------------------------------------------------------------------------
# Response builder
# ---------------------------------------------------------------------------

_CATEGORY_LABELS = {
    "sender_identity":  "Sender Identity Verification",
    "invoice_amount":   "Invoice Amount Anomaly",
    "payment_routing":  "Payment Routing Change",
    "urgency_pressure": "Urgency / Pressure Language",
    "domain_spoofing":  "Domain Spoofing Indicators",
    "approval_chain":   "Approval Chain Compliance",
}


def _build_response(result: dict) -> dict:
    """
    Transform the raw governor result into the clean API response shape
    that the Streamlit UI and any API consumer expects.
    """
    coverage = result["coverage_matrix"]

    return {
        # Top-level verdict
        "audit_id": result["evaluation_id"],
        "decision": result["decision"],
        "decision_reason": result["decision_reason"],

        # Loop metadata
        "convergence_info": {
            "converged":       result["converged"],
            "turns_completed": result["turns_completed"],
            "partial":         result["partial"],
            "deltas":          result["deltas"],
            "elapsed_ms":      result["elapsed_ms"],
        },

        # Per-category risk summary (max severity reached across all turns)
        "risk_profile": {
            cat: {
                "label":    _CATEGORY_LABELS.get(cat, cat),
                "severity": coverage[cat]["max_severity"],
                "assessed": coverage[cat]["addressed"],
            }
            for cat in coverage
        },

        # Full turn-by-turn audit trail (this is the rototilling record)
        "turn_details": result["turn_history"],

        # Token usage
        "token_usage": result["total_tokens"],
    }
