"""
graph/edges.py
===============
Conditional-edge functions used when wiring the StateGraph in
graph/workflow.py.
"""

from __future__ import annotations

from models.state import AgentState


def route_after_router(state: AgentState) -> str:
    """Send the query to the student-mode or professor-mode node based on
    the bucket the router assigned."""
    return "professor_mode" if state.get("mode") == "professor" else "student_mode"


def route_after_confirmation(state: AgentState) -> str:
    """
    The email node is only entered if there is something worth emailing
    about (a selected faculty member). Actual send/no-send is decided
    inside email_agent_node based on state["confirmation"], which the CLI
    layer sets via graph.update_state(...) before resuming past the
    interrupt_before=['email_node'] breakpoint.
    """
    return "email_node" if state.get("selected_faculty") else "end"
