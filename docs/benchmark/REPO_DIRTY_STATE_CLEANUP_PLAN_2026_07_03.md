# Repo Dirty State Cleanup Plan - 2026-07-03

Classification: POST_PUBLIC_COPY_CLEANUP_PATH_SCOPED_PLAN

Repo: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001`
Branch: `codex/ap-publication-integration`
HEAD: `f4c712b12` (`benchmark: add solo failure holo rescue shortlist`)

## Remaining Counts

Remaining dirty paths excluding cleanup reports: `3411`

| Bucket | Count |
| --- | ---: |
| `website_public_copy_changes` | 0 |
| `fable_review_docs` | 0 |
| `benchmark_ablation_discovery_artifacts` | 2 |
| `run_preflight_artifacts` | 3388 |
| `code_scripts_tests` | 21 |
| `unknown_risky` | 0 |

## Current Lanes

- `lane_00_cleanup_reports`: `preserve_refresh`; paths `4`
- `lane_01_fable_review_docs`: `preserved`; paths `0`
- `lane_02_benchmark_summary_docs_remaining`: `hold_owner_review`; paths `2`
- `lane_03_public_copy`: `preserved`; paths `0`
- `lane_04_code_scripts_tests`: `hold_owner_review_and_non_provider_validation`; paths `21`
- `lane_05_live_preflight_evidence`: `hold_do_not_touch`; paths `1641`
- `lane_06_temporary_noise_candidates`: `hold_no_delete_without_explicit_approval`; paths `1747`
- `lane_07_unknown_risky`: `hold_owner_review`; paths `0`

## Immediate Rule

Stop automatic staging here. Remaining paths are code/script/test changes, owner-review benchmark docs, live/preflight evidence, or temporary-noise candidates.

