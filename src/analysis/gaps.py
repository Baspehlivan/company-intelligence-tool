"""
Gap detection between Layer 1 (self-image) and Layer 2 (data reality).

Identifies contradictions, tensions, and blind spots in a company's narrative
vs. what the data actually shows.
"""

from dataclasses import dataclass, field
from .layers import Layer1, Layer2


@dataclass
class Gap:
    """A single gap between what's said and what's shown."""

    category: str  # e.g., "growth_mismatch", "scale_claim", "funding_silence"
    severity: str  # "high", "medium", "low"
    claim: str  # What the company says
    reality: str  # What the data shows
    note: str = ""  # Additional context


@dataclass
class GapReport:
    """Collection of detected gaps between layers."""

    gaps: list[Gap] = field(default_factory=list)
    what_company_says: str = ""
    what_data_shows: str = ""

    @property
    def has_gaps(self) -> bool:
        return len(self.gaps) > 0

    @property
    def high_severity_count(self) -> int:
        return sum(1 for g in self.gaps if g.severity == "high")

    def by_category(self) -> dict[str, list[Gap]]:
        result: dict[str, list[Gap]] = {}
        for g in self.gaps:
            result.setdefault(g.category, []).append(g)
        return result


def detect_gaps(layer1: Layer1, layer2: Layer2) -> GapReport:
    """Compare Layer 1 and Layer 2 to find gaps.

    Runs a series of heuristic checks that look for contradictions between
    what the company claims and what the data shows.
    """
    report = GapReport()

    report.what_company_says = layer1.narrative
    report.what_data_shows = layer2.summary

    # Run all detectors
    detectors = [
        _check_growth_mismatch,
        _check_scale_claims,
        _check_innovation_vs_stage,
        _check_funding_silence,
        _check_heritage_vs_transformation,
        _check_employee_signal,
        _check_market_positioning,
    ]

    for detector in detectors:
        gaps = detector(layer1, layer2)
        report.gaps.extend(gaps)

    return report


# ── Detectors ────────────────────────────────────────────────────────────────


def _check_growth_mismatch(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Does the company claim growth but data doesn't support it (or vice versa)?"""
    gaps = []
    claims_growth = "growth" in l1.claims
    data_growth = bool(l2.growth_signal and any(
        kw in l2.growth_signal.lower()
        for kw in ["up", "growing", "expansion", "doubling", "increase"]
    ))

    if claims_growth and not data_growth:
        gaps.append(Gap(
            category="growth_mismatch",
            severity="medium",
            claim="Company positions itself as growing/fast-growing",
            reality="Growth data is sparse or doesn't clearly confirm the growth narrative",
            note="Could be private data limitation, or the growth claim may be aspirational",
        ))
    elif data_growth and not claims_growth:
        gaps.append(Gap(
            category="hidden_growth",
            severity="low",
            claim="Company doesn't emphasize growth in public positioning",
            reality=f"Data shows growth signals: {l2.growth_signal}",
            note="Potential reframing opportunity: company undersells its momentum",
        ))

    return gaps


def _check_scale_claims(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Does the company claim scale/global presence but data tells a different story?"""
    gaps = []
    claims_scale = "scale" in l1.claims

    if claims_scale:
        # Check if employees suggest a smaller operation
        if l2.employee_signal:
            emp_text = l2.employee_signal.lower()
            # Extract number
            import re
            m = re.search(r"([\d,]+)", emp_text)
            if m:
                emp_count = int(m.group(1).replace(",", ""))
                if emp_count < 200:
                    gaps.append(Gap(
                        category="scale_claim",
                        severity="medium",
                        claim="Company claims global/large-scale presence",
                        reality=f"Only {emp_count} employees — likely a smaller operation than positioning suggests",
                        note="Common for startups to claim 'global' based on a few international clients",
                    ))

    return gaps


def _check_innovation_vs_stage(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Claims of innovation/AI vs. actual funding stage and maturity."""
    gaps = []
    claims_innovation = "innovation" in l1.claims

    if claims_innovation and l2.funding_signal:
        fund_lower = l2.funding_signal.lower()
        if "seed" in fund_lower or "series a" in fund_lower:
            gaps.append(Gap(
                category="innovation_vs_stage",
                severity="medium",
                claim="Company positions as innovative/AI-powered/disruptive",
                reality=f"Still early-stage ({l2.funding_signal.split(';')[0].strip()}) — innovation claims may be ahead of product maturity",
                note="Evaluate whether the AI/innovation is core product or marketing positioning",
            ))

    return gaps


def _check_funding_silence(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Does the company avoid mentioning funding while data shows significant raises?"""
    gaps = []
    narrative_lower = l1.narrative.lower()

    funding_keywords = ["funding", "raised", "series", "investor", "capital", "investment"]
    mentions_funding = any(kw in narrative_lower for kw in funding_keywords)

    if l2.funding_signal and not mentions_funding:
        gaps.append(Gap(
            category="funding_silence",
            severity="low",
            claim="Company doesn't emphasize funding in public positioning",
            reality=f"Has raised capital: {l2.funding_signal}",
            note="May indicate focus on product over fundraising narrative, or recent raise not yet in messaging",
        ))

    return gaps


def _check_heritage_vs_transformation(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Heritage claims vs. signs of active transformation/acquisition."""
    gaps = []
    claims_heritage = "heritage" in l1.claims
    claims_full_service = "full-service" in l1.claims

    if (claims_heritage or claims_full_service) and l2.growth_signal:
        growth_lower = l2.growth_signal.lower()
        if any(kw in growth_lower for kw in ["acquisition", "acquiring", "transform", "pivot"]):
            gaps.append(Gap(
                category="heritage_vs_transformation",
                severity="high",
                claim="Company emphasizes heritage, tradition, and established identity",
                reality=f"Active transformation signals: {l2.growth_signal}",
                note="Classic reframing opportunity: the 'traditional' company is actually mid-transformation",
            ))

    return gaps


def _check_employee_signal(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Employee count vs. positioning claims."""
    gaps = []

    if l2.employee_signal:
        import re
        m = re.search(r"([\d,]+)", l2.employee_signal)
        if m:
            emp_count = int(m.group(1).replace(",", ""))

            # Claims trust/enterprise-grade but very small team
            if "trust" in l1.claims and emp_count < 50:
                gaps.append(Gap(
                    category="trust_vs_team",
                    severity="medium",
                    claim="Company positions as trusted/enterprise-grade/reliable",
                    reality=f"Team of only {emp_count} — buyers may question support capacity",
                    note="Important for enterprise sales positioning",
                ))

    return gaps


def _check_market_positioning(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Does market data align with how the company positions itself?"""
    gaps = []

    if l2.market_signal and l1.positioning:
        # Check for keyword overlap between positioning and market data
        pos_words = set(l1.positioning.lower().split())
        mkt_words = set(l2.market_signal.lower().split())
        overlap = pos_words & mkt_words

        # If positioning uses words not found in market data, it may be aspirational
        aspirational_words = pos_words - mkt_words - {
            "the", "a", "an", "and", "or", "for", "with", "in", "on", "to", "of", "is", "we", "our"
        }
        if len(aspirational_words) > 3 and len(overlap) < 2:
            gaps.append(Gap(
                category="positioning_drift",
                severity="low",
                claim=f"Company positioning uses terms not reflected in market data",
                reality=f"Market data focuses on: {l2.market_signal[:100]}",
                note="May indicate aspirational positioning or the market data source is incomplete",
            ))

    return gaps
