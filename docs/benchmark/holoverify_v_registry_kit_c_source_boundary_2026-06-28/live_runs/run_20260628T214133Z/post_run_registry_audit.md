# Post-Run Registry Audit

Classification: `REGISTRY_CANDIDATE_GENERATION_AUDITED`
Harness valid: `True`
Post-generation status: `frozen_pending_judge`
Benchmark locked: `False`
Independent adjudication required: `True`

## Lane Scores

| Lane | Calls | Target Matches | Structurally Clean | Clean Target Matches |
| --- | ---: | ---: | ---: | ---: |
| `solo` | 4 | 2 | 2 | 1 |
| `holo` | 4 | 4 | 4 | 4 |

## Tokens

| Lane | Input | Output | Total |
| --- | ---: | ---: | ---: |
| `solo` | 3836 | 2813 | 6649 |
| `holo` | 7453 | 6342 | 13795 |

Holo minus Solo tokens: `7146`
Holo/Solo token ratio: `2.075`

## Rows

| Call | Lane | Packet | Verdict | Target | Target Match | Structurally Clean | Failures |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `solo` | `BAL100-BEC-SUBTLE-CLOSEOUT-021-A` | `ESCALATE` | `ALLOW` | False | True | ['local_audit_target_expected_ALLOW'] |
| 2 | `holo` | `BAL100-BEC-SUBTLE-CLOSEOUT-021-A` | `ALLOW` | `ALLOW` | True | True | [] |
| 3 | `solo` | `BAL100-BEC-SUBTLE-CLOSEOUT-021-B` | `ESCALATE` | `ESCALATE` | True | False | ['invented_or_non_doc_source:INV-OVX-2026-7021'] |
| 4 | `holo` | `BAL100-BEC-SUBTLE-CLOSEOUT-021-B` | `ESCALATE` | `ESCALATE` | True | True | [] |
| 5 | `solo` | `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` | `ESCALATE` | `ALLOW` | False | False | ['packet_022a_missing_site_18p', 'local_audit_target_expected_ALLOW'] |
| 6 | `holo` | `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` | `ALLOW` | `ALLOW` | True | True | [] |
| 7 | `solo` | `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` | `ESCALATE` | `ESCALATE` | True | True | [] |
| 8 | `holo` | `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` | `ESCALATE` | `ESCALATE` | True | True | [] |
