"""
provider_health.py

Provider resilience infrastructure for Holo:
  - ProviderUnavailableError / SystemUnavailableError
  - call_with_retry: exponential backoff + jitter, max 3 attempts
  - QuarantineRegistry: in-memory 300s quarantine with auto-restore
  - HealthMonitor: per-run health tracking → run_health annotation
"""

import logging
import random
import time
from datetime import datetime, timezone

logger = logging.getLogger("holo.health")

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ProviderUnavailableError(Exception):
    """Raised when a provider exhausts all retries."""
    def __init__(self, provider, last_error_code, last_error_message, attempts):
        self.provider           = provider
        self.last_error_code    = last_error_code
        self.last_error_message = last_error_message
        self.attempts           = attempts
        super().__init__(
            f"{provider} unavailable after {attempts} attempts "
            f"(code={last_error_code}): {last_error_message}"
        )


class SystemUnavailableError(Exception):
    """Raised when zero healthy providers remain."""
    pass


# ---------------------------------------------------------------------------
# Structured logging
# ---------------------------------------------------------------------------

def _structured_log(provider, error_code, error_message, attempt_number,
                    action, session_id="unknown"):
    logger.warning(
        f"[{action}] provider={provider} code={error_code} "
        f"attempt={attempt_number} session={session_id} | {error_message}"
    )


# ---------------------------------------------------------------------------
# Transient error detection
# ---------------------------------------------------------------------------

_TRANSIENT_CODES   = {"503", "429", "500", "502", "504"}
_TRANSIENT_STRINGS = ("UNAVAILABLE", "overloaded", "rate", "timeout",
                      "DEADLINE_EXCEEDED", "RESOURCE_EXHAUSTED")

def _is_transient(exc) -> bool:
    err_str = str(exc)
    for code in _TRANSIENT_CODES:
        if code in err_str:
            return True
    for phrase in _TRANSIENT_STRINGS:
        if phrase.lower() in err_str.lower():
            return True
    # Check for timeout exception types by name
    type_name = type(exc).__name__.lower()
    return "timeout" in type_name or "deadline" in type_name


def _extract_error_code(exc) -> str:
    err_str = str(exc)
    for code in _TRANSIENT_CODES:
        if code in err_str:
            return code
    if hasattr(exc, "status_code"):
        return str(exc.status_code)
    if hasattr(exc, "code"):
        return str(exc.code)
    return type(exc).__name__


# ---------------------------------------------------------------------------
# Retry wrapper
# ---------------------------------------------------------------------------

def call_with_retry(call_fn, provider, session_id="unknown", max_attempts=3):
    """
    Call call_fn() with exponential backoff on transient errors.

    Backoff: 1s, 2s, 4s + uniform(0, 0.5) jitter.
    Non-transient errors are re-raised immediately.
    On exhaustion: raises ProviderUnavailableError.
    """
    last_exc = None
    last_code = "unknown"
    last_msg  = ""

    for attempt in range(1, max_attempts + 1):
        try:
            return call_fn()
        except Exception as e:
            last_exc  = e
            last_code = _extract_error_code(e)
            last_msg  = str(e)

            if not _is_transient(e):
                raise  # auth errors, parse errors, etc. — don't retry

            wait = (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            _structured_log(provider, last_code, last_msg, attempt,
                            "RETRY", session_id)

            if attempt < max_attempts:
                time.sleep(wait)

    # All attempts exhausted
    _structured_log(provider, last_code, last_msg, max_attempts,
                    "EXHAUSTED", session_id)
    raise ProviderUnavailableError(provider, last_code, last_msg, max_attempts)


# ---------------------------------------------------------------------------
# Quarantine registry
# ---------------------------------------------------------------------------

QUARANTINE_DURATION = 300  # seconds


class QuarantineRegistry:
    """In-memory provider quarantine. Not persistent across restarts."""

    def __init__(self):
        self._quarantined: dict[str, float] = {}  # provider -> expiry timestamp

    def quarantine(self, provider: str, session_id: str = "unknown",
                   duration: int = QUARANTINE_DURATION):
        expiry = time.time() + duration
        self._quarantined[provider] = expiry
        _structured_log(provider, "N/A",
                        f"Quarantined for {duration}s", 0,
                        "QUARANTINE", session_id)
        logger.warning(
            f"[QUARANTINE] {provider} removed from active rotation for {duration}s"
        )

    def is_quarantined(self, provider: str) -> bool:
        expiry = self._quarantined.get(provider)
        if expiry is None:
            return False
        return time.time() < expiry

    def restore_if_expired(self, provider: str, session_id: str = "unknown"):
        expiry = self._quarantined.get(provider)
        if expiry is not None and time.time() >= expiry:
            del self._quarantined[provider]
            _structured_log(provider, "N/A",
                            "Quarantine expired — restored to active pool", 0,
                            "RESTORED", session_id)
            logger.info(f"[RESTORED] {provider} returned to active rotation pool")

    def healthy_providers(self, all_providers: list) -> list:
        for p in all_providers:
            self.restore_if_expired(p)
        return [p for p in all_providers if not self.is_quarantined(p)]


# Module-level singleton
registry = QuarantineRegistry()


# ---------------------------------------------------------------------------
# Health monitor
# ---------------------------------------------------------------------------

class HealthMonitor:
    """Tracks per-run provider health and produces the run_health annotation."""

    def __init__(self, total_providers: int):
        self.total_providers  = total_providers
        self.degraded_turns: list[int] = []

    def check_and_classify(self, healthy_count: int, session_id: str,
                           turn_number: int) -> str:
        """
        Returns "clean" or "degraded".
        Raises SystemUnavailableError when healthy_count == 0.
        """
        if healthy_count == 0:
            raise SystemUnavailableError(
                "All providers are quarantined. Cannot continue evaluation."
            )
        if healthy_count < self.total_providers:
            self.degraded_turns.append(turn_number)
            _structured_log("pool", f"{healthy_count}/{self.total_providers}",
                            f"Running in degraded mode: {healthy_count} of "
                            f"{self.total_providers} providers healthy",
                            0, "DEGRADED_MODE", session_id)
            logger.warning(
                f"[DEGRADED MODE] {healthy_count}/{self.total_providers} providers "
                f"healthy — continuing with reduced pool"
            )
            return "degraded"
        return "clean"

    @property
    def run_health(self) -> str:
        if not self.degraded_turns:
            return "clean"
        return "contaminated"
