from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


FACTORY_DIR = Path(__file__).resolve().parent
DEFAULT_PACKET_DIR = FACTORY_DIR / "mini_scouts/d5_medtech_capacity_strain_001"
DOMAIN_CARD_PATH = FACTORY_DIR / "domain_cards/D5_healthcare_medtech_evidence_synthesis.v4_1.json"
RUBRIC_PATH = FACTORY_DIR / "scoring_policies/combined_artifact_scoring_protocol_v4_1.md"
RUBRIC_LOCK_PATH = FACTORY_DIR / "scoring_policies/combined_artifact_scoring_protocol_v4_1.lock.json"
SCANNER_PATH = FACTORY_DIR / "contamination_readiness_scanner_v4_1.py"

EXPORTER_ID = "d5_mini_scout_blind_packet_exporter_v4_1"
PROVIDER_CALLS = 0
SCORES_GENERATED = 0
VALID_CONDITIONS = ("holo_build_arch", "solo_openai_gpt_5_5")

HOLO_MODE_DIAGNOSTIC_V3 = "diagnostic_v3"
HOLO_MODE_FULL_GOV_V4 = "full_gov_v4"
HOLO_MODE_PATENT_ALIGNED_V4 = "patent_aligned_v4"
PROOF_ELIGIBLE_HOLO_MODE = HOLO_MODE_PATENT_ALIGNED_V4
LEGACY_HOLO_MODES = (HOLO_MODE_DIAGNOSTIC_V3, HOLO_MODE_FULL_GOV_V4)
EXPORT_PURPOSE_PROOF = "proof"
EXPORT_PURPOSE_DIAGNOSTIC_ABLATION = "diagnostic_ablation"
EXPORT_PURPOSES = (EXPORT_PURPOSE_PROOF, EXPORT_PURPOSE_DIAGNOSTIC_ABLATION)
LEGACY_MODE_DEPRECATION_NOTICE = "Legacy Holo modes are preserved for ablation/history only and are banned from proof-credit use."

HARD_FORBIDDEN_PATTERNS = {
    "Holo": re.compile(r"holo", re.IGNORECASE),
    "Gov": re.compile(r"(?<![a-z.])gov(?![a-z])", re.IGNORECASE),
    "Governor": re.compile(r"governor", re.IGNORECASE),
    "draft_not_frozen": re.compile(r"draft_not_frozen", re.IGNORECASE),
    "benchmark_credit": re.compile(r"benchmark_credit", re.IGNORECASE),
    "proof_credit": re.compile(r"proof_credit", re.IGNORECASE),
    "candidate_not_frozen": re.compile(r"candidate_not_frozen", re.IGNORECASE),
    "holo_frontier_fixed_v1": re.compile(r"holo_frontier_fixed_v1", re.IGNORECASE),
    "solo_openai": re.compile(r"solo_openai", re.IGNORECASE),
    "ablation": re.compile(r"ablation", re.IGNORECASE),
    "Context Governor": re.compile(r"context governor", re.IGNORECASE),
    "STATE_OBJECT": re.compile(r"state_object", re.IGNORECASE),
    "Artifact Registry": re.compile(r"artifact registry", re.IGNORECASE),
    "Model Router": re.compile(r"model router", re.IGNORECASE),
    "BATON_PASS": re.compile(r"baton_pass", re.IGNORECASE),
    "adversarial role": re.compile(r"adversarial role", re.IGNORECASE),
    "role compliance": re.compile(r"role[-_ ]compliance", re.IGNORECASE),
    "state audit": re.compile(r"state[-_ ]audit", re.IGNORECASE),
    "synthesis trigger": re.compile(r"synthesis trigger", re.IGNORECASE),
}

CONTEXT_SENSITIVE_PROCESS_PATTERNS = [
    re.compile(r"\bcondition_id\b", re.IGNORECASE),
    re.compile(r"\bbenchmark_condition\b", re.IGNORECASE),
    re.compile(r"\bcondition_family\b", re.IGNORECASE),
    re.compile(r"\bholo_condition\b", re.IGNORECASE),
    re.compile(r"\bsolo_condition\b", re.IGNORECASE),
    re.compile(r"\bgeneration_condition\b", re.IGNORECASE),
    re.compile(r"\bcondition_manifest\b", re.IGNORECASE),
    re.compile(r"\bcondition_type\b", re.IGNORECASE),
    re.compile(r"\bmodel_condition\b", re.IGNORECASE),
    re.compile(r"\binternal_generation\b", re.IGNORECASE),
    re.compile(r"\binternal_state\b", re.IGNORECASE),
    re.compile(r"\binternal_label\b", re.IGNORECASE),
    re.compile(r"\binternal_scaffold\b", re.IGNORECASE),
    re.compile(r"\binternal_process\b", re.IGNORECASE),
    re.compile(r"\binternal_run\b", re.IGNORECASE),
    re.compile(r"\binternal_metadata\b", re.IGNORECASE),
    re.compile(r"\bbuilder_internal\b", re.IGNORECASE),
]


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def artifact_metadata_path(packet_dir: Path, run_id: str, condition: str) -> Path:
    return packet_dir / "runs" / run_id / condition / "artifact_metadata.json"


