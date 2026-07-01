# Wave5 TRES Holo Batch 001 Live Preflight

Status: `PASS`
Batch: `WAVE5_TRES_HOLO_BATCH_001`
Family: `HV-TRES-REP-2026-07-01`
Selection mode: `wave5-domain-5pair-batch`
Freeze root: `3690788df10f817e153113d3eb15f850bb5de2a1a6256253ad8f3031a26238cf`
Root signature: `c4de57749df7f19626047a829d65b08ab096004e86dc9ce5b77742449470445e`

## Expected Calls

- `pairs`: `5`
- `packets`: `10`
- `worker_calls`: `30`
- `gov_calls`: `20`
- `total_provider_calls`: `50`
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
| `expected_provider_calls_50` | `True` |
| `solo_calls_0` | `True` |
| `judge_calls_0` | `True` |

## Provider Approval Gate

Approval required: `True`
Required statement SHA-256: `8ab20ec4cbf93d43701003096470062b231bdc6fd72ec96666a5924c87678c06`

Required approval statement:

`I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_001 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

## Next Step

Run `python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-TRES-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET --approval-statement "I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_001 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."` only when provider calls are explicitly approved.
