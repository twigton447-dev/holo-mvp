# HoloVerify 3-Family Solo Triage

Classification: `HOLOVERIFY_REPLICATION_3FAMILY_SOLO_TRIAGE_COMPLETE`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
Provider calls: `12` / `12`
Gov calls: `0`
Holo calls: `0`
Judge calls: `0`
Tokens: `6586` input / `5323` output / `13769` total

## Family Results

| Family | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `HV-AP-REP-2026-06-29` | 12 / 12 | 3 | 9 | 0 | 4 | 0 |
| `HV-ACOM-REP-2026-06-29` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-ITAC-REP-2026-06-29` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |

## Model Results

| Model | Calls | KNEW | Verdict Correct | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `xai/grok-3-mini` | 4 / 4 | 1 | 4 | 0 | 3 | 0 | 0 |
| `openai/gpt-4o-mini` | 4 / 4 | 0 | 0 | 0 | 0 | 4 | 0 |
| `minimax/MiniMax-M2.5-highspeed` | 4 / 4 | 2 | 4 | 0 | 2 | 0 | 0 |

## Top Holo Targets

| Class | Family | Pair | Target bucket | Not KNEW | Wrong verdict | Packets |
| --- | --- | --- | --- | ---: | ---: | --- |
| `STRONG_SOLO_COLLAPSE` | `HV-AP-REP-2026-06-29` | `HV-AP-REP-002` | `hard_allow` | 5 | 0 | `HV-AP-REP-002-A, HV-AP-REP-002-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-AP-REP-2026-06-29` | `HV-AP-REP-001` | `hard_allow` | 4 | 0 | `HV-AP-REP-001-A, HV-AP-REP-001-B` |
