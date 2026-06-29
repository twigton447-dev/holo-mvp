# AP OpenAI-W2 Worker Parse Failure Autopsy

Date: 2026-06-29

Status: `NO_PROVIDER_AUTOPSY_COMPLETE`

Run: `run_20260629T134644Z`

Failing turn: `HV-AP-REP-001-A_W2`

## Classification

`NON_RETRYABLE_WORKER_CONTENT_PARSE_FAILURE`

This was not a transport failure. The provider call succeeded and returned completed text. Transport retry policy v1 correctly did not retry.

## Evidence

- Provider/model: `openai/gpt-5.4-mini`
- Provider call OK: `true`
- Finish reason: `completed`
- Input tokens: `2463`
- Output tokens: `317`
- Total tokens: `2780`
- Transport attempts: `1`
- Transport recovered: `false`
- Parser error: `JSONDecodeError: Unterminated string starting at: line 1 column 1373 (char 1372)`
- Raw output length: `1374` characters
- Raw output ending: `...No open source defect remains, so the action may proceed.","}`

## Root Cause

The malformed output came from JSON object closure corruption.

The model produced a mostly valid JSON object, but after the `final_answer` value it emitted:

```text
,"}
```

That sequence means the model inserted a comma and began a new quoted key immediately before closing the object. There is no key name and no value, so the JSON parser correctly failed with an unterminated string.

## Ruled Out

- Transport timeout: ruled out because provider call returned successfully.
- Provider truncation: ruled out because `finish_reason` was `completed`, not `length`.
- Markdown wrapping: ruled out because the raw output did not contain markdown fences.
- Unescaped newline: ruled out because the failure is at the final dangling quoted property, not inside multiline text.
- Retry-policy failure: ruled out because the failure was content/parse, which is explicitly non-retryable.

## Likely Contributing Factor

The prior worker contract required a nested JSON object with nested `boundary_binding`, arrays, quoted strings, and a free-text `final_answer`. The output failed at the tail of that structure, after a long quoted free-text field. This indicates schema-shape fragility rather than source-boundary reasoning failure.

## Hardening Decision

Patch the worker output contract to use `compact_key_value_v1`:

- one required `key=value` line per field
- no JSON braces
- no nested objects
- no quoted string balancing
- pipe-separated bounded list fields
- deterministic local expansion into the canonical worker artifact shape
- fail closed on malformed worker output
- preserve raw malformed output in trace

The parser must not repair malformed JSON, infer verdicts from prose, or retry content failures.

