"""All gap detector functions: heuristic, semantic, structural, v2, v3, v4."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .models import Gap
from .helpers import (
    _parse_employee_count,
    _parse_revenue_number,
    _parse_funding_number,
    _regions_in_text,
)
from ..layers import Layer1, Layer2

if TYPE_CHECKING:
    from ..edge_cases import EdgeCaseContext


# ── Edge-case gaps ───────────────────────────────────────────────────────────


def _edge_case_gaps(l1: Layer1, l2: Layer2, edge: EdgeCaseContext) -> list[Gap]:
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
            for kw in [
                "up",
                "growing",
                "expansion",
                "doubling",
                "increase",
                "acquisition",
            ]
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
    stage = l2.funding_signal.split(";")[0].strip()
    if "seed" in fund_lower or "series a" in fund_lower:
        gaps.append(
            Gap(
                category="innovation_vs_stage",
                severity="medium",
                claim="Innovative/AI-powered/disruptive positioning",
                reality=f"Still early-stage ({stage})",
                note="Evaluate whether innovation is core product or marketing",
            )
        )
    elif "series b" in fund_lower:
        emp = _parse_employee_count(l2.employee_signal) or l2.employee_count
        if emp is not None and emp < 300:
            gaps.append(
                Gap(
                    category="innovation_vs_stage",
                    severity="low",
                    claim="Innovative/AI-powered/disruptive positioning",
                    reality=f"Growing Series B company ({stage}) with ~{emp:,} people — still in scale-up, not at category-defining stage yet",
                    note="Reframe: innovation claim is plausible but untested at scale — ask about unit economics, not vision",
                )
            )
    return gaps


def _check_funding_silence(l1: Layer1, l2: Layer2) -> list[Gap]:
    gaps = []
    narrative_lower = l1.narrative.lower()
    funding_keywords = [
        "funding",
        "raised",
        "series",
        "investor",
        "capital",
        "investment",
    ]
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
    if not (
        ("heritage" in l1.claims or "full-service" in l1.claims) and l2.growth_signal
    ):
        return gaps
    growth_lower = l2.growth_signal.lower()
    if any(
        kw in growth_lower
        for kw in ["acquisition", "acquiring", "transform", "pivot", "4pl"]
    ):
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
    stop = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "for",
        "with",
        "in",
        "on",
        "to",
        "of",
        "is",
        "we",
        "our",
    }
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
        "market leader",
        "leading",
        "leader in",
        "#1",
        "number one",
        "largest",
        "dominant",
        "pioneer",
    ]
    claims_leadership = "leadership" in l1.claims or any(
        k in narrative_lower for k in leadership_kw
    )
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
    global_kw = [
        "global",
        "worldwide",
        "international",
        "across continents",
        "100+ countries",
    ]
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
        "ai-native",
        "ai powered",
        "ai-powered",
        "artificial intelligence",
        "machine learning",
        "disrupt",
        "next-gen",
        "next generation",
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
        not l1.narrative or l1.narrative == "No public self-description available."
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


def _check_narrative_staleness(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Novelty/disruption language on an established operator."""
    gaps = []
    narrative_lower = l1.narrative.lower()
    novelty_kw = [
        "next-gen",
        "next generation",
        "groundbreaking",
        "revolutionary",
        "cutting-edge",
        "cutting edge",
        "disrupt",
        "paradigm shift",
    ]
    claims_novelty = any(k in narrative_lower for k in novelty_kw)
    founded = l2.founded_year
    if not claims_novelty or founded is None:
        return gaps

    if founded < 2020 and l2.data_quality in ("moderate", "rich"):
        years_ago = datetime.now().year - founded
        gaps.append(
            Gap(
                category="narrative_staleness",
                severity="medium",
                claim="Novelty/disruption/groundbreaking positioning language",
                reality=f"Founded {founded} ({years_ago} years ago) — established operator still using early-stage framing",
                note="Reframe: ask what's genuinely new vs same process with new labels. Distinguish company age from product age.",
            )
        )
    # Even stronger: pre-2015 with disruption language
    if founded < 2015:
        gaps.append(
            Gap(
                category="legacy_disruption_paradox",
                severity="high",
                claim="Disruption / paradigm shift / revolutionary framing",
                reality=f"Operating since {founded} — a decade-old business using insurgent language",
                note="Classic 'innovator's dilemma in reverse': ask whether fear of being seen as legacy drives the narrative, not actual innovation",
            )
        )
    return gaps


