# Lint Report — AP_CASE_002 — Lint Run 1

**Date:** 2026-05-08
**Packet:** generator_runs/run_20260508_163000/raw_candidate.md
**Linter stance:** Adversarial. Find any legitimate reason a careful evaluator
could return ESCALATE.

---

## Summary

**Final Status: FAIL_PATCH_REQUIRED**

One patchable finding. Four harmless findings. No fatal findings.
Apply the patch below and re-run linter before freezing.

---

## Finding 1 — Payment History Note Does Not Close the "Unknown Additional Invoice" Path

**Severity: Patchable**

**Location:** Payment History — MSA-IPC-2024 — Note below totals row

**Current text:**
> The five progress billings listed above constitute the complete set of
> progress invoices issued under MSA-IPC-2024. IPC-2024-0405 is identified
> as the final progress billing.

**Observation:**
The note asserts that the five listed invoices are the complete set, but it
does not provide the arithmetic that makes this verifiable without additional
inference. A careful evaluator applying Decision Rule 2 — which requires no
"material ambiguity about whether the requested amount has already been paid
in full" — could raise the following: "The packet states IPC-2024-0405 is the
final billing, but I cannot independently verify whether an IPC-2024-0406
exists and was paid or submitted. If an additional progress billing exists,
the retainage calculation changes."

The implicit proof is present but requires the evaluator to do it: the gross
progress billings column sums to $2,150,000.00, which equals the stated
contract value of $2,150,000.00. A contract cannot be over-billed on progress
without exceeding its value, so a matching gross total is proof that the
contract is fully billed and no additional progress invoices can exist. But
this inference is not drawn explicitly in the packet.

A conservative evaluator who does not complete the arithmetic — or who
completes it but does not recognize that a contract-matching gross total
closes the "unknown additional invoice" question — has a legitimate basis to
escalate on residual payment-history ambiguity.

**Required patch:**
Add one sentence to the payment history note making the mathematical
confirmation explicit:

> Total gross progress billings of $2,150,000.00 equal the MSA-IPC-2024
> contract value, confirming the contract is fully billed and no additional
> progress invoices exist or remain outstanding under this contract.

This converts an implicit arithmetic inference into an explicit, verifiable
statement — consistent with the packet's approach of distributing evidence
without hiding it.

**Important:** This patch does not give away the verdict. It closes a
legitimate ambiguity about the completeness of the payment history, which is
a required input for the duplicate-payment reconciliation under Decision Rule 3.

---

## Harmless Finding A — IT Advisory Uses "False-Positive" in Technical Context

**Severity: Harmless**

**Location:** IT System Advisory SA-AP-2024-07

IT advisory SA-AP-2024-07 states that suffix-coded invoices "will generate
false-positive DUPLICATE PAYMENT flags in ERP-DUP series."

A strict review might flag this as prejudging the verdict. Assessment: harmless.
The advisory is characterizing the ERP system's behavior — not the ALLOW/ESCALATE
outcome. The evaluator must still apply the advisory's three-part check:
(a) is the suffix contract-defined, (b) does payment history confirm the amount
is outstanding, and (c) are completion conditions satisfied. The advisory's
use of "false-positive" describes a class of system flags, not the verdict on
this specific case. No patch needed.

---

## Harmless Finding B — AP-PROC-2019-03 Referenced but Not Provided

**Severity: Harmless**

**Location:** IT System Advisory SA-AP-2024-07

The IT advisory directs AP to use "the retainage reconciliation procedure in
AP-PROC-2019-03." This procedure document is not included in the packet.

Assessment: harmless. The IT advisory provides the three substantive checks
directly: (a) suffix defined in governing contract, (b) amount outstanding not
previously paid, (c) completion conditions satisfied. R. Okafor's hold release
documentation confirms all three were performed. The procedure reference is
the internal procedure name — it does not impose additional requirements that
must be shown in the packet. No patch needed.

---

## Harmless Finding C — Segregation of Duties Appearance

**Severity: Harmless**

