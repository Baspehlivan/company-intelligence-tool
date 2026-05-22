"""
Report assembly: combines layers, gaps, edge cases, and insights into final output.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

from .layers import Layer1, Layer2, extract_layer1, extract_layer2
from .gaps import GapReport, detect_gaps
from .insights import ReframingInsight, synthesize_insight
from .edge_cases import EdgeCaseContext, analyze_edge_cases


@dataclass
class GapReportOutput:
    company_name: str = ""
    analyzed_at: str = ""
    data_quality: str = ""

    layer1_summary: str = ""
    layer2_summary: str = ""

    what_company_says: str = ""
    what_data_shows: str = ""
    interview_insight: str = ""
    key_tension: str = ""
    confidence: str = ""

    gaps: list[dict] = field(default_factory=list)
    talking_points: list[str] = field(default_factory=list)
    data_sources: list[str] = field(default_factory=list)

    # Analysis metadata
    synthesis_mode: str = "template"
    edge_flags: list[str] = field(default_factory=list)
    edge_warnings: list[str] = field(default_factory=list)
    enrichment_applied: bool = False

    # v3 enhancements
    strong_gap_label: str = ""
    gap_count: int = 0
    high_severity_count: int = 0

    # v4 professional financial data
    financial_summary: str = ""  # formatted HTML financial summary from SEC EDGAR
    financial_ratios: dict = field(default_factory=dict)  # raw ratios
    executive_summary: str = ""  # one-page investment-style summary
    peer_comparison: str = ""  # peer benchmarking HTML

    # v5 professional enhancements
    market_data: dict = field(default_factory=dict)  # market-cap, EV, P/E, EV/Revenue, EV/EBITDA
    sector_benchmarks: dict = field(default_factory=dict)  # sector percentile rankings
    benchmark_html: str = ""  # formatted benchmark HTML for display
    edgar_status: str = ""  # "ok" | "not_found" | "error" | "no_ticker"
    edgar_error: str = ""  # error detail if applicable

    def __post_init__(self):
        if not self.analyzed_at:
            self.analyzed_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


def build_report(
    collector_output: dict,
    company_name: Optional[str] = None,
    use_reference_enrichment: bool = True,
    use_llm: bool = True,
) -> GapReportOutput:
    """Build a complete gap report from live_collector output."""
    enriched, edge = analyze_edge_cases(
        collector_output,
        use_reference=use_reference_enrichment,
    )

    name = company_name or enriched.get("company_name", "Unknown")
    enriched.setdefault("_sources", [])

    # ── SEC EDGAR + market data enrichment for public companies ──
    financial_summary = ""
    financial_ratios: dict = {}
    market_data: dict = {}
    edgar_status = "no_ticker"
    edgar_error = ""
    benchmark_html = ""

    ticker = enriched.get("ticker")
    if ticker:
        from src.data_collector.edgar import fetch_financials, format_financial_summary
        from src.data_collector.market import fetch_market_data

        # EDGAR financials
        edgar = fetch_financials(ticker)
        edgar_status = edgar.get("_status", "ok")
        edgar_error = edgar.get("_error", "")

        if edgar.get("revenue"):
            financial_summary = format_financial_summary(edgar)
            pick = ("revenue", "revenue_growth", "gross_margin", "operating_margin", "net_margin",
                    "revenue_per_employee", "rd_pct", "sg_a_pct", "employees",
                    "total_assets", "total_liabilities")
            financial_ratios = {k: edgar[k] for k in pick if k in edgar}

            enriched["_sources"].append({"source": "sec_edgar", "ticker": ticker})

            edgar_rev = edgar.get("revenue", {})
            if edgar_rev and not enriched.get("financials", {}).get("revenue"):
                enriched.setdefault("financials", {})["revenue"] = edgar_rev

            for mk in ("market_cap", "enterprise_value", "pe_ratio", "ev_revenue", "ev_ebitda", "price"):
                if mk in edgar:
                    financial_ratios[mk] = edgar[mk]
                    market_data[mk] = edgar[mk]

        # ── Fallback: yfinance financials for non-US public companies ──
        if not edgar.get("revenue") and edgar.get("_status") in ("not_found", "error"):
            try:
                from src.data_collector.yfinance_financials import (
                    fetch_yfinance_financials, format_yfinance_summary
                )
                yf_data = fetch_yfinance_financials(ticker)
                if yf_data.get("revenue"):
                    financial_summary = format_yfinance_summary(yf_data)
                    pick = ("revenue", "revenue_growth", "gross_margin", "operating_margin", "net_margin",
                            "rd_pct", "sg_a_pct", "total_assets", "total_liabilities",
                            "market_cap", "enterprise_value", "pe_ratio", "ev_revenue", "ev_ebitda", "price")
                    financial_ratios = {k: yf_data[k] for k in pick if k in yf_data}
                    enriched["_sources"].append({"source": "yfinance_financials", "ticker": ticker})
                    edgar_status = "ok"

                    for mk in ("market_cap", "enterprise_value", "pe_ratio", "ev_revenue", "ev_ebitda", "price"):
                        if mk in yf_data:
                            market_data[mk] = yf_data[mk]

                    yf_rev = yf_data.get("revenue", {})
                    if yf_rev and not enriched.get("financials", {}).get("revenue"):
                        enriched.setdefault("financials", {})["revenue"] = yf_rev

                    edge.warnings.append(f"Financial data from yfinance (non-US source)")
            except Exception as e:
                edge.warnings.append(f"yfinance financials failed for {ticker}: {e}")

        # Market data (independent of EDGAR — works for non-US tickers too)
        md = fetch_market_data(ticker)
        if md.get("_status") == "ok" and md.get("market_cap"):
            for mk in ("market_cap", "enterprise_value", "pe_ratio", "ev_revenue", "ev_ebitda", "price"):
                if mk in md and mk not in market_data:
                    financial_ratios[mk] = md[mk]
                    market_data[mk] = md[mk]
            enriched["_sources"].append({"source": "yfinance", "ticker": ticker})
        elif md.get("_error"):
            edge.warnings.append(f"Market data unavailable: {md['_error']}")

    # ── Fallback: extract whatever financial data exists in enriched data ──
    # This covers private companies and non-US tickers with reference data
    if not financial_ratios:
        core = enriched.get("core_data", {})
        fin = enriched.get("financials", {})
        rev_raw = fin.get("revenue")
        if isinstance(rev_raw, dict):
            financial_ratios["revenue"] = rev_raw
        employees = core.get("employees")
        if employees:
            financial_ratios["employees"] = employees
        # Try to parse revenue text for display
        rev_text = fin.get("revenue_text") or (str(list(rev_raw.values())[0]) if isinstance(rev_raw, dict) and rev_raw else "")
        if rev_text:
            financial_ratios["_revenue_text"] = rev_text

    # ── Sector benchmarks (run for ANY company with sector info) ──
    sector = enriched.get("core_data", {}).get("sector", "")
    if sector:
        from src.analysis.benchmarks import rank_vs_sector, benchmark_summary

        bench_html = benchmark_summary(sector, financial_ratios)
        if bench_html:
            benchmark_html = bench_html
            for metric in ("gross_margin", "operating_margin", "net_margin",
                           "revenue_growth", "rd_pct", "ev_revenue", "ev_ebitda", "pe_ratio"):
                raw = financial_ratios.get(metric)
                if raw is None:
                    continue
                if isinstance(raw, dict) and raw:
                    val = raw.get(sorted(raw.keys())[-1])
                else:
                    val = raw
                rank = rank_vs_sector(sector, metric, val)
                if rank:
                    financial_ratios.setdefault("_benchmarks", {})[metric] = rank

    layer1 = extract_layer1(enriched)
    layer2 = extract_layer2(enriched)

    gaps = detect_gaps(layer1, layer2, edge=edge, use_llm=use_llm)
    insight = synthesize_insight(
        layer1,
        layer2,
        gaps,
        company_name=name,
        edge_context=edge.summary,
        use_llm=use_llm,
    )

    sources = []
    for src in enriched.get("_sources", []):
        if isinstance(src, dict):
            if src.get("source"):
                sources.append(src["source"])
            elif src.get("error"):
                sources.append(f"error: {src['error']}")

    # ── Executive summary (investment one-pager style) ──
    executive_summary = _generate_executive_summary(name, enriched, financial_ratios, insight, gaps)

    # ── Peer comparison ──
    peer_comparison = _generate_peer_comparison(name, financial_ratios, enriched)

    return GapReportOutput(
        company_name=name,
        data_quality=layer2.data_quality,
        layer1_summary=layer1.narrative,
        layer2_summary=layer2.summary,
        what_company_says=insight.what_company_says,
        what_data_shows=insight.what_data_shows,
        interview_insight=insight.interview_insight,
        key_tension=insight.key_tension,
        confidence=insight.confidence,
        gaps=[
            {
                "category": g.category,
                "severity": g.severity,
                "claim": g.claim,
                "reality": g.reality,
                "note": g.note,
                "strong_label": g.strong_label,
            }
            for g in gaps.gaps
        ],
        talking_points=insight.talking_points,
        data_sources=sources,
        synthesis_mode=insight.synthesis_mode,
        edge_flags=list(edge.flags),
        edge_warnings=list(edge.warnings),
        enrichment_applied=edge.enrichment_applied,
        strong_gap_label=insight.strong_gap_label,
        gap_count=insight.gap_count,
        high_severity_count=insight.high_severity_count,
        financial_summary=financial_summary,
        financial_ratios=financial_ratios,
        executive_summary=executive_summary,
        peer_comparison=peer_comparison,
        market_data=market_data,
        sector_benchmarks=financial_ratios.get("_benchmarks", {}),
        benchmark_html=benchmark_html,
        edgar_status=edgar_status,
        edgar_error=edgar_error,
    )


def _generate_executive_summary(
    name: str, enriched: dict, ratios: dict, insight, gaps
) -> str:
    """Generate an investment-style executive summary."""
    lines = []
    core = enriched.get("core_data", {})
    sector = core.get("sector", "")
    rev = enriched.get("financials", {}).get("revenue", {})
    emp = core.get("employees")

    # Company snapshot
    lines.append(f"<strong>{name}</strong>")
    if sector:
        lines.append(f"  Sector: {sector}")
    if isinstance(rev, dict) and rev:
        latest = sorted(rev.keys())[-1]
        from src.data_collector.edgar import _fmt
        lines.append(f"  Revenue ({latest}): {_fmt(rev[latest])}")
    if emp:
        lines.append(f"  Employees: {emp:,}")

    lines.append("")
    lines.append("<strong>Key Tension</strong>")
    lines.append(f"  {insight.key_tension}")

    # Financial trends from EDGAR
    if ratios.get("revenue_growth"):
        growth = ratios["revenue_growth"]
        latest_g = sorted(growth.keys())[-1] if growth else ""
        if latest_g:
            lines.append(f"  Revenue growth ({latest_g}): {growth[latest_g]:+.1f}%")

    if ratios.get("operating_margin"):
        om = ratios["operating_margin"]
        latest_om = sorted(om.keys())[-1] if om else ""
        if latest_om:
            lines.append(f"  Operating margin ({latest_om}): {om[latest_om]:.1f}%")

    # Market data
    for label, key in [("P/E", "pe_ratio"), ("EV/Revenue", "ev_revenue"), ("EV/EBITDA", "ev_ebitda")]:
        val = ratios.get(key)
        if val:
            lines.append(f"  {label}: {val:.1f}x")

    # Sector benchmark context
    benches = ratios.get("_benchmarks", {})
    if benches:
        top = []
        for metric, rank in benches.items():
            if rank.get("percentile") in ("above_q3", "q2_q3"):
                top.append(f"{metric}: {rank['label']}")
        if top:
            lines.append("")
            lines.append(f"<strong>Sector context</strong>")
            for t in top[:2]:
                lines.append(f"  {t}")

    # Top gaps
    high_gaps = [g for g in gaps.gaps if g.severity == "high"]
    if high_gaps:
        lines.append("")
        lines.append(f"<strong>Risk Factors ({len(high_gaps)})</strong>")
        for g in high_gaps[:3]:
            lines.append(f"  &#9888; {g.strong_label or g.category}: {g.claim[:80]}")

    return "<br>".join(lines)


def _generate_peer_comparison(name: str, ratios: dict, enriched: dict) -> str:
    """Generate peer benchmarking HTML from financial ratios and market data."""
    if not ratios.get("revenue") and not ratios.get("revenue_per_employee"):
        return ""

    lines = []
    lines.append('<table class="peer-table">')
    lines.append("<tr><th>Metric</th><th>Value</th></tr>")

    rev = ratios.get("revenue", {})
    if rev:
        years = sorted(rev.keys())
        for y in years[-3:]:
            from src.data_collector.edgar import _fmt
            lines.append(f"<tr><td>Revenue {y}</td><td class='num'>{_fmt(rev[y])}</td></tr>")

    growth = ratios.get("revenue_growth", {})
    if growth:
        for y in sorted(growth.keys())[-2:]:
            cls = "pos" if growth[y] > 0 else "neg"
            lines.append(f"<tr><td>Growth {y}</td><td class='num {cls}'>{growth[y]:+.1f}%</td></tr>")

    for label, key in [("Gross margin", "gross_margin"), ("Operating margin", "operating_margin"),
                        ("Net margin", "net_margin")]:
        m = ratios.get(key, {})
        if m:
            y = sorted(m.keys())[-1]
            lines.append(f"<tr><td>{label}</td><td class='num'>{m[y]:.1f}%</td></tr>")

    rpe = ratios.get("revenue_per_employee")
    if rpe:
        lines.append(f"<tr><td>Rev/employee</td><td class='num'>${rpe:,.0f}</td></tr>")

    rd = ratios.get("rd_pct", {})
    if rd:
        y = sorted(rd.keys())[-1] if rd else ""
        if y:
            lines.append(f"<tr><td>R&D % revenue ({y})</td><td class='num'>{rd[y]:.1f}%</td></tr>")

    # Valuation multiples
    for label, key, suf in [("Market Cap", "market_cap", ""), ("Enterprise Value", "enterprise_value", ""),
                              ("P/E", "pe_ratio", "x"), ("EV/Revenue", "ev_revenue", "x"),
                              ("EV/EBITDA", "ev_ebitda", "x")]:
        val = ratios.get(key)
        if val:
            if key in ("market_cap", "enterprise_value"):
                from src.data_collector.edgar import _fmt
                lines.append(f"<tr><td>{label}</td><td class='num'>${_fmt(val)}</td></tr>")
            else:
                lines.append(f"<tr><td>{label}</td><td class='num'>{val:.1f}{suf}</td></tr>")

    lines.append("</table>")
    return "\n".join(lines)
