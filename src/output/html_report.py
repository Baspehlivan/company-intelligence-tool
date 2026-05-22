"""Single-file HTML report — v3 with gap matrix, animations, and denser layout."""

from __future__ import annotations

import html
import json
import math

from src.analysis.report import GapReportOutput
from .theme import CIT_CSS_V3, CIT_JS_V3, SEVERITY_COLORS, QUALITY_PCT, CONFIDENCE_PCT


def _ring_svg(pct: int, color: str) -> str:
    """SVG ring progress indicator."""
    r = 15
    circ = 2 * math.pi * r
    offset = circ * (1 - pct / 100)
    return f"""<div class="ring">
  <svg viewBox="0 0 36 36">
    <circle class="bg" cx="18" cy="18" r="{r}"/>
    <circle class="fg" cx="18" cy="18" r="{r}"
      stroke-dasharray="{circ}" stroke-dashoffset="{offset}"
      stroke="{color}"/>
  </svg>
  <span class="pct">{pct}%</span>
</div>"""


def _severity_color(sev: str) -> str:
    return SEVERITY_COLORS.get(sev, "#94a3b8")


def _severity_icon(sev: str) -> str:
    icons = {"high": "&#9888;", "medium": "&#9888;", "low": "&#9679;"}
    return icons.get(sev, "&#9679;")


def to_html(report: GapReportOutput, *, title: str | None = None) -> str:
    title = title or f"CIT — {report.company_name}"
    gaps_json = json.dumps(report.gaps)

    is_sparse = report.data_quality == "sparse" or report.confidence == "low"
    has_gaps = len(report.gaps) > 0

    gap_cards = _gap_cards_html(report.gaps)
    radar_bars = _gap_radar(report.gaps)
    gap_matrix = _gap_matrix_html(report.gaps)
    checklist = _checklist_html(report.talking_points, is_sparse=is_sparse)
    warnings = _warnings_html(report)
    scorecard = _scorecard_html(report)
    sparse_section = _sparse_brief(report) if is_sparse and not has_gaps else ""
    overview = _report_overview(report)

    meta_chips = [
        f'<span class="chip">{html.escape(report.data_quality)} data</span>',
        f'<span class="chip">{html.escape(report.synthesis_mode)} synthesis</span>',
        f'<span class="chip {report.confidence}">{html.escape(report.confidence)} confidence</span>',
    ]
    if report.enrichment_applied:
        meta_chips.append('<span class="chip accent">reference enriched</span>')
    for f in report.edge_flags[:4]:
        meta_chips.append(f'<span class="chip warn">{html.escape(f)}</span>')

    source_text = (
        ", ".join(report.data_sources) if report.data_sources else "not captured"
    )
    meta_chips.append(f'<span class="chip">sources: {html.escape(source_text)}</span>')

    gaps_section = (
        f"""
    <section id="gaps" class="fade-in">
      <h2>Gap analysis <span class="count">({len(report.gaps)} detected)</span></h2>
      {radar_bars}
      {gap_matrix}
      <div class="gap-filters">
        <button class="btn active" data-filter="all" onclick="filterGaps('all')">All</button>
        <button class="btn" data-filter="high" onclick="filterGaps('high')">High</button>
        <button class="btn" data-filter="medium" onclick="filterGaps('medium')">Medium</button>
        <button class="btn" data-filter="low" onclick="filterGaps('low')">Low</button>
      </div>
      <div class="gaps-grid">{gap_cards or _no_gaps_content(report)}</div>
    </section>
    """
        if has_gaps
        else ""
    )

    financial_section = _financial_summary_html(report) if report.financial_summary else ""
    exec_summary = _executive_summary_html(report) if report.executive_summary else ""
    peer_section = _peer_comparison_html(report) if report.peer_comparison else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>{CIT_CSS_V3}</style>
