"""LLM-powered gap detection pass."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models import Gap

if TYPE_CHECKING:
    from ..edge_cases import EdgeCaseContext
    from ..layers import Layer1, Layer2


def _detect_gaps_llm(
    layer1: Layer1,
    layer2: Layer2,
    edge: EdgeCaseContext | None,
    client,
) -> list[dict]:
    from ..prompts import GAP_SYSTEM, gap_user_prompt

    payload = client.complete_json(
        GAP_SYSTEM,
        gap_user_prompt(
            company_name=layer2.company_name or "Unknown",
            layer1_narrative=layer1.narrative,
            layer1_claims=layer1.claims,
            layer2_summary=layer2.summary,
            layer2_signals=layer2.to_signals_dict(),
            edge_context=edge.summary if edge else "",
        ),
    )
    if not payload:
        return []
    return payload.get("gaps") or []
