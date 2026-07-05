"""
graph/nodes.py
===============
Wraps each agent function into a graph-ready node. Several nodes are
conditionally "active" depending on the router's fine-grained intent —
rather than branching the graph itself into many parallel paths, each
node checks relevance and passes state through untouched (cheaply) when
it doesn't apply. This keeps the graph topology exactly matching the
linear pipeline described in the project spec (Router -> Student/Professor
-> Retriever -> Trend -> Collaboration -> Gap -> Project -> Confirmation
-> Email -> END) while avoiding unnecessary API/LLM calls.
"""

from __future__ import annotations

from agents.collaboration_agent import collaboration_node as _collaboration_node
from agents.confirmation import confirmation_node as _confirmation_node
from agents.email_agent import email_agent_node as _email_agent_node
from agents.gap_agent import gap_analysis_node as _gap_analysis_node
from agents.professor_agent import professor_agent_node
from agents.project_agent import project_suggestion_node as _project_suggestion_node
from agents.retrieval import retrieval_node as _retrieval_node
from agents.router import router_node
from agents.student_agent import student_agent_node
from agents.trend_agent import trend_search_node as _trend_search_node
from agents.workload_agent import workload_check_node
from models.state import AgentState
from utils.logger import get_logger

logger = get_logger()

_TREND_INTENTS = {"trend_query", "project_query", "professor_query"}
_COLLAB_INTENTS = {"collaboration_query"}
_GAP_INTENTS = {"professor_query"}
_PROJECT_INTENTS = {"project_query"}


def route_node(state: AgentState) -> AgentState:
    return router_node(state)


def mode_node(state: AgentState) -> AgentState:
    if state.get("mode") == "professor":
        return professor_agent_node(state)
    return student_agent_node(state)


def retriever_node(state: AgentState) -> AgentState:
    # Retrieval always runs: it's cheap, and every downstream node
    # (collaboration, project suggestion, email) benefits from having a
    # `selected_faculty` in context.
    state = _retrieval_node(state)
    return workload_check_node(state)


def trend_node(state: AgentState) -> AgentState:
    if state.get("intent") not in _TREND_INTENTS:
        return state
    return _trend_search_node(state)


def collaboration_graph_node(state: AgentState) -> AgentState:
    if state.get("intent") not in _COLLAB_INTENTS:
        return state
    return _collaboration_node(state)


def gap_node(state: AgentState) -> AgentState:
    if state.get("intent") not in _GAP_INTENTS:
        return state
    return _gap_analysis_node(state)


def project_node(state: AgentState) -> AgentState:
    if state.get("intent") not in _PROJECT_INTENTS:
        return state
    return _project_suggestion_node(state)


def confirmation_graph_node(state: AgentState) -> AgentState:
    return _confirmation_node(state)


def email_node(state: AgentState) -> AgentState:
    return _email_agent_node(state)
