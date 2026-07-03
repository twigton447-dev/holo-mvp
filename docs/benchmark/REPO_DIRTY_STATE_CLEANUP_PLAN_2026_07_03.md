# Repo Dirty State Cleanup Plan - 2026-07-03

Classification: PATH_SCOPED_CLEANUP_PLAN_NO_STAGE

Repo: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001`
Branch: `codex/ap-publication-integration`
HEAD: `b0d836a99` (`benchmark: preserve solo failure factory batch004 scout`)
Basis: `docs/benchmark/REPO_DIRTY_STATE_TRIAGE_2026_07_03.json`

## Guardrails

- No providers, Holo, solo, Gov, or judges.
- No deletes, reverts, git add ., git add -A, or commits outside the selected cleanup lane.
- Live-run/preflight/runtime payload/Batch004/factory materials remain unstaged pending owner review.
- Every proposed preservation lane is path-scoped using exact paths from the refreshed triage JSON or the cleanup reports generated here.

## Current Counts

Dirty paths excluding cleanup report files: `3427`

| Bucket | Count |
| --- | ---: |
| `website_public_copy_changes` | 3 |
| `fable_review_docs` | 40 |
| `benchmark_ablation_discovery_artifacts` | 37 |
| `run_preflight_artifacts` | 3326 |
| `code_scripts_tests` | 21 |
| `unknown_risky` | 0 |

## Recommended Order

- `lane_00_cleanup_reports`: `ready_to_preserve_when_authorized`; paths `4`; Preserve repo hygiene reports generated during cleanup.
- `lane_01_fable_review_docs`: `ready_to_preserve_after_owner_review`; paths `40`; Docs-only Fable review/design handoff material.
- `lane_02_benchmark_summary_docs`: `ready_to_preserve_after_owner_review`; paths `35`; Benchmark summary, lock, result, registry, and rollup docs that are not live-run/preflight payloads.
- `lane_03_batch004_factory_docs_owner_review`: `hold_owner_review`; paths `2`; Batch004/factory/next-bank docs; do not stage while active Batch004/factory work may be in flight.
- `lane_04_public_copy_owner_review`: `hold_owner_review`; paths `3`; Public website/whitepaper claim-boundary changes; review diffs before staging.
- `lane_05_code_scripts_tests_owner_review`: `hold_owner_review_and_non_provider_validation`; paths `21`; Code/scripts/tests need diff review and non-provider validation before staging.
- `lane_06_live_run_and_preflight_evidence_hold`: `hold_do_not_touch`; paths `1639`; Live-run, preflight, prompt, trace, runtime payload, and generated run artifacts. Preserve only through explicit evidence lane; do not delete.
- `lane_07_temporary_noise_candidates_hold`: `hold_no_delete_without_explicit_approval`; paths `1687`; Preflight prompt probes and preflight_latest material likely to be noise, but no deletion is authorized.
- `lane_08_unknown_risky_hold`: `hold_owner_review`; paths `0`; Unclassified paths.

## Lane Details

### lane_00_cleanup_reports

Status: `ready_to_preserve_when_authorized`

Purpose: Preserve repo hygiene reports generated during cleanup.

Proposed commit: `docs: preserve repo dirty state cleanup plan`

Stage command: `git add -- docs/benchmark/REPO_DIRTY_STATE_TRIAGE_2026_07_03.md docs/benchmark/REPO_DIRTY_STATE_TRIAGE_2026_07_03.json docs/benchmark/REPO_DIRTY_STATE_CLEANUP_PLAN_2026_07_03.md docs/benchmark/REPO_DIRTY_STATE_CLEANUP_PLAN_2026_07_03.json`

Paths:

- `docs/benchmark/REPO_DIRTY_STATE_TRIAGE_2026_07_03.md`
- `docs/benchmark/REPO_DIRTY_STATE_TRIAGE_2026_07_03.json`
- `docs/benchmark/REPO_DIRTY_STATE_CLEANUP_PLAN_2026_07_03.md`
- `docs/benchmark/REPO_DIRTY_STATE_CLEANUP_PLAN_2026_07_03.json`

### lane_01_fable_review_docs

Status: `ready_to_preserve_after_owner_review`

Purpose: Docs-only Fable review/design handoff material.

Proposed commit: `docs: preserve Fable review handoffs`

Stage command: `git add -- docs/FABLE_HOLOENGINE_PRESSURE_TEST_HANDOFF_2026_07_02.json docs/FABLE_HOLOENGINE_PRESSURE_TEST_HANDOFF_2026_07_02.md docs/FABLE_HOLOENGINE_SINGLE_MANDATE_2026_07_02.json docs/FABLE_HOLOENGINE_SINGLE_MANDATE_2026_07_02.md docs/benchmark/FABLE_ATLAS_SEAM_REVIEW_AND_10_PAIR_DESIGNS_2026_07_03.md docs/benchmark/FABLE_ATLAS_V3_SCOUT_REVIEW_2026_07_03.md docs/benchmark/FABLE_BLIND_120_BATCH8_CHECKPOINT_AUDIT_2026_07_03.md docs/benchmark/FABLE_BLIND_120_WRAPPER_GATE_2026_07_03.md docs/benchmark/FABLE_HOLOBUILD_COMPARISON_TEST_DESIGN_2026_07_03.md docs/benchmark/FABLE_SEAM_HUNTER_20_NEW_PAIRS_2026_07_03.md docs/benchmark/FABLE_SEAM_MINING_20_PAIR_DESIGNS_2026_07_03.md docs/benchmark/FABLE_SEAM_MINING_V5_DESIGNS_2026_07_03.md docs/benchmark/FABLE_SELECTOR_REPAIR_PATCH_REVIEW_2026_07_03.md docs/benchmark/FABLE_V6_RESCUE_CANDIDATE_REVIEW_2026_07_03.md docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V3_FABLE_HANDOFF_2026_07_03.json docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V3_FABLE_HANDOFF_2026_07_03.md docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V3_FABLE_SCOUT_GATE_2026_07_03.json docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V3_FABLE_SCOUT_GATE_2026_07_03.md docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V3_FABLE_SUBSET_LIVE_SCOUT_HANDOFF_2026_07_03.json docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V3_FABLE_SUBSET_LIVE_SCOUT_HANDOFF_2026_07_03.md docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V4_FABLE_BANK_LIVE_SCOUT_HANDOFF_2026_07_03.json docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V4_FABLE_BANK_LIVE_SCOUT_HANDOFF_2026_07_03.md docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V5_FABLE_BATCH2_EXACT_LIVE_SCOUT_HANDOFF_2026_07_03.json docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V5_FABLE_BATCH2_EXACT_LIVE_SCOUT_HANDOFF_2026_07_03.md docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V6_FABLE_V5_AFFORDANCE_LIVE_SCOUT_HANDOFF_2026_07_03.json docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V6_FABLE_V5_AFFORDANCE_LIVE_SCOUT_HANDOFF_2026_07_03.md docs/benchmark/HOLOVERIFY_FABLE_BATCH2_EXACT_20PAIR_REGISTRY_2026_07_03.json docs/benchmark/HOLOVERIFY_FABLE_BATCH2_EXACT_20PAIR_REGISTRY_2026_07_03.md docs/benchmark/HOLOVERIFY_FABLE_SEAM_BANK_40_DESIGN_ROLLUP_2026_07_03.json docs/benchmark/HOLOVERIFY_FABLE_SEAM_BANK_40_DESIGN_ROLLUP_2026_07_03.md docs/benchmark/HOLOVERIFY_FABLE_SEAM_BANK_V4_REGISTRY_2026_07_03.json docs/benchmark/HOLOVERIFY_FABLE_SEAM_BANK_V4_REGISTRY_2026_07_03.md docs/benchmark/HOLOVERIFY_FABLE_SEAM_HUNTER_ASSIGNMENT_2026_07_03.json docs/benchmark/HOLOVERIFY_FABLE_SEAM_HUNTER_ASSIGNMENT_2026_07_03.md docs/benchmark/HOLOVERIFY_FABLE_V4_TAXONOMY_AND_V6_AFFORDANCE_SCOUT_PLAN_2026_07_03.json docs/benchmark/HOLOVERIFY_FABLE_V4_TAXONOMY_AND_V6_AFFORDANCE_SCOUT_PLAN_2026_07_03.md docs/benchmark/HOLOVERIFY_FABLE_V6_REVIEW_PROMOTION_DECISION_2026_07_03.json docs/benchmark/HOLOVERIFY_FABLE_V6_REVIEW_PROMOTION_DECISION_2026_07_03.md docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/rescored_post_fable/ATLAS_DISCOVERY_RESCORING_POST_FABLE.json docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/rescored_post_fable/ATLAS_DISCOVERY_RESCORING_POST_FABLE.md`

Paths:

- `docs/FABLE_HOLOENGINE_PRESSURE_TEST_HANDOFF_2026_07_02.json`
- `docs/FABLE_HOLOENGINE_PRESSURE_TEST_HANDOFF_2026_07_02.md`
- `docs/FABLE_HOLOENGINE_SINGLE_MANDATE_2026_07_02.json`
- `docs/FABLE_HOLOENGINE_SINGLE_MANDATE_2026_07_02.md`
- `docs/benchmark/FABLE_ATLAS_SEAM_REVIEW_AND_10_PAIR_DESIGNS_2026_07_03.md`
- `docs/benchmark/FABLE_ATLAS_V3_SCOUT_REVIEW_2026_07_03.md`
- `docs/benchmark/FABLE_BLIND_120_BATCH8_CHECKPOINT_AUDIT_2026_07_03.md`
- `docs/benchmark/FABLE_BLIND_120_WRAPPER_GATE_2026_07_03.md`
- `docs/benchmark/FABLE_HOLOBUILD_COMPARISON_TEST_DESIGN_2026_07_03.md`
- `docs/benchmark/FABLE_SEAM_HUNTER_20_NEW_PAIRS_2026_07_03.md`
- `docs/benchmark/FABLE_SEAM_MINING_20_PAIR_DESIGNS_2026_07_03.md`
- `docs/benchmark/FABLE_SEAM_MINING_V5_DESIGNS_2026_07_03.md`
- `docs/benchmark/FABLE_SELECTOR_REPAIR_PATCH_REVIEW_2026_07_03.md`
- `docs/benchmark/FABLE_V6_RESCUE_CANDIDATE_REVIEW_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V3_FABLE_HANDOFF_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V3_FABLE_HANDOFF_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V3_FABLE_SCOUT_GATE_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V3_FABLE_SCOUT_GATE_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V3_FABLE_SUBSET_LIVE_SCOUT_HANDOFF_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V3_FABLE_SUBSET_LIVE_SCOUT_HANDOFF_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V4_FABLE_BANK_LIVE_SCOUT_HANDOFF_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V4_FABLE_BANK_LIVE_SCOUT_HANDOFF_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V5_FABLE_BATCH2_EXACT_LIVE_SCOUT_HANDOFF_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V5_FABLE_BATCH2_EXACT_LIVE_SCOUT_HANDOFF_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V6_FABLE_V5_AFFORDANCE_LIVE_SCOUT_HANDOFF_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V6_FABLE_V5_AFFORDANCE_LIVE_SCOUT_HANDOFF_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_FABLE_BATCH2_EXACT_20PAIR_REGISTRY_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_FABLE_BATCH2_EXACT_20PAIR_REGISTRY_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_FABLE_SEAM_BANK_40_DESIGN_ROLLUP_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_FABLE_SEAM_BANK_40_DESIGN_ROLLUP_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_FABLE_SEAM_BANK_V4_REGISTRY_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_FABLE_SEAM_BANK_V4_REGISTRY_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_FABLE_SEAM_HUNTER_ASSIGNMENT_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_FABLE_SEAM_HUNTER_ASSIGNMENT_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_FABLE_V4_TAXONOMY_AND_V6_AFFORDANCE_SCOUT_PLAN_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_FABLE_V4_TAXONOMY_AND_V6_AFFORDANCE_SCOUT_PLAN_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_FABLE_V6_REVIEW_PROMOTION_DECISION_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_FABLE_V6_REVIEW_PROMOTION_DECISION_2026_07_03.md`
- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/rescored_post_fable/ATLAS_DISCOVERY_RESCORING_POST_FABLE.json`
- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/rescored_post_fable/ATLAS_DISCOVERY_RESCORING_POST_FABLE.md`

### lane_02_benchmark_summary_docs

Status: `ready_to_preserve_after_owner_review`

Purpose: Benchmark summary, lock, result, registry, and rollup docs that are not live-run/preflight payloads.

Proposed commit: `benchmark: preserve ablation and discovery summaries`

Stage command: `git add -- docs/benchmark/HOLOVERIFY_ATLAS_5FAIL_3MODEL_MAJORITY_ENSEMBLE_ABLATION_LOCK_2026_07_03.json docs/benchmark/HOLOVERIFY_ATLAS_5FAIL_3MODEL_MAJORITY_ENSEMBLE_ABLATION_LOCK_2026_07_03.md docs/benchmark/HOLOVERIFY_ATLAS_5FAIL_MAJORITY_ENSEMBLE_ABLATION_RESULT_2026_07_03.json docs/benchmark/HOLOVERIFY_ATLAS_5FAIL_MAJORITY_ENSEMBLE_ABLATION_RESULT_2026_07_03.md docs/benchmark/HOLOVERIFY_ATLAS_5FAIL_WORKERS_ONLY_ABLATION_RESULT_2026_07_03.json docs/benchmark/HOLOVERIFY_ATLAS_5FAIL_WORKERS_ONLY_ABLATION_RESULT_2026_07_03.md docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V4_V5_RECONCILIATION_2026_07_03.json docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V4_V5_RECONCILIATION_2026_07_03.md docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V6B_FIX034_RESCOUT_HANDOFF_2026_07_03.json docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V6B_FIX034_RESCOUT_HANDOFF_2026_07_03.md docs/benchmark/HOLOVERIFY_ATLAS_SEAM_DISCOVERY_MINIRUN_PLAN_2026_07_03.json docs/benchmark/HOLOVERIFY_ATLAS_SEAM_DISCOVERY_MINIRUN_PLAN_2026_07_03.md docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_ABLATION_SEQUENCE_LOCK_2026_07_03.json docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_ABLATION_SEQUENCE_LOCK_2026_07_03.md docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_BASELINE_POSTHOC_SUMMARY_2026_07_03.json docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_BASELINE_POSTHOC_SUMMARY_2026_07_03.md docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_FAILURE_PACKET_FILTER_2026_07_03.json docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_FAILURE_PACKET_FILTER_2026_07_03.md docs/benchmark/HOLOVERIFY_REPO_SEAM_INVENTORY_2026_07_03.json docs/benchmark/HOLOVERIFY_REPO_SEAM_INVENTORY_2026_07_03.md docs/benchmark/HOLOVERIFY_SOLO_COLLAPSE_HOLO_WIN_PAIR_REGISTRY_2026_07_03.json docs/benchmark/HOLOVERIFY_SOLO_COLLAPSE_HOLO_WIN_PAIR_REGISTRY_2026_07_03.md docs/benchmark/HOLOVERIFY_SOLO_COLLAPSE_HOLO_WIN_REGISTRY_2026_07_03.json docs/benchmark/HOLOVERIFY_SOLO_COLLAPSE_HOLO_WIN_REGISTRY_2026_07_03.md docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/ATLAS_SCOUT_CANDIDATE_RULE_VALIDATION_2026_07_03.json docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/rescored_post_fable/v1_rescore.json docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/rescored_post_fable/v2_rescore.json docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/ARCHITECTURE_ABLATION_CATEGORY_COMPARISON_2026_07_02.json docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/ARCHITECTURE_ABLATION_CATEGORY_COMPARISON_2026_07_02.md docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/ARCHITECTURE_ISOLATION_LADDER_STRATEGY_LOCK_2026_07_02.json docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/ARCHITECTURE_ISOLATION_LADDER_STRATEGY_LOCK_2026_07_02.md docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/randomized_corpus_balanced_sample_20260702/KITA_RANDOMIZED_CORPUS_BALANCED_ABLATION_PROVIDER_APPROVAL_PACKET_2026_07_02.json docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/randomized_corpus_balanced_sample_20260702/KITA_RANDOMIZED_CORPUS_BALANCED_ABLATION_PROVIDER_APPROVAL_PACKET_2026_07_02.md docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/randomized_corpus_balanced_sample_20260702/KITA_RANDOMIZED_CORPUS_BALANCED_SAMPLE_LOCK_2026_07_02.json docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/randomized_corpus_balanced_sample_20260702/KITA_RANDOMIZED_CORPUS_BALANCED_SAMPLE_LOCK_2026_07_02.md`

Paths:

- `docs/benchmark/HOLOVERIFY_ATLAS_5FAIL_3MODEL_MAJORITY_ENSEMBLE_ABLATION_LOCK_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_ATLAS_5FAIL_3MODEL_MAJORITY_ENSEMBLE_ABLATION_LOCK_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_ATLAS_5FAIL_MAJORITY_ENSEMBLE_ABLATION_RESULT_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_ATLAS_5FAIL_MAJORITY_ENSEMBLE_ABLATION_RESULT_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_ATLAS_5FAIL_WORKERS_ONLY_ABLATION_RESULT_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_ATLAS_5FAIL_WORKERS_ONLY_ABLATION_RESULT_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V4_V5_RECONCILIATION_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V4_V5_RECONCILIATION_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V6B_FIX034_RESCOUT_HANDOFF_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_ATLAS_DISCOVERY_V6B_FIX034_RESCOUT_HANDOFF_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_ATLAS_SEAM_DISCOVERY_MINIRUN_PLAN_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_ATLAS_SEAM_DISCOVERY_MINIRUN_PLAN_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_ABLATION_SEQUENCE_LOCK_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_ABLATION_SEQUENCE_LOCK_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_BASELINE_POSTHOC_SUMMARY_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_BASELINE_POSTHOC_SUMMARY_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_FAILURE_PACKET_FILTER_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_FAILURE_PACKET_FILTER_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_REPO_SEAM_INVENTORY_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_REPO_SEAM_INVENTORY_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_SOLO_COLLAPSE_HOLO_WIN_PAIR_REGISTRY_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_SOLO_COLLAPSE_HOLO_WIN_PAIR_REGISTRY_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_SOLO_COLLAPSE_HOLO_WIN_REGISTRY_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_SOLO_COLLAPSE_HOLO_WIN_REGISTRY_2026_07_03.md`
- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/ATLAS_SCOUT_CANDIDATE_RULE_VALIDATION_2026_07_03.json`
- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/rescored_post_fable/v1_rescore.json`
- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/rescored_post_fable/v2_rescore.json`
- `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/ARCHITECTURE_ABLATION_CATEGORY_COMPARISON_2026_07_02.json`
- `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/ARCHITECTURE_ABLATION_CATEGORY_COMPARISON_2026_07_02.md`
- `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/ARCHITECTURE_ISOLATION_LADDER_STRATEGY_LOCK_2026_07_02.json`
- `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/ARCHITECTURE_ISOLATION_LADDER_STRATEGY_LOCK_2026_07_02.md`
- `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/randomized_corpus_balanced_sample_20260702/KITA_RANDOMIZED_CORPUS_BALANCED_ABLATION_PROVIDER_APPROVAL_PACKET_2026_07_02.json`
- `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/randomized_corpus_balanced_sample_20260702/KITA_RANDOMIZED_CORPUS_BALANCED_ABLATION_PROVIDER_APPROVAL_PACKET_2026_07_02.md`
- `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/randomized_corpus_balanced_sample_20260702/KITA_RANDOMIZED_CORPUS_BALANCED_SAMPLE_LOCK_2026_07_02.json`
- `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/randomized_corpus_balanced_sample_20260702/KITA_RANDOMIZED_CORPUS_BALANCED_SAMPLE_LOCK_2026_07_02.md`

