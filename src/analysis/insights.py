"""
Insight synthesis: turn detected gaps into interview-ready reframing.

Uses LLM when configured (OPENAI_API_KEY / ANTHROPIC_API_KEY), else template fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .layers import Layer1, Layer2
from .gaps import GapReport, Gap


@dataclass
class ReframingInsight:
    what_company_says: str
    what_data_shows: str
    interview_insight: str
    key_tension: str
    confidence: str
    talking_points: list[str]
    strong_gap_label: str = ""
    synthesis_mode: str = "template"  # "llm" | "template"
    gap_count: int = 0
    high_severity_count: int = 0


def synthesize_insight(
    layer1: Layer1,
    layer2: Layer2,
    gaps: GapReport,
    company_name: str = "The company",
    edge_context: str = "",
    use_llm: bool = True,
) -> ReframingInsight:
    confidence = {
        "rich": "high",
        "moderate": "medium",
        "sparse": "low",
    }.get(layer2.data_quality, "low")

    if use_llm:
        llm_result = _synthesize_llm(
            layer1, layer2, gaps, company_name, edge_context, confidence
        )
        if llm_result:
            llm_result.gap_count = len(gaps.gaps)
            llm_result.high_severity_count = gaps.high_severity_count
            if not llm_result.strong_gap_label:
                llm_result.strong_gap_label = gaps.strong_gap_label
            return llm_result

    return _synthesize_template(layer1, layer2, gaps, company_name, confidence)


def _synthesize_llm(
    layer1: Layer1,
    layer2: Layer2,
    gaps: GapReport,
    company_name: str,
    edge_context: str,
    confidence: str,
) -> Optional[ReframingInsight]:
    from .llm import get_client
    from .prompts import INSIGHT_SYSTEM, insight_user_prompt

    client = get_client()
    if not client.available:
        return None

    gap_dicts = [
        {
            "category": g.category,
            "severity": g.severity,
            "claim": g.claim,
            "reality": g.reality,
            "note": g.note,
        }
        for g in gaps.gaps
    ]

    payload = client.complete_json(
        INSIGHT_SYSTEM,
        insight_user_prompt(
            company_name=company_name,
            layer1_narrative=layer1.narrative,
            layer1_claims=layer1.claims,
            layer2_summary=layer2.summary,
            layer2_signals=layer2.to_signals_dict(),
            gaps=gap_dicts,
            edge_context=edge_context,
            data_quality=layer2.data_quality,
        ),
    )
    if not payload:
        return None

    talking = payload.get("talking_points") or []
    if isinstance(talking, str):
        talking = [talking]

    return ReframingInsight(
        what_company_says=payload.get("what_company_says")
        or _build_layer1_summary(layer1, company_name),
        what_data_shows=payload.get("what_data_shows")
        or _build_layer2_summary(layer2, company_name),
        interview_insight=payload.get("interview_insight") or "",
        key_tension=payload.get("key_tension")
        or _identify_key_tension(gaps, layer1, layer2),
        confidence=confidence,
        talking_points=[str(t) for t in talking[:6]],
        strong_gap_label=payload.get("strong_gap_label") or "",
        synthesis_mode=client.backend_name if client.backend_name != "none" else "llm",
        gap_count=len(gaps.gaps),
        high_severity_count=gaps.high_severity_count,
    )


def _synthesize_template(
    layer1: Layer1,
    layer2: Layer2,
    gaps: GapReport,
    company_name: str,
    confidence: str,
) -> ReframingInsight:
    return ReframingInsight(
        what_company_says=_build_layer1_summary(layer1, company_name),
        what_data_shows=_build_layer2_summary(layer2, company_name),
        interview_insight=_generate_interview_insight_template(
            layer1, layer2, gaps, company_name
        ),
        key_tension=_identify_key_tension(gaps, layer1, layer2),
        confidence=confidence,
        talking_points=_generate_talking_points(layer1, layer2, gaps),
        synthesis_mode="template",
        strong_gap_label=gaps.strong_gap_label,
        gap_count=len(gaps.gaps),
        high_severity_count=gaps.high_severity_count,
    )


def _build_layer1_summary(layer1: Layer1, company_name: str) -> str:
    if (
        not layer1.narrative
        or layer1.narrative == "No public self-description available."
    ):
        return f"{company_name} has limited public self-description available."

    parts = [f"{company_name} positions itself as:"]
    if layer1.tagline:
        parts.append(f'"{layer1.tagline}"')
    if layer1.positioning:
        parts.append(layer1.positioning)
    if layer1.claims:
        parts.append(f"Key claims: {', '.join(layer1.claims)}.")
    return " ".join(parts)


def _build_layer2_summary(layer2: Layer2, company_name: str) -> str:
    if layer2.data_quality == "sparse":
        return f"Limited data available for {company_name}. Key metrics are sparse."

    parts = [f"Data for {company_name} shows:"]
    if layer2.revenue_signal:
        parts.append(layer2.revenue_signal + ".")
    if layer2.funding_signal:
        parts.append(f"Funding: {layer2.funding_signal}.")
    if layer2.growth_signal:
        parts.append(f"Growth: {layer2.growth_signal}.")
    if layer2.employee_signal:
        parts.append(f"Team: {layer2.employee_signal}.")
    if layer2.market_signal:
        parts.append(f"Market: {layer2.market_signal}.")
    return " ".join(parts)


def _identify_key_tension(gaps: GapReport, layer1: Layer1, layer2: Layer2) -> str:
    if not gaps.has_gaps:
        if layer2.data_quality == "sparse":
            return "Limited public data makes it hard to verify positioning claims."
        return "Public positioning and available data appear broadly aligned."

    severity_order = {"high": 0, "medium": 1, "low": 2}
    sorted_gaps = sorted(gaps.gaps, key=lambda g: severity_order.get(g.severity, 3))
    top = sorted_gaps[0]
    return f"{top.claim} — but {top.reality.lower()}"


def _generate_interview_insight_template(
    layer1: Layer1,
    layer2: Layer2,
    gaps: GapReport,
    company_name: str,
) -> str:
    key_tension = _identify_key_tension(gaps, layer1, layer2)

    if not gaps.has_gaps:
        if layer2.data_quality == "sparse":
            return (
                f"Public data on {company_name} is limited. An interviewer would value "
                f"someone who acknowledges this honestly and asks targeted questions about "
                f"metrics that aren't public — rather than speculating."
            )
        return (
            f"{company_name}'s public positioning appears aligned with available data. "
            f"The reframing opportunity is depth: second-order effects of their strategy."
        )

    top_gaps = [g for g in gaps.gaps if g.severity in ("high", "medium")] or gaps.gaps[
        :2
    ]
    best = top_gaps[0]

    category_hooks = {
        "heritage_vs_transformation": (
            f"See through the heritage positioning to active transformation underneath. {best.note}"
        ),
        "growth_mismatch": (
            f"Articulate what's verifiable vs aspirational in growth claims. {best.note}"
        ),
        "scale_claim": (
            f"Test scale claims against operational evidence (headcount, geo revenue). {best.note}"
        ),
        "leadership_vs_headcount": (
            f"Clarify what 'leader' means — category, product, or corporate scale. {best.note}"
        ),
        "global_vs_regional": (
            f"Ask for revenue by region, not marketing geography. {best.note}"
        ),
        "ai_native_vs_legacy": (
            f"Distinguish AI wrapper on legacy process vs model-native product. {best.note}"
        ),
        "entity_scope": (
            f"Confirm whether you're discussing the group, subsidiary, or product line. {best.note}"
        ),
        "identity_transition": (
            f"Ask what changed post-acquisition/rebrand — old narrative may be stale. {best.note}"
        ),
    }

    hook = category_hooks.get(
        best.category,
        f"Explore the tension: {best.note}" if best.note else "",
    )

    parts = [
        f"{company_name}'s public narrative vs data reality: {key_tension}.",
        hook,
    ]
    if layer2.data_quality == "sparse":
        parts.append("(Data quality limited — frame as questions, not conclusions.)")

    return " ".join(p for p in parts if p)


def _generate_talking_points(
    layer1: Layer1, layer2: Layer2, gaps: GapReport
) -> list[str]:
    points = []
    for gap in gaps.gaps:
        if gap.severity in ("high", "medium"):
            points.append(f"[{gap.category}] {gap.claim} vs {gap.reality}")

    if layer2.data_quality == "sparse":
        points.append("Data sparse — position observations as questions")
    elif layer2.data_quality == "rich":
        points.append("Rich data — use specific metrics in answers")

    if "heritage" in layer1.claims:
        points.append("Heritage may mask transformation — ask about change velocity")
    if "innovation" in layer1.claims:
        points.append("Innovation claims need product evidence — ask adoption metrics")
    if "scale" in layer1.claims:
        points.append("Scale claims — ask geo/employee/revenue breakdown")

    return points
