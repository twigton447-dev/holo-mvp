"""
auth_capsule.py

Capsule ID authentication for Holo.

Flow:
  1. Frontend signs user in with Google (GSI) → gets a Google credential JWT
  2. POST /auth/google with that credential
  3. We verify it with Google, get the user's identity (sub, email, name)
  4. Get-or-create their capsule in Supabase
  5. Return a signed Holo capsule token (JWT) the frontend stores
  6. Every subsequent request can include the capsule token to attach user context

Environment variables required:
  GOOGLE_CLIENT_ID   — from Google Cloud Console → APIs & Services → Credentials
  HOLO_JWT_SECRET    — any long random string (used to sign capsule tokens)
"""

import hashlib
import logging
import os
import secrets
import time
from typing import Optional

import bcrypt
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from project_brain import CapsuleIdentityConflict, CapsulePersistenceError, ProjectBrain

logger = logging.getLogger("holo.auth")

_brain = ProjectBrain()

_DEVELOPMENT_JWT_SECRET = "change-me-in-production"
HOLO_JWT_SECRET  = os.getenv("HOLO_JWT_SECRET", _DEVELOPMENT_JWT_SECRET)
CAPSULE_TOKEN_TTL = 60 * 60 * 24 * 30   # 30 days


def _email_google_id(email: str) -> str:
    """Return the stable synthetic google_id used for email auth."""
    return "email:" + hashlib.sha256(email.encode()).hexdigest()[:32]


def _email_auth_capsule_id(email: str) -> str:
    """Return the capsule id used for email password/reset state."""
    return _email_google_id(email.strip().lower())


def _ephemeral_capsules_allowed() -> bool:
    """Keep non-durable identities out of deployed HoloChat environments."""
    return str(os.getenv("HOLOCHAT_ALLOW_EPHEMERAL_AUTH", "")).strip().lower() in {
        "1", "true", "yes", "on",
    }


def _deployed_runtime() -> bool:
    """Return whether this process is serving a deployed HoloChat runtime."""
    return bool(
        os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("RAILWAY_PROJECT_ID")
        or os.getenv("HOLOCHAT_AUTH_STRICT_STARTUP")
    )


def _identity_maintenance_control_required() -> bool:
    return str(
        os.getenv("HOLOCHAT_IDENTITY_MAINTENANCE_REQUIRED", "")
    ).strip().lower() in {"1", "true", "yes", "on"}


def _email_password_capsule(email: str) -> Optional[dict]:
    """Resolve an email/password capsule without choosing an ambiguous row."""
    if not _brain._client:
        raise CapsulePersistenceError("capsule storage is unavailable")
    direct = _brain.get_capsule_by_google_id(_email_google_id(email))
    if direct:
        return direct
    lookup = getattr(_brain, "get_unique_capsule_by_email", None)
    return lookup(email) if callable(lookup) else None


def _assert_identity_signin_available() -> None:
    """Honor a short operator maintenance window around identity surgery."""
    checker = getattr(_brain, "assert_identity_signin_available", None)
    if not callable(checker):
        return
    try:
        checker()
    except CapsuleIdentityConflict as exc:
        raise ValueError(str(exc)) from exc
    except CapsulePersistenceError as exc:
        raise ValueError("account_persistence_unavailable") from exc


def auth_configuration_errors() -> list[str]:
    """Return unsafe authentication configuration without disclosing secrets.

    Email-to-capsule aliases once existed as a convenience during early account
    setup. They let one verified identity receive another capsule's token, so
    they are deliberately unsupported now. Durable account migrations must be
    explicit, audited, and bound to the verified Google subject instead.
    """
    errors: list[str] = []
    secret = str(HOLO_JWT_SECRET or "")
    if secret == _DEVELOPMENT_JWT_SECRET or len(secret.encode("utf-8")) < 32:
        errors.append("HOLO_JWT_SECRET must be a unique value of at least 32 bytes")
    if os.getenv("HOLOCHAT_ACCOUNT_ALIASES", "").strip():
        errors.append("HOLOCHAT_ACCOUNT_ALIASES is unsupported and must be removed")
    if _ephemeral_capsules_allowed():
        errors.append("HOLOCHAT_ALLOW_EPHEMERAL_AUTH must be disabled in deployed environments")
    if _deployed_runtime() and not _identity_maintenance_control_required():
        errors.append(
            "HOLOCHAT_IDENTITY_MAINTENANCE_REQUIRED must be enabled in deployed environments"
        )
    return errors


