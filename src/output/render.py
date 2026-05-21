"""Dispatch report output to requested formats."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from src.analysis.report import GapReportOutput

from .html_report import to_html
from .dashboard import print_dashboard
from .compare import compare_dashboard, compare_html
from .export_md import to_markdown
from .export_csv import to_csv
from .export_pdf import to_pdf

Format = Literal["json", "html", "md", "csv", "pdf", "dashboard"]


def render_report(
    report: GapReportOutput,
    *,
    fmt: Format,
    path: Path | None = None,
) -> str | None:
    """Render report to format. Returns string for text formats when path is None."""
    if fmt == "dashboard":
        print_dashboard(report)
        return None

    if fmt == "json":
        text = report.to_json(indent=2)
    elif fmt == "html":
        text = to_html(report)
    elif fmt == "md":
        text = to_markdown(report)
    elif fmt == "csv":
        text = to_csv(report)
    elif fmt == "pdf":
        if not path:
            raise ValueError("PDF export requires --output path")
        to_pdf(report, path)
        return None
    else:
        raise ValueError(f"Unknown format: {fmt}")

    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return str(path)
    return text


def render_compare(
    a: GapReportOutput,
    b: GapReportOutput,
    *,
    dashboard: bool = True,
    html_path: Path | None = None,
) -> str | None:
    if dashboard:
        compare_dashboard(a, b)
    if html_path:
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(compare_html(a, b), encoding="utf-8")
        return str(html_path)
    return None