def _check_enterprise_vs_team(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Claims enterprise / Fortune 500 / large deployment capability but small team."""
    gaps = []
    narrative_lower = l1.narrative.lower()
    enterprise_kw = [
        "enterprise",
        "enterprise-grade",
        "enterprise class",
        "fortune 500",
        "large-scale",
        "large scale",
        "global deployment",
        "mission-critical",
        "mission critical",
        "multinational",
    ]
    claims_enterprise = any(k in narrative_lower for k in enterprise_kw)
    if not claims_enterprise:
        return gaps

    emp = _parse_employee_count(l2.employee_signal) or l2.employee_count
    if emp is not None and emp < 200:
        gaps.append(
            Gap(
                category="enterprise_vs_team",
                severity="high",
                claim="Enterprise / Fortune 500 / mission-critical positioning",
                reality=f"Team of ~{emp:,} — capacity to support enterprise deployments at scale is unproven",
                note="Key interview angle: ask about support model, SLAs, and largest deployment — not just sales pipeline",
            )
        )
    elif emp is not None and emp < 500:
        gaps.append(
            Gap(
                category="enterprise_vs_team",
                severity="low",
                claim="Enterprise-grade positioning",
                reality=f"Team of ~{emp:,} — midsize operation building toward enterprise credibility",
                note="Watch for: professional services vs product-led growth ratio",
            )
        )
    return gaps


def _check_horizontal_claim_vs_hub_reality(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Claims 'platform / full-stack / multi-product' but single-use-case data."""
    gaps = []
    narrative_lower = l1.narrative.lower()
    platform_kw = [
        "platform",
        "full-stack",
        "full stack",
        "end-to-end",
        "end to end",
        "one-stop",
        "one stop",
        "comprehensive suite",
        "ecosystem",
    ]
    claims_platform = any(k in narrative_lower for k in platform_kw)
    if not claims_platform:
        return gaps

    market = (l2.market_signal or "").lower()
    expansion = (l2.expansion_signal or "").lower()
    combined = f"{market} {expansion} {l2.summary.lower()}"

    narrow_signal = False
    for kw in ["single", "one category", "niche", "specific use case", "only"]:
        if kw in combined:
            narrow_signal = True
            break
    if not narrow_signal and len(combined.split()) < 20:
        narrow_signal = True  # too little info to confirm broad platform

    if narrow_signal:
        gaps.append(
            Gap(
                category="platform_claim_narrow_reality",
                severity="medium",
                claim="Platform / full-stack / ecosystem positioning",
                reality="Available data suggests focused use case, not broad platform play",
                note="Ask: 'What percentage of revenue is still the original product?' — platform bundling vs genuine suite",
            )
        )
    return gaps


def _check_product_category_gap(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Claimed sector/industry positioning doesn't match what data suggests."""
    gaps = []
    positioning = l1.positioning or ""
    sector = l2.sector or ""
    description = l2.description or ""

    if not positioning or not sector:
        return gaps

    pos_lower = positioning.lower()
    sec_lower = sector.lower()

    # If company says "AI" / "tech" but sector is non-tech
    tech_claims = [
        "ai",
        "artificial intelligence",
        "machine learning",
        "saas",
        "software",
        "platform",
    ]
    non_tech_sectors = [
        "consulting",
        "services",
        "manufacturing",
        "logistics",
        "retail",
        "construction",
        "real estate",
    ]

    claims_tech = any(k in pos_lower for k in tech_claims)
    is_non_tech = any(k in sec_lower for k in non_tech_sectors)

    if claims_tech and is_non_tech:
        gaps.append(
            Gap(
                category="product_category_gap",
                severity="high",
                claim=f"AI/tech sector positioning: '{l1.positioning[:80]}'",
                reality=f"Data shows {sector} — technology may be a wrapper on traditional services",
                note="Critical reframe: ask about R&D spend vs services revenue — tech-label vs tech-business",
            )
        )
        return gaps

    # If company says "digital/e-commerce" but data suggests traditional
    digital_claims = [
        "digital",
        "e-commerce",
        "ecommerce",
        "online",
        "d2c",
        "direct-to-consumer",
    ]
    claims_digital = any(k in pos_lower for k in digital_claims)
    if claims_digital and is_non_tech:
        gaps.append(
            Gap(
                category="product_category_gap",
                severity="medium",
                claim=f"Digital-forward positioning: '{l1.positioning[:80]}'",
                reality=f"Data suggests {sector} — digital transformation of traditional business, not digital-native",
                note="Ask: revenue split between digital and traditional channels",
            )
        )
    return gaps


# ── v2 gap detectors ─────────────────────────────────────────────────────────


def _check_revenue_shrinkage(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Company claims growth/demand but revenue data suggests decline or flat."""
    gaps = []
    narrative_lower = l1.narrative.lower()
    growth_kw = [
        "growing",
        "expanding",
        "increasing demand",
        "scaling",
        "upward",
        "accelerating",
    ]
    claims_growth = any(k in narrative_lower for k in growth_kw)

    if not claims_growth or not l2.revenue_signal:
        return gaps

    rev_lower = l2.revenue_signal.lower()
    decline_signals = [
        "decline",
        "down",
        "decreased",
        "fell",
        "drop",
        "reduced",
        "shrank",
        "contraction",
        "negative growth",
        "slowing",
    ]
    if any(k in rev_lower for k in decline_signals):
        gaps.append(
            Gap(
                category="revenue_shrinkage",
                severity="high",
                claim="Growing/expanding/increasing demand positioning",
                reality=f"Revenue data suggests decline or contraction: {l2.revenue_signal[:120]}",
                note="Critical gap: growth narrative actively contradicted by revenue trajectory",
            )
        )
    return gaps


def _check_full_service_vs_niche(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Claims 'full-service' / 'end-to-end' but market data shows narrow niche."""
    gaps = []
    narrative_lower = l1.narrative.lower()
    full_service_kw = ["full-service", "full service", "all-in-one", "one-stop"]
    claims_full_service = any(k in narrative_lower for k in full_service_kw)
    if not claims_full_service:
        return gaps

    market_lower = (l2.market_signal or "").lower()
    niche_kw = ["niche", "specific", "segment", "specialized", "focused", "single"]
    is_niche = any(k in market_lower for k in niche_kw)
    narrow_market = len(market_lower.split()) < 10 if market_lower else True

    if is_niche or narrow_market:
        gaps.append(
            Gap(
                category="full_service_vs_niche",
                severity="medium",
                claim="Full-service / all-in-one / one-stop positioning",
                reality=f"Market data suggests focused niche: {l2.market_signal[:100] or 'limited market description'}",
                note="Full-service claim may mean covering one client's needs broadly, not serving an entire ecosystem",
            )
        )
    return gaps


def _check_market_share_gap(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Named competitors are industry giants but company scale is a fraction."""
    gaps = []
    if not l2.market_signal:
        return gaps

    market_lower = l2.market_signal.lower()
    giant_signals = [
        "dhl",
        "fedex",
        "ups",
        "amazon",
        "google",
        "microsoft",
        "apple",
        "sap",
        "oracle",
        "salesforce",
        "adobe",
        "kuehne+nagel",
        "db schenker",
        "dsv",
    ]
    mentions_giants = any(g in market_lower for g in giant_signals)
    if not mentions_giants:
        return gaps

    emp = _parse_employee_count(l2.employee_signal) or l2.employee_count
    if emp is not None and emp < 5000:
        gaps.append(
            Gap(
                category="market_share_gap",
                severity="medium",
                claim="Named alongside industry giants in competitive positioning",
                reality=f"~{emp:,} employees vs market leaders with hundreds of thousands — 'competing with' may mean 'adjacent to'",
                note="Ask: 'Who is your actual closest competitor by revenue/segment, not ambition?'",
            )
        )
    return gaps


def _check_local_champion_facade(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Claims multi-region/international presence but single-country data."""
    gaps = []
    narrative_lower = l1.narrative.lower()
    multi_region_kw = [
        "across europe",
        "international",
        "multi-country",
        "multi-country",
        "european",
        "across",
        "in all major",
        "in multiple",
    ]
    claims_multi = any(k in narrative_lower for k in multi_region_kw)
    if not claims_multi:
        return gaps

    hq = (l2.hq_location or "").lower()
    if not hq:
        return gaps

    country_names = {
        "germany",
        "france",
        "uk",
        "usa",
        "austria",
        "switzerland",
        "netherlands",
        "belgium",
        "spain",
        "italy",
        "poland",
    }
    hq_country = next((c for c in country_names if c in hq), None)
    if not hq_country:
        return gaps

    market_lower = (l2.market_signal or "").lower()
    expansion_lower = (l2.expansion_signal or "").lower()
    combined = f"{market_lower} {expansion_lower}"

    other_countries = [c for c in country_names if c != hq_country]
    mentions_other = any(c in combined for c in other_countries)

    if not mentions_other:
        gaps.append(
            Gap(
                category="local_champion_facade",
                severity="medium",
                claim="International / multi-region positioning",
                reality=f"HQ in {hq_country.title()} — data shows no confirmed geographic expansion beyond home market",
                note="Ask for revenue by geography, not office count. Many 'international' companies derive 80%+ from home market.",
            )
        )
    return gaps


def _check_age_vs_transformation_velocity(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Old company (>20 years) claims innovation/transformation but no clear transformation signals."""
    gaps = []
    founded = l2.founded_year
    current_year = datetime.now().year
    if founded is None or (current_year - founded) < 20:
        return gaps

    narrative_lower = l1.narrative.lower()
    transformation_kw = [
        "transform",
        "digital",
        "next-generation",
        "next gen",
        "moderniz",
        "reinvent",
        "revolutioniz",
    ]
    claims_transformation = any(k in narrative_lower for k in transformation_kw)
    if not claims_transformation:
        return gaps

    growth_lower = (l2.growth_signal or "").lower()
    has_transformation_signals = any(
        k in growth_lower
        for k in [
            "acquisition",
            "digital",
            "platform",
            "new product",
            "innovation lab",
            "partnership",
            "venture",
            "spin-off",
        ]
    )
    expansion = (l2.expansion_signal or "").lower()
    has_expansion_signals = any(
        k in expansion
        for k in ["digital", "platform", "automation", "ai", "saas", "software"]
    )

    if not has_transformation_signals and not has_expansion_signals:
        age = current_year - founded
        gaps.append(
            Gap(
                category="age_vs_transformation_velocity",
                severity="high",
                claim="Digital / next-generation / modernization positioning",
                reality=f"{age}-year-old company with no confirmed digital/transformation signals in growth data",
                note="Pillar-to-post vs genuine pivot: ask about % revenue from new vs legacy, not marketing language",
            )
        )
    return gaps


def _check_competitor_adjacency_gap(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Company namedrops giant competitors but funding/scale suggests startup niche."""
    gaps = []
    if not l2.funding_signal:
        return gaps

    competitors = (l2.market_signal or "").lower()
    giant_signals = [
        "microsoft",
        "google",
        "amazon",
        "apple",
        "oracle",
        "sap",
        "salesforce",
        "workday",
        "servicenow",
        "adobe",
        "ibm",
    ]
    mentions_giants = any(g in competitors for g in giant_signals)
    if not mentions_giants:
        return gaps

    fund_lower = l2.funding_signal.lower()
    early_stage = any(
        k in fund_lower for k in ["seed", "series a", "series b", "series c"]
    )
    if not early_stage:
        return gaps

    emp = _parse_employee_count(l2.employee_signal) or l2.employee_count
    if emp is None or emp >= 500:
        return gaps

    gaps.append(
        Gap(
            category="competitor_adjacency_gap",
            severity="high",
            claim="Named alongside Big Tech/enterprise giants in competitor list",
            reality=f"Startup-stage funding ({l2.funding_signal[:80]}) with ~{emp:,} employees — 'competitor' likely means adjacent, not direct",
            note="Classic reframe: ask 'What percentage of their market cap comes from your specific niche?' to expose adjacency vs competition",
        )
    )
    return gaps


# ── v3 quantified detectors ──────────────────────────────────────────────────


def _check_revenue_per_employee(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Quantified productivity metric. Flags when positioning (AI/SaaS/platform)
    doesn't match implied revenue-per-employee margins."""
    gaps = []
    emp = _parse_employee_count(l2.employee_signal) or l2.employee_count
    if not emp or emp < 5:
        return gaps

    rev_num = _parse_revenue_number(l2.revenue_signal)
    if rev_num is None:
        return gaps

    rev_per_emp = rev_num / emp
    narrative_lower = l1.narrative.lower()

    claims_product_model = any(
        k in narrative_lower
        for k in [
            "platform",
            "saas",
            "software",
            "ai-native",
            "ai-powered",
            "subscription",
        ]
    )
    claims_efficiency = any(
        k in narrative_lower for k in ["capital efficient", "profitable", "high-margin"]
    )

    if claims_product_model and rev_per_emp < 150000:
        gaps.append(
            Gap(
                category="revenue_per_employee_gap",
                severity="medium",
                claim="Platform/SaaS/AI product positioning — implying high-margin scalable model",
                reality=f"~${rev_per_emp:,.0f}/employee revenue — consistent with services margins, not product software",
                note="Ask: 'What % of revenue is professional services vs product?'. Low rev/emp is often a tell for services-heavy business model disguised as product.",
            )
        )
    elif claims_efficiency and rev_per_emp < 150000:
        gaps.append(
            Gap(
                category="revenue_per_employee_gap",
                severity="medium",
                claim=f"Capital-efficient / high-margin positioning",
                reality=f"~${rev_per_emp:,.0f}/employee revenue — low-end margins for their claim profile",
                note="Ask about actual margin structure: low revenue-per-head often means thin services margins",
            )
        )

    if rev_per_emp > 800000 and emp < 200:
        gaps.append(
            Gap(
                category="revenue_per_employee_gap",
                severity="low",
                claim="Product/SaaS revenue model implied",
                reality=f"~${rev_per_emp:,.0f}/employee at {emp:,} people — could be high-value consulting disguised as product, or genuine product leverage",
                note="Verify: high revenue-per-head in small teams often signals high-ticket services, broad platform, or exceptional product leverage. Ask about revenue composition.",
            )
        )

    return gaps


def _check_claim_consistency(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Detect contradictory claims within the same public narrative."""
    gaps = []
    claims = set(l1.claims)
    narrative_lower = l1.narrative.lower()

    # Claim-set contradictions (heritage vs innovation, etc.)
    contradictions = [
        ({"heritage"}, {"innovation"}, "heritage_vs_innovation_paradox", "high",
         "Heritage/traditional operator claiming next-generation innovation",
         "Heritage and innovation positioning detected simultaneously — suggests rebrand of legacy operation, not greenfield innovation",
         "Classic reframe: ask for R&D investment as % of revenue vs industry average. Heritage marketing and product innovation rarely coexist at the speed claimed."),
        ({"heritage"}, {"growth"}, "heritage_vs_startup_language", "medium",
         "Established operator using startup-style 'fast-growing' language",
         "Heritage/established positioning alongside 'fast-growing'/'scaling' claims — maturity framing mismatch",
         "Ask: 'What's growing — revenue from new products or legacy operations?' Fast-growing established companies are usually transforming, not accelerating core."),
        ({"heritage"}, {"scale"}, "heritage_vs_scale_overlap", "low",
         "Heritage operator claiming global scale",
         "Heritage and scale claims both present — internally consistent but may hide transformation needs",
         "Heritage + scale is common for incumbents. The question is transformation velocity, not positioning truth."),
        ({"innovation"}, {"trust"}, "innovation_vs_trust_paradox", "medium",
         "Bold innovation/disruption claims alongside trust/reliability positioning",
         "Disruption language and enterprise trust language used simultaneously — two different buyer personas targeted with one narrative",
         "Ask: 'Which buyer does your innovation serve — the risk-taker or the risk-averse?' This tension often reveals a muddled go-to-market."),
        ({"scale"}, {"innovation"}, "scale_vs_nimble_innovation", "low",
         "Global scale claim alongside innovation/disruption framing",
         "Scale and innovation claims together — possible but rare",
         "Innovators at scale (Apple, Amazon) are exceptions, not the rule. Ask whether innovation spend is percentage-significant or absolute-small."),
    ]

    for left_set, right_set, cat, severity, claim, reality, note in contradictions:
        if claims & left_set and claims & right_set:
            gaps.append(Gap(category=cat, severity=severity, claim=claim, reality=reality, note=note))

    # Narrative-keyword contradiction (local vs global — detected from narrative, not claims)
    local_kw = ["local", "regional", "home market", "domestic"]
    global_kw = ["global", "worldwide", "international", "across"]
    if any(k in narrative_lower for k in local_kw) and any(k in narrative_lower for k in global_kw):
        gaps.append(
            Gap(
                category="local_vs_global_narrative",
                severity="medium",
                claim="Claims both local/specialist and global/international positioning",
                reality="Local and global framing detected in the same narrative — inconsistent market positioning",
                note="Ask: 'Describe your primary market — is it regional depth or global breadth?' Simultaneous local+global claims often mean neither is true.",
            )
        )

    return gaps


def _check_funding_efficiency(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Capital intensity ratio: total funding / employee count."""
    gaps = []
    emp = _parse_employee_count(l2.employee_signal) or l2.employee_count
    if not emp or emp < 5:
        return gaps

    funding_num = _parse_funding_number(l2.funding_signal)
    if funding_num is None:
        return gaps

    funding_per_emp = funding_num / emp
    narrative_lower = l1.narrative.lower()
    claims_efficiency = any(
        k in narrative_lower
        for k in [
            "capital efficient",
            "capital-efficient",
            "profitable",
            "bootstrapped",
            "lean",
            "high-margin",
            "self-funded",
        ]
    )
    claims_scale = "scale" in l1.claims

    if funding_per_emp > 500000 and (claims_efficiency or claims_scale):
        gaps.append(
            Gap(
                category="funding_efficiency_gap",
                severity="high",
                claim=f"{'Capital-efficient' if claims_efficiency else 'Scale'} positioning",
                reality=f"~${funding_per_emp:,.0f} raised per employee — very high capital intensity for their claim profile",
                note="Reframe: high capital-per-head often reveals a capital-intensive business model (hardware, services, R&D-heavy) masked by efficiency narrative. Ask about unit economics and burn multiple.",
            )
        )
    elif funding_per_emp >= 300000:
        gaps.append(
            Gap(
                category="funding_efficiency_gap",
                severity="low",
                claim="Funding signals well-capitalized operation",
                reality=f"~${funding_per_emp:,.0f} raised per employee — moderate-to-high capital intensity",
                note="Ask about burn rate and path to profitability. High capital-per-head without revenue is a different conversation than capital efficiency.",
            )
        )
    elif funding_per_emp < 50000 and not l2.revenue_signal and "growth" in l1.claims:
        gaps.append(
            Gap(
                category="funding_efficiency_gap",
                severity="medium",
                claim="Growth/fast-growing positioning",
                reality=f"~${funding_per_emp:,.0f} raised per employee — low capital for growth-stage company with no confirmed revenue",
                note="Potential under-capitalization risk. Ask about runway and whether growth is organic or will require near-term fundraising that dilutes or changes strategy.",
            )
        )

    return gaps


# ── v4 detectors ─────────────────────────────────────────────────────────────


def _check_esg_sustainability_gap(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Green/sustainable/net-zero claims in high-emission sectors without
    confirmed transformation programs."""
    gaps = []
    if "sustainability" not in l1.claims:
        return gaps

    high_emission_sectors = {
        "logistics", "manufacturing", "energy", "chemicals",
        "aviation", "shipping", "construction", "automotive",
        "mining", "agriculture", "oil", "gas", "industrial",
        "transportation", "freight", "airlines",
    }
    sector_lower = (l2.sector or "").lower()
    description_lower = (l2.description or "").lower()
    combined = f"{sector_lower} {description_lower}"

    is_high_emission = any(s in combined for s in high_emission_sectors)
    if not is_high_emission:
        return gaps

    growth_lower = (l2.growth_signal or "").lower()
    expansion_lower = (l2.expansion_signal or "").lower()
    combined_growth = f"{growth_lower} {expansion_lower}"

    transformation_kw = [
        "electric", "renewable", "solar", "wind", "carbon offset",
        "sustainable fuel", "emission", "emissions", "green logistics",
        "circular economy", "net zero program", "decarbon",
        "co2 reduction", "carbon neutral program",
        "sustainability program", "sustainability initiative",
        "carbon reduction", "emission reduction",
    ]
    has_transformation = any(k in combined_growth for k in transformation_kw)

    if not has_transformation:
        gaps.append(
            Gap(
                category="esg_sustainability_gap",
                severity="high",
                claim="Environmental / sustainability / green / net-zero positioning",
                reality=(
                    f"Company operates in {l2.sector or 'a high-emission sector'} "
                    "but no confirmed sustainability or emissions-reduction programs found"
                ),
                note=(
                    "Ask: 'What specific sustainability metrics do you track? "
                    "How is your carbon intensity trending vs industry average?' "
                    "Green claims without green operations is a growing scrutiny risk"
                ),
            )
        )
    else:
        gaps.append(
            Gap(
                category="esg_sustainability_gap",
                severity="low",
                claim="Sustainability / green positioning",
                reality=(
                    f"Sector is {l2.sector or 'high-emission'} — transformation signals detected: "
                    f"{combined_growth[:120]}"
                ),
                note=(
                    "Ask: 'What % of revenue comes from green products vs the legacy business?' "
                    "Transformation signals exist — verify depth vs marketing spend"
                ),
            )
        )

    return gaps


def _check_customer_concentration_gap(l1: Layer1, l2: Layer2) -> list[Gap]:
    """'Thousands of customers' / mass adoption claim but rev/emp
    suggests enterprise-whale model with few large clients."""
    gaps = []
    narrative_lower = l1.narrative.lower()

    mass_kw = [
        "thousands of", "millions of", "used by", "1000+", "10000+",
        "100,000+", "over 1000", "companies trust",
        "adopted by", "customers worldwide", "trusted by",
    ]
    claims_mass = any(k in narrative_lower for k in mass_kw)
    if not claims_mass:
        return gaps

    emp = _parse_employee_count(l2.employee_signal) or l2.employee_count
    if not emp or emp < 10:
        return gaps

    rev_num = _parse_revenue_number(l2.revenue_signal)
    if rev_num is None:
        return gaps

    rev_per_emp = rev_num / emp

    if rev_per_emp > 500000:
        gaps.append(
            Gap(
                category="customer_concentration_gap",
                severity="medium",
                claim="Mass adoption / thousands of customers positioning",
                reality=(
                    f"~${rev_per_emp:,.0f}/employee revenue — "
                    "consistent with enterprise-whale model (a few large customers), "
                    "not broad market adoption"
                ),
                note=(
                    "Ask: 'How many paying customers do you have, and what's your net dollar retention?' "
                    "High rev/emp + mass-adoption claim = handful of whales, not mass market"
                ),
            )
        )
    elif rev_per_emp > 250000:
        gaps.append(
            Gap(
                category="customer_concentration_gap",
                severity="low",
                claim="Broad customer base positioning",
                reality=(
                    f"~${rev_per_emp:,.0f}/employee revenue — "
                    "some concentration risk despite broad adoption language"
                ),
                note=(
                    "Ask about customer count and revenue concentration. "
                    "Mid-range rev/emp can mean growing base or a few large + many small."
                ),
            )
        )

    return gaps


def _check_moat_delusion(l1: Layer1, l2: Layer2) -> list[Gap]:
    """'Network effects / data moat / flywheel' claims but
    business signals suggest transactional or services model."""
    gaps = []
    if "moat_claim" not in l1.claims:
        return gaps

    sector_lower = (l2.sector or "").lower()
    market_lower = (l2.market_signal or "").lower()
    description_lower = (l2.description or "").lower()
    combined = f"{sector_lower} {market_lower} {description_lower}"

    transactional_signals = [
        "consulting", "freight", "logistics", "contract",
        "outsourcing", "staffing", "recruitment", "project-based",
        "professional services", "managed services", "broker",
        "agency", "reseller", "distributor",
    ]
    is_transactional = any(s in combined for s in transactional_signals)

    if not is_transactional:
        commodity_kw = ["many competitors", "fragmented", "crowded", "numerous"]
        is_commodity = any(k in market_lower for k in commodity_kw)
        if not is_commodity:
            return gaps

    emp = _parse_employee_count(l2.employee_signal) or l2.employee_count
    emp_note = ""
    if emp is not None and emp < 500:
        emp_note = f" Team of {emp:,} — network effects typically require scale."

    rev_num = _parse_revenue_number(l2.revenue_signal)
    rev_note = ""
    if rev_num is not None and emp is not None and emp > 0:
        rpe = rev_num / emp
        if rpe < 150000:
            rev_note = f" ${rpe:,.0f}/emp suggests services margins, not a platform moat."

    gaps.append(
        Gap(
            category="moat_delusion",
            severity="medium",
            claim="Platform moat / network effects / ecosystem lock-in / flywheel positioning",
            reality=(
                f"Business signals point to {l2.sector or 'transactional'} model — "
                f"moat claims appear aspirational"
                f"{emp_note}{rev_note}"
            ),
            note=(
                "Ask: 'What prevents a customer from switching to a competitor? "
                "Is the moat technical (IP/data), relational (multi-year contracts), "
                "or network-driven (cross-side)?' Most 'network effects' claims are actually "
                "just high switching costs."
            ),
        )
    )

    return gaps


def _check_regulatory_posture_gap(l1: Layer1, l2: Layer2) -> list[Gap]:
    """Compliance/security posture vs sector regulation reality."""
    gaps = []
    narrative_lower = l1.narrative.lower()

    compliance_kw = [
        "fully compliant", "compliant with", "gdpr", "sox", "hipaa",
        "iso 27001", "soc 2", "soc2", "bank-grade", "bank grade",
        "regulated", "audited", "enterprise security",
        "certified", "certification", "regulatory",
    ]
    claims_compliance = any(k in narrative_lower for k in compliance_kw)

    regulated_sectors = {
        "fintech", "finance", "banking", "insurance", "healthcare",
        "pharma", "medical", "legal", "defense", "aerospace",
        "payments", "credit", "lending",
    }
    sector_lower = (l2.sector or "").lower()
    description_lower = (l2.description or "").lower()
    combined = f"{sector_lower} {description_lower}"
    is_regulated = any(s in combined for s in regulated_sectors)

    if claims_compliance and not is_regulated:
        gaps.append(
            Gap(
                category="regulatory_posture_gap",
                severity="low",
                claim="Heavy compliance / security / certification positioning",
                reality=(
                    f"Company operates in {l2.sector or 'non-regulated'} sector — "
                    "compliance emphasis may exceed what the market requires"
                ),
                note=(
                    "Ask: 'Which specific regulations drive your compliance posture? "
                    "Are you selling to regulated buyers who require these certs?' "
                    "Over-indexing on compliance can mean security-theater over product substance."
                ),
            )
        )
    elif not claims_compliance and is_regulated:
        gaps.append(
            Gap(
                category="regulatory_posture_gap",
                severity="high",
                claim="No compliance / regulatory positioning in public narrative",
                reality=(
                    f"Operating in {l2.sector or 'regulated sector'} "
                    "without public compliance messaging — potential regulatory blind spot"
                ),
                note=(
                    "Ask: 'How do you handle regulatory compliance in your sector?' "
                    "Silence on compliance in a regulated sector is a red flag — "
                    "it often means the team hasn't faced regulatory scrutiny yet."
                ),
            )
        )

    return gaps


def _check_market_timing_gap(l1: Layer1, l2: Layer2) -> list[Gap]:
    """'First mover / category creator / pioneer' claims vs actual founding year."""
    gaps = []
    if "uniqueness" not in l1.claims:
        return gaps

    founded = l2.founded_year
    if founded is None:
        return gaps

    narrative_lower = l1.narrative.lower()
    current_year = datetime.now().year
    age = current_year - founded

    first_mover_kw = [
        "first mover", "first-of-its-kind", "first of its kind",
        "category creator", "pioneer in", "pioneering",
        "first company", "created the category",
        "invented", "founded the",
    ]
    claims_first = any(k in narrative_lower for k in first_mover_kw)

    if not claims_first:
        return gaps

    if age > 15:
        gaps.append(
            Gap(
                category="market_timing_gap",
                severity="high",
                claim="First mover / category creator / pioneer positioning",
                reality=(
                    f"Founded {founded} ({age} years ago) — "
                    "first-mover status, if ever earned, has been overtaken by market evolution"
                ),
                note=(
                    "Reframe: 'Ask what your market share is today, not who was first.' "
                    "First-mover advantage erodes — the question is whether they maintained it "
                    "or were leapfrogged."
                ),
            )
        )
    elif age < 3:
        gaps.append(
            Gap(
                category="market_timing_gap",
                severity="medium",
                claim="First mover / category creator / pioneer positioning",
                reality=(
                    f"Founded only {age} years ago ({founded}) — "
                    "too early to claim category creation in an established market"
                ),
                note=(
                    "Ask: 'Who were the players in this space before you?' "
                    "'First mover' for a young company usually means 'first with our angle,' "
                    "not genuinely first to market."
                ),
            )
        )

    return gaps


def _check_complexity_denial_gap(l1: Layer1, l2: Layer2) -> list[Gap]:
    """'Simple / easy / frictionless' claims but signals point
    to enterprise complexity."""
    gaps = []
    if "simplicity" not in l1.claims:
        return gaps

    sector_lower = (l2.sector or "").lower()
    description_lower = (l2.description or "").lower()
    combined = f"{sector_lower} {description_lower}"

    complex_sectors = {
        "enterprise software", "erp", "crm", "hr", "payroll",
        "compliance", "legal", "healthcare", "infrastructure",
        "hris", "bpm", "process mining",
    }
    is_complex_sector = any(s in combined for s in complex_sectors)

    enterprise_kw = [
        "enterprise", "fortune 500", "implementation",
        "deployment", "integration", "customization",
        "professional services", "implementation partner",
    ]
    has_enterprise_signals = any(k in combined for k in enterprise_kw)

    emp = _parse_employee_count(l2.employee_signal) or l2.employee_count
    large_team = emp is not None and emp > 500

    if is_complex_sector or has_enterprise_signals or large_team:
        parts = []
        if is_complex_sector:
            parts.append(f"sector is {l2.sector}")
        if has_enterprise_signals:
            parts.append("enterprise language in description")
        if large_team:
            parts.append(f"{emp:,} employees — enterprise scale")

        gaps.append(
            Gap(
                category="complexity_denial_gap",
                severity="medium",
                claim="Simple / easy-to-use / no-code / frictionless positioning",
                reality=(
                    f"Complexity signals detected: {', '.join(parts)} — "
                    "simplicity claim may reflect UX aspiration, not product reality"
                ),
                note=(
                    "Ask: 'What's your average implementation timeline and time-to-value?' "
                    "'Simple' positioning + enterprise sales cycle = the tension to explore "
                    "in an interview. Simplicity is relative — easy for whom?"
                ),
            )
        )

    return gaps
