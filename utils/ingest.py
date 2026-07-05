"""
utils/ingest.py
================
Turns the seed faculty data into:
1. One .txt document per faculty member under data/faculty/ (as required
   by the project brief — every profile stored as a text document).
2. A list of validated `Faculty` pydantic objects for use elsewhere.

This module has no ChromaDB dependency — ChromaDB ingestion itself lives
in tools/chroma_tool.py so this module stays a pure data-preparation step.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from config import settings
from data.faculty_seed import FACULTY_SEED
from models.faculty import Faculty


def load_faculty() -> List[Faculty]:
    """Validate the seed data into Faculty objects."""
    return [Faculty(**record) for record in FACULTY_SEED]


def materialize_faculty_documents(force: bool = False) -> List[Path]:
    """
    Write one .txt file per faculty member to data/faculty/.
    Returns the list of file paths written (or already present).
    """
    settings.faculty_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    for faculty in load_faculty():
        path = settings.faculty_dir / f"{faculty.id}.txt"
        if force or not path.exists():
            path.write_text(faculty.to_document_text(), encoding="utf-8")
        written.append(path)
    return written


if __name__ == "__main__":
    paths = materialize_faculty_documents(force=True)
    print(f"Wrote {len(paths)} faculty documents to {settings.faculty_dir}")
