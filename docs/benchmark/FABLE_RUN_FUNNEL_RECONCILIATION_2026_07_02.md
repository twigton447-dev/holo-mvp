# Fable Run Funnel Reconciliation

Status: NO_PROVIDER_AUDIT

This inventory reconciles complete, invalid, blocked, and unknown run-result artifacts found under `docs/benchmark`.

## Summary

- Result files scanned: `119`.
- Status counts: `{'complete': 72, 'invalid_or_blocked': 46, 'unknown': 1}`.
- Reason-family counts: `{'gov_contract_or_parse': 2, 'provider_failure': 42, 'verdict_or_admissibility': 1, 'worker_contract_or_parse': 1}`.
- Packet counts by status: `{'complete': 682, 'invalid_or_blocked': 392, 'unknown': 10}`.

## Important Caveat

This is an artifact inventory, not a proof that each complete file belongs in the public denominator. The public denominator still needs a strict inclusion manifest that maps every counted packet to exactly one locked run.

## Invalid Or Blocked Examples

| Status | Reason | Classification | Packets | Path |
| --- | --- | --- | ---: | --- |
| invalid_or_blocked | gov_contract_or_parse | INVALID_OR_INCOMPLETE_FULL_HOLOVERIFY_ARCH_022 | 1 | `docs/benchmark/full_holoverify_arch_kitc_022_2026-06-28/live_runs/run_20260628T234411Z/live_results.json` |
| invalid_or_blocked | gov_contract_or_parse | INVALID_OR_INCOMPLETE_FULL_HOLOVERIFY_ARCH_022 | 1 | `docs/benchmark/hard_allow_fp_5pair_full_arch_freeze_2026-06-28/evidence/HV-KITC-022/run_20260628T234411Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED | 26 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/frozen_complete_run_20260629T052822Z/evidence/preserved_invalid_runs/run_20260629T042132Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED | 20 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/frozen_complete_run_20260629T052822Z/evidence/preserved_invalid_runs/run_20260629T044805Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED | 20 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/frozen_complete_run_20260629T052822Z/evidence/preserved_invalid_runs/run_20260629T050310Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED | 1 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/frozen_complete_run_20260629T052822Z/evidence/preserved_invalid_runs/run_20260629T052724Z/live_results.json` |
| invalid_or_blocked | provider_failure | INVALID_RUN_PROVIDER_FAILURE_BEFORE_COMPLETION | 10 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T020437Z/live_results.json` |
| invalid_or_blocked | provider_failure | INVALID_RUN_HARD_GOV_TOKEN_RATIO_GT_50 | 40 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T021923Z/live_results.json` |
| invalid_or_blocked | provider_failure | INVALID_RUN_HARD_GOV_TOKEN_RATIO_GT_50 | 24 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T025609Z/live_results.json` |
| invalid_or_blocked | provider_failure | INVALID_RUN_HARD_GOV_TOKEN_RATIO_GT_50 | 2 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T032816Z/live_results.json` |
| invalid_or_blocked | provider_failure | INVALID_RUN_TERMINAL_CALL_FAILURE_BEFORE_COMPLETION |  | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T035458Z/live_results.json` |
| invalid_or_blocked | provider_failure | INVALID_RUN_HARD_GOV_TOKEN_RATIO_GT_50 | 1 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T040339Z/live_results.json` |
| invalid_or_blocked | provider_failure | INVALID_RUN_HARD_GOV_TOKEN_RATIO_GT_50 | 1 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T040621Z/live_results.json` |
| invalid_or_blocked | provider_failure | INVALID_RUN_BENCHMARK_LAW_VIOLATION | 1 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T040751Z/live_results.json` |
| invalid_or_blocked | provider_failure | INVALID_RUN_BENCHMARK_LAW_VIOLATION | 1 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T041022Z/live_results.json` |
| invalid_or_blocked | provider_failure | INVALID_RUN_BENCHMARK_LAW_VIOLATION | 2 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T041214Z/live_results.json` |
| invalid_or_blocked | provider_failure | INVALID_RUN_BENCHMARK_LAW_VIOLATION | 2 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T041638Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED | 2 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T041804Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED | 2 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T041955Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED | 26 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T042132Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED | 4 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T044055Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED | 5 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T044404Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED | 20 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T044805Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED | 20 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T050310Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED | 2 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T052541Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED | 1 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T052724Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_AP_REPLICATION_HOLO_INVALID_OR_INCOMPLETE | 9 | `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2/run_20260629T235436Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_AP_REPLICATION_HOLO_INVALID_OR_INCOMPLETE | 25 | `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2/run_20260630T032421Z/live_results.json` |
| invalid_or_blocked | provider_failure | COMMERCE_OPENAI_W2_BATCHED_HOLO_BATCH_INVALID_OR_INCOMPLETE | 14 | `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_1/run_20260630T222408Z/batch_results.json` |
| invalid_or_blocked | provider_failure | COMMERCE_OPENAI_W2_BATCHED_HOLO_BATCH_INVALID_OR_INCOMPLETE | 6 | `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_1/run_20260630T223800Z/batch_results.json` |
| invalid_or_blocked | provider_failure | COMMERCE_OPENAI_W2_BATCHED_HOLO_BATCH_INVALID_OR_INCOMPLETE | 5 | `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_1/run_20260630T230945Z/batch_results.json` |
| invalid_or_blocked | provider_failure | AP_OPENAI_W2_CANARY_INVALID_OR_INCOMPLETE | 1 | `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2/run_20260629T153048Z/canary_results.json` |
| invalid_or_blocked | provider_failure | AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_CANARY_INVALID_OR_INCOMPLETE | 6 | `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260629T191023Z/canary_results.json` |
| invalid_or_blocked | provider_failure | AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_CANARY_INVALID_OR_INCOMPLETE | 12 | `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260629T193200Z/canary_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_AP_REPLICATION_HOLO_INVALID_OR_INCOMPLETE | 27 | `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs/run_20260629T105111Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_AP_REPLICATION_HOLO_INVALID_OR_INCOMPLETE | 9 | `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs/run_20260629T110920Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_AP_REPLICATION_HOLO_INVALID_OR_INCOMPLETE | 6 | `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs/run_20260629T111600Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_AP_REPLICATION_HOLO_INVALID_OR_INCOMPLETE | 2 | `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs_openai_w2/run_20260629T132430Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_AP_REPLICATION_HOLO_INVALID_OR_INCOMPLETE | 1 | `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs_openai_w2/run_20260629T134644Z/live_results.json` |
| invalid_or_blocked | provider_failure | HOLOVERIFY_AP_REPLICATION_HOLO_INVALID_OR_INCOMPLETE | 1 | `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs_openai_w2/run_20260629T140257Z/live_results.json` |

