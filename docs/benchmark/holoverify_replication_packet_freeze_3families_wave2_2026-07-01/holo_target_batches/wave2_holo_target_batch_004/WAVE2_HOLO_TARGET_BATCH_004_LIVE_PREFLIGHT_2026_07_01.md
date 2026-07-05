# Wave 2 Holo Target Batch 004 Live Preflight

Status: `PASS`
Batch: `WAVE2_HOLO_TARGET_BATCH_004`
Selection mode: `target-selection`
Selection mode defaulted: `True`
Freeze root: `80d8106d7efe72bee44d2c05648b71814204c08e1f96934afefd3d75d242845f`
Root signature: `7e9e5dd2b0fff1f8614aa23c0d4570b828c2b31e671748de2001b96e9942dbd9`

## Expected Calls

- `pairs`: `10`
- `packets`: `20`
- `worker_calls`: `60`
- `gov_calls`: `40`
- `total_provider_calls`: `100`
- `solo_calls`: `0`
- `judge_calls`: `0`

## Roster

| Slot | Provider | Model | Role |
| --- | --- | --- | --- |
| `W1` | `xai` | `grok-3-mini` | `SOURCE_BOUNDARY_MAPPER` |
| `W2` | `openai` | `gpt-5.4-mini` | `ADVERSARIAL_SCOPE_CHALLENGER` |
| `W3` | `minimax` | `MiniMax-M2.5-highspeed` | `FINAL_COMPILER` |
| `G1` | `minimax` | `MiniMax-M2.5-highspeed` | Gov |
| `G2` | `minimax` | `MiniMax-M2.5-highspeed` | Gov |

## Checks

| Check | Value |
| --- | --- |
| `staging_preflight_passed` | `True` |
| `freeze_root_matches` | `True` |
| `target_selection_sha_matches` | `True` |
| `pair_count` | `True` |
| `packet_count` | `True` |
| `selected_pair_ids_match_registration` | `True` |
| `packet_hashes_match_freeze` | `True` |
| `prompt_hashes_match_freeze` | `True` |
| `no_packet_edits` | `True` |
| `no_prompt_edits` | `True` |
| `no_manifest_edits` | `True` |
| `worker_roster_declared` | `True` |
| `gov_is_minimax` | `True` |
| `gov_cannot_choose_models` | `True` |
| `w2_is_openai_gpt_5_4_mini` | `True` |
| `no_gemini_active` | `True` |
| `worker_contract_format` | `True` |
| `gov_contract_format` | `True` |
| `gov_max_tokens_1024` | `True` |
| `transport_policy_v1_active` | `True` |
| `deterministic_gates_configured` | `True` |
| `gov_sees_gate_results` | `True` |
| `artifact_registry_configured` | `True` |
| `best_artifact_registry_configured` | `True` |
| `pinned_best_configured` | `True` |
| `final_selector_configured` | `True` |
| `expected_provider_calls_100` | `True` |
| `solo_calls_0` | `True` |
| `judge_calls_0` | `True` |

## Live Execution Gate

Status: `PASS`

## Provider Approval Gate

Approval required: `True`
Required statement SHA-256: `8546b89af04788e72a4ed5592f93223d1ee139f96436e31f79e03eaf73b9e9b0`

Required approval statement:

`I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_004 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

## Next Step

Run `python3 -B docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py --batch-number 4 --run-live --approval-packet-sha256 APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET --approval-statement "I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_004 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."` only when provider calls are approved.
