# BAL100 HoloGov Claim Boundary Patch Regression

Created: 2026-06-20T00:01:26Z

Status: `PASS`

## Claim Boundary Summary

- Correct label: `balanced hard-ALLOW precision inventory`
- Incorrect label: `Holo-vs-solo-collapse win tranche`
- HoloGov result: `5/5 KNEW`
- Active solo result: `15/15 KNEW`
- Solo-collapse win count: `0`
- Public registry: `20` frozen packets, `10_ALLOW_10_ESCALATE`

## Regression Checks

| Check | Result |
| --- | --- |
| `json_valid_core_artifacts` | PASS |
| `public_registry_reached_20` | PASS |
| `public_registry_balanced_10_10` | PASS |
| `added_packet_count_5` | PASS |
| `all_added_truth_allow` | PASS |
| `all_added_judge_pass` | PASS |
| `all_added_hologov_knew` | PASS |
| `all_added_active_solos_knew` | PASS |
| `accounting_update_claim_boundary_present` | PASS |
| `accounting_update_no_holo_over_solo_claim` | PASS |
| `leaderboard_claim_boundary_present` | PASS |
| `leaderboard_no_holo_over_solo_claim` | PASS |
| `scorecard_claim_boundary_present` | PASS |
| `scorecard_no_holo_over_solo_claim` | PASS |
| `ticket_claim_boundary_present` | PASS |
| `ticket_no_holo_over_solo_claim` | PASS |
| `accounting_validation_says_no_collapse_claim` | PASS |
| `accounting_validation_solo_collapse_zero` | PASS |
| `ticket_solo_collapse_zero` | PASS |
| `judge_active_models_consensus_knew` | PASS |
| `judge_hologov_consensus_knew` | PASS |
| `frozen_files_exist` | PASS |
| `official_trace_files_exist` | PASS |
| `frozen_hashes_match_accounting` | PASS |
| `no_new_provider_calls_in_accounting_patch` | PASS |
| `no_judge_rerun_in_accounting_patch` | PASS |
| `no_packet_or_frozen_edits_claimed` | PASS |
| `markdown_claim_boundaries_present` | PASS |
| `markdown_solo_collapse_zero_present` | PASS |
| `markdown_not_claim_present` | PASS |

## Patched Artifacts

- `reports/BAL100_LEADERBOARD_20_ACCOUNTING_UPDATE_001.json`
- `reports/BAL100_LEADERBOARD_20_ACCOUNTING_UPDATE_001.md`
- `reports/BAL100_leaderboard.json`
- `reports/BAL100_leaderboard.md`
- `reports/BAL100_scorecard.json`
- `reports/BAL100_scorecard.md`
- `reports/BAL100_LEADERBOARD_20_ALLOW_BALANCE_TICKET_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_BALANCE_TICKET_001.md`

## Safe Boundaries

No provider calls, new traces, Judge rerun, QA, ablation, packet edits, frozen artifact edits, or push occurred during this patch/regression step.
