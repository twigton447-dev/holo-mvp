"""Holo V1 MVP -- API Key Auth & Rate Limiting.

Validates x-api-key header against Supabase.
In-memory per-key rate limiter (resets on server restart).
"""

from __future__ import annotations

import threading
import time
import logging
from collections import defaultdict

from fastapi import Request, HTTPException

logger = logging.getLogger("holo.auth")


class RateLimiter:
    """In-memory sliding-window rate limiter. Resets on server restart."""

    def __init__(self):
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def check(self, key_id: str, max_rpm: int) -> bool:
        """Return True if the request is allowed, False if rate-limited."""
        now = time.time()
        window_start = now - 60

        with self._lock:
            # Prune old timestamps
            self._requests[key_id] = [
                ts for ts in self._requests[key_id] if ts > window_start
            ]

            if len(self._requests[key_id]) >= max_rpm:
                return False

            self._requests[key_id].append(now)
            return True


# Module-level singleton
_rate_limiter = RateLimiter()


def authenticate_request(request: Request, db) -> dict:
    """Validate x-api-key header. Returns the key record or raises 401/429."""

    api_key = request.headers.get("x-api-key")
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing x-api-key header")

    key_record = db.validate_api_key(api_key)
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Rate limit check
    max_rpm = key_record.get("max_requests_per_minute", 10)
    if not _rate_limiter.check(key_record["id"], max_rpm):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded ({max_rpm} requests/minute)",
        )

    return key_record
