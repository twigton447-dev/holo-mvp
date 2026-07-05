# HoloVerify Domain Consolidation Ledger

Classification: `HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_NO_PROVIDER_2026_07_01`
Package SHA-256: `5532559c86db2ae04579e4edff9472f3807a2ba5a5a3866af17802d67c75c63e`
Generated without provider calls: `True`

## Control Summary

| Lane | State | Evidence | Next gate |
| --- | --- | --- | --- |
| Compiled metrics snapshot | `23` run rows, `128` metric rows | `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/compiled_metrics_package.json` | Keep as current metrics surface |
| Wave 2 packet freeze | `60` pairs / `120` packets frozen | `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/FREEZE_MANIFEST.json` | No packet or prompt edits |
| Wave 2 solo triage | `360` calls, `37` target pairs found | `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/solo_triage_3mini/WAVE2_3FAMILY_SOLO_TRIAGE_EVIDENCE_PACKAGE_2026_07_01.json` | Do not rerun unless explicitly opened |
| Wave 2 Holo selected targets | `37` scored pairs plus `0` staged pairs | `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_004_COMBINED_EVIDENCE_MEMO_2026_07_01.json` | Selected-target lane is complete when staged pairs are `0` |
| Wave 2 full-family remainder | `23` future-staged pairs, `230` expected provider calls if live, live gate `PASS` | `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_005/WAVE2_HOLO_TARGET_BATCH_005_LIVE_PREFLIGHT_2026_07_01.json` | Run only after Batch 004 is live, promoted, and provider-approved |
| Wave 2 statistical lane | `37/60` current per class; `37/60` after Batch 004 if clean; `60/60` only after Batch 005 if clean | `significance_planner.csv` | Keep staged work separate from scored proof until live evidence exists |
| Wave 2 ordering verifier | `PASS` required before opening any provider gate | `docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.json` | Run immediately before Batch 004 live approval |
| Batch 004 provider approval packet | `NOT_READY`, `100` expected calls, approval granted `False` | `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.json` | Required before Batch 004 live execution |

## Wave 2 Domain Status

| Domain | Frozen pairs | Top targets | Scored target pairs | Staged target pairs | Future full-family staged pairs | Remaining target pairs | Unstaged full-family pairs | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `HV-DPRV-REP-2026-07-01` | `20` | `12` | `12` | `0` | `8` | `0` | `0` | `TARGET_POOL_STAGED_COMPLETE_FULL_FAMILY_REMAINDER_STAGED_NOT_SCORED` |
| `HV-FINC-REP-2026-07-01` | `20` | `16` | `16` | `0` | `4` | `0` | `0` | `TARGET_POOL_STAGED_COMPLETE_FULL_FAMILY_REMAINDER_STAGED_NOT_SCORED` |
| `HV-HRWF-REP-2026-07-01` | `20` | `9` | `9` | `0` | `11` | `0` | `0` | `TARGET_POOL_STAGED_COMPLETE_FULL_FAMILY_REMAINDER_STAGED_NOT_SCORED` |

## Wave 2 Scored Metrics

| Metric | Value |
| --- | ---: |
| Scored Holo pairs | `37` |
| Scored Holo packets | `74` |
| Scored Holo correct/admissible packets | `74` |
| Selected-target pair pool | `37` |
| Remaining selected targets after Batch 004 staging | `0` |
| Current pairs needed for 60/class | `23` |
| Pairs needed for 60/class after clean Batch 004 | `23` |
| Full-family remainder future-staged pairs | `23` |
| Unstaged full-family pairs after future stage | `0` |
| Pairs needed for 60/class after clean Batch 004 and Batch 005 | `0` |

## Significance Planner Extract

| Metric | Errors | n | 95% Wilson high | Zero-error n for <5% 95% upper bound |
| --- | ---: | ---: | ---: | ---: |
| `FNR` | `0` | `37` | `0.094058` | `60` |
| `FPR` | `0` | `37` | `0.094058` | `60` |
| `overall_error` | `0` | `74` | `0.04935` | `60` |
| `operational_non_success` | `0` | `74` | `0.04935` | `60` |

## Full-Family Remainder Pairs

