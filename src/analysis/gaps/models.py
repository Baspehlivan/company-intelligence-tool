"""Gap data models and strong-label mappings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Gap:
    category: str
    severity: str  # high, medium, low
    claim: str
    reality: str
    note: str = ""

    @property
    def strong_label(self) -> str:
        return _STRONG_LABELS.get(self.category, "")


@dataclass
class GapReport:
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

    @property
    def dominant_gap(self) -> Optional[Gap]:
        severity_order = {"high": 0, "medium": 1, "low": 2}
        return (
            min(self.gaps, key=lambda g: severity_order.get(g.severity, 9))
            if self.gaps
            else None
        )

    @property
    def strong_gap_label(self) -> str:
        d = self.dominant_gap
        return d.strong_label if d else ""


_STRONG_LABELS: dict[str, str] = {
    "heritage_vs_transformation": "Legacy Disguise",
    "growth_mismatch": "Growth Theatre",
    "hidden_growth": "Undersold Momentum",
    "scale_claim": "Scale Bluff",
    "leadership_vs_headcount": "Category Delusion",
    "global_vs_regional": "Global Facade",
    "ai_native_vs_legacy": "AI Wrapper",
    "enterprise_claim_startup_reality": "Enterprise Mirage",
    "narrative_staleness": "Old Wine, New Label",
    "legacy_disruption_paradox": "Disruption Theatre",
    "enterprise_vs_team": "Enterprise Mirage",
    "platform_claim_narrow_reality": "Suite Illusion",
    "product_category_gap": "Category Confusion",
    "revenue_shrinkage": "Decline Cover-up",
    "age_vs_transformation_velocity": "Pillar-to-Post Pivot",
    "competitor_adjacency_gap": "Name-Drop Gap",
    "local_champion_facade": "Local Champion Facade",
    "full_service_vs_niche": "Niche in Disguise",
    "innovation_vs_stage": "Innovation Theatre",
    "funding_silence": "Funding Quiet",
    "trust_vs_team": "Credibility Gap",
    "market_share_gap": "David-vs-Goliath Gap",
    "positioning_drift": "Positioning Drift",
    "heritage_vs_innovation_paradox": "Legacy Disguise",
    "heritage_vs_startup_language": "Maturity Masquerade",
    "heritage_vs_scale_overlap": "Heritage Halo",
    "innovation_vs_trust_paradox": "Innovation-Trust Trap",
    "scale_vs_nimble_innovation": "Scale-Stasis Paradox",
    "local_vs_global_narrative": "Local-Global Split",
    "narrative_void": "Narrative Void",
    "entity_scope": "Entity Scope Ambiguity",
    "identity_transition": "Identity in Flux",
    "name_collision": "Name Collision Risk",
    "silent_positioning": "Silent Operator",
    "revenue_per_employee_gap": "Productivity Gap",
    "funding_efficiency_gap": "Capital Intensity",
    "claim_contradiction": "Self-Contradiction",
    "esg_sustainability_gap": "Green Facade",
    "customer_concentration_gap": "Whale Dependency",
    "moat_delusion": "Moat Mirage",
    "regulatory_posture_gap": "Compliance Cover",
    "market_timing_gap": "Timing Mismatch",
    "complexity_denial_gap": "Simplicity Spin",
}
