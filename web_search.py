"""Provider-neutral web-search transport for HoloChat.

``run_search`` is the structured transport used by the chat engine.  The
``search`` function remains a deliberately thin text compatibility wrapper for
older callers; it does not retain per-request state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import inspect
import json
import logging
import os
from time import perf_counter
from typing import Any, Callable, Mapping, Protocol, Sequence
from urllib.parse import urlsplit

from holochat_evidence import build_web_evidence_bundle, render_web_evidence


logger = logging.getLogger("holo.search")

DEFAULT_SEARCH_TIMEOUT_SECONDS = 50.0
DEFAULT_SEARCH_MAX_OUTPUT_TOKENS = 1200
DEFAULT_SEARCH_MAX_TOOL_CALLS = 3
DEFAULT_SEARCH_REASONING_EFFORT = "low"


def _search_timeout_seconds() -> float:
    """Bound one backend attempt; broker fallback owns retries, not an SDK loop."""
    try:
        requested = float(os.getenv("HOLOCHAT_SEARCH_TIMEOUT_SECONDS", DEFAULT_SEARCH_TIMEOUT_SECONDS))
    except (TypeError, ValueError):
        requested = DEFAULT_SEARCH_TIMEOUT_SECONDS
    return min(60.0, max(10.0, requested))


def _search_max_output_tokens() -> int:
    """Bound retrieval output plus reasoning before it reaches the worker."""
    try:
        requested = int(os.getenv(
            "HOLOCHAT_SEARCH_MAX_OUTPUT_TOKENS",
            str(DEFAULT_SEARCH_MAX_OUTPUT_TOKENS),
        ))
    except (TypeError, ValueError):
        requested = DEFAULT_SEARCH_MAX_OUTPUT_TOKENS
    return min(4096, max(256, requested))


def _search_max_tool_calls() -> int:
    """Limit total hosted tool calls within one broker request."""
    try:
        requested = int(os.getenv(
            "HOLOCHAT_SEARCH_MAX_TOOL_CALLS",
            str(DEFAULT_SEARCH_MAX_TOOL_CALLS),
        ))
    except (TypeError, ValueError):
        requested = DEFAULT_SEARCH_MAX_TOOL_CALLS
    return min(8, max(1, requested))


def _search_reasoning_effort() -> str:
    requested = str(os.getenv(
        "HOLOCHAT_SEARCH_REASONING_EFFORT",
        DEFAULT_SEARCH_REASONING_EFFORT,
    ) or "").strip().lower()
    return requested if requested in {"none", "minimal", "low", "medium", "high", "xhigh"} else DEFAULT_SEARCH_REASONING_EFFORT

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
    # Set only by a provider transport that returned a first-party URL
    # citation without page text. It is admissible as a link, not a passage.
    citation_only: bool = False
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
        if self.citation_only:
            record["citation_only"] = True
        return record


@dataclass(frozen=True)
class SearchPolicy:
    """HoloGov-owned retrieval policy, independent of provider capabilities."""

    queries: tuple[str, ...] = ()
    allowed_domains: tuple[str, ...] = ()
    excluded_domains: tuple[str, ...] = ()
    risk_class: str = "standard"
    result_budget: int = 5
    tool_budget: int = 1
    live_vs_cached: str = "provider_default"

    def normalized(self, primary_query: str, default_result_budget: int) -> "SearchPolicy":
        result_budget = default_result_budget if self.result_budget is None else self.result_budget
        queries = tuple(dict.fromkeys(
            query for item in (self.queries or (primary_query,))
            if (query := str(item or "").strip())
        ))
        return SearchPolicy(
            queries=queries,
            allowed_domains=_normalize_domains(self.allowed_domains),
            excluded_domains=_normalize_domains(self.excluded_domains),
            risk_class=str(self.risk_class or "standard").strip() or "standard",
            result_budget=max(0, int(result_budget)),
            tool_budget=max(0, int(self.tool_budget)),
            live_vs_cached=str(self.live_vs_cached or "provider_default").strip() or "provider_default",
        )

    def metadata(self) -> dict[str, Any]:
        return {
            "queries": list(self.queries),
            "allowed_domains": list(self.allowed_domains),
            "excluded_domains": list(self.excluded_domains),
            "risk_class": self.risk_class,
            "result_budget": self.result_budget,
            "tool_budget": self.tool_budget,
            "live_vs_cached": self.live_vs_cached,
        }


class SearchAdapter(Protocol):
    """Provider transport; HoloGov retains policy and budget authority."""

    provider: str
    limitations: Sequence[str]

    def is_configured(self) -> bool:
        ...

    def search(
        self, query: str, *, max_results: int, policy: SearchPolicy
    ) -> Sequence[SearchResult]:
        ...


class TavilySearchAdapter:
    """The current default adapter; kept behind the provider-neutral seam."""

    provider = "tavily"
    limitations = ("live_vs_cached_preference_not_supported",)

    def is_configured(self) -> bool:
        return bool(os.getenv("TAVILY_API_KEY"))

    def search(
        self, query: str, *, max_results: int, policy: SearchPolicy | None = None
    ) -> Sequence[SearchResult]:
        # The key is accessed only when this adapter is actually invoked.
        from tavily import TavilyClient

        request: dict[str, Any] = {"query": query, "max_results": max_results}
        if policy and policy.allowed_domains:
            request["include_domains"] = list(policy.allowed_domains)
        if policy and policy.excluded_domains:
            request["exclude_domains"] = list(policy.excluded_domains)
        response = TavilyClient(api_key=os.getenv("TAVILY_API_KEY")).search(**request)
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


def _env_enabled(name: str) -> bool:
    return str(os.getenv(name, "") or "").strip().lower() in {"1", "true", "yes", "on"}


def _openclaw_gateway_is_private(url: str) -> bool:
    hostname = (urlsplit(url).hostname or "").strip().lower()
    if hostname in {"localhost", "::1"} or hostname.startswith("127."):
        return True
    if hostname.startswith("10.") or hostname.startswith("192.168."):
        return True
    if hostname.startswith("172."):
        second = hostname.split(".", 2)[1:2]
        return bool(second and second[0].isdigit() and 16 <= int(second[0]) <= 31)
    return hostname.endswith(".internal") or hostname.endswith(".local")


def _openclaw_result_records(payload: Any) -> list[dict[str, Any]]:
    """Accept only structured OpenClaw web-search output as evidence input."""
    if not isinstance(payload, Mapping) or payload.get("ok") is not True:
        raise SearchPayloadError("OpenClaw gateway did not return an ok result")
    result = payload.get("result")
    candidates: Any = result
    if isinstance(result, Mapping):
        candidates = result.get("results") or result.get("items") or result.get("data") or result.get("content")
    if isinstance(candidates, Mapping):
        candidates = candidates.get("results") or candidates.get("items") or candidates.get("data")
    if isinstance(candidates, str):
        try:
            candidates = json.loads(candidates)
        except json.JSONDecodeError:
            return []
    if isinstance(candidates, Mapping):
        candidates = candidates.get("results") or candidates.get("items") or candidates.get("data")
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)):
        return []

    records: list[dict[str, Any]] = []
    for item in candidates:
        if not isinstance(item, Mapping):
            continue
        if isinstance(item.get("text"), str):
            try:
                decoded = json.loads(item["text"])
            except json.JSONDecodeError:
                continue
            if isinstance(decoded, Mapping):
                decoded = decoded.get("results") or decoded.get("items") or []
            if isinstance(decoded, Sequence) and not isinstance(decoded, (str, bytes)):
                records.extend(entry for entry in decoded if isinstance(entry, Mapping))
            continue
        records.append(dict(item))
    return records


class OpenClawSearchAdapter:
    """Read-only search through an isolated OpenClaw gateway.

    HoloGov authorizes the turn before this adapter runs. It refuses a general
    purpose or remote gateway by default because a direct OpenClaw gateway
    token is an operator credential, not a narrow end-user token.
    """

    provider = "openclaw_web_search"
    limitations = (
        "requires_dedicated_search_only_gateway",
        "gateway_must_remain_private_by_default",
        "openclaw_provider_costs_reported_by_gateway",
    )

    def __init__(
        self,
        *,
        invoke: Callable[[dict[str, Any]], Any] | None = None,
        gateway_url: str | None = None,
        gateway_token: str | None = None,
    ):
        self._invoke = invoke
        self._gateway_url = (gateway_url or os.getenv("HOLOCHAT_OPENCLAW_GATEWAY_URL", "")).rstrip("/")
        self._gateway_token = gateway_token or os.getenv("HOLOCHAT_OPENCLAW_GATEWAY_TOKEN", "")

    def is_configured(self) -> bool:
        if self._invoke is not None:
            return True
        if not (
            _env_enabled("HOLOCHAT_OPENCLAW_SEARCH_ENABLED")
            and _env_enabled("HOLOCHAT_OPENCLAW_SEARCH_DEDICATED_GATEWAY")
            and self._gateway_url
            and self._gateway_token
        ):
            return False
        return _openclaw_gateway_is_private(self._gateway_url) or _env_enabled(
            "HOLOCHAT_OPENCLAW_ALLOW_REMOTE_GATEWAY"
        )

    def _post(self, payload: dict[str, Any]) -> Any:
        if self._invoke is not None:
            return self._invoke(payload)
        if not self.is_configured():
            raise RuntimeError("OpenClaw search gateway is not safely configured")
        import requests

        response = requests.post(
            f"{self._gateway_url}/tools/invoke",
            json=payload,
            headers={
                "Authorization": f"Bearer {self._gateway_token}",
                "Content-Type": "application/json",
                "User-Agent": "HoloChat-SearchBroker/1.0",
            },
            timeout=_search_timeout_seconds(),
        )
        response.raise_for_status()
        return response.json()

    def search(
        self, query: str, *, max_results: int, policy: SearchPolicy | None = None
    ) -> Sequence[SearchResult]:
        requested_results = max(1, int(max_results))
        payload = {
            "tool": "web_search",
            "args": {"query": query, "count": requested_results},
            "sessionKey": os.getenv("HOLOCHAT_OPENCLAW_SEARCH_SESSION_KEY", "holochat-search"),
        }
        records = _openclaw_result_records(self._post(payload))
        normalized: list[SearchResult] = []
        for item in records:
            url = str(item.get("url") or item.get("link") or "").strip()
            title = str(item.get("title") or item.get("name") or "").strip()
            content = str(item.get("content") or item.get("snippet") or item.get("text") or "").strip()
            if not url:
                continue
            normalized.append(SearchResult(
                url=url,
                title=title,
                snippet=content,
                citation_only=bool(title and not content),
                provider_metadata={"source_surface": "openclaw.tools.invoke.web_search"},
            ))
        return _dedupe_search_results(normalized)[:requested_results]


def _field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _normalize_domains(domains: Sequence[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    for domain in domains or ():
        value = str(domain or "").strip().lower().lstrip(".")
        if "://" in value:
            value = (urlsplit(value).hostname or "").lower()
        if value and value not in normalized:
            normalized.append(value)
    return tuple(normalized)


def _domain_matches(hostname: str, domain: str) -> bool:
    return hostname == domain or hostname.endswith(f".{domain}")


def _policy_allows_result(result: SearchResult, policy: SearchPolicy) -> bool:
    hostname = (urlsplit(str(result.url or "")).hostname or "").lower()
    if policy.allowed_domains and not any(
        _domain_matches(hostname, domain) for domain in policy.allowed_domains
    ):
        return False
    return not any(_domain_matches(hostname, domain) for domain in policy.excluded_domains)


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
                citation_only=not bool(str(_field(source, "snippet", "") or "").strip()),
                provider_metadata={"source_surface": "web_search_call.action.sources"},
            ))
        for content in _items(_field(item, "content", []), "output.content"):
            for annotation in _items(_field(content, "annotations", []), "content.annotations"):
                if str(_field(annotation, "type", "") or "") != "url_citation":
                    continue
                results.append(SearchResult(
                    url=str(_field(annotation, "url", "") or ""),
                    title=str(_field(annotation, "title", "") or ""),
                    citation_only=True,
                    provider_metadata={"source_surface": "message.annotation"},
                ))
    return _dedupe_search_results(results)


class OpenAIWebSearchAdapter:
    """OpenAI hosted web search through the Responses API."""

    provider = "openai_web_search"
    limitations = ("excluded_domains_not_supported",)

    def __init__(self, *, client: Any = None, api_key: str | None = None, model: str | None = None):
        self._client = client
        self._api_key = api_key
        self._model = model or os.getenv("OPENAI_SEARCH_MODEL", "gpt-5.5")

    def is_configured(self) -> bool:
        return self._client is not None or bool(self._api_key or os.getenv("OPENAI_API_KEY"))

    def _get_client(self) -> Any:
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self._api_key or os.getenv("OPENAI_API_KEY"),
                timeout=_search_timeout_seconds(),
                max_retries=0,
            )
        return self._client

    def search(
        self, query: str, *, max_results: int, policy: SearchPolicy | None = None
    ) -> Sequence[SearchResult]:
        tool: dict[str, Any] = {"type": "web_search"}
        if policy and policy.allowed_domains:
            tool["filters"] = {"allowed_domains": list(policy.allowed_domains)}
        if policy and policy.live_vs_cached in {"live_only", "prefer_live"}:
            tool["external_web_access"] = True
        elif policy and policy.live_vs_cached in {"cached_only", "prefer_cached"}:
            tool["external_web_access"] = False
        response = self._get_client().responses.create(
            model=self._model,
            input=query,
            instructions=(
                "You are HoloChat's retrieval broker, not the user-facing assistant. "
                "Retrieve only the smallest set of authoritative sources needed for the query. "
                "Do not draft an answer, explain your reasoning, or keep searching after you have "
                "enough primary evidence; the visible worker will synthesize the admitted sources."
            ),
            tools=[tool],
            include=["web_search_call.action.sources"],
            max_output_tokens=_search_max_output_tokens(),
            max_tool_calls=_search_max_tool_calls(),
            reasoning={"effort": _search_reasoning_effort()},
        )
        return _openai_response_sources(response)[:max_results]


class XAIWebSearchAdapter(OpenAIWebSearchAdapter):
    """xAI hosted web search through its Responses-compatible endpoint."""

    provider = "xai_web_search"
    limitations = ("live_vs_cached_preference_not_supported",)

    def search(
        self, query: str, *, max_results: int, policy: SearchPolicy | None = None
    ) -> Sequence[SearchResult]:
        tool: dict[str, Any] = {"type": "web_search"}
        if policy and policy.allowed_domains:
            tool["allowed_domains"] = list(policy.allowed_domains)
        if policy and policy.excluded_domains:
            tool["excluded_domains"] = list(policy.excluded_domains)
        response = self._get_client().responses.create(
            model=self._model,
            input=query,
            tools=[tool],
            include=["web_search_call.action.sources"],
            max_output_tokens=_search_max_output_tokens(),
            max_tool_calls=_search_max_tool_calls(),
        )
        return _openai_response_sources(response)[:max_results]

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
                timeout=_search_timeout_seconds(),
                max_retries=0,
            )
        return self._client


class GeminiGroundingAdapter:
    """Gemini Google Search grounding normalized to HoloChat evidence."""

    provider = "gemini_google_search"
    limitations = (
        "domain_filters_not_supported",
        "live_vs_cached_preference_not_supported",
        "result_budget_applied_after_grounding",
    )

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

    def search(
        self, query: str, *, max_results: int, policy: SearchPolicy | None = None
    ) -> Sequence[SearchResult]:
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
        search_function: Callable[..., Sequence[SearchResult | dict[str, Any]]] | None = None,
        *,
        provider: str = "custom_function_search",
        limitations: Sequence[str] = ("capabilities_declared_by_search_function",),
    ):
        self._search_function = search_function
        self.provider = provider
        self.limitations = tuple(limitations)

    def is_configured(self) -> bool:
        return callable(self._search_function)

    def search(
        self, query: str, *, max_results: int, policy: SearchPolicy | None = None
    ) -> Sequence[SearchResult]:
        if self._search_function is None:
            return []
        if policy is not None and _supports_keyword(self._search_function, "policy"):
            raw_results = self._search_function(query, max_results, policy=policy)
        else:
            raw_results = self._search_function(query, max_results)
        return _normalize_results(raw_results)[:max_results]


def build_search_adapter(provider: str | None = None) -> SearchAdapter:
    """Resolve the configured search transport without making a provider call."""
    selected = str(provider or os.getenv("HOLOCHAT_SEARCH_PROVIDER", "openclaw")).strip().lower()
    factories: dict[str, Callable[[], SearchAdapter]] = {
        "openclaw": OpenClawSearchAdapter,
        "tavily": TavilySearchAdapter,
        "openai": OpenAIWebSearchAdapter,
        "xai": XAIWebSearchAdapter,
        "gemini": GeminiGroundingAdapter,
        "google": GeminiGroundingAdapter,
        # DeepSeek exposes tool calling rather than hosted search. HoloChat
        # executes its provider-neutral retrieval function and gives the
        # normalized evidence back to the DeepSeek worker.
        "deepseek": lambda: CustomFunctionSearchAdapter(
            provider="deepseek_custom_search",
            limitations=(
                "hosted_web_search_not_available",
                "custom_retrieval_function_required",
            ),
        ),
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
    policy: SearchPolicy = field(default_factory=SearchPolicy)
    tool_call_count: int = 0
    provider_limitations: list[str] = field(default_factory=list)
    fallback_trace: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.policy = self.policy.normalized(self.query, self.policy.result_budget)

    @property
    def status(self) -> str:
        """Backward-friendly synonym for the explicit search outcome."""
        return self.outcome

    @property
    def queries(self) -> list[str]:
        return list(self.policy.queries)

    @property
    def allowed_domains(self) -> list[str]:
        return list(self.policy.allowed_domains)

    @property
    def excluded_domains(self) -> list[str]:
        return list(self.policy.excluded_domains)

    @property
    def risk_class(self) -> str:
        return self.policy.risk_class

    @property
    def result_budget(self) -> int:
        return self.policy.result_budget

    @property
    def tool_budget(self) -> int:
        return self.policy.tool_budget

    @property
    def live_vs_cached(self) -> str:
        return self.policy.live_vs_cached

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
            "queries": self.queries,
            "search_policy": self.policy.metadata(),
            "tool_call_count": self.tool_call_count,
            "provider_limitations": list(self.provider_limitations),
            "fallback_trace": list(self.fallback_trace),
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
                citation_only=bool(item.get("citation_only")),
                provider_metadata=dict(item.get("provider_metadata") or {}),
            )
        )
    return normalized


def _supports_keyword(callable_value: Callable[..., Any], keyword: str) -> bool:
    try:
        parameters = inspect.signature(callable_value).parameters.values()
    except (TypeError, ValueError):
        return False
    return any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD or parameter.name == keyword
        for parameter in parameters
    )


def _provider_limitations(adapter: Any) -> list[str]:
    declared = getattr(adapter, "limitations", None)
    if declared is None:
        return ["adapter_did_not_declare_provider_limitations"]
    return [str(item) for item in declared]


def run_search(
    query: str,
    max_results: int = 5,
    *,
    adapter: SearchAdapter | None = None,
    policy: SearchPolicy | None = None,
) -> SearchRun:
    """Run a search through an injectable adapter and return structured data."""
    try:
        selected_adapter = adapter or build_search_adapter()
    except ValueError:
        normalized_query = str(query or "").strip()
        normalized_policy = (policy or SearchPolicy(result_budget=max(1, int(max_results)))).normalized(
            normalized_query, max_results
        )
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
            policy=normalized_policy,
            provider_limitations=["provider_not_recognized"],
        )
    provider = str(getattr(selected_adapter, "provider", "unknown") or "unknown")
    normalized_query = str(query or "").strip()
    normalized_policy = (policy or SearchPolicy(result_budget=max(1, int(max_results)))).normalized(
        normalized_query, max_results
    )
    limitations = _provider_limitations(selected_adapter)
    started_at = perf_counter()

    if not normalized_policy.queries:
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
            policy=normalized_policy,
            provider_limitations=limitations,
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
            policy=normalized_policy,
            provider_limitations=limitations,
        )

    tool_call_count = 0
    try:
        provider_results: list[SearchResult] = []
        for planned_query in normalized_policy.queries[:normalized_policy.tool_budget]:
            remaining = normalized_policy.result_budget - len(provider_results)
            if remaining <= 0:
                break
            tool_call_count += 1
            search_kwargs: dict[str, Any] = {"max_results": remaining}
            if _supports_keyword(selected_adapter.search, "policy"):
                search_kwargs["policy"] = normalized_policy
            provider_results.extend(_normalize_results(
                selected_adapter.search(planned_query, **search_kwargs)
            ))
        provider_results = _dedupe_search_results(provider_results)
        raw_results = [
            result for result in provider_results
            if _policy_allows_result(result, normalized_policy)
        ][:normalized_policy.result_budget]
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
            policy=normalized_policy,
            tool_call_count=tool_call_count,
            provider_limitations=limitations,
        )

    if provider_results and not raw_results:
        outcome = "all_rejected"
        error_category = "all_rejected"
    elif not raw_results:
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
        policy=normalized_policy,
        tool_call_count=tool_call_count,
        provider_limitations=limitations,
    )


DEFAULT_SEARCH_PROVIDER_ORDER = ("openclaw", "openai", "xai", "gemini")
DEFAULT_MAX_CONFIGURED_SEARCH_CALLS = 1


def _max_configured_search_calls() -> int:
    """Cap billable broker attempts for one governed search authorization.

    An unavailable backend is free to skip. Once a configured transport is
    invoked, however, a fallback can create a second paid request. One attempt
    is the safe default; operators may raise it deliberately when they accept
    the corresponding cost and latency tradeoff.
    """
    try:
        requested = int(os.getenv(
            "HOLOCHAT_SEARCH_MAX_PROVIDER_CALLS",
            str(DEFAULT_MAX_CONFIGURED_SEARCH_CALLS),
        ))
    except (TypeError, ValueError):
        requested = DEFAULT_MAX_CONFIGURED_SEARCH_CALLS
    return min(4, max(1, requested))


def resolve_search_provider_order() -> tuple[str, ...]:
    """Ordered search backends, independent of whichever worker is speaking.

    ``HOLOCHAT_SEARCH_PROVIDERS`` (comma-separated) wins verbatim. Otherwise a
    legacy ``HOLOCHAT_SEARCH_PROVIDER`` pins the first slot and the default
    order fills the remaining fallback slots.
    """
    explicit = str(os.getenv("HOLOCHAT_SEARCH_PROVIDERS", "") or "")
    if explicit.strip():
        return tuple(dict.fromkeys(
            name for item in explicit.split(",") if (name := item.strip().lower())
        ))
    pinned = str(os.getenv("HOLOCHAT_SEARCH_PROVIDER", "") or "").strip().lower()
    ordered = ((pinned,) if pinned else ()) + DEFAULT_SEARCH_PROVIDER_ORDER
    return tuple(dict.fromkeys(name for name in ordered if name))


def run_search_with_fallback(
    query: str,
    max_results: int = 5,
    *,
    policy: SearchPolicy | None = None,
    adapters: Sequence[SearchAdapter] | None = None,
) -> SearchRun:
    """Try each configured search backend in order until one returns evidence.

    HoloGov keeps authorization and policy authority; this function only owns
    transport selection. Every attempt is recorded in ``fallback_trace`` so a
    missing key is a visible outcome, never a silent skip.
    """
    # Legacy patch seam: tests and older callers monkeypatch ``run_search``
    # with a single-argument fake. Honor that patch instead of fanning out.
    if run_search is not _STRUCTURED_SEARCH_TRANSPORT:
        return run_search(query)

    attempts: list[dict[str, Any]] = []
    last_run: SearchRun | None = None
    if adapters is not None:
        candidates: list[SearchAdapter | None] = list(adapters)
        names = [str(getattr(item, "provider", "injected") or "injected") for item in candidates]
    else:
        candidates = []
        names = []
        for name in resolve_search_provider_order():
            try:
                candidates.append(build_search_adapter(name))
            except ValueError:
                candidates.append(None)
            names.append(name)
    configured_calls = 0
    max_configured_calls = _max_configured_search_calls()
    for index, (name, adapter) in enumerate(zip(names, candidates)):
        if adapter is None:
            attempts.append({"provider": name, "outcome": "unsupported_provider", "error_type": None})
            continue
        if adapter.is_configured() and configured_calls >= max_configured_calls:
            attempts.extend({
                "provider": str(getattr(skipped, "provider", skipped_name) or skipped_name),
                "outcome": "skipped_cost_cap",
                "error_type": None,
            } for skipped_name, skipped in zip(names[index:], candidates[index:]))
            break
        if adapter.is_configured():
            configured_calls += 1
        run = run_search(query, max_results, adapter=adapter, policy=policy)
        attempts.append({
            "provider": run.provider,
            "outcome": run.outcome,
            "error_type": run.error_type,
        })
        last_run = run
        if run.outcome == "checked":
            break
    if last_run is None:
        last_run = run_search(query, max_results, adapter=_UnsupportedProviderSentinel(), policy=policy)
    last_run.fallback_trace = attempts
    return last_run


class _UnsupportedProviderSentinel:
    """Fail-closed transport used when no provider name in the order is known."""

    provider = "none_configured"
    limitations = ("no_supported_search_provider_configured",)

    def is_configured(self) -> bool:
        return False

    def search(self, query: str, *, max_results: int, policy: SearchPolicy | None = None) -> Sequence[SearchResult]:
        return []


def search(query: str, max_results: int = 5) -> str | None:
    """Compatibility facade for callers that still expect formatted text."""
    return run_search(query, max_results=max_results).rendered_text or None


# The engine uses these identities solely to recognize legacy test/caller patches.
_TEXT_SEARCH_WRAPPER = search
_STRUCTURED_SEARCH_TRANSPORT = run_search
