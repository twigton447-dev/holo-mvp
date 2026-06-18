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


class FailingStreamAdapter(FakeAdapter):
    def stream_chat_call(self, system_prompt, history, user_message, temperature, images=None):
        raise RuntimeError("provider body should not surface")
        yield


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

    def generate_conversation_paths(self, **kwargs):
        return [
            "Trace the exact Gov calls that run before the answer",
            "Compare Gov-as-mind against deterministic Python control",
            "Design the dashboard view for topic transitions",
        ]


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
    assert done["runtime"]["governor_trace"]["web_search"]["source"] == "governor"
    assert done["runtime"]["governor_trace"]["web_search"]["status"] == "checked"
    assert done["runtime"]["governor_trace"]["web_search"]["result_count"] == 1
    assert done["runtime"]["gov_arc_state"]["web_decision"] == "checked via governor"
    assert done["usage"] == done["runtime"]["usage"]
    assert done["usage"]["input_token_estimate"] == done["context_budget"]["total_token_estimate"]
    assert done["usage"]["input_token_source"] == "context_budget_estimate"
    assert done["usage"]["output_token_estimate"] == 4
    assert done["usage"]["output_token_source"] == "provider_usage"
    assert done["usage"]["latency_ms"] >= 0
    assert done["usage"]["estimated_cost_usd"] is None
    assert done["usage"]["cost_source"] == "unknown_pricing"
    assert done["usage"]["cost_is_estimate"] is True
    timing = done["runtime"]["timing_breakdown"]
    assert timing["total_server_ms"] >= 0
    assert timing["governor_pre_ms"] >= 0
    assert timing["analyst_ms"] >= 0
    assert timing["governor_post_ms"] >= 0
    assert timing["primary_time_owner"] in {
        "memory",
        "governor",
        "web",
        "analyst",
        "persistence",
    }
    assert done["conversation_paths"] == [
        "Trace the exact Gov calls that run before the answer",
        "Compare Gov-as-mind against deterministic Python control",
        "Design the dashboard view for topic transitions",
    ]
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
    assert done["runtime"]["governor_trace"]["web_search"]["status"] == "unavailable"
    assert done["runtime"]["governor_trace"]["web_search"]["unavailable_reason"] in {
        "missing_config",
        "no_results_or_search_failed",
    }


