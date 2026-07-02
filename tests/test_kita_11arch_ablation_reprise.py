from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = REPO_ROOT / "docs" / "benchmark" / "run_kita_11arch_ablation_reprise_2026_07_02.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("kita_ablation_reprise_runner", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_default_preflight_locks_three_hard_pairs_and_provider_balanced_144_calls():
    runner = load_runner()

    report = runner.preflight(runner.DEFAULT_PAIR_IDS, runner.DEFAULT_REPRISE_ARCHITECTURES, "pytest_preflight")

    assert report["status"] == "PASS"
    assert report["selected_pair_ids"] == ["HV-AP-REP-011", "HV-ACOM-REP-020", "HV-ITAC-REP-018"]
    assert report["selected_packet_count"] == 6
    assert report["truth_counts"] == {"ALLOW": 3, "ESCALATE": 3}
    assert report["expected_provider_calls"] == 144
    assert report["expected_gov_calls"] == 0
    assert report["expected_holo_calls"] == 0
    assert report["expected_judge_calls"] == 0
    assert report["fairness_frame"]["turns_per_model_per_packet_per_architecture"] == 2
    assert report["checks"]["provider_balanced_two_turns_each_model"] is True
    assert report["provider_balance_failures"] == []
    assert report["checks"]["no_prompt_leakage"] is True
    assert all(row["gov_context_allowed"] is False for row in report["call_plan"])
    assert all(row["holo_state_allowed"] is False for row in report["call_plan"])
    assert all(row["artifact_registry_allowed"] is False for row in report["call_plan"])
    assert all(row["final_selector_allowed"] is False for row in report["call_plan"])


def test_every_architecture_gives_each_model_two_turns_per_packet():
    runner = load_runner()
    report = runner.preflight(runner.DEFAULT_PAIR_IDS, runner.DEFAULT_REPRISE_ARCHITECTURES, "pytest_balance")

    for packet_id in {row["packet_id"] for row in report["call_plan"]}:
        for architecture in runner.DEFAULT_REPRISE_ARCHITECTURES:
            rows = [
                row
                for row in report["call_plan"]
                if row["packet_id"] == packet_id and row["architecture"] == architecture
            ]
            model_counts = {}
            for row in rows:
                model_counts[row["model_key"]] = model_counts.get(row["model_key"], 0) + 1
            assert model_counts == {"xai": 2, "openai_w2": 2, "minimax": 2}


def test_provider_prompt_contains_no_forbidden_holo_controls():
    runner = load_runner()
    record = runner.select_records(runner.read_records(), ("HV-ACOM-REP-020",))[0]
    call_row = runner.build_call_plan([record], ("provider_balanced_council_no_gov_6call",))[0]

    prompt = runner.build_provider_prompt(record, call_row, [])

    assert runner.leakage_hits(prompt) == []
    assert "STATE_BRIEF" not in prompt
    assert "LATEST_GOV_BATON" not in prompt
    assert "artifact_registry" not in prompt
    assert "final_selector" not in prompt
    assert record["action_boundary"] in prompt


def test_fake_live_run_uses_exact_144_call_loop_without_providers(tmp_path):
    runner = load_runner()
    calls = []

    def fake_call(model_key, prompt_text, max_tokens, call_row):
        calls.append(
            {
                "model_key": model_key,
                "packet_id": call_row["packet_id"],
                "architecture": call_row["architecture"],
                "role": call_row["architecture_role"],
            }
        )
        record = call_row["record"]
        return {
            "text": json.dumps(
                {
                    "verdict": record["required_verdict_for_local_audit_only"],
                    "binding_reason": "fixture source-boundary closure",
                    "source_ids": record["required_source_ids_for_local_audit_only"],
                    "open_dependencies": [],
                    "action_boundary": record["action_boundary"],
                },
                sort_keys=True,
            ),
            "finish_reason": "fixture",
            "input_tokens": 1,
            "output_tokens": 1,
            "total_tokens": 2,
        }

    label = "pytest_fake_live"
    runner.OUT_ROOT = tmp_path / "kita_reprise"
    summary = runner.run_live(
        runner.DEFAULT_PAIR_IDS,
        runner.DEFAULT_REPRISE_ARCHITECTURES,
        label,
        fake_call,
        require_env=False,
        run_id="run_pytest_fake",
    )

    assert len(calls) == 144
    assert summary["classification"] == "KITA_11ARCH_ABLATION_REPRISE_LIVE_COMPLETE"
    assert summary["provider_calls"] == 144
    assert summary["expected_provider_calls"] == 144
    assert summary["gov_calls"] == 0
    assert summary["holo_calls"] == 0
    assert summary["judge_calls"] == 0
    assert summary["provider_failures"] == 0
    assert summary["parse_failures"] == 0
    assert summary["selected_pair_ids"] == ["HV-AP-REP-011", "HV-ACOM-REP-020", "HV-ITAC-REP-018"]
    assert Path(summary["run_dir"]).exists()


def test_approval_packet_statement_and_hash_are_stable_for_preflight():
    runner = load_runner()
    report = runner.preflight(runner.DEFAULT_PAIR_IDS, runner.DEFAULT_REPRISE_ARCHITECTURES, "pytest_approval")
    packet = runner.approval_packet(report)

    assert packet["approval_statement_required"] == runner.EXPECTED_APPROVAL_STATEMENT
    assert packet["approval_scope"]["expected_provider_calls"] == 144
    assert packet["approval_scope"]["expected_gov_calls"] == 0
    assert packet["approval_scope"]["expected_holo_calls"] == 0
    assert packet["approval_scope"]["expected_judge_calls"] == 0
    assert packet["approval_packet_sha256"] == report["approval_packet_sha256"]
