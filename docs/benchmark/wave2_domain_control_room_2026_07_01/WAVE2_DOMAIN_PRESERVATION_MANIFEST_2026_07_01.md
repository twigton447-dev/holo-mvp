# Wave 2 Domain Preservation Manifest

Status: `PASS`
Package SHA-256: `fb5b364a87f8479c62ab588a9323eb409d9d3373c7fe72574fcbd464990a4387`
Generated without provider calls: `True`

## Source State

| Item | Value |
| --- | --- |
| Branch | `codex/ap-publication-integration` |
| HEAD | `0a3a5f5d8fe943eb0e597a0a4c821293f1b9cd5e` |
| Dirty paths | `64` |
| Other dirty paths | `1` |

## Artifact Inputs

| Artifact | Status | Package SHA-256 |
| --- | --- | --- |
| `control_room` | `PASS` | `18fb7a9a23aee8682cb10bcf98d85ca9d780178a76dc4f708ba20c4e2d945116` |
| `readiness` | `PASS` | `f58e2474d38183addad8b2e93a6c133f4020d584488631333670cadcf10e292f` |

## Review Groups

| Group | Paths | Statuses |
| --- | ---: | --- |
| `source_scripts_and_tests` | `19` | ` M` |
| `modified_pipeline_scripts` | `0` | `none` |
| `combined_evidence_and_metrics` | `13` | ` M, ??` |
| `batch004_selected_target_stage` | `7` | ` M, ??` |
| `batch005_full_family_remainder_stage` | `2` | ` M` |
| `domain_ledger_outputs` | `4` | ` M` |
| `readiness_outputs` | `2` | ` M` |
| `control_room_outputs` | `16` | ` M` |
| `other_dirty_paths` | `1` | `??` |

## Staging Policy

- Do not use `git add .`.
- Do not use `git add -A`.
- Stage by named group only after review.
- Preserve unrelated dirty paths.

## Group Paths

### source_scripts_and_tests

- ` M` `docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py`
- ` M` `docs/benchmark/build_wave2_domain_completion_audit_2026_07_01.py`
- ` M` `docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py`
- ` M` `docs/benchmark/build_wave2_domain_control_room_2026_07_01.py`
- ` M` `docs/benchmark/build_wave2_domain_operator_handoff_2026_07_01.py`
- ` M` `docs/benchmark/build_wave2_domain_preservation_manifest_2026_07_01.py`
- ` M` `docs/benchmark/build_wave2_domain_selective_staging_plan_2026_07_01.py`
- ` M` `docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py`
- ` M` `docs/benchmark/run_wave2_domain_no_provider_refresh_2026_07_01.py`
- ` M` `docs/benchmark/test_wave2_batch004_provider_approval_gate_2026_07_01.py`
- ` M` `docs/benchmark/test_wave2_batch005_full_family_lock_2026_07_01.py`
- ` M` `docs/benchmark/test_wave2_domain_completion_audit_2026_07_01.py`
- ` M` `docs/benchmark/test_wave2_domain_control_room_2026_07_01.py`
- ` M` `docs/benchmark/test_wave2_domain_operator_handoff_2026_07_01.py`
- ` M` `docs/benchmark/test_wave2_domain_preservation_manifest_2026_07_01.py`
- ` M` `docs/benchmark/test_wave2_statistical_claim_guardrail_2026_07_01.py`
- ` M` `docs/benchmark/test_wave2_timestamp_insensitive_hashes_2026_07_01.py`
- ` M` `docs/benchmark/validate_wave2_no_provider_control_room_2026_07_01.py`
- ` M` `docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py`

### combined_evidence_and_metrics

- ` M` `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/compiled_metrics_package.json`
- ` M` `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/holoverify_metric_summary.csv`
- ` M` `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/holoverify_packet_rows.csv`
- ` M` `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/holoverify_run_summaries.csv`
- ` M` `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/lock_inventory.csv`
- ` M` `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/significance_planner.csv`
- ` M` `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/source_audit.csv`
- `??` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_004_COMBINED_EVIDENCE_MEMO_2026_07_01.json`
- `??` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_004_COMBINED_EVIDENCE_MEMO_2026_07_01.md`
- ` M` `outputs/holoverify_holobuild_metrics_2026_07_01/HoloVerify_HoloBuild_HashLocked_Metrics_2026_07_01.xlsx`
- ` M` `outputs/holoverify_holobuild_metrics_2026_07_01/HoloVerify_HoloBuild_HashLocked_Metrics_2026_07_01.xlsx.inspect.ndjson`
- ` M` `outputs/holoverify_holobuild_metrics_2026_07_01/dashboard_preview.png`
- ` M` `outputs/holoverify_holobuild_metrics_2026_07_01/workbook_manifest.json`

### batch004_selected_target_stage

- ` M` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_LIVE_PREFLIGHT_2026_07_01.json`
- ` M` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_LIVE_PREFLIGHT_2026_07_01.md`
- ` M` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.json`
- ` M` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.md`
- `??` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_SOLO_VS_HOLO_COMPARISON_2026_07_01.json`
- `??` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_SOLO_VS_HOLO_COMPARISON_2026_07_01.md`
- `??` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/live_runs/`

### batch005_full_family_remainder_stage

- ` M` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_005/WAVE2_HOLO_TARGET_BATCH_005_LIVE_PREFLIGHT_2026_07_01.json`
- ` M` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_005/WAVE2_HOLO_TARGET_BATCH_005_LIVE_PREFLIGHT_2026_07_01.md`

### domain_ledger_outputs

- ` M` `docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.json`
- ` M` `docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.md`
- ` M` `docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.json`
- ` M` `docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.md`

### readiness_outputs

- ` M` `docs/benchmark/wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json`
- ` M` `docs/benchmark/wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.md`

### control_room_outputs

- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_COMPLETION_AUDIT_2026_07_01.json`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_COMPLETION_AUDIT_2026_07_01.md`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.json`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.md`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_NO_PROVIDER_REFRESH_RECEIPT_2026_07_01.json`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_NO_PROVIDER_REFRESH_RECEIPT_2026_07_01.md`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_OPERATOR_HANDOFF_2026_07_01.json`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_OPERATOR_HANDOFF_2026_07_01.md`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.json`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.md`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.json`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.md`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01.json`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01.md`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.json`
- ` M` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.md`

### other_dirty_paths

- `??` `docs/benchmark/holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/solo_triage_3mini/`
