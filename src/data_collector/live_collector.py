#!/usr/bin/env python3
"""
Live Data Connector for CIT (Company Intelligence Tool).

Two-path architecture:
  - Public company (has ticker): yfinance for financial statements, key metrics, price history
  - Private company (no ticker): web search + structured extraction (requests + BeautifulSoup)

Both paths return the same normalized schema so the reframing engine is path-agnostic.
"""

import json
import sys
import re
import argparse
from copy import deepcopy
from pathlib import Path
from datetime import datetime
from typing import Optional


# ── Schema ────────────────────────────────────────────────────────────────────

REPORT_SCHEMA = {
    "company_name": "",
    "as_of": "",
    "status": "",  # "public" or "private" or "not_found"
    "ticker": None,
    # Layer 1: What they say about themselves
    "self_description": {
        "tagline": "",
        "mission": "",
        "industry_positioning": "",
        "public_statements": [],
    },
    # Layer 2: What the data shows
    "core_data": {
        "sector": "",
        "industry": "",
        "hq_location": "",
        "employees": None,
        "founded_year": None,
        "description": "",
    },
    "financials": {
        "revenue": None,  # dict: {"2023": "1.2B", "2022": "1.0B"} or None
        "funding_total": None,  # private companies only
        "last_funding_round": None,
        "notable_investors": [],
    },
    "estimated_revenue": None,  # revenue estimate from sector benchmark engine
    "hiring_signal": None,  # hiring signal analysis (job count, growth velocity)
    "growth_signals": {
        "revenue_trend": "",
        "employee_trend": "",
        "recent_acquisitions": [],
        "expansion_indicators": [],  # new offices, new markets, product launches
    },
    "market_position": {
        "competitors": [],
        "market": "",
        "moat_description": "",
    },
    # Raw sources for traceability
    "_sources": [],
}


def empty_report(company_name: str) -> dict:
    report = deepcopy(REPORT_SCHEMA)
    report["company_name"] = company_name
    report["as_of"] = datetime.now().isoformat()
    report["_sources"] = []
    return report


# ── Public Path (yfinance) ────────────────────────────────────────────────────


