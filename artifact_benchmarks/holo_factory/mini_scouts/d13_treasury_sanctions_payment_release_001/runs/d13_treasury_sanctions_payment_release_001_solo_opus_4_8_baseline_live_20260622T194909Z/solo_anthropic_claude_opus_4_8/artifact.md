# Treasury Action Brief: Meridian Supply Pte Ltd. — USD 18,400,000 Cross-Border Wire

## 1. Bottom-line recommendation

**HOLD. Prepare the wire in the bank hold queue without release; do not send final payment confirmation today on current evidence.** Two reversible actions may run now: (a) build and upload the wire as a pending, held item (S10_BANK_CUTOFF_AND_HOLD_QUEUE_NOTICE); and (b) draft a strictly non-committal limited holding notice and route it to Compliance/Legal for wording approval before any send (S1_TREASURY_PAYMENT_RELEASE_POLICY). Release is permissible **only** if all four release gates clear, with proof artifacts, before the 16:30 ET cutoff. They have not cleared as of the latest records (S5_COMPLIANCE_RELEASE_QUEUE_STATUS, 15:12 ET; S6_CURRENT_DAY_UBO_INTERMEDIARY_ESCALATION, 15:08 ET).

## 2. What is happening and why it matters now

Ridgewater is deciding whether to release an USD 18,400,000 cross-border wire to Meridian before a same-day 16:30 ET cutoff (S3_DERIVED_PAYMENT_RISK_DASHBOARD; S10_BANK_CUTOFF_AND_HOLD_QUEUE_NOTICE). The prior-day entity screen was clear (S2_PRIOR_DAY_SANCTIONS_SCREEN_CLEARANCE), but two material facts changed today: the intermediary bank changed after that screen, and the beneficial owner generated an 82% fuzzy match requiring manual disposition (S6_CURRENT_DAY_UBO_INTERMEDIARY_ESCALATION). The current-day rescreen, UBO disposition, and Compliance release are all open (S5_COMPLIANCE_RELEASE_QUEUE_STATUS). The pressure is real but one-sided: a business sponsor and the supplier demand confirmation today (S8_BUSINESS_SPONSOR_SUPPLIER_URGENCY_NOTE). The decision matters now because release is irreversible absent separate bank cancellation (S10_BANK_CUTOFF_AND_HOLD_QUEUE_NOTICE), so a rushed click cannot be undone, while a hold can.

## 3. Strongest evidence

Policy is unambiguous: cross-border wires above USD 5,000,000 require same-business-day screening, documented beneficial owner review, callback, dual Treasury approval, **and** Compliance release before payment; vendor master and payment history do not substitute (S1_TREASURY_PAYMENT_RELEASE_POLICY). Compliance corroborates the live state: RQ-8841 is open, rescreen and UBO pending, **no release issued, payment release not authorized** (S5_COMPLIANCE_RELEASE_QUEUE_STATUS). The escalation record explains why and sets a hard precondition: Compliance disposition is required before release, and the new intermediary bank must be in the screened-party set before any final confirmation (S6_CURRENT_DAY_UBO_INTERMEDIARY_ESCALATION). These three strong sources align: release is not authorized today on present facts.

## 4. Weak, stale, missing, or conflicting evidence

The prior-day clear screen is genuine but stale and explicitly entity-only, with no current refresh, UBO, or new-intermediary coverage (S2_PRIOR_DAY_SANCTIONS_SCREEN_CLEARANCE). The supplier's attestation that "there is no sanctions issue" names no beneficial owners, intermediary screening, or reviewer, and cannot substitute for Ridgewater's screening (S9_WEAK_SUPPLIER_SANCTIONS_ATTESTATION). The dashboard reads green but footnotes that "green does not mean sanctions release," with Compliance release blank and Treasury approval shown as one-of-two (S3_DERIVED_PAYMENT_RISK_DASHBOARD) — a derived, not authoritative, record. Vendor master, callback, and AP history are complete and useful but each disclaims sanctions/release authority (S4_VENDOR_MASTER_BANK_CALLBACK_LOG; S7_AP_VENDOR_HISTORY_ACTIVE_STATUS). **Missing entirely:** any current-day clear result, UBO disposition, Compliance release, corroborated second Treasury approval, bank cancellation guarantee, or contract/default terms.

## 5. Calculations / payment-risk interpretation

