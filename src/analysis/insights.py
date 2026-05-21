"""
Insight synthesis: turn detected gaps into interview-ready reframing.

Takes the gap report and produces a structured insight with:
- What the company says (Layer 1 summary)
- What the data shows (Layer 2 summary)
- The reframing: how to talk about the gap in an interview context
"""

from dataclasses import dataclass
from typing import Optional
from .layers import Layer1, Layer2
from .gaps import GapReport, Gap


@dataclass
class ReframingInsight:
    """The final synthesized output: interview-ready reframing."""

    what_company_says: str
    what_data_shows: str
    interview_insight: str
    key_tension: str  # The single most important gap
    confidence: str  # "high", "medium", "low" based on data quality
    talking_points: list[str]


def synthesize_insight(
    layer1: Layer1,
    layer2: Layer2,
    gaps: GapReport,
    company_name: str = "The company",
) -> ReframingInsight:
    """Synthesize a reframing insight from layers and gaps.

    This is the core intellectual work of the engine: taking the raw gaps
    and turning them into an interview-ready narrative.
    """
    # Determine confidence from data quality
    confidence = {
        "rich": "high",
        "moderate": "medium",
        "sparse": "low",
    }.get(layer2.data_quality, "low")

    # Build Layer 1 summary
    what_says = _build_layer1_summary(layer1, company_name)

    # Build Layer 2 summary
    what_shows = _build_layer2_summary(layer2, company_name)

    # Identify the key tension (highest severity gap)
    key_tension = _identify_key_tension(gaps, layer1, layer2)

    # Generate interview insight
    interview_insight = _generate_interview_insight(
        layer1, layer2, gaps, company_name, key_tension
    )

    # Generate talking points
    talking_points = _generate_talking_points(layer1, layer2, gaps)

    return ReframingInsight(
        what_company_says=what_says,
        what_data_shows=what_shows,
        interview_insight=interview_insight,
        key_tension=key_tension,
        confidence=confidence,
        talking_points=talking_points,
    )


# ── Builders ─────────────────────────────────────────────────────────────────


def _build_layer1_summary(layer1: Layer1, company_name: str) -> str:
    """Summarize what the company says about itself."""
    if not layer1.narrative or layer1.narrative == "No public self-description available.":
        return f"{company_name} has limited public self-description available."

    parts = [f"{company_name} positions itself as:"]
    if layer1.tagline:
        parts.append(f'"{layer1.tagline}"')
    if layer1.positioning:
        parts.append(layer1.positioning)
    if layer1.claims:
        claim_str = ", ".join(layer1.claims)
        parts.append(f"Key claims: {claim_str}.")

    return " ".join(parts)


def _build_layer2_summary(layer2: Layer2, company_name: str) -> str:
    """Summarize what the data shows."""
    if layer2.data_quality == "sparse":
        return f"Limited data available for {company_name}. Key metrics are sparse."

    parts = [f"Data for {company_name} shows:"]
    if layer2.revenue_signal:
        parts.append(layer2.revenue_signal + ".")
    if layer2.funding_signal:
        parts.append(f"Funding: {layer2.funding_signal}.")
    if layer2.growth_signal:
        parts.append(f"Growth signals: {layer2.growth_signal}.")
    if layer2.employee_signal:
        parts.append(f"Team: {layer2.employee_signal}.")
    if layer2.market_signal:
        parts.append(f"Market: {layer2.market_signal}.")

    return " ".join(parts)


def _identify_key_tension(gaps: GapReport, layer1: Layer1, layer2: Layer2) -> str:
    """Find the single most important gap to highlight."""
    if not gaps.has_gaps:
        # No gaps detected — still construct a tension from available data
        if layer2.data_quality == "sparse":
            return "Limited public data makes it hard to verify positioning claims."
        return "Public positioning and available data appear broadly aligned."

    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    sorted_gaps = sorted(gaps.gaps, key=lambda g: severity_order.get(g.severity, 3))

    top = sorted_gaps[0]
    return f"{top.claim} — but {top.reality.lower()}"


