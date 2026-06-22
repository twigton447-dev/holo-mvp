from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


FACTORY_DIR = Path(__file__).resolve().parent
REPO_ROOT = FACTORY_DIR.parents[1]
RUNNER_PATH = FACTORY_DIR / "run_holobuild_mini_scout.py"
D10_PACKET_DIR = REPO_ROOT / "artifact_benchmarks/holo_factory/mini_scouts/d10_infrastructure_configuration_change_001"
D11_PACKET_DIR = REPO_ROOT / "artifact_benchmarks/holo_factory/mini_scouts/d11_cyber_incident_contract_notice_emergency_cloud_access_001"
D12_PACKET_DIR = REPO_ROOT / "artifact_benchmarks/holo_factory/mini_scouts/d12_fund_nav_redemption_cash_release_001"
D13_PACKET_DIR = REPO_ROOT / "artifact_benchmarks/holo_factory/mini_scouts/d13_treasury_sanctions_payment_release_001"
D14_PACKET_DIR = REPO_ROOT / "artifact_benchmarks/holo_factory/mini_scouts/d14_trade_finance_lc_discrepancy_payment_release_001"
D13_BLIND_COMPARISON_PACKET = (
    D13_PACKET_DIR
    / "blind_exports/d13_two_artifact_blind_comparison_20260622T201000Z/judge_packets/D13_TWO_ARTIFACT_BLIND_COMPARISON_PACKET.json"
)
D11_VALIDATOR = REPO_ROOT / "artifact_benchmarks/holo_factory/mini_scouts/d11_cyber_incident_contract_notice_emergency_cloud_access_001/validate_packet_no_provider.py"
D12_VALIDATOR = REPO_ROOT / "artifact_benchmarks/holo_factory/mini_scouts/d12_fund_nav_redemption_cash_release_001/validate_packet_no_provider.py"
D13_VALIDATOR = REPO_ROOT / "artifact_benchmarks/holo_factory/mini_scouts/d13_treasury_sanctions_payment_release_001/validate_packet_no_provider.py"
D11_PACKET_HASH = "2e80109e4149da65b241452a5ffc194fb4caf4117d204616a1065eb47afde371"
D12_PACKET_HASH = "fce82318244558dbd36b0b8aec377bc0c180c885a8c9d5ed3b5a7a703c605bb0"
D13_PACKET_HASH = "716fbc94608107d10d58c4de144d6cbce92c184c7f7c102d2f1581bb6b567801"
D11_PACKET_LOCK_HASH = "27ba069ef63c8c14386ef43a974c316320ebeb5067cfa4623aa9446632e70564"
D12_PACKET_LOCK_HASH = "0550af2c53affb28bdf367be27a2e684007b0eb4c61c484656f458a1eaff2f4f"
D13_PACKET_LOCK_HASH = "c3d9a58418c8a2cd0c7bf648e398b76465266816e36390346acb5cef04c90c6e"
D10_POST_V4_2_CONDITION_DIR = (
    REPO_ROOT
    / "artifact_benchmarks/holo_factory/mini_scouts/d10_infrastructure_configuration_change_001/runs"
    / "d10_infrastructure_configuration_change_001_post_v4_2_opusgovb_holo_only_live_20260622T000000Z"
    / "frontier_holo_opus_gov_b_v1"
)
D11_PROOF_CLEAN_CONDITION_DIR = (
    REPO_ROOT
    / "artifact_benchmarks/holo_factory/mini_scouts/d11_cyber_incident_contract_notice_emergency_cloud_access_001/runs"
    / "d11_cyber_incident_contract_notice_emergency_cloud_access_001_frontier_optimized_opus_gpt55_holo_only_live_20260622T000000Z"
    / "frontier_holo_optimized_opus_gpt55_v1"
)
D12_T3_FAILURE_CONDITION_DIR = (
    REPO_ROOT
    / "artifact_benchmarks/holo_factory/mini_scouts/d12_fund_nav_redemption_cash_release_001/runs"
    / "d12_fund_nav_redemption_cash_release_001_frontier_optimized_opus_gpt55_holo_only_live_20260622T000000Z"
    / "frontier_holo_optimized_opus_gpt55_v1"
)
D12_RETRY2_CONDITION_DIR = (
    REPO_ROOT
    / "artifact_benchmarks/holo_factory/mini_scouts/d12_fund_nav_redemption_cash_release_001/runs"
    / "d12_fund_nav_redemption_cash_release_001_frontier_optimized_opus_gpt55_holo_only_live_retry2_20260622T000000Z"
    / "frontier_holo_optimized_opus_gpt55_v1"
)
D12_RETRY3_CONDITION_DIR = (
    REPO_ROOT
    / "artifact_benchmarks/holo_factory/mini_scouts/d12_fund_nav_redemption_cash_release_001/runs"
    / "d12_fund_nav_redemption_cash_release_001_frontier_optimized_opus_gpt55_holo_only_live_retry3_final_boundary_patch_20260622T000000Z"
    / "frontier_holo_optimized_opus_gpt55_v1"
)
D14_T3_FAILURE_CONDITION_DIR = (
    REPO_ROOT
    / "artifact_benchmarks/holo_factory/mini_scouts/d14_trade_finance_lc_discrepancy_payment_release_001/runs"
    / "d14_trade_finance_lc_discrepancy_payment_release_001_frontier_optimized_opus_gpt55_holo_only_live_20260622T210025Z"
    / "frontier_holo_optimized_opus_gpt55_v1"
)
D14_T3_FAILURE_RUN_MANIFEST = D14_T3_FAILURE_CONDITION_DIR.parent / "run_manifest.json"
D14_RETRY2_CONDITION_DIR = (
    REPO_ROOT
    / "artifact_benchmarks/holo_factory/mini_scouts/d14_trade_finance_lc_discrepancy_payment_release_001/runs"
    / "d14_trade_finance_lc_discrepancy_payment_release_001_frontier_optimized_opus_gpt55_holo_only_live_retry2_same_packet_patch_validation_20260622T212753Z"
    / "frontier_holo_optimized_opus_gpt55_v1"
)
OPTIMIZED_D10_RUN_MANIFEST = (
    REPO_ROOT
    / "artifact_benchmarks/holo_factory/mini_scouts/d10_infrastructure_configuration_change_001/runs"
    / "d10_infrastructure_configuration_change_001_frontier_optimized_opus_gpt55_holo_only_live_retry2_20260622T000000Z"
    / "run_manifest.json"
)
OPTIMIZED_D10_RETRY3_RUN_MANIFEST = (
    REPO_ROOT
    / "artifact_benchmarks/holo_factory/mini_scouts/d10_infrastructure_configuration_change_001/runs"
    / "d10_infrastructure_configuration_change_001_frontier_optimized_opus_gpt55_holo_only_live_retry3_compression_patch_20260622T000000Z"
    / "run_manifest.json"
)
FORBIDDEN_GENERATION_CONTRACT_TERMS = (
    "900-1,500",
    "900-1500",
    "1,500",
    "persuasive ceiling",
    "overage penalty",
    "v6.1 scoring",
    "scoring protocol",
    "judge-visible",
    "final_synthesis_900_1500_words",
)


RUNS = {
    "D6": "artifact_benchmarks/holo_factory/mini_scouts/d6_pe_financial_reporting_consolidation_001/runs/d6_pe_financial_reporting_consolidation_001_full_registry_final_complete_v2_live_20260621T220414Z/holo_build_arch",
    "D7": "artifact_benchmarks/holo_factory/mini_scouts/d7_agentic_commerce_purchase_approval_001/runs/d7_agentic_commerce_purchase_approval_001_full_registry_final_complete_v2_live_20260621T220414Z/holo_build_arch",
    "D9": "artifact_benchmarks/holo_factory/mini_scouts/d9_legal_contract_execution_001/runs/d9_legal_contract_execution_001_opusgovb_opussolo_live_20260622T011221Z/frontier_holo_opus_gov_b_v1",
    "D10": "artifact_benchmarks/holo_factory/mini_scouts/d10_infrastructure_configuration_change_001/runs/d10_infrastructure_configuration_change_001_opusgovb_opussolo_live_20260622T012153Z/frontier_holo_opus_gov_b_v1",
}


