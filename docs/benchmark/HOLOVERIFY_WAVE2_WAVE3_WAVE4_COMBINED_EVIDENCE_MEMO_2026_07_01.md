# HoloVerify Wave2-Wave4 Combined Evidence Memo

Classification: `HOLOVERIFY_WAVE2_WAVE3_WAVE4_COMBINED_EVIDENCE_MEMO_NO_PROVIDER`
Package SHA-256: `d0757722e171281a984337752caf3b894ccee98bc4ffc072232ccf4d31dfc4bb`

## Combined Result

| Metric | Value |
| --- | ---: |
| Waves | `wave2, wave3, wave4` |
| Holo packets | `174` |
| Holo packets correct/admissible | `174` |
| Holo valid sibling pairs | `87` |
| False positives | `0/87` |
| False negatives | `0/87` |
| Provider calls | `870` |
| Worker calls | `522` |
| Gov calls | `348` |
| Judge calls | `0` |
| Provider failures | `0` |
| Holo input tokens | `1565369` |
| Holo output tokens | `319106` |
| Holo total tokens | `2004098` |
| Gov token share | `0.102552` |
| Prompt files scanned for leakage | `870` |
| Intermediate worker misses corrected | `17` |
| Intermediate worker misses uncorrected | `0` |
| Packet error upper 95%, exact | `1.706949%` |
| Packet error upper 95%, rule of three | `1.724138%` |

## Batch Rollup

| Wave | Batch | Classification | Packets | Valid pairs | Calls | Worker/Gov | Tokens | No leakage | Worker misses corrected |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `wave2` | `001` | `WAVE2_HOLO_TARGET_BATCH_001_COMPLETE` | `18/18` | `9` | `90` | `54/36` | `207467` | `PASS` | `1` |
| `wave2` | `002` | `WAVE2_HOLO_TARGET_BATCH_002_COMPLETE` | `18/18` | `9` | `90` | `54/36` | `206630` | `PASS` | `5` |
| `wave2` | `003` | `WAVE2_HOLO_TARGET_BATCH_003_COMPLETE` | `18/18` | `9` | `90` | `54/36` | `208069` | `PASS` | `1` |
| `wave2` | `004` | `WAVE2_HOLO_TARGET_BATCH_004_COMPLETE` | `20/20` | `10` | `100` | `60/40` | `231036` | `PASS` | `1` |
| `wave2` | `005` | `WAVE2_HOLO_TARGET_BATCH_005_COMPLETE` | `46/46` | `23` | `230` | `138/92` | `529033` | `PASS` | `1` |
| `wave3` | `001` | `WAVE3_HOLO_TARGET_BATCH_001_COMPLETE` | `24/24` | `12` | `120` | `72/48` | `278439` | `PASS` | `3` |
| `wave4` | `001` | `WAVE4_HOLO_TARGET_BATCH_001_COMPLETE` | `30/30` | `15` | `150` | `90/60` | `343424` | `PASS` | `5` |

## Correction Trail

These are intra-Holo worker misses, not final Holo failures and not external solo failures.

