"""
tools/tavily_tool.py
=====================
Wrapper around the Tavily Search API for research-trend queries.

Degrades gracefully: if TAVILY_API_KEY is not configured, returns a
clearly-labelled offline placeholder instead of raising, so the rest of
the graph keeps working end-to-end.
"""

from __future__ import annotations

from typing import Any, Dict, List

from config import settings
from utils.logger import get_logger

logger = get_logger()


def search_trends(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search the web for current research trends using Tavily.
    Returns a dict with: query, summary, results (list of {title, url, content}).
    """
    if not settings.has_tavily:
        return {
            "query": query,
            "summary": (
                "Tavily API key not configured, so live web trend search is unavailable. "
                "Set TAVILY_API_KEY in your .env to enable this feature. Showing a placeholder "
                "so the workflow can still be demonstrated."
            ),
            "results": [],
            "source": "offline",
        }

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=settings.tavily_api_key)
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True,
        )
        results: List[Dict[str, str]] = [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
            }
            for r in response.get("results", [])
        ]
        return {
            "query": query,
            "summary": response.get("answer", "No summary available."),
            "results": results,
            "source": "tavily",
        }
    except Exception as exc:  # network / auth / rate-limit failures
        logger.error("Tavily search failed: %s", exc)
        return {
            "query": query,
            "summary": f"Trend search failed ({exc}). Please retry or check your Tavily API key.",
            "results": [],
            "source": "error",
        }
