"""
agents/professor_agent.py
==========================
Mode-specific node for professor-facing queries. Professors are
typically interested in trends, collaborators, and research gaps rather
than being "matched" like students, so this node tags state accordingly
and records the turn in chat history.
"""

from __future__ import annotations

from models.state import AgentState
from utils.logger import get_logger

logger = get_logger()


def professor_agent_node(state: AgentState) -> AgentState:
    state["mode"] = "professor"
    history = state.setdefault("chat_history", [])
    history.append({"role": "user", "content": state.get("user_query", "")})
    logger.info("Professor agent processing query.")
    return state