def fetch_public_company(ticker: str) -> dict:
    """Fetch financial data for a public company using yfinance.

    Returns a REPORT_SCHEMA-shaped dict. All fields populate best-effort.
    Requires yfinance installed (pip install yfinance).
    """
    report = empty_report(ticker)
    report["status"] = "public"
    report["ticker"] = ticker.upper()

    try:
        import yfinance as yf
    except ImportError:
        report["_sources"].append(
            {"error": "yfinance not installed. Run: pip install yfinance"}
        )
        return report

    try:
        stock = yf.Ticker(ticker)
        info = stock.info
    except Exception as e:
        report["_sources"].append({"error": f"yfinance failed for {ticker}: {e}"})
        return report

    if not info or info.get("regularMarketPrice") is None and not info.get("longName"):
        report["_sources"].append(
            {"error": f"No data found for ticker {ticker}. Check symbol."}
        )
        report["status"] = "not_found"
        return report

    # ── Core data ──
    report["company_name"] = info.get("longName") or info.get("shortName") or ticker
    report["core_data"]["sector"] = info.get("sector") or ""
    report["core_data"]["industry"] = info.get("industry") or ""
    report["core_data"]["hq_location"] = (
        (
            f"{info.get('address1', '')}, {info.get('city', '')}, "
            f"{info.get('state', '')} {info.get('zip', '')}, {info.get('country', '')}"
        )
        .strip(", ")
        .strip()
    )
    report["core_data"]["employees"] = info.get("fullTimeEmployees")
    report["core_data"]["founded_year"] = _extract_year(info.get("founded", ""))
    report["core_data"]["description"] = info.get("longBusinessSummary", "")

    # ── Self-description from public sources ──
    website = info.get("website", "")
    report["self_description"]["tagline"] = info.get("companyTagline") or ""
    report["self_description"]["mission"] = ""
    report["self_description"]["industry_positioning"] = info.get("industryDisp", "")
    report["self_description"]["public_statements"] = [
        s
        for s in [
            website,
            info.get("companyDescription", ""),
        ]
        if s
    ]

    # ── Financials ──
    try:
        financials = stock.financials
        if financials is not None and not financials.empty:
            rev = {}
            if "Total Revenue" in financials.index:
                rev_series = financials.loc["Total Revenue"]
                for year, val in rev_series.items():
                    year_str = str(year.year) if hasattr(year, "year") else str(year)
                    rev[year_str] = _fmt_large(val)
            elif "Revenue" in financials.index:
                rev_series = financials.loc["Revenue"]
                for year, val in rev_series.items():
                    year_str = str(year.year) if hasattr(year, "year") else str(year)
                    rev[year_str] = _fmt_large(val)
            # Filter out NaN / invalid values
            rev = {k: v for k, v in rev.items() if v and v not in ("nan", "NaN", "N/A")}
            report["financials"]["revenue"] = rev if rev else None
    except Exception:
        pass  # financials may not be available for some tickers

    # Market cap as alternative revenue signal
    mcap = info.get("marketCap")
    if mcap and report["financials"]["revenue"] is None:
        report["financials"]["revenue"] = {"market_cap": _fmt_large(mcap)}

    # ── Growth signals ──
    try:
        hist = stock.history(period="2y")
        if hist is not None and not hist.empty:
            yearly = hist.resample("YE")["Close"].last()
            if len(yearly) >= 2:
                first = yearly.iloc[0]
                last = yearly.iloc[-1]
                pct = ((last - first) / first) * 100
                trend = "up" if pct > 5 else ("down" if pct < -5 else "stable")
                report["growth_signals"][
                    "revenue_trend"
                ] = f"Stock price {trend} over 2 years ({pct:+.1f}%)"
    except Exception:
        pass

    # Employee trend from company info
    # yfinance only gives current employees, but we note it
    if info.get("fullTimeEmployees"):
        report["growth_signals"][
            "employee_trend"
        ] = f"{info['fullTimeEmployees']:,} employees (current)"

    # ── Market position ──
    report["market_position"]["competitors"] = []
    report["market_position"]["market"] = info.get("industryDisp", "")
    report["market_position"]["moat_description"] = (
        info.get("marketCap", "")
        and f"Market cap: {_fmt_large(info.get('marketCap', 0))}"
        or ""
    )

    report["_sources"].append(
        {
            "source": "yfinance",
            "ticker": ticker,
            "fields": list(info.keys())[:30],  # sample of available fields
        }
    )

    return report


def _extract_year(val) -> Optional[int]:
    if isinstance(val, int):
        return val
    m = re.search(r"\b(19\d\d|20[0-2]\d)\b", str(val))
    return int(m.group(1)) if m else None


def _fmt_large(val) -> str:
    """Format large numbers like 1234567890 -> '1.23B'."""
    if val is None:
        return ""
    try:
        v = float(val)
    except (ValueError, TypeError):
        return str(val)
    if abs(v) >= 1e12:
        return f"{v / 1e12:.2f}T"
    elif abs(v) >= 1e9:
        return f"{v / 1e9:.2f}B"
    elif abs(v) >= 1e6:
        return f"{v / 1e6:.2f}M"
    elif abs(v) >= 1e3:
        return f"{v / 1e3:.2f}K"
    else:
        return f"{v:.2f}"


# ── Private Path (web search based) ──────────────────────────────────────────


