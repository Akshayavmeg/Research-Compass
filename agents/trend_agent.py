"""
agents/trend_agent.py
======================
Combines Tavily web search with Semantic Scholar paper search to answer
"what's trending in X" style queries, producing a summary, recent
breakthroughs (from Tavily), and top cited papers (from Semantic Scholar).
"""

from __future__ import annotations

from models.state import AgentState
from prompts.prompts import TREND_SUMMARY_PROMPT
from tools.semantic_scholar import search_papers
from tools.tavily_tool import search_trends
from utils.helpers import get_llm, truncate
from utils.logger import get_logger

logger = get_logger()


def _extract_topic(query: str) -> str:
    # Strip common question scaffolding to get a cleaner search topic.
    q = query.lower()
    for phrase in ["what's trending in", "whats trending in", "latest research in", "current research in", "trending in", "latest in"]:
        if phrase in q:
            return q.split(phrase, 1)[1].strip(" ?.")
    return query.strip(" ?.")


def _summarize(topic: str, tavily_result: dict) -> str:
    llm = get_llm(temperature=0.3)
    if llm is None or not tavily_result.get("results"):
        return tavily_result.get("summary", "No summary available.")
    try:
        search_blob = "\n".join(
            f"- {r['title']}: {truncate(r['content'], 200)}" for r in tavily_result["results"]
        )
        resp = llm.invoke(TREND_SUMMARY_PROMPT.format(topic=topic, search_results=search_blob))
        return resp.content.strip()
    except Exception as exc:
        logger.error("Trend summarization failed: %s", exc)
        return tavily_result.get("summary", "No summary available.")


def trend_search_node(state: AgentState) -> AgentState:
    topic = _extract_topic(state.get("user_query", ""))

    tavily_result = search_trends(topic)
    summary = _summarize(topic, tavily_result)
    papers = search_papers(topic, limit=5)

    state["trend_results"] = {
        "topic": topic,
        "summary": summary,
        "recent_breakthroughs": [r["title"] for r in tavily_result.get("results", [])[:5]],
        "sources": tavily_result.get("results", []),
        "top_papers": papers,
        "source_type": tavily_result.get("source", "unknown"),
    }
    logger.info("Trend search completed for topic='%s'", topic)
    return state