# ---------------------------------------------------------------------------
# Google token verification
# ---------------------------------------------------------------------------

def verify_google_token(credential: str) -> Optional[dict]:
    """
    Verify a Google Identity Services credential JWT.
    Returns the decoded user info dict, or None on failure.
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        logger.error("GOOGLE_CLIENT_ID not set — cannot verify Google tokens.")
        return None
    try:
        info = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            client_id,
        )
        return info
    except Exception as e:
        logger.warning(f"Google token verification failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Capsule token (Holo's own JWT)
# ---------------------------------------------------------------------------

def issue_capsule_token(capsule_id: str, email: str, mode: str) -> str:
    """Sign and return a Holo capsule JWT."""
    payload = {
        "sub":        capsule_id,
        "email":      email,
        "mode":       mode,
        "iat":        int(time.time()),
        "exp":        int(time.time()) + CAPSULE_TOKEN_TTL,
    }
    return jwt.encode(payload, HOLO_JWT_SECRET, algorithm="HS256")


def decode_capsule_token(token: str) -> Optional[dict]:
    """
    Decode and verify a Holo capsule JWT.
    Returns payload dict or None if invalid/expired.
    """
    try:
        return jwt.decode(token, HOLO_JWT_SECRET, algorithms=["HS256"])
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Sign-in handler
# ---------------------------------------------------------------------------

def handle_google_signin(credential: str) -> Optional[dict]:
    """
    Full sign-in flow:
      1. Verify Google credential
      2. Get-or-create capsule in Supabase
      3. Issue a Holo capsule token

    Returns dict with token + capsule info, or None on failure.
    """
    user_info = verify_google_token(credential)
    if not user_info:
        return None

    google_id  = user_info.get("sub", "")
    email      = user_info.get("email", "")
    name       = user_info.get("name", "")
    avatar_url = user_info.get("picture", "")

    _assert_identity_signin_available()

    try:
        capsule = _brain.get_or_create_capsule(google_id, email, name, avatar_url)
    except CapsuleIdentityConflict as e:
        raise ValueError(str(e)) from e
    except CapsulePersistenceError as e:
        if not _ephemeral_capsules_allowed():
            raise ValueError("account_persistence_unavailable") from e
        capsule = None
    except ValueError as e:
        if "account_cap_reached" in str(e):
            raise
        raise
    if not capsule:
        if not _ephemeral_capsules_allowed():
            raise ValueError("account_persistence_unavailable")
        # No Supabase — create an ephemeral capsule for this session
        import uuid
        capsule = {
            "capsule_id": str(uuid.uuid4()),
            "email":      email,
            "name":       name,
            "avatar_url": avatar_url,
            "mode":       "personal",
        }
        logger.warning("Capsule created without Supabase persistence.")

    # Check a second time immediately before minting a browser token. A
    # reconciliation can begin while Google verification or the account lookup
    # is in flight; a source token issued after that point must never become a
    # usable side channel.
    _assert_identity_signin_available()
    token = issue_capsule_token(capsule["capsule_id"], email, capsule.get("mode", "personal"))

    return {
        "capsule_token": token,
        "capsule_id":    capsule["capsule_id"],
        "email":         email,
        "name":          name,
        "avatar_url":    avatar_url,
        "mode":          capsule.get("mode", "personal"),
    }


def _valid_invite_code(code: str) -> bool:
    """Check code against INVITE_CODES env var (comma-separated). Empty = open signup."""
    raw = os.getenv("INVITE_CODES", "").strip()
    if not raw:
        return True  # no gate set — open
    valid = {c.strip().lower() for c in raw.split(",") if c.strip()}
    return code.strip().lower() in valid


def handle_email_signin(email: str, name: str, password: str,
                        invite_code: str = "") -> Optional[dict]:
    """
    Email + password sign-in.
    - New users must supply a valid invite code.
    - Returning users only need email + password.
    Returns None on wrong password. Raises ValueError on bad invite code.
    """
    email    = email.strip().lower()
    name     = name.strip() or email.split("@")[0]
    password = password.strip()

    if not password:
        logger.warning("Email sign-in attempted with no password.")
        return None

    _assert_identity_signin_available()

    try:
        existing_capsule = _email_password_capsule(email)
    except CapsuleIdentityConflict as e:
        raise ValueError(str(e)) from e
    except CapsulePersistenceError as e:
        raise ValueError("account_persistence_unavailable") from e

    if existing_capsule:
        real_id = existing_capsule["capsule_id"]
        ctx = _brain.get_capsule_context(real_id)
        stored_hash = ctx.get("_password_hash")

        if stored_hash:
            # Returning user — verify password
            if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
                logger.warning(f"Password mismatch for {email}")
                return None
            capsule = existing_capsule
        else:
            # A Google-only identity cannot be claimed by merely entering its
            # mailbox address. It must be linked while already authenticated.
            raise ValueError("account_link_required")
    else:
        # Brand new user — require invite code
        if not _valid_invite_code(invite_code):
            logger.warning(f"Invalid invite code '{invite_code}' for {email}")
            raise ValueError("invalid_invite_code")
        try:
            capsule = _brain.get_or_create_capsule(_email_google_id(email), email, name, "")
        except CapsuleIdentityConflict as e:
            raise ValueError(str(e)) from e
        except CapsulePersistenceError as e:
            raise ValueError("account_persistence_unavailable") from e
        if capsule:
            _assert_identity_signin_available()
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            _brain.set_capsule_context(capsule["capsule_id"], "_password_hash", hashed)
    if not capsule:
        if not _ephemeral_capsules_allowed():
            raise ValueError("account_persistence_unavailable")
        import uuid
        capsule = {
            "capsule_id": str(uuid.uuid4()),
            "email":      email,
            "name":       name,
            "avatar_url": "",
            "mode":       "personal",
        }
        logger.warning("Email capsule created without Supabase persistence.")

    _assert_identity_signin_available()
    token = issue_capsule_token(capsule["capsule_id"], email, capsule.get("mode", "personal"))

    return {
        "capsule_token": token,
        "capsule_id":    capsule["capsule_id"],
        "email":         email,
        "name":          name,
        "avatar_url":    "",
        "mode":          capsule.get("mode", "personal"),
    }


RESET_TOKEN_TTL = 60 * 30  # 30 minutes


def request_password_reset(email: str, base_url: str) -> bool:
    """
    Generate a reset token, store it, and send an email.
    Returns True if email was sent, False if account not found or email failed.
    """
    email = email.strip().lower()

    # Only allow reset for existing email-auth accounts
    if not _brain._client:
        return False
    try:
        _assert_identity_signin_available()
    except ValueError:
        # Preserve the endpoint's anti-enumeration behavior during a brief
        # maintenance window and do not write reset state.
        return True
    try:
        capsule = _email_password_capsule(email)
    except (CapsuleIdentityConflict, CapsulePersistenceError):
        return True
    if not capsule:
        return True
    capsule_id = str(capsule["capsule_id"])
    ctx = _brain.get_capsule_context(capsule_id)
    if not ctx.get("_password_hash"):
        # Don't reveal whether the account exists — just return True silently
        logger.info(f"Password reset requested for unknown email: {email}")
        return True

    token   = secrets.token_urlsafe(32)
    expiry  = int(time.time()) + RESET_TOKEN_TTL
    _brain.set_capsule_context(capsule_id, "_reset_token",  token)
    _brain.set_capsule_context(capsule_id, "_reset_expiry", str(expiry))

    reset_url = f"{base_url.rstrip('/')}/chat?reset={token}&email={email}"

    resend_key = os.getenv("RESEND_API_KEY")
    if not resend_key:
        logger.warning("RESEND_API_KEY not set — reset link: " + reset_url)
        return True  # still return True so we don't block development

    try:
        import resend
        resend.api_key = resend_key
        resend.Emails.send({
            "from":    "Holo <noreply@hologroup.io>",
            "to":      [email],
            "subject": "Reset your Holo password",
            "html":    f"""
