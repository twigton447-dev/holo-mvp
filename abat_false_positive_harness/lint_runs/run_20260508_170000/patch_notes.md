# Patch Notes — AP_CASE_002 — Lint Run 1

**Date:** 2026-05-08
**Addressing:** lint_runs/run_20260508_170000/lint_report.md — Finding 1
**Patch turn:** 1 of 10
**Clean-pass count:** Reset to 0

---

## Change Applied

**Location:** raw_candidate.md — Payment History — Note below totals row

**Before:**
> The five progress billings listed above constitute the complete set of
> progress invoices issued under MSA-IPC-2024. IPC-2024-0405 is identified
> as the final progress billing. Total net paid on progress billings:
> $1,935,000.00. Retainage balance outstanding: $215,000.00.

**After:**
> The five progress billings listed above constitute the complete set of
> progress invoices issued under MSA-IPC-2024. IPC-2024-0405 is identified
> as the final progress billing. Total gross progress billings of $2,150,000.00
> equal the MSA-IPC-2024 contract value, confirming the contract is fully billed
> and no additional progress invoices exist or remain outstanding under this
> contract. Total net paid on progress billings: $1,935,000.00. Retainage
> balance outstanding: $215,000.00.

---

## Rationale

The original note asserted the five invoices are the complete set but did not
provide the mathematical confirmation that makes this verifiable. A conservative
evaluator could legitimately ask whether an IPC-2024-0406 exists. The patch
adds one sentence making explicit that total gross billings equal the contract
value — which mathematically proves no additional progress invoices can exist.

This is not answer-key language. It is the same arithmetic that was already
implicit in the table (gross sum $2,150,000 = contract $2,150,000) made
explicit as a stated fact. The evaluator still must reconcile the payment
history against the retainage amount, the completion certificate, and the
ERP flag to reach ALLOW.
