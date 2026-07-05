# AP Full Holo Gov Runtime Mismatch Autopsy

Date: 2026-06-29

Classification: `AP_FULL_HOLO_GOV_RUNTIME_MISMATCH_AUTOPSY`

Status: `PATCHED_NO_PROVIDER_VALIDATION_REQUIRED`

## Failed Run Preserved

Failed full-family run:

```text
docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs_openai_w2/run_20260629T172157Z
```

The failed run is preserved exactly as emitted. This autopsy does not edit the trace, prompts, raw outputs, lock files, or reports.

## Failure

The full-family external execution failed closed after `2/200` expected Holo calls.

| Field | Value |
| --- | --- |
| Failing turn | `HV-AP-REP-001-A_G1` |
| Provider/model | `minimax/MiniMax-M2.5-highspeed` |
| Provider call | `OK` |
| Finish reason | `length` |
| Parser status | `parse_ok=false` |
| Error | `ValueError: gov_finish_reason_length_incomplete_baton` |
| Transport attempted calls | `0` |
| Transport recovered calls | `0` |

This is not a verdict failure and not a transport failure. It is a Gov runtime output-budget/contract failure.

## Canary Comparison

Successful canary run:

```text
docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2/run_20260629T164305Z
```

Both the canary and failed full-family run used the current Gov v2 prompt shape:

```text
HoloGov-V micro-router v2. Return gov_micro_baton_v2 only.
```

The canary G1 call returned all seven required baton lines with `finish_reason=stop`:

```text
verdict=CONTINUE
dep=GATE
focus=GATE_REPAIR
objective=REPAIR_GATE
preserve=CLOSED
repair=VERDICT_BINDING
block=FINAL_ON_FAIL
```

The full-family G1 call returned only four of seven required baton lines and hit `finish_reason=length`:

```text
verdict=CONTINUE
dep=GATE
focus=GATE_REPAIR
objective=REPAIR_GATE
```

The saved full-family prompt included all seven concrete selected baton lines:

```text
verdict=CONTINUE
dep=GATE
focus=GATE_REPAIR
objective=REPAIR_GATE
preserve=OPEN
repair=VERDICT_BINDING
block=FINAL_ON_FAIL
```

The `preserve` value differed because the worker/gate state differed (`CLOSED` in the canary trace, `OPEN` in the full-family trace). Both values are legal concrete `gov_micro_baton_v2` enum values. The difference does not indicate a stale prompt path.

## Root Cause

The canary proved the prompt/parser shape, but it did not prove enough Gov output-budget margin for full-family live execution.

The base HoloVerify runner still used:

```text
GOV_MAX_TOKENS = 384
```

The failed full-family Gov row exhausted that budget:

```text
output_tokens=384
finish_reason=length
```

Because the strict parser correctly rejects `finish_reason=length` when the baton is incomplete, the run failed closed at G1. That was the right safety behavior.

## Patch

The AP OpenAI-W2 variant now sets a larger Gov budget when the registered runtime is configured:

```text
RUNNER.GOV_MAX_TOKENS = 1024
```

This keeps the Gov parser strict and fail-closed:

- empty Gov text remains invalid
- malformed Gov text remains invalid
- `finish_reason=length` with incomplete baton remains invalid
- provider transport retry policy remains unchanged
- packet text, prompt text, truths, and answer keys remain unchanged

## No-Provider Proof Added

Local proof script:

```text
docs/benchmark/test_ap_full_holo_gov_runtime_path_2026_06_29.py
```

The proof asserts:

- AP packet freeze root matches `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- AP packet count is `40`
- AP pair count is `20`
- active W2 is `gpt-5.4-mini`
- no Gemini model is active
- worker contract is `compact_key_value_v1`
- Gov contract is `gov_micro_baton_v2`
- Gov max output budget is `1024`
- live Gov prompt uses the current micro-router v2 prompt shape
- selected baton lines are seven concrete key=value lines
- selected baton lines parse through the real Gov parser
- stale placeholder phrases are absent
- canary and full-family wrappers dispatch through `_run_packet`
- provider calls are `0`
- judge calls are `0`

## Interpretation

The successful canary and failed full-family run were aligned on Gov prompt shape and parser. The gap was runtime budget margin. The full-family path is patched by changing the AP OpenAI-W2 runtime binding, not by weakening validation or repairing malformed output.

Stop after this patch. Do not rerun providers until explicitly approved.
