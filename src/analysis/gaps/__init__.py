"""Gap detection between Layer 1 (self-image) and Layer 2 (data reality)."""

from .models import Gap, GapReport
from .orchestrator import detect_gaps
from .detectors import (
    _check_narrative_staleness,
    _check_age_vs_transformation_velocity,
)

__all__ = ["Gap", "GapReport", "detect_gaps"]
