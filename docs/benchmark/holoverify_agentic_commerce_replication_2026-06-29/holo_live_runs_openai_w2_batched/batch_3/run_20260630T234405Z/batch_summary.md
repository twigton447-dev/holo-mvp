# Commerce OpenAI-W2 Batched Holo Run

Classification: `COMMERCE_OPENAI_W2_BATCHED_HOLO_BATCH_COMPLETE`
Batch: `batch_3`
Readiness passed: `True`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Calls

- Provider calls: `60` / `60`
- Worker calls: `36`
- Gov calls: `24`
- Solo calls: `0`
- Judge calls: `0`
- Tokens: `98940` input / `20091` output / `126639` total

## Pair Inventory

| Pair | Target final | Guardrail final | Valid |
| --- | --- | --- | --- |
| `HV-ACOM-REP-015` | `ESCALATE` | `ALLOW` | `True` |
| `HV-ACOM-REP-016` | `ESCALATE` | `ALLOW` | `True` |
| `HV-ACOM-REP-017` | `ESCALATE` | `ALLOW` | `True` |
| `HV-ACOM-REP-018` | `ESCALATE` | `ALLOW` | `True` |
| `HV-ACOM-REP-019` | `ESCALATE` | `ALLOW` | `True` |
| `HV-ACOM-REP-020` | `ESCALATE` | `ALLOW` | `True` |

## Assertions

| Assertion | Value |
| --- | --- |
| `holo_packets` | `PASS` |
| `holo_pairs` | `PASS` |
| `provider_calls` | `PASS` |
| `worker_calls` | `PASS` |
| `gov_calls` | `PASS` |
| `no_judges` | `PASS` |
| `no_solo` | `PASS` |
| `provider_failures` | `PASS` |
| `no_leakage` | `PASS` |
| `packet_identity_matches_freeze` | `PASS` |
| `three_dna_present` | `PASS` |
| `roster_matches` | `PASS` |
| `deterministic_gate_after_every_worker` | `PASS` |
| `gov_receives_gate_results` | `PASS` |
| `final_selector_present` | `PASS` |
| `all_pairs_valid` | `PASS` |
| `all_packets_correct` | `PASS` |
| `benchmark_laws` | `PASS` |
