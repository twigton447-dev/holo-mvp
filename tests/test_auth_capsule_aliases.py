import bcrypt
import pytest

import auth_capsule


class FakeBrain:
    def __init__(self, capsules=None, contexts=None):
        self._client = object()
        self.capsules = capsules or {}
        self.contexts = contexts or {}
        self.created = []
        self.google_id_lookups = []

    def get_capsule(self, capsule_id):
        return self.capsules.get(capsule_id)

    def get_active_capsule(self, capsule_id):
        return self.capsules.get(capsule_id)

    def identity_maintenance_active(self):
        return False

    def get_capsule_context(self, capsule_id):
        return self.contexts.get(capsule_id, {})

    def get_capsule_by_google_id(self, google_id):
        self.google_id_lookups.append(google_id)
        return None

    def get_or_create_capsule(self, google_id, email, name, avatar_url):
        self.created.append((google_id, email, name, avatar_url))
        return {
            "capsule_id": "new-capsule",
            "email": email,
            "name": name,
            "avatar_url": avatar_url,
            "mode": "personal",
        }

    def set_capsule_context(self, capsule_id, key, value):
        self.contexts.setdefault(capsule_id, {})[key] = value


@pytest.fixture(autouse=True)
def stable_test_jwt_secret(monkeypatch):
    monkeypatch.setattr(auth_capsule, "HOLO_JWT_SECRET", "x" * 32)
    monkeypatch.delenv("HOLOCHAT_ACCOUNT_ALIASES", raising=False)
    monkeypatch.delenv("HOLOCHAT_ALLOW_EPHEMERAL_AUTH", raising=False)
    monkeypatch.delenv("HOLOCHAT_IDENTITY_MAINTENANCE_REQUIRED", raising=False)
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
    monkeypatch.delenv("RAILWAY_PROJECT_ID", raising=False)
    monkeypatch.delenv("HOLOCHAT_AUTH_STRICT_STARTUP", raising=False)