### lane_03_batch004_factory_docs_owner_review

Status: `hold_owner_review`

Purpose: Batch004/factory/next-bank docs; do not stage while active Batch004/factory work may be in flight.

Stage command: `DO_NOT_STAGE_YET`

Paths:

- `docs/benchmark/HOLOVERIFY_SOLO_FAILURE_FACTORY_SEAM_MINING_NEXT_BANK_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_SOLO_FAILURE_FACTORY_SEAM_MINING_NEXT_BANK_2026_07_03.md`

### lane_04_public_copy_owner_review

Status: `hold_owner_review`

Purpose: Public website/whitepaper claim-boundary changes; review diffs before staging.

Stage command: `DO_NOT_STAGE_YET`

Diff summary:

- `docs/whitepaper.md`: Narrows public benchmark language, removes current public statistical risk-bound claims, and moves to blind-gate replication boundary.
- `frontend/benchmark.html`: Version 7.54; replaces public 614/614 rate tables with under-blind-gate-review claim boundary and disconfirmation plan.
- `frontend/whitepaper.html`: Version 7.84; mirrors narrowed whitepaper claim boundary in rendered HTML.

Paths:

- `docs/whitepaper.md`
- `frontend/benchmark.html`
- `frontend/whitepaper.html`

### lane_05_code_scripts_tests_owner_review

