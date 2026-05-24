"""
Hiring signal analyzer for CIT — detects growth trajectory from job posting volume.

Three signals:
  1. Web search — counts job posting results via DuckDuckGo search
  2. Estimated growth velocity — job count × company size heuristic
  3. Trend direction — compares against typical ratios for growth stages

No API key needed. Uses public web search only.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Optional

CACHE_DIR = Path.home() / ".cit" / "cache" / "hiring"
CACHE_TTL = 43200  # 12 hours (job counts change quickly)


def _cache_path(company_name: str) -> Path:
    safe = "".join(c if c.isalnum() else "_" for c in company_name.lower().strip())[:50]
    return CACHE_DIR / f"{safe}.json"


def _load_cache(company_name: str) -> dict | None:
    path = _cache_path(company_name)
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


def _save_cache(company_name: str, payload: dict) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {"payload": payload, "_cached_at": time.time()}
        _cache_path(company_name).write_text(json.dumps(data, default=str))
    except OSError:
        pass


def analyze_hiring_signal(
    company_name: str,
    sector: Optional[str] = None,
    employee_count: Optional[int] = None,
    *,
    force_refetch: bool = False,
) -> dict:
    """Analyze hiring activity for a company.

    Returns:
        dict with keys:
          - job_count: int (estimated number of open positions)
          - job_urls: list[str] (sample of job listing URLs found)
          - hiring_velocity: str ("high" | "medium" | "low" | "unknown")
          - hiring_trend: str ("growing" | "stable" | "contracting" | "unknown")
          - growth_estimate: str (human-readable, e.g. "Rapidly growing (50+ openings)")
          - employee_job_ratio: float | None (jobs per employee — growth indicator)
          - primary_source: str ("linkedin" | "indeed" | "duckduckgo")
          - _sources: list
    """
    if not force_refetch:
        cached = _load_cache(company_name)
        if cached is not None:
            return cached

    result = _collect_hiring_signals(company_name, sector, employee_count)
    _save_cache(company_name, result)
    return result


def _collect_hiring_signals(
    company_name: str,
    sector: Optional[str],
    employee_count: Optional[int],
) -> dict:
    """Collect hiring signals from multiple sources."""
    result: dict = {
        "job_count": 0,
        "job_urls": [],
        "hiring_velocity": "unknown",
        "hiring_trend": "unknown",
        "growth_estimate": "",
        "employee_job_ratio": None,
        "primary_source": "",
        "_sources": [],
    }

    # 1. Try DuckDuckGo search for "X jobs career"
    ddg_jobs = _search_jobs_ddg(company_name)
    if ddg_jobs:
        result["job_count"] += ddg_jobs.get("count", 0)
        result["job_urls"].extend(ddg_jobs.get("urls", []))
        result["_sources"].append(ddg_jobs.get("_source", "duckduckgo_jobs"))

    # 2. Try LinkedIn jobs search
    linkedin_jobs = _search_jobs_linkedin(company_name)
    if linkedin_jobs:
        result["job_count"] += linkedin_jobs.get("count", 0)
        result["job_urls"].extend(linkedin_jobs.get("urls", []))
        result["_sources"].append(linkedin_jobs.get("_source", "web_jobs"))

    # Deduplicate URLs
    seen = set()
    unique_urls = []
    for url in result["job_urls"]:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    result["job_urls"] = unique_urls[:10]

    # Compute signals
    _compute_hiring_metrics(result, company_name, employee_count)

    return result


def _search_jobs_ddg(company_name: str) -> dict | None:
    """Search DuckDuckGo for job listings at this company."""
    import requests
    from bs4 import BeautifulSoup

    safe = _url_safe(company_name)
    query = f"{safe}+jobs+careers+hiring"
    url = f"https://html.duckduckgo.com/html/?q={query}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None
    except requests.RequestException:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    links = soup.find_all("a", class_="result__a")

    # Look for job board / career page links
    job_urls = []
    job_keywords = [
        "jobs", "careers", "linkedin.com/jobs", "indeed.com",
        "glassdoor.com", "stepstone", "monster.com",
        "arbeitnow", "xing.com/jobs",
    ]

    for a in links:
        href = a.get("href", "")
        text = a.get_text(strip=True).lower()
        # Check link text and URL for job-related keywords
        if any(kw in text or kw in href.lower() for kw in job_keywords):
            job_urls.append(href)

    # Also count job listing aggregator mentions in snippets
    snippets = soup.find_all("a", class_="result__snippet")
    job_count_indicators = 0
    for s in snippets:
        text = s.get_text(strip=True)
        # Look for patterns like "50+ jobs", "30 open positions"
        counts = re.findall(r"(\d+)\+?\s*(?:jobs|openings|positions|vacancies)", text, re.IGNORECASE)
        if counts:
            try:
                job_count_indicators += max(int(c) for c in counts)
            except ValueError:
                pass

    if not job_urls and not job_count_indicators:
        return None

    return {
        "count": max(job_count_indicators, len(job_urls)),
        "urls": job_urls[:8],
        "_source": {"source": "duckduckgo_jobs", "query": query},
    }


def _search_jobs_linkedin(company_name: str) -> dict | None:
    """Try to find job count via job board search queries."""
    import requests
    from bs4 import BeautifulSoup

    safe = _url_safe(company_name)

    # Try LinkedIn jobs search (public page)
    linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={safe}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    job_urls = [linkedin_url]
    count = 0

    try:
        resp = requests.get(linkedin_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)

            # LinkedIn shows "X results" at the top
            result_match = re.search(r"(\d[\d,]*)\+?\s*(?:results?|jobs?|openings?)", text, re.IGNORECASE)
            if result_match:
                try:
                    count = int(result_match.group(1).replace(",", ""))
                except ValueError:
                    pass

    except requests.RequestException:
        pass

    if count == 0:
        # Give a small default if we found the page
        return None

    return {
        "count": count,
        "urls": job_urls,
        "_source": {"source": "linkedin_jobs", "url": linkedin_url},
    }


def _compute_hiring_metrics(
    result: dict,
    company_name: str,
    employee_count: Optional[int],
) -> None:
    """Compute hiring velocity and trend from raw signals."""
    job_count = result["job_count"]

    if job_count == 0:
        result["hiring_velocity"] = "unknown"
        result["hiring_trend"] = "unknown"
        result["growth_estimate"] = "No hiring signal detected"
        return

    # Compute employee:job ratio
    if employee_count and employee_count > 0:
        ratio = employee_count / job_count
        result["employee_job_ratio"] = round(ratio, 1)

        # Hiring velocity based on ratio:
        # < 10 employees per job opening = rapid hiring
        # 10-50 = moderate
        # > 50 = slow/stable
        if ratio < 10:
            result["hiring_velocity"] = "high"
            result["hiring_trend"] = "growing"
            result["growth_estimate"] = f"Rapidly growing ({job_count}+ open positions, ~1 per {ratio:.0f} employees)"
        elif ratio < 50:
            result["hiring_velocity"] = "medium"
            result["hiring_trend"] = "growing"
            result["growth_estimate"] = f"Growing ({job_count}+ open positions, ~1 per {ratio:.0f} employees)"
        elif ratio < 200:
            result["hiring_velocity"] = "low"
            result["hiring_trend"] = "stable"
            result["growth_estimate"] = f"Stable hiring ({job_count}+ open positions)"
        else:
            result["hiring_velocity"] = "low"
            result["hiring_trend"] = "contracting"
            result["growth_estimate"] = f"Minimal hiring relative to size ({job_count}+ open positions)"
    else:
        # No employee count — use absolute job count
        if job_count > 100:
            result["hiring_velocity"] = "high"
            result["hiring_trend"] = "growing"
            result["growth_estimate"] = f"Active hiring (100+ open positions detected)"
        elif job_count > 20:
            result["hiring_velocity"] = "medium"
            result["hiring_trend"] = "growing"
            result["growth_estimate"] = f"Moderate hiring ({job_count} open positions)"
        elif job_count > 5:
            result["hiring_velocity"] = "low"
            result["hiring_trend"] = "stable"
            result["growth_estimate"] = f"Selective hiring ({job_count} open positions)"
        else:
            result["hiring_velocity"] = "low"
            result["hiring_trend"] = "stable"
            result["growth_estimate"] = f"Minimal hiring detected"


def _url_safe(s: str) -> str:
    """URL-safe search query string."""
    import requests as _r
    return _r.utils.quote(s)
