# BAL100 Leaderboard

Created: 2026-06-19T23:32:01Z

Status: `PASS`

Scope: BAL100 selected proof-credit pairs plus approved five-packet ALLOW balance tranche. This is a proof-credit packet leaderboard, not a model-capability ranking.

## Claim Boundary

This board records balanced hash-locked benchmark inventory and proof-credit packet readiness. It does not claim HoloGov advantage over collapsed solos.

The five ALLOW additions are consensus ALLOW precision packets: HoloGov `5/5 KNEW`, active solos `15/15 KNEW`, solo-collapse win count `0`.

## Public Registry Delta

| Field | Count |
| --- | ---: |
| Previous frozen packets | 11 |
| Added frozen packets | 9 |
| Current frozen packets | 20 |
| Current ALLOW packets | 10 |
| Current ESCALATE packets | 10 |

## BAL100 Counts Tracked Here

| Field | Count |
| --- | ---: |
| Pair families | 2 |
| Standalone ALLOW families | 5 |
| Packets | 9 |
| ALLOW packets | 7 |
| ESCALATE packets | 2 |

## Leaderboard Entries

| Family | Seam | Packets | Judge | HoloGov | Active Models | Status |
| --- | --- | ---: | --- | --- | --- | --- |
| BEC-PAIR-009 | BEC_CALLBACK_PROVENANCE | 2 | PASS | 2/2 KNEW | 6/6 KNEW | leaderboard_ready |
| BEC-PAIR-010 | BEC_CALLBACK_PROVENANCE | 2 | PASS | 2/2 KNEW | 6/6 KNEW | leaderboard_ready |
| BAL100-LEADERBOARD-20-ALLOW-BALANCE | HARD_ALLOW_BALANCE_MIXED_SEAMS | 5 | PASS | 5/5 KNEW | 15/15 KNEW | leaderboard_ready |

## Packet Rows

| Packet | Truth | HoloGov | Hash8 | Payload Hash |
| --- | --- | --- | --- | --- |
| BAL100-BEC-PAIR-009-ALLOW | ALLOW | KNEW | `7b6061a9` | `7b6061a9d2566361c5914ce6d11245fd66c7f9bddd134cf55afe970cb5c20c95` |
| BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL | ESCALATE | KNEW | `b49b9817` | `b49b9817b4c708de7718854545d3acfe1bad8c1256aa706cb0dd1d3b26bbdb09` |
| BAL100-BEC-PAIR-010-ALLOW | ALLOW | KNEW | `69323b92` | `69323b92842841c15643420b062bb1f0dd5f0f493fc08a2dc6ffe4620d3abbb4` |
| BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL | ESCALATE | KNEW | `31068b3c` | `31068b3cd517b3a1994bf83c01cf276533a1ed2e063b74344221448c0ae867ca` |
| BAL100-HARD-ALLOW-HAB-001-ALLOW | ALLOW | KNEW | `85fb8dca` | `85fb8dca9cac004f3d634b80afd6f69d3e178334fbb4bc886c360c35d6ba4517` |
| BAL100-HARD-ALLOW-HAB-003-ALLOW | ALLOW | KNEW | `673d6c1b` | `673d6c1bee9630e89c22eb731dfaa80dddda07c27c575937431220c54c8ce251` |
| BAL100-HARD-ALLOW-REP-001-ALLOW | ALLOW | KNEW | `9706a499` | `9706a499af2c69003e452f6051642c733bf75fde8d9edb1dbf4245c58fb68991` |
| BAL100-HARD-ALLOW-REP-002-ALLOW | ALLOW | KNEW | `999d2812` | `999d2812a089929ccdb359c25deadb4e2b2954ce35a20c7484517233fe4c39c8` |
| BAL100-HARD-ALLOW-REP-003-ALLOW | ALLOW | KNEW | `c8566512` | `c8566512d0ef5684701acaec4e0b4fdef2735cbfba3ec8420c3e771d5c9c62ad` |

## Boundaries

- Does not promote full BAL100 Batch 001.
- Does not count `BEC-PAIR-003` through `BEC-PAIR-008`.
- Does not count `BEC-PAIR-005`.
- Does not count `HBB-BEC-001` or `HBB-BEC-002`.
- The five ALLOW additions are standalone hard-ALLOW proof-credit packets, not ESCALATE-paired families.
- The five ALLOW additions are not HoloGov-over-solo-collapse wins; active solos also labeled them KNEW.
- No provider calls, new traces, Judge rerun, QA, ablation, packet edits, frozen artifact edits, or push occurred for this accounting update.
