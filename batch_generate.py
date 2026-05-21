#!/usr/bin/env python3
"""
Batch report generator for CIT — processes multiple companies and generates
JSON, MD, HTML, and CSV reports with an index page.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.engine import analyze_company
from src.output.render import render_report
from src.output.index_page import write_index


COMPANIES = [
    "Europace",
    "SCHUFA Holding AG",
    "NOSTA Holding GmbH",
    "NTG Road GmbH",
    "ONE - Ocean Network Express (Europe) Ltd",
    "Bonisoft",
    "Boplan Deutschland GmbH",
    "Borderless Technologies GmbH",
    "Bosch Energy and Building Solutions",
    "BusinessCode GmbH",
    "catkin GmbH",
    "Chemion Logistik GmbH",
    "Contargo GmbH & Co. KG",
    "Curt Richter SE",
    "DACHSER SE",
    "dbh Logistics IT AG",
    "DB Cargo AG",
    "De Lage Landen Leasing GmbH",
    "DEFRU Logistik GmbH",
    "Den Hartogh Logistics",
    "Funke Logistik GmbH",
    "G. Peter Reber Möbel-Logistik GmbH",
    "GEODIS CL Germany GmbH",
    "Gilgen Logistics GmbH",
    "GOLDBECK West GmbH",
    "GREIWING logistics for you GmbH",
    "GRIESHABER Logistik GmbH",
    "GROUP7 AG",
    "HGK Shipping GmbH",
    "Häfen und Güterverkehr Köln AG",
    "Helrom GmbH",
    "HERMES Einrichtungs Service GmbH & Co. KG",
    "Hettich Logistik Service GmbH & Co. KG",
    "MCL Mallach Container Logistics GmbH",
    "Meyer & Meyer Warehousing Services GmbH",
    "Miebach Consulting GmbH",
    "MotionMiners GmbH",
    "Neuss-Düsseldorfer Häfen GmbH & Co. KG",
    "Rhenus Port Logistics Rhein-Ruhr GmbH",
    "RIO | The Logistics Flow",
    "RM Rail Mobility GmbH",
    "Scheidt & Bachmann IoT Solutions GmbH",
    "Schenker Deutschland AG",
    "Seacon Logistics GmbH",
    "Setlog GmbH",
    "Shippeo",
    "Sievert Logistik SE",
    "Simon Hegele Gesellschaft für Logistik und Service mbH",
    "SPS Smart Parcel Solutions GmbH",
    "Staci Deutschland GmbH",
    "startport GmbH",
    "STILL GmbH",
    "w3logistics AG",
    "Weber Data Service IT GmbH",
    "WESTFRACHT GmbH",
    "Wiltsche Fördersysteme GmbH & Co. KG",
]


def slug(name: str) -> str:
    """Convert company name to filesystem-safe slug."""
    import re
    s = name.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    return s.strip('-')


def process_company(name: str, out_dir: Path) -> dict:
    """Process a single company: collect, analyze, render all formats."""
    s = slug(name)
    company_dir = out_dir / s
    company_dir.mkdir(parents=True, exist_ok=True)

    result = {"name": name, "slug": s, "status": "ok", "errors": []}

    try:
        # Analyze (collect + gap detection + insights)
        report = analyze_company(
            name,
            use_reference_enrichment=True,
            use_llm=False,  # template mode for batch
        )

        # Render all formats
        for fmt in ["json", "md", "html", "csv"]:
            try:
                ext = {"json": ".json", "md": ".md", "html": ".html", "csv": ".csv"}[fmt]
                render_report(report, fmt=fmt, path=company_dir / f"report{ext}")
            except Exception as e:
                result["errors"].append(f"{fmt}: {e}")

        result["confidence"] = report.confidence
        result["data_quality"] = report.data_quality
        result["gaps"] = len(report.gaps)
        result["high_gaps"] = sum(1 for g in report.gaps if g.get("severity") == "high")

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch CIT report generator")
    parser.add_argument("--output", "-o", default="reports/batch", help="Output directory")
    parser.add_argument("--workers", "-w", type=int, default=4, help="Parallel workers")
    parser.add_argument("--companies", "-c", nargs="*", help="Subset of companies to process")
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    companies = args.companies if args.companies else COMPANIES
    print(f"Processing {len(companies)} companies -> {out_dir}")
    print(f"Workers: {args.workers}")
    print("-" * 60)

    results = []
    start = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(process_company, name, out_dir): name
            for name in companies
        }

        for i, future in enumerate(as_completed(futures), 1):
            name = futures[future]
            try:
                result = future.result()
                results.append(result)
                status = "OK" if result["status"] == "ok" else "ERR"
                gaps = result.get("gaps", "?")
                print(f"[{i:3d}/{len(companies)}] {status} {name} ({gaps} gaps)")
                if result["errors"]:
                    for err in result["errors"]:
                        print(f"         -> {err}")
            except Exception as e:
                results.append({"name": name, "status": "error", "errors": [str(e)]})
                print(f"[{i:3d}/{len(companies)}] ERR {name}: {e}")

    elapsed = time.time() - start
    ok = sum(1 for r in results if r["status"] == "ok")
    err = sum(1 for r in results if r["status"] == "error")

    print("-" * 60)
    print(f"Done in {elapsed:.1f}s — {ok} OK, {err} errors")

    # Generate index page
    index_entries = []
    for r in sorted(results, key=lambda x: x["name"]):
        if r["status"] == "ok":
            index_entries.append({
                "name": r["name"],
                "html": f"{r['slug']}/report.html",
                "json": f"{r['slug']}/report.json",
                "confidence": r.get("confidence", "unknown"),
                "gaps": r.get("gaps", 0),
                "type": "report",
            })

    write_index(out_dir, index_entries)
    print(f"\nIndex page: {out_dir / 'index.html'}")

    # Save summary JSON
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total": len(companies),
        "ok": ok,
        "errors": err,
        "elapsed_seconds": round(elapsed, 1),
        "companies": results,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"Summary: {out_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