def load_runner():
    sys.path.insert(0, str(FACTORY_DIR))
    spec = importlib.util.spec_from_file_location("run_holobuild_mini_scout_under_test", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


runner = load_runner()


def read_json(rel_path: str) -> dict:
    return json.loads((REPO_ROOT / rel_path).read_text(encoding="utf-8"))


def raw_text(domain: str, turn: int) -> tuple[str, dict]:
    raw = read_json(f"{RUNS[domain]}/raw_outputs/turn_{turn:03d}.json")
    return raw["text"], raw


def raw_output_path(domain: str, turn: int) -> Path:
    return REPO_ROOT / f"{RUNS[domain]}/raw_outputs/turn_{turn:03d}.json"


def state_after_rejected_options_turn(domain: str) -> tuple[str, str, dict, str]:
    rejected_text, _raw = raw_text(domain, 4)
    rejected_artifact_id = "TURN_004_OPTIONS_OPERATIONAL_USEFULNESS_REVIEWER"
    registry = {
        "artifacts": {
            "TASK_BRIEF": {"status": "PINNED", "hash": "task_hash", "source_reference": "task_brief.md", "content": "frozen task brief"},
            "SOURCE_PACKET_MD": {"status": "PINNED", "hash": "source_hash", "source_reference": "source_packet.md", "content": "frozen source packet"},
            "TURN_001_INITIAL_DECISION_BRIEF_DRAFTER": {
                "status": "INTERMEDIATE_ACCEPTED",
                "hash": "accepted_hash",
                "source_reference": "raw_outputs/turn_001.json",
                "content": "accepted prior artifact content",
            },
        }
    }
    unresolved = {
        "options_operational_usefulness_reviewer": {
            "artifact_id": rejected_artifact_id,
            "role": "options_operational_usefulness_reviewer",
            "status": "rejected",
        }
    }
    final_allowed_ids = runner.retrieved_ids_for_holo_turn(registry, "full_registry")
    state = {"PACKET_HASH": "packet_hash"}
    runner.update_holobuild_state_surfaces(
        state,
        registry,
        rejected_artifact_ids=[rejected_artifact_id],
        unresolved_required_roles=unresolved,
        repair_attempt_status={rejected_artifact_id: runner.repair_attempt_public_status([])},
        final_synthesis_allowed_input_ids=final_allowed_ids,
    )
    final_prompt_surface = (
        "CANONICAL STATE_OBJECT\n======================\n"
        f"{runner.stable_json(state)}\n\n"
        "RETRIEVED PINNED SOURCES AND ARTIFACTS\n======================================\n"
        f"{runner.retrieved_content_for(final_allowed_ids, registry)}\n"
    )
    return rejected_text, rejected_artifact_id, state, final_prompt_surface


def final_text_with_sections(word_target: int = 940) -> str:
    sections = [
        "# Bottom line\nRecommend a conditional go path using S1_TEST_SOURCE and S2_TEST_SOURCE because the packet supports a bounded option, not an unrestricted action.",
        "# Risks of acting\nThe risk of acting is execution error, preventable exposure, and reliance on a source boundary the packet does not prove.",
        "# Risks of waiting\nThe risk of waiting is delay cost, operational drift, and missed escalation timing if leadership does not assign an owner.",
        "# Next steps / stop-go gates\nUse a go trigger, no-go trigger, rollback trigger, monitoring gate, and executive escalation owner before expansion.",
        "# Claim boundaries\nThis brief does not conclude broad approval is available from S1_TEST_SOURCE and S2_TEST_SOURCE, and final execution remains unsupported until gates pass.",
    ]
    filler = " The recommendation remains conditional, source bounded, monitored, reversible where possible, and explicit about what the packet does not prove."
    text = "\n\n".join(sections)
    while runner.word_count(text) < word_target:
        text += filler
    return text


def final_text_with_exact_word_count(word_target: int) -> str:
    text = final_text_with_sections()
    current = runner.word_count(text)
    assert current <= word_target
    padding_words = word_target - current
    if padding_words:
        padding = ["source"] * (padding_words - 1) + ["source."]
        text = f"{text}\n\n{' '.join(padding)}"
    assert runner.word_count(text) == word_target
    return text


def d10_surfaces() -> dict:
    return runner.load_packet_surfaces(D10_PACKET_DIR)


def render_solo_final_prompt(packet_dir: Path) -> str:
    surfaces = runner.load_packet_surfaces(packet_dir)
    base = runner.packet_context(surfaces["task_brief"], surfaces["source_packet_md"])
    role, objective = runner.SOLO_TURNS[-1]
    user = (
        f"{base}\n\nTURN ROLE: {role}\nTURN OBJECTIVE: {objective}\n"
        "Return only the final artifact.\n\n"
        "PRIOR DRAFT OR NOTES\n====================\n[prior solo draft]\n"
    )
    return f"SYSTEM:\n{runner.build_base_system()}\n\nUSER:\n{user}"


def render_d10_solo_final_prompt() -> str:
    return render_solo_final_prompt(D10_PACKET_DIR)


def render_holo_final_prompt(packet_dir: Path) -> str:
    surfaces = runner.load_packet_surfaces(packet_dir)
    packet_hash = runner.sha_file(packet_dir / "source_packet.json")
    registry = {
        "artifacts": {
            "TASK_BRIEF": {"status": "PINNED", "hash": runner.sha_text(surfaces["task_brief"]), "source_reference": "task_brief.md", "content": surfaces["task_brief"]},
            "SOURCE_PACKET_MD": {"status": "PINNED", "hash": runner.sha_text(surfaces["source_packet_md"]), "source_reference": "source_packet.md", "content": surfaces["source_packet_md"]},
            "TURN_001_INITIAL_DECISION_BRIEF_DRAFTER": {
                "status": "INTERMEDIATE_ACCEPTED",
                "hash": "accepted_hash",
                "source_reference": "raw_outputs/turn_001.json",
                "content": "accepted Holo registry artifact",
            },
        }
    }
    final_band = runner.final_word_band_policy()
    state = {
        "USER_GOAL": "Produce a decision-grade crisis/action brief from the frozen packet.",
        "LATEST_INPUT_SUMMARY": surfaces["source_packet_json"].get("decision_question") or surfaces["source_packet_json"].get("crisis_frame"),
        "CRITICAL_CONSTRAINTS": [
            "Use only the frozen task brief and source packet; no browsing.",
            f"Final artifact body must be {final_band['min_words']}-{final_band['max_words']} words, target {final_band['repair_target_words']}.",
            "Separate source facts from inference and preserve claim boundaries.",
        ],
        "PACKET_HASH": packet_hash,
        "SETTLED_DECISIONS": [],
        "REQUIRED_TOOLS": [],
        "REQUIRED_PRACTICAL_RESPONSE_OPTIONS": runner.required_practical_response_options(surfaces["source_packet_json"]),
        "BATON_PASS": {},
        "GOV_NOTES": [],
    }
    retrieved_ids = runner.retrieved_ids_for_holo_turn(registry, "full_registry")
    runner.update_holobuild_state_surfaces(
        state,
        registry,
        rejected_artifact_ids=[],
        unresolved_required_roles={},
        repair_attempt_status={},
        final_synthesis_allowed_input_ids=retrieved_ids,
    )
    gov_notes = runner.gov_notes_for_turn(6, "final_synthesis_author", True, retrieved_ids, state, registry, "full_registry")
    baton = {
        "next_model": "anthropic:claude-opus-4-8",
        "adversarial_role": "final_synthesis_author",
        "focus_area": "Return final artifact.",
        "retrieved_artifact_ids": retrieved_ids,
        "required_output_behavior": "final artifact only",
        "holo_context_profile": "full_registry",
        "gov_notes": gov_notes,
    }
    state["BATON_PASS"] = baton
    state["GOV_NOTES"] = gov_notes
    state_json = runner.stable_json(state)
    baton_json = runner.stable_json(baton)
    registry_json = runner.stable_json({k: {kk: vv for kk, vv in v.items() if kk != "content"} for k, v in registry["artifacts"].items()})
    gov_notes_json = runner.stable_json(gov_notes)
    retrieved = runner.retrieved_content_for(retrieved_ids, registry)
    user = (
        "CONTEXT_GOVERNOR_INSTRUCTIONS\n=============================\n"
        f"{runner.build_context_governor_instructions('HoloGov-B', 'full_registry')}\n\n"
        "CANONICAL STATE_OBJECT\n======================\n"
        f"{state_json}\n\n"
        "GOV_NOTES\n=========\n"
        f"{gov_notes_json}\n\n"
        "BATON_PASS\n==========\n"
        f"{baton_json}\n\n"
        "ARTIFACTS_REGISTRY\n==================\n"
        f"{registry_json}\n\n"
        "RETRIEVED PINNED SOURCES AND ARTIFACTS\n======================================\n"
        f"{retrieved}\n\n"
        "ADVERSARIAL ROLE INSTRUCTION\n============================\n"
        "Role: final_synthesis_author\nObjective: Return final artifact.\n"
        "\nFINAL SYNTHESIS QUALITY BAR\n===========================\n"
        f"Return only the final decision-grade crisis/action brief. Architecture-compliance body word band is {final_band['min_words']}-{final_band['max_words']}; target about {final_band['repair_target_words']}. "
        f"Do not exceed {final_band['max_words']} words. Preserve argument power through tighter synthesis, not overage.\n"
        f"{runner.GENERATION_ARGUMENT_QUALITY_GUIDANCE}\n"
        f"{runner.FINAL_SYNTHESIS_HEADING_TEMPLATE}\n"
        f"{runner.FINAL_SYNTHESIS_CLAIM_BOUNDARY_CONTRACT}\n"
        f"{runner.FINAL_SYNTHESIS_TRIGGER_TAXONOMY}\n"
        "Include the strongest counterargument or temptation for the opposite action, then explain why the recommended path is safer, stronger, or conditional.\n"
        f"{runner.EXACT_SOURCE_ID_GENERATION_INSTRUCTION}\n"
    )
    return f"SYSTEM:\n{runner.build_base_system()}\n\nUSER:\n{user}"


def render_d10_holo_final_prompt() -> str:
    return render_holo_final_prompt(D10_PACKET_DIR)


def render_intermediate_repair_prompt_for_test(role: str = "options_operational_usefulness_reviewer") -> str:
    objective = {
        "initial_decision_brief_drafter": "Draft a source-grounded initial decision frame.",
        "assumption_and_evidence_attacker": "Attack assumptions, weak evidence, stale claims, missing calculations, and unsupported causal links.",
        "contradiction_uncertainty_source_fidelity_reviewer": "Stress-test contradictory evidence, source fidelity, source-status boundaries, and uncertainty handling.",
        "options_operational_usefulness_reviewer": "Stress-test practical options, risks, gates, and operational usefulness.",
    }.get(role, "Perform the assigned intermediate role.")
    failed_role_compliance = {
        "status": "fail",
        "missing_role_behaviors": [],
        "intermediate_artifact_completeness": {
            "status": "fail",
            "word_count": 158,
            "min_words_required": 340,
            "clean_ending": False,
            "failures": [
                "unclean_or_mid_sentence_intermediate_ending",
                "missing_options_role_component:risk_of_acting",
                "missing_options_role_component:true_before_execution",
                "missing_options_role_component:signal_permits_expansion",
                "missing_options_role_component:irreversible_action",
            ],
        },
    }
    if role == "initial_decision_brief_drafter":
        failed_role_compliance["intermediate_artifact_completeness"]["min_words_required"] = 420
        failed_role_compliance["intermediate_artifact_completeness"]["failures"] = ["unclean_or_mid_sentence_intermediate_ending"]
    if role == "assumption_and_evidence_attacker":
        failed_role_compliance["missing_role_behaviors"] = ["revision_pressure"]
        failed_role_compliance["intermediate_artifact_completeness"]["min_words_required"] = 320
        failed_role_compliance["intermediate_artifact_completeness"]["failures"] = []
    user = runner.build_intermediate_repair_user(
        role=role,
        objective=objective,
        failed_role_compliance=failed_role_compliance,
        failed_state_source_audit={"status": "pass", "packet_hash_preserved": True, "invented_source_ids": []},
        context_governor_instructions=runner.build_context_governor_instructions("HoloGov-B", "full_registry"),
        state_json=runner.stable_json({"PACKET_HASH": "packet_hash", "FINAL_SYNTHESIS_ALLOWED_INPUT_IDS": []}),
        gov_notes_json=runner.stable_json(["test gov note"]),
        baton_json=runner.stable_json({"adversarial_role": role}),
        registry_json=runner.stable_json({"TASK_BRIEF": {"status": "PINNED"}, "SOURCE_PACKET_MD": {"status": "PINNED"}}),
        retrieved="ARTIFACT_ID: TASK_BRIEF\n[task]\n\nARTIFACT_ID: SOURCE_PACKET_MD\n[source]",
    )
    return f"SYSTEM:\n{runner.build_base_system()}\n\nUSER:\n{user}"


def render_t3_overword_repair_prompt_for_test() -> str:
    text = synthetic_t3_concise_audit_text(extra_words=260)
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        text,
        final=False,
        output_meta={},
    )
    user = runner.build_intermediate_repair_user(
        role="contradiction_uncertainty_source_fidelity_reviewer",
        objective="Stress-test contradictory evidence, source fidelity, source-status boundaries, and uncertainty handling.",
        failed_role_compliance=compliance,
        failed_state_source_audit={"status": "pass", "packet_hash_preserved": True, "invented_source_ids": []},
        context_governor_instructions=runner.build_context_governor_instructions("HoloGov-B", "full_registry"),
        state_json=runner.stable_json({"PACKET_HASH": "packet_hash", "FINAL_SYNTHESIS_ALLOWED_INPUT_IDS": []}),
        gov_notes_json=runner.stable_json(["test gov note"]),
        baton_json=runner.stable_json({"adversarial_role": "contradiction_uncertainty_source_fidelity_reviewer"}),
        registry_json=runner.stable_json({"TASK_BRIEF": {"status": "PINNED"}, "SOURCE_PACKET_MD": {"status": "PINNED"}}),
        retrieved="ARTIFACT_ID: TASK_BRIEF\n[task]\n\nARTIFACT_ID: SOURCE_PACKET_MD\n[source]",
    )
    return f"SYSTEM:\n{runner.build_base_system()}\n\nUSER:\n{user}"


def render_d14_t3_compression_repair_prompt_for_test() -> str:
    raw = d14_t3_failure_raw_output("turn_003.json")
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        raw["text"],
        final=False,
        output_meta=raw,
    )
    user = runner.build_intermediate_repair_user(
        role="contradiction_uncertainty_source_fidelity_reviewer",
        objective="Stress-test contradictory evidence, source fidelity, source-status boundaries, and uncertainty handling.",
        failed_role_compliance=compliance,
        failed_state_source_audit={"status": "pass", "packet_hash_preserved": True, "invented_source_ids": []},
        context_governor_instructions=runner.build_context_governor_instructions("HoloGov-B", "full_registry"),
        state_json=runner.stable_json({"PACKET_HASH": "packet_hash", "FINAL_SYNTHESIS_ALLOWED_INPUT_IDS": []}),
        gov_notes_json=runner.stable_json(["test gov note"]),
        baton_json=runner.stable_json({"adversarial_role": "contradiction_uncertainty_source_fidelity_reviewer"}),
        registry_json=runner.stable_json({"TASK_BRIEF": {"status": "PINNED"}, "SOURCE_PACKET_MD": {"status": "PINNED"}}),
        retrieved="ARTIFACT_ID: TASK_BRIEF\n[task]\n\nARTIFACT_ID: SOURCE_PACKET_MD\n[source]",
    )
    return f"SYSTEM:\n{runner.build_base_system()}\n\nUSER:\n{user}"


def synthetic_t3_concise_audit_text(extra_words: int = 0, omit_section: str | None = None) -> str:
    sections = {
        "Top 5 source-boundary risks": [
            "Risk one: do not let S1_TEST_SOURCE become approval for facts that S1_TEST_SOURCE does not contain, because source boundaries decide whether the final can act.",
            "Risk two: do not merge S2_PRELIMINARY_ADMIN_NOTE with governing authority; it is preliminary and cannot settle a final action threshold.",
            "Risk three: do not treat S3_DERIVED_TABLE as independent authority when it only organizes estimates and pressure points from other packet facts.",
            "Risk four: do not treat S4_INTERNAL_NOTE as governing authority if the packet labels it internal, stale, weak, or limited in source status.",
            "Risk five: do not let a prior turn's confident wording become evidence; the final must cite exact packet source IDs for each factual claim.",
        ],
        "Top 5 uncertainty claims to preserve": [
            "Uncertainty one: the packet does not prove final approval, so the final must say not shown rather than failed or denied.",
            "Uncertainty two: the packet does not resolve timing, so the final must keep the decision conditional until S1_TEST_SOURCE and S2_PRELIMINARY_ADMIN_NOTE align.",
            "Uncertainty three: the packet does not prove operational readiness, even if S3_DERIVED_TABLE looks precise and decision-ready.",
            "Uncertainty four: the packet leaves the governing interpretation open, so the final cannot collapse uncertainty into a single authoritative conclusion.",
            "Uncertainty five: the strongest counterargument may support reversible preparation, but it does not supply irreversible action authority.",
        ],
        "Stale / weak / derived source cautions": [
            "Caution one: stale sources may explain context but must not override current governing packet authority or exact approval gates.",
            "Caution two: weak sources may support communication tone but must not carry dispositive weight for operational authority.",
            "Caution three: derived tables must remain labeled derived, estimated, and non-authoritative unless another exact source ID grants authority.",
            "Caution four: preliminary notes must remain preliminary and cannot be upgraded because they sound specific or administrative.",
            "Caution five: internal relationship pressure must remain a pressure fact, not a control approval or source of execution authority.",
        ],
        "Exact source-ID audit": [
            "Audit one: cite S1_TEST_SOURCE exactly when using governing authority and do not abbreviate it to S1.",
            "Audit two: cite S2_PRELIMINARY_ADMIN_NOTE exactly when using preliminary status and do not rename it as final approval.",
            "Audit three: cite S3_DERIVED_TABLE exactly when using calculations and label every calculation as derived from that table.",
            "Audit four: cite S4_INTERNAL_NOTE exactly when using urgency or pressure, but do not transform it into approval evidence.",
            "Audit five: no invented source IDs, no shortened IDs, and no uncited factual claims should enter the final synthesis.",
        ],
        "Action-boundary cautions": [
            "Caution one: preserve the central tension between urgency and authority rather than deciding from urgency alone.",
            "Caution two: present the strongest opposing argument before explaining why reversible preparation is the safer action path.",
            "Caution three: convert unresolved facts into stop/go triggers, owner checks, and evidence thresholds.",
            "Caution four: keep derived, stale, weak, preliminary, and internal materials below governing authority in the decision hierarchy.",
            "Caution five: keep the supported action boundary at conditional preparation rather than final execution authority.",
        ],
    }
    expansion = " Keep authority hierarchy, uncertainty, source status, and action boundaries explicit."
    text = "\n\n".join(
        f"## {heading}\n" + "\n".join(f"- {item}{expansion}" for item in items)
        for heading, items in sections.items()
        if heading != omit_section
    )
    if extra_words:
        text += " " + " ".join(["extra"] * extra_words) + "."
    return text


def synthetic_t3_under_target_but_substantive_text() -> str:
    compact_expansion = " Preserve the gate, source rank, reversible boundary, authority chain, and unresolved evidence threshold."
    sections = {
        "Top 5 source-boundary risks": [
            "S1_TEST_SOURCE controls authority; S3_DERIVED_TABLE may organize facts but cannot approve execution." + compact_expansion,
            "S2_PRELIMINARY_ADMIN_NOTE remains preliminary and cannot become final approval through specificity." + compact_expansion,
            "S4_INTERNAL_NOTE shows pressure only; it cannot supply a missing governing gate." + compact_expansion,
        ],
        "Top 5 uncertainty claims to preserve": [
            "The packet does not prove final approval, so state not shown rather than denied." + compact_expansion,
            "Timing remains conditional until S1_TEST_SOURCE and S2_PRELIMINARY_ADMIN_NOTE align." + compact_expansion,
            "Operational readiness remains unresolved even if S3_DERIVED_TABLE appears precise." + compact_expansion,
        ],
        "Stale / weak / derived source cautions": [
            "Stale sources explain context but must stay below current governing authority." + compact_expansion,
            "Weak sources can shape tone but cannot carry dispositive execution weight." + compact_expansion,
            "Derived tables must remain labeled non-authoritative unless a source grants authority." + compact_expansion,
        ],
        "Exact source-ID audit": [
            "Use S1_TEST_SOURCE exactly for governing authority, not shorthand or renamed labels." + compact_expansion,
            "Use S2_PRELIMINARY_ADMIN_NOTE exactly for preliminary status and no final approval." + compact_expansion,
            "Use S3_DERIVED_TABLE and S4_INTERNAL_NOTE exactly when citing calculations or pressure." + compact_expansion,
        ],
        "Action-boundary cautions": [
            "The action boundary supports reversible preparation while blocking final execution." + compact_expansion,
            "The counterargument can support triage speed, not authority to cross a gate." + compact_expansion,
            "Stop/go triggers must preserve owner checks, evidence thresholds, and source hierarchy." + compact_expansion,
        ],
    }
    return "\n\n".join(
        f"## {heading}\n" + "\n".join(f"- {item}" for item in items)
        for heading, items in sections.items()
    )


