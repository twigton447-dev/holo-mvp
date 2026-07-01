# IT Access Replacement 015R1 Frozen Run Summary

Created: 2026-07-01

## Classification

`IT_ACCESS_REPLACEMENT_015R1_FROZEN_HOLO_PASS`

This freezes the successful targeted replacement run for the quarantined ambiguous pair `HV-ITAC-REP-015`.

## Lineage

- Retired pair: `HV-ITAC-REP-015`
- Replacement pair: `HV-ITAC-REP-015R1`
- Replacement freeze commit: `1b914293`
- Replacement freeze root: `6c61024da5f6c36c1ee5210b95efd1d7a1ed0caff60a11efe0ace1ca1e72dc4e`
- Original 3-family freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Run

- Run folder: `holo_live_runs_openai_w2_batched/replacement_015r1/run_20260701T012935Z`
- Classification: `IT_ACCESS_OPENAI_W2_BATCHED_HOLO_BATCH_COMPLETE`
- Readiness passed: `true`
- Provider calls: `10 / 10`
- Worker calls: `6`
- Gov calls: `4`
- Solo calls: `0`
- Judge calls: `0`
- Provider failures: `0`
- Transport recovered calls: `0`
- Tokens: `17757` input / `3071` output / `22521` total

## Verdicts

| Packet | Expected | Final | Correct |
| --- | --- | --- | --- |
| `HV-ITAC-REP-015R1-A` | `ALLOW` | `ALLOW` | `true` |
| `HV-ITAC-REP-015R1-B` | `ESCALATE` | `ESCALATE` | `true` |

Pair validity: `true`

## Assertions

All run assertions passed:

- `holo_packets`
- `holo_pairs`
- `provider_calls`
- `worker_calls`
- `gov_calls`
- `no_judges`
- `no_solo`
- `provider_failures`
- `no_leakage`
- `packet_identity_matches_freeze`
- `three_dna_present`
- `roster_matches`
- `deterministic_gate_after_every_worker`
- `gov_receives_gate_results`
- `final_selector_present`
- `all_pairs_valid`
- `all_packets_correct`
- `benchmark_laws`

## Evidence Files

- `batch_summary.md`
- `batch_results.json`
- `TRACE_CALLS.jsonl`
- `LOCK_MANIFEST.json`
- `LOCK_VALIDATION.json`
- `IT_ACCESS_OPENAI_W2_BATCHED_HOLO_NO_LEAKAGE_AUDIT.json`
- `IT_ACCESS_OPENAI_W2_BATCHED_HOLO_READINESS_ASSERTIONS.json`
- worker/Gov artifact files
- prompt trace files

## Boundary

This is a targeted replacement run only. It does not run or score solo baselines, judges, AP, Commerce, or any other IT pair.
