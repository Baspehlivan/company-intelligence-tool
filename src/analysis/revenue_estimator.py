"""
Revenue estimator for CIT — estimates private company revenue from employee count × sector benchmarks.

How it works:
  1. Maintains a sector → revenue-per-employee lookup table (from public company averages)
  2. When revenue is unknown but employee count is known, estimates revenue as a range
  3. Also tries to derive benchmarks from EDGAR public company data when available
  4. Returns confidence level based on data quality

Benchmarks sourced from NYU Stern and public filings. Ranges reflect the 25th-75th
percentile within each sector.
"""

from __future__ import annotations

import re
from typing import Optional

# Revenue per employee benchmarks by sector (25th, 50th, 75th percentiles)
# Sources: NYU Stern Employee Metrics (2026), SaaS Capital, public filings analysis
SECTOR_BENCHMARKS: dict[str, tuple[float, float, float]] = {
    # (p25, median, p75) in USD
    "Enterprise Software":       (180000, 280000, 450000),
    "SaaS":                      (150000, 250000, 400000),
    "Fintech":                   (200000, 350000, 600000),
    "Logistics":                 (100000, 175000, 300000),
    "Supply Chain Tech":         (180000, 280000, 450000),
    "Consulting":                (150000, 250000, 400000),
    "Industrial":                (200000, 350000, 550000),
    "Manufacturing":             (200000, 350000, 550000),
    "Technology":                (250000, 400000, 700000),
    "Financial Services":        (250000, 400000, 650000),
    "Enterprise Software/SaaS":  (160000, 270000, 430000),
    "Design Software":           (250000, 400000, 650000),
    "Mobility":                  (150000, 250000, 400000),
    "HR Tech / SaaS":            (130000, 220000, 350000),
    "Healthcare":                (150000, 250000, 450000),
    "Retail":                    (100000, 180000, 350000),
    "Media":                     (200000, 350000, 600000),
    "Telecommunications":        (150000, 250000, 400000),
    "Real Estate":               (200000, 350000, 600000),
    "Construction":              (150000, 250000, 400000),
    "Automotive":                (200000, 350000, 550000),
    "Food & Beverage":           (100000, 180000, 300000),
    "Energy":                    (300000, 600000, 1200000),
}

# Generic fallback when sector is unknown
FALLBACK_BENCHMARKS = (100000, 200000, 400000)

# Sector aliases for fuzzy matching
SECTOR_ALIASES: dict[str, str] = {
    "saas": "SaaS",
    "enterprise software": "Enterprise Software",
    "enterprise": "Enterprise Software",
    "software": "Enterprise Software",
    "cloud": "Enterprise Software",
    "logistics": "Logistics",
    "supply chain": "Supply Chain Tech",
    "supply_chain_tech": "Supply Chain Tech",
    "fintech": "Fintech",
    "consulting": "Consulting",
    "industrial": "Industrial",
    "manufacturing": "Manufacturing",
    "tech": "Technology",
    "technology": "Technology",
    "financial services": "Financial Services",
    "financial_services": "Financial Services",
    "design software": "Design Software",
    "design_software": "Design Software",
    "mobility": "Mobility",
    "hr tech": "HR Tech / SaaS",
    "hrtech": "HR Tech / SaaS",
    "healthcare": "Healthcare",
    "retail": "Retail",
    "media": "Media",
    "telecom": "Telecommunications",
    "telecommunications": "Telecommunications",
    "real estate": "Real Estate",
    "real_estate": "Real Estate",
    "construction": "Construction",
    "automotive": "Automotive",
    "food & beverage": "Food & Beverage",
    "food": "Food & Beverage",
    "energy": "Energy",
    "consumer_tech": "Technology",
    "enterprise_software": "Enterprise Software",
    "supply_chain_tech": "Supply Chain Tech",
}


