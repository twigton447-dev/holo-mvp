# HoloVerify 20-Pair Public Proof Summary

HoloVerify completed a 20-pair, 40-packet action-boundary benchmark using 3 worker model DNA plus Gov adjudication. The full architecture correctly handled 10 hard-ALLOW and 10 hard-ESCALATE pairs. Matching one-shot solo baselines were then run on the same frozen packets to measure individual model misses separately from intra-Holo turn misses.

## Conservative Evidence

| Measure | Value |
| --- | --- |
| Frozen packets | 40 |
| Sibling pairs | 20 |
| Holo provider calls | 200 |
| Solo provider calls | 120 |
| Holo correct/admissible packets | 40 |
| Solo KNEW/admissible calls | 6 |
| All-three-solo-miss packets where Holo was correct | 34 |
| Prompt leakage hits | 0 |
| Judges run | 0 |

## Claim Boundaries

- This does not claim Holo is smarter than every model.
- This does not claim Holo always beats solo.
- This does not claim general superiority beyond this frozen packet family.
- This does not claim deterministic normalization corrected model reasoning.
- This does not treat internal Holo misses as standalone solo failures.
