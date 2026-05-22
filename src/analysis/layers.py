"""
Layer extraction from live_collector output.

Layer 1 (Self-Image): What the company says about itself.
Layer 2 (Data Reality): What financials, growth, and market data actually show.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Layer1:
    narrative: str = ""
    tagline: str = ""
    mission: str = ""
    positioning: str = ""
    claims: list[str] = field(default_factory=list)


@dataclass
class Layer2:
    summary: str = ""
    revenue_signal: str = ""
    growth_signal: str = ""
    funding_signal: str = ""
    market_signal: str = ""
    employee_signal: str = ""
    expansion_signal: str = ""
    hq_location: str = ""
    founded_year: Optional[int] = None
    employee_count: Optional[int] = None
    company_name: str = ""
    data_quality: str = ""
    sector: str = ""
    description: str = ""

    def to_signals_dict(self) -> dict:
        return {
            "revenue": self.revenue_signal,
            "growth": self.growth_signal,
            "funding": self.funding_signal,
            "market": self.market_signal,
            "employees": self.employee_signal,
            "hq": self.hq_location,
            "founded_year": self.founded_year,
            "expansion": self.expansion_signal,
        }


def extract_layer1(report: dict) -> Layer1:
    sd = report.get("self_description", {})
    core = report.get("core_data", {})

    layer = Layer1(
        tagline=sd.get("tagline", ""),
        mission=sd.get("mission", ""),
        positioning=sd.get("industry_positioning", ""),
    )

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

    layer.narrative = (
        " ".join(parts) if parts else "No public self-description available."
    )
    layer.claims = _extract_claims(layer.narrative)
    return layer


def extract_layer2(report: dict) -> Layer2:
    fin = report.get("financials", {})
    growth = report.get("growth_signals", {})
    market = report.get("market_position", {})
    core = report.get("core_data", {})

    layer = Layer2(company_name=report.get("company_name", ""))
    layer.hq_location = core.get("hq_location") or ""
    layer.founded_year = core.get("founded_year")
    layer.sector = core.get("sector") or ""
    layer.description = core.get("description") or ""

    emp = core.get("employees")
    if emp is not None:
        try:
            layer.employee_count = int(emp)
            layer.employee_signal = f"{layer.employee_count:,} employees"
        except (TypeError, ValueError):
            layer.employee_signal = str(emp)

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

    if fin.get("funding_total"):
        parts = [f"Total funding: {fin['funding_total']}"]
        if fin.get("last_funding_round"):
            parts.append(f"Last round: {fin['last_funding_round']}")
        if fin.get("notable_investors"):
            parts.append(f"Investors: {', '.join(fin['notable_investors'])}")
        layer.funding_signal = "; ".join(parts)

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

    if market.get("market"):
        layer.market_signal = market["market"]
    if market.get("competitors"):
        layer.market_signal += f" | Competitors: {', '.join(market['competitors'])}"
    if market.get("moat_description"):
        layer.market_signal += f" | Moat: {market['moat_description']}"

    exp = growth.get("expansion_indicators", [])
    if exp:
        layer.expansion_signal = "; ".join(exp)

    filled = sum(
        1
        for v in [
            layer.revenue_signal,
            layer.funding_signal,
            layer.growth_signal,
            layer.market_signal,
            layer.employee_signal,
        ]
        if v
    )
    layer.data_quality = (
        "rich" if filled >= 4 else ("moderate" if filled >= 2 else "sparse")
    )

    summary_parts = [
        s
        for s in [
            layer.revenue_signal,
            layer.funding_signal,
            layer.growth_signal,
            layer.employee_signal,
            layer.market_signal,
        ]
        if s
    ]
    layer.summary = (
        " | ".join(summary_parts) if summary_parts else "Limited data available."
    )
    return layer


def _extract_claims(text: str) -> list[str]:
    claims = []
    text_lower = text.lower()

    claim_patterns = {
        "leadership": [
            "leader",
            "leading",
            "market leader",
            "#1",
            "number one",
            "pioneer",
            "largest",
        ],
        "scale": [
            "global",
            "worldwide",
            "thousands of",
            "millions of",
            "100+",
            "1000+",
        ],
        "heritage": [
            "founded in",
            "years of",
            "century",
            "heritage",
            "since 19",
            "since 20",
        ],
        "innovation": [
            "ai-native",
            "ai powered",
            "ai-powered",
            "innovative",
            "cutting-edge",
            "next-generation",
            "transform",
            "disrupt",
        ],
        "growth": ["fastest-growing", "rapidly growing", "expanding", "scaling"],
        "trust": ["trusted", "reliable", "secure", "enterprise-grade", "fortune 500"],
        "full-service": [
            "end-to-end",
            "full-service",
            "comprehensive",
            "one-stop",
            "complete solution",
        ],
        "sustainability": [
            "sustainable",
            "green",
            "net-zero",
            "net zero",
            "carbon neutral",
            "eco-friendly",
            "environmentally",
            "renewable",
            "esg",
        ],
        "simplicity": [
            "simple",
            "easy",
            "intuitive",
            "frictionless",
            "no-code",
            "low code",
            "easy-to-use",
            "easy to use",
        ],
        "uniqueness": [
            "unique",
            "revolutionary",
            "first-of-its-kind",
            "first of its kind",
            "category creator",
            "first mover",
            "groundbreaking",
            "pioneer in",
            "only company",
        ],
        "moat_claim": [
            "network effect",
            "network effects",
            "data moat",
            "platform moat",
            "flywheel",
            "ecosystem",
        ],
    }

    for category, keywords in claim_patterns.items():
        for kw in keywords:
            if kw in text_lower:
                claims.append(category)
                break

    return claims