def synthetic_options_repair_text(omit_heading: str | None = None) -> str:
    sections = [
        (
            "Available options",
            "Available options are to deny the broad change, hold the manual workaround, approve a narrow time-boxed path, or escalate to named owners when source boundaries are not satisfied.",
        ),
        (
            "Risk of acting",
            "Risk of acting is execution risk because approving a broad path can create blast radius beyond the packet's tested control boundary.",
        ),
        (
            "Risk of waiting",
            "Risk of waiting is delay risk because the customer processing window can close while the manual workaround loses throughput and leadership waits.",
        ),
        (
            "Must be true before execution",
            "Must be true before execution: owners must confirm approvals, policy preview must pass, logging must be active, and source IDs must support the narrower path.",
        ),
        (
            "Stop/go triggers",
            "Stop/go triggers are the explicit halt trigger, go trigger, proceed-only-if gate, and block-execution-if condition that leadership must use.",
        ),
        (
            "Signal that stops execution",
            "Signal that stops execution is any threshold breach, unexpected delete attempt, cross-prefix write, missing approval, or failed audit trail.",
        ),
        (
            "Signal that permits expansion",
            "Signal that permits expansion is a completed canary with zero cross-prefix writes, zero unexpected delete calls, and metrics inside the approved limit.",
        ),
        (
            "What can be reversed",
            "What can be reversed includes the network allow rule, the scoped policy grant, and the manual hold through rollback or revocation.",
        ),
        (
            "What cannot be reversed",
            "What cannot be reversed is external reliance after release, permanent effect from deleted data outside backup recovery, and irreversible exposure of customer information.",
        ),
        (
            "Rollback gates",
            "Rollback gates require a named owner, a policy version to restore, a security group rule to revoke, and a verified stop threshold.",
        ),
        (
            "Monitoring/logging gates",
            "Monitoring/logging gates require object-level logs, centralized audit ingest, alerts, and observable metrics before trust is assigned.",
        ),
        (
            "Executive next actions",
            "Executive next actions are to assign the accountable owner, approve the narrow option, publish the trigger table, and escalate if a gate fails.",
        ),
        (
            "Dependency chain",
            "Dependency chain is first policy preview, then approval confirmation, then canary replay, then leadership review after metric review.",
        ),
        (
            "What must be observable before rollback/canary can be trusted",
            "What must be observable before rollback/canary can be trusted is terminated broad connectivity, revoked delete permission, clean canary metrics, and audit logs proving the control action executed.",
        ),
    ]
    text = "\n\n".join(
        f"## {heading}\n{body}"
        for heading, body in sections
        if heading != omit_heading
    )
    filler = (
        "\n\nOperational note: when any trigger fails, the owner must stop the path, keep the record source bounded, "
        "and preserve accountable leadership review rather than treating speed as proof of safety."
    )
    while runner.word_count(text) < 360:
        text += filler
    return text + "\n\nThis repaired review ends with a complete standalone sentence."


def keyword_stuffed_options_repair_text() -> str:
    fragment = (
        "Available options Risk of acting Risk of waiting Must be true before execution "
        "Signal that stops execution Signal that permits expansion What can be reversed "
        "What cannot be reversed Rollback gates Monitoring logging gates Executive next actions "
        "Dependency chain observable rollback canary trusted "
    )
    return (fragment * 18).strip() + "."


def synthetic_assumption_repair_text(include_revision_pressure: bool = True) -> str:
    text = (
        "The assumption attack should challenge the premise that the infrastructure change is safe merely because the customer impact window is urgent. "
        "The packet supports a narrow controlled path from S1_TEST_SOURCE and S2_TEST_SOURCE, but it does not prove that broad access, delete-capable permissions, or unmonitored expansion are acceptable. "
        "A weak evidence link is the leap from successful manual workaround to production readiness; that assumption must be challenged because manual throughput is not the same as automated blast-radius control. "
        "Another unsupported claim is that approval exists for the full change, even though S1_TEST_SOURCE and S2_TEST_SOURCE support only a narrower source-bounded path. "
    )
    if include_revision_pressure:
        text += (
            "Revision pressure: the final should revise the recommendation into a conditional narrow go path, should avoid implying broad authorization, must include what assumptions remain unproven, and must tighten the unsupported claim that monitoring alone makes the change safe. "
            "The final should preserve exact source IDs copied from the packet and must not invent, abbreviate, rename, shorten, or mutate source IDs. "
        )
    else:
        text += (
            "The critique notes evidence limits and source boundaries while describing the main unsupported assumptions in ordinary terms. "
        )
    filler = (
        "The repaired attacker output remains source bounded, names the assumption, names the weak evidence, identifies the unsupported claim, and gives concrete constraints. "
    )
    while runner.word_count(text) < 340:
        text += filler
    return text + "This assumption and evidence repair ends with a complete standalone sentence."


def synthetic_initial_decision_text(truncated: bool = False) -> str:
    text = (
        "The decision frame recommends a conditional path grounded in the frozen source packet and rejects any broader approval that the packet does not support. "
        "Available options include denial of the broad request, a narrow time-boxed path, continued manual workaround, executive escalation, and a staged canary. "
        "The source grounding is explicit because each claim stays bounded to the packet facts, source IDs, operational constraints, and missing approvals rather than browsing or inventing authority. "
    )
    filler = (
        "The initial brief keeps the decision conditional, separates source facts from inference, preserves the packet boundary, and identifies the owner-visible choice that later reviewers must attack. "
    )
    while runner.word_count(text) < 430:
        text += filler
    text += "This initial decision brief closes with one complete standalone sentence."
    if truncated:
        text += "\n\n* Scope reduction: the narrowed network path remains incomplete at (/29 vs"
    return text


def d10_post_v4_2_arch_evidence() -> dict:
    return json.loads((D10_POST_V4_2_CONDITION_DIR / "arch_evidence.json").read_text(encoding="utf-8"))


def d10_post_v4_2_raw_output(name: str) -> dict:
    return json.loads((D10_POST_V4_2_CONDITION_DIR / "raw_outputs" / name).read_text(encoding="utf-8"))


def d12_t3_failure_raw_output(name: str) -> dict:
    return json.loads((D12_T3_FAILURE_CONDITION_DIR / "raw_outputs" / name).read_text(encoding="utf-8"))


def d12_t3_failure_arch_evidence() -> dict:
    return json.loads((D12_T3_FAILURE_CONDITION_DIR / "arch_evidence.json").read_text(encoding="utf-8"))


def d12_retry2_raw_output(name: str) -> dict:
    return json.loads((D12_RETRY2_CONDITION_DIR / "raw_outputs" / name).read_text(encoding="utf-8"))


def d12_retry2_metadata() -> dict:
    return json.loads((D12_RETRY2_CONDITION_DIR / "artifact_metadata.json").read_text(encoding="utf-8"))


def d12_retry3_raw_output(name: str) -> dict:
    return json.loads((D12_RETRY3_CONDITION_DIR / "raw_outputs" / name).read_text(encoding="utf-8"))


def d14_t3_failure_raw_output(name: str) -> dict:
    return json.loads((D14_T3_FAILURE_CONDITION_DIR / "raw_outputs" / name).read_text(encoding="utf-8"))


def d14_t3_failure_manifest() -> dict:
    return json.loads(D14_T3_FAILURE_RUN_MANIFEST.read_text(encoding="utf-8"))


def d14_t3_failure_arch_evidence() -> dict:
    return json.loads((D14_T3_FAILURE_CONDITION_DIR / "arch_evidence.json").read_text(encoding="utf-8"))


def d14_retry2_raw_output(name: str) -> dict:
    return json.loads((D14_RETRY2_CONDITION_DIR / "raw_outputs" / name).read_text(encoding="utf-8"))


def d12_retry3_metadata() -> dict:
    return json.loads((D12_RETRY3_CONDITION_DIR / "artifact_metadata.json").read_text(encoding="utf-8"))


def d12_retry3_run_manifest() -> dict:
    return json.loads((D12_RETRY3_CONDITION_DIR.parent / "run_manifest.json").read_text(encoding="utf-8"))


def d10_post_v4_2_final_prompt_state() -> tuple[str, dict]:
    prompt = (D10_POST_V4_2_CONDITION_DIR / "prompt_cards/turn_006.md").read_text(encoding="utf-8")
    match = re.search(r"CANONICAL STATE_OBJECT\n=+\n(\{.*?\})\n\nSTATE_OBJECT_SHA256:", prompt, flags=re.S)
    assert match
    return prompt, json.loads(match.group(1))


def assert_common_generation_contract(prompt: str) -> None:
    assert "Final artifact body must be 900-1,300 words" in prompt
    assert runner.EXACT_SOURCE_ID_GENERATION_INSTRUCTION in prompt
    for term in FORBIDDEN_GENERATION_CONTRACT_TERMS:
        assert term not in prompt


def test_runtime_loads_v4_2_policy_thresholds_from_policy_file() -> None:
    policy = runner.load_architecture_policy()
    assert policy["policy_id"] == "HOLOBUILD_ARCHITECTURE_POLICY_V4_2"
    assert runner.architecture_policy_ref()["policy_id"] == "HOLOBUILD_ARCHITECTURE_POLICY_V4_2"
    assert runner.intermediate_default_min_words() == policy["intermediate_registry_gate"]["default_min_visible_words"]
    assert runner.intermediate_role_min_words() == policy["intermediate_registry_gate"]["role_min_visible_words"]
    assert runner.final_word_band_policy()["max_words"] == policy["final_word_band_compliance"]["max_words"]
    assert runner.final_word_band_compliance(" ".join(["word"] * 1301))["threshold_source"].endswith("holobuild_architecture_policy_v4_2.json")


def test_solo_prompt_has_common_hard_contract_without_hologov_surfaces() -> None:
    prompt = render_d10_solo_final_prompt()
    assert_common_generation_contract(prompt)
    assert "TURN ROLE: final_synthesis_900_1300_words" in prompt
    assert "final_synthesis_900_1500_words" not in prompt
    assert "HoloGov-B" not in prompt
    assert "CANONICAL STATE_OBJECT" not in prompt
    assert "ARTIFACTS_REGISTRY" not in prompt
    assert "BATON_PASS" not in prompt
    assert "PROOF_CREDIT_ELIGIBILITY_STATE" not in prompt
    assert "FINAL_SYNTHESIS_ALLOWED_INPUT_IDS" not in prompt


def test_holo_prompt_has_common_hard_contract_and_architecture_surfaces() -> None:
    prompt = render_d10_holo_final_prompt()
    assert_common_generation_contract(prompt)
    assert runner.FINAL_SYNTHESIS_HEADING_TEMPLATE in prompt
    assert runner.FINAL_SYNTHESIS_CLAIM_BOUNDARY_CONTRACT in prompt
    assert "HoloGov-B" in prompt
    assert "CONTEXT_GOVERNOR_INSTRUCTIONS" in prompt
    assert "CANONICAL STATE_OBJECT" in prompt
    assert "ARTIFACTS_REGISTRY" in prompt
    assert "BATON_PASS" in prompt
    assert "PROOF_CREDIT_ELIGIBILITY_STATE" in prompt
    assert "FINAL_SYNTHESIS_ALLOWED_INPUT_IDS" in prompt
    assert "ACCEPTED_ARTIFACT_REGISTRY" in prompt


def test_options_repair_prompt_renders_v4_2_required_checklist() -> None:
    prompt = render_intermediate_repair_prompt_for_test("options_operational_usefulness_reviewer")
    assert "OPTIONS OPERATIONAL REPAIR REQUIRED CHECKLIST" in prompt
    assert "validated against the V4.2 options_operational_usefulness_reviewer role-specific validator" in prompt
    assert "Omission of any required component fails the repair" in prompt
    assert "Keyword-only output still fails" in prompt
    assert "- Stop/go triggers" in prompt
    for heading in runner.OPTIONS_OPERATIONAL_REPAIR_CHECKLIST_ITEMS:
        assert f"- {heading}" in prompt


def test_assumption_repair_prompt_renders_revision_pressure_and_source_id_checklist() -> None:
    prompt = render_intermediate_repair_prompt_for_test("assumption_and_evidence_attacker")
    assert "ASSUMPTION AND EVIDENCE ATTACKER REPAIR REQUIRED CHECKLIST" in prompt
    assert "- Revision pressure" in prompt
    assert "- What the final should revise" in prompt
    assert "- What the final should avoid" in prompt
    assert "- What assumptions must be challenged" in prompt
    assert "- What unsupported claim must be tightened" in prompt
    assert "- Source-ID copy discipline" in prompt
    assert "Do not invent, abbreviate, rename, shorten, or mutate source IDs." in prompt


def test_t3_repair_prompt_contains_five_section_compact_audit_format() -> None:
    prompt = render_intermediate_repair_prompt_for_test("contradiction_uncertainty_source_fidelity_reviewer")
    assert "T3 COMPACT SOURCE-FIDELITY REPAIR REQUIRED FORMAT" in prompt
    for index, heading in enumerate(runner.T3_CONCISE_AUDIT_SECTION_ITEMS, start=1):
        assert f"{index}. {heading}" in prompt


def test_t3_repair_prompt_forbids_prose_essay_and_prior_continuation() -> None:
    prompt = render_intermediate_repair_prompt_for_test("contradiction_uncertainty_source_fidelity_reviewer")
    assert "The previous T3 failed because a required section, source-ID discipline, or minimum substance was missing." in prompt
    assert "Return only the corrected compact T3 audit." in prompt
    assert "Do not continue the prior text." in prompt
    assert "Do not produce an essay." in prompt
    assert "Use bullet-only format with no intro, conclusion, prose paragraphs, appendix, or word-count footer." in prompt


def test_t3_repair_prompt_requires_550_800_words_and_complete_ending() -> None:
    prompt = render_intermediate_repair_prompt_for_test("contradiction_uncertainty_source_fidelity_reviewer")
    assert "Target 550-800 words; prefer 600-720 words." in prompt
    assert "Under 550 words is acceptable only when all required sections, exact source IDs, and substantive bullets are present." in prompt
    assert "3-5 bullets per section" in prompt
    assert f"no more than {runner.T3_CONCISE_AUDIT_MAX_BULLETS} bullets total" in prompt
    assert f"no more than {runner.T3_CONCISE_AUDIT_MAX_SECTION_WORDS} words per section" in prompt
    assert "Action-boundary cautions" in prompt
    assert "5. Final synthesis instructions" not in prompt
    assert "Do not include meta sections such as Final synthesis instructions." in prompt
    assert "End with one complete standalone sentence." in prompt
    assert "Do not append a word-count footer." in prompt


def test_t3_overword_repair_prompt_is_bounded_and_not_truncation_repair() -> None:
    prompt = render_t3_overword_repair_prompt_for_test()
    assert "T3 BOUNDED COMPRESSION-ONLY SOURCE-FIDELITY REPAIR REQUIRED FORMAT" in prompt
    assert "Compress the audit; do not restart it with more scope." in prompt
    assert "incomplete/truncated" not in prompt
    assert "Return only the corrected compact T3 audit." in prompt
    assert "Do not continue the prior text." in prompt
    assert "Do not produce an essay." in prompt
    assert "Target 550-800 words." in prompt
    assert "Preferred repair window is 600-720 words; never exceed 800 words." in prompt
    assert "Use bullet-only format with no intro, conclusion, prose paragraphs, appendix, or word-count footer." in prompt
    assert "Action-boundary cautions" in prompt
    assert "5. Final synthesis instructions" not in prompt
    assert "End with one complete standalone sentence." in prompt
    assert f"capped at {runner.T3_OVERWORD_REPAIR_MAX_TOKENS} tokens" in prompt


