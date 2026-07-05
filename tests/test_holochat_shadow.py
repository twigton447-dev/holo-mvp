import json
from dataclasses import dataclass
from uuid import uuid4

from chat_engine import HoloChatEngine
from holo_context import HoloContextBuilder
from holo_router import HoloRouter


@dataclass
class FakeAdapter:
    provider: str
    model_id: str

    def chat_call(self, system_prompt, history, user_message, temperature, images=None):
        return "shadow-safe answer", 10, 4


class FakeGovernor:
    provider = "hologov"
    model_id = "hologov-model"

    def prepare_for_turn(self, adapter):
        self.provider = "hologov"
        self.model_id = "hologov-model"

    def lock_to_provider(self, provider):
        self.provider = provider or "hologov"

    def assess_chat_temperature(self, user_message, history):
        return 0.3

    def should_search(self, user_message, history):
        return None

    def surface_thought(self, history, capsule_context, baton_pass=None):
        return "private thought"

    def assess_tenor(self, history, capsule_context, **kwargs):
        return "answer normally"

    def verify_claims(self, response_text, search_fn):
        return response_text, []

    def extract_context_updates(self, history, capsule_context):
        return {"preference": "concise"}


class FakeBrain:
    def __init__(self):
        self.context_updates = {}
        self.saved_turns = []

    def load_chat_history(self, session_id):
        return []

    def get_capsule_context(self, capsule_id):
        return {"api_key": "secret-value", "project": "holo"}

    def load_life_context(self, capsule_id):
        return [{"category": "work", "key": "style", "value": "direct"}]

    def load_last_consolidation(self, capsule_id):
        return {"open_threads": ["wire 4DNA shadow"]}

    def set_capsule_context(self, capsule_id, key, value):
        self.context_updates[key] = value

    def append_session_history(self, capsule_id, session_id, user_message):
        pass

    def save_chat_turn(self, **kwargs):
        self.saved_turns.append(kwargs)


def _fake_engine(adapter_count=1):
    adapters = [
        FakeAdapter(provider=f"provider{i}", model_id=f"model{i}")
        for i in range(adapter_count)
    ]
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = adapters
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._holo_context_builder = HoloContextBuilder()
    engine._holo_router = HoloRouter(adapters, env={})
    return engine


def test_holo4dna_shadow_metadata_is_flagged_and_non_behavioral(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_4DNA_SHADOW", "1")
    monkeypatch.setenv("HOLOCHAT_4DNA_ENABLED", "0")
    engine = _fake_engine()

    result = engine.send_message(
        str(uuid4()),
        "Map the next shadow step.",
        capsule_id="capsule-shadow",
    )

    assert result["response"] == "shadow-safe answer"
    assert result["_provider"] == "provider0"
    assert result["holo4dna"]["shadow"] is True
    assert result["holo4dna"]["enabled"] is False
    assert result["holo4dna"]["route"]["runtime_analyst"] == {
        "provider": "provider0",
        "model": "model0",
    }
    assert result["holo4dna"]["route"]["shadow_route"] is True
    assert result["holo4dna"]["context_hash"]
    assert "base_system_prompt" in result["holo4dna"]["context"]["included_blocks"]
    assert engine._brain.saved_turns[0]["provider"] == "provider0"


def test_holo4dna_shadow_is_default_off(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.delenv("HOLOCHAT_4DNA_ENABLED", raising=False)
    engine = _fake_engine()

    result = engine.send_message(str(uuid4()), "No shadow by default.")

    assert "holo4dna" not in result


def test_holo4dna_shadow_metadata_excludes_raw_secret_values(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_4DNA_SHADOW", "1")
    engine = _fake_engine(adapter_count=2)

    result = engine.send_message(
        str(uuid4()),
        "This turn has memory context.",
        capsule_id="capsule-shadow",
    )

    encoded_metadata = json.dumps(result["holo4dna"], sort_keys=True)
    assert "secret-value" not in encoded_metadata
    assert "api_key" not in encoded_metadata
    assert result["holo4dna"]["thread_health"]["status"] == "HEALTHY"
