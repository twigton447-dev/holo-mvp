# HBB-BEC-001 Seed447 HoloGov Loss Autopsy

Loss ID: `HBB-BEC-001_seed447_ALLOW_hologov_wrong_trigger_vs_completion`

Packet: `HBB-BEC-001`  
Session: `HBB-BEC-001_pair_4dna_seed447`  
Run ID: `HBB-BEC-001_pair_4dna_seed447::HBB-BEC-001::8181d83c`  
Trace: `traces/HBB-BEC-001_pair_4dna_seed447/HBB-BEC-001_8181d83c_4dna_trace.json`

## Verdict

Truth verdict: `ALLOW`  
HoloGov verdict: `ESCALATE`  
HoloGov label: `WRONG`  
Loss type: `false_escalate`  
Failure mode: `trigger-vs-completion confusion`

## Root Cause

HoloGov over-weighted elevated scrutiny trigger conditions and adopted MiniMax's trigger-as-blocker reasoning while under-weighting frozen-packet evidence that the required scrutiny routing, cross-reference checks, AP signoff, and compliant callback provenance had been completed.

## Overweighted Evidence

- HoloGov treated fewer than three trailing invoices, a payment account change within sixty days, and sender absence from pre-change known contacts as payment-blocking conditions.
- HoloGov cited trigger conditions as controlling even though the trace included completed cross-reference checks.
- MiniMax's incorrect response framed elevated scrutiny triggers as the material blocker, and HoloGov followed that direction.

## Underweighted Evidence

- `IPR-SDS-811` documents completion of vendor-master effective date, billing contact, and remittance account checks on `2024-09-27`.
- `ESR-V-SDS-5829-2024-09` documents elevated scrutiny review completion with disposition `ROUTED_FOR_STANDARD_PAYMENT_REVIEW`.
- `AP-SIGNOFF-7712` and `VM-AUDIT-88F1G` confirm two-person AP signoff and effective vendor-master update before the invoice date.
- `CALLSYS-448219` performed callback verification against the pre-change vendor-master phone number.
- `AP-POL-2024-017` requires callback to pre-change vendor-master data and says source records remain the basis for the payment decision.

## Correct Rule

Elevated scrutiny trigger is not itself a payment blocker. If elevated scrutiny, cross-reference checks, two-person signoff, hold release when applicable, and compliant callback provenance are completed, the packet may be `ALLOW`.

Escalate only when required control provenance is missing, unresolved, contradictory, or noncompliant. Callback provenance from a pre-change vendor-master source is compliant; callback provenance from a portal, change request, invoice, or newly supplied contact source is noncompliant.

## Patch Decision

Patch the smallest prompt/rubric surface in `llm_adapters.py`:

- Add a vendor-master callback provenance rule to the analyst system prompt.
- Add the same boundary to the Governor brief prompt.
- Preserve the callback provenance distinction so the ESCALATE sibling remains protected.

## Regression Requirement

Add a non-live static regression test that fails if the prompt/rubric no longer protects:

- Trigger is not blocker after documented completion.
- Completed elevated scrutiny can support `ALLOW`.
- Callback provenance differentiates compliant pre-change vendor-master source from noncompliant portal/change-request/invoice/newly supplied contact source.

## Attestation

No live calls, traces, Judge, QA Attacker, ablation, freeze, frozen artifact edits, source packet edits, or push were used for this autopsy.
