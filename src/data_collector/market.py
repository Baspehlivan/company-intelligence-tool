"""
Market data layer: yfinance for market-cap, EV, valuation multiples.

Integrates with EDGAR financials to compute:
  - Market capitalisation
  - Enterprise value (market cap + debt - cash)
  - P/E ratio (trailing twelve months)
  - EV/Revenue, EV/EBITDA
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import time
from typing import Optional

CACHE_DIR = Path.home() / ".cit" / "cache" / "market"
CACHE_TTL = 43200  # 12 hours (prices change intraday)


def _market_cache_path(ticker: str) -> Path:
    return CACHE_DIR / f"{ticker.upper()}.json"


def _load_market_cache(ticker: str) -> dict | None:
    path = _market_cache_path(ticker)
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


def _save_market_cache(ticker: str, payload: dict) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {"payload": payload, "_cached_at": time.time()}
        _market_cache_path(ticker).write_text(json.dumps(data, default=str))
    except OSError:
        pass


def fetch_market_data(ticker: str, *, force_refetch: bool = False) -> dict:
    """Fetch market data from yfinance with cache.

    Returns dict with:
      - market_cap, enterprise_value, pe_ratio
      - ev_revenue, ev_ebitda
      - price, shares_outstanding
      - _status: "ok" | "not_found" | "error"
    """
    if not force_refetch:
        cached = _load_market_cache(ticker)
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
        result["_error"] = "yfinance not installed (pip install yfinance)"
        return result

    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
            result["_status"] = "not_found"
            return result

        price = info.get("currentPrice") or info.get("regularMarketPrice")
        shares = info.get("sharesOutstanding")
        market_cap = info.get("marketCap") or (price * shares if price and shares else None)
        total_debt = info.get("totalDebt") or info.get("longTermDebt") or 0
        cash = info.get("totalCash") or info.get("cashAndShortTermInvestments") or 0
        ebitda = info.get("ebitda")
        revenue_ttm = info.get("totalRevenue")

        ev = None
        if market_cap and total_debt is not None and cash is not None:
            ev = market_cap + total_debt - cash

        pe = info.get("trailingPE") or info.get("forwardPE")

        result["price"] = price
        result["shares_outstanding"] = shares
        result["market_cap"] = market_cap
        result["enterprise_value"] = ev
        result["pe_ratio"] = pe

        if ev is not None and revenue_ttm:
            result["ev_revenue"] = round(ev / revenue_ttm, 2)
        if ev is not None and ebitda:
            result["ev_ebitda"] = round(ev / ebitda, 2)

        result["_currency"] = info.get("currency", "USD")
        result["sector"] = info.get("sector")
        result["industry"] = info.get("industry")

        _save_market_cache(ticker, result)
    except Exception as e:
        result["_status"] = "error"
        result["_error"] = str(e)

    return result
