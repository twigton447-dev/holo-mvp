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
import asyncio
import logging
import os
import threading
import time
import uuid
from typing import Any, Optional

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

from contextlib import asynccontextmanager, redirect_stdout
import json
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from auth import RateLimiter

# Fail loudly if deployed from the wrong repo (context_governor is private/gitignored in holo-mvp).
# All Railway deployments must come from holo-deploy, not holo-mvp.
if not os.path.exists(os.path.join(os.path.dirname(__file__), "context_governor.py")):
    raise RuntimeError(
        "DEPLOYMENT ERROR: context_governor.py is missing. "
        "This app must be deployed from holo-deploy, not holo-mvp. "
        "Disable auto-deploy on holo-mvp in the Railway dashboard."
    )

from context_governor import ContextGovernor
from chat_engine import HoloChatEngine, SessionOwnershipError, _safe_handoff_transition
from holochat_onboarding import build_onboarding_context_writes
from holochat_message_connectors import (
    HoloChatMessageConnectorStore,
    MessageConnectorAuthenticationError,
    MessageConnectorError,
    normalize_connector_request,
    normalize_message_event,
)
from holochat_scope import AccessContext, ScopeKind
from holochat_scope_store import HoloChatScopeStore, ScopeResolutionError
from auth_capsule import handle_google_signin, handle_email_signin, get_capsule_from_request, request_password_reset, reset_password, _brain as _capsule_brain
from db import Database
from billing import create_checkout_session, create_customer_portal_session, construct_webhook_event, PLANS

_rate_limiter = RateLimiter()
_db: Database | None = None

# Governor is instantiated once at startup and reused for every request.
# This means adapters are initialized once (SDK clients, auth, etc.).
_governor: ContextGovernor | None = None
_chat_engine: Optional[HoloChatEngine] = None
_message_connector_store: HoloChatMessageConnectorStore | None = None


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

    async def _memory_idle_sweeper() -> None:
        interval = max(30, int(os.getenv("HOLOCHAT_MEMORY_IDLE_SWEEP_SECONDS", "60")))
        idle_seconds = max(60, int(os.getenv("HOLOCHAT_MEMORY_IDLE_SECONDS", "900")))
        while True:
            await asyncio.sleep(interval)
            try:
                if _chat_engine is not None:
                    _chat_engine.checkpoint_idle_sessions(idle_seconds=idle_seconds)
            except Exception as exc:
                logger.warning("HoloChat memory idle sweep failed: %s", exc)

    idle_task = asyncio.create_task(_memory_idle_sweeper())
    logger.info("Holo API server ready.")
    try:
        yield
    finally:
        idle_task.cancel()
        try:
            await idle_task
        except asyncio.CancelledError:
            pass
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
                 cost_usd: Optional[float] = None, latency_ms: int = 0,
                 access_context: Optional[AccessContext] = None,
                 worker_identity: Optional[dict[str, Any]] = None,
                 hologov_identity: Optional[dict[str, Any]] = None,
                 session_id: Optional[str] = None) -> None:
    """Fire-and-forget usage log. Never raises."""
    if access_context is not None:
        logger.info(
            "HoloChat request authorization",
            extra={
                "holochat_access": access_context.operator_metadata(),
                "holochat_endpoint": endpoint,
                "holochat_status_code": status_code,
            },
        )
    if worker_identity is not None or hologov_identity is not None:
        logger.info(
            "HoloChat runtime usage telemetry",
            extra={
                "holochat_endpoint": endpoint,
                "holochat_worker_identity": worker_identity,
                "holochat_hologov_identity": hologov_identity,
                "holochat_cost_usd": cost_usd,
                "holochat_session_id": session_id,
            },
        )
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


def _chat_usage_telemetry(result: dict[str, Any]) -> dict[str, Any]:
    """Extract final, non-client-facing spend and runtime identities."""
    runtime = result.get("runtime")
    runtime = runtime if isinstance(runtime, dict) else {}
    cost_breakdown = runtime.get("cost_breakdown")
    cost_breakdown = cost_breakdown if isinstance(cost_breakdown, dict) else {}
    worker_identity = runtime.get("selected_analyst")
    worker_identity = worker_identity if isinstance(worker_identity, dict) else None
    context_telemetry = runtime.get("context_telemetry")
    context_telemetry = context_telemetry if isinstance(context_telemetry, dict) else {}
    hologov_identity = context_telemetry.get("gov_model")
    hologov_identity = hologov_identity if isinstance(hologov_identity, dict) else None

    # Do not fall back to the worker-only estimate: it excludes HoloGov spend.
    return {
        "cost_usd": cost_breakdown.get("turn_estimated_cost_usd"),
        "worker_identity": worker_identity,
        "hologov_identity": hologov_identity,
    }


def _private_runtime_metadata_enabled() -> bool:
    """Private control telemetry is local/operator-only and off by default."""
    return os.getenv("HOLOCHAT_EXPOSE_PRIVATE_RUNTIME", "0").strip().lower() in {
        "1", "true", "yes", "on",
    }


def _public_stream_metadata(chunk: dict[str, Any]) -> dict[str, Any]:
    payload = {key: value for key, value in chunk.items() if key != "done" and not key.startswith("_")}
    if not _private_runtime_metadata_enabled():
        for key in ("context_budget", "runtime", "holo4dna", "usage"):
            payload.pop(key, None)
    return payload


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


def _chat_capsule_id(request: Request, api_key: str) -> Optional[str]:
    """Resolve the capsule that may access durable chat state for this request."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    token_capsule_id = capsule.get("sub") if capsule else None

    key_capsule_id = None
    lookup_key_capsule = getattr(_db, "get_capsule_id_for_key", None) if _db else None
    if callable(lookup_key_capsule):
        try:
            key_capsule_id = lookup_key_capsule(api_key)
        except Exception as exc:
            logger.warning("Unable to resolve API-key capsule binding: %s", exc)

    if token_capsule_id and key_capsule_id and token_capsule_id != key_capsule_id:
        raise HTTPException(status_code=403, detail="JWT and API key belong to different capsules.")
    return token_capsule_id or key_capsule_id


def _hybrid_scopes_enabled() -> bool:
    return str(os.getenv("HOLOCHAT_HYBRID_SCOPES_ENABLED", "")).strip().lower() in {"1", "true", "yes", "on"}


def _requested_scope_id(request: Request, body: Optional[dict[str, Any]] = None) -> Optional[str]:
    header_scope = str(request.headers.get("X-Holo-Scope-Id") or "").strip() or None
    body_scope = str((body or {}).get("scope_id") or "").strip() or None
    if header_scope and body_scope and header_scope != body_scope:
        raise HTTPException(status_code=400, detail="Conflicting scope selection.")
    return header_scope or body_scope


def _resolve_active_scope(
    request: Request,
    capsule_id: Optional[str],
    body: Optional[dict[str, Any]] = None,
) -> Optional[AccessContext]:
    """Resolve a client-requested scope from server-owned identity/membership data."""
    requested_scope = _requested_scope_id(request, body)
    if not _hybrid_scopes_enabled():
        if requested_scope:
            raise HTTPException(status_code=409, detail="Hybrid scopes are not enabled.")
        return None
    if not capsule_id:
        raise HTTPException(status_code=401, detail="Sign in required.")
    client = getattr(_capsule_brain, "_client", None)
    if client is None:
        raise HTTPException(status_code=503, detail="Scope authorization is unavailable.")
    try:
        access_context = HoloChatScopeStore(client).resolve(capsule_id, requested_scope)
    except (ScopeResolutionError, TypeError, ValueError):
        raise HTTPException(status_code=404, detail="Scope not found.")
    request.state.access_context = access_context
    logger.info(
        "HoloChat scope authorized",
        extra={"holochat_access": access_context.operator_metadata()},
    )
    return access_context


def _message_connectors() -> HoloChatMessageConnectorStore:
    """Return the server-owned connector store or fail closed."""
    if _message_connector_store is not None:
        return _message_connector_store
    client = getattr(_capsule_brain, "_client", None)
    if client is None:
        raise HTTPException(status_code=503, detail="Message connections are unavailable.")
    return HoloChatMessageConnectorStore(client)


def _personal_external_connector_access(
    request: Request,
    capsule_id: str,
    body: Optional[dict[str, Any]] = None,
) -> AccessContext:
    """Enforce durable Personal scope ownership for sensitive source connectors."""
    if not _hybrid_scopes_enabled():
        raise HTTPException(status_code=409, detail="Personal connections require scoped Personal storage.")
    access_context = _resolve_active_scope(request, capsule_id, body)
    if access_context is None or access_context.scope_kind is not ScopeKind.PERSONAL:
        raise HTTPException(status_code=403, detail="Personal connections can only connect to HoloPersonal.")
    return access_context


def _personal_message_access(
    request: Request,
    capsule_id: str,
    body: Optional[dict[str, Any]] = None,
) -> AccessContext:
    """Phone-message connectors require durable Personal scope enforcement."""
    return _personal_external_connector_access(request, capsule_id, body)


def _bind_session_access(
    request: Request,
    access_context: Optional[AccessContext],
    session_id: Optional[str],
) -> Optional[AccessContext]:
    """Keep session-bound authority available for authorization and telemetry."""
    if access_context is None:
        return None
    bound = access_context.for_session(session_id)
    request.state.access_context = bound
    if bound.session_id:
        logger.info(
            "HoloChat session authority bound",
            extra={"holochat_access": bound.operator_metadata()},
        )
    return bound


def _require_session_ownership(
    session_id: str,
    capsule_id: Optional[str],
    *,
    allow_new_session: bool = False,
    access_context: Optional[AccessContext] = None,
) -> None:
    """Reject durable chat access unless an existing session has the exact owner."""
    if access_context is not None and access_context.session_id != session_id:
        raise HTTPException(status_code=404, detail="Session not found.")
    session = _capsule_brain.get_chat_session(session_id)
    if session is None and allow_new_session:
        return
    scope_id = access_context.scope_id if access_context else None
    durable_owner = session.get("scope_id") if session and scope_id else session.get("capsule_id") if session else None
    if not session or not capsule_id or durable_owner != (scope_id or capsule_id):
        raise HTTPException(status_code=404, detail="Session not found.")


_THREAD_METADATA_CONTEXT_KEY = "_holo_thread_metadata_v1"
_THREAD_METADATA_MAX_ENTRIES = 160


def _clean_thread_life_area(value: Any) -> str:
    """Accept only a compact category key, never arbitrary metadata."""
    area = str(value or "").strip().lower()
    if not area or len(area) > 40:
        return ""
    return area if all(char.isalnum() or char in {"-", "_"} for char in area) else ""


def _clean_thread_title(value: Any) -> str:
    """Normalize a user-facing title without changing the durable session ID."""
    title = " ".join(str(value or "").split())
    return title[:80]


def _read_thread_metadata(capsule_id: str, *, scope_id: Optional[str] = None) -> dict[str, dict[str, str]]:
    """Read scope-local, non-model-visible thread display metadata."""
    try:
        context = _capsule_brain.get_capsule_context(
            capsule_id,
            **({"scope_id": scope_id} if scope_id else {}),
        ) or {}
        raw = context.get(_THREAD_METADATA_CONTEXT_KEY, "")
        decoded = json.loads(str(raw or "")) if raw else {}
    except Exception:
        return {}
    if not isinstance(decoded, dict):
        return {}

    cleaned: dict[str, dict[str, str]] = {}
    for session_id, value in decoded.items():
        sid = str(session_id or "").strip()
        if not sid or len(sid) > 160 or not isinstance(value, dict):
            continue
        entry: dict[str, str] = {}
        area = _clean_thread_life_area(value.get("life_area"))
        title = _clean_thread_title(value.get("title"))
        if area:
            entry["life_area"] = area
        if title:
            entry["title"] = title
        if entry:
            cleaned[sid] = entry
    return cleaned


def _write_thread_metadata(
    capsule_id: str,
    metadata: dict[str, dict[str, str]],
    *,
    scope_id: Optional[str] = None,
) -> None:
    """Persist only bounded display metadata in the caller's authorized scope."""
    while len(metadata) > _THREAD_METADATA_MAX_ENTRIES:
        metadata.pop(next(iter(metadata)))
    _capsule_brain.set_capsule_context(
        capsule_id,
        _THREAD_METADATA_CONTEXT_KEY,
        json.dumps(metadata, ensure_ascii=True, separators=(",", ":")),
        **({"scope_id": scope_id} if scope_id else {}),
    )


