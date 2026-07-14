"""Pure, deterministic memory checkpointing for HoloChat.

This module deliberately owns no I/O.  A caller supplies transcript events,
proposal candidates, and a persistence acknowledgement; the state machine
returns immutable records describing what should be consolidated.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from hashlib import sha256
import json
from typing import Literal


class EventKind(str, Enum):
    NORMAL = "normal"
    CORRECTION = "correction"
    FORGET_REQUEST = "forget_request"
    REVOCATION = "revocation"
    COMMITMENT = "commitment"
    MAJOR_DECISION = "major_decision"


class LifecycleKind(str, Enum):
    THREAD_OPEN = "thread_open"
    THREAD_FORK = "thread_fork"
    IDLE = "idle"
    BEFORE_AUTOCOMPACT = "before_autocompact"


class CheckpointTrigger(str, Enum):
    USER_TURN_INTERVAL = "user_turn_interval"
    NEW_INPUT_TOKENS = "new_input_tokens"
    TOPIC_TRANSITION = "topic_transition"
    IMMEDIATE_CORRECTION = "immediate_correction"
    IMMEDIATE_FORGET_REQUEST = "immediate_forget_request"
    IMMEDIATE_REVOCATION = "immediate_revocation"
    IMMEDIATE_COMMITMENT = "immediate_commitment"
    IMMEDIATE_MAJOR_DECISION = "immediate_major_decision"
    THREAD_OPEN = "thread_open"
    THREAD_FORK = "thread_fork"
    IDLE_WITH_UNCONSOLIDATED_TURNS = "idle_with_unconsolidated_turns"
    BEFORE_AUTOCOMPACT = "before_autocompact"


class ProposalKind(str, Enum):
    FACT = "fact"
    SUPERSESSION = "supersession"
    REVOCATION = "revocation"
    TOPIC = "topic"
    DECISION = "decision"
    PREFERENCE = "preference"


class AdmissionDisposition(str, Enum):
    ADMIT = "admit"
    REJECT = "reject"
    QUARANTINE = "quarantine"


@dataclass(frozen=True)
class CheckpointPolicy:
    """Cadence configuration bounded by the MemorySteward operating law."""

    user_turn_interval: int = 6
    new_input_token_limit: int = 10_000
    admit_confidence: float = 0.80
    quarantine_confidence: float = 0.50

    def __post_init__(self) -> None:
        if not 6 <= self.user_turn_interval <= 8:
            raise ValueError("user_turn_interval must be between 6 and 8")
        if not 10_000 <= self.new_input_token_limit <= 15_000:
            raise ValueError("new_input_token_limit must be between 10,000 and 15,000")
        if not 0.0 <= self.quarantine_confidence <= self.admit_confidence <= 1.0:
            raise ValueError("confidence thresholds must be ordered within [0, 1]")


@dataclass(frozen=True)
class Provenance:
    message_ids: tuple[str, ...]
    sequence_numbers: tuple[int, ...]
    source: Literal["user", "system", "import"] = "user"
    excerpt_hash: str = ""

    def __post_init__(self) -> None:
        if not self.message_ids or not self.sequence_numbers:
            raise ValueError("provenance must name at least one transcript entry")
        if len(self.message_ids) != len(self.sequence_numbers):
            raise ValueError("provenance message_ids and sequence_numbers must align")


@dataclass(frozen=True)
class MemoryProposal:
    proposal_id: str
    kind: ProposalKind
    subject: str
    value: str
    provenance: Provenance
    confidence: float
    target_memory_id: str | None = None

    def __post_init__(self) -> None:
        if not self.proposal_id or not self.subject:
            raise ValueError("proposal_id and subject are required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be within [0, 1]")
        if self.kind in {ProposalKind.SUPERSESSION, ProposalKind.REVOCATION} and not self.target_memory_id:
            raise ValueError("supersessions and revocations require target_memory_id")


@dataclass(frozen=True)
class TranscriptEntry:
    sequence: int
    message_id: str
    role: Literal["user", "assistant", "system"]
    text: str
    input_tokens: int = 0
    topic: str | None = None
    topic_transition: bool = False
    event_kind: EventKind = EventKind.NORMAL
    proposals: tuple[MemoryProposal, ...] = ()

    def __post_init__(self) -> None:
        if self.sequence < 1 or not self.message_id:
            raise ValueError("sequence must be positive and message_id is required")
        if self.input_tokens < 0:
            raise ValueError("input_tokens cannot be negative")


@dataclass(frozen=True)
class TurnInput:
    message_id: str
    role: Literal["user", "assistant", "system"]
    text: str
    input_tokens: int = 0
    topic: str | None = None
    topic_transition: bool = False
    event_kind: EventKind = EventKind.NORMAL
    proposals: tuple[MemoryProposal, ...] = ()


@dataclass(frozen=True)
class LifecycleEvent:
    kind: LifecycleKind


@dataclass(frozen=True)
class ModelWatermark:
    model_id: str
    sequence: int
    transcript_hash: str


@dataclass(frozen=True)
class ReadOnlyDeltaWindow:
    """An immutable transcript range captured at checkpoint creation time."""

    start_exclusive: ModelWatermark
    end_inclusive: ModelWatermark
    entries: tuple[TranscriptEntry, ...]
    input_tokens: int
    user_turns: int


@dataclass(frozen=True)
class AdmissionDecision:
    proposal_id: str
    disposition: AdmissionDisposition
    reason: str


@dataclass(frozen=True)
class DurableMemory:
    memory_id: str
    proposal: MemoryProposal
    checkpoint_id: str


@dataclass(frozen=True)
class Checkpoint:
    checkpoint_id: str
    idempotency_key: str
    triggers: tuple[CheckpointTrigger, ...]
    delta: ReadOnlyDeltaWindow
    proposals: tuple[MemoryProposal, ...]
    decisions: tuple[AdmissionDecision, ...]
    supersedes_checkpoint_id: str | None = None


@dataclass(frozen=True)
class PersistenceAcknowledgement:
    checkpoint_id: str
    idempotency_key: str
    persistence_id: str
    accepted: bool


@dataclass(frozen=True)
class RollingState:
    """Ephemeral transcript state.  It is intentionally not durable memory."""

    thread_id: str
    model_id: str
    transcript: tuple[TranscriptEntry, ...] = ()


@dataclass(frozen=True)
class DurableConsolidation:
    """Only acknowledgement can add here or move its watermark."""

    watermark: ModelWatermark
    memories: tuple[DurableMemory, ...] = ()
    acknowledgements: tuple[PersistenceAcknowledgement, ...] = ()


@dataclass(frozen=True)
class MemoryStewardState:
    rolling: RollingState
    durable: DurableConsolidation
    pending_checkpoint: Checkpoint | None = None
    superseded_checkpoint_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class StewardTransition:
    state: MemoryStewardState
    triggers: tuple[CheckpointTrigger, ...] = ()
    checkpoint: Checkpoint | None = None
    duplicate_event: bool = False
    acknowledgement_status: Literal["not_applicable", "accepted", "rejected", "ignored", "idempotent"] = "not_applicable"


def initial_state(thread_id: str, model_id: str) -> MemoryStewardState:
    if not thread_id or not model_id:
        raise ValueError("thread_id and model_id are required")
    rolling = RollingState(thread_id=thread_id, model_id=model_id)
    watermark = ModelWatermark(model_id=model_id, sequence=0, transcript_hash=_hash_entries(()))
    return MemoryStewardState(rolling=rolling, durable=DurableConsolidation(watermark=watermark))


def restore_state(
    thread_id: str,
    model_id: str,
    transcript: tuple[TurnInput, ...],
    *,
    watermark_sequence: int,
    watermark_hash: str,
) -> MemoryStewardState:
    """Rehydrate rolling transcript around the last acknowledged DB watermark."""
    state = initial_state(thread_id, model_id)
    entries = tuple(
        TranscriptEntry(
            sequence=index,
            message_id=turn.message_id,
            role=turn.role,
            text=turn.text,
            input_tokens=turn.input_tokens,
            topic=turn.topic,
            topic_transition=turn.topic_transition,
            event_kind=turn.event_kind,
            proposals=turn.proposals,
        )
        for index, turn in enumerate(transcript, start=1)
    )
    if watermark_sequence < 0 or watermark_sequence > len(entries):
        raise ValueError("watermark_sequence must lie within the restored transcript")
    watermark = ModelWatermark(
        model_id=model_id,
        sequence=watermark_sequence,
        transcript_hash=watermark_hash or _hash_entries(entries[:watermark_sequence]),
    )
    return replace(
        state,
        rolling=replace(state.rolling, transcript=entries),
        durable=replace(state.durable, watermark=watermark),
    )


def checkpoint_payload(checkpoint: Checkpoint) -> dict[str, object]:
    """Return the stable JSON-compatible payload accepted by HoloBrain."""
    return json.loads(_canonical_json(asdict(checkpoint)))


def apply_turn(
    state: MemoryStewardState,
    turn: TurnInput,
    policy: CheckpointPolicy = CheckpointPolicy(),
) -> StewardTransition:
    """Append one transcript entry and, when warranted, freeze a checkpoint."""

    if any(entry.message_id == turn.message_id for entry in state.rolling.transcript):
        return StewardTransition(state=state, duplicate_event=True, checkpoint=state.pending_checkpoint)

    entry = TranscriptEntry(
        sequence=len(state.rolling.transcript) + 1,
        message_id=turn.message_id,
        role=turn.role,
        text=turn.text,
        input_tokens=turn.input_tokens,
        topic=turn.topic,
        topic_transition=turn.topic_transition,
        event_kind=turn.event_kind,
        proposals=turn.proposals,
    )
    appended = replace(state, rolling=replace(state.rolling, transcript=state.rolling.transcript + (entry,)))
    triggers = _turn_triggers(appended, entry, policy)
    return _maybe_checkpoint(appended, triggers, policy)


def apply_exchange(
    state: MemoryStewardState,
    user: TurnInput,
    assistant: TurnInput,
    policy: CheckpointPolicy = CheckpointPolicy(),
) -> StewardTransition:
    """Append an ordered user/worker exchange, then evaluate checkpoint law."""
    if user.role != "user" or assistant.role != "assistant":
        raise ValueError("apply_exchange requires user then assistant roles")
    if any(entry.message_id in {user.message_id, assistant.message_id} for entry in state.rolling.transcript):
        return StewardTransition(state=state, duplicate_event=True, checkpoint=state.pending_checkpoint)

    user_entry = TranscriptEntry(
        sequence=len(state.rolling.transcript) + 1,
        message_id=user.message_id,
        role=user.role,
        text=user.text,
        input_tokens=user.input_tokens,
        topic=user.topic,
        topic_transition=user.topic_transition,
        event_kind=user.event_kind,
        proposals=user.proposals,
    )
    assistant_entry = TranscriptEntry(
        sequence=user_entry.sequence + 1,
        message_id=assistant.message_id,
        role=assistant.role,
        text=assistant.text,
        input_tokens=assistant.input_tokens,
        topic=assistant.topic,
        topic_transition=False,
        event_kind=EventKind.NORMAL,
        proposals=assistant.proposals,
    )
    appended = replace(
        state,
        rolling=replace(
            state.rolling,
            transcript=state.rolling.transcript + (user_entry, assistant_entry),
        ),
    )
    return _maybe_checkpoint(appended, _turn_triggers(appended, user_entry, policy), policy)


def apply_lifecycle_event(
    state: MemoryStewardState,
    event: LifecycleEvent,
    policy: CheckpointPolicy = CheckpointPolicy(),
) -> StewardTransition:
    """Evaluate explicit lifecycle boundaries without altering the transcript."""

    has_delta = _has_unconsolidated_delta(state)
    trigger = {
        LifecycleKind.THREAD_OPEN: CheckpointTrigger.THREAD_OPEN,
        LifecycleKind.THREAD_FORK: CheckpointTrigger.THREAD_FORK,
        LifecycleKind.IDLE: CheckpointTrigger.IDLE_WITH_UNCONSOLIDATED_TURNS,
        LifecycleKind.BEFORE_AUTOCOMPACT: CheckpointTrigger.BEFORE_AUTOCOMPACT,
    }[event.kind]
    if event.kind is LifecycleKind.IDLE and not has_delta:
        return StewardTransition(state=state)
    return _maybe_checkpoint(state, (trigger,), policy)


def acknowledge_checkpoint(
    state: MemoryStewardState,
    acknowledgement: PersistenceAcknowledgement,
) -> StewardTransition:
    """Commit an immutable checkpoint only after a successful persistence ack."""

    pending = state.pending_checkpoint
    if pending is None:
        if any(ack.idempotency_key == acknowledgement.idempotency_key for ack in state.durable.acknowledgements):
            return StewardTransition(state=state, acknowledgement_status="idempotent")
        return StewardTransition(state=state, acknowledgement_status="ignored")
    if (acknowledgement.checkpoint_id != pending.checkpoint_id or
            acknowledgement.idempotency_key != pending.idempotency_key):
        return StewardTransition(state=state, acknowledgement_status="ignored")
    if not acknowledgement.accepted:
        return StewardTransition(state=state, checkpoint=pending, acknowledgement_status="rejected")

    admitted = tuple(
        DurableMemory(memory_id=decision.proposal_id, proposal=proposal, checkpoint_id=pending.checkpoint_id)
        for proposal, decision in zip(pending.proposals, pending.decisions)
        if decision.disposition is AdmissionDisposition.ADMIT
    )
    durable = replace(
        state.durable,
        watermark=pending.delta.end_inclusive,
        memories=state.durable.memories + admitted,
        acknowledgements=state.durable.acknowledgements + (acknowledgement,),
    )
    return StewardTransition(
        state=replace(state, durable=durable, pending_checkpoint=None),
        acknowledgement_status="accepted",
    )


def _maybe_checkpoint(
    state: MemoryStewardState,
    triggers: tuple[CheckpointTrigger, ...],
    policy: CheckpointPolicy,
) -> StewardTransition:
    if not triggers or not _has_unconsolidated_delta(state):
        return StewardTransition(state=state, triggers=triggers, checkpoint=state.pending_checkpoint)

    immediate = any(trigger.value.startswith("immediate_") for trigger in triggers)
    if state.pending_checkpoint is not None and not immediate:
        return StewardTransition(state=state, triggers=triggers, checkpoint=state.pending_checkpoint)

    checkpoint = _build_checkpoint(state, triggers, policy, state.pending_checkpoint)
    superseded = state.superseded_checkpoint_ids
    if state.pending_checkpoint is not None:
        superseded += (state.pending_checkpoint.checkpoint_id,)
    next_state = replace(state, pending_checkpoint=checkpoint, superseded_checkpoint_ids=superseded)
    return StewardTransition(state=next_state, triggers=triggers, checkpoint=checkpoint)


def _build_checkpoint(
    state: MemoryStewardState,
    triggers: tuple[CheckpointTrigger, ...],
    policy: CheckpointPolicy,
    previous: Checkpoint | None,
) -> Checkpoint:
    start = state.durable.watermark
    entries = tuple(entry for entry in state.rolling.transcript if entry.sequence > start.sequence)
    end = ModelWatermark(
        model_id=state.rolling.model_id,
        sequence=entries[-1].sequence,
        transcript_hash=_hash_entries(state.rolling.transcript[:entries[-1].sequence]),
    )
    delta = ReadOnlyDeltaWindow(
        start_exclusive=start,
        end_inclusive=end,
        entries=entries,
        input_tokens=sum(entry.input_tokens for entry in entries),
        user_turns=sum(entry.role == "user" for entry in entries),
    )
    proposals = tuple(proposal for entry in entries for proposal in entry.proposals)
    decisions = tuple(_decide(proposal, delta, policy) for proposal in proposals)
    seed = _canonical_json({
        "thread_id": state.rolling.thread_id,
        "model_id": state.rolling.model_id,
        "start": start.sequence,
        "end": end.sequence,
        "hash": end.transcript_hash,
        "triggers": [trigger.value for trigger in triggers],
    })
    checkpoint_id = sha256(seed.encode("utf-8")).hexdigest()[:24]
    idempotency_key = sha256(("memory-steward:" + seed).encode("utf-8")).hexdigest()
    return Checkpoint(
        checkpoint_id=checkpoint_id,
        idempotency_key=idempotency_key,
        triggers=triggers,
        delta=delta,
        proposals=proposals,
        decisions=decisions,
        supersedes_checkpoint_id=previous.checkpoint_id if previous else None,
    )


def _decide(proposal: MemoryProposal, delta: ReadOnlyDeltaWindow, policy: CheckpointPolicy) -> AdmissionDecision:
    known_sequences = {entry.sequence for entry in delta.entries}
    if not set(proposal.provenance.sequence_numbers).issubset(known_sequences):
        return AdmissionDecision(proposal.proposal_id, AdmissionDisposition.REJECT, "Provenance lies outside the read-only delta window.")
    direct_user_revocation = proposal.kind is ProposalKind.REVOCATION and proposal.provenance.source == "user"
    if direct_user_revocation:
        return AdmissionDecision(proposal.proposal_id, AdmissionDisposition.ADMIT, "Direct user correction or forget request.")
    if proposal.confidence >= policy.admit_confidence:
        return AdmissionDecision(proposal.proposal_id, AdmissionDisposition.ADMIT, "Confidence meets admission threshold.")
    if proposal.confidence >= policy.quarantine_confidence:
        return AdmissionDecision(proposal.proposal_id, AdmissionDisposition.QUARANTINE, "Needs later confirmation.")
    return AdmissionDecision(proposal.proposal_id, AdmissionDisposition.REJECT, "Confidence is below quarantine threshold.")


def _turn_triggers(
    state: MemoryStewardState,
    entry: TranscriptEntry,
    policy: CheckpointPolicy,
) -> tuple[CheckpointTrigger, ...]:
    triggers: list[CheckpointTrigger] = []
    immediate = {
        EventKind.CORRECTION: CheckpointTrigger.IMMEDIATE_CORRECTION,
        EventKind.FORGET_REQUEST: CheckpointTrigger.IMMEDIATE_FORGET_REQUEST,
        EventKind.REVOCATION: CheckpointTrigger.IMMEDIATE_REVOCATION,
        EventKind.COMMITMENT: CheckpointTrigger.IMMEDIATE_COMMITMENT,
        EventKind.MAJOR_DECISION: CheckpointTrigger.IMMEDIATE_MAJOR_DECISION,
    }.get(entry.event_kind)
    if immediate is not None:
        triggers.append(immediate)
    if entry.topic_transition or _is_meaningful_topic_transition(state.rolling.transcript, entry):
        triggers.append(CheckpointTrigger.TOPIC_TRANSITION)
    delta_entries = tuple(e for e in state.rolling.transcript if e.sequence > state.durable.watermark.sequence)
    if sum(e.role == "user" for e in delta_entries) >= policy.user_turn_interval:
        triggers.append(CheckpointTrigger.USER_TURN_INTERVAL)
    if sum(e.input_tokens for e in delta_entries) >= policy.new_input_token_limit:
        triggers.append(CheckpointTrigger.NEW_INPUT_TOKENS)
    return tuple(triggers)


def _is_meaningful_topic_transition(entries: tuple[TranscriptEntry, ...], entry: TranscriptEntry) -> bool:
    if entry.role != "user" or not entry.topic:
        return False
    earlier_topics = [e.topic for e in entries[:-1] if e.role == "user" and e.topic]
    return bool(earlier_topics and earlier_topics[-1] != entry.topic)


def _has_unconsolidated_delta(state: MemoryStewardState) -> bool:
    return bool(state.rolling.transcript and state.rolling.transcript[-1].sequence > state.durable.watermark.sequence)


def _hash_entries(entries: tuple[TranscriptEntry, ...]) -> str:
    return sha256(_canonical_json([_entry_payload(entry) for entry in entries]).encode("utf-8")).hexdigest()


def _entry_payload(entry: TranscriptEntry) -> dict[str, object]:
    return {
        "sequence": entry.sequence,
        "message_id": entry.message_id,
        "role": entry.role,
        "text": entry.text,
        "input_tokens": entry.input_tokens,
        "topic": entry.topic,
        "topic_transition": entry.topic_transition,
        "event_kind": entry.event_kind.value,
        "proposals": [
            {
                "proposal_id": proposal.proposal_id,
                "kind": proposal.kind.value,
                "subject": proposal.subject,
                "value": proposal.value,
                "target_memory_id": proposal.target_memory_id,
                "confidence": proposal.confidence,
                "provenance": {
                    "message_ids": proposal.provenance.message_ids,
                    "sequence_numbers": proposal.provenance.sequence_numbers,
                    "source": proposal.provenance.source,
                    "excerpt_hash": proposal.provenance.excerpt_hash,
                },
            }
            for proposal in entry.proposals
        ],
    }


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