## Complete Examples

| Status | Classification | Packets | Path |
| --- | --- | ---: | --- |
| complete | FULL_HOLOVERIFY_ARCH_021_COMPLETE | 2 | `docs/benchmark/full_holoverify_arch_kitc_021_2026-06-28/live_runs/run_20260628T233949Z/live_results.json` |
| complete | FULL_HOLOVERIFY_ARCH_022_COMPLETE | 2 | `docs/benchmark/full_holoverify_arch_kitc_022_2026-06-28/live_runs/run_20260628T234645Z/live_results.json` |
| complete | FULL_HOLOVERIFY_ARCH_042_COMPLETE | 2 | `docs/benchmark/full_holoverify_arch_kitc_042_2026-06-28/live_runs/run_20260628T233631Z/live_results.json` |
| complete | FULL_HOLOVERIFY_ARCH_047_COMPLETE | 2 | `docs/benchmark/full_holoverify_arch_kitc_047_2026-06-28/live_runs/run_20260628T232707Z/live_results.json` |
| complete | FULL_HOLOVERIFY_ARCH_082_COMPLETE | 2 | `docs/benchmark/full_holoverify_arch_kitc_082_2026-06-28/live_runs/run_20260628T232009Z/live_results.json` |
| complete | FULL_HOLOVERIFY_ARCH_021_COMPLETE | 2 | `docs/benchmark/hard_allow_fp_5pair_full_arch_freeze_2026-06-28/evidence/HV-KITC-021/run_20260628T233949Z/live_results.json` |
| complete | FULL_HOLOVERIFY_ARCH_022_COMPLETE | 2 | `docs/benchmark/hard_allow_fp_5pair_full_arch_freeze_2026-06-28/evidence/HV-KITC-022/run_20260628T234645Z/live_results.json` |
| complete | FULL_HOLOVERIFY_ARCH_042_COMPLETE | 2 | `docs/benchmark/hard_allow_fp_5pair_full_arch_freeze_2026-06-28/evidence/HV-KITC-042/run_20260628T233631Z/live_results.json` |
| complete | FULL_HOLOVERIFY_ARCH_047_COMPLETE | 2 | `docs/benchmark/hard_allow_fp_5pair_full_arch_freeze_2026-06-28/evidence/HV-KITC-047/run_20260628T232707Z/live_results.json` |
| complete | FULL_HOLOVERIFY_ARCH_082_COMPLETE | 2 | `docs/benchmark/hard_allow_fp_5pair_full_arch_freeze_2026-06-28/evidence/HV-KITC-082/run_20260628T232009Z/live_results.json` |
| complete | HOLOVERIFY_20PAIR_3DNA_COMPLETE | 40 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/frozen_complete_run_20260629T052822Z/evidence/holo_run/live_results.json` |
| complete | HOLOVERIFY_20PAIR_3DNA_COMPLETE | 40 | `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T052822Z/live_results.json` |
| complete | COMMERCE_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_CANARY_COMPLETE | 6 | `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z/canary_results.json` |
| complete | COMMERCE_OPENAI_W2_BATCHED_HOLO_BATCH_COMPLETE | 14 | `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_1/run_20260630T232312Z/batch_results.json` |
| complete | COMMERCE_OPENAI_W2_BATCHED_HOLO_BATCH_COMPLETE | 14 | `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_2/run_20260630T233428Z/batch_results.json` |
| complete | COMMERCE_OPENAI_W2_BATCHED_HOLO_BATCH_COMPLETE | 12 | `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_3/run_20260630T234405Z/batch_results.json` |
| complete | AP_OPENAI_W2_CANARY_READY_FOR_FULL_FAMILY_RUN | 2 | `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2/run_20260629T164305Z/canary_results.json` |
| complete | HOLOVERIFY_AP_REPLICATION_HOLO_COMPLETE | 40 | `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs_openai_w2/run_20260629T201840Z/live_results.json` |
| complete | IT_ACCESS_OPENAI_W2_BATCHED_HOLO_BATCH_COMPLETE | 14 | `docs/benchmark/holoverify_it_access_replication_2026-06-30/holo_live_runs_openai_w2_batched/batch_1/run_20260701T003031Z/batch_results.json` |
| complete | IT_ACCESS_OPENAI_W2_BATCHED_HOLO_BATCH_COMPLETE | 14 | `docs/benchmark/holoverify_it_access_replication_2026-06-30/holo_live_runs_openai_w2_batched/batch_2/run_20260701T005249Z/batch_results.json` |
| complete | IT_ACCESS_OPENAI_W2_BATCHED_HOLO_BATCH_COMPLETE | 2 | `docs/benchmark/holoverify_it_access_replication_2026-06-30/holo_live_runs_openai_w2_batched/replacement_015r1/run_20260701T012935Z/batch_results.json` |
| complete | WAVE2_HOLO_TARGET_BATCH_001_COMPLETE | 18 | `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_001/live_runs/run_20260701T042037Z/live_results.json` |
| complete | WAVE2_HOLO_TARGET_BATCH_002_COMPLETE | 18 | `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_002/live_runs/run_20260701T045827Z/live_results.json` |
| complete | WAVE2_HOLO_TARGET_BATCH_003_COMPLETE | 18 | `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_003/live_runs/run_20260701T054545Z/live_results.json` |
| complete | WAVE2_HOLO_TARGET_BATCH_004_COMPLETE | 20 | `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/live_runs/run_20260701T132715Z/live_results.json` |
| complete | WAVE2_HOLO_TARGET_BATCH_005_COMPLETE | 46 | `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_005/live_runs/run_20260701T141727Z/live_results.json` |
| complete | WAVE3_HOLO_TARGET_BATCH_001_COMPLETE | 24 | `docs/benchmark/holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/holo_target_batches/wave3_holo_target_batch_001/live_runs/run_20260701T163353Z/live_results.json` |
| complete | WAVE4_HOLO_TARGET_BATCH_001_COMPLETE | 30 | `docs/benchmark/holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/holo_target_batches/wave4_holo_target_batch_001/live_runs/run_20260701T163526Z/live_results.json` |
| complete | WAVE5_CLAD_HOLO_BATCH_001_COMPLETE | 10 | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_clad_holo_batch_001/live_runs/run_20260701T214106Z/live_results.json` |
| complete | WAVE5_CLAD_HOLO_BATCH_002_COMPLETE | 10 | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_clad_holo_batch_002/live_runs/run_20260701T215907Z/live_results.json` |
| complete | WAVE5_CLAD_HOLO_BATCH_003_COMPLETE | 10 | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_clad_holo_batch_003/live_runs/run_20260701T225854Z/live_results.json` |
| complete | WAVE5_CLAD_HOLO_BATCH_004_COMPLETE | 10 | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_clad_holo_batch_004/live_runs/run_20260701T231050Z/live_results.json` |
| complete | WAVE5_LREG_HOLO_BATCH_001_COMPLETE | 10 | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_lreg_holo_batch_001/live_runs/run_20260701T204454Z/live_results.json` |
| complete | WAVE5_LREG_HOLO_BATCH_002_COMPLETE | 10 | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_lreg_holo_batch_002/live_runs/run_20260701T205533Z/live_results.json` |
| complete | WAVE5_LREG_HOLO_BATCH_003_COMPLETE | 10 | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_lreg_holo_batch_003/live_runs/run_20260701T210231Z/live_results.json` |
| complete | WAVE5_LREG_HOLO_BATCH_003_COMPLETE | 10 | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_lreg_holo_batch_003/live_runs/run_20260701T210956Z/live_results.json` |
| complete | WAVE5_LREG_HOLO_BATCH_004_COMPLETE | 10 | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_lreg_holo_batch_004/live_runs/run_20260701T212207Z/live_results.json` |
| complete | WAVE5_MEDX_HOLO_BATCH_001_COMPLETE | 10 | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_medx_holo_batch_001/live_runs/run_20260701T190553Z/live_results.json` |
| complete | WAVE5_MEDX_HOLO_BATCH_002_COMPLETE | 10 | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_medx_holo_batch_002/live_runs/run_20260701T192304Z/live_results.json` |
| complete | WAVE5_MEDX_HOLO_BATCH_003_COMPLETE | 10 | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_medx_holo_batch_003/live_runs/run_20260701T193310Z/live_results.json` |
