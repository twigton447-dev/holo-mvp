# HoloVerify 20-Pair No-Provider Local Audit

Status: `PASS`

This audit reads only local frozen artifacts. It does not call providers, run judges, mutate packets, or rerun Holo/Solo.

## Assertions

| Assertion | Status |
| --- | --- |
| frozen_holo_run_present | `PASS` |
| solo_run_present | `PASS` |
| same_40_packet_hashes | `PASS` |
| solo_calls_120 | `PASS` |
| holo_calls_200 | `PASS` |
| no_judges | `PASS` |
| no_leakage | `PASS` |
| clean_all_six_solo_fail_pairs_14 | `PASS` |
| total_valid_holo_pairs_20 | `PASS` |
| evidence_categories_separated | `PASS` |
| invalid_hardening_runs_preserved | `PASS` |
| autopsy_lock_passed | `PASS` |
| solo_raw_outputs_preserved_in_locked_trace | `PASS` |

## Counts

| Count | Value |
| --- | --- |
| frozen_packet_count | 40 |
| holo_trace_rows | 200 |
| solo_trace_rows | 120 |
| holo_provider_calls | 200 |
| solo_provider_calls | 120 |
| holo_worker_calls | 120 |
| holo_gov_calls | 80 |
| holo_judge_calls | 0 |
| solo_judge_calls | 0 |
| prompt_files_scanned | 240 |
| forbidden_prompt_hits | 0 |
| clean_pair_count | 14 |
| valid_holo_pair_count | 20 |
| holo_tokens | 426002 |
| solo_tokens | 206839 |

## Raw Output Preservation

| Field | Value |
| --- | --- |
| raw_outputs_directory_present | False |
| raw_outputs_preserved_in_solo_trace | True |
| trace_path | `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/docs/benchmark/holoverify_20pair_3dna_2026-06-29/solo_one_shot_against_frozen_run_20260629T052822Z/run_20260629T060938Z/SOLO_ONE_SHOT_TRACE.jsonl` |

## Locked Signatures

| Artifact | Signature |
| --- | --- |
| holo_freeze_root_signature | `dcd9f17a76eef5bbe3b2a20195835a98b3694b511aa66d313fa4a91e7f2a17f1` |
| holo_trace_hash | `dbb1d040c516af4989d488a07c44917a3582dc17da75c9fc517b4472228f1201` |
| solo_trace_hash | `5f98d96f82723979123a7eb13ed54900fe09f090cc1eaf7f40af2b073d724f94` |
| solo_run_lock_root_signature | `223aa9dd0f9f1d42b08f5efd44166e80f5100590c591afb655fbadfd89e7438f` |
| autopsy_lock_root_signature | `730c31344a7d38ab2feb3c4d7c4b38127794c295d021f7c5b02c3f9e059b99b6` |
