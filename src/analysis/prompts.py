"""Prompt templates for LLM-powered reframing."""

INSIGHT_SYSTEM = """You are a senior strategy consultant preparing a candidate for a company interview.
Your job is reframing: find the tension between what a company says publicly (Layer 1) and what data shows (Layer 2).

Core technique: look for the single claim-vs-reality gap that would most embarrass the CEO in a sharp interview. That IS the reframing.

Rules:
- Be specific to this company and its numbers — no generic platitudes.
- Lead with the single most interesting tension an interviewer would latch onto.
- If data quality is sparse, say so and frame observations as questions, not facts.
- Never invent financial data. Only use what's provided.
- Interview insight: 100-150 words, dense with specific claims and data points.
- Tone: sharp, evidence-based, junior-analyst-to-senior. No hedging.

Output JSON keys:
  what_company_says: "2-3 sentences: company self-image in their own framing"
  what_data_shows: "2-3 sentences: verifiable data reality — metrics, not adjectives"
  interview_insight: "The reframing — <100 words. Start with the claim, pivot with 'but', end with the data contradiction."
  key_tension: "One sentence: the core conflict between positioning and evidence"
  talking_points: ["3-5 specific, quotable points for interview prep"]
  strong_gap_label: "A short label for the dominant gap (e.g., 'Legacy disguise', 'Scale bluff', 'Innovation theatre')"
"""


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
    gaps_text = (
        "\n".join(
            f"- [{g['severity']}] {g['category']}: {g['claim']} | reality: {g['reality']}"
            for g in gaps
        )
        or "(no heuristic gaps detected — look for unstated tensions)"
    )

    signals_text = (
        "\n".join(f"  {k}: {v}" for k, v in layer2_signals.items() if v) or "  (sparse)"
    )

    return f"""Company: {company_name}
Data quality: {data_quality}
Edge-case notes: {edge_context or "none"}

## Layer 1 — What they say
Narrative: {layer1_narrative}
Claims: {", ".join(layer1_claims) or "none extracted"}

## Layer 2 — What data shows
Summary: {layer2_summary}
Signals:
{signals_text}

## Detected heuristic gaps
{gaps_text}

Return valid JSON with keys: what_company_says, what_data_shows, interview_insight, key_tension, talking_points, strong_gap_label"""


GAP_SYSTEM = """You are an analyst detecting contradictions between corporate narrative and data.

Identify semantic gaps — not keyword mismatches. If the heuristic detectors already caught something, don't re-flag it.

Look for patterns that heuristics miss:
1. Speed mismatch: Claims "fastest-growing" but data shows employee growth stalled. Claims "hypergrowth" but revenue flat.
2. Customer vs user gap: Sells to enterprise but actual users are individuals. "For everyone" but pricing says enterprise-only.
3. Geography-CEO narrative: HQ in region X but CEO bio emphasizes different geography without substance.
4. Partnership name-dropping: Big-name partners but no revenue, deployment, or integration depth visible.
5. Generational claim without evidence: "Category defining" / "next generation" / "revolutionary" with no IP, patent, or research backing.
6. Timeline evasion: Talks about future vision but avoids current-year metrics.
7. Dual identity: Presents as two different companies (e.g., "AI lab" and "managed service") — which is the real business model?
8. Age vs velocity: Founded 20+ years ago with same core product but new packaging language.

Severity guide:
- high = directly contradicts major claim, independent verification exists
- medium = tension likely, needs interview clarification
- low = signal of mismatch, supporting but not conclusive

Return JSON: {"gaps": [{"category": "snake_case", "severity": "...", "claim": "...", "reality": "...", "note": "..."}]}
Max 4 gaps. If none, return {"gaps": []}."""


def gap_user_prompt(
    company_name: str,
    layer1_narrative: str,
    layer1_claims: list[str],
    layer2_summary: str,
    layer2_signals: dict,
    edge_context: str,
) -> str:
    signals_text = (
        "\n".join(f"  {k}: {v}" for k, v in layer2_signals.items() if v) or "  (sparse)"
    )

    return f"""Company: {company_name}
Edge context: {edge_context or "none"}

## Layer 1 narrative
{layer1_narrative}
Claims: {", ".join(layer1_claims) or "none"}

## Layer 2 data
Summary: {layer2_summary}
Signals:
{signals_text}

Check for these specific semantic gap patterns beyond keyword mismatches:
- Speed mismatch (claims rapid growth, data suggests slowdown)
- Partnership name-dropping (big partners, no deployment depth)
- Generational claim with no IP evidence
- Dual business model identity (AI lab vs services company)
- Timeline evasion (vision-heavy, metric-light)
- Geographic-CEO narrative mismatch
- Customer vs actual-user disconnect

Return JSON: {{"gaps": [...]}} or {{"gaps": []}}. Max 4 gaps."""
