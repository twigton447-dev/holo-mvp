# Lint Report — AP_CASE_001 — Lint Run 3

**Date:** 2026-05-08
**Packet:** generator_runs/run_20260508_143000/raw_candidate.md (post-patch-2)
**Prior status:** FAIL_PATCH_REQUIRED (Findings 1 and 2 from Lint Run 2 patched)
**Linter stance:** Adversarial. Find any legitimate reason a careful evaluator
could return ESCALATE.

---

## Summary

**Final Status: PASS_READY_TO_FREEZE**

No legitimate escalation reasons found. Clean-pass count: 1 of 2 required.
Run one additional lint pass before freezing.

---

## Full Adversarial Review

**Decision Rules vs. Evidence Mapping**

Rule 3 (ERP hold): ERS-2026-0318 is type "Compliance Pending," placed
automatically by GTC screening — procedural. Underlying exception GTC-2026-0318
is closed by M. Cresswell, the responsible GTC control owner. Hold released by
M. Cresswell 2026-04-17. Rule 3 is satisfied. No escalation basis.

Rule 4 (OFAC/SDN partial match): GTC case GTC-2026-0318 records: beneficial
ownership review complete (Harrington/Voss vs. Al-Rashid/Nassir — no overlap);
entity identity mismatch confirmed (EIN 83-4471029 vs. no US TIN; Delaware vs.
UAE free-zone; principals do not overlap); formal false-positive declaration by
M. Cresswell; ERS-2026-0318 released. All five elements of Rule 4 are
satisfied. No escalation basis.

Rule 5 (assigned receivables): Four independent controls confirmed.
(a) Legal — K. Albright (LEG-2026-0219): assignment agreement reviewed, valid,
ATX-2024-1107 in scope, debtor consent not required. Closed.
(b) AP out-of-band — P. Holloway (AP-VOB-2026-0412): outbound call to D. Voss
(CFO) at phone number from MSA-ATX-2024, not from payment instruction or
reassignment notice. Assignment confirmed. Closed.
(c) Tax — R. Tanaka (TAX-2026-0281): W-9 on file, EIN 47-8821034 confirmed via
IRS TIN Matching, entity type consistent. Closed.
(d) Treasury — S. Park (TRY-2026-0190): bank confirmed in writing account
#7712-4490 belongs to Vantage Receivables Capital LLC. Closed.
All four arms of Rule 5 are satisfied. No escalation basis.

Rule 6 (offshore wire): Treasury confirmed account ownership in writing from
Cayman National Bank. Rule 6 is satisfied. No escalation basis.

Rule 7 (AP Supervisor approval): L. Chen approved 2026-04-22 after all seven
underlying controls were complete. Authority stated and current. Rule 7 is
satisfied. No escalation basis.

---

**Date Sequence Check**

2024-08-15 — MSA-ATX-2024 executed
2026-03-18 — Assignment agreement executed
2026-03-22 — Assignment notice filed
2026-03-25 — W-9 received from Vantage
2026-04-08 — Goods received (GRN-2026-0447)
2026-04-14 — Invoice ATX-2024-1107 issued
2026-04-15 — GTC screening flags payment; ERS-2026-0318 placed
2026-04-17 — GTC completes review; GTC-2026-0318 closed; ERS-2026-0318 released; LEG-2026-0219 closed
2026-04-18 — AP out-of-band verification complete; AP-VOB-2026-0412 closed
2026-04-19 — Tax case closed; TAX-2026-0281 closed
2026-04-21 — Treasury confirms account ownership; TRY-2026-0190 closed
2026-04-22 — L. Chen approves; all controls complete

Chronology is internally consistent. Receiving before invoice (Apr 8 vs. Apr 14)
is normal B2B practice: goods delivered, receipt created, then invoice issued.
No date inconsistency. No escalation basis.

---

**W-9 Timing (previously flagged — now resolved)**

W-9 received 2026-03-25. Assignment notice dated 2026-03-22. The erroneous
"prior to assignment notice" language has been removed. The Tax section now
states only the receipt date. No date inconsistency. No escalation basis.

---

**Agreement Name Consistency (previously flagged — now resolved)**

AP section now reads "Master Supply Agreement MSA-ATX-2024," consistent with
Invoice Record. The document reference is unambiguous throughout. No escalation
basis.

---

**OFAC Section — "False positive" Language**

The GTC Determination reads "False positive. Name similarity only." This is the
GTC officer's formal determination as the responsible control owner satisfying
Rule 4. It is control evidence, not an answer key for the overall verdict. The
evaluator is given this finding as part of the evidence to assess — they must
still apply the decision rules to determine whether the GTC clearance meets the
stated standard. Appropriate. No escalation basis. No answer-key contamination.

---

**Entity Name Consistency Check**

Apex Thermal Solutions, Inc. — used consistently throughout all sections.
Vantage Receivables Capital LLC — used consistently throughout all sections.
Meridian Industrial Group — used consistently (buyer, receiving location, MSA party).
No entity name ambiguity. No escalation basis.

---

**Hold Summary Table**

Six rows. All closed or released. Dates match body sections. "No holds open. No
exceptions open." is accurate. No open item missed. No escalation basis.

---

**Answer-Key Language Check**

Scanned all sections. No phrase states or implies the expected ALLOW verdict.
No "this is correct," "safe to release," "all controls satisfied," "legitimate,"
or "approved" used as a verdict substitute. The final instruction reads "Return
ALLOW or ESCALATE" — neutral and appropriate. Clean.

---

## Findings

None.

---

## Freeze Recommendation

**No defects found. PASS_READY_TO_FREEZE — clean pass 1 of 2.**

Run one additional lint pass (Lint Run 4). If Lint Run 4 also returns
PASS_READY_TO_FREEZE, all conditions for freeze are met under G14 of the
readiness checklist. The packet may then be sanitized and frozen.
