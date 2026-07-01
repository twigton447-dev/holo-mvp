# AP Replication Resume Plan

Classification: `AP_REPLICATION_RESUME_PLAN_NO_RERUNS_YET`

This plan contains the AP/provider blocker and the only valid resume path. It does not authorize provider calls by itself.

## Current Status

- AP family: `HV-AP-REP-2026-06-29`
- Freeze commit: `de22377be8175d04078ba6c70f1fd35222e9f572`
- Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- AP preflight: `PASS`
- Status: `BLOCKED_ON_REQUIRED_GEMINI_WORKER_503`
- Holo result: `NOT_COMPLETE`
- Solo baseline: `NOT_RUN`
- Judges: `NOT_RUN`
- Commerce/IT: `NOT_RUN`

AP remains blocked until `google/gemini-2.5-flash-lite` is stable enough to complete the required Worker 2 slot in a full HoloVerify run.

## Preserved Invalid Provider-Failure Attempts

The prior attempts remain invalid provider-failure traces and must not be treated as comparative evidence.

| Run | Calls | Worker Calls | Gov Calls | Failure | Lock |
| --- | ---: | ---: | ---: | --- | --- |
| `run_20260629T105111Z` | 133 | 80 | 53 | `google/gemini-2.5-flash-lite` 503 on `HV-AP-REP-014-A_W2` | `PASS` |
| `run_20260629T110920Z` | 43 | 26 | 17 | `google/gemini-2.5-flash-lite` 503 on `HV-AP-REP-005-A_W2` | `PASS` |
| `run_20260629T111600Z` | 28 | 17 | 11 | `google/gemini-2.5-flash-lite` 503 on `HV-AP-REP-003-B_W2` | `PASS` |

## Non-Negotiable Protocol Boundaries

- No roster substitution is allowed under the current protocol.
- No fallback model is allowed for proof credit.
- No packet edits are allowed.
- No prompt edits are allowed.
- No answer-key leakage is allowed.
- Solo must not run until a valid AP Holo freeze exists.
- Commerce/IT must not run until AP is either completed and audited, or explicitly deferred by the user.
- Failed attempts remain invalid provider-failure traces and must be preserved.

## Pre-Resume Health Check Design

Before the next AP live attempt, run only a tiny provider health check:

- Provider/model: `google/gemini-2.5-flash-lite`
- Prompt: harmless non-benchmark test prompt, such as `Return exactly OK.`
- Packet content: none
- Benchmark prompt: none
- Holo run: none
- Solo run: none
- Judges: none
- Expected pass condition: provider call succeeds and response is parseable enough to confirm reachability.

If the Gemini health check fails, keep AP blocked.

If the Gemini health check passes, the next valid move is one fresh full AP HoloVerify attempt from the frozen AP packet bank.

## Next Valid Holo Attempt

Only after the health check passes:

1. Verify AP preflight again.
2. Run a fresh full AP HoloVerify attempt from the frozen AP packet bank.
3. Use the required architecture:
   - `W1 xAI/grok-3-mini`
   - `G1 MiniMax Gov`
   - `W2 google/gemini-2.5-flash-lite`
   - `G2 MiniMax Gov`
   - `W3 minimax/MiniMax-M2.5-highspeed`
4. Run AP only.
5. Do not run judges.
6. Do not run solo until the Holo attempt completes validly with `provider_failures=0`.
7. Preserve and lock any provider-failure attempt as invalid if it fails again.

## Solo Resume Rule

Solo may run only after a valid AP Holo freeze exists.

Solo protocol remains:

- Same frozen AP packets
- `xAI/grok-3-mini`
- `google/gemini-2.5-flash-lite`
- `minimax/MiniMax-M2.5-highspeed`
- One-shot baseline
- No Gov
- No Holo state
- No baton
- No selector
- No judges

## Decision State

AP is blocked, not failed. The correct next action is to wait for Gemini stability, then run the tiny non-benchmark health check. If it passes, proceed with one fresh full AP Holo attempt.