def _generate_interview_insight(
    layer1: Layer1,
    layer2: Layer2,
    gaps: GapReport,
    company_name: str,
    key_tension: str,
) -> str:
    """Generate the interview-ready insight paragraph."""
    if not gaps.has_gaps:
        if layer2.data_quality == "sparse":
            return (
                f"Public data on {company_name} is limited. An interviewer would be impressed "
                f"by someone who acknowledges this honestly and focuses on what can be verified — "
                f"rather than speculating. Ask targeted questions about metrics that aren't public."
            )
        return (
            f"{company_name}'s public positioning appears to align with available data. "
            f"The reframing opportunity here is depth: go beyond what's publicly known "
            f"by asking about the second-order effects of their strategy."
        )

    # Build insight from top gaps
    top_gaps = [g for g in gaps.gaps if g.severity in ("high", "medium")]
    if not top_gaps:
        top_gaps = gaps.gaps[:2]

    parts = []

    # Open with the key tension
    parts.append(f"{company_name}'s public narrative vs. data reality:")
    parts.append(key_tension + ".")

    # Add the most interesting gap insight
    best_gap = top_gaps[0]
    if best_gap.category == "heritage_vs_transformation":
        parts.append(
            f"An interviewer would be struck by someone who sees through the heritage positioning "
            f"to the active transformation underneath. {best_gap.note}"
        )
    elif best_gap.category == "growth_mismatch":
        parts.append(
            f"The growth claims deserve scrutiny. An interviewer would value someone who can "
            f"articulate exactly what's verifiable vs. aspirational. {best_gap.note}"
        )
    elif best_gap.category == "scale_claim":
        parts.append(
            f"Scale claims vs. actual team size is a classic reframing opportunity. "
            f"An interviewer would notice someone who asks the right questions about operational capacity. "
            f"{best_gap.note}"
        )
    elif best_gap.category == "innovation_vs_stage":
        parts.append(
            f"Innovation positioning at an early stage creates a credibility gap. "
            f"An interviewer would respect someone who can distinguish between genuine technical differentiation "
            f"and marketing positioning. {best_gap.note}"
        )
    elif best_gap.category == "funding_silence":
        parts.append(
            f"The quiet funding story suggests the company lets its product speak. "
            f"An interviewer would be impressed by someone who understands what the funding trajectory implies "
            f"about investor confidence and runway. {best_gap.note}"
        )
    elif best_gap.category == "trust_vs_team":
        parts.append(
            f"Enterprise trust claims backed by a small team is a tension worth exploring. "
            f"An interviewer would value someone who can discuss how scale and trust actually relate. "
            f"{best_gap.note}"
        )
    else:
        parts.append(
            f"There's a gap worth exploring: {best_gap.note}" if best_gap.note else ""
        )

    # Close with confidence note
    if layer2.data_quality == "sparse":
        parts.append(
            "(Note: data quality is limited — frame these observations as questions, not conclusions.)"
        )

    return " ".join(p for p in parts if p)


def _generate_talking_points(
    layer1: Layer1, layer2: Layer2, gaps: GapReport
) -> list[str]:
    """Generate concise talking points for interview use."""
    points = []

    if gaps.has_gaps:
        for gap in gaps.gaps:
            if gap.severity in ("high", "medium"):
                points.append(f"[{gap.category}] {gap.claim} vs. {gap.reality}")

    # Always add a data quality note
    if layer2.data_quality == "sparse":
        points.append("Data is sparse — position observations as questions, not assertions")
    elif layer2.data_quality == "rich":
        points.append("Data is rich — strong foundation for specific, evidence-based observations")

    # Add claim-based points
    if "heritage" in layer1.claims:
        points.append("Heritage positioning may mask active transformation — ask about change velocity")
    if "innovation" in layer1.claims:
        points.append("Innovation claims need product evidence — ask about adoption metrics")
    if "scale" in layer1.claims:
        points.append("Scale claims should be tested against operational evidence")

    return points
