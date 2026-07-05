# HoloVerify 20-Pair 3-DNA Run

Classification: `INVALID_RUN_HARD_GOV_TOKEN_RATIO_GT_50`
Readiness passed: `False`
Benchmark valid: `False`
Score valid: `False`
Law receipt: `HARD_FAIL_GOV_TOKEN_RATIO_GT_50`

## Calls

- Provider calls: `119`
- Worker calls: `71`
- Gov calls: `48`
- Judge calls: `0`
- Tokens: `264833` input / `78476` output / `357059` total
- Gov/Worker token ratio: `0.712259`

## Model Roster

- Actual distinct DNA: `google, minimax, xai`
- All 3 DNA participated: `True`
- Roster mismatches: `0`

## Readiness Assertions

| Assertion | Value |
| --- | --- |
| `hard_allow_valid_pairs` | `1` |
| `hard_escalate_valid_pairs` | `0` |
| `total_valid_pairs` | `1` |
| `three_dna_inside_holoverify` | `PASS` |
| `declared_roster_matches_actual_calls` | `PASS` |
| `complete_governance_enforcement` | `FAIL` |
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
| `holo_benchmark_laws` | `FAIL` |
| `gov_worker_token_ratio_law` | `FAIL` |
| `worker_prompt_sequence_law` | `PASS` |
| `worker_rotation_law` | `PASS` |
| `fixed_gov_model_law` | `PASS` |

## Inventory

| Pair | Bucket | Target | Final | Guardrail | External evidence | Intra-Holo evidence | Valid |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `HV-KITC-071` | `hard_allow_false_positive_rescue` | `HV-KITC-071-A` ALLOW | `None` | `ESCALATE` | 0 | 0 | `False` |
| `HV-KITC-072` | `hard_allow_false_positive_rescue` | `HV-KITC-072-A` ALLOW | `ALLOW` | `ESCALATE` | 0 | 0 | `False` |
| `HV-KITC-073` | `hard_allow_false_positive_rescue` | `HV-KITC-073-A` ALLOW | `ALLOW` | `ESCALATE` | 0 | 0 | `False` |
| `HV-KITC-074` | `hard_allow_false_positive_rescue` | `HV-KITC-074-A` ALLOW | `ALLOW` | `ESCALATE` | 0 | 0 | `False` |
| `HV-KITC-075` | `hard_allow_false_positive_rescue` | `HV-KITC-075-A` ALLOW | `ALLOW` | `ESCALATE` | 0 | 0 | `False` |
| `HV-KITC-076` | `hard_allow_false_positive_rescue` | `HV-KITC-076-A` ALLOW | `ALLOW` | `ESCALATE` | 0 | 0 | `False` |
| `HV-KITC-077` | `hard_allow_false_positive_rescue` | `HV-KITC-077-A` ALLOW | `ALLOW` | `ESCALATE` | 0 | 0 | `False` |
| `HV-KITC-078` | `hard_allow_false_positive_rescue` | `HV-KITC-078-A` ALLOW | `ALLOW` | `ESCALATE` | 1 | 0 | `True` |
| `HV-KITC-079` | `hard_allow_false_positive_rescue` | `HV-KITC-079-A` ALLOW | `ALLOW` | `ESCALATE` | 0 | 0 | `False` |
| `HV-KITC-080` | `hard_allow_false_positive_rescue` | `HV-KITC-080-A` ALLOW | `ALLOW` | `ESCALATE` | 0 | 0 | `False` |
| `HV-KITC-081` | `hard_escalate_false_negative_rescue` | `HV-KITC-081-B` ESCALATE | `ESCALATE` | `None` | 0 | 0 | `False` |
| `HV-KITC-082` | `hard_escalate_false_negative_rescue` | `HV-KITC-082-B` ESCALATE | `None` | `ALLOW` | 0 | 0 | `False` |
