# BAL100 Selected Pairs Benchmark Entry Manifest

Created: 2026-06-19T19:00:56Z

Status: `PASS`

Scope: selected BAL100 Batch 001 pairs only. This package does not advance the full batch.

## Counts

- Pair families: 2
- Packets: 4
- ALLOW packets: 2
- ESCALATE packets: 2
- Families: `BEC-PAIR-009`, `BEC-PAIR-010`

## Families

| Family | Seam | Judge | HoloGov | Active Models |
| --- | --- | --- | --- | --- |
| BEC-PAIR-009 | BEC_CALLBACK_PROVENANCE | PASS | 2/2 KNEW | 6/6 KNEW |
| BEC-PAIR-010 | BEC_CALLBACK_PROVENANCE | PASS | 2/2 KNEW | 6/6 KNEW |

## Packets

| Packet | Truth | Hash8 | Frozen Packet | Trace |
| --- | --- | --- | --- | --- |
| BAL100-BEC-PAIR-009-ALLOW | ALLOW | `7b6061a9` | `holo_builder/outputs/frozen/BAL100-BEC-PAIR-009-ALLOW_7b6061a9.json` | `traces/BAL100-BEC-PAIR-009_pair_4dna_seed447/BAL100-BEC-PAIR-009-ALLOW_7b6061a9_4dna_trace.json` |
| BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL | ESCALATE | `b49b9817` | `holo_builder/outputs/frozen/BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL_b49b9817.json` | `traces/BAL100-BEC-PAIR-009_pair_4dna_seed447/BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL_b49b9817_4dna_trace.json` |
| BAL100-BEC-PAIR-010-ALLOW | ALLOW | `69323b92` | `holo_builder/outputs/frozen/BAL100-BEC-PAIR-010-ALLOW_69323b92.json` | `traces/BAL100-BEC-PAIR-010_pair_4dna_seed447/BAL100-BEC-PAIR-010-ALLOW_69323b92_4dna_trace.json` |
| BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL | ESCALATE | `31068b3c` | `holo_builder/outputs/frozen/BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL_31068b3c.json` | `traces/BAL100-BEC-PAIR-010_pair_4dna_seed447/BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL_31068b3c_4dna_trace.json` |

## Validation

- Frozen packets checked: 4
- Traces checked: 4
- Judge packet entries checked: 4
- Payload hashes recomputed: 4
- Failure count: 0

## Non-Actions

- Provider calls: false
- New traces: false
- Judge rerun: false
- QA: false
- Ablation: false
- Packet edits: false
- Frozen artifact edits: false
- Scorecard edits: false
- Push: false

Recommendation: `Ready to use as the selected-pairs benchmark entry package.`
