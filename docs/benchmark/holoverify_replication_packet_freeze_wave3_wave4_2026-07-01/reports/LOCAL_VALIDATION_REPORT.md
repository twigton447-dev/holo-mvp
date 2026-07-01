# Wave 3 / Wave 4 Local Validation Report

Status: `PASS`

## Final Assertions

| Assertion | Result |
| --- | --- |
| `waves` | `2` |
| `families` | `6` |
| `pairs` | `120` |
| `packets` | `240` |
| `schema_validation` | `PASS` |
| `pair_balance` | `PASS` |
| `no_prompt_leakage` | `PASS` |
| `no_answer_key_leakage` | `PASS` |
| `no_provider_calls` | `PASS` |
| `no_judge_calls` | `PASS` |

## Wave Summaries

| Wave | Families | Pairs | Packets | Truths |
| --- | ---: | ---: | ---: | --- |
| `wave3` | 3 | 60 | 120 | `{'ALLOW': 60, 'ESCALATE': 60}` |
| `wave4` | 3 | 60 | 120 | `{'ALLOW': 60, 'ESCALATE': 60}` |

## Family Summaries

| Family | Wave | Pairs | Packets | Truths | Target buckets |
| --- | --- | ---: | ---: | --- | --- |
| `HV-BENC-REP-2026-07-01` | `wave3` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-BKYC-REP-2026-07-01` | `wave3` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-DEFA-REP-2026-07-01` | `wave4` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-GOVP-REP-2026-07-01` | `wave3` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-INSR-REP-2026-07-01` | `wave4` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-UTIL-REP-2026-07-01` | `wave4` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |

## Failures

None.
