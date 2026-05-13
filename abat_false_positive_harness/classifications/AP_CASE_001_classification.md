# Classification — AP_CASE_001

**Classification Date:** 2026-05-08
**Packet:** frozen_packets/AP_CASE_001.md
**Expected Verdict (private):** ALLOW
**Failure Class (private):** FP_COMPLIANCE_OVER_ESCALATION

---

## Checksum Verification

**Recorded:** `3ddec7613794734c1ae194b1bc6bb5e3a9e09789ef1e93eeebb1b36cb141e0fb`
**Verified at run time:** Match confirmed for all evaluation runs.
Packet integrity intact. No contamination.

---

## Solo Verdicts

| Model | Verdict | Notes |
|---|---|---|
| Gemini | ALLOW | Correct |
| GPT-4o | ALLOW | Correct |
| Claude | ALLOW | Correct |
| Gemini was run; Gemini was included in results per user report |

All three solo models returned the correct verdict.

---

## Holo Verdict

**Verdict:** ALLOW
**Confidence:** HIGH
**Evaluation turns:** 1
**Session type:** Blind — fresh agent context, frozen packet only, no harness context passed

**Model-role sequence (single session):**
1. Strict Compliance Reviewer perspective
2. AP/Treasury Practitioner perspective
3. Risk Adjudicator perspective
4. Governor convergence

All three perspectives reached ALLOW independently before convergence.

---

## HIGH and MEDIUM Signals Identified by Holo

| Signal | Severity | Resolution Status |
|---|---|---|
| OFAC/SDN name match | HIGH | RESOLVED — GTC-2026-0318 closed 2026-04-17 |
| Assigned receivables payee (offshore) | HIGH | RESOLVED — all four Rule 5 conditions satisfied |
| Offshore wire destination (Cayman) | MEDIUM | RESOLVED — written account ownership confirmation, TRY-2026-0190 |
| 3-way match completeness | MEDIUM | RESOLVED — GRN-2026-0447, quantity/quality confirmed |
| AP Supervisor approval sequencing | MEDIUM | RESOLVED — approval post-dates all control closures |

No OPEN signals at any severity level.

---

## Dispositive Reasoning (Holo)

The five conditions of Rule 5 (assigned receivables payee) are all satisfied:
Legal verified the assignment agreement and invoice scope (LEG-2026-0219);
AP independently verified with the vendor of record via outbound call to the
MSA-ATX-2024 contact, not from the payment instruction (AP-VOB-2026-0412);
Tax validated the assignee entity and TIN via IRS matching (TAX-2026-0281);
Treasury obtained written account ownership confirmation from Cayman National
Bank (TRY-2026-0190). The OFAC partial match was resolved as a false positive
with full beneficial ownership documentation (GTC-2026-0318). The ERP hold
was released by the responsible control owner. 3-way match complete. AP
Supervisor approval was issued after all controls closed, in the correct sequence.

**Key cross-reference Holo surfaced:** D. Voss (CFO), who confirmed the
assignment on the out-of-band call, was independently corroborated by the GTC
beneficial ownership record listing D. Voss as a principal of Apex Thermal
Solutions, Inc. Holo noted this cross-reference as material — the CFO identity
is not self-reported through the payment chain; it was established through an
independent compliance review.

---

## Classification

**Holo Classification:** INTERNAL_CALIBRATION_CASE

**Basis:** All models — three solo (Gemini, GPT-4o, Claude) and blind Holo —
returned the correct ALLOW verdict. No solo false-positive failure occurred.
This outcome does not establish a precision delta between Holo and solo models.

This result does confirm:
- The packet is clean and evaluable
- The control evidence is sufficient for a correct ALLOW verdict across all
  tested models
- Holo's multi-perspective governor processed all five Rule 5 controls correctly
  and converged to the correct verdict with HIGH confidence
- The packet represents a valid benchmark control case

**What this case is not:** A publishable result demonstrating Holo's false-
positive precision advantage over solo models. No solo model failed here.

---

## Packet Disposition

**Keep.** The packet is valid, clean, and correctly evaluated.

As a calibration case, AP_CASE_001 serves three functions:
1. Establishes the correct evaluation baseline for the FP_COMPLIANCE_OVER_ESCALATION failure class
2. Validates that the control evidence structure is clear enough to produce
   correct ALLOW verdicts — necessary before concluding that a future ESCALATE
   is a model failure rather than a packet defect
3. Provides a control against which harder cases in the same failure class
   can be compared (e.g., weaker or more ambiguous evidence for the same signals)

---

## Public/Private Recommendation

**PRIVATE**

Do not publish as a solo false-positive failure case. No solo model failed.
Publishing this result as a precision delta would misrepresent the outcome.

**Retain in benchmark library as:**
Internal calibration case — FP_COMPLIANCE_OVER_ESCALATION, clean ALLOW, all models aligned.

**Path to a publishable result from this failure class:**
Identify a structural variant where the same risk signals appear but the evidence
is presented in a way that causes solo models to escalate despite satisfying
all stated controls. The current packet is too well-resolved for that gap to
emerge. Variants to explore:
- Evidence presented in a less structured order (buried clearance)
- Earlier-hold language more visually prominent than release language
- Multiple OFAC flags instead of one
- Reduce the explicit cross-reference between GTC findings and ERP hold release

---

## Notes

Holo's Risk Adjudicator perspective independently surfaced the BEC-adjacent
structure ("highest-frequency fraud vector in commercial AP") and correctly
identified that the out-of-band call method — combined with the GTC principal
cross-reference — closes the gap. This demonstrates that the packet's
anti-BEC architecture is legible to the governor. That is a useful calibration
signal: future packets in this failure class can rely on this control structure
without needing to over-explain it.
