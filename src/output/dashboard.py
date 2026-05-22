"""Professional Rich terminal dashboard — market data, benchmarks, financials."""

from __future__ import annotations

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from src.analysis.report import GapReportOutput

SEV_STYLE = {"high": "bold red", "medium": "bold yellow", "low": "bold green"}
LABEL = {"rich": "green", "moderate": "yellow", "sparse": "dim"}
BENCH_COLORS = {"above_q3": "green", "q2_q3": "cyan", "q1_q2": "yellow", "below_q1": "red"}


def _fmt(val) -> str:
    try:
        v = float(val)
    except (ValueError, TypeError):
        return str(val)
    if abs(v) >= 1e12:
        return f"${v/1e12:.2f}T"
    elif abs(v) >= 1e9:
        return f"${v/1e9:.2f}B"
    elif abs(v) >= 1e6:
        return f"${v/1e6:.2f}M"
    elif abs(v) >= 1e3:
        return f"${v/1e3:.1f}K"
    else:
        return f"{v:.2f}"


def print_dashboard(report: GapReportOutput, console: Console | None = None) -> None:
    con = console or Console()

    # ── Header ──
    header = Table.grid(padding=(0, 2))
    header.add_column(style="bold cyan")
    header.add_column()
    header.add_row("Company", report.company_name)
    header.add_row("Analyzed", report.analyzed_at[:19].replace("T", " "))
    header.add_row("Confidence", _badge(report.confidence))
    header.add_row("Data quality", _badge(report.data_quality))
    header.add_row("Synthesis", report.synthesis_mode)
    ticker = report.financial_ratios.get("ticker", "")
    if ticker:
        header.add_row("Ticker", f"[bold]{ticker}[/]")
    if report.data_sources:
        header.add_row("Sources", ", ".join(report.data_sources))
    con.print(
        Panel(header, title="[bold]CIT Professional Report[/]", border_style="blue", box=box.ROUNDED)
    )

    def _clean(s: str) -> str:
        import re
        s = re.sub(r'<[^>]+>', '', s)
        s = s.replace("&mdash;", "\u2014").replace("&ndash;", "\u2013")
        s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        s = s.replace("&#9888;", "\u26a0").replace("&#37;", "%")
        return s.strip()

    # ── Executive summary ──
    if report.executive_summary:
        lines = report.executive_summary.replace("<br>", "\n").split("\n")
        clean = [_clean(l) for l in lines if _clean(l)]
        con.print()
        con.print(Panel("\n".join(clean), title="[bold]Executive Summary[/]", border_style="cyan"))

    # ── Market data panel ──
    if report.market_data:
        md = report.market_data
        mkt = Table.grid(padding=(1, 3))
        mkt.add_column(style="dim")
        mkt.add_column(style="bold", justify="right")
        for label, key in [("Market Cap", "market_cap"), ("Enterprise Value", "enterprise_value"),
                           ("Share Price", "price"), ("P/E", "pe_ratio"),
                           ("EV/Revenue", "ev_revenue"), ("EV/EBITDA", "ev_ebitda")]:
            val = md.get(key)
            if val is not None:
                if key == "price":
                    mkt.add_row(label, f"${val:.2f}")
                elif key in ("pe_ratio", "ev_revenue", "ev_ebitda"):
                    mkt.add_row(label, f"{val:.1f}x")
                else:
                    mkt.add_row(label, _fmt(val))
        con.print()
        con.print(Panel(mkt, title="[bold]Market Data & Valuation[/]", border_style="green"))

    # ── Financial summary table ──
    ratios = report.financial_ratios
    rev = ratios.get("revenue", {})
    if isinstance(rev, dict) and rev:
        years = sorted(rev.keys())[-3:]
        fin = Table(box=box.SIMPLE_HEAVY, expand=True)
        fin.add_column("Year", width=6)
        fin.add_column("Revenue", width=14, justify="right")
        fin.add_column("Growth", width=10, justify="right")
        fin.add_column("Gross \u00d7", width=10, justify="right")
        fin.add_column("Operating \u00d7", width=12, justify="right")
        fin.add_column("Net \u00d7", width=10, justify="right")
        for y in years:
            g = ratios.get("revenue_growth", {}).get(y)
            gm = ratios.get("gross_margin", {}).get(y)
            om = ratios.get("operating_margin", {}).get(y)
            nm = ratios.get("net_margin", {}).get(y)
            g_s = f"[green]{g:+.1f}%[/]" if g and g > 0 else (f"[red]{g:+.1f}%[/]" if g and g < 0 else f"{g:+.1f}%" if g else "\u2014")
            fin.add_row(
                str(y),
                _fmt(rev.get(y, 0)),
                g_s,
                f"{gm:.1f}%" if gm else "\u2014",
                f"{om:.1f}%" if om else "\u2014",
                f"{nm:.1f}%" if nm else "\u2014",
            )
        con.print()
        con.print(Panel(fin, title="[bold]Financial Summary[/] \u00b7 SEC EDGAR", border_style="blue"))

    # ── Sector benchmarks ──
    if report.benchmark_html:
        import re
        lines = report.benchmark_html.replace("<br>", "\n").split("\n")
        clean = []
        for l in lines:
            l = re.sub(r'<[^>]+>', '', l).strip()
            l = l.replace("&mdash;", "\u2014").replace("&ndash;", "\u2013")
            l = l.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
            if l:
                for label, color in [("Top quartile", "green"), ("Above median", "cyan"),
                                      ("Below median", "yellow"), ("Bottom quartile", "red")]:
                    if label in l:
                        l = l.replace(label, f"[{color}]{label}[/]")
                clean.append(l)
        if clean:
            con.print()
            con.print(Panel("\n".join(clean), title="[bold]Sector Context[/]", border_style="cyan"))

    # ── Gap analysis ──
    has_gaps = len(report.gaps) > 0
    if has_gaps:
        con.print()
        gap_table = Table(title="Gap Analysis", box=box.SIMPLE_HEAD, expand=True)
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

        # Radar
        counts = {"high": 0, "medium": 0, "low": 0}
        for g in report.gaps:
            sev = g.get("severity", "low")
            if sev in counts:
                counts[sev] += 1
        mx = max(counts.values()) or 1
        radar = Table(title="Gap Severity Distribution", box=None, show_header=False, padding=(0, 1))
        radar.add_column("Severity", width=10)
        radar.add_column("Bar", width=30)
        radar.add_column("Count", width=6)
        for sev, style in SEV_STYLE.items():
            c = counts.get(sev, 0)
            filled = int(20 * c / mx)
            bar = "\u2588" * filled + "\u2591" * (20 - filled)
            radar.add_row(Text(sev, style=style), bar, str(c))
        con.print(radar)

    # ── Peer metrics (from raw ratios) ──
    peer_items = []
    rev = ratios.get("revenue", {})
    if isinstance(rev, dict) and rev:
        for y in sorted(rev.keys())[-3:]:
            peer_items.append((f"Revenue {y}", _fmt(rev[y])))
    growth = ratios.get("revenue_growth", {})
    if growth:
        for y in sorted(growth.keys())[-2:]:
            v = growth[y]
            peer_items.append((f"Growth {y}", f"{v:+.1f}%" if isinstance(v, (int, float)) else str(v)))
    for label, key in [("Gross margin", "gross_margin"), ("Operating margin", "operating_margin"),
                        ("Net margin", "net_margin")]:
        m = ratios.get(key, {})
        if isinstance(m, dict) and m:
            y = sorted(m.keys())[-1]
            peer_items.append((label, f"{m[y]:.1f}%"))
    rpe = ratios.get("revenue_per_employee")
    if rpe:
        peer_items.append(("Rev/employee", f"${rpe:,.0f}"))
    rd = ratios.get("rd_pct", {})
    if isinstance(rd, dict) and rd:
        y = sorted(rd.keys())[-1]
        peer_items.append((f"R&D % ({y})", f"{rd[y]:.1f}%"))
    for label, key in [("Market Cap", "market_cap"), ("Enterprise Value", "enterprise_value"),
                        ("P/E", "pe_ratio"), ("EV/Revenue", "ev_revenue"), ("EV/EBITDA", "ev_ebitda")]:
        val = ratios.get(key)
        if val is not None:
            if key in ("market_cap", "enterprise_value"):
                peer_items.append((label, _fmt(val)))
            elif key == "pe_ratio":
                peer_items.append((label, f"{val:.1f}x"))
            else:
                peer_items.append((label, f"{val:.1f}x"))
    if peer_items:
        pt = Table(box=box.SIMPLE_HEAVY, expand=True)
        pt.add_column("Metric", width=22)
        pt.add_column("Value", width=18, justify="right")
        for label, val in peer_items:
            pt.add_row(label, val)
        con.print()
        con.print(Panel(pt, title="[bold]Key Metrics[/]", border_style="purple"))

    # ── Key insight ──
    is_sparse = report.data_quality == "sparse"
    if is_sparse and not has_gaps:
        con.print()
        con.print(Panel(
            "[dim]Public data is limited. Use talking points to probe.[/]",
            title="[bold yellow]Limited intelligence[/]", border_style="yellow",
        ))

    con.print()
    con.print(Panel(report.interview_insight, title="[bold]Interview Insight[/]", border_style="green"))

    # ── Layer bridge ──
    layers = Columns(
        [
            Panel(report.what_company_says, title="[blue]Layer 1 \u2014 Says[/]", border_style="blue"),
            Panel(report.what_data_shows, title="[green]Layer 2 \u2014 Data[/]", border_style="green"),
        ],
        equal=True, expand=True,
    )
    con.print(layers)

    # ── Talking points ──
    if report.talking_points:
        tree = Tree("[bold]Talking Points[/]")
        for tp in report.talking_points:
            tree.add(f"[ ] {tp}")
        con.print(tree)

    # ── Edge cases ──
    if report.edge_flags or report.edge_warnings:
        edge = Table(title="Notes", box=box.MINIMAL)
        edge.add_column("Type")
        edge.add_column("Detail")
        for f in report.edge_flags:
            edge.add_row("flag", f)
        for w in report.edge_warnings:
            edge.add_row("warn", w[:100] + ("\u2026" if len(w) > 100 else ""))
        con.print(edge)


def _badge(value: str) -> str:
    colors = {"high": "green", "medium": "yellow", "low": "red",
              "rich": "green", "moderate": "yellow", "sparse": "red"}
    c = colors.get(value, "white")
    return f"[{c}]{value}[/]"
