from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


FACTORY_DIR = Path(__file__).resolve().parent
POLICY_DIR = FACTORY_DIR / "scoring_policies"
SCHEMA_DIR = FACTORY_DIR / "schemas"
DOMAIN_CARD_DIR = FACTORY_DIR / "domain_cards"
JUDGE_POLICY_DIR = FACTORY_DIR / "judge_policies"

PROTOCOL_PATH = POLICY_DIR / "combined_artifact_scoring_protocol_v4_1.md"
LOCK_PATH = POLICY_DIR / "combined_artifact_scoring_protocol_v4_1.lock.json"
MANIFEST_PATH = POLICY_DIR / "combined_artifact_scoring_protocol_v4_1.freeze_manifest.json"
DOMAIN_CARD_SCHEMA_PATH = SCHEMA_DIR / "domain_card_schema.json"
BLIND_PACKET_SCHEMA_PATH = SCHEMA_DIR / "blind_packet_schema.json"
SCANNER_PATH = FACTORY_DIR / "contamination_readiness_scanner_v4_1.py"
JUDGE_POLICY_PATH = JUDGE_POLICY_DIR / "holobuild_generation_judge_separation_policy_v4_1.json"

EXPECTED_DOMAIN_IDS = {
    "D1_capital_markets_execution_risk",
    "D2_oil_gas_middle_east_jv_accounting",
    "D3_insurance_reinsurance_catastrophe_risk",
    "D4_ap_procurement_vendor_risk",
    "D5_healthcare_medtech_evidence_synthesis",
}

CALIBRATION_SET = {
    "gold",
    "fluff",
    "math_wrong",
    "hallucinated_source",
    "hidden_trap_miss",
    "boundary_fail",
}

CRISIS_FIELDS = [
    "domain_crisis_context",
    "intended_reader",
    "decision_report_type",
    "public_value_question",
    "crisis_specific_source_requirements",
    "crisis_specific_hidden_traps",
    "required_data_or_calculation_checks",
    "affected_stakeholders",
    "practical_response_options_required",
    "claim_boundaries",
    "evidence_uncertainty_requirements",
]

GENERATION_COHORT_SUMMARY = {
    "HoloBuild",
    "GPT-5.5 solo",
    "Opus 4.8 solo",
    "Gemini 3.1 Pro solo",
}

