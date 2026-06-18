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
    assert done["usage"] == done["runtime"]["usage"]
    assert done["usage"]["input_token_estimate"] == done["context_budget"]["total_token_estimate"]
    assert done["usage"]["input_token_source"] == "context_budget_estimate"
    assert done["usage"]["output_token_estimate"] == 4
    assert done["usage"]["output_token_source"] == "provider_usage"
    assert done["usage"]["latency_ms"] >= 0
    assert done["usage"]["estimated_cost_usd"] is None
    assert done["usage"]["cost_source"] == "unknown_pricing"
    assert done["usage"]["cost_is_estimate"] is True
    assert "compact search result" not in str(done)
    assert "holo4dna" not in done


def test_streaming_done_metadata_marks_web_unavailable_when_search_fails(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setattr(chat_engine.web_search, "search", lambda query: None)
    engine = _engine()

    events = list(engine.stream_message(str(uuid4()), "Should search?"))
    done = next(event for event in events if isinstance(event, dict) and event.get("done"))

    assert any(isinstance(event, dict) and event.get("searching") for event in events)
    assert done["searched"] is False
    assert done["search_query"] is None
    assert done["web_status"] == "unavailable"


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


def test_non_stream_metadata_marks_web_unavailable_when_search_fails(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setattr(chat_engine.web_search, "search", lambda query: None)
    engine = _engine()

    result = engine.send_message(str(uuid4()), "Should search?")

    assert result["searched"] is False
    assert result["search_query"] is None
    assert result["web_status"] == "unavailable"


def test_frontend_has_web_checked_render_path():
    html = Path("frontend/chat.html").read_text()

    assert "Web checked" in html
    assert "Web: unavailable" in html
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

    assert "<span>HoloChat</span>" in html
    assert '<span id="brand-sub">4DNA</span>' in html
    assert "Memory-attached workspace" not in html
    assert "updateRuntimePanel(data)" in html
    assert 'id="runtime-toggle"' in html
    assert 'id="runtime-panel"' in html
    assert "Runtime/System" in html
    assert "renderRuntimeRail(data)" not in html
    assert "runtimeRailHtml" not in html
    assert "runtime-pill" not in html
    for label in (
        "Runtime",
        "This turn",
        "Mode",
        "serial, one analyst per turn",
        "Selection",
        "Active pool",
        "Governor",
        "Governor mode",
        "Context delivery",
        "Full memory to analyst",
        "Memory store",
        "State object",
        "Baton Pass",
        "Holo4DNA",
        "AutoReseed",
        "Estimated input tokens",
        "Estimated output tokens",
        "Estimated total tokens",
        "Latency",
        "Estimated cost",
        "Cost source",
        "Pricing estimate",
        "exact provider billing may differ",
    ):
        assert label in html

    assert "Meet Holo Chat 1.1" not in html
    assert ("top 3 " + "frontier models") not in html
    assert ("Three " + "models") not in html
    assert ("three models " + "one mind") not in html.lower()
    assert ("rotating " + "analyst") not in html.lower()
    assert ("4DNA " + "active") not in html
    assert ("full lossless " + "memory") not in html.lower()
    assert ("AutoReseed: " + "active") not in html
    assert ("actual " + "billed cost") not in html.lower()
    assert ("raw " + "prompt") not in html.lower()
    assert ("provider request " + "body") not in html.lower()


def test_frontend_header_avatar_has_safe_account_tooltip_and_hidden_count_badge():
    html = Path("frontend/chat.html").read_text()

    assert 'title="Signed-in capsule"' in html
    assert 'aria-label="Signed-in capsule"' in html
    assert 'id="memory-badge" style="display:none"' in html
    assert 'badge.style.display = "none";' in html
    assert "badge.textContent = count" not in html
    assert 'title="${name}"' not in html


def test_frontend_onboarding_memory_seed_prompt_is_safe_and_specific():
    html = Path("frontend/chat.html").read_text()

    assert "Ask your favorite chatbot to create a memory seed profile for HoloChat." in html
    assert "detailed and nuanced operating profile" in html
    assert "Aim for about 1,000 words" in html
    assert "Do not include passwords, account numbers" in html
    assert "Do not include secrets or highly sensitive information." in html
    assert "how I like an AI assistant to help me" in html
    assert "what an AI assistant should avoid doing with me" in html
    assert "Copy prompt" in html
    assert "You can edit it before saving." in html
    assert "Meet Holo Chat 1.1" not in html
    assert "Why Holo?" not in html
    assert "What is Holo Chat?" not in html
    assert "Coming next:" not in html

    assert "everything you tell me" not in html
    assert "full context" not in html
    assert "emotional patterns" not in html
    assert "analyze my soul" not in html
    assert "everything you know" not in html


def test_frontend_assistant_messages_do_not_render_runtime_metadata_inline():
    html = Path("frontend/chat.html").read_text()

    assert "${webCheckedHtml}" in html
    assert "${runtimeRailHtml}" not in html
    assert "trust-row runtime-rail" not in html
    assert "updateRuntimePanel(data);" in html


def test_frontend_assistant_messages_render_three_conversation_paths():
    html = Path("frontend/chat.html").read_text()

    assert 'aria-label="Conversation paths"' in html
    assert "function normalizeConversationPaths(suggestions)" in html
    assert "suggestions: suggestions.slice(0, 3)" in html
    assert "Go deeper on this" in html
    assert "Turn this into a concrete plan" in html
    assert "Explore a different angle" in html
    assert "renderConversationPaths(suggestions)" in html
