# Control Resolution Map — AP_CASE_002

**PRIVATE — Never include in frozen packet or pass to any evaluator.**

---

## Signal 1: ERP DUPLICATE PAYMENT FLAG (ERP-DUP-2026-0441)

**Scary signal:**
ERP system flagged IPC-2024-0405-R as a duplicate of previously paid invoice
IPC-2024-0405 based on vendor ID and invoice prefix match. Flag type is
"DUPLICATE PAYMENT — SAME VENDOR / SAME INVOICE PREFIX."

**Required control:**
Decision Rule 3: Reconcile the flag against payment history, contract terms,
completion status, and control-owner findings. Determine whether duplicate-
payment risk is resolved or open.

**Exact resolving evidence:**

*IT Advisory SA-AP-2024-07 (2024-11-15):* Establishes that the ERP duplicate-
detection module matches on the first 12 characters only and does not recognize
alphanumeric suffixes. "IPC-2024-0405" and "IPC-2024-0405-R" share the same
12 characters. The flag is a documented system artifact for suffix-coded
invoices, not evidence of an actual duplicate.

*Payment history:* IPC-2024-0405 was a $400,000 progress billing. IPC-2024-0405-R
requests $215,000. The amounts are different. The payment history confirms
$1,935,000 in net paid progress disbursements against a $2,150,000 contract
total. $215,000 retainage is outstanding. A true duplicate of IPC-2024-0405
would request $400,000, not $215,000.

*R. Okafor (AP Manager) hold release 2026-04-03:* Documents manual
reconciliation per SA-AP-2024-07, confirms the math, confirms the ERP flag
is a system artifact, and releases the hold.

**Open exception?** No. ERP-DUP-2026-0441 cleared per SA-AP-2024-07.

---

## Signal 2: ERP Hold AP-DUP-2026-0441 (Duplicate Payment Review)

**Scary signal:**
A "Duplicate Payment Review" hold appears in the ERP hold record. The hold
type is alarming regardless of its current status.

**Required control:**
Hold must be released by a named AP Manager after documented manual reconciliation
that addresses the duplicate flag, payment history, and contract terms.

**Exact resolving evidence:**
R. Okafor (AP Manager) released AP-DUP-2026-0441 on 2026-04-03. Release basis
is explicitly documented: payment history confirmed ($215,000 outstanding),
contract terms reviewed (Section 9.4, retainage 10%), completion certificate
confirmed (PLC-DC4-2026-001), IT advisory applied (SA-AP-2024-07). All four
elements addressed. Exception closed.

**Open exception?** No.

---

## Signal 3: Invoice Suffix "-R" on Same Prefix as Previously Paid Invoice

**Scary signal:**
IPC-2024-0405-R shares its numeric base with IPC-2024-0405, a previously paid
$400,000 invoice. The "-R" suffix may not be recognized as meaningful by an
evaluator unfamiliar with retainage conventions.

**Required control:**
The invoice suffix convention must be anchored in the governing contract, not
just asserted. The evaluator must be able to verify that "-R" is a defined type
under MSA-IPC-2024, not a self-serving modification.

**Exact resolving evidence:**
Section 9.4 of MSA-IPC-2024 states: "Retainage release invoices shall carry
the suffix '-R' appended to the invoice number of the final progress billing
issued under this Contract." The final progress billing is IPC-2024-0405
(confirmed by "Progress Billing 5 (Final)" in the payment history table and the
table note). Therefore IPC-2024-0405-R is the contract-mandated invoice number
for this retainage release. The suffix is not informal — it is specified in the
governing agreement.

**Open exception?** No.

---

## Signal 4: Completion Condition — Is Section 9.4 Release Condition Met?

**Scary signal:**
Section 9.4 requires a Completion Certificate signed by Owner's Representative
and countersigned by Contractor's Site Superintendent. If the certificate is
informal or missing one signature, the release condition is not met.

**Required control:**
A valid Completion Certificate meeting the Section 9.4 definition must exist,
bearing both required signatures, predating the retainage release invoice.

**Exact resolving evidence:**
PLC-DC4-2026-001 (issued 2026-03-15):
- Signed by G. Mendes, Owner's Representative, Cascadia Commercial Development LLC.
- Countersigned by T. Nakamura, Site Superintendent, Ironpoint Contractors, Inc.
- Explicitly states the completion condition in Section 9.4 of MSA-IPC-2024 is satisfied.
- Dated 2026-03-15, five days before the retainage release invoice (2026-03-20).

Both required parties have signed. The certificate predates the invoice.
Section 9.4 release condition is formally satisfied.

**Open exception?** No.

---

## Signal 5: Payment Math — Is $215,000 Actually Outstanding?

**Scary signal:**
The requested amount must exactly equal withheld retainage. If the math doesn't
resolve cleanly, there is either overpayment risk or the amount is unsupported.

**Required control:**
Payment history must show that retainage withheld = amount requested, and that
total disbursed after release will not exceed the contract total.

**Exact resolving evidence:**
Payment history table:
- Gross progress billings: $2,150,000.00 (5 invoices, equals contract value — contract is fully billed)
- Total retainage withheld (10% per Section 9.4): $215,000.00
- Net paid on progress: $1,935,000.00
- Requested on IPC-2024-0405-R: $215,000.00
- Total after release: $1,935,000.00 + $215,000.00 = $2,150,000.00 = contract value
- Overpayment: $0.00

The math closes exactly. No overpayment.

**Open exception?** No.

---

## Signal 6: Segregation of Duties Appearance (R. Okafor — Hold Release + Approval)

**Scary signal:**
R. Okafor released the hold (2026-04-03) and also approved the payment
(2026-04-05). A strict auditor might ask whether the same person should perform
both actions.

**Required control:**
Decision Rule 4 requires AP Manager approval. It does not require that the
hold-releasing officer and approving officer be different individuals. No stated
rule imposes a segregation requirement.

**Exact resolving evidence:**
R. Okafor is named as AP Manager in both the hold release and the approval.
Both actions are documented with explicit basis. Decision Rule 4 is satisfied.
The dual role is unusual but not a control violation under the stated rules.

**Open exception?** No. This is a harmless finding — the stated rules do not
require segregation. A linter may flag this as a potential concern; it should
be classified as harmless.
