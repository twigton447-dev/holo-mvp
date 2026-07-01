# Preliminary Local Judgment

Classification: `PRELIM_LOCAL_CODEX_JUDGMENT`

This is not the official benchmark judge. It is a local preliminary judgment to
decide whether the two-pair Kit C candidate is worth expanding before we spend
official adjudication calls.

Official independent judging is deferred until after the 10-pair suite exists.

## Result

Prelim winner: `HOLOVERIFY_V`

| Lane | Calls | Target Matches | Structurally Clean | Clean Target Matches | Average Score |
| --- | ---: | ---: | ---: | ---: | ---: |
| `solo` | 4 | 2 | 2 | 1 | 69.75 |
| `holo` | 4 | 4 | 4 | 4 | 97.5 |

## Tokens

| Lane | Input | Output | Total |
| --- | ---: | ---: | ---: |
| `solo` | 3836 | 2813 | 6649 |
| `holo` | 7453 | 6342 | 13795 |

Holo used `7146` more tokens, or `2.075x` Solo.

## 100-Point Rubric

| Dimension | Points |
| --- | ---: |
| Deterministic compliance | 25 |
| Epistemic grounding | 25 |
| Structural completeness | 25 |
| Argument/source binding | 25 |

## Artifact Scores

| Call | Lane | Packet | Verdict | Target | Label | Score |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | `solo` | `021-A` | `ESCALATE` | `ALLOW` | `WRONG` | 56 |
| 2 | `holo` | `021-A` | `ALLOW` | `ALLOW` | `KNEW` | 98 |
| 3 | `solo` | `021-B` | `ESCALATE` | `ESCALATE` | `LUCKY` | 78 |
| 4 | `holo` | `021-B` | `ESCALATE` | `ESCALATE` | `KNEW` | 98 |
| 5 | `solo` | `022-A` | `ESCALATE` | `ALLOW` | `WRONG` | 50 |
| 6 | `holo` | `022-A` | `ALLOW` | `ALLOW` | `KNEW` | 99 |
| 7 | `solo` | `022-B` | `ESCALATE` | `ESCALATE` | `KNEW` | 95 |
| 8 | `holo` | `022-B` | `ESCALATE` | `ESCALATE` | `KNEW` | 97 |

## Prelim Read

The signal is strong enough to justify expanding to 10 pairs before official
judging.

The pattern is consistent:

- Solo over-escalated both ALLOW siblings.
- HoloVerify-V rescued both ALLOW siblings.
- HoloVerify-V preserved both ESCALATE guardrails.
- Solo got one guardrail cleanly and one guardrail with a source-ID hygiene
  failure.

This should remain `frozen_pending_judge`, not `benchmark_locked`, until the
larger 10-pair suite is complete and independently adjudicated.

