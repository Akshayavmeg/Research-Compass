"""
models/project.py
==================
Data models for suggested research projects and research-gap output.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectSuggestion(BaseModel):
    title: str
    description: str
    difficulty: str = Field(..., description="Beginner | Intermediate | Advanced")
    prerequisites: List[str]
    faculty_mentor: str
    research_area: str
    rationale: str


class CollaborationSuggestion(BaseModel):
    collaborator_name: str
    overlap_score: float
    shared_areas: List[str]
    complementary_areas: List[str]
    reason: str


class ResearchGap(BaseModel):
    missing_domain: str
    evidence: str
    future_opportunity: str
    hiring_suggestion: Optional[str] = None
    lab_recommendation: Optional[str] = None
