"""
app.py
======
ResearchCompass — terminal entry point.

Commands:
    python app.py init      Build faculty documents + populate ChromaDB
    python app.py chat      Interactive REPL (student / professor modes)
    python app.py demo      Run the scripted demo conversations from the README
    python app.py network   Bonus: faculty collaboration network (as a tree)
    python app.py heatmap   Bonus: research-area coverage heatmap

Run `python app.py --help` for details.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table
from rich.tree import Tree

from agents.confirmation import record_confirmation
from graph.workflow import get_compiled_graph
from models.state import new_state
from utils.ingest import load_faculty
from utils.logger import init_db, log_conversation, log_recommendation

app = typer.Typer(help="ResearchCompass — a terminal-based research matching AI agent.")
console = Console()

BANNER = r"""
[bold cyan]
  ____                                 _      ____                                       
 |  _ \ ___  ___  ___  __ _ _ __ ___| |__  / ___|___  _ __ ___  _ __   __ _ ___ ___
 | |_) / _ \/ __|/ _ \/ _` | '__/ __| '_ \| |   / _ \| '_ ` _ \| '_ \ / _` / __/ __|
 |  _ <  __/\__ \  __/ (_| | | | (__| | | | |__| (_) | | | | | | |_) | (_| \__ \__ \
 |_| \_\___||___/\___|\__,_|_|  \___|_| |_|\____\___/|_| |_| |_| .__/ \__,_|___/___/
                                                                |_|
[/bold cyan][dim]University Research Matching AI Agent — powered by LangGraph[/dim]
"""


# --------------------------------------------------------------------------
# Session-level memory (light layer on top of graph/checkpointer memory,
# used to resolve "show another" / "tell me more" / "compare first two")
# --------------------------------------------------------------------------
class Session:
    def __init__(self) -> None:
        self.thread_id = str(uuid.uuid4())
        self.last_topic: str = ""
        self.last_matches: List[Dict[str, Any]] = []
        self.shown_ids: List[str] = []

    @property
    def config(self) -> dict:
        return {"configurable": {"thread_id": self.thread_id}}


def _rewrite_followup(query: str, session: Session) -> str:
    q = query.lower().strip()
    if q in {"tell me more", "more", "tell me more about that"} and session.last_matches:
        name = session.last_matches[0]["faculty"]["name"]
        return f"Tell me about {name}"
    if q in {"show another", "another", "show me another", "any other options"} and session.last_topic:
        return session.last_topic
    if "compare first two" in q or "compare the first two" in q:
        if len(session.last_matches) >= 2:
            return query  # handled specially in display, query text unused for retrieval
    return query


# --------------------------------------------------------------------------
# Rich display helpers
# --------------------------------------------------------------------------
def display_faculty_matches(matches: List[Dict[str, Any]], title: str = "Faculty Matches") -> None:
    if not matches:
        console.print("[yellow]No faculty matches found.[/yellow]")
        return
    table = Table(title=title, show_lines=True)
    table.add_column("Name", style="bold cyan")
    table.add_column("Department")
    table.add_column("Research Areas")
    table.add_column("Similarity", justify="right")
    table.add_column("Slots", justify="right")
    table.add_column("Reason", overflow="fold")

    for m in matches:
        f = m["faculty"]
        workload = m.get("workload", {})
        slots = f"{workload.get('available_slots', '-')}/{f.get('max_project_slots', '-')}"
        slot_style = "red" if workload.get("level") == "OVERLOADED" else "green"
        table.add_row(
            f["name"],
            f["department"],
            ", ".join(f["research_areas"][:2]),
            f"{m['similarity_score']:.2f}",
            f"[{slot_style}]{slots}[/{slot_style}]",
            m["reason"],
        )
    console.print(table)


def display_full_profile(faculty: Dict[str, Any]) -> None:
    body = (
        f"[bold]{faculty['name']}[/bold] — {faculty['designation']}\n"
        f"Department: {faculty['department']}\n"
        f"Research Areas: {', '.join(faculty['research_areas'])}\n"
        f"Keywords: {', '.join(faculty['keywords'])}\n"
        f"Current Projects: {', '.join(faculty['current_projects'])}\n"
        f"Publications:\n  - " + "\n  - ".join(faculty["publications"]) + "\n"
        f"Experience: {faculty['experience_years']} years\n"
        f"Slots: {faculty['current_project_count']}/{faculty['max_project_slots']}\n"
        f"Past Students: {', '.join(faculty['past_students']) or 'None listed'}\n"
        f"Email: {faculty['email']}\n"
        f"Office: {faculty['office']}\n\n"
        f"{faculty['biography']}"
    )
    console.print(Panel(body, title="Faculty Profile", border_style="cyan"))


def display_comparison(a: Dict[str, Any], b: Dict[str, Any]) -> None:
    table = Table(title="Comparison")
    table.add_column("Attribute", style="bold")
    table.add_column(a["faculty"]["name"], style="cyan")
    table.add_column(b["faculty"]["name"], style="magenta")
    table.add_row("Department", a["faculty"]["department"], b["faculty"]["department"])
    table.add_row("Research Areas", ", ".join(a["faculty"]["research_areas"]), ", ".join(b["faculty"]["research_areas"]))
    table.add_row("Experience", f"{a['faculty']['experience_years']} yrs", f"{b['faculty']['experience_years']} yrs")
    table.add_row("Similarity Score", f"{a['similarity_score']:.2f}", f"{b['similarity_score']:.2f}")
    table.add_row(
        "Slots Available",
        str(a["faculty"]["max_project_slots"] - a["faculty"]["current_project_count"]),
        str(b["faculty"]["max_project_slots"] - b["faculty"]["current_project_count"]),
    )
    console.print(table)


def display_trend_results(trend: Dict[str, Any]) -> None:
    console.print(Panel(trend["summary"], title=f"Trends: {trend['topic']}", border_style="green"))
    if trend.get("recent_breakthroughs"):
        table = Table(title="Recent Sources")
        table.add_column("Title", overflow="fold")
        for title in trend["recent_breakthroughs"]:
            table.add_row(title)
        console.print(table)
    if trend.get("top_papers"):
        table = Table(title="Top Cited Papers (Semantic Scholar)")
        table.add_column("Title", overflow="fold")
        table.add_column("Year")
        table.add_column("Citations", justify="right")
        table.add_column("Authors")
        for p in trend["top_papers"][:5]:
            table.add_row(
                p["title"], str(p.get("year", "-")), str(p.get("citation_count", 0)),
                ", ".join(p.get("authors", [])[:3]),
            )
        console.print(table)


def display_collaboration(results: List[Dict[str, Any]]) -> None:
    if not results:
        console.print("[yellow]No collaboration suggestions available.[/yellow]")
        return
    table = Table(title="Suggested Collaborators")
    table.add_column("Collaborator", style="bold cyan")
    table.add_column("Overlap Score", justify="right")
    table.add_column("Shared Areas")
    table.add_column("Complementary Areas")
    table.add_column("Why", overflow="fold")
    for r in results:
        table.add_row(
            r["collaborator_name"], f"{r['overlap_score']:.2f}",
            ", ".join(r["shared_areas"]) or "-", ", ".join(r["complementary_areas"]) or "-",
            r["reason"],
        )
    console.print(table)


def display_gaps(gaps: List[Dict[str, Any]]) -> None:
    if not gaps:
        console.print("[yellow]No research gaps identified.[/yellow]")
        return
    table = Table(title="Research Gap Analysis")
    table.add_column("Missing Domain", style="bold red")
    table.add_column("Evidence", overflow="fold")
    table.add_column("Future Opportunity", overflow="fold")
    table.add_column("Hiring Suggestion", overflow="fold")
    for g in gaps:
        table.add_row(
            g["missing_domain"], g.get("evidence", ""), g.get("future_opportunity", ""),
            g.get("hiring_suggestion") or "-",
        )
    console.print(table)


def display_projects(projects: List[Dict[str, Any]]) -> None:
    if not projects:
        console.print("[yellow]No project suggestions available.[/yellow]")
        return
    table = Table(title="Suggested Projects", show_lines=True)
    table.add_column("Title", style="bold cyan", overflow="fold")
    table.add_column("Difficulty")
    table.add_column("Mentor")
    table.add_column("Description", overflow="fold")
    for p in projects:
        table.add_row(p["title"], p["difficulty"], p["faculty_mentor"], p["description"])
    console.print(table)


# --------------------------------------------------------------------------
# Core turn handler
# --------------------------------------------------------------------------
def run_turn(query: str, session: Session) -> None:
    resolved_query = _rewrite_followup(query, session)

    if "compare first two" in query.lower() and len(session.last_matches) >= 2:
        display_comparison(session.last_matches[0], session.last_matches[1])
        log_conversation(query, "memory_compare", "Displayed comparison of first two matches.")
        return

    graph = get_compiled_graph()
    state_in = new_state(resolved_query)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console, transient=True) as progress:
        progress.add_task(description="Thinking through your query...", total=None)
        result = graph.invoke(state_in, config=session.config)

    intent = result.get("intent", "")
    console.print(f"[dim]Routed as: {intent} ({result.get('mode', '')} mode)[/dim]")

    if result.get("error"):
        console.print(f"[red]{result['error']}[/red]")

    if result.get("faculty_matches"):
        if result.get("selected_faculty") and len(result["faculty_matches"]) == 1:
            display_full_profile(result["selected_faculty"])
        else:
            display_faculty_matches(result["faculty_matches"])
        session.last_matches = result["faculty_matches"]
        session.last_topic = query

    if result.get("trend_results"):
        display_trend_results(result["trend_results"])

    if result.get("collaboration_results"):
        display_collaboration(result["collaboration_results"])

    if result.get("gap_analysis"):
        display_gaps(result["gap_analysis"])

    if result.get("project_suggestions"):
        display_projects(result["project_suggestions"])

    log_conversation(query, intent, "Response generated successfully.")

    # --- Human-in-the-loop: was the graph paused before email_node? ---------
    snapshot = graph.get_state(session.config)
    if snapshot.next and "email_node" in snapshot.next:
        _handle_email_confirmation(graph, session, result)


def _handle_email_confirmation(graph, session: Session, result: Dict[str, Any]) -> None:
    if not result.get("selected_faculty"):
        return

    console.print(
        Panel(
            "ResearchCompass can draft a summary email to the selected faculty member "
            "(selected faculty, suggested project, research topic, collaboration notes).",
            title="Email Draft Available",
            border_style="yellow",
        )
    )
    proceed = Confirm.ask("Do you want to proceed and prepare this email?", default=False)
    graph.update_state(session.config, {"confirmation": proceed})
    final_state = graph.invoke(None, config=session.config)

    if final_state.get("email_summary"):
        console.print(Panel(final_state["email_summary"], title="Email Draft", border_style="blue"))

    if proceed:
        sent = final_state.get("email_sent")
        if sent:
            console.print("[green]✓ Email sent successfully.[/green]")
        else:
            console.print(
                "[yellow]Email was not sent (SMTP not configured or send failed). "
                "It has been logged for your records.[/yellow]"
            )
        log_recommendation("email_confirmed", {"faculty": result["selected_faculty"]["name"]})
    else:
        console.print("[dim]Email not sent — draft discarded per your choice.[/dim]")

    save = Confirm.ask("Do you want to save this recommendation to your history?", default=True)
    if save:
        log_recommendation(
            "faculty_recommendation",
            {
                "faculty": result["selected_faculty"]["name"],
                "query": result.get("user_query", ""),
                "projects": result.get("project_suggestions"),
            },
        )
        console.print("[green]✓ Recommendation saved.[/green]")


# --------------------------------------------------------------------------
# Typer commands
# --------------------------------------------------------------------------
@app.command()
def init(force: bool = typer.Option(False, help="Rebuild faculty documents and ChromaDB from scratch.")):
    """Initialize data files, SQLite logging DB, and the ChromaDB vector store."""
    from scripts.init_chroma import main as init_main
    import sys

    sys.argv = ["init_chroma.py"] + (["--force"] if force else [])
    init_main()


@app.command()
def chat():
    """Start an interactive ResearchCompass session."""
    init_db()
    console.print(BANNER)
    console.print(
        "[dim]Type a question (e.g. 'Who works on NLP?'), or 'exit' to quit.[/dim]\n"
    )
    session = Session()
    while True:
        try:
            query = console.input("[bold green]You:[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")
            break
        if not query:
            continue
        if query.lower() in {"exit", "quit", "bye"}:
            console.print("[dim]Goodbye![/dim]")
            break
        run_turn(query, session)
        console.print()


@app.command()
def demo():
    """Run the scripted demo conversations (see README) non-interactively."""
    init_db()
    console.print(BANNER)

    student_queries = [
        "Who works on NLP?",
        "Tell me about Dr Rao.",
        "Suggest projects.",
        "Show another.",
    ]
    professor_queries = [
        "What's trending in AI?",
        "Who should collaborate with Dr Nair?",
        "What research gaps exist?",
        "Generate collaboration email for Dr Nair.",
    ]

    console.rule("[bold]Student Demo Session[/bold]")
    student_session = Session()
    for q in student_queries:
        console.print(f"\n[bold green]You:[/bold green] {q}")
        run_turn(q, student_session)

    console.rule("[bold]Professor Demo Session[/bold]")
    professor_session = Session()
    for q in professor_queries:
        console.print(f"\n[bold green]You:[/bold green] {q}")
        run_turn(q, professor_session)


@app.command()
def network():
    """Bonus: display the faculty collaboration network as a tree, rooted
    at each faculty member, showing their top potential collaborators."""
    from agents.collaboration_agent import suggest_collaborators

    faculty_list = load_faculty()
    tree = Tree("[bold cyan]ResearchCompass Faculty Network[/bold cyan]")
    for f in faculty_list:
        branch = tree.add(f"[bold]{f.name}[/bold] ({f.department})")
        for collab in suggest_collaborators(f, top_n=2):
            branch.add(f"{collab['collaborator_name']} — overlap {collab['overlap_score']:.2f}")
    console.print(tree)


@app.command()
def heatmap():
    """Bonus: research-area coverage heatmap — how many faculty cover each area."""
    from collections import Counter

    faculty_list = load_faculty()
    counter: Counter = Counter()
    for f in faculty_list:
        for area in f.research_areas:
            counter[area] += 1

    table = Table(title="Research Area Coverage Heatmap")
    table.add_column("Research Area", style="bold")
    table.add_column("Faculty Count", justify="right")
    table.add_column("Coverage")
    max_count = max(counter.values()) if counter else 1
    for area, count in counter.most_common():
        intensity = count / max_count
        color = "green" if intensity > 0.66 else ("yellow" if intensity > 0.33 else "red")
        bar = "█" * count
        table.add_row(area, str(count), f"[{color}]{bar}[/{color}]")
    console.print(table)


if __name__ == "__main__":
    app()
