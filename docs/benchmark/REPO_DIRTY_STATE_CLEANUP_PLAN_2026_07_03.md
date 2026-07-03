# Repo Dirty State Cleanup Plan - 2026-07-03

Classification: POST_CLEANUP_PATH_SCOPED_PLAN

Repo: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001`
Branch: `codex/ap-publication-integration`
HEAD: `fb6d4da9d` (`benchmark: freeze solo failure factory batch005`)
Basis: `docs/benchmark/REPO_DIRTY_STATE_TRIAGE_2026_07_03.json`

## Completed Cleanup Commits Visible At Refresh

- `fb6d4da9d benchmark: freeze solo failure factory batch005`
- `771d2988c benchmark: preserve ablation and discovery summaries`
- `d89427bbe docs: preserve Fable review handoffs`
- `0ae4a8f23 docs: preserve repo dirty state cleanup plan`
- `b0d836a99 benchmark: preserve solo failure factory batch004 scout`

## Guardrails

- No providers, Holo, solo, Gov, or judges.
- No deletes, reverts, git add ., or git add -A.
- Live-run/preflight/runtime payload/Batch004/factory materials remain unstaged pending owner review.
- Remaining public-copy and code/script/test changes require owner review before staging.
- Temporary-noise candidates are not deletion targets without explicit approval.

## Remaining Counts

Remaining dirty paths excluding cleanup report files: `3442`

| Bucket | Count |
| --- | ---: |
| `website_public_copy_changes` | 3 |
| `fable_review_docs` | 0 |
| `benchmark_ablation_discovery_artifacts` | 7 |
| `run_preflight_artifacts` | 3408 |
| `code_scripts_tests` | 24 |
| `unknown_risky` | 0 |

## Current Lanes

- `lane_00_cleanup_reports`: `preserved_then_refreshed`; paths `4`; Repo hygiene reports generated and then refreshed after cleanup commits.
- `lane_01_fable_review_docs`: `preserved_in_commit_d89427bbe`; paths `0`; Docs-only Fable review/design handoff material.
- `lane_02_benchmark_summary_docs_remaining`: `hold_owner_review_for_new_or_remaining_docs`; paths `7`; Remaining benchmark/discovery summaries after the preserved ablation/discovery commit; new files may have appeared during cleanup.
- `lane_03_public_copy_owner_review`: `hold_owner_review`; paths `3`; Public website/whitepaper claim-boundary changes; review diffs before staging.
- `lane_04_code_scripts_tests_owner_review`: `hold_owner_review_and_non_provider_validation`; paths `24`; Code/scripts/tests need diff review and non-provider validation before staging.
- `lane_05_live_run_and_preflight_evidence_hold`: `hold_do_not_touch`; paths `1661`; Live-run, preflight, prompt, trace, runtime payload, and generated run artifacts. Preserve only through explicit evidence lane; do not delete.
- `lane_06_temporary_noise_candidates_hold`: `hold_no_delete_without_explicit_approval`; paths `1747`; Preflight prompt probes and preflight_latest material likely to be noise, but no deletion is authorized.
- `lane_07_unknown_risky_hold`: `hold_owner_review`; paths `0`; Unclassified paths.

## Lane Details

### lane_00_cleanup_reports

Status: `preserved_then_refreshed`

Purpose: Repo hygiene reports generated and then refreshed after cleanup commits.

Stage command: `git add -- docs/benchmark/REPO_DIRTY_STATE_TRIAGE_2026_07_03.md docs/benchmark/REPO_DIRTY_STATE_TRIAGE_2026_07_03.json docs/benchmark/REPO_DIRTY_STATE_CLEANUP_PLAN_2026_07_03.md docs/benchmark/REPO_DIRTY_STATE_CLEANUP_PLAN_2026_07_03.json`

Paths:

- `docs/benchmark/REPO_DIRTY_STATE_TRIAGE_2026_07_03.md`
- `docs/benchmark/REPO_DIRTY_STATE_TRIAGE_2026_07_03.json`
- `docs/benchmark/REPO_DIRTY_STATE_CLEANUP_PLAN_2026_07_03.md`
- `docs/benchmark/REPO_DIRTY_STATE_CLEANUP_PLAN_2026_07_03.json`

### lane_01_fable_review_docs

Status: `preserved_in_commit_d89427bbe`

Purpose: Docs-only Fable review/design handoff material.

Stage command: `NO_REMAINING_PATHS`

Paths:

- None

### lane_02_benchmark_summary_docs_remaining

Status: `hold_owner_review_for_new_or_remaining_docs`

Purpose: Remaining benchmark/discovery summaries after the preserved ablation/discovery commit; new files may have appeared during cleanup.

Stage command: `DO_NOT_STAGE_YET`

Paths:

- `docs/benchmark/HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH005_PACKET_FREEZE_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH005_PACKET_FREEZE_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_SOLO_FAILURE_FACTORY_SEAM_MINING_NEXT_BANK_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_SOLO_FAILURE_FACTORY_SEAM_MINING_NEXT_BANK_2026_07_03.md`
- `docs/benchmark/holoverify_solo_failure_factory_batch005_2026_07_03/holoverify_solo_failure_factory_batch005_hash_manifest_2026_07_03.json`
- `docs/benchmark/holoverify_solo_failure_factory_batch005_2026_07_03/holoverify_solo_failure_factory_batch005_runtime_manifest_2026_07_03.json`
- `docs/benchmark/holoverify_solo_failure_factory_batch005_2026_07_03/holoverify_solo_failure_factory_batch005_scoring_map_2026_07_03.json`

### lane_03_public_copy_owner_review

Status: `hold_owner_review`

Purpose: Public website/whitepaper claim-boundary changes; review diffs before staging.

Stage command: `DO_NOT_STAGE_YET`

Paths:

- `docs/whitepaper.md`
- `frontend/benchmark.html`
- `frontend/whitepaper.html`

### lane_04_code_scripts_tests_owner_review

Status: `hold_owner_review_and_non_provider_validation`

Purpose: Code/scripts/tests need diff review and non-provider validation before staging.

Stage command: `DO_NOT_STAGE_YET`

Tracked diff summary:

- `docs/benchmark/three_mini_seam_scout_2026_06_29.py`: Tracked patch changes evidence text extraction, candidate criteria, --out-root, and selection-rule text.

Paths:

- `docs/benchmark/three_mini_seam_scout_2026_06_29.py`
- `docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_2026_07_03.py`
- `docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v2_2026_07_03.py`
- `docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v3_2026_07_03.py`
- `docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v3_fable_subset_2026_07_03.py`
- `docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v4_fable_bank_2026_07_03.py`
- `docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v5_fable_batch2_exact_2026_07_03.py`
- `docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v6_fable_v5_affordance_2026_07_03.py`
- `docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v6b_fix034_2026_07_03.py`
- `docs/benchmark/build_holoverify_solo_failure_factory_batch005_2026_07_03.py`
- `docs/benchmark/build_randomized_corpus_balanced_ablation_sample_2026_07_02.py`
- `docs/benchmark/filter_holoverify_blind_120_solo_failure_packets_2026_07_03.py`
- `docs/benchmark/preflight_holoverify_atlas_seam_discovery_minirun_2026_07_03.py`
- `docs/benchmark/rescore_holoverify_atlas_seam_discovery_scouts_2026_07_03.py`
- `docs/benchmark/run_holoverify_atlas_5fail_majority_ensemble_ablation_2026_07_03.py`
- `docs/benchmark/run_holoverify_atlas_5fail_workers_only_ablation_2026_07_03.py`
- `docs/benchmark/run_holoverify_solo_failure_factory_batch005_solo_scout_2026_07_03.py`
- `docs/benchmark/run_kita_ablation_series_solo_one_shot_2026_07_02.py`
- `docs/benchmark/run_kita_randomized_corpus_balanced_ablation_2026_07_02.py`
- `docs/benchmark/score_holoverify_atlas_5fail_majority_ensemble_ablation_2026_07_03.py`
- `docs/benchmark/score_holoverify_atlas_5fail_workers_only_ablation_2026_07_03.py`
- `docs/benchmark/score_holoverify_solo_failure_factory_batch005_solo_scout_2026_07_03.py`
- `docs/benchmark/validate_holoverify_atlas_scout_candidate_rule_2026_07_03.py`
- `tests/test_kita_randomized_corpus_balanced_ablation.py`

### lane_05_live_run_and_preflight_evidence_hold

Status: `hold_do_not_touch`

Purpose: Live-run, preflight, prompt, trace, runtime payload, and generated run artifacts. Preserve only through explicit evidence lane; do not delete.

Stage command: `DO_NOT_STAGE_YET`

Paths: `1661` exact paths are stored in the JSON plan under `lanes.lane_05_live_run_and_preflight_evidence_hold.paths`.

### lane_06_temporary_noise_candidates_hold

Status: `hold_no_delete_without_explicit_approval`

Purpose: Preflight prompt probes and preflight_latest material likely to be noise, but no deletion is authorized.

Stage command: `DO_NOT_STAGE_YET`

Paths: `1747` exact paths are stored in the JSON plan under `lanes.lane_06_temporary_noise_candidates_hold.paths`.

### lane_07_unknown_risky_hold

Status: `hold_owner_review`

Purpose: Unclassified paths.

Stage command: `DO_NOT_STAGE_YET`

Paths:

- None

## Immediate Rule

Stop automatic staging here. Remaining paths are owner-review, live/preflight evidence, code/script/test changes, public-copy changes, or temporary-noise candidates requiring explicit deletion approval.

