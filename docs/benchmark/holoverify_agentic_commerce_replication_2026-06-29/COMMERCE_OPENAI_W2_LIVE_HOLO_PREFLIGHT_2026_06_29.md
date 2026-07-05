# Commerce OpenAI-W2 Live Holo Preflight

Classification: `COMMERCE_OPENAI_W2_LIVE_HOLO_PREFLIGHT`
Variant: `COMMERCE_OPENAI_W2_ROSTER_VARIANT_2026_06_29`
Status: `PASS`
Result: `COMMERCE_OPENAI_W2_READY_FOR_FULL_HOLO_RUN`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Roster

| Slot | Provider | Model | Role |
| --- | --- | --- | --- |
| `W1` | `xai` | `grok-3-mini` | `SOURCE_BOUNDARY_MAPPER` |
| `W2` | `openai` | `gpt-5.4-mini` | `ADVERSARIAL_SCOPE_CHALLENGER` |
| `W3` | `minimax` | `MiniMax-M2.5-highspeed` | `FINAL_COMPILER` |
| `G1` | `minimax` | `MiniMax-M2.5-highspeed` | Gov |
| `G2` | `minimax` | `MiniMax-M2.5-highspeed` | Gov |

## Runtime Binding

- Actual W2 provider: `openai`
- Actual W2 model: `gpt-5.4-mini`
- Actual W2 kind: `openai_responses`
- Live Holo started: `False`
- Solo started: `False`
- Judges started: `False`
- Providers called during preflight: `0`

## Checks

| Check | Value |
| --- | --- |
| `registration_file_present` | `True` |
| `availability_file_present` | `True` |
| `availability_passed` | `True` |
| `freeze_root_matches` | `True` |
| `ap_packet_hashes_match_freeze` | `True` |
| `ap_prompt_hashes_match_freeze` | `True` |
| `no_packet_edits` | `True` |
| `no_prompt_edits` | `True` |
| `model_roster_declared` | `True` |
| `actual_runner_w2_is_openai` | `True` |
| `actual_runner_w2_is_not_gemini` | `True` |
| `no_fallback_substitution_enabled` | `True` |
| `deterministic_gates_configured` | `True` |
| `gov_sees_gate_results` | `True` |
| `artifact_registry_configured` | `True` |
| `best_artifact_registry_configured` | `True` |
| `pinned_best_configured` | `True` |
| `monotonic_preservation_configured` | `True` |
| `final_selector_configured` | `True` |
| `trace_accounting_configured` | `True` |
| `gov_contract_format` | `True` |
| `worker_contract_format` | `True` |
| `gov_output_budget_sufficient` | `True` |
| `gov_max_tokens` | `True` |
| `generic_worker_max_tokens` | `True` |
| `minimax_final_compiler_worker_max_tokens` | `True` |
| `minimax_final_compiler_budget_active` | `True` |
| `empty_worker_output_retry_policy_v1_active` | `True` |
| `empty_worker_output_max_retries` | `True` |
| `expected_holo_calls` | `True` |
| `expected_packets` | `True` |
| `expected_pairs` | `True` |
| `solo_not_configured_to_run` | `True` |
| `judges_not_configured_to_run` | `True` |
| `providers_called_during_preflight` | `True` |

## Interpretation

`COMMERCE_OPENAI_W2_READY_FOR_FULL_HOLO_RUN`

Stop here. Do not start full Holo until explicitly approved.
