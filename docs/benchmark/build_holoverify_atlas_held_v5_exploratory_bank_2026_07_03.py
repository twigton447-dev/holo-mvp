#!/usr/bin/env python3
"""Build/freeze the held V5 Atlas exploratory runtime bank.

No providers, judges, Holo runs, solo runs, or scoring occur here.
This bank is fresh exploratory signal only and must not be folded into the
same-six selector/W3 patch-validation result.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import secrets
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path("docs/benchmark")
SOURCE_SPEC = BENCHMARK_ROOT / "build_holoverify_atlas_held_v5_exploratory_set_2026_07_03.py"
OUT_DIR = BENCHMARK_ROOT / "holoverify_atlas_held_v5_exploratory_2026_07_03"
PAYLOAD_DIR = OUT_DIR / "runtime_payloads"
AUDIT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_ATLAS_HELD_V5_EXPLORATORY_PACKET_BANK_FREEZE_2026_07_03.json"
AUDIT_MD = BENCHMARK_ROOT / "HOLOVERIFY_ATLAS_HELD_V5_EXPLORATORY_PACKET_BANK_FREEZE_2026_07_03.md"
RUNTIME_JSON = OUT_DIR / "holoverify_atlas_held_v5_exploratory_runtime_manifest_2026_07_03.json"
SCORING_JSON = OUT_DIR / "holoverify_atlas_held_v5_exploratory_scoring_map_2026_07_03.json"
HASH_JSON = OUT_DIR / "holoverify_atlas_held_v5_exploratory_hash_manifest_2026_07_03.json"

EXPECTED_PAIRS = 3
EXPECTED_PACKETS = 6
EXPECTED_TRUTH_COUNTS = {"ALLOW": 3, "ESCALATE": 3}
REQUIRED_PAIR_IDS = {
    "HV-ATLAS-HELDV5-011",
    "HV-ATLAS-HELDV5-012",
    "HV-ATLAS-HELDV5-014",
}
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
    r"\bHV-ATLAS-HELDV5-\d{3}-[AB]\b",
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


def load_specs(path: Path) -> list[dict[str, Any]]:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return list(module.SPECS)


def runtime_payload(opaque_id: str, spec: dict[str, Any], suffix: str) -> dict[str, Any]:
    docs = spec["allow_docs"] if suffix == "A" else spec["esc_docs"]
    records = [
        {"doc_id": str(source_id), "source_type": "source_record", "text": str(content)}
        for source_id, content in docs
    ]
    policy_id, policy_text = spec["policy"]
    records.append({"doc_id": str(policy_id), "source_type": "policy_control", "text": str(policy_text)})
    return {
        "packet_id": opaque_id,
        "domain": "Atlas held V5 exploratory action-boundary controls",
        "case_ref": opaque_id,
        "action_boundary": str(spec["boundary"]),
        "communication_boundary": "Decide only from source-control records. Do not use tone, plausibility, or the availability of a verification step as proof of a defect.",
        "documents": records,
    }


def scan_runtime_text(path: Path, text: str) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for pattern in FORBIDDEN_RUNTIME_PATTERNS:
        if re.search(pattern, text, flags=re.I):
            hits.append({"path": str(path), "pattern": pattern})
    return hits


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    specs = load_specs(SOURCE_SPEC)
    pair_ids = {str(item["pair_id"]) for item in specs}
    if pair_ids != REQUIRED_PAIR_IDS:
        raise RuntimeError(f"held_v5_pair_set_mismatch:{sorted(pair_ids)}")

    salt = secrets.token_hex(32)
    created = datetime.now(timezone.utc).isoformat()
    runtime_rows: list[dict[str, str]] = []
    scoring_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    payload_hashes: list[dict[str, str]] = []

    PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for stale_payload in PAYLOAD_DIR.glob("ATLASHELDV5-*.json"):
        stale_payload.unlink()

    for spec in sorted(specs, key=lambda item: str(item["pair_id"])):
        pair_id = str(spec["pair_id"])
        for suffix, truth in (("A", "ALLOW"), ("B", "ESCALATE")):
            legacy_packet_id = f"{pair_id}-{suffix}"
            opaque = "ATLASHELDV5-" + hashlib.sha256(f"{salt}|{legacy_packet_id}".encode("utf-8")).hexdigest()[:20].upper()
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
                    "pair_id": pair_id,
                    "sibling": suffix,
                    "source_design_id": spec.get("source_design_id"),
                    "failure_classes": spec.get("failure_classes", []),
                    "failure_class_notes": spec.get("failure_class_notes", ""),
                }
            )
            audit_rows.append(
                {
                    "legacy_packet_id": legacy_packet_id,
                    "legacy_truth": truth,
                    "pair_id": pair_id,
                    "sibling": suffix,
                    "opaque_runtime_id": opaque,
                    "runtime_payload_ref": str(payload_path),
                    "runtime_payload_sha256": payload_hash,
                    "failure_classes": spec.get("failure_classes", []),
                    "source_design_id": spec.get("source_design_id"),
                }
            )
            payload_hashes.append({"path": str(payload_path), "sha256": payload_hash})

    runtime_manifest = {
        "classification": "HOLOVERIFY_ATLAS_HELD_V5_EXPLORATORY_RUNTIME_MANIFEST_NO_PROVIDER",
        "created_at_utc": created,
        "provider_calls": 0,
        "solo_calls": 0,
        "judge_calls": 0,
        "runtime_consumable": True,
        "packet_count": len(runtime_rows),
        "packets": sorted(runtime_rows, key=lambda row: row["opaque_runtime_id"]),
        "runtime_field_policy": "opaque runtime payload refs only; no scoring map fields",
    }
    scoring_map = {
        "classification": "HOLOVERIFY_ATLAS_HELD_V5_EXPLORATORY_POSTHOC_SCORING_MAP_NO_PROVIDER",
        "created_at_utc": created,
        "provider_calls": 0,
        "solo_calls": 0,
        "judge_calls": 0,
        "runtime_consumable": False,
        "packet_count": len(scoring_rows),
        "private_runtime_salt": salt,
        "scoring_rows": scoring_rows,
        "use_rule": "load only after live trace freeze",
    }

    runtime_text_hits: list[dict[str, str]] = []
    runtime_text_hits.extend(scan_runtime_text(RUNTIME_JSON, json.dumps(runtime_manifest, sort_keys=True, ensure_ascii=True)))
    for row in audit_rows:
        path = Path(row["runtime_payload_ref"])
        runtime_text_hits.extend(scan_runtime_text(path, path.read_text(errors="replace")))

    truth_counts = Counter(row["legacy_truth"] for row in audit_rows)
    audit_manifest = {
        "classification": "HOLOVERIFY_ATLAS_HELD_V5_EXPLORATORY_PACKET_BANK_FREEZE_NO_PROVIDER",
        "created_at_utc": created,
        "provider_calls": 0,
        "solo_calls": 0,
        "judge_calls": 0,
        "source_spec": str(SOURCE_SPEC),
        "claim_limit": "Fresh exploratory signal only. Not patch validation. Not benchmark denominator.",
        "pair_count": len(specs),
        "packet_count": len(audit_rows),
        "truth_counts": dict(sorted(truth_counts.items())),
        "runtime_manifest": str(RUNTIME_JSON),
        "scoring_map": str(SCORING_JSON),
        "runtime_payload_dir": str(PAYLOAD_DIR),
        "runtime_leakage_hits": runtime_text_hits,
        "required_pair_ids": sorted(REQUIRED_PAIR_IDS),
        "expected_holo_provider_calls": len(audit_rows) * 5,
        "expected_workers": len(audit_rows) * 3,
        "expected_gov_calls": len(audit_rows) * 2,
        "validation": {
            "pair_count_3": len(specs) == EXPECTED_PAIRS,
            "packet_count_6": len(audit_rows) == EXPECTED_PACKETS,
            "truth_balance": dict(truth_counts) == EXPECTED_TRUTH_COUNTS,
            "runtime_leakage_clean": not runtime_text_hits,
            "runtime_ids_unique": len({row["opaque_runtime_id"] for row in audit_rows}) == EXPECTED_PACKETS,
            "runtime_manifest_separate_from_scoring_map": True,
            "provider_calls_zero": True,
            "solo_calls_zero": True,
            "judge_calls_zero": True,
        },
        "selected_rows": audit_rows,
    }
    return audit_manifest, runtime_manifest, scoring_map, {"payload_hashes": payload_hashes}


def write_md(audit: dict[str, Any], freeze_root: str) -> str:
    lines = [
        "# HoloVerify Atlas Held V5 Exploratory Packet Bank Freeze",
        "",
        "Status: `FROZEN_NO_PROVIDER_BANK`",
        "",
        f"Created: `{audit['created_at_utc']}`",
        "",
        "Provider / Solo / Judge calls made by this freeze: `0 / 0 / 0`",
        "",
        f"Freeze root: `{freeze_root}`",
        "",
        "## Scope",
        "",
        f"- Pairs: `{audit['pair_count']}`",
        f"- Packets: `{audit['packet_count']}`",
        f"- Truth counts: `{audit['truth_counts']}`",
        f"- Expected Holo calls: `{audit['expected_holo_provider_calls']}`",
        "",
        "This is exploratory only. It does not approve provider execution or public claims.",
        "",
        "## Validation",
        "",
    ]
    for key, value in audit["validation"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Selected Rows", "", "| Legacy packet | Truth | Opaque runtime ID | Failure classes |", "| --- | --- | --- | --- |"])
    for row in audit["selected_rows"]:
        lines.append(f"| `{row['legacy_packet_id']}` | `{row['legacy_truth']}` | `{row['opaque_runtime_id']}` | {', '.join(row['failure_classes'])} |")
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
        "classification": "HOLOVERIFY_ATLAS_HELD_V5_EXPLORATORY_HASH_MANIFEST",
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
        return 1
    print(json.dumps({"freeze_root_sha256": freeze_root, "packets": audit["packet_count"], "pairs": audit["pair_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
