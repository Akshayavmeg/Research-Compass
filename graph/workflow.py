"""
graph/workflow.py
==================
Assembles the ResearchCompass LangGraph StateGraph:

    START
      -> router
      -> (student_mode | professor_mode)
      -> retriever
      -> trend_search
      -> collaboration
      -> gap_analysis
      -> project_suggestion
      -> confirmation
      -> (email_node | END)
      -> END

A checkpointer (MemorySaver) is attached so conversation state persists
across turns within a thread_id, giving the graph "memory" for follow-up
queries like "tell me more" / "show another" / "compare first two".

The graph is compiled with `interrupt_before=["email_node"]` so that,
even though the pipeline is linear, no email is ever sent without the
CLI layer explicitly resuming execution after a human confirmation step.
"""

from __future__ import annotations

from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from graph.edges import route_after_confirmation, route_after_router
from graph.nodes import (
    collaboration_graph_node,
    confirmation_graph_node,
    email_node,
    gap_node,
    mode_node,
    project_node,
    retriever_node,
    route_node,
    trend_node,
)
from models.state import AgentState


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", route_node)
    graph.add_node("student_mode", mode_node)
    graph.add_node("professor_mode", mode_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("trend_search", trend_node)
    graph.add_node("collaboration", collaboration_graph_node)
    graph.add_node("gap_analysis", gap_node)
    graph.add_node("project_suggestion", project_node)
    graph.add_node("confirmation", confirmation_graph_node)
    graph.add_node("email_node", email_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route_after_router,
        {"student_mode": "student_mode", "professor_mode": "professor_mode"},
    )

    graph.add_edge("student_mode", "retriever")
    graph.add_edge("professor_mode", "retriever")
    graph.add_edge("retriever", "trend_search")
    graph.add_edge("trend_search", "collaboration")
    graph.add_edge("collaboration", "gap_analysis")
    graph.add_edge("gap_analysis", "project_suggestion")
    graph.add_edge("project_suggestion", "confirmation")

    graph.add_conditional_edges(
        "confirmation",
        route_after_confirmation,
        {"email_node": "email_node", "end": END},
    )
    graph.add_edge("email_node", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer, interrupt_before=["email_node"])


@lru_cache(maxsize=1)
def get_compiled_graph():
    return build_graph()
