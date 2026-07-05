"""
tools/semantic_scholar.py
==========================
Wrapper around the Semantic Scholar Graph API (public, no key strictly
required, though an API key raises rate limits considerably).
"""

from __future__ import annotations

from typing import Any, Dict, List

import requests

from config import settings
from utils.logger import get_logger

logger = get_logger()

_BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
_FIELDS = "title,abstract,year,citationCount,authors,venue,url"


def search_papers(query: str, limit: int = 5, sort_by_citations: bool = True) -> List[Dict[str, Any]]:
    """
    Search Semantic Scholar for papers matching `query`.
    Returns a list of dicts with title, abstract, year, citation_count, authors, venue, url.
    """
    headers = {}
    if settings.semantic_scholar_api_key:
        headers["x-api-key"] = settings.semantic_scholar_api_key

    params = {"query": query, "limit": limit, "fields": _FIELDS}

    try:
        resp = requests.get(_BASE_URL, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        papers = data.get("data", [])
    except Exception as exc:
        logger.error("Semantic Scholar search failed: %s", exc)
        return []

    out = []
    for p in papers:
        authors = [a.get("name", "") for a in p.get("authors", []) or []]
        out.append(
            {
                "title": p.get("title", "Untitled"),
                "abstract": (p.get("abstract") or "Abstract not available.")[:500],
                "year": p.get("year"),
                "citation_count": p.get("citationCount", 0),
                "authors": authors,
                "venue": p.get("venue", ""),
                "url": p.get("url", ""),
            }
        )

    if sort_by_citations:
        out.sort(key=lambda x: x.get("citation_count") or 0, reverse=True)

    return out
