"""Web search service using DuckDuckGo (free, no API key)."""
import logging
from typing import List, Optional
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


def search_web(query: str, max_results: int = 5) -> List[dict]:
    """Search the web and return results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return [
                {"title": r.get("title", ""), "body": r.get("body", ""), "href": r.get("href", "")}
                for r in results
            ]
    except Exception as e:
        logger.warning(f"Web search failed: {e}")
        return []


def build_search_context(query: str, max_results: int = 5) -> str:
    """Search the web and format results as context for the LLM."""
    results = search_web(query, max_results)
    if not results:
        return ""

    parts = ["[Web Search Results]"]
    for i, r in enumerate(results, 1):
        parts.append(f"{i}. {r['title']}\n{r['body']}\nSource: {r['href']}")
    return "\n\n".join(parts)
