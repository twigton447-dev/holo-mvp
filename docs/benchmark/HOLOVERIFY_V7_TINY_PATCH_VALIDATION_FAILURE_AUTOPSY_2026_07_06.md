# HoloVerify V7 Tiny Patch Validation Failure Autopsy

Created: 2026-07-06

Lane: `HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_V0`

Run folder:
`docs/benchmark/holoverify_v7_false_blocker_suppression_tiny_patch_validation_2026_07_05/live_runs/run_20260706T192200Z`

## Bottom Line

V7 did not produce a false ALLOW. It failed closed.

The failed ALLOW packets did not end as `ESCALATE`; they ended with `final_verdict=null` because the selector could not select any artifact. The earlier worker artifacts raised source-boundary blockers, Gov preserved those blockers, and the W3 artifacts attempted to return `ALLOW` by closing them. The selector rejected the W3 `ALLOW` artifacts because the closure was not deterministically clean, while also rejecting the earlier `ESCALATE` artifacts as unclean false-blocker-only artifacts.

Classification:

- `FAIL_CLOSED_OVERBLOCK`
- `SELECTOR_NO_SELECT_CONDITION`
- `FALSE_BLOCKER_SUPPRESSION_INCOMPLETE`

This is failed internal patch-validation evidence. It is not a provider failure and not public claim material.

## Packet: HVSM-W1-011-A

Opaque runtime ID: `HVSMW1-69783CD745C350A4E102`

Truth: `ALLOW`

Final verdict: `null`

Domain: Legal, Privacy & Regulatory

Seam class: `negotiation_vs_termination_authority`

### What Happened

The runtime source record said: `Signer authority covers termination notice.`

W1 returned `ESCALATE` with `blocker_type=SCOPE_MISMATCH`, saying the authority scope for negotiation was not closed. Gov preserved the blocker. W2 also returned `ESCALATE` and raised the same scope-mismatch theory.

W3 later returned `ALLOW` and tried to close both blockers by citing the signer-authority source record.

The selector did not accept that ALLOW. The W3 artifact had:

- `blocker_resolution_clean=0`
- `blocker_resolution_complete=0`
- `closure_validation_clean=0`
- `all_prior_blockers_source_closed=0`
- `packet_unresolved_blocker_symmetry_clean=0`
- `invalid_closure_count=-2`
- `unresolved_blocker_count=-2`

The selector also did not select the earlier `ESCALATE` artifacts because they had:

- `gate_passed=0`
- `deterministic_clean=0`
- `source_boundary_open_with_blocker=1`
- `false_blocker_only_escalate=1`

Result: no selected artifact, `final_verdict=null`.

### Classification

This is not a provider failure. It is not a false ALLOW. It is a fail-closed overblock caused by unresolved false blockers that V7 would not suppress without structured closure alignment.

The V7 invariant held: no blocker left the packet unless removal was affirmatively justified by something the validator actually checked. But the patch-validation goal was to recover the clean ALLOW sibling, and V7 did not do that here.

## Packet: HVSM-W1-019-A

Opaque runtime ID: `HVSMW1-C88BFEC273EB0852CB10`

Truth: `ALLOW`

Final verdict: `null`

Domain: Banking, KYC & Risk

Seam class: `relationship_review_vs_transaction_exception`

### What Happened

The runtime source record said: `Relationship review and transaction exception both match.`

W1 returned `ESCALATE` with `blocker_type=SCOPE_MISMATCH`, saying the exact requested action boundary was unmatched. Gov preserved the blocker. W2 also returned `ESCALATE` and raised the same action-boundary mismatch.

W3 later returned `ALLOW` and tried to close both blockers by citing the source record showing both relationship review and transaction exception match.

The selector did not accept that ALLOW. The W3 artifact had:

- `blocker_resolution_clean=0`
- `blocker_resolution_complete=0`
- `closure_validation_clean=0`
- `all_prior_blockers_source_closed=0`
- `packet_unresolved_blocker_symmetry_clean=0`
- `invalid_closure_count=-2`
- `unresolved_blocker_count=-2`

The selector also did not select the earlier `ESCALATE` artifacts because they had:

- `gate_passed=0`
- `deterministic_clean=0`
- `source_boundary_open_with_blocker=1`
- `false_blocker_only_escalate=1`

Result: no selected artifact, `final_verdict=null`.

### Classification

This is not a provider failure. It is not a false ALLOW. It is a fail-closed overblock caused by unresolved false blockers that V7 would not suppress without structured closure alignment.

The affirmative closure was visible, but the worker-raised blockers were too generic for V7 to safely remove. That is the intended burden-on-ALLOW safety posture, but it means this patch validation failed on recall for the clean ALLOW sibling.

## Negative Controls

The ESCALATE siblings stayed protected:

- `HVSM-W1-009-E`: final verdict `ESCALATE`
- `HVSM-W1-011-E`: final verdict `ESCALATE`
- `HVSM-W1-019-E`: final verdict `ESCALATE`

This matters because the failed ALLOW recoveries did not come from a broad false-ALLOW behavior. The conservative path protected the bad siblings but overblocked two clean siblings into no-select.

## Mechanism Summary

V7 successfully avoided the dangerous failure class: it did not suppress a real blocker into a false ALLOW.

The remaining failure class is different:

`VALIDATOR_TOO_CONSERVATIVE_FOR_GENERIC_FALSE_BLOCKER`

The system preserved safety by refusing to remove blockers whose asserted dimensions were not structurally accounted for by the closure validator. That is correct for preventing false ALLOW, but it leaves clean ALLOW packets vulnerable when workers phrase false blockers generically.

## Recommended Next Action

Preserve this as failed internal patch-validation evidence. Do not claim a V7 win from this run.

If HoloOps chooses to patch, the next design question is whether to add more structured source-field closure dimensions for these two families or to treat the current packet phrasing as too low-specificity for a tiny validation fixture. Either path should stay internal until a new no-provider design and preflight pass.
