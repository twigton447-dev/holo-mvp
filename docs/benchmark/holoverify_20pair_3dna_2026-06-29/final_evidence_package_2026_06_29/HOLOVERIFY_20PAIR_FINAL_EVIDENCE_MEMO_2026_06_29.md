# HoloVerify 20-Pair Final Evidence Memo

On a frozen 40-packet action-boundary benchmark, HoloVerify's 3-DNA governed architecture solved 40/40 packets. Matching one-shot solo baselines using the same mini-model families completed 120/120 calls but produced only 6/120 KNEW/admissible outputs. Fourteen sibling pairs showed complete solo collapse across all six one-shot solo attempts while Holo solved both the hard-ALLOW and hard-ESCALATE siblings. The Holo run used about 2.06x the solo token budget and passed no-leakage checks.

## Locked Result

| Measure | Value |
| --- | --- |
| Frozen packets | 40 |
| Valid sibling pairs | 20 |
| Holo solved/admissible packets | 40 |
| Solo one-shot calls completed | 120 |
| Solo KNEW/admissible outputs | 6 |
| Clean all-six-solo-fail pairs | 14 |
| Mixed pairs | 6 |
| Leakage scan prompt files | 240 |
| Forbidden leakage hits | 0 |
| Holo tokens | 426002 |
| Solo tokens | 206839 |
| Holo/Solo token ratio | 2.060x |
| No-provider local audit | `PASS` |
| Readiness assertions | `PASS` |

## Evidence Locks

| Artifact | Hash / Status |
| --- | --- |
| Holo freeze root signature | `dcd9f17a76eef5bbe3b2a20195835a98b3694b511aa66d313fa4a91e7f2a17f1` |
| Holo trace hash | `dbb1d040c516af4989d488a07c44917a3582dc17da75c9fc517b4472228f1201` |
| Solo trace hash | `5f98d96f82723979123a7eb13ed54900fe09f090cc1eaf7f40af2b073d724f94` |
| Autopsy lock | `730c31344a7d38ab2feb3c4d7c4b38127794c295d021f7c5b02c3f9e059b99b6` |
| Solo run-lock validation | `PASS` |

## Claim Boundaries

- Does not claim Holo beats all models.
- Does not claim Holo is generally superior.
- Does not claim Holo solved safety.
- Does not claim solo models cannot do this universally.
- Does not treat internal Holo misses as standalone solo failures.

## Evidence Separation

External solo failures are reported separately from intra-Holo misses. Internal Holo worker misses are architecture repair evidence, not standalone solo-baseline failures.
