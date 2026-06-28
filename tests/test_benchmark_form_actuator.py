from dataclasses import asdict

from benchmark_form_actuator import (
    FormGateConfig,
    build_form_actuation_baton,
    count_words,
)


def _words(count: int) -> str:
    return " ".join(f"w{i}" for i in range(count))


def test_d12_like_under_band_artifact_gets_expansion_baton():
    baton = build_form_actuation_baton(_words(607))

    assert baton.classification == "FORM_ACTUATION_REQUIRED"
    assert baton.primary_defect == "WORD_BAND_UNDER"
    assert baton.failures == ["word_band_under"]
    assert baton.word_count == 607
    assert baton.minimum_change_to_enter_band == 293
    assert baton.delta_to_target == 493
    assert "Expand by at least 293 words" in baton.final_worker_instruction
    assert "target is 1100" in baton.final_worker_instruction


def test_over_band_artifact_gets_compression_baton():
    baton = build_form_actuation_baton(_words(1852))

    assert baton.classification == "FORM_ACTUATION_REQUIRED"
    assert baton.primary_defect == "WORD_BAND_OVER"
    assert baton.failures == ["word_band_over"]
    assert baton.word_count == 1852
    assert baton.minimum_change_to_enter_band == -552
    assert baton.delta_to_target == -752
    assert "Compress by at least 552 words" in baton.final_worker_instruction


def test_in_band_artifact_does_not_require_actuation():
    baton = build_form_actuation_baton(_words(1115))

    assert baton.classification == "FORM_ACTUATION_NOT_REQUIRED"
    assert baton.primary_defect == "PASS"
    assert baton.failures == []
    assert baton.word_count == 1115
    assert baton.minimum_change_to_enter_band == 0
    assert "Preserve the artifact inside 900-1300 words" in baton.final_worker_instruction


def test_required_sections_are_detected_and_quoted():
    config = FormGateConfig(
        required_sections=(
            "Decision",
            "Source Grounding",
            "Open Dependencies",
            "Final Recommendation",
        )
    )
    text = "\n\n".join(
        (
            "## Decision\n" + _words(100),
            "## Source Grounding\n" + _words(100),
            "## Final Recommendation\n" + _words(100),
        )
    )

    baton = build_form_actuation_baton(text, config)
    reports = {report.name: report for report in baton.section_reports}

    assert "missing_required_sections" in baton.failures
    assert baton.primary_defect == "MISSING_REQUIRED_SECTIONS"
    assert reports["Open Dependencies"].present is False
    assert reports["Decision"].present is True
    assert baton.required_section_order == [
        "Decision",
        "Source Grounding",
        "Open Dependencies",
        "Final Recommendation",
    ]
    assert "Use exactly these sections in this order" in baton.final_worker_instruction
    assert "- Open Dependencies: target 275 words" in baton.final_worker_instruction


def test_section_quotas_sum_to_target_band_and_are_json_serializable():
    config = FormGateConfig(
        required_sections=(
            "Executive Decision",
            "Evidence Ledger",
            "Risk Register",
            "Action Boundary",
        )
    )
    text = "\n\n".join(f"## {section}\n{_words(100)}" for section in config.required_sections)

    baton = build_form_actuation_baton(text, config)
    reports = baton.section_reports

    assert sum(report.target_words for report in reports) == 1100
    assert sum(report.min_words for report in reports) == 900
    assert sum(report.max_words for report in reports) == 1300
    assert all(report.target_words == 275 for report in reports)
    assert count_words(baton.final_worker_instruction) > 0
    assert asdict(baton)["section_reports"][0]["name"] == "Executive Decision"


def test_baton_does_not_embed_or_rewrite_artifact_body():
    artifact = "needle_unique_source_sentence " + _words(606)
    baton = build_form_actuation_baton(artifact)

    assert "needle_unique_source_sentence" not in baton.final_worker_instruction
