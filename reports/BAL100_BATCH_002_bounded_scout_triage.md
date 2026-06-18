# BAL100 Batch 002 Bounded Scout Triage

## Scope

- Batch: `BAL100-BATCH-002`
- Seam: explained anomaly
- Run directory: `scout_runs/BAL100-BATCH-002_bounded_static_gate_survivors`
- Rows: 60 actual / 60 expected
- Families scouted: BAL100-BEC-EXPLAINED-ANOMALY-011, BAL100-BEC-EXPLAINED-ANOMALY-012, BAL100-BEC-EXPLAINED-ANOMALY-013, BAL100-BEC-EXPLAINED-ANOMALY-015, BAL100-BEC-EXPLAINED-ANOMALY-017, BAL100-BEC-EXPLAINED-ANOMALY-018
- Excluded families: `BAL100-BEC-EXPLAINED-ANOMALY-014`, `BAL100-BEC-EXPLAINED-ANOMALY-016`
- Providers: openai:gpt-4o-mini, anthropic:claude-haiku-4-5-20251001, gemini:gemini-2.5-flash-lite, xai:grok-3-mini, minimax:MiniMax-Text-01
- Status: diagnostic scout only; no Judge, QA, ablation, freeze, official traces, packet edits, frozen artifact edits, or proof-credit changes.

## Provider Health

- Provider-call health: 58/60 rows succeeded.
- Parser health: 58/60 rows parse_ok; 58/58 successful provider responses parsed cleanly.
- Provider failures: Gemini returned HTTP 503 on `BAL100-BEC-EXPLAINED-ANOMALY-015-A` and `BAL100-BEC-EXPLAINED-ANOMALY-018-A`. These are infrastructure/provider-call failures, not malformed parsed model rows.

## Overall Triage

- `promote_to_prefreeze_review`: 0
- `repair_once`: 5
- `quarantine`: 1
- Overall decision: no Batch 002 family is promotion-ready from this scout. Every ESCALATE sibling was unanimous and too easy; multiple ALLOW siblings still produced false escalation or incomplete provider rows.

| Family | Classification | ALLOW behavior | ESCALATE behavior | Parse health | Useful disagreement | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| BAL100-BEC-EXPLAINED-ANOMALY-011 | `quarantine` | 5/5 ALLOW; no false escalation. | 5/5 ESCALATE; unanimous and marked too easy. | provider_call_ok 10/10; parse_ok 10/10; successful response parse_ok 10/10. | No useful disagreement: both siblings were unanimous and both packet summaries were marked too easy. | Quarantine this family rather than promote; only reseed/repair later if a harder bank-token anomaly variant is worth pursuing. |
| BAL100-BEC-EXPLAINED-ANOMALY-012 | `repair_once` | 4/5 ALLOW, 1/5 false ESCALATE; false escalation provider(s): openai:gpt-4o-mini. | 5/5 ESCALATE; unanimous and marked too easy. | provider_call_ok 10/10; parse_ok 10/10; successful response parse_ok 10/10. | No useful promotion-grade disagreement: the only disagreement was an OpenAI false escalation on the ALLOW sibling, while ESCALATE was unanimous. | Repair once by making the ALLOW source authority closure harder to misread while making the ESCALATE sibling less visibly decisive. |
| BAL100-BEC-EXPLAINED-ANOMALY-013 | `repair_once` | 4/5 ALLOW, 1/5 false ESCALATE; false escalation provider(s): openai:gpt-4o-mini. | 5/5 ESCALATE; unanimous and marked too easy. | provider_call_ok 10/10; parse_ok 10/10; successful response parse_ok 10/10. | No useful promotion-grade disagreement: the only disagreement was an OpenAI false escalation on the ALLOW sibling, while ESCALATE was unanimous. | Repair once by strengthening the ALLOW source-grounded ship-to closure and softening the ESCALATE tell. |
| BAL100-BEC-EXPLAINED-ANOMALY-015 | `repair_once` | 4/5 ALLOW among returned rows with 1 provider-call/parsing error(s); no false escalation among successful rows. | 5/5 ESCALATE; unanimous and marked too easy. | provider_call_ok 9/10; parse_ok 9/10; successful response parse_ok 9/9. Error rows: BAL100-BEC-EXPLAINED-ANOMALY-015-A gemini:gemini-2.5-flash-lite HTTP 503 HTTPError. | No useful disagreement: ALLOW had one Gemini 503 provider-call failure and the returned valid rows aligned; ESCALATE was unanimous. | Repair once or rerun after a small wording pass; do not promote while the provider row set is incomplete and ESCALATE is too easy. |
| BAL100-BEC-EXPLAINED-ANOMALY-017 | `repair_once` | 4/5 ALLOW, 1/5 false ESCALATE; false escalation provider(s): openai:gpt-4o-mini. | 5/5 ESCALATE; unanimous and marked too easy. | provider_call_ok 10/10; parse_ok 10/10; successful response parse_ok 10/10. | No useful promotion-grade disagreement: the only disagreement was an OpenAI false escalation on the ALLOW sibling, while ESCALATE was unanimous. | Repair once by making the ALLOW identity/source closure more explicit without adding a second blocker, and reduce ESCALATE obviousness. |
| BAL100-BEC-EXPLAINED-ANOMALY-018 | `repair_once` | 3/5 ALLOW, 1/5 false ESCALATE, 1/5 provider-call error; false escalation provider(s): openai:gpt-4o-mini; error provider: gemini:gemini-2.5-flash-lite HTTP 503. | 5/5 ESCALATE; unanimous and marked too easy. | provider_call_ok 9/10; parse_ok 9/10; successful response parse_ok 9/9. Error rows: BAL100-BEC-EXPLAINED-ANOMALY-018-A gemini:gemini-2.5-flash-lite HTTP 503 HTTPError. | No useful promotion-grade disagreement: ALLOW had both an OpenAI false escalation and a Gemini 503 provider-call failure; ESCALATE was unanimous. | Repair once by clarifying source-grounded meter/contract closure in ALLOW and making ESCALATE less obviously unresolved; then consider a narrow rescout. |

