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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from auth import RateLimiter
from context_governor import ContextGovernor
from chat_engine import HoloChatEngine
from auth_capsule import handle_google_signin, handle_email_signin, get_capsule_from_request, request_password_reset, reset_password, _brain as _capsule_brain
from db import Database
from billing import create_checkout_session, create_customer_portal_session, construct_webhook_event, PLANS

_rate_limiter = RateLimiter()
_db: Database | None = None

# Governor is instantiated once at startup and reused for every request.
# This means adapters are initialized once (SDK clients, auth, etc.).
_governor: ContextGovernor | None = None
_chat_engine: Optional[HoloChatEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: validate env and boot the Context Governor."""
    global _governor

    logger.info("Holo API starting up...")

    # 0. Connect to Supabase for usage tracking (optional — won't block startup)
    global _db
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if supabase_url and supabase_key:
        try:
            _db = Database(supabase_url, supabase_key)
            logger.info("Usage tracking: Supabase connected.")
        except Exception as e:
            logger.warning(f"Usage tracking unavailable: {e}")

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the chat UI from /frontend — must be mounted before routes
import pathlib
_frontend_dir = pathlib.Path(__file__).parent / "frontend"
if _frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_frontend_dir)), name="static")


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------

def _track_usage(api_key: str, endpoint: str, status_code: int,
                 input_tokens: int = 0, output_tokens: int = 0,
                 cost_usd: float = 0.0, latency_ms: int = 0) -> None:
    """Fire-and-forget usage log. Never raises."""
    if _db is None:
        return
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
    try:
        _db.log_api_usage({
            "api_key_hash": key_hash,
            "endpoint":     endpoint,
            "status_code":  status_code,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd":     cost_usd,
            "latency_ms":   latency_ms,
        })
    except Exception:
        pass


def _verify_key(request: Request) -> str:
    """
    API key validation. Checks per-user keys in Supabase first, then falls
    back to the HOLO_API_KEY env var for internal/admin use.
    """
    provided = request.headers.get("x-api-key", "")
    if not provided:
        raise HTTPException(status_code=401, detail="Missing x-api-key header.")

    key_id = hashlib.sha256(provided.encode()).hexdigest()[:16]

    # 1. Check per-user keys in Supabase
    if _db is not None:
        row = _db.validate_api_key(provided)
        if row:
            max_rpm = row.get("max_requests_per_minute", 60)
            if not _rate_limiter.check(key_id, max_rpm):
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded ({max_rpm} requests/minute).",
                )
            return provided

    # 2. Fall back to env var (admin / internal use)
    expected = os.getenv("HOLO_API_KEY", "")
    if expected:
        provided_hash = hashlib.sha256(provided.encode()).digest()
        expected_hash = hashlib.sha256(expected.encode()).digest()
        if hmac.compare_digest(provided_hash, expected_hash):
            max_rpm = int(os.getenv("HOLO_MAX_RPM", "60"))
            if not _rate_limiter.check(key_id, max_rpm):
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded ({max_rpm} requests/minute).",
                )
            return provided

    raise HTTPException(status_code=401, detail="Invalid API key.")


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

    # Resolve capsule_id — from JWT if present, otherwise from the API key itself
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    capsule_id = capsule["sub"] if capsule else None
    capsule_email = capsule.get("email", "") if capsule else ""
    if _db and not capsule_id:
        capsule_id = _db.get_capsule_id_for_key(_key)

    # Quota check
    if _db and capsule_id:
        sub = _db.get_or_create_subscription(capsule_id, capsule_email)
        if sub["calls_used"] >= sub["calls_quota"]:
            raise HTTPException(
                status_code=402,
                detail={
                    "error":   "quota_exceeded",
                    "message": f"You've used all {sub['calls_quota']} calls on your {sub['plan']} plan.",
                    "upgrade": "/billing/checkout",
                }
            )

    # Run the live loop
    if _governor is None:
        raise HTTPException(status_code=503, detail="Engine not initialized.")

    t0 = time.time()
    try:
        result = _governor.evaluate(body)
    except Exception as e:
        logger.error(f"Governor error: {type(e).__name__}: {e}", exc_info=True)
        _track_usage(_key, "/v1/evaluate_action", 500)
        raise HTTPException(
            status_code=500,
            detail="Evaluation engine error. See server logs for details.",
        )

    elapsed = int((time.time() - t0) * 1000)
    tokens  = result.get("total_tokens", {})
    _track_usage(
        _key, "/v1/evaluate_action", 200,
        input_tokens  = tokens.get("total_input_tokens", 0),
        output_tokens = tokens.get("total_output_tokens", 0),
        cost_usd      = tokens.get("total_cost_usd", 0.0),
        latency_ms    = elapsed,
    )

    # Increment quota counter
    if _db and capsule_id:
        _db.increment_calls_used(capsule_id)

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

    try:
        result = handle_google_signin(credential)
    except ValueError as e:
        if "account_cap_reached" in str(e):
            raise HTTPException(status_code=503, detail="account_cap_reached")
        raise HTTPException(status_code=401, detail="Google sign-in failed.")
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

    email       = body.get("email", "").strip()
    name        = body.get("name", "").strip()
    password    = body.get("password", "").strip()
    invite_code = body.get("invite_code", "").strip()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="A valid email is required.")
    if not password:
        raise HTTPException(status_code=400, detail="A password is required.")

    try:
        result = handle_email_signin(email, name, password, invite_code)
    except ValueError as e:
        if "account_cap_reached" in str(e):
            raise HTTPException(status_code=503, detail="account_cap_reached")
        raise HTTPException(status_code=403, detail="Invalid invite code.")
    if not result:
        raise HTTPException(status_code=401, detail="Incorrect password.")

    return JSONResponse(content=result)


@app.post("/auth/forgot-password")
async def forgot_password(request: Request):
    """Send a password reset email. Body: { "email": "..." }"""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")
    email = body.get("email", "").strip()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="A valid email is required.")
    base_url = str(request.base_url)
    request_password_reset(email, base_url)
    # Always return 200 — don't reveal whether the account exists
    return JSONResponse(content={"ok": True})


@app.post("/auth/reset-password")
async def do_reset_password(request: Request):
    """Reset password with token. Body: { "email": "...", "token": "...", "password": "..." }"""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")
    email    = body.get("email", "").strip()
    token    = body.get("token", "").strip()
    password = body.get("password", "").strip()
    if not all([email, token, password]):
        raise HTTPException(status_code=400, detail="email, token, and password are required.")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    ok = reset_password(email, token, password)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link. Please request a new one.")
    return JSONResponse(content={"ok": True})


@app.get("/auth/me")
async def get_me(request: Request):
    """
    Return current capsule info. Also ensures the capsule row exists in Supabase
    and re-issues a fresh token — heals ephemeral capsules from earlier sessions.
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Invalid or missing capsule token.")

    # Ensure capsule row exists — creates it if the token was ephemeral
    if _capsule_brain._client:
        existing = _capsule_brain.get_capsule(capsule["sub"])
        if not existing:
            # Heal: create the capsule row using identity from the JWT
            import uuid as _uuid
            try:
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc).isoformat()
                email = capsule.get("email", "")
                # Use a stable synthetic google_id derived from email
                import hashlib
                synthetic_id = "email:" + hashlib.sha256(email.encode()).hexdigest()[:32]
                _capsule_brain._client.table("holo_capsules").upsert({
                    "capsule_id":  capsule["sub"],
                    "google_id":   synthetic_id or capsule["sub"],
                    "email":       email,
                    "name":        email.split("@")[0] if email else "User",
                    "avatar_url":  "",
                    "mode":        capsule.get("mode", "personal"),
                    "created_at":  now,
                    "last_active": now,
                }, on_conflict="capsule_id").execute()
                logger.info(f"Healed ephemeral capsule {capsule['sub'][:8]} → Supabase row created.")
            except Exception as e:
                logger.warning(f"Capsule heal failed: {e}")

    return JSONResponse(content=capsule)


