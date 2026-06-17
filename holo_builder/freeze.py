"""
holo_builder/freeze.py

Freeze a Builder candidate with a static build_freeze_manifest gate.

Precondition: a build_freeze_manifest is hash-bound to the packet payload and
explicitly approved by Taylor.

The frozen packet is the artifact that goes to benchmark execution. Evaluation
models receive only the frozen packet payload — not _frozen, _builder, _internal,
or expected_verdict metadata.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path

from holo_builder.freeze_manifest import compute_payload_hash, validate_build_freeze_manifest


LEDGER_PATH = Path("holo_builder/outputs/ledger.jsonl")
FROZEN_DIR  = Path("holo_builder/outputs/frozen")


def _payload_hash(packet: dict) -> str:
    """SHA-256 of canonical payload JSON (action + context only, sort_keys=True)."""
    return compute_payload_hash(packet)


def freeze_packet(packet: dict, build_freeze_manifest: dict,
                  original_path: Path | None = None) -> tuple[Path, str]:
    """
    Freeze a packet after static build manifest approval.

    Args:
      packet:        Full packet dict (including _builder, _internal, payload).
      build_freeze_manifest: Static manifest approving freeze for this payload hash.
      original_path: Original packet file path (used only for logging).

    Returns:
      (frozen_path, sha256_hash)

    Raises:
      ValueError if the manifest is missing, stale, or not approved.
    """
    pkg_hash = validate_build_freeze_manifest(
        packet,
        build_freeze_manifest,
        original_path or Path(build_freeze_manifest.get("packet_path", "")),
    )
    hash8    = pkg_hash[:8]
    scenario_id = packet.get("scenario_id", "unknown")
    frozen_at   = datetime.utcnow().isoformat() + "Z"

    # Stamp packet with _frozen block
    frozen_packet = copy.deepcopy(packet)
    frozen_packet["_frozen"] = {
        "hash":                              pkg_hash,
        "hash8":                             hash8,
        "freeze_gate":                       "build_freeze_manifest",
        "manifest_type":                     build_freeze_manifest.get("manifest_type", ""),
        "manifest_timestamp":                build_freeze_manifest.get("timestamp", ""),
        "builder_hypothesis_verdict":        build_freeze_manifest.get("builder_hypothesis_verdict", ""),
        "static_lint_result":                build_freeze_manifest.get("static_lint_result", ""),
        "payload_visibility_result":         build_freeze_manifest.get("payload_visibility_result", ""),
        "no_model_visible_expected_verdict": build_freeze_manifest.get("no_model_visible_expected_verdict", False),
        "no_live_model_calls":               build_freeze_manifest.get("no_live_model_calls", False),
        "approved_by":                       build_freeze_manifest.get("approved_by"),
        "frozen_at":                         frozen_at,
        "source_path":                       str(original_path) if original_path else "",
    }
    frozen_packet["scenario_status"] = "frozen"

    # Write frozen packet
    FROZEN_DIR.mkdir(parents=True, exist_ok=True)
    frozen_path = FROZEN_DIR / f"{scenario_id}_{hash8}.json"
    frozen_path.write_text(json.dumps(frozen_packet, indent=2))

    # Append ledger entry
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    ledger_entry = {
        "scenario_id":                scenario_id,
        "hash":                       pkg_hash,
        "hash8":                      hash8,
        "freeze_gate":                "build_freeze_manifest",
        "builder_hypothesis_verdict": build_freeze_manifest.get("builder_hypothesis_verdict", ""),
        "manifest_timestamp":         build_freeze_manifest.get("timestamp", ""),
        "approved_by":                build_freeze_manifest.get("approved_by"),
        "frozen_at":                  frozen_at,
        "frozen_path":                str(frozen_path),
        "source_path":                str(original_path) if original_path else "",
    }
    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(ledger_entry) + "\n")

    return frozen_path, pkg_hash
