from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

FACTORY_DIR = Path(__file__).resolve().parent
REPO_ROOT = FACTORY_DIR.parents[1]
MANIFEST_PATH = FACTORY_DIR / "mini_scouts/TEN_DOMAIN_PACKET_SUITE_MANIFEST.json"
SCORING_LOCK = FACTORY_DIR / "scoring_policies/unified_artifact_scoring_protocol_v5_2_structural_epistemic.lock.json"
RUNNER_PATH = FACTORY_DIR / "run_holobuild_mini_scout.py"
CONFIG_DIR = FACTORY_DIR / "configs"
EXPECTED_DOMAINS = {f"D{i}" for i in range(1, 11)}


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def run_packet_validator(path: Path) -> dict[str, Any]:
    result = subprocess.run([sys.executable, "-B", str(path)], cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    payload: dict[str, Any]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {"status": "PARSE_FAIL", "stdout": result.stdout, "stderr": result.stderr}
    payload["returncode"] = result.returncode
    payload["validator_path"] = repo_rel(path)
    return payload


def main() -> int:
    errors: list[str] = []
    if not MANIFEST_PATH.exists():
        errors.append(f"missing suite manifest: {repo_rel(MANIFEST_PATH)}")
        manifest = {"domains": []}
    else:
        manifest = read_json(MANIFEST_PATH)
    entries = manifest.get("domains", [])
    domain_ids = {item.get("domain_id") for item in entries}
    if domain_ids != EXPECTED_DOMAINS:
        errors.append(f"expected D1-D10 domains, got {sorted(domain_ids)}")
    if not RUNNER_PATH.exists():
        errors.append(f"missing runner: {repo_rel(RUNNER_PATH)}")
    if not SCORING_LOCK.exists():
        errors.append(f"missing scoring lock: {repo_rel(SCORING_LOCK)}")
    config_results = {}
    for name in ["frontier_solo_v1.json", "frontier_holo_v1.json", "mini_solo_v1.stub.json", "mini_holo_v1.stub.json"]:
        path = CONFIG_DIR / name
        if not path.exists():
            errors.append(f"missing config: {repo_rel(path)}")
            continue
        cfg = read_json(path)
        config_results[cfg["config_id"]] = {
            "path": repo_rel(path),
            "hash": sha_file(path),
            "live_ready": cfg.get("live_ready"),
            "condition_type": cfg.get("condition_type"),
            "architecture_mode": cfg.get("architecture_mode"),
            "proof_credit_eligible": cfg.get("proof_credit_eligible"),
        }
    holo_cfg = config_results.get("frontier_holo_v1", {})
    if holo_cfg.get("architecture_mode") != "patent_aligned_v4":
        errors.append("frontier_holo_v1 must use patent_aligned_v4")
    packet_results = []
    for item in entries:
        packet_dir = REPO_ROOT / item["packet_dir"]
        for rel in ["packet_lock.json", "freeze_manifest.json", "source_packet.json", "source_manifest.json", "contamination_scan_config.json", "validate_packet_no_provider.py"]:
            if not (packet_dir / rel).exists():
                errors.append(f"{item.get('domain_id')} missing {rel}")
        hash_checks = {
            "packet_hash": sha_file(packet_dir / "source_packet.json") if (packet_dir / "source_packet.json").exists() else None,
            "packet_lock_hash": sha_file(packet_dir / "packet_lock.json") if (packet_dir / "packet_lock.json").exists() else None,
            "freeze_manifest_hash": sha_file(packet_dir / "freeze_manifest.json") if (packet_dir / "freeze_manifest.json").exists() else None,
        }
        for key, actual in hash_checks.items():
            if actual and item.get(key) != actual:
                errors.append(f"{item.get('domain_id')} manifest {key} mismatch")
        validator_path = REPO_ROOT / item["validator_path"]
        validation = run_packet_validator(validator_path) if validator_path.exists() else {"status": "MISSING", "returncode": 1}
        if validation.get("returncode") != 0 or validation.get("provider_calls") != 0:
            errors.append(f"{item.get('domain_id')} packet validator failed or made provider calls")
        packet_results.append({
            "domain_id": item.get("domain_id"),
            "packet_id": item.get("packet_id"),
            "packet_hash": hash_checks["packet_hash"],
            "validation_status": validation.get("status"),
            "provider_calls": validation.get("provider_calls"),
            "validator_returncode": validation.get("returncode"),
        })
    output = {
        "status": "HOLOBUILD_TEN_DOMAIN_SUITE_READY_NO_PROVIDER" if not errors else "HOLOBUILD_TEN_DOMAIN_SUITE_VALIDATION_FAIL",
        "suite_manifest_path": repo_rel(MANIFEST_PATH),
        "suite_manifest_hash": sha_file(MANIFEST_PATH) if MANIFEST_PATH.exists() else None,
        "domain_count": len(entries),
        "packet_results": packet_results,
        "runner_path": repo_rel(RUNNER_PATH),
        "runner_hash": sha_file(RUNNER_PATH) if RUNNER_PATH.exists() else None,
        "scoring_lock_path": repo_rel(SCORING_LOCK),
        "scoring_lock_hash": sha_file(SCORING_LOCK) if SCORING_LOCK.exists() else None,
        "proof_holo_mode": "patent_aligned_v4",
        "legacy_holo_modes": {
            "diagnostic_v3": "diagnostic_only_no_proof_credit",
            "full_gov_v4": "diagnostic_only_no_proof_credit",
        },
        "configs": config_results,
        "provider_calls": 0,
        "artifact_generation": 0,
        "scoring": 0,
        "judging": 0,
        "unblinding": 0,
        "errors": errors,
    }
    print(json.dumps(output, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
