"""
agents/email_agent.py
======================
Builds a summary email (selected faculty, suggested project, research
topic, collaboration notes) and — only if state["confirmation"] is True
— actually dispatches it via tools/email_tool.py. If confirmation is
False or None, the email body is prepared and shown to the user but
NOT sent, per the human-in-the-loop requirement.
"""

from __future__ import annotations

from models.faculty import Faculty
from models.state import AgentState
from prompts.prompts import EMAIL_SUMMARY_PROMPT
from tools.email_tool import send_email
from utils.helpers import get_llm
from utils.logger import get_logger, log_recommendation

logger = get_logger()


def _compose_body(state: AgentState) -> str:
    faculty_data = state.get("selected_faculty")
    faculty = Faculty(**faculty_data) if faculty_data else None

    project = None
    if state.get("project_suggestions"):
        project = state["project_suggestions"][0]

    collaboration_notes = "N/A"
    if state.get("collaboration_results"):
        top = state["collaboration_results"][0]
        collaboration_notes = f"Potential collaborator: {top['collaborator_name']} ({top['reason']})"

    research_topic = (
        state.get("trend_results", {}).get("topic")
        if state.get("trend_results")
        else (project["research_area"] if project else state.get("user_query", ""))
    )

    llm = get_llm(temperature=0.4)
    if llm is not None and faculty is not None:
        try:
            resp = llm.invoke(
                EMAIL_SUMMARY_PROMPT.format(
                    faculty_name=faculty.name,
                    faculty_email=faculty.email,
                    project_title=project["title"] if project else "To be discussed",
                    research_topic=research_topic or "General research interest",
                    collaboration_notes=collaboration_notes,
                )
            )
            return resp.content.strip()
        except Exception as exc:
            logger.error("Email body LLM generation failed: %s", exc)

    # Deterministic fallback body.
    lines = [
        f"Dear {faculty.name if faculty else 'Professor'},",
        "",
        "I am reaching out through ResearchCompass regarding a potential research opportunity.",
        f"Research topic of interest: {research_topic or 'General research interest'}.",
    ]
    if project:
        lines.append(f"Suggested project: {project['title']} ({project['difficulty']}).")
        lines.append(project["description"])
    if collaboration_notes != "N/A":
        lines.append(collaboration_notes)
    lines += ["", "I would appreciate the opportunity to discuss this further at your convenience.", "", "Best regards,", "ResearchCompass on behalf of a prospective student"]
    return "\n".join(lines)


def email_agent_node(state: AgentState) -> AgentState:
    body = _compose_body(state)
    state["email_summary"] = body

    faculty_data = state.get("selected_faculty")
    faculty_email = faculty_data.get("email") if faculty_data else None

    if state.get("confirmation") is True and faculty_email:
        subject = "Research Opportunity Inquiry via ResearchCompass"
        success, message = send_email(faculty_email, subject, body)
        state["email_sent"] = success
        log_recommendation(
            "email",
            {
                "to": faculty_email,
                "subject": subject,
                "sent": success,
                "message": message,
            },
        )
        logger.info("Email dispatch result: %s", message)
    else:
        state["email_sent"] = False
        logger.info("Email prepared but not sent (confirmation=%s)", state.get("confirmation"))

    return state