def test_streaming_skips_failed_mini_before_output(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setattr(chat_engine.web_search, "search", lambda query: None)
    engine = _engine()
    engine._adapters = [
        FailingStreamAdapter("google", "gemini-2.5-flash-lite"),
        FakeAdapter("openai", "gpt-4o-mini"),
    ]

    events = list(engine.stream_message(str(uuid4()), "Should skip outage?"))
    done = next(event for event in events if isinstance(event, dict) and event.get("done"))

    assert "checked " in events
    assert done["_provider"] == "openai"
    failover = done["runtime"]["failover"]
    assert failover["attempted"] is True
    assert failover["count"] == 1
    assert failover["skipped"] == [
        {
            "provider": "google",
            "model": "gemini-2.5-flash-lite",
            "error_type": "RuntimeError",
        }
    ]
    runtime_text = str(done["runtime"]).lower()
    assert "provider body should not surface" not in runtime_text
    assert ("raw " + "prompt") not in runtime_text


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
    assert result["runtime"]["governor_trace"]["web_search"]["attempted"] is True
    assert result["runtime"]["governor_trace"]["web_search"]["source"] == "governor"
    assert "compact search result" not in str({k: v for k, v in result.items() if k != "response"})


def test_non_stream_metadata_marks_web_unavailable_when_search_fails(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setattr(chat_engine.web_search, "search", lambda query: None)
    engine = _engine()

    result = engine.send_message(str(uuid4()), "Should search?")

    assert result["searched"] is False
    assert result["search_query"] is None
    assert result["web_status"] == "unavailable"
    assert result["runtime"]["governor_trace"]["web_search"]["status"] == "unavailable"


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
    assert 'id="runtime-toggle"' not in html
    assert 'id="holobrain-toggle"' in html
    assert "Engine data" in html
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
        "Frontier assist",
        "Frontier assist pool",
        "Governor",
        "Governor mode",
        "Context delivery",
        "Full memory to analyst",
        "Memory store",
        "State object",
        "Gov Arc State",
        "Baton Pass",
        "Holo4DNA",
        "AutoReseed",
        "Analyst failover",
        "Failover policy",
        "Final analyst",
        "Frontier assist status",
        "Frontier assist reason",
        "Frontier assist model",
        "Gov temperature",
        "Gov web decision",
        "Web decision source",
        "Web attempted",
        "Web provider",
        "Web result count",
        "Web status",
        "Web unavailable reason",
        "Gov claim check",
        "Gov memory extraction",
        "Gov memory writes",
        "Gov paths",
        "Gov thread health",
        "Gov current topic",
        "Gov topic shift",
        "Gov directive",
        "Gov arc web",
        "Gov arc memory",
        "Gov next paths",
        "Gov arc confidence",
        "Time owner",
        "Turn total",
        "Memory/context time",
        "Gov pre-read time",
        "Web/search time",
        "Prompt assembly time",
        "Analyst generation time",
        "Gov post-check time",
        "Persistence time",
        "Timing note",
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


def test_frontend_thread_meter_uses_thread_health_score():
    html = Path("frontend/chat.html").read_text()
    chat_engine_py = Path("chat_engine.py").read_text()

    assert 'id="thread-meter"' in html
    assert 'id="thread-meter-fill"' in html
    assert 'id="thread-meter-label"' in html
    assert "function updateThreadMeter(score)" in html
    assert "updateThreadMeter(doneData.thread_health_score)" in html
    assert "updateThreadMeter(data.thread_health_score)" in html
    assert "updateThreadMeter(100)" in html
    assert "Thread health ${pct}%" in html
    assert "pct <= 40" in html
    assert "pct <= 20" in html
    assert "Start fresh thread" in html
    assert "startHandoffThread()" in html
    assert 'const HANDOFF_TRANSITION_KEY = "holo_handoff_transition";' in html
    assert "safeHandoffTransition(handoff)" in html
    assert "Continuing: ${escHtml(topic)}" in html
    assert "You were working through ${escHtml(topic)}." in html
    assert "A useful next move:" in html
    assert "selected memory and context available here" in html
    assert "Fresh thread, same workspace." in html
    assert ("Start a " + "fresh one") not in html
    assert ("full " + "context") not in html.lower()
    assert ("everything " + "you tell me") not in html.lower()
    assert ("how much context " + "do you want carried") not in chat_engine_py
    assert ("Full detail, " + "key points only") not in chat_engine_py


def test_frontend_header_avatar_has_safe_account_tooltip_and_hidden_count_badge():
    html = Path("frontend/chat.html").read_text()

    assert 'title="Signed-in capsule"' in html
    assert 'aria-label="Signed-in capsule"' in html
    assert 'id="memory-badge" style="display:none"' in html
    assert 'badge.style.display = "none";' in html
    assert "badge.textContent = count" not in html
    assert 'title="${name}"' not in html


def test_mobile_header_keeps_core_controls_available():
    html = Path("frontend/chat.html").read_text()

    assert 'id="mobile-action-bar" aria-label="Mobile chat controls"' in html
    assert 'id="mobile-composer-controls" aria-label="Mobile composer controls"' in html
    assert '<button onclick="toggleThreadPanel()">Threads</button>' in html
    assert '<button onclick="newThread()">New</button>' in html
    assert '<button onclick="openHoloBrainPanel()">Engine</button>' in html
    assert '<button onclick="toggleIncognito()">Incognito</button>' in html
    assert "#mobile-action-bar { display: none; }" in html
    assert "#mobile-composer-controls { display: none; }" in html
    assert "#mobile-action-bar,\n      #mobile-composer-controls { display: none !important; }" in html
    assert "#app { width: 100%; max-width: none; margin: 0; }" in html
    assert "#thread-toggle,\n      #new-thread" in html
    assert "display: inline-flex !important;" in html
    assert '#thread-toggle::before { content: "‹";' in html
    assert '#new-thread::before { content: "✎";' in html
    assert "#holobrain-toggle, #incognito-btn, #theme-toggle { display: none !important; }" in html
    assert '#user-avatar .avatar-placeholder::before' in html
    assert 'content: "•••";' in html
    assert '#avatar-menu .mobile-only { display: block; }' in html
    assert '<button class="mobile-only" onclick="closeAvatarMenu();toggleThreadPanel()">See my threads</button>' in html
    assert '<button class="mobile-only" onclick="closeAvatarMenu();newThread()">Start new thread</button>' in html
    assert '<button class="mobile-only" onclick="closeAvatarMenu();openHoloBrainPanel()">Engine data</button>' in html
    assert '<button class="mobile-only" onclick="closeAvatarMenu();toggleIncognito()">Start incognito thread</button>' in html
    assert "#incognito-btn, #thread-toggle, #new-thread, #theme-toggle { display: none; }" not in html


def test_frontend_streaming_uses_paced_text_reveal():
    html = Path("frontend/chat.html").read_text()

    assert "const STREAM_PACE_MS = 26;" in html
    assert "const STREAM_CHARS_PER_TICK = 3;" in html
    assert "function createPacedStreamRenderer(bubbleEl)" in html
    assert "pacedStream = createPacedStreamRenderer(bubbleEl);" in html
    assert "pacedStream.push(evt.text);" in html
    assert "if (pacedStream) await pacedStream.drain();" in html
    assert "bubbleEl.innerHTML = renderMarkdown(accumulated);" not in html


def test_holochat_runtime_prompt_prefers_structured_human_answers():
    prompt = Path("llm_adapters.py").read_text()
    doctrine = Path("docs/holo_chat_doctrine.md").read_text()
    gov_doctrine = Path("docs/gov_chat_doctrine.md").read_text()

    assert "Sound human in the ordinary sense" in prompt
    assert "short **bold section headers**" in prompt
    assert "Do not leave complex answers as one flat wall of prose" in prompt
    assert "Format guidance for this response: use short **bold headers**" in prompt
    assert "If a sentence could appear in a generic AI demo" in prompt
    assert "No bullets. No headers." not in prompt
    assert "Holo should feel like a vivid, attentive person" in doctrine
    assert "For complex answers, structure is a kindness." in doctrine
    assert "At least one path should pressure-test" in doctrine
    assert "I want you to do a deep calibration pass on me." in doctrine
    assert "inspiring, creative, pragmatic, and hopeful" in doctrine
    assert "imaginative without becoming vague" in doctrine
    assert "Gov should push harder than a normal assistant." in gov_doctrine
    assert "pressure path" in gov_doctrine


def test_frontend_google_auth_is_config_gated():
    html = Path("frontend/chat.html").read_text()
    main_py = Path("main.py").read_text()

    assert '"google_auth_enabled"' in main_py
    assert "HOLOCHAT_GOOGLE_AUTH_ENABLED" in main_py
    assert 'id="google-auth-block" style="display:none;' in html
    assert "_googleAuthEnabled = cfg.google_auth_enabled === true;" in html
    assert "if (!_googleAuthEnabled || !_gsiReady || !_googleClientId || !window.google) return;" in html


def test_password_reset_sender_uses_hologroup_domain():
    auth_py = Path("auth_capsule.py").read_text()

    assert "noreply@hologroup.io" in auth_py
    assert "noreply@hololgroup.io" not in auth_py


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

    assert ("everything " + "you tell me") not in html
    assert ("full " + "context") not in html
    assert ("emotional " + "patterns") not in html
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
    assert "data.conversation_paths || suggestions" in html
    assert "function normalizeConversationPaths(suggestions)" in html
    assert "suggestions: suggestions.slice(0, 3)" in html
    assert "Go deeper on this" in html
    assert "Turn this into a concrete plan" in html
    assert "Explore a different angle" in html
    assert "renderConversationPaths(suggestions)" in html
