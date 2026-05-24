"""
Crunchbase data provider for CIT.

Two-path approach:
  1. API path — uses Crunchbase Basic API v4 when CIT_CRUNCHBASE_API_KEY is set
  2. Public scrape path — parses Crunchbase public profile pages (free, no key needed)

Returns REPORT_SCHEMA-compatible funding data: funding_total, last_funding_round,
notable_investors, and enrichment for core_data and self_description.

Cache: 7-day TTL for API results, 1-day for scrape (scrape results change more often).
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

CACHE_DIR = Path.home() / ".cit" / "cache" / "crunchbase"
API_CACHE_TTL = 604800   # 7 days
SCRAPE_CACHE_TTL = 86400  # 1 day

ENV_KEY = "CIT_CRUNCHBASE_API_KEY"
API_BASE = "https://api.crunchbase.com/api/v4"


def _cache_path(name: str, prefix: str = "api") -> Path:
    safe = "".join(c if c.isalnum() else "_" for c in name.lower().strip())[:60]
    return CACHE_DIR / f"{prefix}_{safe}.json"


def _load_cache(path: Path, ttl: int) -> dict | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        age = time.time() - data.get("_cached_at", 0)
        if age < ttl:
            return data.get("payload")
    except (json.JSONDecodeError, OSError):
        path.unlink(missing_ok=True)
    return None


def _save_cache(path: Path, payload: dict) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {"payload": payload, "_cached_at": time.time()}
        path.write_text(json.dumps(data, default=str))
    except OSError:
        pass


def fetch_crunchbase(company_name: str, *, force_refetch: bool = False) -> dict:
    """Fetch company data from Crunchbase.

    Returns a dict with keys matching live_collector's financials/market data:
      - funding_total: str (e.g. "$45M")
      - last_funding_round: str (e.g. "Series B (2023)")
      - last_funding_date: str (e.g. "2023-06")
      - notable_investors: list[str]
      - estimated_revenue_range: str (e.g. "$10M-$50M")
      - total_funding_usd: float | None (raw number for math)
      - num_funding_rounds: int
      - description: str (short)
      - employees: int | None
      - founded_year: int | None
      - hq_location: str | None
      - categories: list[str]
      - acquisition_status: str | None  # "acquired" | "ipo" | None
      - stock_symbol: str | None
      - _source: str ("crunchbase_api" | "crunchbase_scrape")

    Returns empty dict if unavailable.
    """
    api_key = os.environ.get(ENV_KEY)

    if api_key:
        result = _fetch_via_api(company_name, api_key, force_refetch)
        if result and not result.get("_error"):
            return result

    # Fallback: scrape public profile
    return _scrape_public(company_name, force_refetch)


# ── API Path ──────────────────────────────────────────────────────────────


def _fetch_via_api(company_name: str, api_key: str, force: bool) -> dict:
    cache_path = _cache_path(company_name, "api")
    if not force:
        cached = _load_cache(cache_path, API_CACHE_TTL)
        if cached is not None:
            return cached

    result = _call_search_api(company_name, api_key)
    if result:
        _save_cache(cache_path, result)
    return result or {"_error": "not_found", "_source": "crunchbase_api"}


def _call_search_api(query: str, api_key: str) -> dict:
    """Search Crunchbase API v4 for an organization."""
    import requests

    url = f"{API_BASE}/searches/organizations"
    headers = {
        "X-cb-user-key": api_key,
        "Content-Type": "application/json",
        "User-Agent": "CIT/0.2.0 (company-intelligence-tool; crunchbase-enricher)",
    }
    payload = {
        "field_ids": [
            "name", "short_description", "description",
            "founded_on", "employee_count", "employee_count_enum",
            "num_employees_enum", "categories", "location_identifiers",
            "rank_org", "rank_org_company",
            "total_funding_usd", "last_funding_type", "last_funding_date",
            "num_funding_rounds", "investor_identifiers", "investor_names",
            "acquisition_status", "stock_symbol", "stock_exchange_symbol",
            "estimated_revenue_range", "website_url", "city", "region", "country",
            "rank_org",
        ],
        "limit": 5,
    }

    # First: search by name
    query_params = {
        "query": [
            {
                "type": "predicate",
                "field_id": "name",
                "operator_id": "contains",
                "values": [query],
            }
        ]
    }
    payload["queries"] = [query_params]

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code == 401 or resp.status_code == 403:
            return {"_error": "API key invalid or unauthorized"}
        if resp.status_code != 200:
            return {"_error": f"HTTP {resp.status_code}"}

        data = resp.json()
        entities = data.get("entities", [])
        if not entities:
            return {"_error": "not_found"}

        best = _pick_best_match(entities, query)
        return _parse_api_entity(best)
    except requests.RequestException as e:
        return {"_error": str(e)}


def _pick_best_match(entities: list, query: str) -> dict:
    """Pick the best matching entity from search results."""
    query_lower = query.lower().strip()
    best = None
    best_score = 0

    for entity in entities:
        props = entity.get("properties", {})
        name = (props.get("name") or "").lower()
        score = 0

        # Exact match
        if name == query_lower:
            score = 100
        # Query is substring of name
        elif query_lower in name:
            score = 50
        # Name is substring of query
        elif name and name in query_lower:
            score = 30

        # Prefer organizations with higher rank (more established)
        rank = props.get("rank_org_company") or props.get("rank_org") or 0
        score += max(0, 100 - int(rank)) * 0.1 if rank else 0

        if score > best_score:
            best_score = score
            best = entity

    return best or entities[0]


def _parse_api_entity(entity: dict) -> dict:
    """Parse a Crunchbase API entity into our schema."""
    props = entity.get("properties", {})
    result: dict = {
        "_source": "crunchbase_api",
        "_matched_name": props.get("name", ""),
    }

    # Core data
    if props.get("short_description"):
        result["description"] = props["short_description"]
    elif props.get("description"):
        result["description"] = props["description"]

    if props.get("employee_count"):
        result["employees"] = props["employee_count"]
    elif props.get("employee_count_enum"):
        # e.g. "1_10", "11_50", "51_100", "101_250", "251_500", "501_1000", "1001_5000", "5001_10000", "10001_plus"
        result["employees"] = _parse_employee_enum(props["employee_count_enum"])

    founded = props.get("founded_on")
    if founded and isinstance(founded, str):
        m = re.match(r"(\d{4})", founded)
        if m:
            result["founded_year"] = int(m.group(1))

    # Location
    parts = []
    for k in ("city", "region", "country"):
        v = props.get(k)
        if v:
            parts.append(str(v))
    if parts:
        result["hq_location"] = ", ".join(parts)

    # Categories / sectors
    categories = []
    for cat in props.get("categories", []):
        if isinstance(cat, dict) and cat.get("value"):
            categories.append(cat["value"])
    result["categories"] = categories

    # Financials
    total_funding = props.get("total_funding_usd")
    if total_funding is not None:
        try:
            result["total_funding_usd"] = float(total_funding)
            result["funding_total"] = _fmt_funding(float(total_funding))
        except (ValueError, TypeError):
            pass

    last_type = props.get("last_funding_type")
    last_date = props.get("last_funding_date")
    if last_type:
        date_str = f" ({last_date})" if last_date else ""
        result["last_funding_round"] = f"{last_type}{date_str}"
        result["last_funding_date"] = last_date

    num_rounds = props.get("num_funding_rounds")
    if num_rounds is not None:
        try:
            result["num_funding_rounds"] = int(num_rounds)
        except (ValueError, TypeError):
            pass

    # Investors
    investors = []
    for inv in props.get("investor_identifiers", []):
        if isinstance(inv, dict) and inv.get("value"):
            investors.append(inv["value"])
    for inv_name in props.get("investor_names", []):
        if isinstance(inv_name, str) and inv_name not in investors:
            investors.append(inv_name)
    result["notable_investors"] = investors

    # Revenue estimate
    rev_range = props.get("estimated_revenue_range")
    if rev_range:
        result["estimated_revenue_range"] = rev_range

    # Status
    acq = props.get("acquisition_status")
    if acq:
        result["acquisition_status"] = acq
    symbol = props.get("stock_symbol")
    if symbol:
        result["stock_symbol"] = symbol

    return result


def _parse_employee_enum(enum_val: str) -> Optional[int]:
    """Convert Crunchbase employee enum to midpoint integer."""
    mapping = {
        "1_10": 5,
        "11_50": 30,
        "51_100": 75,
        "101_250": 175,
        "251_500": 375,
        "501_1000": 750,
        "1001_5000": 3000,
        "5001_10000": 7500,
        "10001_plus": 15000,
    }
    norm = enum_val.lower().replace(" ", "_")
    if norm in mapping:
        return mapping[norm]
    # Try parsing "X_Y" format
    m = re.match(r"(\d+)_(\d+)", norm)
    if m:
        return (int(m.group(1)) + int(m.group(2))) // 2
    return None


# ── Scrape Path ───────────────────────────────────────────────────────────


def _scrape_public(company_name: str, force: bool) -> dict:
    """Scrape Crunchbase public profile page for company data."""
    cache_path = _cache_path(company_name, "scrape")
    if not force:
        cached = _load_cache(cache_path, SCRAPE_CACHE_TTL)
        if cached is not None:
            return cached

    result = _do_scrape(company_name)
    if result and not result.get("_error"):
        _save_cache(cache_path, result)
    return result or {"_error": "not_found", "_source": "crunchbase_scrape"}


def _do_scrape(company_name: str) -> dict:
    """Extract company data from public Crunchbase page."""
    import requests
    from bs4 import BeautifulSoup

    # Build URL: lowercase, replace spaces with hyphens, remove special chars
    slug = re.sub(r"[^a-z0-9-]", "", company_name.lower().replace(" ", "-"))
    url = f"https://www.crunchbase.com/organization/{slug}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return {"_error": f"HTTP {resp.status_code}", "url": url}
    except requests.RequestException as e:
        return {"_error": str(e), "url": url}

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    result: dict = {"_source": "crunchbase_scrape", "url": url, "_matched_name": company_name}

    # Meta description
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        result["description"] = meta["content"]

    # Funding amount — look for patterns in page text
    funding_patterns = [
        r"(\$[\d,.]+[BMK]?)\s+(?:in\s+)?(?:Total\s+)?(?:Funding|Equity\s+Funding)",
        r"(?:Total\s+)?(?:Funding|Raised)\s*(?:of\s*)?(\$[\d,.]+[BMK]?)\s*",
        r"(\$[\d,.]+[BMK]?)\s+—\s+(?:Series\s+[A-Za-z0-9]|Seed|Venture)",
    ]
    for pat in funding_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            result["funding_total"] = m.group(1)
            break

    # Last funding round
    round_patterns = [
        r"(Series\s+[A-Za-z0-9]+)\s*(?:round\s*)?(?:of\s*)?(\$[\d,.]+[BMK]?)?\s*(?:on\s+)?([A-Z][a-z]+\s+\d{4})?",
        r"(Seed\s*(?:Round)?)\s*(?:of\s*)?(\$[\d,.]+[BMK]?)?\s*(?:on\s+)?([A-Z][a-z]+\s+\d{4})?",
    ]
    for pat in round_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            parts = [p for p in m.groups() if p]
            if parts:
                result["last_funding_round"] = " ".join(parts)
                break

    # Employee count
    emp_match = re.search(r"(\d[\d,]*)\s*employees?", text, re.IGNORECASE)
    if emp_match:
        try:
            result["employees"] = int(emp_match.group(1).replace(",", ""))
        except ValueError:
            pass

    # Employee range (e.g. "51-100", "11-50 employees")
    emp_range = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*employees?", text, re.IGNORECASE)
    if emp_range and "employees" not in result:
        try:
            lo, hi = int(emp_range.group(1)), int(emp_range.group(2))
            result["employees"] = (lo + hi) // 2
        except ValueError:
            pass

    # Founded year
    founded_match = re.search(r"Founded\s*(?:\sin\s+)?(\d{4})", text)
    if founded_match:
        result["founded_year"] = int(founded_match.group(1))

    # Location
    hq_match = re.search(
        r"(?:Headquarters|HQ|Based in)\s*(?:\sin\s+)?([A-Z][A-Za-z\s,]+?)(?:[,.]|\s+\d|$|\))",
        text,
    )
    if hq_match:
        result["hq_location"] = hq_match.group(1).strip().rstrip(",").strip()

    # Investors — look for notable investor names in text
    investor_prefixes = [
        r"(?:Backed by|Investors include|Notable investors?|Led by)\s*:?\s*([A-Z][A-Za-z\s,&.]+?)(?:[,.]|\s+and\s+)",
    ]
    investors = []
    for pat in investor_prefixes:
        for m in re.finditer(pat, text):
            names = re.split(r"\s*[,&]\s*", m.group(1))
            investors.extend(n.strip() for n in names if n.strip())
    if investors:
        result["notable_investors"] = investors[:5]

    return result


# ── Helpers ───────────────────────────────────────────────────────────────


def _fmt_funding(val: float) -> str:
    """Format a USD funding amount to human-readable."""
    if val >= 1e9:
        return f"${val/1e9:.1f}B"
    elif val >= 1e6:
        return f"${val/1e6:.0f}M"
    elif val >= 1e3:
        return f"${val/1e3:.0f}K"
    else:
        return f"${val:.0f}"