HELD_OUT_JUDGE_COHORT_SUMMARY = {
    "Grok 4.3",
    "MiniMax M3 or MiniMax M2.7",
    "one additional fixed-ID non-generation judge if available",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def load_scanner_module() -> Any:
    spec = importlib.util.spec_from_file_location("contamination_readiness_scanner_v4_1", SCANNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("scanner_import_spec_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_domain_card(card: dict[str, Any], errors: list[str], path: Path) -> None:
    prefix = str(path)
    require(card.get("schema_version") == "domain_card_schema_v4_1", errors, f"{prefix}: bad schema_version")
    require(card.get("protocol_id") == "UNIVERSAL_HOLOBUILD_ARTIFACT_SCORING_PROTOCOL_V4_1", errors, f"{prefix}: bad protocol_id")
    layers = card.get("scoring_layers") or {}
    require(layers.get("layer_1") == "deterministic_gate_admissibility_only", errors, f"{prefix}: missing layer_1")
    require(layers.get("layer_2") == "rigorous_rubric_quality_score", errors, f"{prefix}: missing layer_2")
    require(layers.get("layer_3") == "hard_caps_override", errors, f"{prefix}: missing layer_3")
    require(layers.get("proof_credit_rule") == "no_proof_credit_if_layer_1_fails", errors, f"{prefix}: bad proof rule")
    require(len(card.get("hidden_failure_seams") or []) >= 4, errors, f"{prefix}: insufficient hidden_failure_seams")
    require(len(card.get("action_boundary_risks") or []) >= 2, errors, f"{prefix}: insufficient action_boundary_risks")
    overlay = card.get("overlay_anchors") or {}
    for key in ["DFACT-1", "DTRAP-1", "DOPS-1", "DSRC-1", "DAUD-1"]:
        require(isinstance(overlay.get(key), list) and len(overlay[key]) >= 2, errors, f"{prefix}: missing overlay {key}")
    judge_policy = card.get("judge_policy") or {}
    require(judge_policy.get("anonymous_packets_required") is True, errors, f"{prefix}: judge packets not anonymous")
    require(judge_policy.get("self_judge_decisive_score_allowed") is False, errors, f"{prefix}: self judge not blocked")
    require(set(judge_policy.get("proof_scoring_conflict_handling") or []) >= {"held_out_judges", "leave_one_out"}, errors, f"{prefix}: conflict handling incomplete")
    require(set(card.get("calibration_set_required") or []) == CALIBRATION_SET, errors, f"{prefix}: calibration set mismatch")
    require(card.get("artifact_type") == "decision-grade crisis brief", errors, f"{prefix}: artifact_type is not crisis brief")
    require("crisis brief" in str(card.get("decision_report_type", "")).lower(), errors, f"{prefix}: decision report type missing crisis brief")
    require("?" in str(card.get("public_value_question", "")), errors, f"{prefix}: public value question is not a question")
    for field in CRISIS_FIELDS:
        value = card.get(field)
        if isinstance(value, list):
            require(len(value) >= 3, errors, f"{prefix}: crisis field {field} has too few entries")
        else:
            require(isinstance(value, str) and len(value) >= 20, errors, f"{prefix}: crisis field {field} missing text")
    required_sections = set(card.get("required_sections") or [])
    require(
        required_sections
        >= {"what is happening", "why it matters now", "risks of acting", "risks of waiting", "claim boundaries and disclaimer"},
        errors,
        f"{prefix}: crisis decision sections incomplete",
    )


def main() -> int:
    errors: list[str] = []

    required_paths = [
        PROTOCOL_PATH,
        LOCK_PATH,
        MANIFEST_PATH,
        DOMAIN_CARD_SCHEMA_PATH,
        BLIND_PACKET_SCHEMA_PATH,
        SCANNER_PATH,
        JUDGE_POLICY_PATH,
    ]
    for path in required_paths:
        require(path.exists(), errors, f"missing required file: {path}")

    domain_paths = sorted(DOMAIN_CARD_DIR.glob("D*.v4_1.json"))
    require(len(domain_paths) == 5, errors, f"expected 5 domain cards, found {len(domain_paths)}")

    if errors:
        print(json.dumps({"status": "HOLOBUILD_SCAFFOLD_V4_1_SMOKE_FAIL", "provider_calls": 0, "errors": errors}, indent=2))
        return 1

    lock = read_json(LOCK_PATH)
    manifest = read_json(MANIFEST_PATH)
    judge_policy = read_json(JUDGE_POLICY_PATH)
    read_json(DOMAIN_CARD_SCHEMA_PATH)
    read_json(BLIND_PACKET_SCHEMA_PATH)

    require(lock.get("provider_calls") == 0, errors, "lock provider_calls is not 0")
    require(manifest.get("provider_calls_to_lock") == 0, errors, "manifest provider_calls_to_lock is not 0")
    word_gate = lock.get("word_count_gate") or {}
    require(word_gate.get("applies_to") == "main_artifact_body_only", errors, "word gate scope mismatch")
    require(word_gate.get("mini_test_artifact_body_words") == {"min": 900, "max": 1300}, errors, "mini word gate mismatch")
    require(word_gate.get("full_benchmark_artifact_body_words") == {"min": 1200, "max": 1800}, errors, "full benchmark word gate mismatch")
    require(set(word_gate.get("excluded_from_count") or []) == {"source_appendix", "citation_list", "machine_readable_metadata", "separated_audit_trail"}, errors, "word gate exclusions mismatch")
    require(word_gate.get("proof_credit_if_failed") is False, errors, "word gate allows proof credit on failure")
    protocol_key = str(PROTOCOL_PATH)
    protocol_rel_key = str(PROTOCOL_PATH.relative_to(Path.cwd()))
    expected_protocol_hash = (
        lock.get("protocol_markdown", {}).get("sha256")
        or (lock.get("locked_files") or {}).get(protocol_key)
        or (lock.get("locked_files") or {}).get(protocol_rel_key)
    )
    require(expected_protocol_hash == sha256(PROTOCOL_PATH), errors, "protocol hash mismatch in lock")

    manifest_files = manifest.get("frozen_files") or {}
    for rel_path, expected_hash in manifest_files.items():
        path = Path(rel_path)
        require(path.exists(), errors, f"manifest path missing: {rel_path}")
        if path.exists():
            require(sha256(path) == expected_hash, errors, f"manifest hash mismatch: {rel_path}")

    cards = [read_json(path) for path in domain_paths]
    found_ids = {card.get("domain_id") for card in cards}
    require(found_ids == EXPECTED_DOMAIN_IDS, errors, f"domain id set mismatch: {sorted(found_ids)}")
    for path, card in zip(domain_paths, cards):
        validate_domain_card(card, errors, path)

    scanner = load_scanner_module()
    require(scanner.PROVIDER_CALLS == 0, errors, "scanner provider calls is not 0")
    require("Holo" in scanner.HARD_FORBIDDEN_VISIBLE_LABELS, errors, "scanner missing hard forbidden Holo")
    require("proof_credit" in scanner.HARD_FORBIDDEN_VISIBLE_LABELS, errors, "scanner missing hard forbidden proof_credit")
    require("BATON_PASS" in scanner.HARD_FORBIDDEN_VISIBLE_LABELS, errors, "scanner missing hard forbidden BATON_PASS")
    require("Context Governor" in scanner.HARD_FORBIDDEN_VISIBLE_LABELS, errors, "scanner missing hard forbidden Context Governor")
    require("condition" in scanner.CONTEXT_SENSITIVE_TERMS, errors, "scanner missing context-sensitive condition")
    require("internal" in scanner.CONTEXT_SENSITIVE_TERMS, errors, "scanner missing context-sensitive internal")

    require(judge_policy.get("provider_calls") == 0, errors, "judge policy provider_calls is not 0")
    require(judge_policy.get("fixed_model_ids_only") is True, errors, "judge policy does not require fixed model IDs")
    require(judge_policy.get("latest_aliases_allowed") is False, errors, "judge policy allows latest aliases")
    require(set(judge_policy.get("generation_cohort_summary") or []) == GENERATION_COHORT_SUMMARY, errors, "generation cohort summary mismatch")
    require(set(judge_policy.get("held_out_judge_cohort_summary") or []) == HELD_OUT_JUDGE_COHORT_SUMMARY, errors, "held-out judge cohort summary mismatch")
    require(judge_policy.get("decisive_self_judging_allowed") is False, errors, "decisive self judging is not blocked")
    require(judge_policy.get("anonymous_blind_judge_packets_only") is True, errors, "anonymous blind judge packets are not required")
    require(judge_policy.get("scoring_order") == ["deterministic_gate_first", "held_out_median_score_second", "hard_caps_applied"], errors, "judge scoring order mismatch")
    contested = judge_policy.get("contested_policy") or {}
    require(contested.get("label") == "CONTESTED", errors, "CONTESTED label missing")
    require(contested.get("judge_spread_threshold_points") == 1.5, errors, "CONTESTED judge spread threshold mismatch")
    require(contested.get("hard_cap_disagreement_triggers_contested") is True, errors, "hard-cap disagreement does not trigger CONTESTED")
    require(contested.get("route") == "human_or_expert_adjudication", errors, "CONTESTED route mismatch")
    require(set(judge_policy.get("benchmark_conditions_supported") or []) >= {"solo_one_shot", "solo_self_refine_same_budget", "holo_build_arch"}, errors, "judge policy missing supported benchmark conditions")
    required_metadata = set(judge_policy.get("required_run_metadata_per_generation_and_judging_call") or [])
    require(
        required_metadata
        >= {
            "provider",
            "exact_model_id",
            "endpoint",
            "date",
            "reasoning_setting",
            "temperature",
            "max_tokens",
            "rubric_version_hash",
            "domain_card_hash",
            "packet_hash",
        },
        errors,
        "judge policy missing required run metadata fields",
    )
    final_rule = judge_policy.get("final_score_rule") or {}
    require(final_rule.get("contested_if_judge_spread_gt_points") == 1.5, errors, "judge spread contest threshold mismatch")
    require(final_rule.get("contested_if_hard_cap_disagreement") is True, errors, "hard-cap disagreement contest rule missing")
    self_judge = judge_policy.get("self_judge_policy") or {}
    require(self_judge.get("no_model_may_be_decisive_judge_of_artifact_it_generated") is True, errors, "self-judge generation block missing")
    require(self_judge.get("no_model_may_be_decisive_judge_of_artifact_it_helped_generate") is True, errors, "self-judge helped-generate block missing")

    result = {
        "status": "HOLOBUILD_SCAFFOLD_V4_1_SMOKE_PASS" if not errors else "HOLOBUILD_SCAFFOLD_V4_1_SMOKE_FAIL",
        "provider_calls": 0,
        "live_artifacts_generated": 0,
        "scores_generated": 0,
        "domains": sorted(found_ids),
        "domain_card_count": len(domain_paths),
        "crisis_report_fields_checked": CRISIS_FIELDS,
        "protocol_hash": sha256(PROTOCOL_PATH),
        "lock_hash": sha256(LOCK_PATH),
        "manifest_hash": sha256(MANIFEST_PATH),
        "scanner_id": scanner.SCANNER_ID,
        "judge_policy": str(JUDGE_POLICY_PATH.relative_to(Path.cwd())),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
