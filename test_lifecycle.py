"""
test_lifecycle.py — Invariant test suite for hashlock.py and packet_lifecycle.py.

Four test categories, zero exceptions required before wiring into any harness:

  1. Zero Leakage Rule       — builder metadata / hypothesized_verdict never in model payload
  2. High Sensitivity Rule   — single-char change propagates through all hash layers
  3. Execution Lock Guard    — ablation raises if status != frozen_pending_judge
  4. Label Integrity Guard   — model_labels blocked unless benchmark_locked

Run: python -m pytest test_lifecycle.py -v
"""

from datetime import datetime, timezone

import pytest

from hashlock import (
    FreezeRecord,
    canonical_serialize_packet,
    compute_combined_freeze_hash,
    compute_packet_hash,
    compute_prompt_hash,
    verify_freeze,
)
from packet_lifecycle import (
    BenchmarkStatus,
    BlindAblationResult,
    JudgeAdjudication,
    JudgeConfidence,
    ModelLabel,
    PacketRecord,
    accept_ablation_run,
    adjudicate,
    assign_model_label,
    build_model_visible_payload,
    freeze,
    move_to_diagnostic,
    strip_builder_metadata,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SAMPLE_PROMPT = "You are reviewing enterprise documents. Return ALLOW or ESCALATE."


def _make_raw_packet(**overrides) -> dict:
    base = {
        "scenario_id": "TEST-001",
        "action": {
            "type": "invoice_payment",
            "amount_usd": 218500,
            "description": "Hargrove Consulting — Invoice HGV-2024-0441",
        },
        "context": {
            "documents": [{"doc_id": "DOC-001", "content": "Payment policy §4.3"}]
        },
        # All of the following must never reach the model
        "expected_verdict":     "ALLOW",
        "hidden_ground_truth":  {"seam_type": "bec_bank_change_policy_satisfied"},
        "gold_answer":          {"verdict": "ALLOW", "correct_reasoning": "all gates closed"},
        "scoring_targets":      {"correct_reason_class": "bec_allow"},
        "hypothesized_verdict": "ALLOW",
        "builder_rationale":    "All bank-change policy gates are satisfied.",
        "builder_notes":        "BEC surface present but non-material.",
        "benchmark_status":     "candidate",
    }
    base.update(overrides)
    return base


def _make_freeze_record(packet: dict, prompt: str) -> FreezeRecord:
    ph  = compute_packet_hash(packet)
    prh = compute_prompt_hash(prompt)
    return FreezeRecord(
        frozen_packet_hash   = ph,
        frozen_prompt_hash   = prh,
        combined_freeze_hash = compute_combined_freeze_hash(ph, prh),
        frozen_at            = datetime.now(timezone.utc).isoformat(),
        freeze_confirmed_by  = "test_builder",
    )


def _make_record(status: BenchmarkStatus = BenchmarkStatus.CANDIDATE) -> PacketRecord:
    return PacketRecord(
        candidate_id          = "TEST-001",
        family_id             = "HARGROVE-BEC",
        variant_tag           = None,
        hypothesized_verdict  = "ALLOW",
        builder_rationale     = "All bank-change policy gates satisfied.",
        builder_notes         = "BEC surface present but non-material.",
        benchmark_status      = status,
    )


def _make_blind_run(fr: FreezeRecord, run_id: str = "run-001") -> BlindAblationResult:
    return BlindAblationResult(
        run_id        = run_id,
        model_id      = "gpt-5.4",
        condition     = "A-GPT",
        raw_verdict   = "ALLOW",
        raw_trace_ref = f"/artifacts/{run_id}/raw_output.txt",
        packet_hash   = fr.frozen_packet_hash,
        prompt_hash   = fr.frozen_prompt_hash,
        combined_hash = fr.combined_freeze_hash,
        run_timestamp = datetime.now(timezone.utc).isoformat(),
    )


def _locked_record() -> tuple[PacketRecord, FreezeRecord]:
    """Return a benchmark_locked record with one blind run completed."""
    raw = _make_raw_packet()
    rec = _make_record()
    fr  = _make_freeze_record(raw, SAMPLE_PROMPT)
    freeze(rec, fr)
    accept_ablation_run(rec, _make_blind_run(fr))
    adj = JudgeAdjudication(
        judge_adjudicated_verdict = "ALLOW",
        judge_confidence          = JudgeConfidence.HIGH,
        judge_rationale           = "All policy gates satisfied; BEC surface non-material.",
        adjudicated_at            = datetime.now(timezone.utc).isoformat(),
        adjudicated_by            = "judge_001",
    )
    adjudicate(rec, adj)
    return rec, fr


# ===========================================================================
# 1. ZERO LEAKAGE RULE
# ===========================================================================

class TestZeroLeakage:

    def test_payload_excludes_hypothesized_verdict(self):
        raw = _make_raw_packet()
        rec = _make_record()
        freeze(rec, _make_freeze_record(raw, SAMPLE_PROMPT))
        payload = build_model_visible_payload(rec, raw)
        assert "hypothesized_verdict" not in payload

    def test_payload_excludes_builder_rationale_and_notes(self):
        raw = _make_raw_packet()
        rec = _make_record()
        freeze(rec, _make_freeze_record(raw, SAMPLE_PROMPT))
        payload = build_model_visible_payload(rec, raw)
        assert "builder_rationale" not in payload
        assert "builder_notes"     not in payload

    def test_payload_excludes_expected_verdict_and_answer_keys(self):
        raw = _make_raw_packet()
        rec = _make_record()
        freeze(rec, _make_freeze_record(raw, SAMPLE_PROMPT))
        payload = build_model_visible_payload(rec, raw)
        assert "expected_verdict"    not in payload
        assert "gold_answer"         not in payload
        assert "hidden_ground_truth" not in payload
        assert "scoring_targets"     not in payload

    def test_payload_contains_only_action_and_context(self):
        raw = _make_raw_packet()
        rec = _make_record()
        freeze(rec, _make_freeze_record(raw, SAMPLE_PROMPT))
        payload = build_model_visible_payload(rec, raw)
        assert set(payload.keys()) == {"action", "context"}

    def test_canonical_serialize_excludes_all_metadata(self):
        raw        = _make_raw_packet()
        serialized = canonical_serialize_packet(raw)
        for forbidden in (
            "hypothesized_verdict", "builder_rationale", "expected_verdict",
            "hidden_ground_truth", "gold_answer", "scoring_targets",
        ):
            assert forbidden not in serialized, f"'{forbidden}' leaked into canonical serialization"

    def test_strip_builder_metadata_removes_all_protected_fields(self):
        raw     = _make_raw_packet()
        cleaned = strip_builder_metadata(raw)
        for forbidden in (
            "hypothesized_verdict", "builder_rationale", "builder_notes",
            "benchmark_status", "expected_verdict", "hidden_ground_truth",
            "gold_answer", "scoring_targets",
        ):
            assert forbidden not in cleaned, f"'{forbidden}' survived strip_builder_metadata"

    def test_strip_preserves_action_and_context(self):
        raw     = _make_raw_packet()
        cleaned = strip_builder_metadata(raw)
        assert "action"  in cleaned
        assert "context" in cleaned

    def test_metadata_values_do_not_appear_verbatim_in_payload_context(self):
        # Ensure the builder_rationale text doesn't sneak into context
        raw = _make_raw_packet()
        rec = _make_record()
        freeze(rec, _make_freeze_record(raw, SAMPLE_PROMPT))
        payload = build_model_visible_payload(rec, raw)
        payload_str = str(payload)
        assert "All bank-change policy gates are satisfied" not in payload_str
        assert "BEC surface present but non-material"       not in payload_str


# ===========================================================================
# 2. HIGH SENSITIVITY RULE
# ===========================================================================

class TestHighSensitivity:

    def test_single_int_change_in_action_changes_packet_hash(self):
        raw1 = _make_raw_packet()
        raw2 = _make_raw_packet()
        raw2["action"]["amount_usd"] = 218501
        assert compute_packet_hash(raw1) != compute_packet_hash(raw2)

    def test_single_char_change_in_context_changes_packet_hash(self):
        raw1 = _make_raw_packet()
        raw2 = _make_raw_packet()
        raw2["context"]["documents"][0]["content"] = "Payment policy §4.4"
        assert compute_packet_hash(raw1) != compute_packet_hash(raw2)

    def test_single_char_change_in_prompt_changes_prompt_hash(self):
        p1 = "Return ALLOW or ESCALATE."
        p2 = "Return ALLOW or ESCALATE!"
        assert compute_prompt_hash(p1) != compute_prompt_hash(p2)

    def test_packet_change_propagates_to_combined_hash(self):
        raw1 = _make_raw_packet()
        raw2 = _make_raw_packet()
        raw2["action"]["amount_usd"] = 218501
        prh  = compute_prompt_hash(SAMPLE_PROMPT)
        c1   = compute_combined_freeze_hash(compute_packet_hash(raw1), prh)
        c2   = compute_combined_freeze_hash(compute_packet_hash(raw2), prh)
        assert c1 != c2

    def test_prompt_change_propagates_to_combined_hash(self):
        raw = _make_raw_packet()
        ph  = compute_packet_hash(raw)
        c1  = compute_combined_freeze_hash(ph, compute_prompt_hash("Prompt A."))
        c2  = compute_combined_freeze_hash(ph, compute_prompt_hash("Prompt B."))
        assert c1 != c2

    def test_verify_freeze_detects_packet_mutation_after_freeze(self):
        raw = _make_raw_packet()
        fr  = _make_freeze_record(raw, SAMPLE_PROMPT)
        raw["action"]["amount_usd"] = 999999    # mutate after freeze
        assert verify_freeze(raw, SAMPLE_PROMPT, fr) is False

    def test_verify_freeze_detects_prompt_mutation_after_freeze(self):
        raw = _make_raw_packet()
        fr  = _make_freeze_record(raw, SAMPLE_PROMPT)
        assert verify_freeze(raw, SAMPLE_PROMPT + " (modified)", fr) is False

    def test_verify_freeze_passes_on_unchanged_inputs(self):
        raw = _make_raw_packet()
        fr  = _make_freeze_record(raw, SAMPLE_PROMPT)
        assert verify_freeze(raw, SAMPLE_PROMPT, fr) is True

    def test_metadata_change_does_not_affect_packet_hash(self):
        """Fields outside action/context are excluded and must not change the hash."""
        raw1 = _make_raw_packet()
        raw2 = _make_raw_packet(hypothesized_verdict="ESCALATE")
        assert compute_packet_hash(raw1) == compute_packet_hash(raw2)

    def test_scenario_id_change_does_not_affect_packet_hash(self):
        raw1 = _make_raw_packet(scenario_id="TEST-001")
        raw2 = _make_raw_packet(scenario_id="TEST-999")
        assert compute_packet_hash(raw1) == compute_packet_hash(raw2)


# ===========================================================================
# 3. EXECUTION LOCK GUARD
# ===========================================================================

class TestExecutionLockGuard:

    def test_ablation_blocked_on_candidate(self):
        raw = _make_raw_packet()
        fr  = _make_freeze_record(raw, SAMPLE_PROMPT)
        rec = _make_record(BenchmarkStatus.CANDIDATE)
        with pytest.raises(ValueError, match="frozen_pending_judge"):
            accept_ablation_run(rec, _make_blind_run(fr))

    def test_ablation_blocked_on_benchmark_locked(self):
        raw = _make_raw_packet()
        fr  = _make_freeze_record(raw, SAMPLE_PROMPT)
        rec, _ = _locked_record()
        with pytest.raises(ValueError, match="frozen_pending_judge"):
            accept_ablation_run(rec, _make_blind_run(fr))

    def test_ablation_blocked_on_diagnostic(self):
        raw = _make_raw_packet()
        fr  = _make_freeze_record(raw, SAMPLE_PROMPT)
        rec = _make_record(BenchmarkStatus.DIAGNOSTIC)
        with pytest.raises(ValueError, match="frozen_pending_judge"):
            accept_ablation_run(rec, _make_blind_run(fr))

    def test_ablation_blocked_on_retired(self):
        raw = _make_raw_packet()
        fr  = _make_freeze_record(raw, SAMPLE_PROMPT)
        rec = _make_record(BenchmarkStatus.RETIRED)
        with pytest.raises(ValueError, match="frozen_pending_judge"):
            accept_ablation_run(rec, _make_blind_run(fr))

    def test_ablation_allowed_on_frozen_pending_judge(self):
        raw = _make_raw_packet()
        rec = _make_record()
        fr  = _make_freeze_record(raw, SAMPLE_PROMPT)
        freeze(rec, fr)
        assert rec.benchmark_status == BenchmarkStatus.FROZEN_PENDING_JUDGE
        accept_ablation_run(rec, _make_blind_run(fr))
        assert len(rec.blind_ablation_results) == 1

    def test_build_payload_blocked_on_candidate(self):
        raw = _make_raw_packet()
        rec = _make_record(BenchmarkStatus.CANDIDATE)
        with pytest.raises(ValueError, match="frozen_pending_judge"):
            build_model_visible_payload(rec, raw)

    def test_build_payload_blocked_on_benchmark_locked(self):
        raw      = _make_raw_packet()
        rec, _fr = _locked_record()
        with pytest.raises(ValueError, match="frozen_pending_judge"):
            build_model_visible_payload(rec, raw)

    def test_build_payload_blocked_on_diagnostic(self):
        raw = _make_raw_packet()
        rec = _make_record(BenchmarkStatus.DIAGNOSTIC)
        with pytest.raises(ValueError, match="frozen_pending_judge"):
            build_model_visible_payload(rec, raw)


# ===========================================================================
# 4. LABEL INTEGRITY GUARD
# ===========================================================================

class TestLabelIntegrityGuard:

    def test_model_labels_blocked_on_candidate(self):
        rec = _make_record(BenchmarkStatus.CANDIDATE)
        with pytest.raises(ValueError, match="benchmark_locked"):
            assign_model_label(rec, "run-001", ModelLabel.KNEW)

    def test_model_labels_blocked_on_frozen_pending_judge(self):
        raw = _make_raw_packet()
        rec = _make_record()
        freeze(rec, _make_freeze_record(raw, SAMPLE_PROMPT))
        with pytest.raises(ValueError, match="benchmark_locked"):
            assign_model_label(rec, "run-001", ModelLabel.KNEW)

    def test_model_labels_blocked_on_diagnostic(self):
        rec = _make_record(BenchmarkStatus.DIAGNOSTIC)
        with pytest.raises(ValueError, match="benchmark_locked"):
            assign_model_label(rec, "run-001", ModelLabel.KNEW)

    def test_model_labels_blocked_on_retired(self):
        rec = _make_record(BenchmarkStatus.RETIRED)
        with pytest.raises(ValueError, match="benchmark_locked"):
            assign_model_label(rec, "run-001", ModelLabel.KNEW)

    def test_model_labels_allowed_at_benchmark_locked(self):
        rec, _fr = _locked_record()
        assign_model_label(rec, "run-001", ModelLabel.KNEW)
        assert rec.model_labels["run-001"] == ModelLabel.KNEW

    def test_all_label_values_accepted_at_benchmark_locked(self):
        for label in ModelLabel:
            rec, _fr = _locked_record()
            run_key = f"run-{label.value}"
            assign_model_label(rec, run_key, label)
            assert rec.model_labels[run_key] == label

    def test_low_confidence_adjudication_blocked(self):
        raw = _make_raw_packet()
        rec = _make_record()
        fr  = _make_freeze_record(raw, SAMPLE_PROMPT)
        freeze(rec, fr)
        accept_ablation_run(rec, _make_blind_run(fr))
        adj = JudgeAdjudication(
            judge_adjudicated_verdict = "ALLOW",
            judge_confidence          = JudgeConfidence.LOW,
            judge_rationale           = "Uncertain.",
            adjudicated_at            = datetime.now(timezone.utc).isoformat(),
            adjudicated_by            = "judge_001",
        )
        with pytest.raises(ValueError, match="LOW confidence"):
            adjudicate(rec, adj)
        assert rec.benchmark_status == BenchmarkStatus.FROZEN_PENDING_JUDGE

    def test_adjudication_without_blind_runs_blocked(self):
        raw = _make_raw_packet()
        rec = _make_record()
        fr  = _make_freeze_record(raw, SAMPLE_PROMPT)
        freeze(rec, fr)
        adj = JudgeAdjudication(
            judge_adjudicated_verdict = "ALLOW",
            judge_confidence          = JudgeConfidence.HIGH,
            judge_rationale           = "All gates closed.",
            adjudicated_at            = datetime.now(timezone.utc).isoformat(),
            adjudicated_by            = "judge_001",
        )
        with pytest.raises(ValueError, match="blind ablation run"):
            adjudicate(rec, adj)

    def test_diagnostic_cannot_accept_model_labels(self):
        rec = _make_record()
        move_to_diagnostic(rec, "contaminated pre-protocol")
        with pytest.raises(ValueError, match="benchmark_locked"):
            assign_model_label(rec, "run-001", ModelLabel.WRONG)


# ===========================================================================
# 5. TRANSITION GUARD COMPLETENESS
# ===========================================================================

class TestTransitionGuards:

    def test_freeze_only_from_candidate(self):
        raw = _make_raw_packet()
        fr  = _make_freeze_record(raw, SAMPLE_PROMPT)
        for status in (
            BenchmarkStatus.FROZEN_PENDING_JUDGE,
            BenchmarkStatus.DIAGNOSTIC,
            BenchmarkStatus.RETIRED,
        ):
            rec = _make_record(status)
            with pytest.raises(ValueError, match="candidate status"):
                freeze(rec, fr)

    def test_diagnostic_blocked_from_benchmark_locked(self):
        rec, _ = _locked_record()
        with pytest.raises(ValueError, match="benchmark_locked"):
            move_to_diagnostic(rec, "late discovery")

    def test_full_happy_path(self):
        raw = _make_raw_packet()
        rec = _make_record()
        assert rec.benchmark_status == BenchmarkStatus.CANDIDATE

        fr = _make_freeze_record(raw, SAMPLE_PROMPT)
        freeze(rec, fr)
        assert rec.benchmark_status == BenchmarkStatus.FROZEN_PENDING_JUDGE
        assert rec.freeze_record is not None

        accept_ablation_run(rec, _make_blind_run(fr, "run-001"))
        accept_ablation_run(rec, _make_blind_run(fr, "run-002"))
        assert len(rec.blind_ablation_results) == 2

        adj = JudgeAdjudication(
            judge_adjudicated_verdict = "ALLOW",
            judge_confidence          = JudgeConfidence.HIGH,
            judge_rationale           = "All bank-change policy gates satisfied.",
            adjudicated_at            = datetime.now(timezone.utc).isoformat(),
            adjudicated_by            = "judge_001",
        )
        adjudicate(rec, adj)
        assert rec.benchmark_status == BenchmarkStatus.BENCHMARK_LOCKED
        assert rec.adjudication.judge_adjudicated_verdict == "ALLOW"

        assign_model_label(rec, "run-001", ModelLabel.KNEW)
        assign_model_label(rec, "run-002", ModelLabel.LUCKY)
        assert rec.model_labels == {"run-001": ModelLabel.KNEW, "run-002": ModelLabel.LUCKY}

    def test_candidate_to_diagnostic_path(self):
        rec = _make_record()
        move_to_diagnostic(rec, "pre-protocol contamination")
        assert rec.benchmark_status == BenchmarkStatus.DIAGNOSTIC
        assert rec.status_reason    == "pre-protocol contamination"

    def test_frozen_pending_to_diagnostic_path(self):
        raw = _make_raw_packet()
        rec = _make_record()
        fr  = _make_freeze_record(raw, SAMPLE_PROMPT)
        freeze(rec, fr)
        move_to_diagnostic(rec, "judge found ambiguous evidence chain")
        assert rec.benchmark_status == BenchmarkStatus.DIAGNOSTIC