def test_current_contract_t3_overword_repair_uses_bounded_token_budget() -> None:
    text = synthetic_t3_concise_audit_text(extra_words=260)
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        text,
        final=False,
        output_meta={},
    )
    assert runner.t3_overword_repair_required(compliance) is True
    assert (
        runner.intermediate_repair_max_tokens_for_failure(
            "contradiction_uncertainty_source_fidelity_reviewer",
            compliance,
        )
        == runner.T3_OVERWORD_REPAIR_MAX_TOKENS
    )


def test_missing_section_t3_repair_keeps_full_intermediate_repair_budget() -> None:
    text = synthetic_t3_concise_audit_text(omit_section="Exact source-ID audit")
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        text,
        final=False,
        output_meta={},
    )
    assert runner.t3_overword_repair_required(compliance) is False
    assert (
        runner.intermediate_repair_max_tokens_for_failure(
            "contradiction_uncertainty_source_fidelity_reviewer",
            compliance,
        )
        == runner.INTERMEDIATE_REPAIR_MAX_TOKENS
    )


def test_initial_decision_repair_prompt_includes_clean_terminal_contract() -> None:
    prompt = render_intermediate_repair_prompt_for_test("initial_decision_brief_drafter")
    assert "INTERMEDIATE REPAIR CLEAN ENDING CONTRACT" in prompt
    assert "End with one complete standalone sentence." in prompt
    assert "Do not end mid-sentence." in prompt
    assert "Do not end in an unfinished list item." in prompt
    assert "dangling parenthesis, slash, markdown emphasis, code fence, table row, JSON fragment, or metadata/footer" in prompt
    assert "Do not append a word-count footer." in prompt
    assert "OPTIONS OPERATIONAL REPAIR REQUIRED CHECKLIST" not in prompt


def test_d10_opus_gov_b_config_resolves_to_runnable_config_not_template_lock() -> None:
    configs = runner.load_configs()
    for condition in ("frontier_holo_opus_gov_b_v1", "holo_build_arch_opus_gov_b"):
        cfg = runner.config_for_condition(condition, configs)
        assert cfg["config_id"] == "frontier_holo_opus_gov_b_v1"
        assert cfg["condition_type"] == "holo"
        assert cfg["hologov_profile"] == "HoloGov-B"
        assert len(cfg["model_pool"]) == 3
        assert cfg["governor_model_pool"] == ["anthropic:claude-opus-4-8"]
        plan = runner.randomized_holo_session_plan(
            cfg,
            run_id="PROMPT_PARITY_NO_PROVIDER",
            packet_hash="packet_hash",
            turn_count=len(runner.HOLO_TURNS),
            session_template="opus_gov_b_v1",
        )
        assert plan["hologov_profile"] == "HoloGov-B"
        assert plan["final_synthesis_model"] == "anthropic:claude-opus-4-8"


def test_d10_frontier_optimized_opus_gpt55_config_resolves_to_runnable_config() -> None:
    configs = runner.load_configs()
    for condition in (
        "frontier_holo_optimized_opus_gpt55_v1",
        "holo_build_arch_frontier_optimized_opus_gpt55",
        "HoloFrontierOptimizedOpusGPT55",
    ):
        cfg = runner.config_for_condition(condition, configs)
        assert cfg["config_id"] == "frontier_holo_optimized_opus_gpt55_v1"
        assert cfg["condition_type"] == "holo"
        assert cfg["architecture_mode"] == "patent_aligned_v4"
        assert cfg["hologov_profile"] == "HoloGov-B"
        models = [item["provider_model"] for item in cfg["model_pool"]]
        assert models == [
            "anthropic:claude-opus-4-8",
            "openai:gpt-5.5",
        ]
        assert cfg["distinct_holo_agent_model_count"] == 2
        assert cfg["governor_model_pool"] == ["anthropic:claude-opus-4-8"]
        assert cfg["final_synthesis_model"] == "anthropic:claude-opus-4-8"
        assert cfg["final_compression_repair_model"] == "openai:gpt-5.5"
        assert "grok" not in " ".join(models).lower()
        assert "gemini" not in " ".join(models).lower()
        plan = runner.randomized_holo_session_plan(
            cfg,
            run_id="D10_FRONTIER_OPTIMIZED_NO_PROVIDER",
            packet_hash="packet_hash",
            turn_count=len(runner.HOLO_TURNS),
            session_template="frontier_optimized_opus_gpt55_v1",
        )
        assert plan["hologov_schedule"][0]["governor_model"] == "anthropic:claude-opus-4-8"
        assert plan["holo_agent_turn_models"] == [
            "openai:gpt-5.5",
            "openai:gpt-5.5",
            "anthropic:claude-opus-4-8",
            "openai:gpt-5.5",
            "openai:gpt-5.5",
            "anthropic:claude-opus-4-8",
        ]
        assert plan["final_synthesis_model"] == "anthropic:claude-opus-4-8"
        assert plan["final_compression_repair_model"] == "openai:gpt-5.5"
        assert runner.final_repair_model_for_kind(
            runner.FINAL_REPAIR_KIND_COMPRESSION_ONLY,
            plan["final_synthesis_model"],
            plan,
        ) == "openai:gpt-5.5"
        assert runner.final_repair_model_for_kind(
            runner.FINAL_REPAIR_KIND_MISSING_SECTION,
            plan["final_synthesis_model"],
            plan,
        ) == "anthropic:claude-opus-4-8"
        roster = runner.holo_turn_plan(plan)
        assert roster[0][1] == "openai:gpt-5.5"
        assert roster[1][1] == "openai:gpt-5.5"
        assert roster[2][1] == "anthropic:claude-opus-4-8"
        assert roster[3][1] == "openai:gpt-5.5"
        assert roster[4][1] == "openai:gpt-5.5"
        assert roster[5][1] == "anthropic:claude-opus-4-8"


def test_final_compression_repair_model_default_does_not_change_other_configs() -> None:
    cfg = runner.config_for_condition("frontier_holo_opus_gov_b_v1", runner.load_configs())
    plan = runner.randomized_holo_session_plan(
        cfg,
        run_id="D10_OPUS_GOV_B_NO_PROVIDER",
        packet_hash="packet_hash",
        turn_count=len(runner.HOLO_TURNS),
        session_template="opus_gov_b_v1",
    )
    assert cfg.get("final_compression_repair_model") is None
    assert plan["final_synthesis_model"] == "anthropic:claude-opus-4-8"
    assert plan["final_compression_repair_model"] == "anthropic:claude-opus-4-8"
    assert runner.final_repair_model_for_kind(
        runner.FINAL_REPAIR_KIND_COMPRESSION_ONLY,
        plan["final_synthesis_model"],
        plan,
    ) == "anthropic:claude-opus-4-8"


def test_d10_frontier_optimized_config_does_not_select_solo_or_d11() -> None:
    cfg = runner.config_for_condition(
        "holo_build_arch_frontier_optimized_opus_gpt55",
        runner.load_configs(),
    )
    serialized = json.dumps(cfg, sort_keys=True).lower()
    assert cfg["condition_type"] == "holo"
    assert "solo_anthropic_claude_opus_4_8" not in serialized
    assert "frontier_solo_opus_4_8_v1" not in serialized
    assert "d11_cyber_incident_contract_notice_emergency_cloud_access_001" not in serialized
    assert "d10_infrastructure_configuration_change_001" not in serialized


def test_d11_packet_validator_remains_no_provider_pass() -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(D11_VALIDATOR)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["status"] == "D11_MINI_SCOUT_PACKET_VALIDATION_PASS"
    assert payload["provider_calls"] == 0


def test_d11_runner_domain_gate_accepts_and_resolves_cyber_packet() -> None:
    runner_text = RUNNER_PATH.read_text(encoding="utf-8")
    assert 'choices=[f"D{i}" for i in range(1, 14)]' in runner_text

    manifest = runner.load_suite_manifest(runner.DEFAULT_SUITE_MANIFEST)
    packet_dir, entry = runner.resolve_packet_dir(
        argparse.Namespace(domain="D11", packet_dir=None),
        manifest,
    )
    assert packet_dir == D11_PACKET_DIR.resolve()
    assert entry["domain_id"] == "D11"
    assert entry["packet_id"] == "d11_cyber_incident_contract_notice_emergency_cloud_access_001"
    assert entry["packet_dir"] == "artifact_benchmarks/holo_factory/mini_scouts/d11_cyber_incident_contract_notice_emergency_cloud_access_001"
    assert "d10_infrastructure_configuration_change_001" not in entry["packet_dir"]

    validated = runner.validate_packet_against_manifest(packet_dir, entry)
    assert validated["hashes"]["packet_hash"] == D11_PACKET_HASH
    assert validated["hashes"]["packet_lock_hash"] == D11_PACKET_LOCK_HASH


def test_d12_runner_domain_gate_accepts_and_resolves_fund_nav_packet() -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(D12_VALIDATOR)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["status"] == "D12_MINI_SCOUT_PACKET_VALIDATION_PASS"
    assert payload["provider_calls"] == 0

    manifest = runner.load_suite_manifest(runner.DEFAULT_SUITE_MANIFEST)
    packet_dir, entry = runner.resolve_packet_dir(
        argparse.Namespace(domain="D12", packet_dir=None),
        manifest,
    )
    assert packet_dir == D12_PACKET_DIR.resolve()
    assert entry["domain_id"] == "D12"
    assert entry["packet_id"] == "d12_fund_nav_redemption_cash_release_001"
    assert entry["packet_dir"] == "artifact_benchmarks/holo_factory/mini_scouts/d12_fund_nav_redemption_cash_release_001"

    validated = runner.validate_packet_against_manifest(packet_dir, entry)
    assert validated["hashes"]["packet_hash"] == D12_PACKET_HASH
    assert validated["hashes"]["packet_lock_hash"] == D12_PACKET_LOCK_HASH


def test_d13_runner_domain_gate_accepts_and_resolves_treasury_sanctions_packet() -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(D13_VALIDATOR)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["status"] == "D13_MINI_SCOUT_PACKET_VALIDATION_PASS"
    assert payload["provider_calls"] == 0
    assert payload["judging_runs"] == 0
    assert payload["scores_generated"] == 0

    manifest = runner.load_suite_manifest(runner.DEFAULT_SUITE_MANIFEST)
    packet_dir, entry = runner.resolve_packet_dir(
        argparse.Namespace(domain="D13", packet_dir=None),
        manifest,
    )
    assert packet_dir == D13_PACKET_DIR.resolve()
    assert entry["domain_id"] == "D13"
    assert entry["packet_id"] == "d13_treasury_sanctions_payment_release_001"
    assert entry["packet_dir"] == "artifact_benchmarks/holo_factory/mini_scouts/d13_treasury_sanctions_payment_release_001"

    validated = runner.validate_packet_against_manifest(packet_dir, entry)
    assert validated["hashes"]["packet_hash"] == D13_PACKET_HASH
    assert validated["hashes"]["packet_lock_hash"] == D13_PACKET_LOCK_HASH


def test_d11_optimized_holo_config_resolves_to_fixed_opus_gpt55_roster() -> None:
    cfg = runner.config_for_condition(
        "holo_build_arch_frontier_optimized_opus_gpt55",
        runner.load_configs(),
    )
    plan = runner.randomized_holo_session_plan(
        cfg,
        run_id="D11_FRONTIER_OPTIMIZED_NO_PROVIDER",
        packet_hash=D11_PACKET_HASH,
        turn_count=len(runner.HOLO_TURNS),
        session_template="frontier_optimized_opus_gpt55_v1",
    )
    assert cfg["config_id"] == "frontier_holo_optimized_opus_gpt55_v1"
    assert cfg["condition_type"] == "holo"
    assert cfg["architecture_mode"] == "patent_aligned_v4"
    assert cfg["hologov_profile"] == "HoloGov-B"
    assert cfg["governor_model_pool"] == ["anthropic:claude-opus-4-8"]
    assert plan["hologov_schedule"][0]["governor_model"] == "anthropic:claude-opus-4-8"
    assert plan["holo_agent_turn_models"] == [
        "openai:gpt-5.5",
        "openai:gpt-5.5",
        "anthropic:claude-opus-4-8",
        "openai:gpt-5.5",
        "openai:gpt-5.5",
        "anthropic:claude-opus-4-8",
    ]
    assert plan["final_synthesis_model"] == "anthropic:claude-opus-4-8"
    assert plan["final_compression_repair_model"] == "openai:gpt-5.5"

    prompt = render_holo_final_prompt(D11_PACKET_DIR)
    assert_common_generation_contract(prompt)
    assert "HoloGov-B" in prompt
    assert "FINAL_SYNTHESIS_ALLOWED_INPUT_IDS" in prompt
    assert "PROOF_CREDIT_ELIGIBILITY_STATE" in prompt


def test_d11_fresh_solo_opus_config_resolves_as_six_call_sequential_solo() -> None:
    cfg = runner.config_for_condition("solo_anthropic_claude_opus_4_8", runner.load_configs())
    assert cfg["config_id"] == "frontier_solo_opus_4_8_v1"
    assert cfg["condition_type"] == "solo"
    assert cfg["architecture_mode"] == "solo_self_refine_v1"
    assert [item["provider_model"] for item in cfg["model_pool"]] == ["anthropic:claude-opus-4-8"]
    assert cfg.get("governor_model_pool", []) == []
    assert cfg["proof_credit_eligible"] is False

    structure = cfg["solo_call_structure"]
    assert structure["provider_calls"] == 6
    assert structure["calls_are_sequential_drafting"] is True
    assert structure["calls_are_independent_attempts"] is False
    assert structure["selection_across_multiple_solo_outputs"] is False
    assert structure["artifact_registry"] is False
    assert structure["gov_notes"] is False
    assert structure["comparison_labels"] == [
        "six-call solo",
        "budget-matched solo",
        "sequential solo chain",
    ]
    assert structure["excluded_comparison_labels"] == [
        "one-shot solo",
        "best-of-N solo",
        "retry-expanded solo",
    ]

    prompt = render_solo_final_prompt(D11_PACKET_DIR)
    assert_common_generation_contract(prompt)
    assert "TURN ROLE: final_synthesis_900_1300_words" in prompt
    assert "HoloGov-B" not in prompt
    assert "CANONICAL STATE_OBJECT" not in prompt
    assert "ARTIFACTS_REGISTRY" not in prompt
    assert "PROOF_CREDIT_ELIGIBILITY_STATE" not in prompt


def test_d9_collapsed_turn4_options_fails_pre_registry_gate() -> None:
    text, raw = raw_text("D9", 4)
    compliance = runner.role_compliance("options_operational_usefulness_reviewer", text, final=False, output_meta=raw)
    gate = runner.intermediate_registry_gate(
        artifact_id="TURN_004_OPTIONS_OPERATIONAL_USEFULNESS_REVIEWER",
        role="options_operational_usefulness_reviewer",
        role_compliance_result=compliance,
        state_audit_result={"status": "pass", "packet_hash_preserved": True, "invented_source_ids": []},
        repair_attempts=[],
    )
    assert compliance["status"] == "fail"
    assert gate["status"] == "rejected"


