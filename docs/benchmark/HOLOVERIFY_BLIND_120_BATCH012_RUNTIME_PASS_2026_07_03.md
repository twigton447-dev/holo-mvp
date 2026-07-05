# HoloVerify Blind 120 Batch 012 Runtime Pass

Status: `RUNTIME_FIREWALL_PASS_AND_POSTHOC_SCORE_CLEAN`

Date: 2026-07-03

Run folder:

`docs/benchmark/holoverify_blind_120_live_runs_2026_07_03/run_20260703T042849Z`

## Scope

- Lane: `HOLOVERIFY_BLIND_120_10PKT_RUNTIME_FIREWALL_V0`
- Batch: 12
- Opaque packet indices: 111-120
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

## Post-Hoc Score

After the runtime trace froze, the local post-hoc scorer was run.

- Packets scored: 10
- Correct: 10
- Incorrect: 0
- Score artifact: `blind_120_posthoc_score_trace_bound_v1.json`

## Token Accounting

- Input tokens: 23,937
- Output tokens: 13,060
- Total tokens: 42,591

## Boundary

This is a scored batch checkpoint. With this batch, the fixed-Gov Holo runtime lane has completed 120/120 packets, but no solo comparison, judge result, ablation result, FP/FN public claim, or KNEW rate is licensed by this artifact alone.

## Evidence Pointers

- Summary: `blind_120_live_summary.json`
- Trace: `TRACE_PROVIDER_CALLS.jsonl`
- Runtime results: `blind_canary_runtime_results.json`
- Score artifact: `blind_120_posthoc_score_trace_bound_v1.json`
- Raw provider outputs: `raw_provider_outputs/`
- Runtime manifest subset: `runtime_manifest_subset_i111_n010.json`
