# Commerce OpenAI-W2 Batched Full-Holo Preflight

Classification: `COMMERCE_OPENAI_W2_BATCHED_FULL_HOLO_PREFLIGHT`
Batch: `batch_2`
Status: `PASS`
Result: `COMMERCE_OPENAI_W2_BATCH_READY`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Scope

- Pair range: `pairs_008_014`
- Pair IDs: `HV-ACOM-REP-008, HV-ACOM-REP-009, HV-ACOM-REP-010, HV-ACOM-REP-011, HV-ACOM-REP-012, HV-ACOM-REP-013, HV-ACOM-REP-014`
- Expected packets: `14`
- Expected provider calls: `70`
- Solo calls: `0`
- Judge calls: `0`

## Checks

| Check | Value |
| --- | --- |
| `freeze_root_matches` | `True` |
| `batch_declared` | `True` |
| `target_pairs_match_batch` | `True` |
| `target_pairs_count` | `True` |
| `target_packets_count` | `True` |
| `w2_is_openai_gpt_5_4_mini` | `True` |
| `no_gemini_active` | `True` |
| `gov_is_minimax` | `True` |
| `gov_may_select_models` | `True` |
| `worker_contract_format` | `True` |
| `gov_contract_format` | `True` |
| `generic_worker_max_tokens` | `True` |
| `minimax_final_compiler_worker_max_tokens` | `True` |
| `minimax_final_compiler_budget_active` | `True` |
| `gov_max_tokens` | `True` |
| `transport_policy_v1_active` | `True` |
| `empty_worker_output_retry_policy_v1_active` | `True` |
| `no_packet_edits` | `True` |
| `no_prompt_edits` | `True` |
| `expected_provider_calls` | `True` |
| `expected_worker_calls` | `True` |
| `expected_gov_calls` | `True` |
| `solo_calls_configured` | `True` |
| `judge_calls_configured` | `True` |
| `providers_called_during_preflight` | `True` |

Stop here unless live batch execution is explicitly approved.
