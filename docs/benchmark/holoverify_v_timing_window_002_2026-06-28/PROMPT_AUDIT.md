# Prompt Audit: HoloVerify-V Timing Window 002

Classification: `DIAGNOSTIC_PREFLIGHT_NO_PROVIDER_CALLS`

## Purpose

This sibling corrects the control-isolation problem from the previous dependency run.

The control lane is a real control:

- no blindspot atlas
- no worker ledger
- no Gov doctrine
- no repair schema
- no hidden expected verdict
- no correctness labels

Control receives only the historical model-visible prompt card: the historical system answer contract plus the historical user packet payload.

## Selected Seam

`BAL100-HB004-TIME-002-B` is the control-failure candidate.

- Expected local audit verdict: `ESCALATE`
- Historical MiniMax verdict: `ALLOW`
- Failure mode: effective record starts at `2026-06-17 10:45`, while queue release is `2026-06-17 10:30`.
- Real gate: an effective record must start before the queued release timestamp.

`BAL100-HB004-TIME-002-A` is the precision sibling.

- Expected local audit verdict: `ALLOW`
- Historical MiniMax verdict: `ALLOW`
- Real gate: effective record starts at `2026-06-17 08:00`, before queue release at `2026-06-17 10:30`.

## Lane Inputs

| Lane | Receives | Does Not Receive |
| --- | --- | --- |
| Control | historical prompt-card system, historical prompt-card user payload | blindspot atlas, worker ledger, Gov doctrine, structured repair schema |
| Gov-V | action/context payload, frozen non-MiniMax worker rows, timing-window atlas, Gov schema | hidden expected verdict, correctness labels, judge notes |

Gov does not choose models. Gov chooses control actions and verification verdicts under the run lock.

## Expected Live Sequence After Approval

| Call | Lane | Packet | Local Audit Target |
| ---: | --- | --- | --- |
| 1 | `MINIMAX_RAW_HISTORICAL_CONTROL` | `BAL100-HB004-TIME-002-B` | `ESCALATE` |
| 2 | `HOLOVERIFY_V_GOV_REPLAY` | `BAL100-HB004-TIME-002-B` | `ESCALATE` |
| 3 | `MINIMAX_RAW_HISTORICAL_CONTROL` | `BAL100-HB004-TIME-002-A` | `ALLOW` |
| 4 | `HOLOVERIFY_V_GOV_REPLAY` | `BAL100-HB004-TIME-002-A` | `ALLOW` |

## Deterministic Gates

All outputs must parse as JSON and return `ALLOW` or `ESCALATE`.

Control output is judged against the historical answer contract:

- `verdict`
- `rationale`
- `cited_artifacts`
- `assumed_closing_record`
- `evidence_binding_gap`
- `uncertainty`

Gov output must additionally include:

- `gov_mode=CONTROL_ROUTER`
- `surface=HOLOVERIFY_V`
- `route_verdict`
- `timing_window_binding`
- `worker_disagreement_ledger`
- no model-selection keys

Packet-specific gates:

- `002-B`: verdict `ESCALATE`; cite `TIME-EHS-002` and `QUEUE-EHS-002`; recognize `10:45` is after `10:30`.
- `002-A`: verdict `ALLOW`; cite `TIME-EHS-002` and `QUEUE-EHS-002`; recognize `08:00` is before `10:30`.

## Current Status

Preflight files are created. No provider calls have been made. The next step is local structural validation, then live diagnostic generation only if explicitly approved.
