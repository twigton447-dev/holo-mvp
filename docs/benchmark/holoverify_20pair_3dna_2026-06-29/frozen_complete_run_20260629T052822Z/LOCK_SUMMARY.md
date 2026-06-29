# HoloVerify 20-Pair / 3-DNA Freeze

Classification: `HOLOVERIFY_20PAIR_3DNA_COMPLETE_HASH_FREEZE`
Status: `FROZEN_FOR_SOLO_ONE_SHOT_BASELINE`
Root signature: `dcd9f17a76eef5bbe3b2a20195835a98b3694b511aa66d313fa4a91e7f2a17f1`
Source run: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T052822Z`
Holo trace hash: `dbb1d040c516af4989d488a07c44917a3582dc17da75c9fc517b4472228f1201`

## Scope

- Pairs: `20`
- Packets: `40`
- Holo provider calls: `200`
- Worker calls: `120`
- Gov calls: `80`
- Judge calls: `0`
- Worker DNA: `xai, google, minimax`
- Gov model: `minimax/MiniMax-M2.5-highspeed`

## Assertions

| Assertion | Value |
| --- | --- |
| `artifact_registry_present` | `PASS` |
| `best_artifact_registry_present` | `PASS` |
| `complete_governance_enforcement` | `PASS` |
| `declared_roster_matches_actual_calls` | `PASS` |
| `deterministic_gate_after_every_worker` | `PASS` |
| `external_and_intra_holo_evidence_separated` | `PASS` |
| `final_selector_present` | `PASS` |
| `fixed_gov_model_law` | `PASS` |
| `gov_receives_gate_results` | `PASS` |
| `gov_worker_token_ratio_law` | `PASS` |
| `guardrail_sibling_correct_for_all_pairs` | `PASS` |
| `hard_allow_valid_pairs` | `10` |
| `hard_escalate_valid_pairs` | `10` |
| `holo_benchmark_laws` | `PASS` |
| `invalid_runs_preserved` | `PASS` |
| `monotonic_preservation_enforced` | `PASS` |
| `pinned_best_artifact_present` | `PASS` |
| `three_dna_inside_holoverify` | `PASS` |
| `total_valid_pairs` | `20` |
| `worker_prompt_sequence_law` | `PASS` |
| `worker_rotation_law` | `PASS` |

## Packets

| Packet | Expected For Local Audit | Holo Final | Selection |
| --- | --- | --- | --- |
| `HV-KITC-078-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-078-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-081-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-081-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-082-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-082-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-084-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-084-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-086-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-086-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-087-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-087-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-042-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-042-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-089-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-089-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-090-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-090-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-077-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-077-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-BEC-HARDEN-025-H03-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-BEC-HARDEN-025-H03-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-BEC-HARDEN-025-H06-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-BEC-HARDEN-025-H06-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-001-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-001-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-002-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-002-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-003-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-003-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-004-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-004-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-005-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-005-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-006-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-006-B` | `ESCALATE` | `ESCALATE` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-007-A` | `ALLOW` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `BAL100-HB004-DEP-007-B` | `ESCALATE` | `ESCALATE` | `FINAL_REGRESSED_SELECTED_BEST_PRIOR` |
