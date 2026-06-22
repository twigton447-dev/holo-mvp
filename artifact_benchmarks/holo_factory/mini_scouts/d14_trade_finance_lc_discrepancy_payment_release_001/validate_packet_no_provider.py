from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

PACKET_DIR = Path(__file__).resolve().parent
PACKET_ID = "d14_trade_finance_lc_discrepancy_payment_release_001"
PROVIDER_CALLS = 0
LIVE_ARTIFACTS_GENERATED = 0
SCORES_GENERATED = 0
JUDGING_RUNS = 0

REQUIRED_FILES = [
    "README.md",
    "task_brief.md",
    "source_packet.json",
    "source_packet.md",
    "source_manifest.json",
    "deterministic_gate_policy.json",
    "blind_packet_manifest.json",
    "packet_lock.json",
    "freeze_manifest.json",
    "contamination_scan_config.json",
    "PACKET_READINESS_REPORT.md",
    "INTERNAL_ATLAS_DESIGN_NOTE.md",
    "validate_packet_no_provider.py",
]


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hash(source: dict[str, Any]) -> str:
    payload = {k: v for k, v in source.items() if k != "source_hash"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()


def read_json(name: str) -> Any:
    return json.loads((PACKET_DIR / name).read_text(encoding="utf-8"))


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def scan_visible_files(config: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    for rel in config["model_visible_files"]:
        text = (PACKET_DIR / rel).read_text(encoding="utf-8")
        for term in config["hard_forbidden_visible_labels"]:
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])", text):
                findings.append({"file": rel, "term": term})
    return {"status": "PASS" if not findings else "FAIL", "findings": findings}


