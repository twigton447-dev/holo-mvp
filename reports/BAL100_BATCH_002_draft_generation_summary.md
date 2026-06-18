# BAL100 Batch 002 Draft Generation Summary

Batch: `BAL100-BATCH-002`
Status: draft candidates generated; static only.

Generated 16 BAL100 Batch 002 explained-anomaly draft packet candidates from the committed design. This task did not run scout, live calls, Judge, QA, ablation, freeze, or traces, and did not change proof-credit counts.

## Counts

| Field | Count |
| --- | ---: |
| sibling families | 8 |
| draft packets | 16 |
| ALLOW hypotheses | 8 |
| ESCALATE hypotheses | 8 |
| benchmark-credit packets | 0 |

## Draft Files

| Family | Sibling | Packet ID | File |
| --- | --- | --- | --- |
| `BAL100-BEC-EXPLAINED-ANOMALY-011` | `A` | `BAL100-BEC-EXPLAINED-ANOMALY-011-A` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_011_A_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-011` | `B` | `BAL100-BEC-EXPLAINED-ANOMALY-011-B` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_011_B_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-012` | `A` | `BAL100-BEC-EXPLAINED-ANOMALY-012-A` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_012_A_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-012` | `B` | `BAL100-BEC-EXPLAINED-ANOMALY-012-B` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_012_B_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-013` | `A` | `BAL100-BEC-EXPLAINED-ANOMALY-013-A` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_013_A_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-013` | `B` | `BAL100-BEC-EXPLAINED-ANOMALY-013-B` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_013_B_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-014` | `A` | `BAL100-BEC-EXPLAINED-ANOMALY-014-A` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_014_A_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-014` | `B` | `BAL100-BEC-EXPLAINED-ANOMALY-014-B` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_014_B_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-015` | `A` | `BAL100-BEC-EXPLAINED-ANOMALY-015-A` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_015_A_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-015` | `B` | `BAL100-BEC-EXPLAINED-ANOMALY-015-B` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_015_B_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-016` | `A` | `BAL100-BEC-EXPLAINED-ANOMALY-016-A` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_016_A_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-016` | `B` | `BAL100-BEC-EXPLAINED-ANOMALY-016-B` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_016_B_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-017` | `A` | `BAL100-BEC-EXPLAINED-ANOMALY-017-A` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_017_A_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-017` | `B` | `BAL100-BEC-EXPLAINED-ANOMALY-017-B` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_017_B_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-018` | `A` | `BAL100-BEC-EXPLAINED-ANOMALY-018-A` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_018_A_draft_v0_1.json` |
| `BAL100-BEC-EXPLAINED-ANOMALY-018` | `B` | `BAL100-BEC-EXPLAINED-ANOMALY-018-B` | `holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_018_B_draft_v0_1.json` |

## Invariants

- Packet IDs use neutral `A` / `B` sibling suffixes.
- Each family has one hidden ALLOW hypothesis and one hidden ESCALATE hypothesis.
- Each sibling pair keeps the same action boundary and artifact structure, with one material source-grounding delta.
- Model-visible payload contains only `payload.action` and `payload.context`; expected verdict metadata remains outside payload.
- This draft generation has no benchmark credit and does not reopen Batch 001.

## Proof-Credit Boundary

Proof credit remains only `BEC-PAIR-009` and `BEC-PAIR-010`: 2 pair families / 4 packets.
