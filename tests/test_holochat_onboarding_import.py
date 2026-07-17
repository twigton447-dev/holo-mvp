"""No-provider tests for HoloChat onboarding import admission."""

from __future__ import annotations

from holochat_onboarding import (
    ImportDisposition,
    build_onboarding_context_writes,
    onboarding_prompt_for_areas,
)


def _packet() -> str:
    return """
Stable personal context
- Elliot is a senior valuation associate at Meridian Ridge Capital. Confidence: user-stated. Recency: current.
- His wife is Claire. Confidence: user-stated. Recency: current.
- His children are Owen, age 9, and Lily, age 6. Confidence: user-stated. Recency: current.
- He has intermittent migraines that can affect screen tolerance, focus, patience, sleep, and availability. Confidence: user-stated. Recency: current.
- He likes old jazz records, black coffee, woodworking, early surfing, and quiet Saturday drives. Confidence: user-stated.

Working style
- He prefers concise, evidence-first answers with dates, units, source boundaries, assumptions, and downside cases.

Current priorities
- He is preparing a DCF and DLOM workflow and wants Holo to keep assumption changes explicit.

Needs confirmation
- He may be tempted to over-tighten a DLOM range when under deadline pressure.

Do not import
- His full home address is 123 Example Street.
"""


def test_onboarding_import_admits_family_and_health_as_personal_private() -> None:
    result = build_onboarding_context_writes(_packet(), selected_areas=["HoloFamily", "HoloFinance"])

    private = result.context_writes["holo_personal_private_v1"]
    assert "Claire" in private
    assert "Owen" in private
    assert "Lily" in private
    assert "migraines" in private
    assert result.review_required is False
    assert result.review_available is True
    assert result.no_external_calls is True


def test_onboarding_import_keeps_work_style_without_leaking_private_to_enterprise() -> None:
    result = build_onboarding_context_writes(_packet())

    style = result.context_writes["holo_working_style_v1"]
    boundary = result.context_writes["holo_personal_enterprise_boundary_v1"]

    assert "evidence-first" in style
    assert "Enterprise may receive only minimal user-authorized availability signals" in boundary
    assert "family or medical details" in boundary
    assert all("holo_enterprise" not in key for key in result.context_writes)


def test_onboarding_import_quarantines_uncertain_items_not_facts() -> None:
    result = build_onboarding_context_writes(_packet())

    assert any(item.disposition is ImportDisposition.QUARANTINE for item in result.quarantined)
    assert "over-tighten a DLOM range" in result.context_writes["holo_onboarding_quarantine_v1"]
    assert "over-tighten a DLOM range" not in result.context_writes.get("holo_personal_profile_v1", "")


def test_onboarding_import_rejects_enterprise_confidential_material() -> None:
    packet = """
Stable personal context
- Elliot works in valuation and likes precise assumption logs.

Current priorities
- Client name Apex Meridian and issuer SPCX BetaCo are in a live deal with nonpublic revenue numbers.
- The cap table and investment committee material are attached in the current valuation file.
"""
    result = build_onboarding_context_writes(packet)

    rejected_text = result.context_writes["holo_onboarding_rejected_v1"]
    assert "Client name Apex Meridian" in rejected_text
    assert "cap table" in rejected_text
    assert "Apex Meridian" not in result.context_writes.get("holo_personal_profile_v1", "")
    assert "valuation file" not in result.context_writes.get("holo_current_priorities_v1", "")


def test_onboarding_import_rejects_secrets_and_do_not_import_section() -> None:
    result = build_onboarding_context_writes(_packet())

    rejected = result.context_writes["holo_onboarding_rejected_v1"]
    assert "full home address" in rejected
    assert "123 Example Street" in rejected


def test_context_transfer_prompt_asks_for_holobrain_import_packet() -> None:
    prompt = onboarding_prompt_for_areas(["HoloMarriage", "HoloFinance"])

    assert "Create a HoloBrain Import Packet" in prompt
    assert "HoloMarriage, HoloFinance" in prompt
    assert "Return exactly these labeled sections" in prompt
    assert "Needs confirmation" in prompt
    assert "Do not import" in prompt
    assert "quarantine uncertain items" in prompt
    assert "search the web" not in prompt.lower()
