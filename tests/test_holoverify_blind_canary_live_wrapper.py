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
