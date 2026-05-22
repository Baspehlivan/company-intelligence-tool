"""
SEC EDGAR XBRL financial data source for CIT.

Fetches real financial statements from 10-K filings via SEC's XBRL API.
No API key needed — free public data.

Returns: revenue, gross_profit, operating_income, net_income,
         total_assets, total_liabilities, operating_cash_flow,
         employees, and multi-year trends.
"""

from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import quote

SEC_HEADERS = {
    "User-Agent": "CIT/0.2.0 (company-intelligence-tool; pehlivan@example.com)",
    "Accept": "application/json",
}

CACHE_DIR = Path.home() / ".cit" / "cache" / "edgar"
CACHE_TTL = 86400  # 24 hours


def _cache_path(cik_padded: str) -> Path:
    return CACHE_DIR / f"{cik_padded}.json"


def _load_cache(cik_padded: str) -> dict | None:
    path = _cache_path(cik_padded)
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


def _save_cache(cik_padded: str, payload: dict) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {"payload": payload, "_cached_at": time.time()}
        _cache_path(cik_padded).write_text(json.dumps(data, default=str))
    except OSError:
        pass


def fetch_financials(ticker: str, *, force_refetch: bool = False) -> dict:
    """Fetch financial data from SEC EDGAR for a public company, with cache.

    Returns a dict with keys:
      - company_name, ticker, cik
      - revenue: {year: value, ...}
      - gross_profit: {year: value, ...}
      - operating_income: {year: value, ...}
      - net_income: {year: value, ...}
      - total_assets, total_liabilities, stockholders_equity
      - operating_cash_flow
      - employees
      - revenue_growth: {year: pct, ...}
      - gross_margin, operating_margin, net_margin
      - enterprise_value, market_cap, pe_ratio, ev_revenue, ev_ebitda (via yfinance)
      - as_of: date string
      - _status: "ok" | "not_found" | "error"
    """
    import requests

    result: dict = {
        "ticker": ticker.upper(),
        "as_of": datetime.now().isoformat(),
        "_status": "ok",
    }

    cik = _lookup_cik(ticker.upper())
    if not cik:
        result["_status"] = "not_found"
        result["_error"] = f"No CIK found for ticker {ticker}"
        return result

    result["cik"] = cik
    cik_padded = str(cik).zfill(10)

    # Check cache
    if not force_refetch:
        cached = _load_cache(cik_padded)
        if cached is not None:
            cached["_status"] = "ok"
            cached["_from_cache"] = True
            return cached

    facts = _fetch_company_facts(cik_padded)
    if not facts:
        result["_status"] = "error"
        result["_error"] = f"Failed to fetch XBRL facts for CIK {cik_padded}"
        return result

    us_gaap = facts.get("facts", {}).get("us-gaap", {})
    if not us_gaap:
        if_rs = facts.get("facts", {}).get("ifrs-full", {})
        if if_rs:
            us_gaap = if_rs

    result["company_name"] = facts.get("entityName", "")

    us_gaap = _fix_keys(us_gaap)

    _extract_metric(us_gaap, "RevenueFromContractWithCustomerExcludingAssessedTax", "revenue", result)
    _extract_metric(us_gaap, "Revenues", "revenue", result, merge=True)
    _extract_metric(us_gaap, "RevenueFromContractWithCustomerExcludingAssessedTax", "revenue_asc606", result)
    _extract_metric(us_gaap, "GrossProfit", "gross_profit", result)
    _extract_metric(us_gaap, "OperatingIncomeLoss", "operating_income", result)
    _extract_metric(us_gaap, "IncomeLossFromContinuingOperationsBeforeIncomeTaxExpenseBenefit", "pretax_income", result)
    _extract_metric(us_gaap, "NetIncomeLoss", "net_income", result)
    _extract_metric(us_gaap, "Assets", "total_assets", result)
    _extract_metric(us_gaap, "Liabilities", "total_liabilities", result)
    _extract_metric(us_gaap, "StockholdersEquity", "stockholders_equity", result)
    _extract_metric(us_gaap, "OperatingCashFlow", "operating_cash_flow", result)
    _extract_metric(us_gaap, "NetCashProvidedByUsedInOperatingActivities", "operating_cash_flow", result, merge=True)
    _extract_metric(us_gaap, "SellingGeneralAndAdministrativeExpense", "sg_and_a", result)
    _extract_metric(us_gaap, "ResearchAndDevelopmentExpense", "rd_expense", result)
    _extract_metric(us_gaap, "EmployeeRelatedExpenses", "employee_expense", result)
    _extract_employee_count(us_gaap, result)

    _compute_ratios(result)

    # Enrich with market data (non-blocking, best-effort)
    try:
        from .market import fetch_market_data
        market = fetch_market_data(ticker.upper())
        if market and market.get("_status") == "ok":
            for mk in ("market_cap", "enterprise_value", "pe_ratio", "ev_revenue", "ev_ebitda", "price"):
                if mk in market:
                    result[mk] = market[mk]
        elif market and market.get("_error"):
            result.setdefault("_warnings", []).append(f"market: {market['_error']}")
    except ImportError:
        result.setdefault("_warnings", []).append("market: yfinance not installed (pip install yfinance)")
    except Exception as e:
        result.setdefault("_warnings", []).append(f"market: {e}")

    _save_cache(cik_padded, result)
    return result


