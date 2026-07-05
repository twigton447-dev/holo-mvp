# Wave 2 Holo Target Selection From Solo Triage

Classification: `WAVE2_HOLO_TARGET_SELECTION_FROM_SOLO_TRIAGE_COMPLETE`
Package SHA-256: `75e6681b163a7c2e2ab70e69ab161ac53b727c0d311774609e2eca1959874c99`

## Selection Rule

Recommended first batch includes every all-six-solo-collapse pair plus every top target with at least 5 of 6 solo attempts not KNEW. No Holo or judge calls were used to create this selection.

## Recommended First Batch

| Family | Pair | Class | Bucket | Not KNEW | Wrong Verdict | Parse/Provider Fail | Packets |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-004` | `ALL_SIX_SOLO_COLLAPSE` | `hard_allow` | `6` | `0` | `1` | `HV-FINC-REP-004-A, HV-FINC-REP-004-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-010` | `ALL_SIX_SOLO_COLLAPSE` | `hard_allow` | `6` | `0` | `1` | `HV-FINC-REP-010-A, HV-FINC-REP-010-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-009` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `5` | `0` | `2` | `HV-DPRV-REP-009-A, HV-DPRV-REP-009-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-012` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `5` | `0` | `2` | `HV-HRWF-REP-012-A, HV-HRWF-REP-012-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-018` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `5` | `0` | `2` | `HV-HRWF-REP-018-A, HV-HRWF-REP-018-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-003` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `5` | `0` | `1` | `HV-FINC-REP-003-A, HV-FINC-REP-003-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-006` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `5` | `0` | `1` | `HV-FINC-REP-006-A, HV-FINC-REP-006-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-013` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `5` | `0` | `0` | `HV-FINC-REP-013-A, HV-FINC-REP-013-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-019` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `5` | `0` | `0` | `HV-HRWF-REP-019-A, HV-HRWF-REP-019-B` |

## Domain Target Counts

| Family | Top Targets | All-Six | Not KNEW >= 5 | Wrong-Verdict Pairs |
| --- | ---: | ---: | ---: | ---: |
| `HV-FINC-REP-2026-07-01` | `16` | `2` | `5` | `4` |
| `HV-DPRV-REP-2026-07-01` | `12` | `0` | `1` | `3` |
| `HV-HRWF-REP-2026-07-01` | `9` | `0` | `3` | `2` |

## All Top Targets

| Family | Pair | Class | Bucket | Not KNEW | Wrong Verdict | Score |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-004` | `ALL_SIX_SOLO_COLLAPSE` | `hard_allow` | `6` | `0` | `23` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-010` | `ALL_SIX_SOLO_COLLAPSE` | `hard_allow` | `6` | `0` | `23` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-011` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `1` | `13` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-009` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `5` | `0` | `12` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-012` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `1` | `12` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-013` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `1` | `12` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-019` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `1` | `12` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-012` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `1` | `12` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-015` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `1` | `12` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-019` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `1` | `12` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-012` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `5` | `0` | `12` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-017` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `1` | `12` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-018` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `5` | `0` | `12` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-003` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `5` | `0` | `11` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-006` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `5` | `0` | `11` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-020` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `1` | `11` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-013` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `5` | `0` | `10` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-001` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `10` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-019` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `5` | `0` | `10` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-001` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `9` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-014` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `9` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-015` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `9` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-018` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `9` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-020` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `9` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-001` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `9` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-007` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `9` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-009` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `9` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-016` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `9` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-005` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `8` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-007` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `8` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-008` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `8` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-002` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `8` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-017` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `8` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-020` | `STRONG_SOLO_COLLAPSE` | `hard_escalate` | `4` | `0` | `8` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-006` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `8` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-007` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `8` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-010` | `STRONG_SOLO_COLLAPSE` | `hard_allow` | `4` | `0` | `8` |
