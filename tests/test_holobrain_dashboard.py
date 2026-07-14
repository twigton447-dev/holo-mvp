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


class ScopedFakeBrain(FakeBrain):
    def __init__(self):
        self.scope_calls = []

    def _record(self, name, scope_id):
        self.scope_calls.append((name, scope_id))

    def get_capsule_context(self, capsule_id, *, scope_id=None):
        self._record("context", scope_id)
        return super().get_capsule_context(capsule_id)

    def load_life_context(self, capsule_id, *, scope_id=None):
        self._record("life", scope_id)
        return super().load_life_context(capsule_id)

    def list_sessions(self, capsule_id, limit=40, *, scope_id=None):
        self._record("sessions", scope_id)
        return super().list_sessions(capsule_id, limit)

    def load_last_consolidation(self, capsule_id, *, scope_id=None):
        self._record("consolidation", scope_id)
        return super().load_last_consolidation(capsule_id)

    def list_artifacts(self, capsule_id, limit=50, *, scope_id=None):
        self._record("artifacts", scope_id)
        return super().list_artifacts(capsule_id, limit)


class _PrivateMetadataChatEngine:
    def __init__(self, turn_cost=0.0175):
        self.turn_cost = turn_cost

    def _result(self):
        return {
            "session_id": "session-1",
            "response": "Public answer.",
            "turn_number": 1,
            "thread_health_score": 100,
            "thread_health_level": "GREEN",
            "elapsed_ms": 4,
            "tokens": {"input": 10, "output": 2},
            "runtime": {
                "gov_turn_plan": {"narrative_packet": {"private": "memory"}},
                "cost_breakdown": {"turn_estimated_cost_usd": self.turn_cost},
                "selected_analyst": {"provider": "fake-worker", "model": "fake-worker-v1"},
                "context_telemetry": {
                    "gov_model": {"provider": "fake-gov", "model": "fake-gov-v1"},
                },
            },
            "context_budget": {"worker_context_receipt": {"receipt_hash": "private"}},
            "usage": {"estimated_cost_usd": 1.0},
            "holo4dna": {"trace": "private"},
            "web_sources": [],
            "web_citations": {"status": "no_evidence", "passed": True},
        }

    def send_message(self, *args, **kwargs):
        return self._result()

    def stream_message(self, *args, **kwargs):
        yield "Public answer."
        yield {"done": True, **self._result()}


def test_public_stream_metadata_hides_private_hologov_state_by_default(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_EXPOSE_PRIVATE_RUNTIME", raising=False)
    payload = main._public_stream_metadata({
        "done": True,
        "session_id": "session-1",
        "runtime": {"gov_turn_plan": {"narrative_packet": {"private": "memory"}}},
        "context_budget": {"worker_context_receipt": {"receipt_hash": "secret-hash"}},
        "usage": {"estimated_cost_usd": 1.0},
        "holo4dna": {"trace": "private"},
        "_provider": "openai",
        "web_sources": [{"source_id": "S1", "url": "https://example.com"}],
    })

    assert payload == {
        "session_id": "session-1",
        "web_sources": [{"source_id": "S1", "url": "https://example.com"}],
    }


def test_private_runtime_metadata_requires_explicit_operator_flag(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_EXPOSE_PRIVATE_RUNTIME", "1")
    payload = main._public_stream_metadata({
        "done": True,
        "runtime": {"gov_turn_plan": {"turn_id": "turn-1"}},
        "context_budget": {"worker_context_receipt": {"receipt_hash": "hash"}},
    })

    assert payload["runtime"]["gov_turn_plan"]["turn_id"] == "turn-1"
    assert payload["context_budget"]["worker_context_receipt"]["receipt_hash"] == "hash"


def test_chat_api_does_not_return_private_runtime_by_default(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_EXPOSE_PRIVATE_RUNTIME", raising=False)
    monkeypatch.setenv("HOLO_API_KEY", "test-api-key")
    monkeypatch.setattr(main, "_chat_engine", _PrivateMetadataChatEngine())
    tracked = []
    monkeypatch.setattr(main, "_track_usage", lambda *args, **kwargs: tracked.append((args, kwargs)))
    client = TestClient(main.app)

    response = client.post(
        "/v1/chat",
        headers={"x-api-key": "test-api-key"},
        json={"message": "Hello"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["response"] == "Public answer."
    assert "runtime" not in body
    assert "context_budget" not in body
    assert "usage" not in body
    assert "holo4dna" not in body
    assert tracked[0][1]["cost_usd"] == 0.0175
    assert tracked[0][1]["worker_identity"] == {
        "provider": "fake-worker", "model": "fake-worker-v1",
    }
    assert tracked[0][1]["hologov_identity"] == {
        "provider": "fake-gov", "model": "fake-gov-v1",
    }


def test_stream_api_filters_private_runtime_and_tracks_usage(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_EXPOSE_PRIVATE_RUNTIME", raising=False)
    monkeypatch.setenv("HOLO_API_KEY", "test-api-key")
    monkeypatch.setattr(main, "_chat_engine", _PrivateMetadataChatEngine())
    tracked = []
    monkeypatch.setattr(main, "_track_usage", lambda *args, **kwargs: tracked.append((args, kwargs)))
    client = TestClient(main.app)

    response = client.post(
        "/v1/chat/stream",
        headers={"x-api-key": "test-api-key"},
        json={"message": "Hello"},
    )

    assert response.status_code == 200
    assert '"type": "done"' in response.text
    assert '"runtime"' not in response.text
    assert '"context_budget"' not in response.text
    assert len(tracked) == 1
    assert tracked[0][0][1:3] == ("/v1/chat/stream", 200)
    assert tracked[0][1]["input_tokens"] == 10
    assert tracked[0][1]["output_tokens"] == 2
    assert tracked[0][1]["cost_usd"] == 0.0175


def test_chat_usage_telemetry_keeps_unknown_complete_cost_explicit():
    telemetry = main._chat_usage_telemetry({
        "usage": {"estimated_cost_usd": 0.01},
        "runtime": {
            "cost_breakdown": {"turn_estimated_cost_usd": None},
            "selected_analyst": {"provider": "fake-worker", "model": "unpriced"},
            "context_telemetry": {
                "gov_model": {"provider": "fake-gov", "model": "unpriced"},
            },
        },
    })

    assert telemetry["cost_usd"] is None
    assert telemetry["worker_identity"]["provider"] == "fake-worker"
    assert telemetry["hologov_identity"]["provider"] == "fake-gov"


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


def test_holobrain_payload_keeps_all_memory_reads_in_resolved_scope():
    brain = ScopedFakeBrain()
    main._build_holo_brain_payload(
        {"sub": "canonical-capsule", "email": "alias@example.com", "mode": "personal"},
        brain,
        scope_id="enterprise-scope",
    )

    assert brain.scope_calls
    assert {scope_id for _, scope_id in brain.scope_calls} == {"enterprise-scope"}


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
    assert 'title="Open diagnostics"' in html
    assert ">Diagnostics</button>" in html
    assert 'id="holobrain-panel"' in html
    assert 'id="holobrain-resize-handle"' in html
    assert 'title="Drag to resize diagnostics"' in html
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
    assert "No saved HoloBuild replay is available yet." in html
    assert "After a watched Builder run completes" in html
    assert "HoloBuild replay" in html
    assert "signed-in replay" in html
    assert "Watch live run" in html
    assert "startHoloBuildRun()" in html
    assert "pollHoloBuildRun" in html
    assert "HOLOBUILD_LIVE_RUNS=true" in html
    assert "Refresh diagnostics" in html
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
