# BAL100 Batch 001 Five-Mini Scout Triage

Run: `BAL100-BATCH-001_five_mini_solo_scout_20260617T231819Z`  
Run dir: `scout_runs/BAL100-BATCH-001_five_mini_solo_scout/BAL100-BATCH-001_five_mini_solo_scout_20260617T231819Z`  
Run status: `complete`

BAL100 Batch 001 scout found useful ESCALATE collapse, but ALLOW siblings are too easy to over-escalate or insufficiently closed. Next action should be ALLOW-side repair before prefreeze review, while preserving the strongest ESCALATE collapse candidates.

This is scout triage only. It is not benchmark proof, not an official trace, not Judge, and not freeze evidence.

## Run Counts

| Field | Count |
| --- | ---: |
| total_packets | 16 |
| total_results | 80 |
| provider_call_ok | 80 |
| provider_call_failed | 0 |
| parse_ok | 73 |
| parse_failed | 7 |
| model_disagreement_packets | 13 |

## ALLOW Over-Escalation Table

| Packet | Wrong ESCALATE | Parsed | Parse Errors | Wrong Models | Correct Models |
| --- | --- | --- | --- | --- | --- |
| `BAL100-BEC-PAIR-003-ALLOW` | 2 | 5 | 0 | `minimax:MiniMax-Text-01`<br>`openai:gpt-4o-mini` | `anthropic:claude-haiku-4-5-20251001`<br>`gemini:gemini-2.5-flash-lite`<br>`xai:grok-3-mini` |
| `BAL100-BEC-PAIR-004-ALLOW` | 2 | 4 | 1 | `minimax:MiniMax-Text-01`<br>`openai:gpt-4o-mini` | `gemini:gemini-2.5-flash-lite`<br>`xai:grok-3-mini` |
| `BAL100-BEC-PAIR-005-ALLOW` | 2 | 5 | 0 | `minimax:MiniMax-Text-01`<br>`openai:gpt-4o-mini` | `anthropic:claude-haiku-4-5-20251001`<br>`gemini:gemini-2.5-flash-lite`<br>`xai:grok-3-mini` |
| `BAL100-BEC-PAIR-006-ALLOW` | 2 | 4 | 1 | `minimax:MiniMax-Text-01`<br>`openai:gpt-4o-mini` | `gemini:gemini-2.5-flash-lite`<br>`xai:grok-3-mini` |
| `BAL100-BEC-PAIR-007-ALLOW` | 2 | 4 | 1 | `minimax:MiniMax-Text-01`<br>`openai:gpt-4o-mini` | `gemini:gemini-2.5-flash-lite`<br>`xai:grok-3-mini` |
| `BAL100-BEC-PAIR-008-ALLOW` | 2 | 4 | 1 | `minimax:MiniMax-Text-01`<br>`openai:gpt-4o-mini` | `gemini:gemini-2.5-flash-lite`<br>`xai:grok-3-mini` |
| `BAL100-BEC-PAIR-009-ALLOW` | 2 | 5 | 0 | `minimax:MiniMax-Text-01`<br>`openai:gpt-4o-mini` | `anthropic:claude-haiku-4-5-20251001`<br>`gemini:gemini-2.5-flash-lite`<br>`xai:grok-3-mini` |
| `BAL100-BEC-PAIR-010-ALLOW` | 2 | 5 | 0 | `minimax:MiniMax-Text-01`<br>`openai:gpt-4o-mini` | `anthropic:claude-haiku-4-5-20251001`<br>`gemini:gemini-2.5-flash-lite`<br>`xai:grok-3-mini` |

Interpretation: every ALLOW sibling was over-escalated by two parsed models. The repeated pattern is OpenAI and MiniMax treating compliant pre-change vendor-master callback provenance as if it were newly supplied or change-request provenance.

## ESCALATE Wrong-ALLOW Table