These pairs are not in the 37-pair selected-target pool. They are the exact Wave 2 backlog for full 60-pair coverage across the three new domains; Batch 005 stages them but does not score them.

| Family | Pair | Bucket | Packets |
| --- | --- | --- | --- |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-002` | `hard_allow` | `HV-DPRV-REP-002-A, HV-DPRV-REP-002-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-003` | `hard_allow` | `HV-DPRV-REP-003-A, HV-DPRV-REP-003-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-004` | `hard_allow` | `HV-DPRV-REP-004-A, HV-DPRV-REP-004-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-006` | `hard_allow` | `HV-DPRV-REP-006-A, HV-DPRV-REP-006-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-010` | `hard_allow` | `HV-DPRV-REP-010-A, HV-DPRV-REP-010-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-011` | `hard_escalate` | `HV-DPRV-REP-011-A, HV-DPRV-REP-011-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-016` | `hard_escalate` | `HV-DPRV-REP-016-A, HV-DPRV-REP-016-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-017` | `hard_escalate` | `HV-DPRV-REP-017-A, HV-DPRV-REP-017-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-005` | `hard_allow` | `HV-FINC-REP-005-A, HV-FINC-REP-005-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-008` | `hard_allow` | `HV-FINC-REP-008-A, HV-FINC-REP-008-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-014` | `hard_escalate` | `HV-FINC-REP-014-A, HV-FINC-REP-014-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-018` | `hard_escalate` | `HV-FINC-REP-018-A, HV-FINC-REP-018-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-002` | `hard_allow` | `HV-HRWF-REP-002-A, HV-HRWF-REP-002-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-003` | `hard_allow` | `HV-HRWF-REP-003-A, HV-HRWF-REP-003-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-004` | `hard_allow` | `HV-HRWF-REP-004-A, HV-HRWF-REP-004-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-005` | `hard_allow` | `HV-HRWF-REP-005-A, HV-HRWF-REP-005-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-008` | `hard_allow` | `HV-HRWF-REP-008-A, HV-HRWF-REP-008-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-009` | `hard_allow` | `HV-HRWF-REP-009-A, HV-HRWF-REP-009-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-011` | `hard_escalate` | `HV-HRWF-REP-011-A, HV-HRWF-REP-011-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-013` | `hard_escalate` | `HV-HRWF-REP-013-A, HV-HRWF-REP-013-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-014` | `hard_escalate` | `HV-HRWF-REP-014-A, HV-HRWF-REP-014-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-015` | `hard_escalate` | `HV-HRWF-REP-015-A, HV-HRWF-REP-015-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-016` | `hard_escalate` | `HV-HRWF-REP-016-A, HV-HRWF-REP-016-B` |

## Compiled Evidence Families

| Evidence family | Domains | Architecture packets | Architecture correct | Solo packets/attempts | Tiers |
| --- | --- | ---: | ---: | ---: | --- |
| `Agentic Commerce / All-Six Collapse Canary` | agentic commerce / order execution controls | `6` | `6` | `0` | lock_rooted_canary |
| `Agentic Commerce / Order Execution Replication` | agentic commerce / order execution controls | `40` | `40` | `40` | batched_full_family_complete<br>solo_triage_same_packet_bank_openai_4o_mini |
| `Clinical Activation Boundary Controls / Kit C` | clinical-regulated activation controls | `40` | `40` | `0` | frozen_complete_run |
| `D11-Lock HoloBuild Mini-Suite` | governed work-product quality | `5` | `MISSING_REPO_EVIDENCE` | `0` | ledger_evidence_needs_public_root_package |
| `Hard ALLOW FP 5-Pair Precursor` | source-boundary hard ALLOW controls | `10` | `10` | `0` | frozen_pending_judge_not_benchmark_locked |
| `IT Access / Permission Change Replication` | IT access / permission change controls | `40` | `40` | `40` | batched_family_complete<br>replacement_family_rollup_needs_consolidated_lock<br>solo_triage_same_packet_bank_openai_4o_mini |
| `Vendor-Master Payment Controls / AP Replication` | AP / procurement / vendor-master controls | `40` | `40` | `40` | committed_evidence_package<br>roster_matched_solo_baseline |
| `Wave 2 / HR-Data Privacy-Finance Targeted Holo Runs` | HR, data privacy, and finance close controls | `74` | `74` | `74` | wave2_selected_target_batches_complete<br>wave2_selected_target_solo_triage_exact_roster |

## Next Gates

0. Re-run the full no-provider refresh before opening any provider-call gate:

```bash
python3 -B docs/benchmark/run_wave2_domain_no_provider_refresh_2026_07_01.py
```

Equivalent manual verifier sequence:

```bash
python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py
python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py
python3 -B docs/benchmark/build_wave2_batch004_provider_approval_packet_2026_07_01.py
python3 -B docs/benchmark/build_wave2_domain_control_room_2026_07_01.py
```

Required approval statement:

`I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_004 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

