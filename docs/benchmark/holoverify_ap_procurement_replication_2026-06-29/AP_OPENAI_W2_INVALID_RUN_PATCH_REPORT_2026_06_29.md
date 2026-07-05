# AP OpenAI-W2 Invalid-Run Handling Patch Report

Date: 2026-06-29

## Scope

No providers were run. No AP rerun was started. No solo baseline, judges, commerce, or IT lanes were run.

The invalid AP OpenAI-W2 Holo attempt remains preserved at:

`docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs_openai_w2/run_20260629T114551Z`

## Preserved Invalid Run

Root failure remains:

- stopped at 167 / 200 expected Holo calls
- failing turn: `HV-AP-REP-017-B_G1`
- provider/model: `minimax/MiniMax-M2.5-highspeed`
- call kind: `gov`
- finish_reason: `length`
- text: empty
- parse_ok: `false`
- provider transport failures: `0`
- original trace error: `ValueError: gov_micro_key_value_parse_failed`

This is classified as a Gov output contract/truncation failure, not a Holo verdict failure.

## Patches

### Gov Contract Hardening

- Removed the contradictory Gov instruction that said to return JSON.
- Gov now asks for one compact `key=value` baton only.
- Required Gov keys are: `verdict`, `route`, `final`, `preserve`, `repair`, `block`, `dep`, `objective`, `focus`.
- Gov parser no longer accepts JSON as a fallback for the live micro-router path.
- Empty Gov text fails closed with deterministic error labels.
- `finish_reason=length` plus empty/incomplete baton fails closed.
- Raw Gov output remains preserved in the trace row.
- Parser failures remain parser failures; the parser was not loosened to accept empty or malformed Gov output.

### Reporting Hardening

- Roster audit now supports both the original `architecture_lock.model_roster_declared` shape and the AP OpenAI-W2 top-level `model_roster_declared` shape.
- Expected-count extraction now supports both original `total_provider_calls` and AP variant `holo_calls` fields.
- AP Holo summaries now include `root_failure` and `invalidation_reason`.
- Invalid summaries can be generated without crashing when `architecture_lock` is absent.

## No-Provider Fixture Tests

Test file:

`docs/benchmark/test_ap_openai_w2_invalid_run_handling_2026_06_29.py`

Fixtures:

- empty Gov text -> invalid
- `finish_reason=length` with incomplete baton -> invalid
- valid compact Gov baton -> parse PASS
- invalid run summary with missing `architecture_lock` -> summary PASS
- no packet/prompt hash mutation

## Validation Results

- `py_compile`: PASS
- fixture tests: PASS
- AP packet hashes still match freeze: PASS
- AP prompt hashes still match freeze: PASS
- freeze root matched: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- runner W2 remains: `openai/gpt-5.4-mini`
- no providers called during patch validation: PASS
- no judges called during patch validation: PASS
- invalid AP run preserved: PASS

## Readiness

AP is not automatically rerun by this patch.

After this patch is committed, AP can be considered ready for an explicitly approved fresh full Holo attempt, because the invalid-run reporting and Gov truncation/contract failure handling are hardened.
