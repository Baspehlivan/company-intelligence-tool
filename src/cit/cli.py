#!/usr/bin/env python3
"""Unified CIT CLI — one command, many modes.

Commands:
  report      Analyze a company and output a report (HTML, JSON, dashboard, etc.)
  compare     Side-by-side comparison of two companies
  companies   List registered companies and compare pairs
  serve       Start the FastAPI demo server
  delegate    Hand off a task to OpenClaude
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.analysis.engine import analyze_report, analyze_company
from src.analysis.report import GapReportOutput, report_from_dict
from src.output.render import render_report, render_compare


def _load_or_analyze(
    company: str,
    *,
    ticker: str | None = None,
    from_file: str | None = None,
    no_llm: bool = False,
    no_enrich: bool = False,
) -> GapReportOutput:
    if from_file:
        data = json.loads(Path(from_file).read_text())
        if ticker and not data.get("ticker"):
            data["ticker"] = ticker
        return analyze_report(
            data,
            company_name=company,
            use_reference_enrichment=not no_enrich,
            use_llm=not no_llm,
        )
    return analyze_company(
        company,
        ticker=ticker,
        output_path=None,
        pretty=False,
        use_reference_enrichment=not no_enrich,
        use_llm=not no_llm,
    )


def _slug(name: str) -> str:
    return name.lower().replace(" ", "-").replace("_", "-")


def _resolve_company(key_or_name: str, from_file: str | None = None):
    """Resolve name, file path, and ticker from registry or raw input."""
    from src.cit.companies import get_company, resolve_ticker

    c = get_company(key_or_name)
    if c:
        return c["name"], from_file or c.get("from_file"), c.get("ticker")
    ticker = resolve_ticker(key_or_name)
    return key_or_name, from_file, ticker


def cmd_report(args: argparse.Namespace) -> int:
    """Analyze a company and output report(s). Handles all modes: single, batch, demo."""
    from src.cit.companies import get_company, slug_for
    from src.cit.companies import ROOT as REGISTRY_ROOT

    # ── Demo mode: generate portfolio bundle ──
    if args.demo:
        from src.cit.demo import run_demo

        keys = args.only.split(",") if args.only else None
        out_dir = args.out_dir or "reports/demo"
        out = run_demo(Path(out_dir), no_llm=args.no_llm, keys=keys)
        print(f"Demo bundle written to {out}/", file=sys.stderr)
        print(f"  Open: {out / 'index.html'}", file=sys.stderr)
        return 0

    # ── Batch mode: analyze all targets ──
    if args.batch:
        from src.cit.batch import run_batch

        paths = run_batch(Path(args.out_dir), no_llm=args.no_llm)
        print(f"Batch complete: {len(paths)} files in {args.out_dir}", file=sys.stderr)
        return 0

    # ── Collect mode: fetch collector JSON without analysis ──
    if args.collect:
        from src.data_collector.live_collector import fetch_company
        from src.data_collector.seed import seed_all as seed_reference

        c = get_company(args.company)
        if not c:
            print(f"Unknown company: {args.company}. Run: cit companies", file=sys.stderr)
            return 1

        slug = slug_for(c)
        out = REGISTRY_ROOT / "data" / f"{slug}.json"

        if args.seed:
            seed_reference(REGISTRY_ROOT / "data", [slug])
            print(f"Seeded reference data -> {out}", file=sys.stderr)
            return 0

        report = fetch_company(c["name"], ticker=c.get("ticker"))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        print(f"Collected -> {out}", file=sys.stderr)
        return 0

    # ── Guard: single report mode requires a company name ──
    if not args.company:
        parser.print_help()
        print("\nError: report requires a company name (or --demo / --batch / --collect)", file=sys.stderr)
        return 1

    name, fpath, ticker = _resolve_company(args.company, args.from_file)
    ticker = args.ticker or ticker
    report = _load_or_analyze(
        name,
        ticker=ticker,
        from_file=fpath,
        no_llm=args.no_llm,
        no_enrich=args.no_enrich,
    )

    # Auto-path when --out-dir specified
    if args.out_dir:
        out = Path(args.out_dir)
        slug = _slug(name)
        args.html = args.html or str(out / f"{slug}.html")
        args.json = args.json or str(out / f"{slug}.json")

    # Render each requested format
    outputs: list[tuple[str, str | None]] = []
    if args.html:
        outputs.append(("html", args.html))
    if args.md:
        outputs.append(("md", args.md))
    if args.csv:
        outputs.append(("csv", args.csv))
    if args.pdf:
        outputs.append(("pdf", args.pdf))
    if args.json:
        outputs.append(("json", args.json))

    # Default: show dashboard
    if args.dashboard or not outputs:
        render_report(report, fmt="dashboard")
        if not outputs:
            return 0

    for fmt, path in outputs:
        p = Path(path) if path else None
        if fmt == "pdf" and not p:
            print("PDF requires --pdf PATH", file=sys.stderr)
            return 1
        result = render_report(report, fmt=fmt, path=p)
        if result and p:
            print(f"Wrote {result}", file=sys.stderr)
        elif result and fmt == "json" and not p:
            print(result)

    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    """Side-by-side comparison of two companies."""
    reports = []
    for i, company in enumerate(args.companies):
        from_file = None
        if args.from_files and i < len(args.from_files):
            from_file = args.from_files[i]
        name, fpath, ticker = _resolve_company(company, from_file)
        if fpath:
            data = json.loads(Path(fpath).read_text())
            reports.append(
                analyze_report(
                    data,
                    company_name=name,
                    use_reference_enrichment=not args.no_enrich,
                    use_llm=not args.no_llm,
                )
            )
        else:
            reports.append(
                analyze_company(
                    name,
                    ticker=ticker,
                    use_reference_enrichment=not args.no_enrich,
                    use_llm=not args.no_llm,
                )
            )

    if len(reports) != 2:
        print("Compare requires exactly 2 companies", file=sys.stderr)
        return 1

    html_path = Path(args.html) if args.html else None
    render_compare(reports[0], reports[1], dashboard=not args.no_dashboard, html_path=html_path)
    if html_path:
        print(f"Wrote {html_path}", file=sys.stderr)

    if args.md:
        Path(args.md).write_text(_compare_md(reports[0], reports[1]), encoding="utf-8")
        print(f"Wrote {args.md}", file=sys.stderr)

    return 0


def _compare_md(a: GapReportOutput, b: GapReportOutput) -> str:
    lines = [
        f"# Compare: {a.company_name} vs {b.company_name}",
        "",
        f"| Metric | {a.company_name} | {b.company_name} |",
        "|--------|" + "---|" * 2,
        f"| Confidence | {a.confidence} | {b.confidence} |",
        f"| Data quality | {a.data_quality} | {b.data_quality} |",
        f"| Gaps | {len(a.gaps)} | {len(b.gaps)} |",
        "",
        "## Key tensions",
        f"**{a.company_name}:** {a.key_tension}",
        f"**{b.company_name}:** {b.key_tension}",
    ]
    return "\n".join(lines)


def cmd_companies(args: argparse.Namespace) -> int:
    """List registered companies and compare pairs."""
    from src.cit.companies import load_companies, load_compare_pairs

    for c in load_companies():
        ticker = f" [{c['ticker']}]" if c.get("ticker") else ""
        print(f"  {c.get('key', '?'):12} {c['name']}{ticker}  ({c.get('type')}, {c.get('sector')})")
    print("\nCompare pairs:")
    for a, b in load_compare_pairs():
        print(f"  {a} vs {b}")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    """Start FastAPI demo server."""
    import uvicorn
    from src.cit.api import app

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return 0


def cmd_delegate(args: argparse.Namespace) -> int:
    """Hand off a task to OpenClaude."""
    from src.integration.openclaude_runner import delegate_task, try_headless

    path = delegate_task(args.task, context=args.context)
    print(f"Task written to {path}", file=sys.stderr)
    print("OpenClaude: read .openclaude/inbox/TASK.md in your openclaude session", file=sys.stderr)

    if args.run:
        ok, msg = try_headless(args.task)
        if ok:
            print("\n--- OpenClaude response ---\n", msg)
        else:
            print(f"\nNote: {msg}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cit",
        description="Company Intelligence Tool — collect, analyze, and present company intelligence",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_analysis_flags(p):
        p.add_argument("--no-llm", action="store_true", help="Template synthesis only (no API calls)")
        p.add_argument("--no-enrich", action="store_true", help="Skip reference enrichment")

    # ── report (the main command) ──
    p_report = sub.add_parser("report", help="Analyze a company and generate reports")
    add_analysis_flags(p_report)
    p_report.add_argument("company", nargs="?", default=None, help="Company name (omit for --demo or --batch)")
    p_report.add_argument("--ticker", "-t", help="Stock ticker (skip auto-detect)")
    p_report.add_argument("--from-file", "-f", help="Load collector JSON instead of live fetch")
    p_report.add_argument("--dashboard", "-d", action="store_true", help="Rich terminal dashboard output")
    p_report.add_argument("--html", help="Write HTML report path")
    p_report.add_argument("--md", help="Write Markdown path")
    p_report.add_argument("--csv", help="Write gaps CSV path")
    p_report.add_argument("--pdf", help="Write PDF path")
    p_report.add_argument("--json", help="Write JSON path")
    p_report.add_argument("--out-dir", help="Write {company}.html and {company}.json into directory")

    # Modes (merging old demo/batch/collect subcommands)
    p_report.add_argument("--demo", action="store_true", help="Generate portfolio demo bundle (reports/demo/)")
    p_report.add_argument("--batch", action="store_true", help="Analyze all targets from config/targets.yaml")
    p_report.add_argument("--collect", action="store_true", help="Fetch collector JSON only (no analysis)")
    p_report.add_argument("--seed", action="store_true", help="With --collect: use curated reference (no network)")
    p_report.add_argument("--only", help="With --demo: comma-separated company keys (e.g. rhenus,dhl)")

    p_report.set_defaults(func=cmd_report)

    # ── compare ──
    p_cmp = sub.add_parser("compare", help="Side-by-side comparison of two companies")
    add_analysis_flags(p_cmp)
    p_cmp.add_argument("companies", nargs=2, help="Two company names")
    p_cmp.add_argument("--from-files", nargs=2, metavar="FILE", help="Collector JSON files (one per company)")
    p_cmp.add_argument("--html", help="Write compare HTML")
    p_cmp.add_argument("--md", help="Write compare Markdown")
    p_cmp.add_argument("--no-dashboard", action="store_true", help="Skip terminal dashboard")
    p_cmp.set_defaults(func=cmd_compare)

    # ── companies ──
    sub.add_parser("companies", help="List registered companies and compare pairs").set_defaults(func=cmd_companies)

    # ── serve ──
    p_serve = sub.add_parser("serve", help="Start FastAPI demo server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.set_defaults(func=cmd_serve)

    # ── delegate ──
    p_del = sub.add_parser("delegate", help="Hand off a task to OpenClaude")
    p_del.add_argument("task", help="Task description")
    p_del.add_argument("--run", action="store_true", help="Also try openclaude -p headless")
    p_del.add_argument("--context", default="", help="Extra context")
    p_del.set_defaults(func=cmd_delegate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
