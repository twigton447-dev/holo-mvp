# HoloVerify 3-Family Solo Triage

Classification: `HOLOVERIFY_REPLICATION_3FAMILY_WAVE2_SOLO_TRIAGE_COMPLETE`
Freeze root: `80d8106d7efe72bee44d2c05648b71814204c08e1f96934afefd3d75d242845f`
Provider calls: `120` / `120`
Gov calls: `0`
Holo calls: `0`
Judge calls: `0`
Tokens: `65857` input / `55180` output / `142174` total

## Family Results

| Family | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `HV-HRWF-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-DPRV-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-FINC-REP-2026-07-01` | 120 / 120 | 39 | 81 | 6 | 15 | 0 |

## Model Results

| Model | Calls | KNEW | Verdict Correct | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `xai/grok-3-mini` | 40 / 40 | 4 | 34 | 6 | 30 | 0 | 0 |
| `openai/gpt-5.4-mini` | 40 / 40 | 19 | 40 | 0 | 21 | 0 | 0 |
| `minimax/MiniMax-M2.5-highspeed` | 40 / 40 | 16 | 25 | 0 | 9 | 15 | 0 |

## Top Holo Targets

| Class | Family | Pair | Target bucket | Not KNEW | Wrong verdict | Packets |
| --- | --- | --- | --- | ---: | ---: | --- |
| `ALL_SIX_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-004` | `hard_allow` | 6 | 0 | `HV-FINC-REP-004-A, HV-FINC-REP-004-B` |
| `ALL_SIX_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-010` | `hard_allow` | 6 | 0 | `HV-FINC-REP-010-A, HV-FINC-REP-010-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-003` | `hard_allow` | 5 | 0 | `HV-FINC-REP-003-A, HV-FINC-REP-003-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-006` | `hard_allow` | 5 | 0 | `HV-FINC-REP-006-A, HV-FINC-REP-006-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-013` | `hard_escalate` | 5 | 0 | `HV-FINC-REP-013-A, HV-FINC-REP-013-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-011` | `hard_escalate` | 4 | 1 | `HV-FINC-REP-011-A, HV-FINC-REP-011-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-012` | `hard_escalate` | 4 | 1 | `HV-FINC-REP-012-A, HV-FINC-REP-012-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-015` | `hard_escalate` | 4 | 1 | `HV-FINC-REP-015-A, HV-FINC-REP-015-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-019` | `hard_escalate` | 4 | 1 | `HV-FINC-REP-019-A, HV-FINC-REP-019-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-001` | `hard_allow` | 4 | 0 | `HV-FINC-REP-001-A, HV-FINC-REP-001-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-002` | `hard_allow` | 4 | 0 | `HV-FINC-REP-002-A, HV-FINC-REP-002-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-007` | `hard_allow` | 4 | 0 | `HV-FINC-REP-007-A, HV-FINC-REP-007-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-009` | `hard_allow` | 4 | 0 | `HV-FINC-REP-009-A, HV-FINC-REP-009-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-016` | `hard_escalate` | 4 | 0 | `HV-FINC-REP-016-A, HV-FINC-REP-016-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-017` | `hard_escalate` | 4 | 0 | `HV-FINC-REP-017-A, HV-FINC-REP-017-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-020` | `hard_escalate` | 4 | 0 | `HV-FINC-REP-020-A, HV-FINC-REP-020-B` |