<div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:40px 24px;color:#1a1a1a;">
  <h2 style="font-size:22px;font-weight:700;margin:0 0 12px;">Reset your password</h2>
  <p style="color:#555;line-height:1.6;margin:0 0 28px;">Click the link below to set a new password. It expires in 30 minutes.</p>
  <a href="{reset_url}" style="display:inline-block;background:#1a56e8;color:#fff;text-decoration:none;padding:12px 24px;border-radius:8px;font-weight:600;font-size:15px;">Reset password</a>
  <p style="color:#aaa;font-size:12px;margin-top:32px;">If you didn't request this, ignore this email.</p>
</div>""",
        })
        logger.info(f"Password reset email sent to {email}")
    except Exception as e:
        logger.warning(f"Failed to send reset email: {e}")
        return False

    return True


def reset_password(email: str, token: str, new_password: str) -> bool:
    """
    Verify the reset token and update the password.
    Returns True on success, False on invalid/expired token.
    """
    email        = email.strip().lower()
    new_password = new_password.strip()
    if not new_password or len(new_password) < 8:
        return False

    try:
        _assert_identity_signin_available()
    except ValueError:
        return False

    try:
        capsule = _email_password_capsule(email)
    except (CapsuleIdentityConflict, CapsulePersistenceError):
        return False
    if not capsule:
        return False
    capsule_id = str(capsule["capsule_id"])
    ctx = _brain.get_capsule_context(capsule_id)

    stored_token  = ctx.get("_reset_token", "")
    stored_expiry = int(ctx.get("_reset_expiry", "0"))

    if not stored_token or stored_token != token:
        logger.warning(f"Invalid reset token for {email}")
        return False
    if time.time() > stored_expiry:
        logger.warning(f"Expired reset token for {email}")
        return False

    # Token valid — update password and clear token
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    _brain.set_capsule_context(capsule_id, "_password_hash", hashed)
    _brain.set_capsule_context(capsule_id, "_reset_token",   "")
    _brain.set_capsule_context(capsule_id, "_reset_expiry",  "0")
    logger.info(f"Password reset successful for {email}")
    return True


def get_capsule_from_request(auth_header: Optional[str]) -> Optional[dict]:
    """
    Extract and decode the capsule token from an Authorization header.
    Returns decoded payload or None.
    """
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header[len("Bearer "):]
    payload = decode_capsule_token(token)
    if not payload:
        return None

    # Capsule JWTs are deliberately not a permanent authorization grant. A
    # durable identity can be merged, disabled, or revoked after issuance, so
    # resolve the subject again before allowing it to touch any HoloBrain data.
    # Local ephemeral auth is opt-in only and never permitted in deployment.
    if not getattr(_brain, "_client", None):
        return payload if _ephemeral_capsules_allowed() else None
    try:
        maintenance = getattr(_brain, "identity_maintenance_active", None)
        if callable(maintenance) and maintenance():
            return None
        # A durable runtime must be able to prove that the capsule remains
        # active. Falling back to ``get_capsule`` would let an older adapter
        # revive an archived/merged account from a stale browser token.
        lookup = getattr(_brain, "get_active_capsule", None)
        if not callable(lookup):
            logger.error("Durable HoloChat auth cannot verify capsule activity.")
            return None
        capsule = lookup(payload.get("sub"))
    except (CapsuleIdentityConflict, CapsulePersistenceError):
        return None
    if not capsule:
        return None
    token_email = str(payload.get("email") or "").strip().lower()
    durable_email = str(capsule.get("email") or "").strip().lower()
    if token_email and durable_email and token_email != durable_email:
        return None
    return payload
