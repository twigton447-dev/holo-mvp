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


def _hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


@pytest.fixture(autouse=True)
def stable_test_jwt_secret(monkeypatch):
    monkeypatch.setattr(auth_capsule, "HOLO_JWT_SECRET", "x" * 32)


def test_account_aliases_parse_multiple_separators(monkeypatch):
    monkeypatch.setenv(
        "HOLOCHAT_ACCOUNT_ALIASES",
        " Alias@Example.com : capsule-1 ; second@example.com:capsule-2\nbad-entry",
    )

    aliases = auth_capsule._account_aliases()

    assert aliases == {
        "alias@example.com": "capsule-1",
        "second@example.com": "capsule-2",
    }


def test_mapped_email_signin_issues_token_for_canonical_capsule(monkeypatch):
    password = "correct horse battery staple"
    brain = FakeBrain(
        capsules={
            "canonical-capsule": {
                "capsule_id": "canonical-capsule",
                "email": "canonical@example.com",
                "mode": "personal",
            }
        },
        contexts={
            "canonical-capsule": {
                "_password_hash": _hash_password(password),
            }
        },
    )
    monkeypatch.setattr(auth_capsule, "_brain", brain)
    monkeypatch.setenv("HOLOCHAT_ACCOUNT_ALIASES", "alias@example.com:canonical-capsule")

    result = auth_capsule.handle_email_signin(
        "Alias@Example.com",
        "Alias User",
        password,
    )

    assert result["capsule_id"] == "canonical-capsule"
    assert result["email"] == "alias@example.com"
    assert auth_capsule.decode_capsule_token(result["capsule_token"])["sub"] == "canonical-capsule"
    assert brain.created == []
    assert brain.google_id_lookups == []


def test_mapped_email_signin_rejects_wrong_canonical_password(monkeypatch):
    brain = FakeBrain(
        capsules={"canonical-capsule": {"capsule_id": "canonical-capsule"}},
        contexts={"canonical-capsule": {"_password_hash": _hash_password("right-password")}},
    )
    monkeypatch.setattr(auth_capsule, "_brain", brain)
    monkeypatch.setenv("HOLOCHAT_ACCOUNT_ALIASES", "alias@example.com:canonical-capsule")

    result = auth_capsule.handle_email_signin(
        "alias@example.com",
        "Alias User",
        "wrong-password",
    )

    assert result is None
    assert brain.created == []
    assert brain.google_id_lookups == []


def test_mapped_email_signin_fails_closed_when_target_missing(monkeypatch):
    brain = FakeBrain()
    monkeypatch.setattr(auth_capsule, "_brain", brain)
    monkeypatch.setenv("HOLOCHAT_ACCOUNT_ALIASES", "alias@example.com:missing-capsule")

    result = auth_capsule.handle_email_signin(
        "alias@example.com",
        "Alias User",
        "any-password",
    )

    assert result is None
    assert brain.created == []
    assert brain.google_id_lookups == []