def main() -> int:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        require((PACKET_DIR / rel).exists(), errors, f"missing file: {rel}")

    if errors:
        print(json.dumps({"status": "D14_MINI_SCOUT_PACKET_VALIDATION_FAIL", "provider_calls": 0, "errors": errors}, indent=2))
        return 1

    packet = read_json("source_packet.json")
    manifest = read_json("source_manifest.json")
    gate = read_json("deterministic_gate_policy.json")
    blind = read_json("blind_packet_manifest.json")
    lock = read_json("packet_lock.json")
    freeze = read_json("freeze_manifest.json")
    config = read_json("contamination_scan_config.json")

    require(packet.get("packet_id") == PACKET_ID, errors, "packet id mismatch")
    require(packet.get("frozen_sources_only") is True, errors, "packet does not require frozen sources only")
    require(packet.get("contestants_may_browse") is False, errors, "contestants may browse")
    require(packet.get("source_count") == 10, errors, "source count must equal 10")
    require(packet.get("case_facts", {}).get("facts_are_case_scenario_not_external_sources") is True, errors, "scenario facts not labeled")
    require(packet.get("domain", "").startswith("D14 "), errors, "packet domain is not D14")
    require(packet.get("provider_calls") == 0, errors, "packet provider_calls not zero")
    require(packet.get("artifact_generation") == 0, errors, "packet artifact_generation not zero")
    require(packet.get("judging") == 0, errors, "packet judging not zero")
    require(packet.get("scoring") == 0, errors, "packet scoring not zero")

    exact_ids = [s.get("source_id") for s in packet.get("sources") or []]
    require(len(exact_ids) == len(set(exact_ids)) == 10, errors, "source IDs must be unique and count 10")
    expected_classifications = {
        "S1_LC_PAYMENT_RELEASE_POLICY": "strong",
        "S2_PRIOR_DAY_PARTIAL_DOCUMENT_REVIEW": "stale_tempting",
        "S3_DERIVED_LC_STATUS_DASHBOARD": "table_chart_stat_element",
        "S4_APPLICANT_DISCREPANCY_WAIVER_EMAIL": "useful_normal",
        "S5_CURRENT_FINAL_DOCUMENT_EXAM_QUEUE": "strong",
        "S6_COMPLIANCE_REIMBURSEMENT_HOLD_RECORD": "strong",
        "S7_CARRIER_ARRIVAL_AND_DEMURRAGE_NOTICE": "useful_normal",
        "S8_RELATIONSHIP_MANAGER_APPLICANT_PRESSURE_NOTE": "contradictory_or_complicating",
        "S9_WEAK_BENEFICIARY_CLEAN_DOCS_ASSERTION": "weak_or_limited",
        "S10_SWIFT_PREPARATION_AND_HOLD_QUEUE_LOG": "useful_normal",
    }
    require(exact_ids == list(expected_classifications), errors, "source IDs must match the D14 frozen source mix order")
    for source in packet.get("sources") or []:
        for field in ["source_id", "source_title", "publisher", "publication_or_content_date", "url_or_citation", "excerpt_text", "source_type", "strength_classification", "limitations", "source_hash"]:
            require(bool(source.get(field)), errors, f"{source.get('source_id', 'unknown')}: missing {field}")
        require(source.get("is_synthetic") is True, errors, f"{source.get('source_id')}: expected synthetic internal source")
        require(source.get("source_hash") == source_hash(source), errors, f"{source.get('source_id')}: source hash mismatch")
        require(re.fullmatch(r"S\d+_[A-Z0-9_]+", source.get("source_id", "")) is not None, errors, f"{source.get('source_id')}: source id format not exact")
        require(source.get("strength_classification") == expected_classifications.get(source.get("source_id")), errors, f"{source.get('source_id')}: source classification mismatch")

    counts = manifest.get("source_type_counts") or {}
    require(counts.get("strong", 0) == 3, errors, "source mix must include exactly 3 strong sources")
    require(counts.get("useful_normal", 0) == 3, errors, "source mix must include exactly 3 useful normal sources")
    require(counts.get("contradictory_or_complicating", 0) == 1, errors, "source mix must include exactly 1 contradictory/complicating source")
    require(counts.get("stale_tempting", 0) == 1, errors, "source mix must include exactly 1 stale/tempting source")
    require(counts.get("weak_or_limited", 0) == 1, errors, "source mix must include exactly 1 weak/limited source")
    require(counts.get("table_chart_stat_element", 0) == 1, errors, "source mix must include exactly 1 table/chart/stat element")
    require(manifest.get("no_source_fetching_performed") is True, errors, "source fetching flag not true")

    visible_text = "\n".join((PACKET_DIR / rel).read_text(encoding="utf-8") for rel in ["task_brief.md", "source_packet.md", "source_packet.json"])
    required_terms = [
        "letter of credit",
        "LC",
        "discrepancy",
        "discrepancy waiver",
        "document examination",
        "prior-day",
        "partial document review",
        "stale",
        "derived dashboard",
        "payment release",
        "reimbursement",
        "Compliance release",
        "SWIFT",
        "hold queue",
        "irreversible",
        "final payment confirmation",
        "two-person Trade Finance approval",
        "payment release is not authorized",
        "source IDs",
        "claim boundaries",
        "disclaimer",
    ]
    for term in required_terms:
        require(term.lower() in visible_text.lower(), errors, f"missing expected D14 term: {term}")

    source_packet_text = (PACKET_DIR / "source_packet.md").read_text(encoding="utf-8")
    for source_id in exact_ids:
        require(source_id in source_packet_text, errors, f"source_packet.md missing exact source id: {source_id}")

    word_gate = gate.get("layer_1_deterministic_gate", {}).get("artifact_body_word_count", {})
    require(word_gate.get("min") == 900 and word_gate.get("max") == 1300, errors, "word gate mismatch")
    require(word_gate.get("scope") == "main_artifact_body_only", errors, "word gate scope mismatch")
    require("no_proof_credit" in word_gate.get("failure_result", ""), errors, "word gate does not fail proof credit")
    require(gate.get("layer_1_deterministic_gate", {}).get("source_requirements", {}).get("must_use_exact_source_ids") is True, errors, "exact source ID gate missing")

    require(blind.get("architecture_evidence_visible_to_judges") is False, errors, "architecture evidence visible to judges")
    require(blind.get("contestant_identity_visible_to_judges") is False, errors, "contestant identity visible to judges")
    require(blind.get("internal_design_note_visible_to_judges") is False, errors, "internal design note visible to judges")
    contamination = scan_visible_files(config)
    require(contamination["status"] == "PASS", errors, "visible contamination scan failed")

    for rel in config["model_visible_files"]:
        require(rel != "INTERNAL_ATLAS_DESIGN_NOTE.md", errors, "internal note is model-visible")

    locked_files = lock.get("locked_files") or {}
    for rel, expected in locked_files.items():
        path = PACKET_DIR / rel
        require(path.exists(), errors, f"locked path missing: {rel}")
        if path.exists():
            require(sha_file(path) == expected, errors, f"locked file hash mismatch: {rel}")

    internal_files = lock.get("internal_non_model_visible_files") or {}
    for rel, expected in internal_files.items():
        path = PACKET_DIR / rel
        require(path.exists(), errors, f"internal locked path missing: {rel}")
        if path.exists():
            require(sha_file(path) == expected, errors, f"internal locked file hash mismatch: {rel}")

    frozen_files = freeze.get("frozen_files") or {}
    for rel, expected in frozen_files.items():
        path = PACKET_DIR / rel
        require(path.exists(), errors, f"frozen path missing: {rel}")
        if path.exists():
            require(sha_file(path) == expected, errors, f"frozen file hash mismatch: {rel}")

    result = {
        "status": "D14_MINI_SCOUT_PACKET_VALIDATION_PASS" if not errors else "D14_MINI_SCOUT_PACKET_VALIDATION_FAIL",
        "packet_id": packet.get("packet_id"),
        "provider_calls": PROVIDER_CALLS,
        "live_artifacts_generated": LIVE_ARTIFACTS_GENERATED,
        "judging_runs": JUDGING_RUNS,
        "scores_generated": SCORES_GENERATED,
        "source_count": packet.get("source_count"),
        "source_type_counts": counts,
        "packet_hash": sha_file(PACKET_DIR / "source_packet.json"),
        "packet_lock_hash": sha_file(PACKET_DIR / "packet_lock.json"),
        "freeze_manifest_hash": sha_file(PACKET_DIR / "freeze_manifest.json"),
        "contamination_scan_result": contamination,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
