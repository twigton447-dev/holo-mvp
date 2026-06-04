"""
packet_lifecycle.py — Five-stage benchmark packet lifecycle state machine.

Stages:
  candidate              Zero official harness execution. Builder-only state.
  frozen_pending_judge   Packet + prompt hash-locked. Blind ablation runs accumulate.
  benchmark_locked       Judge adjudicated, confidence >= MEDIUM. Immutable verdict.
  diagnostic             Terminal. Contaminated, too easy, ambiguous, or pre-protocol.
  retired                Terminal. Explicitly deprecated.

Invariants enforced at transition boundaries:
  - Ablation runs only accepted at frozen_pending_judge.
  - Adjudication requires frozen_pending_judge + at least one blind run.
  - LOW confidence adjudication cannot lock a benchmark; caller must use diagnostic.
  - model_labels only accepted at benchmark_locked.
  - benchmark_locked cannot be moved to diagnostic.
  - build_model_visible_payload only executes at frozen_pending_judge.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from hashlock import FreezeRecord


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BenchmarkStatus(str, Enum):
    CANDIDATE             = "candidate"
    FROZEN_PENDING_JUDGE  = "frozen_pending_judge"
    BENCHMARK_LOCKED      = "benchmark_locked"
    DIAGNOSTIC            = "diagnostic"
    RETIRED               = "retired"


class ModelLabel(str, Enum):
    KNEW     = "KNEW"
    LUCKY    = "LUCKY"
    WRONG    = "WRONG"
    CONFUSED = "CONFUSED"


class JudgeConfidence(str, Enum):
    LOW    = "LOW"
    MEDIUM = "MEDIUM"
    HIGH   = "HIGH"


# ---------------------------------------------------------------------------
# Sub-records
# ---------------------------------------------------------------------------

@dataclass
class BlindAblationResult:
    run_id:        str
    model_id:      str
    condition:     str    # e.g. "A-GPT", "B-Claude", "E-HoloArch"
    raw_verdict:   str    # "ALLOW" | "ESCALATE" | "UNCLEAR" | "ERROR"
    raw_trace_ref: str    # path to raw_output artifact
    packet_hash:   str    # must match freeze_record.frozen_packet_hash at write time
    prompt_hash:   str    # must match freeze_record.frozen_prompt_hash at write time
    combined_hash: str    # must match freeze_record.combined_freeze_hash at write time
    run_timestamp: str
    annotated:     bool = False   # always False until Judge phase


@dataclass
class JudgeAdjudication:
    judge_adjudicated_verdict: str              # "ALLOW" | "ESCALATE-*" | "AMBIGUOUS"
    judge_confidence:          JudgeConfidence
    judge_rationale:           str
    adjudicated_at:            str
    adjudicated_by:            str
    judge_dissent:             Optional[str] = None


# ---------------------------------------------------------------------------
# Core record
# ---------------------------------------------------------------------------

@dataclass
class PacketRecord:
    # Identity
    candidate_id:         str
    family_id:            str
    variant_tag:          Optional[str]

    # Builder layer — set at creation, never mutated after freeze
    hypothesized_verdict: str    # "ALLOW" | "ESCALATE-*" | "AMBIGUOUS"
    builder_rationale:    str
    builder_notes:        Optional[str]

    # Lifecycle
    benchmark_status:  BenchmarkStatus = BenchmarkStatus.CANDIDATE
    status_reason:     Optional[str]   = None

    # Freeze layer (None until frozen)
    freeze_record:     Optional[FreezeRecord] = None

    # Ablation layer (populated blind, never pre-filled)
    blind_ablation_results: list[BlindAblationResult] = field(default_factory=list)

    # Judge layer (None until adjudicated)
    adjudication:      Optional[JudgeAdjudication] = None

    # Post-lock labels (empty until benchmark_locked)
    model_labels:      dict[str, ModelLabel] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Transition guards
# ---------------------------------------------------------------------------

def freeze(record: PacketRecord, freeze_rec: FreezeRecord) -> None:
    """candidate → frozen_pending_judge."""
    if record.benchmark_status != BenchmarkStatus.CANDIDATE:
        raise ValueError(
            f"{record.candidate_id}: freeze requires candidate status; "
            f"current={record.benchmark_status}"
        )
    record.freeze_record    = freeze_rec
    record.benchmark_status = BenchmarkStatus.FROZEN_PENDING_JUDGE


def accept_ablation_run(record: PacketRecord, result: BlindAblationResult) -> None:
    """Append a blind ablation result. Only permitted at frozen_pending_judge."""
    if record.benchmark_status != BenchmarkStatus.FROZEN_PENDING_JUDGE:
        raise ValueError(
            f"{record.candidate_id}: ablation runs require frozen_pending_judge; "
            f"current={record.benchmark_status}"
        )
    if record.freeze_record is None:
        raise ValueError(
            f"{record.candidate_id}: no freeze_record present — packet was not properly frozen"
        )
    record.blind_ablation_results.append(result)


def adjudicate(record: PacketRecord, adj: JudgeAdjudication) -> None:
    """
    frozen_pending_judge + ≥1 blind run → benchmark_locked.
    LOW confidence is rejected; caller must use move_to_diagnostic instead.
    """
    if record.benchmark_status != BenchmarkStatus.FROZEN_PENDING_JUDGE:
        raise ValueError(
            f"{record.candidate_id}: adjudication requires frozen_pending_judge; "
            f"current={record.benchmark_status}"
        )
    if not record.blind_ablation_results:
        raise ValueError(
            f"{record.candidate_id}: adjudication requires at least one blind ablation run"
        )
    if adj.judge_confidence == JudgeConfidence.LOW:
        raise ValueError(
            f"{record.candidate_id}: LOW confidence cannot lock benchmark; "
            "use move_to_diagnostic instead"
        )
    record.adjudication     = adj
    record.benchmark_status = BenchmarkStatus.BENCHMARK_LOCKED


def assign_model_label(record: PacketRecord, run_id: str, label: ModelLabel) -> None:
    """Assign KNEW/LUCKY/WRONG/CONFUSED to a run. Only permitted at benchmark_locked."""
    if record.benchmark_status != BenchmarkStatus.BENCHMARK_LOCKED:
        raise ValueError(
            f"{record.candidate_id}: model_labels require benchmark_locked; "
            f"current={record.benchmark_status}"
        )
    record.model_labels[run_id] = label


def move_to_diagnostic(record: PacketRecord, reason: str) -> None:
    """
    Move to diagnostic from any non-locked state.
    benchmark_locked is final and cannot be moved to diagnostic.
    """
    if record.benchmark_status == BenchmarkStatus.BENCHMARK_LOCKED:
        raise ValueError(
            f"{record.candidate_id}: benchmark_locked packet cannot be moved to diagnostic"
        )
    record.benchmark_status = BenchmarkStatus.DIAGNOSTIC
    record.status_reason    = reason


def retire(record: PacketRecord, reason: str) -> None:
    """Move to retired. Valid from any state; use explicitly and deliberately."""
    record.benchmark_status = BenchmarkStatus.RETIRED
    record.status_reason    = reason


# ---------------------------------------------------------------------------
# Payload construction
# ---------------------------------------------------------------------------

_STRIP_KEYS = frozenset({
    "hypothesized_verdict",
    "builder_rationale",
    "builder_notes",
    "judge_adjudicated_verdict",
    "judge_confidence",
    "judge_rationale",
    "judge_dissent",
    "adjudicated_at",
    "adjudicated_by",
    "benchmark_status",
    "model_labels",
    "freeze_record",
    "blind_ablation_results",
    "status_reason",
    "expected_verdict",
    "hidden_ground_truth",
    "gold_answer",
    "scoring_targets",
})


def strip_builder_metadata(packet_dict: dict) -> dict:
    """
    Return a copy of a raw packet dict with all builder and judge metadata removed.
    Operates on the serialized dict form, not a PacketRecord.
    Does not modify the input dict.
    """
    return {k: v for k, v in packet_dict.items() if k not in _STRIP_KEYS}


def build_model_visible_payload(record: PacketRecord, raw_packet: dict) -> dict:
    """
    Assemble the sterile context payload for model evaluation.
    Contains only {"action": ..., "context": ...}.
    Enforces execution lock: raises if record is not frozen_pending_judge.
    """
    if record.benchmark_status != BenchmarkStatus.FROZEN_PENDING_JUDGE:
        raise ValueError(
            f"{record.candidate_id}: build_model_visible_payload requires frozen_pending_judge; "
            f"current={record.benchmark_status}"
        )
    return {
        "action":  raw_packet.get("action", {}),
        "context": raw_packet.get("context", {}),
    }
