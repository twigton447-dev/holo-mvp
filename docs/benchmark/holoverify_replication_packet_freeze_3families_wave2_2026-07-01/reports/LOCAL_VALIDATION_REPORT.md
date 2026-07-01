# Local Validation Report

Status: PASS

## Final Assertions

| Assertion | Result |
| --- | --- |
| `families` | `3` |
| `pairs` | `60` |
| `packets` | `120` |
| `schema_validation` | `PASS` |
| `pair_balance` | `PASS` |
| `no_prompt_leakage` | `PASS` |
| `no_answer_key_leakage` | `PASS` |
| `no_provider_calls` | `PASS` |
| `no_judge_calls` | `PASS` |

## Family Summaries

| Family | Pairs | Packets | Truths | Target buckets |
| --- | ---: | ---: | --- | --- |
| `HV-HRWF-REP-2026-07-01` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-DPRV-REP-2026-07-01` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-FINC-REP-2026-07-01` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |

## Failures

None.