The controlling math is asymmetry, not arithmetic. A hold is fully recoverable: the wire can sit in queue and fire within minutes if gates clear (S10_BANK_CUTOFF_AND_HOLD_QUEUE_NOTICE). A release is irreversible absent separate bank cancellation (S10), so the full USD 18,400,000 is at risk into a chain whose intermediary bank is unscreened and whose UBO match is undispositioned (S6_CURRENT_DAY_UBO_INTERMEDIARY_ESCALATION). Treasury approval at one-of-two is a control-incomplete state reported only by a derived source (S3_DERIVED_PAYMENT_RISK_DASHBOARD). Expected-cost logic favors holding: the downside of waiting is a delayed payment, recoverable later; the downside of releasing wrong is unrecoverable sanctions exposure on the full amount. No fact in the packet narrows that gap.

## 6. Practical response options

A sequence, not a menu — 1–2 run now, 3 is contingent, 4–5 rejected.
1. **HOLD + prepare wire in hold queue (recommended; Treasury Ops; now).** Upload as pending, held, **unreleased** (S10_BANK_CUTOFF_AND_HOLD_QUEUE_NOTICE). Reversible; blocks nothing; preserves the ability to fire fast if gates clear.
2. **Draft limited holding notice → Compliance/Legal approve wording (Treasury drafts; now).** Non-committal only; send nothing if unapproved (S1_TREASURY_PAYMENT_RELEASE_POLICY).
3. **Conditional GO (second Treasury approver; contingent).** Only if all four gates clear pre-cutoff. On present evidence we judge this unlikely today, since rescreen and UBO are both pending (S5_COMPLIANCE_RELEASE_QUEUE_STATUS; S6_CURRENT_DAY_UBO_INTERMEDIARY_ESCALATION).
4. **Release / confirm now (rejected).** Breaches S1 and S5; acts on an undispositioned match (S6).
5. **Rely on supplier attestation to beat cutoff (rejected).** Inverts the screening requirement (S1; S9_WEAK_SUPPLIER_SANCTIONS_ATTESTATION).

## 7. Risks of acting

Releasing or confirming now breaches policy gates (S1_TREASURY_PAYMENT_RELEASE_POLICY) and the standing non-authorization (S5_COMPLIANCE_RELEASE_QUEUE_STATUS), transmitting USD 18,400,000 into a chain whose new intermediary bank is unscreened and whose UBO match is undispositioned (S6_CURRENT_DAY_UBO_INTERMEDIARY_ESCALATION) — irreversible absent bank cancellation (S10_BANK_CUTOFF_AND_HOLD_QUEUE_NOTICE). Secondary: a holding notice that drifts into commitment language becomes de facto confirmation, which S1 allows only post-release or post-approval. Given S10's irreversibility warning, release rights should stay locked until GO triggers are verified by name, so an uploaded-but-held wire is not pushed to "released" under cutoff pressure. Leaning on S9_WEAK_SUPPLIER_SANCTIONS_ATTESTATION substitutes self-serving assurance for required screening and would not survive review.

## 8. Risks of waiting

The sponsor warns of component holds and possible line stoppage, and the supplier states it needs confirmation today to allocate inventory (S8_BUSINESS_SPONSOR_SUPPLIER_URGENCY_NOTE). A hold past the 16:30 ET cutoff likely delays settlement past today's window (S10_BANK_CUTOFF_AND_HOLD_QUEUE_NOTICE). These costs are real and should not be minimized: a missed cutoff can ripple into production and strain a four-year supplier relationship. AP history *suggests*, though the packet does not state, that a counterparty with five clean prior payments above USD 2,000,000 may absorb a short, well-communicated delay (S7_AP_VENDOR_HISTORY_ACTIVE_STATUS). Critically, every waiting cost is asserted by interested parties (sponsor, supplier) and none carries contract default terms or a quantified penalty in the packet. The brief should weigh these costs without treating them as authority to release.

## 9. Recommended next steps and stop/go triggers

**Now (parallel):** (1) Treasury Ops prepares and uploads the wire to hold queue, unreleased (S10_BANK_CUTOFF_AND_HOLD_QUEUE_NOTICE). (2) Treasury drafts a limited holding notice and routes to Compliance/Legal for wording sign-off; do not send until approved (S1_TREASURY_PAYMENT_RELEASE_POLICY). (3) Escalate RQ-8841 to Compliance for expedited disposition (S5_COMPLIANCE_RELEASE_QUEUE_STATUS; S6_CURRENT_DAY_UBO_INTERMEDIARY_ESCALATION).

**GO triggers — release only if ALL are met and evidenced before 16:30 ET:**
- Current-day sanctions rescreen returns clear, including the new intermediary bank in the screened-party set (S6_CURRENT_DAY_UBO_INTERMEDIARY_ESCALATION).
- UBO 82% match dispositioned by a named Compliance reviewer (S6).
- Compliance release issued on RQ-8841 (S5_COMPLIANCE_RELEASE_QUEUE_STATUS).
- Second Treasury approval rec