# HoloVerify 14-Pair Public Proof Summary

On a frozen 40-packet action-boundary benchmark, HoloVerify's 3-DNA governed architecture solved 40/40 packets. Matching one-shot solo baselines using the same mini-model families completed 120/120 calls but produced only 6/120 KNEW/admissible outputs. Fourteen sibling pairs showed complete solo collapse across all six one-shot solo attempts while Holo solved both the hard-ALLOW and hard-ESCALATE siblings. The Holo run used about 2.06x the solo token budget and passed no-leakage checks.

This summary is public-safe and conservative. It describes one frozen benchmark result, not a universal superiority claim.

## Clean Subset

- Clean all-six-solo-fail sibling pairs: 14
- Clean subset packets: 28
- Leakage status: PASS
- Holo trace hash: `dbb1d040c516af4989d488a07c44917a3582dc17da75c9fc517b4472228f1201`
- Solo trace hash: `5f98d96f82723979123a7eb13ed54900fe09f090cc1eaf7f40af2b073d724f94`

## Boundaries

- This does not claim Holo beats all models.
- This does not claim Holo is generally superior.
- This does not claim Holo solved safety.
- This does not claim solo models cannot solve similar packets universally.
- Internal Holo misses remain intra-Holo misses, not standalone solo failures.
