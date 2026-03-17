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
from fastapi.responses import JSONResponse

from auth import RateLimiter
from context_governor import ContextGovernor

_rate_limiter = RateLimiter()

# Governor is instantiated once at startup and reused for every request.
# This means adapters are initialized once (SDK clients, auth, etc.).
_governor: ContextGovernor | None = None


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
