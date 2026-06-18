# BAL100 Batch 003 Bounded Scout Triage

Status: diagnostic scout complete  
Batch: `BAL100-BATCH-003`  
Scout scope: families `019`, `020`, `021`, `022` only  
Run directory: `scout_runs/BAL100-BATCH-003_bounded_scout`  
Benchmark credit: `false`  
Official trace: `false`  
Judge / QA / ablation / freeze: not run

## Run Health

The bounded scout completed the expected 40 rows: 8 packets x 5 providers.

Provider roster:

- `openai:gpt-4o-mini`
- `anthropic:claude-haiku-4-5-20251001`
- `gemini:gemini-2.5-flash-lite`
- `xai:grok-3-mini`
- `minimax:MiniMax-Text-01`

Operational result:

- Rows attempted: 40
- Provider calls succeeded: 40
- Provider calls failed: 0
- Parse OK: 40
- Parse failed: 0
- Incomplete packets: 0

Proof-credit remains unchanged: 2 pair families / 4 packets, `BEC-PAIR-009` and `BEC-PAIR-010`.

## Family Results

| Family | ALLOW behavior | ESCALATE behavior | Primary failure mode | Triage |
| --- | --- | --- | --- | --- |
| `BAL100-BEC-SUBTLE-CLOSEOUT-019` | 4 ALLOW / 1 ESCALATE. OpenAI false-escalated. | 3 ESCALATE / 2 ALLOW. Useful disagreement preserved, not too easy. | Close, but ALLOW is not clean and two providers missed the ESCALATE risk. | `repair_once` |
| `BAL100-BEC-SUBTLE-CLOSEOUT-020` | 3 ALLOW / 2 ESCALATE. OpenAI and Gemini false-escalated. | 5 ESCALATE / 0 ALLOW. Unanimous and too obvious. | Timing seam is too neon on ESCALATE, while ALLOW timing closure is still ambiguous to two providers. | `repair_once` |
| `BAL100-BEC-SUBTLE-CLOSEOUT-021` | 1 ALLOW / 4 ESCALATE. ALLOW collapsed. | 5 ESCALATE / 0 ALLOW. Unanimous and too obvious. | Hold-class authority closure did not read as safe, and the sibling defect was obvious. | `kill_before_freeze` |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022` | 0 ALLOW / 5 ESCALATE. ALLOW fully collapsed. | 5 ESCALATE / 0 ALLOW. Unanimous and too obvious. | Lab-vs-production naming-prefix material contaminated the ALLOW sibling and made the ESCALATE sibling neon. | `kill_before_freeze` |

## Triage Counts

- `promote_to_prefreeze_review`: 0
- `repair_once`: 2
- `kill_before_freeze`: 2
- `quarantine`: 0

## Interpretation

Batch 003 did improve the operational side: no provider failures, no parse failures, and the bounded runner stayed inside the exact 8-packet scout scope. It did not produce a prefreeze-ready family.

`019` is the strongest repair candidate because its ESCALATE sibling preserved useful disagreement and its ALLOW sibling had only one false escalation. `020` is a weaker but still plausible one-repair candidate because it kept the single timing delta, but its ESCALATE sibling was unanimous. `021` and `022` should not be repaired in this lane: both had ALLOW collapse plus unanimous ESCALATE behavior.

Recommended next action: repair only `019` and possibly `020`; retire or reseed `021` and `022`. Do not claim proof-credit from Batch 003.