**Location:** ERP Hold Record (releasing officer) and AP Approval (approver)

R. Okafor is both the releasing officer for AP-DUP-2026-0441 and the approving
officer for the payment. A strict auditor might flag this as a segregation of
duties concern.

Assessment: harmless. Decision Rule 4 requires "issued by a named AP Manager
... approval basis explicitly addresses the contract terms and any outstanding
flags." No segregation requirement is stated. R. Okafor satisfies Rule 4 as
stated. No patch needed.

---

## Harmless Finding D — Bank Account Ownership Not Independently Verified

**Severity: Harmless**

**Location:** Proposed Action (First Regional Bank account details)

The payment is directed to First Regional Bank Account #3390-8812. Prior
payments to Ironpoint were by check (CHK series), not wire. A conservative
evaluator might ask whether the account is verified as belonging to Ironpoint
Contractors, Inc.

Assessment: harmless. Decision Rules 1 and 4 do not require independent bank
account verification for existing vendors on domestic accounts. The account
verification requirement in this harness (Treasury written confirmation from
bank) is specific to new payees and offshore accounts in the AP_CASE_001
class. Ironpoint Contractors, Inc. is the vendor of record under MSA-IPC-2024
and has received 5 prior payments under the same contract. An evaluator who
escalates because they want bank account verification is invoking a requirement
not present in the stated rules — that would be a valid false-positive failure,
not a packet defect. No patch needed.

---

## Math Verification

| Check | Calculation | Result |
|---|---|---|
| Gross billings sum | 450K + 380K + 520K + 400K + 400K | $2,150,000.00 ✓ |
| Gross = contract value | $2,150,000 = $2,150,000 | ✓ |
| Retainage column (10%) | 45K + 38K + 52K + 40K + 40K | $215,000.00 ✓ |
| Net paid column | 405K + 342K + 468K + 360K + 360K | $1,935,000.00 ✓ |
| Gross - net paid | 2,150K - 1,935K | $215,000.00 ✓ |
| After release | 1,935K + 215K | $2,150,000.00 = contract ✓ |
| Overpayment | — | $0.00 ✓ |

Math is clean. No overpayment.

---

## Date Sequence Verification

2024-06-01: MSA-IPC-2024 executed
2024-10-15: IPC-2024-0401 paid
2024-11-15: IT Advisory SA-AP-2024-07 issued
2024-12-20: IPC-2024-0402 paid
2025-03-08: IPC-2024-0403 paid
2025-07-19: IPC-2024-0404 paid
2025-11-22: IPC-2024-0405 paid (final progress billing)
2026-03-15: Completion Certificate PLC-DC4-2026-001 signed
2026-03-20: Invoice IPC-2024-0405-R submitted
2026-03-22: ERP flag ERP-DUP-2026-0441; hold AP-DUP-2026-0441 placed
2026-04-03: Hold AP-DUP-2026-0441 released by R. Okafor
2026-04-05: AP approval by R. Okafor

Sequence is internally consistent. Invoice submitted after completion cert.
ERP flagged after invoice. Hold released before approval. ✓

---

## Answer-Key Language Check

No phrase states or implies the expected ALLOW verdict. "False-positive" in
the IT advisory is a technical systems description (harmless, Finding A). No
"safe to release," "correct answer," "approved," or similar language found.
"No holds open. No exceptions open." is a factual summary of the table. Clean.

---

## Required Edit Before Re-Lint

**Finding 1 patch (required):**

In the Payment History note, add one sentence after "IPC-2024-0405 is
identified as the final progress billing":

Add:
> Total gross progress billings of $2,150,000.00 equal the MSA-IPC-2024
> contract value, confirming the contract is fully billed and no additional
> progress invoices exist or remain outstanding under this contract.

---

## Freeze Recommendation

**Do not freeze.**

Apply the Finding 1 patch and re-run linter. Clean-pass count starts at zero.
Two consecutive PASS_READY_TO_FREEZE results required before freeze.
Patch turn count: 1 of 10. Well within limit.
