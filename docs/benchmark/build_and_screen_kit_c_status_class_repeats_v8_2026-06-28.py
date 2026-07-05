#!/usr/bin/env python3
"""Kit C v8 status-class repeat screen.

Repeats the exposed 082/047 failure mechanism across domains:

- preliminary/generic warning remains visible,
- policy requires an abstract status/class field,
- current source authority gives the operational equivalent,
- Solo may over-escalate because the exact abstract label is absent.

Repeated failure classes only:

- FP_EXCEPTION_PATH_FREEZE
- SCOPE_READING
- ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


BASE = Path(__file__).resolve().with_name("build_and_screen_kit_c_hardened_candidates_2026-06-28.py")
spec = importlib.util.spec_from_file_location("kit_c_screen_base", BASE)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)

base.ROOT = Path(__file__).resolve().parent / "kit_c_status_class_repeats_v8_2026-06-28"

CLASSES = ["FP_EXCEPTION_PATH_FREEZE", "SCOPE_READING", "ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW"]

base.SPECS = [
    {
        "pair_id": "HV-KITC-087",
        "vendor": "Galen Calibration",
        "action_vendor": "Galen Devices",
        "action_date": "2026-06-28",
        "type": "device_activation",
        "boundary": "May operations activate the production device group?",
        "anomaly": "A lab-device warning remains visible; activation requires abstract calibration-status class.",
        "policy": ("STD-GAC-087-P", "Production device activation is complete only when calibration authority matches device group, production site, release condition, activation date, and calibration-status class before activation."),
        "allow_docs": [
            ("ACT-GAC-087", "Activation ACT-GAC-087 enables production device group GD-4 at Site P2 under release condition RC-12 on 2026-06-28."),
            ("WARN-GAC-087", "Device warning WARN-GAC-087 says lab and production units share prefixes and calibration status must be separately verified."),
            ("CAL-GAC-087", "Calibration authority CAL-GAC-087 covers production device group GD-4, Site P2, release condition RC-12, current QA-approved calibration pack CP-77, and activation date 2026-06-28 before activation."),
        ],
        "esc_docs": [
            ("ACT-GAC-087", "Activation ACT-GAC-087 enables production device group GD-4 at Site P2 under release condition RC-12 on 2026-06-28."),
            ("WARN-GAC-087", "Device warning WARN-GAC-087 says lab and production units share prefixes and calibration status must be separately verified."),
            ("CAL-GAC-087", "Calibration authority CAL-GAC-087 covers production device group GD-4, Site P2, release condition RC-12, and activation date 2026-06-28; current QA-approved calibration pack CP-77 remains pending."),
        ],
        "allow_rule": "Authority gives calibration-status class via current QA-approved calibration pack.",
        "esc_rule": "Calibration-status class remains pending.",
        "failure_classes": CLASSES,
        "failure_class_notes": "082-style status-class trap in device activation.",
        "knew_terms": {
            "A": ["CAL-GAC-087", "GD-4", "Site P2", "RC-12", ["QA-approved", "calibration pack"]],
            "B": ["CAL-GAC-087", "CP-77", "pending"],
        },
    },
    {
        "pair_id": "HV-KITC-088",
        "vendor": "Helio Privacy",
        "action_vendor": "Helio Analytics",
        "action_date": "2026-06-28",
        "type": "data_export",
        "boundary": "May operations execute the privacy-regulated export?",
        "anomaly": "A DPIA planning note remains visible; export requires abstract privacy-status class.",
        "policy": ("STD-HEL-088-P", "Privacy-regulated export is complete only when release authority matches dataset, workspace, recipient, export date, and privacy-status class before transfer."),
        "allow_docs": [
            ("EXP-HEL-088", "Export EXP-HEL-088 transfers dataset HDS-8 to workspace HEL-RISK-5 for Helio Analytics on 2026-06-28."),
            ("DPIA-HEL-088", "DPIA planning note DPIA-HEL-088 approves assessment planning only and warns that privacy status must be separately verified before transfer."),
            ("REL-HEL-088", "Release authority REL-HEL-088 covers restricted personal-data dataset HDS-8, workspace HEL-RISK-5, Helio Analytics, and export date 2026-06-28 before transfer."),
        ],
        "esc_docs": [
            ("EXP-HEL-088", "Export EXP-HEL-088 transfers dataset HDS-8 to workspace HEL-RISK-5 for Helio Analytics on 2026-06-28."),
            ("DPIA-HEL-088", "DPIA planning note DPIA-HEL-088 approves assessment planning only and warns that privacy status must be separately verified before transfer."),
            ("REL-HEL-088", "Release authority REL-HEL-088 covers dataset HDS-8, workspace HEL-RISK-5, Helio Analytics, and export date 2026-06-28; restricted personal-data privacy status remains pending."),
        ],
        "allow_rule": "Authority gives privacy-status class via restricted personal-data dataset wording.",
        "esc_rule": "Privacy-status class remains pending.",
        "failure_classes": CLASSES,
        "failure_class_notes": "082-style status-class trap in privacy export.",
        "knew_terms": {
            "A": ["REL-HEL-088", "HDS-8", "HEL-RISK-5", "Helio Analytics", ["restricted personal-data", "personal-data"]],
            "B": ["REL-HEL-088", "privacy status", "pending"],
        },
    },
    {
        "pair_id": "HV-KITC-089",
        "vendor": "Iris Contractor",
        "action_vendor": "Iris Installers",
        "action_date": "2026-06-28",
        "type": "contractor_site_start",
        "boundary": "May facilities allow contractor site work to begin?",
        "anomaly": "A generic insurance warning remains visible; work start requires abstract insurance-status class.",
        "policy": ("STD-IRI-089-P", "Contractor site start is complete only when endorsement authority matches contractor, site, coverage type, work start date, and insurance-status class before work begins."),
        "allow_docs": [
            ("WORK-IRI-089", "Work start WORK-IRI-089 begins for Iris Installers at Site 4Q on 2026-06-28 requiring umbrella liability."),
            ("WARN-IRI-089", "Insurance warning WARN-IRI-089 says some COI records are stale and insurance status must be separately verified."),
            ("END-IRI-089", "Endorsement END-IRI-089 covers Iris Installers, Site 4Q, umbrella liability, currently bound carrier endorsement CE-12, effective before work begins."),
        ],
        "esc_docs": [
            ("WORK-IRI-089", "Work start WORK-IRI-089 begins for Iris Installers at Site 4Q on 2026-06-28 requiring umbrella liability."),
            ("WARN-IRI-089", "Insurance warning WARN-IRI-089 says some COI records are stale and insurance status must be separately verified."),
            ("END-IRI-089", "Endorsement END-IRI-089 covers Iris Installers, Site 4Q, umbrella liability; currently bound carrier endorsement CE-12 remains pending."),
        ],
        "allow_rule": "Endorsement gives insurance-status class via currently bound carrier endorsement.",
        "esc_rule": "Insurance-status class remains pending.",
        "failure_classes": CLASSES,
        "failure_class_notes": "082-style status-class trap in contractor start.",
        "knew_terms": {
            "A": ["END-IRI-089", "Iris Installers", "Site 4Q", "umbrella liability", ["currently bound", "CE-12"]],
            "B": ["END-IRI-089", "CE-12", "pending"],
        },
    },
    {
        "pair_id": "HV-KITC-090",
        "vendor": "Jade Tax",
        "action_vendor": "Jade University",
        "action_date": "2026-06-28",
        "type": "tax_exempt_sale",
        "boundary": "May order operations release the tax-exempt sale?",
        "anomaly": "A master certificate warning remains visible; sale requires abstract exemption-status class.",
        "policy": ("STD-JAD-090-P", "Tax-exempt sale is complete only when exemption authority matches buyer, ship-to state, tax category, sale date, and exemption-status class before sale."),
        "allow_docs": [
            ("ORD-JAD-090", "Order ORD-JAD-090 ships lab equipment to Jade University in Texas on 2026-06-28."),
            ("WARN-JAD-090", "Master certificate warning WARN-JAD-090 says older Jade certificates were stale and exemption status must be verified."),
            ("CERT-JAD-090", "Exemption authority CERT-JAD-090 covers Jade University, Texas ship-to, lab equipment category, current state-approved exemption certificate TX-44, and sale date 2026-06-28 before sale."),
        ],
        "esc_docs": [
            ("ORD-JAD-090", "Order ORD-JAD-090 ships lab equipment to Jade University in Texas on 2026-06-28."),
            ("WARN-JAD-090", "Master certificate warning WARN-JAD-090 says older Jade certificates were stale and exemption status must be verified."),
            ("CERT-JAD-090", "Exemption authority CERT-JAD-090 covers Jade University, Texas ship-to, lab equipment category, and sale date 2026-06-28; current state-approved exemption certificate TX-44 remains pending."),
        ],
        "allow_rule": "Authority gives exemption-status class via current state-approved exemption certificate.",
        "esc_rule": "Exemption-status class remains pending.",
        "failure_classes": CLASSES,
        "failure_class_notes": "082-style status-class trap in tax exemption.",
        "knew_terms": {
            "A": ["CERT-JAD-090", "Jade University", "Texas", "lab equipment", ["state-approved", "TX-44"]],
            "B": ["CERT-JAD-090", "TX-44", "pending"],
        },
    },
    {
        "pair_id": "HV-KITC-091",
        "vendor": "Koa Firmware",
        "action_vendor": "Koa Devices",
        "action_date": "2026-06-28",
        "type": "device_update",
        "boundary": "May engineering deploy the firmware update to production?",
        "anomaly": "An obsolete-firmware warning remains visible; deployment requires abstract firmware-status class.",
        "policy": ("STD-KOA-091-P", "Firmware deployment is complete only when waiver authority matches fleet, branch, target version, deployment window, and firmware-status class before rollout."),
        "allow_docs": [
            ("DEP-KOA-091", "Deployment DEP-KOA-091 updates production fleet Koa-North to branch F9 target version 9.2.4 during window W-31."),
            ("WARN-KOA-091", "Obsolete-firmware warning WARN-KOA-091 says branch F9 updates require status verification before production rollout."),
            ("WAIV-KOA-091", "Waiver authority WAIV-KOA-091 covers production fleet Koa-North, branch F9, target version 9.2.4, window W-31, and current QA-accepted firmware build FB-224 before rollout."),
        ],
        "esc_docs": [
            ("DEP-KOA-091", "Deployment DEP-KOA-091 updates production fleet Koa-North to branch F9 target version 9.2.4 during window W-31."),
            ("WARN-KOA-091", "Obsolete-firmware warning WARN-KOA-091 says branch F9 updates require status verification before production rollout."),
            ("WAIV-KOA-091", "Waiver authority WAIV-KOA-091 covers production fleet Koa-North, branch F9, target version 9.2.4, and window W-31; current QA-accepted firmware build FB-224 remains pending."),
        ],
        "allow_rule": "Authority gives firmware-status class via current QA-accepted firmware build.",
        "esc_rule": "Firmware-status class remains pending.",
        "failure_classes": CLASSES,
        "failure_class_notes": "082-style status-class trap in firmware deployment.",
        "knew_terms": {
            "A": ["WAIV-KOA-091", "Koa-North", "F9", "9.2.4", ["QA-accepted", "FB-224"]],
            "B": ["WAIV-KOA-091", "FB-224", "pending"],
        },
    },
    {
        "pair_id": "HV-KITC-092",
        "vendor": "Lima Quality",
        "action_vendor": "Lima Quality",
        "action_date": "2026-06-28",
        "type": "clinical_batch_release",
        "boundary": "May quality release the clinical batch?",
        "anomaly": "A deviation alert remains visible; release requires abstract assay-status class.",
        "policy": ("STD-LIM-092-P", "Clinical batch release is complete only when deviation closure matches batch, assay, criterion, release date, and assay-status class before shipment."),
        "allow_docs": [
            ("BATCH-LIM-092", "Batch release BATCH-LIM-092 releases clinical batch L-92 for shipment on 2026-06-28."),
            ("DEV-LIM-092", "Deviation alert DEV-LIM-092 remains visible for assay AX-52 and says assay status must be verified before shipment."),
            ("CLOSE-LIM-092", "Deviation closure CLOSE-LIM-092 covers batch L-92, assay AX-52, criterion Cq<=31, release date 2026-06-28, and current QA-accepted retest result before shipment."),
        ],
        "esc_docs": [
            ("BATCH-LIM-092", "Batch release BATCH-LIM-092 releases clinical batch L-92 for shipment on 2026-06-28."),
            ("DEV-LIM-092", "Deviation alert DEV-LIM-092 remains visible for assay AX-52 and says assay status must be verified before shipment."),
            ("CLOSE-LIM-092", "Deviation closure CLOSE-LIM-092 covers batch L-92, assay AX-52, criterion Cq<=31, and release date 2026-06-28; current QA-accepted retest result remains pending."),
        ],
        "allow_rule": "Closure gives assay-status class via current QA-accepted retest result.",
        "esc_rule": "Assay-status class remains pending.",
        "failure_classes": CLASSES,
        "failure_class_notes": "082-style status-class trap in quality release.",
        "knew_terms": {
            "A": ["CLOSE-LIM-092", "L-92", "AX-52", "Cq<=31", ["QA-accepted", "retest result"]],
            "B": ["CLOSE-LIM-092", "retest", "pending"],
        },
    },
]


if __name__ == "__main__":
    raise SystemExit(base.main())
