from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


FACTORY_DIR = Path(__file__).resolve().parent
PACKET_DIR = FACTORY_DIR / "mini_scouts/d5_medtech_capacity_strain_001"
RUNNER_PATH = FACTORY_DIR / "run_d5_mini_scout_live.py"
EXPORTER_PATH = FACTORY_DIR / "export_d5_mini_scout_blind_packets_v4_1.py"
ARCH_SCHEMA_PATH = FACTORY_DIR / "schemas/holo_build_arch_evidence_schema.json"
ARCH_POLICY_PATH = FACTORY_DIR / "architecture_policies/holobuild_patent_alignment_policy_v4_1.json"
SCORING_LOCK_PATH = FACTORY_DIR / "scoring_policies/combined_artifact_scoring_protocol_v4_1.lock.json"

PROVIDER_CALLS = 0
LIVE_ARTIFACTS_GENERATED = 0
SCORES_GENERATED = 0
EXPECTED_PACKET_HASH = "b73292d9d2e4aac5f65a93ae168235d9d581ae17ebaf0a91aa16437018c527aa"
EXPECTED_CONDITIONS = {"holo_build_arch", "solo_openai_gpt_5_5"}
EXPECTED_TURN_COUNT = 6
EXPECTED_FULL_GOV_V4_CALL_COUNT = 14
EXPECTED_GOVERNOR_MAX_REPAIR_ATTEMPTS = 1
EXPECTED_WORD_TARGET = 1100
PROOF_ELIGIBLE_HOLO_MODE = "patent_aligned_v4"
LEGACY_HOLO_MODES = ("diagnostic_v3", "full_gov_v4")
LEGACY_MODE_DEPRECATION_NOTICE = "Legacy Holo modes are preserved for ablation/history only and are banned from proof-credit use."
REQUIRED_ARCH_TOKENS = [
    "CANONICAL STATE_OBJECT",
    "STATE_OBJECT_SHA256",
    "BATON_PASS",
    "BATON_PASS_SHA256",
    "ARTIFACT_REGISTRY",
    "ARTIFACT_REGISTRY_SHA256",
    "ARTIFACTS_REGISTRY",
    "ARTIFACTS_REGISTRY_SHA256",
    "RETRIEVED PINNED SOURCES AND ARTIFACTS",
    "gov_notes",
    "source_boundaries",
    "unresolved_tensions",
    "state_object_hash",
    "state_object_snapshot_path",
    "critical_constraints_preserved",
    "settled_decisions_if_present",
    "artifact_registry_entries",
    "artifact_registry_hash",
    "pinned_source_hashes",
    "pinned_artifact_hashes",
    "retrieve_by_id_or_source_reference_behavior",
    "token_budget_partial_injection_flags",
    "baton_pass",
    "selected_model",
    "adversarial_role",
    "role_compliance_result",
    "state_audit_constraint_preservation_result",
    "synthesis_trigger",
    "final_artifact_hash",
    "architecture_evidence_visible_to_judges",
    "prompt_card_sha256",
    "retrieved_ids",
    "semantic_role_checks",
    "invented_source_ids",
]
REQUIRED_FULL_GOV_V4_TOKENS = [
    "HOLO_MODE_FULL_GOV_V4",
    "RUN_MODE_FULL_GOV_V4",
    "FULL_GOV_V4_EXPECTED_HOLO_CALL_COUNT",
    "GOVERNOR_PROVIDER_MODEL",
    "--holo-mode",
    "governor_system_prompt",
    "governor_prompt",
    "parse_governor_json",
    "call_governor",
    "run_holobuild_full_gov_v4",
    "gov_init",
    "gov_update_audit",
    "gov_final_audit",
    "state_object_source",
    "governor_output",
    "baton_pass_source",
    "artifact_registry_source",
    "governor_output_or_governor_locked_update",
    "proof_credit_class",
    "no_provider_smoke_only",
    "diagnostic_only_no_proof_credit",
    "synthetic_smoke_only",
    "expected_holo_call_count",
    "generation prompt hash not matching Gov-produced state/baton/registry = no proof credit",
    "Gov final audit fail = no proof credit",
    "external provider-Governor v4 evidence is diagnostic-only unless explicitly reclassified by a future frozen policy",
    "GOVERNOR_MAX_REPAIR_ATTEMPTS",
    "GOV_REPAIR_SMOKE_CASES",
    "validate_governor_output_contract",
    "governor_repair_prompt",
    "repair_governor_output",
    "run_governor_repair_smoke_case",
    "--gov-repair-smoke-case",
    "BATON_PASS.missing_retrieved_artifact_ids",
    "governor_repair_failed",
    "invalid_init_missing_retrieved_ids_no_repair",
    "invalid_init_missing_retrieved_ids_repair_success",
    "invalid_init_missing_retrieved_ids_repair_fail",
    "The runner will not invent or backfill missing canonical Gov fields",
    "Proof credit is allowed only if final accepted Gov output is Governor-produced",
    "ATTEMPTED_PROVIDER_CALLS",
    "ACCEPTED_PROVIDER_CALLS",
    "FAILED_PROVIDER_CALLS",
    "attempted_provider_calls",
    "accepted_provider_calls",
    "failed_provider_calls",
    "save_failed_provider_attempts",
    "write_run_failure_report",
    "run_empty_gov_failure_accounting_smoke",
    "--empty-gov-failure-smoke",
    "--gov-model",
    "DEFAULT_GOVERNOR_PROVIDER_MODEL",
    "selected_governor_model",
    "raw_response_metadata",
    "provider_adapter_did_not_expose_raw_response_metadata_on_exception",
    "repair_retry_reason",
    "provider returned no accepted visible Gov output; repair only applies to invalid Gov JSON/text",
    "no_artifact_created_after_failure",
    "counts_consistent",
    "HOLO_MODE_PATENT_ALIGNED_V4",
    "RUN_MODE_PATENT_ALIGNED_V4",
    "patent_aligned_v4",
    "internal_state_management_step",
    "context_governor_implementation",
    "external_governor_provider_calls_required_for_proof_credit",
    "reported_not_forced",
    "patent_aligned_v4_proof_eligible",
    "USER_GOAL",
    "LATEST_INPUT_SUMMARY",
    "CRITICAL_CONSTRAINTS",
    "ROLLING_SUMMARY",
    "SETTLED_DECISIONS",
    "ARTIFACTS_REGISTRY",
    "REQUIRED_TOOLS",
    "PROOF_ELIGIBLE_HOLO_MODE",
    "LEGACY_HOLO_MODES",
    "LEGACY_MODE_DEPRECATION_NOTICE",
    "D5_MINI_SCOUT_LEGACY_HOLO_MODE_FAIL_CLOSED",
    "--diagnostic-legacy-holo-mode",
    "diagnostic_only_no_proof_credit",
    "proof_credit_eligible",
    "legacy_holo_mode",
    "legacy_mode_reason",
    "proof_credit_architecture_requirements",
]
EXPECTED_SOLO_ROLES = [
    "initial_decision_brief_draft",
    "assumption_and_evidence_attack",
    "contradiction_uncertainty_source_fidelity_pass",
    "options_risks_operational_usefulness_pass",
    "claim_discipline_overclaim_reduction_pass",
    "final_synthesis_900_1300_words",
]
EXPECTED_HOLO_REVIEWER_ROLES = [
    "initial_decision_brief_drafter",
    "assumption_and_evidence_attacker",
    "contradiction_uncertainty_source_fidelity_reviewer",
    "options_operational_usefulness_reviewer",
    "claim_discipline_overclaim_reducer",
]
BLIND_EXPORT_FORBIDDEN_TOKENS = [
    "architecture evidence",
    "condition names",
    "generation traces",
    "prior scores",
    "generator identity",
    "benchmark metadata",
]


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def load_module_from_path(module_name: str, path: Path) -> Any:
    if str(path.parent) not in sys.path:
        sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def literal_assignments(source: str) -> dict[str, Any]:
    assignments: dict[str, Any] = {}
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            try:
                assignments[name] = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                continue
    return assignments


