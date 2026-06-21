from pathlib import Path


DOC_PATH = Path(__file__).resolve().parents[1] / "docs" / "HOLOGOVERNOR_TAXONOMY.md"


def _taxonomy_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_hologovernor_taxonomy_locks_canonical_terms():
    text = _taxonomy_doc()

    required_lines = [
        "HoloGovernor = core governing architecture family.",
        "HoloContext = context-control subsystem inside HoloGovernor.",
        "HoloBrain = durable cognition/state layer.",
        "HoloGov-C = HoloGovernor Chat, responsible for HoloChat continuity and context admission.",
        "HoloGov-V = HoloGovernor Verify, responsible for action-boundary adjudication and ALLOW/ESCALATE.",
        "HoloGov-B = HoloGovernor Build, responsible for artifact refinement and freeze readiness.",
        "HoloGov-J = HoloGovernor Judge, responsible for evaluation and scoring if needed.",
        "ContextGovernor = legacy/internal implementation term only. Do not treat it as the universal HoloGovernor.",
    ]

    for line in required_lines:
        assert line in text


def test_hologov_c_and_hologov_v_state_boundaries_are_distinct():
    text = _taxonomy_doc()

    assert (
        "HoloGov-C uses HoloContext to budget-gate HoloBrain state into private model context."
        in text
    )
    assert (
        "HoloGov-V uses HoloContext to manage action goal, evidence coverage, findings, baton, audit, and final ALLOW/ESCALATE."
        in text
    )
    assert "Do not collapse HoloChat continuity state into HoloVerify action-evaluation state." in text


def test_contextgovernor_is_not_universal_hologovernor():
    text = _taxonomy_doc()

    assert "ContextGovernor = legacy/internal implementation term only" in text
    assert "Do not treat it as the universal HoloGovernor." in text
    assert "Shared doctrine does not mean shared runtime state." in text
