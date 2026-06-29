# AP All-Six-Collapse Empty Worker Retry Patch Report

Date: 2026-06-29

Status: `NO_PROVIDER_VALIDATION_PASS`

## Scope

This patch is prospective only. It preserves the invalid AP all-six-collapse canary run at `run_20260629T191023Z` and registers a narrow retry policy for exact-empty worker output.

## Failure Addressed

- Failing turn: `HV-AP-REP-013-B_W1`
- Provider/model: `xai/grok-3-mini`
- Provider call OK: `true`
- Text: `""`
- Output tokens: `0`
- Error: `ValueError: worker_empty_text`

## Patch

- Added `HOLOVERIFY_EMPTY_WORKER_OUTPUT_RETRY_POLICY_V1_2026_06_29`.
- Added worker retry handling only for exact empty text with `output_tokens=0` and non-`length` finish reason.
- Added trace metadata for empty-worker retry attempts.
- Left malformed worker content, Gov baton failures, wrong verdicts, deterministic gates, and schema/admissibility failures non-retryable.
- Added all-six canary preflight checks for the empty-worker retry policy.

## Validation

- `py_compile`: `PASS`
- no-provider fixture tests: `PASS`
- AP freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- AP packet count: `40`
- W2 binding: `openai/gpt-5.4-mini`
- Gov contract: `gov_micro_baton_v2`
- Worker contract: `compact_key_value_v1`
- Gov max tokens: `1024`
- Provider calls during validation: `0`
- Judge calls during validation: `0`

## Next Valid Move

The next valid live move is a fresh AP OpenAI-W2 all-six-collapse Holo canary using the patched runner. Do not resume the invalid run. Do not run solo or judges before a valid Holo canary freeze exists.
