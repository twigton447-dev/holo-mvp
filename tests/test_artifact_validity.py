import sys
from pathlib import Path


HARNESS_DIR = Path(__file__).resolve().parents[1] / "artifact_benchmarks" / "harness"
sys.path.insert(0, str(HARNESS_DIR))

from artifact_validity import (  # noqa: E402
    artifact_validity_report,
    context_required_items,
    context_word_bounds,
)


def test_current_event_brief_shape_supplies_required_items_and_word_bounds():
    context = {
        "deliverable_requirements": {
            "target_length_words": [2800, 3400],
            "must_include": [
                "A current-event market setup using the provided source pack only.",
                "Explicit statement that this is not investment advice.",
            ],
        }
    }

    assert context_word_bounds(context) == (2800, 3400)
    assert context_required_items(context) == [
        "A current-event market setup using the provided source pack only.",
        "Explicit statement that this is not investment advice.",
    ]


def test_final_artifact_flags_mission_packet_residue(tmp_path):
    artifact = tmp_path / "final.md"
    artifact.write_text(
        "This final report is not investment advice. "
        "It accidentally leaked repair_ledger process residue.",
        encoding="utf-8",
    )

    report = artifact_validity_report(
        artifact,
        require_disclaimer=True,
        require_clean_final=True,
    )

    assert not report["valid"]
    assert "internal_process_residue" in report["flags"]
