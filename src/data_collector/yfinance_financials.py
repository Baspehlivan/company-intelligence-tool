"""
yfinance financial data source for non-US public companies.

Mirrors the EDGAR format (revenue, margins, ratios) but uses
yfinance's financial statements instead of SEC XBRL.

Works for: .DE, .SW, .CO, .L, .PA, and other non-US exchange tickers.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import time
from typing import Optional

CACHE_DIR = Path.home() / ".cit" / "cache" / "yfinance_fin"
CACHE_TTL = 86400  # 24 hours


def _cache_path(ticker: str) -> Path:
    return CACHE_DIR / f"{ticker.upper()}.json"


def _load_cache(ticker: str) -> dict | None:
    path = _cache_path(ticker)
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


def _save_cache(ticker: str, payload: dict) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {"payload": payload, "_cached_at": time.time()}
        _cache_path(ticker).write_text(json.dumps(data, default=str))
    except OSError:
        pass


def fetch_yfinance_financials(ticker: str, *, force_refetch: bool = False) -> dict:
    """Fetch financial statements from yfinance for a non-US public company.

    Returns EDGAR-compatible dict with:
      - company_name, ticker, currency
      - revenue: {year: value, ...}
      - gross_profit, operating_income, net_income
      - revenue_growth, gross_margin, operating_margin, net_margin
      - rd_expense, sg_and_a
      - total_assets, total_liabilities
      - _status: "ok" | "not_found" | "error"
    """
    if not force_refetch:
        cached = _load_cache(ticker)
        if cached is not None:
            return cached

    result: dict = {
        "ticker": ticker.upper(),
        "as_of": datetime.now().isoformat(),
        "_status": "ok",
    }

    try:
        import yfinance as yf
    except ImportError:
        result["_status"] = "error"
        result["_error"] = "yfinance not installed"
        return result

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Try info-based financials first (simpler)
        currency = info.get("currency", "USD")
        result["company_name"] = info.get("longName") or info.get("shortName") or ticker
        result["currency"] = currency

        # Use annual financial statements
        fin = stock.financials
        bs = stock.balance_sheet

        if fin is None or fin.empty:
            result["_status"] = "not_found"
            result["_error"] = f"No financial data for {ticker}"
            return result

        # Extract annual data (columns are dates)
        years = sorted(fin.columns.year)

        def _extract_row(row_name: str) -> dict:
            """Extract a row from financials by name match."""
            for idx_name in fin.index:
                if row_name.lower() in str(idx_name).lower():
                    values = {}
                    for col in fin.columns:
                        val = fin.loc[idx_name, col]
                        if val is not None and not (isinstance(val, float) and val != val):
                            values[str(col.year)] = float(val)
                    if values:
                        return values
            return {}

        def _extract_bs(row_name: str) -> dict:
            """Extract a row from balance sheet by name match."""
            if bs is None or bs.empty:
                return {}
            for idx_name in bs.index:
                if row_name.lower() in str(idx_name).lower():
                    values = {}
                    for col in bs.columns:
                        val = bs.loc[idx_name, col]
                        if val is not None and not (isinstance(val, float) and val != val):
                            values[str(col.year)] = float(val)
                    if values:
                        return values
            return {}

        # Revenue — try multiple names
        rev = _extract_row("Total Revenue")
        if not rev:
            rev = _extract_row("Revenue")
        if not rev:
            rev = _extract_row("Sales")
        if rev:
            result["revenue"] = rev

            # Growth rates
            years_sorted = sorted(rev.keys())
            growth = {}
            for i in range(1, len(years_sorted)):
                prev = float(rev.get(years_sorted[i-1], 0))
                curr = float(rev.get(years_sorted[i], 0))
                if prev and curr:
                    growth[years_sorted[i]] = round((curr - prev) / prev * 100, 1)
            if growth:
                result["revenue_growth"] = growth

        # Profit metrics
        gp = _extract_row("Gross Profit")
        if gp:
            result["gross_profit"] = gp
        oi = _extract_row("Operating Income")
        if not oi:
            oi = _extract_row("Operating Income Loss")
        if oi:
            result["operating_income"] = oi
        ni = _extract_row("Net Income")
        if not ni:
            ni = _extract_row("Net Income Common")
        if ni:
            result["net_income"] = ni

        # Expenses
        rd = _extract_row("Research And Development")
        if rd:
            result["rd_expense"] = rd
        sga = _extract_row("Selling General And Administrative")
        if sga:
            result["sg_and_a"] = sga
        if not sga:
            sga_total = _extract_row("Selling And Marketing Expense")
            if sga_total:
                result["sg_and_a"] = sga_total

        # Balance sheet
        assets = _extract_bs("Total Assets")
        if assets:
            result["total_assets"] = assets
        liabilities = _extract_bs("Total Liabilities Net Minority Interest")
        if not liabilities:
            liabilities = _extract_bs("Total Liabilities")
        if liabilities:
            result["total_liabilities"] = liabilities
        equity = _extract_bs("Stockholders Equity")
        if not equity:
            equity = _extract_bs("Total Equity")
        if equity:
            result["stockholders_equity"] = equity

        # Compute ratios
        _compute_ratios(result)

        # Enrich with market data
        if info.get("marketCap"):
            result["market_cap"] = info["marketCap"]
            result["enterprise_value"] = info.get("enterpriseValue")
            result["pe_ratio"] = info.get("trailingPE")
            result["price"] = info.get("currentPrice") or info.get("regularMarketPrice")
            rev_ttm = info.get("totalRevenue")
            ev = info.get("enterpriseValue")
            ebitda = info.get("ebitda")
            if ev and rev_ttm:
                result["ev_revenue"] = round(ev / rev_ttm, 2)
            if ev and ebitda and ebitda > 0:
                result["ev_ebitda"] = round(ev / ebitda, 2)

        _save_cache(ticker, result)

    except Exception as e:
        result["_status"] = "error"
        result["_error"] = str(e)

    return result


def _compute_ratios(result: dict) -> None:
    """Compute margins from extracted data."""
    revenue = result.get("revenue", {})
    if not revenue:
        return
    years = sorted(revenue.keys())

    for label, key in [("gross_margin", "gross_profit"), ("operating_margin", "operating_income"),
                        ("net_margin", "net_income")]:
        data = result.get(key, {})
        for y in years:
            rev = float(revenue.get(y, 0))
            val = float(data.get(y, 0))
            if rev and val:
                result.setdefault(label, {})[y] = round(val / rev * 100, 1)

    # R&D and SG&A as % of revenue
    for label, key in [("rd_pct", "rd_expense"), ("sg_a_pct", "sg_and_a")]:
        data = result.get(key, {})
        for y in years:
            rev = float(revenue.get(y, 0))
            val = float(data.get(y, 0))
            if rev and val:
                result.setdefault(label, {})[y] = round(val / rev * 100, 1)


def format_yfinance_summary(data: dict) -> str:
    """Format yfinance financial data into readable summary (EDGAR-compatible)."""
    if not data.get("revenue"):
        return ""

    lines = []
    ticker = data.get("ticker", "")
    currency = data.get("currency", "USD")
    rev = data.get("revenue", {})
    years = sorted(rev.keys())
    display_years = years[-5:] if len(years) > 5 else years
    if not display_years:
        return ""

    sym = "€" if currency == "EUR" else "£" if currency == "GBP" else "$"
    lines.append(f'yFinance ({ticker}):')
    rev_str = "; ".join(f'{y}={sym}{_fmt(rev[y])}' for y in display_years)
    lines.append(f"  Revenue: {rev_str}")

    growth = data.get("revenue_growth", {})
    if growth:
        valid = [y for y in display_years if y in growth]
        if valid:
            g_str = "; ".join(f'{y}={growth[y]:+.1f}%' for y in valid)
            lines.append(f"  Growth: {g_str}")

    for label, key in [("Gross margin", "gross_margin"), ("Operating margin", "operating_margin"),
                        ("Net margin", "net_margin")]:
        margin = data.get(key, {})
        valid = [y for y in display_years if y in margin]
        if valid:
            m_str = "; ".join(f'{y}={margin[y]:.1f}%' for y in valid)
            lines.append(f"  {label}: {m_str}")

    for label, key in [("R&D %", "rd_pct"), ("SG&A %", "sg_a_pct")]:
        pct = data.get(key, {})
        valid = [y for y in display_years if y in pct]
        if valid:
            p_str = "; ".join(f'{y}={pct[y]:.1f}%' for y in valid)
            lines.append(f"  {label}: {p_str}")

    return "<br>".join(lines)


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