def fetch_private_company(company_name: str) -> dict:
    """Fetch data for a private company using web search + structured extraction.

    Uses requests + basic HTML parsing to search Crunchbase and general web
    for company info. Falls back gracefully if sources are unreachable.
    Enriches with Wikipedia data, Google Knowledge Graph, and curated reference
    data when available.
    """
    report = empty_report(company_name)
    report["status"] = "private"

    # ── Knowledge Graph enrichment (fast, structured, no HTML parsing) ──
    _enrich_from_knowledge_graph(company_name, report)

    # ── Wikipedia enrichment (fast, structured, no HTML parsing) ──
    _enrich_from_wikipedia(company_name, report)

    # ── Curated reference data (gold-standard for known companies) ──
    _merge_reference_data(company_name, report)

    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        report["_sources"].append(
            {
                "error": "requests/bs4 not installed. Run: pip install requests beautifulsoup4"
            }
        )
        return report

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    safe_name = requests.utils.quote(company_name)

    # ── Crunchbase attempt ──
    cb_url = (
        f"https://www.crunchbase.com/organization/{safe_name.lower().replace(' ', '-')}"
    )
    try:
        resp = requests.get(cb_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)

            if not report["core_data"]["description"]:
                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc and meta_desc.get("content"):
                    report["core_data"]["description"] = meta_desc["content"]
                    report["self_description"]["industry_positioning"] = meta_desc[
                        "content"
                    ][:200]

            if not report["financials"]["funding_total"]:
                funding_patterns = [
                    r"(\$[\d,.]+[MBK]?)\s+(?:in\s+)?(?:Funding|Series [A-Z]|Seed|Venture)",
                    r"(?:Funding|Raised)\s*(?:of\s*)?(\$[\d,.]+[MBK]?)",
                    r"(?:Series [A-Z]|Seed)\s*(?:round\s*)?(?:of\s*)?(\$[\d,.]+[MBK]?)",
                ]
                for pat in funding_patterns:
                    m = re.search(pat, text, re.IGNORECASE)
                    if m:
                        report["financials"]["funding_total"] = m.group(1)
                        break

            report["_sources"].append({"source": "crunchbase", "url": cb_url})
    except Exception as e:
        report["_sources"].append({"source": "crunchbase", "error": str(e)})

    # ── Structured Crunchbase enrichment (funding, investors, categories) ──
    _enrich_from_crunchbase(company_name, report)

    # ── DuckDuckGo web search: general company data ──
    _duckduckgo_search(
        company_name, safe_name, report, headers,
        query=f"{safe_name}+company+funding+employees",
        source_label="duckduckgo (general)",
    )

    # ── DuckDuckGo web search: narrative / positioning (Layer 1) ──
    _duckduckgo_search(
        company_name, safe_name, report, headers,
        query=f"{safe_name}+about+mission+statement+company+positioning",
        source_label="duckduckgo (narrative)",
        extract_narrative=True,
    )

    # ── Hiring signal analysis (job postings, growth velocity) ──
    _enrich_hiring_signal(company_name, report)

    return report


def _enrich_from_knowledge_graph(company_name: str, report: dict) -> None:
    """Merge Google Knowledge Graph data into report — fills empty fields only.

    Knowledge Graph provides high-quality structured data including
    detailed descriptions (often positioning language), sector, and HQ.
    Gracefully skips if CIT_KNOWLEDGE_GRAPH_API_KEY is not set.
    """
    try:
        from .knowledge_graph import fetch_knowledge_graph

        kg = fetch_knowledge_graph(company_name)
        if not kg or kg.get("_not_found") or kg.get("_error"):
            return

        if kg.get("description") and not report["core_data"]["description"]:
            report["core_data"]["description"] = kg["description"]

        # Detailed description is richer — use for narrative / positioning
        detailed = kg.get("detailed_description", "")
        if detailed:
            if not report["self_description"]["industry_positioning"]:
                report["self_description"]["industry_positioning"] = detailed[:300]
            if not report["self_description"]["tagline"]:
                # First sentence works as a tagline
                first_sentence = detailed.split(".")[0].strip()
                if first_sentence and len(first_sentence) < 120:
                    report["self_description"]["tagline"] = first_sentence
            # Add as a public statement
            if detailed:
                report["self_description"]["public_statements"].append(detailed[:500])

        if kg.get("sector") and not report["core_data"]["sector"]:
            report["core_data"]["sector"] = kg["sector"]

        if kg.get("hq_location") and not report["core_data"]["hq_location"]:
            report["core_data"]["hq_location"] = kg["hq_location"]

        report["_sources"].append(
            {
                "source": "google_knowledge_graph",
                "matched_name": kg.get("_matched_name", ""),
                "url": kg.get("url", ""),
            }
        )
    except ImportError:
        pass  # knowledge_graph.py not available
    except Exception:
        pass


