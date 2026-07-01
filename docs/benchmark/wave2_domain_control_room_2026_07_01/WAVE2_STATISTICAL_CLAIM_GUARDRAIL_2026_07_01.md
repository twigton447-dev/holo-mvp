# Wave 2 Statistical Claim Guardrail

Status: `PASS`
Package SHA-256: `086f77cfae5273fc4835bb1be0137db558be55cc242cc2775ed1984cc2f9286c`
Generated without provider calls: `True`

## Claim Boundary

Current claim: `SELECTED_TARGET_EVIDENCE_ONLY_NOT_FULL_FAMILY_STATISTICAL_PROOF`
Statistical proof claim: `NOT_ACHIEVED_BATCH005_LOCKED`

## Statistical Lane

| Item | Value |
| --- | ---: |
| Current scored pairs | `27` |
| Current scored packets | `54` |
| Current per-class n | `27` |
| Full-family pairs | `60` |
| Pairs needed for 60/class now | `33` |
| Per-class n after clean Batch004 | `37` |
| Per-class n after clean Batch004+Batch005 | `60` |

## Wave 2 Holo Significance Rows

| Metric | n | Observed errors | Wilson 95 high | Zero-error n for <5% upper |
| --- | ---: | ---: | ---: | ---: |
| `FNR` | `27` | `0` | `0.124555` | `60` |
| `FPR` | `27` | `0` | `0.124555` | `60` |
| `overall_error` | `54` | `0` | `0.066414` | `60` |
| `operational_non_success` | `54` | `0` | `0.066414` | `60` |

## Checks

| Check | Result |
| --- | --- |
| `metrics_generated_without_provider_calls` | `PASS` |
| `metrics_claim_boundary_declared` | `PASS` |
| `ledger_claim_boundary_declared` | `PASS` |
| `current_wave2_holo_metric_rows_are_selected_target_tier` | `PASS` |
| `current_selected_target_counts_27_pairs_54_packets` | `PASS` |
| `current_per_class_n_below_full_family_n` | `PASS` |
| `rule_of_three_threshold_not_met_for_fpr_fnr` | `PASS` |
| `after_batch004_still_below_60_per_class` | `PASS` |
| `batch004_staged_not_scored` | `PASS` |
| `batch005_needed_for_60_per_class_is_locked` | `PASS` |
| `batch005_has_no_approval_packet` | `PASS` |
| `domain_rows_are_not_current_per_domain_statistical_proofs` | `PASS` |
| `future_planning_rows_present` | `PASS` |
| `missing_repo_evidence_not_inferred` | `PASS` |
| `provider_boundary_closed` | `PASS` |

## Stop Rules

- This guardrail does not approve provider calls.
- Do not call current Wave 2 selected-target evidence full-family statistical proof.
- Do not count Batch004 as live evidence until explicit approval and a clean live result exist.
- Do not count Batch005 as live evidence until Batch004 is promoted and a separate approval exists.
- Do not infer missing repository evidence into proof-credit.
