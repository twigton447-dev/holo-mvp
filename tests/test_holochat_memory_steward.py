"""No-provider tests for the deterministic HoloChat memory steward."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from holochat_memory_steward import (
    AdmissionDisposition,
    CheckpointPolicy,
    CheckpointTrigger,
    EventKind,
    LifecycleEvent,
    LifecycleKind,
    MemoryProposal,
    PersistenceAcknowledgement,
    ProposalKind,
    Provenance,
    TurnInput,
    acknowledge_checkpoint,
    apply_exchange,
    apply_lifecycle_event,
    apply_turn,
    initial_state,
    restore_state,
)


def user_turn(number: int, **overrides: object) -> TurnInput:
    values: dict[str, object] = {
        "message_id": f"user-{number}",
        "role": "user",
        "text": f"User turn {number}",
        "input_tokens": 10,
    }
    values.update(overrides)
    return TurnInput(**values)  # type: ignore[arg-type]


class MemoryStewardTests(unittest.TestCase):
    def test_restore_state_preserves_acknowledged_watermark_and_transcript(self) -> None:
        state = restore_state(
            "thread-a",
            "model-a",
            (
                user_turn(1),
                TurnInput("assistant-1", "assistant", "Worker response"),
            ),
            watermark_sequence=2,
            watermark_hash="stored-hash",
        )
        self.assertEqual(state.durable.watermark.sequence, 2)
        self.assertEqual(state.durable.watermark.transcript_hash, "stored-hash")
        self.assertEqual([entry.sequence for entry in state.rolling.transcript], [1, 2])

    def test_exchange_checkpoint_includes_user_and_worker_in_order(self) -> None:
        state = initial_state("thread-a", "model-a")
        transition = apply_exchange(
            state,
            user_turn(1, event_kind=EventKind.COMMITMENT),
            TurnInput("assistant-1", "assistant", "Worker response", input_tokens=20),
        )
        self.assertEqual(
            [entry.role for entry in transition.checkpoint.delta.entries],  # type: ignore[union-attr]
            ["user", "assistant"],
        )
        self.assertEqual(transition.checkpoint.delta.end_inclusive.sequence, 2)  # type: ignore[union-attr]

    def test_policy_enforces_operating_law_bounds(self) -> None:
        with self.assertRaises(ValueError):
            CheckpointPolicy(user_turn_interval=5)
        with self.assertRaises(ValueError):
            CheckpointPolicy(user_turn_interval=9)
        with self.assertRaises(ValueError):
            CheckpointPolicy(new_input_token_limit=9_999)
        with self.assertRaises(ValueError):
            CheckpointPolicy(new_input_token_limit=15_001)

    def test_turn_cadence_creates_checkpoint_at_configured_interval(self) -> None:
        state = initial_state("thread-a", "model-a")
        for number in range(1, 6):
            transition = apply_turn(state, user_turn(number))
            self.assertIsNone(transition.checkpoint)
            state = transition.state
        transition = apply_turn(state, user_turn(6))
        self.assertEqual(transition.triggers, (CheckpointTrigger.USER_TURN_INTERVAL,))
        self.assertIsNotNone(transition.checkpoint)
        self.assertEqual(transition.checkpoint.delta.user_turns, 6)  # type: ignore[union-attr]

    def test_new_input_token_threshold_creates_checkpoint(self) -> None:
        state = initial_state("thread-a", "model-a")
        transition = apply_turn(state, user_turn(1, input_tokens=10_000))
        self.assertEqual(transition.triggers, (CheckpointTrigger.NEW_INPUT_TOKENS,))
        self.assertEqual(transition.checkpoint.delta.input_tokens, 10_000)  # type: ignore[union-attr]

    def test_explicit_and_labeled_topic_transitions_checkpoint(self) -> None:
        state = apply_turn(initial_state("thread-a", "model-a"), user_turn(1, topic="planning")).state
        transition = apply_turn(state, user_turn(2, topic="travel"))
        self.assertIn(CheckpointTrigger.TOPIC_TRANSITION, transition.triggers)

        state = initial_state("thread-b", "model-a")
        transition = apply_turn(state, user_turn(1, topic_transition=True))
        self.assertIn(CheckpointTrigger.TOPIC_TRANSITION, transition.triggers)

    def test_urgent_event_kinds_checkpoint_immediately(self) -> None:
        expected = {
            EventKind.CORRECTION: CheckpointTrigger.IMMEDIATE_CORRECTION,
            EventKind.FORGET_REQUEST: CheckpointTrigger.IMMEDIATE_FORGET_REQUEST,
            EventKind.REVOCATION: CheckpointTrigger.IMMEDIATE_REVOCATION,
            EventKind.COMMITMENT: CheckpointTrigger.IMMEDIATE_COMMITMENT,
            EventKind.MAJOR_DECISION: CheckpointTrigger.IMMEDIATE_MAJOR_DECISION,
        }
        for kind, trigger in expected.items():
            with self.subTest(kind=kind):
                transition = apply_turn(initial_state("thread-a", "model-a"), user_turn(1, event_kind=kind))
                self.assertEqual(transition.triggers[0], trigger)
                self.assertIsNotNone(transition.checkpoint)

    def test_lifecycle_boundaries_checkpoint_when_delta_exists(self) -> None:
        for kind, trigger in (
            (LifecycleKind.THREAD_OPEN, CheckpointTrigger.THREAD_OPEN),
            (LifecycleKind.THREAD_FORK, CheckpointTrigger.THREAD_FORK),
            (LifecycleKind.IDLE, CheckpointTrigger.IDLE_WITH_UNCONSOLIDATED_TURNS),
            (LifecycleKind.BEFORE_AUTOCOMPACT, CheckpointTrigger.BEFORE_AUTOCOMPACT),
        ):
            with self.subTest(kind=kind):
                state = apply_turn(initial_state("thread-a", "model-a"), user_turn(1)).state
                transition = apply_lifecycle_event(state, LifecycleEvent(kind))
                self.assertEqual(transition.triggers, (trigger,))
                self.assertIsNotNone(transition.checkpoint)

    def test_idle_without_delta_does_not_checkpoint(self) -> None:
        state = initial_state("thread-a", "model-a")
        transition = apply_lifecycle_event(state, LifecycleEvent(LifecycleKind.IDLE))
        self.assertIsNone(transition.checkpoint)
        self.assertEqual(transition.triggers, ())

    def test_delta_window_is_read_only_and_hashes_are_deterministic(self) -> None:
        state = apply_turn(initial_state("thread-a", "model-a"), user_turn(1, event_kind=EventKind.COMMITMENT)).state
        checkpoint = state.pending_checkpoint
        self.assertIsNotNone(checkpoint)
        with self.assertRaises(FrozenInstanceError):
            checkpoint.delta.entries = ()  # type: ignore[misc]
        same = apply_turn(initial_state("thread-a", "model-a"), user_turn(1, event_kind=EventKind.COMMITMENT))
        self.assertEqual(checkpoint.idempotency_key, same.checkpoint.idempotency_key)  # type: ignore[union-attr]
        self.assertEqual(checkpoint.delta.end_inclusive.transcript_hash, same.checkpoint.delta.end_inclusive.transcript_hash)  # type: ignore[union-attr]

    def test_pending_checkpoint_is_idempotent_until_an_immediate_event_replaces_it(self) -> None:
        state = apply_turn(initial_state("thread-a", "model-a"), user_turn(1)).state
        first = apply_lifecycle_event(state, LifecycleEvent(LifecycleKind.THREAD_FORK))
        state = first.state
        same = apply_turn(state, user_turn(2))
        self.assertEqual(same.checkpoint.checkpoint_id, first.checkpoint.checkpoint_id)  # type: ignore[union-attr]

        urgent = apply_turn(same.state, user_turn(3, event_kind=EventKind.CORRECTION))
        self.assertNotEqual(urgent.checkpoint.checkpoint_id, first.checkpoint.checkpoint_id)  # type: ignore[union-attr]
        self.assertEqual(urgent.checkpoint.supersedes_checkpoint_id, first.checkpoint.checkpoint_id)  # type: ignore[union-attr]
        self.assertEqual(urgent.checkpoint.delta.end_inclusive.sequence, 3)  # type: ignore[union-attr]

    def test_watermark_does_not_move_before_successful_acknowledgement(self) -> None:
        transition = apply_turn(initial_state("thread-a", "model-a"), user_turn(1, event_kind=EventKind.MAJOR_DECISION))
        checkpoint = transition.checkpoint
        self.assertIsNotNone(checkpoint)
        rejected = acknowledge_checkpoint(
            transition.state,
            PersistenceAcknowledgement(checkpoint.checkpoint_id, checkpoint.idempotency_key, "store-1", False),
        )
        self.assertEqual(rejected.state.durable.watermark.sequence, 0)
        self.assertIsNotNone(rejected.state.pending_checkpoint)

        accepted = acknowledge_checkpoint(
            rejected.state,
            PersistenceAcknowledgement(checkpoint.checkpoint_id, checkpoint.idempotency_key, "store-1", True),
        )
        self.assertEqual(accepted.acknowledgement_status, "accepted")
        self.assertEqual(accepted.state.durable.watermark.sequence, 1)
        self.assertIsNone(accepted.state.pending_checkpoint)

    def test_acknowledgement_is_idempotent_and_wrong_ack_is_ignored(self) -> None:
        transition = apply_turn(initial_state("thread-a", "model-a"), user_turn(1, event_kind=EventKind.COMMITMENT))
        checkpoint = transition.checkpoint
        self.assertIsNotNone(checkpoint)
        wrong = acknowledge_checkpoint(
            transition.state,
            PersistenceAcknowledgement("wrong", checkpoint.idempotency_key, "store", True),
        )
        self.assertEqual(wrong.acknowledgement_status, "ignored")
        accepted = acknowledge_checkpoint(
            transition.state,
            PersistenceAcknowledgement(checkpoint.checkpoint_id, checkpoint.idempotency_key, "store", True),
        )
        duplicate = acknowledge_checkpoint(
            accepted.state,
            PersistenceAcknowledgement(checkpoint.checkpoint_id, checkpoint.idempotency_key, "store", True),
        )
        self.assertEqual(duplicate.acknowledgement_status, "idempotent")

    def test_proposals_cover_admit_quarantine_reject_and_direct_revocation(self) -> None:
        provenance = Provenance(("user-1",), (1,))
        proposals = (
            MemoryProposal("fact", ProposalKind.FACT, "name", "Taylor", provenance, 0.9),
            MemoryProposal("topic", ProposalKind.TOPIC, "work", "HoloChat", provenance, 0.6),
            MemoryProposal("preference", ProposalKind.PREFERENCE, "tone", "short", provenance, 0.2),
            MemoryProposal("forget", ProposalKind.REVOCATION, "old preference", "forget", provenance, 0.0, "memory-1"),
        )
        transition = apply_turn(
            initial_state("thread-a", "model-a"),
            user_turn(1, event_kind=EventKind.FORGET_REQUEST, proposals=proposals),
        )
        decisions = {decision.proposal_id: decision.disposition for decision in transition.checkpoint.decisions}  # type: ignore[union-attr]
        self.assertEqual(decisions["fact"], AdmissionDisposition.ADMIT)
        self.assertEqual(decisions["topic"], AdmissionDisposition.QUARANTINE)
        self.assertEqual(decisions["preference"], AdmissionDisposition.REJECT)
        self.assertEqual(decisions["forget"], AdmissionDisposition.ADMIT)

    def test_out_of_window_provenance_is_rejected(self) -> None:
        proposal = MemoryProposal(
            "bad", ProposalKind.DECISION, "scope", "narrow",
            Provenance(("missing",), (99,)), 1.0,
        )
        transition = apply_turn(
            initial_state("thread-a", "model-a"),
            user_turn(1, event_kind=EventKind.MAJOR_DECISION, proposals=(proposal,)),
        )
        self.assertEqual(transition.checkpoint.decisions[0].disposition, AdmissionDisposition.REJECT)  # type: ignore[union-attr]

    def test_only_admitted_proposals_become_durable_memory(self) -> None:
        provenance = Provenance(("user-1",), (1,))
        proposals = (
            MemoryProposal("fact", ProposalKind.FACT, "name", "Taylor", provenance, 0.9),
            MemoryProposal("low", ProposalKind.FACT, "rumor", "maybe", provenance, 0.1),
        )
        transition = apply_turn(
            initial_state("thread-a", "model-a"),
            user_turn(1, event_kind=EventKind.MAJOR_DECISION, proposals=proposals),
        )
        checkpoint = transition.checkpoint
        acknowledged = acknowledge_checkpoint(
            transition.state,
            PersistenceAcknowledgement(checkpoint.checkpoint_id, checkpoint.idempotency_key, "store", True),  # type: ignore[union-attr]
        )
        self.assertEqual([memory.memory_id for memory in acknowledged.state.durable.memories], ["fact"])

    def test_duplicate_turn_does_not_change_transcript_or_create_a_new_checkpoint(self) -> None:
        state = apply_turn(initial_state("thread-a", "model-a"), user_turn(1)).state
        duplicate = apply_turn(state, user_turn(1))
        self.assertTrue(duplicate.duplicate_event)
        self.assertEqual(len(duplicate.state.rolling.transcript), 1)


if __name__ == "__main__":
    unittest.main()
