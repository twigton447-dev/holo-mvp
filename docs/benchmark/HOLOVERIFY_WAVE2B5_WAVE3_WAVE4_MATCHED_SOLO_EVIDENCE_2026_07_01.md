# HoloVerify Matched Solo Evidence: Wave2 Batch005 + Wave3/Wave4

Classification: `HOLOVERIFY_WAVE2B5_WAVE3_WAVE4_MATCHED_SOLO_EVIDENCE`
Root signature: `6f867de79e861c574a0a22da4bd08ee835c6dd24632fe825eddde27c65f9c4a2`

This package extracts matched solo-control rows from already completed solo traces.
It does not run providers, does not run Holo, and does not run judges.

## Summary

- Holo packets: `100` / `100` correct.
- Holo pairs: `50` / `50` valid.
- Matched solo calls: `300` across the same `100` packets.
- Holo provider calls represented: `500`.
- Judges: `0`.
- Holo tokens: `1150896` total.
- Matched solo tokens: `363620` total.
- Holo/solo token ratio: `3.165106`.
- Intermediate Holo single-DNA misses corrected or absorbed by the architecture: `18`.

## Solo Outcome Counts

| Label | Count |
| --- | ---: |
| `KNEW` | 116 |
| `PARSE_FAIL` | 40 |
| `STRUCTURAL_OR_EVIDENCE_FAIL` | 131 |
| `WRONG_VERDICT` | 13 |

## Pair Classes

| Class | Pairs |
| --- | ---: |
| `ALL_SIX_SOLO_COLLAPSE` | 1 |
| `MIXED_SEAM` | 16 |
| `STRONG_SOLO_COLLAPSE` | 33 |

## Model Totals

| Model | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Structural/Evidence Fail | Verdict Correct | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `minimax/MiniMax-M2.5-highspeed` | 100 | 26 | 74 | 0 | 40 | 34 | 60 | 167003 |
| `openai/gpt-5.4-mini` | 100 | 82 | 18 | 0 | 0 | 18 | 100 | 64438 |
| `xai/grok-3-mini` | 100 | 8 | 92 | 13 | 0 | 79 | 87 | 132179 |

## Scope Totals

| Scope | Packets | Pairs | Holo Calls | Solo Calls | Holo Correct | Holo Valid Pairs | All-Six Collapse | Strong Collapse | Mixed | No Seam |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `WAVE2_BATCH005` | 46 | 23 | 230 | 138 | 46 | 23 | 1 | 6 | 16 | 0 |
| `WAVE3_BATCH001` | 24 | 12 | 120 | 72 | 24 | 12 | 0 | 12 | 0 | 0 |
| `WAVE4_BATCH001` | 30 | 15 | 150 | 90 | 30 | 15 | 0 | 15 | 0 | 0 |

## Conservative Claim Boundary

This proves matched-control evidence for these 100 already Holo-passed packets only.
It does not claim universal model superiority, and it keeps external solo misses separate from intermediate Holo worker misses.

## Assertions

| Assertion | Status |
| --- | --- |
| `matched_packets` | `PASS` |
| `matched_pairs` | `PASS` |
| `matched_solo_calls` | `PASS` |
| `holo_calls` | `PASS` |
| `holo_packets_correct` | `PASS` |
| `holo_pairs_valid` | `PASS` |
| `no_judges` | `PASS` |
| `no_new_provider_calls_by_compiler` | `PASS` |
| `external_solo_and_intra_holo_evidence_separated` | `PASS` |
