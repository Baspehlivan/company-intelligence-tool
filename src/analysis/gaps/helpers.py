"""Parsing helpers for employee counts, revenue, funding, and regions."""

from __future__ import annotations

import re
from typing import Optional


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


def _parse_revenue_number(revenue_signal: str) -> Optional[float]:
    """Extract latest annual revenue number from revenue_signal text.

    Handles formats:
      - "Revenue trend: 2023=391.00B USD -> 2024=383.00B USD"
      - "Revenue: 100M USD"
      - "Revenue: $50 million"
      - "Revenue: EUR 45M"
      - "391.00B"
    """
    if not revenue_signal:
        return None

    text = revenue_signal

    # Pattern 1: Trend format — split on -> or →, take the rightmost segment
    segments = re.split(r"\s*(?:->|→)\s*", text)
    if len(segments) >= 2:
        last_seg = segments[-1].strip()
        # Strip leading "year=" prefix if present (e.g. "2024=8.00B EUR" -> "8.00B EUR")
        last_seg = re.sub(r"^\d{4}\s*=\s*", "", last_seg).strip()
        return _parse_money_string(last_seg)

    # Pattern 2: "Revenue: X" — extract value after "Revenue" or "Turnover"
    rev_prefix = re.search(
        r"(?:revenue|turnover)\s*[:\\-]?\s*([^,;]+)", text, re.IGNORECASE
    )
    if rev_prefix:
        val_str = rev_prefix.group(1).strip()
        return _parse_money_string(val_str)

    # Pattern 3: Try to parse the whole string as a money value
    return _parse_money_string(text)


def _parse_funding_number(funding_signal: str) -> Optional[float]:
    """Extract total funding amount from funding_signal text.

    Handles:
      - "Total funding: EUR 45M+; Last round: Series B (EUR 30M, 2023)"
      - "Total funding: $100M"
      - "Series A: $5M"
    """
    if not funding_signal:
        return None

    text = funding_signal

    # Try "Total funding: X" first
    total_match = re.search(
        r"(?:total|raised|accumulated)\s*(?:funding|capital|investment)\s*[:\\-]?\s*([^;,.]+)",
        text,
        re.IGNORECASE,
    )
    if total_match:
        val_str = total_match.group(1).strip()
    else:
        # Fallback: first amount-like string in the text (include suffix in capture)
        amount_match = re.search(r"([$€££]?\s*[\d,.]+)\s*([MBKmbk])", text)
        if amount_match:
            val_str = amount_match.group(1).strip() + amount_match.group(2)
        else:
            return None

    return _parse_money_string(val_str)


def _parse_money_string(s: str) -> Optional[float]:
    """Parse a money string like 'EUR 45M', '$100M', '391.00B' into float."""
    s = s.replace(",", "").replace("$", "").replace("€", "").replace("£", "")
    s = s.replace("USD", "").replace("EUR", "").replace("GBP", "").strip()

    multiplier = 1
    if re.search(r"[Bb](?:\b|illon)", s):
        multiplier = 1_000_000_000
        s = re.sub(r"[Bb].*$", "", s)
    elif re.search(r"[Mm](?:\b|illion)", s):
        multiplier = 1_000_000
        s = re.sub(r"[Mm].*$", "", s)
    elif re.search(r"[Kk](?:\b|housand)", s):
        multiplier = 1_000
        s = re.sub(r"[Kk].*$", "", s)

    s = s.strip()
    # Remove trailing +/-
    s = s.rstrip("+-")
    try:
        return float(s) * multiplier
    except (ValueError, TypeError):
        return None


_REGION_KEYWORDS = {
    "europe": [
        "germany",
        "europe",
        "eu",
        "uk",
        "france",
        "netherlands",
        "cologne",
        "berlin",
        "munich",
        "london",
        "paris",
        "amsterdam",
        "brussels",
        "zurich",
        "vienna",
    ],
    "north_america": [
        "usa",
        "united states",
        "north america",
        "new york",
        "san francisco",
        "silicon valley",
        "california",
    ],
    "asia": ["asia", "china", "singapore", "japan", "india", "hong kong", "shenzhen"],
    "middle_east": ["dubai", "uae", "saudi", "middle east", "riyadh", "doha", "qatar"],
}


def _regions_in_text(text: str) -> set[str]:
    text = text.lower()
    found = set()
    for region, kws in _REGION_KEYWORDS.items():
        if any(kw in text for kw in kws):
            found.add(region)
    return found
