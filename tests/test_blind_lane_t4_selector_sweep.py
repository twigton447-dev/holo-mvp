"""T4 - selector truth-swap sweep.

Falsifies: "the final selector chooses by closed-form blind criteria only."
Passing does NOT show the criteria are well-chosen (e.g., verbosity bias).
"""

import copy

import pytest

from blind_lane_suite.fixtures import selector_sweep_cases
from blind_lane_suite.runner_contract import SKIP_REASON, load_runner


def _runner_or_skip():
    runner, missing = load_runner()
    if runner is None:
        pytest.skip(SKIP_REASON)
    assert not missing, f"blind runner contract violation - missing attrs: {missing}"
    return runner


def test_selection_invariant_under_truth_swap():
    """Same artifact set, truth flipped: the pick must not move. The fixture
    makes the truth-matching artifact structurally WEAKER, so any
    truth-following pick is visible."""
    runner = _runner_or_skip()
    picks = {}
    for case in selector_sweep_cases():
        artifacts = copy.deepcopy(case["artifacts"])  # truth key never passed in
        picks[case["truth"]] = runner.select_final(artifacts)["selected_artifact_id"]
    assert picks["ALLOW"] == picks["ESCALATE"], (
        f"TRUTH-CORRELATED SELECTION: pick changed when only truth changed: {picks}"
    )


def test_selection_matches_declared_criteria():
    """Undeclared criteria detection: recomputation from SELECTOR_CRITERIA
    alone must reproduce every actual selection."""
    runner = _runner_or_skip()
    assert isinstance(runner.SELECTOR_CRITERIA, (list, tuple)) and runner.SELECTOR_CRITERIA, (
        "SELECTOR_CRITERIA must be a non-empty closed-form list"
    )
    for case in selector_sweep_cases():
        artifacts = copy.deepcopy(case["artifacts"])
        actual = runner.select_final(artifacts)["selected_artifact_id"]
        recomputed = runner.apply_criteria(artifacts)["selected_artifact_id"]
        assert actual == recomputed, (
            f"UNDECLARED CRITERIA: select_final={actual} but declared criteria give {recomputed} "
            f"(case={case['case_id']})"
        )


def test_criteria_names_are_blind():
    """No declared criterion may reference truth or spec-derived features."""
    runner = _runner_or_skip()
    forbidden = ("truth", "expected", "knew", "critical_term", "suffix")
    bad = [c for c in runner.SELECTOR_CRITERIA if any(t in str(c).lower() for t in forbidden)]
    assert not bad, f"TRUTH-ADJACENT SELECTOR CRITERIA: {bad}"
