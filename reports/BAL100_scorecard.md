# BAL100 Scorecard

Created: 2026-06-18

Scope: Balanced 100-packet benchmark factory accounting after BAL100 Batch 001 selected-pair Judge.

This scorecard records proof-credit status only. It does not create new traces, run Judge, run QA or ablation, edit packets, edit frozen artifacts, or advance full BAL100 Batch 001 wholesale.

## Current Plain-English Status

We now have two clean factory-produced pair families that went from draft to scout to repair to freeze to trace to Judge with all KNEW labels.

That is 4 proof-credit-ready packets toward the 100-packet target.

The process works, but 48 pair families remain.

## Target Accounting

| Field | Count |
| --- | ---: |
| Target pair families | 50 |
| Target packets | 100 |
| Target ALLOW packets | 50 |
| Target ESCALATE packets | 50 |
| Proof-credit-ready pair families | 2 |
| Proof-credit-ready packets | 4 |
| Proof-credit-ready ALLOW packets | 2 |
| Proof-credit-ready ESCALATE packets | 2 |
| Remaining pair families | 48 |
| Remaining packets | 96 |

## Proof-Credit-Ready Families

| Family | ALLOW packet | ESCALATE packet | Judge status | HoloGov labels | Active model labels | Credit scope |
| --- | --- | --- | --- | --- | --- | --- |
| `BEC-PAIR-009` | `BAL100-BEC-PAIR-009-ALLOW` | `BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL` | PASS | 2/2 KNEW | 6/6 KNEW | Selected BAL100 Batch 001 pair only |
| `BEC-PAIR-010` | `BAL100-BEC-PAIR-010-ALLOW` | `BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL` | PASS | 2/2 KNEW | 6/6 KNEW | Selected BAL100 Batch 001 pair only |

## Evidence Pointers

| Packet | Truth | Frozen artifact | Payload hash | Trace | Judge |
| --- | --- | --- | --- | --- | --- |
| `BAL100-BEC-PAIR-009-ALLOW` | ALLOW | `holo_builder/outputs/frozen/BAL100-BEC-PAIR-009-ALLOW_7b6061a9.json` | `7b6061a9d2566361c5914ce6d11245fd66c7f9bddd134cf55afe970cb5c20c95` | `traces/BAL100-BEC-PAIR-009_pair_4dna_seed447/BAL100-BEC-PAIR-009-ALLOW_7b6061a9_4dna_trace.json` | `reports/BAL100_BATCH_001_selected_pairs_judge_summary.json` |
| `BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL` | ESCALATE | `holo_builder/outputs/frozen/BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL_b49b9817.json` | `b49b9817b4c708de7718854545d3acfe1bad8c1256aa706cb0dd1d3b26bbdb09` | `traces/BAL100-BEC-PAIR-009_pair_4dna_seed447/BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL_b49b9817_4dna_trace.json` | `reports/BAL100_BATCH_001_selected_pairs_judge_summary.json` |
| `BAL100-BEC-PAIR-010-ALLOW` | ALLOW | `holo_builder/outputs/frozen/BAL100-BEC-PAIR-010-ALLOW_69323b92.json` | `69323b92842841c15643420b062bb1f0dd5f0f493fc08a2dc6ffe4620d3abbb4` | `traces/BAL100-BEC-PAIR-010_pair_4dna_seed447/BAL100-BEC-PAIR-010-ALLOW_69323b92_4dna_trace.json` | `reports/BAL100_BATCH_001_selected_pairs_judge_summary.json` |
| `BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL` | ESCALATE | `holo_builder/outputs/frozen/BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL_31068b3c.json` | `31068b3cd517b3a1994bf83c01cf276533a1ed2e063b74344221448c0ae867ca` | `traces/BAL100-BEC-PAIR-010_pair_4dna_seed447/BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL_31068b3c_4dna_trace.json` | `reports/BAL100_BATCH_001_selected_pairs_judge_summary.json` |

## BEC Seam Progress

| Segment | Pair families | Packets | Status |
| --- | ---: | ---: | --- |
| BAL100 Batch 001 selected set | 2 | 4 | `proof_credit_ready` |
| HBB-BEC-001 / HBB-BEC-002 | 2 | 4 | Frozen, ledgered, traced, judged, loss-autopsied, patched, regression-protected; needs post-patch rerun before proof credit |
| BAL100 Batch 001 non-selected drafts 003-008 | 6 | 12 | Draft/repair candidates; not proof-credit-ready |

## Non-Credit Boundaries

- Do not claim full BAL100 Batch 001 is proof-ready.
- Do not claim all 16 Batch 001 drafts passed.
- Do not count `BEC-PAIR-003` through `BEC-PAIR-008` as proof-credit-ready.
- Do not count `HBB-BEC-001` or `HBB-BEC-002` as proof-credit-ready until post-patch rerun evidence exists.
- Historical ledger rows remain scout or historical material unless promoted through the active evidence pipeline.

## Attestation

No live calls, new traces, Judge rerun, QA, ablation, packet edits, frozen artifact edits, or push occurred for this scorecard update.
