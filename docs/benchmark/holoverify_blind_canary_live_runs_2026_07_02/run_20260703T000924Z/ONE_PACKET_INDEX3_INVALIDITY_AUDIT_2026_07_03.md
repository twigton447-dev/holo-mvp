# One-Packet Blind Canary Invalidity Audit

Status: `INVALID_ONE_PACKET_CONTENT_FAILURE_G2_EMPTY_TEXT_AFTER_LENGTH`

Run folder:

`docs/benchmark/holoverify_blind_canary_live_runs_2026_07_02/run_20260703T000924Z`

## Scope

- Packet scope: one opaque runtime packet only
- Packet index: `3`
- Expected provider calls: `5`
- Observed provider calls: `4`
- Solo calls: `0`
- Judge calls: `0`
- Source runtime manifest hash: `b80861ab6e407f98d69a7dd268ee102648b0455c19a1823ad0504fb321768bd7`
- Runtime subset hash: `10af8671093b77ed50338c13c1ed5904e07f37f31aa6eb36e74c42ac7d848b0b`

## Result

The run is invalid and incomplete. It is not a HoloVerify verdict failure, not a score-valid result, and not a public benchmark result.

The run failed closed at the fourth provider call:

- Call: `4`
- Slot: `G2`
- Role: `gov`
- Provider: `minimax`
- Model: `MiniMax-M2.5-highspeed`
- Finish reason: `length`
- Error: `G2_empty_text`
- Transport attempts: `1`
- Transport recovered: `false`

## Root Cause

The raw MiniMax G2 output began with hidden thinking and reached the output limit before producing a parseable compact Gov baton. After the runner's thinking filter, the contract-bearing text was empty.

The runner correctly treated this as a content/contract failure and did not score the packet.

## Preserved Evidence

- Provider trace: `TRACE_PROVIDER_CALLS.jsonl`
- Live summary: `blind_canary_live_summary.json`
- Raw G2 output: `raw_provider_outputs/004_G2.json`
- Runtime subset: `runtime_manifest_subset_i003_n001.json`

## Claim Boundary

This invalid attempt preserves a runtime failure in the blind canary lane. It must not be counted as a pass, failure-rate datapoint, FP/FN datapoint, or architecture-quality result.
