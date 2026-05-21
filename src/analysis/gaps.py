"""
Gap detection between Layer 1 (self-image) and Layer 2 (data reality).

Heuristic + semantic detectors, with optional LLM pass for novel gaps.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .layers import Layer1, Layer2

if TYPE_CHECKING:
    from .edge_cases import EdgeCaseContext


@dataclass
class Gap:
    category: str
    severity: str  # high, medium, low
    claim: str
    reality: str
    note: str = ""


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


def detect_gaps(
    layer1: Layer1,
    layer2: Layer2,
    edge: Optional["EdgeCaseContext"] = None,
    use_llm: bool = True,
) -> GapReport:
    report = GapReport()
    report.what_company_says = layer1.narrative
    report.what_data_shows = layer2.summary

    detectors = [
        _check_growth_mismatch,
        _check_scale_claims,
        _check_innovation_vs_stage,
        _check_funding_silence,
        _check_heritage_vs_transformation,
        _check_employee_signal,
        _check_market_positioning,
        # Semantic detectors
        _check_leadership_vs_headcount,
        _check_global_vs_regional,
        _check_ai_native_vs_age,
        _check_trust_at_scale,
        _check_zero_narrative_rich_data,
    ]

    for detector in detectors:
        report.gaps.extend(detector(layer1, layer2))

    if edge:
        report.gaps.extend(_edge_case_gaps(layer1, layer2, edge))

    if use_llm:
        from .llm import get_client
        from .edge_cases import merge_gaps

        client = get_client()
        if client.available:
            llm_gaps = _detect_gaps_llm(layer1, layer2, edge, client)
            report.gaps = merge_gaps(report.gaps, llm_gaps)

    return report


def _edge_case_gaps(l1: Layer1, l2: Layer2, edge: "EdgeCaseContext") -> list[Gap]:
    gaps = []
    if "zero_public_narrative" in edge.flags and l2.data_quality != "sparse":
        gaps.append(
            Gap(
                category="narrative_void",
                severity="medium",
                claim="No public self-description or positioning text",
                reality=f"Data still shows signals: {l2.summary[:120]}",
                note="Reframing from data-only — ask how they want to be perceived vs what metrics prove",
            )
        )
    if "possible_subsidiary" in edge.flags or "possible_brand_line" in edge.flags:
        gaps.append(
            Gap(
                category="entity_scope",
                severity="high",
                claim="Analysis target may be a subsidiary or business line",
                reality="Financial and employee figures may describe parent group or different legal entity",
                note="Clarify in interview: 'Are we discussing the group or this division?'",
            )
        )
    if "rename_or_acquisition" in edge.flags:
        gaps.append(
            Gap(
                category="identity_transition",
                severity="high",
                claim="Public brand identity may reflect pre-transaction positioning",
                reality="M&A or rebrand signals in data — operating model may have already changed",
                note="Ask what changed after the transaction, not what the old annual report said",
            )
        )
    if "ambiguous_company_name" in edge.flags:
        gaps.append(
            Gap(
                category="name_collision",
                severity="medium",
                claim=f"Company name '{l1.narrative[:40]}...' is commercially ambiguous",
                reality="Multiple distinct entities can share this name — verify ticker, HQ, and sector",
                note="Disambiguate before any strong reframing claim",
            )
        )
    return gaps


# ── Original heuristic detectors ─────────────────────────────────────────────


def _check_growth_mismatch(l1: Layer1, l2: Layer2) -> list[Gap]:
    gaps = []
    claims_growth = "growth" in l1.claims
    data_growth = bool(
        l2.growth_signal
        and any(
            kw in l2.growth_signal.lower()
            for kw in ["up", "growing", "expansion", "doubling", "increase", "acquisition"]
        )
    )
    if claims_growth and not data_growth:
        gaps.append(
            Gap(
                category="growth_mismatch",
                severity="medium",
                claim="Company positions itself as growing/fast-growing",
                reality="Growth data is sparse or doesn't clearly confirm the growth narrative",
                note="Could be private data limitation, or aspirational growth positioning",
            )
        )
    elif data_growth and not claims_growth:
        gaps.append(
            Gap(
                category="hidden_growth",
                severity="low",
                claim="Company doesn't emphasize growth in public positioning",
                reality=f"Data shows growth signals: {l2.growth_signal}",
                note="Undersold momentum — reframing opportunity",
            )
        )
    return gaps


def _check_scale_claims(l1: Layer1, l2: Layer2) -> list[Gap]:
    gaps = []
    if "scale" not in l1.claims:
        return gaps
    emp = _parse_employee_count(l2.employee_signal)
    if emp is not None and emp < 200:
        gaps.append(
            Gap(
                category="scale_claim",
                severity="medium",
                claim="Company claims global/large-scale presence",
                reality=f"Only {emp:,} employees — smaller operation than positioning suggests",
                note="Common for startups to claim 'global' based on a few international clients",
            )
        )
    return gaps


def _check_innovation_vs_stage(l1: Layer1, l2: Layer2) -> list[Gap]:
    gaps = []
    if "innovation" not in l1.claims or not l2.funding_signal:
        return gaps
    fund_lower = l2.funding_signal.lower()
    if "seed" in fund_lower or "series a" in fund_lower:
        gaps.append(
            Gap(
                category="innovation_vs_stage",
                severity="medium",
                claim="Innovative/AI-powered/disruptive positioning",
                reality=f"Still early-stage ({l2.funding_signal.split(';')[0].strip()})",
                note="Evaluate whether innovation is core product or marketing",
            )
        )
    return gaps


def _check_funding_silence(l1: Layer1, l2: Layer2) -> list[Gap]:
    gaps = []
    narrative_lower = l1.narrative.lower()
    funding_keywords = ["funding", "raised", "series", "investor", "capital", "investment"]
    mentions_funding = any(kw in narrative_lower for kw in funding_keywords)
    if l2.funding_signal and not mentions_funding:
        gaps.append(
            Gap(
                category="funding_silence",
                severity="low",
                claim="Company doesn't emphasize funding in public positioning",
                reality=f"Has raised capital: {l2.funding_signal}",
                note="Product-led narrative vs investor story",
            )
        )
    return gaps


def _check_heritage_vs_transformation(l1: Layer1, l2: Layer2) -> list[Gap]:
    gaps = []
    if not (("heritage" in l1.claims or "full-service" in l1.claims) and l2.growth_signal):
        return gaps
    growth_lower = l2.growth_signal.lower()
    if any(kw in growth_lower for kw in ["acquisition", "acquiring", "transform", "pivot", "4pl"]):
        gaps.append(
            Gap(
                category="heritage_vs_transformation",
                severity="high",
                claim="Heritage/tradition/trusted operator positioning",
                reality=f"Active transformation: {l2.growth_signal}",
                note="Classic reframing: traditional facade, platform transformation underneath",
            )
        )
    return gaps


def _check_employee_signal(l1: Layer1, l2: Layer2) -> list[Gap]:
    gaps = []
    emp = _parse_employee_count(l2.employee_signal)
    if emp is not None and "trust" in l1.claims and emp < 50:
        gaps.append(
            Gap(
                category="trust_vs_team",
                severity="medium",
                claim="Trusted/enterprise-grade/reliable positioning",
                reality=f"Team of only {emp:,} — enterprise buyers may question support capacity",
                note="Important for enterprise sales interviews",
            )
        )
    return gaps


def _check_market_positioning(l1: Layer1, l2: Layer2) -> list[Gap]:
    gaps = []
    if not (l2.market_signal and l1.positioning):
        return gaps
    pos_words = set(l1.positioning.lower().split())
    mkt_words = set(l2.market_signal.lower().split())
    overlap = pos_words & mkt_words
    stop = {"the", "a", "an", "and", "or", "for", "with", "in", "on", "to", "of", "is", "we", "our"}
    aspirational = pos_words - mkt_words - stop
    if len(aspirational) > 3 and len(overlap) < 2:
        gaps.append(
            Gap(
                category="positioning_drift",
                severity="low",
                claim="Positioning terms not reflected in market/industry data",
                reality=f"Market data: {l2.market_signal[:100]}",
                note="Aspirational positioning or incomplete market data",
            )
        )
    return gaps


# ── Semantic detectors ───────────────────────────────────────────────────────


def _check_leadership_vs_headcount(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Market leader / #1 claims vs small team."""
    gaps = []
    narrative_lower = l1.narrative.lower()
    leadership_kw = [
        "market leader", "leading", "leader in", "#1", "number one",
        "largest", "dominant", "pioneer",
    ]
    claims_leadership = "leadership" in l1.claims or any(k in narrative_lower for k in leadership_kw)
    emp = _parse_employee_count(l2.employee_signal) or l2.employee_count

    if claims_leadership and emp is not None and emp < 100:
        gaps.append(
            Gap(
                category="leadership_vs_headcount",
                severity="high",
                claim="Positions as market leader or category leader",
                reality=f"Only {emp:,} employees — scale inconsistent with leadership claim",
                note="Leadership may mean product category niche, not company size — verify definition",
            )
        )
    return gaps


