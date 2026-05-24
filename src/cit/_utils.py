"""Shared CIT utilities — one source of truth for formatters, slugs, and helpers.

Every module in CIT should import from here instead of defining its own _fmt().
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


def fmt_large(val, include_suffix: bool = True) -> str:
    """Format large numbers: 1234567890 -> '1.23B'.

    Args:
        val: Number to format (int, float, or string).
        include_suffix: If True (default), returns '1.23B'. If False, returns '1.23'.
    """
    if val is None:
        return ""
    try:
        v = float(val)
    except (ValueError, TypeError):
        return str(val)
    if abs(v) >= 1e12:
        s = f"{v / 1e12:.2f}"
        return f"{s}T" if include_suffix else s
    elif abs(v) >= 1e9:
        s = f"{v / 1e9:.2f}"
        return f"{s}B" if include_suffix else s
    elif abs(v) >= 1e6:
        s = f"{v / 1e6:.2f}"
        return f"{s}M" if include_suffix else s
    elif abs(v) >= 1e3:
        s = f"{v / 1e3:.2f}"
        return f"{s}K" if include_suffix else s
    else:
        return f"{v:.2f}"


def fmt_compact(val) -> str:
    """Alias for fmt_large with suffix."""
    return fmt_large(val, include_suffix=True)


def slug(name: str) -> str:
    """Convert company name to filesystem-safe slug."""
    return name.lower().replace(" ", "-").replace("_", "-").replace("/", "-")


def trunc(text: str, n: int) -> str:
    """Truncate text to n characters, adding ellipsis if needed."""
    return text if len(text) <= n else text[: n - 1] + "…"


def sanitize_html(text: str) -> str:
    """Remove HTML tags from text for plain-text display."""
    text = re.sub(r"<[^>]+>", "", text)
    text = (
        text.replace("&mdash;", "\u2014")
        .replace("&ndash;", "\u2013")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&#9888;", "\u26a0")
        .replace("&#37;", "%")
        .replace("&#9679;", "\u2022")
    )
    return text.strip()


def extract_year(val) -> int | None:
    """Extract a 4-digit year from a value (int, string, or None)."""
    if isinstance(val, int):
        return val
    m = re.search(r"\b(19\d\d|20[0-2]\d)\b", str(val))
    return int(m.group(1)) if m else None


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()
