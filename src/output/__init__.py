"""CIT output layer — HTML, CLI dashboard, exports, compare."""

from src.analysis.report import report_from_dict
from .render import render_report, render_compare

__all__ = ["report_from_dict", "render_report", "render_compare"]
