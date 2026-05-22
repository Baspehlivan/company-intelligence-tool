"""
Sector benchmark tables for percentile ranking.

Provides median, Q1, Q3 values for key financial metrics by sector.
Sourced from aggregated US public company data (approximate).

Usage:
    from src.analysis.benchmarks import rank_vs_sector
    rank = rank_vs_sector("Technology", "gross_margin", 46.9)
    # -> {"percentile": "Q3", "label": "Above median", "median": 55.0}
"""

from __future__ import annotations

SECTOR_BENCHMARKS: dict[str, dict[str, dict[str, float]]] = {
    "Technology": {
        "gross_margin": {"q1": 45.0, "median": 60.0, "q3": 75.0},
        "operating_margin": {"q1": 8.0, "median": 18.0, "q3": 30.0},
        "net_margin": {"q1": 5.0, "median": 12.0, "q3": 22.0},
        "rd_pct": {"q1": 5.0, "median": 10.0, "q3": 18.0},
        "revenue_growth": {"q1": 2.0, "median": 10.0, "q3": 22.0},
        "ev_revenue": {"q1": 1.5, "median": 4.0, "q3": 8.0},
        "ev_ebitda": {"q1": 8.0, "median": 15.0, "q3": 25.0},
        "pe_ratio": {"q1": 12.0, "median": 22.0, "q3": 35.0},
    },
    "SaaS": {
        "gross_margin": {"q1": 65.0, "median": 75.0, "q3": 82.0},
        "operating_margin": {"q1": -5.0, "median": 10.0, "q3": 22.0},
        "net_margin": {"q1": -8.0, "median": 5.0, "q3": 18.0},
        "rd_pct": {"q1": 15.0, "median": 22.0, "q3": 30.0},
        "revenue_growth": {"q1": 10.0, "median": 22.0, "q3": 40.0},
        "ev_revenue": {"q1": 4.0, "median": 8.0, "q3": 15.0},
        "ev_ebitda": {"q1": 15.0, "median": 25.0, "q3": 45.0},
        "pe_ratio": {"q1": 20.0, "median": 35.0, "q3": 60.0},
    },
    "Enterprise": {
        "gross_margin": {"q1": 40.0, "median": 55.0, "q3": 68.0},
        "operating_margin": {"q1": 5.0, "median": 15.0, "q3": 25.0},
        "net_margin": {"q1": 3.0, "median": 10.0, "q3": 18.0},
        "rd_pct": {"q1": 8.0, "median": 14.0, "q3": 22.0},
        "revenue_growth": {"q1": 3.0, "median": 8.0, "q3": 18.0},
        "ev_revenue": {"q1": 2.0, "median": 4.5, "q3": 8.0},
        "ev_ebitda": {"q1": 10.0, "median": 18.0, "q3": 30.0},
        "pe_ratio": {"q1": 15.0, "median": 25.0, "q3": 40.0},
    },
    "Fintech": {
        "gross_margin": {"q1": 30.0, "median": 50.0, "q3": 65.0},
        "operating_margin": {"q1": 5.0, "median": 18.0, "q3": 30.0},
        "net_margin": {"q1": 3.0, "median": 12.0, "q3": 22.0},
        "rd_pct": {"q1": 5.0, "median": 10.0, "q3": 18.0},
        "revenue_growth": {"q1": 5.0, "median": 12.0, "q3": 25.0},
        "ev_revenue": {"q1": 2.0, "median": 5.0, "q3": 10.0},
        "ev_ebitda": {"q1": 10.0, "median": 20.0, "q3": 35.0},
        "pe_ratio": {"q1": 12.0, "median": 20.0, "q3": 30.0},
    },
    "Logistics": {
        "gross_margin": {"q1": 15.0, "median": 25.0, "q3": 35.0},
        "operating_margin": {"q1": 3.0, "median": 8.0, "q3": 14.0},
        "net_margin": {"q1": 2.0, "median": 5.0, "q3": 10.0},
        "rd_pct": {"q1": 0.5, "median": 1.5, "q3": 3.0},
        "revenue_growth": {"q1": 0.0, "median": 4.0, "q3": 10.0},
        "ev_revenue": {"q1": 0.5, "median": 1.0, "q3": 2.0},
        "ev_ebitda": {"q1": 5.0, "median": 10.0, "q3": 15.0},
        "pe_ratio": {"q1": 8.0, "median": 15.0, "q3": 22.0},
    },
    "Consumer": {
        "gross_margin": {"q1": 25.0, "median": 40.0, "q3": 55.0},
        "operating_margin": {"q1": 5.0, "median": 12.0, "q3": 20.0},
        "net_margin": {"q1": 3.0, "median": 8.0, "q3": 15.0},
        "rd_pct": {"q1": 2.0, "median": 5.0, "q3": 10.0},
        "revenue_growth": {"q1": 1.0, "median": 5.0, "q3": 12.0},
        "ev_revenue": {"q1": 0.8, "median": 1.5, "q3": 3.0},
        "ev_ebitda": {"q1": 6.0, "median": 12.0, "q3": 18.0},
        "pe_ratio": {"q1": 10.0, "median": 18.0, "q3": 28.0},
    },
    "Consulting": {
        "gross_margin": {"q1": 20.0, "median": 30.0, "q3": 40.0},
        "operating_margin": {"q1": 8.0, "median": 15.0, "q3": 22.0},
        "net_margin": {"q1": 5.0, "median": 10.0, "q3": 16.0},
        "rd_pct": {"q1": 1.0, "median": 2.0, "q3": 5.0},
        "revenue_growth": {"q1": 2.0, "median": 6.0, "q3": 12.0},
        "ev_revenue": {"q1": 1.0, "median": 2.0, "q3": 3.5},
        "ev_ebitda": {"q1": 8.0, "median": 14.0, "q3": 20.0},
        "pe_ratio": {"q1": 12.0, "median": 18.0, "q3": 25.0},
    },
    "Design": {
        "gross_margin": {"q1": 50.0, "median": 65.0, "q3": 78.0},
        "operating_margin": {"q1": 5.0, "median": 15.0, "q3": 25.0},
        "net_margin": {"q1": 3.0, "median": 10.0, "q3": 20.0},
        "rd_pct": {"q1": 15.0, "median": 25.0, "q3": 35.0},
        "revenue_growth": {"q1": 8.0, "median": 15.0, "q3": 28.0},
        "ev_revenue": {"q1": 4.0, "median": 7.0, "q3": 12.0},
        "ev_ebitda": {"q1": 15.0, "median": 25.0, "q3": 40.0},
        "pe_ratio": {"q1": 18.0, "median": 30.0, "q3": 50.0},
    },
}

