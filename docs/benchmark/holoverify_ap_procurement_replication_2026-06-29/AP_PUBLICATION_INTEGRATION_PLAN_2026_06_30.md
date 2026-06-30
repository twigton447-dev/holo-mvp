# AP Publication Integration Plan

Date: 2026-06-30

Source evidence commit: `78164d47`

Evidence root:

`docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/final_evidence_package`

## Bottom Line

AP should be added as a second frozen HoloVerify replication family, not as a new "solo-collapse" headline.

The clean public story is:

> HoloVerify now has a second committed 20-pair / 40-packet action-boundary family in AP / procurement / vendor-master controls. Holo solved 40/40 packets and 20/20 sibling pairs. Matching one-shot solo baselines using the same three mini-model families completed 120/120 calls and produced 53/120 KNEW/admissible outputs. Every AP pair had at least two strict solo failures across six one-shot attempts, while Holo solved both siblings. One AP pair showed complete all-six solo collapse. The Holo run used about 2.84x the solo token budget and passed packet-identity and no-leakage audits.

## What AP Adds

AP is valuable because it is not the same evidence shape as Kit C.

- Kit C is the strong public-collapse family: 14 clean all-six-solo-fail pairs.
- AP is the replication family: Holo still went 40/40, but solo performance was mixed rather than uniformly collapsed.
- That makes AP useful for credibility because it shows Holo is not only winning on hand-picked total-collapse seams.
- AP also shows that even when solo models sometimes get the verdict, one-shot solo reliability is unstable under strict KNEW/admissibility standards.

## AP Facts To Use

| Measure | Value |
| --- | --- |
| Family name | Vendor-Master Payment Controls |
| Source commit | `78164d47` |
| Freeze root | `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7` |
| Holo packets correct | `40/40` |
| Holo valid pairs | `20/20` |
| Solo calls | `120/120` |
| Solo KNEW/admissible | `53/120` |
| Strict solo failures | `67/120` |
| All-six-solo-fail pairs | `1` |
| Mixed pairs | `19` |
| Holo tokens | `414,016` |
| Solo tokens | `146,061` |
| Token ratio | `2.835x` |
| Packet identity | `PASS` |
| No leakage | `PASS` |
| Judges | `0` |
| Holo provider failures | `0` |

## Strongest AP Claim

Use:

> In the AP replication family, every sibling pair had at least two strict one-shot solo failures across the six same-family solo attempts, while Holo solved both siblings in all 20 pairs.

Why this is strong:

- It does not require every solo to fail.
- It does not overstate parse or admissibility failures as wrong verdicts.
- It demonstrates instability at the action boundary.
- It preserves the KNEW standard: right verdict alone is not enough if the reasoning or structure is not admissible.

## Claim Boundaries

Do not say:

- "AP proves Holo always beats solo."
- "AP produced 14 clean solo-collapse pairs."
- "All AP solos failed."
- "Every solo failure was a wrong verdict."
- "Parse failures are the same as wrong business reasoning."
- "AP was externally judged."

Do say:

- "AP is an internal frozen replication family."
- "The baseline was one-shot solo, not every possible solo scaffold."
- "Strict solo failures include verdict failures, parse failures, and structural/admissibility failures."
- "Holo used more tokens: about 2.84x solo."
- "AP passed packet identity and no-leakage audits."
- "AP should be treated separately from Kit C because the solo-failure distribution differs."

## Whitepaper Placement

Add AP inside `docs/whitepaper.md`, Section 09, after the current Kit A / Kit B discussion and before HoloBuild.

Suggested subsection title:

`### Replication Family: Vendor-Master Payment Controls`

Suggested insert:

> We then ran a larger AP / procurement replication family using 20 sibling pairs and 40 frozen packets. Each pair contained an ALLOW sibling and an ESCALATE sibling, testing whether the system could distinguish valid payment authority from unresolved vendor-master, approval, callback, duplicate-payment, or emergency-exception risk.
>
> HoloVerify solved 40/40 packets and 20/20 sibling pairs. Matching one-shot solo baselines using the same three mini-model families completed 120/120 calls and produced 53/120 KNEW/admissible outputs.
>
> This result should not be described as total solo collapse. It is more useful than that. AP showed mixed solo behavior: in every pair, at least two of six solo attempts failed the strict KNEW/admissibility standard, while Holo solved both siblings. One pair showed complete six-of-six solo collapse.
>
> The cost was higher than Kit C. Holo used 414,016 tokens versus 146,061 for the solo one-shot baseline, or about 2.84x the solo budget. That cost delta is part of the finding: governed verification buys reliability by spending more work at the action boundary.

## Benchmark Page Placement

Add AP to the public benchmark/registry as a separate row under replication families.

Recommended table:

| Family | Domain | Packets | Pairs | Holo | Solo baseline | Clean collapse pairs | Token ratio | Status |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | --- |
| Clinical Activation Boundary Controls | clinical-regulated activation controls | 40 | 20 | 40/40 | 6/120 KNEW/admissible | 14 | 2.06x | committed public package |
| Vendor-Master Payment Controls | AP / procurement / vendor-master controls | 40 | 20 | 40/40 | 53/120 KNEW/admissible | 1 | 2.84x | committed evidence package |

## Cumulative Claim Shape

Safe cumulative sentence:

> Across two committed internal HoloVerify families, Holo solved 80/80 frozen action-boundary packets and 40/40 sibling pairs. The two families had different solo-baseline behavior: Kit C produced broad clean solo collapse, while AP produced mixed solo behavior with strict failures present in every pair.

Avoid:

> Holo is 80/80, therefore it is generally superior.

## Next Publication Tasks

1. Create an AP public-safe benchmark update draft from `78164d47`.
2. Create an AP whitepaper insert draft from `78164d47`.
3. Update the cumulative benchmark table to include Kit C and AP separately.
4. Update the whitepaper economics section to show token ratios vary by family: Kit C about `2.06x`, AP about `2.84x`.
5. Keep AP labeled internal/committed until final public registry review.
6. Do not merge AP with Commerce until Commerce has a valid full-family Holo freeze and matching solo baseline.