def test_d10_collapsed_turn4_options_fails_pre_registry_gate() -> None:
    text, raw = raw_text("D10", 4)
    compliance = runner.role_compliance("options_operational_usefulness_reviewer", text, final=False, output_meta=raw)
    gate = runner.intermediate_registry_gate(
        artifact_id="TURN_004_OPTIONS_OPERATIONAL_USEFULNESS_REVIEWER",
        role="options_operational_usefulness_reviewer",
        role_compliance_result=compliance,
        state_audit_result={"status": "pass", "packet_hash_preserved": True, "invented_source_ids": []},
        repair_attempts=[],
    )
    assert compliance["status"] == "fail"
    assert gate["status"] == "rejected"


def test_d10_turn2_missing_revision_pressure_fails_or_requires_repair() -> None:
    text, raw = raw_text("D10", 2)
    compliance = runner.role_compliance("assumption_and_evidence_attacker", text, final=False, output_meta=raw)
    gate = runner.intermediate_registry_gate(
        artifact_id="TURN_002_ASSUMPTION_AND_EVIDENCE_ATTACKER",
        role="assumption_and_evidence_attacker",
        role_compliance_result=compliance,
        state_audit_result={"status": "pass", "packet_hash_preserved": True, "invented_source_ids": []},
        repair_attempts=[],
    )
    assert compliance["status"] == "fail"
    assert "revision_pressure" in compliance["missing_role_behaviors"]
    assert gate["status"] == "rejected"


def test_d7_collapsed_truncated_turn4_options_fails_v4_2_gate() -> None:
    text, raw = raw_text("D7", 4)
    compliance = runner.role_compliance("options_operational_usefulness_reviewer", text, final=False, output_meta=raw)
    completeness = compliance["intermediate_artifact_completeness"]
    assert compliance["status"] == "fail"
    assert completeness["word_count"] < runner.intermediate_role_min_words()["options_operational_usefulness_reviewer"]
    assert completeness["status"] == "fail"


def test_d6_positive_control_complete_non_options_turns_still_pass() -> None:
    for turn, role in [
        (2, "assumption_and_evidence_attacker"),
        (5, "claim_discipline_overclaim_reducer"),
    ]:
        text, raw = raw_text("D6", turn)
        compliance = runner.role_compliance(role, text, final=False, output_meta=raw)
        assert compliance["status"] == "pass"
        assert compliance["intermediate_artifact_completeness"]["status"] == "pass"


def test_keyword_stuffed_operational_options_output_fails_as_empty_analysis() -> None:
    stuffed = "option risk waiting sequence trigger rollback monitoring logging executive next action reversible irreversible observable " * 60
    compliance = runner.role_compliance("options_operational_usefulness_reviewer", stuffed.strip() + ".", final=False, output_meta={})
    failures = compliance["intermediate_artifact_completeness"]["failures"]
    assert compliance["status"] == "fail"
    assert "options_operational_analysis_too_thin_or_keyword_only" in failures


def test_substantive_operational_options_output_passes() -> None:
    paragraph = (
        "Available options are to block execution, approve a narrow pilot, hold for missing evidence, or escalate to the executive owner. "
        "The risk of acting is that a broad approval expands blast radius before the packet proves control readiness. "
        "The risk of waiting is delay cost, manual workaround fatigue, and a missed deadline if the dependency chain is already satisfied. "
        "Before execution, the prerequisite must be true: owners confirm source-backed authority, logging is live, and the first stage has a canary threshold. "
        "The stop signal is any failed audit trail, missing approval, threshold breach, or new source contradiction; the go signal permits expansion only after monitored canary results stay inside the limit. "
        "Rollback gates must define what is reversible, such as approval revocation and configuration revert, and what cannot be reversed, such as external counterparty reliance after release. "
        "Monitoring gates require observable logs, alerts, metrics, and a named owner before rollback can be trusted. "
        "Executive next actions are to assign the accountable owner, choose the narrow path, publish the go/no-go trigger table, and schedule escalation if any condition fails. "
    )
    compliance = runner.role_compliance("options_operational_usefulness_reviewer", paragraph * 3, final=False, output_meta={})
    assert compliance["status"] == "pass"


def test_synthetic_repaired_options_turn_with_all_required_headings_passes() -> None:
    compliance = runner.role_compliance(
        "options_operational_usefulness_reviewer",
        synthetic_options_repair_text(),
        final=False,
        output_meta={},
    )
    assert compliance["status"] == "pass"
    assert compliance["intermediate_artifact_completeness"]["role_specific_presence"]["status"] == "pass"


def test_synthetic_assumption_repair_with_revision_pressure_passes() -> None:
    text = synthetic_assumption_repair_text()
    compliance = runner.role_compliance("assumption_and_evidence_attacker", text, final=False, output_meta={})
    audit = runner.state_audit(
        text,
        {"CRITICAL_CONSTRAINTS": ["test"], "PACKET_HASH": "packet_hash"},
        {"S1_TEST_SOURCE", "S2_TEST_SOURCE"},
        "packet_hash",
        {"artifacts": {"TASK_BRIEF": {"status": "PINNED"}}},
    )
    assert compliance["status"] == "pass"
    assert audit["status"] == "pass"


def test_synthetic_assumption_repair_missing_revision_pressure_fails() -> None:
    compliance = runner.role_compliance(
        "assumption_and_evidence_attacker",
        synthetic_assumption_repair_text(include_revision_pressure=False),
        final=False,
        output_meta={},
    )
    assert compliance["status"] == "fail"
    assert "revision_pressure" in compliance["missing_role_behaviors"]


def test_synthetic_assumption_repair_invented_source_id_fails_state_audit() -> None:
    text = synthetic_assumption_repair_text() + " The final should avoid relying on invented source S9_FAKE_APPROVAL."
    audit = runner.state_audit(
        text,
        {"CRITICAL_CONSTRAINTS": ["test"], "PACKET_HASH": "packet_hash"},
        {"S1_TEST_SOURCE", "S2_TEST_SOURCE"},
        "packet_hash",
        {"artifacts": {"TASK_BRIEF": {"status": "PINNED"}}},
    )
    assert audit["status"] == "fail"
    assert audit["invented_source_ids"] == ["S9_FAKE_APPROVAL"]


def test_synthetic_repaired_options_turn_missing_risk_of_acting_fails() -> None:
    compliance = runner.role_compliance(
        "options_operational_usefulness_reviewer",
        synthetic_options_repair_text(omit_heading="Risk of acting"),
        final=False,
        output_meta={},
    )
    failures = compliance["intermediate_artifact_completeness"]["failures"]
    assert compliance["status"] == "fail"
    assert "missing_options_role_component:risk_of_acting" in failures


def test_synthetic_repaired_options_turn_missing_true_before_execution_fails() -> None:
    compliance = runner.role_compliance(
        "options_operational_usefulness_reviewer",
        synthetic_options_repair_text(omit_heading="Must be true before execution"),
        final=False,
        output_meta={},
    )
    failures = compliance["intermediate_artifact_completeness"]["failures"]
    assert compliance["status"] == "fail"
    assert "missing_options_role_component:true_before_execution" in failures


def test_synthetic_repaired_options_turn_missing_signal_permits_expansion_fails() -> None:
    compliance = runner.role_compliance(
        "options_operational_usefulness_reviewer",
        synthetic_options_repair_text(omit_heading="Signal that permits expansion"),
        final=False,
        output_meta={},
    )
    failures = compliance["intermediate_artifact_completeness"]["failures"]
    assert compliance["status"] == "fail"
    assert "missing_options_role_component:signal_permits_expansion" in failures


def test_synthetic_repaired_options_turn_missing_irreversible_action_fails() -> None:
    compliance = runner.role_compliance(
        "options_operational_usefulness_reviewer",
        synthetic_options_repair_text(omit_heading="What cannot be reversed"),
        final=False,
        output_meta={},
    )
    failures = compliance["intermediate_artifact_completeness"]["failures"]
    assert compliance["status"] == "fail"
    assert "missing_options_role_component:irreversible_action" in failures


def test_keyword_stuffed_options_repair_with_headings_still_fails() -> None:
    compliance = runner.role_compliance(
        "options_operational_usefulness_reviewer",
        keyword_stuffed_options_repair_text(),
        final=False,
        output_meta={},
    )
    failures = compliance["intermediate_artifact_completeness"]["failures"]
    assert compliance["status"] == "fail"
    assert "options_operational_analysis_too_thin_or_keyword_only" in failures


def test_stop_go_trigger_aliases_pass_when_substantive() -> None:
    text = synthetic_options_repair_text().replace(
        "Stop/go triggers are the explicit halt trigger, go trigger, proceed-only-if gate, and block-execution-if condition that leadership must use.",
        "Proceed only if the canary stays inside threshold, expand only after owner review, authorized only if audit logs are live, block execution if delete calls appear, and do not proceed unless rollback ownership is named.",
    )
    compliance = runner.role_compliance("options_operational_usefulness_reviewer", text, final=False, output_meta={})
    assert compliance["status"] == "pass"
    assert compliance["intermediate_artifact_completeness"]["role_specific_presence"]["component_presence"]["stop_go_triggers"] is True


def test_synthetic_concise_t3_source_fidelity_audit_passes() -> None:
    text = synthetic_t3_concise_audit_text()
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        text,
        final=False,
        output_meta={},
    )
    presence = compliance["intermediate_artifact_completeness"]["role_specific_presence"]
    assert runner.T3_CONCISE_AUDIT_MIN_WORDS <= runner.word_count(text) <= runner.T3_CONCISE_AUDIT_MAX_WORDS
    assert compliance["status"] == "pass"
    assert presence["status"] == "pass"
    assert all(presence["section_presence"].values())


def test_synthetic_t3_under_target_but_substantive_audit_passes() -> None:
    text = synthetic_t3_under_target_but_substantive_text()
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        text,
        final=False,
        output_meta={},
    )
    completeness = compliance["intermediate_artifact_completeness"]
    presence = completeness["role_specific_presence"]
    assert runner.word_count(text) < runner.T3_CONCISE_AUDIT_MIN_WORDS
    assert runner.word_count(text) >= completeness["min_words_required"]
    assert compliance["status"] == "pass"
    assert presence["status"] == "pass"
    assert presence["under_target_words_nonblocking"] is True
    assert "t3_compact_audit_under_target_words" not in completeness["failures"]


def test_synthetic_t3_essay_over_target_token_ceiling_style_fails() -> None:
    text = synthetic_t3_concise_audit_text(extra_words=260)
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        text,
        final=False,
        output_meta={"output_tokens": 3800, "max_tokens_requested": 3800},
    )
    failures = compliance["intermediate_artifact_completeness"]["failures"]
    assert compliance["status"] == "fail"
    assert "t3_compact_audit_over_target_words" in failures


def test_synthetic_t3_missing_required_section_fails() -> None:
    text = synthetic_t3_concise_audit_text(omit_section="Exact source-ID audit")
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        text,
        final=False,
        output_meta={},
    )
    failures = compliance["intermediate_artifact_completeness"]["failures"]
    assert compliance["status"] == "fail"
    assert "missing_t3_compact_section:Exact source-ID audit" in failures


def test_synthetic_t3_section_cap_violation_fails() -> None:
    text = synthetic_t3_concise_audit_text().replace(
        "Risk one: do not let S1_TEST_SOURCE become approval for facts that S1_TEST_SOURCE does not contain, because source boundaries decide whether the final can act.",
        "Risk one: do not let S1_TEST_SOURCE become approval for facts that S1_TEST_SOURCE does not contain, because source boundaries decide whether the final can act. "
        + " ".join(["overexpanded"] * 45),
    )
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        text,
        final=False,
        output_meta={},
    )
    failures = compliance["intermediate_artifact_completeness"]["failures"]
    assert compliance["status"] == "fail"
    assert "t3_compact_section_over_word_cap:Top 5 source-boundary risks" in failures
    assert "t3_compact_bullet_over_word_cap:Top 5 source-boundary risks" in failures


def test_d14_t3_original_mixed_failure_rejects_meta_section_and_uses_full_repair() -> None:
    raw = d14_t3_failure_raw_output("turn_003.json")
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        raw["text"],
        final=False,
        output_meta=raw,
    )
    completeness = compliance["intermediate_artifact_completeness"]
    failures = completeness["failures"]
    prompt = render_d14_t3_compression_repair_prompt_for_test()
    assert compliance["status"] == "fail"
    assert completeness["word_count"] == 980
    assert completeness["clean_ending"] is False
    assert completeness["hit_requested_token_ceiling"] is True
    assert "missing_t3_compact_section:Action-boundary cautions" in failures
    assert "t3_compact_audit_forbidden_meta_section:Final synthesis instructions" in failures
    assert "t3_compact_audit_over_target_words" in failures
    assert "unclean_or_mid_sentence_intermediate_ending" in failures
    assert "provider_output_hit_max_tokens_with_unclean_intermediate_ending" in failures
    assert "t3_compact_section_over_word_cap:Top 5 source-boundary risks" in failures
    assert "t3_compact_bullet_over_word_cap:Top 5 source-boundary risks" in failures
    assert runner.t3_overword_repair_required(compliance) is False
    assert (
        runner.intermediate_repair_max_tokens_for_failure(
            "contradiction_uncertainty_source_fidelity_reviewer",
            compliance,
        )
        == runner.INTERMEDIATE_REPAIR_MAX_TOKENS
    )
    assert "T3 COMPACT SOURCE-FIDELITY REPAIR REQUIRED FORMAT" in prompt
    assert "Action-boundary cautions" in prompt
    assert "5. Final synthesis instructions" not in prompt
    assert "incomplete/truncated" not in prompt


def test_d14_retry2_t3_output_rejects_meta_section_without_hard_under_target_failure() -> None:
    raw = d14_retry2_raw_output("turn_003.json")
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        raw["text"],
        final=False,
        output_meta=raw,
    )
    completeness = compliance["intermediate_artifact_completeness"]
    presence = completeness["role_specific_presence"]
    failures = completeness["failures"]
    assert compliance["status"] == "fail"
    assert completeness["word_count"] == 654
    assert completeness["clean_ending"] is True
    assert completeness["hit_requested_token_ceiling"] is False
    assert "missing_t3_compact_section:Action-boundary cautions" in failures
    assert "t3_compact_audit_forbidden_meta_section:Final synthesis instructions" in failures
    assert "t3_compact_audit_under_target_words" not in failures
    assert presence["forbidden_meta_sections"] == ["Final synthesis instructions"]
    assert presence["prose_paragraph_line_count"] == 1


def test_d14_retry2_t3_repair_output_rejects_meta_section_without_hard_under_target_failure() -> None:
    raw = d14_retry2_raw_output("turn_003_intermediate_repair_001.json")
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        raw["text"],
        final=False,
        output_meta=raw,
    )
    completeness = compliance["intermediate_artifact_completeness"]
    presence = completeness["role_specific_presence"]
    failures = completeness["failures"]
    assert compliance["status"] == "fail"
    assert completeness["word_count"] == 574
    assert completeness["clean_ending"] is True
    assert completeness["hit_requested_token_ceiling"] is False
    assert "missing_t3_compact_section:Action-boundary cautions" in failures
    assert "t3_compact_audit_forbidden_meta_section:Final synthesis instructions" in failures
    assert "t3_compact_audit_under_target_words" not in failures
    assert presence["forbidden_meta_sections"] == ["Final synthesis instructions"]
    assert presence["prose_paragraph_line_count"] == 1


