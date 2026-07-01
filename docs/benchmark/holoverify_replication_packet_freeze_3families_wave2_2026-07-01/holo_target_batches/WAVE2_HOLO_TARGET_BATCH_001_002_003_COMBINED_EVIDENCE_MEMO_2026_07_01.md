# Wave 2 Holo Target Batch 001+002+003 Combined Evidence Memo

Classification: `WAVE2_HOLO_TARGET_BATCH_001_002_003_COMBINED_EVIDENCE_MEMO_NO_PROVIDER`
Package SHA-256: `d74d76ce0e13fe1cf31cc8ca731eb315d744fbc1f2122923216c90c41bfdfda6`

## Scope

This is a no-provider combined memo over the Wave 2 Holo target Batch 001, Batch 002, Batch 003 evidence. It does not add judge calls, provider calls, packet edits, prompt edits, or new scoring rules.

## Combined Result

| Metric | Value |
| --- | ---: |
| Batches included | `3` |
| Holo sibling pairs | `27` |
| Holo packets | `54` |
| Holo packets correct/admissible | `54` |
| Holo valid pairs | `27` |
| Holo provider failures | `0` |
| Holo parse failures | `0` |
| Selected solo attempts | `162` |
| Solo KNEW/admissible | `43` |
| Solo not KNEW | `119` |
| Solo wrong verdicts | `9` |
| Solo parse fails | `29` |
| Solo structural/evidence fails | `81` |
| All-six solo-collapse pairs | `2` |
| Strong solo-collapse pairs | `25` |
| Non-target full-family completion pairs | `0` |
| Intra-Holo worker misses corrected | `8` |
| Solo not KNEW rate | `0.734568` |
| Holo vs selected solo token ratio | `3.17477` |
| Gov share of Holo tokens | `0.102039` |

## Batch Comparison

| Batch | Holo packets | Holo valid pairs | Solo KNEW | Solo not KNEW | Wrong verdicts | Parse fails | Structural/evidence fails | Intra-Holo corrections | Token ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 001 | `18/18` | `9/9` | `7` | `47` | `0` | `10` | `37` | `1` | `3.310468` |
| 002 | `18/18` | `9/9` | `18` | `36` | `9` | `9` | `18` | `5` | `3.078516` |
| 003 | `18/18` | `9/9` | `18` | `36` | `0` | `10` | `26` | `2` | `3.143891` |

## Claim Boundaries

- This memo covers only Wave 2 Holo target Batches 001, 002, 003, not the entire Wave 2 frozen packet bank.
- Holo solved all selected target packets run in these batches: 54/54 packets and 27/27 sibling pairs.
- The matched solo one-shot results on the same selected packets were unreliable: 119/162 attempts were not KNEW/admissible.
- Selected-target evidence remains separate from full-family statistical proof until the non-target remainder has live Holo evidence.
- Any staged selected-target or full-family remainder section is preflight-only and excluded from scored totals.
- Token ratio is operational bookkeeping only. It is not a proof claim because solo was one-shot while Holo used governed multi-turn architecture.
- No judges are included in this package. No new provider calls were made to create this combined memo.
- Internal Holo worker misses are separated from external solo failures. They show governance correction, not standalone solo failure.

## Family Breakdown

| Family | Pairs | Packets | Holo correct/admissible packets | Solo attempts | Solo KNEW | Solo not KNEW | Wrong verdicts | Parse fails | Structural/evidence fails |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `HV-DPRV-REP-2026-07-01` | `9` | `18` | `18` | `54` | `17` | `37` | `3` | `10` | `24` |
| `HV-FINC-REP-2026-07-01` | `12` | `24` | `24` | `72` | `17` | `55` | `4` | `12` | `39` |
| `HV-HRWF-REP-2026-07-01` | `6` | `12` | `12` | `36` | `9` | `27` | `2` | `7` | `18` |

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

## Remaining Target Pool

Solo triage produced `37` top targets. These batches have run `27` pairs, leaving `10` target pairs.

## Staged Final Target Batch

Batch: `WAVE2_HOLO_TARGET_BATCH_004`
Selection mode: `target-selection`
Selection mode defaulted: `True`
Status: `PASS`
Ready for live Holo: `True`
Selected pairs match expected target pool: `True`
Providers called: `0`
Live Holo started: `False`
Live execution gate: `PASS`
Solo started: `False`
Judges started: `False`
Expected live provider calls: `100` (`60` worker, `40` Gov)
Expected solo calls: `0`
Expected judge calls: `0`
Live preflight root signature: `bfa320f216b25ac3f5f9c321573ae56270a66292906f0038531ae12bce5c0a3b`

Claim boundary: Staged/preflight evidence only; not counted as Holo result, solo comparison, judge result, or statistical proof.

| Priority | Family | Pair | Class | Bucket | Not KNEW | Wrong verdicts | Parse/provider fails |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: |
| `9` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-016` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `1` |
| `8` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-005` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `0` |
| `8` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-007` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `0` |
| `8` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-008` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `0` |
| `8` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-002` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `0` |
| `8` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-017` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `0` |
| `8` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-020` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `0` |
| `8` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-006` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `0` |
| `8` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-007` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `0` |
| `8` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-010` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `0` |

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
Live execution gate: `LOCKED`
Solo started: `False`
Judges started: `False`
Expected live provider calls: `230` (`138` worker, `92` Gov)
Expected solo calls: `0`
Expected judge calls: `0`
Live preflight root signature: `3cf24480f79bde31d58774d5e2a32290f97f2c1ab9d5088b9f1eaf676909b46b`

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

Run explicitly approved live Holo execution for WAVE2_HOLO_TARGET_BATCH_004. Do not run solo or judges first.