@app.post("/auth/keys")
async def issue_key(request: Request):
    """
    Issue a new API key for the authenticated user.

    Requires: Authorization: Bearer <capsule_token>
    Body (optional): { "name": "my-agent" }
    Returns: { "api_key": "holo_sk_...", "key_prefix": "holo_sk_XXXXXX" }

    The raw api_key is returned exactly once. Store it — it cannot be retrieved again.
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")

    if _db is None:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    try:
        body = await request.json()
    except Exception:
        body = {}

    name = (body.get("name") or "default").strip()[:64]

    raw_key = _db.issue_api_key(capsule_id=capsule["sub"], name=name)
    key_prefix = raw_key[:14]

    logger.info(f"API key issued: prefix={key_prefix} capsule={capsule['sub'][:8]}")

    return JSONResponse(content={
        "api_key":    raw_key,
        "key_prefix": key_prefix,
        "name":       name,
        "note":       "Store this key — it will not be shown again.",
    })


@app.get("/auth/keys")
async def list_keys(request: Request):
    """
    List all active API keys for the authenticated user.
    Returns key prefixes only — never the raw key or its hash.
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")

    if _db is None:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    keys = _db.get_api_keys(capsule["sub"])
    return JSONResponse(content={"keys": keys})


@app.delete("/auth/keys/{key_prefix}")
async def revoke_key(key_prefix: str, request: Request):
    """
    Revoke an API key by its prefix. Only the key's owner can revoke it.
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")

    if _db is None:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    revoked = _db.revoke_api_key(capsule_id=capsule["sub"], key_prefix=key_prefix)
    if not revoked:
        raise HTTPException(status_code=404, detail="Key not found or already revoked.")

    logger.info(f"API key revoked: prefix={key_prefix} capsule={capsule['sub'][:8]}")
    return JSONResponse(content={"revoked": True, "key_prefix": key_prefix})


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
def serve_landing():
    """Serve the Holo landing page."""
    landing = _frontend_dir / "index.html"
    if landing.exists():
        return FileResponse(str(landing))
    return {"status": "ok", "message": "Holo API running. Frontend not found."}


@app.get("/appendix.html")
def serve_appendix():
    """Serve the benchmark appendix page."""
    f = _frontend_dir / "appendix.html"
    if f.exists():
        return FileResponse(str(f))
    raise HTTPException(status_code=404, detail="Not found.")


@app.get("/payloads/")
def serve_payloads_index():
    """Serve the payloads index page."""
    f = _frontend_dir / "payloads" / "index.html"
    if f.exists():
        return FileResponse(str(f))
    raise HTTPException(status_code=404, detail="Not found.")


@app.get("/payloads/{filename}")
def serve_payload_file(filename: str):
    """Serve a payload JSON file for download."""
    f = _frontend_dir / "payloads" / filename
    if f.exists() and f.suffix == ".json":
        return FileResponse(str(f), media_type="application/json")
    raise HTTPException(status_code=404, detail="Not found.")


@app.get("/sw.js")
def serve_service_worker():
    """Serve the PWA service worker from root scope so it can control all pages."""
    sw = _frontend_dir / "sw.js"
    if not sw.exists():
        raise HTTPException(status_code=404, detail="Service worker not found.")
    return FileResponse(
        str(sw),
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"},
    )


@app.get("/chat")
def serve_chat_ui():
    """Serve the Holo chat UI."""
    index = _frontend_dir / "chat.html"
    if index.exists():
        return FileResponse(str(index))
    return {"status": "ok", "message": "Holo API running. Chat UI not found."}


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
    incognito  = bool(body.get("incognito", False))  # blind mode — no memory injected

    # Attach capsule identity if a capsule token is provided
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    # Incognito: treat as anonymous regardless of sign-in state
    capsule_id = (capsule["sub"] if capsule else None) if not incognito else None

    t0 = time.time()
    try:
        result = _chat_engine.send_message(session_id, message, capsule_id=capsule_id,
                                           images=images, incognito=incognito)
    except Exception as e:
        logger.error(f"Chat engine error: {type(e).__name__}: {e}", exc_info=True)
        _track_usage(_key, "/v1/chat", 500)
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")

    elapsed = int((time.time() - t0) * 1000)
    tokens  = result.get("tokens", {})
    _track_usage(
        _key, "/v1/chat", 200,
        input_tokens  = tokens.get("input", 0),
        output_tokens = tokens.get("output", 0),
        latency_ms    = elapsed,
    )

    return JSONResponse(content={
        "session_id":          result["session_id"],
        "response":            result["response"],
        "turn_number":         result["turn_number"],
        "thread_health_score": result["thread_health_score"],
        "thread_health_level": result["thread_health_level"],
        "elapsed_ms":          result["elapsed_ms"],
        "tokens":              result["tokens"],
        "thought":             result.get("thought"),
        "artifacts":           result.get("artifacts", []),
    })


@app.get("/v1/capsule/last-session")
async def get_last_session(request: Request):
    """
    Return the last session ID and full history for the authenticated user.
    Used to restore a thread after a page refresh or server restart.
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    ctx = _capsule_brain.get_capsule_context(capsule["sub"])
    session_id = ctx.get("last_session_id")
    if not session_id:
        return JSONResponse(content={"session_id": None, "history": []})
    # Restore into engine memory (loads from Supabase if not already in memory)
    if _chat_engine:
        session = _chat_engine.get_or_create_session(session_id)
        history = session.history
    else:
        history = _capsule_brain.load_chat_history(session_id) or []
    return JSONResponse(content={"session_id": session_id, "history": history})


