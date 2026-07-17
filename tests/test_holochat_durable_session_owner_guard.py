from __future__ import annotations

from types import SimpleNamespace

from project_brain import ProjectBrain


class _Query:
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name
        self.filters = {}

    def select(self, _columns):
        self.client.reads.append(self.table_name)
        return self

    def eq(self, key, value):
        self.filters[key] = value
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, _value):
        return self

    def execute(self):
        rows = [
            row for row in self.client.rows.get(self.table_name, [])
            if all(row.get(key) == value for key, value in self.filters.items())
        ]
        return SimpleNamespace(data=rows)


class _Client:
    def __init__(self):
        self.reads: list[str] = []
        self.rows = {
            "holo_chat_sessions": [
                {"session_id": "owner-session", "capsule_id": "capsule-a", "title": "A"},
                {"session_id": "other-session", "capsule_id": "capsule-b", "title": "B"},
            ],
            "holo_chat_messages": [
                {"session_id": "owner-session", "role": "user", "content": "owned"},
                {"session_id": "other-session", "role": "user", "content": "private"},
            ],
        }

    def table(self, table_name):
        return _Query(self, table_name)


def _brain() -> tuple[ProjectBrain, _Client]:
    brain = ProjectBrain.__new__(ProjectBrain)
    client = _Client()
    brain._client = client
    return brain, client


def test_history_loader_never_reads_a_foreign_session_transcript(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_HYBRID_SCOPES_ENABLED", raising=False)
    brain, client = _brain()

    assert brain.load_chat_history("other-session", capsule_id="capsule-a") is None
    assert client.reads == ["holo_chat_sessions"]


def test_history_loader_reads_only_the_authenticated_capsules_session(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_HYBRID_SCOPES_ENABLED", raising=False)
    brain, client = _brain()

    assert brain.load_chat_history("owner-session", capsule_id="capsule-a") == [
        {"role": "user", "content": "owned"}
    ]
    assert client.reads == ["holo_chat_sessions", "holo_chat_messages"]


def test_session_bound_writes_refuse_a_foreign_capsule(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_HYBRID_SCOPES_ENABLED", raising=False)
    brain, client = _brain()

    brain.save_chat_turn(
        "other-session",
        1,
        "attempted write",
        "must not persist",
        "test",
        0.0,
        capsule_id="capsule-a",
    )
    brain.save_consolidation("capsule-a", "other-session", {"captain_note": "blocked"})
    artifact = brain.save_artifact(
        "capsule-a",
        "other-session",
        1,
        "blocked",
        "must not persist",
    )

    assert artifact is None
    assert client.reads
    assert set(client.reads) == {"holo_chat_sessions"}
