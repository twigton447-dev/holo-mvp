# HoloVerify 3-Family Solo Triage

Classification: `HOLOVERIFY_REPLICATION_3FAMILY_SOLO_TRIAGE_COMPLETE`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
Provider calls: `30` / `30`
Gov calls: `0`
Holo calls: `0`
Judge calls: `0`
Tokens: `16353` input / `13487` output / `34895` total

## Family Results

| Family | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `HV-AP-REP-2026-06-29` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-ACOM-REP-2026-06-29` | 30 / 30 | 8 | 22 | 0 | 12 | 0 |
| `HV-ITAC-REP-2026-06-29` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |

## Model Results

| Model | Calls | KNEW | Verdict Correct | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `xai/grok-3-mini` | 10 / 10 | 2 | 10 | 0 | 8 | 0 | 0 |
| `openai/gpt-4o-mini` | 10 / 10 | 0 | 0 | 0 | 0 | 10 | 0 |
| `minimax/MiniMax-M2.5-highspeed` | 10 / 10 | 6 | 8 | 0 | 2 | 2 | 0 |

## Top Holo Targets

| Class | Family | Pair | Target bucket | Not KNEW | Wrong verdict | Packets |
| --- | --- | --- | --- | ---: | ---: | --- |
| `ALL_SIX_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-004` | `hard_allow` | 6 | 0 | `HV-ACOM-REP-004-A, HV-ACOM-REP-004-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-001` | `hard_allow` | 4 | 0 | `HV-ACOM-REP-001-A, HV-ACOM-REP-001-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-002` | `hard_allow` | 4 | 0 | `HV-ACOM-REP-002-A, HV-ACOM-REP-002-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-003` | `hard_allow` | 4 | 0 | `HV-ACOM-REP-003-A, HV-ACOM-REP-003-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-ACOM-REP-2026-06-29` | `HV-ACOM-REP-005` | `hard_allow` | 4 | 0 | `HV-ACOM-REP-005-A, HV-ACOM-REP-005-B` |
