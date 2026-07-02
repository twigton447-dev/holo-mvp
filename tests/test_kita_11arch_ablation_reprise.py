from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = REPO_ROOT / "docs" / "benchmark" / "run_kita_11arch_ablation_reprise_2026_07_02.py"
VALID_RUN_DIR = (
    REPO_ROOT
    / "docs"
    / "benchmark"
    / "kita_11arch_ablation_reprise_2026-07-02"
    / "cross_domain_3pair_hard"
    / "live_runs"
    / "run_20260702T184308Z"
)
AUTOPSY_PATH = VALID_RUN_DIR / "KITA_11ARCH_ABLATION_REPRISE_6CALL_AUTOPSY_2026_07_02.json"
OPENAI54_RUN_DIR = (
    REPO_ROOT
    / "docs"
    / "benchmark"
    / "kita_11arch_ablation_reprise_2026-07-02"
    / "openai54_homogeneous_6call_same_arch_family"
    / "live_runs"
    / "run_20260702T193334Z"
)
OPENAI54_RESULTS_PATH = OPENAI54_RUN_DIR / "live_results.json"
OPENAI54_AUDIT_PATH = OPENAI54_RUN_DIR / "KITA_OPENAI54_HOMOGENEOUS_6CALL_COMPLETION_AUDIT_2026_07_02.json"
OPENAI54_AUTOPSY_PATH = OPENAI54_RUN_DIR / "KITA_OPENAI54_HOMOGENEOUS_6CALL_AUTOPSY_2026_07_02.json"


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
    assert report["fairness_frame"]["calls_per_packet_per_architecture"] == 6
    assert report["fairness_frame"]["architecture_model_distributions"] == {
        architecture: {"xai": 2, "openai_w2": 2, "minimax": 2}
        for architecture in runner.DEFAULT_REPRISE_ARCHITECTURES
    }
    assert report["checks"]["provider_balanced_two_turns_each_model"] is True
    assert report["checks"]["architecture_model_distribution_matches_declared_family"] is True
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


def test_openai54_homogeneous_architectures_match_packet_set_and_call_budget():
    runner = load_runner()
    report = runner.preflight(
        runner.DEFAULT_PAIR_IDS,
        runner.OPENAI54_HOMOGENEOUS_REPRISE_ARCHITECTURES,
        "pytest_openai54_homogeneous",
    )

    assert report["status"] == "PASS"
    assert report["selected_pair_ids"] == ["HV-AP-REP-011", "HV-ACOM-REP-020", "HV-ITAC-REP-018"]
    assert report["selected_packet_count"] == 6
    assert report["expected_provider_calls"] == 144
    assert report["expected_gov_calls"] == 0
    assert report["expected_holo_calls"] == 0
    assert report["expected_judge_calls"] == 0
    assert report["provider_balance_failures"] == []
    assert report["checks"]["architecture_model_distribution_matches_declared_family"] is True
    assert report["checks"]["provider_balanced_two_turns_each_model"] == "N/A"
    assert report["fairness_frame"]["calls_per_packet_per_architecture"] == 6
    assert report["fairness_frame"]["architecture_model_distributions"] == {
        architecture: {"openai_w2": 6}
        for architecture in runner.OPENAI54_HOMOGENEOUS_REPRISE_ARCHITECTURES
    }
    assert {row["model_key"] for row in report["call_plan"]} == {"openai_w2"}
    assert {row["model"] for row in report["call_plan"]} == {"gpt-5.4-mini"}
    assert all(row["gov_context_allowed"] is False for row in report["call_plan"])
    assert all(row["holo_state_allowed"] is False for row in report["call_plan"])
    assert all(row["artifact_registry_allowed"] is False for row in report["call_plan"])
    assert all(row["final_selector_allowed"] is False for row in report["call_plan"])


def test_openai54_homogeneous_roles_reuse_same_architecture_family_roles():
    runner = load_runner()
    paired = [
        ("provider_balanced_reconsider_no_gov_6call", "openai54_reconsider_no_gov_6call"),
        ("provider_balanced_vote_no_gov_6call", "openai54_vote_no_gov_6call"),
        ("provider_balanced_council_no_gov_6call", "openai54_council_no_gov_6call"),
        ("provider_balanced_debate_no_gov_6call", "openai54_debate_no_gov_6call"),
    ]

    for provider_balanced, openai54 in paired:
        assert [role for _, role in runner.ARCH_CALL_SHAPES[openai54]] == [
            role for _, role in runner.ARCH_CALL_SHAPES[provider_balanced]
        ]
        assert [model_key for model_key, _ in runner.ARCH_CALL_SHAPES[openai54]] == ["openai_w2"] * 6


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


