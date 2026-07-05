# HoloVerify Wave3/Wave4 Final Evidence Memo

Classification: `HOLOVERIFY_WAVE3_WAVE4_FINAL_EVIDENCE_MEMO`
Root signature: `0472a5e605dab76426fef2a68a83914c631dae9886942ba2c18b384228fa2ca1`
Source matched-control root: `6f867de79e861c574a0a22da4bd08ee835c6dd24632fe825eddde27c65f9c4a2`

This is an internal evidence-completion memo for Wave3 and Wave4 only.
It does not make a public claim and it does not run providers or judges.

## Result

- Holo packets: `54` / `54` correct.
- Holo pairs: `27` / `27` valid.
- Matched solo calls: `162` over the same `54` packets.
- Holo provider calls represented: `270`.
- Holo worker/Gov calls: `162` / `108`.
- Judges: `0`.
- Holo tokens: `621863`.
- Matched solo tokens: `200436`.
- Holo/solo token ratio: `3.102551`.
- Intermediate Holo single-DNA misses corrected or absorbed: `16`.

## Solo Outcome Counts

| Label | Count |
| --- | ---: |
| `KNEW` | 54 |
| `PARSE_FAIL` | 25 |
| `STRUCTURAL_OR_EVIDENCE_FAIL` | 74 |
| `WRONG_VERDICT` | 9 |

## Pair Classes

| Class | Pairs |
| --- | ---: |
| `STRONG_SOLO_COLLAPSE` | 27 |

## Model Totals

| Model | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Structural/Evidence Fail | Verdict Correct | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `minimax/MiniMax-M2.5-highspeed` | 54 | 3 | 51 | 0 | 25 | 26 | 29 | 90971 |
| `openai/gpt-5.4-mini` | 54 | 51 | 3 | 0 | 0 | 3 | 54 | 35420 |
| `xai/grok-3-mini` | 54 | 0 | 54 | 9 | 0 | 45 | 45 | 74045 |

## Scope Totals

| Scope | Packets | Pairs | Holo Correct | Holo Valid Pairs | Solo Calls | Strong Collapse Pairs | Tokens Holo/Solo |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `WAVE3_BATCH001` | 24 | 12 | 24 | 12 | 72 | 12 | 278439 / 88981 |
| `WAVE4_BATCH001` | 30 | 15 | 30 | 15 | 90 | 15 | 343424 / 111455 |

## Boundary

Use this memo to finish Wave3/Wave4 internally before drafting public copy.
Do not merge it into public language as a universal superiority claim.
External solo misses and intermediate Holo worker misses remain separate evidence categories.

## Assertions

| Assertion | Status |
| --- | --- |
| `wave3_scope_present` | `PASS` |
| `wave4_scope_present` | `PASS` |
| `packet_count_54` | `PASS` |
| `pair_count_27` | `PASS` |
| `holo_54_of_54_correct` | `PASS` |
| `holo_27_of_27_pairs_valid` | `PASS` |
| `matched_solo_162_calls` | `PASS` |
| `all_pairs_strong_solo_collapse` | `PASS` |
| `no_judges` | `PASS` |
| `no_new_provider_calls` | `PASS` |
| `external_solo_and_intra_holo_evidence_separated` | `PASS` |
