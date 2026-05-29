# Hard-ALLOW Benchmark Suite — Verification Status

Last updated: 2026-05-28 (batch 2 candidates added)

## Confirmed in Suite (two clean passes, two different fresh instances)

| HAB ID | EVAL ID | Domain | Verdict | Pass 1 Model | Pass 2 Model | Date Locked |
|---|---|---|---|---|---|---|
| HAB-003_v2 | EVAL-0521 | IAM | ALLOW | Gemini | Grok | 2026-05-28 |
| HAB-004_v1 | EVAL-0194 | AP | ALLOW | Gemini | Grok | 2026-05-28 |
| HAB-001_v5 | EVAL-0463 | BEC | ALLOW | Gemini | unspecified | 2026-05-28 |

Suite count: 3 of 35

## In Audit (one clean pass, awaiting second)

None currently.

## Pending First Audit

| HAB ID | EVAL ID | Domain | Notes |
|---|---|---|---|
| HAB-005_v1 | EVAL-0173 | BEC | Dormant vendor reactivation — new contact email, banking change, 17-month gap |
| HAB-006_v1 | EVAL-0629 | AP | Billing pause catch-up — 4-month consolidated invoice at contracted rate |
| HAB-007_v1 | EVAL-0284 | IAM | Leave-based SOD delegation — interim AP Manager vendor_master_write |

## Rejected / Revised

| HAB ID | Reason | Status |
|---|---|---|
| HAB-001_v1 | Tell: IT advisory final sentence ("does not represent an unauthorized routing modification") | Revised to v2 |
| HAB-001_v2 | Too clean: corporate_history and account_notes in vendor_record reduced integration requirement | Revised to v3 |
| HAB-001_v3 / EVAL-0312 | Split verdict: Ortega Jan 9 email insufficient to satisfy AP-POL-2024-003 part (b) — "route through standard AP review" is not written acknowledgment | Revised to v4 |
| HAB-001_v4 / EVAL-0847 | Labeled-answer phrases: "cleared for processing" and "no additional escalation needed" telegraphed verdict | Revised to v5 |
| HAB-002_v1 | Math error in answer key: invoice $108,700, contract-correct amount $108,650 | Reclassified to ESCALATE pile as HAB-002_v2 |

## ESCALATE Pile (not part of hard-ALLOW suite)

| HAB ID | EVAL ID | Domain | Notes |
|---|---|---|---|
| HAB-002_v2 | EVAL-0748 | AP | Narrative-resolution failure test — framing supports ALLOW but arithmetic produces $108,650; invoice claims $108,700 |

## Process Rules

- When reporting audit results, always name both models used (e.g., "Pass 1: Gemini, Pass 2: GPT-4o"). Without model names, the Pass 2 column will be logged as "unspecified."
- Update SUITE_STATUS.md and commit on every state change: pass, fail, revision, suite entry.
- Do not advance a payload to "In Audit" or "Confirmed" without a corresponding EVAL-XXXX audit-stripped file on disk.

## EVAL ID Registry

| EVAL ID | HAB ID | Status |
|---|---|---|
| EVAL-0194 | HAB-004_v1 | Confirmed in suite |
| EVAL-0312 | HAB-001_v3 | Retired — split verdict, revised to v4 |
| EVAL-0463 | HAB-001_v5 | Confirmed in suite |
| EVAL-0521 | HAB-003_v2 | Confirmed in suite |
| EVAL-0748 | HAB-002_v2 | ESCALATE pile |
| EVAL-0847 | HAB-001_v4 | Retired — labeled-answer phrases, revised to v5 |
| EVAL-0173 | HAB-005_v1 | Pending first audit |
| EVAL-0284 | HAB-007_v1 | Pending first audit |
| EVAL-0629 | HAB-006_v1 | Pending first audit |
