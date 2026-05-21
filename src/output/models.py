"""Bridge analysis output to output renderers."""

from __future__ import annotations

from dataclasses import fields
from typing import Any

from src.analysis.report import GapReportOutput


def report_from_dict(data: dict[str, Any]) -> GapReportOutput:
    valid = {f.name for f in fields(GapReportOutput)}
    kwargs = {k: v for k, v in data.items() if k in valid}
    return GapReportOutput(**kwargs)
