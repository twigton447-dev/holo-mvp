# HoloVerify 20-Pair 3-DNA Run

Classification: `INVALID_RUN_HARD_GOV_TOKEN_RATIO_GT_50`
Readiness passed: `False`
Benchmark valid: `False`
Score valid: `False`
Law receipt: `HARD_FAIL_GOV_TOKEN_RATIO_GT_50`

## Calls

- Provider calls: `2`
- Worker calls: `1`
- Gov calls: `1`
- Judge calls: `0`
- Tokens: `2027` input / `749` output / `3432` total
- Gov/Worker token ratio: `0.524656`

## Model Roster

- Actual distinct DNA: `minimax, xai`
- All 3 DNA participated: `False`
- Roster mismatches: `0`

## Readiness Assertions

| Assertion | Value |
| --- | --- |
| `hard_allow_valid_pairs` | `0` |
| `hard_escalate_valid_pairs` | `0` |
| `total_valid_pairs` | `0` |
| `three_dna_inside_holoverify` | `FAIL` |
| `declared_roster_matches_actual_calls` | `PASS` |
| `complete_governance_enforcement` | `PASS` |
| `deterministic_gate_after_every_worker` | `PASS` |
| `gov_receives_gate_results` | `PASS` |
| `artifact_registry_present` | `PASS` |
| `best_artifact_registry_present` | `FAIL` |
| `pinned_best_artifact_present` | `FAIL` |
| `monotonic_preservation_enforced` | `FAIL` |
| `final_selector_present` | `PASS` |
| `guardrail_sibling_correct_for_all_pairs` | `FAIL` |
| `external_and_intra_holo_evidence_separated` | `PASS` |
| `invalid_runs_preserved` | `PASS` |
| `holo_benchmark_laws` | `FAIL` |
| `gov_worker_token_ratio_law` | `FAIL` |
| `worker_prompt_sequence_law` | `PASS` |
| `worker_rotation_law` | `FAIL` |
| `fixed_gov_model_law` | `PASS` |

## Inventory

| Pair | Bucket | Target | Final | Guardrail | External evidence | Intra-Holo evidence | Valid |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `HV-KITC-078` | `hard_allow_false_positive_rescue` | `HV-KITC-078-A` ALLOW | `None` | `None` | 1 | 0 | `False` |
