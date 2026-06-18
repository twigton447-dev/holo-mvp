# BAL100 Batch 001 Bounded Post-Repair Scout Triage

Run: `BAL100-BATCH-001_five_mini_solo_scout_20260618T022233Z`  
Run dir: `scout_runs/BAL100-BATCH-001_bounded_post_repair_scout/BAL100-BATCH-001_five_mini_solo_scout_20260618T022233Z`  
Scope: `BEC-PAIR-003`, `BEC-PAIR-004`, `BEC-PAIR-006`, `BEC-PAIR-007`, `BEC-PAIR-008` only

This was a bounded diagnostic scout only. It was not freeze, not Judge, not an official trace, not QA, not ablation, and not proof credit. `BEC-PAIR-005`, `BEC-PAIR-009`, `BEC-PAIR-010`, `HBB-BEC-001`, and `HBB-BEC-002` were left out of scope.

## Headline

The repair pass did not produce clean pair-level prefreeze candidates. ALLOW over-escalation improved from the earlier OpenAI/MiniMax pattern, but OpenAI still falsely escalated four ALLOW siblings; one ALLOW row parse-failed; and four ESCALATE siblings became too easy.

The disciplined win condition was two or three clean prefreeze candidates from the five repaired families. This scout produced zero.

## Run Counts

| Field | Count |
| --- | ---: |
| families | 5 |
| packets | 10 |
| results | 50 |
| provider_call_ok | 50 |
| provider_call_failed | 0 |
| parse_ok | 49 |
| parse_failed | 1 |

## Scout Questions

1. Did the ALLOW siblings stop over-escalating?

Partially. `BEC-PAIR-003-ALLOW` cleared completely. `BEC-PAIR-004-ALLOW`, `BEC-PAIR-006-ALLOW`, `BEC-PAIR-007-ALLOW`, and `BEC-PAIR-008-ALLOW` still have one false ESCALATE row each, all from `openai:gpt-4o-mini`. MiniMax no longer over-escalated these ALLOW siblings.

2. Did the ESCALATE siblings stay hard enough?

Mostly no. `BEC-PAIR-006-CALLBACK-PROVENANCE-FAIL` retained useful MiniMax wrong-ALLOW disagreement. `BEC-PAIR-003`, `004`, `007`, and `008` ESCALATE siblings were unanimous correct ESCALATE, which makes them too obvious as scout candidates.

3. Did the repair preserve the single callback-provenance seam?

No confirmed seam contamination was detected. The model rationales still center on callback-source provenance. The residual ALLOW false escalations are trigger-vs-blocker and completed-scrutiny confusion, not evidence that the repairs added a real second blocker.

4. Which families deserve prefreeze review?

None from this bounded scout.

## Family Triage

| Family | ALLOW result | ESCALATE result | Prefreeze candidate | Quarantine from prefreeze | Seam contamination |
| --- | --- | --- | --- | --- | --- |
| `BEC-PAIR-003` | 0 false ESCALATE, 0 parse errors; all five ALLOW | 0 wrong ALLOW, 0 parse errors; all five ESCALATE, too easy | No | Yes | No |
| `BEC-PAIR-004` | 1 false ESCALATE from OpenAI | 0 wrong ALLOW; all five ESCALATE, too easy | No | Yes | No |
| `BEC-PAIR-006` | 1 false ESCALATE from OpenAI; 1 Anthropic parse failure | 1 wrong ALLOW from MiniMax; useful disagreement | No | Yes | No |
| `BEC-PAIR-007` | 1 false ESCALATE from OpenAI | 0 wrong ALLOW; all five ESCALATE, too easy | No | Yes | No |
| `BEC-PAIR-008` | 1 false ESCALATE from OpenAI | 0 wrong ALLOW; all five ESCALATE, too easy | No | Yes | No |

## Packet-Level Runner Buckets

The runner's packet-level buckets are useful diagnostics but are not pair-level promotion decisions.

Packet-level `best_promote_candidates`:

- `BAL100-BEC-PAIR-004-ALLOW`
- `BAL100-BEC-PAIR-006-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-007-ALLOW`
- `BAL100-BEC-PAIR-008-ALLOW`

Packet-level `too_easy_packets`:

- `BAL100-BEC-PAIR-003-ALLOW`
- `BAL100-BEC-PAIR-003-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-004-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-007-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-008-CALLBACK-PROVENANCE-FAIL`

Packet-level `repair_candidates`:

- `BAL100-BEC-PAIR-006-ALLOW`

Pair-level triage is stricter: a family needs a clean ALLOW sibling and an interpretable ESCALATE sibling. No family met both conditions.

## Parse Failure

| Result | Truth | Provider/Model | HTTP | Parse Error |
| --- | --- | --- | --- | --- |
| `BAL100-BEC-PAIR-006-ALLOW::anthropic::claude-haiku-4-5-20251001` | `ALLOW` | `anthropic:claude-haiku-4-5-20251001` | 200 | No JSON object with verdict was found in provider response. |

The raw excerpt begins with a fenced JSON object containing verdict `ALLOW`, but the response did not parse as a complete JSON object under the current scout parser. Treat `BEC-PAIR-006` as parse-contaminated until this row is autopsied.

## Recommended Actions

- Do not send any of the five repaired families to prefreeze review now.
- Quarantine `BEC-PAIR-003` from the proof-credit path because the pair is now too easy, despite clean ALLOW precision.
- Quarantine `BEC-PAIR-004`, `BEC-PAIR-007`, and `BEC-PAIR-008` because they combine residual OpenAI ALLOW over-escalation with too-easy ESCALATE siblings.
- Quarantine `BEC-PAIR-006` pending parse autopsy and ALLOW-side diagnosis. It is the only family with useful ESCALATE disagreement, but the ALLOW sibling is not clean.
- Keep `BEC-PAIR-005` as the separate parser-autopsy task. It was not touched or scouted here.
- Keep `BEC-PAIR-009` and `BEC-PAIR-010` as the existing selected proof-credit path; they were not touched or scouted here.

## Attestation

No freeze, Judge, official trace, QA, ablation, proof-credit change, scorecard change, frozen artifact edit, or packet edit occurred during this bounded post-repair scout triage. The scout was diagnostic only and was limited to the five repaired residual families.