def main() -> int:
    errors: list[str] = []
    require(PACKET_DIR.exists(), errors, f"missing packet dir: {PACKET_DIR}")
    require(RUNNER_PATH.exists(), errors, f"missing runner: {RUNNER_PATH}")
    require(EXPORTER_PATH.exists(), errors, f"missing blind exporter: {EXPORTER_PATH}")
    require(ARCH_SCHEMA_PATH.exists(), errors, f"missing architecture schema: {ARCH_SCHEMA_PATH}")
    require(ARCH_POLICY_PATH.exists(), errors, f"missing architecture policy: {ARCH_POLICY_PATH}")
    require(SCORING_LOCK_PATH.exists(), errors, f"missing scoring lock: {SCORING_LOCK_PATH}")

    if not errors:
        packet_hash = sha_file(PACKET_DIR / "source_packet.json")
        packet = read_json(PACKET_DIR / "source_packet.json")
        gate = read_json(PACKET_DIR / "deterministic_gate_policy.json")
        lock = read_json(PACKET_DIR / "packet_lock.json")
        scoring_lock = read_json(SCORING_LOCK_PATH)
        arch_schema = read_json(ARCH_SCHEMA_PATH)
        arch_policy = read_json(ARCH_POLICY_PATH)
        runner_text = RUNNER_PATH.read_text(encoding="utf-8")
        exporter_text = EXPORTER_PATH.read_text(encoding="utf-8")
        runner_assignments = literal_assignments(runner_text)
        runner_module = load_module_from_path("d5_runner_guard_validation", RUNNER_PATH)
        exporter_module = load_module_from_path("d5_exporter_guard_validation", EXPORTER_PATH)

        require(packet_hash == EXPECTED_PACKET_HASH, errors, "D5 packet hash mismatch")
        require(packet.get("real_public_sources_only") is True, errors, "packet is not real-public-sources-only")
        require(packet.get("contestants_may_browse") is False, errors, "packet allows contestant browsing")
        require(packet.get("source_count") == 9, errors, "source count mismatch")

        word_gate = gate["layer_1_deterministic_gate"]["artifact_body_word_count"]
        require(word_gate.get("min") == 900 and word_gate.get("max") == 1300, errors, "mini scout word gate mismatch")
        require(word_gate.get("scope") == "main_artifact_body_only", errors, "word gate scope mismatch")
        require("no_proof_credit" in word_gate.get("failure_result", ""), errors, "word gate does not block proof credit")
        require(scoring_lock["word_count_gate"]["mini_test_artifact_body_words"] == {"min": 900, "max": 1300}, errors, "scoring lock mini word gate mismatch")

        locked = lock.get("locked_files") or {}
        require(locked.get("source_packet.json") == EXPECTED_PACKET_HASH, errors, "packet lock does not pin source_packet hash")

        require("--live" in runner_text, errors, "runner missing --live support")
        require("--no-provider-smoke" in runner_text, errors, "runner missing --no-provider-smoke support")
        require("HOLO_ALLOW_LIVE" in runner_text, errors, "runner missing second live approval guard")
        require("D5_MINI_SCOUT_LIVE_FAIL_CLOSED" in runner_text, errors, "runner missing live fail-closed status")
        require(runner_assignments.get("RUN_MODE") == "d5_medtech_capacity_strain_001_corrected_v2_six_turn", errors, "runner missing corrected v2 run mode")
        require(runner_assignments.get("RUN_MODE_FULL_GOV_V4") == "d5_medtech_capacity_strain_001_full_gov_v4", errors, "runner missing full Gov v4 run mode")
        require(runner_assignments.get("RUN_MODE_PATENT_ALIGNED_V4") == "d5_medtech_capacity_strain_001_patent_aligned_v4", errors, "runner missing patent-aligned v4 run mode")
        require(runner_assignments.get("HOLO_MODE_FULL_GOV_V4") == "full_gov_v4", errors, "runner missing full Gov v4 mode literal")
        require(runner_assignments.get("HOLO_MODE_PATENT_ALIGNED_V4") == "patent_aligned_v4", errors, "runner missing patent-aligned v4 mode literal")
        require(runner_assignments.get("PROOF_ELIGIBLE_HOLO_MODE") is None or "PROOF_ELIGIBLE_HOLO_MODE = HOLO_MODE_PATENT_ALIGNED_V4" in runner_text, errors, "runner does not lock proof mode to patent_aligned_v4")
        require("LEGACY_HOLO_MODES = (HOLO_MODE_DIAGNOSTIC_V3, HOLO_MODE_FULL_GOV_V4)" in runner_text, errors, "runner does not hard-code legacy Holo modes")
        require(LEGACY_MODE_DEPRECATION_NOTICE in runner_text, errors, "runner missing legacy deprecation notice")
        require(runner_assignments.get("FULL_GOV_V4_EXPECTED_HOLO_CALL_COUNT") == EXPECTED_FULL_GOV_V4_CALL_COUNT, errors, "full Gov v4 expected call count is not 14")
        require(runner_assignments.get("GOVERNOR_MAX_REPAIR_ATTEMPTS") == EXPECTED_GOVERNOR_MAX_REPAIR_ATTEMPTS, errors, "Governor repair attempts are not bounded to one")
        require(runner_assignments.get("DEFAULT_GOVERNOR_PROVIDER_MODEL") == "openai:gpt-5.5", errors, "default Governor model is not a fixed model ID")
        require("GOVERNOR_PROVIDER_MODEL = DEFAULT_GOVERNOR_PROVIDER_MODEL" in runner_text, errors, "runner does not initialize Governor model from fixed default")
        require(runner_assignments.get("EXPECTED_PACKET_HASH") == EXPECTED_PACKET_HASH, errors, "runner does not pin expected packet hash")
        require(runner_assignments.get("EXPECTED_TURN_COUNT") == EXPECTED_TURN_COUNT, errors, "runner expected turn count is not 6")
        require(runner_assignments.get("FINAL_WORD_TARGET") == EXPECTED_WORD_TARGET, errors, "runner final word target is not 1100")
        require(runner_assignments.get("FINAL_WORD_MIN") == 900 and runner_assignments.get("FINAL_WORD_MAX") == 1300, errors, "runner final word range mismatch")
        solo_turns = runner_assignments.get("SOLO_SELF_REFINE_TURNS") or ()
        holo_turns = runner_assignments.get("HOLO_PROVIDER_TURNS") or ()
        require(len(solo_turns) == EXPECTED_TURN_COUNT, errors, "solo self-refine turn count is not 6")
        require(len(holo_turns) + 1 == EXPECTED_TURN_COUNT, errors, "HoloBuild reviewer plus synthesis turn count is not 6")
        require([item.get("role") for item in solo_turns] == EXPECTED_SOLO_ROLES, errors, "solo self-refine roles do not match required sequence")
        require([item.get("role") for item in holo_turns] == EXPECTED_HOLO_REVIEWER_ROLES, errors, "HoloBuild reviewer roles do not match corrected v2 sequence")
        require("If the draft exceeds" in runner_text and "revise shorter before final answer" in runner_text, errors, "runner missing hard final shortening instruction")
        for condition in EXPECTED_CONDITIONS:
            require(condition in runner_text, errors, f"runner missing condition {condition}")
        for token in REQUIRED_FULL_GOV_V4_TOKENS:
            require(token in runner_text, errors, f"runner missing full Gov v4 token: {token}")
        require("expected_holobuild_provider_models" in runner_text, errors, "runner missing full Gov model-count helper")
        require("GOVERNOR_PROVIDER_MODEL] + generation_models + [GOVERNOR_PROVIDER_MODEL] * (EXPECTED_TURN_COUNT + 1)" in runner_text, errors, "runner does not model 1 Gov init + 6 generation + 6 update + 1 final Gov call")
        require("external_governor_provider_calls_required_for_proof_credit\": False" in runner_text, errors, "runner still appears to require external Governor provider calls for proof credit")
        require("default=PROOF_ELIGIBLE_HOLO_MODE" in runner_text, errors, "runner default Holo mode is not patent_aligned_v4")
        require("--diagnostic-legacy-holo-mode" in runner_text, errors, "runner missing explicit diagnostic legacy flag")
        require("enforce_legacy_holo_mode_guard(args.holo_mode" in runner_text, errors, "runner does not enforce legacy-mode guard")
        require("D5_MINI_SCOUT_LEGACY_HOLO_MODE_FAIL_CLOSED" in runner_text, errors, "runner missing legacy mode fail-closed status")
        require("token_burn_policy\": \"reported_not_forced\"" in runner_text, errors, "runner does not record token burn as reported, not forced")
        for state_field in ("USER_GOAL", "LATEST_INPUT_SUMMARY", "CRITICAL_CONSTRAINTS", "ROLLING_SUMMARY", "SETTLED_DECISIONS", "ARTIFACTS_REGISTRY", "REQUIRED_TOOLS"):
            require(state_field in runner_text, errors, f"runner missing patent STATE_OBJECT field: {state_field}")
        require("synthetic_smoke_only\") and evidence.get(\"proof_credit_class\") != \"no_provider_smoke_only\"" in runner_text, errors, "validator does not fail smoke-as-proof")
        require("state_object_sha256\") not in prompt_surface" in runner_text, errors, "full Gov validator does not tie state hash to prompt")
        require("baton_pass_sha256\") not in prompt_surface" in runner_text, errors, "full Gov validator does not tie baton hash to prompt")
        require("artifact_registry_sha256\") not in prompt_surface" in runner_text, errors, "full Gov validator does not tie registry hash to prompt")
        require("Gov final audit did not pass" in runner_text, errors, "full Gov validator does not fail missing/failed final audit")
        require("if holo_mode == HOLO_MODE_FULL_GOV_V4" in runner_text, errors, "runner missing explicit full Gov v4 branch")
        require("repair_enabled=False" in runner_text, errors, "runner missing no-repair fail-closed smoke case")
        require("force_invalid_missing_retrieved_ids=True" in runner_text, errors, "runner missing invalid Gov output smoke injection")
        require("repair_attempts\": len(repairs)" in runner_text, errors, "runner does not record repair attempts in smoke result")
        require("repair_attempts" in runner_text and "bounded_max_attempts" in runner_text, errors, "runner does not record bounded repair evidence")

        for token in REQUIRED_ARCH_TOKENS:
            require(token in runner_text, errors, f"runner missing architecture evidence token: {token}")
        require("holo_architecture_user_prompt" in runner_text, errors, "runner missing canonical Holo architecture prompt builder")
        require("retrieve_registry_entries" in runner_text, errors, "runner missing registry retrieval by ID")
        require("def role_compliance(text: str, *, role: str" in runner_text, errors, "runner still appears to use shallow role compliance")
        require("generic_praise_only_pass" in runner_text, errors, "runner missing praise-only role compliance failure")
        require("missing_required_sections" in runner_text, errors, "runner missing final required-section compliance check")
        require("def state_audit(" in runner_text and "invented_source_ids" in runner_text, errors, "runner missing semantic state audit")
        require("text.strip() else \"fail\"" not in runner_text, errors, "runner still appears to use non-empty-output state audit")
        require("holo_turn_user_prompt(packet_dir, objective=turn[\"objective\"], previous_notes=reviewer_notes)" not in runner_text, errors, "runner still passes loose reviewer notes instead of registry artifacts")
        require(arch_schema["properties"]["architecture_evidence_visible_to_judges"]["const"] is False, errors, "architecture schema does not force judge-hidden evidence")
        require(arch_policy["architecture_evidence_visible_to_judges"] is False, errors, "architecture policy exposes evidence to judges")

        for token in BLIND_EXPORT_FORBIDDEN_TOKENS:
            require(token in exporter_text, errors, f"blind exporter missing hidden-field handling: {token}")
        require("neutral_domain_card" in exporter_text, errors, "blind exporter missing neutral domain card")
        require("neutral_rubric" in exporter_text, errors, "blind exporter missing neutral rubric")
        require("scan_text" in exporter_text, errors, "blind exporter missing contamination scan")
        require("--export-purpose" in exporter_text, errors, "blind exporter missing explicit export purpose")
        require("diagnostic_ablation" in exporter_text, errors, "blind exporter missing explicit diagnostic/ablation export purpose")
        require("proof_export_guard" in exporter_text, errors, "blind exporter missing proof export guard")
        require("D5_MINI_SCOUT_BLIND_EXPORT_FAIL_CLOSED_LEGACY_MODE" in exporter_text, errors, "blind exporter does not fail closed on legacy proof exports")
        require("D5_MINI_SCOUT_BLIND_EXPORT_FAIL_CLOSED_PROOF_INELIGIBLE" in exporter_text, errors, "blind exporter does not fail closed on proof-ineligible Holo artifacts")
        require("patent_aligned_v4_proof_eligible" in exporter_text, errors, "blind exporter does not require patent_aligned proof class")

        # Dynamic guard checks: prove old modes cannot become proof-eligible and proof export refuses them.
        for legacy_mode in LEGACY_HOLO_MODES:
            policy = runner_module.holo_mode_policy(legacy_mode, evidence_valid=True, deterministic_gate_pass=True)
            require(policy.get("proof_credit_eligible") is False, errors, f"{legacy_mode} unexpectedly proof-eligible")
            require(policy.get("proof_credit_class") == "diagnostic_only_no_proof_credit", errors, f"{legacy_mode} proof class is not diagnostic-only")
            try:
                runner_module.enforce_legacy_holo_mode_guard(legacy_mode, diagnostic_legacy_holo_mode=False)
                require(False, errors, f"{legacy_mode} did not fail closed without diagnostic flag")
            except SystemExit:
                pass
            runner_module.enforce_legacy_holo_mode_guard(legacy_mode, diagnostic_legacy_holo_mode=True)
        patent_policy = runner_module.holo_mode_policy(PROOF_ELIGIBLE_HOLO_MODE, evidence_valid=True, deterministic_gate_pass=True)
        require(patent_policy.get("proof_credit_eligible") is True, errors, "patent_aligned_v4 is not proof-eligible after evidence and gate pass")
        patent_without_evidence = runner_module.holo_mode_policy(PROOF_ELIGIBLE_HOLO_MODE, evidence_valid=False, deterministic_gate_pass=True)
        require(patent_without_evidence.get("proof_credit_eligible") is False, errors, "patent_aligned_v4 proof eligible without evidence validation")

        original_loader = exporter_module.load_condition_metadata
        try:
            exporter_module.load_condition_metadata = lambda packet_dir, run_id, condition: {
                "holo_mode": "diagnostic_v3",
                "legacy_holo_mode": True,
                "proof_credit_eligible": False,
                "proof_credit_class": "diagnostic_only_no_proof_credit",
                "deterministic_gate_status": "pass",
                "architecture_evidence_status": "valid",
            }
            legacy_export = exporter_module.proof_export_guard(PACKET_DIR, "synthetic", {"holo_build_arch": "body"}, "proof")
            require(legacy_export.get("proof_export_allowed") is False, errors, "proof export allows legacy diagnostic_v3")
            require(legacy_export.get("status") == "D5_MINI_SCOUT_BLIND_EXPORT_FAIL_CLOSED_LEGACY_MODE", errors, "legacy proof export does not fail with legacy-mode status")
            diagnostic_export = exporter_module.proof_export_guard(PACKET_DIR, "synthetic", {"holo_build_arch": "body"}, "diagnostic_ablation")
            require(diagnostic_export.get("proof_export_allowed") is True and diagnostic_export.get("diagnostic_export") is True, errors, "diagnostic export does not explicitly allow legacy ablation")
            exporter_module.load_condition_metadata = lambda packet_dir, run_id, condition: {
                "holo_mode": "patent_aligned_v4",
                "legacy_holo_mode": False,
                "proof_credit_eligible": True,
                "proof_credit_class": "patent_aligned_v4_proof_eligible",
                "deterministic_gate_status": "pass",
                "architecture_evidence_status": "valid",
            }
            proof_export = exporter_module.proof_export_guard(PACKET_DIR, "synthetic", {"holo_build_arch": "body"}, "proof")
            require(proof_export.get("proof_export_allowed") is True and proof_export.get("diagnostic_export") is False, errors, "proof export refuses valid patent_aligned_v4")
            exporter_module.load_condition_metadata = lambda packet_dir, run_id, condition: {
                "holo_mode": "patent_aligned_v4",
                "legacy_holo_mode": False,
                "proof_credit_eligible": False,
                "proof_credit_class": "diagnostic_only_no_proof_credit",
                "deterministic_gate_status": "pass",
                "architecture_evidence_status": "valid",
            }
            ineligible_export = exporter_module.proof_export_guard(PACKET_DIR, "synthetic", {"holo_build_arch": "body"}, "proof")
            require(ineligible_export.get("proof_export_allowed") is False, errors, "proof export allows patent mode without proof eligibility")
        finally:
            exporter_module.load_condition_metadata = original_loader

        runner_hash = sha_file(RUNNER_PATH)
        exporter_hash = sha_file(EXPORTER_PATH)
        arch_schema_hash = sha_file(ARCH_SCHEMA_PATH)
        arch_policy_hash = sha_file(ARCH_POLICY_PATH)
    else:
        packet_hash = None
        runner_hash = None
        exporter_hash = None
        arch_schema_hash = None
        arch_policy_hash = None

    result = {
        "status": "D5_MINI_SCOUT_READINESS_V4_1_PASS" if not errors else "D5_MINI_SCOUT_READINESS_V4_1_FAIL",
        "provider_calls": PROVIDER_CALLS,
        "live_artifacts_generated": LIVE_ARTIFACTS_GENERATED,
        "scores_generated": SCORES_GENERATED,
        "packet_dir": str(PACKET_DIR),
        "packet_hash": packet_hash,
        "conditions_supported": sorted(EXPECTED_CONDITIONS),
        "expected_turn_count_per_condition": EXPECTED_TURN_COUNT,
        "expected_full_gov_v4_holo_call_count": EXPECTED_FULL_GOV_V4_CALL_COUNT,
        "holobuild_modes": ["diagnostic_v3", "full_gov_v4", "patent_aligned_v4"],
        "diagnostic_v3_status": "diagnostic_only_no_proof_credit",
        "full_gov_v4_status": "diagnostic_only_no_proof_credit",
        "patent_aligned_v4_status": "proof_eligible_if_evidence_validates",
        "proof_eligible_holobuild_mode": PROOF_ELIGIBLE_HOLO_MODE,
        "legacy_mode_deprecation_notice": LEGACY_MODE_DEPRECATION_NOTICE,
        "final_word_target": EXPECTED_WORD_TARGET,
        "live_mode_fail_closed_by_default": True,
        "live_requires": ["--live", "HOLO_ALLOW_LIVE=1"],
        "holobuild_architecture_evidence_path_wired": RUNNER_PATH.exists(),
        "blind_export_path_wired": EXPORTER_PATH.exists(),
        "hashes": {
            "runner": runner_hash,
            "blind_exporter": exporter_hash,
            "architecture_schema": arch_schema_hash,
            "architecture_policy": arch_policy_hash,
        },
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
