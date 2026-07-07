import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "docs" / "benchmark" / "run_holoverify_blind_120_live_2026_07_03.py"


def load_script():
    spec = importlib.util.spec_from_file_location("blind_120_live_wrapper_test", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_120_preflight_passes_without_provider_calls(tmp_path, monkeypatch):
    script = load_script()
    monkeypatch.setenv("XAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("MINIMAX_API_KEY", "dummy")

    report = script.preflight(tmp_path / "preflight")

    assert report["classification"] == "HOLOVERIFY_BLIND_120_LIVE_PREFLIGHT_V0"
    assert report["passed"] is True
    assert report["freeze_root_sha256"] == script.FREEZE_ROOT_SHA256
    assert report["runtime_manifest_sha256"] == script.EXPECTED_RUNTIME_MANIFEST_SHA256
    assert report["packets"] == 120
    assert report["expected_provider_calls"] == 600
    assert report["checks"]["provider_calls_not_yet_made"] is True
    assert report["checks"]["solo_calls_disabled"] is True
    assert report["checks"]["judge_calls_disabled"] is True
    assert report["runtime_input_leakage_hits"] == []
    assert report["prompt_probe_leakage_hits"] == []
    assert report["scoring_map_access_control"]["live_wrapper_has_scoring_map_path"] is False
    assert "test_preflight_does_not_read_120_scoring_map_bytes" in report["scoring_map_access_control"]["preflight_read_guard_enforced_by"]
    assert report["posthoc_scoring_required_after_trace_freeze"] is True
    assert report["selector_policy"]["selector_policy_version"] == "SELECTOR_V9_GENERIC_BLOCKER_RESOLUTION_2026_07_06"
    assert report["selector_policy"]["selector_policy_sha256"] == "cb53549bcc01d882836fc47e68e1ec5610b302cdbd8ddfd1967f7fac5a235416"
    assert report["worker_contract"]["worker_contract_version"] == "WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04"
    assert len(report["worker_contract"]["worker_contract_sha256"]) == 64


def test_120_one_packet_preflight_limits_scope_to_five_calls(tmp_path, monkeypatch):
    script = load_script()
    monkeypatch.setenv("XAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("MINIMAX_API_KEY", "dummy")

    script.configure_runtime()
    manifest_path = script.CANARY.materialize_runtime_subset(tmp_path, 1)
    report = script.preflight(tmp_path / "preflight_one", manifest_path)

    assert report["passed"] is True
    assert report["packets"] == 1
    assert report["expected_provider_calls"] == 5
    assert report["checks"]["provider_calls_not_yet_made"] is True
    assert report["checks"]["content_contract_attempt_budget"] is True
    assert report["checks"]["live_run_attempt_budget"] is True


def test_120_approval_sentence_binds_full_scope():
    script = load_script()
    approval = script.scoped_approval_sentence()

    assert "HOLOVERIFY_BLIND_120_RUNTIME_FIREWALL_V0" in approval
    assert script.FREEZE_ROOT_SHA256 in approval
    assert script.EXPECTED_RUNTIME_MANIFEST_SHA256 in approval
    assert "exactly 600 provider calls" in approval
    assert "W1 xai/grok-3-mini x120" in approval
    assert "W3 minimax/MiniMax-M2.5-highspeed x120" in approval
    assert "No judges, no solo, no scoring map before trace freeze" in approval


def test_120_partial_batch_approval_sentence_binds_scope():
    script = load_script()
    approval = script.scoped_approval_sentence(packet_limit=3, packet_index=10)

    assert "HOLOVERIFY_BLIND_120_3PKT_RUNTIME_FIREWALL_V0" in approval
    assert "opaque packet indices 10-12 only" in approval
    assert "exactly 15 provider calls" in approval
    assert "W1 xai/grok-3-mini x3" in approval
    assert "W3 minimax/MiniMax-M2.5-highspeed x3" in approval
    assert approval != script.EXACT_APPROVAL_SENTENCE


def test_120_registered_batches_cover_all_packets_without_overlap():
    script = load_script()
    seen = []
    for batch_number in range(1, 13):
        scope = script.batch_scope(batch_number)
        assert scope["batch_number"] == batch_number
        assert scope["batch_count"] == 12
        assert scope["batch_size"] == 10
        assert scope["packet_limit"] == 10
        assert scope["expected_provider_calls"] == 50
        assert f"HOLOVERIFY_BLIND_120_10PKT_RUNTIME_FIREWALL_V0" in scope["approval_sentence"]
        assert f"opaque packet indices {scope['packet_index']}-{scope['packet_index_end']} only" in scope["approval_sentence"]
        seen.extend(range(scope["packet_index"], scope["packet_index_end"] + 1))

    assert seen == list(range(1, 121))


def test_120_batch_number_bounds():
    script = load_script()
    assert script.packet_index_for_batch(1) == 1
    assert script.packet_index_for_batch(12) == 111
    with pytest.raises(ValueError, match="batch_number must be 1-12"):
        script.packet_index_for_batch(0)
    with pytest.raises(ValueError, match="batch_number must be 1-12"):
        script.packet_index_for_batch(13)


def test_120_live_wrapper_does_not_keep_scoring_map_path_or_posthoc_scorer():
    source = SCRIPT_PATH.read_text()

    assert "SCORING_MAP =" not in source
    assert "def posthoc_score" not in source
    assert "load_json(SCORING_MAP)" not in source
    assert "posthoc_scoring_required_after_trace_freeze" not in source
    assert "score_holoverify_blind_120_posthoc_2026_07_03.py" in source


def test_preflight_does_not_read_120_scoring_map_bytes(tmp_path, monkeypatch):
    script = load_script()
    monkeypatch.setenv("XAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("MINIMAX_API_KEY", "dummy")
    scoring_map_path = (
        script.BENCHMARK_ROOT
        / "holoverify_blind_120_bank_2026_07_03"
        / "holoverify_blind_120_scoring_map_2026_07_03.json"
    )
    real_sha256_file = script.CANARY.sha256_file

    def guarded_sha256_file(path):
        assert Path(path).resolve() != scoring_map_path.resolve()
        return real_sha256_file(path)

    monkeypatch.setattr(script.CANARY, "sha256_file", guarded_sha256_file)
    report = script.preflight(tmp_path / "preflight_no_scoring_map_read")

    assert report["passed"] is True
    assert report["scoring_map_access_control"]["live_wrapper_has_scoring_map_path"] is False


def test_120_live_rejects_canary_approval_before_preflight(monkeypatch):
    script = load_script()
    canary_approval = script.EXACT_APPROVAL_SENTENCE.replace(
        "HOLOVERIFY_BLIND_120_RUNTIME_FIREWALL_V0",
        "HOLOVERIFY_BLIND_CANARY_20PKT_RUNTIME_FIREWALL_V0",
    )
    called = {"preflight": False}

    def fail_if_called(_run_dir, _runtime_manifest_path=None):
        called["preflight"] = True
        raise AssertionError("preflight should not run on bad approval")

    script.configure_runtime()
    monkeypatch.setattr(script.CANARY, "preflight", fail_if_called)
    with pytest.raises(RuntimeError, match="approval_statement_mismatch"):
        script.run_live(canary_approval)
    assert called["preflight"] is False
