"""
models/state.py
================
The shared state object that flows through every node of the LangGraph
workflow. Every agent reads from and writes to this single TypedDict,
which is what gives the graph its memory / conversational continuity.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class ChatTurn(TypedDict):
    role: str  # "user" | "assistant"
    content: str


class AgentState(TypedDict, total=False):
    # --- input -----------------------------------------------------------
    user_query: str
    mode: str  # high-level bucket: "student" | "professor" | "general"
    intent: str  # fine-grained classification from the router, e.g. "trend_query"

    # --- retrieval ---------------------------------------------------------
    retrieved_docs: List[Dict[str, Any]]
    faculty_matches: List[Dict[str, Any]]
    selected_faculty: Optional[Dict[str, Any]]

    # --- research intelligence ----------------------------------------------
    trend_results: Optional[Dict[str, Any]]
    collaboration_results: Optional[List[Dict[str, Any]]]
    gap_analysis: Optional[List[Dict[str, Any]]]
    project_suggestions: Optional[List[Dict[str, Any]]]

    # --- human-in-the-loop ---------------------------------------------------
    confirmation: Optional[bool]
    pending_action: Optional[str]
    email_summary: Optional[str]
    email_sent: Optional[bool]

    # --- memory --------------------------------------------------------------
    chat_history: List[ChatTurn]

    # --- routing / control -----------------------------------------------------
    next_node: Optional[str]
    error: Optional[str]


def new_state(user_query: str, chat_history: Optional[List[ChatTurn]] = None) -> AgentState:
    """Factory for a fresh state, preserving prior chat history if given."""
    return AgentState(
        user_query=user_query,
        mode="",
        intent="",
        retrieved_docs=[],
        faculty_matches=[],
        selected_faculty=None,
        trend_results=None,
        collaboration_results=None,
        gap_analysis=None,
        project_suggestions=None,
        confirmation=None,
        pending_action=None,
        email_summary=None,
        email_sent=None,
        chat_history=chat_history or [],
        next_node=None,
        error=None,
    )