</head>
<body data-theme="dark">
  <div class="wrap">
    <header class="topbar fade-in">
      <div>
        <div class="brand">{_source_badge(report)}</div>
        <h1>{html.escape(report.company_name)}</h1>
        <p class="sub">Professional Company Intelligence Report &middot; {html.escape(report.analyzed_at[:19].replace("T", " "))} UTC</p>
      </div>
      <div class="toolbar">
        <button class="btn" onclick="window.print()">Print</button>
        <button class="btn" id="copy-btn" onclick="copyInsight()">Copy insight</button>
        <button class="btn" onclick="toggleTheme()">Theme</button>
      </div>
    </header>

    <nav class="nav-pills fade-in">
      <a href="#snapshot">Snapshot</a>
      {exec_summary and '<a href="#exec">Summary</a>' or ''}
      {financial_section and '<a href="#financials">Financials</a>' or ''}
      <a href="#insight">Analysis</a>
      {has_gaps and '<a href="#gaps">Gaps</a>' or ''}
      {peer_section and '<a href="#peers">Peers</a>' or ''}
      <a href="#prep">Prep</a>
    </nav>

    {exec_summary}
    {financial_section}

    {overview}
    {scorecard}
    {sparse_section}
    {warnings}

    <div class="chips fade-in">
      {''.join(meta_chips)}
    </div>

    <div id="snapshot" class="insight-box fade-in">
      <h2>Key insight</h2>
      <p class="tension">{html.escape(report.key_tension)}</p>
      <p class="insight-body" id="insight-text">{html.escape(report.interview_insight)}</p>
    </div>

    <div class="reframe-bridge fade-in">
      <div class="layer layer1">
        <h3><span class="num">1</span> Narrative</h3>
        <p>{html.escape(report.what_company_says)}</p>
      </div>
      <div class="bridge-arrow" title="Reframing gap">&#10230;</div>
      <div class="layer layer2">
        <h3><span class="num">2</span> Data</h3>
        <p>{html.escape(report.what_data_shows)}</p>
      </div>
    </div>

    {gaps_section}

    {peer_section}

    <section id="prep" class="fade-in">
      <h2>Interview preparation</h2>
      <ul class="checklist">{checklist}</ul>
    </section>

    <footer class="fade-in">
      <span>Generated by CIT &middot; {html.escape(report.synthesis_mode)} synthesis &middot; SEC EDGAR + Wikipedia + yfinance</span>
      <span>{html.escape(report.company_name)} &middot; {html.escape(report.confidence)} confidence</span>
    </footer>
  </div>
  <script>var gaps = {gaps_json};{CIT_JS_V3}</script>
</body>
</html>"""


def _report_overview(report: GapReportOutput) -> str:
    gap_count = len(report.gaps)
    high_count = sum(1 for g in report.gaps if g.get("severity") == "high")
    gap_info = f"{gap_count} gap{'s' if gap_count != 1 else ''} identified"
    if high_count:
        gap_info += f" ({high_count} high severity)"
    elif not gap_count:
        gap_info = "limited public data \u2014 insights are directional"

    return f"""<div class="report-overview fade-in">
  <p>
    <strong>{html.escape(report.company_name)}</strong> &mdash; {html.escape(report.key_tension[:120])}
  </p>
  <div>
    <span class="quick-stat">{gap_info}</span>
    <span class="quick-stat">{html.escape(report.data_quality)} data quality</span>
    <span class="quick-stat">{html.escape(report.confidence)} confidence</span>
  </div>
</div>"""


def _sparse_brief(report: GapReportOutput) -> str:
    return f"""<div class="sparse-notice fade-in">
  <h3>Limited public intelligence</h3>
  <p>Public data on {html.escape(report.company_name)} is sparse. This is normal for private or regional companies. The insight below is directional \u2014 designed to help you ask better questions, not to tell you what to think.</p>
  <div class="questions">
    <li>What core product or service drives revenue? (no public breakdown available)</li>
    <li>Are they growing headcount? Look for recent job postings or LinkedIn growth</li>
    <li>Who are their key customers or partners? Check case studies, press releases</li>
    <li>What recent hires or board changes signal strategic direction?</li>
  </div>
</div>"""


def _no_gaps_content(report: GapReportOutput) -> str:
    if report.data_quality == "sparse":
        return '<p class="muted">Not enough public data to detect structural gaps. Use the questions above to probe during conversation.</p>'
    return '<p class="muted">No material gaps between narrative and data at this level of analysis. Consider diving deeper into specific business units.</p>'


def _scorecard_html(report: GapReportOutput) -> str:
    conf_pct = CONFIDENCE_PCT.get(report.confidence, 50)
    qual_pct = QUALITY_PCT.get(report.data_quality, 40)
    high = sum(1 for g in report.gaps if g.get("severity") == "high")
    gap_count = len(report.gaps)

    def stat(label: str, val: str, pct: int, color: str) -> str:
        return f"""<div class="stat">
  <label>{html.escape(label)}</label>
  <div class="ring-wrap">{_ring_svg(pct, color)}</div>
  <div class="val">{html.escape(val)}</div>
</div>"""

    return f"""<div class="scorecard fade-in">
  {stat("Confidence", report.confidence, conf_pct, "#3b82f6")}
  {stat("Data quality", report.data_quality, qual_pct, "#22d3a7")}
  {stat("Gaps found", str(gap_count), min(100, gap_count * 20 + high * 10), "#a78bfa")}
  {stat("High severity", str(high), min(100, high * 40), "#ef4444")}
