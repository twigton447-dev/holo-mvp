#!/usr/bin/env python3
"""
adjudicate_packet.py — Generic lifecycle adjudication for any Holo benchmark packet.

GUARDRAILS enforced unconditionally:
  1. All required_conditions declared in freeze record must appear in blind_ablation_results.
  2. Packet + prompt hash verification must pass before verdict is accepted.
  3. hypothesized_verdict is never read, displayed, or used as ground truth.
  4. Model labels (KNEW/LUCKY/WRONG/CONFUSED) may only be assigned after benchmark_locked.
  5. LOW confidence cannot lock a packet — use --move-to-diagnostic for those.

ADJUDICATION MODE:
  python adjudicate_packet.py \\
      --freeze-record ledger/foo_freeze_record.json \\
      --verdict ALLOW \\
      --confidence HIGH \\
      --rationale "Full policy-grounded rationale..." \\
      [--dissent "Minority view or open questions..."] \\
      [--adjudicated-by "judge:taylor_wigton"]

  For long rationale/dissent, pass a file path with @:
      --rationale @rationale.txt
      --dissent @dissent.txt

LABEL ASSIGNMENT MODE (packet must already be benchmark_locked):
  python adjudicate_packet.py \\
      --freeze-record ledger/foo_freeze_record.json \\
      --labels labels.json

  labels.json format:
    {
      "<run_id>:<condition>": "KNEW" | "LUCKY" | "WRONG" | "CONFUSED"
    }

STATUS CHECK MODE (read-only, no mutation):
  python adjudicate_packet.py --freeze-record ledger/foo_freeze_record.json --status

DIAGNOSTIC MODE:
  python adjudicate_packet.py \\
      --freeze-record ledger/foo_freeze_record.json \\
      --move-to-diagnostic "reason text"
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from hashlock import FreezeRecord, verify_freeze
from packet_lifecycle import (
    BenchmarkStatus,
    BlindAblationResult,
    JudgeAdjudication,
    JudgeConfidence,
    ModelLabel,
    PacketRecord,
    accept_ablation_run,
    adjudicate,
    assign_model_label,
    freeze,
    move_to_diagnostic,
)

_CAP = "═" * 72
_VALID_VERDICTS = {"ALLOW", "ESCALATE", "AMBIGUOUS"}
_VALID_LABELS   = {m.value for m in ModelLabel}


# ---------------------------------------------------------------------------
# Load / persist
# ---------------------------------------------------------------------------

def _load_freeze_record(path: Path) -> dict:
    if not path.exists():
        print(f"  ERROR: freeze record not found: {path}")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def _build_packet_record(data: dict) -> PacketRecord:
    fr = data["freeze_record"]
    freeze_rec = FreezeRecord(
        frozen_packet_hash   = fr["frozen_packet_hash"],
        frozen_prompt_hash   = fr["frozen_prompt_hash"],
        combined_freeze_hash = fr["combined_freeze_hash"],
        frozen_at            = fr["frozen_at"],
        freeze_confirmed_by  = fr["freeze_confirmed_by"],
    )
    record = PacketRecord(
        candidate_id         = data["candidate_id"],
        family_id            = data["family_id"],
        variant_tag          = data.get("variant_tag"),
        hypothesized_verdict = data.get("hypothesized_verdict", "REDACTED"),
        builder_rationale    = data.get("builder_rationale", ""),
        builder_notes        = data.get("builder_notes"),
        benchmark_status     = BenchmarkStatus(data["benchmark_status"]),
        status_reason        = data.get("status_reason"),
        freeze_record        = freeze_rec,
    )
    for r in data.get("blind_ablation_results", []):
        record.blind_ablation_results.append(BlindAblationResult(
            run_id        = r["run_id"],
            model_id      = r["model_id"],
            condition     = r["condition"],
            raw_verdict   = r["raw_verdict"],
            raw_trace_ref = r["raw_trace_ref"],
            packet_hash   = r["packet_hash"],
            prompt_hash   = r["prompt_hash"],
            combined_hash = r["combined_hash"],
            run_timestamp = r["run_timestamp"],
            annotated     = r.get("annotated", False),
        ))
    return record, freeze_rec


def _persist(path: Path, data: dict, record: PacketRecord, adj: JudgeAdjudication | None) -> None:
    if adj is not None:
        data["adjudication"] = {
            "judge_adjudicated_verdict": adj.judge_adjudicated_verdict,
            "judge_confidence":          adj.judge_confidence.value,
            "judge_rationale":           adj.judge_rationale,
            "judge_dissent":             adj.judge_dissent,
            "adjudicated_at":            adj.adjudicated_at,
            "adjudicated_by":            adj.adjudicated_by,
        }
    data["benchmark_status"] = record.benchmark_status.value
    data["model_labels"]     = {k: v.value for k, v in record.model_labels.items()}
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

def _check_required_conditions(data: dict) -> None:
    """Block if any required condition is absent from blind_ablation_results."""
    required  = data.get("required_conditions", [])
    completed = {r["condition"] for r in data.get("blind_ablation_results", [])}

    print(f"\n[G1] Required conditions check ...")
    if not required:
        print(f"  WARNING: required_conditions is absent or empty in freeze record.")
        print(f"  This means no conditions were declared required at freeze time.")
        print(f"  For canonical packets, required_conditions must be set by freeze_packet.py.")
        print(f"  Blocking to prevent adjudication without declared conditions.")
        sys.exit(1)

    missing = [c for c in required if c not in completed]
    for c in required:
        mark = "✓" if c in completed else "✗ MISSING"
        print(f"    {c:<40}  {mark}")

    if missing:
        print(f"\n  BLOCKED: {len(missing)} required condition(s) not yet run:")
        for c in missing:
            print(f"    - {c}")
        sys.exit(1)

    print(f"  All {len(required)} required conditions present  ✓")


def _check_hash_integrity(data: dict, freeze_rec: FreezeRecord) -> None:
    """Block if hash fields are absent, empty, or do not verify against the packet on disk."""
    print(f"\n[G2] Hash integrity check ...")

    fr_data = data["freeze_record"]
    packet_hash   = fr_data.get("frozen_packet_hash", "")
    prompt_hash   = fr_data.get("frozen_prompt_hash", "")
    combined_hash = fr_data.get("combined_freeze_hash", "")

    if not packet_hash or not prompt_hash or not combined_hash:
        print(f"  BLOCKED: freeze record has empty hash fields.")
        print(f"    frozen_packet_hash:   {packet_hash!r}")
        print(f"    frozen_prompt_hash:   {prompt_hash!r}")
        print(f"    combined_freeze_hash: {combined_hash!r}")
        print(f"  A packet cannot be adjudicated without valid hash locks.")
        sys.exit(1)

    packet_path = Path(data.get("packet_path", ""))
    if not packet_path.is_absolute():
        packet_path = _HERE / packet_path
    if not packet_path.exists():
        print(f"  BLOCKED: packet file not found at stored path: {packet_path}")
        print(f"  Cannot verify hash without the packet on disk.")
        sys.exit(1)

    prompt_used = data.get("prompt_used", "")
    if not prompt_used:
        print(f"  BLOCKED: prompt_used is absent from freeze record.")
        print(f"  Cannot verify prompt hash without the stored prompt text.")
        sys.exit(1)

    raw_packet = json.loads(packet_path.read_text(encoding="utf-8"))
    ok = verify_freeze(raw_packet, prompt_used, freeze_rec)

    print(f"    frozen_packet_hash:   {packet_hash[:16]}...  {'✓' if ok else '✗'}")
    print(f"    frozen_prompt_hash:   {prompt_hash[:16]}...  {'✓' if ok else '✗'}")
    print(f"    combined_freeze_hash: {combined_hash[:16]}...  {'✓' if ok else '✗'}")

    if not ok:
        print(f"\n  BLOCKED: hash verification failed.")
        print(f"  The packet on disk does not match the freeze record.")
        print(f"  Packet may have been mutated after freeze.")
        sys.exit(1)

    print(f"  Hash verification passed  ✓")


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def _read_text_arg(value: str) -> str:
    """Resolve @filename or return the string as-is."""
    if value.startswith("@"):
        p = Path(value[1:])
        if not p.exists():
            print(f"  ERROR: rationale/dissent file not found: {p}")
            sys.exit(1)
        return p.read_text(encoding="utf-8").strip()
    return value


def mode_status(freeze_record_path: Path) -> None:
    data = _load_freeze_record(freeze_record_path)
    candidate_id = data["candidate_id"]
    status       = data["benchmark_status"]
    lc           = data.get("lifecycle_classification", "")
    required     = data.get("required_conditions", [])
    completed    = {r["condition"] for r in data.get("blind_ablation_results", [])}
    missing      = [c for c in required if c not in completed]
    adj          = data.get("adjudication") or {}

    print(f"\n{_CAP}")
    print(f"  STATUS: {candidate_id}")
    print(_CAP)
    print(f"  benchmark_status      : {status}")
    if lc:
        print(f"  lifecycle_classif.    : {lc}")
    print(f"  required_conditions   : {len(required)}")
    print(f"  completed conditions  : {len(completed)}")
    if missing:
        print(f"  MISSING               : {missing}")
    else:
        print(f"  all conditions run    : ✓")

    if adj:
        print(f"  adjudicated_verdict   : {adj.get('judge_adjudicated_verdict')}")
        print(f"  adjudicated_by        : {adj.get('adjudicated_by')}")
        print(f"  adjudicated_at        : {adj.get('adjudicated_at')}")

    labels = data.get("model_labels", {})
    if labels:
        print(f"  model_labels          : {len(labels)} assigned")
    print(_CAP)


def mode_adjudicate(
    freeze_record_path: Path,
    verdict:        str,
    confidence:     str,
    rationale:      str,
    dissent:        str | None,
    adjudicated_by: str,
) -> None:
    data = _load_freeze_record(freeze_record_path)
    candidate_id = data["candidate_id"]

    print(f"\n{_CAP}")
    print(f"  ADJUDICATE: {candidate_id}")
    print(_CAP)

    # Status guard
    status = BenchmarkStatus(data["benchmark_status"])
    if status == BenchmarkStatus.BENCHMARK_LOCKED:
        print(f"\n  Already benchmark_locked — nothing to adjudicate.")
        sys.exit(0)
    if status != BenchmarkStatus.FROZEN_PENDING_JUDGE:
        print(f"\n  ERROR: adjudication requires frozen_pending_judge; current={status.value}")
        sys.exit(1)

    # Confidence guard (LOW cannot lock)
    conf = JudgeConfidence(confidence)
    if conf == JudgeConfidence.LOW:
        print(f"\n  BLOCKED: LOW confidence cannot lock a benchmark packet.")
        print(f"  Use --move-to-diagnostic instead.")
        sys.exit(1)

    # Verdict guard — hypothesized_verdict is never shown; accept any valid verdict
    if verdict not in _VALID_VERDICTS and not verdict.startswith("ESCALATE-"):
        print(f"\n  ERROR: verdict must be ALLOW, ESCALATE, ESCALATE-<reason>, or AMBIGUOUS.")
        sys.exit(1)

    record, freeze_rec = _build_packet_record(data)

    # Required conditions guard
    _check_required_conditions(data)

    # Hash integrity guard
    _check_hash_integrity(data, freeze_rec)

    # Adjudicate
    print(f"\n[1] Recording Judge adjudication ...")
    adj = JudgeAdjudication(
        judge_adjudicated_verdict = verdict,
        judge_confidence          = conf,
        judge_rationale           = rationale,
        judge_dissent             = dissent,
        adjudicated_at            = datetime.now(timezone.utc).isoformat(),
        adjudicated_by            = adjudicated_by,
    )
    adjudicate(record, adj)
    assert record.benchmark_status == BenchmarkStatus.BENCHMARK_LOCKED

    # Persist
    print(f"\n[2] Persisting ...")
    _persist(freeze_record_path, data, record, adj)

    print(f"""
{_CAP}
  BENCHMARK LOCKED — {candidate_id}
{_CAP}

  benchmark_status     : {record.benchmark_status.value}
  verdict              : {verdict}
  confidence           : {confidence}
  adjudicated_by       : {adjudicated_by}
  adjudicated_at       : {adj.adjudicated_at}

  Freeze record        : {freeze_record_path}
{_CAP}
""")


def mode_labels(freeze_record_path: Path, labels_path: Path) -> None:
    data = _load_freeze_record(freeze_record_path)
    candidate_id = data["candidate_id"]

    print(f"\n{_CAP}")
    print(f"  ASSIGN LABELS: {candidate_id}")
    print(_CAP)

    status = BenchmarkStatus(data["benchmark_status"])
    if status != BenchmarkStatus.BENCHMARK_LOCKED:
        print(f"\n  BLOCKED: model_labels require benchmark_locked; current={status.value}")
        sys.exit(1)

    if not labels_path.exists():
        print(f"\n  ERROR: labels file not found: {labels_path}")
        sys.exit(1)

    raw_labels = json.loads(labels_path.read_text(encoding="utf-8"))
    if not isinstance(raw_labels, dict):
        print(f"\n  ERROR: labels file must be a JSON object mapping run_id:condition → label")
        sys.exit(1)

    record, freeze_rec = _build_packet_record(data)

    # Restore existing labels
    for k, v in data.get("model_labels", {}).items():
        record.model_labels[k] = ModelLabel(v)

    print(f"\n[1] Assigning labels ...")
    for key, value in raw_labels.items():
        label_str = value if isinstance(value, str) else value.get("label", "")
        if label_str not in _VALID_LABELS:
            print(f"  ERROR: invalid label {label_str!r} for {key!r}. Must be one of {_VALID_LABELS}")
            sys.exit(1)
        label = ModelLabel(label_str)
        assign_model_label(record, key, label)
        mark = "✓" if label in (ModelLabel.KNEW, ModelLabel.LUCKY) else "✗"
        print(f"  {key:<50}  {label.value:<8}  {mark}")

    print(f"\n[2] Persisting ...")
    _persist(freeze_record_path, data, record, adj=None)

    print(f"\n  Labels written to : {freeze_record_path}")
    print(f"  Total assigned    : {len(record.model_labels)}")


def mode_diagnostic(freeze_record_path: Path, reason: str) -> None:
    data = _load_freeze_record(freeze_record_path)
    candidate_id = data["candidate_id"]

    print(f"\n{_CAP}")
    print(f"  MOVE TO DIAGNOSTIC: {candidate_id}")
    print(_CAP)

    record, _ = _build_packet_record(data)
    move_to_diagnostic(record, reason)
    data["benchmark_status"] = record.benchmark_status.value
    data["status_reason"]    = reason
    freeze_record_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"  benchmark_status : {record.benchmark_status.value}")
    print(f"  reason           : {reason}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generic lifecycle adjudication for Holo benchmark packets.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--freeze-record", required=True, metavar="PATH",
                   help="Path to the freeze record JSON.")

    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--status",           action="store_true",
                      help="Print status without mutating anything.")
    mode.add_argument("--labels",           metavar="PATH",
                      help="JSON file of model labels to assign (packet must be benchmark_locked).")
    mode.add_argument("--move-to-diagnostic", metavar="REASON",
                      help="Move packet to diagnostic state with given reason.")

    p.add_argument("--verdict",         metavar="VERDICT",
                   help="ALLOW | ESCALATE | ESCALATE-<reason> | AMBIGUOUS")
    p.add_argument("--confidence",      metavar="HIGH|MEDIUM",
                   help="Judge confidence. LOW is rejected (cannot lock).")
    p.add_argument("--rationale",       metavar="TEXT|@FILE",
                   help="Judge rationale. Use @filename.txt for long text.")
    p.add_argument("--dissent",         metavar="TEXT|@FILE", default=None,
                   help="Minority dissent or open questions. Optional.")
    p.add_argument("--adjudicated-by",  metavar="STR", default="judge:human",
                   help="Identifier of the adjudicator. Default: judge:human")
    return p.parse_args()


def main() -> None:
    args    = _parse()
    fr_path = Path(args.freeze_record)

    if args.status:
        mode_status(fr_path)
        return

    if args.labels:
        mode_labels(fr_path, Path(args.labels))
        return

    if args.move_to_diagnostic:
        mode_diagnostic(fr_path, args.move_to_diagnostic)
        return

    # Adjudication mode — all three required
    missing_args = []
    if not args.verdict:    missing_args.append("--verdict")
    if not args.confidence: missing_args.append("--confidence")
    if not args.rationale:  missing_args.append("--rationale")
    if missing_args:
        print(f"\n  ERROR: adjudication mode requires: {', '.join(missing_args)}")
        print(f"  Run with --status to inspect the current state.")
        sys.exit(1)

    mode_adjudicate(
        freeze_record_path = fr_path,
        verdict            = args.verdict.upper(),
        confidence         = args.confidence.upper(),
        rationale          = _read_text_arg(args.rationale),
        dissent            = _read_text_arg(args.dissent) if args.dissent else None,
        adjudicated_by     = args.adjudicated_by,
    )


if __name__ == "__main__":
    main()