def load_condition_metadata(packet_dir: Path, run_id: str, condition: str) -> dict[str, Any] | None:
    path = artifact_metadata_path(packet_dir, run_id, condition)
    if not path.exists():
        return None
    return read_json(path)


def proof_export_guard(packet_dir: Path, run_id: str, artifacts: dict[str, str], export_purpose: str) -> dict[str, Any]:
    if export_purpose not in EXPORT_PURPOSES:
        return {
            "proof_export_allowed": False,
            "status": "D5_MINI_SCOUT_BLIND_EXPORT_FAIL_CLOSED_PROOF_INELIGIBLE",
            "reason": "unknown_export_purpose",
            "export_purpose": export_purpose,
        }
    metadata = load_condition_metadata(packet_dir, run_id, "holo_build_arch") if "holo_build_arch" in artifacts else None
    if metadata is None:
        if "holo_build_arch" not in artifacts:
            return {
                "proof_export_allowed": True,
                "diagnostic_export": export_purpose == EXPORT_PURPOSE_DIAGNOSTIC_ABLATION,
                "export_purpose": export_purpose,
                "holo_mode": None,
                "proof_export_policy": "no_holobuild_artifact_in_export",
            }
        return {
            "proof_export_allowed": export_purpose == EXPORT_PURPOSE_DIAGNOSTIC_ABLATION,
            "status": "D5_MINI_SCOUT_BLIND_EXPORT_FAIL_CLOSED_PROOF_INELIGIBLE",
            "reason": "missing_holobuild_artifact_metadata",
            "export_purpose": export_purpose,
            "holo_mode": None,
            "diagnostic_export": export_purpose == EXPORT_PURPOSE_DIAGNOSTIC_ABLATION,
        }
    holo_mode = metadata.get("holo_mode")
    legacy_holo_mode = bool(metadata.get("legacy_holo_mode")) or holo_mode in LEGACY_HOLO_MODES
    deterministic_gate_pass = metadata.get("deterministic_gate_status") == "pass"
    architecture_evidence_valid = metadata.get("architecture_evidence_status") == "valid"
    proof_credit_eligible = bool(metadata.get("proof_credit_eligible"))
    proof_credit_class = metadata.get("proof_credit_class")
    if export_purpose == EXPORT_PURPOSE_DIAGNOSTIC_ABLATION:
        return {
            "proof_export_allowed": True,
            "diagnostic_export": True,
            "export_purpose": export_purpose,
            "holo_mode": holo_mode,
            "legacy_holo_mode": legacy_holo_mode,
            "legacy_mode_reason": LEGACY_MODE_DEPRECATION_NOTICE if legacy_holo_mode else None,
            "proof_credit_eligible": False,
            "proof_export_policy": "diagnostic_ablation_export_explicitly_requested",
        }
    if legacy_holo_mode:
        return {
            "proof_export_allowed": False,
            "status": "D5_MINI_SCOUT_BLIND_EXPORT_FAIL_CLOSED_LEGACY_MODE",
            "reason": "legacy_holobuild_mode_banned_from_proof_export",
            "export_purpose": export_purpose,
            "holo_mode": holo_mode,
            "legacy_holo_mode": True,
            "legacy_mode_reason": LEGACY_MODE_DEPRECATION_NOTICE,
            "proof_credit_eligible": False,
        }
    checks = {
        "holo_mode_is_patent_aligned_v4": holo_mode == PROOF_ELIGIBLE_HOLO_MODE,
        "proof_credit_eligible_true": proof_credit_eligible is True,
        "proof_credit_class_patent_aligned": proof_credit_class == "patent_aligned_v4_proof_eligible",
        "deterministic_gate_pass": deterministic_gate_pass,
        "architecture_evidence_valid": architecture_evidence_valid,
    }
    if not all(checks.values()):
        return {
            "proof_export_allowed": False,
            "status": "D5_MINI_SCOUT_BLIND_EXPORT_FAIL_CLOSED_PROOF_INELIGIBLE",
            "reason": "holobuild_artifact_not_proof_eligible",
            "export_purpose": export_purpose,
            "holo_mode": holo_mode,
            "legacy_holo_mode": False,
            "proof_credit_eligible": proof_credit_eligible,
            "proof_credit_class": proof_credit_class,
            "eligibility_checks": checks,
        }
    return {
        "proof_export_allowed": True,
        "diagnostic_export": False,
        "export_purpose": export_purpose,
        "holo_mode": holo_mode,
        "legacy_holo_mode": False,
        "proof_credit_eligible": True,
        "proof_export_policy": "patent_aligned_v4_only_if_gate_and_architecture_evidence_validate",
        "eligibility_checks": checks,
    }


