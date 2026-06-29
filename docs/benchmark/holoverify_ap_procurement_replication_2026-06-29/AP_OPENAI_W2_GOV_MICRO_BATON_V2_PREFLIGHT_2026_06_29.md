# AP OpenAI-W2 Gov Micro-Baton v2 Preflight

Date: 2026-06-29

Status: `PASS`

Scope: no-provider preflight only. No AP live run, Holo run, solo run, judges, commerce, or IT execution was started.

## Runtime Gov Prompt Probe

The AP OpenAI-W2 runner imports the shared Holo runner and uses the shared Gov prompt builder. A local prompt probe for `HV-AP-REP-001-A_G1` produced the Gov v2 instruction:

```text
HoloGov-V micro-router v2. Return gov_micro_baton_v2 only.
Exactly seven lines. No prose. No reasoning. No JSON. No Markdown. No braces. No quotes.
Required keys in order: verdict,dep,focus,objective,preserve,repair,block.
Allowed verdict values: CONTINUE,FINAL,FAIL.
If gpass true: verdict=FINAL dep=NONE focus=FINAL_CHECK objective=FINALIZE preserve=wb_code repair=NONE block=NONE.
If gpass false: verdict=CONTINUE dep=GATE focus=GATE_REPAIR objective=REPAIR_GATE preserve=wb_code repair=fail_code block=FINAL_ON_FAIL.
Use only uppercase enum/code values from the prompt. No sentences.
```

The local user object supplied only short routing codes plus a non-authoritative note:

```json
{
  "fail_code": "VERDICT_BINDING",
  "gpass": false,
  "id": "HV-AP-REP-001-A",
  "notes_non_authoritative": "missing_boundary_binding:escalate_rule_assessment",
  "wb_code": "CLOSED",
  "wv": "ALLOW"
}
```

## Assertions

| Assertion | Result |
| --- | --- |
| Gov contract is `gov_micro_baton_v2` | PASS |
| Required fields are exactly `verdict,dep,focus,objective,preserve,repair,block` | PASS |
| Long prose repair/block directives removed from required baton fields | PASS |
| Gov output with `finish_reason=length` fails closed | PASS |
| Empty Gov output fails closed | PASS |
| Missing required Gov fields fail closed | PASS |
| Unknown enum/code values fail closed | PASS |
| Overlong/prose fields fail closed | PASS |
| JSON/braces/quotes/markdown fail closed | PASS |
| AP packet hashes match freeze | PASS |
| AP prompt hashes match freeze | PASS |
| W2 remains `openai/gpt-5.4-mini` | PASS |
| Worker contract remains `compact_key_value_v1` | PASS |
| Transport policy V1 unchanged | PASS |
| Provider calls during preflight | 0 |
| Judge calls during preflight | 0 |

## Next Live Step

Do not run a full 200-call AP lane next. The next live step should be a 1-pair AP canary under Gov micro-baton v2.

