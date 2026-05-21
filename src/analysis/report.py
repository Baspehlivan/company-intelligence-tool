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
    )
