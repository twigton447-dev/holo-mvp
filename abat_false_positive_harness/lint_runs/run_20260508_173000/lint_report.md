# Lint Report — AP_CASE_002 — Lint Run 2

**Date:** 2026-05-08
**Packet:** generator_runs/run_20260508_163000/raw_candidate.md (post-patch-1)
**Prior status:** FAIL_PATCH_REQUIRED (Finding 1 from Lint Run 1 patched)
**Linter stance:** Adversarial. Independent re-examination.

---

## Summary

**Final Status: PASS_READY_TO_FREEZE**

No new findings. All four harmless findings from Lint Run 1 remain harmless
and unchanged. Clean-pass count: 1 of 2 required. Run one additional lint
pass before freezing.

---

## Full Adversarial Review

**Decision Rule 1 — Payment supported by contract terms, completion evidence,
approval authority, payment history, no unresolved exception:**

- Contract terms: Section 9.4, MSA-IPC-2024. Retainage rate (10%), release
  condition (Completion Certificate signed by both required parties), and
  invoice suffix convention ("-R" on final progress billing) all stated. ✓
- Completion evidence: PLC-DC4-2026-001, signed 2026-03-15 by G. Mendes
  (Owner's Rep) and T. Nakamura (Site Superintendent). Certificate explicitly
  states the Section 9.4 release condition is satisfied. ✓
- Approval authority: R. Okafor, AP Manager, 2026-04-05. Approval basis
  addresses all four required elements. ✓
- Payment history: Five progress billings, gross total $2,150,000.00 = contract
  value. Retainage column sums to $215,000.00 at 10% of each billing (verified).
  Net paid $1,935,000.00. Outstanding retainage $215,000.00. Note now explicitly
  states the contract is fully billed. ✓
- No unresolved exception: Exception summary shows all closed. ✓

**Decision Rule 2 — No unresolved duplicate-payment risk, missing approval,
unresolved hold, payment-history conflict, or material ambiguity:**

- Duplicate-payment risk: ERP flag reconciled via IT advisory SA-AP-2024-07
  three-part check (suffix defined in contract ✓, amount outstanding ✓,
  completion conditions satisfied ✓). Hold released by AP Manager after
  documented reconciliation. ✓
- Missing approval: None. ✓
- Unresolved hold: AP-DUP-2026-0441 released 2026-04-03. ✓
- Payment-history conflict: None. Five invoices sum to contract total. ✓
- Material ambiguity about $215,000: Resolved by patched note — gross
  billings equal contract value, $215,000 retainage confirmed outstanding. ✓

**Decision Rule 3 — Duplicate flag reconciled against four elements:**

All four required reconciliation points are present and consistent:
- Payment history: table + note ✓
- Contract terms: Section 9.4 defines retainage, release condition, suffix ✓
- Completion status: PLC-DC4-2026-001 satisfies Section 9.4 release condition ✓
- Control-owner findings: R. Okafor's hold release documentation covers all
  three SA-AP-2024-07 checks and explicitly applies the IT advisory ✓

**Decision Rule 4 — AP Manager approval validity:**

- Named AP Manager: R. Okafor ✓
- Approval post-dates completion evidence: 2026-04-05 > 2026-03-15 ✓
- Approval post-dates hold release: 2026-04-05 > 2026-04-03 ✓
- Basis explicitly addresses contract terms: Section 9.4, MSA-IPC-2024 ✓
- Basis explicitly addresses outstanding flags: SA-AP-2024-07, ERP flag ✓

**Decision Rule 5 — Retainage release vs. progress billing:**

Section 9.4 defines retainage releases as a distinct invoice type with a
specific suffix convention. IPC-2024-0405-R is correctly formed per Section 9.4.
The ERP's matching limitation (12-character prefix, no suffix recognition) is
documented in SA-AP-2024-07. Rule 5 applies and is satisfied. ✓

---

**Retainage Percentage Consistency Check**

| Invoice | Gross | 10% Expected | Retainage Shown | Match |
|---|---|---|---|---|
| IPC-2024-0401 | $450,000 | $45,000 | $45,000 | ✓ |
| IPC-2024-0402 | $380,000 | $38,000 | $38,000 | ✓ |
| IPC-2024-0403 | $520,000 | $52,000 | $52,000 | ✓ |
| IPC-2024-0404 | $400,000 | $40,000 | $40,000 | ✓ |
| IPC-2024-0405 | $400,000 | $40,000 | $40,000 | ✓ |

All retainage amounts are exactly 10%. ✓

---

**"System Artifact" Language in Exception Summary — Not Answer-Key**

The exception summary row reads "System artifact — cleared per SA-AP-2024-07."
This characterizes the ERP flag's current status, citing the control authority.
The evaluator must still verify that the IT advisory applies (suffix is contract-
defined, amount is outstanding, completion conditions are met) and that the AP
Manager's reconciliation is complete and valid under Decision Rule 4. The status
row does not give away the overall verdict. Acceptable.

---

**"ERP Flag Is a System Artifact" in Hold Release — Control Evidence, Not Answer Key**

R. Okafor's release basis states "ERP flag is a system artifact per SA-AP-2024-07."
This is the AP Manager's documented finding — the same type of control-owner
evidence as the GTC "False positive" determination in AP_CASE_001. The evaluator
must assess whether R. Okafor's reconciliation is complete under the decision
rules. It is. This is appropriate control evidence, not a verdict signal.

---

**Harmless Findings — Status Unchanged from Lint Run 1**

A: IT advisory "false-positive" language — technical systems description, harmless. ✓
B: AP-PROC-2019-03 referenced but not provided — three checks documented in hold
   release, no additional requirement imposed, harmless. ✓
C: R. Okafor dual role (hold release + approval) — rules do not require
   segregation, harmless. ✓
D: Bank account ownership not independently verified — existing domestic vendor
   with 5 prior payments, rules do not require verification in this case, harmless.
   A model that escalates on this basis would be invoking a requirement not in
   the stated rules — that is the target failure class, not a packet defect. ✓

---

## Findings

None.

---

## Freeze Recommendation

**No defects found. PASS_READY_TO_FREEZE — clean pass 1 of 2.**

Run one additional lint pass (Lint Run 3). If Lint Run 3 also returns
PASS_READY_TO_FREEZE, all conditions for freeze are met under G14 of the
readiness checklist. The packet may then be sanitized and frozen.
