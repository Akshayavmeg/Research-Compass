"""
agents/confirmation.py
=======================
Human-in-the-loop gate. Any action that mutates persistent state
(logging a recommendation, sending an email) must pass through here
first. The actual "ask the user" interaction happens in the CLI layer
(app.py) via `rich`'s Confirm prompt; this module only defines what
counts as a "pending action" and records the resulting decision onto
the state, plus a pure-logic helper for non-interactive/test contexts.
"""

from __future__ import annotations

from models.state import AgentState
from utils.logger import get_logger

logger = get_logger()

CONFIRMABLE_ACTIONS = {"log_recommendation", "send_email", "save_recommendation"}


def request_confirmation(state: AgentState, action: str) -> AgentState:
    """Marks an action as pending confirmation. The CLI layer is
    responsible for actually prompting the user and calling
    `record_confirmation` with the result."""
    if action not in CONFIRMABLE_ACTIONS:
        logger.warning("Unknown confirmable action requested: %s", action)
    state["pending_action"] = action
    state["confirmation"] = None
    return state


def record_confirmation(state: AgentState, approved: bool) -> AgentState:
    state["confirmation"] = approved
    logger.info("User %s action '%s'", "approved" if approved else "declined", state.get("pending_action"))
    return state


def confirmation_node(state: AgentState) -> AgentState:
    """
    Graph node placeholder: in the interactive CLI flow, confirmation is
    actually collected outside the graph (Rich prompt) between graph
    invocations, since LangGraph nodes are non-interactive by default.
    This node simply ensures the field exists and passes state through,
    defaulting to "not yet decided" so downstream nodes know to gate.
    """
    if "confirmation" not in state:
        state["confirmation"] = None
    return state
