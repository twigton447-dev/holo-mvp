# HoloVerify Atlas Selector + W3 Patch Validation Result

Status: PATCH_VALIDATION_PASSED
Date: 2026-07-03

This memo records a narrow mechanical patch-validation result. It is not fresh
benchmark evidence, not a public rate claim, and not a general architecture
claim.

## Question Tested

Did `SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03` plus
`WORKER_CONTRACT_V2_ARTIFACT_FIRST_2026_07_03` correct the known Atlas same-six
failure mode without introducing a new selector-caused miss?

Answer: yes, on the fixed same-six Atlas rescue packet set.

## Lineage

Patch commit:

`495421bd168f275e5df7fa8601ed3e1ef8324819`

Selector policy:

`SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03`

Selector policy hash:

`32663f8cd92298468ce3648ec57d9491f76ecf9a9ecb526eaf4bb0c8275118f6`

W3 worker contract:

`WORKER_CONTRACT_V2_ARTIFACT_FIRST_2026_07_03`

W3 worker contract hash:

`d5fdea3133f2bcdea0a9c16f1261081a8fe5ca8264f2a2f0a7e43d41c69a0320`

Packet freeze root:

`d4e130d4598963b55e7cc6b708ff6b850a7e14df1a4b2d9bc2b24c3f08fbb7da`

Runtime manifest:

`0cd8ab98da5c6a4089279922cf644d3cbcb0820555be65d14f88b68b99f453f7`

## Prior Runs Preserved

### Pre-Patch Completed Run

Run:

`docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/run_20260703T140931Z`

Result:

`11/12` correct.

Failure:

`HV-ATLAS-DISC-033-B` was repaired by W3, but the final selector chose the wrong
intermediate W2 artifact.

Failure class:

`FINAL_SELECTOR_CHOSE_WRONG_INTERMEDIATE_ARTIFACT_DESPITE_LATER_WORKER_REPAIR`

### Invalid Patch-Validation Attempt

Run:

`docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/run_20260703T155734Z`

Result:

Invalid, not scored.

Failure:

The final W3 call returned empty visible artifact text after `finish_reason=length`.
This was classified as a W3 output contract failure, not a verdict failure and
not a transport failure.

Autopsy finding:

`MINIMAX_W3_HIDDEN_THINKING_RUNAWAY_ON_AMBIGUOUS_SOURCE_SEAM`

## Patched Replay

Run:

`docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/run_20260703T162431Z`

Live result:

- Expected provider calls: `60`
- Observed provider calls: `60`
- Runtime failure: none
- Runtime firewall: pass
- Judges: none
- Solo: none
- Substitutions: none
- Scoring map before trace freeze: no

Post-freeze score:

- Packets: `12`
- Pairs: `6`
- Correct packets: `12`
- Incorrect packets: `0`
- Pairs with both siblings correct: `6`

Token totals:

- Input tokens: `26,875`
- Output tokens: `15,561`
- Total tokens: `49,912`

## Trace Binding

The score artifact binds to the frozen trace using the following hashes:

- `trace_calls_sha256`: `c736b4c608211f2a2bfa067f1a7abae63b0b19dd5c6a095e72f074bae2456d75`
- `trace_provider_calls_sha256`: `92b86bed2a4ba62e3e4c1c231e3201cc66f9ff19f3572ec330015536edef2bf6`
- `runtime_results_sha256`: `214ee06d915be6d274be319e7e76439bcf2cb1d0e802d30e33a473a2b706ac0a`
- `live_summary_sha256`: `8d1409722976c1db2ad97bab5a84f662ddf57d48d7cb91df0ee60edd47551938`
- `scoring_map_sha256`: `70ddcbcf5a32e4c1a75ebef563dd60c0514e3cc40eda90f5653ef80974661e19`

## Interpretation

The patch validation passed.

The narrow conclusion is:

`SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03` and
`WORKER_CONTRACT_V2_ARTIFACT_FIRST_2026_07_03` corrected the known same-six
Atlas selector/W3 failure pattern under fixed packet, model, prompt, and call
conditions.

## Claim Boundary

Allowed internal language:

"The patched selector and W3 artifact-first contract were rerun on the same
six-pair Atlas rescue set. The replay completed 60/60 provider calls and scored
12/12 after trace freeze. This validates the patch against the known failure
mode."

Forbidden language:

- "The patch improves benchmark performance from 11/12 to 12/12."
- "Atlas now achieves 12/12."
- "This is fresh benchmark evidence."
- "This proves HoloVerify is generally robust."
- "Consensus-first is globally better."
- "This result should be added to the public denominator."

## Next Step

If we want fresh signal, run 2-3 held V5 pairs under a separate exploratory
label. Do not mix those with this same-six patch-validation result.
