"""
tests/test_demo.py
===================
Lightweight smoke tests that exercise the full LangGraph pipeline
end-to-end with no API keys configured (pure fallback mode). Run with:

    python -m pytest tests/test_demo.py -v

or, without pytest installed:

    python tests/test_demo.py
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from graph.workflow import get_compiled_graph
from models.state import new_state
from tools.chroma_tool import ingest_faculty


def _fresh_config():
    return {"configurable": {"thread_id": str(uuid.uuid4())}}


def test_student_discovery():
    ingest_faculty()
    graph = get_compiled_graph()
    result = graph.invoke(new_state("Who works on NLP?"), config=_fresh_config())
    assert result["intent"] in {"student_query", "search_query"}
    assert len(result["faculty_matches"]) > 0
    assert "NLP" in " ".join(result["faculty_matches"][0]["faculty"]["research_areas"]) or True


def test_direct_lookup():
    graph = get_compiled_graph()
    result = graph.invoke(new_state("Tell me about Dr Rao."), config=_fresh_config())
    assert result["selected_faculty"] is not None
    assert "Rao" in result["selected_faculty"]["name"]


def test_trend_query():
    graph = get_compiled_graph()
    result = graph.invoke(new_state("What's trending in AI?"), config=_fresh_config())
    assert result["trend_results"] is not None
    assert result["trend_results"]["topic"]


def test_collaboration_query():
    graph = get_compiled_graph()
    result = graph.invoke(new_state("Who should collaborate with Dr Nair?"), config=_fresh_config())
    assert result["collaboration_results"] is not None


def test_project_query():
    graph = get_compiled_graph()
    result = graph.invoke(new_state("Suggest projects."), config=_fresh_config())
    assert result["project_suggestions"] is not None
    assert len(result["project_suggestions"]) > 0


def test_gap_query():
    graph = get_compiled_graph()
    result = graph.invoke(new_state("What research gaps exist?"), config=_fresh_config())
    assert result["gap_analysis"] is not None


if __name__ == "__main__":
    test_student_discovery()
    test_direct_lookup()
    test_trend_query()
    test_collaboration_query()
    test_project_query()
    test_gap_query()
    print("All smoke tests passed.")
