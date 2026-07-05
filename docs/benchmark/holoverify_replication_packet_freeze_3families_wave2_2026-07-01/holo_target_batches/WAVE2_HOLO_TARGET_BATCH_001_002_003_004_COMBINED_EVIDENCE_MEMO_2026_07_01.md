# Wave 2 Holo Target Batch 001+002+003+004 Combined Evidence Memo

Classification: `WAVE2_HOLO_TARGET_BATCH_001_002_003_COMBINED_EVIDENCE_MEMO_NO_PROVIDER`
Package SHA-256: `d4ad201b4c177154741ec8b3ee7b4929c3db764451a2ef8862e3148d44b0198d`

## Scope

This is a no-provider combined memo over the Wave 2 Holo target Batch 001, Batch 002, Batch 003, Batch 004 evidence. It does not add judge calls, provider calls, packet edits, prompt edits, or new scoring rules.

## Combined Result

| Metric | Value |
| --- | ---: |
| Batches included | `4` |
| Holo sibling pairs | `37` |
| Holo packets | `74` |
| Holo packets correct/admissible | `74` |
| Holo valid pairs | `37` |
| Holo provider failures | `0` |
| Holo parse failures | `0` |
| Selected solo attempts | `222` |
| Solo KNEW/admissible | `63` |
| Solo not KNEW | `159` |
| Solo wrong verdicts | `9` |
| Solo parse fails | `30` |
| Solo structural/evidence fails | `120` |
| All-six solo-collapse pairs | `2` |
| Strong solo-collapse pairs | `35` |
| Non-target full-family completion pairs | `0` |
| Intra-Holo worker misses corrected | `10` |
| Solo not KNEW rate | `0.716216` |
| Holo vs selected solo token ratio | `3.193312` |
| Gov share of Holo tokens | `0.101825` |

## Batch Comparison

| Batch | Holo packets | Holo valid pairs | Solo KNEW | Solo not KNEW | Wrong verdicts | Parse fails | Structural/evidence fails | Intra-Holo corrections | Token ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 001 | `18/18` | `9/9` | `7` | `47` | `0` | `10` | `37` | `1` | `3.310468` |
| 002 | `18/18` | `9/9` | `18` | `36` | `9` | `9` | `18` | `5` | `3.078516` |
| 003 | `18/18` | `9/9` | `18` | `36` | `0` | `10` | `26` | `2` | `3.143891` |
| 004 | `20/20` | `10/10` | `20` | `40` | `0` | `1` | `39` | `2` | `3.244341` |

## Claim Boundaries

- This memo covers only Wave 2 Holo target Batches 001, 002, 003, 004, not the entire Wave 2 frozen packet bank.
- Holo solved all selected target packets run in these batches: 74/74 packets and 37/37 sibling pairs.
- The matched solo one-shot results on the same selected packets were unreliable: 159/222 attempts were not KNEW/admissible.
- Selected-target evidence remains separate from full-family statistical proof until the non-target remainder has live Holo evidence.
- Any staged selected-target or full-family remainder section is preflight-only and excluded from scored totals.
- Token ratio is operational bookkeeping only. It is not a proof claim because solo was one-shot while Holo used governed multi-turn architecture.
- No judges are included in this package. No new provider calls were made to create this combined memo.
- Internal Holo worker misses are separated from external solo failures. They show governance correction, not standalone solo failure.

## Family Breakdown

| Family | Pairs | Packets | Holo correct/admissible packets | Solo attempts | Solo KNEW | Solo not KNEW | Wrong verdicts | Parse fails | Structural/evidence fails |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `HV-DPRV-REP-2026-07-01` | `12` | `24` | `24` | `72` | `23` | `49` | `3` | `10` | `36` |
| `HV-FINC-REP-2026-07-01` | `16` | `32` | `32` | `96` | `25` | `71` | `4` | `13` | `54` |
| `HV-HRWF-REP-2026-07-01` | `9` | `18` | `18` | `54` | `15` | `39` | `2` | `7` | `30` |

