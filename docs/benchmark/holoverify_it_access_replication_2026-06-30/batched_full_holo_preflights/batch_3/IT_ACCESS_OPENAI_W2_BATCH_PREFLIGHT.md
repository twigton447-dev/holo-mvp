# IT Access OpenAI-W2 Batched Full-Holo Preflight

Classification: `IT_ACCESS_OPENAI_W2_BATCHED_FULL_HOLO_PREFLIGHT`
Batch: `batch_3`
Status: `PASS`
Result: `IT_ACCESS_OPENAI_W2_BATCH_READY`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Scope

- Pair range: `pairs_015_020`
- Pair IDs: `HV-ITAC-REP-015, HV-ITAC-REP-016, HV-ITAC-REP-017, HV-ITAC-REP-018, HV-ITAC-REP-019, HV-ITAC-REP-020`
- Expected packets: `12`
- Expected provider calls: `60`
- Solo calls: `0`
- Judge calls: `0`
- MiniMax health required: `False`
- MiniMax recent clean health: `False`
- MiniMax worker smoke required: `False`
- MiniMax recent worker smoke: `False`

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
| `no_providers_called_during_preflight` | `True` |

Stop here unless live batch execution is explicitly approved.
