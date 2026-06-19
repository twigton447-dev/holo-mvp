# Judge Brief: Adaptive Execution Intelligence Report

Judges receive the original brief, the frozen source pack, the weighted rubric, and two blind documents labeled Document X and Document Y. Judges must not browse.

The judge panel is the same frontier cohort as the generation cohort:

- `judge_frontier_01`: OpenAI `gpt-5.5`
- `judge_frontier_02`: Anthropic `claude-opus-4-8`
- `judge_frontier_03`: xAI `grok-4.3`

The documents are blinded. Judges are not told which document is Holo, which document is Solo, which model generated either document, or how other judges scored.

## Scoring

Use `judge_rubric_8criteria.json`.

Each criterion must receive:

- `score_1_5`
- `score_1_10`
- criterion-specific notes

The weighted overall score uses the `score_1_10` scale.

## Criteria And Weights

1. Source-grounded current-market accuracy - 15%
2. Execution and microstructure sophistication - 15%
3. Benchmark and peer-comparison design - 15%
4. Portfolio-weight, risk, and funding integration - 15%
5. Adaptive decision-policy quality - 12%
6. Regulatory, control, and audit realism - 10%
7. Model-risk and adversarial insight - 10%
8. Executive clarity and client usefulness - 8%

## Required Judge Output

Return strict JSON with:

- `judge_id`
- `blindness_confirmation`
- per-document summary description
- per-document scores for every criterion
- per-document weighted score
- top 3 strengths for each document
- top 3 weaknesses or hidden failures for each document
- unsupported or stale claims
- math or benchmark logic issues
- comparative verdict
- validation flags

## Blindness Confirmation

Each judge must confirm that they were not told which document is Holo or Solo and were not told the generating model identities.