| Wave | Batch | Turn | Packet | Model | Reasons | Expected | Local | Final | Selector reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `wave2` | `001` | `HV-FINC-REP-013-A_W1` | `HV-FINC-REP-013-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave2` | `002` | `HV-DPRV-REP-012-A_W1` | `HV-DPRV-REP-012-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave2` | `002` | `HV-FINC-REP-012-A_W1` | `HV-FINC-REP-012-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave2` | `002` | `HV-FINC-REP-015-A_W1` | `HV-FINC-REP-015-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave2` | `002` | `HV-FINC-REP-019-A_W1` | `HV-FINC-REP-019-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave2` | `002` | `HV-HRWF-REP-017-A_W1` | `HV-HRWF-REP-017-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave2` | `003` | `HV-DPRV-REP-015-A_W1` | `HV-DPRV-REP-015-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave2` | `004` | `HV-FINC-REP-016-A_W1` | `HV-FINC-REP-016-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave2` | `005` | `HV-DPRV-REP-016-A_W1` | `HV-DPRV-REP-016-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave3` | `001` | `HV-BKYC-REP-016-A_W1` | `HV-BKYC-REP-016-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave3` | `001` | `HV-BENC-REP-015-A_W1` | `HV-BENC-REP-015-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave3` | `001` | `HV-BENC-REP-020-A_W1` | `HV-BENC-REP-020-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave4` | `001` | `HV-DEFA-REP-015-A_W1` | `HV-DEFA-REP-015-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave4` | `001` | `HV-UTIL-REP-012-A_W1` | `HV-UTIL-REP-012-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave4` | `001` | `HV-INSR-REP-011-A_W1` | `HV-INSR-REP-011-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave4` | `001` | `HV-INSR-REP-018-A_W1` | `HV-INSR-REP-018-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `wave4` | `001` | `HV-INSR-REP-020-A_W1` | `HV-INSR-REP-020-A` | `grok-3-mini` | `inadmissible,truth_mismatch` | `ALLOW` | `ESCALATE` | `ALLOW` | `FINAL_ARTIFACT_ADMISSIBLE` |

## Family Breakdown

| Family | Pairs | Packets | Correct/admissible packets |
| --- | ---: | ---: | ---: |
| `HV-BENC-REP-2026-07-01` | `4` | `8` | `8` |
| `HV-BKYC-REP-2026-07-01` | `5` | `10` | `10` |
| `HV-DEFA-REP-2026-07-01` | `6` | `12` | `12` |
| `HV-DPRV-REP-2026-07-01` | `20` | `40` | `40` |
| `HV-FINC-REP-2026-07-01` | `20` | `40` | `40` |
| `HV-GOVP-REP-2026-07-01` | `3` | `6` | `6` |
| `HV-HRWF-REP-2026-07-01` | `20` | `40` | `40` |
| `HV-INSR-REP-2026-07-01` | `7` | `14` | `14` |
| `HV-UTIL-REP-2026-07-01` | `2` | `4` | `4` |

## Pair Rows

| Wave | Batch | Family | Pair | Bucket | Evidence class | Target | Guardrail |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `wave2` | `001` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-004` | `hard_allow` | `ALL_SIX_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `001` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-010` | `hard_allow` | `ALL_SIX_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `001` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-009` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `001` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-012` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `001` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-018` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `001` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-003` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `001` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-006` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `001` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-013` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `001` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-019` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `002` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-011` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `002` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-012` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `002` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-013` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `002` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-019` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `002` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-012` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `002` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-015` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `002` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-019` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `002` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-017` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `002` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-020` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `003` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-001` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `003` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-014` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `003` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-015` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `003` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-018` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `003` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-020` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `003` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-001` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `003` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-007` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `003` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-009` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `003` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-001` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `004` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-005` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `004` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-007` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `004` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-008` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `004` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-002` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `004` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-016` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `004` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-017` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `004` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-020` | `hard_escalate` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `004` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-006` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `004` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-007` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `004` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-010` | `hard_allow` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-002` | `hard_allow` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-003` | `hard_allow` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-004` | `hard_allow` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-006` | `hard_allow` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-010` | `hard_allow` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-011` | `hard_escalate` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `005` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-016` | `hard_escalate` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `005` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-017` | `hard_escalate` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `005` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-005` | `hard_allow` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-008` | `hard_allow` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-014` | `hard_escalate` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `005` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-018` | `hard_escalate` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `005` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-002` | `hard_allow` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-003` | `hard_allow` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-004` | `hard_allow` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-005` | `hard_allow` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-008` | `hard_allow` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-009` | `hard_allow` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave2` | `005` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-011` | `hard_escalate` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `005` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-013` | `hard_escalate` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `005` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-014` | `hard_escalate` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `005` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-015` | `hard_escalate` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave2` | `005` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-016` | `hard_escalate` | `FULL_FAMILY_HOLO_COMPLETION_NO_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave3` | `001` | `HV-BENC-REP-2026-07-01` | `HV-BENC-REP-001` | `hard_allow` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave3` | `001` | `HV-BENC-REP-2026-07-01` | `HV-BENC-REP-015` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave3` | `001` | `HV-BENC-REP-2026-07-01` | `HV-BENC-REP-016` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave3` | `001` | `HV-BENC-REP-2026-07-01` | `HV-BENC-REP-020` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave3` | `001` | `HV-BKYC-REP-2026-07-01` | `HV-BKYC-REP-009` | `hard_allow` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave3` | `001` | `HV-BKYC-REP-2026-07-01` | `HV-BKYC-REP-011` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave3` | `001` | `HV-BKYC-REP-2026-07-01` | `HV-BKYC-REP-016` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave3` | `001` | `HV-BKYC-REP-2026-07-01` | `HV-BKYC-REP-018` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave3` | `001` | `HV-BKYC-REP-2026-07-01` | `HV-BKYC-REP-020` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave3` | `001` | `HV-GOVP-REP-2026-07-01` | `HV-GOVP-REP-006` | `hard_allow` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave3` | `001` | `HV-GOVP-REP-2026-07-01` | `HV-GOVP-REP-012` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave3` | `001` | `HV-GOVP-REP-2026-07-01` | `HV-GOVP-REP-014` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave4` | `001` | `HV-DEFA-REP-2026-07-01` | `HV-DEFA-REP-005` | `hard_allow` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave4` | `001` | `HV-DEFA-REP-2026-07-01` | `HV-DEFA-REP-010` | `hard_allow` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave4` | `001` | `HV-DEFA-REP-2026-07-01` | `HV-DEFA-REP-014` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave4` | `001` | `HV-DEFA-REP-2026-07-01` | `HV-DEFA-REP-015` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave4` | `001` | `HV-DEFA-REP-2026-07-01` | `HV-DEFA-REP-019` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave4` | `001` | `HV-DEFA-REP-2026-07-01` | `HV-DEFA-REP-020` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave4` | `001` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-002` | `hard_allow` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave4` | `001` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-008` | `hard_allow` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave4` | `001` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-009` | `hard_allow` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave4` | `001` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-010` | `hard_allow` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ALLOW->ALLOW` | `ESCALATE->ESCALATE` |
| `wave4` | `001` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-011` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave4` | `001` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-018` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave4` | `001` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-020` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave4` | `001` | `HV-UTIL-REP-2026-07-01` | `HV-UTIL-REP-012` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |
| `wave4` | `001` | `HV-UTIL-REP-2026-07-01` | `HV-UTIL-REP-013` | `hard_escalate` | `HOLO_TARGET_BATCH_ONLY_NO_MATCHED_SOLO_BASELINE` | `ESCALATE->ESCALATE` | `ALLOW->ALLOW` |

## Claim Boundaries

- This package combines already-frozen Holo live runs for Wave2, Wave3, and Wave4.
- Wave2 includes a selected-target solo comparison layer for Wave2 Batch001-004 only; Wave2 Batch005 and Wave3/Wave4 are Holo completion evidence without matched live solo baselines.
- Do not describe Wave3/Wave4 as solo-collapse proof until matched solo baselines are run against those exact packets.
- Internal Holo worker misses are reported separately from external solo failures.
- No judges are included in this package.
- No provider calls were made to create this combined memo.

## Next Live Work Recommendation

Recommended: `RUN_MATCHED_SOLO_BASELINES_FOR_WAVE3_WAVE4_AND_WAVE2_BATCH005_BEFORE_PUBLIC_COMPARATIVE_CLAIMS`

The Holo completion layer is now strong; the next proof gap is matched control evidence for the newly proven Holo target packets.

Deferred until labels are clean:
- `MORE_HOLO_BATCHES_UNTIL_THIS_COMPARISON_LAYER_IS_CLOSED`
- `PUBLIC_SAFE_BENCHMARK_OR_WHITEPAPER_UPDATE_UNTIL_MATCHED_SOLO_GAPS_ARE_LABELED`
