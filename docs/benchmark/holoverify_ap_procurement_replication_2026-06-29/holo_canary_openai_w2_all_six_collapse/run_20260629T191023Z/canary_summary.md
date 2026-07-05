# AP OpenAI-W2 All-Six-Collapse Holo Canary

Classification: `AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_CANARY_INVALID_OR_INCOMPLETE`
Readiness passed: `False`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Calls

- Provider calls: `26` / `60`
- Worker calls: `16`
- Gov calls: `10`
- Solo calls: `0`
- Judge calls: `0`
- Tokens: `41379` input / `9432` output / `53563` total

## Pair Inventory

| Pair | Target final | Guardrail final | Valid |
| --- | --- | --- | --- |
| `HV-AP-REP-011` | `ESCALATE` | `ALLOW` | `False` |
| `HV-AP-REP-012` | `ESCALATE` | `ALLOW` | `False` |
| `HV-AP-REP-013` | `None` | `ALLOW` | `False` |

## Assertions

| Assertion | Value |
| --- | --- |
| `holo_packets` | `FAIL` |
| `holo_pairs` | `FAIL` |
| `provider_calls` | `FAIL` |
| `worker_calls` | `FAIL` |
| `gov_calls` | `FAIL` |
| `no_judges` | `PASS` |
| `no_solo` | `PASS` |
| `provider_failures` | `PASS` |
| `no_leakage` | `PASS` |
| `packet_identity_matches_freeze` | `PASS` |
| `three_dna_present` | `PASS` |
| `roster_matches` | `PASS` |
| `deterministic_gate_after_every_worker` | `FAIL` |
| `gov_receives_gate_results` | `PASS` |
| `final_selector_present` | `PASS` |
| `all_target_pairs_valid` | `FAIL` |
| `all_packets_correct` | `FAIL` |
| `benchmark_laws` | `PASS` |
