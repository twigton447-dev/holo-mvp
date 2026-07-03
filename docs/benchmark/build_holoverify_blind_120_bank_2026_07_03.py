#!/usr/bin/env python3
"""Build/freeze the 120-packet HoloVerify blind runtime bank.

No providers, judges, Holo runs, or solo runs occur here.

The package is split into:
- audit manifest: legacy packet IDs, domain allocation, validation;
- runtime manifest/payloads: opaque runtime IDs only;
- scoring map: opaque-to-truth map for post-freeze scoring only;
- hash manifest: file hashes and freeze root.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path("docs/benchmark")
SOURCE_BANK = BENCHMARK_ROOT / "holoverify_blind_canary_bank_2026_07_02.json"
PRIOR_CANARY_MANIFEST = BENCHMARK_ROOT / "holoverify_blind_canary_manifest_2026_07_02.json"
SEQUENCE_LOCK = BENCHMARK_ROOT / "HOLOVERIFY_BLIND_120_SEQUENCE_LOCK_2026_07_03.json"

OUT_DIR = BENCHMARK_ROOT / "holoverify_blind_120_bank_2026_07_03"
PAYLOAD_DIR = OUT_DIR / "runtime_payloads"
AUDIT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_BLIND_120_PACKET_BANK_FREEZE_2026_07_03.json"
AUDIT_MD = BENCHMARK_ROOT / "HOLOVERIFY_BLIND_120_PACKET_BANK_FREEZE_2026_07_03.md"
RUNTIME_JSON = OUT_DIR / "holoverify_blind_120_runtime_manifest_2026_07_03.json"
SCORING_JSON = OUT_DIR / "holoverify_blind_120_scoring_map_2026_07_03.json"
HASH_JSON = OUT_DIR / "holoverify_blind_120_hash_manifest_2026_07_03.json"

PACKET_TARGET = 120
PAIR_TARGET = 60
TRUTH_TARGET = {"ALLOW": 60, "ESCALATE": 60}
SELECTION_LABEL = "bank_hash_balanced_domain_pair_selection_no_author_seed"
FORBIDDEN_RUNTIME_PATTERNS = (
    r"\bHV-[A-Z]+-REP-\d{3}-[AB]\b",
    r"\bBAL100-[A-Z0-9-]+-[AB]\b",
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
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(errors="replace"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def packet_path_index() -> dict[str, Path]:
    out: dict[str, Path] = {}
    for path in BENCHMARK_ROOT.rglob("*.packet.json"):
        packet_id = path.name.removesuffix(".packet.json")
        out[packet_id] = path
    return out


def runtime_records(packet: dict[str, Any]) -> list[dict[str, str]]:
    visible = packet.get("model_visible_payload") or {}
    source_context = visible.get("source_context") or {}
    records = source_context.get("records") if isinstance(source_context, dict) else None
    if not isinstance(records, list):
        records = packet.get("source_control_facts") or []
    out: list[dict[str, str]] = []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        source_id = rec.get("source_id")
        content = rec.get("content")
        if not source_id or not content:
            continue
        out.append(
            {
                "doc_id": str(source_id),
                "text": str(content),
                "source_type": str(rec.get("source_type", "source_record")),
            }
        )
    return out


def runtime_payload(opaque_id: str, packet: dict[str, Any]) -> dict[str, Any]:
    visible = packet.get("model_visible_payload") or {}
    return {
        "packet_id": opaque_id,
        "domain": visible.get("domain") or packet.get("domain"),
        "case_ref": visible.get("case_ref"),
        "action_boundary": visible.get("action_boundary") or packet.get("action_boundary"),
        "communication_boundary": visible.get("communication_boundary") or packet.get("communication_boundary"),
        "documents": runtime_records(packet),
    }


def scan_runtime_text(path: Path, text: str) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for pattern in FORBIDDEN_RUNTIME_PATTERNS:
        if re.search(pattern, text, flags=re.I):
            hits.append({"path": str(path), "pattern": pattern})
    return hits


def load_available_pairs() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    bank = load_json(SOURCE_BANK)
    packet_paths = packet_path_index()
    prior_ids = set(load_json(PRIOR_CANARY_MANIFEST).get("packet_ids", []))

    rows_by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    missing: list[str] = []
    excluded_prior: list[str] = []
    for row in bank.get("rows", []):
        legacy_id = str(row["legacy_packet_id"])
        if legacy_id in prior_ids:
            excluded_prior.append(legacy_id)
            continue
        packet_path = packet_paths.get(legacy_id)
        if not packet_path:
            missing.append(legacy_id)
            continue
        packet = load_json(packet_path)
        pair_id = str(packet.get("pair_id") or legacy_id[:-2])
        truth = str(packet.get("packet_truth"))
        domain = str(packet.get("domain") or (packet.get("model_visible_payload") or {}).get("domain") or "UNKNOWN")
        rows_by_pair[pair_id].append(
            {
                "legacy_packet_id": legacy_id,
                "legacy_packet_ref": str(packet_path),
                "legacy_packet_sha256": sha256_file(packet_path),
                "truth": truth,
                "domain": domain,
                "first_turn_correct": bool(row.get("first_turn_correct")),
            }
        )

    complete_pairs: list[dict[str, Any]] = []
    for pair_id, rows in rows_by_pair.items():
        domains = {row["domain"] for row in rows}
        by_truth: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            by_truth[row["truth"]].append(row)
        if domains and len(domains) == 1 and by_truth.get("ALLOW") and by_truth.get("ESCALATE"):
            # One packet per truth side. If duplicate files exist, use stable ID order.
            allow = sorted(by_truth["ALLOW"], key=lambda row: row["legacy_packet_id"])[0]
            escalate = sorted(by_truth["ESCALATE"], key=lambda row: row["legacy_packet_id"])[0]
            complete_pairs.append(
                {
                    "pair_id": pair_id,
                    "domain": next(iter(domains)),
                    "packets": [allow, escalate],
                    "first_turn_correct_all": bool(allow["first_turn_correct"] and escalate["first_turn_correct"]),
                }
            )

    diagnostics = {
        "source_bank": str(SOURCE_BANK),
        "source_bank_sha256": sha256_file(SOURCE_BANK),
        "source_bank_hash": bank.get("bank_hash"),
        "source_bank_rows": len(bank.get("rows", [])),
        "prior_canary_manifest": str(PRIOR_CANARY_MANIFEST),
        "prior_canary_packet_ids_excluded": len(excluded_prior),
        "missing_packet_files": len(missing),
        "complete_balanced_pairs_available": len(complete_pairs),
    }
    return complete_pairs, diagnostics


def allocation_for_domains(pairs: list[dict[str, Any]], bank_hash: str) -> dict[str, int]:
    by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        by_domain[pair["domain"]].append(pair)
    quotas = {domain: 0 for domain in by_domain}
    while sum(quotas.values()) < PAIR_TARGET:
        eligible = [domain for domain, domain_pairs in by_domain.items() if quotas[domain] < len(domain_pairs)]
        if not eligible:
            raise RuntimeError("not enough complete domain pairs to fill 120-packet bank")
        eligible.sort(
            key=lambda domain: (
                quotas[domain],
                hashlib.sha256(f"{bank_hash}|domain|{domain}|{quotas[domain]}".encode("utf-8")).hexdigest(),
            )
        )
        quotas[eligible[0]] += 1
    return quotas


def select_pairs(pairs: list[dict[str, Any]], bank_hash: str) -> list[dict[str, Any]]:
    quotas = allocation_for_domains(pairs, bank_hash)
    by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        by_domain[pair["domain"]].append(pair)

    selected: list[dict[str, Any]] = []
    for domain, quota in quotas.items():
        domain_pairs = sorted(
            by_domain[domain],
            key=lambda pair: hashlib.sha256(f"{bank_hash}|blind120|pair|{pair['pair_id']}".encode("utf-8")).hexdigest(),
        )
        selected.extend(domain_pairs[:quota])
    return sorted(selected, key=lambda pair: (pair["domain"], pair["pair_id"]))


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    complete_pairs, diagnostics = load_available_pairs()
    bank_hash = str(diagnostics["source_bank_hash"])
    selected_pairs = select_pairs(complete_pairs, bank_hash)
    if len(selected_pairs) != PAIR_TARGET:
        raise RuntimeError(f"selected_pair_count_mismatch:{len(selected_pairs)}")

    salt = secrets.token_hex(32)
    runtime_rows: list[dict[str, str]] = []
    scoring_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    payload_hashes: list[dict[str, str]] = []

    PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for stale_payload in PAYLOAD_DIR.glob("BLIND120-*.json"):
        stale_payload.unlink()
    for pair in selected_pairs:
        for packet_row in sorted(pair["packets"], key=lambda row: row["truth"]):
            legacy_id = packet_row["legacy_packet_id"]
            opaque = "BLIND120-" + hashlib.sha256(f"{salt}|{legacy_id}".encode("utf-8")).hexdigest()[:20].upper()
            packet_path = Path(packet_row["legacy_packet_ref"])
            packet = load_json(packet_path)
            payload = runtime_payload(opaque, packet)
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
                    "legacy_packet_id": legacy_id,
                    "legacy_packet_ref": str(packet_path),
                    "legacy_packet_sha256": packet_row["legacy_packet_sha256"],
                    "legacy_truth": packet_row["truth"],
                    "domain": packet_row["domain"],
                    "pair_id": pair["pair_id"],
                }
            )
            audit_rows.append(
                {
                    "domain": packet_row["domain"],
                    "first_turn_correct": packet_row["first_turn_correct"],
                    "legacy_packet_id": legacy_id,
                    "legacy_packet_ref": str(packet_path),
                    "legacy_packet_sha256": packet_row["legacy_packet_sha256"],
                    "legacy_truth": packet_row["truth"],
                    "opaque_runtime_id": opaque,
                    "pair_id": pair["pair_id"],
                    "runtime_payload_ref": str(payload_path),
                    "runtime_payload_sha256": payload_hash,
                }
            )
            payload_hashes.append({"path": str(payload_path), "sha256": payload_hash})

    runtime_manifest = {
        "classification": "HOLOVERIFY_BLIND_120_RUNTIME_MANIFEST_NO_PROVIDER",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider_calls": 0,
        "judge_calls": 0,
        "runtime_consumable": True,
        "packet_count": len(runtime_rows),
        "packets": sorted(runtime_rows, key=lambda row: row["opaque_runtime_id"]),
        "runtime_field_policy": "opaque runtime payload refs only; no scoring map fields",
    }
    scoring_map = {
        "classification": "HOLOVERIFY_BLIND_120_POSTHOC_SCORING_MAP_NO_PROVIDER",
        "created_at_utc": runtime_manifest["created_at_utc"],
        "provider_calls": 0,
        "judge_calls": 0,
        "runtime_consumable": False,
        "packet_count": len(scoring_rows),
        "private_runtime_salt": salt,
        "scoring_rows": scoring_rows,
        "use_rule": "load only after live trace freeze",
    }

    truth_counts = Counter(row["legacy_truth"] for row in audit_rows)
    domain_counts = Counter(row["domain"] for row in audit_rows)
    domain_truth_counts = Counter((row["domain"], row["legacy_truth"]) for row in audit_rows)
    runtime_text_hits: list[dict[str, str]] = []
    runtime_text_hits.extend(
        scan_runtime_text(RUNTIME_JSON, json.dumps(runtime_manifest, sort_keys=True, ensure_ascii=True))
    )
    for path in [Path(row["runtime_payload_ref"]) for row in audit_rows]:
        runtime_text_hits.extend(scan_runtime_text(path, path.read_text(errors="replace")))

    audit_manifest = {
        "classification": "HOLOVERIFY_BLIND_120_PACKET_BANK_FREEZE_NO_PROVIDER",
        "created_at_utc": runtime_manifest["created_at_utc"],
        "provider_calls": 0,
        "judge_calls": 0,
        "sequence_lock": str(SEQUENCE_LOCK),
        "selection_label": SELECTION_LABEL,
        "selection_rule": "exclude prior 20-packet blind canary; allocate 60 sibling pairs across available domains by minimum quota then deterministic bank-hash tie break; select pairs within each domain by sha256(bank_hash|blind120|pair|pair_id)",
        "redraw_policy": "no redraws; any change requires a new freeze artifact",
        "claim_limit": "This freeze only prepares the blind runtime bank. It does not license provider execution or public claims.",
        "diagnostics": diagnostics,
        "pair_count": len(selected_pairs),
        "packet_count": len(audit_rows),
        "truth_counts": dict(sorted(truth_counts.items())),
        "domain_counts": dict(sorted(domain_counts.items())),
        "domain_truth_counts": {
            f"{domain}::{truth}": count
            for (domain, truth), count in sorted(domain_truth_counts.items())
        },
        "runtime_manifest": str(RUNTIME_JSON),
        "scoring_map": str(SCORING_JSON),
        "runtime_payload_dir": str(PAYLOAD_DIR),
        "runtime_leakage_hits": runtime_text_hits,
        "validation": {
            "packet_count_120": len(audit_rows) == PACKET_TARGET,
            "pair_count_60": len(selected_pairs) == PAIR_TARGET,
            "truth_balance": dict(truth_counts) == TRUTH_TARGET,
            "runtime_leakage_clean": not runtime_text_hits,
            "runtime_ids_unique": len({row["opaque_runtime_id"] for row in audit_rows}) == PACKET_TARGET,
            "runtime_manifest_separate_from_scoring_map": True,
            "provider_calls_zero": True,
            "judge_calls_zero": True,
        },
        "selected_rows": audit_rows,
    }
    return audit_manifest, runtime_manifest, scoring_map, {"payload_hashes": payload_hashes}


def write_md(audit: dict[str, Any], freeze_root: str) -> str:
    lines = [
        "# HoloVerify Blind 120 Packet Bank Freeze",
        "",
        "Status: `FROZEN_NO_PROVIDER_BANK`",
        "",
        f"Created: `{audit['created_at_utc']}`",
        "",
        "Provider calls made by this freeze: `0`",
        "",
        "Judge calls made by this freeze: `0`",
        "",
        f"Freeze root: `{freeze_root}`",
        "",
        "## Scope",
        "",
        f"- Pairs: `{audit['pair_count']}`",
        f"- Packets: `{audit['packet_count']}`",
        f"- Truth counts: `{audit['truth_counts']}`",
        f"- Domains: `{len(audit['domain_counts'])}`",
        "",
        "This is a build/freeze artifact only. It does not approve provider execution or public claims.",
        "",
        "## Validation",
        "",
    ]
    for key, value in audit["validation"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Domain Counts", "", "| Domain | Packets |", "| --- | ---: |"])
    for domain, count in audit["domain_counts"].items():
        lines.append(f"| {domain} | {count} |")
    lines.extend(["", "## Selected Legacy Rows", "", "| Legacy packet | Truth | Domain | Opaque runtime ID |", "| --- | --- | --- | --- |"])
    for row in audit["selected_rows"]:
        lines.append(
            f"| `{row['legacy_packet_id']}` | `{row['legacy_truth']}` | {row['domain']} | `{row['opaque_runtime_id']}` |"
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
        "classification": "HOLOVERIFY_BLIND_120_HASH_MANIFEST",
        "created_at_utc": audit["created_at_utc"],
        "files": sorted(files, key=lambda row: row["path"]),
    }
    freeze_root = sha256_text(json.dumps(hash_manifest_base, sort_keys=True))
    hash_manifest = {
        **hash_manifest_base,
        "freeze_root_sha256": freeze_root,
    }
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
