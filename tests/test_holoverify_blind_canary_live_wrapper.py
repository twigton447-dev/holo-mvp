import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest
from blind_lane_suite.static_guards import scan_import_closure_for_truth_reachability


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "docs" / "benchmark" / "run_holoverify_blind_canary_live_2026_07_02.py"
SCORER_PATH = REPO_ROOT / "docs" / "benchmark" / "score_holoverify_blind_canary_posthoc_2026_07_03.py"
CANONICAL_ONE_PACKET_RUN = (
    REPO_ROOT
    / "docs"
    / "benchmark"
    / "holoverify_blind_canary_live_runs_2026_07_02"
    / "run_20260703T005220Z"
)


def load_script():
    spec = importlib.util.spec_from_file_location("blind_canary_live_wrapper_test", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def load_scorer():
    spec = importlib.util.spec_from_file_location("blind_canary_posthoc_scorer_test", SCORER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_preflight_passes_without_provider_calls(tmp_path, monkeypatch):
    script = load_script()
    monkeypatch.setenv("XAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("MINIMAX_API_KEY", "dummy")

    report = script.preflight(tmp_path / "preflight")

    assert report["passed"] is True
    assert report["expected_provider_calls"] == 100
    assert report["checks"]["provider_calls_not_yet_made"] is True
    assert report["runtime_input_leakage_hits"] == []
    assert report["prompt_probe_leakage_hits"] == []
    assert report["scoring_map_access_control"]["live_wrapper_has_scoring_map_path"] is False
    assert "test_preflight_does_not_read_scoring_map_bytes" in report["scoring_map_access_control"]["preflight_read_guard_enforced_by"]
    assert report["posthoc_scoring_required_after_trace_freeze"] is True
    assert report["selector_policy"]["selector_policy_version"] == "SELECTOR_V3_DEPENDENCY_AWARE_REPAIR_2026_07_03"
    assert len(report["selector_policy"]["selector_policy_sha256"]) == 64
    assert report["worker_contract"]["worker_contract_version"] == "WORKER_CONTRACT_V2_ARTIFACT_FIRST_2026_07_03"
    assert len(report["worker_contract"]["worker_contract_sha256"]) == 64


def test_one_packet_preflight_limits_scope_to_five_calls(tmp_path, monkeypatch):
    script = load_script()
    monkeypatch.setenv("XAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("MINIMAX_API_KEY", "dummy")

    manifest_path = script.materialize_runtime_subset(tmp_path, 1)
    report = script.preflight(tmp_path / "preflight_one", manifest_path)

    assert report["passed"] is True
    assert report["packets"] == 1
    assert report["expected_provider_calls"] == 5
    assert report["checks"]["provider_calls_not_yet_made"] is True
    assert report["checks"]["content_contract_attempt_budget"] is True
    assert report["checks"]["live_run_attempt_budget"] is True


def test_one_packet_subset_can_select_second_opaque_packet(tmp_path):
    script = load_script()
    source = json.loads(script.RUNTIME_MANIFEST.read_text())

    manifest_path = script.materialize_runtime_subset(tmp_path, 1, packet_index=2)
    subset = json.loads(manifest_path.read_text())

    assert subset["packet_count"] == 1
    assert subset["subset_packet_start_index_1based"] == 2
    assert subset["packets"][0]["opaque_runtime_id"] == source["packets"][1]["opaque_runtime_id"]
    assert subset["packets"][0]["opaque_runtime_id"] != source["packets"][0]["opaque_runtime_id"]


def test_live_requires_exact_approval_before_preflight(monkeypatch):
    script = load_script()
    called = {"preflight": False}

    def fail_if_called(_run_dir):
        called["preflight"] = True
        raise AssertionError("preflight should not run on bad approval")

    monkeypatch.setattr(script, "preflight", fail_if_called)
    with pytest.raises(RuntimeError, match="approval_statement_mismatch"):
        script.run_live("approved")
    assert called["preflight"] is False


def test_one_packet_live_uses_separate_approval_sentence(monkeypatch):
    script = load_script()
    called = {"preflight": False}

    def fail_if_called(_run_dir, _runtime_manifest_path=None):
        called["preflight"] = True
        raise AssertionError("preflight should not run on bad approval")

    monkeypatch.setattr(script, "preflight", fail_if_called)
    with pytest.raises(RuntimeError, match="approval_statement_mismatch"):
        script.run_live(script.EXACT_APPROVAL_SENTENCE, packet_limit=1)
    assert called["preflight"] is False


def test_one_packet_approval_sentence_binds_packet_index(monkeypatch):
    script = load_script()
    assert "opaque packet index 2 only" in script.one_packet_approval_sentence(2)
    assert script.one_packet_approval_sentence(1) != script.one_packet_approval_sentence(2)

    called = {"preflight": False}

    def fail_if_called(_run_dir, _runtime_manifest_path=None):
        called["preflight"] = True
        raise AssertionError("preflight should not run on wrong packet-index approval")

    monkeypatch.setattr(script, "preflight", fail_if_called)
    with pytest.raises(RuntimeError, match="approval_statement_mismatch"):
        script.run_live(script.one_packet_approval_sentence(1), packet_limit=1, packet_index=2)
    assert called["preflight"] is False


def test_partial_batch_approval_sentence_binds_scope(monkeypatch):
    script = load_script()
    approval = script.scoped_approval_sentence(packet_limit=3, packet_index=10)

    assert "HOLOVERIFY_BLIND_CANARY_3PKT_RUNTIME_FIREWALL_V0" in approval
    assert "opaque packet indices 10-12 only" in approval
    assert "exactly 15 provider calls" in approval
    assert "W1 xai/grok-3-mini x3" in approval
    assert "W3 minimax/MiniMax-M2.5-highspeed x3" in approval
    assert approval != script.EXACT_APPROVAL_SENTENCE

    called = {"preflight": False}

    def fail_if_called(_run_dir, _runtime_manifest_path=None):
        called["preflight"] = True
        raise AssertionError("preflight should not run on wrong batch approval")

    monkeypatch.setattr(script, "preflight", fail_if_called)
    with pytest.raises(RuntimeError, match="approval_statement_mismatch"):
        script.run_live(script.EXACT_APPROVAL_SENTENCE, packet_limit=3, packet_index=10)
    assert called["preflight"] is False


def test_slot_order_enforced():
    script = load_script()
    script.assert_message_matches_slot(
        [{"role": "user", "content": "RUN LOCK: packet=BLIND turn=1 role=W1"}],
        "W1",
    )
    script.assert_message_matches_slot(
        [
            {"role": "system", "content": "Data formatting task."},
            {"role": "user", "content": "status_values:\nroute_verdict=CONTINUE"},
        ],
        "G1",
    )
    with pytest.raises(RuntimeError, match="slot_message_mismatch"):
        script.assert_message_matches_slot(
            [{"role": "user", "content": "RUN LOCK: packet=BLIND turn=1 role=W2"}],
            "W1",
        )


def test_worker_contract_failure_is_fail_closed():
    script = load_script()
    with pytest.raises(RuntimeError, match="W1_worker_contract_bad_prefix"):
        script.validate_live_output_contract(
            "W1",
            {
                "text": "boundary_closed=false\nsource=SRC-1\nreason=missing approval",
                "finish_reason": "stop",
            },
        )


def test_worker_output_must_start_with_worker_role():
    script = load_script()
    with pytest.raises(script.BLIND.BlindRunnerContentFailure, match="W3_worker_contract_bad_prefix"):
        script.validate_live_output_contract(
            "W3",
            {
                "text": "\n".join(
                    [
                        "Here is the answer:",
                        "worker_role=W3",
                        "verification_verdict=ALLOW",
                        "binding_class=SOURCE_BOUNDARY_CLOSED",
                        "action_boundary=closed by current source",
                        "cited_evidence=SRC-1",
                        "final_answer=ALLOW because the cited source closes the current action boundary.",
                    ]
                ),
                "finish_reason": "stop",
            },
        )


def test_worker_output_role_must_match_slot():
    script = load_script()
    with pytest.raises(script.BLIND.BlindRunnerContentFailure, match="W3_worker_contract_bad_role:W2"):
        script.validate_live_output_contract(
            "W3",
            {
                "text": "\n".join(
                    [
                        "worker_role=W3",
                        "worker_role=W2",
                        "verification_verdict=ALLOW",
                        "binding_class=SOURCE_BOUNDARY_CLOSED",
                        "action_boundary=closed by current source",
                        "cited_evidence=SRC-1",
                        "final_answer=ALLOW because the cited source closes the current action boundary.",
                    ]
                ),
                "finish_reason": "stop",
            },
        )


def test_gov_length_finish_is_fail_closed():
    script = load_script()
    with pytest.raises(script.BLIND.BlindRunnerContentFailure, match="G1_finish_reason_length"):
        script.validate_live_output_contract(
            "G1",
            {
                "text": "route_verdict=CONTINUE\nrepair_target=preserve",
                "finish_reason": "length",
        },
    )


def test_unclosed_thinking_block_strips_to_empty_and_fails_closed():
    script = load_script()
    response = {
        "text": script.strip_thinking_blocks("<think>\nI will reason until the model budget ends."),
        "finish_reason": "stop",
    }
    assert response["text"] == ""
    with pytest.raises(script.BLIND.BlindRunnerContentFailure, match="G2_empty_text"):
        script.validate_live_output_contract("G2", response)


def test_w3_hidden_thinking_only_strips_to_empty_and_fails_closed():
    script = load_script()
    raw = "<think>\nI will debate the source seam until the output budget ends.\n</think>\n"
    response = {
        "text": script.strip_thinking_blocks(raw),
        "finish_reason": "stop",
    }

    assert response["text"] == ""
    with pytest.raises(script.BLIND.BlindRunnerContentFailure, match="W3_empty_text"):
        script.validate_live_output_contract("W3", response)


def test_w3_hidden_thinking_plus_valid_artifact_passes_after_strip():
    script = load_script()
    raw = "\n".join(
        [
            "<think>ignore this hidden reasoning</think>",
            "worker_role=W3",
            "verification_verdict=ESCALATE",
            "binding_class=SOURCE_BOUNDARY_OPEN",
            "action_boundary=invoice ID link remains unresolved",
            "cited_evidence=SRC-1|SRC-2",
            "open_blockers=invoice ID link missing",
            "final_answer=ESCALATE because the visible source support leaves the action boundary open.",
        ]
    )
    text = script.strip_thinking_blocks(raw)

    assert text.startswith("worker_role=W3")
    script.validate_live_output_contract("W3", {"text": text, "finish_reason": "stop"})


def test_content_failure_is_not_retried_by_blind_runner():
    script = load_script()
    calls = {"count": 0}
    retry_log = []

    def transport(_messages):
        calls["count"] += 1
        raise script.BLIND.BlindRunnerContentFailure("contract_failed")

    with pytest.raises(script.BLIND.BlindRunnerContentFailure, match="contract_failed"):
        script.BLIND._call_transport(transport, [{"role": "user", "content": "x"}], retry_log)
    assert calls["count"] == 1
    assert retry_log == []


def test_final_compiler_uses_larger_output_budget():
    script = load_script()
    assert script.max_output_tokens_for_slot("W1") == script.MAX_OUTPUT_TOKENS
    assert script.max_output_tokens_for_slot("G1") == script.GOV_MAX_OUTPUT_TOKENS
    assert script.max_output_tokens_for_slot("G2") == script.GOV_MAX_OUTPUT_TOKENS
    assert script.GOV_MAX_OUTPUT_TOKENS == script.MAX_OUTPUT_TOKENS
    assert script.max_output_tokens_for_slot("W3") == script.FINAL_COMPILER_MAX_OUTPUT_TOKENS
    assert script.FINAL_COMPILER_MAX_OUTPUT_TOKENS > script.MAX_OUTPUT_TOKENS


def test_gov_prompt_is_truth_free_copy_contract():
    script = load_script()
    payload = {"packet_id": "BLIND-TEST", "documents": []}
    worker_row = {"gate_result": {"passed": True, "failures": []}}
    messages = script.BLIND._build_gov_messages(payload, worker_row, {"turns_completed": []})
    joined = "\n".join(message["content"] for message in messages)

    assert messages[0]["role"] == "system"
    assert "status_values:" in joined
    assert "route_verdict=CONTINUE" in joined
    assert "repair_target=preserve source-grounded reasoning" in joined
    assert "blocked_move=do not invent source IDs" in joined
    assert "BLIND_GATE_SUMMARY" not in joined
    assert "Gov actuator" not in joined
    assert "HoloGov" not in joined
    assert "COPY MODE" not in joined
    assert "copy exactly" not in joined
    assert "RUN LOCK" not in joined
    assert "role=GOV" not in joined
    assert "hidden thinking" not in joined
    assert len(joined) < 900
    assert "ALLOW" not in joined
    assert "ESCALATE" not in joined
    assert "packet_truth" not in joined


def test_w3_prompt_uses_final_compiler_output_firewall():
    script = load_script()
    payload = {"packet_id": "BLIND-TEST", "documents": [{"doc_id": "SRC-1", "text": "fixture"}]}
    messages = script.BLIND._build_worker_messages(
        payload,
        3,
        {"turns_completed": []},
        {"route_verdict": "CONTINUE", "repair_target": "preserve", "blocked_move": "do not invent"},
    )
    joined = "\n".join(message["content"] for message in messages)

    assert messages[0]["role"] == "system"
    assert "W3 ARTIFACT-FIRST CONTRACT V2" in joined
    assert "W3 ARTIFACT-FIRST GUARD" in joined
    assert "The first output characters must be exactly: worker_role=W3" in joined
    assert "Do not emit hidden thinking" in joined
    assert "If uncertain, still emit the compact artifact immediately." in joined
    assert "Represent ambiguity only with verification_verdict, binding_class, open_blockers, and final_answer." in joined
    assert "First visible output line must be worker_role=W3" in joined
    assert "packet_truth" not in joined


def test_valid_contract_passes():
    script = load_script()
    script.validate_live_output_contract(
        "W3",
        {
            "text": "\n".join(
                [
                    "worker_role=W3",
                    "verification_verdict=ALLOW",
                    "action_boundary=closed by current source",
                    "binding_class=SOURCE_BOUNDARY_CLOSED",
                    "cited_evidence=SRC-1",
                    "final_answer=The current source closes the exact requested action boundary.",
                ]
            ),
            "finish_reason": "stop",
        },
    )
    script.validate_live_output_contract(
        "G2",
        {
            "text": "\n".join(
                [
                    "route_verdict=CONTINUE",
                    "repair_target=preserve source grounded reasoning",
                    "blocked_move=do not invent source IDs",
                ]
            ),
            "finish_reason": "stop",
        },
    )


def test_pass_condition_uses_scoped_expected_call_count():
    source = SCRIPT_PATH.read_text()
    assert "len(transport.provider_rows) == expected_call_count" in source
    assert "len(transport.provider_rows) == EXPECTED_CALL_COUNT" not in source


def test_live_wrapper_does_not_keep_scoring_map_path_or_posthoc_scorer():
    source = SCRIPT_PATH.read_text()

    assert "SCORING_MAP =" not in source
    assert "def posthoc_score" not in source
    assert "load_json(SCORING_MAP)" not in source
    assert "posthoc_scoring_required_after_trace_freeze" in source


def test_preflight_does_not_read_scoring_map_bytes(tmp_path, monkeypatch):
    script = load_script()
    monkeypatch.setenv("XAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("MINIMAX_API_KEY", "dummy")
    scoring_map_path = script.BENCHMARK_ROOT / "holoverify_blind_canary_scoring_map_2026_07_02.json"
    real_sha256_file = script.sha256_file

    def guarded_sha256_file(path):
        assert Path(path).resolve() != scoring_map_path.resolve()
        return real_sha256_file(path)

    monkeypatch.setattr(script, "sha256_file", guarded_sha256_file)
    report = script.preflight(tmp_path / "preflight_no_scoring_map_read")

    assert report["passed"] is True
    assert report["scoring_map_access_control"]["live_wrapper_has_scoring_map_path"] is False


def test_current_head_reports_clear_git_preflight_blocker(monkeypatch):
    script = load_script()

    def broken_git(*_args, **_kwargs):
        raise subprocess.CalledProcessError(128, ["git", "rev-parse", "HEAD"])

    monkeypatch.setattr(script.subprocess, "check_output", broken_git)
    with pytest.raises(RuntimeError, match="git_head_unavailable: preflight requires a healthy git checkout"):
        script.current_head()


def test_posthoc_scorer_binds_score_to_frozen_trace_hashes(tmp_path):
    scorer = load_scorer()
    for name in (
        "TRACE_CALLS.jsonl",
        "TRACE_PROVIDER_CALLS.jsonl",
        "blind_canary_runtime_results.json",
        "blind_canary_live_summary.json",
    ):
        shutil.copyfile(CANONICAL_ONE_PACKET_RUN / name, tmp_path / name)

    report = scorer.posthoc_score(tmp_path)
    binding = report["trace_binding"]

    assert report["classification"] == "HOLOVERIFY_BLIND_CANARY_POSTHOC_SCORE_TRACE_BOUND_V1"
    assert report["scoring_map_loaded_after_trace_hash_binding"] is True
    assert binding["trace_calls_sha256"] == scorer.sha256_file(tmp_path / "TRACE_CALLS.jsonl")
    assert binding["trace_provider_calls_sha256"] == scorer.sha256_file(tmp_path / "TRACE_PROVIDER_CALLS.jsonl")
    assert binding["runtime_results_sha256"] == scorer.sha256_file(tmp_path / "blind_canary_runtime_results.json")
    assert binding["live_summary_sha256"] == scorer.sha256_file(tmp_path / "blind_canary_live_summary.json")
    assert report["packet_count"] == 1
    assert report["correct_count"] == 1
    assert report["incorrect_count"] == 0


def test_live_wrapper_import_closure_scan_has_only_detector_literals():
    findings = scan_import_closure_for_truth_reachability(SCRIPT_PATH, repo_root=REPO_ROOT)
    allowed_detector_names = {"packet_truth", "knew_terms", "allow_rule", "esc_rule"}
    unexpected = [
        finding
        for finding in findings
        if finding.get("kind") != "forbidden_field_string"
        or finding.get("name") not in allowed_detector_names
    ]

    assert unexpected == []
