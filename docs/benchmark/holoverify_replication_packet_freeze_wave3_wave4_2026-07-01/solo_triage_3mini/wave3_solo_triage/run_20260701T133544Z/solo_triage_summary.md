# HoloVerify 3-Family Solo Triage

Classification: `HOLOVERIFY_REPLICATION_WAVE3_WAVE4_SOLO_TRIAGE_COMPLETE`
Freeze root: `ac44c5d69ad73c64dcae1591e37cc9ade8a80ed5e71a05786cd2490a445c2dd5`
Provider calls: `360` / `360`
Gov calls: `0`
Holo calls: `0`
Judge calls: `0`
Tokens: `200763` input / `164571` output / `437312` total

## Family Results

| Family | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `HV-GOVP-REP-2026-07-01` | 120 / 120 | 65 | 55 | 3 | 14 | 0 |
| `HV-BENC-REP-2026-07-01` | 120 / 120 | 72 | 48 | 3 | 13 | 0 |
| `HV-BKYC-REP-2026-07-01` | 120 / 120 | 68 | 52 | 7 | 16 | 0 |
| `HV-DEFA-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-INSR-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-UTIL-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |

## Model Results

| Model | Calls | KNEW | Verdict Correct | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `xai/grok-3-mini` | 120 / 120 | 30 | 107 | 13 | 77 | 0 | 0 |
| `openai/gpt-5.4-mini` | 120 / 120 | 118 | 120 | 0 | 2 | 0 | 0 |
| `minimax/MiniMax-M2.5-highspeed` | 120 / 120 | 57 | 77 | 0 | 20 | 43 | 0 |

## Top Holo Targets

| Class | Family | Pair | Target bucket | Not KNEW | Wrong verdict | Packets |
| --- | --- | --- | --- | ---: | ---: | --- |
| `STRONG_SOLO_COLLAPSE` | `HV-BENC-REP-2026-07-01` | `HV-BENC-REP-016` | `hard_escalate` | 4 | 1 | `HV-BENC-REP-016-A, HV-BENC-REP-016-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-BKYC-REP-2026-07-01` | `HV-BKYC-REP-011` | `hard_escalate` | 4 | 1 | `HV-BKYC-REP-011-A, HV-BKYC-REP-011-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-BKYC-REP-2026-07-01` | `HV-BKYC-REP-016` | `hard_escalate` | 4 | 1 | `HV-BKYC-REP-016-A, HV-BKYC-REP-016-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-BKYC-REP-2026-07-01` | `HV-BKYC-REP-018` | `hard_escalate` | 4 | 1 | `HV-BKYC-REP-018-A, HV-BKYC-REP-018-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-BKYC-REP-2026-07-01` | `HV-BKYC-REP-020` | `hard_escalate` | 4 | 1 | `HV-BKYC-REP-020-A, HV-BKYC-REP-020-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-GOVP-REP-2026-07-01` | `HV-GOVP-REP-012` | `hard_escalate` | 4 | 1 | `HV-GOVP-REP-012-A, HV-GOVP-REP-012-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-BENC-REP-2026-07-01` | `HV-BENC-REP-001` | `hard_allow` | 4 | 0 | `HV-BENC-REP-001-A, HV-BENC-REP-001-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-BENC-REP-2026-07-01` | `HV-BENC-REP-015` | `hard_escalate` | 4 | 0 | `HV-BENC-REP-015-A, HV-BENC-REP-015-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-BENC-REP-2026-07-01` | `HV-BENC-REP-020` | `hard_escalate` | 4 | 0 | `HV-BENC-REP-020-A, HV-BENC-REP-020-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-BKYC-REP-2026-07-01` | `HV-BKYC-REP-009` | `hard_allow` | 4 | 0 | `HV-BKYC-REP-009-A, HV-BKYC-REP-009-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-GOVP-REP-2026-07-01` | `HV-GOVP-REP-006` | `hard_allow` | 4 | 0 | `HV-GOVP-REP-006-A, HV-GOVP-REP-006-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-GOVP-REP-2026-07-01` | `HV-GOVP-REP-014` | `hard_escalate` | 4 | 0 | `HV-GOVP-REP-014-A, HV-GOVP-REP-014-B` |
