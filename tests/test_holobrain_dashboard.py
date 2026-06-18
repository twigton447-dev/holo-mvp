from pathlib import Path

from fastapi.testclient import TestClient

import main


class FakeBrain:
    _client = None

    def get_capsule(self, capsule_id):
        assert capsule_id == "canonical-capsule"
        return {
            "capsule_id": capsule_id,
            "email": "taylor@example.com",
            "name": "Taylor",
            "mode": "personal",
            "created_at": "2026-06-01T00:00:00Z",
            "last_active": "2026-06-17T00:00:00Z",
        }

    def get_capsule_context(self, capsule_id):
        assert capsule_id == "canonical-capsule"
        return {
            "_password_hash": "do-not-return-this",
            "project": "HoloChat",
            "api_token_note": "do-not-return-either",
        }

    def load_life_context(self, capsule_id):
        assert capsule_id == "canonical-capsule"
        return [{"category": "work", "key": "focus", "value": "Build Holo", "confidence": 0.9}]

    def list_sessions(self, capsule_id, limit=40):
        assert capsule_id == "canonical-capsule"
        return [{
            "session_id": "session-1234567890",
            "created_at": "2026-06-16T00:00:00Z",
            "last_active": "2026-06-17T00:00:00Z",
            "turn_count": 3,
            "title": "Memory repair",
            "preview": "Memory repair",
        }]

    def load_last_consolidation(self, capsule_id):
        assert capsule_id == "canonical-capsule"
        return {
            "session_id": "session-1234567890",
            "created_at": "2026-06-17T00:00:00Z",
            "what_changed": "Memory link verified",
            "what_surfaced": "",
            "open_threads": [],
            "captain_note": "Continue carefully",
        }

    def list_artifacts(self, capsule_id, limit=50):
        assert capsule_id == "canonical-capsule"
        return [{"artifact_id": "artifact-1", "title": "Plan", "artifact_type": "html"}]


def test_holobrain_endpoint_requires_auth(monkeypatch):
    monkeypatch.setattr(main, "get_capsule_from_request", lambda header: None)
    client = TestClient(main.app)

    response = client.get("/v1/holo-brain")

    assert response.status_code == 401


