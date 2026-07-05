"""
utils/helpers.py
=================
Small, dependency-light helper functions shared across agents:
- LLM factory with graceful degradation when no API key is configured
- keyword extraction
- cosine similarity
- simple text truncation for terminal display
"""

from __future__ import annotations

import re
from collections import Counter
from typing import List, Optional, Sequence

import numpy as np

from config import settings

_STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "for", "and", "or", "to", "is",
    "are", "with", "what's", "whats", "what", "trending", "current",
    "latest", "research", "about", "me", "tell", "who", "works", "show",
    "another", "compare", "first", "two", "please", "can", "you", "i",
    "want", "need", "find", "search",
}


def get_llm(temperature: Optional[float] = None):
    """
    Returns a LangChain chat model if OPENAI_API_KEY is configured,
    otherwise returns None so callers can fall back to deterministic
    template-based generation. This keeps the whole system runnable
    out-of-the-box, with no API key, for demo / offline purposes.
    """
    if not settings.has_openai:
        return None
    try:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.openai_model,
            temperature=temperature if temperature is not None else settings.llm_temperature,
            api_key=settings.openai_api_key,
        )
    except Exception:
        return None


def extract_keywords(text: str, top_n: int = 8) -> List[str]:
    """Very lightweight keyword extractor (frequency-based, stopword-filtered).
    Used when no LLM is available, and as a cheap pre-filter otherwise."""
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9\-]{2,}", text.lower())
    words = [w for w in words if w not in _STOPWORDS]
    counts = Counter(words)
    return [w for w, _ in counts.most_common(top_n)]


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    va, vb = np.array(a, dtype=float), np.array(b, dtype=float)
    denom = (np.linalg.norm(va) * np.linalg.norm(vb))
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def truncate(text: str, length: int = 280) -> str:
    text = text.strip().replace("\n", " ")
    return text if len(text) <= length else text[: length - 1].rstrip() + "…"


def dedupe_preserve_order(items: Sequence[str]) -> List[str]:
    seen = set()
    out = []
    for it in items:
        key = it.lower().strip()
        if key not in seen:
            seen.add(key)
            out.append(it)
    return out
