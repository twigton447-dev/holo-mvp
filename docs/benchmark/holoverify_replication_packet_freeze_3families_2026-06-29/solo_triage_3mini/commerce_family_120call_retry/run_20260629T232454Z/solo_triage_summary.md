# HoloVerify 3-Family Solo Triage

Classification: `HOLOVERIFY_REPLICATION_3FAMILY_SOLO_TRIAGE_COMPLETE`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
Provider calls: `120` / `120`
Gov calls: `0`
Holo calls: `0`
Judge calls: `0`
Tokens: `65060` input / `55586` output / `142165` total

## Family Results

| Family | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `HV-AP-REP-2026-06-29` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-ACOM-REP-2026-06-29` | 120 / 120 | 26 | 94 | 4 | 56 | 0 |
| `HV-ITAC-REP-2026-06-29` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |

## Model Results

| Model | Calls | KNEW | Verdict Correct | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `xai/grok-3-mini` | 40 / 40 | 7 | 36 | 4 | 29 | 0 | 0 |
| `openai/gpt-4o-mini` | 40 / 40 | 0 | 0 | 0 | 0 | 40 | 0 |
| `minimax/MiniMax-M2.5-highspeed` | 40 / 40 | 19 | 24 | 0 | 5 | 16 | 0 |

## Top Holo Targets

| Class | Family | Pair | Target bucket | Not KNEW | Wrong verdict | Packets |
| --- | --- | --- | --- | ---: | ---: | --- |
| `ALL_SIX_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-020` | `hard_escalate` | 6 | 1 | `HV-ACOM-REP-020-A, HV-ACOM-REP-020-B` |
| `ALL_SIX_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-006` | `hard_allow` | 6 | 0 | `HV-ACOM-REP-006-A, HV-ACOM-REP-006-B` |
| `ALL_SIX_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-019` | `hard_escalate` | 6 | 0 | `HV-ACOM-REP-019-A, HV-ACOM-REP-019-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-011` | `hard_escalate` | 5 | 1 | `HV-ACOM-REP-011-A, HV-ACOM-REP-011-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-003` | `hard_allow` | 5 | 0 | `HV-ACOM-REP-003-A, HV-ACOM-REP-003-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-007` | `hard_allow` | 5 | 0 | `HV-ACOM-REP-007-A, HV-ACOM-REP-007-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-012` | `hard_escalate` | 5 | 0 | `HV-ACOM-REP-012-A, HV-ACOM-REP-012-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-014` | `hard_escalate` | 5 | 0 | `HV-ACOM-REP-014-A, HV-ACOM-REP-014-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-015` | `hard_escalate` | 5 | 0 | `HV-ACOM-REP-015-A, HV-ACOM-REP-015-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-016` | `hard_escalate` | 5 | 0 | `HV-ACOM-REP-016-A, HV-ACOM-REP-016-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-018` | `hard_escalate` | 5 | 0 | `HV-ACOM-REP-018-A, HV-ACOM-REP-018-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-013` | `hard_escalate` | 4 | 1 | `HV-ACOM-REP-013-A, HV-ACOM-REP-013-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-017` | `hard_escalate` | 4 | 1 | `HV-ACOM-REP-017-A, HV-ACOM-REP-017-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-001` | `hard_allow` | 4 | 0 | `HV-ACOM-REP-001-A, HV-ACOM-REP-001-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-002` | `hard_allow` | 4 | 0 | `HV-ACOM-REP-002-A, HV-ACOM-REP-002-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-004` | `hard_allow` | 4 | 0 | `HV-ACOM-REP-004-A, HV-ACOM-REP-004-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-005` | `hard_allow` | 4 | 0 | `HV-ACOM-REP-005-A, HV-ACOM-REP-005-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-008` | `hard_allow` | 4 | 0 | `HV-ACOM-REP-008-A, HV-ACOM-REP-008-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-009` | `hard_allow` | 4 | 0 | `HV-ACOM-REP-009-A, HV-ACOM-REP-009-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-010` | `hard_allow` | 4 | 0 | `HV-ACOM-REP-010-A, HV-ACOM-REP-010-B` |
