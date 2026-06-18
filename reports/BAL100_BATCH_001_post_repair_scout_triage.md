# BAL100 Batch 001 Post-Repair Scout Triage

Post-repair run: `BAL100-BATCH-001_five_mini_solo_scout_20260617T235736Z`  
Run dir: `scout_runs/BAL100-BATCH-001_five_mini_solo_scout/BAL100-BATCH-001_five_mini_solo_scout_20260617T235736Z`  
Run status: `complete`

This is scout triage only: `benchmark_credit=false`, `official_trace=false`, `judge=false`, `freeze=false`.

## Run Counts

| Field | Count |
| --- | ---: |
| provider_call_ok | 80 |
| provider_call_failed | 0 |
| parse_ok | 80 |
| parse_failed | 0 |
| total_results | 80 |

## Before / After

| Metric | Before | After |
| --- | ---: | ---: |
| ALLOW over-escalation packets | 8 | 8 |
| ALLOW false ESCALATE model rows | 16 | 8 |
| ESCALATE wrong-ALLOW packets | 5 | 0 |
| ESCALATE wrong-ALLOW model rows | 6 | 0 |
| model disagreement packets | 13 | 8 |
| too-easy packets | 2 | 8 |
| parse failures | 7 | 0 |

## Specific Answers

Did ALLOW over-escalation drop from 8 packets / 16 model rows?  
Yes by row count, no by packet count. It moved from `8 packets / 16 rows` to `8 packets / 8 rows`; OpenAI still over-escalated every ALLOW sibling.

Did ESCALATE 003 and 005 remain useful collapse candidates?  
No. Both became all-correct ESCALATE packets with zero wrong-ALLOW rows, so they are clean but too easy.

Did ESCALATE 007 and 010 become less too-easy?  
No. They remained too easy, and all ESCALATE siblings are now too easy.

Are any pairs suitable for prefreeze review?  
No. Every ALLOW sibling still has one false ESCALATE row, and every ESCALATE sibling is too easy/all-correct.

## Promote Candidates

Runner best_promote_candidates:

- `BAL100-BEC-PAIR-003-ALLOW`
- `BAL100-BEC-PAIR-004-ALLOW`
- `BAL100-BEC-PAIR-005-ALLOW`
- `BAL100-BEC-PAIR-006-ALLOW`
- `BAL100-BEC-PAIR-007-ALLOW`
- `BAL100-BEC-PAIR-008-ALLOW`
- `BAL100-BEC-PAIR-009-ALLOW`
- `BAL100-BEC-PAIR-010-ALLOW`

Prefreeze-suitable sibling pairs:

- none

Interpretation: the runner bucket reflects ALLOW-side improvement, not balanced prefreeze-ready sibling pairs.

## Remaining Repair Candidates

- `BAL100-BEC-PAIR-003-ALLOW`
- `BAL100-BEC-PAIR-003-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-004-ALLOW`
- `BAL100-BEC-PAIR-004-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-005-ALLOW`
- `BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-006-ALLOW`
- `BAL100-BEC-PAIR-006-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-007-ALLOW`
- `BAL100-BEC-PAIR-007-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-008-ALLOW`
- `BAL100-BEC-PAIR-008-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-009-ALLOW`
- `BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-010-ALLOW`
- `BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL`

## Too-Easy Packets After Repair

- `BAL100-BEC-PAIR-003-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-004-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-006-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-007-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-008-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL`

## Discard Candidates

- none

## Recommendation

Status: `needs_another_repair_pass`  
Prefreeze-ready: `false`

Repairs improved parse reliability and reduced ALLOW false-escalation model rows, but Batch 001 still needs another repair pass before prefreeze review. The next pass should reduce the remaining OpenAI ALLOW false ESCALATE behavior and reintroduce useful ESCALATE-side collapse without adding second blockers.

Next repair focus:

- Reduce remaining OpenAI false ESCALATE on every ALLOW sibling without removing scary trigger conditions.
- Reintroduce useful ESCALATE-side collapse by making callback-source defects subtler while preserving one material blocker only.
- Do not freeze Batch 001 or move any pair to prefreeze until at least some sibling pairs show ALLOW precision plus non-trivial ESCALATE disagreement.

## Attestation

No freeze, official traces, Judge, QA, ablation, packet edits after scout, frozen artifact edits, or push occurred during this post-repair triage task.
