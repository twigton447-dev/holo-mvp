# BAL100 Batch 002 Repair Candidate Ranking

Batch: `BAL100-BATCH-002`  
Seam: explained anomaly  
Status: ranking for one targeted repair pass only

## Scope

- Candidate pool: `repair_once` families from the bounded scout triage.
- Ranked candidates: `BAL100-BEC-EXPLAINED-ANOMALY-012`, `013`, `015`, `017`, `018`.
- Excluded from repair: `BAL100-BEC-EXPLAINED-ANOMALY-011` remains quarantined; `014` and `016` remain excluded before scout.
- This report does not run scout, live calls, Judge, QA, ablation, freeze, or traces.
- Proof credit remains unchanged: 2 pair families / 4 packets.

## Ranking Criteria

Preference was given to families with clean provider and parser health, fewer ALLOW false escalations, no Gemini 503 on a key ALLOW row, a clean action boundary, easy preservation of exactly one material evidence delta, and a narrow repair that can make ESCALATE less obvious without muddying the explained-anomaly seam.

## Ranked Candidates

| Rank | Family | Repair decision | Basis |
| ---: | --- | --- | --- |
| 1 | `BAL100-BEC-EXPLAINED-ANOMALY-013` | repair | Clean 10/10 provider and parse health, one OpenAI false escalation on ALLOW, crisp ship-to action boundary, and an easy one-doc source-grounding repair. ESCALATE can be softened from an explicit absence statement into a pending/not-yet-active customer-master distinction. |
| 2 | `BAL100-BEC-EXPLAINED-ANOMALY-017` | repair | Clean 10/10 provider and parse health, one OpenAI false escalation on ALLOW, and a narrow identity-session source repair. ESCALATE can preserve unresolved timing/source mismatch without adding a second blocker. |
| 3 | `BAL100-BEC-EXPLAINED-ANOMALY-012` | repair | Clean 10/10 provider and parse health, one OpenAI false escalation on ALLOW, and a straightforward amount-uplift source-authority repair. It ranks below 013/017 because amount anomalies tend to invite conservative false escalation, but the repair is still narrow and obvious. |
| 4 | `BAL100-BEC-EXPLAINED-ANOMALY-015` | no repair in this pass | No false escalation among successful ALLOW rows, but the key ALLOW packet had a Gemini HTTP 503 and therefore an incomplete clean provider row set. This remains repairable later, but is not in the best three under the no-503 preference. |
| 5 | `BAL100-BEC-EXPLAINED-ANOMALY-018` | no repair in this pass | ALLOW had both an OpenAI false escalation and a Gemini HTTP 503 on the key ALLOW packet. It has the weakest provider-row basis among the repair candidates. |

## Selected Repair Set

Repair only:

- `BAL100-BEC-EXPLAINED-ANOMALY-013`
- `BAL100-BEC-EXPLAINED-ANOMALY-017`
- `BAL100-BEC-EXPLAINED-ANOMALY-012`

Do not repair in this pass:

- `BAL100-BEC-EXPLAINED-ANOMALY-015`
- `BAL100-BEC-EXPLAINED-ANOMALY-018`

## Boundary

This is a draft repair-ranking artifact only. It creates no benchmark credit and does not mark any Batch 002 family prefreeze-ready.
