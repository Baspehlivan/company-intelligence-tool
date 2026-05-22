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
    """
    if not revenue_signal:
        return None

    text = revenue_signal

    # Pattern 1: "Revenue trend: year1=X -> year2=Y" — get the latest (rightmost)
    trend_match = re.search(r"(?:->|→)\s*(.+?)$", text)
    if trend_match:
        val_str = trend_match.group(1).strip()
    else:
        # Pattern 2: "Revenue: X" — extract first value after "Revenue"
        rev_prefix = re.search(
            r"(?:revenue|turnover)\s*[:\-]?\s*([^,;.]+)", text, re.IGNORECASE
        )
        if rev_prefix:
            val_str = rev_prefix.group(1).strip()
        else:
            # Pattern 3: any dollar/EUR amount in the text
            val_str = text

    # Normalize: remove commas, "USD", "EUR", "$", "€", "million", "billion"
    val_str = (
        val_str.replace(",", "")
        .replace("$", "")
        .replace("€", "")
        .replace("USD", "")
        .replace("EUR", "")
        .strip()
    )

    # Check for B/billion, M/million, K/thousand
    multiplier = 1
    if (
        re.search(r"\bbillion\b", val_str, re.IGNORECASE)
        or ("B" in val_str.upper()
            and not re.search(r"\d+B", val_str))
    ):
        # "391.00B" or "391 billion"
        b_match = re.search(r"[\d.]+(?=\s*B)", val_str, re.IGNORECASE) or re.search(
            r"([\d.]+)\s*B", val_str, re.IGNORECASE
        )
        if b_match:
            val_str = b_match.group(1)
            multiplier = 1_000_000_000
        else:
            return None
    elif (
        re.search(r"\bmillion\b", val_str, re.IGNORECASE)
        or ("M" in val_str.upper()
            and not re.search(r"\d+M", val_str))
    ):
        m_match = re.search(r"[\d.]+(?=\s*M)", val_str, re.IGNORECASE) or re.search(
            r"([\d.]+)\s*M", val_str, re.IGNORECASE
        )
        if m_match:
            val_str = m_match.group(1)
            multiplier = 1_000_000
        else:
            return None
    else:
        # Check for "391.00B" / "100M" compact notation
        b_compact = re.search(r"([\d.]+)\s*[Bb]", val_str)
        if b_compact:
            val_str = b_compact.group(1)
            multiplier = 1_000_000_000
        m_compact = re.search(r"([\d.]+)\s*[Mm](?!\w)", val_str)
        if m_compact:
            val_str = m_compact.group(1)
            multiplier = 1_000_000

    try:
        return float(val_str) * multiplier
    except (ValueError, TypeError):
        return None


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
        r"(?:total|raised|accumulated)\s*(?:funding|capital|investment)\s*[:\-]?\s*([^;,.]+)",
        text,
        re.IGNORECASE,
    )
    if total_match:
        val_str = total_match.group(1).strip()
    else:
        # Fallback: first amount-like string in the text
        amount_match = re.search(r"([$€£EURUSD]?\s*[\d,.]+)\s*[MBKmbk]", text)
        if amount_match:
            val_str = amount_match.group(1).strip()
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
