"""Prompt templates for LLM-powered reframing."""

INSIGHT_SYSTEM = """You are a senior strategy consultant preparing a candidate for a company interview.
Your job is reframing: find the tension between what a company says publicly (Layer 1) and what data shows (Layer 2).

Rules:
- Be specific to this company — no generic platitudes.
- Lead with the single most interesting tension an interviewer would notice.
- If data quality is sparse, say so and frame observations as questions, not facts.
- Tone: sharp, evidence-based, 120-180 words for interview_insight.
- Do not invent financial numbers not present in the data."""


def insight_user_prompt(
    company_name: str,
    layer1_narrative: str,
    layer1_claims: list[str],
    layer2_summary: str,
    layer2_signals: dict,
    gaps: list[dict],
    edge_context: str,
    data_quality: str,
) -> str:
    gaps_text = "\n".join(
        f"- [{g['severity']}] {g['category']}: {g['claim']} | reality: {g['reality']}"
        for g in gaps
    ) or "(no heuristic gaps detected — look for unstated tensions)"

    return f"""Company: {company_name}
Data quality: {data_quality}
Edge-case notes: {edge_context or "none"}

## Layer 1 — What they say
Narrative: {layer1_narrative}
Claim tags: {", ".join(layer1_claims) or "none extracted"}

## Layer 2 — What data shows
Summary: {layer2_summary}
Signals:
{chr(10).join(f"  {k}: {v}" for k, v in layer2_signals.items() if v) or "  (sparse)"}

## Detected gaps (heuristic)
{gaps_text}

Return JSON with exactly these keys:
{{
  "what_company_says": "2-3 sentence summary of public positioning",
  "what_data_shows": "2-3 sentence summary of verifiable data reality",
  "interview_insight": "The reframing paragraph — novel, interview-ready",
  "key_tension": "One sentence: the core claim vs reality tension",
  "talking_points": ["3-5 bullet strings for interview prep"]
}}"""


GAP_SYSTEM = """You are an analyst detecting gaps between corporate narrative and data.
Identify semantic contradictions — not just keyword mismatches.
Only flag gaps supported by the provided data. Severity: high | medium | low.

Return JSON: {{"gaps": [{{"category": "snake_case", "severity": "...", "claim": "...", "reality": "...", "note": "..."}}]}}
If none, return {{"gaps": []}}. Max 5 gaps."""


def gap_user_prompt(
    company_name: str,
    layer1_narrative: str,
    layer1_claims: list[str],
    layer2_summary: str,
    layer2_signals: dict,
    edge_context: str,
) -> str:
    return f"""Company: {company_name}
Edge context: {edge_context or "none"}

Layer 1 narrative: {layer1_narrative}
Claims: {", ".join(layer1_claims) or "none"}

Layer 2 summary: {layer2_summary}
Signals: {layer2_signals}

Look for patterns like:
- Claims market leadership but tiny headcount
- "Global" positioning but single-region footprint
- AI-native / disruptive framing vs old founding date or legacy sector
- Subsidiary vs parent confusion (same name, different scale)
- Post-acquisition identity (old brand, new owner)
- Zero public narrative but significant funding in data"""
