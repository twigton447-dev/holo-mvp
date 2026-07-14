from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import chat_engine
import web_search
from chat_engine import HoloChatEngine, _deterministic_search_query
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


class StaticSearchAdapter:
    provider = "native-test"

    def __init__(self, results):
        self.results = results
        self.calls = []

    def is_configured(self):
        return True

    def search(self, query, *, max_results):
        self.calls.append((query, max_results))
        return self.results


def test_deterministic_search_requires_explicit_intent_or_volatile_fact_category():
    assert _deterministic_search_query(
        "Now use everything you know and tell me who I really am."
    ) is None
    assert _deterministic_search_query(
        "That felt blunt. I want the truth right now, but keep it humane."
    ) is None
    assert _deterministic_search_query(
        "A new worker arrived; preserve the conversation context."
    ) is None
    assert _deterministic_search_query(
        "What is the weather in Seattle right now?"
    ) == "What is the weather in Seattle right now?"
    assert _deterministic_search_query(
        "Search the web for official sources about this API."
    ) == "Search the web for official sources about this API."


def _patch_structured_search(monkeypatch, text):
    def fake_run(query):
        if text is None:
            bundle = web_search.build_web_evidence_bundle(
                query, [], provider="test-search", status="no_results", error_category="no_results"
            )
            return web_search.SearchRun(
                query=query, provider="test-search", outcome="no_results",
                latency_ms=0, error_category="no_results", evidence_bundle=bundle,
            )
        bundle = web_search.build_web_evidence_bundle(
            query,
            [{"url": "https://example.test/source", "title": "Test source", "content": text}],
            provider="test-search",
        )
        return web_search.SearchRun(
            query=query, provider="test-search", outcome="checked", latency_ms=0,
            evidence_bundle=bundle,
        )
    monkeypatch.setattr(chat_engine.web_search, "run_search", fake_run)


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
    _patch_structured_search(monkeypatch, "compact search result")
    engine = _engine()

    events = list(engine.stream_message(str(uuid4()), "Should search?"))
    done = next(event for event in events if isinstance(event, dict) and event.get("done"))

    assert any(isinstance(event, dict) and event.get("searching") for event in events)
    assert done["searched"] is True
    assert done["search_query"] == "weather in Seattle"
    assert done["runtime"]["governor_trace"]["web_search"]["source"] == "deterministic_governor"
    assert done["runtime"]["governor_trace"]["web_search"]["status"] == "checked"
    assert done["runtime"]["governor_trace"]["web_search"]["result_count"] == 1
    assert done["runtime"]["gov_arc_state"]["web_decision"] == "checked via deterministic_governor"
    assert done["usage"] == done["runtime"]["usage"]
    assert done["usage"]["input_token_estimate"] == 10
    assert done["usage"]["input_token_source"] == "provider_usage"
    assert done["usage"]["context_budget_input_token_estimate"] == done["context_budget"]["total_token_estimate"]
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
    _patch_structured_search(monkeypatch, None)
    engine = _engine()

    events = list(engine.stream_message(str(uuid4()), "Should search?"))
    done = next(event for event in events if isinstance(event, dict) and event.get("done"))

    assert any(isinstance(event, dict) and event.get("searching") for event in events)
    assert done["searched"] is False
    assert done["search_query"] is None
    assert done["web_status"] == "no_results"
    assert done["runtime"]["governor_trace"]["web_search"]["status"] == "no_results"
    assert done["runtime"]["governor_trace"]["web_search"]["unavailable_reason"] == "no_results"


