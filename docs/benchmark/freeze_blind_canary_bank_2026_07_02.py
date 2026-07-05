"""Freeze the first-turn correctness bank used by the blind canary sampler."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from blind_lane_suite.canary_skew import bank_stats, first_turn_correctness


OUT = Path("docs/benchmark/holoverify_blind_canary_bank_2026_07_02.json")


def bank_hash(rows: list[dict]) -> str:
    payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    ft = first_turn_correctness()
    rows = [
        {"legacy_packet_id": pid, "first_turn_correct": bool(value)}
        for pid, value in sorted(ft.items())
    ]
    payload = {
        "classification": "HOLOVERIFY_BLIND_CANARY_FROZEN_FIRST_TURN_BANK_NO_PROVIDER",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider_calls": 0,
        "judge_calls": 0,
        "bank_stats": bank_stats(ft),
        "bank_hash": bank_hash(rows),
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(OUT)
    print(payload["bank_hash"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
