"""T2 - poisoned-spec byte-invariance + static truth-reachability guard.

Falsifies: "runtime behavior is a pure function of the model-visible payload
and model outputs." Passing does NOT bind fields added later; the static
guard re-runs on every change as the regression net.
"""

import pytest

from blind_lane_suite import BENCH
from blind_lane_suite.fixtures import (
    SENTINEL,
    build_poisoned_variants,
    canonicalize_run_result,
    mock_transcripts,
    model_visible_payload,
)
from blind_lane_suite.runner_contract import SKIP_REASON, load_runner, runner_source_path
from blind_lane_suite.static_guards import (
    scan_import_closure_for_truth_reachability,
    scan_source_for_truth_reachability,
    source_import_closure,
)

GOVERNED_RUNNER = BENCH / "run_20pair_holoverify_3dna_2026_06_29.py"


def test_static_detector_catches_governed_runner():
    """Detector validation: the governed runner is KNOWN leaky (suffix-derived
    verdicts, knew_terms gate, directional repair). Zero findings here means
    the AST scanner is broken."""
    if not GOVERNED_RUNNER.exists():
        pytest.skip("governed runner not in checkout - detector NOT validated")
    findings = scan_source_for_truth_reachability(GOVERNED_RUNNER)
    kinds = {f["kind"] for f in findings}
    assert findings, "AST scanner found nothing in the known-leaky governed runner - scanner broken"
    assert "suffix_verdict_derivation" in kinds or "forbidden_field_string" in kinds


def test_registered_blind_runner_source_is_truth_free():
    runner, missing = load_runner()
    if runner is None:
        pytest.skip(SKIP_REASON)
    assert not missing, f"blind runner contract violation - missing attrs: {missing}"
    src = runner_source_path(runner)
    assert src, "registered runner has no source path"
    findings = scan_source_for_truth_reachability(src)
    assert not findings, f"TRUTH REACHABILITY in blind runner source: {findings[:10]}"


def test_registered_blind_runner_import_closure_is_truth_free():
    runner, missing = load_runner()
    if runner is None:
        pytest.skip(SKIP_REASON)
    assert not missing, f"blind runner contract violation - missing attrs: {missing}"
    src = runner_source_path(runner)
    assert src, "registered runner has no source path"
    closure = source_import_closure(src)
    assert closure, "import-closure scan found no source files"
    findings = scan_import_closure_for_truth_reachability(src)
    assert not findings, f"TRUTH REACHABILITY in runner import closure: {findings[:10]}"


def test_poisoned_spec_byte_invariance(tmp_path):
    """Run the blind runner over truth-poisoned spec variants with identical
    transcripts; every prompt/gate/baton/selector byte must match, and no
    sentinel string may surface anywhere."""
    runner, missing = load_runner()
    if runner is None:
        pytest.skip(SKIP_REASON)
    assert not missing, f"blind runner contract violation - missing attrs: {missing}"

    variants = build_poisoned_variants()
    transcripts = mock_transcripts(verdict="ESCALATE")
    canon = {}
    for name, spec in variants.items():
        payload = model_visible_payload(spec, "B")
        out_dir = tmp_path / name
        out_dir.mkdir()
        result = runner.run_blind_fixture(payload, transcripts, str(out_dir))
        text = canonicalize_run_result(result)
        assert SENTINEL not in text, (
            f"TRUTH LEAK: sentinel spec content surfaced in runtime output (variant={name})"
        )
        canon[name] = text

    baseline = canon["as_written"]
    for name, text in canon.items():
        assert text == baseline, (
            f"TRUTH SENSITIVITY: runtime output differs under poisoning variant '{name}' - "
            "behavior is not a pure function of payload + model outputs"
        )
