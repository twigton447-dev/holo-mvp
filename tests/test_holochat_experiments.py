from pathlib import Path

import pytest

from holochat_experiments import PRICE_CATALOG, PRICING_VERSION, build_manifest, run_live_smoke


def test_manifest_is_deterministic_and_dry_run_only():
    first = build_manifest(lane="balanced", condition="C", rotations=3)
    second = build_manifest(lane="balanced", condition="C", rotations=3)

    assert first == second
    assert first["mode"] == "dry_run"
    assert first["provider_calls_made"] is False
    assert first["rotation"]["strategy"] == "alternating_workers_fixed_governor"
    assert [event["role"] for event in first["call_events"]] == ["governor", "worker"] * 3
    assert [event["model"] for event in first["call_events"] if event["role"] == "worker"] == ["gpt-5.4", "grok-4.3", "gpt-5.4"]


def test_catalog_has_requested_versioned_prices():
    assert PRICING_VERSION == "official-2026-07-14"
    assert len(PRICE_CATALOG) == 10
    assert str(PRICE_CATALOG["openai/gpt-5.5"].input_per_million) == "5"
    assert str(PRICE_CATALOG["deepseek/v4-pro"].output_per_million) == "0.87"


def test_call_events_and_aggregate_expose_accounting_schema():
    manifest = build_manifest(lane="economy", condition="D", rotations=2, input_tokens_per_call=1_000, output_tokens_per_call=500)
    event = manifest["call_events"][0]

    assert event["pricing"]["estimate"] is True
    assert event["latency_ms"] is None
    assert event["context_tokens"] == 1_000
    assert event["quality"]["score"] is None
    assert manifest["aggregate"]["call_count"] == 4
    assert manifest["aggregate"]["estimated_cost_usd"] != "0"


def test_live_requires_both_explicit_gates(tmp_path: Path):
    manifest = build_manifest(lane="frontier", condition="A")
    with pytest.raises(PermissionError):
        run_live_smoke(manifest=manifest, live=True, confirm_live=False, smoke_script=tmp_path / "missing.py")


def test_live_invokes_injected_runner_only_after_gates(tmp_path: Path):
    smoke = tmp_path / "holochat_live_smoke.py"
    smoke.write_text("# --experiment-mode\n# HOLOCHAT_EXPERIMENT_MODE\n", encoding="utf-8")
    received = []

    result = run_live_smoke(manifest=build_manifest(lane="economy", condition="A", rotations=4), live=True, confirm_live=True, smoke_script=smoke, runner=lambda command, check, env: received.append((command, check, env)) or "ok")

    assert result == "ok"
    assert received[0][1] is True
    assert "--disable-gov-control" in received[0][0]
    assert received[0][0][-1] == "--disable-gov-control"
    assert received[0][2]["OPENAI_FAST_MODEL"] == "gpt-5.4-mini"
    assert received[0][2]["XAI_FAST_MODEL"] == "grok-4.3"
    assert received[0][2]["HOLOCHAT_GOV_MODEL"] == "gpt-5.4-mini"
    assert received[0][2]["HOLOCHAT_EXPERIMENT_MODE"] == "1"
    assert received[0][2]["HOLOCHAT_RUNTIME_PROFILE"] == "holochat_canonical"
    assert "OPENAI_API_KEY" not in received[0][2]


def test_live_rejects_smoke_without_experiment_mode_support(tmp_path: Path):
    smoke = tmp_path / "holochat_live_smoke.py"
    smoke.write_text("# old smoke fixture\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="experiment mode"):
        run_live_smoke(manifest=build_manifest(lane="frontier", condition="C"), live=True, confirm_live=True, smoke_script=smoke, runner=lambda **_: None)


def test_live_frontier_environment_applies_its_models(tmp_path: Path):
    smoke = tmp_path / "holochat_live_smoke.py"
    smoke.write_text("# --experiment-mode\n# HOLOCHAT_EXPERIMENT_MODE\n", encoding="utf-8")
    captured = {}

    run_live_smoke(manifest=build_manifest(lane="frontier", condition="C"), live=True, confirm_live=True, smoke_script=smoke, runner=lambda command, check, env: captured.update(command=command, env=env))

    assert "--respect-env" in captured["command"]
    assert captured["env"]["OPENAI_FAST_MODEL"] == "gpt-5.5"
    assert captured["env"]["XAI_FAST_MODEL"] == "grok-4.5"
    assert captured["env"]["HOLOCHAT_GOV_MODEL"] == "gpt-5.5"


def test_condition_c_and_d_execute_distinct_context_modes(tmp_path: Path):
    smoke = tmp_path / "holochat_live_smoke.py"
    smoke.write_text("# --experiment-mode\n# HOLOCHAT_EXPERIMENT_MODE\n", encoding="utf-8")
    commands = {}

    for condition in ("C", "D"):
        run_live_smoke(
            manifest=build_manifest(lane="balanced", condition=condition),
            live=True,
            confirm_live=True,
            smoke_script=smoke,
            runner=lambda command, check, env, condition=condition: commands.update({condition: command}),
        )

    assert "--disable-selective-context" in commands["C"]
    assert "--disable-selective-context" not in commands["D"]
    assert commands["C"] != commands["D"]
