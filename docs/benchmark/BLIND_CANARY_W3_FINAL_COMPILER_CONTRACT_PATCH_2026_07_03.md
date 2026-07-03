# Blind Canary W3 Final Compiler Contract Patch

Date: 2026-07-03

Status: `NO_PROVIDER_PATCH_READY`

## Why This Patch Exists

The preserved final blind-canary attempt `run_20260703T004112Z` failed closed on the last provider call:

- Slot: `W3`
- Model: `minimax/MiniMax-M2.5-highspeed`
- Failure: `W3_empty_text`
- Finish reason: `length`
- Raw output behavior: hidden thinking consumed the output budget, then the thinking filter produced empty visible text.

This was not a wrong verdict, false positive, false negative, or transport outage. It was a final compiler content-contract/truncation failure.

## Patch Summary

The patch hardens the W3/final-compiler path without changing packet text, truths, scoring, or fail-closed behavior.

Changes:

- Worker prompts now include a system-level output firewall.
- All worker slots state that the first output characters must be exactly `worker_role=<slot>`.
- W3 receives `FINAL COMPILER STRICT MODE`.
- W3 is instructed not to explain reasoning before fields.
- W3 fields are bounded shorter to reduce truncation risk.
- Live validation now rejects worker output that does not visibly start with `worker_role=<slot>`.
- Live validation now rejects worker output whose parsed `worker_role` does not match the active slot.

## Non-Changes

- No truth metadata was added to runtime prompts.
- No parser permissiveness was added.
- No malformed output repair was added.
- No content retry was added.
- `finish_reason=length` still fails closed.
- Empty visible text still fails closed.
- Scoring remains post-trace-freeze only.

## Validation

Targeted no-provider validation:

- `py_compile`: PASS
- `tests/test_holoverify_blind_canary_live_wrapper.py`: `19 passed`
- Blind-lane suite plus wrapper: `38 passed, 12 skipped`

Broad `pytest tests -q -k 'blind or holoverify_blind_canary'` was intentionally not used as final validation because pytest still collects unrelated app tests before keyword selection in this environment; those unrelated tests require missing local dependencies such as `fastapi`, `pydantic`, `bcrypt`, and `cryptography`.

## Next Action

Commit this patch before any fresh live attempt. Then rerun the failed scope conservatively:

1. Preflight packet 20 only, or packet 19/20 one at a time.
2. Run live only after preflight passes.
3. Preserve the result exactly.

