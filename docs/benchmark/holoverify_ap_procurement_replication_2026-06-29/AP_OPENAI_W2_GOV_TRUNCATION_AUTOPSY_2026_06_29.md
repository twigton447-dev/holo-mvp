# AP OpenAI-W2 Gov Truncation Autopsy

Date: 2026-06-29

Status: `NO_PROVIDER_AUTOPSY_COMPLETE`

Run: `run_20260629T140257Z`

Failing turn: `HV-AP-REP-001-A_G1`

## Classification

`GOV_CONTRACT_OR_TRUNCATION_FAILURE`

This was not a provider transport failure. MiniMax returned text with `provider_call_ok=true`, but the response ended with `finish_reason=length` and the compact baton was incomplete. Transport retry policy v1 correctly did not retry because `finish_reason=length` with incomplete output is a content/contract failure, not transport.

## Evidence

- Provider/model: `minimax/MiniMax-M2.5-highspeed`
- Provider call OK: `true`
- Finish reason: `length`
- Input tokens: `235`
- Output tokens: `384`
- Total tokens: `619`
- Transport attempts: `1`
- Transport recovered: `false`
- Parser error: `ValueError: gov_finish_reason_length_incomplete_baton:gov_micro_missing_keys:dep,focus,objective`
- Raw baton length: `296` characters
- Raw baton ending: `timing/s`

## Root Cause

Gov micro-baton v1 allowed long natural-language repair and block directives inside parse-required fields:

```text
repair=Repair deterministic gate failures while preserving the source-boundary finding SOURCE_BOUNDARY_CLOSED: missing_boundary_binding:escalate_rule_assessment
block=Do not drop source IDs, action boundary, timing/s
```

The model hit the configured output limit before producing required fields `dep`, `objective`, and `focus`. The parser correctly failed closed.

## Ruled Out

- AP worker compact contract failure: ruled out because the failing turn was Gov `G1`, before W2.
- Transport retry failure: ruled out because this was not a transport exception.
- Provider outage: ruled out because the provider returned content.
- Prompt leakage: no-leakage audit for the run passed.
- Lock failure: lock validation passed.

## Hardening Decision

Patch Gov to `gov_micro_baton_v2`:

- fixed seven fields only: `verdict`, `dep`, `focus`, `objective`, `preserve`, `repair`, `block`
- uppercase enum/code values only
- no prose
- no markdown
- no JSON
- no braces or quotes
- no long repair directive in parse-required fields
- fail closed on empty output, `finish_reason=length`, missing fields, overlong fields, unknown codes, or forbidden punctuation

Longer Gov explanations may exist only as local non-authoritative notes or deterministic state repair directives after parsing. They must not be required provider parse material.

