# HoloVerify Empty Worker Output Retry Policy v1

Date: 2026-06-29

Status: `REGISTERED_NO_PROVIDER`

Policy ID: `HOLOVERIFY_EMPTY_WORKER_OUTPUT_RETRY_POLICY_V1_2026_06_29`

## Purpose

This prospective policy handles one narrow provider-content anomaly observed in the preserved AP OpenAI-W2 all-six-collapse Holo canary: a worker provider call returned successfully but produced exactly empty text and `0` output tokens. The prior run remains invalid and is not retroactively repaired.

This policy does not retry reasoning, malformed content, wrong verdicts, Gov failures, deterministic gate failures, or schema/admissibility failures.

## Allowed Retry Class

A worker call may receive bounded retry only when all conditions are true:

- call kind is `worker`
- provider call returned a response object
- response text is exactly empty: `""`
- output token count is exactly `0`
- finish reason is not `length`
- no parsed worker content exists

Registered class: `EMPTY_WORKER_TEXT_ZERO_OUTPUT_TOKENS`

## Non-Retryable Classes

The following remain fail-closed without retry:

- wrong verdict
- parse failure with any non-empty text
- markdown-wrapped output
- malformed JSON
- malformed compact key-value output
- empty Gov text
- malformed Gov baton
- `finish_reason=length` with empty or incomplete output
- schema/admissibility failure
- deterministic gate failure
- invented source IDs

## Invariance Requirements

Every retry must use the exact same:

- packet
- prompt
- model
- provider
- temperature/settings
- worker role
- turn ID lineage
- max output token budget

Retry attempts must not include:

- feedback about the prior failed attempt
- repair instruction
- changed prompt
- changed max tokens
- changed model
- fallback provider

## Retry Budget

- Maximum retries per exact-empty worker call: `2`
- Maximum attempts per call including the original: `3`
- Backoff policy: bounded backoff using `1s`, then `2s`
- All attempts must be logged in the final trace metadata

Trace rows must include:

- `empty_worker_output_retry_policy_version`
- `empty_worker_output_attempt_count`
- `empty_worker_output_recovered`
- `empty_worker_output_retry_failures`

## Outcomes

If retry succeeds:

- `empty_worker_output_recovered=true`
- failed empty-attempt metadata remains in `empty_worker_output_retry_failures`
- the run may continue
- final evidence must report recovered empty-worker count

If retries fail:

- the run fails closed
- the invalid run is preserved
- no solo baseline may run

## Implementation Boundary

This policy is implemented after provider transport returns and before worker content parsing. It applies only to worker calls. Gov calls remain governed by the Gov baton contract and fail closed on empty, malformed, or truncated output.

Existing invalid runs remain invalid. This policy is prospective only.

## Validation Requirements

Before any provider run may use this policy, local validation must pass:

- `py_compile`
- exact-empty worker retry fixtures
- malformed worker content non-retry fixtures
- worker retry exhaustion fail-closed fixture
- AP packet hashes still match freeze
- AP prompt hashes still match freeze
- provider calls: `0`
- judge calls: `0`
