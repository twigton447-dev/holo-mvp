# Commerce OpenAI-W2 All-Six-Collapse Holo Canary Preflight

Classification: `COMMERCE_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_CANARY_PREFLIGHT`
Status: `PASS`
Result: `COMMERCE_OPENAI_W2_ALL_SIX_COLLAPSE_CANARY_READY`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Scope

- Target pairs: `HV-ACOM-REP-020, HV-ACOM-REP-006, HV-ACOM-REP-019`
- Expected packets: `6`
- Expected provider calls: `30`
- Solo calls: `0`
- Judge calls: `0`

## Checks

| Check | Value |
| --- | --- |
| `freeze_root_matches` | `True` |
| `target_pairs_count` | `True` |
| `target_packets_count` | `True` |
| `solo_triage_run_present` | `True` |
| `solo_triage_lock_pass` | `True` |
| `solo_triage_all_six_pairs_match` | `True` |
| `w2_is_openai_gpt_5_4_mini` | `True` |
| `no_gemini_active` | `True` |
| `gov_is_minimax` | `True` |
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

Stop here unless live canary execution is explicitly approved.
