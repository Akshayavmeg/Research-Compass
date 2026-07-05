"""
agents/student_agent.py
========================
Mode-specific node for student-facing queries. Students primarily care
about discovering faculty and project opportunities, so this node
mostly annotates state so downstream nodes (retriever, project agent)
know to optimize for "discovery" framing, and appends the turn to chat
history for memory support.
"""

from __future__ import annotations

from models.state import AgentState
from utils.logger import get_logger

logger = get_logger()


def student_agent_node(state: AgentState) -> AgentState:
    state["mode"] = "student"
    history = state.setdefault("chat_history", [])
    history.append({"role": "user", "content": state.get("user_query", "")})
    logger.info("Student agent processing query.")
    return state
