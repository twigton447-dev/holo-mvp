"""
web_search.py

Live web search for Holo chat mode.
Uses Tavily — purpose-built for LLM agents, returns clean summarized results.

Get a free API key at: https://tavily.com
Add to .env: TAVILY_API_KEY=tvly-...
"""

import logging
import os
from typing import Optional

logger = logging.getLogger("holo.search")


def search(query: str, max_results: int = 5) -> Optional[str]:
    """
    Run a web search and return results as a formatted text block
    ready for injection into a model's context.

    Returns None if TAVILY_API_KEY is not set or the search fails.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.warning("TAVILY_API_KEY not set — web search unavailable.")
        return None

    try:
        from tavily import TavilyClient
        client   = TavilyClient(api_key=api_key)
        response = client.search(query=query, max_results=max_results)
        results  = response.get("results", [])

        if not results:
            return None

        lines = [f"=== WEB SEARCH: {query} ==="]
        for r in results:
            lines.append(f"\nSource: {r.get('url', '')}")
            lines.append(f"Title:  {r.get('title', '')}")
            lines.append(f"{(r.get('content') or '')[:500]}")
        lines.append("\n=== END SEARCH RESULTS ===")

        logger.info(f"Web search: '{query}' → {len(results)} results.")
        return "\n".join(lines)

    except Exception as e:
        logger.warning(f"Web search failed: {e}")
        return None
