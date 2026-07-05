"""
agents/collaboration_agent.py
==============================
Given a target faculty member, computes research-area overlap against
every other faculty member and ranks the best potential collaborators,
distinguishing "shared" expertise (direct overlap) from "complementary"
expertise (adjacent but distinct areas worth combining).
"""

from __future__ import annotations

import re
from typing import List

from models.faculty import Faculty
from models.state import AgentState
from prompts.prompts import COLLABORATION_REASON_PROMPT
from tools.chroma_tool import get_faculty_by_name
from utils.helpers import get_llm
from utils.ingest import load_faculty
from utils.logger import get_logger

logger = get_logger()

_NAME_PATTERNS = [
    r"collaborate with (?:dr\.?|prof\.?|professor)?\s*([a-zA-Z\.\s]+)",
    r"collaborators? for (?:dr\.?|prof\.?|professor)?\s*([a-zA-Z\.\s]+)",
]


def _extract_target_name(query: str) -> str | None:
    for pattern in _NAME_PATTERNS:
        m = re.search(pattern, query, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip(" .?")
    return None


def _overlap(a: Faculty, b: Faculty) -> tuple[list[str], list[str], float]:
    set_a = {x.lower() for x in a.research_areas + a.keywords}
    set_b = {x.lower() for x in b.research_areas + b.keywords}
    shared = sorted(set_a & set_b)
    complementary = sorted((set_b - set_a))[:3]
    union = set_a | set_b
    jaccard = len(set_a & set_b) / len(union) if union else 0.0
    return shared, complementary, round(jaccard, 4)


def _reason(a: Faculty, b: Faculty, shared: list[str], complementary: list[str]) -> str:
    llm = get_llm(temperature=0.3)
    if llm is None:
        base = f"Shares expertise in {', '.join(shared[:2]) or 'related areas'}"
        if complementary:
            base += f" and brings complementary strength in {', '.join(complementary[:2])}."
        else:
            base += "."
        return base
    try:
        resp = llm.invoke(
            COLLABORATION_REASON_PROMPT.format(
                faculty_a=a.name,
                faculty_b=b.name,
                shared_areas=", ".join(shared) or "none directly",
                complementary_areas=", ".join(complementary) or "none",
            )
        )
        return resp.content.strip()
    except Exception as exc:
        logger.error("Collaboration reason generation failed: %s", exc)
        return f"Shares expertise in {', '.join(shared[:2]) or 'related areas'}."


def suggest_collaborators(target: Faculty, top_n: int = 3) -> List[dict]:
    candidates = [f for f in load_faculty() if f.id != target.id]
    scored = []
    for c in candidates:
        shared, complementary, score = _overlap(target, c)
        if score == 0 and not complementary:
            continue
        scored.append((c, shared, complementary, score))
    scored.sort(key=lambda t: t[3], reverse=True)

    out = []
    for c, shared, complementary, score in scored[:top_n]:
        out.append(
            {
                "collaborator_name": c.name,
                "overlap_score": score,
                "shared_areas": shared,
                "complementary_areas": complementary,
                "reason": _reason(target, c, shared, complementary),
            }
        )
    return out


def collaboration_node(state: AgentState) -> AgentState:
    query = state.get("user_query", "")
    name = _extract_target_name(query)

    target = None
    if name:
        target = get_faculty_by_name(name)
    if target is None and state.get("selected_faculty"):
        target = Faculty(**state["selected_faculty"])

    if target is None:
        state["collaboration_results"] = []
        state["error"] = "Could not identify which faculty member to find collaborators for."
        logger.warning("Collaboration node: no target faculty resolved.")
        return state

    results = suggest_collaborators(target)
    state["collaboration_results"] = results
    state["selected_faculty"] = target.model_dump()
    logger.info("Collaboration suggestions generated for %s (%d results)", target.name, len(results))
    return state
