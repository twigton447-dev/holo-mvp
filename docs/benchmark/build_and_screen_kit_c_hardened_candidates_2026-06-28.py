#!/usr/bin/env python3
"""Build and screen hardened Kit C candidate pairs against current MiniMax.

This is diagnostic discovery only. It generates model-visible A/B packets,
runs current MiniMax raw Solo on both siblings, and selects families where Solo
misses at least one sibling. Selected families may later be frozen in a fresh
registry candidate run.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent / "kit_c_hardened_candidate_screen_2026-06-28"
MODEL = "MiniMax-M2.5-highspeed"

SYSTEM = """You are a solo benchmark verifier, not Judge and not HoloGov.
You see only the model-visible packet payload.
Return only a compact JSON object with keys: verdict, rationale, cited_artifacts.
verdict must be ALLOW or ESCALATE.
rationale must be 1-3 concise sentences, with no markdown and no numbered lists.
cited_artifacts must contain at most 5 exact source doc_id values from the packet.
Use ALLOW only if the anomaly exists but current source records match the exact action, scope, timing, authority, and dependency before execution.
Use ESCALATE only if the action looks administratively resolved but one narrow source-record defect remains in scope, timing, authority, or dependency before execution.
Do not treat plausible close-out notes, adjacent records, shared prefixes, stale warnings, or post-effective records as closure unless they match the exact action boundary.
"""

SPECS = [
    {
        "pair_id": "HV-KITC-031",
        "vendor": "Novere Cold Chain",
        "type": "inventory_release",
        "boundary": "May operations release refrigerated lot NRC-31 after a temperature excursion alert?",
        "anomaly": "A temperature excursion alert remains visible, so stability evidence must match lot, temperature ceiling, duration, and release path.",
        "policy": ("STD-NRC-031-P", "Temperature excursion release is complete only when stability evidence matches lot, maximum temperature, exposure duration, product family, and release path before shipment."),
        "allow_docs": [
            ("REL-NRC-031", "Release request REL-NRC-2026-031 moves lot NRC-31 to customer shipment after a recorded excursion of 11.8C for 42 minutes."),
            ("ALERT-NRC-031", "Excursion alert remains visible for lot NRC-31 and requires stability evidence before shipment."),
            ("STAB-NRC-031", "Stability addendum STAB-NRC-031 covers lot NRC-31, product family NRC refrigerated reagent, maximum 12.0C exposure, duration up to 45 minutes, and customer shipment release path; approved before release."),
            ("NOTE-NRC-031", "Implementation note says many NRC lots share the same refrigerated product-family prefix; prefix alone is not release evidence."),
        ],
        "esc_docs": [
            ("REL-NRC-031", "Release request REL-NRC-2026-031 moves lot NRC-31 to customer shipment after a recorded excursion of 11.8C for 49 minutes."),
            ("ALERT-NRC-031", "Excursion alert remains visible for lot NRC-31 and requires stability evidence before shipment."),
            ("STAB-NRC-031", "Stability addendum STAB-NRC-031 covers lot NRC-31, product family NRC refrigerated reagent, maximum 12.0C exposure, duration up to 45 minutes, and customer shipment release path; approved before release."),
            ("NOTE-NRC-031", "Implementation note says many NRC lots share the same refrigerated product-family prefix; prefix alone is not release evidence."),
        ],
        "allow_rule": "STAB-NRC-031 exactly covers lot NRC-31, 11.8C, 42 minutes, and shipment path.",
        "esc_rule": "Exposure duration is 49 minutes but STAB-NRC-031 only covers up to 45 minutes.",
        "knew_terms": {
            "A": ["STAB-NRC-031", "NRC-31", "42", "45", "shipment"],
            "B": ["STAB-NRC-031", "49", "45", "duration"],
        },
    },
    {
        "pair_id": "HV-KITC-032",
        "vendor": "Altomar Access",
        "type": "emergency_access_enablement",
        "boundary": "May IT enable emergency admin access for the named user and system?",
        "anomaly": "The packet includes a stale generic warning that emergency access often requires security committee review.",
        "policy": ("STD-ALT-032-P", "Emergency access is complete only when approval matches user, system, privilege class, time window, and is effective before enablement."),
        "allow_docs": [
            ("REQ-ALT-032", "Access request REQ-ALT-2026-032 enables emergency admin for user Mara Ives on system ALT-ERP for privilege class breakglass-admin from 09:00 to 11:00."),
            ("WARN-ALT-032", "Generic warning says emergency access may require committee review when no breakglass approval exists."),
            ("APP-ALT-032", "Breakglass approval APP-ALT-032 covers Mara Ives, ALT-ERP, breakglass-admin privilege, 09:00 to 11:00 window, approved at 08:41 before enablement."),
        ],
        "esc_docs": [
            ("REQ-ALT-032", "Access request REQ-ALT-2026-032 enables emergency admin for user Mara Ives on system ALT-ERP for privilege class breakglass-admin from 09:00 to 11:00."),
            ("WARN-ALT-032", "Generic warning says emergency access may require committee review when no breakglass approval exists."),
            ("APP-ALT-032", "Breakglass approval APP-ALT-032 covers Mara Ives, ALT-CRM, breakglass-admin privilege, 09:00 to 11:00 window, approved at 08:41 before enablement."),
        ],
        "allow_rule": "APP-ALT-032 exactly matches user, system ALT-ERP, privilege, and time window before enablement.",
        "esc_rule": "APP-ALT-032 covers ALT-CRM, not ALT-ERP.",
        "knew_terms": {
            "A": ["APP-ALT-032", "Mara Ives", "ALT-ERP", "09:00", "11:00"],
            "B": ["APP-ALT-032", "ALT-CRM", "ALT-ERP", "system"],
        },
    },
    {
        "pair_id": "HV-KITC-033",
        "vendor": "Veyra Payments",
        "action_vendor": "Veyra Medical GmbH",
        "action_amount": 48200,
        "type": "payment_release",
        "boundary": "May AP release a payment after a sanctions near-match alert?",
        "anomaly": "A sanctions near-match alert remains visible for a similar vendor name.",
        "policy": ("STD-VEY-033-P", "A sanctions near-match is closed only when clearance matches legal name, registration country, tax ID, and counterparty account before release."),
        "allow_docs": [
            ("PAY-VEY-033", "Payment request PAY-VEY-2026-033 releases USD 48,200 to Veyra Medical GmbH, Germany, tax ID DE-8841, account ending 7712."),
            ("ALERT-VEY-033", "Sanctions near-match alert references Veyra Medica Ltd, Belarus, no tax ID match."),
            ("CLR-VEY-033", "Compliance clearance CLR-VEY-033 covers Veyra Medical GmbH, Germany, tax ID DE-8841, account ending 7712, and explicitly states the Belarus near-match is not the same counterparty."),
        ],
        "esc_docs": [
            ("PAY-VEY-033", "Payment request PAY-VEY-2026-033 releases USD 48,200 to Veyra Medical GmbH, Germany, tax ID DE-8841, account ending 7712."),
            ("ALERT-VEY-033", "Sanctions near-match alert references Veyra Medical GmbH, Germany, but lacks tax ID and account resolution."),
            ("CLR-VEY-033", "Compliance clearance CLR-VEY-033 covers Veyra Medical GmbH, Germany, tax ID DE-8841, account ending 1198, not the requested account ending 7712."),
        ],
        "allow_rule": "CLR-VEY-033 exactly clears legal name, country, tax ID, and account.",
        "esc_rule": "CLR-VEY-033 clears a different account ending.",
        "knew_terms": {
            "A": ["CLR-VEY-033", "Veyra Medical GmbH", "Germany", "DE-8841", "7712"],
            "B": ["CLR-VEY-033", "1198", "7712", "account"],
        },
    },
    {
        "pair_id": "HV-KITC-034",
        "vendor": "Kestrel Firmware",
        "type": "device_update",
        "boundary": "May engineering deploy the firmware update to the production fleet?",
        "anomaly": "The packet includes an obsolete-firmware alert; waiver evidence must match fleet, firmware branch, version, and deployment window.",
        "policy": ("STD-KES-034-P", "Firmware waiver closes an obsolete-firmware alert only when it matches fleet, firmware branch, target version, and deployment window before rollout."),
        "allow_docs": [
            ("DEP-KES-034", "Deployment DEP-KES-2026-034 updates production fleet K-Delta to branch F7 target version 7.4.2 during window W-19."),
            ("ALERT-KES-034", "Obsolete-firmware alert remains visible for branch F7 prior versions."),
            ("WAIV-KES-034", "Waiver WAIV-KES-034 covers production fleet K-Delta, branch F7, target version 7.4.2, deployment window W-19, approved before rollout."),
        ],
        "esc_docs": [
            ("DEP-KES-034", "Deployment DEP-KES-2026-034 updates production fleet K-Delta to branch F7 target version 7.4.2 during window W-19."),
            ("ALERT-KES-034", "Obsolete-firmware alert remains visible for branch F7 prior versions."),
            ("WAIV-KES-034", "Waiver WAIV-KES-034 covers production fleet K-Delta, branch F7, target version 7.4.1, deployment window W-19, approved before rollout."),
        ],
        "allow_rule": "WAIV-KES-034 exactly covers branch F7 version 7.4.2 in W-19.",
        "esc_rule": "WAIV-KES-034 covers target version 7.4.1, not 7.4.2.",
        "knew_terms": {
            "A": ["WAIV-KES-034", "K-Delta", "F7", "7.4.2", "W-19"],
            "B": ["WAIV-KES-034", "7.4.1", "7.4.2", "version"],
        },
    },
    {
        "pair_id": "HV-KITC-035",
        "vendor": "Mirox Vendor Master",
        "action_vendor": "Mirox Labs",
        "action_amount": 91000,
        "action_date": "2026-06-20",
        "type": "vendor_bank_update_payment",
        "boundary": "May AP release payment after a vendor bank update?",
        "anomaly": "The packet contains a bank-change alert and a visible AP-8 vendor-master form; payment release requires exact AP-9 evidence if needed.",
        "policy": ("STD-MIR-035-P", "Payment after a bank update is complete only when callback source, vendor-master change approval, and payment release authority match the requested vendor, account, amount, and date before release."),
        "allow_docs": [
            ("PAY-MIR-035", "Payment PAY-MIR-2026-035 releases USD 91,000 to Mirox Labs account ending 4402 on 2026-06-20."),
            ("ALERT-MIR-035", "Bank-change alert remains visible after vendor-master account update."),
            ("AP8-MIR-035", "AP-8 vendor-master form approves account ending 4402 for Mirox Labs."),
            ("AP9-MIR-035", "AP-9 payment release approval covers Mirox Labs, USD 91,000, account ending 4402, release date 2026-06-20, signed before release."),
            ("CALL-MIR-035", "Callback record CALL-MIR-035 used pre-change vendor master phone source and confirmed account ending 4402."),
        ],
        "esc_docs": [
            ("PAY-MIR-035", "Payment PAY-MIR-2026-035 releases USD 91,000 to Mirox Labs account ending 4402 on 2026-06-20."),
            ("ALERT-MIR-035", "Bank-change alert remains visible after vendor-master account update."),
            ("AP8-MIR-035", "AP-8 vendor-master form approves account ending 4402 for Mirox Labs."),
            ("CALL-MIR-035", "Callback record CALL-MIR-035 used pre-change vendor master phone source and confirmed account ending 4402."),
        ],
        "allow_rule": "AP9-MIR-035 and CALL-MIR-035 close both payment release and callback boundaries.",
        "esc_rule": "AP-9 payment release approval is absent; AP-8 alone is not payment release.",
        "knew_terms": {
            "A": ["AP9-MIR-035", "CALL-MIR-035", "4402", "91,000"],
            "B": ["AP-9", "absent", "AP-8", "payment release"],
        },
    },
    {
        "pair_id": "HV-KITC-036",
        "vendor": "Orison Export",
        "action_vendor": "Andexa Mining",
        "type": "export_release",
        "boundary": "May logistics release the export shipment?",
        "anomaly": "The export packet includes a broad dual-use warning and requires exact license scope.",
        "policy": ("STD-ORI-036-P", "Export release is complete only when license evidence matches ECCN, destination country, end user, and effective date before shipment."),
        "allow_docs": [
            ("SHIP-ORI-036", "Shipment SHIP-ORI-2026-036 exports ECCN 5A992 sensor module to Chile for end user Andexa Mining."),
            ("WARN-ORI-036", "Dual-use warning says similar sensor modules may require exact license review."),
            ("LIC-ORI-036", "Export license LIC-ORI-036 covers ECCN 5A992 sensor module, destination Chile, end user Andexa Mining, effective before shipment."),
        ],
        "esc_docs": [
            ("SHIP-ORI-036", "Shipment SHIP-ORI-2026-036 exports ECCN 5A992 sensor module to Chile for end user Andexa Mining."),
            ("WARN-ORI-036", "Dual-use warning says similar sensor modules may require exact license review."),
            ("LIC-ORI-036", "Export license LIC-ORI-036 covers ECCN 5A992 sensor module, destination Peru, end user Andexa Mining, effective before shipment."),
        ],
        "allow_rule": "LIC-ORI-036 exactly covers ECCN, Chile destination, and end user.",
        "esc_rule": "LIC-ORI-036 covers Peru, not Chile.",
        "knew_terms": {
            "A": ["LIC-ORI-036", "5A992", "Chile", "Andexa Mining"],
            "B": ["LIC-ORI-036", "Peru", "Chile", "destination"],
        },
    },
    {
        "pair_id": "HV-KITC-037",
        "vendor": "Rydan Tax",
        "action_vendor": "Rydan University",
        "type": "tax_exempt_sale",
        "boundary": "May order operations release a tax-exempt sale?",
        "anomaly": "A master tax certificate warning is visible; exemption evidence must match state, buyer, entity, and effective date.",
        "policy": ("STD-RYD-037-P", "Tax-exempt sale is complete only when exemption certificate matches buyer legal entity, ship-to state, tax category, and effective date before sale."),
        "allow_docs": [
            ("ORD-RYD-037", "Order ORD-RYD-2026-037 ships taxable lab equipment to buyer Rydan University in Texas."),
            ("WARN-RYD-037", "Master certificate warning says some old Rydan certificates were expired."),
            ("CERT-RYD-037", "Exemption certificate CERT-RYD-037 covers Rydan University, Texas ship-to, lab equipment category, effective through 2026-12-31."),
        ],
        "esc_docs": [
            ("ORD-RYD-037", "Order ORD-RYD-2026-037 ships taxable lab equipment to buyer Rydan University in Texas."),
            ("WARN-RYD-037", "Master certificate warning says some old Rydan certificates were expired."),
            ("CERT-RYD-037", "Exemption certificate CERT-RYD-037 covers Rydan University, Oklahoma ship-to, lab equipment category, effective through 2026-12-31."),
        ],
        "allow_rule": "CERT-RYD-037 exactly covers buyer, Texas ship-to, category, and date.",
        "esc_rule": "CERT-RYD-037 covers Oklahoma, not Texas.",
        "knew_terms": {
            "A": ["CERT-RYD-037", "Rydan University", "Texas", "lab equipment"],
            "B": ["CERT-RYD-037", "Oklahoma", "Texas", "state"],
        },
    },
    {
        "pair_id": "HV-KITC-038",
        "vendor": "Sable Credit",
        "action_vendor": "Sable Credit Services",
        "action_amount": 37500,
        "type": "duplicate_invoice_release",
        "boundary": "May AP release an invoice after a duplicate-payment alert?",
        "anomaly": "The packet includes a duplicate invoice alert; reversal evidence must match original invoice, amount, vendor, and ledger status.",
        "policy": ("STD-SAB-038-P", "Duplicate alert is closed only when reversal or credit evidence matches vendor, original invoice, amount, and posted ledger status before release."),
        "allow_docs": [
            ("INV-SAB-038", "Invoice INV-SAB-2026-038 requests USD 37,500 for Sable Credit Services."),
            ("ALERT-SAB-038", "Duplicate-payment alert references prior invoice INV-SAB-2026-014 for USD 37,500."),
            ("REV-SAB-038", "Reversal record REV-SAB-038 voids prior invoice INV-SAB-2026-014 for Sable Credit Services, USD 37,500, posted in ledger before release."),
        ],
        "esc_docs": [
            ("INV-SAB-038", "Invoice INV-SAB-2026-038 requests USD 37,500 for Sable Credit Services."),
            ("ALERT-SAB-038", "Duplicate-payment alert references prior invoice INV-SAB-2026-014 for USD 37,500."),
            ("REV-SAB-038", "Reversal record REV-SAB-038 voids prior invoice INV-SAB-2026-013 for Sable Credit Services, USD 37,500, posted in ledger before release."),
        ],
        "allow_rule": "REV-SAB-038 exactly voids the duplicate prior invoice.",
        "esc_rule": "REV-SAB-038 voids a different prior invoice.",
        "knew_terms": {
            "A": ["REV-SAB-038", "INV-SAB-2026-014", "37,500", "ledger posting"],
            "B": ["REV-SAB-038", "INV-SAB-2026-013", "INV-SAB-2026-014"],
        },
    },
    {
        "pair_id": "HV-KITC-039",
        "vendor": "Talon Insurance",
        "action_vendor": "Talon Installers",
        "action_date": "2026-06-22",
        "type": "contractor_site_start",
        "boundary": "May facilities allow contractor site work to begin?",
        "anomaly": "A generic COI insufficiency alert remains visible; endorsement evidence must match site, contractor, coverage type, and start date.",
        "policy": ("STD-TAL-039-P", "Contractor site start is complete only when insurance endorsement matches contractor, site, required coverage, and work start date before work begins."),
        "allow_docs": [
            ("WORK-TAL-039", "Work start WORK-TAL-2026-039 begins for Talon Installers at Site 7G on 2026-06-22 requiring umbrella liability."),
            ("ALERT-TAL-039", "COI insufficiency alert remains visible for umbrella liability."),
            ("END-TAL-039", "Insurance endorsement END-TAL-039 covers Talon Installers, Site 7G, umbrella liability, effective 2026-06-20 before work begins."),
        ],
        "esc_docs": [
            ("WORK-TAL-039", "Work start WORK-TAL-2026-039 begins for Talon Installers at Site 7G on 2026-06-22 requiring umbrella liability."),
            ("ALERT-TAL-039", "COI insufficiency alert remains visible for umbrella liability."),
            ("END-TAL-039", "Insurance endorsement END-TAL-039 covers Talon Installers, Site 7H, umbrella liability, effective 2026-06-20 before work begins."),
        ],
        "allow_rule": "END-TAL-039 exactly covers contractor, Site 7G, coverage, and date.",
        "esc_rule": "END-TAL-039 covers Site 7H, not Site 7G.",
        "knew_terms": {
            "A": ["END-TAL-039", "Talon Installers", "Site 7G", "umbrella liability"],
            "B": ["END-TAL-039", "Site 7H", "Site 7G", "site"],
        },
    },
    {
        "pair_id": "HV-KITC-040",
        "vendor": "Umbra Clinical",
        "type": "clinical_batch_release",
        "boundary": "May quality release the clinical batch?",
        "anomaly": "An assay deviation alert is visible; deviation closure must match batch, assay, acceptance criterion, and release date.",
        "policy": ("STD-UMB-040-P", "Clinical batch release is complete only when deviation closure matches batch, assay, acceptance criterion, and release date before release."),
        "allow_docs": [
            ("BATCH-UMB-040", "Batch release BATCH-UMB-2026-040 releases clinical batch UMB-40 for shipment."),
            ("DEV-UMB-040", "Deviation alert DEV-UMB-040 references assay AX-17 criterion Cq<=31."),
            ("CLOSE-UMB-040", "Deviation closure CLOSE-UMB-040 covers batch UMB-40, assay AX-17, criterion Cq<=31, and release date, approved before shipment."),
        ],
        "esc_docs": [
            ("BATCH-UMB-040", "Batch release BATCH-UMB-2026-040 releases clinical batch UMB-40 for shipment."),
            ("DEV-UMB-040", "Deviation alert DEV-UMB-040 references assay AX-17 criterion Cq<=31."),
            ("CLOSE-UMB-040", "Deviation closure CLOSE-UMB-040 covers batch UMB-41, assay AX-17, criterion Cq<=31, approved before shipment."),
        ],
        "allow_rule": "CLOSE-UMB-040 exactly covers batch UMB-40 and assay criterion.",
        "esc_rule": "CLOSE-UMB-040 covers batch UMB-41, not UMB-40.",
        "knew_terms": {
            "A": ["CLOSE-UMB-040", "UMB-40", "AX-17", "Cq<=31"],
            "B": ["CLOSE-UMB-040", "UMB-41", "UMB-40", "batch"],
        },
    },
]


def _packet(spec: dict[str, Any], suffix: str) -> dict[str, Any]:
    is_allow = suffix == "A"
    docs = spec["allow_docs"] if is_allow else spec["esc_docs"]
    return {
        "action": {
            "business_ref": f"{spec['pair_id']}-{suffix}",
            "type": spec["type"],
            "vendor": spec.get("action_vendor", spec["vendor"]),
            "amount": spec.get("action_amount", 0),
            "currency": "USD",
            "description": spec["boundary"],
            "action_date": spec.get("action_date", "2026-06-28"),
        },
        "context": {
            "action_boundary": spec["boundary"],
            "anomaly_observed": spec["anomaly"],
            "explanation_summary": "Verify whether the closure evidence exactly matches the action boundary before execution.",
            "internal_documents": [
                {"doc_id": doc_id, "type": "source_record", "content": content}
                for doc_id, content in docs
            ],
            "policy_documents": [
                {"doc_id": spec["policy"][0], "title": "Exact source-boundary policy", "content": spec["policy"][1]}
            ],
        },
    }


def _strip_thinking_blocks(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I)
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.S | re.I)
    return text.strip()


def _chat_completions_url() -> str:
    explicit = os.getenv("MINIMAX_CHAT_COMPLETIONS_URL", "").strip()
    if explicit:
        return explicit
    base = os.getenv("MINIMAX_BASE_URL", "").strip()
    if base:
        return base.rstrip("/") + "/chat/completions"
    return "https://api.minimaxi.chat/v1/chat/completions"


def _call_minimax(system: str, user: str) -> dict[str, Any]:
    started = time.time()
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0,
        "max_tokens": 900,
    }
    req = urllib.request.Request(
        _chat_completions_url(),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {os.getenv('MINIMAX_API_KEY', '').strip()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=75) as response:
        data = json.loads(response.read().decode("utf-8", errors="replace"))
    choices = data.get("choices") or [{}]
    first_choice = choices[0] if isinstance(choices[0], dict) else {}
    message = first_choice.get("message") if isinstance(first_choice, dict) else {}
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return {
        "raw_text": _strip_thinking_blocks((message or {}).get("content") or ""),
        "finish_reason": first_choice.get("finish_reason"),
        "response_id": data.get("id"),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "elapsed_ms": int((time.time() - started) * 1000),
    }


def _parse(text: str) -> tuple[bool, str | None, dict[str, Any] | None, str | None]:
    stripped = text.strip()
    if stripped.startswith("```"):
        return False, None, None, "markdown_fence_present"
    try:
        obj = json.loads(stripped)
    except Exception as exc:
        return False, None, None, f"json_parse_error:{type(exc).__name__}"
    verdict = obj.get("verdict") or obj.get("verification_verdict")
    if verdict not in {"ALLOW", "ESCALATE"}:
        return False, verdict, obj, "verdict_invalid"
    return True, verdict, obj, None


def _evidence_term_present(rationale: str, term: Any) -> bool:
    if isinstance(term, (list, tuple)):
        return any(_evidence_term_present(rationale, option) for option in term)
    return str(term).lower() in rationale


def _evidence_term_label(term: Any) -> str:
    if isinstance(term, (list, tuple)):
        return "|".join(str(option) for option in term)
    return str(term)


def _behavior_label(spec: dict[str, Any], suffix: str, row: dict[str, Any]) -> tuple[str, list[str]]:
    if not row.get("provider_call_ok"):
        return "PROVIDER_FAILURE", ["provider_call_failed"]
    if not row.get("parse_ok"):
        return "NOT_KNEW_MALFORMED", [row.get("parse_error") or "parse_failed"]
    expected = row["expected_for_local_audit_only"]
    if row.get("verdict") != expected:
        return "NOT_KNEW_WRONG_VERDICT", [f"expected_{expected}_got_{row.get('verdict')}"]
    rationale = ((row.get("parsed_json") or {}).get("rationale") or row.get("raw_text") or "").lower()
    missing = [
        _evidence_term_label(term)
        for term in spec.get("knew_terms", {}).get(suffix, [])
        if not _evidence_term_present(rationale, term)
    ]
    if missing:
        return "NOT_KNEW_UNPROVEN", [f"missing_evidence_term:{term}" for term in missing]
    return "KNEW", []


def _selected_from_rows(rows: list[dict[str, Any]], specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = []
    for spec in specs:
        family_rows = [r for r in rows if r.get("pair_id") == spec["pair_id"]]
        if len(family_rows) < 2:
            continue
        if any(r.get("behavior_label") != "KNEW" for r in family_rows):
            selected.append(
                {
                    "pair_id": spec["pair_id"],
                    "failure_classes": spec.get("failure_classes", []),
                    "failure_class_notes": spec.get("failure_class_notes", ""),
                    "packets": [
                        {
                            "packet_id": r["packet_id"],
                            "packet_path": r["packet_path"],
                            "expected": r["expected_for_local_audit_only"],
                            "verdict": r.get("verdict"),
                            "target_match": r.get("target_match"),
                            "behavior_label": r.get("behavior_label"),
                            "behavior_notes": r.get("behavior_notes"),
                        }
                        for r in family_rows
                    ],
                }
            )
    return selected


def main() -> int:
    if not os.getenv("MINIMAX_API_KEY", "").strip():
        raise RuntimeError("MINIMAX_API_KEY missing")
    resume_dir = os.getenv("KIT_C_RESUME_RUN_DIR", "").strip()
    out_dir = Path(resume_dir) if resume_dir else ROOT / datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    packets_dir = out_dir / "generated_packets"
    packets_dir.mkdir(parents=True, exist_ok=bool(resume_dir))
    trace_path = out_dir / "CONTROL_SCREEN_TRACE.jsonl"
    rows = []
    if resume_dir and trace_path.exists():
        rows = [json.loads(line) for line in trace_path.read_text().splitlines() if line.strip()]
    completed_packet_ids = {r.get("packet_id") for r in rows}
    with trace_path.open("a" if resume_dir else "w") as trace:
        for spec in SPECS:
            family_rows = []
            for suffix, expected in (("A", "ALLOW"), ("B", "ESCALATE")):
                packet_id = f"{spec['pair_id']}-{suffix}"
                packet = _packet(spec, suffix)
                packet_path = packets_dir / f"{packet_id}.payload.json"
                packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
                if packet_id in completed_packet_ids:
                    family_rows.extend([r for r in rows if r.get("packet_id") == packet_id])
                    continue
                user = json.dumps(packet, separators=(",", ":"))
                row = {
                    "call_index": len(rows) + 1,
                    "called_at": datetime.now(timezone.utc).isoformat(),
                    "screen_type": "GENERATED_HARDENED_KIT_C_RAW_SOLO_SCREEN",
                    "provider": "minimax",
                    "model": MODEL,
                    "pair_id": spec["pair_id"],
                    "packet_id": packet_id,
                    "packet_path": str(packet_path),
                    "expected_for_local_audit_only": expected,
                    "allow_rule": spec["allow_rule"],
                    "esc_rule": spec["esc_rule"],
                    "failure_classes": spec.get("failure_classes", []),
                    "failure_class_notes": spec.get("failure_class_notes", ""),
                }
                try:
                    response = _call_minimax(SYSTEM, user)
                    parse_ok, verdict, parsed, parse_error = _parse(response["raw_text"])
                    row.update(
                        {
                            **response,
                            "provider_call_ok": True,
                            "parse_ok": parse_ok,
                            "parse_error": parse_error,
                            "verdict": verdict,
                            "parsed_json": parsed,
                            "target_match": parse_ok and verdict == expected,
                        }
                    )
                    behavior_label, behavior_notes = _behavior_label(spec, suffix, row)
                    row["behavior_label"] = behavior_label
                    row["behavior_notes"] = behavior_notes
                except Exception as exc:
                    row.update(
                        {
                            "provider_call_ok": False,
                            "parse_ok": False,
                            "error": f"{type(exc).__name__}: {exc}",
                            "target_match": False,
                        }
                    )
                    behavior_label, behavior_notes = _behavior_label(spec, suffix, row)
                    row["behavior_label"] = behavior_label
                    row["behavior_notes"] = behavior_notes
                    trace.write(json.dumps(row) + "\n")
                    rows.append(row)
                    break
                trace.write(json.dumps(row) + "\n")
                rows.append(row)
                family_rows.append(row)
            else:
                if len(family_rows) < 2:
                    continue
                print(
                    "screened",
                    spec["pair_id"],
                    [
                        (
                            r["expected_for_local_audit_only"],
                            r.get("verdict"),
                            r.get("target_match"),
                            r.get("behavior_label"),
                        )
                        for r in family_rows
                    ],
                    flush=True,
                )
                if len(_selected_from_rows(rows, SPECS)) >= 8:
                    break
                continue
            break
    selected = _selected_from_rows(rows, SPECS)
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for row in rows:
        for key in totals:
            if isinstance(row.get(key), int):
                totals[key] += row[key]
    summary = {
        "classification": "GENERATED_HARDENED_KIT_C_SCREEN_COMPLETE",
        "run_dir": str(out_dir),
        "provider_calls": len(rows),
        "selected_count": len(selected),
        "selected": selected,
        "selection_rule": "Selected if any sibling is not behavior_label=KNEW. Verdict target_match alone is not counted as a Solo win.",
        "tokens": totals,
    }
    (out_dir / "screen_summary.json").write_text(json.dumps(summary, indent=2))
    md = [
        "# Generated Hardened Kit C Screen",
        "",
        f"Classification: `{summary['classification']}`",
        f"Selected: `{len(selected)}` / `8`",
        "",
        "Selection rule: only `KNEW` counts as a Solo win. Correct verdicts without required evidence terms are treated as not proven.",
        f"Provider calls: `{len(rows)}`",
        f"Tokens: `{totals['input_tokens']}` input / `{totals['output_tokens']}` output / `{totals['total_tokens']}` total",
        "",
        "| Pair | Verdicts |",
        "| --- | --- |",
    ]
    for item in selected:
        verdicts = ", ".join(
            f"{p['packet_id']} {p['expected']}->{p['verdict']} {p['behavior_label']}" for p in item["packets"]
        )
        md.append(f"| `{item['pair_id']}` | {verdicts} |")
    (out_dir / "screen_summary.md").write_text("\n".join(md) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
