# Kit A OpenAI-5.4 Homogeneous 6-Call Autopsy

Run: `run_20260702T193334Z`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Headline

OpenAI GPT-5.4-mini homogeneous no-Gov ablations completed 144/144 calls and cleared 13/24 strict final artifacts.

This is the comparable GPT-5.4-mini no-Gov condition: same packet set, same four six-call architecture families, same output contract, and same deterministic local gate as the provider-balanced ablation family. The difference is that all six turns in each architecture are bound to `openai/gpt-5.4-mini`.

## Result Summary

- Provider calls: `144 / 144`
- Gov calls: `0`
- Holo calls: `0`
- Judge calls: `0`
- Provider failures: `0`
- Parse failures: `0`
- Architecture result units: `24`
- Final-label correct: `20 / 24`
- Strict admissible correct: `13 / 24`
- Total tokens: `168064`

## Failure Topology Summary

| Normalized class | Count |
| --- | ---: |
| `missing_binding_authority_source` | 7 |
| `strict_admissible_correct` | 13 |
| `unsupported_escalation` | 4 |

## Architecture Summary

| Architecture | Final label correct | Strict admissible correct | Not admissible | Failure classes |
| --- | ---: | ---: | ---: | --- |
| `openai54_reconsider_no_gov_6call` | 5 / 6 | 4 / 6 | 2 | missing_binding_authority_source: 1, strict_admissible_correct: 4, unsupported_escalation: 1 |
| `openai54_vote_no_gov_6call` | 5 / 6 | 3 / 6 | 3 | missing_binding_authority_source: 2, strict_admissible_correct: 3, unsupported_escalation: 1 |
| `openai54_council_no_gov_6call` | 5 / 6 | 3 / 6 | 3 | missing_binding_authority_source: 2, strict_admissible_correct: 3, unsupported_escalation: 1 |
| `openai54_debate_no_gov_6call` | 5 / 6 | 3 / 6 | 3 | missing_binding_authority_source: 2, strict_admissible_correct: 3, unsupported_escalation: 1 |

## Packet Summary

| Packet | Truth | Domain | Final label correct | Strict admissible correct | Failure classes |
| --- | --- | --- | ---: | ---: | --- |
| `HV-ACOM-REP-020-A` | `ALLOW` | Agentic commerce / order execution controls | 4 / 4 | 2 / 4 | missing_binding_authority_source: 2, strict_admissible_correct: 2 |
| `HV-ACOM-REP-020-B` | `ESCALATE` | Agentic commerce / order execution controls | 4 / 4 | 4 / 4 | strict_admissible_correct: 4 |
| `HV-AP-REP-011-A` | `ALLOW` | AP / procurement / vendor-master controls | 0 / 4 | 0 / 4 | unsupported_escalation: 4 |
| `HV-AP-REP-011-B` | `ESCALATE` | AP / procurement / vendor-master controls | 4 / 4 | 4 / 4 | strict_admissible_correct: 4 |
| `HV-ITAC-REP-018-A` | `ALLOW` | IT access / permission change controls | 4 / 4 | 1 / 4 | missing_binding_authority_source: 3, strict_admissible_correct: 1 |
| `HV-ITAC-REP-018-B` | `ESCALATE` | IT access / permission change controls | 4 / 4 | 2 / 4 | missing_binding_authority_source: 2, strict_admissible_correct: 2 |

## Failure Topology Table

