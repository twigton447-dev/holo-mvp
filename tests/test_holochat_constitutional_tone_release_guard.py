from uuid import uuid4

import chat_engine
from chat_engine import HoloChatEngine, _runtime_metadata
from holochat_constitution import HOLOCHAT_CONSTITUTIONAL_TONE_LAW
from holochat_context_governor import deterministic_visible_release
from llm_adapters import GOVERNOR_SYSTEM_PROMPT, HOLO_CHAT_SYSTEM_PROMPT


class CapturingAdapter:
    provider = "openai"
    model_id = "gpt-5.5"

    def __init__(self, response="Warm answer."):
        self.response = response
        self.last_system_prompt = ""

    def chat_call(self, system_prompt, history, user_message, temperature, images=None):
        self.last_system_prompt = system_prompt
        return self.response, 3, 2

    def stream_chat_call(self, system_prompt, history, user_message, temperature, images=None):
        self.last_system_prompt = system_prompt
        for chunk in self.response.split("|"):
            yield chunk
        yield {"done": True, "in_tok": 3, "out_tok": 2}


class ConstitutionalAdvisor:
    provider = "xai"
    model_id = "grok-4.3"

    def __init__(self, *, tenor=None, thought=None):
        self.tenor = tenor
        self.thought = thought

    def prepare_for_turn(self, adapter):
        self.provider = "xai"

    def lock_to_provider(self, provider):
        self.provider = provider or "xai"

    def assess_chat_temperature(self, user_message, history):
        return 0.8

    def should_search(self, user_message, history):
        return None

    def surface_thought(self, history, capsule_context, baton_pass=None):
        return self.thought

    def assess_tenor(self, history, capsule_context, **kwargs):
        return self.tenor

    def verify_claims(self, response_text, search_fn):
        return response_text, []

    def extract_context_updates(self, history, capsule_context):
        return {}

    def generate_conversation_paths(self, **kwargs):
        return []


class CapsuleBrain:
    def __init__(self):
        self.saved_turns = []

    def load_chat_history(self, session_id):
        return []

    def get_capsule_context(self, capsule_id):
        return {
            "project_context": "Randall asked Holo to preserve warmth and stop scolding behavior.",
        }

    def load_life_context(self, capsule_id):
        return []

    def load_last_consolidation(self, capsule_id):
        return None

    def set_capsule_context(self, capsule_id, key, value):
        pass

    def append_session_history(self, capsule_id, session_id, user_message):
        pass

    def save_chat_turn(self, **kwargs):
        self.saved_turns.append(kwargs)

    def save_artifact(self, **kwargs):
        return "artifact-1"


def _engine(adapter, advisor, brain=None):
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._runtime_profile = "mini_only"
    engine._adapters = [adapter]
    engine._bench = []
    engine._gov_advisor = advisor
    engine._governor = advisor
    engine._brain = brain or CapsuleBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None
    return engine


def test_worker_and_governor_prompts_contain_constitutional_tone_law():
    assert "HOLOCHAT CONSTITUTIONAL TONE LAW" in HOLO_CHAT_SYSTEM_PROMPT
    assert "HOLOCHAT CONSTITUTIONAL TONE LAW" in GOVERNOR_SYSTEM_PROMPT
    assert "Never scold, shame, punish" in HOLO_CHAT_SYSTEM_PROMPT
    assert "warm collaborative precision only" in GOVERNOR_SYSTEM_PROMPT
    assert "Gov should push harder than a normal assistant." not in GOVERNOR_SYSTEM_PROMPT
    assert "at least one path should be a pressure path" not in GOVERNOR_SYSTEM_PROMPT


def test_captain_brief_in_actual_worker_prompt_carries_constitution(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter()
    advisor = ConstitutionalAdvisor(
        tenor="Clarify the assumption, but do it warmly and collaboratively."
    )
    engine = _engine(adapter, advisor)

    engine.send_message(str(uuid4()), "Help me think this through.", capsule_id="cap-1")

    assert "CAPTAIN BRIEF - READ + DIRECTIVE" in adapter.last_system_prompt
    assert HOLOCHAT_CONSTITUTIONAL_TONE_LAW in adapter.last_system_prompt
    assert "Clarify the assumption" in adapter.last_system_prompt


def test_hostile_visible_output_is_repaired_without_echoing_prosecution():
    decision = deterministic_visible_release(
        "Help me understand this.",
        "You need to admit you obviously ignored the real issue.",
    )

    assert decision.repaired is True
    assert decision.release is True
    assert "need to admit" not in decision.text
    assert "obviously ignored" not in decision.text
    assert "without making you feel prosecuted" in decision.text


def test_streaming_buffers_until_constitutional_release_guard(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter(response="You need |to admit you ignored this.")
    engine = _engine(adapter, ConstitutionalAdvisor())

    events = list(engine.stream_message(str(uuid4()), "Please answer plainly."))
    text_events = [event for event in events if isinstance(event, str)]

    assert "You need " not in text_events
    assert "to admit you ignored this." not in text_events
    assert len(text_events) == 1
    assert "without making you feel prosecuted" in text_events[0]
    assert events[-1]["done"] is True


def test_surface_thought_metadata_is_admitted_before_ui_exposure(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter()
    advisor = ConstitutionalAdvisor(
        thought={"text": "You need to admit you are being evasive.", "color": "red"}
    )
    engine = _engine(adapter, advisor)
    session_id = str(uuid4())
    session = engine.get_or_create_session(session_id)
    session.history = [
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "second"},
        {"role": "user", "content": "third"},
        {"role": "assistant", "content": "fourth"},
    ]

    result = engine.send_message(session_id, "What now?", capsule_id="cap-2")

    assert result["thought"] is None


def test_capsule_memory_reaches_prompt_as_grounding_not_accusation(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter()
    advisor = ConstitutionalAdvisor(
        tenor="Use the supplied capsule context as continuity, not as a verdict about Randall."
    )
    engine = _engine(adapter, advisor, CapsuleBrain())

    engine.send_message(str(uuid4()), "Continue from context.", capsule_id="cap-3")

    assert "Randall asked Holo to preserve warmth" in adapter.last_system_prompt
    assert "HoloBrain memory grounds continuity" in adapter.last_system_prompt
    assert "must never become accusatory theory" in adapter.last_system_prompt
