# HoloVerify Solo Failure Factory Holo Rescue Shortlist

Status: `NO_PROVIDER_SHORTLIST`

Created: `2026-07-03`

Source evidence: Batch001-Batch004 live rollups and post-hoc scoring summaries only.

Provider calls: `0`
Holo calls: `0`
Gov calls: `0`
Judge calls: `0`
Public claims: `0`

## Decision

Pause live Batch005 execution. Batch005 is already frozen, but Batch004 raised the factory to 29 solo-failure pair candidates and produced the strongest yield so far: 6 useful pairs out of 10. The next best move is to select a Holo rescue set from Batch001-Batch004 before spending more provider calls on new solo discovery.

## Selection Rule

Primary evidence should be wrong-verdict failures, not answer-contract brittleness.

- Prefer false positives and false negatives over parse/admissibility failures.
- Include both hard-ALLOW and hard-ESCALATE siblings in any future Holo rescue run.
- Prefer repeated domains: refund/balance, IT change/window, banking/high-risk relationship.
- Keep parse/admissibility-only pairs in a separate contract-brittleness holdout.
- Avoid promoting heavy non-KNEW-only behavior as rescue evidence.

## Primary Holo Rescue Shortlist

These are the cleanest Batch001-Batch004 wrong-verdict candidates in repeated seams.

| Priority | Pair | Domain | Solo failure signal | Why promote |
| --- | --- | --- | --- | --- |
| P1 | `HVSF-FACTORY-010` | IT change management | OpenAI false positive on A and false negative on B | Best two-sided pair: Holo must handle both siblings, so it cannot win by simple escalation bias. |
| P1 | `HVSF-FACTORY4-008` | Banking / high-risk relationship controls | OpenAI false negative on B | Strong hard-ESCALATE failure in a repeated high-risk authority seam. |
| P1 | `HVSF-FACTORY4-010` | Banking / high-risk relationship controls | OpenAI false negative on B | Reinforces high-risk stale-authority failure class from a separate pair. |
| P1 | `HVSF-FACTORY3-008` | Banking / high-risk relationship controls | OpenAI false negative on B; xAI admissibility failure on A | Strong high-risk pair with both verdict and contract brittleness. |
| P1 | `HVSF-FACTORY2-005` | Customer operations / refund exception controls | OpenAI false negative on B | Strong refund/balance ESCALATE miss. |
| P1 | `HVSF-FACTORY4-004` | Customer operations / refund controls | OpenAI false positive on A | Strong clean refund over-escalation seam. |
| P1 | `HVSF-FACTORY3-004` | Customer operations / refund controls | OpenAI false positive on A | Repeats clean refund over-escalation from a different packet. |
| P1 | `HVSF-FACTORY-009` | Customer operations / refunds | OpenAI false positive on A; xAI admissibility failure on B | Good refund pair with both precision failure and answer-contract brittleness. |
| P1 | `HVSF-FACTORY4-007` | IT change management | OpenAI false positive on A | Repeated IT change/window clean-side overblock. |
| P1 | `HVSF-FACTORY3-007` | IT change management | OpenAI false positive on A | Another clean-side IT overblock. |
| P1 | `HVSF-FACTORY2-006` | IT change management | OpenAI false positive on A | Earlier IT clean-side overblock, useful for seam repetition. |
| P1 | `HVSF-FACTORY3-006` | IT change management | OpenAI false positive on A; MiniMax admissibility failure on A | Useful because a second model also shows contract brittleness on the same sibling. |
| P1 | `HVSF-FACTORY-001` | Banking / KYC / AML controls | OpenAI false negative on B | Broader banking high-risk cousin seam. |

## Secondary Wrong-Verdict Shortlist

These are still wrong-verdict failures, but agentic commerce was less repeatable after Batch004, so they should be lower priority than refund, IT change, and banking.

| Priority | Pair | Domain | Solo failure signal | Why hold as secondary |
| --- | --- | --- | --- | --- |
| P2 | `HVSF-FACTORY-004` | Agentic commerce / order execution controls | OpenAI false negative on B | Useful, but the later generic agentic-commerce variants did not keep firing. |
| P2 | `HVSF-FACTORY2-003` | Agentic commerce / order execution controls | OpenAI false negative on B | Useful, but should be sharpened or paired with a clearer authorization-boundary variant. |

## Contract-Brittleness Holdout

These should not be in the first rescue proof unless we explicitly label the run as answer-contract resilience. They are useful, but they answer a different question than false-positive/false-negative rescue.

| Priority | Pair | Domain | Solo failure signal | Recommendation |
| --- | --- | --- | --- | --- |
| Hold | `HVSF-FACTORY2-004` | Agentic commerce / subscription controls | xAI parse/admissibility failure on B; verdict direction was correct | Hold for contract-brittleness lane. |
| Hold | `HVSF-FACTORY4-003` | Customer operations / refund controls | xAI and MiniMax parse/admissibility failures; verdict directions were correct | Hold unless testing Holo's ability to turn brittle outputs into admissible artifacts. |
| Hold | `HVSF-FACTORY4-009` | IT access / temporary privilege controls | MiniMax parse/admissibility failure on A; verdict direction was correct | Hold for answer-contract brittleness, not verdict rescue. |

## Recommended Next Run Shape

Start with a no-provider Holo rescue registration using the P1 list only, or a smaller representative slice:

- Refund/balance: `HVSF-FACTORY2-005`, `HVSF-FACTORY3-004`, `HVSF-FACTORY4-004`, `HVSF-FACTORY-009`
- IT change/window: `HVSF-FACTORY-010`, `HVSF-FACTORY2-006`, `HVSF-FACTORY3-006`, `HVSF-FACTORY3-007`, `HVSF-FACTORY4-007`
- Banking/high-risk: `HVSF-FACTORY-001`, `HVSF-FACTORY3-008`, `HVSF-FACTORY4-008`, `HVSF-FACTORY4-010`

For every selected pair, include both siblings. Success should require Holo to get both siblings correct and admissible after trace freeze, with no scoring map before live execution.

## Short Answer

Yes, pause Batch005 live execution. Build the Holo rescue shortlist first.

Include parse/admissibility-only pairs only in a separate contract-brittleness lane. Do not mix them into the first verdict-rescue proof.
