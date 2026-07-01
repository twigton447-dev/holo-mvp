# HoloVerify 3-Family Solo Triage

Classification: `HOLOVERIFY_REPLICATION_3FAMILY_WAVE2_SOLO_TRIAGE_COMPLETE`
Freeze root: `80d8106d7efe72bee44d2c05648b71814204c08e1f96934afefd3d75d242845f`
Provider calls: `120` / `120`
Gov calls: `0`
Holo calls: `0`
Judge calls: `0`
Tokens: `66425` input / `54628` output / `142508` total

## Family Results

| Family | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `HV-HRWF-REP-2026-07-01` | 120 / 120 | 43 | 77 | 3 | 16 | 0 |
| `HV-DPRV-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-FINC-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |

## Model Results

| Model | Calls | KNEW | Verdict Correct | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `xai/grok-3-mini` | 40 / 40 | 7 | 37 | 3 | 30 | 0 | 0 |
| `openai/gpt-5.4-mini` | 40 / 40 | 23 | 40 | 0 | 17 | 0 | 0 |
| `minimax/MiniMax-M2.5-highspeed` | 40 / 40 | 13 | 24 | 0 | 11 | 16 | 0 |

## Top Holo Targets

| Class | Family | Pair | Target bucket | Not KNEW | Wrong verdict | Packets |
| --- | --- | --- | --- | ---: | ---: | --- |
| `ALL_SIX_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-009` | `hard_allow` | 6 | 0 | `HV-HRWF-REP-009-A, HV-HRWF-REP-009-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-002` | `hard_allow` | 5 | 0 | `HV-HRWF-REP-002-A, HV-HRWF-REP-002-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-003` | `hard_allow` | 5 | 0 | `HV-HRWF-REP-003-A, HV-HRWF-REP-003-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-008` | `hard_allow` | 5 | 0 | `HV-HRWF-REP-008-A, HV-HRWF-REP-008-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-010` | `hard_allow` | 5 | 0 | `HV-HRWF-REP-010-A, HV-HRWF-REP-010-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-012` | `hard_escalate` | 5 | 0 | `HV-HRWF-REP-012-A, HV-HRWF-REP-012-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-019` | `hard_escalate` | 5 | 0 | `HV-HRWF-REP-019-A, HV-HRWF-REP-019-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-017` | `hard_escalate` | 4 | 1 | `HV-HRWF-REP-017-A, HV-HRWF-REP-017-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-018` | `hard_escalate` | 4 | 1 | `HV-HRWF-REP-018-A, HV-HRWF-REP-018-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-005` | `hard_allow` | 4 | 0 | `HV-HRWF-REP-005-A, HV-HRWF-REP-005-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-006` | `hard_allow` | 4 | 0 | `HV-HRWF-REP-006-A, HV-HRWF-REP-006-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-007` | `hard_allow` | 4 | 0 | `HV-HRWF-REP-007-A, HV-HRWF-REP-007-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-011` | `hard_escalate` | 4 | 0 | `HV-HRWF-REP-011-A, HV-HRWF-REP-011-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-015` | `hard_escalate` | 4 | 0 | `HV-HRWF-REP-015-A, HV-HRWF-REP-015-B` |