def _lookup_cik(ticker: str) -> Optional[int]:
    """Lookup CIK number from stock ticker via SEC's ticker-to-CIK mapping."""
    import requests

    url = "https://www.sec.gov/files/company_tickers.json"
    try:
        resp = requests.get(url, headers=SEC_HEADERS, timeout=15)
        if resp.status_code != 200:
            return None
        mapping = resp.json()
        for entry in mapping.values():
            if entry.get("ticker", "").upper() == ticker.upper():
                return int(entry["cik_str"])
    except Exception:
        pass
    return None


def _fetch_company_facts(cik_padded: str) -> Optional[dict]:
    """Fetch all XBRL facts for a company from SEC EDGAR."""
    import requests

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
    try:
        resp = requests.get(url, headers=SEC_HEADERS, timeout=20)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def _fix_keys(us_gaap: dict) -> dict:
    """SEC API sometimes uses lowercase keys — normalize."""
    if not us_gaap:
        return us_gaap
    # Check if keys look wrong (all lowercase)
    sample = next(iter(us_gaap.keys()), "")
    if sample and sample[0].islower():
        fixed = {}
        for k, v in us_gaap.items():
            fixed[_normalize_gaap_key(k)] = v
        return fixed
    return us_gaap


def _normalize_gaap_key(key: str) -> str:
    """Try to normalize a lowercase GAAP key to the proper camelCase."""
    # Common mappings for lowercase keys
    mapping = {
        "revenuefromcontractwithcustomerexcludingassessedtax": "RevenueFromContractWithCustomerExcludingAssessedTax",
        "revenues": "RevenueFromContractWithCustomerExcludingAssessedTax",
        "grossprofit": "GrossProfit",
        "operatingincomeloss": "OperatingIncomeLoss",
        "netincomeloss": "NetIncomeLoss",
        "assets": "Assets",
        "liabilities": "Liabilities",
        "stockholdersequity": "StockholdersEquity",
        "operatingcashflow": "NetCashProvidedByUsedInOperatingActivities",
        "sellinggeneralandadministrativeexpense": "SellingGeneralAndAdministrativeExpense",
        "researchanddevelopmentexpense": "ResearchAndDevelopmentExpense",
    }
    return mapping.get(key.lower(), key)


