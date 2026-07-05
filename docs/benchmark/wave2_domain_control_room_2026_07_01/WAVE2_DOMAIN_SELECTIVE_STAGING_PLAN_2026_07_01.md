# Wave 2 Domain Selective Staging Plan

Status: `PASS`
Package SHA-256: `c0c1bab57dba1b8914e98cfa5e5bb11671207490a4a7cef0fd4c411c327d041b`
Generated without provider calls: `True`
Preservation manifest SHA-256: `fb5b364a87f8479c62ab588a9323eb409d9d3373c7fe72574fcbd464990a4387`

## Policy

- This artifact does not stage files.
- Do not use `git add .`.
- Do not use `git add -A`.
- Review and stage by named group only.

## Group Commands

1. `source_scripts_and_tests` - `19` paths

```bash
git add -- 'docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py' 'docs/benchmark/build_wave2_domain_completion_audit_2026_07_01.py' 'docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py' 'docs/benchmark/build_wave2_domain_control_room_2026_07_01.py' 'docs/benchmark/build_wave2_domain_operator_handoff_2026_07_01.py' 'docs/benchmark/build_wave2_domain_preservation_manifest_2026_07_01.py' 'docs/benchmark/build_wave2_domain_selective_staging_plan_2026_07_01.py' 'docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py' 'docs/benchmark/run_wave2_domain_no_provider_refresh_2026_07_01.py' 'docs/benchmark/test_wave2_batch004_provider_approval_gate_2026_07_01.py' 'docs/benchmark/test_wave2_batch005_full_family_lock_2026_07_01.py' 'docs/benchmark/test_wave2_domain_completion_audit_2026_07_01.py' 'docs/benchmark/test_wave2_domain_control_room_2026_07_01.py' 'docs/benchmark/test_wave2_domain_operator_handoff_2026_07_01.py' 'docs/benchmark/test_wave2_domain_preservation_manifest_2026_07_01.py' 'docs/benchmark/test_wave2_statistical_claim_guardrail_2026_07_01.py' 'docs/benchmark/test_wave2_timestamp_insensitive_hashes_2026_07_01.py' 'docs/benchmark/validate_wave2_no_provider_control_room_2026_07_01.py' 'docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py'
```

2. `combined_evidence_and_metrics` - `13` paths

```bash
git add -- 'docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/compiled_metrics_package.json' 'docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/holoverify_metric_summary.csv' 'docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/holoverify_packet_rows.csv' 'docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/holoverify_run_summaries.csv' 'docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/lock_inventory.csv' 'docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/significance_planner.csv' 'docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/source_audit.csv' 'docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_004_COMBINED_EVIDENCE_MEMO_2026_07_01.json' 'docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_004_COMBINED_EVIDENCE_MEMO_2026_07_01.md' 'outputs/holoverify_holobuild_metrics_2026_07_01/HoloVerify_HoloBuild_HashLocked_Metrics_2026_07_01.xlsx' 'outputs/holoverify_holobuild_metrics_2026_07_01/HoloVerify_HoloBuild_HashLocked_Metrics_2026_07_01.xlsx.inspect.ndjson' 'outputs/holoverify_holobuild_metrics_2026_07_01/dashboard_preview.png' 'outputs/holoverify_holobuild_metrics_2026_07_01/workbook_manifest.json'
```

3. `batch004_selected_target_stage` - `7` paths

```bash
git add -- 'docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_LIVE_PREFLIGHT_2026_07_01.json' 'docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_LIVE_PREFLIGHT_2026_07_01.md' 'docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.json' 'docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.md' 'docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_SOLO_VS_HOLO_COMPARISON_2026_07_01.json' 'docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_SOLO_VS_HOLO_COMPARISON_2026_07_01.md' 'docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/live_runs/'
```

4. `batch005_full_family_remainder_stage` - `2` paths

```bash
git add -- 'docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_005/WAVE2_HOLO_TARGET_BATCH_005_LIVE_PREFLIGHT_2026_07_01.json' 'docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_005/WAVE2_HOLO_TARGET_BATCH_005_LIVE_PREFLIGHT_2026_07_01.md'
```

5. `domain_ledger_outputs` - `4` paths

```bash
git add -- 'docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.json' 'docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.md' 'docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.json' 'docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.md'
```

6. `readiness_outputs` - `2` paths

```bash
git add -- 'docs/benchmark/wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json' 'docs/benchmark/wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.md'
```

7. `control_room_outputs` - `16` paths

```bash
git add -- 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_COMPLETION_AUDIT_2026_07_01.json' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_COMPLETION_AUDIT_2026_07_01.md' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.json' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.md' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_NO_PROVIDER_REFRESH_RECEIPT_2026_07_01.json' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_NO_PROVIDER_REFRESH_RECEIPT_2026_07_01.md' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_OPERATOR_HANDOFF_2026_07_01.json' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_OPERATOR_HANDOFF_2026_07_01.md' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.json' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.md' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.json' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.md' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01.json' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01.md' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.json' 'docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.md'
```

8. `other_dirty_paths` - `1` paths

```bash
git add -- 'docs/benchmark/holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/solo_triage_3mini/'
```

## Checks

| Check | Result |
| --- | --- |
| `all_manifest_paths_represented` | `PASS` |
| `commands_are_path_limited` | `PASS` |
| `no_git_add_all_command` | `PASS` |
| `other_dirty_paths_reported_for_manual_exclusion` | `PASS` |
| `preservation_manifest_pass` | `PASS` |