| Packet | Wrong ALLOW | Parsed | Parse Errors | Wrong Models | Correct Models |
| --- | --- | --- | --- | --- | --- |
| `BAL100-BEC-PAIR-003-CALLBACK-PROVENANCE-FAIL` | 1 | 5 | 0 | `gemini:gemini-2.5-flash-lite` | `anthropic:claude-haiku-4-5-20251001`<br>`minimax:MiniMax-Text-01`<br>`openai:gpt-4o-mini`<br>`xai:grok-3-mini` |
| `BAL100-BEC-PAIR-004-CALLBACK-PROVENANCE-FAIL` | 1 | 4 | 1 | `gemini:gemini-2.5-flash-lite` | `minimax:MiniMax-Text-01`<br>`openai:gpt-4o-mini`<br>`xai:grok-3-mini` |
| `BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL` | 1 | 5 | 0 | `gemini:gemini-2.5-flash-lite` | `anthropic:claude-haiku-4-5-20251001`<br>`minimax:MiniMax-Text-01`<br>`openai:gpt-4o-mini`<br>`xai:grok-3-mini` |
| `BAL100-BEC-PAIR-008-CALLBACK-PROVENANCE-FAIL` | 2 | 5 | 0 | `anthropic:claude-haiku-4-5-20251001`<br>`gemini:gemini-2.5-flash-lite` | `minimax:MiniMax-Text-01`<br>`openai:gpt-4o-mini`<br>`xai:grok-3-mini` |
| `BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL` | 1 | 4 | 1 | `anthropic:claude-haiku-4-5-20251001` | `minimax:MiniMax-Text-01`<br>`openai:gpt-4o-mini`<br>`xai:grok-3-mini` |

Interpretation: the ESCALATE side produced useful collapse. Pairs 003 and 005 are the cleanest promote candidates because they have one wrong-ALLOW model with no parse failures and four parsed correct escalations.

## Model Disagreement Table

| Packet | Truth | Wrong ALLOW | Wrong ESCALATE | Parse Errors |
| --- | --- | --- | --- | --- |
| `BAL100-BEC-PAIR-003-ALLOW` | `ALLOW` | 0 | 2 | 0 |
| `BAL100-BEC-PAIR-003-CALLBACK-PROVENANCE-FAIL` | `ESCALATE` | 1 | 0 | 0 |
| `BAL100-BEC-PAIR-004-ALLOW` | `ALLOW` | 0 | 2 | 1 |
| `BAL100-BEC-PAIR-004-CALLBACK-PROVENANCE-FAIL` | `ESCALATE` | 1 | 0 | 1 |
| `BAL100-BEC-PAIR-005-ALLOW` | `ALLOW` | 0 | 2 | 0 |
| `BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL` | `ESCALATE` | 1 | 0 | 0 |
| `BAL100-BEC-PAIR-006-ALLOW` | `ALLOW` | 0 | 2 | 1 |
| `BAL100-BEC-PAIR-007-ALLOW` | `ALLOW` | 0 | 2 | 1 |
| `BAL100-BEC-PAIR-008-ALLOW` | `ALLOW` | 0 | 2 | 1 |
| `BAL100-BEC-PAIR-008-CALLBACK-PROVENANCE-FAIL` | `ESCALATE` | 2 | 0 | 0 |
| `BAL100-BEC-PAIR-009-ALLOW` | `ALLOW` | 0 | 2 | 0 |
| `BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL` | `ESCALATE` | 1 | 0 | 1 |
| `BAL100-BEC-PAIR-010-ALLOW` | `ALLOW` | 0 | 2 | 0 |

## Parse Failure Summary

All failures were parse/format failures after successful provider calls; none were transport/provider-call failures.

| Model | Parse failures |
| --- | ---: |
| `anthropic:claude-haiku-4-5-20251001` | 5 |
| `gemini:gemini-2.5-flash-lite` | 2 |

| Result | Truth | Provider/Model | HTTP | Parse Error |
| --- | --- | --- | --- | --- |
| `BAL100-BEC-PAIR-004-ALLOW::anthropic::claude-haiku-4-5-20251001` | `ALLOW` | `anthropic:claude-haiku-4-5-20251001` | 200 | No JSON object with verdict was found in provider response. |
| `BAL100-BEC-PAIR-004-CALLBACK-PROVENANCE-FAIL::anthropic::claude-haiku-4-5-20251001` | `ESCALATE` | `anthropic:claude-haiku-4-5-20251001` | 200 | No JSON object with verdict was found in provider response. |
| `BAL100-BEC-PAIR-006-ALLOW::anthropic::claude-haiku-4-5-20251001` | `ALLOW` | `anthropic:claude-haiku-4-5-20251001` | 200 | No JSON object with verdict was found in provider response. |
| `BAL100-BEC-PAIR-006-CALLBACK-PROVENANCE-FAIL::gemini::gemini-2.5-flash-lite` | `ESCALATE` | `gemini:gemini-2.5-flash-lite` | 200 | No JSON object with verdict was found in provider response. |
| `BAL100-BEC-PAIR-007-ALLOW::anthropic::claude-haiku-4-5-20251001` | `ALLOW` | `anthropic:claude-haiku-4-5-20251001` | 200 | No JSON object with verdict was found in provider response. |
| `BAL100-BEC-PAIR-008-ALLOW::anthropic::claude-haiku-4-5-20251001` | `ALLOW` | `anthropic:claude-haiku-4-5-20251001` | 200 | No JSON object with verdict was found in provider response. |
| `BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL::gemini::gemini-2.5-flash-lite` | `ESCALATE` | `gemini:gemini-2.5-flash-lite` | 200 | No JSON object with verdict was found in provider response. |

