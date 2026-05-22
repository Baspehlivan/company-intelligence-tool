"""Quick test to verify all gap detectors fire correctly."""

import json
import sys

sys.path.insert(0, "/home/pehlivan/cit")

from src.analysis.report import build_report


def test_company(name, path):
    with open(path) as f:
        data = json.load(f)
    report = build_report(
        data, company_name=name, use_llm=False, use_reference_enrichment=False
    )
    print(f"\n=== {name} ===")
    print(f"Data quality: {report.data_quality}")
    print(f"Synthesis mode: {report.synthesis_mode}")
    print(f"Edge flags: {report.edge_flags}")
    print(f"Gaps ({len(report.gaps)}):")
    for g in report.gaps:
        print(f"  [{g['severity']:>6}] {g['category']:<35s} {g['claim'][:50]}")
    print(f"Key tension: {report.key_tension[:150]}")
    print(f"Talking points ({len(report.talking_points)}):")
    for tp in report.talking_points[:5]:
        print(f"  - {tp[:100]}")


test_company("Rhenus", "/home/pehlivan/cit/data/rhenus.json")
test_company("Buynomics", "/home/pehlivan/cit/data/buynomics.json")
