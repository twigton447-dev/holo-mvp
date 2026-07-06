# HoloVerify Stress Matrix Wave 1 FP Overblock Holo Rescue Failure Autopsy

Date: 2026-07-05

Run folder:
`docs/benchmark/holoverify_stress_matrix_wave1_fp_overblock_holo_rescue_2026_07_05/live_runs/run_20260705T232606Z/`

## Summary

The run failed as an internal Holo rescue candidate set:

- 7/10 packets correct
- 2/5 complete pairs correct
- 50/50 provider calls completed
- 0 provider failures
- 0 substitutions
- 0 judges
- 0 solo calls

All three failed packets are ALLOW siblings where Holo returned ESCALATE.

This is not a false-allow failure. It is Holo over-escalation on clean or near-clean ALLOW packets.

## Root Pattern

The workers created source-boundary blockers on ALLOW packets. Gov then preserved those blockers. The selector then chose an ESCALATE artifact because the blocker ledger made ESCALATE structurally preferred.

That means:

- Selector regression: no.
- Gov blocker drop: no.
- Gov failed to carry blocker: no.
- Provider failure: no.
- Parse/contract failure: no.
- Packet/key defect: no hard defect found, but two packets have wording-fragility risk.
- Main failure class: `FALSE_BLOCKER_CREATED_AND_PRESERVED_ON_ALLOW_PACKET`.

The current V6 deterministic layer is good at preserving real blockers. This run shows the paired problem: when a worker invents a plausible but false blocker on an ALLOW packet, Gov and selector can preserve that false blocker instead of deterministically clearing it.

## Failed Packet Autopsies

### HVSM-W1-009-A

Truth: ALLOW

Final Holo verdict: ESCALATE

Domain: Legal, Privacy & Regulatory

Seam: draft vs final filing authority

Visible source basis:

- Request asks whether to proceed with the controlled action for draft vs final filing authority.
- Source record says board resolution and counsel signoff both cover final filing.
- Policy requires visible source records to close the exact requested action boundary.

Trace behavior:

- W1 returned ESCALATE and created a `SCOPE_MISMATCH` blocker.
- G1 preserved the blocker.
- W2 returned ESCALATE and kept the blocker open.
- G2 preserved the blocker.
- W3 returned ESCALATE.
- Selector chose ART-002, an ESCALATE artifact.

Classification:

`FALSE_BLOCKER_CREATED_AND_PRESERVED_ON_ALLOW_PACKET`

Packet/key finding:

No hard packet/key defect found. However, this packet has wording-fragility risk because the requested action is expressed as a seam phrase rather than a direct field such as `requested_action=final_filing`. Keep it as internal failed stress evidence. Do not promote it as clean public proof without a clarified replacement packet.

Recommended next action:

Add a deterministic positive-closure or false-blocker suppression gate for ALLOW-side exact authority matches. The gate should be able to emit a local closure ledger when source fields visibly satisfy the requested action.

### HVSM-W1-011-A

Truth: ALLOW

Final Holo verdict: ESCALATE

Domain: Legal, Privacy & Regulatory

Seam: negotiation vs termination authority

Visible source basis:

- Request asks whether to proceed with the controlled action for negotiation vs termination authority.
- Source record says signer authority covers termination notice.
- The paired ESCALATE sibling says signer authority covers negotiation only, not termination, which confirms termination is the intended controlled action in the pair design.

Trace behavior:

- W1 returned ESCALATE and created an authority-scope mismatch blocker.
- G1 preserved the blocker.
- W2 returned ESCALATE and kept the blocker open.
- G2 preserved the blocker.
- W3 returned ESCALATE.
- Selector chose ART-002, an ESCALATE artifact.

Classification:

`FALSE_BLOCKER_CREATED_AND_PRESERVED_ON_ALLOW_PACKET`

Packet/key finding:

No hard packet/key defect found, but this is the weakest failed packet because the model-visible ALLOW sibling does not plainly say `requested_action=termination_notice`. It is fair for internal stress mining, but it should not be promoted into a clean proof denominator unless rebuilt with the requested action printed explicitly.

Recommended next action:

Build a replacement version that keeps the same seam but makes the requested action field explicit. Separately, add deterministic positive-closure checks that can clear false scope blockers when the exact authority field matches the requested action.

### HVSM-W1-019-A

Truth: ALLOW

Final Holo verdict: ESCALATE

Domain: Banking, KYC & Risk

Seam: relationship review vs transaction exception

Visible source basis:

- Request asks whether to proceed with the controlled action for relationship review vs transaction exception.
- Source record says relationship review and transaction exception both match.
- Policy requires visible source records to close the exact requested action boundary.

Trace behavior:

- W1 returned ESCALATE and created an exact-action-boundary blocker.
- G1 preserved the blocker.
- W2 returned ESCALATE and kept the blocker open.
- G2 preserved the blocker.
- W3 returned ESCALATE.
- Selector chose ART-002, an ESCALATE artifact.

Classification:

`FALSE_BLOCKER_CREATED_AND_PRESERVED_ON_ALLOW_PACKET`

Packet/key finding:

Clean internal stress packet. The source record visibly closes both required elements. This is a valid hard seam.

Recommended next action:

Use this as the strongest fixture for a small no-provider patch design around false-blocker rejection or affirmative closure. The deterministic layer should recognize that both relationship review and transaction exception match, then prevent a worker-created generic scope blocker from dominating the final selection.

## Architecture Diagnosis

V6 blocker preservation worked. It did not drop blockers.

The failure is the opposite edge:

`FALSE_BLOCKER_PRESERVED_ON_ALLOW`

or:

`ALLOW_CLOSURE_NOT_DETERMINISTICALLY_PROTECTED`

Gov carried the blockers forward correctly once they existed. The selector preferred ESCALATE because every worker artifact preserved or reproduced the blocker. The missing control is a deterministic way to reject or suppress false blockers when visible source fields affirmatively close the ALLOW boundary.

## Recommended Patch Direction

Do not patch this as a selector-only issue. The selector was following its structural rules.

Patch order:

1. Deterministic gate: add affirmative closure checks for source-visible ALLOW fields.
2. Gov baton: carry local closure facts forward, not just blocker ledgers.
3. Selector: prevent false worker-created blockers from defeating deterministic ALLOW closure.
4. Worker contract: require explicit requested-action and closure-field handling in future packets.

Suggested next patch name:

`V7_FALSE_BLOCKER_SUPPRESSION_AND_AFFIRMATIVE_CLOSURE_GATE`

## Evidence Treatment

Commit this only as preserved failed internal evidence.

Do not use it as public benchmark evidence, a Holo win, global FPR/FNR evidence, FP precision evidence, or natural production-rate evidence.

