# AP OpenAI-W2 One-Pair Holo Canary

Classification: `AP_OPENAI_W2_CANARY_READY_FOR_FULL_FAMILY_RUN`
Readiness passed: `True`
Failure class: `None`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Calls

- Provider calls: `10` / `10`
- Worker calls: `6`
- Gov calls: `4`
- Solo calls: `0`
- Judge calls: `0`
- Tokens: `15786` input / `3578` output / `20310` total
- Transport recovered calls: `0`

## Assertions

| Assertion | Value |
| --- | --- |
| `holo_packets` | `PASS` |
| `holo_pairs` | `PASS` |
| `holo_calls` | `PASS` |
| `unrecovered_provider_failures` | `PASS` |
| `no_judges` | `PASS` |
| `no_solo` | `PASS` |
| `no_leakage` | `PASS` |
| `packet_identity_matches_freeze` | `PASS` |
| `gov_v2_parsed_every_gov_turn` | `PASS` |
| `worker_compact_parsed_every_worker_turn` | `PASS` |
| `both_sibling_final_verdicts_correct` | `PASS` |
| `final_selector_present` | `PASS` |
| `declared_call_count_10` | `PASS` |

## Packet Inventory

| Packet | Expected | Final | Correct |
| --- | --- | --- | --- |
| `HV-AP-REP-001-A` | `ALLOW` | `ALLOW` | `True` |
| `HV-AP-REP-001-B` | `ESCALATE` | `ESCALATE` | `True` |
