# Wave 3 Holo Target Batch 001 Live Preflight

Status: `PASS`
Batch: `WAVE3_HOLO_TARGET_BATCH_001`
Freeze root: `ac44c5d69ad73c64dcae1591e37cc9ade8a80ed5e71a05786cd2490a445c2dd5`
Root signature: `4fa40081fa4d54c56c6fbf463a70a98d90fa62d8d27b12b67e59bc23ef271ba6`

## Expected Calls

- `pairs`: `12`
- `packets`: `24`
- `worker_calls`: `72`
- `gov_calls`: `48`
- `total_provider_calls`: `120`
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
| `expected_provider_calls_120` | `True` |
| `solo_calls_0` | `True` |
| `judge_calls_0` | `True` |

## Provider Approval Gate

Approval required: `True`
Required statement SHA-256: `6c176e893866e5fb9d7bb63144f40a5c6254816132e70ed931f751f1dc6dbc6d`

Required approval statement:

`I explicitly approve provider calls for WAVE3_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE3_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

## Next Step

Run `python3 -B docs/benchmark/run_wave3_wave4_holo_target_batch_2026_07_01.py --wave wave3 --batch-number 1 --run-live --approval-packet-sha256 APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET --approval-statement "I explicitly approve provider calls for WAVE3_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE3_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."` only when provider calls are explicitly approved.
