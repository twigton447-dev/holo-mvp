# Dry Run Trace: HoloVerify-V Subtle Closeout 021

Classification: `GOV_V_RESCUE_PREFLIGHT_AFTER_CONTROL_FAILURE_FOUND`

## Source Case

Source run:

`/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-003_bounded_scout`

Selected family:

`BAL100-BEC-SUBTLE-CLOSEOUT-021`

## Frozen Failed Control

`BAL100-BEC-SUBTLE-CLOSEOUT-021-A`

- Expected local audit verdict: `ALLOW`
- Current MiniMax M2.5 raw control verdict: `ESCALATE`
- Control screen run: `run_continue_20260628T204437Z`
- Gov calls in the control screen: `0`
- Holo calls in the control screen: `0`

## Historical Worker Shape

For `021-A`, most frozen non-MiniMax workers escalated, while Grok allowed:

- OpenAI: `ESCALATE`
- Anthropic: `ESCALATE`
- Gemini: `ESCALATE`
- XAI/Grok: `ALLOW`

That means Gov-V must adjudicate source binding, not vote.

For `021-B`, all frozen workers escalated.

## Planned Live Calls

| Call | Lane | Provider | Model | Packet | Local Audit Target |
| ---: | --- | --- | --- | --- | --- |
| 1 | `HOLOVERIFY_V_GOV_REPLAY` | minimax | `MiniMax-M2.5-highspeed` | `021-A` | `ALLOW` |
| 2 | `HOLOVERIFY_V_GOV_REPLAY` | minimax | `MiniMax-M2.5-highspeed` | `021-B` | `ESCALATE` |

No control rerun. No worker calls. No judge calls.

## Stop Conditions

Stop immediately and classify invalid if:

- provider call fails
- model substitution is needed
- fallback is attempted
- control is rerun
- provider prompt includes hidden expected verdict
- provider prompt includes correctness labels
- Gov output includes model-selection keys
- deterministic gates are skipped

## Current Status

Ready for the approved two-call Gov-V rescue run.