def test_d14_t3_repair_output_remains_rejected_and_final_synthesis_does_not_consume_it() -> None:
    raw = d14_t3_failure_raw_output("turn_003_intermediate_repair_001.json")
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        raw["text"],
        final=False,
        output_meta=raw,
    )
    arch_evidence = d14_t3_failure_arch_evidence()
    failures = compliance["intermediate_artifact_completeness"]["failures"]
    turn3 = next(entry for entry in arch_evidence["turns"] if entry["turn"] == 3)
    registry_entry = turn3["registry_acceptance"]
    validation = arch_evidence["architecture_evidence_validation"]
    assert compliance["status"] == "fail"
    assert raw["output_tokens"] == 3600
    assert raw["max_tokens_requested"] == 3600
    assert raw["text"].rstrip().endswith("release boundary until bank-")
    assert "unclean_or_mid_sentence_intermediate_ending" in failures
    assert "provider_output_hit_max_tokens_with_unclean_intermediate_ending" in failures
    assert turn3["intermediate_repair_attempts"][0]["accepted"] is False
    assert registry_entry["status"] == "rejected"
    assert validation["failed_required_turns_consumed_by_final"] == []
    assert validation["no_failed_required_turn_consumed_by_final"] is True
    assert validation["final_synthesis_blocked"] is True


def test_d12_historical_t3_original_still_fails_compact_audit_gate() -> None:
    raw = d12_t3_failure_raw_output("turn_003.json")
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        raw["text"],
        final=False,
        output_meta=raw,
    )
    failures = compliance["intermediate_artifact_completeness"]["failures"]
    assert compliance["status"] == "fail"
    assert raw["output_tokens"] == 3800
    assert raw["max_tokens_requested"] == 3800
    assert raw["text"].rstrip().endswith("10. Hold the final body to")
    assert "unclean_or_mid_sentence_intermediate_ending" in failures
    assert "provider_output_hit_max_tokens_with_unclean_intermediate_ending" in failures
    assert "t3_compact_audit_over_target_words" in failures


def test_d12_historical_t3_repair_still_fails_compact_audit_gate() -> None:
    raw = d12_t3_failure_raw_output("turn_003_intermediate_repair_001.json")
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        raw["text"],
        final=False,
        output_meta=raw,
    )
    failures = compliance["intermediate_artifact_completeness"]["failures"]
    assert compliance["status"] == "fail"
    assert raw["output_tokens"] == 3600
    assert raw["max_tokens_requested"] == 3600
    assert raw["text"].rstrip().endswith("ensure every factual claim carries an")
    assert "unclean_or_mid_sentence_intermediate_ending" in failures
    assert "provider_output_hit_max_tokens_with_unclean_intermediate_ending" in failures
    assert "t3_compact_audit_over_target_words" in failures


def test_d12_retry3_t3_original_now_fails_overword_and_legacy_meta_section_gate() -> None:
    raw = d12_retry3_raw_output("turn_003.json")
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        raw["text"],
        final=False,
        output_meta=raw,
    )
    completeness = compliance["intermediate_artifact_completeness"]
    failures = completeness["failures"]
    assert compliance["status"] == "fail"
    assert completeness["word_count"] == 913
    assert completeness["clean_ending"] is True
    assert completeness["hit_requested_token_ceiling"] is False
    assert "t3_compact_audit_over_target_words" in failures
    assert "t3_compact_section_over_word_cap:Top 5 source-boundary risks" in failures
    assert "t3_compact_bullet_over_word_cap:Top 5 source-boundary risks" in failures
    assert "missing_t3_compact_section:Action-boundary cautions" in failures
    assert "t3_compact_audit_forbidden_meta_section:Final synthesis instructions" in failures
    assert completeness["role_specific_presence"]["missing_sections"] == ["Action-boundary cautions"]


def test_d12_retry3_t3_repair_still_fails_overword_and_truncation_gate() -> None:
    raw = d12_retry3_raw_output("turn_003_intermediate_repair_001.json")
    compliance = runner.role_compliance(
        "contradiction_uncertainty_source_fidelity_reviewer",
        raw["text"],
        final=False,
        output_meta=raw,
    )
    failures = compliance["intermediate_artifact_completeness"]["failures"]
    assert compliance["status"] == "fail"
    assert raw["output_tokens"] == 3600
    assert raw["max_tokens_requested"] == 3600
    assert raw["text"].rstrip().endswith("valuation acceptance, li")
    assert "unclean_or_mid_sentence_intermediate_ending" in failures
    assert "provider_output_hit_max_tokens_with_unclean_intermediate_ending" in failures
    assert "t3_compact_audit_over_target_words" in failures


def test_initial_decision_repaired_draft_complete_ending_passes_clean_ending_check() -> None:
    completeness = runner.intermediate_artifact_completeness(
        "initial_decision_brief_drafter",
        synthetic_initial_decision_text(),
    )
    assert completeness["status"] == "pass"
    assert completeness["clean_ending"] is True


def test_initial_decision_repaired_draft_truncated_29_vs_fails_clean_ending_check() -> None:
    completeness = runner.intermediate_artifact_completeness(
        "initial_decision_brief_drafter",
        synthetic_initial_decision_text(truncated=True),
    )
    assert completeness["status"] == "fail"
    assert completeness["clean_ending"] is False
    assert "unclean_or_mid_sentence_intermediate_ending" in completeness["failures"]


def test_invented_source_id_fails_state_audit_and_blocks_registry_acceptance() -> None:
    compliance = {"status": "pass", "intermediate_artifact_completeness": {"status": "pass"}}
    audit = {"status": "fail", "packet_hash_preserved": True, "invented_source_ids": ["S7_UETA"]}
    gate = runner.intermediate_registry_gate(
        artifact_id="TURN_003_CONTRADICTION_UNCERTAINTY_SOURCE_FIDELITY_REVIEWER",
        role="contradiction_uncertainty_source_fidelity_reviewer",
        role_compliance_result=compliance,
        state_audit_result=audit,
        repair_attempts=[],
    )
    assert gate["status"] == "rejected"
    assert "invented_source_ids" in gate["failures"]


def test_final_synthesis_retrieval_uses_only_accepted_registry_entries() -> None:
    registry = {
        "artifacts": {
            "TASK_BRIEF": {"content": "task"},
            "SOURCE_PACKET_MD": {"content": "source"},
            "TURN_001_INITIAL_DECISION_BRIEF_DRAFTER": {"status": "INTERMEDIATE_ACCEPTED", "content": "accepted"},
            "TURN_004_OPTIONS_OPERATIONAL_USEFULNESS_REVIEWER": {"status": "REJECTED", "content": "rejected"},
        }
    }
    ids = runner.retrieved_ids_for_holo_turn(registry, "full_registry")
    assert "TURN_001_INITIAL_DECISION_BRIEF_DRAFTER" in ids
    assert "TURN_004_OPTIONS_OPERATIONAL_USEFULNESS_REVIEWER" not in ids


def assert_rejected_options_turn_does_not_leak(domain: str) -> None:
    rejected_text, rejected_artifact_id, state, final_prompt_surface = state_after_rejected_options_turn(domain)
    state_json = runner.stable_json(state)
    assert "ROLLING_SUMMARY" not in state_json
    assert "rolling_summary" not in state_json
    assert rejected_text not in state_json
    assert rejected_text not in final_prompt_surface
    assert rejected_artifact_id in state["REJECTED_ARTIFACT_IDS"]
    assert rejected_artifact_id not in state["FINAL_SYNTHESIS_ALLOWED_INPUT_IDS"]
    assert state["FINAL_SYNTHESIS_ALLOWED_INPUT_IDS"] == [
        "TASK_BRIEF",
        "SOURCE_PACKET_MD",
        "TURN_001_INITIAL_DECISION_BRIEF_DRAFTER",
    ]
    assert "options_operational_usefulness_reviewer" in state["UNRESOLVED_REQUIRED_ROLES"]
    assert state["PROOF_CREDIT_ELIGIBILITY_STATE"]["eligible"] is False
    assert "unresolved_required_roles" in state["PROOF_CREDIT_ELIGIBILITY_STATE"]["reasons"]
    assert "TURN_001_INITIAL_DECISION_BRIEF_DRAFTER" in state["ACCEPTED_ARTIFACT_REGISTRY"]
    assert "accepted prior artifact content" in final_prompt_surface
    assert "content" not in state["ACCEPTED_ARTIFACT_REGISTRY"]["TURN_001_INITIAL_DECISION_BRIEF_DRAFTER"]


def test_d10_rejected_turn4_content_does_not_enter_state_or_final_prompt() -> None:
    assert_rejected_options_turn_does_not_leak("D10")


def test_d9_rejected_turn4_content_does_not_enter_state_or_final_prompt() -> None:
    assert_rejected_options_turn_does_not_leak("D9")


def test_rejected_turn4_raw_outputs_remain_preserved_on_disk() -> None:
    for domain in ("D9", "D10"):
        path = raw_output_path(domain, 4)
        assert path.exists()
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert raw["text"]


def test_d12_rejected_t3_remains_blocked_from_registry_and_final_synthesis() -> None:
    evidence = d12_t3_failure_arch_evidence()
    validation = evidence["architecture_evidence_validation"]
    t3_turn = next(item for item in evidence["turns"] if item["role"] == "contradiction_uncertainty_source_fidelity_reviewer")
    final_turn = next(item for item in evidence["turns"] if item["role"] == "final_synthesis_author")
    assert t3_turn["registry_acceptance"]["status"] == "rejected"
    assert t3_turn["registry_acceptance"]["repair_succeeded"] is False
    assert validation["required_roles_all_completed"] is False
    assert validation["proof_credit_eligible"] is False
    assert validation["failed_required_turns_consumed_by_final"] == []
    assert "TURN_003_CONTRADICTION_UNCERTAINTY_SOURCE_FIDELITY_REVIEWER" not in final_turn["retrieved_artifact_ids"]


def test_d10_post_v4_2_fixture_replay_preserves_gate_strictness_and_final_isolation() -> None:
    evidence = d10_post_v4_2_arch_evidence()
    turns = {item["turn"]: item for item in evidence["turns"]}

    turn1_raw = d10_post_v4_2_raw_output("turn_001.json")
    turn1_compliance = runner.role_compliance("initial_decision_brief_drafter", turn1_raw["text"], final=False, output_meta=turn1_raw)
    assert turn1_compliance["status"] == "fail"
    assert turn1_compliance["missing_role_behaviors"] == []
    assert turn1_compliance["intermediate_artifact_completeness"]["failures"] == ["unclean_or_mid_sentence_intermediate_ending"]
    assert turns[1]["registry_acceptance"]["status"] == "rejected"

    turn4_raw = d10_post_v4_2_raw_output("turn_004.json")
    turn4_compliance = runner.role_compliance("options_operational_usefulness_reviewer", turn4_raw["text"], final=False, output_meta=turn4_raw)
    assert turn4_compliance["status"] == "fail"
    turn4_failures = turn4_compliance["intermediate_artifact_completeness"]["failures"]
    assert "intermediate_artifact_too_short" in turn4_failures
    assert "unclean_or_mid_sentence_intermediate_ending" in turn4_failures
    assert "missing_options_role_component:available_options" in turn4_failures
    assert turns[4]["registry_acceptance"]["status"] == "rejected"

    turn4_repair_raw = d10_post_v4_2_raw_output("turn_004_intermediate_repair_001.json")
    turn4_repair_compliance = runner.role_compliance(
        "options_operational_usefulness_reviewer",
        turn4_repair_raw["text"],
        final=False,
        output_meta=turn4_repair_raw,
    )
    repair_failures = turn4_repair_compliance["intermediate_artifact_completeness"]["failures"]
    assert turn4_repair_compliance["status"] == "fail"
    assert "missing_options_role_component:risk_of_acting" in repair_failures
    assert "missing_options_role_component:true_before_execution" in repair_failures
    assert "missing_options_role_component:signal_permits_expansion" in repair_failures
    assert turns[4]["intermediate_repair_attempts"][0]["accepted"] is False

    synthetic_valid = runner.role_compliance(
        "options_operational_usefulness_reviewer",
        synthetic_options_repair_text(),
        final=False,
        output_meta={},
    )
    assert synthetic_valid["status"] == "pass"

    final_prompt, final_state = d10_post_v4_2_final_prompt_state()
    state_json = runner.stable_json(final_state)
    rejected_ids = {
        "TURN_001_INITIAL_DECISION_BRIEF_DRAFTER",
        "TURN_004_OPTIONS_OPERATIONAL_USEFULNESS_REVIEWER",
    }
    accepted_only_ids = [
        "TASK_BRIEF",
        "SOURCE_PACKET_MD",
        "TURN_002_ASSUMPTION_AND_EVIDENCE_ATTACKER",
        "TURN_003_CONTRADICTION_UNCERTAINTY_SOURCE_FIDELITY_REVIEWER",
        "TURN_005_CLAIM_DISCIPLINE_OVERCLAIM_REDUCER",
    ]
    assert final_state["FINAL_SYNTHESIS_ALLOWED_INPUT_IDS"] == accepted_only_ids
    assert rejected_ids <= set(final_state["REJECTED_ARTIFACT_IDS"])
    assert not rejected_ids.intersection(final_state["FINAL_SYNTHESIS_ALLOWED_INPUT_IDS"])
    assert set(final_state["ACCEPTED_ARTIFACT_REGISTRY"]) == set(accepted_only_ids)

    rejected_bodies = [
        turn1_raw["text"],
        d10_post_v4_2_raw_output("turn_001_intermediate_repair_001.json")["text"],
        turn4_raw["text"],
        turn4_repair_raw["text"],
    ]
    for body in rejected_bodies:
        assert body not in state_json
        assert body not in final_prompt

    final_artifact = (D10_POST_V4_2_CONDITION_DIR / "artifact.md").read_text(encoding="utf-8")
    final_compliance = runner.role_compliance("final_synthesis_author", final_artifact, final=True, output_meta={})
    assert final_compliance["status"] == "pass"


def test_holobuild_runner_has_no_rolling_summary_prompt_surface() -> None:
    runner_text = RUNNER_PATH.read_text(encoding="utf-8")
    assert "ROLLING_SUMMARY" not in runner_text
    assert "rolling_summary" not in runner_text
    assert "excerpt(output_text" not in runner_text


def test_proof_credit_false_if_failed_required_turn_was_consumed_by_final() -> None:
    evidence_turns = [
        {
            "turn": 4,
            "role": "options_operational_usefulness_reviewer",
            "artifact_id": "TURN_004_OPTIONS_OPERATIONAL_USEFULNESS_REVIEWER",
            "prompt_card_hash": "abc",
            "role_compliance": {"status": "fail", "intermediate_artifact_completeness": {"status": "fail"}},
            "state_audit": {"status": "pass"},
            "registry_acceptance": {"status": "rejected"},
        },
        {
            "turn": 6,
            "role": "final_synthesis_author",
            "prompt_card_hash": "def",
            "retrieved_artifact_ids": ["TASK_BRIEF", "TURN_004_OPTIONS_OPERATIONAL_USEFULNESS_REVIEWER"],
            "role_compliance": {"status": "pass", "final_word_band_status": "pass", "final_artifact_completeness": {"status": "pass"}},
            "state_audit": {"status": "pass"},
            "registry_acceptance": {"status": "accepted"},
        },
    ]
    summary = runner.architecture_evidence_summary(evidence_turns, {"deterministic_gate_status": "pass"}, runner.PROOF_ELIGIBLE_HOLO_MODE)
    assert summary["proof_credit_eligible"] is False
    assert summary["no_failed_required_turn_consumed_by_final"] is False


