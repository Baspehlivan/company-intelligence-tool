"""
CIT Reframing Analysis Engine.

Takes the live_collector output (company info + financials + growth + positioning)
and produces a structured gap report:
  - Layer 1: What the company says publicly
  - Layer 2: What the data actually shows
  - Synthesized interview-ready insight
"""

from .engine import analyze_company, analyze_report
from .report import GapReportOutput

__all__ = ["analyze_company", "analyze_report", "GapReportOutput"]
