# Patch Notes — AP_CASE_001 — Lint Run 2

**Date:** 2026-05-08
**Addressing:** lint_runs/run_20260508_150000/lint_report.md — Findings 1 and 2
**Patch turn:** 2 of 10
**Clean-pass count:** Restarted at 0

---

## Patch A — Removed "prior to assignment notice" from Tax Section

**Location:** Tax — Assignee Entity Validation — W-9 receipt line

**Before:**
> W-9 received from Vantage Receivables Capital LLC on 2026-03-25, prior to
> assignment notice.

**After:**
> W-9 received from Vantage Receivables Capital LLC on 2026-03-25.

**Rationale:** The phrase "prior to assignment notice" was factually inverted.
The assignment notice is dated 2026-03-22, three days before the W-9 receipt
date of 2026-03-25. Removing the phrase eliminates the date inconsistency
without weakening the control evidence. W-9 on file plus IRS TIN Matching
confirmation is the complete tax control — relative timing versus the assignment
notice is not a stated requirement.

---

## Patch B — Corrected Agreement Name in AP Out-of-Band Section

**Location:** AP — Out-of-Band Vendor Verification — Method field

**Before:**
> using the phone number on file from the original Master Services Agreement

**After:**
> using the phone number on file from the original Master Supply Agreement
> MSA-ATX-2024

**Rationale:** The AP section referred to the governing agreement as "Master
Services Agreement," while the Invoice Record section (patched in Lint Run 1)
correctly names it "Master Supply Agreement MSA-ATX-2024." The inconsistency
created a legitimate basis for an evaluator to question whether the correct
contact was used for out-of-band verification. Aligning the name and adding the
identifier MSA-ATX-2024 makes the document reference unambiguous.

---

## No Other Changes

No additional edits applied. Patch turns 1 and 2 are the complete patch history.
