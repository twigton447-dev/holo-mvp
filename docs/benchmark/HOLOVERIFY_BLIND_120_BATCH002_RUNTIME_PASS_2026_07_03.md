# HoloVerify Blind 120 Batch 002 Runtime Pass

Status: `RUNTIME_FIREWALL_PASS_UNSCORED`

Date: 2026-07-03

Run folder:

`docs/benchmark/holoverify_blind_120_live_runs_2026_07_03/run_20260703T025830Z`

## Scope

- Lane: `HOLOVERIFY_BLIND_120_10PKT_RUNTIME_FIREWALL_V0`
- Batch: 2
- Opaque packet indices: 11-20
- Expected provider calls: 50
- Observed provider calls: 50
- Solo calls: 0
- Judge calls: 0
- Scoring map before trace freeze: no
- Substitutions: none

## Runtime Result

The batch completed the live runtime firewall.

- Provider failures: 0
- Content contract failures: 0
- Transport recovered calls: 0
- Trace rows: 50
- Slot counts: W1=10, G1=10, W2=10, G2=10, W3=10
- Runtime firewall passed: true

## Token Accounting

- Input tokens: 23,860
- Output tokens: 14,131
- Total tokens: 43,017

## Boundary

This is a runtime pass, not a scored benchmark result. The post-hoc scorer was not run in this step. No solo comparison, judge result, FP/FN claim, public claim, or KNEW rate is licensed by this artifact alone.

## Evidence Pointers

- Summary: `blind_120_live_summary.json`
- Trace: `TRACE_PROVIDER_CALLS.jsonl`
- Runtime results: `blind_canary_runtime_results.json`
- Raw provider outputs: `raw_provider_outputs/`
- Runtime manifest subset: `runtime_manifest_subset_i011_n010.json`
