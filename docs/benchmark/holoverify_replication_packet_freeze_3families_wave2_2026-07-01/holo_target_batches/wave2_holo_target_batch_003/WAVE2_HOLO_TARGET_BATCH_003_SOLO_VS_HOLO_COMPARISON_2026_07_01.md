# WAVE2_HOLO_TARGET_BATCH_003 Solo vs Holo Comparison

Classification: `WAVE2_HOLO_TARGET_BATCH_003_SOLO_VS_HOLO_COMPARISON_COMPLETE`
Package SHA-256: `664f61cbb16805aca3259185cee5e180981d0fcca01391cfdd0b62f57f3fec8b`

## Scope

This is a no-provider comparison built from the completed Holo live run and the existing Wave 2 solo triage package.

## Summary Metrics

| Metric | Value |
| --- | ---: |
| Holo packets correct/admissible | `18` |
| Holo packets total | `18` |
| Holo valid pairs | `9` |
| Holo pair count | `9` |
| Holo provider failures | `0` |
| Solo attempts on selected packets | `54` |
| Solo KNEW/admissible | `18` |
| Solo not KNEW | `36` |
| Solo wrong verdicts | `0` |
| Solo parse fails | `10` |
| Solo structural/evidence fails | `26` |
| All-six solo-collapse pairs | `0` |
| Strong solo-collapse pairs | `9` |
| Intra-Holo worker misses corrected | `2` |
| Holo/selected solo token ratio | `3.143891` |

## Claim Boundaries

- This comparison covers only WAVE2_HOLO_TARGET_BATCH_003, not all Wave 2 packets.
- No new provider calls, Holo calls, solo calls, or judge calls were made to build this comparison.
- Solo evidence comes from the existing Wave 2 three-mini one-shot solo triage package.
- Internal Holo worker misses are separated from external solo failures.
- Token ratio is operational bookkeeping, not a proof claim.

## Pair Rows

| Pair | Family | Bucket | Solo not KNEW | Solo wrong verdicts | Holo target | Holo guardrail | Evidence class |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| `HV-DPRV-REP-001` | `HV-DPRV-REP-2026-07-01` | `hard_allow` | `4` | `0` | `HV-DPRV-REP-001-A ALLOW->ALLOW` | `HV-DPRV-REP-001-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-DPRV-REP-014` | `HV-DPRV-REP-2026-07-01` | `hard_escalate` | `4` | `0` | `HV-DPRV-REP-014-B ESCALATE->ESCALATE` | `HV-DPRV-REP-014-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-DPRV-REP-015` | `HV-DPRV-REP-2026-07-01` | `hard_escalate` | `4` | `0` | `HV-DPRV-REP-015-B ESCALATE->ESCALATE` | `HV-DPRV-REP-015-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-DPRV-REP-018` | `HV-DPRV-REP-2026-07-01` | `hard_escalate` | `4` | `0` | `HV-DPRV-REP-018-B ESCALATE->ESCALATE` | `HV-DPRV-REP-018-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-DPRV-REP-020` | `HV-DPRV-REP-2026-07-01` | `hard_escalate` | `4` | `0` | `HV-DPRV-REP-020-B ESCALATE->ESCALATE` | `HV-DPRV-REP-020-A ALLOW->ALLOW` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-FINC-REP-001` | `HV-FINC-REP-2026-07-01` | `hard_allow` | `4` | `0` | `HV-FINC-REP-001-A ALLOW->ALLOW` | `HV-FINC-REP-001-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-FINC-REP-007` | `HV-FINC-REP-2026-07-01` | `hard_allow` | `4` | `0` | `HV-FINC-REP-007-A ALLOW->ALLOW` | `HV-FINC-REP-007-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-FINC-REP-009` | `HV-FINC-REP-2026-07-01` | `hard_allow` | `4` | `0` | `HV-FINC-REP-009-A ALLOW->ALLOW` | `HV-FINC-REP-009-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |
| `HV-HRWF-REP-001` | `HV-HRWF-REP-2026-07-01` | `hard_allow` | `4` | `0` | `HV-HRWF-REP-001-A ALLOW->ALLOW` | `HV-HRWF-REP-001-B ESCALATE->ESCALATE` | `STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED` |

## Holo Run

- `classification`: `WAVE2_HOLO_TARGET_BATCH_003_COMPLETE`
- `run_dir`: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_003/live_runs/run_20260701T054545Z`
- `readiness_passed`: `True`
- `trace_hash`: `3dbd34deeb719a08a91697f4585e9a685750120ed48739a1b8b79f8f8c75aa2f`
- `lock_validation_status`: `PASS`
- `no_leakage_status`: `PASS`
