# HoloVerify 3-Family Solo Triage

Classification: `HOLOVERIFY_REPLICATION_3FAMILY_WAVE2_SOLO_TRIAGE_COMPLETE`
Freeze root: `80d8106d7efe72bee44d2c05648b71814204c08e1f96934afefd3d75d242845f`
Provider calls: `120` / `120`
Gov calls: `0`
Holo calls: `0`
Judge calls: `0`
Tokens: `66425` input / `53769` output / `141882` total

## Family Results

| Family | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `HV-HRWF-REP-2026-07-01` | 120 / 120 | 52 | 68 | 2 | 10 | 0 |
| `HV-DPRV-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-FINC-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |

## Model Results

| Model | Calls | KNEW | Verdict Correct | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `xai/grok-3-mini` | 40 / 40 | 6 | 38 | 2 | 32 | 0 | 0 |
| `openai/gpt-5.4-mini` | 40 / 40 | 27 | 40 | 0 | 13 | 0 | 0 |
| `minimax/MiniMax-M2.5-highspeed` | 40 / 40 | 19 | 30 | 0 | 11 | 10 | 0 |

## Top Holo Targets

| Class | Family | Pair | Target bucket | Not KNEW | Wrong verdict | Packets |
| --- | --- | --- | --- | ---: | ---: | --- |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-012` | `hard_escalate` | 5 | 0 | `HV-HRWF-REP-012-A, HV-HRWF-REP-012-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-018` | `hard_escalate` | 5 | 0 | `HV-HRWF-REP-018-A, HV-HRWF-REP-018-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-019` | `hard_escalate` | 5 | 0 | `HV-HRWF-REP-019-A, HV-HRWF-REP-019-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-017` | `hard_escalate` | 4 | 1 | `HV-HRWF-REP-017-A, HV-HRWF-REP-017-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-020` | `hard_escalate` | 4 | 1 | `HV-HRWF-REP-020-A, HV-HRWF-REP-020-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-001` | `hard_allow` | 4 | 0 | `HV-HRWF-REP-001-A, HV-HRWF-REP-001-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-006` | `hard_allow` | 4 | 0 | `HV-HRWF-REP-006-A, HV-HRWF-REP-006-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-007` | `hard_allow` | 4 | 0 | `HV-HRWF-REP-007-A, HV-HRWF-REP-007-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-010` | `hard_allow` | 4 | 0 | `HV-HRWF-REP-010-A, HV-HRWF-REP-010-B` |
