# AP OpenAI-W2 One-Pair Holo Canary

Classification: `AP_OPENAI_W2_CANARY_INVALID_OR_INCOMPLETE`
Readiness passed: `False`
Failure class: `GOV_CONTRACT_OR_ADMISSIBILITY_FAILURE`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Calls

- Provider calls: `2` / `10`
- Worker calls: `1`
- Gov calls: `1`
- Solo calls: `0`
- Judge calls: `0`
- Tokens: `1949` input / `381` output / `2726` total
- Transport recovered calls: `0`

## Assertions

| Assertion | Value |
| --- | --- |
| `holo_packets` | `FAIL` |
| `holo_pairs` | `PASS` |
| `holo_calls` | `FAIL` |
| `unrecovered_provider_failures` | `PASS` |
| `no_judges` | `PASS` |
| `no_solo` | `PASS` |
| `no_leakage` | `PASS` |
| `packet_identity_matches_freeze` | `PASS` |
| `gov_v2_parsed_every_gov_turn` | `FAIL` |
| `worker_compact_parsed_every_worker_turn` | `FAIL` |
| `both_sibling_final_verdicts_correct` | `FAIL` |
| `final_selector_present` | `PASS` |
| `declared_call_count_10` | `PASS` |

## Root Failure

- Turn: `HV-AP-REP-001-A_G1`
- Kind: `gov`
- Provider/model: `minimax/MiniMax-M2.5-highspeed`
- Error: `ValueError: gov_micro_v2_unknown_enum:preserve:wb_code`

## Packet Inventory

| Packet | Expected | Final | Correct |
| --- | --- | --- | --- |
| `HV-AP-REP-001-A` | `ALLOW` | `None` | `False` |
