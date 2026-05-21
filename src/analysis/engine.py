"""
Reframing Analysis Engine — main orchestrator.
"""

import json
import sys
from pathlib import Path
from typing import Optional

from .report import GapReportOutput, build_report


def analyze_report(
    collector_output: dict,
    company_name: Optional[str] = None,
    use_reference_enrichment: bool = True,
    use_llm: bool = True,
) -> GapReportOutput:
    return build_report(
        collector_output,
        company_name=company_name,
        use_reference_enrichment=use_reference_enrichment,
        use_llm=use_llm,
    )


def analyze_company(
    name: str,
    ticker: Optional[str] = None,
    output_path: Optional[str] = None,
    pretty: bool = True,
    use_reference_enrichment: bool = True,
    use_llm: bool = True,
) -> GapReportOutput:
    from src.data_collector.live_collector import fetch_company

    collector_output = fetch_company(name, ticker=ticker)
    report = analyze_report(
        collector_output,
        company_name=name,
        use_reference_enrichment=use_reference_enrichment,
        use_llm=use_llm,
    )

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report.to_json(indent=2 if pretty else None))
        print(f"Report written to {out}", file=sys.stderr)

    return report


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="CIT Reframing Analysis Engine — gap reports from company data"
    )
    parser.add_argument("company", help="Company name to analyze")
    parser.add_argument("--ticker", "-t", help="Stock ticker (skip auto-detect)")
    parser.add_argument("--output", "-o", help="Output file path (JSON)")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty-print JSON")
    parser.add_argument(
        "--from-file", "-f",
        help="Load collector output from JSON instead of live fetch",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Use template synthesis only (no API calls)",
    )
    parser.add_argument(
        "--no-enrich",
        action="store_true",
        help="Disable reference enrichment for sparse live data",
    )

    args = parser.parse_args()
    use_llm = not args.no_llm
    use_enrich = not args.no_enrich

    if args.from_file:
        data = json.loads(Path(args.from_file).read_text())
        report = analyze_report(
            data,
            company_name=args.company,
            use_reference_enrichment=use_enrich,
            use_llm=use_llm,
        )
        if args.output:
            Path(args.output).write_text(report.to_json(indent=2))
    else:
        report = analyze_company(
            args.company,
            ticker=args.ticker,
            output_path=args.output,
            pretty=args.pretty,
            use_reference_enrichment=use_enrich,
            use_llm=use_llm,
        )

    if args.pretty or not args.output:
        print(report.to_json(indent=2))


if __name__ == "__main__":
    main()
