"""
models/faculty.py
==================
Pydantic data model describing a faculty member, plus a lightweight
result wrapper used by the retrieval layer.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class Faculty(BaseModel):
    """Canonical representation of a faculty member."""

    id: str = Field(..., description="Stable unique identifier, e.g. 'fac_001'")
    name: str
    designation: str
    department: str
    research_areas: List[str]
    keywords: List[str]
    current_projects: List[str]
    publications: List[str]
    experience_years: int
    max_project_slots: int
    current_project_count: int
    past_students: List[str] = Field(default_factory=list)
    email: EmailStr
    office: str
    biography: str

    @field_validator("research_areas", "keywords", "current_projects", "publications", mode="before")
    @classmethod
    def _ensure_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return v

    @property
    def available_slots(self) -> int:
        return max(0, self.max_project_slots - self.current_project_count)

    @property
    def is_overloaded(self) -> bool:
        return self.current_project_count >= self.max_project_slots

    def to_document_text(self) -> str:
        """Flatten the profile into a single text blob suitable for embedding."""
        return (
            f"Name: {self.name}\n"
            f"Designation: {self.designation}\n"
            f"Department: {self.department}\n"
            f"Research Areas: {', '.join(self.research_areas)}\n"
            f"Keywords: {', '.join(self.keywords)}\n"
            f"Current Projects: {', '.join(self.current_projects)}\n"
            f"Publications: {', '.join(self.publications)}\n"
            f"Experience: {self.experience_years} years\n"
            f"Available Project Slots: {self.available_slots} / {self.max_project_slots}\n"
            f"Past Students: {', '.join(self.past_students)}\n"
            f"Email: {self.email}\n"
            f"Office: {self.office}\n"
            f"Biography: {self.biography}\n"
        )


class FacultyMatch(BaseModel):
    """A single retrieval hit: a faculty profile plus similarity metadata."""

    faculty: Faculty
    similarity_score: float
    reason: str
