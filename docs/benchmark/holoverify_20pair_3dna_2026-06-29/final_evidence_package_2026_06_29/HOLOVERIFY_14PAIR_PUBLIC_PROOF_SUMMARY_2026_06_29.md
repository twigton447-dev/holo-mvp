# HoloVerify 14-Pair Public Proof Summary

Fourteen sibling pairs form the clean solo-collapse subset: every one of the six one-shot solo attempts in each pair failed, while HoloVerify solved both the hard-ALLOW and hard-ESCALATE siblings.

## Public-Safe Claim

On a frozen 40-packet action-boundary benchmark, HoloVerify's 3-DNA governed architecture solved 40/40 packets. Matching one-shot solo baselines using the same mini-model families completed 120/120 calls but produced only 6/120 KNEW/admissible outputs. Fourteen sibling pairs showed complete solo collapse across all six one-shot solo attempts while Holo solved both the hard-ALLOW and hard-ESCALATE siblings. The Holo run used about 2.06x the solo token budget and passed no-leakage checks.

## Clean Subset

| Measure | Value |
| --- | --- |
| Clean pairs | 14 |
| Clean packets | 28 |
| Solo calls in clean subset | 84 |
| Holo tokens, full 20-pair run | 426002 |
| Solo tokens, full 20-pair run | 206839 |
| Token ratio, full 20-pair run | 2.060x |
| Leakage status | `PASS` |

## Pair IDs

- `BAL100-BEC-HARDEN-025-H03`
- `BAL100-BEC-HARDEN-025-H06`
- `BAL100-BEC-SUBTLE-CLOSEOUT-022`
- `BAL100-HB004-DEP-001`
- `BAL100-HB004-DEP-002`
- `BAL100-HB004-DEP-003`
- `BAL100-HB004-DEP-004`
- `BAL100-HB004-DEP-005`
- `BAL100-HB004-DEP-006`
- `BAL100-HB004-DEP-007`
- `HV-KITC-077`
- `HV-KITC-078`
- `HV-KITC-081`
- `HV-KITC-087`

## Claim Boundaries

- Does not claim Holo beats all models.
- Does not claim Holo is generally superior.
- Does not claim Holo solved safety.
- Does not claim solo models cannot do this universally.
- Does not treat internal Holo misses as standalone solo failures.
