"""
prompts/prompts.py
===================
Central location for every LLM prompt template used across agents.
Keeping them in one file makes tone/format changes easy and avoids
prompt strings scattered through business logic.
"""

ROUTER_PROMPT = """You are the routing engine for ResearchCompass, a university research-matching \
assistant. Classify the user's message into exactly one of these categories:

- student_query: a student looking for faculty, projects, or guidance
- professor_query: a professor looking for trends, collaborators, or gaps
- search_query: a request to look up specific faculty (e.g. "tell me about Dr. X")
- trend_query: a request about current research trends / latest developments
- collaboration_query: a request about who should collaborate with whom
- project_query: a request for project suggestions
- general_query: anything else / small talk / unclear intent

Respond with ONLY the category label, nothing else.

User message: {query}
"""

FACULTY_RECOMMENDATION_REASON_PROMPT = """Given the student's query: "{query}"
and this faculty member's profile:
{profile}

Write ONE concise sentence (max 30 words) explaining why this faculty member is a good match. \
Be specific about the research-area overlap. Do not mention similarity scores."""

TREND_SUMMARY_PROMPT = """You are summarizing current research trends for a university researcher.
Topic: {topic}

Web search results:
{search_results}

Write a concise summary (4-6 sentences) covering: what's currently trending, any recent \
breakthroughs, and why it matters for someone in this field. Do not fabricate facts not present \
in the search results."""

COLLABORATION_REASON_PROMPT = """Faculty A: {faculty_a}
Faculty B: {faculty_b}
Shared research areas: {shared_areas}
Complementary areas: {complementary_areas}

In 1-2 sentences, explain why Faculty B would be a strong research collaborator for Faculty A, \
referencing the shared and complementary expertise."""

PROJECT_SUGGESTION_PROMPT = """Based on:
- Faculty expertise: {faculty_areas}
- Current research trends: {trends}
- Identified research gaps: {gaps}
- Student interest (if any): {student_interest}

Suggest ONE novel research project. Respond in this exact format:
Title: <short title>
Difficulty: <Beginner|Intermediate|Advanced>
Description: <2-3 sentences>
Prerequisites: <comma separated>
Rationale: <1 sentence tying it to trends/gaps>"""

GAP_ANALYSIS_PROMPT = """Current research trends in the field: {trends}
Existing faculty expertise areas at this university: {faculty_areas}

Identify ONE meaningful research gap: a topic that is trending in the wider field but is \
under-represented among this faculty's expertise. Respond in this exact format:
Missing Domain: <domain>
Evidence: <1 sentence>
Future Opportunity: <1 sentence>
Hiring Suggestion: <1 sentence or 'None'>
Lab Recommendation: <1 sentence or 'None'>"""

EMAIL_SUMMARY_PROMPT = """Write a professional, concise email (max 150 words) with the following content:

Selected Faculty: {faculty_name} ({faculty_email})
Suggested Project: {project_title}
Research Topic: {research_topic}
Collaboration Notes: {collaboration_notes}

The email should be addressed to the faculty member, introduce the student's interest, summarize \
the project, and propose a short meeting. Sign off as 'ResearchCompass on behalf of a prospective student'.
Output ONLY the email body (no subject line)."""