def _extract_metric(us_gaap: dict, gaap_key: str, output_key: str, result: dict, merge: bool = False) -> None:
    """Extract a financial metric from XBRL data, taking the most recent fiscal years.

    If merge=True, fills gaps in an already-extracted dict (for multi-taxonomy support).
    """
    concept = us_gaap.get(gaap_key)
    if not concept:
        return

    units = concept.get("units", {})
    for unit_key in ("USD", "EUR", "GBP", "CHF", "SEK", "NOK", "DKK"):
        values = units.get(unit_key)
        if values:
            break
    else:
        for vals in units.values():
            values = vals
            break

    if not values:
        return

    # Filter to FY entries only and sort by end date descending
    annually = [
        v for v in values
        if v.get("fp") == "FY" and (not v.get("frame") or "Q" not in v.get("frame", ""))
    ]
    if not annually:
        annually = sorted(values, key=lambda x: x.get("end", ""), reverse=True)

    annually.sort(key=lambda x: x.get("end", ""), reverse=True)

    # Deduplicate by year — prefer entries with frame= (confirmed annual)
    # over entries without frame (may be corrected values)
    by_year: dict[str, float] = {}
    seen_dates: set[str] = set()
    for v in annually:
        end = v.get("end", "")
        year = end[:4] if len(end) >= 4 else ""
        if not year or not year.isdigit():
            continue
        # Skip if we already have this exact date value
        date_val = f"{end}_{v.get('val', '')}"
        if date_val in seen_dates:
            continue
        seen_dates.add(date_val)
        val = _parse_xbrl_value(v)
        if val is not None:
            # Prefer frame-qualified values over unqualified
            has_frame = bool(v.get("frame"))
            if year not in by_year or has_frame:
                by_year[year] = val

    if not by_year:
        return

    sorted_data = dict(sorted(by_year.items()))

    if merge and output_key in result and isinstance(result[output_key], dict):
        # Merge: don't overwrite existing years, only fill gaps
        existing = result[output_key]
        for y, v in sorted_data.items():
            if y not in existing:
                existing[y] = v
        result[output_key] = dict(sorted(existing.items()))
    else:
        result[output_key] = sorted_data


def _extract_employee_count(us_gaap: dict, result: dict) -> None:
    """Extract employee count from XBRL."""
    for key in ("EmployeeRelatedExpenses", "RevenueFromContractWithCustomerExcludingAssessedTax"):
        pass

    # Try common employee count concepts
    for gaap_key in ("EmployeeRelatedExpenses", "ShareBasedCompensation", "RevenueFromContractWithCustomerExcludingAssessedTax"):
        pass

    concept = us_gaap.get("EmployeeRelatedExpenses")
    if not concept:
        return

    units = concept.get("units", {})
    for vals in units.values():
        for v in vals:
            if v.get("fp") == "FY":
                val = _parse_xbrl_value(v)
                if val is not None and val > 1000:  # likely headcount, not annual expense
                    result["employees"] = int(val)
                    return

    # Try to find employee count from other fields or use revenue/employee proxy
    concept = us_gaap.get("RevenueFromContractWithCustomerExcludingAssessedTax")
    if not concept:
        concept = us_gaap.get("Revenues")
    if concept:
        units = concept.get("units", {})
        for vals in units.values():
            for v in vals:
                if "EmployeeNumber" in str(v.get("accn", "")):
                    val = _parse_xbrl_value(v)
                    if val:
                        result["employees"] = int(val)
                        return


