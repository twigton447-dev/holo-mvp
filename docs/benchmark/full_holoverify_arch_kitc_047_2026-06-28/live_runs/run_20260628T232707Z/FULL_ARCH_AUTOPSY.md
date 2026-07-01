# Full HoloVerify Architecture 047 Autopsy

Run: `run_20260628T232707Z`

Classification: `FULL_ARCH_CANDIDATE_PAIR_PENDING_JUDGE`

Benchmark locked: no

## Scope

This was a full HoloVerify architecture replay for `HV-KITC-047`, the original exposed-class license-exception pair.

Repeated classes:

- `FP_EXCEPTION_PATH_FREEZE`
- `ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW`

No Solo rerun. No judges. No model substitutions.

## Architecture Calls

| Call Type | Count |
| --- | ---: |
| Worker calls | 6 |
| Real HoloGov calls | 4 |
| Solo rerun calls | 0 |
| Judge calls | 0 |
| Total provider calls | 10 |

Token total: `21171` input / `10558` output / `31729` total.

## Outcome

| Packet | Target Behavior | Full-Arch Output | Selector |
| --- | --- | --- | --- |
| `HV-KITC-047-A` | Hard ALLOW rescue | `ALLOW` / `EXACT_EXCEPTION_CLOSED` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-KITC-047-B` | ESCALATE guardrail | `ESCALATE` / `CONSIGNEE_ROLE_MISMATCH` | `FINAL_ARTIFACT_ADMISSIBLE` |

## Enforcement Notes

`047-A` was stable:

- Worker 1, Worker 2, and Worker 3 all passed deterministic gates.
- The final selector accepted the final worker artifact.

`047-B` demonstrated repair:

- Worker 1 incorrectly allowed the guardrail sibling.
- The deterministic gate rejected Worker 1 because it failed `source_gate_verdict_expected_ESCALATE` and `source_gate_binding_expected_CONSIGNEE_ROLE_MISMATCH`.
- Later workers repaired the output to `ESCALATE` / `CONSIGNEE_ROLE_MISMATCH`.
- The final selector accepted the final admissible artifact.

## Interpretation

This is the second full-architecture hard-ALLOW false-positive rescue candidate in the current ledger.

It repeats the same exposed failure class used by `082` but in the original license-exception domain.
