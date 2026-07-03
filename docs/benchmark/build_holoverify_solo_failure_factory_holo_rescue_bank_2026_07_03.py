#!/usr/bin/env python3
"""Build/freeze the 13-pair Holo rescue runtime bank.

No providers, judges, Holo runs, solo runs, or scoring occur here.

This bank is intentionally directional evidence only:
- the pair set comes from solo-scout seam discovery and Fable review;
- both siblings per pair must be scored after trace freeze;
- truth stays in the scoring map and never in the runtime manifest.
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
SHORTLIST_JSON = BENCHMARK_ROOT / "HOLOVERIFY_SOLO_FAILURE_FACTORY_HOLO_RESCUE_SHORTLIST_2026_07_03.json"
OUT_DIR = BENCHMARK_ROOT / "holoverify_solo_failure_factory_holo_rescue_2026_07_03"
PAYLOAD_DIR = OUT_DIR / "runtime_payloads"
AUDIT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_SOLO_FAILURE_FACTORY_HOLO_RESCUE_PACKET_BANK_FREEZE_2026_07_03.json"
AUDIT_MD = BENCHMARK_ROOT / "HOLOVERIFY_SOLO_FAILURE_FACTORY_HOLO_RESCUE_PACKET_BANK_FREEZE_2026_07_03.md"
RUNTIME_JSON = OUT_DIR / "holoverify_solo_failure_factory_holo_rescue_runtime_manifest_2026_07_03.json"
SCORING_JSON = OUT_DIR / "holoverify_solo_failure_factory_holo_rescue_scoring_map_2026_07_03.json"
HASH_JSON = OUT_DIR / "holoverify_solo_failure_factory_holo_rescue_hash_manifest_2026_07_03.json"

EXPECTED_PAIRS = 13
EXPECTED_PACKETS = 26
EXPECTED_TRUTH_COUNTS = {"ALLOW": 13, "ESCALATE": 13}
REQUIRED_PAIR_IDS = {
    "HVSF-FACTORY-001",
    "HVSF-FACTORY-009",
    "HVSF-FACTORY-010",
    "HVSF-FACTORY2-005",
    "HVSF-FACTORY2-006",
    "HVSF-FACTORY3-004",
    "HVSF-FACTORY3-006",
    "HVSF-FACTORY3-007",
    "HVSF-FACTORY3-008",
    "HVSF-FACTORY4-004",
    "HVSF-FACTORY4-007",
    "HVSF-FACTORY4-008",
    "HVSF-FACTORY4-010",
}
BATCH_ROOTS = {
    "BATCH001": BENCHMARK_ROOT / "holoverify_solo_failure_factory_batch001_2026_07_03",
    "BATCH002": BENCHMARK_ROOT / "holoverify_solo_failure_factory_batch002_2026_07_03",
    "BATCH003": BENCHMARK_ROOT / "holoverify_solo_failure_factory_batch003_2026_07_03",
    "BATCH004": BENCHMARK_ROOT / "holoverify_solo_failure_factory_batch004_2026_07_03",
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
    r"target_bucket",
    r"target_sibling",
    r"expected verdict",
    r"\bHVSF-FACTORY\d*-\d{3}-[AB]\b",
    r"\bHVSF00[1-4]-[0-9A-F]{20}\b",
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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(errors="replace"))


def source_batch_for_pair(pair_id: str) -> str:
    if pair_id.startswith("HVSF-FACTORY4-"):
        return "BATCH004"
    if pair_id.startswith("HVSF-FACTORY3-"):
        return "BATCH003"
    if pair_id.startswith("HVSF-FACTORY2-"):
        return "BATCH002"
    if pair_id.startswith("HVSF-FACTORY-"):
        return "BATCH001"
    raise ValueError(f"unknown pair namespace: {pair_id}")


def load_batch_index() -> dict[tuple[str, str], dict[str, Any]]:
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    for batch_id, root in BATCH_ROOTS.items():
        scoring_path = next(root.glob("*scoring_map*.json"))
        runtime_path = next(root.glob("*runtime_manifest*.json"))
        runtime = load_json(runtime_path)
        payload_ref_by_opaque = {
            row["opaque_runtime_id"]: row["runtime_payload_ref"]
            for row in runtime.get("packets", [])
        }
        scoring = load_json(scoring_path)
        for row in scoring.get("scoring_rows", []):
            pair_id = str(row["pair_id"])
            sibling = str(row["sibling"])
            source_opaque = str(row["opaque_runtime_id"])
            payload_ref = payload_ref_by_opaque[source_opaque]
            indexed[(pair_id, sibling)] = {
                "batch_id": batch_id,
                "scoring_row": row,
                "runtime_payload_ref": payload_ref,
                "runtime_payload_sha256": sha256_file(Path(payload_ref)),
                "source_runtime_manifest": str(runtime_path),
                "source_scoring_map": str(scoring_path),
            }
    return indexed


def load_shortlist_pair_ids() -> list[str]:
    shortlist = load_json(SHORTLIST_JSON)
    pair_ids = [str(row["pair_id"]) for row in shortlist["primary_wrong_verdict_shortlist"]]
    if set(pair_ids) != REQUIRED_PAIR_IDS:
        raise RuntimeError(f"shortlist_pair_set_mismatch:{sorted(pair_ids)}")
    return pair_ids


def runtime_payload(opaque_id: str, source_payload: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(json.dumps(source_payload, sort_keys=True))
    payload["packet_id"] = opaque_id
    payload["case_ref"] = opaque_id
    return payload


def scan_runtime_text(path: Path, text: str) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for pattern in FORBIDDEN_RUNTIME_PATTERNS:
        if re.search(pattern, text, flags=re.I):
            hits.append({"path": str(path), "pattern": pattern})
    return hits


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    pair_ids = load_shortlist_pair_ids()
    source_index = load_batch_index()
    if set(pair_ids) != REQUIRED_PAIR_IDS:
        raise RuntimeError(f"promotion_pair_set_mismatch:{sorted(pair_ids)}")

    salt = secrets.token_hex(32)
    created = datetime.now(timezone.utc).isoformat()
    runtime_rows: list[dict[str, str]] = []
    scoring_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    payload_hashes: list[dict[str, str]] = []

    PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for stale_payload in PAYLOAD_DIR.glob("SFFRESCUE-*.json"):
        stale_payload.unlink()

    for pair_id in sorted(pair_ids):
        expected_batch_id = source_batch_for_pair(pair_id)
        for suffix, truth in (("A", "ALLOW"), ("B", "ESCALATE")):
            legacy_packet_id = f"{pair_id}-{suffix}"
            source = source_index[(pair_id, suffix)]
            if source["batch_id"] != expected_batch_id:
                raise RuntimeError(f"source_batch_mismatch:{pair_id}:{source['batch_id']}:{expected_batch_id}")
            source_scoring = source["scoring_row"]
            source_payload = load_json(Path(source["runtime_payload_ref"]))
            opaque = "SFFRESCUE-" + hashlib.sha256(f"{salt}|{legacy_packet_id}".encode("utf-8")).hexdigest()[:20].upper()
            payload = runtime_payload(opaque, source_payload)
            payload_path = PAYLOAD_DIR / f"{opaque}.json"
            write_json(payload_path, payload)
            payload_hash = sha256_file(payload_path)
            runtime_rows.append(
                {
                    "opaque_runtime_id": opaque,
                    "runtime_payload_ref": str(payload_path),
                }
            )
            scoring_rows.append(
                {
                    "opaque_runtime_id": opaque,
                    "legacy_packet_id": legacy_packet_id,
                    "legacy_truth": truth,
                    "pair_id": pair_id,
                    "sibling": suffix,
                    "source_batch": source["batch_id"],
                    "source_opaque_runtime_id": source_scoring["opaque_runtime_id"],
                    "source_domain": source_scoring.get("domain"),
                    "target_failure_side": source_scoring.get("target_failure_side"),
                    "seam_family": source_scoring.get("seam_family"),
                    "failure_classes": source_scoring.get("failure_classes", []),
                }
            )
            audit_rows.append(
                {
                    "legacy_packet_id": legacy_packet_id,
                    "legacy_truth": truth,
                    "pair_id": pair_id,
                    "sibling": suffix,
                    "source_batch": source["batch_id"],
                    "source_opaque_runtime_id": source_scoring["opaque_runtime_id"],
                    "source_runtime_payload_ref": source["runtime_payload_ref"],
                    "source_runtime_payload_sha256": source["runtime_payload_sha256"],
                    "source_domain": source_scoring.get("domain"),
                    "target_failure_side": source_scoring.get("target_failure_side"),
                    "seam_family": source_scoring.get("seam_family"),
                    "opaque_runtime_id": opaque,
                    "runtime_payload_ref": str(payload_path),
                    "runtime_payload_sha256": payload_hash,
                    "failure_classes": source_scoring.get("failure_classes", []),
                }
            )
            payload_hashes.append({"path": str(payload_path), "sha256": payload_hash})

    runtime_manifest = {
        "classification": "HOLOVERIFY_SOLO_FAILURE_FACTORY_HOLO_RESCUE_RUNTIME_MANIFEST_NO_PROVIDER",
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
        "classification": "HOLOVERIFY_SOLO_FAILURE_FACTORY_HOLO_RESCUE_POSTHOC_SCORING_MAP_NO_PROVIDER",
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
        "use_rule": "load only after live trace freeze",
    }

    runtime_text_hits: list[dict[str, str]] = []
    runtime_text_hits.extend(scan_runtime_text(RUNTIME_JSON, json.dumps(runtime_manifest, sort_keys=True, ensure_ascii=True)))
    for row in audit_rows:
        path = Path(row["runtime_payload_ref"])
        runtime_text_hits.extend(scan_runtime_text(path, path.read_text(errors="replace")))

    truth_counts = Counter(row["legacy_truth"] for row in audit_rows)
    audit_manifest = {
        "classification": "HOLOVERIFY_SOLO_FAILURE_FACTORY_HOLO_RESCUE_PACKET_BANK_FREEZE_NO_PROVIDER",
        "created_at_utc": created,
        "provider_calls": 0,
        "solo_calls": 0,
        "holo_calls": 0,
        "gov_calls": 0,
        "judge_calls": 0,
        "source_shortlist": str(SHORTLIST_JSON),
        "source_batches": {key: str(value) for key, value in BATCH_ROOTS.items()},
        "claim_limit": "Directional governance rescue evidence only. Not a public error-rate claim.",
        "pair_count": len(pair_ids),
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
            "pair_count_13": len(pair_ids) == EXPECTED_PAIRS,
            "packet_count_26": len(audit_rows) == EXPECTED_PACKETS,
            "truth_balance": dict(truth_counts) == EXPECTED_TRUTH_COUNTS,
            "runtime_leakage_clean": not runtime_text_hits,
            "runtime_ids_unique": len({row["opaque_runtime_id"] for row in audit_rows}) == EXPECTED_PACKETS,
            "runtime_manifest_separate_from_scoring_map": True,
            "source_payloads_rekeyed": all(row["opaque_runtime_id"] != row["source_opaque_runtime_id"] for row in audit_rows),
            "selected_from_primary_wrong_verdict_shortlist": set(pair_ids) == REQUIRED_PAIR_IDS,
            "provider_calls_zero": True,
            "solo_calls_zero": True,
            "holo_calls_zero": True,
            "gov_calls_zero": True,
            "judge_calls_zero": True,
        },
        "selected_rows": audit_rows,
    }
    return audit_manifest, runtime_manifest, scoring_map, {"payload_hashes": payload_hashes}


def write_md(audit: dict[str, Any], freeze_root: str) -> str:
    lines = [
        "# HoloVerify Solo Failure Factory Holo Rescue Packet Bank Freeze",
        "",
        "Status: `FROZEN_NO_PROVIDER_BANK`",
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
        f"- Expected Holo calls: `{audit['expected_holo_provider_calls']}`",
        f"- Expected worker/Gov split: `{audit['expected_workers']} / {audit['expected_gov_calls']}`",
        f"- Source shortlist: `{audit['source_shortlist']}`",
        "",
        "This is a build/freeze artifact only. It re-keys frozen Batch001-Batch004 payloads from the P1 wrong-verdict shortlist. It does not approve provider execution or public claims.",
        "",
        "## Validation",
        "",
    ]
    for key, value in audit["validation"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Selected Rows", "", "| Legacy packet | Truth | Source batch | Domain | Opaque runtime ID | Seam family |", "| --- | --- | --- | --- | --- | --- |"])
    for row in audit["selected_rows"]:
        lines.append(
            f"| `{row['legacy_packet_id']}` | `{row['legacy_truth']}` | `{row['source_batch']}` | {row['source_domain']} | `{row['opaque_runtime_id']}` | {row['seam_family']} |"
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
        "classification": "HOLOVERIFY_SOLO_FAILURE_FACTORY_HOLO_RESCUE_HASH_MANIFEST",
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
