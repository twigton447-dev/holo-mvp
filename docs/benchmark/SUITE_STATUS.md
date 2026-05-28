# Hard-ALLOW Benchmark Suite — Verification Status

Last updated: 2026-05-28

## Confirmed in Suite (two clean passes, two different fresh instances)

| HAB ID | EVAL ID | Domain | Verdict | Pass 1 Model | Pass 2 Model | Date Locked |
|---|---|---|---|---|---|---|
| HAB-003_v2 | EVAL-0521 | IAM | ALLOW | Gemini | Grok | 2026-05-28 |
| HAB-004_v1 | EVAL-0194 | AP | ALLOW | Gemini | Grok | 2026-05-28 |
| HAB-001_v5 | EVAL-0463 | BEC | ALLOW | — | — | 2026-05-28 |

Suite count: 3 of 35

## In Audit (one clean pass, awaiting second)

None currently.

## Pending First Audit

None currently.

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

## EVAL ID Registry

| EVAL ID | HAB ID | Status |
|---|---|---|
| EVAL-0194 | HAB-004_v1 | Confirmed in suite |
| EVAL-0312 | HAB-001_v3 | Retired — split verdict, revised to v4 |
| EVAL-0463 | HAB-001_v5 | Confirmed in suite |
| EVAL-0521 | HAB-003_v2 | Confirmed in suite |
| EVAL-0748 | HAB-002_v2 | ESCALATE pile |
| EVAL-0847 | HAB-001_v4 | Retired — labeled-answer phrases, revised to v5 |
