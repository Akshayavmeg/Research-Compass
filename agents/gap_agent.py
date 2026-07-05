"""
agents/gap_agent.py
====================
Research gap analysis: compares topics identified as currently trending
(via trend_agent / Tavily) against the university's existing faculty
research-area coverage, and surfaces domains that are under-represented.
"""

from __future__ import annotations

from typing import List

from models.state import AgentState
from prompts.prompts import GAP_ANALYSIS_PROMPT
from tools.tavily_tool import search_trends
from utils.helpers import extract_keywords, get_llm
from utils.ingest import load_faculty
from utils.logger import get_logger

logger = get_logger()

# A broad reference list of currently-hot AI/CS domains used as a fallback
# comparison set when live web trend data is unavailable (no Tavily key).
_REFERENCE_TRENDING_DOMAINS = [
    "large language model agents",
    "retrieval-augmented generation",
    "multimodal foundation models",
    "AI safety and alignment",
    "federated learning",
    "quantum machine learning",
    "explainable AI",
    "edge AI / on-device inference",
    "synthetic data generation",
    "AI for scientific discovery",
    "privacy-preserving machine learning",
    "autonomous multi-agent systems",
]


def _current_faculty_domains() -> set[str]:
    domains: set[str] = set()
    for f in load_faculty():
        for area in f.research_areas + f.keywords:
            domains.add(area.lower())
    return domains


def _llm_gap(trend_topic: str, missing_domain: str, faculty_areas: list[str]) -> dict:
    llm = get_llm(temperature=0.3)
    if llm is None:
        return {
            "missing_domain": missing_domain.title(),
            "evidence": f"'{missing_domain}' appears among broadly trending research areas but no faculty member lists it directly.",
            "future_opportunity": f"A new hire or lab focused on {missing_domain} would let the department engage with this growing area.",
            "hiring_suggestion": f"Consider recruiting faculty with a background in {missing_domain}.",
            "lab_recommendation": f"Establish a small working group or lab exploring {missing_domain}.",
        }
    try:
        resp = llm.invoke(
            GAP_ANALYSIS_PROMPT.format(
                trends=missing_domain, faculty_areas=", ".join(faculty_areas[:20])
            )
        )
        text = resp.content.strip()
        parsed = {"missing_domain": missing_domain.title()}
        for line in text.splitlines():
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip().lower().replace(" ", "_")
            parsed_key = {
                "missing_domain": "missing_domain",
                "evidence": "evidence",
                "future_opportunity": "future_opportunity",
                "hiring_suggestion": "hiring_suggestion",
                "lab_recommendation": "lab_recommendation",
            }.get(key)
            if parsed_key:
                parsed[parsed_key] = value.strip()
        parsed.setdefault("evidence", "Identified as an under-represented but trending domain.")
        parsed.setdefault("future_opportunity", "Potential for new research direction.")
        return parsed
    except Exception as exc:
        logger.error("Gap analysis LLM call failed: %s", exc)
        return {
            "missing_domain": missing_domain.title(),
            "evidence": "Identified as an under-represented but trending domain.",
            "future_opportunity": "Potential for new research direction.",
            "hiring_suggestion": None,
            "lab_recommendation": None,
        }


def analyze_gaps(query_topic: str | None = None, top_n: int = 4) -> List[dict]:
    faculty_domains = _current_faculty_domains()

    trend_topics = list(_REFERENCE_TRENDING_DOMAINS)
    if query_topic:
        tavily_result = search_trends(query_topic)
        extra = extract_keywords(tavily_result.get("summary", ""), top_n=8)
        trend_topics = extra + trend_topics

    missing = []
    for topic in trend_topics:
        topic_l = topic.lower()
        covered = any(topic_l in fd or fd in topic_l for fd in faculty_domains)
        if not covered:
            missing.append(topic)
        if len(missing) >= top_n:
            break

    faculty_area_list = sorted(faculty_domains)
    return [_llm_gap(query_topic or "", domain, faculty_area_list) for domain in missing]


def gap_analysis_node(state: AgentState) -> AgentState:
    topic = None
    trend_results = state.get("trend_results")
    if trend_results:
        topic = trend_results.get("topic")
    gaps = analyze_gaps(topic)
    state["gap_analysis"] = gaps
    logger.info("Gap analysis produced %d gaps", len(gaps))
    return state
