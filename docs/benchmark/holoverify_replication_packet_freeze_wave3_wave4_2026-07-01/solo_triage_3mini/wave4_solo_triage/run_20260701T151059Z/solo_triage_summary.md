# HoloVerify 3-Family Solo Triage

Classification: `HOLOVERIFY_REPLICATION_WAVE3_WAVE4_SOLO_TRIAGE_COMPLETE`
Freeze root: `ac44c5d69ad73c64dcae1591e37cc9ade8a80ed5e71a05786cd2490a445c2dd5`
Provider calls: `360` / `360`
Gov calls: `0`
Holo calls: `0`
Judge calls: `0`
Tokens: `205068` input / `166828` output / `445098` total

## Family Results

| Family | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `HV-GOVP-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-BENC-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-BKYC-REP-2026-07-01` | 0 / 0 | 0 | 0 | 0 | 0 | 0 |
| `HV-DEFA-REP-2026-07-01` | 120 / 120 | 64 | 56 | 3 | 11 | 0 |
| `HV-INSR-REP-2026-07-01` | 120 / 120 | 62 | 58 | 4 | 15 | 0 |
| `HV-UTIL-REP-2026-07-01` | 120 / 120 | 73 | 47 | 4 | 17 | 0 |

## Model Results

| Model | Calls | KNEW | Verdict Correct | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `xai/grok-3-mini` | 120 / 120 | 29 | 109 | 11 | 80 | 0 | 0 |
| `openai/gpt-5.4-mini` | 120 / 120 | 116 | 120 | 0 | 4 | 0 | 0 |
| `minimax/MiniMax-M2.5-highspeed` | 120 / 120 | 54 | 77 | 0 | 23 | 43 | 0 |

## Top Holo Targets

| Class | Family | Pair | Target bucket | Not KNEW | Wrong verdict | Packets |
| --- | --- | --- | --- | ---: | ---: | --- |
| `STRONG_SOLO_COLLAPSE` | `HV-DEFA-REP-2026-07-01` | `HV-DEFA-REP-010` | `hard_allow` | 4 | 1 | `HV-DEFA-REP-010-A, HV-DEFA-REP-010-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DEFA-REP-2026-07-01` | `HV-DEFA-REP-015` | `hard_escalate` | 4 | 1 | `HV-DEFA-REP-015-A, HV-DEFA-REP-015-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-UTIL-REP-2026-07-01` | `HV-UTIL-REP-012` | `hard_escalate` | 4 | 1 | `HV-UTIL-REP-012-A, HV-UTIL-REP-012-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DEFA-REP-2026-07-01` | `HV-DEFA-REP-005` | `hard_allow` | 4 | 0 | `HV-DEFA-REP-005-A, HV-DEFA-REP-005-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DEFA-REP-2026-07-01` | `HV-DEFA-REP-014` | `hard_escalate` | 4 | 0 | `HV-DEFA-REP-014-A, HV-DEFA-REP-014-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DEFA-REP-2026-07-01` | `HV-DEFA-REP-019` | `hard_escalate` | 4 | 0 | `HV-DEFA-REP-019-A, HV-DEFA-REP-019-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-DEFA-REP-2026-07-01` | `HV-DEFA-REP-020` | `hard_escalate` | 4 | 0 | `HV-DEFA-REP-020-A, HV-DEFA-REP-020-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-002` | `hard_allow` | 4 | 0 | `HV-INSR-REP-002-A, HV-INSR-REP-002-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-008` | `hard_allow` | 4 | 0 | `HV-INSR-REP-008-A, HV-INSR-REP-008-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-009` | `hard_allow` | 4 | 0 | `HV-INSR-REP-009-A, HV-INSR-REP-009-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-010` | `hard_allow` | 4 | 0 | `HV-INSR-REP-010-A, HV-INSR-REP-010-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-011` | `hard_escalate` | 4 | 0 | `HV-INSR-REP-011-A, HV-INSR-REP-011-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-018` | `hard_escalate` | 4 | 0 | `HV-INSR-REP-018-A, HV-INSR-REP-018-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-INSR-REP-2026-07-01` | `HV-INSR-REP-020` | `hard_escalate` | 4 | 0 | `HV-INSR-REP-020-A, HV-INSR-REP-020-B` |
| `STRONG_SOLO_COLLAPSE` | `HV-UTIL-REP-2026-07-01` | `HV-UTIL-REP-013` | `hard_escalate` | 4 | 0 | `HV-UTIL-REP-013-A, HV-UTIL-REP-013-B` |
