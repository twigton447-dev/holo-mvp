#!/usr/bin/env python3
"""Build/freeze Solo Failure Factory Batch 002.

This is a no-provider build step. It creates a runtime-safe packet bank and a
separate post-hoc scoring map for a later solo scout.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path("docs/benchmark")
BATCH_ID = "BATCH002"
OPAQUE_PREFIX = "HVSF002"
DESIGN_JSON = BENCHMARK_ROOT / "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH002_DESIGN_2026_07_03.json"
OUT_DIR = BENCHMARK_ROOT / "holoverify_solo_failure_factory_batch002_2026_07_03"
PAYLOAD_DIR = OUT_DIR / "runtime_payloads"
RUNTIME_JSON = OUT_DIR / "holoverify_solo_failure_factory_batch002_runtime_manifest_2026_07_03.json"
SCORING_JSON = OUT_DIR / "holoverify_solo_failure_factory_batch002_scoring_map_2026_07_03.json"
HASH_JSON = OUT_DIR / "holoverify_solo_failure_factory_batch002_hash_manifest_2026_07_03.json"
AUDIT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH002_PACKET_FREEZE_2026_07_03.json"
AUDIT_MD = BENCHMARK_ROOT / "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH002_PACKET_FREEZE_2026_07_03.md"

EXPECTED_PAIRS = 10
EXPECTED_PACKETS = 20
EXPECTED_TRUTH_COUNTS = {"ALLOW": 10, "ESCALATE": 10}

FORBIDDEN_RUNTIME_PATTERNS = (
    r"packet_truth",
    r"legacy_truth",
    r"legacy_packet_id",
    r"deterministic_answer_key",
    r"answer_key",
    r"knew_terms",
    r"allow_rule",
    r"esc_rule",
    r"expected verdict",
    r"target_failure",
    r"tempting_wrong_move",
    r"hidden_dependency",
    r"single_delta",
    r"open_dependency",
    r"closed_control",
    r"\bALLOW\b",
    r"\bESCALATE\b",
    r"\bHVSF-FACTORY2-\d{3}-[AB]\b",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def runtime_payload(opaque_id: str, spec: dict[str, Any], suffix: str) -> dict[str, Any]:
    docs = spec["allow_docs"] if suffix == "A" else spec["esc_docs"]
    return {
        "packet_id": opaque_id,
        "domain": spec["domain"],
        "case_ref": opaque_id,
        "action_boundary": spec["action_boundary"],
        "communication_boundary": spec["communication_boundary"],
        "documents": [
            {"doc_id": str(source_id), "source_type": "source_record", "text": str(content)}
            for source_id, content in docs
        ],
    }


def scan_runtime_text(path: Path, text: str) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for pattern in FORBIDDEN_RUNTIME_PATTERNS:
        if re.search(pattern, text, flags=re.I):
            hits.append({"path": str(path), "pattern": pattern})
    return hits


def validate_design(design: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    pairs = design.get("pairs", [])
    if len(pairs) != EXPECTED_PAIRS:
        failures.append(f"expected_{EXPECTED_PAIRS}_pairs")
    pair_ids = [pair.get("pair_id") for pair in pairs]
    if len(pair_ids) != len(set(pair_ids)):
        failures.append("duplicate_pair_ids")
    for spec in pairs:
        for key in (
            "pair_id",
            "domain",
            "action_boundary",
            "communication_boundary",
            "target_failure_side",
            "seam_family",
            "failure_classes",
            "allow_docs",
            "esc_docs",
        ):
            if key not in spec:
                failures.append(f"missing_{spec.get('pair_id', 'UNKNOWN')}_{key}")
        if len(spec.get("allow_docs", [])) < 4 or len(spec.get("esc_docs", [])) < 4:
            failures.append(f"too_few_docs_{spec.get('pair_id', 'UNKNOWN')}")
    return failures


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    design = json.loads(DESIGN_JSON.read_text())
    design_failures = validate_design(design)
    salt = secrets.token_hex(32)
    created = datetime.now(timezone.utc).isoformat()
    runtime_rows: list[dict[str, str]] = []
    scoring_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    payload_hashes: list[dict[str, str]] = []

    PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for stale_payload in PAYLOAD_DIR.glob(f"{OPAQUE_PREFIX}-*.json"):
        stale_payload.unlink()

    for spec in design["pairs"]:
        for suffix, truth in (("A", "ALLOW"), ("B", "ESCALATE")):
            legacy_packet_id = f"{spec['pair_id']}-{suffix}"
            opaque = OPAQUE_PREFIX + "-" + hashlib.sha256(f"{salt}|{legacy_packet_id}".encode("utf-8")).hexdigest()[:20].upper()
            payload = runtime_payload(opaque, spec, suffix)
            payload_path = PAYLOAD_DIR / f"{opaque}.json"
            write_json(payload_path, payload)
            payload_hash = sha256_file(payload_path)
            runtime_rows.append({"opaque_runtime_id": opaque, "runtime_payload_ref": str(payload_path)})
            scoring_rows.append(
                {
                    "opaque_runtime_id": opaque,
                    "legacy_packet_id": legacy_packet_id,
                    "legacy_truth": truth,
                    "pair_id": spec["pair_id"],
                    "sibling": suffix,
                    "domain": spec["domain"],
                    "target_failure_side": spec["target_failure_side"],
                    "seam_family": spec["seam_family"],
                    "failure_classes": spec["failure_classes"],
                }
            )
            audit_rows.append(
                {
                    "legacy_packet_id": legacy_packet_id,
                    "legacy_truth": truth,
                    "pair_id": spec["pair_id"],
                    "sibling": suffix,
                    "domain": spec["domain"],
                    "opaque_runtime_id": opaque,
                    "runtime_payload_ref": str(payload_path),
                    "runtime_payload_sha256": payload_hash,
                    "target_failure_side": spec["target_failure_side"],
                    "seam_family": spec["seam_family"],
                    "failure_classes": spec["failure_classes"],
                }
            )
            payload_hashes.append({"path": str(payload_path), "sha256": payload_hash})

    runtime_manifest = {
        "classification": "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH002_RUNTIME_MANIFEST_NO_PROVIDER",
        "created_at_utc": created,
        "provider_calls": 0,
        "solo_calls": 0,
        "holo_calls": 0,
        "gov_calls": 0,
        "judge_calls": 0,
        "runtime_consumable": True,
        "packet_count": len(runtime_rows),
        "packets": sorted(runtime_rows, key=lambda row: row["opaque_runtime_id"]),
        "runtime_field_policy": "opaque runtime payload refs only; no scoring map fields",
    }
    scoring_map = {
        "classification": "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH002_POSTHOC_SCORING_MAP_NO_PROVIDER",
        "created_at_utc": created,
        "provider_calls": 0,
        "solo_calls": 0,
        "holo_calls": 0,
        "gov_calls": 0,
        "judge_calls": 0,
        "runtime_consumable": False,
        "packet_count": len(scoring_rows),
        "private_runtime_salt": salt,
        "scoring_rows": scoring_rows,
        "use_rule": "load only after live solo trace freeze",
    }

    runtime_text_hits: list[dict[str, str]] = []
    runtime_text_hits.extend(scan_runtime_text(RUNTIME_JSON, json.dumps(runtime_manifest, sort_keys=True, ensure_ascii=True)))
    for row in audit_rows:
        path = Path(row["runtime_payload_ref"])
        runtime_text_hits.extend(scan_runtime_text(path, path.read_text(errors="replace")))

    truth_counts = Counter(row["legacy_truth"] for row in audit_rows)
    target_side_counts = Counter(row["target_failure_side"] for row in audit_rows if row["sibling"] == "A")
    audit_manifest = {
        "classification": "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH002_PACKET_FREEZE_NO_PROVIDER",
        "created_at_utc": created,
        "source_design": str(DESIGN_JSON),
        "claim_limit": "Solo-failure discovery only. No benchmark credit. No Holo run. No public claim.",
        "provider_calls": 0,
        "solo_calls": 0,
        "holo_calls": 0,
        "gov_calls": 0,
        "judge_calls": 0,
        "pair_count": len(design["pairs"]),
        "packet_count": len(audit_rows),
        "expected_solo_provider_calls": len(audit_rows) * 3,
        "truth_counts": dict(sorted(truth_counts.items())),
        "target_failure_side_counts": dict(sorted(target_side_counts.items())),
        "runtime_manifest": str(RUNTIME_JSON),
        "scoring_map": str(SCORING_JSON),
        "runtime_payload_dir": str(PAYLOAD_DIR),
        "runtime_leakage_hits": runtime_text_hits,
        "selected_rows": audit_rows,
        "validation": {
            "design_json_parse": bool(design.get("classification")),
            "design_schema": not design_failures,
            "pair_count_10": len(design["pairs"]) == EXPECTED_PAIRS,
            "packet_count_20": len(audit_rows) == EXPECTED_PACKETS,
            "truth_balance": dict(truth_counts) == EXPECTED_TRUTH_COUNTS,
            "target_failure_side_has_allow": target_side_counts.get("ALLOW", 0) > 0,
            "target_failure_side_has_escalate": target_side_counts.get("ESCALATE", 0) > 0,
            "runtime_leakage_clean": not runtime_text_hits,
            "runtime_ids_unique": len({row["opaque_runtime_id"] for row in audit_rows}) == EXPECTED_PACKETS,
            "runtime_manifest_separate_from_scoring_map": True,
            "provider_calls_zero": True,
            "solo_calls_zero": True,
            "holo_calls_zero": True,
            "gov_calls_zero": True,
            "judge_calls_zero": True,
        },
        "design_validation_failures": design_failures,
    }
    return audit_manifest, runtime_manifest, scoring_map, {"payload_hashes": payload_hashes}


def write_md(audit: dict[str, Any], freeze_root: str) -> str:
    lines = [
        "# HoloVerify Solo Failure Factory Batch 002 Packet Freeze",
        "",
        "Status: `FROZEN_NO_PROVIDER_SOLO_SCOUT_BANK`",
        "",
        f"Created: `{audit['created_at_utc']}`",
        "",
        "Provider / Solo / Holo / Gov / Judge calls made by this freeze: `0 / 0 / 0 / 0 / 0`",
        "",
        f"Freeze root: `{freeze_root}`",
        "",
        "## Scope",
        "",
        f"- Pairs: `{audit['pair_count']}`",
        f"- Packets: `{audit['packet_count']}`",
        f"- Truth counts: `{audit['truth_counts']}`",
        f"- Target failure side counts: `{audit['target_failure_side_counts']}`",
        f"- Expected solo provider calls if approved later: `{audit['expected_solo_provider_calls']}`",
        "",
        "This bank is for solo-failure discovery only. It does not approve provider execution, Holo execution, scoring claims, or public claims.",
        "",
        "## Validation",
        "",
    ]
    for key, value in audit["validation"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Selected Rows",
            "",
            "| Legacy packet | Truth | Target side | Opaque runtime ID | Seam family |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in audit["selected_rows"]:
        lines.append(
            f"| `{row['legacy_packet_id']}` | `{row['legacy_truth']}` | `{row['target_failure_side']}` | `{row['opaque_runtime_id']}` | {row['seam_family']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    audit, runtime_manifest, scoring_map, aux = build()
    write_json(RUNTIME_JSON, runtime_manifest)
    write_json(SCORING_JSON, scoring_map)
    files = [
        {"path": str(RUNTIME_JSON), "sha256": sha256_file(RUNTIME_JSON)},
        {"path": str(SCORING_JSON), "sha256": sha256_file(SCORING_JSON)},
        *aux["payload_hashes"],
    ]
    hash_manifest_base = {
        "classification": "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH002_HASH_MANIFEST",
        "created_at_utc": audit["created_at_utc"],
        "files": sorted(files, key=lambda row: row["path"]),
    }
    freeze_root = sha256_text(json.dumps(hash_manifest_base, sort_keys=True))
    hash_manifest = {**hash_manifest_base, "freeze_root_sha256": freeze_root}
    write_json(HASH_JSON, hash_manifest)
    audit["hash_manifest"] = str(HASH_JSON)
    audit["freeze_root_sha256"] = freeze_root
    write_json(AUDIT_JSON, audit)
    write_text(AUDIT_MD, write_md(audit, freeze_root))
    if not all(audit["validation"].values()):
        print(json.dumps(audit["validation"], indent=2, sort_keys=True))
        if audit.get("runtime_leakage_hits"):
            print(json.dumps(audit["runtime_leakage_hits"][:10], indent=2, sort_keys=True))
        return 1
    print(json.dumps({"freeze_root_sha256": freeze_root, "packets": audit["packet_count"], "pairs": audit["pair_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
