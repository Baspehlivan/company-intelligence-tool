"""
Edge-case handling for the reframing engine.

Covers: zero public data, subsidiary/parent confusion, rename/acquisition,
and sparse-data enrichment from reference snapshots.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EdgeCaseContext:
    """Flags and notes passed into gap detection and LLM prompts."""

    flags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    enrichment_applied: bool = False
    original_data_quality: str = ""

    @property
    def summary(self) -> str:
        parts = []
        if self.flags:
            parts.append("Flags: " + ", ".join(self.flags))
        if self.warnings:
            parts.append("Warnings: " + "; ".join(self.warnings))
        if self.enrichment_applied:
            parts.append("Reference enrichment merged into sparse live data")
        return " | ".join(parts) if parts else ""


# Patterns suggesting subsidiary / division of larger group
_SUBSIDIARY_PATTERNS = [
    r"\b(?:a\s+)?(?:division|subsidiary|unit)\s+of\b",
    r"\bpart\s+of\s+(?:the\s+)?[\w\s]+\s+group\b",
    r"\bowned\s+by\b",
    r"\bacquired\s+by\b",
    r"\b(?:formerly|previously)\s+known\s+as\b",
]

_RENAME_PATTERNS = [
    r"\brebrand(?:ed)?\b",
    r"\bformerly\s+(?:known\s+as\s+)?[\w\s]+",
    r"\bchanged\s+(?:its\s+)?name\b",
    r"\bmerger\s+with\b",
    r"\bacquisition\s+(?:of|by)\b",
]

_PARENT_HINTS = [
    "group", "holdings", "inc.", "corp", "plc", "ag", "gmbh",
]


def analyze_edge_cases(report: dict, use_reference: bool = True) -> tuple[dict, EdgeCaseContext]:
    """Inspect collector output, optionally enrich, return (report, context)."""
    ctx = EdgeCaseContext()
    ctx.original_data_quality = _assess_fill(report)

    enriched = report
    if use_reference and (_is_sparse(report) or _needs_layer1_enrichment(report)):
        enriched = _try_reference_enrichment(report, ctx)

    _check_zero_public_data(enriched, ctx)
    _check_subsidiary_signals(enriched, ctx)
    _check_rename_acquisition(enriched, ctx)
    _check_name_collision(enriched, ctx)

    return enriched, ctx


def _needs_layer1_enrichment(report: dict) -> bool:
    sd = report.get("self_description") or {}
    has_l1 = any(
        sd.get(k)
        for k in ("tagline", "mission", "industry_positioning")
    ) or sd.get("public_statements")
    if has_l1:
        return False
    try:
        from src.data_collector.reference import get_reference
    except ImportError:
        from data_collector.reference import get_reference  # type: ignore
    return get_reference(report.get("company_name", "")) is not None


def _assess_fill(report: dict) -> str:
    sd = report.get("self_description", {})
    core = report.get("core_data", {})
    fin = report.get("financials", {})
    filled = sum(
        1
        for v in [
            sd.get("tagline"),
            sd.get("industry_positioning"),
            core.get("description"),
            core.get("employees"),
            fin.get("revenue"),
            fin.get("funding_total"),
        ]
        if v
    )
    return "sparse" if filled <= 1 else ("moderate" if filled <= 3 else "rich")


def _is_sparse(report: dict) -> bool:
    return _assess_fill(report) == "sparse"


def _check_zero_public_data(report: dict, ctx: EdgeCaseContext) -> None:
    sd = report.get("self_description", {})
    narrative_parts = [
        sd.get("tagline", ""),
        sd.get("mission", ""),
        sd.get("industry_positioning", ""),
        *sd.get("public_statements", []),
    ]
    has_narrative = any(p and str(p).strip() for p in narrative_parts)
    core_desc = (report.get("core_data") or {}).get("description", "")

    if not has_narrative and not core_desc:
        ctx.flags.append("zero_public_narrative")
        ctx.warnings.append(
            "No Layer 1 self-description — gaps must come from data signals only; "
            "frame all insights as questions"
        )


def _check_subsidiary_signals(report: dict, ctx: EdgeCaseContext) -> None:
    blob = _text_blob(report)
    for pat in _SUBSIDIARY_PATTERNS:
        if re.search(pat, blob, re.IGNORECASE):
            ctx.flags.append("possible_subsidiary")
            ctx.warnings.append(
                "Entity may be a subsidiary/division — financials may reflect parent group, not this unit"
            )
            return

    name = (report.get("company_name") or "").lower()
    # e.g. "Rhenus Warehousing Solutions" under Rhenus Group
    if any(h in name for h in ("solutions", "services", "digital", "labs", "ventures")):
        parent_guess = name.split()[0] if name.split() else ""
        if parent_guess and parent_guess not in name.replace(parent_guess, "", 1):
            pass
        ctx.flags.append("possible_brand_line")
        ctx.warnings.append(
            "Name suggests a business line or subsidiary — verify whether data applies to whole group"
        )


def _check_rename_acquisition(report: dict, ctx: EdgeCaseContext) -> None:
    blob = _text_blob(report)
    for pat in _RENAME_PATTERNS:
        if re.search(pat, blob, re.IGNORECASE):
            ctx.flags.append("rename_or_acquisition")
            ctx.warnings.append(
                "Signals of rebrand, merger, or acquisition — historical data may not match current positioning"
            )
            return

    growth = report.get("growth_signals") or {}
    if growth.get("recent_acquisitions"):
        ctx.flags.append("active_acquirer")
        ctx.warnings.append(
            "Recent acquisitions — public heritage narrative may lag operational reality"
        )


def _check_name_collision(report: dict, ctx: EdgeCaseContext) -> None:
    """Same name as a larger public entity but collected as private."""
    status = report.get("status", "")
    name = (report.get("company_name") or "").lower()
    employees = (report.get("core_data") or {}).get("employees")

    if status == "private" and employees and employees > 10000:
        ctx.flags.append("scale_name_mismatch")
        ctx.warnings.append(
            "Large employee count with private status — may be division of group or data attribution error"
        )

    # Famous names that are often wrong ticker
    ambiguous = {"delta", "target", "square", "ring", "amazon"}
    first_token = name.split()[0] if name else ""
    if first_token in ambiguous and not report.get("ticker"):
        ctx.flags.append("ambiguous_company_name")
        ctx.warnings.append(
            f"'{report.get('company_name')}' is ambiguous — confirm exact entity before reframing"
        )


def _try_reference_enrichment(report: dict, ctx: EdgeCaseContext) -> dict:
    try:
        from src.data_collector.reference import get_reference
    except ImportError:
        from data_collector.reference import get_reference  # type: ignore

    ref = get_reference(report.get("company_name", ""))
    if not ref:
        return report

    merged = _merge_sparse(report, ref)
    ctx.enrichment_applied = True
    ctx.flags.append("reference_enriched")
    ctx.warnings.append(
        f"Sparse live data enriched with curated reference for {ref.get('company_name')}"
    )
    return merged


def _merge_sparse(live: dict, ref: dict) -> dict:
    """Fill empty live fields from reference without overwriting live values."""
    out = {**live}
    for key in ("self_description", "core_data", "financials", "growth_signals", "market_position"):
        live_sec = dict(live.get(key) or {})
        ref_sec = ref.get(key) or {}
        for k, v in ref_sec.items():
            if live_sec.get(k) in (None, "", [], {}):
                live_sec[k] = v
        out[key] = live_sec

    sources = list(out.get("_sources") or [])
    sources.append({"source": "reference_enrichment", "note": "merged into sparse live report"})
    out["_sources"] = sources
    return out


def _text_blob(report: dict) -> str:
    parts = []
    sd = report.get("self_description") or {}
    core = report.get("core_data") or {}
    parts.extend(
        [
            sd.get("tagline", ""),
            sd.get("mission", ""),
            sd.get("industry_positioning", ""),
            core.get("description", ""),
        ]
    )
    parts.extend(sd.get("public_statements") or [])
    growth = report.get("growth_signals") or {}
    parts.extend(growth.get("recent_acquisitions") or [])
    return " ".join(str(p) for p in parts if p)


def merge_gaps(heuristic: list, llm_gaps: list[dict]) -> list:
    """Deduplicate LLM gaps against heuristic by category."""
    from .gaps import Gap

    seen_cats = {g.category for g in heuristic}
    merged = list(heuristic)
    for g in llm_gaps:
        cat = g.get("category", "llm_detected")
        if cat in seen_cats:
            continue
        merged.append(
            Gap(
                category=cat,
                severity=g.get("severity", "medium"),
                claim=g.get("claim", ""),
                reality=g.get("reality", ""),
                note=g.get("note", ""),
            )
        )
        seen_cats.add(cat)
    return merged
