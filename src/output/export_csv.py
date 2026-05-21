"""CSV export of gaps for spreadsheet analysis."""

from __future__ import annotations

import csv
import io

from src.analysis.report import GapReportOutput


def to_csv(report: GapReportOutput) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "company",
        "analyzed_at",
        "category",
        "severity",
        "claim",
        "reality",
        "note",
    ])
    for g in report.gaps:
        writer.writerow([
            report.company_name,
            report.analyzed_at,
            g.get("category", ""),
            g.get("severity", ""),
            g.get("claim", ""),
            g.get("reality", ""),
            g.get("note", ""),
        ])
    if not report.gaps:
        writer.writerow([
            report.company_name,
            report.analyzed_at,
            "",
            "",
            "",
            "",
            "no gaps detected",
        ])
    return buf.getvalue()
