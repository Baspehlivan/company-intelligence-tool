"""
Layer extraction from live_collector output.

Layer 1 (Self-Image): What the company says about itself.
Layer 2 (Data Reality): What financials, growth, and market data actually show.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Layer1:
    """What the company says publicly."""

    narrative: str = ""  # Synthesized self-description
    tagline: str = ""
    mission: str = ""
    positioning: str = ""
    claims: list[str] = field(default_factory=list)  # Extracted claims


@dataclass
class Layer2:
    """What the data shows."""

    summary: str = ""  # Synthesized data story
    revenue_signal: str = ""
    growth_signal: str = ""
    funding_signal: str = ""
    market_signal: str = ""
    employee_signal: str = ""
    expansion_signal: str = ""
    data_quality: str = ""  # "rich", "moderate", "sparse"


def extract_layer1(report: dict) -> Layer1:
    """Extract Layer 1 (self-image) from a collector report dict."""
    sd = report.get("self_description", {})
    core = report.get("core_data", {})

    layer = Layer1(
        tagline=sd.get("tagline", ""),
        mission=sd.get("mission", ""),
        positioning=sd.get("industry_positioning", ""),
    )

    # Build narrative from available self-description fields
    parts = []
    if layer.tagline:
        parts.append(layer.tagline)
    if layer.mission:
        parts.append(layer.mission)
    if layer.positioning:
        parts.append(layer.positioning)
    for stmt in sd.get("public_statements", []):
        if stmt:
            parts.append(stmt)
    if core.get("description") and not parts:
        parts.append(core["description"])

    layer.narrative = " ".join(parts) if parts else "No public self-description available."

    # Extract discrete claims from the narrative
    layer.claims = _extract_claims(layer.narrative)

    return layer


def extract_layer2(report: dict) -> Layer2:
    """Extract Layer 2 (data reality) from a collector report dict."""
    fin = report.get("financials", {})
    growth = report.get("growth_signals", {})
    market = report.get("market_position", {})
    core = report.get("core_data", {})

    layer = Layer2()

    # Revenue signal
    rev = fin.get("revenue")
    if rev:
        if isinstance(rev, dict):
            years = sorted(rev.keys())
            if len(years) >= 2:
                layer.revenue_signal = f"Revenue trend: {years[0]}={rev[years[0]]} -> {years[-1]}={rev[years[-1]]}"
            elif years:
                layer.revenue_signal = f"Revenue: {rev[years[0]]}"
        else:
            layer.revenue_signal = str(rev)

    # Funding signal
    if fin.get("funding_total"):
        parts = [f"Total funding: {fin['funding_total']}"]
        if fin.get("last_funding_round"):
            parts.append(f"Last round: {fin['last_funding_round']}")
        if fin.get("notable_investors"):
            parts.append(f"Investors: {', '.join(fin['notable_investors'])}")
        layer.funding_signal = "; ".join(parts)

    # Growth signals
    growth_parts = []
    if growth.get("revenue_trend"):
        growth_parts.append(growth["revenue_trend"])
    if growth.get("employee_trend"):
        growth_parts.append(growth["employee_trend"])
    if growth.get("recent_acquisitions"):
        growth_parts.append(f"Acquisitions: {', '.join(growth['recent_acquisitions'])}")
    if growth.get("expansion_indicators"):
        growth_parts.append(f"Expanding: {', '.join(growth['expansion_indicators'])}")
    layer.growth_signal = "; ".join(growth_parts) if growth_parts else ""

    # Market signal
    if market.get("market"):
        layer.market_signal = market["market"]
    if market.get("competitors"):
        layer.market_signal += f" | Competitors: {', '.join(market['competitors'])}"
    if market.get("moat_description"):
        layer.market_signal += f" | Moat: {market['moat_description']}"

    # Employee signal
    if core.get("employees"):
        layer.employee_signal = f"{core['employees']:,} employees"

    # Expansion signal
    exp = growth.get("expansion_indicators", [])
    if exp:
        layer.expansion_signal = "; ".join(exp)

    # Data quality assessment
    filled = sum(1 for v in [
        layer.revenue_signal, layer.funding_signal, layer.growth_signal,
        layer.market_signal, layer.employee_signal
    ] if v)
    layer.data_quality = "rich" if filled >= 4 else ("moderate" if filled >= 2 else "sparse")

    # Build summary
    summary_parts = [
        s for s in [
            layer.revenue_signal, layer.funding_signal, layer.growth_signal,
            layer.employee_signal, layer.market_signal
        ] if s
    ]
    layer.summary = " | ".join(summary_parts) if summary_parts else "Limited data available."

    return layer


def _extract_claims(text: str) -> list[str]:
    """Extract discrete claims from company narrative text.

    Looks for common positioning patterns: leadership claims, scale claims,
    innovation claims, heritage claims, etc.
    """
    claims = []
    text_lower = text.lower()

    claim_patterns = {
        "leadership": ["leader", "leading", "market leader", "#1", "number one", "pioneer"],
        "scale": ["global", "worldwide", "thousands of", "millions of", "100+", "1000+"],
        "heritage": ["founded in", "years of", "century", "heritage", "since 19", "since 20"],
        "innovation": ["ai-powered", "innovative", "cutting-edge", "next-generation", "transform", "disrupt"],
        "growth": ["fastest-growing", "rapidly growing", "expanding", "scaling"],
        "trust": ["trusted", "reliable", "secure", "enterprise-grade", "fortune 500"],
        "full-service": ["end-to-end", "full-service", "comprehensive", "one-stop", "complete solution"],
    }

    for category, keywords in claim_patterns.items():
        for kw in keywords:
            if kw in text_lower:
                claims.append(category)
                break

    return claims
