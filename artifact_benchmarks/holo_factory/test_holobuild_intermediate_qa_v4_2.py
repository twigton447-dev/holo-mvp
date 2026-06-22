from __future__ import annotations

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
D11_VALIDATOR = REPO_ROOT / "artifact_benchmarks/holo_factory/mini_scouts/d11_cyber_incident_contract_notice_emergency_cloud_access_001/validate_packet_no_provider.py"
D10_POST_V4_2_CONDITION_DIR = (
    REPO_ROOT
    / "artifact_benchmarks/holo_factory/mini_scouts/d10_infrastructure_configuration_change_001/runs"
    / "d10_infrastructure_configuration_change_001_post_v4_2_opusgovb_holo_only_live_20260622T000000Z"
    / "frontier_holo_opus_gov_b_v1"
)
OPTIMIZED_D10_RUN_MANIFEST = (
    REPO_ROOT
    / "artifact_benchmarks/holo_factory/mini_scouts/d10_infrastructure_configuration_change_001/runs"
    / "d10_infrastructure_configuration_change_001_frontier_optimized_opus_gpt55_holo_only_live_retry2_20260622T000000Z"
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
        "# Bottom Line\nRecommend a conditional go path using S1_TEST_SOURCE and S2_TEST_SOURCE because the packet supports a bounded option, not an unrestricted action.",
        "# Risks of Acting\nThe risk of acting is execution error, preventable exposure, and reliance on a source boundary the packet does not prove.",
        "# Risks of Waiting\nThe risk of waiting is delay cost, operational drift, and missed escalation timing if leadership does not assign an owner.",
        "# Trigger Taxonomy\nUse a go trigger, no-go trigger, rollback trigger, monitoring gate, and executive escalation owner before expansion.",
        "# Claim Boundaries\nThis benchmark artifact uses only S1_TEST_SOURCE and S2_TEST_SOURCE. It does not provide legal, medical, regulatory, statistical, or operational approval.",
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


def render_d10_solo_final_prompt() -> str:
    surfaces = d10_surfaces()
    base = runner.packet_context(surfaces["task_brief"], surfaces["source_packet_md"])
    role, objective = runner.SOLO_TURNS[-1]
    user = (
        f"{base}\n\nTURN ROLE: {role}\nTURN OBJECTIVE: {objective}\n"
        "Return only the final artifact.\n\n"
        "PRIOR DRAFT OR NOTES\n====================\n[prior solo draft]\n"
    )
    return f"SYSTEM:\n{runner.build_base_system()}\n\nUSER:\n{user}"


def render_d10_holo_final_prompt() -> str:
    surfaces = d10_surfaces()
    packet_hash = runner.sha_file(D10_PACKET_DIR / "source_packet.json")
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
        f"{runner.FINAL_SYNTHESIS_TRIGGER_TAXONOMY}\n"
        "Include the strongest counterargument or temptation for the opposite action, then explain why the recommended path is safer, stronger, or conditional.\n"
        f"{runner.EXACT_SOURCE_ID_GENERATION_INSTRUCTION}\n"
    )
    return f"SYSTEM:\n{runner.build_base_system()}\n\nUSER:\n{user}"


def render_intermediate_repair_prompt_for_test(role: str = "options_operational_usefulness_reviewer") -> str:
    objective = {
        "initial_decision_brief_drafter": "Draft a source-grounded initial decision frame.",
        "assumption_and_evidence_attacker": "Attack assumptions, weak evidence, stale claims, missing calculations, and unsupported causal links.",
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
        roster = runner.holo_turn_plan(plan)
        assert roster[0][1] == "openai:gpt-5.5"
        assert roster[1][1] == "openai:gpt-5.5"
        assert roster[2][1] == "anthropic:claude-opus-4-8"
        assert roster[3][1] == "openai:gpt-5.5"
        assert roster[4][1] == "openai:gpt-5.5"
        assert roster[5][1] == "anthropic:claude-opus-4-8"


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
        "# Bottom Line\nRecommend a conditional go path using S1_TEST_SOURCE and S2_TEST_SOURCE because the packet supports a bounded option, not an unrestricted action.",
        "# Risks of Acting\nThe risk of acting is execution error, preventable exposure, and reliance on a source boundary the packet does not prove.",
        "# Risks of Waiting\nThe risk of waiting is delay cost, operational drift, and missed escalation timing if leadership does not assign an owner.",
        "# Trigger Taxonomy\nUse a go trigger, no-go trigger, rollback trigger, monitoring gate, and executive escalation owner before expansion.",
        "# Counterargument and claim boundaries\nThe strongest counterargument is speed, but this packet only supports a source-bounded conditional action. It does not prove broad approval, legal clearance, irreversible release authority, or operational approval beyond S1_TEST_SOURCE and S2_TEST_SOURCE.",
    ]
    text = "\n\n".join(sections)
    while runner.word_count(text) < 940:
        text += " The recommendation remains conditional, source bounded, monitored, reversible where possible, and explicit about what the packet does not prove."
    compliance = runner.role_compliance("final_synthesis_author", text, final=True, output_meta={})
    assert compliance["status"] == "pass"
    assert compliance["final_artifact_completeness"]["section_presence"]["claim_boundaries"] is True


def test_counterargument_claim_boundaries_heading_without_boundary_text_fails() -> None:
    sections = [
        "# Bottom Line\nRecommend a conditional go path using S1_TEST_SOURCE and S2_TEST_SOURCE because the packet supports a bounded option, not an unrestricted action.",
        "# Risks of Acting\nThe risk of acting is execution error, preventable exposure, and reliance on a source boundary the packet does not prove.",
        "# Risks of Waiting\nThe risk of waiting is delay cost, operational drift, and missed escalation timing if leadership does not assign an owner.",
        "# Trigger Taxonomy\nUse a go trigger, no-go trigger, rollback trigger, monitoring gate, and executive escalation owner before expansion.",
        "# Counterargument and claim boundaries\nThe strongest counterargument is speed. Leaders want momentum, confidence, crisp ownership, fast execution, immediate delivery, and strong implementation.",
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


def test_final_compression_prompt_forbids_new_analysis_and_preserves_boundaries_and_source_ids() -> None:
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
    assert "claim boundaries" in prompt
    assert "Preserve exact source IDs." in prompt
    assert "Preserve recommendation and action-boundary logic." in prompt
    assert "Cut lower-priority wording." in prompt
    assert "Merge repetitive sentences." in prompt
    assert "Remove filler and duplicate explanation." in prompt
    assert "Return only the repaired artifact body." in prompt


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


def test_synthetic_repaired_final_1295_words_with_sections_passes() -> None:
    repaired = final_text_with_exact_word_count(1295)
    compliance = runner.role_compliance("final_synthesis_author", repaired, final=True, output_meta={})
    assert compliance["status"] == "pass"
    assert compliance["final_word_band_status"] == "pass"
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
