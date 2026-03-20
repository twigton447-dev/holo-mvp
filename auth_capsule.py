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

from project_brain import ProjectBrain

logger = logging.getLogger("holo.auth")

_brain = ProjectBrain()

HOLO_JWT_SECRET  = os.getenv("HOLO_JWT_SECRET", "change-me-in-production")
CAPSULE_TOKEN_TTL = 60 * 60 * 24 * 30   # 30 days


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

    capsule = _brain.get_or_create_capsule(google_id, email, name, avatar_url)
    if not capsule:
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

    synthetic_id = "email:" + hashlib.sha256(email.encode()).hexdigest()[:32]

    # Check if capsule already exists
    existing_ctx = _brain.get_capsule_context(synthetic_id) if _brain._client else {}
    stored_hash  = existing_ctx.get("_password_hash")

    if stored_hash:
        # Returning user — verify password only
        if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
            logger.warning(f"Password mismatch for {email}")
            return None
    else:
        # New user — check invite code first
        if not _valid_invite_code(invite_code):
            logger.warning(f"Invalid invite code '{invite_code}' for {email}")
            raise ValueError("invalid_invite_code")
        # Hash and store password
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        _brain.set_capsule_context(synthetic_id, "_password_hash", hashed)

    capsule = _brain.get_or_create_capsule(synthetic_id, email, name, "")
    if not capsule:
        import uuid
        capsule = {
            "capsule_id": str(uuid.uuid4()),
            "email":      email,
            "name":       name,
            "avatar_url": "",
            "mode":       "personal",
        }
        logger.warning("Email capsule created without Supabase persistence.")

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
    synthetic_id = "email:" + hashlib.sha256(email.encode()).hexdigest()[:32]

    # Only allow reset for existing email-auth accounts
    if not _brain._client:
        return False
    ctx = _brain.get_capsule_context(synthetic_id)
    if not ctx.get("_password_hash"):
        # Don't reveal whether the account exists — just return True silently
        logger.info(f"Password reset requested for unknown email: {email}")
        return True

    token   = secrets.token_urlsafe(32)
    expiry  = int(time.time()) + RESET_TOKEN_TTL
    _brain.set_capsule_context(synthetic_id, "_reset_token",  token)
    _brain.set_capsule_context(synthetic_id, "_reset_expiry", str(expiry))

    reset_url = f"{base_url.rstrip('/')}/chat?reset={token}&email={email}"

    resend_key = os.getenv("RESEND_API_KEY")
    if not resend_key:
        logger.warning("RESEND_API_KEY not set — reset link: " + reset_url)
        return True  # still return True so we don't block development

    try:
        import resend
        resend.api_key = resend_key
        resend.Emails.send({
            "from":    "Holo <noreply@hololgroup.io>",
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

    synthetic_id = "email:" + hashlib.sha256(email.encode()).hexdigest()[:32]
    ctx = _brain.get_capsule_context(synthetic_id)

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
    _brain.set_capsule_context(synthetic_id, "_password_hash", hashed)
    _brain.set_capsule_context(synthetic_id, "_reset_token",   "")
    _brain.set_capsule_context(synthetic_id, "_reset_expiry",  "0")
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
    return decode_capsule_token(token)
