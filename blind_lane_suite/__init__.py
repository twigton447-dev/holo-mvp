"""Blind-lane disconfirmation suite (T1-T7).

No-provider, no-judge test tooling per
docs/benchmark/FABLE_BLIND_LANE_DISCONFIRMATION_BATTERY_2026_07_02.md.

Reads frozen evidence strictly read-only. Never mutates packets, truths,
prompts, traces, or lock manifests. All fixture output goes to temp dirs.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "docs" / "benchmark"
FRONTEND = ROOT / "frontend"

# Contract: a candidate blind runner registers itself via this env var
# (module path importable from repo root). Absent => contract tests SKIP
# loudly; a skip is NOT a pass and must never be reported as one.
BLIND_RUNNER_ENV = "BLIND_RUNNER_MODULE"

# Canary scale ceiling for claim-scope lint (T7).
CANARY_MAX_DENOMINATOR = 40
