from types import SimpleNamespace

import chat_engine
from chat_engine import (
    ChatSession,
    _advance_memory_steward,
    _claim_autocompact_for_context_window,
)
from holochat_memory_steward import MemoryStewardState
from holochat_memory_steward import TurnInput, apply_exchange, initial_state


class CheckpointBrain:
    def __init__(self, persistence_id="stored-checkpoint"):
        self.persistence_id = persistence_id
        self.calls = []

    def persist_memory_checkpoint(self, **kwargs):
        self.calls.append(kwargs)
        return self.persistence_id


def plan_with_memory_proposals(*proposals):
    return SimpleNamespace(narrative_packet={
        "memory_admission_proposals": list(proposals),
        "active_threads": [],
        "topic_events": [],
    })


def advance(monkeypatch, message, *, plan=None, brain=None, session=None, context_budget=None):
    monkeypatch.setenv("HOLOCHAT_MEMORY_STEWARD_ENABLED", "1")
    return _advance_memory_steward(
        session=session or ChatSession("steward-runtime", owner_capsule_id="cap", owner_scope_id="scope"),
        brain=brain or CheckpointBrain(),
        capsule_id="cap",
        scope_id="scope",
        user_message=message,
        response_text="A grounded worker response.",
        gov_turn_plan=plan or plan_with_memory_proposals(),
        context_budget=context_budget or {},
    )


def test_commitment_checkpoint_persists_then_advances_watermark(monkeypatch):
    brain = CheckpointBrain()
    session = ChatSession("commitment", owner_capsule_id="cap", owner_scope_id="scope")
    session.turn_count = 1

    trace = advance(monkeypatch, "I will call the clinic tomorrow.", brain=brain, session=session)

    assert len(brain.calls) == 1
    assert trace["persistence_acknowledged"] is True
    assert trace["pending_checkpoint"] is False
    assert trace["watermark_sequence"] == 2
    assert brain.calls[0]["payload"]["delta"]["entries"][0]["message_id"] == "commitment:user:1"


def test_failed_checkpoint_persistence_keeps_pending_and_blocks_autocompact(monkeypatch):
    brain = CheckpointBrain(persistence_id=None)
    session = ChatSession("failed", owner_capsule_id="cap", owner_scope_id="scope")
    session.turn_count = 1

    trace = advance(monkeypatch, "I decided this is the final plan.", brain=brain, session=session)

    assert trace["pending_checkpoint"] is True
    assert trace["watermark_sequence"] == 0
    session.history = [{"role": "user", "content": "x" * 160_000}]
    assert _claim_autocompact_for_context_window(
        session,
        capsule_id="cap",
        incognito=False,
    ) is False


def test_unresolved_forget_and_correction_do_not_claim_durable_success(monkeypatch):
    for message in (
        "Forget the old address.",
        "Actually, that project status is wrong.",
    ):
        brain = CheckpointBrain()
        session = ChatSession(message, owner_capsule_id="cap", owner_scope_id="scope")
        session.turn_count = 1
        trace = advance(monkeypatch, message, brain=brain, session=session)

        assert brain.calls == []
        assert trace["unresolved_urgent_memory_target"] is True
        assert trace["pending_checkpoint"] is True
        assert trace["watermark_sequence"] == 0


def test_unresolved_urgent_checkpoint_stays_blocked_on_later_normal_turn(monkeypatch):
    brain = CheckpointBrain()
    session = ChatSession("urgent-stays-blocked", owner_capsule_id="cap", owner_scope_id="scope")
    session.turn_count = 1
    advance(monkeypatch, "Forget the old address.", brain=brain, session=session)
    session.turn_count = 2

    trace = advance(monkeypatch, "Let us discuss something else.", brain=brain, session=session)

    assert brain.calls == []
    assert session.memory_steward_persistence_blocked is True
    assert trace["pending_checkpoint"] is True


def test_grounded_forget_proposal_is_persisted_as_revocation(monkeypatch):
    message = "Forget the old address."
    plan = plan_with_memory_proposals({
        "operation": "forget",
        "target_memory_id": "address-old",
        "key": "address",
        "evidence": "Forget the old address.",
    })
    brain = CheckpointBrain()
    session = ChatSession("forget", owner_capsule_id="cap", owner_scope_id="scope")
    session.turn_count = 1

    trace = advance(monkeypatch, message, plan=plan, brain=brain, session=session)

    assert trace["unresolved_urgent_memory_target"] is False
    assert trace["persistence_acknowledged"] is True
    proposal = brain.calls[0]["payload"]["proposals"][0]
    assert proposal["kind"] == "revocation"
    assert proposal["target_memory_id"] == "address-old"


