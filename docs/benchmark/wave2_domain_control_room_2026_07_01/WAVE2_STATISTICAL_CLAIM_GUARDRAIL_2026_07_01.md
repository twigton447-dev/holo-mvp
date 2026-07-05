# Wave 2 Statistical Claim Guardrail

Status: `PASS`
Package SHA-256: `f1234a344da2aedd428a022a2a2190ba77172c6e4a7ffdf06f7c7082ec450474`
Generated without provider calls: `True`

## Claim Boundary

Current claim: `SELECTED_TARGET_EVIDENCE_ONLY_NOT_FULL_FAMILY_STATISTICAL_PROOF`
Statistical proof claim: `NOT_ACHIEVED_BATCH005_NOT_RUN`

## Statistical Lane

| Item | Value |
| --- | ---: |
| Current scored pairs | `37` |
| Current scored packets | `74` |
| Current per-class n | `37` |
| Full-family pairs | `60` |
| Pairs needed for 60/class now | `23` |
| Per-class n after clean Batch004 | `37` |
| Per-class n after clean Batch004+Batch005 | `60` |

## Wave 2 Holo Significance Rows

| Metric | n | Observed errors | Wilson 95 high | Zero-error n for <5% upper |
| --- | ---: | ---: | ---: | ---: |
| `FNR` | `37` | `0` | `0.094058` | `60` |
| `FPR` | `37` | `0` | `0.094058` | `60` |
| `overall_error` | `74` | `0` | `0.04935` | `60` |
| `operational_non_success` | `74` | `0` | `0.04935` | `60` |

## Checks

| Check | Result |
| --- | --- |
| `metrics_generated_without_provider_calls` | `PASS` |
| `metrics_claim_boundary_declared` | `PASS` |
| `ledger_claim_boundary_declared` | `PASS` |
| `current_wave2_holo_metric_rows_are_selected_target_tier` | `PASS` |
| `current_selected_target_counts_37_pairs_74_packets` | `PASS` |
| `current_per_class_n_below_full_family_n` | `PASS` |
| `rule_of_three_threshold_not_met_for_fpr_fnr` | `PASS` |
| `after_batch004_still_below_60_per_class` | `PASS` |
| `batch004_scored_selected_target_evidence` | `PASS` |
| `batch005_needed_for_60_per_class_requires_separate_approval` | `PASS` |
| `batch005_has_no_approval_packet` | `PASS` |
| `domain_rows_are_not_current_per_domain_statistical_proofs` | `PASS` |
| `future_planning_rows_present` | `PASS` |
| `missing_repo_evidence_not_inferred` | `PASS` |
| `provider_boundary_closed` | `PASS` |

## Stop Rules

- This guardrail does not approve provider calls.
- Do not call current Wave 2 selected-target evidence full-family statistical proof.
- Batch004 selected-target evidence is already promoted in this package.
- Do not count Batch005 as live evidence until a separate approval exists and a clean live run completes.
- Do not infer missing repository evidence into proof-credit.
