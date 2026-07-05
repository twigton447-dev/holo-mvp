# Wave 2 3-Family Solo Triage Evidence Package

Classification: `WAVE2_3FAMILY_SOLO_TRIAGE_EVIDENCE_PACKAGE_COMPLETE`
Freeze root: `80d8106d7efe72bee44d2c05648b71814204c08e1f96934afefd3d75d242845f`
Package SHA-256: `c40e45eec78cee8312af9be390388a0c3061f79050db6ed87e093f7383d882ca`

## Scope

- Families: Workforce, Data Privacy, Finance Close
- Frozen packets: 120 total, 40 per domain
- Provider calls: 360 total, 120 per domain
- Models: `xai/grok-3-mini`, `openai/gpt-5.4-mini`, `minimax/MiniMax-M2.5-highspeed`
- Gov calls: 0
- Holo calls: 0
- Judge calls: 0

## Aggregate Result

| Metric | Count |
| --- | ---: |
| Provider calls | `360` |
| Expected provider calls | `360` |
| KNEW/admissible | `140` |
| Not KNEW | `220` |
| Wrong verdict | `12` |
| Parse fail | `38` |
| Structural/evidence fail | `170` |
| Provider fail | `0` |
| Top Holo target pairs | `37` |
| All-six solo-collapse pairs | `2` |

Tokens: `198223` input / `167185` output / `429773` total

## Domain Results

| Domain | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Structural/Evidence Fail | Lock | Trace Hash |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| HR / payroll / workforce controls | `120/120` | `52` | `68` | `2` | `10` | `56` | `PASS` | `29ecc48f97dadc47b661ce17fe642454dd8ac4f68fd5aa27464336c142ac1c7b` |
| Data privacy / customer data release controls | `120/120` | `49` | `71` | `4` | `13` | `54` | `PASS` | `3373c912e689f85d8ebb276873f3a83ee4e84bfd00e9fb924c13067122aa25af` |
| Finance close / revenue / expense recognition controls | `120/120` | `39` | `81` | `6` | `15` | `60` | `PASS` | `273ea42e7de222dd67c8d861441f554a27b3f81294bb6dd738a922d24512e659` |

## Model Totals

| Model | Calls | KNEW | Verdict Correct | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `minimax/MiniMax-M2.5-highspeed` | `120/120` | `56` | `82` | `0` | `26` | `38` | `0` | `200215` |
| `openai/gpt-5.4-mini` | `120/120` | `71` | `120` | `0` | `49` | `0` | `0` | `75632` |
| `xai/grok-3-mini` | `120/120` | `13` | `108` | `12` | `95` | `0` | `0` | `153926` |

## Canonical Run Paths

- `HV-HRWF-REP-2026-07-01`: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/solo_triage_3mini/wave2_workforce_solo_triage_clean_001/run_20260701T021517Z`
- `HV-DPRV-REP-2026-07-01`: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/solo_triage_3mini/wave2_data_privacy_solo_triage_clean_001/run_20260701T024118Z`
- `HV-FINC-REP-2026-07-01`: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/solo_triage_3mini/wave2_finance_close_solo_triage_clean_001/run_20260701T030250Z`

## Excluded Runs

These runs are preserved locally if present but are not counted in the aggregate package.

- `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/solo_triage_3mini/wave2_workforce_solo_triage/run_20260701T020822Z`: noncanonical early Workforce batch label; superseded by clean_001 canonical run; exists=True; calls=120/120; trace_hash=`654c8a28166cb8f90e5791c97e924884b3b5d6e3623330b0c86aaa1744f0b69a`
- `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/solo_triage_3mini/wave2_workforce_solo_triage_clean_001/run_20260701T022623Z`: duplicate Workforce run under clean_001 label; started while canonical clean_001 run was active; not counted; exists=True; calls=120/120; trace_hash=`bfe075bca816c0a1f388786688586f0d094be9fc1b5154fd71da7f4cce52e038`

## Assertions

- `three_canonical_domains_complete`: `True`
- `provider_calls_360_of_360`: `True`
- `no_provider_failures`: `True`
- `no_gov_holo_judge_calls`: `True`
- `all_locks_pass`: `True`
- `canonical_runs_only_counted`: `True`

## Claim Boundary

This package is solo-triage evidence only. It does not contain Holo, Gov, or judge results. It identifies seams and Holo target pairs; it does not prove Holo performance on these Wave 2 domains until separate Holo runs are executed and frozen.
