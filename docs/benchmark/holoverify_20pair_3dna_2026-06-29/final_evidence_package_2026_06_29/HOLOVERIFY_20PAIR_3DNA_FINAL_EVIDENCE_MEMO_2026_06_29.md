# HoloVerify 20-Pair / 3-DNA Final Evidence Memo

This memo freezes the completed HoloVerify full-architecture run and the matching one-shot solo baseline into a conservative comparative evidence package. No judges were run, no Holo reruns were performed, and no solo output was repaired.

## Locked Evidence

| Artifact | Value |
| --- | --- |
| Holo freeze root signature | `dcd9f17a76eef5bbe3b2a20195835a98b3694b511aa66d313fa4a91e7f2a17f1` |
| Holo trace hash | `dbb1d040c516af4989d488a07c44917a3582dc17da75c9fc517b4472228f1201` |
| Solo trace hash | `5f98d96f82723979123a7eb13ed54900fe09f090cc1eaf7f40af2b073d724f94` |
| Solo audit status | `PASS` |
| Readiness status | `PASS` |

## Solo Baseline

| Model | KNEW | Verdict Correct | Hard-ALLOW FP Failures | Hard-ESCALATE FN Failures | Admissibility Failures |
| --- | --- | --- | --- | --- | --- |
| `xai/grok-3-mini` | 4 | 5 | 20 | 16 | 36 |
| `google/gemini-2.5-flash-lite` | 0 | 5 | 20 | 20 | 40 |
| `minimax/MiniMax-M2.5-highspeed` | 2 | 10 | 19 | 19 | 38 |

## Holo Run

| Metric | Value |
| --- | --- |
| Holo correct count | 40 |
| Holo hard-ALLOW correct count | 20 |
| Holo hard-ESCALATE correct count | 20 |
| Target hard-ALLOW correct count | 10 |
| Target hard-ESCALATE correct count | 10 |
| Guardrail sibling correct count | 20 |
| Final selector fires | 1 |
| Intra-Holo single-DNA misses | 33 |
| Cross-DNA rescues | 18 |
| Gov rescues | 5 |
| Deterministic normalizations | 46 |
| Provider failures | 0 |
| Total tokens | 426002 |

## Comparative Takeaways

| Metric | Value |
| --- | --- |
| At least one solo failed, Holo correct | 40 |
| All three solos failed, Holo correct | 34 |
| Solo correct but Holo needed final selector | 0 |
| Holo corrected intra-Holo miss | 13 |
| Holo total tokens | 426002 |
| Solo total tokens | 206839 |
| Token delta | 219163 |
| Holo calls | 200 |
| Solo calls | 120 |
| Call delta | 80 |

## Strongest Public-Narrative Examples

- `BAL100-HB004-DEP-007-B`
- `HV-KITC-081-A`
- `HV-KITC-084-A`
- `BAL100-HB004-DEP-005-B`
- `BAL100-HB004-DEP-006-B`

## Weakest Or Ambiguous Packets Not To Overclaim

- `HV-KITC-042`
- `HV-KITC-082`
- `HV-KITC-084`
- `HV-KITC-086`
- `HV-KITC-089`
- `HV-KITC-090`