def test_streaming_skips_failed_mini_before_output(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    _patch_structured_search(monkeypatch, None)
    engine = _engine()
    engine._adapters = [
        FailingStreamAdapter("google", "gemini-2.5-flash-lite"),
        FakeAdapter("openai", "gpt-4o-mini"),
    ]

    events = list(engine.stream_message(str(uuid4()), "Should skip outage?"))
    done = next(event for event in events if isinstance(event, dict) and event.get("done"))

    assert "checked answer" in events
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
    _patch_structured_search(monkeypatch, "compact search result")
    engine = _engine()

    events = list(engine.stream_message(str(uuid4()), "Should search with shadow?"))
    done = next(event for event in events if isinstance(event, dict) and event.get("done"))

    assert done["holo4dna"]["shadow"] is True
    assert done["holo4dna"]["state_id"]
    assert done["holo4dna"]["context_hash"]
    assert done["holo4dna"]["thread_health"]["status"] == "HEALTHY"


def test_non_stream_metadata_includes_searched(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    _patch_structured_search(monkeypatch, "compact search result")
    engine = _engine()

    result = engine.send_message(str(uuid4()), "Should search?")

    assert result["searched"] is True
    assert result["search_query"] == "weather in Seattle"
    assert result["runtime"]["governor_trace"]["web_search"]["attempted"] is True
    assert result["runtime"]["governor_trace"]["web_search"]["source"] == "deterministic_governor"
    assert "compact search result" not in str({k: v for k, v in result.items() if k != "response"})


def test_non_stream_metadata_marks_web_unavailable_when_search_fails(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    _patch_structured_search(monkeypatch, None)
    engine = _engine()

    result = engine.send_message(str(uuid4()), "Should search?")

    assert result["searched"] is False
    assert result["search_query"] is None
    assert result["web_status"] == "no_results"
    assert result["runtime"]["governor_trace"]["web_search"]["status"] == "no_results"


def test_provider_neutral_run_uses_injected_adapter_and_structured_metadata():
    adapter = StaticSearchAdapter([
        web_search.SearchResult(
            url="https://example.com/current?utm_source=test",
            title="Current source",
            snippet="A current fact.",
            score=0.9,
        )
    ])

    run = web_search.run_search("current facts", adapter=adapter)

    assert adapter.calls == [("current facts", 5)]
    assert run.provider == "native-test"
    assert run.outcome == "checked"
    assert run.status == "checked"
    assert run.latency_ms >= 0
    assert run.error_category is None
    assert run.result_count == 1
    assert run.evidence_bundle["sources"][0]["canonical_url"] == "https://example.com/current"
    assert "[S1]" in run.rendered_text


def test_hologov_search_policy_controls_queries_budgets_domains_and_telemetry():
    class PolicyAwareAdapter:
        provider = "policy-test"
        limitations = ("cached_only_not_supported",)

        def __init__(self):
            self.calls = []

        def is_configured(self):
            return True

        def search(self, query, *, max_results, policy):
            self.calls.append((query, max_results, policy.risk_class))
            domain = "allowed.example" if query == "first query" else "excluded.example"
            return [web_search.SearchResult(
                url=f"https://{domain}/{query.replace(' ', '-')}",
                title=query,
                snippet=f"Evidence for {query}",
            )]

    adapter = PolicyAwareAdapter()
    policy = web_search.SearchPolicy(
        queries=("first query", "second query", "third query"),
        allowed_domains=("allowed.example", "excluded.example"),
        excluded_domains=("excluded.example",),
        risk_class="high",
        result_budget=3,
        tool_budget=2,
        live_vs_cached="prefer_cached",
    )

    run = web_search.run_search("fallback query", adapter=adapter, policy=policy)

    assert adapter.calls == [
        ("first query", 3, "high"),
        ("second query", 2, "high"),
    ]
    assert [result.url for result in run.results] == [
        "https://allowed.example/first-query"
    ]
    assert run.tool_call_count == 2
    assert run.provider_limitations == ["cached_only_not_supported"]
    assert run.queries == ["first query", "second query", "third query"]
    assert run.allowed_domains == ["allowed.example", "excluded.example"]
    assert run.excluded_domains == ["excluded.example"]
    assert run.risk_class == "high"
    assert run.result_budget == 3
    assert run.tool_budget == 2
    assert run.live_vs_cached == "prefer_cached"
    assert run.metadata()["queries"] == ["first query", "second query", "third query"]
    assert run.metadata()["search_policy"] == {
        "queries": ["first query", "second query", "third query"],
        "allowed_domains": ["allowed.example", "excluded.example"],
        "excluded_domains": ["excluded.example"],
        "risk_class": "high",
        "result_budget": 3,
        "tool_budget": 2,
        "live_vs_cached": "prefer_cached",
    }


def test_hologov_zero_budgets_prevent_fake_provider_calls():
    class NoCallAdapter(StaticSearchAdapter):
        def search(self, query, *, max_results):
            raise AssertionError("zero Gov budget must prevent provider calls")

    run = web_search.run_search(
        "do not retrieve",
        adapter=NoCallAdapter([]),
        policy=web_search.SearchPolicy(result_budget=0, tool_budget=0),
    )

    assert run.outcome == "no_results"
    assert run.result_budget == 0
    assert run.tool_call_count == 0


def test_openai_search_forwards_supported_policy_without_live_call():
    client = FakeResponsesClient({"output": []})
    policy = web_search.SearchPolicy(
        allowed_domains=("docs.example",),
        excluded_domains=("blocked.example",),
        live_vs_cached="cached_only",
    )

    run = web_search.run_search(
        "official docs",
        adapter=web_search.OpenAIWebSearchAdapter(client=client, model="test"),
        policy=policy,
    )

    assert client.calls[0]["tools"] == [{
        "type": "web_search",
        "filters": {"allowed_domains": ["docs.example"]},
        "external_web_access": False,
    }]
    assert run.tool_call_count == 1
    assert run.provider_limitations == ["excluded_domains_not_supported"]


def test_no_provider_configuration_returns_missing_config_without_provider_call(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    def provider_call(*args, **kwargs):
        raise AssertionError("provider should not be called without configuration")

    monkeypatch.setattr(web_search.TavilySearchAdapter, "search", provider_call)

    run = web_search.run_search("current facts")

    assert run.provider == "tavily"
    assert run.outcome == "missing_config"
    assert run.error_category == "missing_config"
    assert run.result_count == 0
    assert run.evidence_bundle["status"] == "missing_config"
    assert web_search.search("current facts") is None


def test_search_outcomes_distinguish_empty_provider_error_and_rejected_results():
    empty = web_search.run_search("current facts", adapter=StaticSearchAdapter([]))
    assert empty.outcome == "no_results"
    assert empty.error_category == "no_results"

    rejected = web_search.run_search(
        "current facts",
        adapter=StaticSearchAdapter([web_search.SearchResult(url="javascript:alert(1)")]),
    )
    assert rejected.outcome == "all_rejected"
    assert rejected.error_category == "all_rejected"
    assert rejected.evidence_bundle["rejection_reasons"] == ["unsupported_url"]

    class BrokenSearchAdapter(StaticSearchAdapter):
        provider = "broken-test"

        def search(self, query, *, max_results):
            raise RuntimeError("unavailable")

    failed = web_search.run_search("current facts", adapter=BrokenSearchAdapter([]))
    assert failed.outcome == "provider_error"
    assert failed.error_category == "provider_error"
    assert failed.error_type == "RuntimeError"


class FakeResponsesClient:
    def __init__(self, response):
        self.response = response
        self.calls = []
        self.responses = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


def test_openai_and_xai_hosted_search_normalize_sources_without_live_calls():
    response = {
        "output": [
            {
                "type": "web_search_call",
                "action": {"sources": [
                    {"url": "https://example.com/a", "title": "A", "snippet": "alpha"},
                    {"url": "https://example.com/b", "title": "B", "snippet": "beta"},
                ]},
            },
            {
                "type": "message",
                "content": [{"annotations": [
                    {"type": "url_citation", "url": "https://example.com/a", "title": "A duplicate"},
                    {"type": "url_citation", "url": "https://example.com/b", "title": "B"},
                ]}],
            },
        ],
    }
    openai_client = FakeResponsesClient(response)
    xai_client = FakeResponsesClient(response)

    openai_run = web_search.run_search(
        "current facts",
        adapter=web_search.OpenAIWebSearchAdapter(client=openai_client, model="openai-test"),
    )
    xai_run = web_search.run_search(
        "current facts",
        adapter=web_search.XAIWebSearchAdapter(client=xai_client, model="xai-test"),
    )

    assert openai_run.outcome == "checked"
    assert [source["url"] for source in openai_run.evidence_bundle["sources"]] == [
        "https://example.com/a", "https://example.com/b",
    ]
    assert openai_client.calls[0]["tools"] == [{"type": "web_search"}]
    assert openai_client.calls[0]["include"] == ["web_search_call.action.sources"]
    assert xai_run.provider == "xai_web_search"
    assert xai_client.calls[0]["model"] == "xai-test"


def test_gemini_grounding_and_custom_function_search_share_the_evidence_contract():
    class FakeModels:
        def __init__(self):
            self.calls = []

        def generate_content(self, **kwargs):
            self.calls.append(kwargs)
            return SimpleNamespace(candidates=[SimpleNamespace(
                grounding_metadata=SimpleNamespace(grounding_chunks=[
                    SimpleNamespace(web=SimpleNamespace(uri="https://example.org/g", title="Grounded")),
                ], grounding_supports=[
                    SimpleNamespace(
                        grounding_chunk_indices=[0],
                        segment=SimpleNamespace(text="Grounded supporting passage."),
                    ),
                ])
            )])

    models = FakeModels()
    gemini = web_search.GeminiGroundingAdapter(
        client=SimpleNamespace(models=models), model="gemini-test"
    )
    gemini_run = web_search.run_search("ground this", adapter=gemini)
    custom_run = web_search.run_search(
        "deepseek tool query",
        adapter=web_search.CustomFunctionSearchAdapter(
            lambda query, limit: [{"url": "https://example.net/d", "title": query, "content": "Custom retrieved evidence."}],
            provider="deepseek_custom_search",
        ),
    )

    assert gemini_run.evidence_bundle["sources"][0]["url"] == "https://example.org/g"
    assert models.calls[0]["config"] == {"tools": [{"google_search": {}}]}
    assert custom_run.provider == "deepseek_custom_search"
    assert custom_run.outcome == "checked"


def test_search_provider_factory_is_explicit_and_rejects_unknown_values(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_SEARCH_PROVIDER", "openai")
    assert isinstance(web_search.build_search_adapter(), web_search.OpenAIWebSearchAdapter)

    monkeypatch.setenv("HOLOCHAT_SEARCH_PROVIDER", "unsupported")
    try:
        web_search.build_search_adapter()
    except ValueError as exc:
        assert "Unsupported HoloChat search provider" in str(exc)
    else:
        raise AssertionError("unknown providers must fail closed")


def test_malformed_hosted_payload_is_provider_error_not_false_no_results():
    malformed = FakeResponsesClient({"output": {"unexpected": "mapping"}})
    run = web_search.run_search(
        "current facts",
        adapter=web_search.OpenAIWebSearchAdapter(client=malformed, model="test"),
    )

    assert run.outcome == "provider_error"
    assert run.error_type == "SearchPayloadError"


def test_gemini_bare_url_without_grounded_passage_is_rejected():
    response = SimpleNamespace(candidates=[SimpleNamespace(
        grounding_metadata=SimpleNamespace(
            grounding_chunks=[SimpleNamespace(web=SimpleNamespace(
                uri="https://example.org/bare", title="Bare URL",
            ))],
            grounding_supports=[],
        )
    )])
    adapter = web_search.GeminiGroundingAdapter(
        client=SimpleNamespace(models=SimpleNamespace(
            generate_content=lambda **kwargs: response
        )),
        model="gemini-test",
    )

    run = web_search.run_search("ground this", adapter=adapter)
    assert run.outcome == "all_rejected"
    assert run.evidence_bundle["rejection_reasons"] == ["missing_evidence_text"]


def test_unknown_configured_provider_returns_explicit_outcome(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_SEARCH_PROVIDER", "unknown-provider")
    run = web_search.run_search("current facts")
    assert run.outcome == "unsupported_provider"
    assert run.error_category == "unsupported_provider"


def test_deepseek_selection_uses_holochat_custom_retrieval_backend(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_SEARCH_PROVIDER", "deepseek")
    adapter = web_search.build_search_adapter()
    assert isinstance(adapter, web_search.CustomFunctionSearchAdapter)
    assert adapter.provider == "deepseek_custom_search"
    assert adapter.is_configured() is False

    run = web_search.run_search("current facts", adapter=adapter)
    assert run.outcome == "missing_config"
    assert run.tool_call_count == 0
    assert run.provider_limitations == [
        "hosted_web_search_not_available",
        "custom_retrieval_function_required",
    ]


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
    assert '<span id="brand-sub">3.1</span>' in html
    assert 'if (response.status === 404) return true;' in html
    assert "#brand-sub { display: inline;" in html
    assert "<span>My Chats</span>" in html
    assert 'title="My Chats">My Chats</button>' in html
    assert "Library</button>" not in html
    assert "Memory-attached workspace" not in html
    assert "updateRuntimePanel(data)" in html
    assert 'id="runtime-toggle"' not in html
    assert 'id="holobrain-toggle" class="dev-only header-btn header-label-btn"' in html
    assert "Engine data" not in html
    assert "DEV_TOOLS_ENABLED" in html
    assert "window.enableHoloDevTools" in html
    assert "window.disableHoloDevTools" in html
    assert 'title="Open diagnostics"' in html
    assert ">Diagnostics</button>" in html
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


def test_frontend_start_state_is_minimal_and_name_aware():
    html = Path("frontend/chat.html").read_text()

    assert "Hey, ${firstName}, what’s on your mind?" in html
    assert "Hey, what’s on your mind?" in html
    assert 'id="greeting-sub"' in html
    assert "sub.textContent = \"\";" in html
    assert "Holo is here" not in html
    assert "Pick up where you left off" not in html
    assert "What Holo knows" not in html
    assert "<h3>My Context</h3>" in html
    assert 'if (window.matchMedia("(min-width: 701px)").matches) openThreadPanel();' not in html
    assert "if (capsuleToken) openSurfacePanel();" not in html


def test_frontend_thread_meter_uses_thread_health_score():
    html = Path("frontend/chat.html").read_text()
    chat_engine_py = Path("chat_engine.py").read_text()
    main_py = Path("main.py").read_text()

    assert 'id="thread-meter" class="dev-only"' in html
    assert 'id="thread-meter-fill"' in html
    assert 'id="thread-meter-label"' in html
    assert ".dev-only { display: none !important; }" in html
    assert "body.dev-tools #thread-meter.dev-only" in html
    assert "function updateThreadMeter(score)" in html
    assert "updateThreadMeter(doneData.thread_health_score)" in html
    assert "updateThreadMeter(data.thread_health_score)" not in html
    assert "updateThreadMeter(100)" in html
    assert "Thread health ${pct}%" in html
    assert "pct <= 40" in html
    assert "pct <= 20" in html
    assert "Start fresh thread" in html
    assert "startHandoffThread()" in html
    assert 'const HANDOFF_TRANSITION_KEY = "holo_handoff_transition";' in html
    assert "safeHandoffTransition(handoff)" in html
    assert "let _activeHandoffTransition = null;" in html
    assert "function clearActiveHandoffTransition()" in html
    assert "reqBody.handoff_transition = handoffTransitionForTurn" in html
    assert "clearActiveHandoffTransition();" in html
    assert '_safe_handoff_transition(body.get("handoff_transition"))' in main_py
    assert "handoff_transition=handoff_transition" in main_py
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
    assert '<button onclick="toggleIncognito()">Private</button>' in html
    assert '<button onclick="openHoloBrainPanel()">Engine</button>' not in html
    assert "#mobile-action-bar { display: none; }" in html
    assert "#mobile-composer-controls { display: none; }" in html
    assert "#mobile-action-bar,\n      #mobile-composer-controls { display: none !important; }" in html
    assert "#app { width: 100%; max-width: none; margin: 0; }" in html
    assert "#thread-toggle,\n      #new-thread" in html
    assert "display: inline-flex !important;" in html
    assert '#thread-toggle::before { content: "‹";' in html
    assert '#new-thread svg { width: 15px; height: 15px; }' in html
    assert "#holobrain-toggle, #incognito-btn, #theme-toggle { display: none !important; }" in html
    assert '#user-avatar .avatar-placeholder::before' in html
    assert 'content: "•••";' in html
    assert '#avatar-menu .mobile-only { display: block; }' in html
    assert '#avatar-menu .dev-only.mobile-only { display: none !important; }' in html
    assert 'body.dev-tools #avatar-menu .dev-only.mobile-only { display: block !important; }' in html
    assert '<button onclick="closeAvatarMenu();openMemoryPanel()">Memory</button>' in html
    assert '<button onclick="closeAvatarMenu();injectDepthChoice(true)">Depth</button>' in html
    assert '<button class="mobile-only" onclick="closeAvatarMenu();openHoloBrainPanel()">Engine data</button>' not in html
    assert '<button class="mobile-only dev-only" onclick="closeAvatarMenu();openHoloBrainPanel()">Diagnostics</button>' in html
    assert '<button class="mobile-only" onclick="closeAvatarMenu();toggleTheme()">Switch theme</button>' in html
    assert '<button class="mobile-only" onclick="closeAvatarMenu();toggleIncognito()">Private thread</button>' in html
    assert "#incognito-btn, #thread-toggle, #new-thread, #theme-toggle { display: none; }" not in html


def test_frontend_streaming_uses_paced_text_reveal():
    html = Path("frontend/chat.html").read_text()

    assert "const STREAM_PACE_MS = 42;" in html
    assert "const STREAM_MIN_CHARS_PER_TICK = 14;" in html
    assert "const STREAM_MAX_CHARS_PER_TICK = 42;" in html
    assert "function nextStreamTake()" in html
    assert "windowText.lastIndexOf(\". \")" in html
    assert "function createPacedStreamRenderer(bubbleEl)" in html
    assert "pacedStream = createPacedStreamRenderer(bubbleEl);" in html
    assert "pacedStream.push(evt.text);" in html
    assert "if (pacedStream) await pacedStream.drain();" in html
    assert "bubbleEl.innerHTML = renderMarkdown(accumulated);" not in html


def test_frontend_stream_disconnect_does_not_replay_paid_turn():
    html = Path("frontend/chat.html").read_text()
    send_message = html.split("async function sendMessage()", 1)[1].split(
        "function createStreamingBubble()", 1
    )[0]

    assert send_message.count('fetch("/v1/chat/stream",') == 1
    assert 'fetch("/v1/chat",' not in send_message
    assert "if (!streamOk)" in send_message
    assert 'throw new Error("Invalid stream event.")' in send_message
    assert 'streamError = "Connection interrupted before the response was complete.' in send_message
    assert "appendError(streamError, retryTurn)" in send_message
    assert "restoreDraft();" in send_message
    assert 'title = "Retry message"' in html


def test_frontend_uses_editorial_reader_typography_without_heavy_default_bold():
    html = Path("frontend/chat.html").read_text()

    assert "--reader-font: Georgia, 'Times New Roman', Times, serif;" in html
    assert ".holo-body .bubble { font-family: var(--reader-font); font-size: 18.5px; font-weight: 390;" in html
    assert "text-shadow: 0 1px 0 rgba(255,255,255,0.035)" in html
    assert ".holo-body strong { font-weight: 600;" in html
    assert "rgba(91,122,229,0.18)" in html
    assert ".holo-body em { font-style: italic; color: #c9c2b6;" in html
    assert ".holo-body blockquote { border-left: 2px solid var(--accent);" in html
    assert "box-shadow: inset 10px 0 22px rgba(91,122,229,0.06);" in html
    assert ".holo-body ul { list-style: none;" in html
    assert ".holo-body ol { list-style: none; counter-reset: holo-list;" in html
    assert ".holo-body ul li::before" in html
    assert ".holo-body ol li::before" in html
    assert ".inline-next-step:hover" in html
    assert ".holo-body .bubble" in html
    assert "font-weight: 500; line-height: 1.82" not in html


def test_frontend_streaming_keeps_reader_anchored_at_message_top():
    html = Path("frontend/chat.html").read_text()

    assert 'msg.className = "msg holo streaming";' in html
    assert 'scrollMessageTopIntoReadingPosition(holoEl, "smooth");' in html
    assert 'function scrollMessageTopIntoReadingPosition(msgEl, behavior = "auto")' in html
    assert "function preserveMessageTopAfterRender(msgEl, previousTop)" in html
    assert "preserveMessageTopAfterRender(msgEl, anchorTop);" in html
    renderer = html[
        html.index("function createPacedStreamRenderer"):
        html.index("function finalizeStreamingBubble")
    ]
    assert "scrollToBottom()" not in renderer


def test_holochat_runtime_prompt_prefers_structured_human_answers():
    prompt = Path("llm_adapters.py").read_text()
    doctrine = Path("docs/holo_chat_doctrine.md").read_text()
    gov_doctrine = Path("docs/gov_chat_doctrine.md").read_text()

    assert "Sound human in the ordinary sense" in prompt
    assert "conversational presence first" in prompt
    assert "voice must never become a memo, report, performance, or UI script" in prompt
    assert "short **bold section header**" in prompt
    assert "create a scan anchor only where it helps" in prompt
    assert "Use bullets when they create momentum" in prompt
    assert "choose the person over the format" in prompt
    assert 'Do not append a visible "Next-step suggestions" menu' in prompt
    assert "[[HOLO_CONVERSATION_PATHS]]" in prompt
    assert "one should pressure-test an assumption or missing risk" in prompt
    assert "Do not leave complex answers as one flat wall of prose" in prompt
    assert "Format guidance for this response: use short **bold headers**" in prompt
    assert "If a sentence could appear in a generic AI demo" in prompt
    assert "Do not force the person's situation into a clean revelation" in prompt
    assert "Anger, hesitation, correction, or resistance is not evidence" in prompt
    assert "identify who actually has decision rights" in prompt
    assert "never generate a plausible memory audit" in prompt
    assert "No bullets. No headers." not in prompt
    assert "Holo should feel like a vivid, attentive person" in doctrine
    assert "For complex answers, structure is a kindness." in doctrine
    assert "At least one path should pressure-test" in doctrine
    assert "I want you to do a deep calibration pass on me." in doctrine
    assert "inspiring, creative, pragmatic, and hopeful" in doctrine
    assert "imaginative without becoming vague" in doctrine
    assert "Gov should preserve warm precision" in gov_doctrine
    assert "warm precision path" in gov_doctrine
    assert "three most useful continuations" in prompt
    assert "Holo can offer after this exact answer" in prompt
    assert "Each path must contain a concrete noun or verb" in prompt
    assert "no generic phrases like 'go deeper'" in prompt


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


def test_frontend_onboarding_depth_choice_is_consent_first_and_revocable():
    html = Path("frontend/chat.html").read_text()
    main_py = Path("main.py").read_text()
    chat_engine_py = Path("chat_engine.py").read_text()
    brain_py = Path("project_brain.py").read_text()

    assert "How deep should Holo know you?" in html
    assert "Surface</strong>" in html
    assert "Personal</strong>" in html
    assert "Deep</strong>" in html
    assert "By choosing Personal or Deep you are confirming you understand what will be asked and stored." in html
    assert "Skip any question." in html
    assert "Do not include passwords, financial account numbers, medical records" in html
    assert "If anything here feels like too much, just say so and we’ll stop or go lighter." in html
    assert "holo_depth_preference" in html
    assert "holo_depth_consent_v1" in html
    assert "holo_seed_personal_v1" in html
    assert "holo_seed_deep_v1" in html
    assert "maybePromptDepthChoice();" in html
    assert "maybePromptDepthChoiceOnLaunch();" in html
    assert "renderRecentThemes(userName);" in html
    assert "editMemoryEntry" in html
    assert "deleteMemoryEntry" in html
    assert 'method: "DELETE"' in html
    assert '@app.delete("/v1/capsule/context/{key}")' in main_py
    assert "delete_capsule_context" in brain_py
    assert "_capsule_context_for_depth_preference" in chat_engine_py
    assert 'key_str == "holo_seed_deep_v1" and preference != "deep"' in chat_engine_py
    assert 'key_str == "holo_seed_personal_v1" and preference == "surface"' in chat_engine_py
    assert "value_limit = 3000" in main_py
    assert "delete_capsule_context(capsule" in main_py
    assert "Ask your favorite chatbot to create a memory seed profile for HoloChat." not in html
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
    assert "const suggestionBlockPattern" in html
    assert "Thread (?:battery|power)" in html
    assert 'class="inline-next-step" onclick="useChip(this)"' in html
    assert 'aria-label="Next-step suggestions"' in html
    assert "inline-next-num" in html
    assert "Name the real decision underneath this" not in html
    assert "Turn the strongest insight into one next move" not in html
    assert "Check the assumption this answer depends on" not in html
    assert 'if (!paths.length) return "";' in html
    assert "renderConversationPaths(suggestions)" in html


def test_worker_conversation_paths_are_extracted_and_never_released():
    from chat_engine import _extract_worker_conversation_paths

    response = """A useful answer with a real point.

[[HOLO_CONVERSATION_PATHS]]
1. Which family expectation needs a concrete boundary before the pilot begins?
2. Draft the smallest paid pilot that protects time and preserves honest evidence.
3. What changes if uncertainty is treated as information instead of a veto?
[[/HOLO_CONVERSATION_PATHS]]"""

    clean, paths = _extract_worker_conversation_paths(response)

    assert clean == "A useful answer with a real point."
    assert paths == [
        "Which family expectation needs a concrete boundary before the pilot begins?",
        "Draft the smallest paid pilot that protects time and preserves honest evidence.",
        "What changes if uncertainty is treated as information instead of a veto?",
    ]
    assert "HOLO_CONVERSATION_PATHS" not in clean


def test_malformed_worker_conversation_paths_fail_closed():
    from chat_engine import _extract_worker_conversation_paths

    clean, paths = _extract_worker_conversation_paths(
        "Visible answer.\n[[HOLO_CONVERSATION_PATHS]]\n1. Truncated metadata"
    )

    assert clean == "Visible answer."
    assert paths == []
