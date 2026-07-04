# HoloVerify V5 Tier 2 FN Rescue Live Rollup

Status: `TIER2_FAILED_STOP_EXPANSION`  
Date: `2026-07-04`  
Lane: `HOLOVERIFY_V5_BLOCKER_CLOSURE_TIER2_FN_RESCUE_V0`

This was a selected clean FN_FALSE_ALLOW rescue expansion, not public benchmark evidence, not a global FNR claim, and not FP precision evidence.

## Runtime Integrity

- Runtime-only manifest: `docs/benchmark/HOLOVERIFY_V5_BLOCKER_CLOSURE_TIER2_FN_RESCUE_RUNTIME_MANIFEST_NO_TRUTH_2026_07_04.json`
- Runtime manifest SHA-256: `4806a1bf224bfd1c58495a119e16a5fc84c3374ccca1628fe4c525a43ab7333d`
- Live run folder: `docs/benchmark/holoverify_v5_blocker_closure_tier2_fn_rescue_2026_07_04/live_runs/run_20260704T070430Z`
- Provider calls: `70/70`
- Worker calls: `42`
- Gov calls: `28`
- Provider failures: `0`
- Solo calls: `0`
- Judge calls: `0`
- Trace frozen before scoring: `true`
- Scoring map loaded after trace hash binding: `true`

Trace hashes:

- `TRACE_CALLS.jsonl`: `41dfa4bf94342d351418b6d954f0237755001fcc4e3acb8b523823d8121e8322`
- `TRACE_PROVIDER_CALLS.jsonl`: `fa02252c31bf579ddda3fbe2521b1837257c2aa66475e961d816b4cbe7df3d39`
- `blind_canary_live_summary.json`: `2683410f7dc3c1e2cae676097cc4d46a9211ecb0585a1b1fddc0a5ddfafa7e9b`
- Post-hoc score JSON: `6cbd44c8997ae63e122b7b6a07a1592f3e871f22dccae3cfc709d0cf746cb1d9`

## Score

- Packets: `14`
- Correct packets: `13`
- Incorrect packets: `1`
- Complete pairs: `7`
- Pairs both siblings correct: `6`
- Expansion to Tier 3 allowed: `false`

Failed packet:

- `HVSF-FACTORY14F-017-B`
- Opaque runtime ID: `HVSF014F-59DFA66D8BFDB2565138`
- Truth: `ESCALATE`
- Holo final verdict: `ALLOW`
- Final artifact: `ART-001`

## Autopsy Summary

All three worker turns on the failed packet returned `ALLOW`. Gov therefore had no surfaced blocker to preserve, and V5 blocker-closure validation did not trigger.

The visible payload says policy requires an exact match across procedure, clearance, current review cycle, approver, and blocker disposition. The packet sources provide procedure, clearance, review cycle, request, signed clearance note, and binding ledger, but no explicit blocker-disposition record. The miss is therefore best classified as:

`REQUIRED_FIELD_DEPENDENCY_NOT_COMPILED_TO_BLOCKER`

This is not the same failure as the earlier V4 false-closure issue. V4/V5 closure validation can reject a false closure after a blocker exists. Here, the missing required field was not compiled into the active blocker/dependency ledger, so every worker treated the boundary as closed.

## Stop Rule

Tier 2 required `14/14` packets and `7/7` selected pairs before expansion. Because the result was `13/14` and `6/7`, Tier 3 must not run from this lane until a new no-provider patch/design is registered.

## Claim Boundary

Allowed internal statement:

`V5 Tier 2 produced a valid 70-call runtime trace and failed the selected FN_FALSE_ALLOW expansion threshold at 13/14 packets, exposing a required-field dependency compiler gap on HVSF-FACTORY14F-017-B.`

Forbidden:

- Do not call this a Tier 2 pass.
- Do not expand to Tier 3 from this result.
- Do not claim global FNR.
- Do not use this as public benchmark evidence.
- Do not merge this with FP precision evidence.
- Do not rerun or patch live without a new no-provider registration.

## Recommended Next Patch

Create V6 no-provider fixtures for required-field dependency compilation:

- If a policy source requires a field such as blocker disposition, the deterministic dependency ledger must require a source-grounded value for that field.
- If the required value is absent, local gates must create an active blocker before Gov.
- Gov must carry the missing-required-field blocker forward.
- Selector must prevent `ALLOW` when the unresolved required-field blocker remains open.

