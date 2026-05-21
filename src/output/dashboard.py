"""Rich terminal dashboard for CIT reports."""

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


def print_dashboard(report: GapReportOutput, console: Console | None = None) -> None:
    con = console or Console()

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

    con.print(Panel(header, title="[bold]CIT Report[/]", border_style="blue", box=box.ROUNDED))

    con.print()
    con.print(Panel(
        Text(report.key_tension, style="bold magenta"),
        title="[bold]Key tension[/]",
        border_style="magenta",
    ))
    con.print(Panel(
        report.interview_insight,
        title="[bold]Interview insight[/]",
        border_style="green",
    ))

    layers = Columns([
        Panel(report.what_company_says, title="[blue]Layer 1 — Says[/]", border_style="blue"),
        Panel(report.what_data_shows, title="[green]Layer 2 — Data[/]", border_style="green"),
    ], equal=True, expand=True)
    con.print(layers)

    if report.gaps:
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
                f"{g.get('claim', '')}\n[dim]→ {g.get('reality', '')}[/]",
            )
        con.print(gap_table)

        radar = Table(title="Gap radar", box=None, show_header=False, padding=(0, 1))
        radar.add_column("Severity", width=10)
        radar.add_column("Bar", width=30)
        radar.add_column("Count", width=6)
        counts = {"high": 0, "medium": 0, "low": 0}
        for g in report.gaps:
            counts[g.get("severity", "low")] = counts.get(g.get("severity", "low"), 0) + 1
        mx = max(counts.values()) or 1
        for sev, style in SEV_STYLE.items():
            c = counts.get(sev, 0)
            bar = "█" * int(20 * c / mx) + "░" * (20 - int(20 * c / mx))
            radar.add_row(Text(sev, style=style), bar, str(c))
        con.print(radar)
    else:
        con.print("[dim]No gaps detected[/]")

    if report.talking_points:
        tree = Tree("[bold]Talking points[/]")
        for tp in report.talking_points:
            tree.add(f"[ ] {tp}")
        con.print(tree)

    if report.edge_flags or report.edge_warnings:
        edge = Table(title="Edge cases", box=box.MINIMAL)
        edge.add_column("Type")
        edge.add_column("Detail")
        for f in report.edge_flags:
            edge.add_row("flag", f)
        for w in report.edge_warnings:
            edge.add_row("warn", w[:80] + ("…" if len(w) > 80 else ""))
        con.print(edge)


def _badge(value: str) -> str:
    colors = {"high": "green", "medium": "yellow", "low": "red", "rich": "green", "moderate": "yellow", "sparse": "red"}
    c = colors.get(value, "white")
    return f"[{c}]{value}[/]"
