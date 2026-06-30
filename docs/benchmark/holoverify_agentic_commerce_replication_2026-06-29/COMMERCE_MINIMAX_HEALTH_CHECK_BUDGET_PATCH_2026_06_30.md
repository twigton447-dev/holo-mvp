# Commerce MiniMax Health Check Budget Patch

Date: 2026-06-30

Classification: `COMMERCE_MINIMAX_HEALTH_CHECK_BUDGET_PATCH`

Status: `PATCH_REGISTERED_NO_BENCHMARK_PROVIDER_CALLS`

## Trigger

Taylor ran the new Commerce MiniMax health gate before a live batch. The health check used no benchmark content and produced this result:

- Provider call OK: `True`
- Transport attempts: `1`
- Transport recovered: `False`
- Finish reason: `length`
- Output tokens: `16`
- Visible response text: empty string
- Expected response: `MINIMAX_READY`

The health-gated batch preflight then correctly blocked with:

`preflight_failed:['minimax_health_check_recent_clean_pass']`

## Root Cause

The first health probe used `16` max output tokens. That was too low for MiniMax in this runtime because the provider consumed the small output budget without emitting visible text after the thinking-filter pass.

This was not a Commerce benchmark result, not a Holo verdict failure, and not a packet failure.

## Patch

The harmless MiniMax health check output budget is now `128` tokens.

The pass condition remains strict:

- response text must be exactly `MINIMAX_READY`
- transport attempts must equal `1`
- transport recovered must be `False`
- no packet text, prompt text, source IDs, traps, or answer keys may be included

Existing failed health reports remain preserved and are not reclassified as passing.