def test_final_word_count_edge_cases_use_policy_hard_max() -> None:
    assert runner.final_word_band_compliance(" ".join(["word"] * 899))["status"] == "fail_under_minimum"
    assert runner.final_word_band_compliance(" ".join(["word"] * 900))["status"] == "pass"
    assert runner.final_word_band_compliance(" ".join(["word"] * 1300))["status"] == "pass"
    assert runner.final_word_band_compliance(" ".join(["word"] * 1301))["status"] == "fail_over_hard_max"


def test_failed_final_repair_above_1300_remains_failed() -> None:
    overlength = " ".join(["word"] * 1463)
    assert runner.final_word_band_compliance(overlength)["status"] == "fail_over_hard_max"
    evidence_turns = [
        {
            "turn": 6,
            "role": "final_synthesis_author",
            "prompt_card_hash": "abc",
            "retrieved_artifact_ids": ["TASK_BRIEF"],
            "role_compliance": {
                "status": "fail",
                "final_word_band_status": "fail_over_hard_max",
                "final_word_count": 1463,
                "final_artifact_completeness": {"status": "pass"},
            },
            "state_audit": {"status": "pass"},
            "registry_acceptance": {"status": "accepted"},
            "final_repair_required": True,
            "final_repair_succeeded": False,
            "final_repair_attempts": [{"repaired_word_count": 1463, "accepted": False}],
        }
    ]
    summary = runner.architecture_evidence_summary(evidence_turns, {"deterministic_gate_status": "pass"}, runner.PROOF_ELIGIBLE_HOLO_MODE)
    assert summary["final_word_band_pass"] is False
    assert summary["final_repair_succeeded_if_used"] is False
    assert summary["proof_credit_eligible"] is False


def test_counterargument_claim_boundaries_heading_requires_substantive_boundary_text() -> None:
    sections = [
        "# Bottom line\nRecommend a conditional go path using S1_TEST_SOURCE and S2_TEST_SOURCE because the packet supports a bounded option, not an unrestricted action.",
        "# Risks of acting\nThe risk of acting is execution error, preventable exposure, and reliance on a source boundary the packet does not prove.",
        "# Risks of waiting\nThe risk of waiting is delay cost, operational drift, and missed escalation timing if leadership does not assign an owner.",
        "# Next steps / stop-go gates\nUse a go trigger, no-go trigger, rollback trigger, monitoring gate, and executive escalation owner before expansion.",
        "# Claim boundaries\nThe strongest counterargument is speed, but this brief does not prove broad approval, legal clearance, irreversible release authority, or operational approval beyond S1_TEST_SOURCE and S2_TEST_SOURCE.",
    ]
    text = "\n\n".join(sections)
    while runner.word_count(text) < 940:
        text += " The recommendation remains conditional, source bounded, monitored, reversible where possible, and explicit about what the packet does not prove."
    compliance = runner.role_compliance("final_synthesis_author", text, final=True, output_meta={})
    assert compliance["status"] == "pass"
    assert compliance["final_artifact_completeness"]["section_presence"]["claim_boundaries"] is True


def test_counterargument_claim_boundaries_heading_without_boundary_text_fails() -> None:
    sections = [
        "# Bottom line\nRecommend a conditional go path using S1_TEST_SOURCE and S2_TEST_SOURCE because the packet supports a bounded option, not an unrestricted action.",
        "# Risks of acting\nThe risk of acting is execution error, preventable exposure, and reliance on a source boundary the packet does not prove.",
        "# Risks of waiting\nThe risk of waiting is delay cost, operational drift, and missed escalation timing if leadership does not assign an owner.",
        "# Next steps / stop-go gates\nUse a go trigger, no-go trigger, rollback trigger, monitoring gate, and executive escalation owner before expansion.",
        "# Claim boundaries\nThe strongest counterargument is speed. Leaders want momentum, confidence, crisp ownership, fast execution, immediate delivery, and strong implementation.",
    ]
    text = "\n\n".join(sections)
    while runner.word_count(text) < 940:
        text += " Execution momentum remains the repeated counterargument for leadership because teams want progress, delivery, confidence, accountability, and speed."
    compliance = runner.role_compliance("final_synthesis_author", text, final=True, output_meta={})
    failures = compliance["final_artifact_completeness"]["failures"]
    assert compliance["status"] == "fail"
    assert "claim_boundary_section_lacks_substantive_boundary_text" in failures


def test_final_repair_prompt_requires_add_missing_section_and_compress_under_hard_max() -> None:
    runner_text = RUNNER_PATH.read_text(encoding="utf-8")
    assert "Preserve or add the missing section identified by the audit, then compress elsewhere" in runner_text
    assert "do not return an overlength repair" in runner_text
    assert "Target approximately" in runner_text
    assert "remove or compress lower-priority wording" in runner_text


def test_historical_d12_retry2_original_final_failure_fixture_remains_detected() -> None:
    metadata = d12_retry2_metadata()
    repair_attempt = metadata["final_repair_attempts"][0]
    previous_completeness = repair_attempt["previous_final_completeness"]
    assert repair_attempt["previous_word_count"] == 1294
    assert repair_attempt["previous_final_word_band_compliance"]["status"] == "pass"
    assert previous_completeness["status"] == "fail"
    assert previous_completeness["failures"] == ["claim_boundary_section_lacks_substantive_boundary_text"]


def test_historical_d12_retry2_final_repair_failure_still_fails() -> None:
    repair = d12_retry2_raw_output("turn_006_final_repair_001.json")
    completeness = runner.final_artifact_completeness(repair["text"], repair)
    assert repair["output_tokens"] == 5200
    assert repair["max_tokens_requested"] == 5200
    assert completeness["status"] == "fail"
    assert "unclean_or_mid_sentence_ending" in completeness["failures"]
    assert "provider_output_hit_max_tokens_with_unclean_ending" in completeness["failures"]


def test_historical_d12_retry3_final_original_is_complete_but_three_words_over() -> None:
    raw = d12_retry3_raw_output("turn_006.json")
    completeness = runner.final_artifact_completeness(raw["text"], raw)
    word_band = runner.final_word_band_compliance(raw["text"])
    assert completeness["status"] == "pass"
    assert completeness["section_presence"] == {
        "bottom_line": True,
        "risks_of_acting": True,
        "risks_of_waiting": True,
        "next_steps": True,
        "claim_boundaries": True,
    }
    assert word_band["status"] == "fail_over_hard_max"
    assert word_band["word_count"] == 1303
    assert word_band["over_max_words"] == 3


def test_historical_d12_retry3_final_repair_fixture_detects_heading_loss() -> None:
    repair = d12_retry3_raw_output("turn_006_final_repair_001.json")
    completeness = runner.final_artifact_completeness(repair["text"], repair)
    word_band = runner.final_word_band_compliance(repair["text"])
    assert word_band["status"] == "pass"
    assert word_band["word_count"] == 1133
    assert completeness["status"] == "fail"
    assert completeness["missing_sections"] == [
        "bottom_line",
        "risks_of_acting",
        "risks_of_waiting",
        "next_steps",
        "claim_boundaries",
    ]
    assert "missing_final_section:bottom_line" in completeness["failures"]
    assert "missing_final_section:claim_boundaries" in completeness["failures"]


def test_historical_d12_retry3_metadata_remains_not_proof_clean() -> None:
    metadata = d12_retry3_metadata()
    manifest = d12_retry3_run_manifest()
    validation = metadata["architecture_evidence_validation"]
    assert metadata["provider_calls"] == 9
    assert metadata["scores_generated"] == 0
    assert manifest["judging_runs"] == 0
    assert manifest["scores_generated"] == 0
    assert manifest["unblinding_runs"] == 0
    assert validation["proof_credit_eligible"] is False
    assert validation["required_roles_all_completed"] is False
    assert validation["final_artifact_completeness_pass"] is True
    assert validation["final_word_band_pass"] is False
    assert validation["no_failed_required_turn_consumed_by_final"] is True


def test_synthetic_final_with_required_five_headings_passes() -> None:
    text = final_text_with_sections()
    compliance = runner.role_compliance("final_synthesis_author", text, final=True, output_meta={})
    assert compliance["status"] == "pass"
    assert compliance["final_artifact_completeness"]["status"] == "pass"
    assert compliance["final_artifact_completeness"]["section_presence"] == {
        "bottom_line": True,
        "risks_of_acting": True,
        "risks_of_waiting": True,
        "next_steps": True,
        "claim_boundaries": True,
    }


def test_synthetic_final_vague_claim_boundaries_fail() -> None:
    sections = [
        "# Bottom line\nRecommend a conditional go path using S1_TEST_SOURCE and S2_TEST_SOURCE because the packet supports a bounded option.",
        "# Risks of acting\nThe risk of acting is execution error and preventable exposure.",
        "# Risks of waiting\nThe risk of waiting is delay cost and missed escalation timing.",
        "# Next steps / stop-go gates\nUse a no-go trigger, narrow-go trigger, rollback trigger, monitoring gate, and accountable owner.",
        "# Claim boundaries\nThis benchmark artifact uses sources and should not be treated as advice.",
    ]
    text = "\n\n".join(sections)
    while runner.word_count(text) < 940:
        text += " The source packet supports conditional execution discipline, monitoring, rollback ownership, and explicit approval checks."
    compliance = runner.role_compliance("final_synthesis_author", text, final=True, output_meta={})
    assert compliance["status"] == "fail"
    assert "claim_boundary_section_lacks_substantive_boundary_text" in compliance["final_artifact_completeness"]["failures"]


def test_synthetic_final_does_not_conclude_and_unsupported_until_gates_passes() -> None:
    sections = [
        "# Bottom line\nRecommend a conditional go path using S1_TEST_SOURCE and S2_TEST_SOURCE because the packet supports a bounded option.",
        "# Risks of acting\nThe risk of acting is execution error and preventable exposure.",
        "# Risks of waiting\nThe risk of waiting is delay cost and missed escalation timing.",
        "# Next steps / stop-go gates\nUse a no-go trigger, narrow-go trigger, rollback trigger, monitoring gate, and accountable owner.",
        "# Claim boundaries\nThis brief does not conclude broad approval exists, and final execution remains unsupported until gates pass under S1_TEST_SOURCE and S2_TEST_SOURCE.",
    ]
    text = "\n\n".join(sections)
    while runner.word_count(text) < 940:
        text += " The recommendation remains conditional, source bounded, monitored, reversible where possible, and explicit about what remains unsupported until gates pass."
    compliance = runner.role_compliance("final_synthesis_author", text, final=True, output_meta={})
    assert compliance["status"] == "pass"


def test_claim_boundary_only_repair_prompt_is_bounded_and_exactly_structured() -> None:
    failed = "\n\n".join([
        "# Bottom line\nRecommend a conditional go path using S1_TEST_SOURCE and S2_TEST_SOURCE because the packet supports a bounded option.",
        "# Risks of acting\nThe risk of acting is execution error and preventable exposure.",
        "# Risks of waiting\nThe risk of waiting is delay cost and missed escalation timing.",
        "# Next steps / stop-go gates\nUse a no-go trigger, narrow-go trigger, rollback trigger, monitoring gate, and accountable owner.",
        "# Claim boundaries\nThis benchmark artifact uses sources and should not be treated as advice.",
    ])
    while runner.word_count(failed) < 940:
        failed += " The source packet supports conditional execution discipline, monitoring, rollback ownership, and explicit approval checks."
    word_band = runner.final_word_band_compliance(failed)
    completeness = runner.final_artifact_completeness(failed, {})
    repair_kind = runner.final_repair_prompt_kind(
        word_band_result=word_band,
        final_completeness_result=completeness,
    )
    prompt = runner.build_final_repair_user(
        repair_kind=repair_kind,
        final_band=runner.final_word_band_policy(),
        previous_word_count=runner.word_count(failed),
        failed_final_word_band=word_band,
        final_quality_failures=completeness["failures"],
        final_completeness=completeness,
        final_state_source_audit={"status": "pass", "packet_hash_preserved": True, "invented_source_ids": []},
        context_governor_instructions="Use frozen context only.",
        state_json="{}",
        gov_notes_json="{}",
        baton_json="{}",
        registry_json="{}",
        retrieved="SOURCE_PACKET_MD",
        required_options_text="conditional_go",
        failed_output_text=failed,
    )
    assert repair_kind == runner.FINAL_REPAIR_KIND_CLAIM_BOUNDARY_ONLY
    assert "FINAL_ARTIFACT_CLAIM_BOUNDARY_REPAIR" in prompt
    assert "Repair only the claim-boundary failure." in prompt
    assert "Return the full final artifact." in prompt
    assert "Bottom line" in prompt
    assert "Risks of acting" in prompt
    assert "Risks of waiting" in prompt
    assert "Next steps / stop-go gates" in prompt
    assert "Claim boundaries" in prompt
    assert "Target 1050-1150 words." in prompt
    assert "Must end with a complete standalone sentence." in prompt
    assert "No commentary." in prompt
    assert "No appendix." in prompt
    assert "No judge-facing explanation." in prompt
    assert "Do not continue prior truncated text." in prompt


def test_final_compression_prompt_renders_for_complete_overlength_final() -> None:
    overlength = final_text_with_exact_word_count(1375)
    word_band = runner.final_word_band_compliance(overlength)
    completeness = runner.final_artifact_completeness(overlength, {})
    source_audit = {"status": "pass", "packet_hash_preserved": True, "invented_source_ids": []}
    repair_kind = runner.final_repair_prompt_kind(
        word_band_result=word_band,
        final_completeness_result=completeness,
    )
    prompt = runner.build_final_repair_user(
        repair_kind=repair_kind,
        final_band=runner.final_word_band_policy(),
        previous_word_count=runner.word_count(overlength),
        failed_final_word_band=word_band,
        final_quality_failures=["word_band_failure"],
        final_completeness=completeness,
        final_state_source_audit=source_audit,
        context_governor_instructions="Use frozen context only.",
        state_json="{}",
        gov_notes_json="{}",
        baton_json="{}",
        registry_json="{}",
        retrieved="SOURCE_PACKET_MD",
        required_options_text="conditional_go",
        failed_output_text=overlength,
    )
    assert repair_kind == runner.FINAL_REPAIR_KIND_COMPRESSION_ONLY
    assert "FINAL_ARTIFACT_COMPRESSION_REPAIR" in prompt
    assert "The current artifact is complete but too long." in prompt
    assert "The hard 900-1,300 body-word band remains mandatory." in prompt
    assert "Target 1180 words." in prompt
    assert "Returning over 1300 fails." in prompt
    assert "You must cut at least 180 words unless already below 1300." in prompt
    assert "The output must be at least 10 percent shorter than the input and no more than 1,250 words." in prompt
    assert "If the input is over 1300, returning above 1300 is invalid." in prompt
    assert f"capped at {runner.FINAL_COMPRESSION_REPAIR_MAX_TOKENS}" in prompt
    for heading in runner.FINAL_SYNTHESIS_REQUIRED_HEADINGS:
        assert f"## {heading}" in prompt
    assert runner.final_repair_max_tokens_for_kind(repair_kind) == runner.FINAL_COMPRESSION_REPAIR_MAX_TOKENS