def _enrich_from_wikipedia(company_name: str, report: dict) -> None:
    """Merge Wikipedia data into report — only fills fields that are still empty."""
    try:
        from .wikipedia import fetch_company_data

        wiki = fetch_company_data(company_name)
        if not wiki:
            return

        if wiki.get("description") and not report["core_data"]["description"]:
            report["core_data"]["description"] = wiki["description"]

        if wiki.get("founded_year") and report["core_data"]["founded_year"] is None:
            report["core_data"]["founded_year"] = wiki["founded_year"]

        if wiki.get("hq_location") and not report["core_data"]["hq_location"]:
            report["core_data"]["hq_location"] = wiki["hq_location"]

        if wiki.get("employees") and report["core_data"]["employees"] is None:
            report["core_data"]["employees"] = wiki["employees"]

        if wiki.get("revenue_signal"):
            rev = wiki["revenue_signal"]
            if report["financials"]["revenue"] is None:
                report["financials"]["revenue"] = {"wikipedia_est": rev}

        if wiki.get("sector") and not report["core_data"]["sector"]:
            report["core_data"]["sector"] = wiki["sector"]

        for src in wiki.get("_sources", []):
            report["_sources"].append(src)
    except Exception:
        pass


def _merge_reference_data(company_name: str, report: dict) -> None:
    """Merge curated reference data into report for known companies.

    Reference data is gold-standard curated content for our 30 configured
    companies. Only fills fields that are still empty — never overwrites
    live-collected data.
    """
    try:
        from .reference import get_reference

        ref = get_reference(company_name)
        if not ref:
            return

        # Core data
        core = ref.get("core_data", {})
        for field in ("sector", "industry", "hq_location", "description"):
            if core.get(field) and not report["core_data"][field]:
                report["core_data"][field] = core[field]

        if core.get("employees") and report["core_data"]["employees"] is None:
            report["core_data"]["employees"] = core["employees"]

        if core.get("founded_year") and report["core_data"]["founded_year"] is None:
            report["core_data"]["founded_year"] = core["founded_year"]

        # Self-description (Layer 1)
        sd = ref.get("self_description", {})
        if sd.get("tagline") and not report["self_description"]["tagline"]:
            report["self_description"]["tagline"] = sd["tagline"]
        if sd.get("industry_positioning") and not report["self_description"]["industry_positioning"]:
            report["self_description"]["industry_positioning"] = sd["industry_positioning"]
        if sd.get("mission") and not report["self_description"]["mission"]:
            report["self_description"]["mission"] = sd["mission"]
        existing_statements = set(report["self_description"]["public_statements"])
        for stmt in sd.get("public_statements", []):
            if stmt not in existing_statements:
                report["self_description"]["public_statements"].append(stmt)
                existing_statements.add(stmt)

        # Financials
        fin = ref.get("financials", {})
        if fin.get("revenue") and report["financials"]["revenue"] is None:
            report["financials"]["revenue"] = fin["revenue"]
        if fin.get("funding_total") and not report["financials"]["funding_total"]:
            report["financials"]["funding_total"] = fin["funding_total"]
        if fin.get("last_funding_round") and not report["financials"]["last_funding_round"]:
            report["financials"]["last_funding_round"] = fin["last_funding_round"]
        for inv in fin.get("notable_investors", []):
            if inv not in report["financials"]["notable_investors"]:
                report["financials"]["notable_investors"].append(inv)

        # Growth signals
        gs = ref.get("growth_signals", {})
        if gs.get("revenue_trend") and not report["growth_signals"]["revenue_trend"]:
            report["growth_signals"]["revenue_trend"] = gs["revenue_trend"]
        if gs.get("employee_trend") and not report["growth_signals"]["employee_trend"]:
            report["growth_signals"]["employee_trend"] = gs["employee_trend"]
        for acq in gs.get("recent_acquisitions", []):
            if acq not in report["growth_signals"]["recent_acquisitions"]:
                report["growth_signals"]["recent_acquisitions"].append(acq)
        for exp in gs.get("expansion_indicators", []):
            if exp not in report["growth_signals"]["expansion_indicators"]:
                report["growth_signals"]["expansion_indicators"].append(exp)

        # Market position
        mp = ref.get("market_position", {})
        if mp.get("market") and not report["market_position"]["market"]:
            report["market_position"]["market"] = mp["market"]
        if mp.get("moat_description") and not report["market_position"]["moat_description"]:
            report["market_position"]["moat_description"] = mp["moat_description"]
        for comp in mp.get("competitors", []):
            if comp not in report["market_position"]["competitors"]:
                report["market_position"]["competitors"].append(comp)

        report["_sources"].append({"source": "reference", "note": "curated enrichment"})
    except (ImportError, Exception):
        pass