def _parse_xbrl_value(v: dict) -> Optional[float]:
    """Parse an XBRL value safely."""
    val = v.get("val")
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _compute_ratios(result: dict) -> None:
    """Compute financial ratios from raw data."""
    revenue = result.get("revenue", {})
    years = sorted(revenue.keys())

    # Revenue growth
    growth = {}
    for i in range(1, len(years)):
        prev = float(revenue.get(str(years[i - 1]), 0))
        curr = float(revenue.get(str(years[i]), 0))
        if prev and curr:
            growth[str(years[i])] = round((curr - prev) / prev * 100, 1)
    if growth:
        result["revenue_growth"] = growth

    # Margins
    gross = result.get("gross_profit", {})
    operating = result.get("operating_income", {})
    net = result.get("net_income", {})

    for year in years:
        rev = float(revenue.get(year, 0))
        if rev == 0:
            continue
        if year in gross:
            result.setdefault("gross_margin", {})[year] = round(float(gross[year]) / rev * 100, 1)
        if year in operating:
            result.setdefault("operating_margin", {})[year] = round(float(operating[year]) / rev * 100, 1)
        if year in net:
            result.setdefault("net_margin", {})[year] = round(float(net[year]) / rev * 100, 1)

    # Revenue per employee
    employees = result.get("employees")
    latest_rev_year = years[-1] if years else None
    if employees and latest_rev_year and latest_rev_year in revenue:
        rev_val = float(revenue[latest_rev_year])
        if rev_val and employees:
            result["revenue_per_employee"] = round(rev_val / employees, 0)

    # R&D as % of revenue
    rd = result.get("rd_expense", {})
    for year in years:
        rev_val = float(revenue.get(year, 0))
        rd_val = float(rd.get(year, 0))
        if rev_val and rd_val:
            result.setdefault("rd_pct", {})[year] = round(rd_val / rev_val * 100, 1)

    # SG&A as % of revenue
    sga = result.get("sg_and_a", {})
    for year in years:
        rev_val = float(revenue.get(year, 0))
        sga_val = float(sga.get(year, 0))
        if rev_val and sga_val:
            result.setdefault("sg_a_pct", {})[year] = round(sga_val / rev_val * 100, 1)


def format_financial_summary(edgar_data: dict) -> str:
    """Format EDGAR financial data into a readable summary string.
    Shows only the most recent 5 consistent fiscal years."""
    if not edgar_data.get("revenue"):
        return ""

    lines = []
    ticker = edgar_data.get("ticker", "")
    rev = edgar_data.get("revenue", {})
    years = sorted(rev.keys())

    # Only show last 5 years to avoid erratic pre-standardization data
    display_years = years[-5:] if len(years) > 5 else years
    if not display_years:
        return ""

    lines.append(f'SEC EDGAR ({ticker}):')
    rev_str = '; '.join(f'{y}=${_fmt(rev[y])}' for y in display_years)
    lines.append(f'  Revenue: {rev_str}')

    growth = edgar_data.get("revenue_growth", {})
    if growth:
        valid = [y for y in display_years if y in growth and abs(growth[y]) < 100]
        if valid:
            g_str = '; '.join(f'{y}={growth[y]:+.1f}%' for y in valid)
            lines.append(f'  Growth: {g_str}')

    for label, key in [("Gross margin", "gross_margin"), ("Operating margin", "operating_margin"), ("Net margin", "net_margin")]:
        margin = edgar_data.get(key, {})
        valid = [y for y in display_years if y in margin and 0 <= margin[y] <= 100]
        if valid:
            m_str = '; '.join(f'{y}={margin[y]:.1f}%' for y in valid)
            lines.append(f'  {label}: {m_str}')

    rpe = edgar_data.get("revenue_per_employee")
    if rpe:
        lines.append(f'  Revenue/employee: ${rpe:,.0f}')

    rd = edgar_data.get("rd_pct", {})
    valid_rd = [y for y in display_years if y in rd and 0 <= rd[y] <= 100]
    if valid_rd:
        rd_str = '; '.join(f'{y}={rd[y]:.1f}%' for y in valid_rd)
        lines.append(f'  R&D % revenue: {rd_str}')

    return '<br>'.join(lines)


def _fmt(val) -> str:
    try:
        v = float(val)
    except (ValueError, TypeError):
        return str(val)
    if abs(v) >= 1e12:
        return f"{v/1e12:.2f}T"
    elif abs(v) >= 1e9:
        return f"{v/1e9:.2f}B"
    elif abs(v) >= 1e6:
        return f"{v/1e6:.2f}M"
    elif abs(v) >= 1e3:
        return f"{v/1e3:.1f}K"
    else:
        return f"{v:.2f}"
