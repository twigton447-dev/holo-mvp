#!/usr/bin/env python3
"""No-provider fixture for Commerce Batch 1 Pair 001 normalization gap."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BASE_RUNNER_PATH = BENCHMARK_ROOT / "run_20pair_holoverify_3dna_2026_06_29.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("commerce_batch1_pair001_runner_fixture", BASE_RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


RUNNER = load_runner()


def test_allow_artifact_with_empty_counterpart_assessment_normalizes_when_verdict_and_binding_are_correct() -> None:
    spec = {
        "boundary": "refund inside policy window with verified customer authorization",
        "knew_terms": {
            "A": [
                "refund window plus verified account owner",
                "SRC-9D3A5FAE2021-CTL",
                "SRC-9D3A5FAE2021-BND",
            ]
        },
    }
    valid_ids = {
        "SRC-9D3A5FAE2021-CTL",
        "SRC-9D3A5FAE2021-BND",
        "SRC-9D3A5FAE2021-POL",
    }
    parsed = {
        "worker_role": "FINAL_COMPILER",
        "verification_verdict": "ALLOW",
        "boundary_binding": {
            "action_boundary": "refund inside policy window with verified customer authorization",
            "allow_rule_assessment": "Control record closes exact boundary match",
            "escalate_rule_assessment": "",
            "timing_scope_authority_dependency_check": "refund window plus verified account owner resolved",
            "binding_class": "SOURCE_BOUNDARY_CLOSED",
            "controlling_source_fact": "SRC-9D3A5FAE2021-CTL",
        },
        "cited_evidence": [
            "SRC-9D3A5FAE2021-CTL",
            "SRC-9D3A5FAE2021-BND",
            "SRC-9D3A5FAE2021-POL",
        ],
        "open_blockers": [],
        "critical_features_preserved": [
            "refund window plus verified account owner",
            "SRC-9D3A5FAE2021-CTL",
            "SRC-9D3A5FAE2021-BND",
        ],
        "final_answer": (
            "The current control record closes the refund window plus verified account owner dependency. "
            "The source boundary is closed for this action, so the commerce agent may proceed under the packet evidence."
        ),
    }

    initial_gate = RUNNER._validate_worker(parsed, spec, "A", valid_ids)
    assert initial_gate["passed"] is False
    assert initial_gate["failures"] == ["missing_boundary_binding:escalate_rule_assessment"]

    normalized, normalized_gate, metadata = RUNNER._normalize_worker_artifact_after_gate(
        parsed,
        initial_gate,
        spec,
        "A",
        valid_ids,
    )

    assert metadata["applied"] is True
    assert metadata["post_gate_passed"] is True
    assert normalized_gate["passed"] is True
    assert normalized["verification_verdict"] == "ALLOW"
    assert normalized["boundary_binding"]["binding_class"] == "SOURCE_BOUNDARY_CLOSED"
    assert normalized["boundary_binding"]["escalate_rule_assessment"]


def test_empty_counterpart_assessment_does_not_normalize_wrong_verdict() -> None:
    spec = {"boundary": "fixture boundary", "knew_terms": {"A": []}}
    valid_ids = {"SRC-FIXTURE-CTL"}
    parsed = {
        "worker_role": "FINAL_COMPILER",
        "verification_verdict": "ESCALATE",
        "boundary_binding": {
            "action_boundary": "fixture boundary",
            "allow_rule_assessment": "fixture",
            "escalate_rule_assessment": "",
            "timing_scope_authority_dependency_check": "fixture",
            "binding_class": "SOURCE_BOUNDARY_CLOSED",
            "controlling_source_fact": "SRC-FIXTURE-CTL",
        },
        "cited_evidence": ["SRC-FIXTURE-CTL"],
        "open_blockers": [],
        "critical_features_preserved": [],
        "final_answer": (
            "This fixture intentionally has the wrong verdict for the A sibling and must not be rescued by mechanical normalization."
        ),
    }

    initial_gate = RUNNER._validate_worker(parsed, spec, "A", valid_ids)
    normalized, normalized_gate, metadata = RUNNER._normalize_worker_artifact_after_gate(
        parsed,
        initial_gate,
        spec,
        "A",
        valid_ids,
    )

    assert metadata["applied"] is False
    assert normalized is parsed
    assert normalized_gate is initial_gate