# Sector aliases — map company.yaml sectors to benchmark sectors
SECTOR_ALIASES: dict[str, str] = {
    "consumer_tech": "Consumer",
    "consumer": "Consumer",
    "saas": "SaaS",
    "software": "SaaS",
    "enterprise": "Enterprise",
    "enterprise_software": "Enterprise",
    "enterprise_tech": "Enterprise",
    "fintech": "Fintech",
    "financial_services": "Fintech",
    "logistics": "Logistics",
    "transportation": "Logistics",
    "supply_chain": "Logistics",
    "consulting": "Consulting",
    "professional_services": "Consulting",
    "design_tools": "Design",
    "design": "Design",
    "technology": "Technology",
    "tech": "Technology",
    "hardware": "Technology",
    "semiconductor": "Technology",
    "healthcare": "Technology",
    "biotech": "Technology",
    "media": "Consumer",
    "ecommerce": "Consumer",
    "retail": "Consumer",
    "b2b_software": "SaaS",
    "b2b_saas": "SaaS",
    "cloud": "SaaS",
    "data_infrastructure": "Enterprise",
    "data_analytics": "Enterprise",
    "cybersecurity": "Enterprise",
    "ai": "Technology",
    "artificial_intelligence": "Technology",
    "manufacturing": "Logistics",
    "industrial": "Logistics",
    "automotive": "Consumer",
}