Parse failures are not counted as ALLOW or ESCALATE verdicts in this triage, even where the raw excerpt appears to contain a verdict string.

## Candidate Buckets

Best promote candidates:

- `BAL100-BEC-PAIR-003-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL`

Repair candidates:

- `BAL100-BEC-PAIR-003-ALLOW`
- `BAL100-BEC-PAIR-004-ALLOW`
- `BAL100-BEC-PAIR-004-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-005-ALLOW`
- `BAL100-BEC-PAIR-006-ALLOW`
- `BAL100-BEC-PAIR-006-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-007-ALLOW`
- `BAL100-BEC-PAIR-008-ALLOW`
- `BAL100-BEC-PAIR-008-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-009-ALLOW`
- `BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-010-ALLOW`

Too easy packets:

- `BAL100-BEC-PAIR-007-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL`

Discard candidates: none.

## Recommended Action By Family

| Family | ALLOW over-escalates | ESCALATE wrong-ALLOW | ESCALATE parse errors | ESCALATE too easy | Recommendation |
| --- | --- | --- | --- | --- | --- |
| `BAL100-BEC-PAIR-003` | 2 | 1 | 0 | False | Preserve ESCALATE sibling as a strong promote candidate; repair ALLOW sibling because OpenAI and MiniMax over-escalated compliant pre-change vendor-master callback provenance. |
| `BAL100-BEC-PAIR-004` | 2 | 1 | 1 | False | Repair both siblings. ALLOW is over-escalated by OpenAI and MiniMax with one Anthropic parse failure; ESCALATE has a Gemini wrong-ALLOW plus one Anthropic parse failure. |
| `BAL100-BEC-PAIR-005` | 2 | 1 | 0 | False | Preserve ESCALATE sibling as a strong promote candidate; repair ALLOW sibling for the repeated OpenAI/MiniMax over-escalation pattern. |
| `BAL100-BEC-PAIR-006` | 2 | 0 | 1 | False | Repair ALLOW sibling; review ESCALATE sibling because the only collapse signal there is a Gemini parse failure, not a counted wrong-ALLOW verdict. |
| `BAL100-BEC-PAIR-007` | 2 | 0 | 0 | True | Repair ALLOW sibling; treat ESCALATE sibling as too easy for promotion because all parsed models escalated correctly with no disagreement. |
| `BAL100-BEC-PAIR-008` | 2 | 2 | 0 | False | Repair both siblings. ALLOW over-escalated by OpenAI and MiniMax; ESCALATE has two wrong-ALLOW rows from Anthropic and Gemini. |
| `BAL100-BEC-PAIR-009` | 2 | 1 | 1 | False | Repair both siblings. ALLOW over-escalated by OpenAI and MiniMax; ESCALATE has one Anthropic wrong-ALLOW and one Gemini parse failure. |
| `BAL100-BEC-PAIR-010` | 2 | 0 | 0 | True | Repair ALLOW sibling; treat ESCALATE sibling as too easy for promotion because all parsed models escalated correctly with no disagreement. |

## Recommended Next Batch Action

- Do not freeze Batch 001 yet.
- Repair all ALLOW siblings so compliant pre-change vendor-master callback provenance is harder to misread as a newly supplied or change-request callback source.
- Preserve BAL100-BEC-PAIR-003-CALLBACK-PROVENANCE-FAIL and BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL as the strongest ESCALATE-side promote candidates after ALLOW-side repair.
- Repair or replace ESCALATE siblings 004, 006, 008, and 009 before prefreeze review because their collapse signal is either too weak, parse-contaminated, or too often wrongly allowed.
- Treat ESCALATE siblings 007 and 010 as too easy for promotion unless strengthened into higher-disagreement variants.
- After packet repair only, rerun scout only with explicit approval; do not count this scout as benchmark proof.

## Attestation

No live calls, scout rerun, freeze, official traces, Judge, QA, ablation, draft packet edits, frozen artifact edits, source packet edits, or push occurred during this triage task.
