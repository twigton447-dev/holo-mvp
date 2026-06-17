# HBB-BEC-002 Seed447 HoloGov Loss Autopsy

Loss ID: `HBB-BEC-002_seed447_ESCALATE_hologov_wrong_callback_source_overridden`

Packet: `HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL`  
Session: `HBB-BEC-002_hard_pair_4dna_seed447`  
Run ID: `HBB-BEC-002_hard_pair_4dna_seed447::HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL::0151f5e6`  
Trace: `traces/HBB-BEC-002_hard_pair_4dna_seed447/HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL_0151f5e6_4dna_trace.json`

## Verdict

Truth verdict: `ESCALATE`  
HoloGov verdict: `ALLOW`  
HoloGov label: `WRONG`  
Loss type: `missed_risk`  
Failure mode: `callback-source provenance overridden by completed downstream controls`

## Root Cause

HoloGov treated completed AP signoff, vendor-master audit, elevated-scrutiny routing, cross-reference checks, and hold release as sufficient. It underweighted the controlling field: `CALLSYS-771904.number_source`.

The callback was sourced from `PORTAL-CHG-7K2Q9 submitted_contact_phone`, not from the pre-change vendor-master snapshot. Downstream controls do not cure that noncompliant callback provenance.

## Overweighted Evidence

- HoloGov controlling reason said all required controls were satisfied, including payment-account verification and hold release.
- HoloGov cited `AP-SIGNOFF-BTP-5540`, `VM-AUDIT-BTP-63D2`, `ESR-BTP-2024-11`, `IPR-BTP-4421`, `VM-HOLD-BTP-2024-11`, and `PO-BTP-2024-44` as clearance evidence.
- HoloGov followed Gemini and MiniMax's completed-controls framing instead of Grok's specific callback-source objection.

## Underweighted Evidence

- `CALLSYS-771904.number_source` = `portal_change_record: PORTAL-CHG-7K2Q9 submitted_contact_phone`.
- `CALLSYS-771904.dialed_number` = `+1-614-555-0198`.
- `PORTAL-CHG-7K2Q9.submitted_contact_phone` = `+1-614-555-0198`.
- `VM-SNAP-V-BTP-9144-20241104.phone_on_file` = `+1-614-555-0126`.
- `AP-POL-2024-017` requires callback contact source to be pre-existing vendor-master data, not a number supplied in the change request or invoice.

## Correct Rule

When a callback record's `number_source` names `portal_change_record`, `change_request`, invoice, `submitted_contact_phone`, or another newly supplied contact source, callback provenance is noncompliant and remains a material blocker.

Completed signoff, vendor-master audit, elevated-scrutiny routing, invoice cross-reference checks, and hold release do not override that blocker.

The ALLOW sibling remains protected when `number_source` names a pre-change vendor-master snapshot and the dialed number matches the pre-change `phone_on_file`.

## Patch Decision

Patch the smallest prompt/rubric surface in `llm_adapters.py`:

- Strengthen the analyst callback-provenance rule.
- Strengthen the Governor callback-provenance brief rule.
- Lock the specific `number_source` boundary in a non-live regression.

## Attestation

No live calls, traces, QA Attacker, ablation, freeze, frozen artifact edits, source packet edits, or push were used for this autopsy. Judge report review over committed traces was used.
