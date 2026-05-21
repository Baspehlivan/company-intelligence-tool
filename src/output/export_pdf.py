"""Simple PDF export via fpdf2."""

from __future__ import annotations

from pathlib import Path

from src.analysis.report import GapReportOutput


def to_pdf(report: GapReportOutput, path: Path) -> None:
    try:
        from fpdf import FPDF
    except ImportError as e:
        raise ImportError(
            "PDF export requires fpdf2. Install: pip install fpdf2"
        ) from e

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"CIT Report: {report.company_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, f"Analyzed: {report.analyzed_at} | Confidence: {report.confidence}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    sections = [
        ("Key tension", report.key_tension),
        ("Interview insight", report.interview_insight),
        ("What company says", report.what_company_says),
        ("What data shows", report.what_data_shows),
    ]
    for title, text in sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, _sanitize(text))
        pdf.ln(2)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Gaps", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for g in report.gaps:
        line = f"[{g.get('severity', '?').upper()}] {g.get('category', '')}: {g.get('claim', '')}"
        pdf.multi_cell(0, 5, _sanitize(line))
        pdf.multi_cell(0, 5, _sanitize(f"  Reality: {g.get('reality', '')}"))
        pdf.ln(1)

    if report.talking_points:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Talking points", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        for tp in report.talking_points:
            pdf.multi_cell(0, 5, _sanitize(f"- {tp}"))

    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(path))


def _sanitize(text: str) -> str:
    return text.encode("latin-1", errors="replace").decode("latin-1")
