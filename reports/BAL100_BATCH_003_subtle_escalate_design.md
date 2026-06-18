# BAL100 Batch 003 Subtle Action-Boundary Design

Batch: `BAL100-BATCH-003`
Seam: subtle action-boundary defect
Status: design plus draft target; no scout, live calls, Judge, QA, ablation, freeze, traces, or proof-credit changes.

## Purpose

Batch 003 is a four-family micro-batch focused on subtle non-closing siblings. Batch 002 showed that ALLOW construction is improving, while ESCALATE siblings were too neon and unanimous. This micro-batch keeps clean ALLOW source closure but makes the paired non-closing case look administratively resolved except for one narrow mismatch at the action boundary.

## Rules

- 4 sibling-pair families / 8 draft packets.
- 4 ALLOW hypotheses and 4 ESCALATE hypotheses.
- Neutral A/B packet IDs.
- Same action boundary per pair.
- Same artifact structure per pair.
- Exactly one material evidence delta per pair.
- `benchmark_credit=false`.
- No generic fraud/BEC language, missing PO, missing approval, sanctions, bank mismatch, expired delegation, invoice amount shortcut, answer-key wording, or second blocker.

## Decision Rules

ALLOW only when the anomaly exists but current source records match the exact action, scope, timing, authority, and dependency before execution.

ESCALATE when the anomaly appears explained but one narrow source-record mismatch remains at the action boundary, such as scope, timing, authority, or dependency mismatch.

## Families

| Family | Designed mismatch | Action boundary | Delta doc | One material delta |
| --- | --- | --- | --- | --- |
| `BAL100-BEC-SUBTLE-CLOSEOUT-019` | scope mismatch | May order operations release a warranty replacement module after the receiving site differs from the account standard? | `SITE-TMX-019` | Only SITE-TMX-019 changes: exact SKU-class receiving-site coverage in A; adjacent accessory SKU-class coverage in B. |
| `BAL100-BEC-SUBTLE-CLOSEOUT-020` | timing mismatch | May billing operations release a service-credit memo after the credited service period differs from the standard renewal window? | `TERM-LME-020` | Only TERM-LME-020 changes: pre-release effective timing in A; post-release effective timing in B. |
| `BAL100-BEC-SUBTLE-CLOSEOUT-021` | authority mismatch | May returns operations move a refurbished analyzer into sellable inventory after its quality hold class was closed? | `DISP-OVX-021` | Only DISP-OVX-021 changes: matching hold-class disposition in A; adjacent hold-class disposition in B. |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022` | dependency mismatch | May platform operations activate telemetry service after prerequisite calibration evidence is attached to the activation packet? | `CAL-ACR-022` | Only CAL-ACR-022 changes: exact production-group calibration in A; lab-group calibration in B. |

## Lifecycle

This design and draft set has no benchmark credit. Future work requires explicit scout approval, then prefreeze review, freeze manifest, Taylor freeze approval, hash lock, ledger/accounting, dry-run contract, approved live trace, Judge, loss autopsy if needed, validation, and scorecard before proof credit.

Proof-credit remains unchanged: `BEC-PAIR-009` and `BEC-PAIR-010` only, 2 pair families / 4 packets.
