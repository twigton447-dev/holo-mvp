# Wave 2 Domain Control Room

Status: `PASS`
Package SHA-256: `18fb7a9a23aee8682cb10bcf98d85ca9d780178a76dc4f708ba20c4e2d945116`
Generated without provider calls: `True`

## Current State

| Item | Value |
| --- | --- |
| Current phase | `POST_BATCH_004_EVIDENCE_LOCKED` |
| Next allowed live batch | `WAVE2_HOLO_TARGET_BATCH_005` |
| Scored batches | `001-004` |
| Current scored pairs | `37` |
| Current scored packets correct/admissible | `74/74` |
| Selected-target pool | `37` pairs |
| Per-class n now | `37` |
| Per-class n after clean Batch004 | `37` |
| Per-class n after clean Batch004+Batch005 | `60` |
| Pairs still needed for 60/class now | `23` |
| Pairs still needed for 60/class after Batch004 | `23` |

## Domain Map

| Domain | Frozen pairs | Scored target | Batch004 target staged | Batch005 remainder staged | Unstaged after Batch005 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Data privacy / customer data release controls | `20` | `12` | `0` | `8` | `0` |
| Finance close / revenue / expense recognition controls | `20` | `16` | `0` | `4` | `0` |
| HR / payroll / workforce controls | `20` | `9` | `0` | `11` | `0` |

## Gates

| Gate | State | Pairs | Packets | Expected provider calls | Live gate |
| --- | --- | ---: | ---: | ---: | --- |
| Batch004 | `HISTORICAL_BATCH004_APPROVAL_PACKET_BATCH004_ALREADY_PROMOTED` | `10` | `20` | `100` | `PASS` |
| Batch005 | `EVIDENCE_UNLOCKED_PENDING_SEPARATE_PROVIDER_APPROVAL_PACKET` | `23` | `46` | `230` | `PASS` |

## Batch004 Approval

Approval packet status: `NOT_READY`
Approval granted by packet: `False`
Approval packet SHA-256: `a94bb0b83c000e9ce17723526545e240323686fc21da9f9d4f95ec9590f3d5dd`

Required approval statement:

`I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_004 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Run command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py --batch-number 4 --run-live --approval-packet-sha256 a94bb0b83c000e9ce17723526545e240323686fc21da9f9d4f95ec9590f3d5dd --approval-statement "I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_004 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Next Actions

1. `run_full_no_provider_refresh`

```bash
python3 -B docs/benchmark/run_wave2_domain_no_provider_refresh_2026_07_01.py
```

2. `validate_no_provider_control_room`

```bash
python3 -B docs/benchmark/validate_wave2_no_provider_control_room_2026_07_01.py
```

3. `build_statistical_claim_guardrail_after_control_room`

```bash
python3 -B docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py
```

4. `build_preservation_manifest_after_refresh`

```bash
python3 -B docs/benchmark/build_wave2_domain_preservation_manifest_2026_07_01.py
```

5. `build_selective_staging_plan_after_preservation`

```bash
python3 -B docs/benchmark/build_wave2_domain_selective_staging_plan_2026_07_01.py
```

6. `build_operator_handoff_after_staging_plan`

```bash
python3 -B docs/benchmark/build_wave2_domain_operator_handoff_2026_07_01.py
```

7. `refresh_no_provider_verifiers`

```bash
python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py
python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py
python3 -B docs/benchmark/build_wave2_batch004_provider_approval_packet_2026_07_01.py
python3 -B docs/benchmark/build_wave2_domain_control_room_2026_07_01.py
python3 -B docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py
```

8. `batch004_live_complete_and_promoted`

```bash
python3 -B docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py --batch-number 4 --run-live --approval-packet-sha256 a94bb0b83c000e9ce17723526545e240323686fc21da9f9d4f95ec9590f3d5dd --approval-statement "I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_004 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

9. `post_batch004_promotion_after_clean_live`

```bash
python3 -B docs/benchmark/build_wave2_holo_target_batch_comparison_2026_07_01.py --batch-number 4
python3 -B docs/benchmark/build_wave2_holo_target_combined_evidence_2026_07_01.py --batches 1 2 3 4
python3 -B docs/benchmark/compile_holoverify_holobuild_metrics_2026_07_01.py
node docs/benchmark/build_holoverify_holobuild_metrics_workbook_2026_07_01.mjs
python3 -B docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py
python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py
python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py
python3 -B docs/benchmark/build_wave2_domain_control_room_2026_07_01.py
python3 -B docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py
```

10. `batch005_requires_separate_future_approval`
   Blocked by: `None`

## Stop Rules

- This artifact does not approve provider calls.
- Run Batch 004 only after the exact approval statement and exact approval packet SHA are supplied.
- Do not run Batch 005 until a separate Batch 005 approval packet and explicit approval exist.
- Do not run solo or judge lanes from this control-room lane.
- Preserve selected-target evidence separately from full-family statistical proof until Batch 005 has live evidence.

## Checks

| Check | Result |
| --- | --- |
| `ledger_generated_without_provider_calls` | `PASS` |
| `ordering_pass` | `PASS` |
| `readiness_pass` | `PASS` |
| `readiness_no_failed_checks` | `PASS` |
| `declared_source_package_hashes_valid` | `PASS` |
| `current_phase_post_batch004_evidence_locked` | `PASS` |
| `next_allowed_live_batch005` | `PASS` |
| `compiled_metrics_no_provider` | `PASS` |
| `combined_memo_no_provider` | `PASS` |
| `combined_memo_no_judges` | `PASS` |
| `batch004_approval_packet_preserved` | `PASS` |
| `batch004_approval_does_not_self_grant` | `PASS` |
| `batch004_approval_hash_valid` | `PASS` |
| `batch004_approval_markdown_matches_packet_state` | `PASS` |
| `batch004_run_command_not_current_permission` | `PASS` |
| `batch004_live_gate_pass` | `PASS` |
| `batch004_no_provider_calls_started` | `PASS` |
| `batch004_expected_provider_calls_100` | `PASS` |
| `batch004_selected_target_count_10` | `PASS` |
| `batch005_gate_expected_evidence_unlocked_state` | `PASS` |
| `batch005_live_gate_pass` | `PASS` |
| `batch005_lock_blockers_cleared` | `PASS` |
| `batch005_no_provider_calls_started` | `PASS` |
| `batch005_expected_provider_calls_230` | `PASS` |
| `batch005_remainder_count_23` | `PASS` |
| `batch005_has_no_approval_packet` | `PASS` |
| `current_scored_pairs_37` | `PASS` |
| `selected_target_lane_closes_after_batch004` | `PASS` |
| `full_family_remainder_staged_to_60` | `PASS` |
| `full_family_no_unstaged_pairs_after_batch005` | `PASS` |
| `domain_rows_all_staged_after_batch005` | `PASS` |