def test_final_compression_prompt_forbids_new_analysis_and_preserves_markdown_headings_and_source_ids() -> None:
    text = final_text_with_exact_word_count(1375)
    prompt = runner.build_final_repair_user(
        repair_kind=runner.FINAL_REPAIR_KIND_COMPRESSION_ONLY,
        final_band=runner.final_word_band_policy(),
        previous_word_count=1375,
        failed_final_word_band=runner.final_word_band_compliance(text),
        final_quality_failures=["word_band_failure"],
        final_completeness=runner.final_artifact_completeness(text, {}),
        final_state_source_audit={"status": "pass", "packet_hash_preserved": True, "invented_source_ids": []},
        context_governor_instructions="Use frozen context only.",
        state_json="{}",
        gov_notes_json="{}",
        baton_json="{}",
        registry_json="{}",
        retrieved="SOURCE_PACKET_MD",
        required_options_text="conditional_go",
        failed_output_text=text,
    )
    assert "Do not add new analysis." in prompt
    assert "Do not add new sections." in prompt
    assert "Preserve the five required Markdown heading lines exactly" in prompt
    assert "## Bottom line; ## Risks of acting; ## Risks of waiting; ## Next steps / stop-go gates; ## Claim boundaries." in prompt
    assert "Do not convert headings to plain text, bullets, labels, inline phrases, or unmarked section names." in prompt
    assert "Do not return the artifact if any required heading line is missing, duplicated, renamed, demoted to plain text, or moved out of order." in prompt
    assert "A compression repair with lost headings fails even if the word count is valid." in prompt
    assert "Before returning, verify each required Markdown heading line remains present exactly once, as its own line, in the same order." in prompt
    assert "Preserve exact source IDs." in prompt
    assert "Preserve recommendation and action-boundary logic." in prompt
    assert "Cut lower-priority wording." in prompt
    assert "Merge repetitive sentences." in prompt
    assert "Remove filler and duplicate explanation." in prompt
    assert "Prefer deleting explanatory repetition over preserving every sentence." in prompt
    assert "Do not preserve paragraph count." in prompt
    assert "Do not preserve section length." in prompt
    assert "Compress tables/bullets aggressively." in prompt
    assert "Keep exact source IDs, but remove redundant citations." in prompt
    assert "Return only the compressed final artifact." in prompt


def test_final_compression_repair_requires_exact_heading_template_for_acceptance() -> None:
    repaired = final_text_with_exact_word_count(1180).replace("# ", "## ")
    assert runner.final_heading_template_compliance(repaired)["status"] == "pass"
    assert (
        runner.final_repair_heading_template_requirement(
            runner.FINAL_REPAIR_KIND_COMPRESSION_ONLY,
            repaired,
        )["status"]
        == "pass"
    )

    heading_loss = repaired.replace("## Bottom line", "Bottom line", 1)
    template = runner.final_repair_heading_template_requirement(
        runner.FINAL_REPAIR_KIND_COMPRESSION_ONLY,
        heading_loss,
    )
    assert template["status"] == "fail"
    assert "missing_exact_final_heading:## Bottom line" in template["failures"]


def test_historical_d12_retry3_final_repair_fixture_fails_exact_heading_template() -> None:
    repair = d12_retry3_raw_output("turn_006_final_repair_001.json")
    template = runner.final_repair_heading_template_requirement(
        runner.FINAL_REPAIR_KIND_COMPRESSION_ONLY,
        repair["text"],
    )
    assert template["status"] == "fail"
    assert set(template["missing_headings"]) == {
        "## Bottom line",
        "## Risks of acting",
        "## Risks of waiting",
        "## Next steps / stop-go gates",
        "## Claim boundaries",
    }


def test_final_repair_attempts_record_actual_repair_model() -> None:
    runner_text = RUNNER_PATH.read_text(encoding="utf-8")
    assert "repair_out = call_model(repair_model" in runner_text
    assert '"model": repair_model' in runner_text
    assert '"final_synthesis_model": model' in runner_text


def test_synthetic_complete_1375_word_final_triggers_compression_repair_path() -> None:
    overlength = final_text_with_exact_word_count(1375)
    assert runner.final_artifact_completeness(overlength, {})["status"] == "pass"
    assert runner.final_word_band_compliance(overlength)["status"] == "fail_over_hard_max"
    assert (
        runner.final_repair_prompt_kind(
            word_band_result=runner.final_word_band_compliance(overlength),
            final_completeness_result=runner.final_artifact_completeness(overlength, {}),
        )
        == runner.FINAL_REPAIR_KIND_COMPRESSION_ONLY
    )


def test_synthetic_complete_1440_word_final_routes_to_gpt55_compression_repair() -> None:
    overlength = final_text_with_exact_word_count(1440)
    cfg = runner.config_for_condition("holo_build_arch_frontier_optimized_opus_gpt55", runner.load_configs())
    plan = runner.randomized_holo_session_plan(
        cfg,
        run_id="D10_RETRY3_ROUTE_NO_PROVIDER",
        packet_hash="packet_hash",
        turn_count=len(runner.HOLO_TURNS),
        session_template="frontier_optimized_opus_gpt55_v1",
    )
    repair_kind = runner.final_repair_prompt_kind(
        word_band_result=runner.final_word_band_compliance(overlength),
        final_completeness_result=runner.final_artifact_completeness(overlength, {}),
    )
    assert repair_kind == runner.FINAL_REPAIR_KIND_COMPRESSION_ONLY
    assert runner.final_repair_model_for_kind(
        repair_kind,
        plan["final_synthesis_model"],
        plan,
    ) == "openai:gpt-5.5"


def test_synthetic_repaired_final_1250_words_with_sections_passes() -> None:
    repaired = final_text_with_exact_word_count(1250)
    compliance = runner.role_compliance("final_synthesis_author", repaired, final=True, output_meta={})
    assert compliance["status"] == "pass"
    assert compliance["final_word_band_status"] == "pass"
    assert compliance["final_artifact_completeness"]["status"] == "pass"


def test_synthetic_repaired_final_1295_words_with_sections_passes() -> None:
    repaired = final_text_with_exact_word_count(1295)
    compliance = runner.role_compliance("final_synthesis_author", repaired, final=True, output_meta={})
    assert compliance["status"] == "pass"
    assert compliance["final_word_band_status"] == "pass"
    assert compliance["final_artifact_completeness"]["status"] == "pass"


def test_synthetic_repaired_final_1421_words_with_sections_fails_word_band() -> None:
    repaired = final_text_with_exact_word_count(1421)
    compliance = runner.role_compliance("final_synthesis_author", repaired, final=True, output_meta={})
    assert compliance["status"] == "fail"
    assert compliance["final_word_band_status"] == "fail_over_hard_max"
    assert compliance["final_artifact_completeness"]["status"] == "pass"


def test_synthetic_repaired_final_1347_words_with_sections_fails_word_band() -> None:
    repaired = final_text_with_exact_word_count(1347)
    compliance = runner.role_compliance("final_synthesis_author", repaired, final=True, output_meta={})
    assert compliance["status"] == "fail"
    assert compliance["final_word_band_status"] == "fail_over_hard_max"
    assert compliance["final_artifact_completeness"]["status"] == "pass"


def test_synthetic_under_1300_final_missing_claim_boundaries_fails() -> None:
    sections = [
        "# Bottom Line\nRecommend the source-bounded conditional path using S1_TEST_SOURCE and S2_TEST_SOURCE.",
        "# Risks of Acting\nThe risk of acting is execution error, preventable exposure, and overbroad authority.",
        "# Risks of Waiting\nThe risk of waiting is operational delay, missed escalation timing, and stakeholder confusion.",
        "# Trigger Taxonomy\nUse a no-go trigger, narrow-go trigger, rollback trigger, monitoring gate, and accountable owner.",
    ]
    text = "\n\n".join(sections)
    while runner.word_count(text) < 940:
        text += " The source packet supports conditional execution discipline, monitoring, rollback ownership, and explicit approval checks."
    compliance = runner.role_compliance("final_synthesis_author", text, final=True, output_meta={})
    assert runner.word_count(text) < 1300
    assert compliance["status"] == "fail"
    assert "missing_final_section:claim_boundaries" in compliance["final_artifact_completeness"]["failures"]


def test_d13_artifact_002_incomplete_blind_fixture_fails_solo_baseline_eligibility() -> None:
    packet = json.loads(D13_BLIND_COMPARISON_PACKET.read_text(encoding="utf-8"))
    artifacts = {item["artifact_label"]: item for item in packet["artifacts"]}
    artifact = artifacts["ARTIFACT_002"]
    text = artifact["artifact_text"]

    assert hashlib.sha256(text.encode()).hexdigest() == artifact["artifact_text_sha256"]
    assert artifact["artifact_body_word_count"] == 1032
    assert runner.word_count(text) == 1032

    completeness = runner.final_artifact_completeness(text, {})
    assert completeness["status"] == "fail"
    assert "unclean_or_mid_sentence_ending" in completeness["failures"]
    assert "missing_final_section:claim_boundaries" in completeness["failures"]

    validation = runner.solo_baseline_eligibility_validation(D13_PACKET_DIR, text)
    assert validation["deterministic_gate_pass"] is True
    assert validation["final_word_band_pass"] is True
    assert validation["final_artifact_completeness_pass"] is False
    assert validation["solo_baseline_eligible"] is False
    assert "final_artifact_completeness_failed" in validation["failures"]


def test_historical_optimized_d10_repair_1347_remains_not_proof_clean() -> None:
    manifest = json.loads(OPTIMIZED_D10_RUN_MANIFEST.read_text(encoding="utf-8"))
    condition = manifest["conditions"][0]
    repair_attempt = condition["final_repair_attempts"][0]
    arch_summary = condition["architecture_evidence_validation"]
    assert repair_attempt["repaired_word_count"] == 1347
    assert repair_attempt["repaired_final_word_band_compliance"]["status"] == "fail_over_hard_max"
    assert repair_attempt["repaired_final_completeness"]["status"] == "pass"
    assert arch_summary["final_word_band_pass"] is False
    assert arch_summary["proof_credit_eligible"] is False


def test_historical_optimized_d10_retry3_1421_remains_not_proof_clean() -> None:
    manifest = json.loads(OPTIMIZED_D10_RETRY3_RUN_MANIFEST.read_text(encoding="utf-8"))
    condition = manifest["conditions"][0]
    repair_attempts = condition["final_repair_attempts"]
    arch_summary = condition["architecture_evidence_validation"]
    assert manifest["provider_calls"] == 10
    assert manifest["failed_provider_calls"] == 0
    assert manifest["judging_runs"] == 0
    assert manifest["scores_generated"] == 0
    assert manifest["unblinding_runs"] == 0
    assert condition["artifact_hash"] == "42eefd19d1f156d747463083157f8dec915b33cda8cbd9031b9a48090d62d812"
    assert [item["repair_kind"] for item in repair_attempts] == [
        runner.FINAL_REPAIR_KIND_COMPRESSION_ONLY,
        runner.FINAL_REPAIR_KIND_COMPRESSION_ONLY,
    ]
    assert [item["repaired_word_count"] for item in repair_attempts] == [1429, 1421]
    assert repair_attempts[-1]["repaired_final_word_band_compliance"]["status"] == "fail_over_hard_max"
    assert repair_attempts[-1]["repaired_final_completeness"]["status"] == "pass"
    assert arch_summary["final_artifact_completeness_pass"] is True
    assert arch_summary["final_word_band_pass"] is False
    assert arch_summary["proof_credit_eligible"] is False


def test_historical_d11_optimized_holo_remains_proof_clean() -> None:
    metadata = json.loads((D11_PROOF_CLEAN_CONDITION_DIR / "artifact_metadata.json").read_text(encoding="utf-8"))
    arch_evidence = json.loads((D11_PROOF_CLEAN_CONDITION_DIR / "arch_evidence.json").read_text(encoding="utf-8"))
    validation = metadata["architecture_evidence_validation"]
    assert metadata["proof_credit_eligible"] is True
    assert validation["proof_credit_eligible"] is True
    assert validation["deterministic_gate_pass"] is True
    assert validation["required_roles_all_completed"] is True
    assert validation["role_compliance_all_pass"] is True
    assert validation["intermediate_completeness_all_pass"] is True
    assert validation["state_audit_all_pass"] is True
    assert validation["registry_acceptance_all_pass"] is True
    assert validation["no_failed_required_turn_consumed_by_final"] is True
    assert arch_evidence["proof_credit_architecture_status"] == "eligible_if_all_turn_audits_pass_and_deterministic_gate_passes"


def test_v4_2_proof_credit_word_band_strictness_remains_unchanged() -> None:
    policy = runner.final_word_band_policy()
    assert policy == {"min_words": 900, "max_words": 1300, "repair_target_words": 1180}
    assert runner.final_word_band_compliance(" ".join(["word"] * 1300))["status"] == "pass"
    assert runner.final_word_band_compliance(" ".join(["word"] * 1301))["status"] == "fail_over_hard_max"


def test_bounded_second_compression_repair_requires_clean_source_and_no_other_blockers() -> None:
    repaired = final_text_with_exact_word_count(1347)
    word_band = runner.final_word_band_compliance(repaired)
    completeness = runner.final_artifact_completeness(repaired, {})
    clean_source = {"status": "pass", "packet_hash_preserved": True, "invented_source_ids": []}
    dirty_source = {"status": "fail", "packet_hash_preserved": True, "invented_source_ids": ["S9_FAKE"]}
    assert runner.eligible_for_bounded_final_compression_repair(
        word_band_result=word_band,
        final_completeness_result=completeness,
        state_source_audit_result=clean_source,
        other_final_blockers=[],
    )
    assert not runner.eligible_for_bounded_final_compression_repair(
        word_band_result=word_band,
        final_completeness_result=completeness,
        state_source_audit_result=dirty_source,
        other_final_blockers=[],
    )
    assert not runner.eligible_for_bounded_final_compression_repair(
        word_band_result=word_band,
        final_completeness_result=completeness,
        state_source_audit_result=clean_source,
        other_final_blockers=["missing_claim_boundaries"],
    )


def test_successful_final_repair_preserves_required_sections_and_source_ids() -> None:
    repaired = final_text_with_sections()
    compliance = runner.role_compliance("final_synthesis_author", repaired, final=True, output_meta={})
    assert compliance["status"] == "pass"
    assert compliance["final_word_band_status"] == "pass"
    assert compliance["final_artifact_completeness"]["status"] == "pass"
    assert {"S1_TEST_SOURCE", "S2_TEST_SOURCE"} <= set(runner.SOURCE_ID_RE.findall(repaired))
