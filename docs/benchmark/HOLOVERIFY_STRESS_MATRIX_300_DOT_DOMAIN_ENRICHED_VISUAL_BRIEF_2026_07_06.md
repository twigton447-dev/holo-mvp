# HoloVerify 300-Dot Stress Matrix Visual Brief

Status: INTERNAL STRESS-MATRIX DISCOVERY ONLY

This is a derived visual-rendering package. It does not mutate frozen runtime evidence, runtime manifests, prompts, raw outputs, traces, or post-hoc score files.

## What To Render

Render `50` sibling pairs as `50` small 3x2 blocks.

Each pair block has two rows:

| Row | Meaning |
| :--- | :--- |
| ALLOW | The clean sibling for that pair |
| ESCALATE | The blocker sibling for that pair |

Each row has three columns:

| Column | Model |
| :--- | :--- |
| xAI | xai/grok-3-mini |
| OpenAI | openai/gpt-5.4-mini |
| MiniMax | minimax/MiniMax-M2.5-highspeed |

Use dot colors this way:

| Dot | Meaning |
| :--- | :--- |
| Green | KNEW/admissible solo answer |
| Red | Failed solo attempt: wrong verdict or parse/admissibility failure |

## Totals

| Scope | Pairs | Packets | Solo dots | Green | Red |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Wave 1 | 20 | 40 | 120 | 90 | 30 |
| Wave 2 | 30 | 60 | 180 | 124 | 56 |
| Combined | 50 | 100 | 300 | 214 | 86 |

Combined failure split:

| Class | Count |
| :--- | ---: |
| False positive overblock dots | 65 |
| False negative underblock dots | 0 |
| Parse/admissibility dots | 21 |
| Pairs with any red dot | 42 |
| Wrong-verdict pairs | 35 |
| Parse-only pairs | 7 |

## Domain Enrichment

Wave 1 domains come from `HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE1_SOLO_ROLLUP_2026_07_05.json` and its post-hoc score file. Wave 2 domains come from `HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE2_DESIGN_2026_07_06.json`, because the Wave 2 rollup intentionally leaves pair domains null.

| Domain | Pairs | Dots | Green | Red |
| :--- | ---: | ---: | ---: | ---: |
| Banking, KYC & Risk | 10 | 60 | 46 | 14 |
| Clinical & Regulated Activation | 10 | 60 | 43 | 17 |
| Legal, Privacy & Regulatory | 10 | 60 | 41 | 19 |
| Operations, Insurance & Industrial | 10 | 60 | 41 | 19 |
| Public Sector, Benefits & Grants | 10 | 60 | 43 | 17 |

## JSON Shape

Use `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_300_DOT_DOMAIN_ENRICHED_VISUAL_DATA_2026_07_06.json` as the renderer input.

Important fields:

- `totals`: reconciled Wave 1, Wave 2, and combined counts.
- `render_contract`: row order, column order, model labels, and dot color legend.
- `pairs[].dot_block`: per-pair 3x2 matrix keyed by `ALLOW` / `ESCALATE` rows and `xAI` / `OpenAI` / `MiniMax` columns.
- `pairs[].domain`: domain label for the pair.
- `pairs[].any_red`: true if any of the six solo dots failed.
- `pairs[].wrong_verdict_pair`: true if any dot failed by wrong verdict.
- `pairs[].parse_only_pair`: true if failures are parse/admissibility-only.
- `pairs[].all_three_collapse`: true if either sibling had all three solo attempts fail.
- Dot fields include `source_wave`, `model`, `verdict_class`, `failure_class`, `error_class`, `solo_verdict`, and `dot_color`.

## Claim Boundary

Internal stress-matrix discovery only. Not public benchmark evidence, not a global FPR/FNR claim, not natural production-rate evidence, and not Holo evidence.