def _duckduckgo_search(
    company_name: str,
    safe_name: str,
    report: dict,
    headers: dict,
    query: str,
    source_label: str = "duckduckgo",
    extract_narrative: bool = False,
) -> None:
    """Run a DuckDuckGo search and extract data from results.

    Args:
        extract_narrative: If True, extracts narrative/positioning text
                          for Layer 1 self-description (tagline, mission, statements).
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        report["_sources"].append(
            {"source": source_label, "error": "requests/bs4 not installed"}
        )
        return

    search_url = f"https://html.duckduckgo.com/html/?q={query}"
    try:
        resp = requests.get(search_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return

        soup = BeautifulSoup(resp.text, "html.parser")
        snippets = soup.find_all("a", class_="result__a")
        results = []
        for a in snippets[:10]:
            results.append(a.get_text(strip=True))

        snippets_b = soup.find_all("a", class_="result__snippet")
        for s in snippets_b[:5]:
            results.append(s.get_text(strip=True))

        report["_sources"].append(
            {
                "source": source_label,
                "query": query.replace("+", " "),
                "results": results[:5],
            }
        )

        all_text = " ".join(results)

        if extract_narrative:
            # Extract narrative/positioning from search results
            if not report["self_description"]["tagline"]:
                # Look for a short, punchy description
                sentences = re.split(r"[.!?]", all_text)
                for s in sentences:
                    s = s.strip()
                    if 20 < len(s) < 120 and company_name.lower() in s.lower():
                        report["self_description"]["tagline"] = s
                        break

            if not report["self_description"]["industry_positioning"]:
                # First substantive paragraph mentioning the company
                paras = [r for r in results if company_name.lower() in r.lower() and len(r) > 80]
                if paras:
                    report["self_description"]["industry_positioning"] = paras[0][:300]

            # Add notable sentences as public statements
            for r in results:
                if company_name.lower() in r.lower() and len(r) > 60:
                    if r[:500] not in report["self_description"]["public_statements"]:
                        report["self_description"]["public_statements"].append(r[:500])
        else:
            # Extract structured data (employees, funding, HQ)
            if report["core_data"]["employees"] is None:
                emp_match = re.search(
                    r"(\d[\d,]*)\s*employees?", all_text, re.IGNORECASE
                )
                if emp_match:
                    report["core_data"]["employees"] = int(
                        emp_match.group(1).replace(",", "")
                    )

            if not report["financials"]["funding_total"]:
                fund_match = re.search(
                    r"(?:raised|funding|secured)\s*(?:a\s+)?(\$[\d,.]+[MBK]?)",
                    all_text,
                    re.IGNORECASE,
                )
                if fund_match:
                    report["financials"]["funding_total"] = fund_match.group(1)

            if not report["core_data"]["hq_location"]:
                hq_match = re.search(
                    r"(?:based in|headquarters|HQ)\s*(?:in\s+)?([A-Z][a-zA-Z\s,]+)",
                    all_text,
                )
                if hq_match:
                    report["core_data"]["hq_location"] = hq_match.group(1).strip()

    except Exception as e:
        report["_sources"].append({"source": source_label, "error": str(e)})


def _enrich_from_crunchbase(company_name: str, report: dict) -> None:
    """Merge Crunchbase data into report — funding, investors, core data.

    Uses the structured crunchbase module which tries API first, then
    falls back to public page scraping. Only fills empty fields.
    """
    try:
        from .crunchbase import fetch_crunchbase

        cb = fetch_crunchbase(company_name)
        if not cb or cb.get("_error"):
            return

        # Core data enrichment
        if cb.get("description") and not report["core_data"]["description"]:
            report["core_data"]["description"] = cb["description"]
        if cb.get("employees") and report["core_data"]["employees"] is None:
            report["core_data"]["employees"] = cb["employees"]
        if cb.get("founded_year") and report["core_data"]["founded_year"] is None:
            report["core_data"]["founded_year"] = cb["founded_year"]
        if cb.get("hq_location") and not report["core_data"]["hq_location"]:
            report["core_data"]["hq_location"] = cb["hq_location"]

        # Financials: funding
        if cb.get("funding_total") and not report["financials"]["funding_total"]:
            report["financials"]["funding_total"] = cb["funding_total"]
        if cb.get("last_funding_round") and not report["financials"]["last_funding_round"]:
            report["financials"]["last_funding_round"] = cb["last_funding_round"]
        if cb.get("total_funding_usd"):
            report["financials"]["_total_funding_usd"] = cb["total_funding_usd"]

        # Investors
        cb_investors = cb.get("notable_investors", [])
        if cb_investors:
            existing = report["financials"]["notable_investors"]
            for inv in cb_investors:
                if inv not in existing:
                    existing.append(inv)

        # Revenue estimate from Crunchbase
        if cb.get("estimated_revenue_range") and report["financials"]["revenue"] is None:
            report["financials"]["revenue"] = {"crunchbase_est": cb["estimated_revenue_range"]}

        # Categories -> sector hint
        categories = cb.get("categories", [])
        if categories and not report["core_data"]["sector"]:
            report["core_data"]["sector"] = categories[0]

        report["_sources"].append({
            "source": cb.get("_source", "crunchbase"),
            "matched_name": cb.get("_matched_name", ""),
        })
    except ImportError:
        pass  # crunchbase.py not available
    except Exception:
        pass


def _enrich_hiring_signal(company_name: str, report: dict) -> None:
    """Analyze hiring signal and add to report.

    Uses the structured hiring_signal module which searches job boards
    and estimates growth velocity from job posting volume.
    """
    try:
        from .hiring_signal import analyze_hiring_signal

        sector = report.get("core_data", {}).get("sector", "")
        employees = report.get("core_data", {}).get("employees")

        hs = analyze_hiring_signal(
            company_name,
            sector=sector,
            employee_count=employees,
        )
        if not hs or hs.get("job_count", 0) == 0:
            # No hiring signal — don't add noise
            return

        report["hiring_signal"] = hs

        # Merge growth estimate into growth_signals
        if hs.get("growth_estimate"):
            existing = report["growth_signals"]["employee_trend"]
            if existing:
                report["growth_signals"]["employee_trend"] = f"{existing}; {hs['growth_estimate']}"
            else:
                report["growth_signals"]["employee_trend"] = hs["growth_estimate"]

        report["_sources"].append({"source": "hiring_signal", "job_count": hs.get("job_count")})
    except ImportError:
        pass  # hiring_signal.py not available
    except Exception:
        pass


# ── Orchestrator ──────────────────────────────────────────────────────────────


def fetch_company(company_name: str, ticker: Optional[str] = None) -> dict:
    """Main entry point. Try public first (if ticker given or can be found),
    fall back to private path.

    Args:
        company_name: Company name to analyze
        ticker: Optional stock ticker. If given, skips public/private detection.
    """

    # If ticker explicitly provided, go straight to public path
    if ticker:
        return fetch_public_company(ticker)

    # Try to auto-detect: is this a known public company?
    # Try to auto-detect: is this a known public company?
    # We use yfinance — suppress stderr to avoid 404 noise for private cos
    try:
        import yfinance as yf
        import os, sys

        # Try the name as a ticker (for obvious cases like AAPL, MSFT)
        with open(os.devnull, "w") as devnull:
            old_stderr = sys.stderr
            sys.stderr = devnull
            try:
                test = yf.Ticker(company_name.upper())
                test_info = test.info
            finally:
                sys.stderr = old_stderr
        if test_info and test_info.get("longName"):
            result = fetch_public_company(company_name.upper())
            if result["status"] == "public" and result["core_data"]["description"]:
                result["_sources"].append(
                    {"note": f"Auto-detected ticker from name: {company_name.upper()}"}
                )
                return result
    except Exception:
        pass

    # Fall back to private path
    return fetch_private_company(company_name)


# ── CLI ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="CIT Live Data Connector — fetch company intelligence data"
    )
    parser.add_argument("company", help="Company name or stock ticker")
    parser.add_argument("--ticker", "-t", help="Stock ticker (skip auto-detect)")
    parser.add_argument("--output", "-o", help="Output file path (JSON)")
    parser.add_argument(
        "--pretty", "-p", action="store_true", help="Pretty-print to stdout"
    )

    args = parser.parse_args()

    report = fetch_company(args.company, ticker=args.ticker)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, default=str))
        print(f"Written to {out_path}")

    if args.pretty or not args.output:
        print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