</div>"""


def _gap_matrix_html(gaps: list[dict]) -> str:
    """Visual matrix: gap categories as rows, severity as color blocks."""
    if not gaps:
        return ""

    severity_order = {"high": 0, "medium": 1, "low": 2}
    sorted_gaps = sorted(
        gaps, key=lambda g: severity_order.get(g.get("severity", "low"), 3)
    )

    rows = []
    for i, g in enumerate(sorted_gaps):
        sev = g.get("severity", "low")
        color = _severity_color(sev)
        cat = g.get("category", "gap")
        label = cat.replace("_", " ").title()
        icon = _severity_icon(sev)
        rows.append(
            f"""<div class="matrix-row">
  <div class="matrix-cat">{html.escape(label)}</div>
  <div class="matrix-bar">
    <div class="matrix-fill" style="width:{(3 - severity_order.get(sev, 2)) * 33}%;background:{color};animation-delay:{i * 0.1}s"></div>
  </div>
  <div class="matrix-badge" style="color:{color}">{icon} {html.escape(sev)}</div>
</div>"""
        )

    return f"""<div class="gap-matrix">
  <h3 class="matrix-title">Gap profile</h3>
  <div class="matrix-body">
    {"".join(rows)}
  </div>
</div>"""


def _gap_cards_html(gaps: list[dict]) -> str:
    parts = []
    for g in gaps:
        sev = g.get("severity", "low")
        color = _severity_color(sev)
        category = g.get("category", "gap")
        claim = g.get("claim", "")
        reality = g.get("reality", "")
        note = g.get("note", "")
        parts.append(
            f"""<article class="gap-card" data-severity="{html.escape(sev)}">
  <header>
    <span class="severity-dot" style="background:{color}"></span>
    <span class="gap-cat">{html.escape(category)}</span>
    <span class="severity-badge" style="border-color:{color};color:{color}">{html.escape(sev)}</span>
  </header>
  <div class="gap-row">
    <div class="accent-bar" style="background:{color}"></div>
    <div>
      <span class="label">Claim</span>
      {html.escape(claim)}
    </div>
  </div>
  <div class="gap-row">
    <div class="accent-bar" style="background:{color};opacity:0.5"></div>
    <div>
      <span class="label">Reality</span>
      {html.escape(reality)}
    </div>
  </div>
  {f'<p class="note">{html.escape(note)}</p>' if note else ''}
</article>"""
        )
    return "\n".join(parts)


def _gap_radar(gaps: list[dict]) -> str:
    counts = {"high": 0, "medium": 0, "low": 0}
    for g in gaps:
        sev = g.get("severity", "low")
        if sev in counts:
            counts[sev] += 1
    mx = max(counts.values()) if gaps else 1
    parts = []
    for sev in ("high", "medium", "low"):
        c = counts.get(sev, 0)
        pct = round(c / mx * 100) if mx else 0
        parts.append(
            f"""<div class="radar-row">
  <span class="radar-label">{sev}</span>
  <div class="radar-bar"><div class="radar-fill" style="width:{pct}%;background:{SEVERITY_COLORS.get(sev, '#94a3b8')}"></div></div>
  <span>{c}</span>
</div>"""
        )
    return "".join(parts)


def _checklist_html(points: list[str], is_sparse: bool = False) -> str:
    if not points:
        if is_sparse:
            return '<li class="muted">Data limited \u2014 lead with questions, not assertions</li>'
        return '<li class="muted">No talking points generated</li>'
    items = "".join(
        f'<li><label><input type="checkbox" /> {html.escape(tp)}</label></li>'
        for tp in points
    )
    return items


def _warnings_html(report: GapReportOutput) -> str:
    if not report.edge_warnings:
        return ""
    items = "".join(f"<li>{html.escape(w)}</li>" for w in report.edge_warnings)
    return (
        f'<div class="warnings"><strong>Edge-case notes</strong><ul>{items}</ul></div>'
    )


def _source_badge(report: GapReportOutput) -> str:
    if "sec_edgar" in report.data_sources:
        return 'CIT Professional &middot; <span class="badge-edgar">SEC EDGAR</span>'
    if report.data_quality == "rich":
        return "CIT Professional"
    return "Company Intelligence Tool"


def _financial_summary_html(report: GapReportOutput) -> str:
    """Render financial data from SEC EDGAR as a professional summary panel."""
    if not report.financial_summary:
        return ""
    ratios = report.financial_ratios
    rev = ratios.get("revenue", {})
    years = sorted(rev.keys())[-3:]

    rows = ""
    for y in years:
        rows += f"<tr><td>{y}</td><td class='num'>${_fmt_fin(rev[y])}</td>"

        growth = ratios.get("revenue_growth", {}).get(y)
        rows += f"<td class='num {'pos' if growth and growth > 0 else 'neg' if growth and growth < 0 else ''}'>{f'{growth:+.1f}%' if growth else '—'}</td>"

        gm = ratios.get("gross_margin", {}).get(y)
        rows += f"<td class='num'>{f'{gm:.1f}%' if gm else '—'}</td>"

        om = ratios.get("operating_margin", {}).get(y)
        rows += f"<td class='num'>{f'{om:.1f}%' if om else '—'}</td>"

        nm = ratios.get("net_margin", {}).get(y)
        rows += f"<td class='num'>{f'{nm:.1f}%' if nm else '—'}</td>"

        rd = ratios.get("rd_pct", {}).get(y)
        rows += f"<td class='num'>{f'{rd:.1f}%' if rd else '—'}</td>"
        rows += "</tr>"

    rpe = ratios.get("revenue_per_employee")
    rpe_html = f'<span class="fin-kpi"><label>Rev/Employee</label><span class="val">${rpe:,.0f}</span></span>' if rpe else ""

    fin_summary = report.financial_summary.replace("<br>", " ")

    # ── Market data cards ──
    market_html = _market_data_html(report.market_data)

    # ── Benchmark annotations ──
    bench_html = ""
    if report.benchmark_html:
        bench_lines = report.benchmark_html.split("<br>")
        parts = []
        for l in bench_lines:
            if not l.strip():
                continue
            # Wrap each line in <li>, preserving pre-existing HTML tags
            parts.append(f"<li>{l}</li>")
        bench_html = f'<div class="bench-section"><h3>Sector context</h3><ul class="bench-list">{"".join(parts)}</ul></div>'

    return f"""
