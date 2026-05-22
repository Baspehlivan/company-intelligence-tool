"""Maturity cluster meta-detector: escalates severity when related gaps co-occur."""

from __future__ import annotations

from .models import Gap

_CLUSTERS = [
    {
        "name": "scale_mismatch",
        "label": "Scale Mismatch",
        "member_categories": {
            "scale_claim",
            "leadership_vs_headcount",
            "enterprise_vs_team",
            "enterprise_claim_startup_reality",
            "competitor_adjacency_gap",
            "market_share_gap",
            "global_vs_regional",
            "local_champion_facade",
            "customer_concentration_gap",
        },
        "min_to_escalate": 2,
        "severity_boost": True,
        "severity_if_all_high": "high",
    },
    {
        "name": "innovation_theatre",
        "label": "Innovation Theatre",
        "member_categories": {
            "innovation_vs_stage",
            "ai_native_vs_legacy",
            "narrative_staleness",
            "legacy_disruption_paradox",
            "age_vs_transformation_velocity",
            "product_category_gap",
            "heritage_vs_innovation_paradox",
            "market_timing_gap",
        },
        "min_to_escalate": 2,
        "severity_boost": True,
        "severity_if_all_high": "high",
    },
    {
        "name": "positioning_confusion",
        "label": "Positioning Confusion",
        "member_categories": {
            "positioning_drift",
            "platform_claim_narrow_reality",
            "full_service_vs_niche",
            "product_category_gap",
            "local_vs_global_narrative",
            "claim_contradiction",
            "heritage_vs_startup_language",
            "complexity_denial_gap",
            "regulatory_posture_gap",
            "moat_delusion",
        },
        "min_to_escalate": 2,
        "severity_boost": True,
        "severity_if_all_high": "high",
    },
    {
        "name": "growth_theatre",
        "label": "Growth Theatre",
        "member_categories": {
            "growth_mismatch",
            "revenue_shrinkage",
            "funding_efficiency_gap",
            "revenue_per_employee_gap",
            "age_vs_transformation_velocity",
            "esg_sustainability_gap",
        },
        "min_to_escalate": 2,
        "severity_boost": True,
        "severity_if_all_high": "medium",
    },
]


def _cluster_maturity_gaps(gaps: list[Gap]) -> list[Gap]:
    """Meta-detector: group related gaps by cluster, escalate severity when
    multiple detectors fire on the same underlying tension."""
    if not gaps:
        return gaps

    # Build category -> list of gap indices
    cat_indices: dict[str, list[int]] = {}
    for i, g in enumerate(gaps):
        cat_indices.setdefault(g.category, []).append(i)

    for cluster in _CLUSTERS:
        matching: set[int] = set()
        for cat in cluster["member_categories"]:
            if cat in cat_indices:
                matching.update(cat_indices[cat])

        if len(matching) >= cluster["min_to_escalate"]:
            # Boost severity of all matching gaps
            severity_order = {"high": 0, "medium": 1, "low": 2}
            highest = min(
                (severity_order.get(gaps[i].severity, 9) for i in matching), default=2
            )
            # The cluster itself is as severe as its most severe member
            cluster_severity = (
                ["high", "medium", "low"][highest] if highest <= 2 else "low"
            )

            # Add cluster note to each member
            for i in matching:
                g = gaps[i]
                if cluster["severity_boost"]:
                    # Only boost if not already high
                    if g.severity == "low":
                        g.severity = "medium"
                    elif g.severity == "medium":
                        g.severity = "high"
                # Append cluster info to note
                cluster_tag = f"[{cluster['label']}]"
                if cluster_tag not in g.note:
                    g.note = f"{cluster_tag} {g.note}"

    return gaps
