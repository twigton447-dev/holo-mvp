from fastapi.testclient import TestClient

import main
from holochat_scope import AccessContext, ScopeKind
from project_brain import ProjectBrain


class _Result:
    def __init__(self, data):
        self.data = data


class _Query:
    def __init__(self, client, table_name):
        self._client = client
        self._table_name = table_name
        self._filters = []
        self._upsert_record = None
        self._delete_requested = False

    def select(self, _columns):
        return self

    def eq(self, key, value):
        self._filters.append((key, value))
        return self

    def limit(self, _count):
        return self

    def upsert(self, record, on_conflict=None):
        self._upsert_record = (dict(record), on_conflict)
        return self

    def delete(self):
        self._delete_requested = True
        return self

    def execute(self):
        rows = self._client.tables.setdefault(self._table_name, [])
        matched = [
            row for row in rows
            if all(row.get(key) == value for key, value in self._filters)
        ]
        if self._upsert_record:
            record, _on_conflict = self._upsert_record
            key = (record.get("scope_id"), record.get("key"))
            for index, existing in enumerate(rows):
                if (existing.get("scope_id"), existing.get("key")) == key:
                    rows[index] = {**existing, **record}
                    break
            else:
                rows.append(record)
            return _Result([record])
        if self._delete_requested:
            self._client.tables[self._table_name] = [row for row in rows if row not in matched]
        return _Result(matched)


class _MemorySupabase:
    def __init__(self, tables):
        self.tables = {name: [dict(row) for row in rows] for name, rows in tables.items()}

    def table(self, name):
        return _Query(self, name)


def test_hybrid_context_defaults_legacy_callers_to_personal_scope(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_HYBRID_SCOPES_ENABLED", "1")
    brain = ProjectBrain.__new__(ProjectBrain)
    brain._client = _MemorySupabase({
        "holo_capsule_principals": [{
            "capsule_id": "capsule-a",
            "personal_scope_id": "personal-a",
        }],
        "holo_capsule_context": [
            {"capsule_id": "capsule-a", "scope_id": "personal-a", "key": "private", "value": "family"},
            {"capsule_id": "capsule-a", "scope_id": "enterprise-a", "key": "work", "value": "valuation"},
            {"capsule_id": "capsule-a", "scope_id": "personal-a", "key": "shared", "value": "personal"},
            {"capsule_id": "capsule-a", "scope_id": "enterprise-a", "key": "shared", "value": "enterprise"},
        ],
    })

    assert brain.get_capsule_context("capsule-a") == {
        "private": "family",
        "shared": "personal",
    }

    brain.set_capsule_context("capsule-a", "password_state", "stored")
    stored = brain.get_capsule_context("capsule-a")
    assert stored["password_state"] == "stored"
    assert "password_state" not in brain.get_capsule_context("capsule-a", scope_id="enterprise-a")

    assert brain.delete_capsule_context("capsule-a", "shared") is True
    assert "shared" not in brain.get_capsule_context("capsule-a")
    assert brain.get_capsule_context("capsule-a", scope_id="enterprise-a")["shared"] == "enterprise"


class _ScopedContextBrain:
    def __init__(self):
        self._client = object()
        self.contexts = {
            "personal-a": {"personal_fact": "private", "shared": "personal"},
            "enterprise-a": {"work_fact": "restricted", "shared": "enterprise"},
        }

    def get_capsule_context(self, capsule_id, *, scope_id=None):
        assert capsule_id == "capsule-a"
        return dict(self.contexts[scope_id])

    def set_capsule_context(self, capsule_id, key, value, *, scope_id=None):
        assert capsule_id == "capsule-a"
        self.contexts[scope_id][key] = value

    def delete_capsule_context(self, capsule_id, key, *, scope_id=None):
        assert capsule_id == "capsule-a"
        return self.contexts[scope_id].pop(key, None) is not None


def test_capsule_context_http_routes_stay_inside_authorized_scope(monkeypatch):
    brain = _ScopedContextBrain()
    monkeypatch.setenv("HOLOCHAT_HYBRID_SCOPES_ENABLED", "1")
    monkeypatch.setattr(main, "_capsule_brain", brain)
    monkeypatch.setattr(main, "get_capsule_from_request", lambda _header: {"sub": "capsule-a"})

    class Resolver:
        def __init__(self, client):
            assert client is brain._client

        def resolve(self, capsule_id, requested_scope_id=None):
            assert capsule_id == "capsule-a"
            scope_id = requested_scope_id or "personal-a"
            kind = ScopeKind.PERSONAL if scope_id == "personal-a" else ScopeKind.ENTERPRISE
            return AccessContext(
                "principal-a",
                scope_id,
                kind,
                tenant_id="tenant-a" if kind is ScopeKind.ENTERPRISE else None,
                membership_id="membership-a" if kind is ScopeKind.ENTERPRISE else None,
            )

    monkeypatch.setattr(main, "HoloChatScopeStore", Resolver)
    client = TestClient(main.app)
    headers = {"Authorization": "Bearer capsule-a"}

    personal = client.get("/v1/capsule/context", headers={**headers, "X-Holo-Scope-Id": "personal-a"})
    enterprise = client.get("/v1/capsule/context", headers={**headers, "X-Holo-Scope-Id": "enterprise-a"})
    assert personal.status_code == 200
    assert personal.json()["context"] == {"personal_fact": "private", "shared": "personal"}
    assert enterprise.status_code == 200
    assert enterprise.json()["context"] == {"work_fact": "restricted", "shared": "enterprise"}

    onboarding_from_enterprise = client.get(
        "/v1/capsule/onboarding",
        headers={**headers, "X-Holo-Scope-Id": "enterprise-a"},
    )
    assert onboarding_from_enterprise.status_code == 409
    assert "HoloPersonal only" in onboarding_from_enterprise.json()["detail"]

    seeded = client.post(
        "/v1/capsule/context",
        headers={**headers, "X-Holo-Scope-Id": "enterprise-a"},
        json={"context": {"memo_state": "draft"}},
    )
    assert seeded.status_code == 200
    assert brain.contexts["enterprise-a"]["memo_state"] == "draft"
    assert "memo_state" not in brain.contexts["personal-a"]

    deleted = client.delete(
        "/v1/capsule/context/shared",
        headers={**headers, "X-Holo-Scope-Id": "personal-a"},
    )
    assert deleted.status_code == 200
    assert "shared" not in brain.contexts["personal-a"]
    assert brain.contexts["enterprise-a"]["shared"] == "enterprise"