1. Live Batch 004 only after explicit provider-call approval:

```bash
python3 -B docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py --batch-number 4 --run-live --approval-packet-sha256 APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET --approval-statement "I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_004 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

2. If Batch 004 finishes cleanly, build the comparison and promote only then:

```bash
python3 -B docs/benchmark/build_wave2_holo_target_batch_comparison_2026_07_01.py --batch-number 4
python3 -B docs/benchmark/build_wave2_holo_target_combined_evidence_2026_07_01.py --batches 1 2 3 4
python3 -B docs/benchmark/compile_holoverify_holobuild_metrics_2026_07_01.py
node docs/benchmark/build_holoverify_holobuild_metrics_workbook_2026_07_01.mjs
python3 -B docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py
python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py
python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py
python3 -B docs/benchmark/build_wave2_domain_control_room_2026_07_01.py
```

3. Batch 005 full-family remainder is staged/preflighted, but remains locked behind Batch 004 promotion plus explicit provider-call approval:

```bash
python3 -B docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py --batch-number 5 --run-live --approval-packet-sha256 APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET --approval-statement "I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_005 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_005_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

4. If Batch 005 finishes cleanly, build its comparison and promote it under full-family statistical language, not selected-target language:

```bash
python3 -B docs/benchmark/build_wave2_holo_target_batch_comparison_2026_07_01.py --batch-number 5
python3 -B docs/benchmark/build_wave2_holo_target_combined_evidence_2026_07_01.py --batches 1 2 3 4 5
python3 -B docs/benchmark/compile_holoverify_holobuild_metrics_2026_07_01.py
node docs/benchmark/build_holoverify_holobuild_metrics_workbook_2026_07_01.mjs
python3 -B docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py
python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py
python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py
python3 -B docs/benchmark/build_wave2_domain_control_room_2026_07_01.py
```

## Claim Boundaries

- This ledger consolidates existing file-backed evidence only; it does not create new benchmark scores.
- No provider, solo, judge, or Holo execution is performed by this ledger builder.
- Compiled historical families are summarized from the metrics package in this checkout; missing external trees are not inferred.
- Wave 2 selected-target evidence is separated from full-family statistical proof.
- This memo covers only Wave 2 Holo target Batches 001, 002, 003, 004, not the entire Wave 2 frozen packet bank.
- Holo solved all selected target packets run in these batches: 74/74 packets and 37/37 sibling pairs.
- The matched solo one-shot results on the same selected packets were unreliable: 159/222 attempts were not KNEW/admissible.
- Selected-target evidence remains separate from full-family statistical proof until the non-target remainder has live Holo evidence.
- Any staged selected-target or full-family remainder section is preflight-only and excluded from scored totals.
- Token ratio is operational bookkeeping only. It is not a proof claim because solo was one-shot while Holo used governed multi-turn architecture.
- No judges are included in this package. No new provider calls were made to create this combined memo.
- Internal Holo worker misses are separated from external solo failures. They show governance correction, not standalone solo failure.
- Batch 004 is scored selected-target evidence in this post-live package.
- Completing the selected-target pool is not the same as completing all 60 frozen Wave 2 pairs.
- The full-family statistical lane requires the remaining non-target pairs after the selected-target lane.
- Batch 004 selected-target evidence is promoted; no staged selected-target batch remains.
- Batch 005 live preflight root signature: `a99fba06753da20549e6fea991c2c2a3d829e07aaf4541813ffa31a1f484c12d`.
