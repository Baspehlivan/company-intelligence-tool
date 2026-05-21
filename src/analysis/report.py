"""
Report assembly: combines layers, gaps, and insights into the final output.

The output format mirrors collect.py's CompanyReport structure so the two
modules are interchangeable.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

from .layers import Layer1, Layer2, extract_layer1, extract_layer2
from .gaps import GapReport, Gap, detect_gaps
from .insights import ReframingInsight, synthesize_insight


@dataclass
class GapReportOutput:
    """The final structured output from the analysis engine."""

    company_name: str = ""
    analyzed_at: str = ""
    data_quality: str = ""  # "rich", "moderate", "sparse"

    # Layer summaries
    layer1_summary: str = ""  # What the company says
    layer2_summary: str = ""  # What the data shows

    # The reframing
    what_company_says: str = ""
    what_data_shows: str = ""
    interview_insight: str = ""
    key_tension: str = ""
    confidence: str = ""  # "high", "medium", "low"

    # Detailed gaps
    gaps: list[dict] = field(default_factory=list)

    # Talking points for interview prep
    talking_points: list[str] = field(default_factory=list)

    # Source traceability
    data_sources: list[str] = field(default_factory=list)

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
) -> GapReportOutput:
    """Build a complete gap report from live_collector output.

    Args:
        collector_output: The dict returned by live_collector.fetch_company()
        company_name: Override company name (uses collector_output.company_name if not given)

    Returns:
        GapReportOutput with all layers, gaps, and insights assembled
    """
    name = company_name or collector_output.get("company_name", "Unknown")

    # Extract layers
    layer1 = extract_layer1(collector_output)
    layer2 = extract_layer2(collector_output)

    # Detect gaps
    gaps = detect_gaps(layer1, layer2)

    # Synthesize insight
    insight = synthesize_insight(layer1, layer2, gaps, company_name=name)

    # Collect sources
    sources = []
    for src in collector_output.get("_sources", []):
        if isinstance(src, dict):
            if src.get("source"):
                sources.append(src["source"])
            elif src.get("error"):
                sources.append(f"error: {src['error']}")

    # Assemble output
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
            }
            for g in gaps.gaps
        ],
        talking_points=insight.talking_points,
        data_sources=sources,
    )
