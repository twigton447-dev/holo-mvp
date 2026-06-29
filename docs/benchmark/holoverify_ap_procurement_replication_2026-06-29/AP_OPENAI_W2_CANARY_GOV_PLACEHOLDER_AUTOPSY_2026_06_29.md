# AP OpenAI-W2 Canary Gov Placeholder Autopsy

Date: 2026-06-29

Classification: `AP_OPENAI_W2_CANARY_GOV_PLACEHOLDER_AUTOPSY`

Status: `PATCH_REQUIRED_NO_PROVIDER_RERUN`

## Preserved Run

- Run: `run_20260629T153048Z`
- Path: `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2/run_20260629T153048Z`
- Scope: one AP pair canary, sibling A/B intended
- Calls completed: `2 / 10`
- Solo calls: `0`
- Judge calls: `0`
- Provider failures: `0`
- Lock validation: `PASS`
- No-leakage audit: `PASS`

## Root Failure

- Turn: `HV-AP-REP-001-A_G1`
- Provider/model: `minimax/MiniMax-M2.5-highspeed`
- Provider call: `OK`
- Finish reason: `stop`
- Parse status: `FAIL`
- Error: `ValueError: gov_micro_v2_unknown_enum:preserve:wb_code`

Raw Gov output:

```text
verdict=CONTINUE
dep=GATE
focus=GATE_REPAIR
objective=REPAIR_GATE
preserve=wb_code
repair=VERDICT_BINDING
block=FINAL_ON_FAIL
```

## Root Cause

The Gov v2 prompt contract included literal placeholder-style output examples:

```text
If gpass true: verdict=FINAL dep=NONE focus=FINAL_CHECK objective=FINALIZE preserve=wb_code repair=NONE block=NONE.
If gpass false: verdict=CONTINUE dep=GATE focus=GATE_REPAIR objective=REPAIR_GATE preserve=wb_code repair=fail_code block=FINAL_ON_FAIL.
```

The user payload supplied concrete short codes (`wb_code=CLOSED`, `fail_code=VERDICT_BINDING`), but the provider-facing instruction itself taught `preserve=wb_code` as a valid-looking baton line. MiniMax copied the literal placeholder. The strict v2 parser rejected it because `wb_code` is not in the allowed `preserve` enum set.

This is a Gov prompt/contract defect. It is not a transport failure, not a provider outage, and not an AP verdict failure.

## Patch Direction

- Preserve the failed canary run exactly as-is.
- Do not loosen parsing to accept `wb_code`.
- Pre-materialize concrete `selected_baton_lines` before the Gov provider call.
- Provider-facing Gov instructions must contain only concrete enum/code values in output examples.
- Parser must explicitly fail closed on placeholder tokens such as `wb_code`, `fail_code`, `field_name`, `value`, `TODO`, `example`, and `placeholder`.
- Next live step after patch is another one-pair AP canary, not full AP.