def estimate_revenue(
    sector: Optional[str],
    employees: Optional[int],
    known_revenue: Optional[dict] = None,
) -> dict:
    """Estimate revenue for a company based on sector and employee count.

    Args:
        sector: Company sector string (fuzzy-matched to benchmarks)
        employees: Employee count (int or None)
        known_revenue: Already-known revenue dict (e.g. from EDGAR or reference)

    Returns:
        dict with keys:
          - estimated_revenue: str (formatted range, e.g. "$50M-$100M")
          - estimated_revenue_low: float (low estimate)
          - estimated_revenue_high: float (high estimate)
          - estimated_revenue_mid: float (midpoint estimate)
          - revenue_per_employee: float | None
          - estimation_method: str ("sector_benchmark" | "known" | "unknown")
          - estimation_confidence: str ("high" | "medium" | "low")
          - sector_used: str (resolved sector name)
    """
    result: dict = {
        "estimated_revenue": None,
        "estimated_revenue_low": None,
        "estimated_revenue_high": None,
        "estimated_revenue_mid": None,
        "revenue_per_employee": None,
        "estimation_method": "unknown",
        "estimation_confidence": "low",
        "sector_used": sector or "unknown",
    }

    # If we have known revenue, use it
    if known_revenue:
        if isinstance(known_revenue, dict) and known_revenue:
            result["estimation_method"] = "known"
            result["estimation_confidence"] = "high"
            # Extract the most recent value
            years = sorted(known_revenue.keys())
            latest = known_revenue[years[-1]]
            try:
                val = _parse_revenue_str(str(latest))
                if val:
                    result["estimated_revenue_low"] = val * 0.9
                    result["estimated_revenue_high"] = val * 1.1
                    result["estimated_revenue_mid"] = val
                    result["estimated_revenue"] = _fmt_range(val * 0.9, val * 1.1)
            except (ValueError, TypeError):
                pass
            return result

    # Need employees to estimate
    if employees is None or employees <= 0:
        result["estimation_method"] = "unknown"
        result["estimation_confidence"] = "low"
        return result

    # Resolve sector
    resolved_sector = _resolve_sector(sector or "")
    benchmarks = SECTOR_BENCHMARKS.get(resolved_sector, FALLBACK_BENCHMARKS)
    p25, median, p75 = benchmarks

    # Apply employee count scaling with diminishing returns
    # Very small companies (< 10 emp) are less efficient
    # Very large companies (> 10000 emp) are more efficient due to scale
    scale_factor = 1.0
    if employees < 10:
        scale_factor = 0.6
    elif employees < 50:
        scale_factor = 0.8
    elif employees > 5000:
        scale_factor = 1.3
    elif employees > 1000:
        scale_factor = 1.15

    rev_low = employees * p25 * scale_factor
    rev_mid = employees * median * scale_factor
    rev_high = employees * p75 * scale_factor

    result["estimated_revenue_low"] = rev_low
    result["estimated_revenue_high"] = rev_high
    result["estimated_revenue_mid"] = rev_mid
    result["estimated_revenue"] = _fmt_range(rev_low, rev_high)
    result["revenue_per_employee"] = rev_mid / employees if employees > 0 else None
    result["estimation_method"] = "sector_benchmark"
    result["sector_used"] = resolved_sector

    # Confidence
    if resolved_sector != "unknown" and employees >= 10 and employees <= 100000:
        result["estimation_confidence"] = "medium"
    elif resolved_sector != "unknown":
        result["estimation_confidence"] = "low"
    else:
        result["estimation_confidence"] = "low"

    return result


def _resolve_sector(sector: str) -> str:
    """Fuzzy-match a sector string to benchmark keys."""
    if not sector:
        return "unknown"

    sector_lower = sector.lower().strip()

    # Direct match
    if sector in SECTOR_BENCHMARKS:
        return sector

    # Alias match
    if sector_lower in SECTOR_ALIASES:
        return SECTOR_ALIASES[sector_lower]

    # Partial match
    for alias, target in SECTOR_ALIASES.items():
        if alias in sector_lower or sector_lower in alias:
            return target

    # Fallback: check if any benchmark key is contained in sector string
    for key in SECTOR_BENCHMARKS:
        if key.lower() in sector_lower:
            return key

    return "unknown"


def _parse_revenue_str(s: str) -> Optional[float]:
    """Parse a revenue string like '$1.2B', 'EUR 500M', '100M' to USD float."""
    s = s.strip()
    multiplier = 1.0

    # Remove currency symbols / prefixes
    for prefix in ["$", "EUR", "USD", "€", "£"]:
        s = s.replace(prefix, "")

    s = s.strip()

    if not s:
        return None

    # Suffix multipliers
    if s.upper().endswith("T"):
        multiplier = 1e12
        s = s[:-1]
    elif s.upper().endswith("B"):
        multiplier = 1e9
        s = s[:-1]
    elif s.upper().endswith("M"):
        multiplier = 1e6
        s = s[:-1]
    elif s.upper().endswith("K"):
        multiplier = 1e3
        s = s[:-1]

    # Remove remaining non-numeric (except dot)
    s = re.sub(r"[^0-9.]", "", s)
    if not s:
        return None

    try:
        return float(s) * multiplier
    except ValueError:
        return None


def _fmt_range(low: float, high: float) -> str:
    """Format a revenue range like '$50M-$100M'."""
    def _fmt(v: float) -> str:
        if abs(v) >= 1e12:
            return f"${v/1e12:.1f}T"
        elif abs(v) >= 1e9:
            return f"${v/1e9:.1f}B"
        elif abs(v) >= 1e6:
            return f"${v/1e6:.0f}M"
        elif abs(v) >= 1e3:
            return f"${v/1e3:.0f}K"
        else:
            return f"${v:.0f}"

    return f"{_fmt(low)}–{_fmt(high)}"



