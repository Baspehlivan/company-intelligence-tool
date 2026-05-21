"""Side-by-side comparison — terminal and HTML."""

from __future__ import annotations

import html

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from src.analysis.report import GapReportOutput
from .theme import CIT_CSS, CIT_JS, SEVERITY_COLORS


def compare_dashboard(a: GapReportOutput, b: GapReportOutput, console: Console | None = None) -> None:
    con = console or Console()
    con.print(Panel(
        f"[bold cyan]{a.company_name}[/]  vs  [bold magenta]{b.company_name}[/]",
        title="[bold]CIT Compare[/]",
        border_style="blue",
    ))

    table = Table(box=box.ROUNDED, expand=True)
    table.add_column("Metric", style="dim", width=18)
    table.add_column(a.company_name, style="cyan")
    table.add_column(b.company_name, style="magenta")

    rows = [
        ("Confidence", a.confidence, b.confidence),
        ("Data quality", a.data_quality, b.data_quality),
        ("Synthesis", a.synthesis_mode, b.synthesis_mode),
        ("Gaps (total)", str(len(a.gaps)), str(len(b.gaps))),
        ("High severity", str(_count_sev(a, "high")), str(_count_sev(b, "high"))),
        ("Enriched", _yn(a.enrichment_applied), _yn(b.enrichment_applied)),
    ]
    for label, va, vb in rows:
        table.add_row(label, va, vb)
    table.add_row("Key tension", _trunc(a.key_tension, 55), _trunc(b.key_tension, 55))
    con.print(table)

    gap_cmp = Table(title="Gap categories", box=box.SIMPLE)
    gap_cmp.add_column("Category")
    gap_cmp.add_column(a.company_name)
    gap_cmp.add_column(b.company_name)
    for cat in sorted(set(_cats(a)) | set(_cats(b))):
        gap_cmp.add_row(cat, _cat_cell(a, cat), _cat_cell(b, cat))
    con.print(gap_cmp)

    ins = Table(title="Interview insights", box=box.MINIMAL, expand=True)
    ins.add_column(a.company_name, overflow="fold")
    ins.add_column(b.company_name, overflow="fold")
    ins.add_row(_trunc(a.interview_insight, 350), _trunc(b.interview_insight, 350))
    con.print(ins)


def compare_html(a: GapReportOutput, b: GapReportOutput) -> str:
    def col(r: GapReportOutput, css: str) -> str:
        gaps_html = ""
        for g in r.gaps[:8]:
            sev = g.get("severity", "low")
            color = SEVERITY_COLORS.get(sev, "#94a3b8")
            gaps_html += f"""
            <div class="gap-card" style="margin-bottom:0.5rem">
              <header><span class="severity-dot" style="background:{color}"></span>
              <span class="gap-cat">{html.escape(g.get('category',''))}</span></header>
              <p style="font-size:0.82rem">{html.escape(_trunc(g.get('claim',''), 120))}</p>
            </div>"""
        if not r.gaps:
            gaps_html = "<p class='muted'>No gaps</p>"

        return f"""
        <div class="compare-col {css}">
          <h3>{html.escape(r.company_name)}</h3>
          <p class="sub">confidence {html.escape(r.confidence)} · {len(r.gaps)} gaps</p>
          <p class="tension" style="font-size:0.95rem;margin:0.75rem 0">{html.escape(_trunc(r.key_tension, 200))}</p>
          <p style="font-size:0.88rem;margin-bottom:0.75rem">{html.escape(_trunc(r.interview_insight, 400))}</p>
          <h4 style="font-size:0.75rem;color:var(--muted);margin-bottom:0.5rem">TOP GAPS</h4>
          {gaps_html}
        </div>"""

    metrics_rows = ""
    for label, va, vb in [
        ("Confidence", a.confidence, b.confidence),
        ("Data quality", a.data_quality, b.data_quality),
        ("Total gaps", str(len(a.gaps)), str(len(b.gaps))),
        ("High severity", str(_count_sev(a, "high")), str(_count_sev(b, "high"))),
        ("Synthesis", a.synthesis_mode, b.synthesis_mode),
    ]:
        metrics_rows += f"<tr><th>{html.escape(label)}</th><td>{html.escape(va)}</td><td>{html.escape(vb)}</td></tr>"

    all_cats = sorted(set(_cats(a)) | set(_cats(b)))
    gap_rows = ""
    for cat in all_cats:
        gap_rows += f"<tr><td><code>{html.escape(cat)}</code></td><td>{html.escape(_cat_cell(a, cat))}</td><td>{html.escape(_cat_cell(b, cat))}</td></tr>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Compare: {html.escape(a.company_name)} vs {html.escape(b.company_name)}</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&display=swap" rel="stylesheet"/>
  <style>{CIT_CSS}
  table {{ width:100%; border-collapse:collapse; margin:1rem 0; font-size:0.88rem; }}
  th, td {{ border:1px solid var(--border); padding:0.65rem; text-align:left; vertical-align:top; }}
  th {{ background:var(--surface2); width:16%; color:var(--muted); font-weight:600; }}
  </style>
</head>
<body data-theme="dark">
  <div class="wrap">
    <header class="topbar">
      <div>
        <div class="brand">CIT Compare</div>
        <h1><span style="color:var(--accent)">{html.escape(a.company_name)}</span> vs <span style="color:var(--accent2)">{html.escape(b.company_name)}</span></h1>
      </div>
      <div class="toolbar">
        <button class="btn" onclick="window.print()">Print</button>
        <button class="btn" onclick="toggleTheme()">Theme</button>
      </div>
    </header>

    <table>
      <thead><tr><th>Metric</th><th>{html.escape(a.company_name)}</th><th>{html.escape(b.company_name)}</th></tr></thead>
      <tbody>{metrics_rows}</tbody>
    </table>

    <div class="compare-grid">
      {col(a, 'a')}
      {col(b, 'b')}
    </div>

    <section style="margin-top:1.5rem">
      <h2>Gap category matrix</h2>
      <table>
        <thead><tr><th>Category</th><th>{html.escape(a.company_name)}</th><th>{html.escape(b.company_name)}</th></tr></thead>
        <tbody>{gap_rows or '<tr><td colspan=3 class=muted>—</td></tr>'}</tbody>
      </table>
    </section>
    <footer>Generated by CIT Compare</footer>
  </div>
  <script>{CIT_JS}</script>
</body>
</html>"""


def _count_sev(r: GapReportOutput, sev: str) -> int:
    return sum(1 for g in r.gaps if g.get("severity") == sev)


def _cats(r: GapReportOutput) -> list[str]:
    return [g.get("category", "") for g in r.gaps]


def _cat_cell(r: GapReportOutput, cat: str) -> str:
    for g in r.gaps:
        if g.get("category") == cat:
            return f"[{g.get('severity', '?')}] {g.get('claim', '')[:55]}"
    return "—"


def _trunc(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def _yn(v: bool) -> str:
    return "yes" if v else "no"