## Pair Rows

| Batch | Family | Pair | Bucket | Triage class | Solo not KNEW | Solo wrong verdicts | Holo target | Holo guardrail | Evidence class |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| `001` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-004` | `hard_allow` | `ALL_SIX_SOLO_COLLAPSE` | `6` | `0` | `HV-FINC-REP-004-A ALLOW->ALLOW` | `HV-FINC-REP-004-B ESCALATE->ESCALATE` | `ALL_SIX_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `001` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-010` | `hard_allow` | `ALL_SIX_SOLO_COLLAPSE` | `6` | `0` | `HV-FINC-REP-010-A ALLOW->ALLOW` | `HV-FINC-REP-010-B ESCALATE->ESCALATE` | `ALL_SIX_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `001` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-009` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `5` | `0` | `HV-DPRV-REP-009-A ALLOW->ALLOW` | `HV-DPRV-REP-009-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `001` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-012` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `5` | `0` | `HV-HRWF-REP-012-B ESCALATE->ESCALATE` | `HV-HRWF-REP-012-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `001` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-018` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `5` | `0` | `HV-HRWF-REP-018-B ESCALATE->ESCALATE` | `HV-HRWF-REP-018-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `001` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-003` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `5` | `0` | `HV-FINC-REP-003-A ALLOW->ALLOW` | `HV-FINC-REP-003-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `001` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-006` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `5` | `0` | `HV-FINC-REP-006-A ALLOW->ALLOW` | `HV-FINC-REP-006-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `001` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-013` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `5` | `0` | `HV-FINC-REP-013-B ESCALATE->ESCALATE` | `HV-FINC-REP-013-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `001` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-019` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `5` | `0` | `HV-HRWF-REP-019-B ESCALATE->ESCALATE` | `HV-HRWF-REP-019-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `002` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-011` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `1` | `HV-FINC-REP-011-B ESCALATE->ESCALATE` | `HV-FINC-REP-011-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `002` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-012` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `1` | `HV-DPRV-REP-012-B ESCALATE->ESCALATE` | `HV-DPRV-REP-012-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `002` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-013` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `1` | `HV-DPRV-REP-013-B ESCALATE->ESCALATE` | `HV-DPRV-REP-013-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `002` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-019` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `1` | `HV-DPRV-REP-019-B ESCALATE->ESCALATE` | `HV-DPRV-REP-019-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `002` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-012` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `1` | `HV-FINC-REP-012-B ESCALATE->ESCALATE` | `HV-FINC-REP-012-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `002` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-015` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `1` | `HV-FINC-REP-015-B ESCALATE->ESCALATE` | `HV-FINC-REP-015-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `002` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-019` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `1` | `HV-FINC-REP-019-B ESCALATE->ESCALATE` | `HV-FINC-REP-019-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `002` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-017` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `1` | `HV-HRWF-REP-017-B ESCALATE->ESCALATE` | `HV-HRWF-REP-017-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `002` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-020` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `1` | `HV-HRWF-REP-020-B ESCALATE->ESCALATE` | `HV-HRWF-REP-020-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `003` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-001` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-DPRV-REP-001-A ALLOW->ALLOW` | `HV-DPRV-REP-001-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `003` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-014` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-DPRV-REP-014-B ESCALATE->ESCALATE` | `HV-DPRV-REP-014-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `003` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-015` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-DPRV-REP-015-B ESCALATE->ESCALATE` | `HV-DPRV-REP-015-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `003` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-018` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-DPRV-REP-018-B ESCALATE->ESCALATE` | `HV-DPRV-REP-018-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `003` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-020` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-DPRV-REP-020-B ESCALATE->ESCALATE` | `HV-DPRV-REP-020-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `003` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-001` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-FINC-REP-001-A ALLOW->ALLOW` | `HV-FINC-REP-001-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `003` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-007` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-FINC-REP-007-A ALLOW->ALLOW` | `HV-FINC-REP-007-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `003` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-009` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-FINC-REP-009-A ALLOW->ALLOW` | `HV-FINC-REP-009-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `003` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-001` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-HRWF-REP-001-A ALLOW->ALLOW` | `HV-HRWF-REP-001-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `004` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-005` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-DPRV-REP-005-A ALLOW->ALLOW` | `HV-DPRV-REP-005-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `004` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-007` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-DPRV-REP-007-A ALLOW->ALLOW` | `HV-DPRV-REP-007-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `004` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-008` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-DPRV-REP-008-A ALLOW->ALLOW` | `HV-DPRV-REP-008-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `004` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-002` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-FINC-REP-002-A ALLOW->ALLOW` | `HV-FINC-REP-002-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `004` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-016` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-FINC-REP-016-B ESCALATE->ESCALATE` | `HV-FINC-REP-016-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `004` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-017` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-FINC-REP-017-B ESCALATE->ESCALATE` | `HV-FINC-REP-017-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `004` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-020` | `hard_escalate` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-FINC-REP-020-B ESCALATE->ESCALATE` | `HV-FINC-REP-020-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `004` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-006` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-HRWF-REP-006-A ALLOW->ALLOW` | `HV-HRWF-REP-006-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `004` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-007` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-HRWF-REP-007-A ALLOW->ALLOW` | `HV-HRWF-REP-007-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `004` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-010` | `hard_allow` | `STRONG_SOLO_COLLAPSE` | `4` | `0` | `HV-HRWF-REP-010-A ALLOW->ALLOW` | `HV-HRWF-REP-010-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |

