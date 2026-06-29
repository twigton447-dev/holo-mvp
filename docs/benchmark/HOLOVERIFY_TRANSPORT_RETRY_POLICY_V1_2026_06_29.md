# HoloVerify Transport Retry Policy v1

Date: 2026-06-29

Status: `REGISTERED_NO_PROVIDER`

Policy ID: `HOLOVERIFY_TRANSPORT_RETRY_POLICY_V1_2026_06_29`

## Purpose

This policy separates provider transport instability from model/content failures before any further long-run HoloVerify replication attempt. It allows bounded retry only when the model call failed before producing usable model content because the transport layer was unavailable or interrupted.

Existing invalid runs remain invalid. This policy is prospective only and must not be retroactively applied to prior traces.

## Allowed Retry Classes

A failed provider call may receive bounded retry only for these transport classes:

- HTTP `429`
- HTTP `500`
- HTTP `502`
- HTTP `503`
- HTTP `504`
- read timeout
- connection reset
- transient network error

## Non-Retryable Classes

These failures are content, model, contract, schema, or deterministic-gate failures and must fail closed without retry:

- wrong verdict
- parse failure
- empty model text
- `finish_reason=length` with incomplete output
- malformed Gov baton
- schema/admissibility failure
- deterministic gate failure

## Invariance Requirements

Every retry must use the exact same:

- packet
- prompt
- model
- provider
- temperature/settings
- role
- turn ID lineage

Retry attempts must not include:

- feedback about the prior failed attempt
- repair instruction
- changed prompt
- changed max tokens
- changed model
- fallback provider

## Retry Budget

- Maximum retries per transport-failed call: `2`
- Maximum attempts per call including the original: `3`
- Backoff policy: exponential bounded backoff using `2s`, then `4s`
- All attempts must be logged in the final trace metadata
- Final trace rows must include `transport_attempt_count`

## Outcomes

If retries fail:

- the run fails closed
- the invalid run is preserved
- no solo baseline may run

If retry succeeds:

- the call row must include `transport_recovered=true`
- failed-attempt metadata must remain in `transport_retry_failures`
- the run may continue
- final evidence must report recovered transport count

## Timeout Values

Registered timeout values after this policy:

- Shared OpenAI-compatible/Gemini HTTP adapter timeout: `150` seconds
- AP OpenAI-W2 Responses adapter timeout: `240` seconds

The AP OpenAI-W2 timeout was increased from the prior `150` seconds after the preserved `run_20260629T132430Z` failed on a read timeout from `openai/gpt-5.4-mini`.

## Implementation Boundary

Retry is implemented inside the provider transport adapter before model content is parsed. Once provider text exists, Gov parsing, worker parsing, schema validation, deterministic gates, admissibility, and final selection remain non-retryable governance outcomes.

## Validation Requirements

Before any provider run may use this policy, local validation must pass:

- `py_compile`
- retry classification fixtures
- AP packet hashes still match freeze
- AP prompt hashes still match freeze
- provider calls: `0`
- judge calls: `0`

