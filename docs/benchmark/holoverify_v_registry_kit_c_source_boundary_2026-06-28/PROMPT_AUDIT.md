# Prompt Audit: HoloVerify-V Kit C Source-Boundary Candidate

Classification: `REGISTRY_GRADE_CANDIDATE_PREFLIGHT`

This package creates a new pre-registered Kit C candidate lane for the two
HoloVerify-V source-boundary pairs discovered during diagnostic work:

- `HV-KITC-021`: quality-hold close-out precision
- `HV-KITC-022`: activation dependency precision

The prior diagnostic traces are not promoted directly. They remain diagnostic
evidence. This package creates a fresh hash-locked generation attempt.

## Fairness Rule

The A/B pair is the fairness unit.

For each packet:

- Solo receives one MiniMax API call using only the ordinary model-visible packet
  prompt.
- HoloVerify-V receives one MiniMax Gov-V API call using the current packet,
  source-neutral family atlas, frozen non-MiniMax worker evidence, and Gov-V
  structured schema.

Across two A/B pairs:

- Solo calls: `4`
- HoloVerify-V Gov calls: `4`
- Worker calls: `0`
- Judge calls during generation: `0`
- Total generation calls: `8`

## HoloVerify-V Inputs

Gov-V receives:

- current packet `action`
- current packet `context`
- source-neutral family atlas
- frozen active non-MiniMax worker responses
- Gov-V structured control-router schema

Gov-V does not receive:

- hidden expected verdict
- correctness labels
- judge notes
- old HoloGov verdict
- failed control raw text
- authority to choose or substitute models

## Solo Inputs

Solo receives:

- historical model-visible packet system prompt
- historical model-visible packet user prompt

Solo does not receive:

- source-neutral family atlas
- frozen worker responses
- Gov-V schema
- Gov baton
- hidden expected verdict
- correctness labels

## Deterministic Gates

Local gates run on every provider output.

Common gates:

- JSON parse
- valid `ALLOW` or `ESCALATE` verdict
- exact source ID hygiene
- packet-specific semantic trap checks

Gov-V-only gates:

- `gov_mode=CONTROL_ROUTER`
- `surface=HOLOVERIFY_V`
- no model-selection fields
- route/verdict/compiler consistency
- binding class consistency

## Publication Status

If generation succeeds, this package can only move to:

`frozen_pending_judge`

It cannot become `benchmark_locked` until independent adjudication is run over
the frozen traces.

## Stop Conditions

Stop and classify invalid if:

- any provider fails
- any model substitution occurs
- any fallback occurs
- prompt contamination is detected
- JSON parsing fails
- deterministic gates are skipped
- source IDs are invented
- Gov emits model-selection keys
- Gov route/verdict/final-compiler fields conflict

