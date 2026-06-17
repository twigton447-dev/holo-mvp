from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import chat_engine
from chat_engine import HoloChatEngine
from holo_context import HoloContextBuilder
from holo_router import HoloRouter


@dataclass
class FakeAdapter:
    provider: str = "provider0"
    model_id: str = "model0"

    def chat_call(self, system_prompt, history, user_message, temperature, images=None):
        return "checked answer", 10, 4

    def stream_chat_call(self, system_prompt, history, user_message, temperature, images=None):
        yield "checked "
        yield "answer"
        yield {"done": True, "in_tok": 10, "out_tok": 4}


class SearchGovernor:
    provider = "governor"
    model_id = "governor-model"

    def prepare_for_turn(self, adapter):
        self.provider = "governor"

    def lock_to_provider(self, provider):
        self.provider = provider or "governor"

    def assess_chat_temperature(self, user_message, history):
        return 0.2

    def should_search(self, user_message, history):
        return "weather in Seattle"

    def surface_thought(self, history, capsule_context, baton_pass=None):
        return None

    def assess_tenor(self, history, capsule_context, **kwargs):
        return None

    def verify_claims(self, response_text, search_fn):
        return response_text, []

    def extract_context_updates(self, history, capsule_context):
        return {}


class FakeBrain:
    def load_chat_history(self, session_id):
        return []

    def get_capsule_context(self, capsule_id):
        return {}

    def load_life_context(self, capsule_id):
        return []

    def load_last_consolidation(self, capsule_id):
        return None

    def set_capsule_context(self, capsule_id, key, value):
        pass

    def append_session_history(self, capsule_id, session_id, user_message):
        pass

    def save_chat_turn(self, **kwargs):
        pass


def _engine():
    adapters = [FakeAdapter()]
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = adapters
    engine._bench = []
    engine._governor = SearchGovernor()
    engine._brain = FakeBrain()
    engine._holo_context_builder = HoloContextBuilder()
    engine._holo_router = HoloRouter(adapters, env={})
    return engine


def test_streaming_done_metadata_includes_searched_without_raw_results(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setattr(chat_engine.web_search, "search", lambda query: "compact search result")
    engine = _engine()

    events = list(engine.stream_message(str(uuid4()), "Should search?"))
    done = next(event for event in events if isinstance(event, dict) and event.get("done"))

    assert any(isinstance(event, dict) and event.get("searching") for event in events)
    assert done["searched"] is True
    assert done["search_query"] == "weather in Seattle"
    assert "compact search result" not in str(done)
    assert "holo4dna" not in done


def test_streaming_done_metadata_includes_shadow_holo4dna_when_enabled(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_4DNA_SHADOW", "1")
    monkeypatch.setattr(chat_engine.web_search, "search", lambda query: "compact search result")
    engine = _engine()

    events = list(engine.stream_message(str(uuid4()), "Should search with shadow?"))
    done = next(event for event in events if isinstance(event, dict) and event.get("done"))

    assert done["holo4dna"]["shadow"] is True
    assert done["holo4dna"]["state_id"]
    assert done["holo4dna"]["context_hash"]
    assert done["holo4dna"]["thread_health"]["status"] == "HEALTHY"


def test_non_stream_metadata_includes_searched(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setattr(chat_engine.web_search, "search", lambda query: "compact search result")
    engine = _engine()

    result = engine.send_message(str(uuid4()), "Should search?")

    assert result["searched"] is True
    assert result["search_query"] == "weather in Seattle"
    assert "compact search result" not in str({k: v for k, v in result.items() if k != "response"})


def test_frontend_has_web_checked_render_path():
    html = Path("frontend/chat.html").read_text()

    assert "Web checked" in html
    assert "renderWebCheckedIndicator(data)" in html
    assert "finalizeStreamingBubble(holoEl, doneData.response || accumulated, doneData)" in html
    assert "data-search-query" in html


def test_frontend_message_copy_has_fallback_and_targets_response_bubbles():
    html = Path("frontend/chat.html").read_text()

    assert "async function copyMsg(id, btn)" in html
    assert "el.innerText || el.textContent" in html
    assert "async function copyReadableText(text)" in html
    assert "function copyTextFallback(text)" in html
    assert "document.execCommand(\"copy\")" in html
    assert "onclick=\"copyMsg('${responseId}', this)\"" in html


def test_frontend_runtime_rail_uses_truthful_serial_labels():
    html = Path("frontend/chat.html").read_text()

    assert "renderRuntimeRail(data)" in html
    for label in (
        "Runtime:",
        "This turn:",
        "Mode: ${modeLabel}",
        "serial, one analyst per turn",
        "Selection:",
        "Active pool:",
        "Governor:",
        "Governor mode:",
        "Context delivery:",
        "Full memory to analyst:",
        "HoloBrain:",
        "State object:",
        "Baton Pass:",
        "Holo4DNA:",
        "AutoReseed:",
    ):
        assert label in html

    assert "Memory-attached workspace" in html
    assert "one selected analyst model" in html
    assert ("top 3 " + "frontier models") not in html
    assert ("Three " + "models") not in html
    assert ("three models " + "one mind") not in html.lower()
    assert ("rotating " + "analyst") not in html.lower()
    assert ("4DNA " + "active") not in html
    assert ("full lossless " + "memory") not in html.lower()
    assert ("AutoReseed: " + "active") not in html
