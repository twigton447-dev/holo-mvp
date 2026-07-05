# HoloVerify Blind 120 Batches 001-012 Post-Hoc Score Checkpoint

Status: `HOLO_RUNTIME_120_POSTHOC_SCORE_COMPLETE`

Date: 2026-07-03

## Scope

This checkpoint scores only the already trace-frozen fixed-Gov Holo runtime batches:

- Batch 001: opaque packet indices 1-10
- Batch 002: opaque packet indices 11-20
- Batch 003: opaque packet indices 21-30
- Batch 004: opaque packet indices 31-40
- Batch 005: opaque packet indices 41-50
- Batch 006: opaque packet indices 51-60
- Batch 007: opaque packet indices 61-70
- Batch 008: opaque packet indices 71-80
- Batch 009: opaque packet indices 81-90
- Batch 010: opaque packet indices 91-100
- Batch 011: opaque packet indices 101-110
- Batch 012: opaque packet indices 111-120

No solo runs, judges, ablations, runtime reruns, substitutions, or public-claim steps were executed during scoring.

## Score Result

- Packets scored: 120
- Correct: 120
- Incorrect: 0
- Runtime batches included: 12
- Provider calls represented: 600

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
| 008 | `run_20260703T035527Z` | 10 | 10 | 0 | 42,488 |
| 009 | `run_20260703T040448Z` | 10 | 10 | 0 | 42,946 |
| 010 | `run_20260703T041255Z` | 10 | 10 | 0 | 42,964 |
| 011 | `run_20260703T042127Z` | 10 | 10 | 0 | 43,865 |
| 012 | `run_20260703T042849Z` | 10 | 10 | 0 | 42,591 |

## Token Accounting

- Total Holo tokens represented: 515,497
- Average tokens per packet: 4,295.81
- Average tokens per 10-packet batch: 42,958.08

## Trace Hash Binding

Each score artifact binds to the frozen runtime trace before scoring. The final checkpoint records the recomputed per-batch trace hashes so the rollup demonstrates that linkage directly.

| Batch | Run Folder | `TRACE_CALLS.jsonl` SHA-256 | `TRACE_PROVIDER_CALLS.jsonl` SHA-256 |
|---|---|---|---|
| 001 | `run_20260703T025059Z` | `856faa06fba2fa029f5f5808d2223fc2ecc119e09fe724b80d75bd6c7376ec82` | `dccafc4e4f797967537013d29f3bcd5884204a0a798f166df0f8bcf68c84159c` |
| 002 | `run_20260703T025830Z` | `3c06ee1ca174a28faa4bb1785df88b8bfbf719473c3e8e6fafb2567d1eae297d` | `4d0c05fb29bdb757c47ab322fa9d73803a89dbe03a3afec2bf413ec9f299f5e5` |
| 003 | `run_20260703T030659Z` | `40166e6205995607c40458457c98abe68c386c02678813ff2c570a0b0f41e965` | `01184072b8328c6a7d3d865a41347a234d98572f9b8d67fe8a03825d636a4536` |
| 004 | `run_20260703T032108Z` | `cadb4243b8f4f1c812058f8f4026b327c6003a3ab7bf6d8adaa9affa24b5caeb` | `8aa123d946aaadc559b457e888aad94d9ab51a06f84689a5ea8a2fad8ece5372` |
| 005 | `run_20260703T032844Z` | `cd223da6cba4a72ec3cabf10620a48cad5ba9f1ea38da6e2c08c18468ada2b1d` | `44e1856eb6d8493afcfc10f8158d438bd704f687c657ca781ffceb8c15e61642` |
| 006 | `run_20260703T033717Z` | `ef252446fb183b9b2ab067964733eab289c9b7f06780b71d56a12b95dfe75dc1` | `28063d048c79e443a92832377b261a3a68ecaaaa3c471df288e025306fd853d5` |
| 007 | `run_20260703T034719Z` | `118c2cbafa3174d0a8863702c019657892dff2b6a83419407005ae8ef577c980` | `bdd271dd883af379a19a053ec5a0a09f83a4569aa7e7ba94ed45d06a1ba1f58c` |
| 008 | `run_20260703T035527Z` | `b28c761139eaa65667604cd49da2800d54e9145454506934a78dcee8c84968d4` | `9699ce4892dfe6e57c61be54e19ac184a6ba1e1476cb232bc193c6c0cdf9031e` |
| 009 | `run_20260703T040448Z` | `2f5e3bdfd039ee4cedf3c4538678f3d0a64d61f5d0c8d83ba2ea6754bb382231` | `39e1f8951dbaa46d5f4ec51c87b3df0e1f7867bccf1df4bfb9ffb1078a82ebf0` |
| 010 | `run_20260703T041255Z` | `49e6a99f6248bd61e840b7d2b52c367fce64ef9ae48986f9e54e517099b523bf` | `97b15ac56820eb4e010dc4ef89b0f842c751e6ebe00c81d1638891758220184a` |
| 011 | `run_20260703T042127Z` | `957eac8c7dd5006e1ec2b40a6fcb7b3bdad441e6b593ae7dcd598176b43f8998` | `d964ff533f67c5907422fa986e7700aef919ffacc223962c42d9c9749e04cdf1` |
| 012 | `run_20260703T042849Z` | `525dd7e2c40dfc5ac800c6e3caaa8eaac09ea48a86307b6637f2807afde786c5` | `ba42c0f3949013432ae0d0459a5802c1b1510af02caf32b5a2b5ada7d8c0d983` |

## Decision

The fixed-Gov Holo runtime lane completed 120/120 packets with 120 correct post-hoc scores and no Holo miss. No patch is indicated from this Holo-only checkpoint.

## Boundary

This checkpoint completes the fixed-Gov Holo 120 runtime result only. It is not a solo comparison, not an ablation result, not a judge result, and not a public FP/FN or KNEW-rate claim by itself.

Next locked sequence remains:

1. Run the full same-model solo baseline on all 120 packets.
2. Build the Holo-vs-solo comparison memo.
3. Run the randomized ablation subset.
4. Only then update public claims.
