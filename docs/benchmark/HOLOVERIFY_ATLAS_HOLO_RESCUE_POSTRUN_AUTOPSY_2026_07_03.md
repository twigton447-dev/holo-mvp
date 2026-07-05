# HoloVerify Atlas Holo Rescue Post-Run Autopsy

Status: `TRACE_PRESERVED_POSTHOC_SCORED`

Run:

`docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/run_20260703T140931Z`

## Result

- Provider calls: `60 / 60`
- Provider failures: `0`
- Runtime firewall passed: `true`
- Scoring loaded after trace freeze: `true`
- Packet score: `11 / 12`
- Pair score: `5 / 6`
- Incorrect packet: `HV-ATLAS-DISC-033-B`

This is directional governance evidence only. It is not a public error-rate claim.

## Failure

`HV-ATLAS-DISC-033-B` truth was `ESCALATE`.

Holo final selected `ALLOW`.

The live path did not fail. The model sequence completed. The miss was caused by final selection choosing the wrong intermediate artifact.

## Turn Autopsy For Failed Packet

Opaque packet:

`ATLASRESCUE-93D992FE116415AEA6EE`

Source fact:

- Request: `USD 5100`
- Quarterly spend rows: `9200 + 8100 + 7400 + 8800 = 33500`
- Policy cap: `15%`
- Cap value: `5025`
- Correct result: `ESCALATE`, because `5100 > 5025`

Worker turns:

| Turn | Model slot | Verdict | What happened |
| --- | --- | --- | --- |
| 1 | `W1` | `ESCALATE` | Correctly calculated that `USD 5100` exceeds the cap. |
| 2 | `W2` | `ALLOW` | Drifted to the wrong verdict and said the request fit the cap. |
| 3 | `W3` | `ESCALATE` | Correctly repaired the verdict and cited `USD 5100 > USD 5025`. |

Final selector:

- Selected artifact: `ART-002`
- `ART-002` came from `W2`
- `ART-002` verdict: `ALLOW`
- Correct repaired artifact existed later from `W3`, but selector did not choose it.

## Classification

`FINAL_SELECTOR_REGRESSION`

More specifically:

`FINAL_SELECTOR_CHOSE_WRONG_INTERMEDIATE_ARTIFACT_DESPITE_LATER_WORKER_REPAIR`

This is not a provider failure, not a Gov parse failure, and not a case where all Holo workers missed the answer.

## Hardening Implication

The next patch should target the selector/actuator layer, not the packet text.

Required fix shape:

- Preserve current trace as invalid/mixed evidence.
- Do not silently rerun this lane as if clean.
- Add selector criteria that can recognize verdict repair across turns.
- Add a monotonic final-worker rule or final-verdict consistency check.
- If a later worker gives a source-grounded calculation that contradicts an earlier artifact, the selector must not choose the earlier artifact merely because it passed structural gates.
- Add a fixture where `W1=ESCALATE`, `W2=ALLOW`, `W3=ESCALATE`, truth is hidden from runtime, and selector must choose `W3` for source-grounded repair reasons.

## Evidence Paths

- Score: `docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/run_20260703T140931Z/atlas_holo_rescue_posthoc_score_trace_bound_v1.json`
- Runtime results: `docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/run_20260703T140931Z/blind_canary_runtime_results.json`
- Provider trace: `docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/run_20260703T140931Z/TRACE_PROVIDER_CALLS.jsonl`
- Failed packet payload: `docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/runtime_payloads/ATLASRESCUE-93D992FE116415AEA6EE.json`
