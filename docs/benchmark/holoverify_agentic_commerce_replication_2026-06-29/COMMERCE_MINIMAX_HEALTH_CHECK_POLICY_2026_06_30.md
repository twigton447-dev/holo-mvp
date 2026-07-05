# Commerce MiniMax Health Check Policy

Date: 2026-06-30

Classification: `COMMERCE_MINIMAX_HEALTH_CHECK_POLICY`

Status: `REGISTERED_NO_PROVIDER_CALLS`

## Purpose

Commerce Batch 1 has now produced provider-reliability blockers on MiniMax during long governed runs. The benchmark should not keep exporting frozen Commerce prompts into a long batch when MiniMax is already failing DNS or requiring recovery on a harmless request.

This policy adds a non-benchmark MiniMax health gate before any Commerce live batch.

## Health Check Scope

Allowed:

- one harmless MiniMax call
- prompt: `Return exactly MINIMAX_READY`
- max output tokens: `128`
- no packet content
- no benchmark prompt content
- no source IDs
- no traps
- no answer keys
- no solo
- no judges

Pass requires:

- response text exactly `MINIMAX_READY`
- transport attempt count = `1`
- transport recovered = `False`
- no final transport failure class

Fail or block if:

- DNS failure
- timeout
- HTTP 429 or 5xx after retries
- connection reset
- wrong response text
- any transport recovery was required

## Commerce Batch Gate

Before a batch run, the runner must find a recent passing MiniMax health check. The maximum age is `1800` seconds. If no recent clean health check exists, the health-gated batch preflight fails and the batch must not start.

Existing invalid runs remain invalid. This policy does not retroactively recover or repair previous runs.
