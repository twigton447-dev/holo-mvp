# WAVE2_HOLO_TARGET_BATCH_004 Solo vs Holo Comparison

Classification: `WAVE2_HOLO_TARGET_BATCH_004_SOLO_VS_HOLO_COMPARISON_COMPLETE`
Package SHA-256: `c031012847029399974fdc8218da45459f3886b13cc367369601b791159015da`

## Scope

This is a no-provider comparison built from the completed Holo live run and the existing Wave 2 solo triage package.

## Summary Metrics

| Metric | Value |
| --- | ---: |
| Holo packets correct/admissible | `20` |
| Holo packets total | `20` |
| Holo valid pairs | `10` |
| Holo pair count | `10` |
| Holo provider failures | `0` |
| Solo attempts on selected packets | `60` |
| Solo KNEW/admissible | `20` |
| Solo not KNEW | `40` |
| Solo wrong verdicts | `0` |
| Solo parse fails | `1` |
| Solo structural/evidence fails | `39` |
| All-six solo-collapse pairs | `0` |
| Strong solo-collapse pairs | `10` |
| Non-target full-family completion pairs | `0` |
| Intra-Holo worker misses corrected | `2` |
| Holo/selected solo token ratio | `3.244341` |

## Claim Boundaries

- This comparison covers only WAVE2_HOLO_TARGET_BATCH_004, not all Wave 2 packets.
- No new provider calls, Holo calls, solo calls, or judge calls were made to build this comparison.
- Solo evidence comes from the existing Wave 2 three-mini one-shot solo triage package.
- Internal Holo worker misses are separated from external solo failures.
- Token ratio is operational bookkeeping, not a proof claim.

## Pair Rows

| Pair | Family | Bucket | Solo not KNEW | Solo wrong verdicts | Holo target | Holo guardrail | Evidence class |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| `HV-DPRV-REP-005` | `HV-DPRV-REP-2026-07-01` | `hard_allow` | `4` | `0` | `HV-DPRV-REP-005-A ALLOW->ALLOW` | `HV-DPRV-REP-005-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-DPRV-REP-007` | `HV-DPRV-REP-2026-07-01` | `hard_allow` | `4` | `0` | `HV-DPRV-REP-007-A ALLOW->ALLOW` | `HV-DPRV-REP-007-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-DPRV-REP-008` | `HV-DPRV-REP-2026-07-01` | `hard_allow` | `4` | `0` | `HV-DPRV-REP-008-A ALLOW->ALLOW` | `HV-DPRV-REP-008-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-FINC-REP-002` | `HV-FINC-REP-2026-07-01` | `hard_allow` | `4` | `0` | `HV-FINC-REP-002-A ALLOW->ALLOW` | `HV-FINC-REP-002-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-FINC-REP-016` | `HV-FINC-REP-2026-07-01` | `hard_escalate` | `4` | `0` | `HV-FINC-REP-016-B ESCALATE->ESCALATE` | `HV-FINC-REP-016-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-FINC-REP-017` | `HV-FINC-REP-2026-07-01` | `hard_escalate` | `4` | `0` | `HV-FINC-REP-017-B ESCALATE->ESCALATE` | `HV-FINC-REP-017-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-FINC-REP-020` | `HV-FINC-REP-2026-07-01` | `hard_escalate` | `4` | `0` | `HV-FINC-REP-020-B ESCALATE->ESCALATE` | `HV-FINC-REP-020-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-HRWF-REP-006` | `HV-HRWF-REP-2026-07-01` | `hard_allow` | `4` | `0` | `HV-HRWF-REP-006-A ALLOW->ALLOW` | `HV-HRWF-REP-006-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-HRWF-REP-007` | `HV-HRWF-REP-2026-07-01` | `hard_allow` | `4` | `0` | `HV-HRWF-REP-007-A ALLOW->ALLOW` | `HV-HRWF-REP-007-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-HRWF-REP-010` | `HV-HRWF-REP-2026-07-01` | `hard_allow` | `4` | `0` | `HV-HRWF-REP-010-A ALLOW->ALLOW` | `HV-HRWF-REP-010-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |

## Holo Run

- `classification`: `WAVE2_HOLO_TARGET_BATCH_004_COMPLETE`
- `run_dir`: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/live_runs/run_20260701T132715Z`
- `readiness_passed`: `True`
- `trace_hash`: `b78a66e5afcb0e2cc6cd9266217c83c07dffb46f5d3519f9c1865f0b17fdfee5`
- `lock_validation_status`: `PASS`
- `no_leakage_status`: `PASS`
