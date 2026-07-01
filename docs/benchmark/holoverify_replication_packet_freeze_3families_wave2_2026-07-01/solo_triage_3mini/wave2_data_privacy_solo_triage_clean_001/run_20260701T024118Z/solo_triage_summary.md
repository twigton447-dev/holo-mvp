# HoloVerify 3-Family Solo Triage

Classification: `HOLOVERIFY_REPLICATION_3FAMILY_WAVE2_SOLO_TRIAGE_COMPLETE`
Freeze root: `80d8106d7efe72bee44d2c05648b71814204c08e1f96934afefd3d75d242845f`
Provider calls: `120` / `120`
Gov calls: `0`
Holo calls: `0`
Judge calls: `0`
Tokens: `65941` input / `58236` output / `145717` total

## Family Results

| Family | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `HV-HRWF-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-DPRV-REP-2026-07-01` | 120 / 120 | 49 | 71 | 4 | 13 | 0 |
| `HV-FINC-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |

## Model Results

| Model | Calls | KNEW | Verdict Correct | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `xai/grok-3-mini` | 40 / 40 | 3 | 36 | 4 | 33 | 0 | 0 |
| `openai/gpt-5.4-mini` | 40 / 40 | 25 | 40 | 0 | 15 | 0 | 0 |
| `minimax/MiniMax-M2.5-highspeed` | 40 / 40 | 21 | 27 | 0 | 6 | 13 | 0 |

## Top Holo Targets

| Class | Family | Pair | Target bucket | Not KNEW | Wrong verdict | Packets |
| --- | --- | --- | --- | ---: | ---: | --- |
| `STRONG_SOLO_COLLAPSE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-009` | `hard_allow` | 5 | 0 | `HV-DPRV-REP-009-A, HV-DPRV-REP-009-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-012` | `hard_escalate` | 4 | 1 | `HV-DPRV-REP-012-A, HV-DPRV-REP-012-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-013` | `hard_escalate` | 4 | 1 | `HV-DPRV-REP-013-A, HV-DPRV-REP-013-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-019` | `hard_escalate` | 4 | 1 | `HV-DPRV-REP-019-A, HV-DPRV-REP-019-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-001` | `hard_allow` | 4 | 0 | `HV-DPRV-REP-001-A, HV-DPRV-REP-001-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-005` | `hard_allow` | 4 | 0 | `HV-DPRV-REP-005-A, HV-DPRV-REP-005-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-007` | `hard_allow` | 4 | 0 | `HV-DPRV-REP-007-A, HV-DPRV-REP-007-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-008` | `hard_allow` | 4 | 0 | `HV-DPRV-REP-008-A, HV-DPRV-REP-008-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-014` | `hard_escalate` | 4 | 0 | `HV-DPRV-REP-014-A, HV-DPRV-REP-014-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-015` | `hard_escalate` | 4 | 0 | `HV-DPRV-REP-015-A, HV-DPRV-REP-015-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-018` | `hard_escalate` | 4 | 0 | `HV-DPRV-REP-018-A, HV-DPRV-REP-018-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-020` | `hard_escalate` | 4 | 0 | `HV-DPRV-REP-020-A, HV-DPRV-REP-020-B` |