Status: `hold_owner_review_and_non_provider_validation`

Purpose: Code/scripts/tests need diff review and non-provider validation before staging.

Stage command: `DO_NOT_STAGE_YET`

Tracked diff summary:

- `docs/benchmark/three_mini_seam_scout_2026_06_29.py`: Adds evidence text extraction from rationale/cited artifacts, tightens candidate criteria to wrong-verdict or heavy both-sibling non-KNEW signal, adds --out-root, and updates selection-rule text.

Allowed non-provider validation examples:

- `python3 -m py_compile docs/benchmark/three_mini_seam_scout_2026_06_29.py`
- `python3 -m py_compile <selected untracked scripts>`
- `pytest tests/test_kita_randomized_corpus_balanced_ablation.py -q if dependencies are local and no provider calls are triggered`

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
- `docs/benchmark/build_randomized_corpus_balanced_ablation_sample_2026_07_02.py`
- `docs/benchmark/filter_holoverify_blind_120_solo_failure_packets_2026_07_03.py`
- `docs/benchmark/preflight_holoverify_atlas_seam_discovery_minirun_2026_07_03.py`
- `docs/benchmark/rescore_holoverify_atlas_seam_discovery_scouts_2026_07_03.py`
- `docs/benchmark/run_holoverify_atlas_5fail_majority_ensemble_ablation_2026_07_03.py`
- `docs/benchmark/run_holoverify_atlas_5fail_workers_only_ablation_2026_07_03.py`
- `docs/benchmark/run_kita_ablation_series_solo_one_shot_2026_07_02.py`
- `docs/benchmark/run_kita_randomized_corpus_balanced_ablation_2026_07_02.py`
- `docs/benchmark/score_holoverify_atlas_5fail_majority_ensemble_ablation_2026_07_03.py`
- `docs/benchmark/score_holoverify_atlas_5fail_workers_only_ablation_2026_07_03.py`
- `docs/benchmark/validate_holoverify_atlas_scout_candidate_rule_2026_07_03.py`
- `tests/test_kita_randomized_corpus_balanced_ablation.py`

### lane_06_live_run_and_preflight_evidence_hold

Status: `hold_do_not_touch`

Purpose: Live-run, preflight, prompt, trace, runtime payload, and generated run artifacts. Preserve only through explicit evidence lane; do not delete.

Stage command: `DO_NOT_STAGE_YET`

Paths: `1639` exact paths are stored in the JSON plan under `lanes.lane_06_live_run_and_preflight_evidence_hold.paths`.

### lane_07_temporary_noise_candidates_hold

Status: `hold_no_delete_without_explicit_approval`

Purpose: Preflight prompt probes and preflight_latest material likely to be noise, but no deletion is authorized.

Stage command: `DO_NOT_STAGE_YET`

Paths: `1687` exact paths are stored in the JSON plan under `lanes.lane_07_temporary_noise_candidates_hold.paths`.

### lane_08_unknown_risky_hold

Status: `hold_owner_review`

Purpose: Unclassified paths.

Stage command: `DO_NOT_STAGE_YET`

Paths:

- None

## Immediate Rule

If authorized, stage and commit only lane_00_cleanup_reports first using exact listed paths. Otherwise continue owner review without staging.

