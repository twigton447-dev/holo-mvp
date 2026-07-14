import pytest

from holochat_scope import ScopeKind
from holochat_scope_store import HoloChatScopeStore, ScopeResolutionError


class Result:
    def __init__(self, data):
        self.data = data


class Query:
    def __init__(self, rows):
        self.rows = list(rows)
        self.filters = []

    def select(self, columns):
        return self

    def eq(self, key, value):
        self.filters.append((key, value))
        return self

    def limit(self, count):
        return self

    def execute(self):
        rows = [row for row in self.rows if all(row.get(key) == value for key, value in self.filters)]
        return Result(rows[:1])


class Client:
    def __init__(self, tables):
        self.tables = tables

    def table(self, name):
        return Query(self.tables.get(name, []))


def _store(*, active=True):
    return HoloChatScopeStore(Client({
        "holo_capsule_principals": [{
            "capsule_id": "cap-a", "principal_id": "principal-a", "personal_scope_id": "personal-a",
        }],
        "holo_scopes": [
            {"scope_id": "personal-a", "scope_kind": "personal", "owner_principal_id": "principal-a", "tenant_id": None, "disabled_at": None},
            {"scope_id": "personal-b", "scope_kind": "personal", "owner_principal_id": "principal-b", "tenant_id": None, "disabled_at": None},
            {"scope_id": "work-a", "scope_kind": "enterprise", "owner_principal_id": None, "tenant_id": "tenant-a", "disabled_at": None},
        ],
        "holo_tenant_memberships": [{
            "membership_id": "member-a", "tenant_id": "tenant-a", "principal_id": "principal-a",
            "roles": ["member", "researcher"], "authz_version": 4,
            "status": "active" if active else "suspended",
        }],
    }))


def test_default_scope_is_the_principals_personal_scope():
    access = _store().resolve("cap-a")
    assert access.scope_id == "personal-a"
    assert access.scope_kind is ScopeKind.PERSONAL
    assert access.principal_id == "principal-a"
    assert access.workspace_id is None


def test_active_membership_authorizes_enterprise_scope_with_server_roles():
    access = _store().resolve("cap-a", "work-a")
    assert access.scope_kind is ScopeKind.ENTERPRISE
    assert access.tenant_id == "tenant-a"
    assert access.membership_id == "member-a"
    assert access.roles == ("member", "researcher")
    assert access.authz_version == 4
    assert access.workspace_id is None


def test_other_personal_scope_and_inactive_enterprise_membership_are_denied():
    with pytest.raises(ScopeResolutionError, match="another principal"):
        _store().resolve("cap-a", "personal-b")
    with pytest.raises(ScopeResolutionError, match="active enterprise membership"):
        _store(active=False).resolve("cap-a", "work-a")


def test_client_cannot_invent_a_scope_or_unmapped_capsule():
    with pytest.raises(ScopeResolutionError, match="unavailable"):
        _store().resolve("cap-a", "made-up")
    with pytest.raises(ScopeResolutionError, match="no principal mapping"):
        _store().resolve("cap-unknown")


def test_malformed_membership_authority_is_denied():
    store = _store()
    store._client.tables["holo_tenant_memberships"][0]["roles"] = "member"

    with pytest.raises(ScopeResolutionError, match="authority is invalid"):
        store.resolve("cap-a", "work-a")
