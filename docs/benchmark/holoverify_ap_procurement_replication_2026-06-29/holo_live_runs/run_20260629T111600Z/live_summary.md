# AP HoloVerify Replication Live Summary

Classification: `HOLOVERIFY_AP_REPLICATION_HOLO_INVALID_OR_INCOMPLETE`
Readiness passed: `False`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Calls

- Provider calls: `28` / `200`
- Worker calls: `17`
- Gov calls: `11`
- Judge calls: `0`
- Tokens: `40616` input / `12024` output / `56237` total

## Assertions

| Assertion | Value |
| --- | --- |
| `packet_hashes_match_freeze` | `PASS` |
| `holo_packets` | `6` |
| `holo_valid_pairs` | `2` |
| `holo_no_judges` | `PASS` |
| `holo_provider_failures` | `1` |
| `three_dna_inside_holoverify` | `PASS` |
| `declared_roster_matches_actual_calls` | `PASS` |
| `deterministic_gate_after_every_worker` | `FAIL` |
| `gov_receives_gate_results` | `PASS` |
| `final_selector_present` | `PASS` |
| `holo_benchmark_laws` | `PASS` |

## Pair Inventory

| Pair | Bucket | Target final | Guardrail final | Valid |
| --- | --- | --- | --- | --- |
| `HV-AP-REP-001` | `hard_allow` | `ALLOW` | `ESCALATE` | `True` |
| `HV-AP-REP-002` | `hard_allow` | `ALLOW` | `ESCALATE` | `True` |
| `HV-AP-REP-003` | `hard_allow` | `ALLOW` | `None` | `False` |
