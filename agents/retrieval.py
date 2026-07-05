"""
agents/retrieval.py
====================
RAG retrieval node. Handles two distinct query shapes:

1. Broad discovery ("Who works on NLP?") -> top-K semantic matches
2. Direct lookup ("Tell me about Dr. Rao") -> single full profile

Populates state["faculty_matches"] and, for direct lookups,
state["selected_faculty"].
"""

from __future__ import annotations

import re
from typing import List

from models.state import AgentState
from prompts.prompts import FACULTY_RECOMMENDATION_REASON_PROMPT
from tools.chroma_tool import get_faculty_by_name, semantic_search
from tools.workload_tool import workload_status
from utils.helpers import get_llm, truncate
from utils.logger import get_logger

logger = get_logger()

_NAME_PATTERNS = [
    r"tell me (?:more )?about (?:dr\.?|prof\.?|professor)?\s*([a-zA-Z\.\s]+)",
    r"who is (?:dr\.?|prof\.?|professor)?\s*([a-zA-Z\.\s]+)",
    r"profile of (?:dr\.?|prof\.?|professor)?\s*([a-zA-Z\.\s]+)",
]


def _extract_name(query: str) -> str | None:
    q = query.strip()
    for pattern in _NAME_PATTERNS:
        m = re.search(pattern, q, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip(" .?")
    return None


def _llm_reason(query: str, profile_text: str) -> str | None:
    llm = get_llm(temperature=0.2)
    if llm is None:
        return None
    try:
        resp = llm.invoke(
            FACULTY_RECOMMENDATION_REASON_PROMPT.format(query=query, profile=truncate(profile_text, 600))
        )
        return resp.content.strip()
    except Exception as exc:
        logger.error("LLM reason generation failed: %s", exc)
        return None


def retrieval_node(state: AgentState) -> AgentState:
    query = state.get("user_query", "")
    name = _extract_name(query)

    if name:
        faculty = get_faculty_by_name(name)
        if faculty:
            state["selected_faculty"] = faculty.model_dump()
            state["faculty_matches"] = [
                {
                    "faculty": faculty.model_dump(),
                    "similarity_score": 1.0,
                    "reason": "Direct profile lookup.",
                    "workload": workload_status(faculty),
                }
            ]
            logger.info("Direct lookup resolved to %s", faculty.name)
            return state
        logger.info("Direct lookup found no faculty matching name fragment '%s'", name)

    hits = semantic_search(query)
    matches: List[dict] = []
    for faculty, score, reason in hits:
        better_reason = _llm_reason(query, faculty.to_document_text()) or reason
        matches.append(
            {
                "faculty": faculty.model_dump(),
                "similarity_score": score,
                "reason": better_reason,
                "workload": workload_status(faculty),
            }
        )
    state["faculty_matches"] = matches
    state["retrieved_docs"] = [{"id": m["faculty"]["id"], "score": m["similarity_score"]} for m in matches]
    if matches:
        state["selected_faculty"] = matches[0]["faculty"]
    logger.info("Semantic search returned %d matches", len(matches))
    return state
