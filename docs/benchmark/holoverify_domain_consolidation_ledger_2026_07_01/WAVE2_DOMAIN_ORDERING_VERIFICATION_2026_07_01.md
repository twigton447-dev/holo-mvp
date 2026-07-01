# Wave 2 Domain Ordering Verification

Classification: `WAVE2_DOMAIN_ORDERING_VERIFICATION_NO_PROVIDER_2026_07_01`
Status: `PASS`
Package SHA-256: `0a93c2dcdc98f6df2a0ab08d82a66d0389aa56669493b5448f3dd2348b29a435`
Generated without provider calls: `True`

## Gate State

Current phase: `PRE_BATCH_004_LIVE`
Next allowed live batch: `WAVE2_HOLO_TARGET_BATCH_004`
Batch 005 gate: `LOCKED_UNTIL_BATCH_004_LIVE_COMPARISON_PROMOTION_AND_EXPLICIT_PROVIDER_APPROVAL`

## Counts

| Item | Value |
| --- | ---: |
| Completed comparison batches | `001, 002, 003` |
| Scored pairs | `27` |
| Target pair pool | `37` |
| Remaining selected-target pairs | `10` |
| Full-family remainder pairs | `23` |

## Batch Gates

| Batch | Mode | Pairs | Packets | Provider calls if live | Providers called | Live started | Preflight | Live gate |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| `WAVE2_HOLO_TARGET_BATCH_004` | `target-selection` | `10` | `20` | `100` | `0` | `False` | `PASS` | `PASS` |
| `WAVE2_HOLO_TARGET_BATCH_005` | `full-family-remainder` | `23` | `46` | `230` | `0` | `False` | `PASS` | `LOCKED` |

## Checks

| Check | Result |
| --- | --- |
| `freeze_scope_60_pairs_120_packets` | `True` |
| `target_selection_has_37_pairs` | `True` |
| `completed_comparison_batches_are_001_002_003` | `True` |
| `combined_memo_no_provider` | `True` |
| `domain_ledger_no_provider` | `True` |
| `scored_pairs_27_packets_54` | `True` |
| `batch_004_comparison_absent` | `True` |
| `batch_004_effective_selection_mode_target_selection` | `True` |
| `batch_004_selected_pairs_match_remaining_target_pool` | `True` |
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
| `batch_005_live_execution_gate_locked_until_batch004_promotion` | `True` |
| `batch_005_not_started` | `True` |
| `batch_005_root_signature_present` | `True` |
| `ledger_selected_targets_fully_staged_not_scored` | `True` |
| `ledger_statistical_lane_27_37_60` | `True` |
| `ledger_full_family_remainder_fully_staged_not_scored` | `True` |

## Next Gates

1. Batch 004 live Holo is the only next live execution lane, and it still requires explicit provider-call approval.
2. Batch 004 comparison and combined-memo promotion must happen before Batch 005 can become eligible.
3. Batch 005 remains full-family remainder only; it is not selected-target evidence and is not scored proof while staged.

## Root Signatures

- Batch 004 live preflight: `bfa320f216b25ac3f5f9c321573ae56270a66292906f0038531ae12bce5c0a3b`
- Batch 005 live preflight: `3cf24480f79bde31d58774d5e2a32290f97f2c1ab9d5088b9f1eaf676909b46b`
