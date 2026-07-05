"""
scripts/init_chroma.py
=======================
Standalone script to (re)build the faculty text documents and ingest
them into ChromaDB. Run this once after installing dependencies, and
again any time data/faculty_seed.py is edited.

Usage:
    python scripts/init_chroma.py           # ingest if not already populated
    python scripts/init_chroma.py --force   # wipe and rebuild from scratch
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console

from tools.chroma_tool import ingest_faculty
from utils.ingest import materialize_faculty_documents
from utils.logger import init_db

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize ResearchCompass ChromaDB collection.")
    parser.add_argument("--force", action="store_true", help="Wipe and rebuild the collection.")
    args = parser.parse_args()

    console.print("[bold cyan]ResearchCompass — ChromaDB Initialization[/bold cyan]")

    init_db()
    console.print("[green]✓[/green] SQLite logging database ready.")

    paths = materialize_faculty_documents(force=args.force)
    console.print(f"[green]✓[/green] {len(paths)} faculty text documents written to data/faculty/")

    count = ingest_faculty(force=args.force)
    console.print(f"[green]✓[/green] ChromaDB collection populated with {count} faculty profiles.")
    console.print("[bold green]Initialization complete. You can now run: python app.py chat[/bold green]")


if __name__ == "__main__":
    main()
