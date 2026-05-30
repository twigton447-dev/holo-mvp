"""
holo_builder/freeze.py

Freeze a Builder candidate that has passed QA Attacker review.

Precondition: QA Attacker final_classification == CLEAN_TO_FREEZE.

Steps:
  1. Extract payload (action + context) — the only thing Engine will see.
  2. Compute SHA-256 of canonical payload JSON (sort_keys=True).
  3. Stamp packet with _frozen metadata block (hash, qa_classification, frozen_at).
  4. Write frozen packet to holo_builder/outputs/frozen/<scenario_id>_<hash8>.json.
  5. Append ledger entry to holo_builder/outputs/ledger.jsonl.

The frozen packet is the artifact that goes to Engine blind adjudication.
Engine receives only the frozen packet payload — not the _frozen, _builder, or _internal blocks.

Usage:
  from holo_builder.freeze import freeze_packet
  frozen_path, pkg_hash = freeze_packet(packet, qa_result, original_packet_path)
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path


LEDGER_PATH = Path("holo_builder/outputs/ledger.jsonl")
FROZEN_DIR  = Path("holo_builder/outputs/frozen")


def _payload_hash(packet: dict) -> str:
    """SHA-256 of canonical payload JSON (action + context only, sort_keys=True)."""
    payload = packet.get("payload", {})
    canonical = {
        "action":  payload.get("action", {}),
        "context": payload.get("context", {}),
    }
    canonical_json = json.dumps(canonical, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def freeze_packet(packet: dict, qa_result: dict,
                  original_path: Path | None = None) -> tuple[Path, str]:
    """
    Freeze a packet after QA Attacker approval.

    Args:
      packet:        Full packet dict (including _builder, _internal, payload).
      qa_result:     QA Attacker result dict (must have final_classification=CLEAN_TO_FREEZE).
      original_path: Original packet file path (used only for logging).

    Returns:
      (frozen_path, sha256_hash)

    Raises:
      ValueError if QA classification is not CLEAN_TO_FREEZE.
    """
    classification = qa_result.get("final_classification", "")
    if classification != "CLEAN_TO_FREEZE":
        raise ValueError(
            f"Cannot freeze: QA classification is '{classification}', "
            f"must be CLEAN_TO_FREEZE."
        )

    pkg_hash = _payload_hash(packet)
    hash8    = pkg_hash[:8]
    scenario_id = packet.get("scenario_id", "unknown")
    frozen_at   = datetime.utcnow().isoformat() + "Z"

    # Stamp packet with _frozen block
    import copy
    frozen_packet = copy.deepcopy(packet)
    frozen_packet["_frozen"] = {
        "hash":              pkg_hash,
        "hash8":             hash8,
        "qa_classification": classification,
        "qa_id":             qa_result.get("qa_id", ""),
        "qa_turns":          qa_result.get("turns_completed", 0),
        "frozen_at":         frozen_at,
        "source_path":       str(original_path) if original_path else "",
    }
    frozen_packet["scenario_status"] = "frozen"

    # Write frozen packet
    FROZEN_DIR.mkdir(parents=True, exist_ok=True)
    frozen_path = FROZEN_DIR / f"{scenario_id}_{hash8}.json"
    frozen_path.write_text(json.dumps(frozen_packet, indent=2))

    # Append ledger entry
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    ledger_entry = {
        "scenario_id":       scenario_id,
        "hash":              pkg_hash,
        "hash8":             hash8,
        "qa_classification": classification,
        "qa_id":             qa_result.get("qa_id", ""),
        "frozen_at":         frozen_at,
        "frozen_path":       str(frozen_path),
        "source_path":       str(original_path) if original_path else "",
    }
    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(ledger_entry) + "\n")

    return frozen_path, pkg_hash
