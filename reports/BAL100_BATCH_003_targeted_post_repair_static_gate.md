# BAL100 Batch 003 Targeted Post-Repair Static Gate

Status: targeted repair pass complete  
Scope: `019` and `020` only  
Not touched: `021`, `022`  
Live scout / Judge / QA / ablation / freeze / official traces: not run  
Benchmark credit: unchanged

## Repair Plan

- `019`: edit only `SITE-TMX-019` in both siblings. Make the ALLOW ledger row explicitly cover `TMX-18R` field replacements, and make the ESCALATE ledger row cover adjacent `TMX-18A` accessory-kit replacements without adding another blocker.
- `020`: clarify timing while preserving the single `TERM-LME-020` delta. Add the release queue timestamp identically in the billing log for both siblings, make ALLOW effective before that queue, and make ESCALATE entered before queue but effective in the next nightly cycle.

## Static Gate

| Family | Repair Applied | Class |
| --- | --- | --- |
| `BAL100-BEC-SUBTLE-CLOSEOUT-019` | `SITE-TMX-019` now closes A with exact `TMX-18R` field-replacement coverage and leaves B with adjacent `TMX-18A` accessory-kit coverage. | `targeted_rescout_ready` |
| `BAL100-BEC-SUBTLE-CLOSEOUT-020` | `TERM-LME-020` now closes A before the `2026-06-12 16:00` queue and leaves B with a change entered before queue but effective in the next nightly cycle. | `targeted_rescout_ready` |

## Gate Checks

Both repaired families pass the targeted static gate:

- ALLOW sibling still closes the exact action boundary.
- ESCALATE sibling still has one narrow unresolved defect.
- The unresolved defect is subtle enough for targeted rescout, not a direct neon stop sign.
- Exactly one material delta remains per pair.
- No new secondary blocker was introduced.
- Sibling artifact structure still mirrors.
- No benchmark-credit mutation occurred.

`021` and `022` remain retired from this proof-credit path after the previous `kill_before_freeze` scout triage.

Proof-credit remains unchanged: 2 pair families / 4 packets, `BEC-PAIR-009` and `BEC-PAIR-010`.

Recommended next action: run a targeted no-Judge, no-freeze rescout for repaired Batch 003 families `019` and `020` only.
