# AP HoloVerify Replication Live Summary

Classification: `HOLOVERIFY_AP_REPLICATION_HOLO_INVALID_OR_INCOMPLETE`
Readiness passed: `False`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Calls

- Provider calls: `2` / `200`
- Worker calls: `1`
- Gov calls: `1`
- Judge calls: `0`
- Transport attempted calls: `0`
- Transport recovered calls: `0`
- Tokens: `1966` input / `565` output / `2990` total

## Root Failure

- Invalidation reason: `GOV_CONTRACT_OR_TRUNCATION_FAILURE`
- Turn: `HV-AP-REP-001-A_G1`
- Packet: `HV-AP-REP-001-A`
- Kind: `gov`
- Provider/model: `minimax/MiniMax-M2.5-highspeed`
- Finish reason: `length`
- Error: `ValueError: gov_finish_reason_length_incomplete_baton:gov_micro_missing_keys:dep,focus,objective`
- Transport attempts: `1`
- Transport final failure class: `None`

## Assertions

| Assertion | Value |
| --- | --- |
| `packet_hashes_match_freeze` | `PASS` |
| `holo_packets` | `1` |
| `holo_valid_pairs` | `0` |
| `holo_no_judges` | `PASS` |
| `holo_provider_failures` | `0` |
| `three_dna_inside_holoverify` | `FAIL` |
| `declared_roster_matches_actual_calls` | `PASS` |
| `deterministic_gate_after_every_worker` | `PASS` |
| `gov_receives_gate_results` | `PASS` |
| `final_selector_present` | `PASS` |
| `holo_benchmark_laws` | `FAIL` |

## Pair Inventory

| Pair | Bucket | Target final | Guardrail final | Valid |
| --- | --- | --- | --- | --- |
| `HV-AP-REP-001` | `N/A` | `N/A` | `N/A` | `False` |
