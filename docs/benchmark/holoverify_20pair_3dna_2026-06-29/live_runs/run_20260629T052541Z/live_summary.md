# HoloVerify 20-Pair 3-DNA Run

Classification: `HOLOVERIFY_20PAIR_3DNA_INCOMPLETE_OR_REPAIR_REQUIRED`
Readiness passed: `False`
Benchmark valid: `False`
Score valid: `False`
Law receipt: `HOLO_BENCHMARK_LAWS_PASS`

## Calls

- Provider calls: `10`
- Worker calls: `6`
- Gov calls: `4`
- Judge calls: `0`
- Tokens: `13468` input / `3980` output / `18446` total
- Gov/Worker token ratio: `0.102702`

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
| `complete_governance_enforcement` | `PASS` |
| `deterministic_gate_after_every_worker` | `PASS` |
| `gov_receives_gate_results` | `PASS` |
| `artifact_registry_present` | `PASS` |
| `best_artifact_registry_present` | `PASS` |
| `pinned_best_artifact_present` | `PASS` |
| `monotonic_preservation_enforced` | `PASS` |
| `final_selector_present` | `PASS` |
| `guardrail_sibling_correct_for_all_pairs` | `PASS` |
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
| `HV-KITC-042` | `hard_allow_false_positive_rescue` | `HV-KITC-042-A` ALLOW | `ALLOW` | `ESCALATE` | 1 | 0 | `True` |
