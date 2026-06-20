# BAL100 Scorecard

Created: 2026-06-19T23:32:01Z

Scope: Balanced 100-packet benchmark factory accounting after BAL100 Batch 001 selected-pair Judge, residual closure, BEC-PAIR-005 diagnostic closure, and BAL100 leaderboard-to-20 five-ALLOW Judge approval.

This scorecard records proof-credit status only. This update moves the approved five-packet ALLOW tranche into accounting; it does not create new traces, rerun Judge, run QA or ablation, edit packets, edit frozen artifacts, or push.

## Claim Boundary

This scorecard records proof-credit status and balanced inventory accounting. It does not claim HoloGov advantage over collapsed solos.

The five added ALLOW packets were accepted because HoloGov and active solos agreed: HoloGov `5/5 KNEW`, active solos `15/15 KNEW`, solo-collapse win count `0`.

## Current Plain-English Status

BAL100 now has the selected Batch 001 pair-family proof-credit set plus the five Judge-passed hard-ALLOW additions for the leaderboard-to-20 balance target.

Public registry target reached: **20 frozen packets**, balanced as **10 ALLOW / 10 ESCALATE**.

Scorecard-local proof-credit rows now tracked here: **9 packets**: 7 ALLOW and 2 ESCALATE. The difference is because the public registry also includes the pre-existing 11 packets outside this selected BAL100 accounting artifact.

## Target Accounting

| Field | Count |
| --- | ---: |
| Target pair families | 50 |
| Target packets | 100 |
| Target ALLOW packets | 50 |
| Target ESCALATE packets | 50 |
| Proof-credit-ready pair families | 2 |
| Proof-credit-ready standalone ALLOW packets | 5 |
| Proof-credit-ready packets tracked here | 9 |
| Proof-credit-ready ALLOW packets tracked here | 7 |
| Proof-credit-ready ESCALATE packets tracked here | 2 |
| Public registry packets after update | 20 |
| Public registry ALLOW packets after update | 10 |
| Public registry ESCALATE packets after update | 10 |
| Remaining packets to 100-packet target | 91 |

## Proof-Credit-Ready Pair Families

| Family | ALLOW packet | ESCALATE packet | Judge status | HoloGov labels | Active model labels | Credit scope |
| --- | --- | --- | --- | --- | --- | --- |
| `BEC-PAIR-009` | `BAL100-BEC-PAIR-009-ALLOW` | `BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL` | PASS | 2/2 KNEW | 6/6 KNEW | Selected BAL100 Batch 001 pair only |
| `BEC-PAIR-010` | `BAL100-BEC-PAIR-010-ALLOW` | `BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL` | PASS | 2/2 KNEW | 6/6 KNEW | Selected BAL100 Batch 001 pair only |

## Leaderboard-20 ALLOW Additions

| Packet | Truth | Hash8 | Judge | HoloGov | Active Models |
| --- | --- | --- | --- | --- | --- |
| `BAL100-HARD-ALLOW-HAB-001-ALLOW` | ALLOW | `85fb8dca` | PASS | KNEW | 3/3 KNEW |
| `BAL100-HARD-ALLOW-HAB-003-ALLOW` | ALLOW | `673d6c1b` | PASS | KNEW | 3/3 KNEW |
| `BAL100-HARD-ALLOW-REP-001-ALLOW` | ALLOW | `9706a499` | PASS | KNEW | 3/3 KNEW |
| `BAL100-HARD-ALLOW-REP-002-ALLOW` | ALLOW | `999d2812` | PASS | KNEW | 3/3 KNEW |
| `BAL100-HARD-ALLOW-REP-003-ALLOW` | ALLOW | `c8566512` | PASS | KNEW | 3/3 KNEW |

## Evidence Pointers For ALLOW Additions

| Packet | Truth | Frozen artifact | Payload hash | Trace | Judge |
| --- | --- | --- | --- | --- | --- |
| `BAL100-HARD-ALLOW-HAB-001-ALLOW` | ALLOW | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-001-ALLOW_85fb8dca.json` | `85fb8dca9cac004f3d634b80afd6f69d3e178334fbb4bc886c360c35d6ba4517` | `scout_runs/BAL100-LEADERBOARD-20_allow_official_trace_live_20260619T205143Z/official_trace_records/BAL100-HARD-ALLOW-HAB-001-ALLOW_85fb8dca_official_trace.json` | `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_SUMMARY_001.json` |
| `BAL100-HARD-ALLOW-HAB-003-ALLOW` | ALLOW | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-003-ALLOW_673d6c1b.json` | `673d6c1bee9630e89c22eb731dfaa80dddda07c27c575937431220c54c8ce251` | `scout_runs/BAL100-LEADERBOARD-20_allow_official_trace_live_20260619T205143Z/official_trace_records/BAL100-HARD-ALLOW-HAB-003-ALLOW_673d6c1b_official_trace.json` | `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_SUMMARY_001.json` |
| `BAL100-HARD-ALLOW-REP-001-ALLOW` | ALLOW | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-REP-001-ALLOW_9706a499.json` | `9706a499af2c69003e452f6051642c733bf75fde8d9edb1dbf4245c58fb68991` | `scout_runs/BAL100-LEADERBOARD-20_allow_replacement_official_trace_live_20260619T220000Z/official_trace_records/BAL100-HARD-ALLOW-REP-001-ALLOW_9706a499_official_trace.json` | `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_SUMMARY_001.json` |
| `BAL100-HARD-ALLOW-REP-002-ALLOW` | ALLOW | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-REP-002-ALLOW_999d2812.json` | `999d2812a089929ccdb359c25deadb4e2b2954ce35a20c7484517233fe4c39c8` | `scout_runs/BAL100-LEADERBOARD-20_allow_replacement_official_trace_live_20260619T220000Z/official_trace_records/BAL100-HARD-ALLOW-REP-002-ALLOW_999d2812_official_trace.json` | `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_SUMMARY_001.json` |
| `BAL100-HARD-ALLOW-REP-003-ALLOW` | ALLOW | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-REP-003-ALLOW_c8566512.json` | `c8566512d0ef5684701acaec4e0b4fdef2735cbfba3ec8420c3e771d5c9c62ad` | `scout_runs/BAL100-LEADERBOARD-20_allow_replacement_official_trace_live_20260619T220000Z/official_trace_records/BAL100-HARD-ALLOW-REP-003-ALLOW_c8566512_official_trace.json` | `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_SUMMARY_001.json` |

## Non-Credit Boundaries

- Do not claim full BAL100 Batch 001 is proof-ready.
- Do not count `BEC-PAIR-003` through `BEC-PAIR-008` as proof-credit-ready.
- Do not mark `BEC-PAIR-005` prefreeze-ready or proof-credit-ready from the diagnostic rescout.
- Do not count `HBB-BEC-001` or `HBB-BEC-002` as proof-credit-ready until post-patch rerun evidence exists.
- The five ALLOW additions are standalone hard-ALLOW proof-credit packets, not ESCALATE-paired families.
- The five ALLOW additions are not HoloGov-over-solo-collapse wins; active solos also labeled them KNEW.

## Attestation

Scorecard movement and leaderboard update were performed under Taylor approval. No provider calls, new traces, Judge rerun, QA, ablation, packet edits, frozen artifact edits, or push occurred for this accounting update.
