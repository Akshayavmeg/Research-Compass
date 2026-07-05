"""
agents/workload_agent.py
=========================
Annotates faculty_matches with workload/capacity status and raises
overload warnings. This is a lightweight enrichment node rather than a
primary router destination — it runs whenever faculty_matches is
populated so students/professors always see availability at a glance.
"""

from __future__ import annotations

from models.faculty import Faculty
from models.state import AgentState
from tools.workload_tool import workload_status
from utils.logger import get_logger

logger = get_logger()


def workload_check_node(state: AgentState) -> AgentState:
    matches = state.get("faculty_matches") or []
    warnings = []
    for match in matches:
        faculty = Faculty(**match["faculty"])
        status = workload_status(faculty)
        match["workload"] = status
        if status.get("warning"):
            warnings.append(status["warning"])

    if warnings:
        logger.info("Workload warnings: %s", "; ".join(warnings))
    state["faculty_matches"] = matches
    return state
