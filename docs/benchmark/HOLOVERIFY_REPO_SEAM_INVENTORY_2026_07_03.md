# HoloVerify Repo Seam Inventory

Date: 2026-07-03

Status: NO_PROVIDER_INVENTORY

This file computes the current seam reservoir from repo-backed evidence. It separates clean evidence from discovery evidence and design-only ideas.

## Plain English

We do have seams. The cleanest current starting point is 11 blind-120 sibling pairs where at least one solo one-shot failed and HoloVerify won on the same frozen blind bank. But those 11 are all ALLOW-side failures, so they mostly prove overblocking / false escalation. To get to a strong 50-pair benchmark, the next work should mine ESCALATE-side false-ALLOW failures and re-freeze the older seam reservoirs under the modern blind firewall.

## Counts

| Tier | Evidence class | Count | Can count in clean benchmark now? |
|---|---|---:|---|
| 1 | Blind-120 verified solo-failure + Holo-win pairs | 11 | Yes, as starter registry |
| 2 | Atlas same-six Holo rescue pairs | 6 | Not as fresh benchmark evidence; patch-validation/directional only |
| 3 | Atlas strict wrong-verdict scout pairs, raw | 11 | No, discovery only until re-frozen |
| 3 | Atlas strict wrong-verdict pairs usable/promoted after exclusions | 9 | No, discovery only until re-frozen |
| 3 | Atlas heavy non-KNEW only pairs | 10 | No |
| 4 | KitC/BAL100 balanced wrong-verdict candidates | 20 | No, but high-priority reservoir |
| 5 | Fable design-level candidates | 55 | No, designs only |

## Clean Starter Registry

- 11 verified pair-level seams from blind-120.
- 8 pairs have 1 of 6 solo failures.
- 3 pairs have 2 of 6 solo failures.
- 0 pairs have 3+ of 6 solo failures.
- 11/11 current failures are on ALLOW-truth siblings.

Source: `docs/benchmark/HOLOVERIFY_SOLO_COLLAPSE_HOLO_WIN_PAIR_REGISTRY_2026_07_03.json`.

## Best Near-Term Reservoirs

1. KitC/BAL100 balanced candidate file: 20 wrong-verdict seam candidates, including 10 selected hard-ALLOW and 10 selected hard-ESCALATE candidates. This is likely the fastest path to more balanced pairs, but it must be rebuilt or re-frozen under the modern blind/firewall protocol before it becomes clean evidence.
2. Atlas additional strict wrong-verdict scouts not already promoted: 001, 022, and 024. These are small and likely easier to clean up next.
3. Fable Batch2 exact bank: 20 designs, split 10 non-human-alarm false positives and 10 unit/coordinate/arithmetic false negatives. The exact first scout was preflighted but not run.
4. Fable V5 bank: 15 designs, especially computed FN frontier pairs such as percentage-of-sum, business-day counting, toxic role combination, rolling windows, composite conversion, and depletion across documents.

## Falsified Or Weakened Hypotheses
- printed_one_join_unit_blindness_FN: FALSIFIED_FOR_V4_SCOPE — V4 review says planted one-join unit gaps were caught by all three minis.
- blanket_verification_affordance_overblocking: FALSIFIED_AS_STRONG_CLASS — Documented FX and printed tolerance cured the strong version; surviving class is graded, model-idiosyncratic clean-side false escalation.
- literal_phrase_pressure_FP_004_A: WEAK_OR_STRING_REFLEX — Paraphrase test 011 produced zero wrong verdicts; original 004-A should not be treated as broad seam proof.
- HV_ATLAS_DISC_034_original: RETIRED_REPLACED_BY_036 — Original 034 had an unfair duplicate-looking value; fixed 036 is the replacement.

## Recommended Path To 50
1. Use the 11 clean blind-120 pair registry as slots 1-11, with the caveat that all are ALLOW-side failures.
2. If internal directional evidence is acceptable, keep the six Atlas rescue pairs as a separate sidebar, not merged into the clean blind-120 denominator.
3. Use the three additional Atlas strict wrong pairs not yet promoted (001, 022, 024) as near-term candidates after a modern blind refreeze/retest.
4. Use the KitC/BAL100 balanced 20 wrong-verdict candidate reservoir as the fastest path to more pairs, especially ESCALATE-side failures, but only after modern blind/firewall cleanup.
5. Use Fable Batch2 and V5 designs to generate new scouts when we run out of verified solo failures. Prioritize ESCALATE-truth false-ALLOW seams to balance the currently ALLOW-heavy registry.

No providers, Holo calls, solo calls, Gov calls, judges, or scoring changes were run to create this inventory.