def test_grounded_correction_supersedes_the_old_memory(monkeypatch):
    message = "Actually, the launch date is August 20."
    plan = plan_with_memory_proposals({
        "operation": "correct",
        "target_memory_id": "launch-date-old",
        "key": "launch_date",
        "value": "The launch date is August 20.",
        "evidence": "Actually, the launch date is August 20.",
    })
    brain = CheckpointBrain()
    session = ChatSession("correction", owner_capsule_id="cap", owner_scope_id="scope")
    session.turn_count = 1

    trace = advance(monkeypatch, message, plan=plan, brain=brain, session=session)

    assert trace["unresolved_urgent_memory_target"] is False
    proposal = next(
        item for item in brain.calls[0]["payload"]["proposals"]
        if item["kind"] == "supersession"
    )
    assert proposal["target_memory_id"] == "launch-date-old"


def test_restored_uncheckpointed_history_triggers_thread_open_checkpoint(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_MEMORY_STEWARD_ENABLED", "1")
    from holochat_memory_steward import TurnInput, restore_state

    session = ChatSession("opened", owner_capsule_id="cap", owner_scope_id="scope")
    session.turn_count = 2
    session.memory_steward_state = restore_state(
        "opened",
        "hologov-canonical",
        (
            TurnInput("old-user", "user", "Earlier context"),
            TurnInput("old-worker", "assistant", "Earlier answer"),
        ),
        watermark_sequence=0,
        watermark_hash="",
    )
    brain = CheckpointBrain()

    trace = advance(monkeypatch, "Continue from there.", brain=brain, session=session)

    assert "thread_open" in trace["triggers"]
    assert brain.calls[0]["payload"]["delta"]["end_inclusive"]["sequence"] == 2


def test_explicit_thread_fork_lifecycle_persists_without_provider_call(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_MEMORY_STEWARD_ENABLED", "1")
    brain = CheckpointBrain()
    engine = chat_engine.HoloChatEngine.__new__(chat_engine.HoloChatEngine)
    engine._brain = brain
    session = ChatSession("fork-lifecycle", owner_capsule_id="cap", owner_scope_id="scope")
    session.memory_steward_state = apply_exchange(
        initial_state("fork-lifecycle", "hologov-canonical"),
        TurnInput("fork-user", "user", "Unconsolidated context"),
        TurnInput("fork-worker", "assistant", "A response"),
    ).state
    chat_engine._sessions[session.session_id] = session

    result = engine.checkpoint_memory_lifecycle(
        session.session_id,
        "thread_fork",
        capsule_id="cap",
        scope_id="scope",
    )

    assert result["status"] == "persisted"
    assert result["lifecycle"] == "thread_fork"
    assert result["watermark_sequence"] == 2
    assert len(brain.calls) == 1


def test_idle_sweeper_checkpoints_only_due_sessions(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_MEMORY_STEWARD_ENABLED", "1")
    brain = CheckpointBrain()
    engine = chat_engine.HoloChatEngine.__new__(chat_engine.HoloChatEngine)
    engine._brain = brain
    due = ChatSession("idle-due", owner_capsule_id="cap", owner_scope_id="scope")
    due.last_active = 100.0
    due.memory_steward_state = apply_exchange(
        initial_state("idle-due", "hologov-canonical"),
        TurnInput("idle-user", "user", "Unconsolidated context"),
        TurnInput("idle-worker", "assistant", "A response"),
    ).state
    fresh = ChatSession("idle-fresh", owner_capsule_id="cap", owner_scope_id="scope")
    fresh.last_active = 950.0
    fresh.memory_steward_state = due.memory_steward_state
    chat_engine._sessions[due.session_id] = due
    chat_engine._sessions[fresh.session_id] = fresh

    results = engine.checkpoint_idle_sessions(idle_seconds=500, now=1000.0)

    assert [item["session_id"] for item in results] == ["idle-due"]
    assert results[0]["lifecycle"] == "idle"
    assert len(brain.calls) == 1


def test_restart_restores_acknowledged_watermark(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_MEMORY_STEWARD_ENABLED", "1")

    class RestartBrain:
        def get_chat_session(self, session_id):
            return {"session_id": session_id, "capsule_id": "cap", "scope_id": "scope"}

        def load_chat_history(self, session_id, **kwargs):
            return [
                {"role": "user", "content": "First turn"},
                {"role": "assistant", "content": "First answer"},
            ]

        def load_latest_memory_checkpoint(self, **kwargs):
            return {"end_sequence": 2, "transcript_hash": "durable-hash"}

    engine = chat_engine.HoloChatEngine.__new__(chat_engine.HoloChatEngine)
    engine._brain = RestartBrain()
    engine._adapters = [SimpleNamespace(provider="openai")]
    session_id = "restart-memory-steward"
    chat_engine._sessions.pop(session_id, None)

    session = engine.get_or_create_session(
        session_id,
        capsule_id="cap",
        scope_id="scope",
    )

    assert isinstance(session.memory_steward_state, MemoryStewardState)
    assert session.memory_steward_state.durable.watermark.sequence == 2
    assert session.memory_steward_state.durable.watermark.transcript_hash == "durable-hash"
    assert len(session.memory_steward_state.rolling.transcript) == 2
