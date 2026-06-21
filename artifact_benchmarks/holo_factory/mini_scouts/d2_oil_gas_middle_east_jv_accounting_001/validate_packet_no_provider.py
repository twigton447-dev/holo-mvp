from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

PACKET_DIR = Path(__file__).resolve().parent
PROVIDER_CALLS = 0
LIVE_ARTIFACTS_GENERATED = 0
SCORES_GENERATED = 0

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
            # Match full labels only so ordinary domain words like Government do not
            # trip the Gov architecture-leak guard.
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])", text):
                findings.append({"file": rel, "term": term})
    return {"status": "PASS" if not findings else "FAIL", "findings": findings}


def main() -> int:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        require((PACKET_DIR / rel).exists(), errors, f"missing file: {rel}")

    if errors:
        print(json.dumps({"status": "D2_MINI_SCOUT_PACKET_VALIDATION_FAIL", "provider_calls": 0, "errors": errors}, indent=2))
        return 1

    packet = read_json("source_packet.json")
    manifest = read_json("source_manifest.json")
    gate = read_json("deterministic_gate_policy.json")
    blind = read_json("blind_packet_manifest.json")
    lock = read_json("packet_lock.json")
    freeze = read_json("freeze_manifest.json")
    config = read_json("contamination_scan_config.json")

    require(packet.get("real_public_sources_only") is True, errors, "packet does not require real public sources only")
    require(packet.get("contestants_may_browse") is False, errors, "contestants may browse")
    require(packet.get("source_count", 0) >= 8, errors, "source count below required minimum")
    require(packet.get("case_facts", {}).get("facts_are_case_scenario_not_external_sources") is True, errors, "scenario facts not labeled")
    for source in packet.get("sources") or []:
        for field in ["source_id", "source_title", "publisher", "publication_or_content_date", "url_or_citation", "excerpt_text", "source_type", "strength_classification", "limitations", "source_hash"]:
            require(bool(source.get(field)), errors, f"{source.get('source_id', 'unknown')}: missing {field}")
        require(source.get("is_synthetic") is False, errors, f"{source.get('source_id')}: synthetic source marked true")
        require(source.get("source_hash") == source_hash(source), errors, f"{source.get('source_id')}: source hash mismatch")

    counts = manifest.get("source_type_counts") or {}
    require(counts.get("strong", 0) >= 2, errors, "missing 2 strong sources")
    require(counts.get("useful_normal", 0) >= 2, errors, "missing 2 useful normal sources")
    require(counts.get("stale_tempting", 0) >= 1, errors, "missing stale/tempting source")
    require(counts.get("contradictory_or_complicating", 0) >= 1, errors, "missing contradictory/complicating source")
    require(counts.get("weak_or_limited", 0) >= 1, errors, "missing weak/limited source")
    require(counts.get("table_chart_stat_element", 0) >= 1, errors, "missing table/chart/stat element")

    word_gate = gate.get("layer_1_deterministic_gate", {}).get("artifact_body_word_count", {})
    require(word_gate.get("min") == 900 and word_gate.get("max") == 1300, errors, "word gate mismatch")
    require(word_gate.get("scope") == "main_artifact_body_only", errors, "word gate scope mismatch")
    require("no_proof_credit" in word_gate.get("failure_result", ""), errors, "word gate does not fail proof credit")

    require(blind.get("architecture_evidence_visible_to_judges") is False, errors, "architecture evidence visible to judges")
    require(blind.get("contestant_identity_visible_to_judges") is False, errors, "contestant identity visible to judges")
    contamination = scan_visible_files(config)
    require(contamination["status"] == "PASS", errors, "visible contamination scan failed")

    locked_files = lock.get("locked_files") or {}
    for rel, expected in locked_files.items():
        path = PACKET_DIR / rel
        require(path.exists(), errors, f"locked path missing: {rel}")
        if path.exists():
            require(sha_file(path) == expected, errors, f"locked file hash mismatch: {rel}")

    frozen_files = freeze.get("frozen_files") or {}
    for rel, expected in frozen_files.items():
        path = PACKET_DIR / rel
        require(path.exists(), errors, f"frozen path missing: {rel}")
        if path.exists():
            require(sha_file(path) == expected, errors, f"frozen file hash mismatch: {rel}")

    result = {
        "status": "D2_MINI_SCOUT_PACKET_VALIDATION_PASS" if not errors else "D2_MINI_SCOUT_PACKET_VALIDATION_FAIL",
        "packet_id": packet.get("packet_id"),
        "provider_calls": PROVIDER_CALLS,
        "live_artifacts_generated": LIVE_ARTIFACTS_GENERATED,
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
