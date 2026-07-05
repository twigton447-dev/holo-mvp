# IT Access OpenAI-W2 Batched Full-Holo Preflight

Classification: `IT_ACCESS_OPENAI_W2_BATCHED_FULL_HOLO_PREFLIGHT`
Batch: `replacement_015r1`
Status: `PASS`
Result: `IT_ACCESS_OPENAI_W2_BATCH_READY`
Freeze root: `6c61024da5f6c36c1ee5210b95efd1d7a1ed0caff60a11efe0ace1ca1e72dc4e`
Original freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
Supplemental replacement freeze: `True`
Replacement for: `HV-ITAC-REP-015`

## Scope

- Pair range: `replacement_pair_015r1`
- Pair IDs: `HV-ITAC-REP-015R1`
- Expected packets: `2`
- Expected provider calls: `10`
- Solo calls: `0`
- Judge calls: `0`
- MiniMax health required: `False`
- MiniMax recent clean health: `True`
- MiniMax worker smoke required: `False`
- MiniMax recent worker smoke: `True`

## Checks

| Check | Value |
| --- | --- |
| `freeze_root_matches` | `True` |
| `original_freeze_root_preserved` | `True` |
| `replacement_freeze_root_matches` | `True` |
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
| `no_providers_called_during_preflight` | `True` |

Stop here unless live batch execution is explicitly approved.
