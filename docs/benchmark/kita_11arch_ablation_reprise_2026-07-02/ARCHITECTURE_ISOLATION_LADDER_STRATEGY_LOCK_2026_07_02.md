# Architecture Isolation Ladder Strategy Lock

Status: `LOCKED_STRATEGY_NO_PROVIDER`

Created: `2026-07-02`

No providers, Holo runs, solo runs, judges, packet edits, or prompt edits are authorized by this document.

## Moral Center

HoloVerify's result is strong; the ablations are there to test what actually caused it.

## Statistical Language

Use this exact framing for the headline result:

> On this frozen 614-packet corpus, HoloVerify observed 0 false positives and 0 false negatives. The one-sided 95% upper confidence bound is approximately 0.97% per side.

Do not shorten this to "zero errors" without the frozen-corpus scope and confidence bound.

## Experiment Frame

The page section should be called:

**Architecture Isolation Ladder**

The ladder is:

1. Solo one-shot
2. No-Gov reconsider
3. No-Gov vote
4. No-Gov council
5. No-Gov debate
6. Full HoloVerify

The logic is progressive isolation:

- Solo one-shot tests whether the same model families can solve the packet alone.
- No-Gov multi-call architectures test whether more turns and more model interaction alone solve the packet.
- Full HoloVerify tests the governed stack: Gov, deterministic gates, state enforcement, artifact preservation, best-artifact preservation, monotonic preservation, final selector, and trace-grade accounting.

## Decision Criterion

The 12-packet ablation packet set will support an architecture-causation claim if the following pattern appears:

1. Full HoloVerify is strict-admissible correct on `12/12` packets.
2. Solo one-shot is not perfect on the same `12` packets across the same three model families.
3. No-Gov multi-call architectures remain materially below Full HoloVerify despite comparable call budgets.
4. The no-Gov failures include enforcement-relevant failure modes, not merely harmless wording differences.

Use these thresholds:

- `STRONG_ARCHITECTURE_SIGNAL`
  - Full HoloVerify: `12/12` strict-admissible correct.
  - No-Gov aggregate: `<= 40/48` strict-admissible correct, meaning at least `8` strict failures across the four no-Gov architecture columns.
  - Solo one-shot aggregate: `<= 30/36` KNEW/admissible correct, or at least `4/12` packets have one or more solo miss/fail outcomes.
  - Failures are not concentrated in only one packet or one model.

- `MODERATE_ARCHITECTURE_SIGNAL`
  - Full HoloVerify: `12/12` strict-admissible correct.
  - No-Gov aggregate: `41/48` to `45/48` strict-admissible correct.
  - Solo one-shot shows at least one miss/fail, or no-Gov failures appear across multiple architectures.
  - Claim must be phrased as directional evidence, not proof.

- `INCONCLUSIVE`
  - Full HoloVerify: `12/12`, but no-Gov aggregate is `46/48` or better and solo one-shot is `34/36` or better.
  - Or failures are concentrated in one ambiguous packet.
  - Do not claim architecture causation; report that the sample was too easy or too small.

- `AGAINST_ARCHITECTURE_CLAIM`
  - Full HoloVerify is not `12/12` on the same packets.
  - Or no-Gov and solo both match Full HoloVerify cleanly.
  - Preserve the result and say the ablation did not support the mechanism claim.

## Failure Modes That Count

Count these as meaningful failures:

- wrong final verdict
- false positive on an ALLOW packet
- false negative on an ESCALATE packet
- missing required source IDs
- invented source IDs
- unsupported binding rationale
- action-boundary mismatch
- parse/content failure
- malformed/unusable output
- correct verdict but not strict-admissible

Do not count harmless phrasing differences as failures.

## One-Glance Artifact

Use one artifact as the centerpiece:

**Architecture Isolation Ladder Matrix**

Rows: the `12` exact packets.

Columns:

1. `packet_id`
2. `truth`
3. `domain`
4. `solo_one_shot_3model_result`
5. `no_gov_reconsider`
6. `no_gov_vote`
7. `no_gov_council`
8. `no_gov_debate`
9. `full_holoverify`
10. `dominant_failure_mode`
11. `architecture_interpretation`

Cell vocabulary:

- `STRICT_PASS`
- `CORRECT_NOT_ADMISSIBLE`
- `WRONG_VERDICT`
- `EVIDENCE_FAIL`
- `PARSE_FAIL`
- `NOT_RUN`

The bottom of the matrix must include one aggregate row:

- Solo one-shot: `KNEW/admissible correct / 36`
- No-Gov reconsider: `strict correct / 12`
- No-Gov vote: `strict correct / 12`
- No-Gov council: `strict correct / 12`
- No-Gov debate: `strict correct / 12`
- No-Gov aggregate: `strict correct / 48`
- Full HoloVerify: `strict correct / 12`

## Whitepaper Claim Shape

If the strong pattern appears, use this claim:

> On the 12-packet Architecture Isolation Ladder sample, the same model families were tested as solo one-shots and as multi-call no-Gov architectures before comparison to Full HoloVerify. The governed stack remained strict-admissible on the same packets, while no-Gov architectures showed material closure failures. This supports the interpretation that HoloVerify's result is architectural, not merely a function of model choice or additional turns.

If only the moderate pattern appears:

> On this 12-packet sample, the direction of evidence favored governed architecture over no-Gov multi-call coordination, but the sample is too small to treat the result as a general statistical proof.

If inconclusive or against:

> This ablation sample did not establish architecture causation. The result is preserved as a boundary condition and used to refine the next packet sample.

## Publication Rule

Do not present the ablation as a victory speech.

Present it as a measurement scaffold:

- HoloVerify result: observed performance on frozen action-boundary packets.
- Ablation ladder: what breaks when architecture components are removed.
- Solo baseline: whether the same model families can solve the same packets without governance.
- Decision criterion: what numerical pattern would support or weaken the architecture explanation.

## Prompt Freeze Amendment

Each ladder rung must freeze and version the exact prompt it receives, including packet prompt, wrapper instructions, output contract, model roster binding, prompt hash, and generated provider-prompt hash; otherwise that rung is not eligible for comparison credit.
