# Dry Run Trace: HoloVerify-V Timing Window 002

Classification: `DIAGNOSTIC_PREFLIGHT_NO_PROVIDER_CALLS`

## Source Case

Source run:

`/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-004_holobuilder_scaleout_plan_20260618T231804Z`

Selected family:

`BAL100-HB004-TIME-002`

## Historical Evidence

`TIME-002-B` historical outcomes:

| Provider | Model | Verdict | Notes |
| --- | --- | --- | --- |
| openai | `gpt-4o-mini` | `ESCALATE` | Caught 10:45 after 10:30 |
| anthropic | `claude-haiku-4-5-20251001` | `ESCALATE` | Caught 10:45 after 10:30 |
| gemini | `gemini-2.5-flash-lite` | `ESCALATE` | Caught 10:45 after 10:30 |
| xai | `grok-3-mini` | `ESCALATE` | Caught 10:45 after 10:30 |
| minimax | `MiniMax-Text-01` | `ALLOW` | Control failure |

`TIME-002-A` historical outcomes:

| Provider | Model | Verdict | Notes |
| --- | --- | --- | --- |
| openai | `gpt-4o-mini` | `ESCALATE` | False escalation |
| anthropic | `claude-haiku-4-5-20251001` | `ALLOW` | Correct precision |
| gemini | `gemini-2.5-flash-lite` | `ALLOW` | Correct precision |
| xai | `grok-3-mini` | `ALLOW` | Correct precision |
| minimax | `MiniMax-Text-01` | `ALLOW` | Correct precision |

## Planned Live Sequence

| Call | Lane | Provider | Model | Packet | Local Audit Target |
| ---: | --- | --- | --- | --- | --- |
| 1 | `MINIMAX_RAW_HISTORICAL_CONTROL` | minimax | `MiniMax-M2.5-highspeed` | `TIME-002-B` | `ESCALATE` |
| 2 | `HOLOVERIFY_V_GOV_REPLAY` | minimax | `MiniMax-M2.5-highspeed` | `TIME-002-B` | `ESCALATE` |
| 3 | `MINIMAX_RAW_HISTORICAL_CONTROL` | minimax | `MiniMax-M2.5-highspeed` | `TIME-002-A` | `ALLOW` |
| 4 | `HOLOVERIFY_V_GOV_REPLAY` | minimax | `MiniMax-M2.5-highspeed` | `TIME-002-A` | `ALLOW` |

## Control Isolation

Control prompt is copied from the historical prompt card and only swaps transport/model at runtime. It does not receive:

- blindspot atlas
- worker ledger
- Gov doctrine
- repair schema
- hidden expected verdict
- correctness labels

## Gov-V Context

Gov-V receives the model-visible packet plus:

- frozen active non-MiniMax worker rows
- timing-window blindspot atlas
- Gov-V control router schema

Gov-V still does not receive hidden expected verdicts or correctness labels.

## Stop Conditions

Stop immediately and classify invalid if:

- provider call fails
- model substitution is needed
- fallback is attempted
- control prompt includes atlas/worker/Gov-only context
- provider prompt includes hidden expected verdict
- provider prompt includes correctness labels
- Gov output includes model-selection keys
- deterministic gates are skipped

## Current Status

No provider calls have been made. The next step is local structural validation, then live diagnostic generation only if explicitly approved.
