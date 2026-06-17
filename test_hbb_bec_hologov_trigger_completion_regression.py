from __future__ import annotations

from pathlib import Path


def _combined_prompt_surface() -> str:
    return " ".join(Path("llm_adapters.py").read_text().lower().split())


def test_trigger_is_not_blocker_after_documented_completion() -> None:
    prompt = _combined_prompt_surface()

    assert "elevated scrutiny triggers" in prompt
    assert "not payment blockers after documented control closure" in prompt
    assert "escalate only when required control provenance is missing" in prompt
    assert "unresolved" in prompt
    assert "contradictory" in prompt
    assert "noncompliant" in prompt


def test_completed_elevated_scrutiny_can_support_allow() -> None:
    prompt = _combined_prompt_surface()

    assert "elevated scrutiny routing" in prompt
    assert "cross-reference checks" in prompt
    assert "two-person ap signoff" in prompt
    assert "callback verification" in prompt
    assert "may support allow" in prompt


def test_callback_provenance_boundary_is_preserved() -> None:
    prompt = _combined_prompt_surface()

    assert "pre-change vendor-master" in prompt
    assert "compliant" in prompt
    assert "portal change request" in prompt
    assert "invoice" in prompt
    assert "newly supplied contact" in prompt
    assert "noncompliant" in prompt
    assert "material blocker" in prompt
