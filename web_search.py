"""Provider-neutral web-search transport for HoloChat.

``run_search`` is the structured transport used by the chat engine.  The
``search`` function remains a deliberately thin text compatibility wrapper for
older callers; it does not retain per-request state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
import os
from time import perf_counter
from typing import Any, Callable, Mapping, Protocol, Sequence

from holochat_evidence import build_web_evidence_bundle, render_web_evidence


logger = logging.getLogger("holo.search")

SEARCH_OUTCOMES = {
    "missing_config",
    "no_results",
    "provider_error",
    "all_rejected",
    "checked",
    "unsupported_provider",
}


class SearchPayloadError(ValueError):
    """Raised when a hosted search response no longer matches its contract."""


@dataclass(frozen=True)
class SearchResult:
    """One provider-normalized result, independent of the search vendor."""

    url: str
    title: str = ""
    snippet: str = ""
    score: float | None = None
    published_at: str | None = None
    provider_metadata: dict[str, Any] = field(default_factory=dict)

    def as_evidence_record(self) -> dict[str, Any]:
        record: dict[str, Any] = {
            "url": self.url,
            "title": self.title,
            "content": self.snippet,
        }
        if self.score is not None:
            record["score"] = self.score
        if self.published_at is not None:
            record["published_at"] = self.published_at
        return record


class SearchAdapter(Protocol):
    """Adapter seam for Tavily and future native provider search APIs."""

    provider: str

    def is_configured(self) -> bool:
        ...

    def search(self, query: str, *, max_results: int) -> Sequence[SearchResult]:
        ...


class TavilySearchAdapter:
    """The current default adapter; kept behind the provider-neutral seam."""

    provider = "tavily"

    def is_configured(self) -> bool:
        return bool(os.getenv("TAVILY_API_KEY"))

    def search(self, query: str, *, max_results: int) -> Sequence[SearchResult]:
        # The key is accessed only when this adapter is actually invoked.
        from tavily import TavilyClient

        response = TavilyClient(api_key=os.getenv("TAVILY_API_KEY")).search(
            query=query,
            max_results=max_results,
        )
        results: list[SearchResult] = []
        for item in response.get("results", []) or []:
            if not isinstance(item, dict):
                continue
            score = item.get("score")
            try:
                normalized_score = float(score) if score is not None else None
            except (TypeError, ValueError):
                normalized_score = None
            results.append(
                SearchResult(
                    url=str(item.get("url") or ""),
                    title=str(item.get("title") or ""),
                    snippet=str(item.get("content") or item.get("snippet") or ""),
                    score=normalized_score,
                    published_at=item.get("published_date") or item.get("published_at"),
                )
            )
        return results


def _field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _items(value: Any, path: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise SearchPayloadError(f"Expected a sequence at {path}")
    return list(value)


def _dedupe_search_results(results: Sequence[SearchResult]) -> list[SearchResult]:
    unique: list[SearchResult] = []
    seen: set[str] = set()
    for result in results:
        key = str(result.url or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(result)
    return unique


def _openai_response_sources(response: Any) -> list[SearchResult]:
    """Normalize Responses-API search sources and URL annotations."""
    results: list[SearchResult] = []
    for item in _items(_field(response, "output", []), "response.output"):
        action = _field(item, "action", {}) or {}
        for source in _items(_field(action, "sources", []), "output.action.sources"):
            results.append(SearchResult(
                url=str(_field(source, "url", "") or ""),
                title=str(_field(source, "title", "") or ""),
                snippet=str(_field(source, "snippet", "") or ""),
                provider_metadata={"source_surface": "web_search_call.action.sources"},
            ))
        for content in _items(_field(item, "content", []), "output.content"):
            for annotation in _items(_field(content, "annotations", []), "content.annotations"):
                if str(_field(annotation, "type", "") or "") != "url_citation":
                    continue
                results.append(SearchResult(
                    url=str(_field(annotation, "url", "") or ""),
                    title=str(_field(annotation, "title", "") or ""),
                    provider_metadata={"source_surface": "message.annotation"},
                ))
    return _dedupe_search_results(results)


class OpenAIWebSearchAdapter:
    """OpenAI hosted web search through the Responses API."""

    provider = "openai_web_search"

    def __init__(self, *, client: Any = None, api_key: str | None = None, model: str | None = None):
        self._client = client
        self._api_key = api_key
        self._model = model or os.getenv("OPENAI_SEARCH_MODEL", "gpt-5.5")

    def is_configured(self) -> bool:
        return self._client is not None or bool(self._api_key or os.getenv("OPENAI_API_KEY"))

    def _get_client(self) -> Any:
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self._api_key or os.getenv("OPENAI_API_KEY"))
        return self._client

    def search(self, query: str, *, max_results: int) -> Sequence[SearchResult]:
        response = self._get_client().responses.create(
            model=self._model,
            input=query,
            tools=[{"type": "web_search"}],
            include=["web_search_call.action.sources"],
        )
        return _openai_response_sources(response)[:max_results]


class XAIWebSearchAdapter(OpenAIWebSearchAdapter):
    """xAI hosted web search through its Responses-compatible endpoint."""

    provider = "xai_web_search"

    def __init__(self, *, client: Any = None, api_key: str | None = None, model: str | None = None):
        super().__init__(client=client, api_key=api_key, model=model or os.getenv("XAI_SEARCH_MODEL", "grok-4.3"))

    def is_configured(self) -> bool:
        return self._client is not None or bool(self._api_key or os.getenv("XAI_API_KEY"))

    def _get_client(self) -> Any:
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self._api_key or os.getenv("XAI_API_KEY"),
                base_url=os.getenv("XAI_BASE_URL", "https://api.x.ai/v1"),
            )
        return self._client


class GeminiGroundingAdapter:
    """Gemini Google Search grounding normalized to HoloChat evidence."""

    provider = "gemini_google_search"

    def __init__(self, *, client: Any = None, api_key: str | None = None, model: str | None = None):
        self._client = client
        self._api_key = api_key
        self._model = model or os.getenv("GEMINI_SEARCH_MODEL", "gemini-3.1-pro-preview")

    def is_configured(self) -> bool:
        return self._client is not None or bool(
            self._api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        )

    def _get_client(self) -> Any:
        if self._client is None:
            from google import genai
            self._client = genai.Client(
                api_key=self._api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            )
        return self._client

    def search(self, query: str, *, max_results: int) -> Sequence[SearchResult]:
        response = self._get_client().models.generate_content(
            model=self._model,
            contents=query,
            config={"tools": [{"google_search": {}}]},
        )
        results: list[SearchResult] = []
        for candidate in _items(_field(response, "candidates", []), "response.candidates"):
            grounding = _field(candidate, "grounding_metadata", {}) or {}
            support_text: dict[int, list[str]] = {}
            for support in _items(_field(grounding, "grounding_supports", []), "grounding_supports"):
                text = str(_field(_field(support, "segment", {}) or {}, "text", "") or "").strip()
                for index in _items(_field(support, "grounding_chunk_indices", []), "grounding_chunk_indices"):
                    if text:
                        support_text.setdefault(int(index), []).append(text)
            for index, chunk in enumerate(_items(_field(grounding, "grounding_chunks", []), "grounding_chunks")):
                web = _field(chunk, "web", {}) or {}
                results.append(SearchResult(
                    url=str(_field(web, "uri", "") or ""),
                    title=str(_field(web, "title", "") or ""),
                    snippet=" ".join(support_text.get(index, [])),
                    provider_metadata={"source_surface": "grounding_metadata.grounding_chunks"},
                ))
        return _dedupe_search_results(results)[:max_results]


class CustomFunctionSearchAdapter:
    """Search-function bridge for DeepSeek and providers without hosted search."""

    def __init__(
        self,
        search_function: Callable[[str, int], Sequence[SearchResult | dict[str, Any]]],
        *,
        provider: str = "custom_function_search",
    ):
        self._search_function = search_function
        self.provider = provider

    def is_configured(self) -> bool:
        return callable(self._search_function)

    def search(self, query: str, *, max_results: int) -> Sequence[SearchResult]:
        return _normalize_results(self._search_function(query, max_results))[:max_results]


def build_search_adapter(provider: str | None = None) -> SearchAdapter:
    """Resolve the configured search transport without making a provider call."""
    selected = str(provider or os.getenv("HOLOCHAT_SEARCH_PROVIDER", "tavily")).strip().lower()
    factories: dict[str, Callable[[], SearchAdapter]] = {
        "tavily": TavilySearchAdapter,
        "openai": OpenAIWebSearchAdapter,
        "xai": XAIWebSearchAdapter,
        "gemini": GeminiGroundingAdapter,
        "google": GeminiGroundingAdapter,
        # DeepSeek exposes tool calling rather than hosted search. HoloChat
        # executes its provider-neutral retrieval function and gives the
        # normalized evidence back to the DeepSeek worker.
        "deepseek": TavilySearchAdapter,
    }
    try:
        return factories[selected]()
    except KeyError as exc:
        raise ValueError(f"Unsupported HoloChat search provider: {selected}") from exc


@dataclass
class SearchRun:
    """Complete, inspectable result of one search transport attempt."""

    query: str
    provider: str
    outcome: str
    latency_ms: int
    results: list[SearchResult] = field(default_factory=list)
    error_category: str | None = None
    error_type: str | None = None
    evidence_bundle: dict[str, Any] = field(default_factory=dict)
    text_override: str | None = None
    compatibility_mode: bool = False

    @property
    def status(self) -> str:
        """Backward-friendly synonym for the explicit search outcome."""
        return self.outcome

    @property
    def rendered_text(self) -> str:
        return self.text_override or render_web_evidence(self.evidence_bundle)

    @property
    def result_count(self) -> int:
        count = len(self.evidence_bundle.get("sources") or [])
        return count or int(bool(self.compatibility_mode and self.text_override))

    def metadata(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "outcome": self.outcome,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "error_category": self.error_category,
            "error_type": self.error_type,
            "result_count": self.result_count,
            "raw_result_count": len(self.results),
            "compatibility_mode": self.compatibility_mode,
        }

    @classmethod
    def from_legacy_text(cls, query: str, text: str | None) -> "SearchRun":
        """Bridge old patched text callers without restoring hidden state."""
        outcome = "checked" if text else "no_results"
        return cls(
            query=query,
            provider="legacy_text_wrapper",
            outcome=outcome,
            latency_ms=0,
            error_category=None if text else "no_results",
            evidence_bundle=build_web_evidence_bundle(
                query,
                [],
                provider="legacy_text_wrapper",
                status=outcome,
                error_category=None if text else "no_results",
            ),
            text_override=str(text or ""),
            compatibility_mode=True,
        )


def _normalize_results(items: Sequence[SearchResult | dict[str, Any]]) -> list[SearchResult]:
    normalized: list[SearchResult] = []
    for item in items or []:
        if isinstance(item, SearchResult):
            normalized.append(item)
            continue
        if not isinstance(item, dict):
            continue
        score = item.get("score")
        try:
            normalized_score = float(score) if score is not None else None
        except (TypeError, ValueError):
            normalized_score = None
        normalized.append(
            SearchResult(
                url=str(item.get("url") or ""),
                title=str(item.get("title") or ""),
                snippet=str(item.get("content") or item.get("snippet") or ""),
                score=normalized_score,
                published_at=item.get("published_at") or item.get("published_date"),
            )
        )
    return normalized


def run_search(
    query: str,
    max_results: int = 5,
    *,
    adapter: SearchAdapter | None = None,
) -> SearchRun:
    """Run a search through an injectable adapter and return structured data."""
    try:
        selected_adapter = adapter or build_search_adapter()
    except ValueError:
        normalized_query = str(query or "").strip()
        provider = str(os.getenv("HOLOCHAT_SEARCH_PROVIDER", "unknown") or "unknown")
        bundle = build_web_evidence_bundle(
            normalized_query, [], provider=provider, status="unsupported_provider",
            error_category="unsupported_provider",
        )
        return SearchRun(
            query=normalized_query,
            provider=provider,
            outcome="unsupported_provider",
            latency_ms=0,
            error_category="unsupported_provider",
            evidence_bundle=bundle,
        )
    provider = str(getattr(selected_adapter, "provider", "unknown") or "unknown")
    normalized_query = str(query or "").strip()
    started_at = perf_counter()

    if not normalized_query:
        bundle = build_web_evidence_bundle(
            normalized_query, [], provider=provider, status="no_results", error_category="empty_query"
        )
        return SearchRun(
            query=normalized_query,
            provider=provider,
            outcome="no_results",
            latency_ms=0,
            error_category="empty_query",
            evidence_bundle=bundle,
        )

    configured = getattr(selected_adapter, "is_configured", None)
    if callable(configured) and not configured():
        bundle = build_web_evidence_bundle(
            normalized_query,
            [],
            provider=provider,
            status="missing_config",
            error_category="missing_config",
        )
        return SearchRun(
            query=normalized_query,
            provider=provider,
            outcome="missing_config",
            latency_ms=int((perf_counter() - started_at) * 1000),
            error_category="missing_config",
            evidence_bundle=bundle,
        )

    try:
        raw_results = _normalize_results(
            selected_adapter.search(normalized_query, max_results=max(1, int(max_results)))
        )
    except Exception as exc:
        error_type = type(exc).__name__
        logger.warning("Web search provider failed (%s).", error_type)
        bundle = build_web_evidence_bundle(
            normalized_query,
            [],
            provider=provider,
            status="provider_error",
            error_category="provider_error",
        )
        return SearchRun(
            query=normalized_query,
            provider=provider,
            outcome="provider_error",
            latency_ms=int((perf_counter() - started_at) * 1000),
            error_category="provider_error",
            error_type=error_type,
            evidence_bundle=bundle,
        )

    if not raw_results:
        outcome = "no_results"
        error_category = "no_results"
    else:
        outcome = "checked"
        error_category = None
    bundle = build_web_evidence_bundle(
        normalized_query,
        [item.as_evidence_record() for item in raw_results],
        provider=provider,
        status=outcome,
        error_category=error_category,
    )
    if raw_results and not bundle.get("sources"):
        outcome = "all_rejected"
        error_category = "all_rejected"
        bundle = build_web_evidence_bundle(
            normalized_query,
            [item.as_evidence_record() for item in raw_results],
            provider=provider,
            status=outcome,
            error_category=error_category,
        )
    return SearchRun(
        query=normalized_query,
        provider=provider,
        outcome=outcome,
        latency_ms=int((perf_counter() - started_at) * 1000),
        results=raw_results,
        error_category=error_category,
        evidence_bundle=bundle,
    )


def search(query: str, max_results: int = 5) -> str | None:
    """Compatibility facade for callers that still expect formatted text."""
    return run_search(query, max_results=max_results).rendered_text or None


# The engine uses this identity solely to recognize legacy test/caller patches.
_TEXT_SEARCH_WRAPPER = search
