"""
Reframing Analysis Engine — main orchestrator.

Two entry points:
  - analyze_company(name): runs collector + analysis in one call
  - analyze_report(collector_output): analysis only, from existing collector data
"""

import json
import sys
from pathlib import Path
from typing import Optional

from .report import GapReportOutput, build_report


def analyze_report(collector_output: dict, company_name: Optional[str] = None) -> GapReportOutput:
    """Analyze an existing collector output dict.

    Args:
        collector_output: Dict from live_collector.fetch_company() or loaded from JSON
        company_name: Optional override for company name

    Returns:
        GapReportOutput with reframing analysis
    """
    return build_report(collector_output, company_name=company_name)


def analyze_company(
    name: str,
    ticker: Optional[str] = None,
    output_path: Optional[str] = None,
    pretty: bool = True,
) -> GapReportOutput:
    """Run collector + analysis in one call.

    Args:
        name: Company name to analyze
        ticker: Optional stock ticker (skip auto-detect)
        output_path: Optional path to save the JSON report
        pretty: Pretty-print JSON output

    Returns:
        GapReportOutput with reframing analysis
    """
    # Import live collector
    from src.data_collector.live_collector import fetch_company

    # Collect data
    collector_output = fetch_company(name, ticker=ticker)

    # Analyze
    report = analyze_report(collector_output, company_name=name)

    # Save if requested
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report.to_json(indent=2 if pretty else None))
        print(f"Report written to {out}", file=sys.stderr)

    return report


def main():
    """CLI entry point for the analysis engine."""
    import argparse

    parser = argparse.ArgumentParser(
        description="CIT Reframing Analysis Engine — produce gap reports from company data"
    )
    parser.add_argument("company", help="Company name to analyze")
    parser.add_argument("--ticker", "-t", help="Stock ticker (skip auto-detect)")
    parser.add_argument("--output", "-o", help="Output file path (JSON)")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty-print JSON")
    parser.add_argument(
        "--from-file", "-f",
        help="Load collector output from JSON file instead of fetching live"
    )

    args = parser.parse_args()

    if args.from_file:
        # Load from existing file
        data = json.loads(Path(args.from_file).read_text())
        report = analyze_report(data, company_name=args.company)
    else:
        # Live collection + analysis
        report = analyze_company(
            args.company,
            ticker=args.ticker,
            output_path=args.output,
            pretty=args.pretty,
        )

    # Print to stdout if no output file or --pretty
    if args.pretty or not args.output:
        print(report.to_json(indent=2))


if __name__ == "__main__":
    main()
