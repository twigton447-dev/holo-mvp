# HoloVerify Blind 120 Batches 001-007 Post-Hoc Score Checkpoint

Status: `POSTHOC_SCORE_CHECKPOINT_CLEAN`

Date: 2026-07-03

## Scope

This checkpoint scores only the already trace-frozen Holo runtime batches:

- Batch 001: opaque packet indices 1-10
- Batch 002: opaque packet indices 11-20
- Batch 003: opaque packet indices 21-30
- Batch 004: opaque packet indices 31-40
- Batch 005: opaque packet indices 41-50
- Batch 006: opaque packet indices 51-60
- Batch 007: opaque packet indices 61-70

No providers, solo runs, judges, or runtime reruns were executed during scoring.

## Score Result

- Packets scored: 70
- Correct: 70
- Incorrect: 0
- Runtime batches included: 7
- Provider calls represented: 350

## Batch Breakdown

| Batch | Run Folder | Packets | Correct | Incorrect | Tokens |
|---|---|---:|---:|---:|---:|
| 001 | `run_20260703T025059Z` | 10 | 10 | 0 | 42,972 |
| 002 | `run_20260703T025830Z` | 10 | 10 | 0 | 43,017 |
| 003 | `run_20260703T030659Z` | 10 | 10 | 0 | 43,040 |
| 004 | `run_20260703T032108Z` | 10 | 10 | 0 | 42,550 |
| 005 | `run_20260703T032844Z` | 10 | 10 | 0 | 43,077 |
| 006 | `run_20260703T033717Z` | 10 | 10 | 0 | 42,235 |
| 007 | `run_20260703T034719Z` | 10 | 10 | 0 | 43,752 |

## Decision

No Holo miss is present in the first 70 scored packets. No patch is indicated from this checkpoint. Continue the fixed-Gov Holo 120 runtime sequence unless a later scored batch reveals an error.

## Boundary

This checkpoint covers 70/120 Holo packets only. It is not the final 120-packet result, not a solo comparison, not an ablation result, and not a public claim by itself.
