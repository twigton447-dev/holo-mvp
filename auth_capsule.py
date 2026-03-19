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

import logging
import os
import time
from typing import Optional

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


def handle_email_signin(email: str, name: str) -> Optional[dict]:
    """
    Simple email-based sign-in — no Google OAuth required.
    Creates or loads a capsule keyed by email, issues a Holo capsule token.
    """
    email = email.strip().lower()
    name  = name.strip() or email.split("@")[0]

    # Use a stable synthetic ID so the same email always maps to the same capsule
    import hashlib
    synthetic_id = "email:" + hashlib.sha256(email.encode()).hexdigest()[:32]

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


def get_capsule_from_request(auth_header: Optional[str]) -> Optional[dict]:
    """
    Extract and decode the capsule token from an Authorization header.
    Returns decoded payload or None.
    """
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header[len("Bearer "):]
    return decode_capsule_token(token)