@app.get("/v1/capsule/sessions")
async def list_sessions(request: Request):
    """
    Return all past chat sessions for the authenticated user, newest first.
    Each entry: {id, at, preview}
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    # Direct table query — requires capsule_id column on holo_chat_sessions
    sessions = _capsule_brain.list_sessions(capsule["sub"])
    # Map to the shape the frontend expects: {id, at, preview, title}
    mapped = [
        {
            "id":      s.get("session_id"),
            "at":      s.get("last_active") or s.get("created_at"),
            "preview": s.get("preview", ""),
            "title":   s.get("title") or s.get("preview", ""),
        }
        for s in sessions
    ]
    return JSONResponse(content={"sessions": mapped})


@app.get("/v1/artifacts")
async def list_artifacts(request: Request):
    """Return all saved artifacts for the authenticated user, newest first."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    artifacts = _capsule_brain.list_artifacts(capsule["sub"])
    return JSONResponse(content={"artifacts": artifacts})


@app.get("/v1/artifacts/{artifact_id}")
async def get_artifact(artifact_id: str, request: Request):
    """Return a single artifact by ID. User must own it."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    artifact = _capsule_brain.get_artifact(capsule["sub"], artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found.")
    return JSONResponse(content=artifact)


_summary_cache: dict = {}
_surface_cache: dict = {}

@app.get("/v1/capsule/surface")
async def capsule_surface(
    request: Request,
    _key: str = Depends(_verify_key),
):
    """
    Governor-generated surface briefing: top 5 topics + priority to-dos.
    Cached per capsule for 30 minutes to avoid redundant LLM calls.
    """
    import time
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    capsule_id = capsule["sub"]

    # Return cached result if fresh (< 30 min)
    cached = _surface_cache.get(capsule_id)
    if cached and (time.time() - cached["ts"]) < 1800:
        return JSONResponse(content=cached["data"])

    if _chat_engine is None:
        raise HTTPException(status_code=503, detail="Chat engine not initialized.")

    context = _capsule_brain.get_capsule_context(capsule_id) or {}
    sessions = _capsule_brain.list_sessions(capsule_id)
    result = _chat_engine._captain.generate_surface(context, sessions)
    if not result:
        return JSONResponse(content={"topics": [], "todos": []})

    _surface_cache[capsule_id] = {"data": result, "ts": time.time()}
    return JSONResponse(content=result)


@app.get("/v1/chat/{session_id}/summary")
async def thread_summary(
    session_id: str,
    _key: str = Depends(_verify_key),
):
    """Return a Governor-written summary of the thread for sidebar hover preview."""
    if session_id in _summary_cache:
        return JSONResponse(content={"summary": _summary_cache[session_id]})
    if _chat_engine is None:
        raise HTTPException(status_code=503, detail="Chat engine not initialized.")
    # Try in-memory session first, fall back to DB
    session = _chat_engine.get_or_create_session(session_id)
    history = session.history
    if not history:
        history = _capsule_brain.load_chat_history(session_id) or []
    if not history:
        raise HTTPException(status_code=404, detail="Session not found.")
    summary = _chat_engine._captain.summarize_thread(history)
    if summary:
        _summary_cache[session_id] = summary
    return JSONResponse(content={"summary": summary})


@app.get("/v1/chat/{session_id}/history")
async def chat_history(
    session_id: str,
    _key: str = Depends(_verify_key),
):
    """Return the full message history for a session."""
    if _chat_engine is None:
        raise HTTPException(status_code=503, detail="Chat engine not initialized.")
    # Try in-memory first, then fall back to Supabase via session restore
    session = _chat_engine.get_or_create_session(session_id)
    history = session.history
    if not history:
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


@app.delete("/v1/session/{session_id}")
async def delete_session(
    session_id: str,
    request: Request,
    _key: str = Depends(_verify_key),
):
    """Permanently delete a session and all its messages. User must own the session."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Authentication required.")
    capsule_id = capsule["sub"]
    if _chat_engine:
        _chat_engine.clear_session(session_id)
    deleted = _capsule_brain.delete_session(capsule_id, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found or access denied.")
    return JSONResponse(content={"deleted": True, "session_id": session_id})


# ---------------------------------------------------------------------------
# Billing routes
# ---------------------------------------------------------------------------

@app.post("/billing/checkout")
async def billing_checkout(request: Request):
    """
    Create a Stripe Checkout session.
    Body: { "plan": "starter"|"pro", "capsule_token": "..." }
    Returns: { "checkout_url": "..." }
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required to upgrade.")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON.")

    plan = body.get("plan", "")
    if plan not in ("starter", "pro"):
        raise HTTPException(status_code=400, detail="plan must be 'starter' or 'pro'")

    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    try:
        url = create_checkout_session(
            plan=plan,
            customer_email=capsule.get("email", ""),
            success_url=f"{base_url}/?upgrade=success",
            cancel_url=f"{base_url}/?upgrade=cancelled",
        )
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session.")

    return JSONResponse(content={"checkout_url": url})


@app.post("/billing/portal")
async def billing_portal(request: Request):
    """
    Create a Stripe Customer Portal session for managing/cancelling subscription.
    Returns: { "portal_url": "..." }
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")

    if _db is None:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    sub = _db.get_subscription(capsule["sub"])
    if not sub or not sub.get("stripe_customer_id"):
        raise HTTPException(status_code=404, detail="No active subscription found.")

    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    try:
        url = create_customer_portal_session(
            stripe_customer_id=sub["stripe_customer_id"],
            return_url=f"{base_url}/",
        )
    except Exception as e:
        logger.error(f"Stripe portal error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create portal session.")

    return JSONResponse(content={"portal_url": url})


@app.post("/billing/webhook")
async def billing_webhook(request: Request):
    """
    Stripe webhook — updates subscription status after payment.
    Must be called by Stripe, not the frontend.
    """
    payload    = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = construct_webhook_event(payload, sig_header)
    except Exception as e:
        logger.warning(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid webhook signature.")

    if event["type"] == "checkout.session.completed":
        session           = event["data"]["object"]
        plan              = session.get("metadata", {}).get("plan", "starter")
        stripe_customer   = session.get("customer")
        stripe_sub        = session.get("subscription")
        customer_email    = session.get("customer_email", "")
        quota             = PLANS.get(plan, {}).get("calls_per_month", 500)

        if _db and customer_email:
            # Find the capsule by email and upgrade their plan
            result = (
                _db.client.table("subscriptions")
                .select("capsule_id")
                .eq("email", customer_email)
                .execute()
            )
            if result.data:
                capsule_id = result.data[0]["capsule_id"]
                _db.update_subscription_plan(
                    capsule_id=capsule_id,
                    plan=plan,
                    quota=quota,
                    stripe_customer_id=stripe_customer,
                    stripe_sub_id=stripe_sub,
                )
                logger.info(f"Upgraded {customer_email} to {plan} ({quota} calls/mo)")

    elif event["type"] == "customer.subscription.deleted":
        stripe_customer = event["data"]["object"].get("customer")
        if _db and stripe_customer:
            _db.client.table("subscriptions").update(
                {"plan": "free", "calls_quota": 1, "calls_used": 0,
                 "stripe_sub_id": None, "updated_at": "now()"}
            ).eq("stripe_customer_id", stripe_customer).execute()
            logger.info(f"Subscription cancelled for customer {stripe_customer}")

    return JSONResponse(content={"received": True})


@app.post("/evaluate")
async def evaluate(
    request: Request,
    _key: str = Depends(_verify_key),
):
    """
    Simplified evaluation endpoint.

    Accepts invoice_data at the top level and maps it to the governor's
    action/context shape. Runs the full multi-model adversarial loop.

    Required fields:
      invoice_data.action   — action descriptor (type, actor, parameters)
      invoice_data.context  — context bundle (email_chain required)
    """
    if _governor is None:
        raise HTTPException(status_code=503, detail="Engine not initialized.")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")

    invoice_data = body.get("invoice_data", body)  # accept either wrapped or flat

    if "action" not in invoice_data:
        raise HTTPException(status_code=400, detail="Missing required field: action")
    context = invoice_data.get("context", {})
    if not context or not context.get("email_chain"):
        raise HTTPException(status_code=400, detail="Missing required field: context.email_chain")

    t0 = time.time()
    try:
        result = _governor.evaluate(invoice_data)
    except Exception as e:
        logger.error(f"Governor error: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Evaluation engine error. See server logs.")

    elapsed = int((time.time() - t0) * 1000)
    tokens  = result.get("total_tokens", {})
    _track_usage(
        _key, "/evaluate", 200,
        input_tokens  = tokens.get("total_input_tokens", 0),
        output_tokens = tokens.get("total_output_tokens", 0),
        cost_usd      = tokens.get("total_cost_usd", 0.0),
        latency_ms    = elapsed,
    )

    return JSONResponse(content=_build_response(result))


@app.post("/project-brain/connect")
async def project_brain_connect(request: Request):
    """
    Authenticate a workspace to the Project Brain and store the connection.

    Body: { "workspace_id": str, "api_key": str }
    Returns: { "status": "connected", "memory_size": int, "context_loaded": bool }

    The connection is recorded in holo_integrations keyed by workspace_id.
    Requires a valid capsule token (Authorization: Bearer <token>).
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")

    workspace_id = body.get("workspace_id", "").strip()
    api_key      = body.get("api_key", "").strip()
    if not workspace_id or not api_key:
        raise HTTPException(status_code=400, detail="workspace_id and api_key are required.")

    if len(api_key) < 16:
        raise HTTPException(status_code=400, detail="api_key appears invalid (too short).")

    if _db is None:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    try:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()

        _db.client.table("holo_integrations").upsert(
            {
                "capsule_id":     capsule["sub"],
                "source":         "workspace",
                "status":         "connected",
                "connected_at":   now,
                "last_synced_at": now,
                "metadata": {
                    "workspace_id": workspace_id,
                    "api_key_hash": hashlib.sha256(api_key.encode()).hexdigest()[:16],
                },
            },
            on_conflict="capsule_id,source",
        ).execute()

        ctx_resp = (
            _db.client.table("holo_capsule_context")
            .select("key", count="exact")
            .eq("capsule_id", capsule["sub"])
            .execute()
        )
        memory_size    = ctx_resp.count or 0
        context_loaded = memory_size > 0

        logger.info(
            f"Project Brain: workspace '{workspace_id}' connected "
            f"for capsule {capsule['sub'][:8]}. memory_size={memory_size}"
        )

    except Exception as e:
        logger.error(f"project-brain/connect error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to store workspace connection.")

    return JSONResponse(content={
        "status":         "connected",
        "memory_size":    memory_size,
        "context_loaded": context_loaded,
    })


@app.get("/v1/capsule/context")
async def get_capsule_context(request: Request):
    """Return what Holo knows about the authenticated user."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    ctx = _capsule_brain.get_capsule_context(capsule["sub"])
    public = {k: v for k, v in ctx.items() if not k.startswith("_") and k != "last_session_id"}
    return JSONResponse(content={"context": public})


@app.post("/v1/capsule/context")
async def seed_capsule_context(request: Request):
    """
    Seed or update facts Holo knows about you.
    Body: { "context": { "key": "value", ... } }
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON.")
    context = body.get("context", {})
    if not isinstance(context, dict):
        raise HTTPException(status_code=400, detail="context must be a dict.")
    for key, value in context.items():
        if key and isinstance(value, str):
            _capsule_brain.set_capsule_context(capsule["sub"], str(key)[:50], str(value)[:500])
    logger.info(f"Capsule seeded for {capsule['sub'][:8]}: {list(context.keys())}")
    return JSONResponse(content={"seeded": list(context.keys())})


@app.get("/billing/status")
async def billing_status(request: Request):
    """Return the current user's plan and quota usage."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")

    if _db is None:
        return JSONResponse(content={"plan": "free", "calls_used": 0, "calls_quota": 1})

    sub = _db.get_or_create_subscription(capsule["sub"], capsule.get("email", ""))
    return JSONResponse(content={
        "plan":        sub["plan"],
        "calls_used":  sub["calls_used"],
        "calls_quota": sub["calls_quota"],
        "overage_rate": 0.15 if sub["plan"] == "starter" else (0.10 if sub["plan"] == "pro" else 0),
    })


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