def scan_text(text: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for label, pattern in HARD_FORBIDDEN_PATTERNS.items():
        match = pattern.search(text)
        if match:
            findings.append({"term": label, "excerpt": text[max(0, match.start() - 60): match.end() + 60]})
    for pattern in CONTEXT_SENSITIVE_PROCESS_PATTERNS:
        match = pattern.search(text)
        if match:
            findings.append({"term": pattern.pattern, "excerpt": text[max(0, match.start() - 60): match.end() + 60]})
    return findings


def neutral_domain_card() -> dict[str, Any]:
    card = read_json(DOMAIN_CARD_PATH)
    return {
        "schema_version": "judge_visible_domain_card_v4_1",
        "domain_id": card["domain_id"],
        "domain_label": card["domain_label"],
        "artifact_type": card["artifact_type"],
        "intended_reader": card["intended_reader"],
        "decision_report_type": card["decision_report_type"],
        "domain_crisis_context": card["domain_crisis_context"],
        "public_value_question": card["public_value_question"],
        "required_sections": card["required_sections"],
        "required_disclaimer": card["required_disclaimer"],
        "claim_boundaries": card["claim_boundaries"],
        "evidence_uncertainty_requirements": card["evidence_uncertainty_requirements"],
        "practical_response_options_required": card["practical_response_options_required"],
        "required_data_or_calculation_checks": card["required_data_or_calculation_checks"],
    }


def neutral_rubric() -> dict[str, Any]:
    lock = read_json(RUBRIC_LOCK_PATH)
    word_gate = lock["word_count_gate"]
    return {
        "schema_version": "judge_visible_frozen_rubric_v4_1",
        "rubric_hash": sha_file(RUBRIC_PATH),
        "rubric_lock_hash": sha_file(RUBRIC_LOCK_PATH),
        "scoring_layers": {
            "layer_1": "deterministic gate is admission-only",
            "layer_2": "quality score is based only on visible artifact evidence",
            "layer_3": "hard caps override raw quality scores; lowest cap wins",
        },
        "word_count_gate": {
            "applies_to": word_gate["applies_to"],
            "mini_test_artifact_body_words": word_gate["mini_test_artifact_body_words"],
            "full_benchmark_artifact_body_words": word_gate["full_benchmark_artifact_body_words"],
            "excluded_from_count": word_gate["excluded_from_count"],
            "failure_result": "deterministic_gate_invalid_for_official_score_unless_explicit_packet_override",
        },
        "universal_criteria": [
            "source grounding and evidence discipline",
            "quantitative correctness and reproducibility",
            "hidden-failure detection",
            "domain reasoning and causal logic",
            "operational specificity",
            "control path and action-boundary discipline",
            "missing-data and uncertainty handling",
            "statistical, sensitivity, and assumption calibration",
            "auditability, replayability, and ownership",
            "implementation readiness, testing, and rollback",
            "communication quality and client usability",
        ],
        "judge_rules": [
            "Score only the anonymous artifact against the frozen source packet and task brief.",
            "Do not infer who or what generated the artifact.",
            "Do not award credit for length, polish, generic risk language, or unsupported confidence.",
            "Apply hard caps for invented facts, source-boundary failures, missing action boundaries, unclean truncation, or unsupported major crisis-resolution claims.",
        ],
    }


def artifact_label_order(run_id: str, available_conditions: list[str]) -> list[tuple[str, str]]:
    ranked = sorted((sha_text(f"{run_id}:{condition}"), condition) for condition in available_conditions)
    return [(condition, f"ARTIFACT_{index:03d}") for index, (_, condition) in enumerate(ranked, start=1)]


def load_artifacts(packet_dir: Path, run_id: str) -> dict[str, str]:
    artifacts: dict[str, str] = {}
    for condition in VALID_CONDITIONS:
        artifact_path = packet_dir / "runs" / run_id / condition / "artifact.md"
        if artifact_path.exists():
            artifacts[condition] = artifact_path.read_text(encoding="utf-8")
    return artifacts


def build_packet(packet_dir: Path, run_id: str, condition: str, label: str, artifact_text: str) -> dict[str, Any]:
    return {
        "artifact_label": label,
        "artifact_text": artifact_text,
        "task_brief": {
            "text": (packet_dir / "task_brief.md").read_text(encoding="utf-8"),
            "sha256": sha_file(packet_dir / "task_brief.md"),
        },
        "domain_card": neutral_domain_card(),
        "source_packet": read_json(packet_dir / "source_packet.json"),
        "frozen_rubric": neutral_rubric(),
    }


def export_packets(packet_dir: Path, run_id: str, output_dir: Path, *, export_purpose: str = EXPORT_PURPOSE_PROOF) -> int:
    artifacts = load_artifacts(packet_dir, run_id)
    if not artifacts:
        print(
            json.dumps(
                {
                    "status": "D5_MINI_SCOUT_BLIND_EXPORT_NO_ARTIFACTS",
                    "reason": "No artifact.md files exist yet; live generation has not run.",
                    "provider_calls": PROVIDER_CALLS,
                    "scores_generated": SCORES_GENERATED,
                },
                indent=2,
            )
        )
        return 2

    proof_guard = proof_export_guard(packet_dir, run_id, artifacts, export_purpose)
    if not proof_guard.get("proof_export_allowed"):
        print(
            json.dumps(
                {
                    "status": proof_guard.get("status", "D5_MINI_SCOUT_BLIND_EXPORT_FAIL_CLOSED_PROOF_INELIGIBLE"),
                    **proof_guard,
                    "provider_calls": PROVIDER_CALLS,
                    "scores_generated": SCORES_GENERATED,
                },
                indent=2,
            )
        )
        return 3

    labels = artifact_label_order(run_id, sorted(artifacts))
    contamination: list[dict[str, Any]] = []
    exported: list[dict[str, str]] = []
    internal_map: dict[str, str] = {}
    for condition, label in labels:
        packet = build_packet(packet_dir, run_id, condition, label, artifacts[condition])
        packet_text = json.dumps(packet, indent=2, sort_keys=False)
        findings = scan_text(packet_text)
        if findings:
            contamination.append({"artifact_label": label, "findings": findings})
            continue
        path = output_dir / f"{label}.json"
        write_json(path, packet)
        exported.append({"artifact_label": label, "path": str(path), "sha256": sha_file(path)})
        internal_map[label] = condition

    map_path = output_dir / "anonymization_map.internal.json"
    manifest_path = output_dir / "blind_export_manifest.json"
    write_json(map_path, internal_map)
    manifest = {
        "exporter_id": EXPORTER_ID,
        "run_id": run_id,
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "blind_packets": exported,
        "anonymization_map_path": str(map_path),
        "judge_visible_fields": ["anonymous_artifact", "source_packet", "task_brief", "domain_card", "frozen_rubric"],
        "judge_hidden_fields": [
            "generator identity",
            "condition names",
            "architecture evidence",
            "generation traces",
            "benchmark metadata",
            "prior scores",
        ],
        "proof_export_guard": proof_guard,
        "contamination_scan_passed": not contamination,
        "contamination_findings": contamination,
        "provider_calls": PROVIDER_CALLS,
        "scores_generated": SCORES_GENERATED,
    }
    write_json(manifest_path, manifest)
    print(json.dumps({"status": "D5_MINI_SCOUT_BLIND_EXPORT_PASS" if not contamination else "D5_MINI_SCOUT_BLIND_EXPORT_FAIL", **manifest}, indent=2))
    return 0 if not contamination else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Export anonymous D5 mini scout judge packets.")
    parser.add_argument("--packet-dir", default=str(DEFAULT_PACKET_DIR))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--export-purpose", choices=EXPORT_PURPOSES, default=EXPORT_PURPOSE_PROOF)
    args = parser.parse_args()
    packet_dir = Path(args.packet_dir).resolve()
    output_dir = Path(args.output_dir).resolve() if args.output_dir else packet_dir / "runs" / args.run_id / "blind_judge_packets_v4_1"
    return export_packets(packet_dir, args.run_id, output_dir, export_purpose=args.export_purpose)


if __name__ == "__main__":
    raise SystemExit(main())
