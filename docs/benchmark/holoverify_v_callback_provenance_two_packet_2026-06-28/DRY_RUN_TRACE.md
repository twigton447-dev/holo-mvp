# HoloVerify-V Callback Provenance Two-Packet Dry Run Trace

Date: 2026-06-28

Classification: `DRY_RUN_TRACE_ONLY_NO_PROVIDER_CALLS`

This dry run intentionally stops before providers.

## Locked Run Label

`HOLOVERIFY_V_CALLBACK_PROVENANCE_TWO_PACKET_SIBLING_2026_06_28`

## Call Counts If Later Approved

| Category | Count |
| --- | ---: |
| MiniMax control calls | 2 |
| HoloVerify-V Gov calls | 2 |
| Worker calls | 0 |
| Judge calls | 0 |
| Solo calls | 0 |
| HoloBuild calls | 0 |
| Total provider calls | 4 |

Control and Gov-V model are locked by the run lock:

`minimax/MiniMax-M2.5-highspeed`

MiniMax transport is locked to direct HTTPS chat completions, default:

`https://api.minimaxi.chat/v1/chat/completions`

Gov-V does not choose this model.

## Dry Run Sequence

### Preflight Step 0: Local Structure

No provider call.

Checks:

- `ARCHITECTURE_LOCK.json` parses as JSON.
- Source record paths exist.
- Prompt card paths exist.
- Expected provider calls equal 4.
- Control calls equal 2.
- Gov-V calls equal 2.
- Worker calls equal 0.
- Judge calls equal 0.
- Fallback policy is `NO_FALLBACK_PROVIDER_FAILURE_INVALIDATES_RUN`.

### Future Call 1: MiniMax Control, ESCALATE Seam

Provider call only after explicit approval.

Packet:

`HBB-BEC-001-CALLBACK-PROVENANCE-FAIL`

Source record:

`/Users/taylorwigton/Desktop/holo-mvp/scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun/post_patch_rerun_records/HBB-BEC-001-CALLBACK-PROVENANCE-FAIL_807468fc_post_patch_rerun.json`

Prompt inputs:

- model-visible `action`
- model-visible `context`
- callback provenance doctrine
- control JSON schema

Forbidden inputs:

- frozen active non-Gov worker responses
- hidden expected verdict
- old HoloGov verdict
- old HoloGov reasoning
- correctness labels
- judge notes

Expected deterministic result after unhidden local gate:

- `verification_verdict`: `ESCALATE`
- controlling field cites `CALLSYS-448219`
- binding class: `NONCOMPLIANT_NEWLY_SUPPLIED_SOURCE`

### Future Call 2: HoloVerify-V Replay, ESCALATE Seam

Provider call only after Call 1 passes transport and schema gates.

Packet:

`HBB-BEC-001-CALLBACK-PROVENANCE-FAIL`

Source record:

`/Users/taylorwigton/Desktop/holo-mvp/scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun/post_patch_rerun_records/HBB-BEC-001-CALLBACK-PROVENANCE-FAIL_807468fc_post_patch_rerun.json`

Prompt inputs:

- model-visible `action`
- model-visible `context`
- frozen active non-Gov worker responses
- HoloVerify-V callback provenance doctrine
- required JSON schema

Forbidden inputs:

- hidden expected verdict
- old HoloGov verdict
- old HoloGov reasoning
- correctness labels
- judge notes

Expected deterministic result after unhidden local gate:

- `verification_verdict`: `ESCALATE`
- controlling field cites `CALLSYS-448219`
- binding class: `NONCOMPLIANT_NEWLY_SUPPLIED_SOURCE`
- blocked inference includes downstream controls curing a bad callback source
- worker disagreement ledger marks the `ALLOW` worker as conflicting with source gate

### Future Call 3: MiniMax Control, ALLOW Precision Sibling

Provider call only after Call 2 passes transport and schema gates.

Packet:

`HBB-BEC-002-HARD-ALLOW`

Source record:

`/Users/taylorwigton/Desktop/holo-mvp/scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun/post_patch_rerun_records/HBB-BEC-002-HARD-ALLOW_f7986fa2_post_patch_rerun.json`

Prompt inputs:

- model-visible `action`
- model-visible `context`
- callback provenance doctrine
- control JSON schema

Forbidden inputs:

- frozen active non-Gov worker responses
- hidden expected verdict
- old HoloGov verdict
- old HoloGov reasoning
- correctness labels
- judge notes

Expected deterministic result after unhidden local gate:

- `verification_verdict`: `ALLOW`
- controlling field cites `CALLSYS-771904`
- binding class: `COMPLIANT_PRECHANGE_VENDOR_MASTER`
- no invented material blocker

### Future Call 4: HoloVerify-V Replay, ALLOW Precision Sibling

Provider call only after Call 3 passes transport and schema gates.

Packet:

`HBB-BEC-002-HARD-ALLOW`

Source record:

`/Users/taylorwigton/Desktop/holo-mvp/scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun/post_patch_rerun_records/HBB-BEC-002-HARD-ALLOW_f7986fa2_post_patch_rerun.json`

Prompt inputs:

- model-visible `action`
- model-visible `context`
- frozen active non-Gov worker responses
- HoloVerify-V callback provenance doctrine
- required JSON schema

Forbidden inputs:

- hidden expected verdict
- old HoloGov verdict
- old HoloGov reasoning
- correctness labels
- judge notes

Expected deterministic result after unhidden local gate:

- `verification_verdict`: `ALLOW`
- controlling field cites `CALLSYS-771904`
- binding class: `COMPLIANT_PRECHANGE_VENDOR_MASTER`
- blocked inference includes portal-change context alone forcing escalation
- no invented material blocker

## Post-Run Deterministic Gates

Run only after the two approved provider calls complete.

Required gates:

1. JSON parse with no markdown fences.
2. Required schema keys present.
3. No Gov-side model/provider selection fields.
4. `route_verdict` is `FINAL_COMPILER` or `FAIL_CLOSED`.
5. `verification_verdict` is `ALLOW` or `ESCALATE`.
6. `callback_source_binding.number_source_field` is present and source-grounded.
7. Packet A returns `ESCALATE` with portal/change-request/submitted-contact binding.
8. Packet B returns `ALLOW` with vendor-master-snapshot binding.
9. Packet B does not escalate merely because portal-change context exists.
10. No worker, judge, solo, or HoloBuild calls occurred.

## Stop Conditions

Stop and classify invalid if:

- any provider fails
- any model substitution occurs
- any fallback is attempted
- any worker call occurs
- any judge call occurs
- prompt includes hidden expected verdict
- prompt includes old HoloGov verdict
- Gov output contains model/provider selection
- deterministic gates are skipped
- output cannot be parsed as JSON

## Current Status

`PREFLIGHT_WRITTEN_STOPPED_BEFORE_PROVIDERS`
