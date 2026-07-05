# Wave 2 Domain Ordering Verification

Classification: `WAVE2_DOMAIN_ORDERING_VERIFICATION_NO_PROVIDER_2026_07_01`
Status: `PASS`
Package SHA-256: `091aaafaf70ca6413614a54497ddb794be58552aae608635794bbe504abcee2b`
Generated without provider calls: `True`

## Gate State

Current phase: `POST_BATCH_004_EVIDENCE_LOCKED`
Next allowed live batch: `WAVE2_HOLO_TARGET_BATCH_005`
Batch 005 gate: `EVIDENCE_UNLOCKED_PENDING_EXPLICIT_PROVIDER_APPROVAL`

## Counts

| Item | Value |
| --- | ---: |
| Completed comparison batches | `001, 002, 003, 004` |
| Scored pairs | `37` |
| Target pair pool | `37` |
| Remaining selected-target pairs | `0` |
| Full-family remainder pairs | `23` |

## Batch Gates

| Batch | Mode | Pairs | Packets | Provider calls if live | Providers called | Live started | Preflight | Live gate |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| `WAVE2_HOLO_TARGET_BATCH_004` | `target-selection` | `10` | `20` | `100` | `0` | `False` | `PASS` | `PASS` |
| `WAVE2_HOLO_TARGET_BATCH_005` | `full-family-remainder` | `23` | `46` | `230` | `0` | `False` | `PASS` | `PASS` |

## Checks

| Check | Result |
| --- | --- |
| `freeze_scope_60_pairs_120_packets` | `True` |
| `target_selection_has_37_pairs` | `True` |
| `completed_comparison_batches_are_001_002_003_004` | `True` |
| `combined_memo_no_provider` | `True` |
| `domain_ledger_no_provider` | `True` |
| `scored_pairs_37_packets_74` | `True` |
| `batch_004_comparison_present` | `True` |
| `batch_004_effective_selection_mode_target_selection` | `True` |
| `batch_004_selected_pairs_match_scored_comparison` | `True` |
| `batch_004_expected_counts_10_pairs_20_packets_100_calls` | `True` |
| `batch_004_preflights_passed` | `True` |
| `batch_004_live_execution_gate_pass` | `True` |
| `batch_004_not_started` | `True` |
| `batch_004_root_signature_present` | `True` |
| `batch_005_comparison_absent` | `True` |
| `batch_005_selection_mode_full_family_remainder` | `True` |
| `batch_005_selected_pairs_match_full_family_remainder` | `True` |
| `batch_005_no_selected_target_overlap` | `True` |
| `batch_005_expected_counts_23_pairs_46_packets_230_calls` | `True` |
| `batch_005_preflights_passed` | `True` |
| `batch_005_live_execution_gate_pass_after_batch004_promotion` | `True` |
| `batch_005_not_started` | `True` |
| `batch_005_root_signature_present` | `True` |
| `ledger_selected_targets_fully_scored` | `True` |
| `ledger_statistical_lane_37_37_60` | `True` |
| `ledger_full_family_remainder_fully_staged_not_scored` | `True` |

## Next Gates

1. Batch 004 live Holo evidence has been promoted into the selected-target comparison and combined memo.
2. Batch 005 is the next eligible live lane, but it still requires a separate provider approval packet and explicit approval.
3. Batch 005 remains full-family remainder only; it is not selected-target evidence and is not scored proof while staged.

## Root Signatures

- Batch 004 live preflight: `7e9e5dd2b0fff1f8614aa23c0d4570b828c2b31e671748de2001b96e9942dbd9`
- Batch 005 live preflight: `a99fba06753da20549e6fea991c2c2a3d829e07aaf4541813ffa31a1f484c12d`
