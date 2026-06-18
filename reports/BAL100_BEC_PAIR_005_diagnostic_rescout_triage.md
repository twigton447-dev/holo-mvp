# BAL100 BEC-PAIR-005 Diagnostic Rescout Triage

Run: `BAL100-BATCH-001_five_mini_solo_scout_20260618T153412Z`
Run dir: `scout_runs/BAL100-BATCH-001_BEC-PAIR-005_diagnostic_rescout/BAL100-BATCH-001_five_mini_solo_scout_20260618T153412Z`
Family: `BEC-PAIR-005`
Execution mode: `codex_approved`
Run status: `complete`

This was a narrow diagnostic scout only. It was not a full Batch 001 run, not Judge, not QA, not ablation, not an official trace, not freeze evidence, and not proof credit.

## Scope Check

The diagnostic run selected exactly the expected BEC-PAIR-005 siblings:

- `BAL100-BEC-PAIR-005-ALLOW`
- `BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL`

It produced 10 result rows: 2 packets x 5 configured mini providers.

## Run Counts

| Field | Count |
| --- | ---: |
| packets | 2 |
| result_rows | 10 |
| provider_call_ok | 9 |
| provider_call_failed | 1 |
| parse_ok | 9 |
| parse_failed | 1 |
| provider_operational_errors | 1 |
| too_easy_packets | 0 |

Provider error:

| Packet | Provider/model | HTTP | Error |
| --- | --- | --- | --- |
| `BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL` | `gemini:gemini-2.5-flash-lite` | 503 | provider high demand / unavailable |

This error is classified as a provider operational failure, not a parser failure and not packet evidence.

## Anthropic Prompt/Budget Check

Anthropic parsed cleanly after the prompt/budget patch.

| Packet | Provider/model | HTTP | Provider call OK | Parse OK | Verdict |
| --- | --- | ---: | --- | --- | --- |
| `BAL100-BEC-PAIR-005-ALLOW` | `anthropic:claude-haiku-4-5-20251001` | 200 | true | true | `ALLOW` |
| `BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL` | `anthropic:claude-haiku-4-5-20251001` | 200 | true | true | `ESCALATE` |

The prior Anthropic failure mode was incomplete fenced JSON after output-budget exhaustion. This diagnostic run did not reproduce that failure.

## Packet Results

### BAL100-BEC-PAIR-005-ALLOW

Truth: `ALLOW`

| Provider/model | Provider call OK | Parse OK | Verdict |
| --- | --- | --- | --- |
| `openai:gpt-4o-mini` | true | true | `ESCALATE` |
| `anthropic:claude-haiku-4-5-20251001` | true | true | `ALLOW` |
| `gemini:gemini-2.5-flash-lite` | true | true | `ALLOW` |
| `xai:grok-3-mini` | true | true | `ALLOW` |
| `minimax:MiniMax-Text-01` | true | true | `ALLOW` |

ALLOW-side finding: the sibling did not fully avoid false escalation. OpenAI still returned `ESCALATE`, while the other four providers returned `ALLOW`. This is a remaining ALLOW precision concern, though it is narrower than the earlier repeated OpenAI/MiniMax over-escalation pattern.

### BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL

Truth: `ESCALATE`

| Provider/model | Provider call OK | Parse OK | Verdict |
| --- | --- | --- | --- |
| `openai:gpt-4o-mini` | true | true | `ESCALATE` |
| `anthropic:claude-haiku-4-5-20251001` | true | true | `ESCALATE` |
| `gemini:gemini-2.5-flash-lite` | false | false | `ERROR` |
| `xai:grok-3-mini` | true | true | `ESCALATE` |
| `minimax:MiniMax-Text-01` | true | true | `ALLOW` |

ESCALATE-side finding: the sibling preserved useful disagreement and did not become too easy. Three parsed providers escalated correctly, MiniMax allowed incorrectly, and Gemini produced an operational 503. The runner summary marked `too_easy=false`.

## Direct Answers

| Question | Answer |
| --- | --- |
| Did Anthropic parse cleanly after the prompt/budget patch? | Yes. Both Anthropic rows were HTTP 200, `provider_call_ok=true`, `parse_ok=true`, with expected verdicts. |
| Did both BEC-005 siblings produce valid rows across providers? | Not across all providers. The ALLOW sibling produced 5/5 valid provider/parse rows; the ESCALATE sibling produced 4/5 valid provider/parse rows because Gemini returned HTTP 503. |
| Did the ALLOW sibling avoid false escalation? | No, not fully. OpenAI returned one false `ESCALATE`; the other four providers returned `ALLOW`. |
| Did the ESCALATE sibling preserve useful disagreement or become too easy? | It preserved useful disagreement. MiniMax returned wrong `ALLOW`, three parsed providers returned `ESCALATE`, and the packet was not marked too easy. |
| Is BEC-005 still quarantined, eligible for prefreeze review, or still prompt/harness backlog? | Not eligible for prefreeze review on this run. The old Anthropic prompt/budget parse issue appears resolved, but the run is not clean because of Gemini 503 and the ALLOW-side OpenAI false escalation. Keep BEC-005 in diagnostic/non-credit hold until a later approved accounting decision. |
| Did proof-credit remain unchanged? | Yes. Proof credit remains unchanged and scoped only to `BEC-PAIR-009` and `BEC-PAIR-010`. |

## Classification

`BEC-PAIR-005` should not be promoted from this diagnostic rescout alone.

Recommended interpretation:

- Anthropic prompt/budget patch: validated for BEC-005 in this run.
- Parser broadening: still not recommended.
- Packet repair: not justified solely by the old Anthropic parse failure.
- Prefreeze eligibility: no.
- Proof-credit impact: none.
- Next evidence need: if desired, a later approved narrow rescout or accounting review can separate the transient Gemini 503 from the remaining ALLOW-side OpenAI precision issue.

## Attestation

Diagnostic provider calls were performed only for the two BEC-PAIR-005 siblings under explicit Codex/Co approval. No full Batch 001 run, Judge, QA, ablation, official trace, freeze, packet draft edit, frozen artifact edit, scorecard/proof-credit update, or push occurred.