PERCENTILE_LABELS: dict[str, str] = {
    "above_q3": "Top quartile",
    "q2_q3": "Above median",
    "q1_q2": "Below median",
    "below_q1": "Bottom quartile",
}


def normalize_sector(sector: str) -> str | None:
    """Map company sector to benchmark sector name.

    Matches by:
      1. Exact alias key
      2. Token overlap — find best alias matching most tokens
      3. Direct benchmark sector name
    """
    if not sector:
        return None
    key = sector.lower().strip().replace(" ", "_")

    # 1. Exact alias match
    if key in SECTOR_ALIASES:
        return SECTOR_ALIASES[key]

    # 2. Token overlap: e.g. "Enterprise Software" -> "enterprise" -> "Enterprise"
    tokens = set(key.split("_"))
    best_alias = None
    best_score = 0
    for alias_key, bench_sector in SECTOR_ALIASES.items():
        alias_tokens = set(alias_key.split("_"))
        overlap = len(tokens & alias_tokens)
        if overlap > best_score:
            best_score = overlap
            best_alias = bench_sector
    if best_score > 0:
        return best_alias

    # 3. Direct benchmark sector match
    return key if key in SECTOR_BENCHMARKS else None


def rank_vs_sector(
    sector: str, metric: str, value: float | None
) -> dict | None:
    """Rank a metric value against sector benchmarks.

    Returns dict with:
      - percentile: "above_q3" | "q2_q3" | "q1_q2" | "below_q1"
      - label: "Top quartile" | "Above median" | "Below median" | "Bottom quartile"
      - median: sector median value
      - q1, q3: quartile boundaries
    """
    if value is None:
        return None
    bench_sector = normalize_sector(sector)
    if not bench_sector:
        return None
    bench = SECTOR_BENCHMARKS.get(bench_sector, {}).get(metric)
    if not bench:
        return None

    q1 = bench["q1"]
    q3 = bench["q3"]
    median = bench["median"]

    if value > q3:
        percentile = "above_q3"
    elif value > median:
        percentile = "q2_q3"
    elif value > q1:
        percentile = "q1_q2"
    else:
        percentile = "below_q1"

    return {
        "percentile": percentile,
        "label": PERCENTILE_LABELS[percentile],
        "median": median,
        "q1": q1,
        "q3": q3,
    }


def benchmark_summary(sector: str, ratios: dict) -> str:
    """Generate HTML snippet with sector-relative rankings for key metrics."""
    bench_sector = normalize_sector(sector)
    if not bench_sector:
        return ""
    lines = []
    metrics = [
        ("gross_margin", "Gross margin", "%"),
        ("operating_margin", "Operating margin", "%"),
        ("net_margin", "Net margin", "%"),
        ("revenue_growth", "Revenue growth", "%"),
        ("rd_pct", "R&D spend", "%"),
    ]

    for key, label, unit in metrics:
        latest = None
        data = ratios.get(key, {})
        if isinstance(data, dict) and data:
            latest = data.get(sorted(data.keys())[-1])
        if latest is None:
            continue
        rank = rank_vs_sector(sector, key, latest)
        if rank:
            lines.append(
                f"  {label}: {latest:.1f}{unit} "
                f"<span class=\"bench-rank bench-{rank['percentile']}\">"
                f"({rank['label']} &mdash; sector median: {rank['median']:.1f}{unit})</span>"
            )

    # Market multiples
    mult_metrics = [
        ("ev_revenue", "EV/Revenue", "x"),
        ("ev_ebitda", "EV/EBITDA", "x"),
        ("pe_ratio", "P/E", "x"),
    ]
    for key, label, unit in mult_metrics:
        val = ratios.get(key)
        if val is None:
            continue
        rank = rank_vs_sector(sector, key, val)
        if rank:
            lines.append(
                f"  {label}: {val:.1f}{unit} "
                f"<span class=\"bench-rank bench-{rank['percentile']}\">"
                f"({rank['label']} &mdash; sector median: {rank['median']:.1f}{unit})</span>"
            )

    if not lines:
        return ""
    return f"<strong>Sector benchmark: {bench_sector}</strong><br>" + "<br>".join(lines)