def test_holobrain_endpoint_uses_token_capsule_and_redacts_sensitive_context(monkeypatch):
    monkeypatch.setattr(main, "_capsule_brain", FakeBrain())
    monkeypatch.setattr(
        main,
        "get_capsule_from_request",
        lambda header: {"sub": "canonical-capsule", "email": "alias@example.com", "mode": "personal"},
    )
    client = TestClient(main.app)

    response = client.get("/v1/holo-brain", headers={"Authorization": "Bearer test"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["capsule"]["id"] == "canonical-capsule"
    assert payload["capsule"]["email_masked"] == "t***r@example.com"
    assert payload["capsule_context"]["count"] == 3
    assert payload["capsule_context"]["redacted_count"] == 2
    assert payload["life_context"]["count"] == 1
    assert payload["sessions"]["count"] == 1
    assert payload["consolidations"]["count"] == 1
    assert payload["artifacts"]["count"] == 1
    assert "do-not-return-this" not in str(payload)
    assert "do-not-return-either" not in str(payload)


def test_holobuild_endpoint_requires_auth(monkeypatch):
    monkeypatch.setattr(main, "get_capsule_from_request", lambda header: None)
    client = TestClient(main.app)

    response = client.get("/v1/holo-build")

    assert response.status_code == 401


def test_holobuild_endpoint_returns_sanitized_specs_and_trace(monkeypatch, tmp_path):
    specs_dir = tmp_path / "specs"
    results_dir = tmp_path / "builder_results"
    specs_dir.mkdir()
    results_dir.mkdir()
    (specs_dir / "TEST_spec.json").write_text("""{
      "scenario_id": "TEST-HB-001",
      "domain": "AP",
      "target_verdict": "ALLOW",
      "packet_format": "payment_email",
      "artifact_placement_brief": {"minimum_internal_documents": 4}
    }""")
    (results_dir / "builder_TEST-HB-001.json").write_text("""{
      "builder_id": "builder_TEST-HB-001",
      "scenario_id": "TEST-HB-001",
      "packet_format": "payment_email",
      "builder_status": "BUILDER_EXHAUSTED",
      "converged": false,
      "retire_signal": false,
      "exit_reason": "max_turns",
      "turns_completed": 2,
      "qa_turn_count": 1,
      "qa_deltas": [3],
      "provider_fallback_used": false,
      "governor_briefs": [{
        "after_turn": 2,
        "governor_provider": "anthropic",
        "overall_trajectory": "IMPROVING",
        "highest_risk_category": "overfit_risk",
        "brief_for_builder": "Make the invoice evidence less answer-key shaped."
      }],
      "turn_history": [{
        "turn_number": 1,
        "turn_type": "BUILDER",
        "provider": "openai",
        "model_id": "gpt-4o-mini",
        "elapsed_ms": 12,
        "input_tokens": 100,
        "output_tokens": 50,
        "draft": {"raw": "must not leak"}
      }, {
        "turn_number": 2,
        "turn_type": "INTERNAL_QA_ATTACKER",
        "provider": "google",
        "model_id": "gemini-2.5-flash-lite",
        "elapsed_ms": 14,
        "input_tokens": 80,
        "output_tokens": 40,
        "assessment": "NEEDS_REPAIR",
        "verdict": "ESCALATE",
        "critical_findings": "The callback record is too conclusory.",
        "categories": {"overfit_risk": "HIGH"}
      }],
      "final_draft": {"raw": "must not leak"},
      "total_tokens": {"input": 180, "output": 90},
      "timestamp": "2026-06-17T00:00:00Z"
    }""")
    monkeypatch.setattr(main, "_HOLO_BUILD_SPECS_DIR", specs_dir)
    monkeypatch.setattr(main, "_HOLO_BUILD_RESULT_DIRS", (results_dir,))
    monkeypatch.setattr(
        main,
        "get_capsule_from_request",
        lambda header: {"sub": "canonical-capsule", "email": "taylor@example.com"},
    )
    client = TestClient(main.app)

    response = client.get("/v1/holo-build", headers={"Authorization": "Bearer test"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "read_only"
    assert payload["live_runs_enabled"] is False
    assert payload["specs"][0]["scenario_id"] == "TEST-HB-001"
    assert payload["runs"][0]["builder_status"] == "BUILDER_EXHAUSTED"
    assert payload["runs"][0]["turn_history"][1]["high_categories"] == ["overfit_risk"]
    assert payload["runs"][0]["governor_briefs"][0]["highest_risk_category"] == "overfit_risk"
    assert "must not leak" not in str(payload)
    assert "draft" not in str(payload)
    assert "final_draft" not in str(payload)


def test_holobuild_live_run_endpoint_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("HOLOBUILD_LIVE_RUNS", raising=False)
    monkeypatch.setattr(
        main,
        "get_capsule_from_request",
        lambda header: {"sub": "canonical-capsule", "email": "taylor@example.com"},
    )
    client = TestClient(main.app)

    response = client.post(
        "/v1/holo-build/runs",
        headers={"Authorization": "Bearer test"},
        json={"spec_file": "TEST_spec.json"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "HoloBuild live runs are disabled."


def test_holobuild_job_runner_captures_live_events_and_sanitized_result(monkeypatch, tmp_path):
    specs_dir = tmp_path / "specs"
    results_dir = tmp_path / "builder_results"
    specs_dir.mkdir()
    results_dir.mkdir()
    (specs_dir / "TEST_spec.json").write_text("""{
      "scenario_id": "TEST-HB-LIVE",
      "domain": "AP",
      "target_verdict": "ALLOW"
    }""")
    monkeypatch.setattr(main, "_HOLO_BUILD_SPECS_DIR", specs_dir)
    monkeypatch.setattr(main, "_HOLO_BUILD_RESULT_DIRS", (results_dir,))
    with main._holo_build_jobs_lock:
        main._holo_build_jobs.clear()

    job = main._create_holobuild_job("TEST_spec.json", 11, False, [])

    def fake_runner(spec, seed=None, force_max_turns=False, skip_providers=None):
        print("Turn 1 | openai | BUILDER -> draft rev=1")
        print("Turn 2 | anthropic | INTERNAL_QA -> NEEDS_REPAIR")
        print("Governor (google): IMPROVING risk_cat=overfit_risk")
        return {
            "builder_id": "builder_TEST-HB-LIVE",
            "scenario_id": spec["scenario_id"],
            "packet_format": "payment_email",
            "builder_status": "BUILDER_CONVERGED",
            "converged": True,
            "retire_signal": False,
            "exit_reason": "convergence",
            "turns_completed": 2,
            "qa_turn_count": 1,
            "qa_deltas": [0],
            "provider_fallback_used": False,
            "governor_briefs": [{
                "after_turn": 2,
                "governor_provider": "google",
                "overall_trajectory": "IMPROVING",
                "highest_risk_category": "overfit_risk",
                "brief_for_builder": "Tighten the clearing artifact.",
            }],
            "turn_history": [{
                "turn_number": 1,
                "turn_type": "BUILDER",
                "provider": "openai",
                "model_id": "gpt-4o-mini",
                "elapsed_ms": 5,
                "input_tokens": 10,
                "output_tokens": 20,
                "draft": {"raw": "must not leak"},
            }],
            "final_draft": {"raw": "must not leak"},
            "total_tokens": {"input": 10, "output": 20},
            "timestamp": "2026-06-17T00:00:00Z",
        }

    main._run_holobuild_job(
        job["job_id"],
        "TEST_spec.json",
        11,
        False,
        [],
        runner=fake_runner,
    )

    snapshot = main._snapshot_holobuild_job(job["job_id"])
    assert snapshot["status"] == "completed"
    assert snapshot["result"]["builder_status"] == "BUILDER_CONVERGED"
    assert snapshot["result_file"] == "builder_TEST-HB-LIVE.json"
    assert (results_dir / "builder_TEST-HB-LIVE.json").exists()
    event_text = str(snapshot["events"])
    assert "Turn 1 | openai | BUILDER" in event_text
    assert "Governor (google): IMPROVING" in event_text
    assert "must not leak" not in str(snapshot)
    assert "final_draft" not in str(snapshot["result"])


def test_frontend_has_holobrain_button_and_render_path():
    html = Path("frontend/chat.html").read_text()

    assert 'id="holobrain-toggle"' in html
    assert 'title="Open engine data"' in html
    assert ">Engine data</button>" in html
    assert 'id="holobrain-panel"' in html
    assert 'id="holobrain-resize-handle"' in html
    assert 'title="Drag to resize engine data"' in html
    assert "initEnginePanelResize()" in html
    assert "setEnginePanelWidth(window.innerWidth - moveEvent.clientX)" in html
    assert "holo_engine_panel_width" in html
    assert "Engine runtime" in html
    assert 'fetch("/v1/holo-brain"' in html
    assert 'fetch("/v1/holo-build"' in html
    assert "renderHoloBrain(data)" in html
    assert "buildRuntimeRows(_latestRuntimeData)" in html
    assert "renderHoloBuildDashboard(holoBuild)" in html
    assert "HoloBuild turn timeline" in html
    assert "HoloBuild Gov briefs" in html
    assert "Watch live run" in html
    assert "startHoloBuildRun()" in html
    assert "pollHoloBuildRun" in html
    assert "HOLOBUILD_LIVE_RUNS=true" in html
    assert "Refresh engine data" in html
    assert "Attached capsule" not in html
    assert "capsule.id_short" not in html
    assert "Start HoloBuild run" not in html


def test_frontend_holobrain_hides_capsule_context_rows_by_default():
    html = Path("frontend/chat.html").read_text()

    assert "Memory details hidden by default" in html
    assert "Context counts stay visible without showing stored rows." in html
    assert "const contextRows = brainRows(ctx.entries" not in html
    assert 'brainSection("Saved memory", `${ctx.count || 0} rows`, contextRows, true)' not in html
    assert 'brainSection("Life context", `${life.count || 0} rows`, lifeRows, true)' not in html
