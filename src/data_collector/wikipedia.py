"""
Wikipedia data source for CIT.

Uses MediaWiki Action API to fetch company summaries and structured data.
Fills: description, founded_year, HQ, employees, revenue_signal, sector.
"""

from __future__ import annotations

import re
import time
from typing import Optional

WIKI_API = "https://en.wikipedia.org/w/api.php"


def fetch_company_data(company_name: str) -> dict:
    """Fetch structured company data from Wikipedia.

    Tries exact title first, then search. Handles disambiguation pages
    by searching for a qualified variant. Returns REPORT_SCHEMA-shaped subset.
    Returns empty dict on failure or rate-limit.
    """
    result: dict = {}
    headers = {"User-Agent": "CIT/0.2.0 (company-intelligence-tool)"}

    page_data = _query_page(company_name, headers)
    if not page_data:
        return result

    # Detect disambiguation page — search for a qualified variant
    if page_data.get("disambiguation"):
        qualified = _resolve_disambiguation(company_name, headers)
        if qualified:
            page_data = qualified
        else:
            return result

    extract = page_data.get("extract", "") or ""
    title = page_data.get("title", company_name)

    result["_sources"] = [
        {
            "source": "wikipedia",
            "title": title,
            "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
        }
    ]

    desc = page_data.get("description") or ""
    if desc:
        result["description"] = desc
    elif extract:
        result["description"] = extract[:300]

    _extract_structured_data(extract, result)

    return result


def _query_page(title: str, headers: dict) -> Optional[dict]:
    """Query a Wikipedia page by exact title. Returns page data or None."""
    params = {
        "action": "query",
        "titles": title,
        "prop": "extracts|pageprops",
        "exintro": True,
        "explaintext": True,
        "redirects": True,
        "format": "json",
    }

    try:
        import requests

        resp = requests.get(WIKI_API, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
    except Exception:
        return None

    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        if pid == "-1":
            continue
        return {
            "title": page.get("title", ""),
            "extract": page.get("extract", ""),
            "description": page.get("description", ""),
            "disambiguation": "disambiguation" in page.get("pageprops", {}),
        }
    return None


def _search_page(query: str, headers: dict) -> Optional[str]:
    """Search Wikipedia for the best page matching a query. Returns title or None."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 5,
    }
    try:
        import requests

        resp = requests.get(WIKI_API, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
    except Exception:
        return None

    pages = data.get("query", {}).get("search", [])
    if not pages:
        return None
    return pages[0].get("title")


def _resolve_disambiguation(company_name: str, headers: dict) -> Optional[dict]:
    """Try to find the right page when the first match is disambiguation."""
    # Try with " (company)" suffix
    for suffix in [" (company)", " (technology company)", ""]:
        candidate = _query_page(company_name + suffix, headers)
        if candidate and not candidate["disambiguation"] and candidate["extract"]:
            return candidate

    # Try broader search
    search_terms = [
        f"{company_name} company",
        f"{company_name} corporation",
    ]
    for term in search_terms:
        title = _search_page(term, headers)
        if title:
            candidate = _query_page(title, headers)
            if candidate and not candidate["disambiguation"] and candidate["extract"]:
                return candidate

    return None


def _extract_structured_data(extract: str, result: dict) -> None:
    """Parse founded year, HQ, employees, revenue from extract text."""
    if not extract:
        return

    text = extract[:2000]

    # Founded year
    m = re.search(
        r"(?:founded|established|incorporated)\s*(?:in\s*|on\s*)?"
        r"(?:\w+\s+)?(\d{4})",
        text,
        re.IGNORECASE,
    )
    if m:
        result["founded_year"] = int(m.group(1))

    # Headquarters
    m = re.search(
        r"(?:headquartered|based|headquarters)\s*(?:in\s*)?\s*"
        r"([A-Z][A-Za-z\s,]+?)(?:[,.]|\s+and|\s+\d|$|\))",
        text,
    )
    if m:
        result["hq_location"] = m.group(1).strip().rstrip(",").strip()

    # Employees
    m = re.search(r"([\d,]+)\s*\+?\s*employees?", text, re.IGNORECASE)
    if m:
        try:
            result["employees"] = int(m.group(1).replace(",", ""))
        except ValueError:
            pass

    # Revenue
    m = re.search(
        r"revenue\s+(?:of\s+)?"
        r"([$€£][\d,.]+\s*(?:[MBT]|million|billion|trillion)?"
        r"|€?[\d,.]+\s*(?:million|billion|trillion))",
        text,
        re.IGNORECASE,
    )
    if m:
        result["revenue_signal"] = m.group(0)

    # Sector detection from description
    sector_keywords = {
        "logistics": ["logistics", "supply chain", "freight", "shipping", "courier"],
        "technology": [
            "technology",
            "software",
            "saas",
            "cloud",
            "platform",
        ],
        "financial_services": [
            "financial",
            "fintech",
            "banking",
            "insurance",
            "payments",
        ],
        "manufacturing": ["manufacturing", "industrial", "factory", "production"],
        "healthcare": ["healthcare", "pharma", "medical", "biotech"],
        "consulting": ["consulting", "professional services", "advisory"],
        "retail": ["retail", "e-commerce", "ecommerce", "consumer"],
        "energy": ["energy", "oil", "gas", "renewable", "utility"],
    }
    text_lower = text.lower()
    for sector, kws in sector_keywords.items():
        if any(kw in text_lower for kw in kws):
            result["sector"] = sector.replace("_", " ").title()
            break

    if "sector" not in result and result.get("description"):
        # Use description as a fallback
        desc = result["description"]
        for sector, kws in sector_keywords.items():
            if any(kw in desc.lower() for kw in kws):
                result["sector"] = sector.replace("_", " ").title()
                break