def _remove_thread_metadata(
    capsule_id: str,
    session_id: str,
    *,
    scope_id: Optional[str] = None,
) -> None:
    metadata = _read_thread_metadata(capsule_id, scope_id=scope_id)
    if str(session_id) not in metadata:
        return
    metadata.pop(str(session_id), None)
    _write_thread_metadata(capsule_id, metadata, scope_id=scope_id)


def _reject_durable_incognito_session(session_id: str) -> None:
    """Incognito threads never restore durable history, regardless of its owner."""
    if _capsule_brain.get_chat_session(session_id) is not None:
        raise HTTPException(status_code=404, detail="Session not found.")


def _get_owned_engine_session(
    session_id: str,
    capsule_id: Optional[str],
    access_context: Optional[AccessContext] = None,
):
    """Restore an owned non-incognito session without exposing owner details."""
    try:
        kwargs = {"capsule_id": capsule_id, "incognito": False}
        scope_id = access_context.scope_id if access_context else None
        if scope_id:
            kwargs["scope_id"] = scope_id
        return _chat_engine.get_or_create_session(session_id, **kwargs)
    except SessionOwnershipError:
        raise HTTPException(status_code=404, detail="Session not found.")


def _get_incognito_engine_session(session_id: str):
    """Create or resume only an isolated in-memory incognito session."""
    try:
        return _chat_engine.get_or_create_session(
            session_id,
            capsule_id=None,
            incognito=True,
        )
    except SessionOwnershipError:
        raise HTTPException(status_code=404, detail="Session not found.")


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
    google_auth_enabled = (
        os.getenv("HOLOCHAT_GOOGLE_AUTH_ENABLED", "").strip().lower()
        in {"1", "true", "yes", "on"}
    )
    return {
        "google_client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "google_auth_enabled": google_auth_enabled and bool(os.getenv("GOOGLE_CLIENT_ID", "").strip()),
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


# ---------------------------------------------------------------------------
# /v1/evaluate — OpenClaw-compatible evaluation endpoint
# ---------------------------------------------------------------------------

class EvaluateRequest(BaseModel):
    client_id: str
    domain: str
    action_payload: dict


def _verify_bearer(request: Request) -> str:
    """
    Extract and validate a Bearer token from the Authorization header.
    Validates against Supabase api_keys table, falls back to HOLO_API_KEY env var.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header. Expected: Bearer <token>")
    token = auth_header[len("Bearer "):]
    if not token:
        raise HTTPException(status_code=401, detail="Empty Bearer token.")

    key_id = hashlib.sha256(token.encode()).hexdigest()[:16]

    # 1. Supabase api_keys table
    if _db is not None:
        row = _db.validate_api_key(token)
        if row:
            max_rpm = row.get("max_requests_per_minute", 60)
            if not _rate_limiter.check(key_id, max_rpm):
                raise HTTPException(status_code=429, detail=f"Rate limit exceeded ({max_rpm} req/min).")
            return token

    # 2. Env var fallback
    expected = os.getenv("HOLO_API_KEY", "")
    if expected:
        if hmac.compare_digest(
            hashlib.sha256(token.encode()).digest(),
            hashlib.sha256(expected.encode()).digest(),
        ):
            max_rpm = int(os.getenv("HOLO_MAX_RPM", "60"))
            if not _rate_limiter.check(key_id, max_rpm):
                raise HTTPException(status_code=429, detail=f"Rate limit exceeded ({max_rpm} req/min).")
            return token

    raise HTTPException(status_code=401, detail="Invalid Bearer token.")


def _map_confidence(result: dict) -> str:
    """Map governor result to HIGH / MEDIUM / LOW confidence."""
    if result.get("partial"):
        return "LOW"
    coverage = result.get("coverage_matrix", {})
    any_high = any(v.get("max_severity") == "HIGH" for v in coverage.values())
    if any_high:
        return "HIGH"
    if result.get("converged"):
        return "HIGH"
    return "MEDIUM"


@app.post("/v1/evaluate")
async def evaluate_v1(
    body: EvaluateRequest,
    request: Request,
    _key: str = Depends(_verify_bearer),
):
    """
    OpenClaw evaluation endpoint.

    Accepts a structured action payload and returns a simple verdict.
    On provider failure, returns ESCALATE with a provider_error field instead of crashing.
    """
    if _governor is None:
        raise HTTPException(status_code=503, detail="Engine not initialized.")

    evaluation_id = f"holo_{__import__('uuid').uuid4().hex[:8]}"
    t0 = time.time()

    # Adapt the incoming payload to the governor's expected shape
    governor_request = {
        "action": {
            "type": body.domain,
            **body.action_payload,
        },
        "context": body.action_payload,
    }

    try:
        result = _governor.evaluate(governor_request)
    except Exception as e:
        elapsed = int((time.time() - t0) * 1000)
        logger.error(f"[/v1/evaluate] provider error: {type(e).__name__}: {e}", exc_info=True)

        error_payload = {
            "evaluation_id": evaluation_id,
            "verdict": "ESCALATE",
            "confidence": "LOW",
            "primary_signal": None,
            "latency_ms": elapsed,
            "provider_error": str(e),
        }

        # Best-effort Supabase log — never blocks response
        if _db is not None:
            try:
                _db.log_evaluation({
                    "evaluation_id": evaluation_id,
                    "client_id": body.client_id,
                    "domain": body.domain,
                    "decision": "ESCALATE",
                    "confidence": "LOW",
                    "primary_signal": None,
                    "latency_ms": elapsed,
                    "provider_error": str(e),
                    "rounds_completed": 0,
                    "total_cost_usd": 0.0,
                })
            except Exception:
                pass

        return JSONResponse(content=error_payload)

    elapsed = int((time.time() - t0) * 1000)

    verdict        = result.get("decision", "ESCALATE")
    confidence     = _map_confidence(result)
    primary_signal = result.get("decision_reason") or None

    response_payload = {
        "evaluation_id": result.get("evaluation_id", evaluation_id),
        "verdict": verdict,
        "confidence": confidence,
        "primary_signal": primary_signal,
        "latency_ms": elapsed,
    }

    # Log to Supabase
    if _db is not None:
        try:
            tokens = result.get("total_tokens", {})
            _db.log_evaluation({
                "evaluation_id": response_payload["evaluation_id"],
                "client_id": body.client_id,
                "domain": body.domain,
                "decision": verdict,
                "confidence": confidence,
                "primary_signal": primary_signal,
                "latency_ms": elapsed,
                "rounds_completed": result.get("turns_completed", 0),
                "total_cost_usd": tokens.get("total_cost_usd", 0.0),
            })
        except Exception as log_err:
            logger.warning(f"[/v1/evaluate] Supabase log failed: {log_err}")

    _track_usage(_key, "/v1/evaluate", 200, latency_ms=elapsed)

    return JSONResponse(content=response_payload)


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
    """Switch the visible Holo space after server-side scope authorization."""
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
    access_context = None
    if _hybrid_scopes_enabled():
        access_context = _resolve_active_scope(request, capsule["sub"], body)
        expected_kind = "enterprise" if mode == "work" else "personal"
        if access_context.scope_kind.value != expected_kind:
            raise HTTPException(status_code=403, detail="Selected space is not authorized for this mode.")
    elif mode == "work":
        raise HTTPException(status_code=409, detail="Enterprise access is not configured for this account.")
    _capsule_brain.set_capsule_mode(capsule["sub"], mode)
    return JSONResponse(content={
        "capsule_id": capsule["sub"],
        "mode": mode,
        "scope_id": access_context.scope_id if access_context else None,
    })


@app.get("/auth/spaces")
async def list_authorized_spaces(request: Request):
    """Discover Personal plus currently authorized Enterprise spaces.

    This endpoint is only a UI affordance. The scope resolver remains the
    enforcement point for mode changes and every scoped request.
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Invalid or missing capsule token.")
    if not _hybrid_scopes_enabled():
        return JSONResponse(content={
            "hybrid_scopes_enabled": False,
            "spaces": [{"scope_id": None, "kind": "personal"}],
        })
    client = getattr(_capsule_brain, "_client", None)
    if client is None:
        raise HTTPException(status_code=503, detail="Scope authorization is unavailable.")
    try:
        spaces = HoloChatScopeStore(client).list_authorized_spaces(capsule["sub"])
    except (ScopeResolutionError, TypeError, ValueError):
        raise HTTPException(status_code=403, detail="No authorized Personal space is available.")
    return JSONResponse(content={"hybrid_scopes_enabled": True, "spaces": spaces})


@app.get("/v1/capsule/message-connectors")
async def list_message_connectors(request: Request):
    """List browser-safe Personal phone-message connector state."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    access_context = _personal_message_access(request, capsule["sub"])
    return JSONResponse(content={"connectors": _message_connectors().list_for_scope(access_context.scope_id)})


@app.post("/v1/capsule/message-connectors")
async def prepare_message_connector(request: Request):
    """Create a one-time secret for a read-only Personal message bridge.

    The returned secret is shown once to the authenticated owner. It permits
    normalized context-event ingestion only, never raw transcript upload or
    cross-scope transfer.
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Request body must be an object.")
    access_context = _personal_message_access(request, capsule["sub"], body)
    try:
        request_data = normalize_connector_request(body)
        connector, secret = _message_connectors().create_pending(
            scope_id=access_context.scope_id,
            capsule_id=capsule["sub"],
            provider=request_data["provider"],
            label=request_data["label"],
        )
    except MessageConnectorError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Message connector setup failed: %s", type(exc).__name__, exc_info=True)
        raise HTTPException(status_code=500, detail="Message connection could not be prepared.") from exc

    logger.info(
        "Personal message connector prepared",
        extra={"capsule": capsule["sub"][:8], "scope_id": access_context.scope_id, "provider": connector["provider"]},
    )
    return JSONResponse(content={
        "connector": connector,
        "ingest": {
            "endpoint": "/v1/connectors/messages/events",
            "connector_id": connector["connector_id"],
            "connector_secret": secret,
            "capability": "message_context_ingest",
            "raw_messages_accepted": False,
        },
    }, status_code=201)


@app.post("/v1/capsule/message-connectors/{connector_id}/pause")
async def pause_message_connector(connector_id: str, request: Request):
    """Stop future Personal message context intake without deleting its audit trail."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    access_context = _personal_message_access(request, capsule["sub"])
    connector = _message_connectors().pause(scope_id=access_context.scope_id, connector_id=connector_id)
    if connector is None:
        raise HTTPException(status_code=404, detail="Active message connection not found.")
    return JSONResponse(content={"connector": connector})


@app.delete("/v1/capsule/message-connectors/{connector_id}")
async def revoke_message_connector(connector_id: str, request: Request):
    """Permanently revoke future ingestion from one Personal message connector."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    access_context = _personal_message_access(request, capsule["sub"])
    connector = _message_connectors().revoke(scope_id=access_context.scope_id, connector_id=connector_id)
    if connector is None:
        raise HTTPException(status_code=404, detail="Message connection not found.")
    return JSONResponse(content={"connector": connector})


@app.post("/v1/connectors/messages/events")
async def ingest_message_context_event(request: Request):
    """Accept one normalized event from a paired local message bridge.

    This endpoint does not accept a user JWT because it is called by a local
    bridge. The connector's one-time secret, scoped connector record, and
    restrictive payload contract provide the authentication boundary.
    """
    connector_id = str(request.headers.get("X-Holo-Connector-Id") or "").strip()
    connector_secret = str(request.headers.get("X-Holo-Connector-Secret") or "").strip()
    if not connector_id or not connector_secret:
        raise HTTPException(status_code=401, detail="Connector credentials are required.")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")
    try:
        event = normalize_message_event(body)
        result, duplicate = _message_connectors().ingest_event(
            connector_id=connector_id,
            secret=connector_secret,
            event=event,
        )
    except MessageConnectorAuthenticationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except MessageConnectorError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Message context ingestion failed: %s", type(exc).__name__, exc_info=True)
        raise HTTPException(status_code=500, detail="Message context could not be recorded.") from exc
    return JSONResponse(content={**result, "duplicate": duplicate, "raw_messages_accepted": False})


@app.get("/")
@app.get("/index.html")
def serve_landing():
    """Serve the Holo landing page."""
    landing = _frontend_dir / "index.html"
    if landing.exists():
        return FileResponse(str(landing))
    return {"status": "ok", "message": "Holo API running. Frontend not found."}


@app.get("/openclaw")
@app.get("/openclaw.html")
def serve_openclaw():
    """Serve the OpenClaw security brief."""
    f = _frontend_dir / "openclaw.html"
    if f.exists():
        return FileResponse(str(f))
    raise HTTPException(status_code=404, detail="Not found.")


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
    handoff_transition = None if incognito else _safe_handoff_transition(body.get("handoff_transition"))

    # Attach capsule identity if a capsule token is provided
    capsule_id = _chat_capsule_id(request, _key)
    access_context = None if incognito else _resolve_active_scope(request, capsule_id, body)
    access_context = _bind_session_access(request, access_context, session_id)
    scope_id = access_context.scope_id if access_context else None
    # Incognito: treat as anonymous regardless of sign-in state
    if session_id:
        if incognito:
            _reject_durable_incognito_session(session_id)
        else:
            _require_session_ownership(
                session_id, capsule_id, allow_new_session=True,
                access_context=access_context,
            )
    capsule_id = capsule_id if not incognito else None

    t0 = time.time()
    try:
        result = _chat_engine.send_message(session_id, message, capsule_id=capsule_id, scope_id=scope_id,
                                           images=images, incognito=incognito,
                                           handoff_transition=handoff_transition)
    except SessionOwnershipError:
        raise HTTPException(status_code=404, detail="Session not found.")
    except Exception as e:
        logger.error(f"Chat engine error: {type(e).__name__}: {e}", exc_info=True)
        _track_usage(_key, "/v1/chat", 500, access_context=access_context)
        raise HTTPException(status_code=500, detail="HoloChat could not complete this turn.")

    elapsed = int((time.time() - t0) * 1000)
    tokens  = result.get("tokens", {})
    usage_telemetry = _chat_usage_telemetry(result)
    access_context = _bind_session_access(request, access_context, result.get("session_id"))
    _track_usage(
        _key, "/v1/chat", 200,
        input_tokens  = tokens.get("input", 0),
        output_tokens = tokens.get("output", 0),
        cost_usd      = usage_telemetry["cost_usd"],
        latency_ms    = elapsed,
        access_context=access_context,
        worker_identity=usage_telemetry["worker_identity"],
        hologov_identity=usage_telemetry["hologov_identity"],
        session_id=result.get("session_id"),
    )

    response_content = {
        "session_id":          result["session_id"],
        "response":            result["response"],
        "turn_number":         result["turn_number"],
        "thread_health_score": result["thread_health_score"],
        "thread_health_level": result["thread_health_level"],
        "elapsed_ms":          result["elapsed_ms"],
        "tokens":              result["tokens"],
        "thought":             result.get("thought"),
        "artifacts":           result.get("artifacts", []),
        "handoff":             result.get("handoff"),
        "conversation_paths":  result.get("conversation_paths", []),
        "searched":            bool(result.get("searched", result.get("search_query") is not None)),
    }
    if result.get("search_query") is not None:
        response_content["search_query"] = result.get("search_query")
    if result.get("web_status") is not None:
        response_content["web_status"] = result.get("web_status")
    if result.get("web_sources"):
        response_content["web_sources"] = result.get("web_sources")
    if result.get("web_citations") is not None:
        response_content["web_citations"] = result.get("web_citations")
    if _private_runtime_metadata_enabled():
        if result.get("context_budget") is not None:
            response_content["context_budget"] = result.get("context_budget")
        if result.get("usage") is not None:
            response_content["usage"] = result.get("usage")
        if result.get("runtime") is not None:
            response_content["runtime"] = result.get("runtime")
        if result.get("holo4dna") is not None:
            response_content["holo4dna"] = result.get("holo4dna")
    return JSONResponse(content=response_content)


@app.post("/v1/chat/stream")
async def chat_stream(
    request: Request,
    _key: str = Depends(_verify_key),
):
    """
    Server-Sent Events variant of /v1/chat.

    Streams analyst tokens as they arrive. Each SSE event carries a JSON payload:
      {"type": "token",     "text": "..."}          — incremental text chunk
      {"type": "searching"}                          — Governor triggered a web search
      {"type": "done",      "session_id": "...", ...} — final metadata (same fields as /v1/chat)

    Clients must not replay an ambiguous interrupted stream through /v1/chat.
    Preserve the draft and require an explicit user retry instead.
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
    images     = body.get("images") or None
    incognito  = bool(body.get("incognito", False))
    handoff_transition = None if incognito else _safe_handoff_transition(body.get("handoff_transition"))
    capsule_id = _chat_capsule_id(request, _key)
    access_context = None if incognito else _resolve_active_scope(request, capsule_id, body)
    access_context = _bind_session_access(request, access_context, session_id)
    scope_id = access_context.scope_id if access_context else None
    if session_id:
        if incognito:
            _reject_durable_incognito_session(session_id)
        else:
            _require_session_ownership(
                session_id, capsule_id, allow_new_session=True,
                access_context=access_context,
            )
    capsule_id = capsule_id if not incognito else None

    if session_id:
        if incognito:
            _get_incognito_engine_session(session_id)
        else:
            _get_owned_engine_session(session_id, capsule_id, access_context)

    def _sse(event: dict) -> str:
        return f"data: {json.dumps(event)}\n\n"

    def _generate():
        started_at = time.time()
        usage_tracked = False
        try:
            for chunk in _chat_engine.stream_message(
                session_id, message, capsule_id=capsule_id, scope_id=scope_id, images=images,
                incognito=incognito, handoff_transition=handoff_transition
            ):
                if isinstance(chunk, dict) and chunk.get("done"):
                    tokens = chunk.get("tokens") or {}
                    usage_telemetry = _chat_usage_telemetry(chunk)
                    completed_access = _bind_session_access(
                        request, access_context, chunk.get("session_id") or session_id,
                    )
                    _track_usage(
                        _key,
                        "/v1/chat/stream",
                        200,
                        input_tokens=tokens.get("input", 0),
                        output_tokens=tokens.get("output", 0),
                        cost_usd=usage_telemetry["cost_usd"],
                        latency_ms=int((time.time() - started_at) * 1000),
                        access_context=completed_access,
                        worker_identity=usage_telemetry["worker_identity"],
                        hologov_identity=usage_telemetry["hologov_identity"],
                        session_id=chunk.get("session_id"),
                    )
                    usage_tracked = True
                    yield _sse({"type": "done", **_public_stream_metadata(chunk)})
                elif isinstance(chunk, dict) and chunk.get("searching"):
                    yield _sse({"type": "searching", "scope": str(chunk.get("scope") or "current")})
                else:
                    yield _sse({"type": "token", "text": chunk})
        except Exception as e:
            logger.error(f"Stream error: {type(e).__name__}: {e}", exc_info=True)
            if not usage_tracked:
                _track_usage(
                    _key,
                    "/v1/chat/stream",
                    500,
                    latency_ms=int((time.time() - started_at) * 1000),
                    access_context=access_context,
                )
            yield _sse({"type": "error", "detail": "Stream interrupted. Please try again."})

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/v1/capsule/portrait")
async def get_portrait(request: Request, format: str = "json"):
    """
    Return the evolving portrait for the authenticated capsule.

    The portrait is generated fresh from the current state of life_context,
    session consolidations, and capsule context — it always reflects now,
    not a cached snapshot.

    ?format=md   → returns the portrait as a markdown string
    ?format=json → returns structured life_context + recent session notes (default)
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")

    if _capsule_brain._client is None:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    capsule_id = capsule["sub"]
    access_context = _resolve_active_scope(request, capsule_id)
    scope_id = access_context.scope_id if access_context else None
    scope_kwargs = {"scope_id": scope_id} if scope_id else {}

    if format == "md":
        md = _capsule_brain.generate_portrait_md(capsule_id, **scope_kwargs)
        return JSONResponse(content={"portrait_md": md, "capsule_id": capsule_id})

    # JSON format — structured data
    life_context   = _capsule_brain.load_life_context(capsule_id, **scope_kwargs)
    last_note      = _capsule_brain.load_last_consolidation(capsule_id, **scope_kwargs)
    capsule_ctx    = _capsule_brain.get_capsule_context(capsule_id, **scope_kwargs)

    return JSONResponse(content={
        "capsule_id":     capsule_id,
        "life_context":   life_context,
        "last_session":   last_note,
        "capsule_context": {k: v for k, v in capsule_ctx.items() if not k.startswith("_")},
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
    access_context = _resolve_active_scope(request, capsule["sub"])
    scope_id = access_context.scope_id if access_context else None
    ctx = _capsule_brain.get_capsule_context(capsule["sub"], **({"scope_id": scope_id} if scope_id else {}))
    session_id = ctx.get("last_session_id")
    if not session_id:
        return JSONResponse(content={"session_id": None, "history": []})
    access_context = _bind_session_access(request, access_context, session_id)
    _require_session_ownership(session_id, capsule["sub"], access_context=access_context)
    # Restore into engine memory (loads from Supabase if not already in memory)
    if _chat_engine:
        session = _get_owned_engine_session(session_id, capsule["sub"], access_context)
        history = session.history
    else:
        history = _capsule_brain.load_chat_history(
            session_id,
            capsule_id=capsule["sub"],
            **({"scope_id": scope_id} if scope_id else {}),
        ) or []
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
    access_context = _resolve_active_scope(request, capsule["sub"])
    scope_id = access_context.scope_id if access_context else None
    sessions = _capsule_brain.list_sessions(capsule["sub"], **({"scope_id": scope_id} if scope_id else {}))
    metadata = _read_thread_metadata(capsule["sub"], scope_id=scope_id)
    # Map to the shape the frontend expects: {id, at, preview, title}
    mapped = [
        {
            "id":      s.get("session_id"),
            "at":      s.get("last_active") or s.get("created_at"),
            "preview": s.get("preview", ""),
            # A human-selected title always wins over the automatic summary title.
            "title":   metadata.get(str(s.get("session_id")), {}).get("title") or s.get("title") or s.get("preview", ""),
            "life_area": metadata.get(str(s.get("session_id")), {}).get("life_area", ""),
        }
        for s in sessions
    ]
    return JSONResponse(content={"sessions": mapped})


@app.post("/v1/capsule/thread-metadata")
async def update_thread_metadata(request: Request):
    """Save a scoped thread title and/or category after exact ownership checks."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON.")
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Request body must be an object.")

    session_id = str(body.get("session_id") or "").strip()
    if not session_id or len(session_id) > 160:
        raise HTTPException(status_code=400, detail="A valid session_id is required.")
    if "life_area" not in body and "title" not in body:
        raise HTTPException(status_code=400, detail="Provide a title or life_area.")

    access_context = _resolve_active_scope(request, capsule["sub"], body)
    access_context = _bind_session_access(request, access_context, session_id)
    _require_session_ownership(session_id, capsule["sub"], access_context=access_context)
    scope_id = access_context.scope_id if access_context else None

    metadata = _read_thread_metadata(capsule["sub"], scope_id=scope_id)
    entry = dict(metadata.get(session_id) or {})
    if "life_area" in body:
        life_area = _clean_thread_life_area(body.get("life_area"))
        if not life_area:
            raise HTTPException(status_code=400, detail="life_area is invalid.")
        entry["life_area"] = life_area
    if "title" in body:
        title = _clean_thread_title(body.get("title"))
        if not title:
            raise HTTPException(status_code=400, detail="title is invalid.")
        entry["title"] = title
        # Keep the session table useful to existing exports without allowing the
        # automatic title worker to replace the user's choice in the list API.
        _capsule_brain.update_session_name(
            capsule["sub"],
            session_id,
            title,
            **({"scope_id": scope_id} if scope_id else {}),
        )

    metadata.pop(session_id, None)
    metadata[session_id] = entry
    _write_thread_metadata(capsule["sub"], metadata, scope_id=scope_id)
    return JSONResponse(content={"session_id": session_id, **entry})


@app.post("/v1/capsule/thread-life-area")
async def update_thread_life_area(request: Request):
    """Compatibility endpoint for clients released before thread metadata v1."""
    return await update_thread_metadata(request)


@app.get("/v1/artifacts")
async def list_artifacts(request: Request):
    """Return all saved artifacts for the authenticated user, newest first."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    access_context = _resolve_active_scope(request, capsule["sub"])
    scope_id = access_context.scope_id if access_context else None
    artifacts = _capsule_brain.list_artifacts(capsule["sub"], **({"scope_id": scope_id} if scope_id else {}))
    return JSONResponse(content={"artifacts": artifacts})


@app.get("/v1/artifacts/{artifact_id}")
async def get_artifact(artifact_id: str, request: Request):
    """Return a single artifact by ID. User must own it."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    access_context = _resolve_active_scope(request, capsule["sub"])
    scope_id = access_context.scope_id if access_context else None
    artifact = _capsule_brain.get_artifact(capsule["sub"], artifact_id, **({"scope_id": scope_id} if scope_id else {}))
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found.")
    return JSONResponse(content=artifact)


_summary_cache: dict = {}
_surface_cache: dict = {}

_SENSITIVE_HOLO_KEY_PARTS = (
    "password",
    "hash",
    "secret",
    "token",
    "api_key",
    "apikey",
    "jwt",
    "cookie",
    "invite",
    "provider_key",
)
_HOLO_BUILD_SPECS_DIR = pathlib.Path(__file__).parent / "holo_builder" / "specs"
_HOLO_BUILD_RESULT_DIRS = (
    pathlib.Path(__file__).parent / "builder_results",
    pathlib.Path(__file__).parent / "holo_builder" / "outputs" / "builder",
)
_holo_build_jobs_lock = threading.RLock()
_holo_build_jobs: dict[str, dict[str, Any]] = {}


def _mask_email(email: str) -> str:
    email = (email or "").strip()
    if "@" not in email:
        return ""
    local, domain = email.split("@", 1)
    if not local:
        return f"*@{domain}"
    if len(local) <= 2:
        return f"{local[0]}***@{domain}"
    return f"{local[0]}***{local[-1]}@{domain}"


def _prefix_suffix(value: str, prefix: int = 8, suffix: int = 4) -> str:
    value = str(value or "")
    if len(value) <= prefix + suffix + 3:
        return value
    return f"{value[:prefix]}...{value[-suffix:]}"


def _is_sensitive_holo_key(key: str) -> bool:
    normalized = (key or "").strip().lower()
    if normalized.startswith("_"):
        return True
    return any(part in normalized for part in _SENSITIVE_HOLO_KEY_PARTS)


def _safe_holo_text(value: Any, limit: int = 420) -> str:
    text = str(value or "").replace("\x00", "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _load_json_file(path: pathlib.Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _holo_build_live_runs_enabled() -> bool:
    return os.getenv("HOLOBUILD_LIVE_RUNS", "").strip().lower() in {"1", "true", "yes", "on"}


def _utc_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _sanitize_holobuild_log_line(value: Any, limit: int = 520) -> str:
    import re
    text = _safe_holo_text(value, limit)
    text = re.sub(r"sk-[A-Za-z0-9_\-]{12,}", "[redacted-key]", text)
    text = re.sub(r"AIza[0-9A-Za-z_\-]{16,}", "[redacted-key]", text)
    text = re.sub(
        r"eyJ[A-Za-z0-9_\-]{12,}\.[A-Za-z0-9_\-]{12,}\.[A-Za-z0-9_\-]{12,}",
        "[redacted-token]",
        text,
    )
    return text


def _select_holobuild_spec(spec_file: str | None = None) -> pathlib.Path:
    if not _HOLO_BUILD_SPECS_DIR.exists():
        raise ValueError("HoloBuild specs directory not found.")
    if spec_file:
        safe_name = pathlib.Path(str(spec_file)).name
        path = _HOLO_BUILD_SPECS_DIR / safe_name
        if not path.exists() or path.suffix != ".json":
            raise ValueError("HoloBuild spec not found.")
        return path
    specs = sorted(_HOLO_BUILD_SPECS_DIR.glob("*.json"))
    if not specs:
        raise ValueError("No HoloBuild specs found.")
    return specs[0]


def _safe_holobuild_specs(limit: int = 20) -> list[dict[str, Any]]:
    if not _HOLO_BUILD_SPECS_DIR.exists():
        return []
    specs: list[dict[str, Any]] = []
    for path in sorted(_HOLO_BUILD_SPECS_DIR.glob("*.json"))[:limit]:
        raw = _load_json_file(path) or {}
        placement = raw.get("artifact_placement_brief") or {}
        specs.append({
            "file": path.name,
            "scenario_id": raw.get("scenario_id") or path.stem,
            "domain": raw.get("domain") or "",
            "target_verdict": raw.get("target_verdict") or "",
            "packet_format": raw.get("packet_format") or "payment_email",
            "minimum_internal_documents": placement.get("minimum_internal_documents"),
        })
    return specs


def _iter_holobuild_result_files(limit: int = 12) -> list[pathlib.Path]:
    found: list[pathlib.Path] = []
    for directory in _HOLO_BUILD_RESULT_DIRS:
        if directory.exists():
            found.extend(path for path in directory.glob("*.json") if path.is_file())
    found.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return found[:limit]


def _safe_holobuild_event(event: dict[str, Any]) -> dict[str, Any]:
    allowed = (
        "turn_number",
        "event",
        "failed_provider",
        "fallback_provider",
        "provider",
        "repair_provider",
        "outcome",
        "target_doc_title",
        "attempt",
        "attempts_used",
        "resolved",
    )
    return {key: _safe_holo_text(event.get(key), 160) for key in allowed if event.get(key) is not None}


def _safe_holobuild_turn(turn: dict[str, Any]) -> dict[str, Any]:
    categories = turn.get("categories") if isinstance(turn.get("categories"), dict) else {}
    high_categories = [
        key for key, value in categories.items()
        if isinstance(value, str) and value.upper() in {"HIGH", "CRITICAL"}
    ]
    return {
        "turn_number": _safe_int(turn.get("turn_number")),
        "turn_type": _safe_holo_text(turn.get("turn_type"), 80),
        "provider": _safe_holo_text(turn.get("provider"), 80),
        "model_id": _safe_holo_text(turn.get("model_id"), 120),
        "elapsed_ms": _safe_int(turn.get("elapsed_ms")),
        "input_tokens": _safe_int(turn.get("input_tokens")),
        "output_tokens": _safe_int(turn.get("output_tokens")),
        "assessment": _safe_holo_text(turn.get("assessment"), 80),
        "verdict": _safe_holo_text(turn.get("verdict"), 80),
        "critical_findings": _safe_holo_text(turn.get("critical_findings"), 420),
        "high_categories": high_categories,
        "error": "present" if turn.get("error") else "",
    }


def _safe_holobuild_governor_brief(brief: dict[str, Any]) -> dict[str, Any]:
    return {
        "after_turn": _safe_int(brief.get("after_turn")),
        "governor_provider": _safe_holo_text(brief.get("governor_provider"), 80),
        "overall_trajectory": _safe_holo_text(brief.get("overall_trajectory"), 80),
        "highest_risk_category": _safe_holo_text(brief.get("highest_risk_category"), 120),
        "brief_for_builder": _safe_holo_text(brief.get("brief_for_builder"), 520),
        "elapsed_ms": _safe_int(brief.get("elapsed_ms")),
        "error": "present" if brief.get("error") else "",
    }


def _safe_holobuild_run(raw: dict[str, Any], path: pathlib.Path) -> dict[str, Any]:
    event_keys = (
        "fallback_events",
        "verdict_drift_events",
        "artifact_collapse_events",
        "builder_json_fallback_events",
        "assertion_violation_events",
    )
    events = {
        key: [_safe_holobuild_event(item) for item in raw.get(key, [])[:8] if isinstance(item, dict)]
        for key in event_keys
    }
    return {
        "file": path.name,
        "builder_id": _safe_holo_text(raw.get("builder_id"), 160),
        "scenario_id": _safe_holo_text(raw.get("scenario_id"), 160),
        "packet_format": _safe_holo_text(raw.get("packet_format"), 80),
        "builder_status": _safe_holo_text(raw.get("builder_status"), 120),
        "converged": bool(raw.get("converged")),
        "retire_signal": bool(raw.get("retire_signal")),
        "exit_reason": _safe_holo_text(raw.get("exit_reason"), 160),
        "turns_completed": _safe_int(raw.get("turns_completed")),
        "qa_turn_count": _safe_int(raw.get("qa_turn_count")),
        "qa_deltas": raw.get("qa_deltas", [])[:10] if isinstance(raw.get("qa_deltas"), list) else [],
        "provider_fallback_used": bool(raw.get("provider_fallback_used")),
        "coverage": raw.get("coverage", {}) if isinstance(raw.get("coverage"), dict) else {},
        "governor_briefs": [
            _safe_holobuild_governor_brief(item)
            for item in raw.get("governor_briefs", [])[:8]
            if isinstance(item, dict)
        ],
        "turn_history": [
            _safe_holobuild_turn(item)
            for item in raw.get("turn_history", [])[:12]
            if isinstance(item, dict)
        ],
        "events": events,
        "total_tokens": {
            "input": _safe_int((raw.get("total_tokens") or {}).get("input")),
            "output": _safe_int((raw.get("total_tokens") or {}).get("output")),
        },
        "timestamp": _safe_holo_text(raw.get("timestamp"), 80),
    }


def _record_holobuild_job_event(job_id: str, kind: str, message: str = "",
                                fields: dict[str, Any] | None = None) -> None:
    event = {
        "at": _utc_iso(),
        "kind": _safe_holo_text(kind, 80),
        "message": _sanitize_holobuild_log_line(message),
    }
    for key, value in (fields or {}).items():
        event[key] = _safe_holo_text(value, 180)
    with _holo_build_jobs_lock:
        job = _holo_build_jobs.get(job_id)
        if not job:
            return
        job.setdefault("events", []).append(event)
        job["events"] = job["events"][-240:]
        job["updated_at"] = event["at"]


class _HoloBuildJobWriter:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self._buffer = ""

    def write(self, text: str) -> int:
        self._buffer += str(text)
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            line = line.strip()
            if line:
                _record_holobuild_job_event(self.job_id, "log", line)
        return len(text)

    def flush(self) -> None:
        line = self._buffer.strip()
        if line:
            _record_holobuild_job_event(self.job_id, "log", line)
        self._buffer = ""


def _has_active_holobuild_job() -> bool:
    with _holo_build_jobs_lock:
        return any(job.get("status") in {"queued", "running"} for job in _holo_build_jobs.values())


def _create_holobuild_job(spec_file: str | None, seed: int | None,
                          force_max_turns: bool, skip_providers: list[str]) -> dict[str, Any]:
    job_id = f"hb_{uuid.uuid4().hex[:12]}"
    now = _utc_iso()
    job = {
        "job_id": job_id,
        "status": "queued",
        "spec_file": _safe_holo_text(spec_file or "", 180),
        "seed": seed,
        "force_max_turns": bool(force_max_turns),
        "skip_providers": [_safe_holo_text(item, 80) for item in skip_providers],
        "created_at": now,
        "updated_at": now,
        "events": [],
        "result": None,
        "result_file": "",
        "error": "",
    }
    with _holo_build_jobs_lock:
        _holo_build_jobs[job_id] = job
    _record_holobuild_job_event(job_id, "queued", "HoloBuild job queued.")
    return _snapshot_holobuild_job(job_id) or job


def _snapshot_holobuild_job(job_id: str) -> dict[str, Any] | None:
    with _holo_build_jobs_lock:
        job = _holo_build_jobs.get(job_id)
        if not job:
            return None
        return {
            "job_id": job.get("job_id"),
            "status": job.get("status"),
            "spec_file": job.get("spec_file", ""),
            "seed": job.get("seed"),
            "force_max_turns": bool(job.get("force_max_turns")),
            "skip_providers": list(job.get("skip_providers") or []),
            "created_at": job.get("created_at"),
            "updated_at": job.get("updated_at"),
            "events": list(job.get("events") or []),
            "result": job.get("result"),
            "result_file": job.get("result_file", ""),
            "error": job.get("error", ""),
        }


def _recent_holobuild_jobs(limit: int = 4) -> list[dict[str, Any]]:
    with _holo_build_jobs_lock:
        job_ids = sorted(
            _holo_build_jobs,
            key=lambda jid: _holo_build_jobs[jid].get("created_at", ""),
            reverse=True,
        )[:limit]
    return [job for jid in job_ids if (job := _snapshot_holobuild_job(jid))]


def _run_holobuild_job(job_id: str, spec_file: str | None, seed: int | None,
                       force_max_turns: bool, skip_providers: list[str],
                       runner: Any | None = None) -> None:
    with _holo_build_jobs_lock:
        if job_id in _holo_build_jobs:
            _holo_build_jobs[job_id]["status"] = "running"
            _holo_build_jobs[job_id]["updated_at"] = _utc_iso()
    try:
        spec_path = _select_holobuild_spec(spec_file)
        spec = _load_json_file(spec_path)
        if not isinstance(spec, dict):
            raise ValueError("HoloBuild spec must be valid JSON.")
        with _holo_build_jobs_lock:
            if job_id in _holo_build_jobs:
                _holo_build_jobs[job_id]["spec_file"] = spec_path.name
        _record_holobuild_job_event(job_id, "start", "Starting HoloBuild live run.", {
            "spec_file": spec_path.name,
            "seed": "" if seed is None else seed,
        })
        if runner is None:
            from holo_builder.loop import run_builder as runner
        writer = _HoloBuildJobWriter(job_id)
        with redirect_stdout(writer):
            result = runner(
                spec,
                seed=seed,
                force_max_turns=force_max_turns,
                skip_providers=skip_providers,
            )
        writer.flush()
        if not isinstance(result, dict):
            raise RuntimeError("HoloBuild runner returned an invalid result.")
        out_dir = _HOLO_BUILD_RESULT_DIRS[0]
        out_dir.mkdir(parents=True, exist_ok=True)
        builder_id = result.get("builder_id") or f"builder_{uuid.uuid4().hex[:12]}"
        result_path = out_dir / f"{pathlib.Path(str(builder_id)).name}.json"
        result_path.write_text(json.dumps(result, indent=2))
        safe_result = _safe_holobuild_run(result, result_path)
        with _holo_build_jobs_lock:
            if job_id in _holo_build_jobs:
                _holo_build_jobs[job_id]["status"] = "completed"
                _holo_build_jobs[job_id]["result"] = safe_result
                _holo_build_jobs[job_id]["result_file"] = result_path.name
                _holo_build_jobs[job_id]["updated_at"] = _utc_iso()
        _record_holobuild_job_event(job_id, "complete", "HoloBuild run completed.", {
            "builder_status": safe_result.get("builder_status", ""),
            "turns_completed": safe_result.get("turns_completed", 0),
        })
    except Exception as exc:
        message = _sanitize_holobuild_log_line(f"{type(exc).__name__}: {exc}", 320)
        with _holo_build_jobs_lock:
            if job_id in _holo_build_jobs:
                _holo_build_jobs[job_id]["status"] = "failed"
                _holo_build_jobs[job_id]["error"] = message
                _holo_build_jobs[job_id]["updated_at"] = _utc_iso()
        _record_holobuild_job_event(job_id, "failed", message)


def _build_holobuild_dashboard_payload(limit: int = 6) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    for path in _iter_holobuild_result_files(limit=limit):
        raw = _load_json_file(path)
        if isinstance(raw, dict):
            runs.append(_safe_holobuild_run(raw, path))
    return {
        "mode": "live_watch" if _holo_build_live_runs_enabled() else "read_only",
        "live_runs_enabled": _holo_build_live_runs_enabled(),
        "specs": _safe_holobuild_specs(),
        "runs": runs,
        "run_count": len(runs),
        "jobs": _recent_holobuild_jobs(),
        "result_locations": ["builder_results", "holo_builder/outputs/builder"],
    }


def _redact_context_entries(context: dict[str, Any]) -> list[dict[str, Any]]:
    entries = []
    for key in sorted(context.keys()):
        sensitive = _is_sensitive_holo_key(key)
        entries.append({
            "key": key,
            "value": "[redacted]" if sensitive else str(context.get(key, "")),
            "redacted": sensitive,
        })
    return entries


def _safe_count_capsule_rows(
    brain, table_name: str, capsule_id: str, scope_id: Optional[str] = None
) -> Optional[int]:
    client = getattr(brain, "_client", None)
    if client is None:
        return None
    try:
        query = client.table(table_name).select("scope_id" if scope_id else "capsule_id", count="exact")
        query = query.eq("scope_id", scope_id) if scope_id else query.eq("capsule_id", capsule_id)
        resp = query.execute()
        return resp.count
    except Exception:
        return None


def _safe_count_session_messages(
    brain, session_ids: list[str], scope_id: Optional[str] = None
) -> Optional[int]:
    client = getattr(brain, "_client", None)
    if client is None or not session_ids:
        return 0
    try:
        query = client.table("holo_chat_messages").select("session_id", count="exact")
        query = query.in_("session_id", session_ids[:200])
        if scope_id:
            query = query.eq("scope_id", scope_id)
        resp = query.execute()
        return resp.count
    except Exception:
        return None


def _safe_recent_messages(
    brain, session_ids: list[str], limit: int, scope_id: Optional[str] = None
) -> list[dict[str, Any]]:
    client = getattr(brain, "_client", None)
    if client is None or not session_ids:
        return []
    try:
        query = client.table("holo_chat_messages").select(
            "session_id, role, content, created_at, turn_number"
        ).in_("session_id", session_ids[:50])
        if scope_id:
            query = query.eq("scope_id", scope_id)
        return query.order("created_at", desc=True).limit(limit).execute().data or []
    except Exception:
        return []


def _safe_recent_consolidations(
    brain, capsule_id: str, limit: int, scope_id: Optional[str] = None
) -> list[dict[str, Any]]:
    client = getattr(brain, "_client", None)
    if client is None:
        last = brain.load_last_consolidation(
            capsule_id, **({"scope_id": scope_id} if scope_id else {})
        )
        return [last] if last else []
    try:
        query = client.table("holo_session_consolidations").select(
            "session_id, created_at, what_changed, what_surfaced, open_threads, captain_note"
        )
        query = query.eq("scope_id", scope_id) if scope_id else query.eq("capsule_id", capsule_id)
        return query.order("created_at", desc=True).limit(limit).execute().data or []
    except Exception:
        last = brain.load_last_consolidation(
            capsule_id, **({"scope_id": scope_id} if scope_id else {})
        )
        return [last] if last else []


def _build_holo_brain_payload(
    capsule: dict[str, Any],
    brain,
    scope_id: Optional[str] = None,
    session_limit: int = 25,
    message_limit: int = 80,
    consolidation_limit: int = 25,
    artifact_limit: int = 50,
) -> dict[str, Any]:
    capsule_id = capsule["sub"]
    scope_kwargs = {"scope_id": scope_id} if scope_id else {}
    capsule_row = brain.get_capsule(capsule_id) or {}
    context = brain.get_capsule_context(capsule_id, **scope_kwargs) or {}
    context_entries = _redact_context_entries(context)
    life_context = brain.load_life_context(capsule_id, **scope_kwargs) or []
    sessions = brain.list_sessions(capsule_id, limit=session_limit, **scope_kwargs) or []
    session_ids = [s.get("session_id") for s in sessions if s.get("session_id")]
    recent_messages = _safe_recent_messages(brain, session_ids, message_limit, scope_id)
    consolidations = _safe_recent_consolidations(brain, capsule_id, consolidation_limit, scope_id)
    artifacts = brain.list_artifacts(capsule_id, limit=artifact_limit, **scope_kwargs) or []

    session_items = []
    for session in sessions:
        sid = session.get("session_id", "")
        session_items.append({
            "id": sid,
            "id_short": _prefix_suffix(sid),
            "created_at": session.get("created_at"),
            "last_active": session.get("last_active"),
            "turn_count": session.get("turn_count") or 0,
            "title": session.get("title") or session.get("preview") or "",
            "preview": session.get("preview") or "",
        })

    grouped_messages: dict[str, list[dict[str, Any]]] = {}
    for row in recent_messages:
        sid = row.get("session_id", "")
        grouped_messages.setdefault(sid, []).append({
            "session_id": sid,
            "session_id_short": _prefix_suffix(sid),
            "role": row.get("role"),
            "content": row.get("content") or "",
            "created_at": row.get("created_at"),
            "turn_number": row.get("turn_number"),
        })

    email = capsule_row.get("email") or capsule.get("email", "")
    message_count = _safe_count_session_messages(brain, session_ids, scope_id)
    return {
        "capsule": {
            "id": capsule_id,
            "id_short": _prefix_suffix(capsule_id),
            "email_masked": _mask_email(email),
            "token_email_masked": _mask_email(capsule.get("email", "")),
            "name": capsule_row.get("name") or "",
            "mode": capsule_row.get("mode") or capsule.get("mode", ""),
            "created_at": capsule_row.get("created_at"),
            "last_active": capsule_row.get("last_active"),
            "identity_type": "capsule_token",
        },
        "capsule_context": {
            "count": _safe_count_capsule_rows(brain, "holo_capsule_context", capsule_id, scope_id) or len(context_entries),
            "redacted_count": sum(1 for item in context_entries if item["redacted"]),
            "entries": context_entries,
        },
        "life_context": {
            "count": _safe_count_capsule_rows(brain, "holo_life_context", capsule_id, scope_id) or len(life_context),
            "entries": life_context,
        },
        "sessions": {
            "count": _safe_count_capsule_rows(brain, "holo_chat_sessions", capsule_id, scope_id) or len(session_items),
            "shown": len(session_items),
            "items": session_items,
        },
        "recent_messages": {
            "count": message_count if message_count is not None else len(recent_messages),
            "shown": len(recent_messages),
            "by_session": grouped_messages,
        },
        "consolidations": {
            "count": _safe_count_capsule_rows(brain, "holo_session_consolidations", capsule_id, scope_id) or len(consolidations),
            "shown": len(consolidations),
            "items": consolidations,
        },
        "artifacts": {
            "count": _safe_count_capsule_rows(brain, "holo_artifacts", capsule_id, scope_id) or len(artifacts),
            "shown": len(artifacts),
            "items": artifacts,
        },
        "limits": {
            "sessions": session_limit,
            "messages": message_limit,
            "consolidations": consolidation_limit,
            "artifacts": artifact_limit,
        },
    }


@app.get("/v1/holo-brain")
async def holo_brain_dashboard(request: Request):
    """Return authenticated capsule memory/dashboard data for local browser inspection."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    access_context = _resolve_active_scope(request, capsule["sub"])
    scope_id = access_context.scope_id if access_context else None
    return JSONResponse(content=_build_holo_brain_payload(capsule, _capsule_brain, scope_id))


@app.get("/v1/holo-build")
async def holo_build_dashboard(request: Request):
    """Return read-only HoloBuild specs and sanitized saved run traces."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    return JSONResponse(content=_build_holobuild_dashboard_payload())


@app.post("/v1/holo-build/runs")
async def start_holo_build_run(request: Request):
    """Start a watched HoloBuild run when explicitly enabled."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    if not _holo_build_live_runs_enabled():
        raise HTTPException(status_code=403, detail="HoloBuild live runs are disabled.")
    if _has_active_holobuild_job():
        raise HTTPException(status_code=409, detail="A HoloBuild run is already active.")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")
    spec_file = body.get("spec_file") or None
    seed_raw = body.get("seed")
    seed = None
    if seed_raw not in (None, ""):
        try:
            seed = int(seed_raw)
        except Exception:
            raise HTTPException(status_code=400, detail="seed must be an integer.")
    force_max_turns = bool(body.get("force_max_turns", False))
    skip_raw = body.get("skip_providers") or []
    if not isinstance(skip_raw, list):
        raise HTTPException(status_code=400, detail="skip_providers must be a list.")
    skip_providers = [str(item) for item in skip_raw if str(item).strip()]
    try:
        _select_holobuild_spec(spec_file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    job = _create_holobuild_job(spec_file, seed, force_max_turns, skip_providers)
    thread = threading.Thread(
        target=_run_holobuild_job,
        args=(job["job_id"], spec_file, seed, force_max_turns, skip_providers),
        daemon=True,
    )
    thread.start()
    return JSONResponse(content=_snapshot_holobuild_job(job["job_id"]) or job)


@app.get("/v1/holo-build/runs/{job_id}")
async def get_holo_build_run(job_id: str, request: Request):
    """Return a sanitized watched HoloBuild job snapshot."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    job = _snapshot_holobuild_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="HoloBuild job not found.")
    return JSONResponse(content=job)


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
    access_context = _resolve_active_scope(request, capsule_id)
    scope_id = access_context.scope_id if access_context else None
    scope_kwargs = {"scope_id": scope_id} if scope_id else {}

    # Return cached result if fresh (< 30 min)
    cache_key = f"{capsule_id}:{scope_id or 'personal'}"
    cached = _surface_cache.get(cache_key)
    if cached and (time.time() - cached["ts"]) < 1800:
        return JSONResponse(content=cached["data"])

    if _chat_engine is None:
        raise HTTPException(status_code=503, detail="Chat engine not initialized.")

    context = _capsule_brain.get_capsule_context(capsule_id, **scope_kwargs) or {}
    sessions = _capsule_brain.list_sessions(capsule_id, **scope_kwargs)
    result = _chat_engine._captain.generate_surface(context, sessions)
    if not result:
        return JSONResponse(content={"topics": [], "todos": []})

    _surface_cache[cache_key] = {"data": result, "ts": time.time()}
    return JSONResponse(content=result)


@app.get("/v1/chat/{session_id}/summary")
async def thread_summary(
    session_id: str,
    request: Request,
    _key: str = Depends(_verify_key),
):
    """Return a Governor-written summary of the thread for sidebar hover preview."""
    capsule_id = _chat_capsule_id(request, _key)
    access_context = _resolve_active_scope(request, capsule_id)
    access_context = _bind_session_access(request, access_context, session_id)
    scope_id = access_context.scope_id if access_context else None
    _require_session_ownership(session_id, capsule_id, access_context=access_context)
    if session_id in _summary_cache:
        return JSONResponse(content={"summary": _summary_cache[session_id]})
    if _chat_engine is None:
        raise HTTPException(status_code=503, detail="Chat engine not initialized.")
    # Try in-memory session first, fall back to DB
    session = _get_owned_engine_session(session_id, capsule_id, access_context)
    history = session.history
    if not history:
        history = _capsule_brain.load_chat_history(
            session_id,
            capsule_id=capsule_id,
            **({"scope_id": scope_id} if scope_id else {}),
        ) or []
    if not history:
        raise HTTPException(status_code=404, detail="Session not found.")
    summary = _chat_engine._captain.summarize_thread(history)
    if summary:
        _summary_cache[session_id] = summary
    return JSONResponse(content={"summary": summary})


@app.get("/v1/chat/{session_id}/history")
async def chat_history(
    session_id: str,
    request: Request,
    _key: str = Depends(_verify_key),
):
    """Return the full message history for a session."""
    capsule_id = _chat_capsule_id(request, _key)
    access_context = _resolve_active_scope(request, capsule_id)
    access_context = _bind_session_access(request, access_context, session_id)
    scope_id = access_context.scope_id if access_context else None
    _require_session_ownership(session_id, capsule_id, access_context=access_context)
    if _chat_engine is None:
        raise HTTPException(status_code=503, detail="Chat engine not initialized.")
    # Try in-memory first, then fall back to Supabase via session restore
    session = _get_owned_engine_session(session_id, capsule_id, access_context)
    history = session.history
    if not history:
        raise HTTPException(status_code=404, detail="Session not found.")
    return JSONResponse(content={"session_id": session_id, "history": history})


@app.post("/v1/chat/{session_id}/memory-checkpoint")
async def checkpoint_chat_memory(session_id: str, request: Request):
    """Persist a thread-open/fork lifecycle boundary without invoking a model."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    try:
        body = await request.json()
    except Exception:
        body = {}
    lifecycle = str(body.get("lifecycle") or "thread_fork").strip().lower()
    if lifecycle not in {"thread_open", "thread_fork"}:
        raise HTTPException(status_code=400, detail="Unsupported checkpoint lifecycle.")
    capsule_id = capsule["sub"]
    access_context = _resolve_active_scope(request, capsule_id, body)
    access_context = _bind_session_access(request, access_context, session_id)
    scope_id = access_context.scope_id if access_context else None
    _require_session_ownership(session_id, capsule_id, access_context=access_context)
    if _chat_engine is None:
        raise HTTPException(status_code=503, detail="Chat engine not initialized.")
    try:
        result = _chat_engine.checkpoint_memory_lifecycle(
            session_id,
            lifecycle,
            capsule_id=capsule_id,
            scope_id=scope_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    status_code = 409 if result.get("status") == "blocked_unresolved_urgent_memory" else 200
    return JSONResponse(content=result, status_code=status_code)


@app.delete("/v1/chat/{session_id}")
async def clear_chat(
    session_id: str,
    request: Request,
    _key: str = Depends(_verify_key),
):
    """Clear a chat session and start fresh."""
    capsule_id = _chat_capsule_id(request, _key)
    access_context = _resolve_active_scope(request, capsule_id)
    access_context = _bind_session_access(request, access_context, session_id)
    scope_id = access_context.scope_id if access_context else None
    _require_session_ownership(session_id, capsule_id, access_context=access_context)
    if _chat_engine is None:
        raise HTTPException(status_code=503, detail="Chat engine not initialized.")
    try:
        cleared = _chat_engine.clear_session(session_id, capsule_id=capsule_id, scope_id=scope_id)
    except SessionOwnershipError:
        raise HTTPException(status_code=404, detail="Session not found.")
    return JSONResponse(content={"cleared": cleared, "session_id": session_id})


@app.delete("/v1/session/{session_id}")
async def delete_session(
    session_id: str,
    request: Request,
    _key: str = Depends(_verify_key),
):
    """Permanently delete a session and all its messages. User must own the session."""
    capsule_id = _chat_capsule_id(request, _key)
    access_context = _resolve_active_scope(request, capsule_id)
    access_context = _bind_session_access(request, access_context, session_id)
    scope_id = access_context.scope_id if access_context else None
    _require_session_ownership(session_id, capsule_id, access_context=access_context)
    if _chat_engine:
        try:
            _chat_engine.clear_session(session_id, capsule_id=capsule_id, scope_id=scope_id)
        except SessionOwnershipError:
            raise HTTPException(status_code=404, detail="Session not found.")
    deleted = _capsule_brain.delete_session(capsule_id, session_id, **({"scope_id": scope_id} if scope_id else {}))
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found or access denied.")
    try:
        _remove_thread_metadata(capsule_id, session_id, scope_id=scope_id)
    except Exception as exc:
        logger.warning("HoloChat thread metadata cleanup failed: %s", exc)
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
    access_context = _resolve_active_scope(request, capsule["sub"])
    scope_id = access_context.scope_id if access_context else None
    ctx = _capsule_brain.get_capsule_context(
        capsule["sub"],
        **({"scope_id": scope_id} if scope_id else {}),
    )
    public = {k: v for k, v in ctx.items() if not k.startswith("_") and k != "last_session_id"}
    return JSONResponse(content={"context": public})


def _onboarding_scope(request: Request, capsule_id: str, body: Optional[dict[str, Any]] = None) -> Optional[str]:
    access_context = _resolve_active_scope(request, capsule_id, body) if _hybrid_scopes_enabled() else None
    if access_context and access_context.scope_kind is not ScopeKind.PERSONAL:
        raise HTTPException(status_code=409, detail="Onboarding import targets HoloPersonal only.")
    return access_context.scope_id if access_context else None


def _read_onboarding_state(capsule_id: str, *, scope_id: Optional[str] = None) -> dict[str, Any]:
    context = _capsule_brain.get_capsule_context(
        capsule_id,
        **({"scope_id": scope_id} if scope_id else {}),
    )
    raw = str((context or {}).get("holo_onboarding_state_v1") or "").strip()
    try:
        state = json.loads(raw) if raw else {}
    except Exception:
        state = {}
    if not isinstance(state, dict):
        state = {}
    selected = state.get("selected_areas")
    return {
        "required": bool(state.get("required", False)),
        "completed": bool(state.get("completed", False)),
        "step": int(state.get("step") or 1) if str(state.get("step") or "1").isdigit() else 1,
        "selected_areas": selected if isinstance(selected, list) else [],
        "review_available": bool(state.get("review_available", True)),
        "review_required": bool(state.get("review_required", False)),
        "import_summary": state.get("import_summary") if isinstance(state.get("import_summary"), dict) else None,
    }


@app.get("/v1/capsule/onboarding")
async def get_capsule_onboarding(request: Request):
    """Return resumable first-run onboarding state for the authenticated capsule."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    scope_id = _onboarding_scope(request, capsule["sub"])
    return JSONResponse(content=_read_onboarding_state(capsule["sub"], scope_id=scope_id))


@app.post("/v1/capsule/onboarding")
async def save_capsule_onboarding(request: Request):
    """
    Save resumable onboarding progress and deterministically admit a pasted
    HoloBrain import packet into HoloPersonal.
    """
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON.")
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Request body must be an object.")

    scope_id = _onboarding_scope(request, capsule["sub"], body)
    scope_kwargs = {"scope_id": scope_id} if scope_id else {}
    state = _read_onboarding_state(capsule["sub"], scope_id=scope_id)

    selected_areas = body.get("selected_areas")
    if selected_areas is not None and not isinstance(selected_areas, list):
        raise HTTPException(status_code=400, detail="selected_areas must be a list.")
    if isinstance(selected_areas, list):
        state["selected_areas"] = [str(area).strip()[:40] for area in selected_areas if str(area).strip()][:12]

    try:
        state["step"] = min(4, max(1, int(body.get("step", state.get("step") or 1))))
    except (TypeError, ValueError):
        state["step"] = 1

    imported_context = str(body.get("imported_context") or "").strip()
    saved_keys: list[str] = []
    if imported_context:
        import_result = build_onboarding_context_writes(
            imported_context,
            selected_areas=state.get("selected_areas") or [],
        )
        for key, value in import_result.context_writes.items():
            _capsule_brain.set_capsule_context(capsule["sub"], str(key)[:50], str(value)[:5000], **scope_kwargs)
            saved_keys.append(str(key)[:50])
        state["import_summary"] = import_result.summary()
        state["review_available"] = import_result.review_available
        state["review_required"] = import_result.review_required

    if body.get("completed") is True:
        state["completed"] = True
        state["required"] = False
    elif body.get("required") is not None:
        state["required"] = bool(body.get("required"))

    _capsule_brain.set_capsule_context(
        capsule["sub"],
        "holo_onboarding_state_v1",
        json.dumps(state, ensure_ascii=True, separators=(",", ":"))[:5000],
        **scope_kwargs,
    )
    logger.info(
        "HoloChat onboarding saved",
        extra={
            "capsule": capsule["sub"][:8],
            "scope_id": scope_id,
            "step": state.get("step"),
            "completed": state.get("completed"),
            "saved_key_count": len(saved_keys),
        },
    )
    return JSONResponse(content={**state, "saved_keys": saved_keys})


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
    access_context = _resolve_active_scope(request, capsule["sub"], body)
    scope_id = access_context.scope_id if access_context else None
    scope_kwargs = {"scope_id": scope_id} if scope_id else {}
    for key, value in context.items():
        if key and isinstance(value, str):
            key_str = str(key)[:50]
            value_limit = 3000 if key_str in {"holo_seed_personal_v1", "holo_seed_deep_v1"} else 500
            _capsule_brain.set_capsule_context(
                capsule["sub"], key_str, str(value)[:value_limit], **scope_kwargs
            )
    logger.info(f"Capsule seeded for {capsule['sub'][:8]}: {list(context.keys())}")
    return JSONResponse(content={"seeded": list(context.keys())})


@app.delete("/v1/capsule/context/{key}")
async def delete_capsule_context(key: str, request: Request):
    """Delete one editable capsule memory entry."""
    capsule = get_capsule_from_request(request.headers.get("Authorization"))
    if not capsule:
        raise HTTPException(status_code=401, detail="Sign in required.")
    key = str(key or "").strip()[:50]
    if not key or key.startswith("_") or key == "last_session_id":
        raise HTTPException(status_code=400, detail="That memory entry cannot be deleted here.")
    access_context = _resolve_active_scope(request, capsule["sub"])
    scope_id = access_context.scope_id if access_context else None
    deleted = _capsule_brain.delete_capsule_context(
        capsule["sub"], key, **({"scope_id": scope_id} if scope_id else {})
    )
    return JSONResponse(content={"deleted": bool(deleted), "key": key})


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
