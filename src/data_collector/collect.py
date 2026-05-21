#!/usr/bin/env python3
"""
CIT Data Collector — delegates to live_collector (single entry point).

Previously held static Rhenus/Buynomics implementations; those now live in
reference.py and are merged by the analysis engine when live data is sparse.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from src.data_collector.live_collector import fetch_company, main as live_main
except ImportError:
    from live_collector import fetch_company, main as live_main  # type: ignore


def collect_company(name: str, ticker: str | None = None) -> dict:
    """Fetch company data using the live two-path connector."""
    return fetch_company(name, ticker=ticker)


def main():
    parser = argparse.ArgumentParser(
        description="CIT Data Collector (live) — use live_collector.py directly"
    )
    parser.add_argument("company", help="Company name or ticker")
    parser.add_argument("--ticker", "-t", help="Stock ticker")
    parser.add_argument("--output", "-o", help="Output JSON path")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty-print")
    args = parser.parse_args()

    report = collect_company(args.company, ticker=args.ticker)
    text = json.dumps(report, indent=2 if args.pretty else None, default=str)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print(f"Written to {out}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    # Allow: python collect.py OR python -m src.data_collector.collect
    if len(sys.argv) > 1:
        main()
    else:
        live_main()