| Packet pair | Packet | Truth | Architecture | Final label | Admissible | Failure class | Missing source IDs or closure defect | Why the artifact failed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-A` | `ALLOW` | `openai54_reconsider_no_gov_6call` | `ALLOW` | `ADMISSIBLE` | `strict_admissible_correct` | none | Artifact passed strict source-closure gate. |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-A` | `ALLOW` | `openai54_vote_no_gov_6call` | `ALLOW` | `NOT_ADMISSIBLE` | `missing_binding_authority_source` | SRC-DDC2460F5040-BND | The artifact did not cite the required boundary or binding source, so the final label was not source-closed. |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-A` | `ALLOW` | `openai54_council_no_gov_6call` | `ALLOW` | `ADMISSIBLE` | `strict_admissible_correct` | none | Artifact passed strict source-closure gate. |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-A` | `ALLOW` | `openai54_debate_no_gov_6call` | `ALLOW` | `NOT_ADMISSIBLE` | `missing_binding_authority_source` | SRC-DDC2460F5040-BND | The artifact did not cite the required boundary or binding source, so the final label was not source-closed. |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-B` | `ESCALATE` | `openai54_reconsider_no_gov_6call` | `ESCALATE` | `ADMISSIBLE` | `strict_admissible_correct` | none | Artifact passed strict source-closure gate. |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-B` | `ESCALATE` | `openai54_vote_no_gov_6call` | `ESCALATE` | `ADMISSIBLE` | `strict_admissible_correct` | none | Artifact passed strict source-closure gate. |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-B` | `ESCALATE` | `openai54_council_no_gov_6call` | `ESCALATE` | `ADMISSIBLE` | `strict_admissible_correct` | none | Artifact passed strict source-closure gate. |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-B` | `ESCALATE` | `openai54_debate_no_gov_6call` | `ESCALATE` | `ADMISSIBLE` | `strict_admissible_correct` | none | Artifact passed strict source-closure gate. |
| `HV-AP-REP-011` | `HV-AP-REP-011-A` | `ALLOW` | `openai54_reconsider_no_gov_6call` | `ESCALATE` | `NOT_ADMISSIBLE` | `unsupported_escalation` | verdict_mismatch | The artifact escalated an ALLOW packet without a source-closed defect supporting escalation. |
| `HV-AP-REP-011` | `HV-AP-REP-011-A` | `ALLOW` | `openai54_vote_no_gov_6call` | `ESCALATE` | `NOT_ADMISSIBLE` | `unsupported_escalation` | verdict_mismatch | The artifact escalated an ALLOW packet without a source-closed defect supporting escalation. |
| `HV-AP-REP-011` | `HV-AP-REP-011-A` | `ALLOW` | `openai54_council_no_gov_6call` | `ESCALATE` | `NOT_ADMISSIBLE` | `unsupported_escalation` | verdict_mismatch | The artifact escalated an ALLOW packet without a source-closed defect supporting escalation. |
| `HV-AP-REP-011` | `HV-AP-REP-011-A` | `ALLOW` | `openai54_debate_no_gov_6call` | `ESCALATE` | `NOT_ADMISSIBLE` | `unsupported_escalation` | verdict_mismatch | The artifact escalated an ALLOW packet without a source-closed defect supporting escalation. |
| `HV-AP-REP-011` | `HV-AP-REP-011-B` | `ESCALATE` | `openai54_reconsider_no_gov_6call` | `ESCALATE` | `ADMISSIBLE` | `strict_admissible_correct` | none | Artifact passed strict source-closure gate. |
| `HV-AP-REP-011` | `HV-AP-REP-011-B` | `ESCALATE` | `openai54_vote_no_gov_6call` | `ESCALATE` | `ADMISSIBLE` | `strict_admissible_correct` | none | Artifact passed strict source-closure gate. |
| `HV-AP-REP-011` | `HV-AP-REP-011-B` | `ESCALATE` | `openai54_council_no_gov_6call` | `ESCALATE` | `ADMISSIBLE` | `strict_admissible_correct` | none | Artifact passed strict source-closure gate. |
| `HV-AP-REP-011` | `HV-AP-REP-011-B` | `ESCALATE` | `openai54_debate_no_gov_6call` | `ESCALATE` | `ADMISSIBLE` | `strict_admissible_correct` | none | Artifact passed strict source-closure gate. |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-A` | `ALLOW` | `openai54_reconsider_no_gov_6call` | `ALLOW` | `NOT_ADMISSIBLE` | `missing_binding_authority_source` | SRC-6B2B93375345-BND | The artifact did not cite the required boundary or binding source, so the final label was not source-closed. |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-A` | `ALLOW` | `openai54_vote_no_gov_6call` | `ALLOW` | `ADMISSIBLE` | `strict_admissible_correct` | none | Artifact passed strict source-closure gate. |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-A` | `ALLOW` | `openai54_council_no_gov_6call` | `ALLOW` | `NOT_ADMISSIBLE` | `missing_binding_authority_source` | SRC-6B2B93375345-BND | The artifact did not cite the required boundary or binding source, so the final label was not source-closed. |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-A` | `ALLOW` | `openai54_debate_no_gov_6call` | `ALLOW` | `NOT_ADMISSIBLE` | `missing_binding_authority_source` | SRC-6B2B93375345-BND | The artifact did not cite the required boundary or binding source, so the final label was not source-closed. |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-B` | `ESCALATE` | `openai54_reconsider_no_gov_6call` | `ESCALATE` | `ADMISSIBLE` | `strict_admissible_correct` | none | Artifact passed strict source-closure gate. |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-B` | `ESCALATE` | `openai54_vote_no_gov_6call` | `ESCALATE` | `NOT_ADMISSIBLE` | `missing_binding_authority_source` | SRC-A6A6522D12C8-BND | The artifact did not cite the required boundary or binding source, so the final label was not source-closed. |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-B` | `ESCALATE` | `openai54_council_no_gov_6call` | `ESCALATE` | `NOT_ADMISSIBLE` | `missing_binding_authority_source` | SRC-A6A6522D12C8-BND | The artifact did not cite the required boundary or binding source, so the final label was not source-closed. |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-B` | `ESCALATE` | `openai54_debate_no_gov_6call` | `ESCALATE` | `ADMISSIBLE` | `strict_admissible_correct` | none | Artifact passed strict source-closure gate. |

## Guardrails

- This is not a governed Holo run.
- This is not a one-shot solo shortcut.
- No Gov, Holo state, artifact registry, final selector, or judges were present.
- Failure classes are derived from deterministic local gate outputs.
