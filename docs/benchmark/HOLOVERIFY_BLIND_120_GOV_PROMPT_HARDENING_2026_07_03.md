# HoloVerify Blind 120 Gov Prompt Hardening

Status: `NO_PROVIDER_PATCH`

Date: 2026-07-03

## Trigger

Batch 1 failed closed in:

`docs/benchmark/holoverify_blind_120_live_runs_2026_07_03/run_20260703T024113Z`

The failure occurred at call `014_G2` when MiniMax returned prose refusing the Gov prompt as prompt injection instead of returning the required baton fields.

## Root Cause

The Gov prompt used operational framing that MiniMax sometimes interpreted as suspicious:

- `HoloVerify blind Gov actuator`
- `COPY MODE`
- `RUN LOCK`
- `role=GOV`
- `copy exactly`
- hidden-thinking/no-reasoning language

The runner correctly failed closed, but the prompt framing was brittle for MiniMax.

## Patch

The Gov prompt is now neutral status-record formatting:

- System prompt: plain data formatting task
- User prompt: `status_values`
- Required visible fields remain unchanged:
  - `route_verdict`
  - `repair_target`
  - `blocked_move`

The parser and fail-closed behavior are unchanged. Malformed, missing, prose, or refusal output still invalidates the run. No content retry was added.

## Scope

Changed:

- `holoverify_blind_runner_v0.py`
- `docs/benchmark/run_holoverify_blind_canary_live_2026_07_02.py`
- `tests/test_holoverify_blind_canary_live_wrapper.py`
- `tests/test_blind_lane_t5_canary_skew.py`

Not changed:

- Frozen runtime bank
- Runtime manifest hash
- Scoring map
- Provider roster
- Batch approval requirements
- Solo/judge/scoring locks
- Transport retry policy

## Validation Boundary

This patch is no-provider only. It does not produce benchmark evidence. It only makes the next live batch less likely to fail for MiniMax prompt-framing refusal while preserving strict contract failure behavior.

## No-Provider Validation

- JSON report parse: PASS
- Python compile: PASS
- Targeted pytest: `41 passed, 1 skipped`
- Batch 1 no-provider preflight: PASS
- Generated Gov prompt contains `status_values:` and `route_verdict=CONTINUE`
- Generated Gov prompt does not contain:
  - `Gov actuator`
  - `HoloGov`
  - `COPY MODE`
  - `copy exactly`
  - `RUN LOCK`
  - `role=GOV`
  - `hidden thinking`