def test_legacy_alias_configuration_is_reported_as_unsafe(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_ACCOUNT_ALIASES", "alias@example.com:canonical-capsule")

    assert auth_capsule.auth_configuration_errors() == [
        "HOLOCHAT_ACCOUNT_ALIASES is unsupported and must be removed"
    ]


def test_weak_jwt_secret_is_reported_as_unsafe(monkeypatch):
    monkeypatch.setattr(auth_capsule, "HOLO_JWT_SECRET", "change-me-in-production")

    assert auth_capsule.auth_configuration_errors() == [
        "HOLO_JWT_SECRET must be a unique value of at least 32 bytes"
    ]


def test_ephemeral_auth_configuration_is_reported_as_unsafe(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_ALLOW_EPHEMERAL_AUTH", "1")

    assert auth_capsule.auth_configuration_errors() == [
        "HOLOCHAT_ALLOW_EPHEMERAL_AUTH must be disabled in deployed environments"
    ]


def test_deployed_runtime_requires_the_identity_maintenance_control(monkeypatch):
    monkeypatch.setenv("RAILWAY_ENVIRONMENT", "production")

    assert auth_capsule.auth_configuration_errors() == [
        "HOLOCHAT_IDENTITY_MAINTENANCE_REQUIRED must be enabled in deployed environments"
    ]


def test_google_signin_never_maps_one_verified_identity_to_another_capsule(monkeypatch):
    brain = FakeBrain(
        capsules={
            "canonical-capsule": {
                "capsule_id": "canonical-capsule",
                "email": "canonical@example.com",
                "name": "Canonical User",
                "mode": "personal",
            }
        }
    )
    monkeypatch.setattr(auth_capsule, "_brain", brain)
    monkeypatch.setenv("HOLOCHAT_ACCOUNT_ALIASES", "alias@example.com:canonical-capsule")
    monkeypatch.setattr(
        auth_capsule,
        "verify_google_token",
        lambda credential: {
            "sub": "google-subject-for-alias-user",
            "email": "alias@example.com",
            "name": "Alias User",
            "picture": "https://example.com/avatar.png",
        },
    )

    result = auth_capsule.handle_google_signin("verified-token")

    assert result["capsule_id"] == "new-capsule"
    assert auth_capsule.decode_capsule_token(result["capsule_token"])["sub"] == "new-capsule"
    assert brain.created == [
        (
            "google-subject-for-alias-user",
            "alias@example.com",
            "Alias User",
            "https://example.com/avatar.png",
        )
    ]


def test_email_signin_never_maps_one_email_to_another_capsule(monkeypatch):
    brain = FakeBrain(
        capsules={"canonical-capsule": {"capsule_id": "canonical-capsule"}}
    )
    monkeypatch.setattr(auth_capsule, "_brain", brain)
    monkeypatch.setenv("HOLOCHAT_ACCOUNT_ALIASES", "alias@example.com:canonical-capsule")

    result = auth_capsule.handle_email_signin(
        "Alias@Example.com",
        "Alias User",
        "correct horse battery staple",
    )

    assert result["capsule_id"] == "new-capsule"
    assert auth_capsule.decode_capsule_token(result["capsule_token"])["sub"] == "new-capsule"
    assert brain.created[0][1:] == ("alias@example.com", "Alias User", "")
    assert brain.created[0][0].startswith("email:")


def test_google_signin_fails_closed_when_persistence_reports_duplicate_identity(monkeypatch):
    class DuplicateIdentityBrain(FakeBrain):
        def get_or_create_capsule(self, *args):
            raise auth_capsule.CapsuleIdentityConflict("duplicate_email_identity")

    monkeypatch.setattr(auth_capsule, "_brain", DuplicateIdentityBrain())
    monkeypatch.setattr(
        auth_capsule,
        "verify_google_token",
        lambda credential: {
            "sub": "google-subject",
            "email": "person@example.com",
            "name": "Person",
            "picture": "",
        },
    )

    with pytest.raises(ValueError, match="duplicate_email_identity"):
        auth_capsule.handle_google_signin("verified-token")


def test_google_signin_never_mints_an_ephemeral_account_when_persistence_is_down(monkeypatch):
    class OfflineBrain:
        _client = None

        def get_or_create_capsule(self, *args):
            raise auth_capsule.CapsulePersistenceError("capsule storage is unavailable")

    monkeypatch.setattr(auth_capsule, "_brain", OfflineBrain())
    monkeypatch.setattr(
        auth_capsule,
        "verify_google_token",
        lambda credential: {
            "sub": "google-subject",
            "email": "person@example.com",
            "name": "Person",
            "picture": "",
        },
    )

    with pytest.raises(ValueError, match="account_persistence_unavailable"):
        auth_capsule.handle_google_signin("verified-token")


def test_google_signin_stops_during_identity_maintenance(monkeypatch):
    class MaintenanceBrain(FakeBrain):
        def assert_identity_signin_available(self):
            raise auth_capsule.CapsuleIdentityConflict("identity_maintenance_in_progress")

    monkeypatch.setattr(auth_capsule, "_brain", MaintenanceBrain())
    monkeypatch.setattr(
        auth_capsule,
        "verify_google_token",
        lambda credential: {
            "sub": "google-subject",
            "email": "person@example.com",
            "name": "Person",
            "picture": "",
        },
    )

    with pytest.raises(ValueError, match="identity_maintenance_in_progress"):
        auth_capsule.handle_google_signin("verified-token")


def test_email_password_cannot_claim_a_google_only_capsule(monkeypatch):
    google_only_capsule = {
        "capsule_id": "google-capsule",
        "google_id": "verified-google-subject",
        "email": "person@example.com",
        "mode": "personal",
    }

    class GoogleOnlyBrain(FakeBrain):
        def get_unique_capsule_by_email(self, email):
            assert email == "person@example.com"
            return google_only_capsule

    brain = GoogleOnlyBrain()
    monkeypatch.setattr(auth_capsule, "_brain", brain)

    with pytest.raises(ValueError, match="account_link_required"):
        auth_capsule.handle_email_signin(
            "person@example.com",
            "Person",
            "correct horse battery staple",
        )

    assert brain.created == []


def test_archived_capsule_token_is_rejected_after_identity_reconciliation(monkeypatch):
    class ArchivedBrain:
        _client = object()

        def get_active_capsule(self, capsule_id):
            assert capsule_id == "merged-capsule"
            return None

    monkeypatch.setattr(auth_capsule, "_brain", ArchivedBrain())
    token = auth_capsule.issue_capsule_token(
        "merged-capsule",
        "person@example.com",
        "personal",
    )

    assert auth_capsule.get_capsule_from_request(f"Bearer {token}") is None


def test_active_capsule_token_is_checked_against_the_durable_identity(monkeypatch):
    class ActiveBrain:
        _client = object()

        def get_active_capsule(self, capsule_id):
            assert capsule_id == "active-capsule"
            return {"capsule_id": capsule_id, "email": "person@example.com", "identity_status": "active"}

    monkeypatch.setattr(auth_capsule, "_brain", ActiveBrain())
    token = auth_capsule.issue_capsule_token(
        "active-capsule",
        "person@example.com",
        "personal",
    )

    assert auth_capsule.get_capsule_from_request(f"Bearer {token}")["sub"] == "active-capsule"


def test_durable_token_fails_closed_when_active_lookup_is_unavailable(monkeypatch):
    class LegacyDurableBrain:
        _client = object()

        def get_capsule(self, capsule_id):
            return {"capsule_id": capsule_id, "email": "person@example.com"}

    monkeypatch.setattr(auth_capsule, "_brain", LegacyDurableBrain())
    token = auth_capsule.issue_capsule_token(
        "legacy-capsule",
        "person@example.com",
        "personal",
    )

    assert auth_capsule.get_capsule_from_request(f"Bearer {token}") is None


def test_durable_token_is_rejected_during_identity_maintenance(monkeypatch):
    class MaintenanceBrain:
        _client = object()

        def identity_maintenance_active(self):
            return True

        def get_active_capsule(self, capsule_id):
            raise AssertionError("maintenance must reject before capsule lookup")

    monkeypatch.setattr(auth_capsule, "_brain", MaintenanceBrain())
    token = auth_capsule.issue_capsule_token(
        "active-capsule",
        "person@example.com",
        "personal",
    )

    assert auth_capsule.get_capsule_from_request(f"Bearer {token}") is None
