"""Rich terminal dashboard for CIT reports — v2 with sparse-aware layout."""

from __future__ import annotations

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from src.analysis.report import GapReportOutput

SEV_STYLE = {
    "high": "bold red",
    "medium": "bold yellow",
    "low": "bold green",
}

LABEL = {"rich": "green", "moderate": "yellow", "sparse": "dim"}


def print_dashboard(report: GapReportOutput, console: Console | None = None) -> None:
    con = console or Console()

    is_sparse = report.data_quality == "sparse" or report.confidence == "low"
    has_gaps = len(report.gaps) > 0

    # Header
    header = Table.grid(padding=(0, 2))
    header.add_column(style="bold cyan")
    header.add_column()
    header.add_row("Company", report.company_name)
    header.add_row("Analyzed", report.analyzed_at[:19])
    header.add_row("Confidence", _badge(report.confidence))
    header.add_row("Data quality", _badge(report.data_quality))
    header.add_row("Synthesis", report.synthesis_mode)
    if report.enrichment_applied:
        header.add_row("Enrichment", "[green]reference merged[/]")
    if report.data_sources:
        header.add_row("Sources", ", ".join(report.data_sources))
    con.print(
        Panel(header, title="[bold]CIT Report[/]", border_style="blue", box=box.ROUNDED)
    )

    # Insight
    con.print()
    con.print(
        Panel(
            Text(report.key_tension, style="bold magenta"),
            title="[bold]Key tension[/]",
            border_style="magenta",
        )
    )

    # Sparse notice
    if is_sparse and not has_gaps:
        con.print(
            Panel(
                "[dim]Public data is limited. The insight below is directional — use the talking points to probe.[/]",
                title="[bold yellow]Limited intelligence[/]",
                border_style="yellow",
            )
        )

    con.print(
        Panel(
            report.interview_insight,
            title="[bold]Interview insight[/]",
            border_style="green",
        )
    )

    # Layer bridge
    layers = Columns(
        [
            Panel(
                report.what_company_says,
                title="[blue]Layer 1 — Says[/]",
                border_style="blue",
            ),
            Panel(
                report.what_data_shows,
                title="[green]Layer 2 — Data[/]",
                border_style="green",
            ),
        ],
        equal=True,
        expand=True,
    )
    con.print(layers)

    # Gaps (only if they exist)
    if has_gaps:
        gap_table = Table(title="Gaps", box=box.SIMPLE_HEAD, expand=True)
        gap_table.add_column("Sev", width=8)
        gap_table.add_column("Category", width=22)
        gap_table.add_column("Claim vs Reality")
        for g in report.gaps:
            sev = g.get("severity", "low")
            style = SEV_STYLE.get(sev, "")
            gap_table.add_row(
                Text(sev.upper(), style=style),
                g.get("category", ""),
                f"{g.get('claim', '')}\n[dim]\u2192 {g.get('reality', '')}[/]",
            )
        con.print(gap_table)

        radar = Table(title="Gap radar", box=None, show_header=False, padding=(0, 1))
        radar.add_column("Severity", width=10)
        radar.add_column("Bar", width=30)
        radar.add_column("Count", width=6)
        counts = {"high": 0, "medium": 0, "low": 0}
        for g in report.gaps:
            sev = g.get("severity", "low")
            if sev in counts:
                counts[sev] += 1
        mx = max(counts.values()) or 1
        for sev, style in SEV_STYLE.items():
            c = counts.get(sev, 0)
            filled = int(20 * c / mx)
            bar = "\u2588" * filled + "\u2591" * (20 - filled)
            radar.add_row(Text(sev, style=style), bar, str(c))
        con.print(radar)
    else:
        if is_sparse:
            con.print("[dim]No structural gaps detected (limited data)[/]")
        else:
            con.print("[dim]No material gaps found at this analysis level[/]")

    # Talking points
    if report.talking_points:
        tree = Tree("[bold]Talking points[/]")
        for tp in report.talking_points:
            tree.add(f"[ ] {tp}")
        con.print(tree)
    elif is_sparse:
        tree = Tree("[bold yellow]Probes[/]")
        tree.add("[ ] What core product or service drives revenue?")
        tree.add("[ ] Are they growing headcount? Check LinkedIn/job postings")
        tree.add("[ ] Who are their key customers or partners?")
        con.print(tree)

    # Edge cases
    if report.edge_flags or report.edge_warnings:
        edge = Table(title="Edge cases", box=box.MINIMAL)
        edge.add_column("Type")
        edge.add_column("Detail")
        for f in report.edge_flags:
            edge.add_row("flag", f)
        for w in report.edge_warnings:
            edge.add_row("warn", w[:80] + ("\u2026" if len(w) > 80 else ""))
        con.print(edge)


def _badge(value: str) -> str:
    colors = {
        "high": "green",
        "medium": "yellow",
        "low": "red",
        "rich": "green",
        "moderate": "yellow",
        "sparse": "red",
    }
    c = colors.get(value, "white")
    return f"[{c}]{value}[/]"
