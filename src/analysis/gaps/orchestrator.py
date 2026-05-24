"""Main gap detection orchestrator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models import GapReport
from .detectors import (
    _check_growth_mismatch,
    _check_scale_claims,
    _check_innovation_vs_stage,
    _check_funding_silence,
    _check_heritage_vs_transformation,
    _check_employee_signal,
    _check_market_positioning,
    _check_leadership_vs_headcount,
    _check_global_vs_regional,
    _check_ai_native_vs_age,
    _check_trust_at_scale,
    _check_zero_narrative_rich_data,
    _check_narrative_staleness,
    _check_enterprise_vs_team,
    _check_horizontal_claim_vs_hub_reality,
    _check_product_category_gap,
    _check_revenue_shrinkage,
    _check_full_service_vs_niche,
    _check_market_share_gap,
    _check_local_champion_facade,
    _check_age_vs_transformation_velocity,
    _check_competitor_adjacency_gap,
    _check_revenue_per_employee,
    _check_claim_consistency,
    _check_funding_efficiency,
    _check_esg_sustainability_gap,
    _check_customer_concentration_gap,
    _check_moat_delusion,
    _check_regulatory_posture_gap,
    _check_market_timing_gap,
    _check_complexity_denial_gap,
    _edge_case_gaps,
)
from .clusters import _cluster_maturity_gaps
from .llm import _detect_gaps_llm
from ..layers import Layer1, Layer2

if TYPE_CHECKING:
    from ..edge_cases import EdgeCaseContext


def detect_gaps(
    layer1: Layer1,
    layer2: Layer2,
    edge: EdgeCaseContext | None = None,
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
        # Structural gap detectors
        _check_narrative_staleness,
        _check_enterprise_vs_team,
        _check_horizontal_claim_vs_hub_reality,
        _check_product_category_gap,
        # --- v2 addition ---
        _check_revenue_shrinkage,
        _check_full_service_vs_niche,
        _check_market_share_gap,
        _check_local_champion_facade,
        _check_age_vs_transformation_velocity,
        _check_competitor_adjacency_gap,
        # --- v3 additions (quantified + consistency) ---
        _check_revenue_per_employee,
        _check_claim_consistency,
        _check_funding_efficiency,
        # --- v4 additions (ESG, concentration, moat, regulatory, timing, complexity) ---
        _check_esg_sustainability_gap,
        _check_customer_concentration_gap,
        _check_moat_delusion,
        _check_regulatory_posture_gap,
        _check_market_timing_gap,
        _check_complexity_denial_gap,
    ]

    for detector in detectors:
        report.gaps.extend(detector(layer1, layer2))

    if edge:
        report.gaps.extend(_edge_case_gaps(layer1, layer2, edge))

    # Meta-detector: cluster related gaps and escalate severity
    report.gaps = _cluster_maturity_gaps(report.gaps)

    if use_llm:
        from ..llm import get_client
        from ..edge_cases import merge_gaps

        client = get_client()
        if client.available:
            llm_gaps = _detect_gaps_llm(layer1, layer2, edge, client)
            report.gaps = merge_gaps(report.gaps, llm_gaps)

    return report