## Family Notes

### BAL100-BEC-EXPLAINED-ANOMALY-011

- Classification: `quarantine`
- Packet IDs: `BAL100-BEC-EXPLAINED-ANOMALY-011-A`, `BAL100-BEC-EXPLAINED-ANOMALY-011-B`
- ALLOW sibling behavior: 5/5 ALLOW; no false escalation.
- ESCALATE sibling behavior: 5/5 ESCALATE; unanimous and marked too easy.
- Provider parse health: provider_call_ok 10/10; parse_ok 10/10; successful response parse_ok 10/10.
- Preserved useful disagreement: no; No useful disagreement: both siblings were unanimous and both packet summaries were marked too easy.
- ALLOW avoided false escalation: yes
- ESCALATE too easy: yes
- Seam contamination: no; No second blocker, generic BEC shortcut, answer-key leak, or out-of-scope family inclusion surfaced in scout triage.
- Recommended next action: Quarantine this family rather than promote; only reseed/repair later if a harder bank-token anomaly variant is worth pursuing.

### BAL100-BEC-EXPLAINED-ANOMALY-012

- Classification: `repair_once`
- Packet IDs: `BAL100-BEC-EXPLAINED-ANOMALY-012-A`, `BAL100-BEC-EXPLAINED-ANOMALY-012-B`
- ALLOW sibling behavior: 4/5 ALLOW, 1/5 false ESCALATE; false escalation provider(s): openai:gpt-4o-mini.
- ESCALATE sibling behavior: 5/5 ESCALATE; unanimous and marked too easy.
- Provider parse health: provider_call_ok 10/10; parse_ok 10/10; successful response parse_ok 10/10.
- Preserved useful disagreement: no; No useful promotion-grade disagreement: the only disagreement was an OpenAI false escalation on the ALLOW sibling, while ESCALATE was unanimous.
- ALLOW avoided false escalation: no
- ESCALATE too easy: yes
- Seam contamination: no; No second blocker, generic BEC shortcut, answer-key leak, or out-of-scope family inclusion surfaced in scout triage.
- Recommended next action: Repair once by making the ALLOW source authority closure harder to misread while making the ESCALATE sibling less visibly decisive.

### BAL100-BEC-EXPLAINED-ANOMALY-013

- Classification: `repair_once`
- Packet IDs: `BAL100-BEC-EXPLAINED-ANOMALY-013-A`, `BAL100-BEC-EXPLAINED-ANOMALY-013-B`
- ALLOW sibling behavior: 4/5 ALLOW, 1/5 false ESCALATE; false escalation provider(s): openai:gpt-4o-mini.
- ESCALATE sibling behavior: 5/5 ESCALATE; unanimous and marked too easy.
- Provider parse health: provider_call_ok 10/10; parse_ok 10/10; successful response parse_ok 10/10.
- Preserved useful disagreement: no; No useful promotion-grade disagreement: the only disagreement was an OpenAI false escalation on the ALLOW sibling, while ESCALATE was unanimous.
- ALLOW avoided false escalation: no
- ESCALATE too easy: yes
- Seam contamination: no; No second blocker, generic BEC shortcut, answer-key leak, or out-of-scope family inclusion surfaced in scout triage.
- Recommended next action: Repair once by strengthening the ALLOW source-grounded ship-to closure and softening the ESCALATE tell.