def _check_global_vs_regional(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Global/worldwide claims vs single-region HQ and market."""
    gaps = []
    narrative_lower = l1.narrative.lower()
    global_kw = ["global", "worldwide", "international", "across continents", "100+ countries"]
    claims_global = "scale" in l1.claims or any(k in narrative_lower for k in global_kw)

    if not claims_global:
        return gaps

    hq = (l2.hq_location or "").lower()
    market = (l2.market_signal or "").lower()
    regions_found = _regions_in_text(f"{hq} {market} {l2.expansion_signal}")

    if len(regions_found) <= 1 and hq:
        gaps.append(
            Gap(
                category="global_vs_regional",
                severity="medium",
                claim="Global/worldwide footprint positioning",
                reality=f"HQ and market signals point to regional focus ({hq or 'single region'})",
                note="May export globally from one hub — ask for revenue/geo split not adjectives",
            )
        )
    return gaps


def _check_ai_native_vs_age(l1: Layer1, l2: Layer2) -> list[Gap]:
    """AI-native/disruptive framing vs pre-2015 founding."""
    gaps = []
    narrative_lower = l1.narrative.lower()
    ai_kw = [
        "ai-native", "ai powered", "ai-powered", "artificial intelligence",
        "machine learning", "disrupt", "next-gen", "next generation",
    ]
    claims_ai = "innovation" in l1.claims or any(k in narrative_lower for k in ai_kw)
    founded = l2.founded_year

    if claims_ai and founded is not None and founded < 2015:
        gaps.append(
            Gap(
                category="ai_native_vs_legacy",
                severity="medium",
                claim="AI-native / disruptive / next-generation positioning",
                reality=f"Founded {founded} — legacy operator rebranding around AI, not greenfield AI startup",
                note="Distinguish AI wrapper on legacy process vs genuine model-native product",
            )
        )
    return gaps


def _check_trust_at_scale(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Fortune 500 / enterprise trust claims with startup-scale funding."""
    gaps = []
    if "trust" not in l1.claims:
        return gaps
    if l2.funding_signal and any(
        x in l2.funding_signal.lower() for x in ("seed", "series a", "series b")
    ):
        emp = _parse_employee_count(l2.employee_signal) or l2.employee_count
        if emp is not None and emp < 500:
            gaps.append(
                Gap(
                    category="enterprise_claim_startup_reality",
                    severity="medium",
                    claim="Enterprise-grade / Fortune 500 / trusted partner positioning",
                    reality=f"Startup-scale: {l2.funding_signal}; ~{emp:,} employees",
                    note="Land-and-expand narrative — credibility gap is the interview angle",
                )
            )
    return gaps


def _check_zero_narrative_rich_data(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Silent on positioning but data tells a story."""
    gaps = []
    empty_l1 = (
        not l1.narrative
        or l1.narrative == "No public self-description available."
    )
    if empty_l1 and l2.data_quality in ("moderate", "rich"):
        gaps.append(
            Gap(
                category="silent_positioning",
                severity="low",
                claim="Minimal public narrative — company lets data/funding speak",
                reality=f"Observable signals without messaging: {l2.summary[:150]}",
                note="Interview angle: why aren't they telling this story publicly?",
            )
        )
    return gaps


# ── LLM gap pass ─────────────────────────────────────────────────────────────


def _detect_gaps_llm(
    layer1: Layer1,
    layer2: Layer2,
    edge: Optional["EdgeCaseContext"],
    client,
) -> list[dict]:
    from .prompts import GAP_SYSTEM, gap_user_prompt

    payload = client.complete_json(
        GAP_SYSTEM,
        gap_user_prompt(
            company_name=layer2.company_name or "Unknown",
            layer1_narrative=layer1.narrative,
            layer1_claims=layer1.claims,
            layer2_summary=layer2.summary,
            layer2_signals=layer2.to_signals_dict(),
            edge_context=edge.summary if edge else "",
        ),
    )
    if not payload:
        return []
    return payload.get("gaps") or []


# ── Helpers ────────────────────────────────────────────────────────────────────


def _parse_employee_count(text: str) -> Optional[int]:
    if not text:
        return None
    m = re.search(r"([\d,]+)", text.replace(",", ""))
    if m:
        try:
            return int(m.group(1).replace(",", ""))
        except ValueError:
            pass
    return None


_REGION_KEYWORDS = {
    "europe": ["germany", "europe", "eu", "uk", "france", "netherlands", "cologne", "berlin"],
    "north_america": ["usa", "united states", "north america", "new york", "san francisco"],
    "asia": ["asia", "china", "singapore", "japan", "india"],
}


def _regions_in_text(text: str) -> set[str]:
    text = text.lower()
    found = set()
    for region, kws in _REGION_KEYWORDS.items():
        if any(kw in text for kw in kws):
            found.add(region)
    return found