<section id="financials" class="fade-in fin-section">
  <div class="fin-header">
    <h2>Financial Summary <span class="count">SEC EDGAR &middot; {html.escape(ratios.get('ticker', ''))}</span></h2>
    <p class="fin-note">{fin_summary}</p>
  </div>
  <div class="fin-panels">
    <div class="fin-panel-main">
      {rpe_html}
      <table class="fin-table">
        <thead><tr>
          <th>Year</th><th>Revenue</th><th>Growth</th><th>Gross &#37;</th><th>Operating &#37;</th><th>Net &#37;</th><th>R&amp;D &#37;</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    {market_html}
  </div>
  {bench_html}
</section>"""


def _market_data_html(market: dict) -> str:
    """Render market data cards."""
    if not market:
        return ""
    items = []
    mc = market.get("market_cap")
    if mc:
        items.append(f'<div class="mkt-card"><label>Market Cap</label><span class="val">${_fmt_fin(mc)}</span></div>')
    ev = market.get("enterprise_value")
    if ev:
        items.append(f'<div class="mkt-card"><label>Enterprise Value</label><span class="val">${_fmt_fin(ev)}</span></div>')
    pe = market.get("pe_ratio")
    if pe:
        items.append(f'<div class="mkt-card"><label>P/E</label><span class="val">{pe:.1f}x</span></div>')
    evr = market.get("ev_revenue")
    if evr:
        items.append(f'<div class="mkt-card"><label>EV/Revenue</label><span class="val">{evr:.1f}x</span></div>')
    eve = market.get("ev_ebitda")
    if eve:
        items.append(f'<div class="mkt-card"><label>EV/EBITDA</label><span class="val">{eve:.1f}x</span></div>')
    price = market.get("price")
    if price:
        items.append(f'<div class="mkt-card"><label>Share Price</label><span class="val">${price:.2f}</span></div>')
    if not items:
        return ""
    inner = "".join(items)
    return f'<div class="mkt-panel"><h3>Market Data</h3><div class="mkt-grid">{inner}</div></div>'


def _executive_summary_html(report: GapReportOutput) -> str:
    if not report.executive_summary:
        return ""
    return f"""
<section id="exec" class="fade-in">
  <div class="exec-summary">
    <h2>Executive Summary</h2>
    <div class="exec-body">
      {report.executive_summary}
    </div>
  </div>
</section>"""


def _peer_comparison_html(report: GapReportOutput) -> str:
    if not report.peer_comparison:
        return ""
    return f"""
<section id="peers" class="fade-in">
  <h2>Peer Comparison <span class="count">key financial metrics</span></h2>
  <div class="peer-wrap">
    {report.peer_comparison}
  </div>
</section>"""


def _fmt_fin(val) -> str:
    try:
        v = float(val)
    except (ValueError, TypeError):
        return str(val)
    if abs(v) >= 1e12:
        return f"{v/1e12:.2f}T"
    elif abs(v) >= 1e9:
        return f"{v/1e9:.2f}B"
    elif abs(v) >= 1e6:
        return f"{v/1e6:.2f}M"
    elif abs(v) >= 1e3:
        return f"{v/1e3:.1f}K"
    else:
        return f"{v:.2f}"
