# Wave 2 Domain Preservation Manifest

Status: `PASS`
Package SHA-256: `9d7242752c609e97c899035b6f6f3881dbb8e24748e2d2ed2f414529a8a45c1c`
Generated without provider calls: `True`

## Source State

| Item | Value |
| --- | --- |
| Branch | `codex/ap-publication-integration` |
| HEAD | `930ac680cd8b57198a3f8e53eb6176044bf3c64e` |
| Dirty paths | `66` |
| Other dirty paths | `0` |

## Artifact Inputs

| Artifact | Status | Package SHA-256 |
| --- | --- | --- |
| `control_room` | `PASS` | `06110e4c86904686a3ac730620e88d838a0c6221e461fdcca152700a2d7960db` |
| `readiness` | `PASS` | `5a50849c7db8c49b74b7d3eeaabf05d4a3d2292843b626bd65e2a0bd724ec017` |

## Review Groups

| Group | Paths | Statuses |
| --- | ---: | --- |
| `source_scripts_and_tests` | `21` | `A ` |
| `modified_pipeline_scripts` | `5` | `M ` |
| `combined_evidence_and_metrics` | `6` | `M , MM` |
| `batch004_selected_target_stage` | `7` | `A , AM` |
| `batch005_full_family_remainder_stage` | `5` | `A , AM` |
| `domain_ledger_outputs` | `4` | `A , AM` |
| `readiness_outputs` | `2` | `A , AM` |
| `control_room_outputs` | `16` | `A , AM` |
| `other_dirty_paths` | `0` | `none` |

## Staging Policy

- Do not use `git add .`.
- Do not use `git add -A`.
- Stage by named group only after review.
- Preserve unrelated dirty paths.

## Group Paths

### source_scripts_and_tests

- `A ` `docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py`
- `A ` `docs/benchmark/build_wave2_batch004_provider_approval_packet_2026_07_01.py`
- `A ` `docs/benchmark/build_wave2_domain_completion_audit_2026_07_01.py`
- `A ` `docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py`
- `A ` `docs/benchmark/build_wave2_domain_control_room_2026_07_01.py`
- `A ` `docs/benchmark/build_wave2_domain_operator_handoff_2026_07_01.py`
- `A ` `docs/benchmark/build_wave2_domain_preservation_manifest_2026_07_01.py`
- `A ` `docs/benchmark/build_wave2_domain_selective_staging_plan_2026_07_01.py`
- `A ` `docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py`
- `A ` `docs/benchmark/run_wave2_domain_no_provider_refresh_2026_07_01.py`
- `A ` `docs/benchmark/test_wave2_batch004_provider_approval_gate_2026_07_01.py`
- `A ` `docs/benchmark/test_wave2_batch005_full_family_lock_2026_07_01.py`
- `A ` `docs/benchmark/test_wave2_domain_completion_audit_2026_07_01.py`
- `A ` `docs/benchmark/test_wave2_domain_control_room_2026_07_01.py`
- `A ` `docs/benchmark/test_wave2_domain_operator_handoff_2026_07_01.py`
- `A ` `docs/benchmark/test_wave2_domain_preservation_manifest_2026_07_01.py`
- `A ` `docs/benchmark/test_wave2_domain_selective_staging_plan_2026_07_01.py`
- `A ` `docs/benchmark/test_wave2_statistical_claim_guardrail_2026_07_01.py`
- `A ` `docs/benchmark/test_wave2_timestamp_insensitive_hashes_2026_07_01.py`
- `A ` `docs/benchmark/validate_wave2_no_provider_control_room_2026_07_01.py`
- `A ` `docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py`

### modified_pipeline_scripts

- `M ` `docs/benchmark/build_wave2_holo_target_batch_comparison_2026_07_01.py`
- `M ` `docs/benchmark/build_wave2_holo_target_combined_evidence_2026_07_01.py`
- `M ` `docs/benchmark/compile_holoverify_holobuild_metrics_2026_07_01.py`
- `M ` `docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py`
- `M ` `docs/benchmark/stage_wave2_holo_target_batch_2026_07_01.py`

### combined_evidence_and_metrics

- `M ` `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/compiled_metrics_package.json`
- `M ` `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/source_audit.csv`
- `MM` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_COMBINED_EVIDENCE_MEMO_2026_07_01.json`
- `M ` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_COMBINED_EVIDENCE_MEMO_2026_07_01.md`
- `MM` `outputs/holoverify_holobuild_metrics_2026_07_01/HoloVerify_HoloBuild_HashLocked_Metrics_2026_07_01.xlsx`
- `MM` `outputs/holoverify_holobuild_metrics_2026_07_01/HoloVerify_HoloBuild_HashLocked_Metrics_2026_07_01.xlsx.inspect.ndjson`

### batch004_selected_target_stage

- `A ` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_LIVE_PREFLIGHT_2026_07_01.json`
- `A ` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_LIVE_PREFLIGHT_2026_07_01.md`
- `A ` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_PREFLIGHT_2026_07_01.json`
- `A ` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_PREFLIGHT_2026_07_01.md`
- `AM` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.json`
- `A ` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.md`
- `A ` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_REGISTRATION_2026_07_01.json`

### batch005_full_family_remainder_stage

- `AM` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_005/WAVE2_HOLO_TARGET_BATCH_005_LIVE_PREFLIGHT_2026_07_01.json`
- `A ` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_005/WAVE2_HOLO_TARGET_BATCH_005_LIVE_PREFLIGHT_2026_07_01.md`
- `A ` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_005/WAVE2_HOLO_TARGET_BATCH_005_PREFLIGHT_2026_07_01.json`
- `A ` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_005/WAVE2_HOLO_TARGET_BATCH_005_PREFLIGHT_2026_07_01.md`
- `A ` `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_005/WAVE2_HOLO_TARGET_BATCH_005_REGISTRATION_2026_07_01.json`

### domain_ledger_outputs

- `AM` `docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.json`
- `A ` `docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.md`
- `AM` `docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.json`
- `A ` `docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.md`

### readiness_outputs

- `AM` `docs/benchmark/wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json`
- `A ` `docs/benchmark/wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.md`

### control_room_outputs

- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_COMPLETION_AUDIT_2026_07_01.json`
- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_COMPLETION_AUDIT_2026_07_01.md`
- `AM` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.json`
- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.md`
- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_NO_PROVIDER_REFRESH_RECEIPT_2026_07_01.json`
- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_NO_PROVIDER_REFRESH_RECEIPT_2026_07_01.md`
- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_OPERATOR_HANDOFF_2026_07_01.json`
- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_OPERATOR_HANDOFF_2026_07_01.md`
- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.json`
- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.md`
- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.json`
- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.md`
- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01.json`
- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01.md`
- `AM` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.json`
- `A ` `docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.md`
