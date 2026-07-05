# Wave 2 Holo Target Batch 001+002 Combined Evidence Memo

Classification: `WAVE2_HOLO_TARGET_BATCH_001_002_COMBINED_EVIDENCE_MEMO_NO_PROVIDER`
Package SHA-256: `555dd1269a488dce4813dabd1492fffe3bd31efb1493294bbcf0847f9c6196b1`

## Scope

This is a no-provider combined memo over the committed Wave 2 Holo target Batch 001 and Batch 002 evidence. It does not add judge calls, provider calls, packet edits, prompt edits, or new scoring rules.

Source commits:

- Batch 001: `582b36e5`
- Batch 002: `8cff396d`

## Combined Result

| Metric | Value |
| --- | ---: |
| Batches included | `2` |
| Holo sibling pairs | `18` |
| Holo packets | `36` |
| Holo packets correct/admissible | `36` |
| Holo valid pairs | `18` |
| Holo provider failures | `0` |
| Holo parse failures | `0` |
| Selected solo attempts | `108` |
| Solo KNEW/admissible | `25` |
| Solo not KNEW | `83` |
| Solo wrong verdicts | `9` |
| Solo parse fails | `19` |
| Solo structural/evidence fails | `55` |
| All-six solo-collapse pairs | `2` |
| Strong solo-collapse pairs | `16` |
| Intra-Holo worker misses corrected | `6` |
| Solo not KNEW rate | `0.768519` |
| Holo vs selected solo token ratio | `3.190515` |
| Gov share of Holo tokens | `0.102662` |

## Batch Comparison

| Batch | Holo packets | Holo valid pairs | Solo KNEW | Solo not KNEW | Wrong verdicts | Parse fails | Structural/evidence fails | All-six pairs | Intra-Holo corrections | Token ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 001 | `18/18` | `9/9` | `7` | `47` | `0` | `10` | `37` | `2` | `1` | `3.310468` |
| 002 | `18/18` | `9/9` | `18` | `36` | `9` | `9` | `18` | `0` | `5` | `3.078516` |

## Claim Boundaries

- This memo covers only Wave 2 Holo target Batch 001 and Batch 002, not the entire Wave 2 frozen packet bank.
- Holo solved all selected target packets run so far: 36/36 packets and 18/18 sibling pairs.
- The matched solo one-shot results on the same selected packets were unreliable: 83/108 attempts were not KNEW/admissible.
- Batch 002 is not an all-six solo-collapse batch. Its evidence value is stronger wrong-verdict signal: 9 solo wrong verdicts versus 0 in Batch 001.
- Token ratio is operational bookkeeping only. It is not a proof claim because solo was one-shot while Holo used governed multi-turn architecture.
- No judges are included in this package. No new provider calls were made to create the comparison memo.
- Internal Holo worker misses are separated from external solo failures. They show governance correction, not standalone solo failure.

## Why Batch 002 Matters

Batch 002 is not an all-six-collapse batch. Its evidence value is different: it contains 9 solo wrong verdicts while Holo still solved 18/18 packets and 9/9 pairs. That makes Batch 002 useful for showing verdict-level boundary failure, not just parse or admissibility brittleness.

## Family Breakdown

| Family | Pairs | Packets | Holo correct/admissible packets | Solo attempts | Solo KNEW | Solo not KNEW | Wrong verdicts | Parse fails | Structural/evidence fails |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `HV-DPRV-REP-2026-07-01` | `4` | `8` | `8` | `24` | `7` | `17` | `3` | `5` | `9` |
| `HV-FINC-REP-2026-07-01` | `9` | `18` | `18` | `54` | `11` | `43` | `4` | `9` | `30` |
| `HV-HRWF-REP-2026-07-01` | `5` | `10` | `10` | `30` | `7` | `23` | `2` | `5` | `16` |

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

## Remaining Target Pool

Solo triage produced `37` top targets. Batch 001+002 have run `18` pairs, leaving `19` target pairs.

Recommended Batch 003 preview:

| Rank | Family | Pair | Class | Bucket | Not KNEW | Wrong verdicts | Score |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: |
| `1` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-001` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `10` |
| `2` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-001` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `9` |
| `3` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-014` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `9` |
| `4` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-015` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `9` |
| `5` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-018` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `9` |
| `6` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-020` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `9` |
| `7` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-001` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `9` |
| `8` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-007` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `9` |
| `9` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-009` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `9` |

## Next Valid Step

Stage Wave 2 Holo Target Batch 003 from the remaining target pool. Do not run providers until live run is explicitly approved.
