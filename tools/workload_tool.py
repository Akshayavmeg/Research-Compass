"""
tools/workload_tool.py
=======================
Faculty workload / capacity checks. Used by workload_agent and surfaced
inside retrieval results so students see availability up front, and
professors get overload warnings.
"""

from __future__ import annotations

from typing import Dict, List

from models.faculty import Faculty


def workload_status(faculty: Faculty) -> Dict[str, object]:
    ratio = (
        faculty.current_project_count / faculty.max_project_slots
        if faculty.max_project_slots
        else 1.0
    )
    if faculty.is_overloaded:
        level = "OVERLOADED"
    elif ratio >= 0.75:
        level = "NEAR CAPACITY"
    else:
        level = "AVAILABLE"

    return {
        "name": faculty.name,
        "current_project_count": faculty.current_project_count,
        "max_project_slots": faculty.max_project_slots,
        "available_slots": faculty.available_slots,
        "level": level,
        "warning": (
            f"{faculty.name} is at full capacity ({faculty.current_project_count}/"
            f"{faculty.max_project_slots}). Consider suggesting a co-mentor."
            if faculty.is_overloaded
            else None
        ),
    }


def workload_report(faculty_list: List[Faculty]) -> List[Dict[str, object]]:
    return [workload_status(f) for f in faculty_list]
