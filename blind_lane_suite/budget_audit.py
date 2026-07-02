"""T6 - budget parity audit.

Falsifies: "the blind lane buys no accuracy through extra attempts."

governed_envelope() extracts per-packet call budgets from frozen manifests
(read-only). Contract tests then require the registered blind runner's
BUDGET_LIMITS to stay within the envelope, and the forced-failure fixture to
show capped, logged, transport-only retries.

Passing does NOT show parity with solo baselines, nor that budgets are right -
only that the blind lane is not privileged relative to the governed lane.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import BENCH

# Fallback from the governed architecture (5 calls per packet: W1 G1 W2 G2 W3),
# used only when no manifest is readable; flagged in the report.
FALLBACK_CALLS_PER_PACKET = 5
FALLBACK_WORKER_TURNS = 3
GOVERNED_TRANSPORT_RETRY_LIMIT = 1  # per HOLOVERIFY_TRANSPORT_RETRY_POLICY_V1
GOVERNED_MAX_OUTPUT_TOKENS = 1024


def governed_envelope() -> dict:
    calls_per_packet: list[float] = []
    sources: list[str] = []
    for pattern in ("*PREFLIGHT*.json", "*REGISTRATION*.json"):
        for path in sorted(BENCH.rglob(pattern))[:200]:
            try:
                data = json.loads(path.read_text(errors="replace"))
            except Exception:
                continue
            for holder in (data, data.get("architecture_lock") or {}):
                counts = holder.get("expected_counts") if isinstance(holder, dict) else None
                if isinstance(counts, dict):
                    packets = counts.get("packets")
                    total = counts.get("total_provider_calls")
                    if isinstance(packets, int) and packets and isinstance(total, int):
                        calls_per_packet.append(total / packets)
                        sources.append(str(path))
                        break
    if calls_per_packet:
        max_cpp = max(calls_per_packet)
        fallback = False
    else:
        max_cpp = FALLBACK_CALLS_PER_PACKET
        fallback = True
    return {
        "max_calls_per_packet": max_cpp,
        "max_worker_turns_per_packet": FALLBACK_WORKER_TURNS,
        "transport_retry_limit": GOVERNED_TRANSPORT_RETRY_LIMIT,
        "max_output_tokens": GOVERNED_MAX_OUTPUT_TOKENS,
        "manifests_sampled": len(sources),
        "fallback_used": fallback,
    }


def check_runner_budget(budget_limits: dict, envelope: dict | None = None) -> list[dict]:
    env = envelope or governed_envelope()
    violations = []
    checks = (
        ("max_calls_per_packet", env["max_calls_per_packet"]),
        ("max_worker_turns_per_packet", env["max_worker_turns_per_packet"]),
        ("transport_retry_limit", env["transport_retry_limit"]),
        ("max_output_tokens", env["max_output_tokens"]),
    )
    for key, ceiling in checks:
        got = budget_limits.get(key)
        if got is None:
            violations.append({"kind": "budget_key_missing", "key": key})
        elif got > ceiling:
            violations.append({"kind": "budget_exceeds_governed_envelope", "key": key, "got": got, "ceiling": ceiling})
    return violations


def check_retry_log(retry_log: list[dict], retry_limit: int) -> list[dict]:
    violations = []
    transport = [r for r in retry_log if r.get("kind") == "transport"]
    other = [r for r in retry_log if r.get("kind") != "transport"]
    if other:
        violations.append({"kind": "non_transport_retry", "entries": other[:5]})
    if len(transport) > retry_limit:
        violations.append({"kind": "retry_cap_exceeded", "retries": len(transport), "limit": retry_limit})
    return violations
