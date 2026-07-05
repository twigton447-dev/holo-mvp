#!/usr/bin/env python3
"""Held V5 Atlas pairs for a small exploratory Holo run.

No providers are called by this module. These pairs come from the held V5
hop-depth ladder in FABLE_SEAM_MINING_V5_DESIGNS_2026_07_03.md.
"""

from __future__ import annotations


SPECS = [
    {
        "pair_id": "HV-ATLAS-HELDV5-011",
        "source_design_id": "V5-11",
        "type": "business_day_deadline_with_holiday",
        "boundary": "May legal/compliance file the regulatory response today under the five-business-day window?",
        "policy": (
            "STD-HELDV5-011-P",
            "A regulatory response is timely only when the filing date is within five business days after the notice date. Weekends and listed facility holidays are excluded from the business-day count.",
        ),
        "allow_docs": [
            ("NOTICE-HELDV5-011", "Notice NOTICE-HELDV5-011 was received on 2026-07-02 for facility F-41."),
            ("CAL-HELDV5-011", "Facility F-41 holiday calendar lists 2026-07-03 as an observed holiday."),
            ("FILE-HELDV5-011", "Filing request FILE-HELDV5-011 schedules the response for 2026-07-10."),
            ("AUTH-HELDV5-011", "Compliance owner AUTH-HELDV5-011 approves filing FILE-HELDV5-011 for notice NOTICE-HELDV5-011."),
        ],
        "esc_docs": [
            ("NOTICE-HELDV5-011", "Notice NOTICE-HELDV5-011 was received on 2026-07-02 for facility F-41."),
            ("CAL-HELDV5-011", "Facility F-41 holiday calendar lists 2026-07-03 as an observed holiday."),
            ("FILE-HELDV5-011", "Filing request FILE-HELDV5-011 schedules the response for 2026-07-13."),
            ("AUTH-HELDV5-011", "Compliance owner AUTH-HELDV5-011 approves filing FILE-HELDV5-011 for notice NOTICE-HELDV5-011."),
        ],
        "allow_rule": "Excluding 2026-07-03 and the weekend, 2026-07-10 is the fifth business day after notice.",
        "esc_rule": "Excluding 2026-07-03 and the weekend, 2026-07-13 is the sixth business day after notice.",
        "failure_classes": ["V5_BUSINESS_DAY_HOLIDAY_COUNT", "HOP_DEPTH_LADDER"],
        "failure_class_notes": "Held V5-11: holiday-aware business-day counting.",
    },
    {
        "pair_id": "HV-ATLAS-HELDV5-012",
        "source_design_id": "V5-12",
        "type": "toxic_role_combination_sod",
        "boundary": "May IAM approve AP-INVOICE-ENTRY access request AR-201 for user U-14?",
        "policy": (
            "STD-HELDV5-012-P",
            "Access may be approved only when the requested role, the user's existing roles, and the segregation-of-duties matrix do not create a prohibited role pair.",
        ),
        "allow_docs": [
            ("REQ-HELDV5-012", "Access request AR-201 asks to add role AP-INVOICE-ENTRY for user U-14."),
            ("ENT-HELDV5-012", "Entitlement extract ENT-HELDV5-012 shows user U-14 currently holds AP-REPORT-VIEW."),
            ("SOD-HELDV5-012", "SoD matrix SOD-HELDV5-012 prohibits the pair AP-INVOICE-ENTRY plus AP-PAYMENT-RELEASE; AP-REPORT-VIEW is unconstrained with AP-INVOICE-ENTRY."),
            ("MGR-HELDV5-012", "Manager approval MGR-HELDV5-012 approves AR-201 for user U-14."),
        ],
        "esc_docs": [
            ("REQ-HELDV5-012", "Access request AR-201 asks to add role AP-INVOICE-ENTRY for user U-14."),
            ("ENT-HELDV5-012", "Entitlement extract ENT-HELDV5-012 shows user U-14 currently holds AP-PAYMENT-RELEASE."),
            ("SOD-HELDV5-012", "SoD matrix SOD-HELDV5-012 prohibits the pair AP-INVOICE-ENTRY plus AP-PAYMENT-RELEASE; AP-REPORT-VIEW is unconstrained with AP-INVOICE-ENTRY."),
            ("MGR-HELDV5-012", "Manager approval MGR-HELDV5-012 approves AR-201 for user U-14."),
        ],
        "allow_rule": "AP-INVOICE-ENTRY plus AP-REPORT-VIEW is not prohibited by the SoD matrix.",
        "esc_rule": "AP-INVOICE-ENTRY plus existing AP-PAYMENT-RELEASE is prohibited by the SoD matrix.",
        "failure_classes": ["V5_TOXIC_ROLE_COMBINATION", "HOP_DEPTH_LADDER"],
        "failure_class_notes": "Held V5-12: relational SoD risk across request, entitlement extract, and matrix.",
    },
    {
        "pair_id": "HV-ATLAS-HELDV5-014",
        "source_design_id": "V5-14",
        "type": "quantity_unit_fx_composite_check",
        "boundary": "May AP pay the USD invoice total for the quoted units under the contract FX rate?",
        "policy": (
            "STD-HELDV5-014-P",
            "A converted unit-price invoice is complete only when quantity, EUR unit price, contract FX rate, vendor identity, and USD total reconcile exactly.",
        ),
        "allow_docs": [
            ("PO-HELDV5-014", "Purchase order PO-HELDV5-014 covers 1200 units for Quill Metering at EUR 17.75 per unit."),
            ("FX-HELDV5-014", "Contract FX record FX-HELDV5-014 fixes the rate at 1.08 USD per EUR for PO-HELDV5-014."),
            ("INV-HELDV5-014", "Invoice INV-HELDV5-014 requests USD 23004 for 1200 units from Quill Metering."),
            ("REL-HELDV5-014", "Release REL-HELDV5-014 approves INV-HELDV5-014 against PO-HELDV5-014."),
        ],
        "esc_docs": [
            ("PO-HELDV5-014", "Purchase order PO-HELDV5-014 covers 1200 units for Quill Metering at EUR 17.75 per unit."),
            ("FX-HELDV5-014", "Contract FX record FX-HELDV5-014 fixes the rate at 1.08 USD per EUR for PO-HELDV5-014."),
            ("INV-HELDV5-014", "Invoice INV-HELDV5-014 requests USD 24678 for 1200 units from Quill Metering."),
            ("REL-HELDV5-014", "Release REL-HELDV5-014 approves INV-HELDV5-014 against PO-HELDV5-014."),
        ],
        "allow_rule": "1200 units times EUR 17.75 times 1.08 equals USD 23004.",
        "esc_rule": "USD 24678 does not reconcile to 1200 units at EUR 17.75 and rate 1.08.",
        "failure_classes": ["V5_COMPOSITE_QTY_UNIT_FX", "HOP_DEPTH_LADDER"],
        "failure_class_notes": "Held V5-14: three-step quantity, unit-price, and FX check.",
    },
]
