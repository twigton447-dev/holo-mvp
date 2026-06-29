# Solo One-Shot 3-Mini Baseline Audit

| Check | Value |
| --- | --- |
| audit_status | `PASS` |
| solo_provider_calls | 120 |
| packet_count | 40 |
| models_per_packet | 3 |
| no_gov_calls | True |
| no_holo_state_brief | True |
| no_gov_baton | True |
| no_artifact_registry | True |
| no_final_selector | True |
| no_holo_deterministic_normalization_as_rescue | True |
| no_judges | True |
| no_packet_drift_from_frozen_holo_run | True |
| no_prompt_leakage_of_expected_verdicts | True |
| deterministic_audit_post_hoc_only | True |
| provider_failures | 0 |
| prompt_files_scanned | 240 |
| forbidden_prompt_hits | 0 |

## Model Coverage

| Model | Ran Once On Every Packet |
| --- | --- |
| xai/grok-3-mini | True |
| google/gemini-2.5-flash-lite | True |
| minimax/MiniMax-M2.5-highspeed | True |

## Notes

The solo baseline was preserved as emitted. Deterministic audit was applied only after provider output to classify verdict, evidence, and schema admissibility. The solo lane had no Gov, no state brief, no Gov baton, no artifact registry, no final selector, no Holo normalization rescue, and no judges.
