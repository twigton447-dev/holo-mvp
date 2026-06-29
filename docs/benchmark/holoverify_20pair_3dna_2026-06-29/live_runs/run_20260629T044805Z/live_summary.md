# HoloVerify 20-Pair 3-DNA Run

Classification: `HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED`
Readiness passed: `False`
Benchmark valid: `False`
Score valid: `False`
Law receipt: `HOLO_BENCHMARK_LAWS_PASS`

## Calls

- Provider calls: `100`
- Worker calls: `60`
- Gov calls: `40`
- Judge calls: `0`
- Tokens: `134859` input / `53704` output / `200361` total
- Gov/Worker token ratio: `0.14684`

## Model Roster

- Actual distinct DNA: `google, minimax, xai`
- All 3 DNA participated: `True`
- Roster mismatches: `0`

## Readiness Assertions

| Assertion | Value |
| --- | --- |
| `hard_allow_valid_pairs` | `8` |
| `hard_escalate_valid_pairs` | `0` |
| `total_valid_pairs` | `8` |
| `three_dna_inside_holoverify` | `PASS` |
| `declared_roster_matches_actual_calls` | `PASS` |
| `complete_governance_enforcement` | `PASS` |
| `deterministic_gate_after_every_worker` | `PASS` |
| `gov_receives_gate_results` | `PASS` |
| `artifact_registry_present` | `PASS` |
| `best_artifact_registry_present` | `FAIL` |
| `pinned_best_artifact_present` | `PASS` |
| `monotonic_preservation_enforced` | `FAIL` |
| `final_selector_present` | `PASS` |
| `guardrail_sibling_correct_for_all_pairs` | `FAIL` |
| `external_and_intra_holo_evidence_separated` | `PASS` |
| `invalid_runs_preserved` | `PASS` |
| `holo_benchmark_laws` | `PASS` |
| `gov_worker_token_ratio_law` | `PASS` |
| `worker_prompt_sequence_law` | `PASS` |
| `worker_rotation_law` | `PASS` |
| `fixed_gov_model_law` | `PASS` |

## Inventory

| Pair | Bucket | Target | Final | Guardrail | External evidence | Intra-Holo evidence | Valid |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022` | `hard_allow_false_positive_rescue` | `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` ALLOW | `None` | `None` | 1 | 4 | `False` |
| `HV-KITC-078` | `hard_allow_false_positive_rescue` | `HV-KITC-078-A` ALLOW | `ALLOW` | `ESCALATE` | 1 | 0 | `True` |
| `HV-KITC-081` | `hard_allow_false_positive_rescue` | `HV-KITC-081-A` ALLOW | `ALLOW` | `ESCALATE` | 1 | 3 | `True` |
| `HV-KITC-082` | `hard_allow_false_positive_rescue` | `HV-KITC-082-A` ALLOW | `ALLOW` | `ESCALATE` | 3 | 3 | `True` |
| `HV-KITC-084` | `hard_allow_false_positive_rescue` | `HV-KITC-084-A` ALLOW | `ALLOW` | `ESCALATE` | 2 | 4 | `True` |
| `HV-KITC-086` | `hard_allow_false_positive_rescue` | `HV-KITC-086-A` ALLOW | `ALLOW` | `ESCALATE` | 3 | 2 | `True` |
| `HV-KITC-087` | `hard_allow_false_positive_rescue` | `HV-KITC-087-A` ALLOW | `ALLOW` | `ESCALATE` | 3 | 3 | `True` |
| `HV-KITC-088` | `hard_allow_false_positive_rescue` | `HV-KITC-088-A` ALLOW | `None` | `ESCALATE` | 3 | 5 | `False` |
| `HV-KITC-089` | `hard_allow_false_positive_rescue` | `HV-KITC-089-A` ALLOW | `ALLOW` | `ESCALATE` | 2 | 3 | `True` |
| `HV-KITC-090` | `hard_allow_false_positive_rescue` | `HV-KITC-090-A` ALLOW | `ALLOW` | `ESCALATE` | 1 | 4 | `True` |
