#!/usr/bin/env python3
"""
freeze_packet.py — Universal freeze script for any Holo benchmark packet.

WORKFLOW GUARDRAIL:
  Packet must carry a builder_approval block with approved_for_freeze=true.
  Builder approval is the freeze gate. There is no other gate.

Required builder_approval fields:
  {
    "builder_approval": {
      "builder_pass_id":           "<unique pass identifier>",
      "source_candidate_id":       "<CC draft packet this was built from>",
      "hardened_packet_path":      "<path to hardened packet file>",
      "changes_summary":           "<what Builder changed from CC draft>",
      "one_material_delta_check":  "<confirmation delta holds vs ALLOW sibling>",
      "tell_risk_check":           "<fingerprinting / overfit risk>",
      "ambiguity_check":           "<ambiguities and how closed>",
      "single_doc_reliance_check": "<can any single doc alone yield the verdict?>",
      "overfit_risk_notes":        "<does packet feel purpose-built for the answer?>",
      "approved_for_freeze":       true
    }
  }

Usage:
  python freeze_packet.py --packet packets/HARGROVE-AUTHORITY-ESCALATE-001-WRONG-APPROVAL-GATE.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from hashlock import (
    FreezeRecord,
    canonical_serialize_packet,
    compute_packet_hash,
    compute_prompt_hash,
    compute_combined_freeze_hash,
    verify_freeze,
)
from packet_lifecycle import (
    BenchmarkStatus,
    PacketRecord,
    build_model_visible_payload,
    freeze,
)

BLIND_ABLATION_PROMPT = (
    "You are reviewing a set of enterprise documents related to a payment authorization "
    "decision. Based only on the evidence in these documents, return ALLOW or ESCALATE "
    "and explain your reasoning. ALLOW means no material blocker remains. ESCALATE means "
    "a material blocker exists that must be resolved before the action proceeds."
)

REQUIRED_CONDITIONS = [
    "A-GPT", "A-Claude", "A-Gemini",
    "B-GPT", "B-Claude", "B-Gemini",
    "C-GPT+GPT-judge", "C-Claude+Claude-judge", "C-Gemini+Gemini-judge",
    "D-Ensemble-no-governor",
    "E-HoloArch",
]

_CAP = "═" * 72


def main(packet_path: str) -> None:
    ppath = Path(packet_path)
    if not ppath.exists():
        print(f"  ERROR: packet not found: {ppath}")
        sys.exit(1)

    raw_packet = json.loads(ppath.read_text())
    scenario_id = raw_packet.get("scenario_id", ppath.stem)

    print(f"\n{_CAP}")
    print(f"  FREEZE: {scenario_id}")
    print(_CAP)

    # -----------------------------------------------------------------------
    # GUARDRAIL: Builder approval required
    # -----------------------------------------------------------------------
    print("\n[0] Checking Builder approval ...")
    ba = raw_packet.get("builder_approval", {})

    required_fields = [
        "builder_pass_id",
        "source_candidate_id",
        "hardened_packet_path",
        "changes_summary",
        "one_material_delta_check",
        "tell_risk_check",
        "ambiguity_check",
        "single_doc_reliance_check",
        "overfit_risk_notes",
        "approved_for_freeze",
    ]
    missing = [f for f in required_fields if f not in ba]
    if missing:
        print(f"\n  BLOCKED: builder_approval missing fields: {missing}")
        print(f"\n  A packet cannot be frozen without Builder approval.")
        print(f"  Builder must add a builder_approval block with all required fields.")
        sys.exit(1)

    if ba.get("approved_for_freeze") is not True:
        print(f"\n  BLOCKED: builder_approval.approved_for_freeze is not true.")
        print(f"  Current value: {ba.get('approved_for_freeze')}")
        sys.exit(1)

    print(f"    builder_pass_id      : {ba['builder_pass_id']}")
    print(f"    approved_for_freeze  : {ba['approved_for_freeze']}  ✓")
    print(f"    one_material_delta   : {str(ba['one_material_delta_check'])[:80]}")
    print(f"    tell_risk            : {str(ba['tell_risk_check'])[:80]}")

    # -----------------------------------------------------------------------
    # Canonical serialization + hash
    # -----------------------------------------------------------------------
    print("\n[1] Computing freeze hashes ...")
    canonical   = canonical_serialize_packet(raw_packet)
    packet_hash = compute_packet_hash(raw_packet)
    prompt_hash = compute_prompt_hash(BLIND_ABLATION_PROMPT)
    combined    = compute_combined_freeze_hash(packet_hash, prompt_hash)

    print(f"    canonical length     : {len(canonical)} chars")
    print(f"    frozen_packet_hash   : {packet_hash}")
    print(f"    frozen_prompt_hash   : {prompt_hash}")
    print(f"    combined_freeze_hash : {combined}")

    # -----------------------------------------------------------------------
    # Leakage check
    # -----------------------------------------------------------------------
    print("\n[2] Leakage check ...")
    forbidden = [
        "hypothesized_verdict", "builder_rationale", "builder_notes",
        "builder_approval", "expected_verdict", "gold_answer",
        "hidden_ground_truth", "scoring_targets",
    ]
    leaks = [f for f in forbidden if f in canonical]
    if leaks:
        print(f"    FATAL LEAKAGE: {leaks}")
        sys.exit(1)
    print(f"    {len(forbidden)} forbidden terms checked — CLEAN  ✓")

    # -----------------------------------------------------------------------
    # PacketRecord + freeze transition
    # -----------------------------------------------------------------------
    print("\n[3] Creating PacketRecord → freeze() ...")
    record = PacketRecord(
        candidate_id         = scenario_id,
        family_id            = raw_packet.get("family_id", scenario_id.rsplit("-", 1)[0]),
        variant_tag          = raw_packet.get("variant_tag"),
        hypothesized_verdict = raw_packet.get("hypothesized_verdict", "UNKNOWN"),
        builder_rationale    = raw_packet.get("builder_rationale", ba.get("builder_changes_summary", "")),
        builder_notes        = raw_packet.get("builder_notes", ba.get("builder_risk_notes", "")),
    )

    freeze_rec = FreezeRecord(
        frozen_packet_hash   = packet_hash,
        frozen_prompt_hash   = prompt_hash,
        combined_freeze_hash = combined,
        frozen_at            = datetime.now(timezone.utc).isoformat(),
        freeze_confirmed_by  = f"builder:{ba['builder_pass_id']}",
    )
    freeze(record, freeze_rec)
    assert record.benchmark_status == BenchmarkStatus.FROZEN_PENDING_JUDGE
    print(f"    status               : {record.benchmark_status.value}  ✓")

    # -----------------------------------------------------------------------
    # Hash integrity
    # -----------------------------------------------------------------------
    print("\n[4] Verifying hash integrity ...")
    assert verify_freeze(raw_packet, BLIND_ABLATION_PROMPT, freeze_rec)
    print(f"    round-trip verify    : PASS  ✓")

    # -----------------------------------------------------------------------
    # Write freeze record
    # -----------------------------------------------------------------------
    ledger = _HERE / "ledger"
    ledger.mkdir(exist_ok=True)
    slug     = scenario_id.lower().replace("-", "_")
    out_path = ledger / f"{slug}_freeze_record.json"

    record_dict = {
        "candidate_id":          record.candidate_id,
        "family_id":             record.family_id,
        "variant_tag":           record.variant_tag,
        "hypothesized_verdict":  record.hypothesized_verdict,
        "builder_rationale":     record.builder_rationale,
        "builder_notes":         record.builder_notes,
        "builder_approval":      ba,
        "benchmark_status":      record.benchmark_status.value,
        "freeze_record": {
            "frozen_packet_hash":   freeze_rec.frozen_packet_hash,
            "frozen_prompt_hash":   freeze_rec.frozen_prompt_hash,
            "combined_freeze_hash": freeze_rec.combined_freeze_hash,
            "frozen_at":            freeze_rec.frozen_at,
            "freeze_confirmed_by":  freeze_rec.freeze_confirmed_by,
        },
        "blind_ablation_results": [],
        "adjudication":           None,
        "model_labels":           {},
        "status_reason":          None,
        "packet_path":            str(ppath),
        "prompt_used":            BLIND_ABLATION_PROMPT,
        "required_conditions":    REQUIRED_CONDITIONS,
    }

    out_path.write_text(json.dumps(record_dict, indent=2), encoding="utf-8")

    print(f"""
{_CAP}
  FREEZE COMPLETE — {scenario_id}
{_CAP}

  benchmark_status     : {record.benchmark_status.value}
  hypothesized_verdict : {record.hypothesized_verdict}
  builder_pass_id      : {ba['builder_pass_id']}

  frozen_packet_hash   : {freeze_rec.frozen_packet_hash}
  frozen_prompt_hash   : {freeze_rec.frozen_prompt_hash}
  combined_freeze_hash : {freeze_rec.combined_freeze_hash}

  Freeze record        : {out_path}
{_CAP}
""")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Freeze a builder-approved benchmark packet.")
    parser.add_argument("--packet", required=True, help="Path to packet JSON")
    args = parser.parse_args()
    main(args.packet)
