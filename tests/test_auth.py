"""
Unit tests for auth.py — RateLimiter.
"""
import time
import pytest
from auth import RateLimiter


class TestRateLimiter:

    def test_first_request_allowed(self):
        rl = RateLimiter()
        assert rl.check("key1", max_rpm=10) is True

    def test_requests_within_limit_all_allowed(self):
        rl = RateLimiter()
        for _ in range(5):
            assert rl.check("key1", max_rpm=10) is True

    def test_request_at_limit_blocked(self):
        rl = RateLimiter()
        for _ in range(5):
            rl.check("key1", max_rpm=5)
        # 6th request should be blocked
        assert rl.check("key1", max_rpm=5) is False

    def test_different_keys_independent(self):
        rl = RateLimiter()
        for _ in range(5):
            rl.check("key1", max_rpm=5)
        # key2 is completely unaffected
        assert rl.check("key2", max_rpm=5) is True

    def test_max_rpm_one_allows_exactly_one(self):
        rl = RateLimiter()
        assert rl.check("key1", max_rpm=1) is True
        assert rl.check("key1", max_rpm=1) is False

    def test_window_expiry_allows_new_requests(self):
        """
        Timestamps older than 60s should be pruned, freeing up the window.
        We inject old timestamps directly.
        """
        rl = RateLimiter()
        old_ts = time.time() - 61  # outside the 60-second window
        rl._requests["key1"] = [old_ts] * 5  # fill window with expired entries
        # All 5 slots are expired — next request should be allowed
        assert rl.check("key1", max_rpm=5) is True

    def test_mixed_fresh_and_stale_timestamps(self):
        rl = RateLimiter()
        now = time.time()
        rl._requests["key1"] = [now - 61, now - 59, now - 1]  # 1 stale, 2 fresh
        # max_rpm=3: 2 fresh + this call = 3, allowed
        assert rl.check("key1", max_rpm=3) is True
        # Now 3 fresh entries, next blocked
        assert rl.check("key1", max_rpm=3) is False

    def test_thread_safety_lock_exists(self):
        """RateLimiter must have a _lock attribute (thread safety requirement)."""
        rl = RateLimiter()
        assert hasattr(rl, "_lock")
        import threading
        assert isinstance(rl._lock, type(threading.Lock()))