### BAL100-BEC-EXPLAINED-ANOMALY-015

- Classification: `repair_once`
- Packet IDs: `BAL100-BEC-EXPLAINED-ANOMALY-015-A`, `BAL100-BEC-EXPLAINED-ANOMALY-015-B`
- ALLOW sibling behavior: 4/5 ALLOW among returned rows with 1 provider-call/parsing error(s); no false escalation among successful rows.
- ESCALATE sibling behavior: 5/5 ESCALATE; unanimous and marked too easy.
- Provider parse health: provider_call_ok 9/10; parse_ok 9/10; successful response parse_ok 9/9. Error rows: BAL100-BEC-EXPLAINED-ANOMALY-015-A gemini:gemini-2.5-flash-lite HTTP 503 HTTPError.
- Preserved useful disagreement: no; No useful disagreement: ALLOW had one Gemini 503 provider-call failure and the returned valid rows aligned; ESCALATE was unanimous.
- ALLOW avoided false escalation: yes
- ESCALATE too easy: yes
- Seam contamination: no; No second blocker, generic BEC shortcut, answer-key leak, or out-of-scope family inclusion surfaced in scout triage.
- Recommended next action: Repair once or rerun after a small wording pass; do not promote while the provider row set is incomplete and ESCALATE is too easy.

### BAL100-BEC-EXPLAINED-ANOMALY-017

- Classification: `repair_once`
- Packet IDs: `BAL100-BEC-EXPLAINED-ANOMALY-017-A`, `BAL100-BEC-EXPLAINED-ANOMALY-017-B`
- ALLOW sibling behavior: 4/5 ALLOW, 1/5 false ESCALATE; false escalation provider(s): openai:gpt-4o-mini.
- ESCALATE sibling behavior: 5/5 ESCALATE; unanimous and marked too easy.
- Provider parse health: provider_call_ok 10/10; parse_ok 10/10; successful response parse_ok 10/10.
- Preserved useful disagreement: no; No useful promotion-grade disagreement: the only disagreement was an OpenAI false escalation on the ALLOW sibling, while ESCALATE was unanimous.
- ALLOW avoided false escalation: no
- ESCALATE too easy: yes
- Seam contamination: no; No second blocker, generic BEC shortcut, answer-key leak, or out-of-scope family inclusion surfaced in scout triage.
- Recommended next action: Repair once by making the ALLOW identity/source closure more explicit without adding a second blocker, and reduce ESCALATE obviousness.

### BAL100-BEC-EXPLAINED-ANOMALY-018

- Classification: `repair_once`
- Packet IDs: `BAL100-BEC-EXPLAINED-ANOMALY-018-A`, `BAL100-BEC-EXPLAINED-ANOMALY-018-B`
- ALLOW sibling behavior: 3/5 ALLOW, 1/5 false ESCALATE, 1/5 provider-call error; false escalation provider(s): openai:gpt-4o-mini; error provider: gemini:gemini-2.5-flash-lite HTTP 503.
- ESCALATE sibling behavior: 5/5 ESCALATE; unanimous and marked too easy.
- Provider parse health: provider_call_ok 9/10; parse_ok 9/10; successful response parse_ok 9/9. Error rows: BAL100-BEC-EXPLAINED-ANOMALY-018-A gemini:gemini-2.5-flash-lite HTTP 503 HTTPError.
- Preserved useful disagreement: no; No useful promotion-grade disagreement: ALLOW had both an OpenAI false escalation and a Gemini 503 provider-call failure; ESCALATE was unanimous.
- ALLOW avoided false escalation: no
- ESCALATE too easy: yes
- Seam contamination: no; No second blocker, generic BEC shortcut, answer-key leak, or out-of-scope family inclusion surfaced in scout triage.
- Recommended next action: Repair once by clarifying source-grounded meter/contract closure in ALLOW and making ESCALATE less obviously unresolved; then consider a narrow rescout.

## Proof Credit

- Proof-credit remains unchanged: 2 pair families / 4 packets.
- Credit remains limited to `BEC-PAIR-009` and `BEC-PAIR-010`.
- Batch 002 remains diagnostic/non-credit.
