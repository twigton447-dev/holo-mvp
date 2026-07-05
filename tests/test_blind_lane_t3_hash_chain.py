"""T3 - artifact provenance hash chain / no-mutation.

Falsifies: "the harness never writes into worker artifacts."
Passing does NOT show artifacts are good - only untouched.
"""

import pytest

from blind_lane_suite.fixtures import mock_transcripts, model_visible_payload, SYNTHETIC_PAIR_SPEC
from blind_lane_suite.hash_chain import sha256_text, verify_hash_chain
from blind_lane_suite.runner_contract import SKIP_REASON, load_runner, runner_source_path
from blind_lane_suite.static_guards import scan_source_for_truth_reachability


def test_verifier_flags_mutation():
    """Detector validation: a mutated artifact MUST be flagged. A verifier
    that passes this synthetic mutation is broken."""
    raw = "worker_role=X\nverification_verdict=ESCALATE\nfinal_answer=raw"
    mutated_run = {
        "worker_rows": [
            {
                "raw_output_sha256": sha256_text(raw),
                "artifact_text": raw + "\ncritical_features_preserved=INJECTED-BY-HARNESS",
            }
        ]
    }
    violations = verify_hash_chain(mutated_run, [raw])
    assert any(v["kind"] == "artifact_mutated" for v in violations), (
        "hash-chain verifier failed to flag a synthetic mutation - verifier broken"
    )


def test_verifier_accepts_untouched_chain():
    raw = "worker_role=X\nverification_verdict=ALLOW\nfinal_answer=raw"
    clean_run = {"worker_rows": [{"raw_output_sha256": sha256_text(raw), "artifact_text": raw}]}
    assert verify_hash_chain(clean_run, [raw]) == []


def test_blind_runner_artifacts_untouched(tmp_path):
    runner, missing = load_runner()
    if runner is None:
        pytest.skip(SKIP_REASON)
    assert not missing, f"blind runner contract violation - missing attrs: {missing}"
    transcripts = mock_transcripts(verdict="ALLOW")
    payload = model_visible_payload(SYNTHETIC_PAIR_SPEC, "A")
    result = runner.run_blind_fixture(payload, transcripts, str(tmp_path))
    violations = verify_hash_chain(result, transcripts)
    assert not violations, f"ARTIFACT MUTATION in blind runner: {violations[:5]}"


def test_blind_runner_has_no_normalizer_reachability():
    """The governed lane's mutation entry points must be unreachable from the
    blind runner (same AST guard as T2; asserted here for the mutation names
    specifically so a T2 waiver cannot silently re-admit mutation)."""
    runner, missing = load_runner()
    if runner is None:
        pytest.skip(SKIP_REASON)
    src = runner_source_path(runner)
    findings = [
        f
        for f in scan_source_for_truth_reachability(src)
        if f.get("name") in {"_normalize_worker_artifact_after_gate", "_worker_expected_binding"}
        or f["kind"] in {"forbidden_call", "forbidden_def"}
    ]
    assert not findings, f"MUTATION PATH reachable from blind runner: {findings[:5]}"
