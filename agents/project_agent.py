"""
agents/project_agent.py
========================
Generates research project suggestions by combining:
- faculty expertise (from retrieval / faculty_matches)
- current research trends (from trend_agent, if available)
- identified research gaps (from gap_agent, if available)
- the student's stated interest (the raw query)

Produces up to 5 ProjectSuggestion-shaped dicts.
"""

from __future__ import annotations

from typing import List

from models.faculty import Faculty
from models.state import AgentState
from prompts.prompts import PROJECT_SUGGESTION_PROMPT
from utils.helpers import get_llm
from utils.ingest import load_faculty
from utils.logger import get_logger

logger = get_logger()

_DIFFICULTY_CYCLE = ["Beginner", "Intermediate", "Advanced", "Intermediate", "Advanced"]

_TEMPLATE_PREREQS = {
    "Beginner": ["Python programming", "Intro to Machine Learning"],
    "Intermediate": ["Deep Learning fundamentals", "Linear Algebra", "Python programming"],
    "Advanced": ["Deep Learning", "Research methodology", "Relevant domain coursework"],
}


def _template_project(faculty: Faculty, index: int, trend_hint: str | None, gap_hint: str | None) -> dict:
    difficulty = _DIFFICULTY_CYCLE[index % len(_DIFFICULTY_CYCLE)]
    area = faculty.research_areas[index % len(faculty.research_areas)]
    focus = trend_hint or gap_hint or area
    title = f"{area}: {focus.title() if focus != area else 'Applied ' + area} Project"
    return {
        "title": title,
        "description": (
            f"An applied project exploring {focus} within the broader context of {area}, "
            f"mentored by {faculty.name}, drawing on their work on "
            f"{faculty.current_projects[0] if faculty.current_projects else area}."
        ),
        "difficulty": difficulty,
        "prerequisites": _TEMPLATE_PREREQS[difficulty],
        "faculty_mentor": faculty.name,
        "research_area": area,
        "rationale": f"Combines {faculty.name}'s expertise with a currently active research direction.",
    }


def _llm_project(faculty: Faculty, trend_hint: str, gap_hint: str, student_interest: str) -> dict | None:
    llm = get_llm(temperature=0.5)
    if llm is None:
        return None
    try:
        resp = llm.invoke(
            PROJECT_SUGGESTION_PROMPT.format(
                faculty_areas=", ".join(faculty.research_areas),
                trends=trend_hint or "general advances in the field",
                gaps=gap_hint or "none specifically identified",
                student_interest=student_interest or "open-ended",
            )
        )
        text = resp.content.strip()
        fields = {"title": "", "difficulty": "Intermediate", "description": "", "prerequisites": [], "rationale": ""}
        for line in text.splitlines():
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip().lower()
            value = value.strip()
            if key == "title":
                fields["title"] = value
            elif key == "difficulty":
                fields["difficulty"] = value
            elif key == "description":
                fields["description"] = value
            elif key == "prerequisites":
                fields["prerequisites"] = [p.strip() for p in value.split(",") if p.strip()]
            elif key == "rationale":
                fields["rationale"] = value
        if not fields["title"]:
            return None
        return {
            "title": fields["title"],
            "description": fields["description"] or "Description unavailable.",
            "difficulty": fields["difficulty"] or "Intermediate",
            "prerequisites": fields["prerequisites"] or ["Relevant coursework"],
            "faculty_mentor": faculty.name,
            "research_area": faculty.research_areas[0] if faculty.research_areas else "General",
            "rationale": fields["rationale"] or "Aligned with faculty expertise and current trends.",
        }
    except Exception as exc:
        logger.error("Project suggestion LLM call failed: %s", exc)
        return None


def generate_projects(state: AgentState, max_projects: int = 5) -> List[dict]:
    matches = state.get("faculty_matches") or []
    if matches:
        faculty_candidates = [Faculty(**m["faculty"]) for m in matches]
    else:
        faculty_candidates = load_faculty()[:max_projects]

    trend_hint = None
    if state.get("trend_results"):
        trend_hint = state["trend_results"].get("topic")

    gap_hint = None
    if state.get("gap_analysis"):
        gap_hint = state["gap_analysis"][0].get("missing_domain")

    student_interest = state.get("user_query", "")

    projects = []
    for i, faculty in enumerate(faculty_candidates[:max_projects]):
        project = _llm_project(faculty, trend_hint or "", gap_hint or "", student_interest)
        if project is None:
            project = _template_project(faculty, i, trend_hint, gap_hint)
        projects.append(project)

    return projects[:max_projects]


def project_suggestion_node(state: AgentState) -> AgentState:
    projects = generate_projects(state)
    state["project_suggestions"] = projects
    logger.info("Generated %d project suggestions", len(projects))
    return state
