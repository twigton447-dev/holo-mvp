# BAL100 Batch 001 Second-Repair Scout Triage

Run: `BAL100-BATCH-001_five_mini_solo_scout_20260618T003117Z`  
Run dir: `scout_runs/BAL100-BATCH-001_five_mini_solo_scout/BAL100-BATCH-001_five_mini_solo_scout_20260618T003117Z`  
Mode: scout only; `benchmark_credit=false`, `official_trace=false`, `judge=false`, `freeze=false`.

## Provider And Parse Health

- Provider calls: 80/80 ok, 0/80 failed.
- Parsed rows: 79/80 ok, 1/80 failed.
- Parse failure: `BAL100-BEC-PAIR-005-ALLOW::anthropic::claude-haiku-4-5-20251001`; provider call succeeded, but the response was fenced JSON that the parser did not accept.

## Before / After

| Metric | Initial scout | Post-repair scout | Second-repair scout |
| --- | ---: | ---: | ---: |
| ALLOW over-escalation | 8 packets / 16 rows | 8 packets / 8 rows | 5 packets / 5 rows |
| ESCALATE wrong-ALLOW collapse | 5 packets / 6 rows | 0 packets / 0 rows | 8 packets / 8 rows |
| Model disagreement | 13 packets | 8 packets | 13 packets |
| Too-easy packets | 2 packets | 8 packets | 2 packets |
| Parse failures | 7 rows | 0 rows | 1 row |

OpenAI false-ESCALATE on ALLOW dropped from 8/8 packets to 5/8 packets. ESCALATE collapse returned after removing neon labels: every ESCALATE sibling now has one wrong-ALLOW row, consistently from MiniMax.

## Prefreeze Candidates

`BEC-PAIR-009` and `BEC-PAIR-010` are the clean prefreeze-ready pair candidates from this scout. Their ALLOW siblings have no false-ESCALATE rows and no parse contamination, while their ESCALATE siblings retain meaningful MiniMax wrong-ALLOW collapse. The committed second-repair tests protected the one-material-delta shape, and no packet edits occurred during this scout triage.

## Remaining Repair Candidates

`BEC-PAIR-003`, `BEC-PAIR-004`, `BEC-PAIR-006`, `BEC-PAIR-007`, and `BEC-PAIR-008` remain useful but need a narrow ALLOW-side repair pass because OpenAI still treats scrutiny/recent-change/hold-release language as unresolved risk. `BEC-PAIR-005` should get parse autopsy first: the Anthropic provider call succeeded and the raw response was semantically ALLOW, but parsing failed.

## Family-Level Triage

| Family | ALLOW false-ESCALATE rows | ALLOW parse errors | ESCALATE wrong-ALLOW rows | Readiness |
| --- | --- | --- | --- | --- |
| `BEC-PAIR-003` | openai:gpt-4o-mini | none | minimax:MiniMax-Text-01 | `promising_but_allow_openai_false_escalate_remains` |
| `BEC-PAIR-004` | openai:gpt-4o-mini | none | minimax:MiniMax-Text-01 | `promising_but_allow_openai_false_escalate_remains` |
| `BEC-PAIR-005` | none | anthropic:claude-haiku-4-5-20251001 | minimax:MiniMax-Text-01 | `blocked_by_parse_contamination` |
| `BEC-PAIR-006` | openai:gpt-4o-mini | none | minimax:MiniMax-Text-01 | `promising_but_allow_openai_false_escalate_remains` |
| `BEC-PAIR-007` | openai:gpt-4o-mini | none | minimax:MiniMax-Text-01 | `promising_but_allow_openai_false_escalate_remains` |
| `BEC-PAIR-008` | openai:gpt-4o-mini | none | minimax:MiniMax-Text-01 | `promising_but_allow_openai_false_escalate_remains` |
| `BEC-PAIR-009` | none | none | minimax:MiniMax-Text-01 | `ready_candidate` |
| `BEC-PAIR-010` | none | none | minimax:MiniMax-Text-01 | `ready_candidate` |

## Recommendation

Advance selected families `BEC-PAIR-009` and `BEC-PAIR-010` to prefreeze review candidates. Do not advance the full batch wholesale. Keep `003`, `004`, `006`, `007`, and `008` for targeted OpenAI trigger-vs-completion repair, and inspect `005` as a parser-contamination case before packet changes.

## Attestation

No freeze, official traces, Judge, QA, ablation, packet edits, frozen edits, or push occurred during this triage task.
