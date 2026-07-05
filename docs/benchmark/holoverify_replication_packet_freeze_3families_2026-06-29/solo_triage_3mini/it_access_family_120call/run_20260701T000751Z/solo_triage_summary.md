# HoloVerify 3-Family Solo Triage

Classification: `HOLOVERIFY_REPLICATION_3FAMILY_SOLO_TRIAGE_COMPLETE`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
Provider calls: `120` / `120`
Gov calls: `0`
Holo calls: `0`
Judge calls: `0`
Tokens: `64472` input / `57462` output / `142943` total

## Family Results

| Family | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `HV-AP-REP-2026-06-29` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-ACOM-REP-2026-06-29` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-ITAC-REP-2026-06-29` | 120 / 120 | 24 | 96 | 9 | 55 | 0 |

## Model Results

| Model | Calls | KNEW | Verdict Correct | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `xai/grok-3-mini` | 40 / 40 | 4 | 32 | 8 | 28 | 0 | 0 |
| `openai/gpt-4o-mini` | 40 / 40 | 0 | 0 | 0 | 0 | 40 | 0 |
| `minimax/MiniMax-M2.5-highspeed` | 40 / 40 | 20 | 24 | 1 | 4 | 15 | 0 |

## Top Holo Targets

| Class | Family | Pair | Target bucket | Not KNEW | Wrong verdict | Packets |
| --- | --- | --- | --- | ---: | ---: | --- |
| `ALL_SIX_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-018` | `hard_escalate` | 6 | 2 | `HV-ITAC-REP-018-A, HV-ITAC-REP-018-B` |
| `ALL_SIX_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-012` | `hard_escalate` | 6 | 1 | `HV-ITAC-REP-012-A, HV-ITAC-REP-012-B` |
| `ALL_SIX_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-016` | `hard_escalate` | 6 | 1 | `HV-ITAC-REP-016-A, HV-ITAC-REP-016-B` |
| `ALL_SIX_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-010` | `hard_allow` | 6 | 0 | `HV-ITAC-REP-010-A, HV-ITAC-REP-010-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-011` | `hard_escalate` | 5 | 1 | `HV-ITAC-REP-011-A, HV-ITAC-REP-011-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-013` | `hard_escalate` | 5 | 1 | `HV-ITAC-REP-013-A, HV-ITAC-REP-013-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-015` | `hard_escalate` | 5 | 1 | `HV-ITAC-REP-015-A, HV-ITAC-REP-015-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-020` | `hard_escalate` | 5 | 1 | `HV-ITAC-REP-020-A, HV-ITAC-REP-020-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-005` | `hard_allow` | 5 | 0 | `HV-ITAC-REP-005-A, HV-ITAC-REP-005-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-006` | `hard_allow` | 5 | 0 | `HV-ITAC-REP-006-A, HV-ITAC-REP-006-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-007` | `hard_allow` | 5 | 0 | `HV-ITAC-REP-007-A, HV-ITAC-REP-007-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-014` | `hard_escalate` | 5 | 0 | `HV-ITAC-REP-014-A, HV-ITAC-REP-014-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-019` | `hard_escalate` | 5 | 0 | `HV-ITAC-REP-019-A, HV-ITAC-REP-019-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-017` | `hard_escalate` | 4 | 1 | `HV-ITAC-REP-017-A, HV-ITAC-REP-017-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-001` | `hard_allow` | 4 | 0 | `HV-ITAC-REP-001-A, HV-ITAC-REP-001-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-002` | `hard_allow` | 4 | 0 | `HV-ITAC-REP-002-A, HV-ITAC-REP-002-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-003` | `hard_allow` | 4 | 0 | `HV-ITAC-REP-003-A, HV-ITAC-REP-003-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-008` | `hard_allow` | 4 | 0 | `HV-ITAC-REP-008-A, HV-ITAC-REP-008-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ITAC-REP-2026-06-29` | `HV-ITAC-REP-009` | `hard_allow` | 4 | 0 | `HV-ITAC-REP-009-A, HV-ITAC-REP-009-B` |
