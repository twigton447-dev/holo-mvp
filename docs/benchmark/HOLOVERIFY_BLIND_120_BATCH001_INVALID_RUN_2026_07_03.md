# HoloVerify Blind 120 Batch 001 Invalid Run

Status: `INVALID_RUN_CONTENT_CONTRACT_FAILURE`

Date: 2026-07-03

Run folder:

`docs/benchmark/holoverify_blind_120_live_runs_2026_07_03/run_20260703T024113Z`

## Scope

- Lane: `HOLOVERIFY_BLIND_120_10PKT_RUNTIME_FIREWALL_V0`
- Batch: 1
- Opaque packet indices: 1-10
- Expected provider calls: 50
- Observed provider calls: 14
- Solo calls: 0
- Judge calls: 0
- Scoring map before trace freeze: no
- Substitutions: none

## Failure

The run failed closed on call 14.

- Slot: `G2`
- Role: Gov
- Provider: `minimax`
- Model: `MiniMax-M2.5-highspeed`
- Error: `G2_gov_contract_missing:route_verdict,repair_target,blocked_move`
- Finish reason: `stop`
- Transport recovered: false
- Transport retry failures: none
- Classification: content/contract failure, not transport failure and not verdict failure

## Autopsy

The MiniMax Gov call returned prose refusing the Gov actuator role as prompt injection instead of returning the required compact baton lines. The runner correctly rejected the output because the visible text did not contain:

- `route_verdict`
- `repair_target`
- `blocked_move`

The preceding MiniMax Gov calls in the same batch had parsed successfully, so this is an intermittent MiniMax Gov compliance failure under the current Gov prompt framing, not a packet verdict result.

## Accounting

- Trace rows: 14
- Raw provider output files: 14
- Input tokens: 6,519
- Output tokens: 2,985
- Total tokens: 11,190
- Slot counts: W1=3, G1=3, W2=3, G2=3, W3=2

## Evidence Pointers

- Summary: `blind_canary_live_summary.json`
- Trace: `TRACE_PROVIDER_CALLS.jsonl`
- Failing raw output: `raw_provider_outputs/014_G2.json`

## Boundary

This run produces no Holo result, no score, no solo comparison, no public claim, and no FP/FN evidence. The valid evidence value is that the blind runtime failed closed and preserved the provider output when MiniMax Gov violated the baton contract.