## Remaining Target Pool

Solo triage produced `37` top targets. These batches have run `37` pairs, leaving `0` target pairs.

## Full-Family Remainder After Target Pool

These pairs are outside the selected-target pool and are needed only for full 60-pair Wave 2 coverage.

Remaining non-target full-family pairs: `23`.

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

## Staged Full-Family Remainder Batch

Batch: `WAVE2_HOLO_TARGET_BATCH_005`
Selection mode: `full-family-remainder`
Selection mode defaulted: `False`
Status: `PASS`
Ready for live Holo: `True`
Selected pairs match remaining full-family backlog: `True`
Providers called: `0`
Live Holo started: `False`
Live execution gate: `PASS`
Solo started: `False`
Judges started: `False`
Expected live provider calls: `230` (`138` worker, `92` Gov)
Expected solo calls: `0`
Expected judge calls: `0`
Live preflight root signature: `a99fba06753da20549e6fea991c2c2a3d829e07aaf4541813ffa31a1f484c12d`

Claim boundary: Full-family remainder staging only; not selected-target evidence and not scored until a live Holo run exists.

| Priority | Family | Pair | Class | Bucket | Not KNEW | Wrong verdicts | Parse/provider fails |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: |
| `MISSING_REPO_EVIDENCE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-002` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_allow` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-003` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_allow` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-004` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_allow` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-006` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_allow` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-010` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_allow` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-011` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_escalate` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-016` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_escalate` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-017` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_escalate` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-005` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_allow` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-008` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_allow` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-014` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_escalate` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-018` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_escalate` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-002` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_allow` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-003` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_allow` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-004` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_allow` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-005` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_allow` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-008` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_allow` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-009` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_allow` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-011` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_escalate` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-013` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_escalate` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-014` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_escalate` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-015` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_escalate` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |
| `MISSING_REPO_EVIDENCE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-016` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `hard_escalate` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` | `MISSING_REPO_EVIDENCE` |

## Next Valid Step

After selected-target promotion is complete, run explicitly approved live Holo execution for WAVE2_HOLO_TARGET_BATCH_005. Keep it under full-family statistical language.
