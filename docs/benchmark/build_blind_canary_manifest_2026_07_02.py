"""Build a seeded no-provider blind canary package.

Outputs are split by use:

- audit manifest: legacy IDs for pre-registration and T5 skew checks.
- runtime manifest/payloads: opaque IDs and model-visible content only.
- scoring map: opaque-to-legacy mapping for post-run scoring only.

No providers, judges, or packet edits occur here.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from blind_lane_suite.canary_skew import bank_stats, skew_check


OUT_JSON = Path("docs/benchmark/holoverify_blind_canary_manifest_2026_07_02.json")
OUT_MD = Path("docs/benchmark/holoverify_blind_canary_manifest_2026_07_02.md")
RUNTIME_JSON = Path("docs/benchmark/holoverify_blind_canary_runtime_manifest_2026_07_02.json")
SCORING_JSON = Path("docs/benchmark/holoverify_blind_canary_scoring_map_2026_07_02.json")
RUNTIME_PAYLOAD_DIR = Path("docs/benchmark/holoverify_blind_canary_runtime_payloads_2026_07_02")
FROZEN_BANK = Path("docs/benchmark/holoverify_blind_canary_bank_2026_07_02.json")
SEED_LABEL = "derived_from_bank_hash_no_author_seed"


def _load_frozen_bank() -> tuple[dict[str, bool], str, dict]:
    data = json.loads(FROZEN_BANK.read_text(errors="replace"))
    rows = data.get("rows") or []
    first_turn = {
        str(row["legacy_packet_id"]): bool(row["first_turn_correct"])
        for row in rows
    }
    return first_turn, str(data["bank_hash"]), data


def _private_salt() -> str:
    # Generated once per package build and stored only in the post-hoc scoring map.
    return secrets.token_hex(32)


def _opaque_id(private_salt: str, legacy_id: str) -> str:
    digest = hashlib.sha256(f"{private_salt}|{legacy_id}".encode("utf-8")).hexdigest()[:16].upper()
    return f"BLIND-{digest}"


def _packet_file(legacy_id: str) -> Path:
    hits = sorted(Path("docs/benchmark").rglob(f"{legacy_id}.packet.json"))
    if not hits:
        raise FileNotFoundError(f"packet payload not found for {legacy_id}")
    return hits[0]


def _records_from_packet(packet: dict) -> list[dict]:
    visible = packet.get("model_visible_payload") or {}
    source_context = visible.get("source_context") or {}
    records = source_context.get("records") if isinstance(source_context, dict) else None
    if not isinstance(records, list):
        records = packet.get("source_control_facts") or []
    out = []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        sid = rec.get("source_id")
        content = rec.get("content")
        if sid and content:
            out.append(
                {
                    "doc_id": str(sid),
                    "text": str(content),
                    "source_type": str(rec.get("source_type", "source_record")),
                }
            )
    return out


def _runtime_payload(opaque_id: str, packet: dict) -> dict:
    visible = packet.get("model_visible_payload") or {}
    return {
        "packet_id": opaque_id,
        "action_boundary": visible.get("action_boundary") or packet.get("action_boundary"),
        "domain": visible.get("domain") or packet.get("domain"),
        "case_ref": visible.get("case_ref"),
        "documents": _records_from_packet(packet),
    }


def _paired_bank(first_turn: dict[str, bool]) -> list[str]:
    pairs = {}
    for pid in first_turn:
        if pid.endswith("-A") or pid.endswith("-B"):
            pairs.setdefault(pid[:-2], set()).add(pid[-1])
    return sorted(pair for pair, sides in pairs.items() if sides == {"A", "B"})


def _sample_pair_ids(pair_bank: list[str], bank_hash: str, count: int = 10) -> list[str]:
    keyed = sorted(
        (
            hashlib.sha256(f"{bank_hash}|pair|{pair}".encode("utf-8")).hexdigest(),
            pair,
        )
        for pair in pair_bank
    )
    return sorted(pair for _digest, pair in keyed[:count])


def build_package() -> tuple[dict, dict, dict]:
    first_turn, bank_hash, frozen_bank = _load_frozen_bank()
    pair_ids = _sample_pair_ids(_paired_bank(first_turn), bank_hash, 10)
    selected = sorted(side for pair in pair_ids for side in (f"{pair}-A", f"{pair}-B"))
    skew = skew_check(selected)
    salt = _private_salt()

    runtime_payloads = []
    scoring_rows = []
    for legacy_id in selected:
        opaque = _opaque_id(salt, legacy_id)
        packet_path = _packet_file(legacy_id)
        packet = json.loads(packet_path.read_text(errors="replace"))
        payload = _runtime_payload(opaque, packet)
        payload_ref = RUNTIME_PAYLOAD_DIR / f"{opaque}.json"
        runtime_payloads.append(
            {
                "opaque_runtime_id": opaque,
                "runtime_payload_ref": str(payload_ref),
            }
        )
        scoring_rows.append(
            {
                "opaque_runtime_id": opaque,
                "legacy_packet_id": legacy_id,
                "legacy_packet_ref": str(packet_path),
                "legacy_truth": packet.get("packet_truth"),
            }
        )
        payload_ref.parent.mkdir(parents=True, exist_ok=True)
        payload_ref.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    audit_base = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider_calls": 0,
        "judge_calls": 0,
        "seed_label": SEED_LABEL,
        "seed_material": "pinned_bank_hash",
        "bank_hash": bank_hash,
        "bank_ref": str(FROZEN_BANK),
        "selection_rule": "select first 10 sibling pairs by sha256(bank_hash|pair|pair_id); include both siblings",
        "redraw_policy": "no redraws allowed; if skew check fails, canary remains blocked",
        "redraw_log": [],
    }
    audit_manifest = {
        **audit_base,
        "classification": "HOLOVERIFY_BLIND_CANARY_AUDIT_MANIFEST_NO_PROVIDER",
        "runtime_consumable": False,
        "packet_count": len(selected),
        "pair_count": len(pair_ids),
        "legacy_allow_count": sum(1 for pid in selected if pid.endswith("-A")),
        "legacy_escalate_count": sum(1 for pid in selected if pid.endswith("-B")),
        "bank": {
            **bank_stats(first_turn),
            "legacy_pair_available": len(_paired_bank(first_turn)),
            "frozen_bank_stats": frozen_bank.get("bank_stats"),
        },
        "skew_check": skew,
        "pair_ids": sorted(pair_ids),
        "packet_ids": selected,
        "runtime_manifest": str(RUNTIME_JSON),
        "scoring_map": str(SCORING_JSON),
        "claim_limit": "This canary can test the blind runtime firewall only; it cannot support an error-rate claim.",
    }
    runtime_manifest = {
        "classification": "HOLOVERIFY_BLIND_CANARY_RUNTIME_MANIFEST_NO_PROVIDER",
        "created_at_utc": audit_base["created_at_utc"],
        "provider_calls": 0,
        "judge_calls": 0,
        "runtime_consumable": True,
        "packet_count": len(runtime_payloads),
        "packets": sorted(runtime_payloads, key=lambda row: row["opaque_runtime_id"]),
        "runtime_field_policy": "opaque runtime payload refs only; no scoring map fields",
    }
    scoring_map = {
        **audit_base,
        "classification": "HOLOVERIFY_BLIND_CANARY_POSTHOC_SCORING_MAP_NO_PROVIDER",
        "runtime_consumable": False,
        "packet_count": len(scoring_rows),
        "private_runtime_salt": salt,
        "scoring_rows": scoring_rows,
        "use_rule": "load only after live trace freeze",
    }
    return audit_manifest, runtime_manifest, scoring_map


def write_md(manifest: dict) -> str:
    lines = [
        "# HoloVerify Blind Canary Manifest",
        "",
        "Status: PRE_REGISTERED_NO_PROVIDER_SELECTION",
        "",
        f"Seed label: `{manifest['seed_label']}`",
        f"Bank hash seed: `{manifest['bank_hash']}`",
        "",
        f"Pairs: `{manifest['pair_count']}`",
        f"Packets: `{manifest['packet_count']}`",
        f"Legacy ALLOW-side IDs: `{manifest['legacy_allow_count']}`",
        f"Legacy ESCALATE-side IDs: `{manifest['legacy_escalate_count']}`",
        "",
        "Runtime rule: live runtime consumes the separate runtime manifest and opaque runtime payloads only. Legacy packet IDs and truths live only in the post-hoc scoring map.",
        "",
        "Redraw policy: no redraws are allowed. If skew check fails, the canary remains blocked.",
        "",
        "Claim limit: this canary can test the blind runtime firewall only. It cannot support an error-rate claim.",
        "",
        "## Skew Check",
        "",
        f"Bank first-turn rate: `{manifest['bank']['rate']}`",
        f"Sample first-turn rate: `{manifest['skew_check']['sample_rate']}`",
        f"One-sided binomial p-value: `{manifest['skew_check']['one_sided_binomial_p_value']}`",
        f"Skew violation: `{manifest['skew_check']['skew_violation']}`",
        "",
        "## Selected Legacy Packets",
        "",
        "| Legacy packet ID |",
        "| --- |",
    ]
    for pid in manifest["packet_ids"]:
        lines.append(f"| `{pid}` |")
    return "\n".join(lines) + "\n"


def main() -> int:
    audit_manifest, runtime_manifest, scoring_map = build_package()
    OUT_JSON.write_text(json.dumps(audit_manifest, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(write_md(audit_manifest))
    RUNTIME_JSON.write_text(json.dumps(runtime_manifest, indent=2, sort_keys=True) + "\n")
    SCORING_JSON.write_text(json.dumps(scoring_map, indent=2, sort_keys=True) + "\n")
    print(OUT_JSON)
    print(OUT_MD)
    print(RUNTIME_JSON)
    print(SCORING_JSON)
    if audit_manifest["skew_check"]["skew_violation"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