def test_openai54_provider_prompt_uses_same_output_contract_and_no_holo_controls():
    runner = load_runner()
    record = runner.select_records(runner.read_records(), ("HV-ACOM-REP-020",))[0]
    call_row = runner.build_call_plan([record], ("openai54_council_no_gov_6call",))[0]

    prompt = runner.build_provider_prompt(record, call_row, [])

    assert call_row["model_key"] == "openai_w2"
    assert call_row["model"] == "gpt-5.4-mini"
    assert "Return JSON only with exactly these keys: verdict, binding_reason, source_ids, open_dependencies, action_boundary." in prompt
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


def test_fake_openai54_homogeneous_run_uses_exact_144_call_loop_without_providers(tmp_path):
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

    label = "pytest_fake_openai54_homogeneous"
    runner.OUT_ROOT = tmp_path / "kita_reprise"
    summary = runner.run_live(
        runner.DEFAULT_PAIR_IDS,
        runner.OPENAI54_HOMOGENEOUS_REPRISE_ARCHITECTURES,
        label,
        fake_call,
        require_env=False,
        run_id="run_pytest_fake_openai54",
    )

    assert len(calls) == 144
    assert {call["model_key"] for call in calls} == {"openai_w2"}
    assert summary["classification"] == "KITA_11ARCH_ABLATION_REPRISE_LIVE_COMPLETE"
    assert summary["provider_calls"] == 144
    assert summary["expected_provider_calls"] == 144
    assert summary["gov_calls"] == 0
    assert summary["holo_calls"] == 0
    assert summary["judge_calls"] == 0
    assert summary["provider_failures"] == 0
    assert summary["parse_failures"] == 0
    assert summary["selected_reprise_architectures"] == list(runner.OPENAI54_HOMOGENEOUS_REPRISE_ARCHITECTURES)
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


def test_committed_autopsy_uses_normalized_failure_topology():
    data = json.loads(AUTOPSY_PATH.read_text())
    allowed = set(data["normalized_failure_class_taxonomy"]["allowed_classes"])
    rows = data["failure_topology_rows"]

    assert len(rows) == 24
    assert {row["normalized_failure_class"] for row in rows} <= allowed
    assert data["failure_topology_summary"]["normalized_failure_class_counts"] == {
        "missing_binding_authority_source": 6,
        "missing_policy_source": 3,
        "parse_failure_unusable_artifact": 2,
        "strict_admissible_correct": 8,
        "unsupported_escalation": 5,
    }
    for row in rows:
        assert row["packet_pair"]
        assert row["architecture"]
        assert row["admissibility_status"] in {"ADMISSIBLE", "NOT_ADMISSIBLE"}
        assert row["missing_source_ids_or_closure_defect"]
        assert row["failure_explanation"]


def test_openai54_homogeneous_live_run_is_comparable_and_complete():
    results = json.loads(OPENAI54_RESULTS_PATH.read_text())
    audit = json.loads(OPENAI54_AUDIT_PATH.read_text())
    autopsy = json.loads(OPENAI54_AUTOPSY_PATH.read_text())
    trace_rows = [
        json.loads(line)
        for line in (OPENAI54_RUN_DIR / "TRACE_CALLS.jsonl").read_text().splitlines()
        if line.strip()
    ]

    assert results["classification"] == "KITA_11ARCH_ABLATION_REPRISE_LIVE_COMPLETE"
    assert results["provider_calls"] == 144
    assert results["expected_provider_calls"] == 144
    assert results["gov_calls"] == 0
    assert results["holo_calls"] == 0
    assert results["judge_calls"] == 0
    assert results["provider_failures"] == 0
    assert results["parse_failures"] == 0
    assert results["selected_pair_ids"] == ["HV-AP-REP-011", "HV-ACOM-REP-020", "HV-ITAC-REP-018"]
    assert results["selected_packet_count"] == 6
    assert results["selected_reprise_architectures"] == [
        "openai54_reconsider_no_gov_6call",
        "openai54_vote_no_gov_6call",
        "openai54_council_no_gov_6call",
        "openai54_debate_no_gov_6call",
    ]
    assert len(trace_rows) == 144
    assert {(row["provider"], row["model"], row["model_key"]) for row in trace_rows} == {
        ("openai", "gpt-5.4-mini", "openai_w2")
    }
    assert all(row["gov_context_in_prompt"] is False for row in trace_rows)
    assert all(row["holo_state_in_prompt"] is False for row in trace_rows)
    assert all(row["artifact_registry_in_prompt"] is False for row in trace_rows)
    assert all(row["final_selector_in_prompt"] is False for row in trace_rows)
    assert audit["status"] == "PASS"
    assert all(audit["requirements"].values())
    assert autopsy["result_summary"]["strict_admissible_correct"] == 13
    assert autopsy["result_summary"]["failure_topology_counts"] == {
        "missing_binding_authority_source": 7,
        "strict_admissible_correct": 13,
        "unsupported_escalation": 4,
    }
    assert len(autopsy["failure_topology_rows"]) == 24
