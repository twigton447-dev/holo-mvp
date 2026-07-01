# HoloVerify 20-Pair Whitepaper Insert Draft

Source: `87b39f2 benchmark: freeze holoverify 20pair 3dna solo comparison`

Underlying frozen evidence source: `93118d7 benchmark: freeze holoverify 20pair 3dna and solo baseline`

Canonical public package lock root:

`5ffe3c41e5cf35324f9bb0518c24df118aad0eea15900abbb1d9996df1756695`

## Suggested Insert

HoloVerify was evaluated on a frozen 40-packet action-boundary benchmark built from 20 sibling pairs. Each pair contained a hard-ALLOW sibling and a hard-ESCALATE sibling, requiring the system to distinguish when an irreversible or operationally sensitive action was actually authorized by current source evidence versus when a narrow missing dependency still required escalation.

The result should not be framed as model superiority. The benchmark is about architecture at the action boundary: whether a governed verification loop can preserve source constraints, expose narrow authority gaps, and prevent a fluent model response from becoming an unsafe approval.

In the locked run, HoloVerify's 3-DNA governed architecture solved 40/40 packets and 20/20 sibling pairs. The matching one-shot solo baseline used the same mini-model families on the same frozen packet bank and completed 120/120 calls. Those solo one-shots produced only 6/120 KNEW/admissible outputs. Fourteen sibling pairs showed complete one-shot solo collapse across all six solo attempts while HoloVerify solved both siblings.

The architecture paid for that reliability. The Holo run used 426,002 total tokens compared with 206,839 total tokens for the solo baseline, or about 2.06x the solo token budget. That cost delta is part of the evidence, not a footnote: HoloVerify spends more tokens to run adversarial checkpointing, Gov adjudication, deterministic gates, artifact preservation, and final selection.

This matters most for irreversible approvals. In ordinary drafting tasks, a single model may often produce a useful answer. At an action boundary, the risk is different: the system must decide whether current source evidence closes the exact approval chain. A plausible answer is not enough. HoloVerify is designed to make the approval path auditable by separating worker generation, Gov control actions, deterministic admissibility checks, artifact preservation, and final selection.

## Why The Architecture Matters

- Same packet bank: Holo and the solo baselines were evaluated against the same 40 frozen packets.
- Same mini-model families: the solo baselines used the same mini-model families that appeared inside the HoloVerify architecture.
- Adversarial checkpointing: Holo workers were routed through Gov instructions and challenged to preserve, repair, block, or resolve specific boundary issues.
- Deterministic enforcement: local gates checked verdict structure, required source IDs, invented source IDs, timing/scope/dependency requirements, and admissibility conditions.
- Governance separation: worker misses inside Holo remained visible as intra-Holo events and were not counted as external solo failures.
- Cost transparency: the governed architecture used about 2.06x the solo token budget.
- Public auditability: `87b39f2` adds a public package lock over the 14-pair subset, public memo, no-provider audit, and public proof summary.

## Limitations

- This is an internal benchmark result until externally reviewed.
- The baseline is a mini-model one-shot baseline, not every possible solo configuration, prompt strategy, tool setup, memory strategy, or retry policy.
- The packets are action-boundary packets; the result should not be generalized to all domains without additional frozen benchmark families.
- The result does not prove universal model superiority.
- The result does not prove that solo models cannot solve these classes under stronger scaffolding.
- Internal Holo misses must remain separate from external solo failures. Inside-Holo misses show the value of governance correction; they are not standalone solo model claims.
- Public registry publication requires final review before release.

## Suggested Whitepaper Framing

The strongest framing is:

> HoloVerify is not a claim that one model is better than another. It is a claim that high-stakes action boundaries need governed architecture: multiple model DNA, adversarial checkpointing, deterministic enforcement, artifact preservation, and auditable final selection. In the 20-pair internal benchmark, that architecture solved every frozen packet while same-family one-shot solo baselines collapsed on most attempts, at roughly twice the token cost.

Avoid stronger language such as:

- "Holo beats all models."
- "Holo is generally superior."
- "Holo solved safety."
- "Solo models cannot do this."
- "Every internal Holo miss is a solo failure."
