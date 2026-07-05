"""
agents/router.py
=================
Classifies the incoming user query into one of the supported modes:
student_query, professor_query, search_query, trend_query,
collaboration_query, project_query, general_query.

Uses the LLM when available; otherwise falls back to a keyword-based
rule engine so the whole system remains usable without an API key.
"""

from __future__ import annotations

import re

from models.state import AgentState
from prompts.prompts import ROUTER_PROMPT
from utils.helpers import get_llm
from utils.logger import get_logger

logger = get_logger()

_VALID_MODES = {
    "student_query",
    "professor_query",
    "search_query",
    "trend_query",
    "collaboration_query",
    "project_query",
    "general_query",
}

_RULES = [
    (r"\btell me about\b|\bwho is\b|\bprofile of\b", "search_query"),
    (r"\btrend|\blatest\b|\bcurrent research\b|\bwhat'?s trending\b|\bbreakthrough", "trend_query"),
    (r"\bcollaborat", "collaboration_query"),
    (r"\bprojects?\b|\bsuggest a project\b|\bproject idea", "project_query"),
    (r"\bgaps?\b|\bresearch gaps?\b|\bmissing domain", "professor_query"),
    (r"\bwho works on\b|\bfind faculty\b|\bfaculty for\b|\bmatch me\b", "student_query"),
]


def _rule_based_route(query: str) -> str:
    q = query.lower()
    for pattern, mode in _RULES:
        if re.search(pattern, q):
            return mode
    # crude heuristic default
    if "professor" in q or "my student" in q or "workload" in q:
        return "professor_query"
    return "student_query"


def classify_query(query: str) -> str:
    llm = get_llm(temperature=0.0)
    if llm is not None:
        try:
            response = llm.invoke(ROUTER_PROMPT.format(query=query))
            label = response.content.strip().lower()
            label = re.sub(r"[^a-z_]", "", label)
            if label in _VALID_MODES:
                return label
            logger.warning("Router LLM returned unexpected label '%s'; falling back to rules.", label)
        except Exception as exc:
            logger.error("Router LLM call failed: %s; falling back to rules.", exc)
    return _rule_based_route(query)


_BUCKET_MAP = {
    "student_query": "student",
    "search_query": "student",
    "project_query": "student",
    "professor_query": "professor",
    "trend_query": "professor",
    "collaboration_query": "professor",
    "general_query": "general",
}


def router_node(state: AgentState) -> AgentState:
    query = state.get("user_query", "")
    intent = classify_query(query)
    state["intent"] = intent
    state["mode"] = _BUCKET_MAP.get(intent, "general")
    logger.info("Routed query to intent=%s (bucket=%s)", intent, state["mode"])
    return state
