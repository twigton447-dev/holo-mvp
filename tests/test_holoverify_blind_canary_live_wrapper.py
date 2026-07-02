import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "docs" / "benchmark" / "run_holoverify_blind_canary_live_2026_07_02.py"


def load_script():
    spec = importlib.util.spec_from_file_location("blind_canary_live_wrapper_test", SCRIPT_PATH)
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


def test_slot_order_enforced():
    script = load_script()
    script.assert_message_matches_slot(
        [{"role": "user", "content": "RUN LOCK: packet=BLIND turn=1 role=W1"}],
        "W1",
    )
    script.assert_message_matches_slot(
        [{"role": "user", "content": "SYSTEM ROLE: HoloVerify blind Gov actuator."}],
        "G1",
    )
    with pytest.raises(RuntimeError, match="slot_message_mismatch"):
        script.assert_message_matches_slot(
            [{"role": "user", "content": "RUN LOCK: packet=BLIND turn=1 role=W2"}],
            "W1",
        )


def test_worker_contract_failure_is_fail_closed():
    script = load_script()
    with pytest.raises(RuntimeError, match="W1_worker_contract_missing"):
        script.validate_live_output_contract(
            "W1",
            {
                "text": "boundary_closed=false\nsource=SRC-1\nreason=missing approval",
                "finish_reason": "stop",
            },
        )


def test_gov_length_finish_is_fail_closed():
    script = load_script()
    with pytest.raises(RuntimeError, match="G1_finish_reason_length"):
        script.validate_live_output_contract(
            "G1",
            {
                "text": "route_verdict=CONTINUE\nrepair_target=preserve",
                "finish_reason": "length",
            },
        )


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
