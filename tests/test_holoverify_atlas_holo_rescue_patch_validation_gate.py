import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "docs" / "benchmark" / "run_holoverify_atlas_holo_rescue_live_2026_07_03.py"


def load_script():
    spec = importlib.util.spec_from_file_location("atlas_holo_rescue_patch_validation_test", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_atlas_approval_sentence_binds_selector_patch_validation_scope():
    script = load_script()
    approval = script.scoped_approval_sentence()
    selector = script.CANARY.BLIND.selector_policy_identity()
    worker_contract = script.CANARY.BLIND.worker_contract_identity()

    assert script.LANE_LABEL in approval
    assert script.FREEZE_ROOT_SHA256 in approval
    assert script.EXPECTED_RUNTIME_MANIFEST_SHA256 in approval
    assert "exactly 60 provider calls" in approval
    assert "W1 xai/grok-3-mini x12" in approval
    assert "W3 minimax/MiniMax-M2.5-highspeed x12" in approval
    assert selector["selector_policy_version"] in approval
    assert selector["selector_policy_sha256"] in approval
    assert worker_contract["worker_contract_version"] in approval
    assert worker_contract["worker_contract_sha256"] in approval
    assert "PATCH VALIDATION ONLY" in approval
    assert "not fresh benchmark evidence" in approval
    assert "No judges, no solo, no scoring map before trace freeze" in approval


def test_atlas_preflight_stamps_patch_validation_falsifier(tmp_path, monkeypatch):
    script = load_script()
    monkeypatch.setenv("XAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("MINIMAX_API_KEY", "dummy")

    report = script.preflight(tmp_path / "preflight")

    assert report["passed"] is True
    assert report["expected_provider_calls"] == 60
    assert report["patch_validation_scope"] == script.PATCH_VALIDATION_SCOPE
    assert "does not correct the known failed packet" in report["patch_validation_falsifier"]
    assert report["selector_policy"]["selector_policy_version"] == "SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03"
    assert len(report["selector_policy"]["selector_policy_sha256"]) == 64
    assert report["worker_contract"]["worker_contract_version"] == "WORKER_CONTRACT_V2_ARTIFACT_FIRST_2026_07_03"
    assert len(report["worker_contract"]["worker_contract_sha256"]) == 64
