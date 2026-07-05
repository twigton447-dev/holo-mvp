# Wave 4 Holo Target Batch 001 Live Preflight

Status: `PASS`
Batch: `WAVE4_HOLO_TARGET_BATCH_001`
Freeze root: `ac44c5d69ad73c64dcae1591e37cc9ade8a80ed5e71a05786cd2490a445c2dd5`
Root signature: `808e579bb56984877ce884a7ee1bec8297b37fdb66d7b2aadfe17aacd50a96cf`

## Expected Calls

- `pairs`: `15`
- `packets`: `30`
- `worker_calls`: `90`
- `gov_calls`: `60`
- `total_provider_calls`: `150`
- `solo_calls`: `0`
- `judge_calls`: `0`

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
| `expected_provider_calls_150` | `True` |
| `solo_calls_0` | `True` |
| `judge_calls_0` | `True` |

## Provider Approval Gate

Approval required: `True`
Required statement SHA-256: `c7f4359d7de5fe3b3e29d7bb7e5c70be8d107118076623825879ff28916d4ebc`

Required approval statement:

`I explicitly approve provider calls for WAVE4_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE4_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

## Next Step

Run `python3 -B docs/benchmark/run_wave3_wave4_holo_target_batch_2026_07_01.py --wave wave4 --batch-number 1 --run-live --approval-packet-sha256 APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET --approval-statement "I explicitly approve provider calls for WAVE4_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE4_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."` only when provider calls are explicitly approved.
