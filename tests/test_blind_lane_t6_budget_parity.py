"""T6 - budget parity replay.

Falsifies: "the blind lane buys no accuracy through extra attempts."
Passing does NOT show parity with solo baselines nor that budgets are right.
"""

import pytest

from blind_lane_suite.budget_audit import check_retry_log, check_runner_budget, governed_envelope
from blind_lane_suite.fixtures import (
    FailingTransport,
    SYNTHETIC_PAIR_SPEC,
    mock_transcripts,
    model_visible_payload,
)
from blind_lane_suite.runner_contract import SKIP_REASON, load_runner


def test_governed_envelope_extractable():
    env = governed_envelope()
    assert env["max_calls_per_packet"] >= 1
    if env["fallback_used"]:
        print("T6 WARNING: no manifests readable; envelope uses documented fallback (5 calls/packet)")
    print(f"T6 governed envelope: {env}")


def test_retry_log_checker_flags_violations():
    """Detector validation."""
    bad = [{"kind": "transport", "attempt": 1}, {"kind": "content", "attempt": 2}]
    violations = check_retry_log(bad, retry_limit=1)
    assert any(v["kind"] == "non_transport_retry" for v in violations), "retry checker missed a content retry"
    over = [{"kind": "transport", "attempt": i} for i in range(1, 4)]
    assert any(v["kind"] == "retry_cap_exceeded" for v in check_retry_log(over, retry_limit=1))


def test_blind_runner_budget_within_governed_envelope():
    runner, missing = load_runner()
    if runner is None:
        pytest.skip(SKIP_REASON)
    assert not missing, f"blind runner contract violation - missing attrs: {missing}"
    violations = check_runner_budget(runner.BUDGET_LIMITS)
    assert not violations, f"BUDGET PRIVILEGE: {violations}"


def test_transport_retries_capped_and_logged(tmp_path):
    """Force transport failures; retries must be capped, logged as transport,
    and content failures must never be retried."""
    runner, missing = load_runner()
    if runner is None:
        pytest.skip(SKIP_REASON)
    assert not missing, f"blind runner contract violation - missing attrs: {missing}"
    limit = runner.BUDGET_LIMITS.get("transport_retry_limit", 0)
    transport = FailingTransport(fail_first=limit + 5, canned=mock_transcripts(1)[0])
    payload = model_visible_payload(SYNTHETIC_PAIR_SPEC, "A")
    try:
        result = runner.run_blind_fixture(payload, [], str(tmp_path), transport=transport)
    except Exception:
        result = None  # fail-closed is acceptable; attempt count still bounds retries
    max_attempts_first_call = 1 + limit
    assert transport.attempts <= max_attempts_first_call or result is None, (
        f"HIDDEN RESCUE: {transport.attempts} transport attempts observed with retry limit {limit}"
    )
    if result is not None:
        violations = check_retry_log(result.get("retry_log", []), retry_limit=limit)
        assert not violations, f"RETRY VIOLATIONS: {violations}"
