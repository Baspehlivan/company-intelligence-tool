"""
Google Knowledge Graph API — structured entity data for companies.

Fetches structured metadata (description, sector, HQ, detailed description,
logo) from Google's Knowledge Graph. Works for public and private companies.

Usage:
    from .knowledge_graph import fetch_knowledge_graph

    data = fetch_knowledge_graph("Rhenus")
    # -> {"description": "...", "sector": "...", ...} or {} on failure/no key

Requires: CIT_KNOWLEDGE_GRAPH_API_KEY env var (free via Google Cloud).
Without it, returns empty dict gracefully.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

CACHE_DIR = Path.home() / ".cit" / "cache" / "knowledge_graph"
CACHE_TTL = 604800  # 7 days (entity data is stable)

ENV_KEY = "CIT_KNOWLEDGE_GRAPH_API_KEY"
API_URL = "https://kgsearch.googleapis.com/v1/entities:search"


def _cache_path(query: str) -> Path:
    safe = "".join(c if c.isalnum() else "_" for c in query.lower().strip())[:80]
    return CACHE_DIR / f"{safe}.json"


def _load_cache(query: str) -> dict | None:
    path = _cache_path(query)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        age = time.time() - data.get("_cached_at", 0)
        if age < CACHE_TTL:
            return data.get("payload")
    except (json.JSONDecodeError, OSError):
        path.unlink(missing_ok=True)
    return None


def _save_cache(query: str, payload: dict) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {"payload": payload, "_cached_at": time.time()}
        _cache_path(query).write_text(json.dumps(data, default=str))
    except OSError:
        pass


def fetch_knowledge_graph(
    company_name: str, *, force_refetch: bool = False
) -> dict:
    """Fetch structured entity data from Google Knowledge Graph.

    Returns a REPORT_SCHEMA-compatible subset:
      - description: str
      - detailed_description: str (longer form, often includes positioning language)
      - sector: str (derived from @type)
      - hq_location: str (if in detailed description)
      - logo_url: str (if available)
      - _sources: list

    Returns empty dict if API key is not set, request fails, or entity not found.
    """
    key = os.environ.get(ENV_KEY)
    if not key:
        return {}  # Graceful degradation when no key configured

    query = company_name.strip()
    if not query:
        return {}

    if not force_refetch:
        cached = _load_cache(query)
        if cached is not None:
            return cached

    result = _query_api(query, key)
    _save_cache(query, result)
    return result


def _query_api(query: str, api_key: str) -> dict:
    """Call the Knowledge Graph Search API."""
    import requests

    params = {
        "query": query,
        "key": api_key,
        "limit": 3,
        "indent": True,
    }
    headers = {
        "User-Agent": "CIT/0.2.0 (company-intelligence-tool; knowledge-graph-enricher)",
    }

    try:
        resp = requests.get(
            API_URL, params=params, headers=headers, timeout=10
        )
        if resp.status_code == 403:
            return {"_error": "API key invalid or quota exceeded"}
        if resp.status_code != 200:
            return {"_error": f"HTTP {resp.status_code}"}

        data = resp.json()
    except requests.RequestException as e:
        return {"_error": str(e)}
    except ValueError as e:
        return {"_error": f"Invalid JSON response: {e}"}

    item_list = data.get("itemListElement", [])
    if not item_list:
        return {"_not_found": True}

    # Try to find the best matching entity (prefer Organization type)
    best = None
    for item in item_list:
        entity = item.get("result", {})
        types = [t.lower() for t in entity.get("@type", [])]
        if any(t in types for t in ("organization", "corporation", "ngo")):
            best = entity
            break

    if not best:
        best = item_list[0].get("result", {})

    if not best or not best.get("name"):
        return {"_not_found": True}

    result: dict = {
        "_source": "google_knowledge_graph",
        "_matched_name": best.get("name", ""),
    }

    # Description (short)
    desc = best.get("description", "")
    if desc:
        result["description"] = desc

    # Detailed description (longer, high-quality narrative)
    detailed = best.get("detailedDescription", {})
    article_body = detailed.get("articleBody", "")
    if article_body:
        result["detailed_description"] = article_body
        # Also extract potential HQ from detailed description
        import re
        hq_match = re.search(
            r"(?:headquartered|based|headquarters)\s*(?:in\s*)?\s*"
            r"([A-Z][A-Za-z\s,]+?)(?:[,.]|\s+and|\s+\d|$|\))",
            article_body,
        )
        if hq_match:
            result["hq_location"] = hq_match.group(1).strip().rstrip(",").strip()

    # Logo
    image = best.get("image", {})
    if isinstance(image, dict) and image.get("contentUrl"):
        result["logo_url"] = image["contentUrl"]

    # Entity type -> sector mapping
    types = best.get("@type", [])
    sector = _map_entity_type_to_sector(types)
    if sector:
        result["sector"] = sector

    # Knowledge panel URL
    url = best.get("url", "") or detailed.get("url", "")
    if url:
        result["url"] = url

    return result


def _map_entity_type_to_sector(types: list[str]) -> str:
    """Map Knowledge Graph entity types to CIT sector strings."""
    type_lower = set(t.lower() for t in types)

    # Direct type-to-sector mapping
    type_map = {
        "logisticscompany": "Logistics",
        "shippingcompany": "Logistics",
        "freightcompany": "Logistics",
        "airline": "Logistics",
        "softwarecompany": "Enterprise Software",
        "cloudcompany": "Enterprise Software",
        "saas": "Enterprise Software",
        "insurancecompany": "Financial Services",
        "bank": "Financial Services",
        "financialservice": "Financial Services",
        "financialorganization": "Financial Services",
        "consultingcompany": "Consulting",
        "consultingfirm": "Consulting",
        "manufacturingcompany": "Manufacturing",
        "industrialcompany": "Industrial",
        "technologycompany": "Technology",
        "retailcompany": "Retail",
        "ecommercecompany": "Retail",
        "energycompany": "Energy",
        "healthcarecompany": "Healthcare",
        "pharmaceuticalcompany": "Healthcare",
        "mediacompany": "Media",
        "telecommunicationscompany": "Telecommunications",
        "realestatecompany": "Real Estate",
        "constructioncompany": "Construction",
        "automotivecompany": "Automotive",
        "foodcompany": "Food & Beverage",
        "designcompany": "Design Software",
        "fintech": "Fintech",
        "mobilitycompany": "Mobility",
        "transportationcompany": "Logistics",
    }

    for t in type_lower:
        clean_t = t.replace(" ", "").replace("-", "").replace("_", "")
        if clean_t in type_map:
            return type_map[clean_t]

    # Broader fallback: keyword matching on combined types
    combined = " ".join(type_lower)
    broad_map = {
        "logistics": "Logistics",
        "freight": "Logistics",
        "software": "Enterprise Software",
        "cloud": "Enterprise Software",
        "saas": "Enterprise Software",
        "financ": "Financial Services",
        "bank": "Financial Services",
        "insurance": "Financial Services",
        "consult": "Consulting",
        "manufactur": "Manufacturing",
        "technolog": "Technology",
        "retail": "Retail",
        "ecommerce": "Retail",
        "energy": "Energy",
        "health": "Healthcare",
        "pharma": "Healthcare",
        "media": "Media",
        "telecom": "Telecommunications",
        "real estate": "Real Estate",
        "construct": "Construction",
        "automotive": "Automotive",
        "food": "Food & Beverage",
        "mobility": "Mobility",
        "transport": "Logistics",
    }
    for kw, sector in broad_map.items():
        if kw in combined:
            return sector

    return ""
