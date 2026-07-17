from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import main
from db import Database
from project_brain import CapsuleIdentityConflict, CapsulePersistenceError, ProjectBrain


class _Query:
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name
        self.filters = {}

    def select(self, _columns):
        return self

    def eq(self, key, value):
        self.filters[key] = value
        self.client.filters.append((self.table_name, key, value))
        return self

    def limit(self, _value):
        return self

    def order(self, *_args, **_kwargs):
        return self

    def execute(self):
        if self.client.error:
            raise self.client.error
        return SimpleNamespace(data=self.client.rows_for(self.table_name, self.filters))


class _Client:
    def __init__(self, *, api_key=None, capsules=None, error=None):
        self.api_key = api_key
        self.capsules = capsules or {}
        self.error = error
        self.filters = []

    def table(self, table_name):
        return _Query(self, table_name)

    def rows_for(self, table_name, filters):
        if table_name == "api_keys":
            return [self.api_key] if self.api_key else []
        if table_name == "holo_capsules":
            capsule_id = filters.get("capsule_id")
            capsule = self.capsules.get(capsule_id)
            return [capsule] if capsule else []
        return []


def _database(client):
    database = Database.__new__(Database)
    database.client = client
    return database


def test_capsule_bound_api_key_requires_an_active_capsule():
    client = _Client(
        api_key={"capsule_id": "active", "max_requests_per_minute": 60},
        capsules={"active": {"capsule_id": "active", "identity_status": "active"}},
    )

    database = _database(client)

    assert database.validate_api_key("holo_sk_test") == {
        "capsule_id": "active",
        "max_requests_per_minute": 60,
    }
    assert database.get_capsule_id_for_key("holo_sk_test") == "active"


def test_archived_capsule_api_key_is_rejected_even_when_key_is_marked_active():
    client = _Client(
        api_key={"capsule_id": "merged", "max_requests_per_minute": 60},
        capsules={"merged": {"capsule_id": "merged", "identity_status": "merged"}},
    )

    database = _database(client)

    assert database.validate_api_key("holo_sk_stale") is None
    assert database.get_capsule_id_for_key("holo_sk_stale") is None


def test_legacy_unbound_internal_key_does_not_attempt_capsule_lookup():
    client = _Client(api_key={"max_requests_per_minute": 60})

    assert _database(client).validate_api_key("internal-key") == {
        "max_requests_per_minute": 60,
    }
    assert not [item for item in client.filters if item[0] == "holo_capsules"]


def test_identity_maintenance_lookup_fails_closed_after_feature_is_enabled(monkeypatch):
    brain = ProjectBrain.__new__(ProjectBrain)
    brain._client = _Client(error=RuntimeError("relation unavailable"))
    monkeypatch.setenv("HOLOCHAT_IDENTITY_MAINTENANCE_REQUIRED", "1")

    with pytest.raises(CapsulePersistenceError, match="identity maintenance control is unavailable"):
        brain.identity_maintenance_active()


def test_missing_maintenance_control_row_fails_closed_after_feature_is_enabled(monkeypatch):
    brain = ProjectBrain.__new__(ProjectBrain)
    brain._client = _Client()
    monkeypatch.setenv("HOLOCHAT_IDENTITY_MAINTENANCE_REQUIRED", "1")

    with pytest.raises(CapsulePersistenceError, match="identity maintenance control is unavailable"):
        brain.identity_maintenance_active()


def test_identity_maintenance_lookup_remains_off_only_before_feature_enablement(monkeypatch):
    brain = ProjectBrain.__new__(ProjectBrain)
    brain._client = _Client(error=RuntimeError("relation unavailable"))
    monkeypatch.delenv("HOLOCHAT_IDENTITY_MAINTENANCE_REQUIRED", raising=False)

    assert brain.identity_maintenance_active() is False


def test_capsule_email_lookup_uses_exact_canonical_equality(monkeypatch):
    brain = ProjectBrain.__new__(ProjectBrain)
    client = _Client()
    brain._client = client

    assert brain.get_capsules_by_email(" Person_Name%Test@Example.com ") == []
    assert ("holo_capsules", "email", "person_name%test@example.com") in client.filters


def test_google_signin_never_auto_links_a_legacy_capsule_by_email(monkeypatch):
    brain = ProjectBrain.__new__(ProjectBrain)
    brain._client = _Client()
    legacy_capsule = {
        "capsule_id": "legacy-capsule",
        "google_id": "email:person@example.com",
        "email": "person@example.com",
        "identity_status": "active",
    }
    monkeypatch.setattr(
        brain,
        "get_capsules_by_email",
        lambda _email: [legacy_capsule],
    )

    with pytest.raises(CapsuleIdentityConflict, match="account_link_required"):
        brain.get_or_create_capsule(
            "verified-google-subject",
            "person@example.com",
            "Person",
            "",
        )


def test_api_traffic_fails_closed_when_required_maintenance_control_cannot_be_checked(monkeypatch):
    class BrokenMaintenanceBrain:
        _client = object()

        def identity_maintenance_active(self):
            raise RuntimeError("database unavailable")

    monkeypatch.setattr(main, "_capsule_brain", BrokenMaintenanceBrain())
    monkeypatch.setenv("HOLOCHAT_IDENTITY_MAINTENANCE_REQUIRED", "1")

    with pytest.raises(HTTPException) as exc_info:
        main._require_identity_maintenance_clear()

    assert exc_info.value.status_code == 503
