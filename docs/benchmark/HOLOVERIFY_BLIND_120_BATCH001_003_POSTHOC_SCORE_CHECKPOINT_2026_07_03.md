# HoloVerify Blind 120 Batches 001-003 Post-Hoc Score Checkpoint

Status: `POSTHOC_SCORE_CHECKPOINT_CLEAN`

Date: 2026-07-03

## Scope

This checkpoint scores only the already trace-frozen Holo runtime batches:

- Batch 001: opaque packet indices 1-10
- Batch 002: opaque packet indices 11-20
- Batch 003: opaque packet indices 21-30

No providers, solo runs, judges, or runtime reruns were executed during scoring.

## Score Result

- Packets scored: 30
- Correct: 30
- Incorrect: 0
- Runtime batches included: 3
- Provider calls represented: 150

## Batch Breakdown

| Batch | Run Folder | Packets | Correct | Incorrect | Tokens |
|---|---|---:|---:|---:|---:|
| 001 | `run_20260703T025059Z` | 10 | 10 | 0 | 42,972 |
| 002 | `run_20260703T025830Z` | 10 | 10 | 0 | 43,017 |
| 003 | `run_20260703T030659Z` | 10 | 10 | 0 | 43,040 |

## Trace-Binding

Each post-hoc score artifact binds to the frozen trace before loading the hidden scoring map.

Score artifacts:

- `run_20260703T025059Z/blind_120_posthoc_score_trace_bound_v1.json`
- `run_20260703T025830Z/blind_120_posthoc_score_trace_bound_v1.json`
- `run_20260703T030659Z/blind_120_posthoc_score_trace_bound_v1.json`

## Decision

No Holo miss is present in the first 30 scored packets. No patch is indicated from this checkpoint. Continue the fixed-Gov Holo 120 runtime sequence unless a later scored batch reveals an error.

## Boundary

This checkpoint covers 30/120 Holo packets only. It is not the final 120-packet result, not a solo comparison, not an ablation result, and not a public claim by itself.
