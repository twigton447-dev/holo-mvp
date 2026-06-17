from __future__ import annotations

import json
from pathlib import Path

from holo_builder.freeze_manifest import compute_payload_hash


LEDGER = Path("holo_builder/outputs/ledger.jsonl")
FROZEN_BEC_PACKETS = [
    Path("holo_builder/outputs/frozen/HBB-BEC-001-CALLBACK-PROVENANCE-FAIL_807468fc.json"),
    Path("holo_builder/outputs/frozen/HBB-BEC-001_8181d83c.json"),
    Path("holo_builder/outputs/frozen/HBB-BEC-002-HARD-ALLOW_f7986fa2.json"),
    Path("holo_builder/outputs/frozen/HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL_0151f5e6.json"),
]


def _ledger_by_scenario_id() -> dict[str, dict]:
    rows = [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]
    return {row["scenario_id"]: row for row in rows}


def test_hbb_bec_frozen_packets_have_matching_freeze_ledger_entries() -> None:
    ledger = _ledger_by_scenario_id()

    for frozen_path in FROZEN_BEC_PACKETS:
        packet = json.loads(frozen_path.read_text())
        frozen = packet["_frozen"]
        scenario_id = packet["scenario_id"]
        computed_hash = compute_payload_hash(packet)

        assert scenario_id in ledger
        assert ledger[scenario_id] == {
            "scenario_id": scenario_id,
            "hash": computed_hash,
            "hash8": computed_hash[:8],
            "freeze_gate": frozen["freeze_gate"],
            "builder_hypothesis_verdict": frozen["builder_hypothesis_verdict"],
            "manifest_timestamp": frozen["manifest_timestamp"],
            "approved_by": frozen["approved_by"],
            "frozen_at": frozen["frozen_at"],
            "frozen_path": str(frozen_path),
            "source_path": frozen["source_path"],
        }
