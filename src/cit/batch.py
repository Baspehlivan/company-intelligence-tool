"""Batch analyze targets from config/companies.yaml."""

from __future__ import annotations

import json
from pathlib import Path

from src.analysis.engine import analyze_report, analyze_company
from src.output.render import render_report, render_compare
from src.output.index_page import write_index
from src.cit.companies import load_companies, load_compare_pairs, slug_for, load_targets


def run_batch(
    out_dir: Path,
    *,
    no_llm: bool = False,
    keys: list[str] | None = None,
) -> list[Path]:
    root = Path(__file__).resolve().parents[2]
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    written: list[Path] = []
    reports_by_key: dict = {}

    companies = load_companies()
    if not companies:
        companies = [{"name": t["name"], "key": t["name"].lower(), **t} for t in load_targets()]

    if keys:
        key_set = {k.lower() for k in keys}
        companies = [c for c in companies if c.get("key", "").lower() in key_set]

    for c in companies:
        name = c["name"]
        slug = slug_for(c)
        from_file = c.get("from_file")
        ticker = c.get("ticker")

        if from_file:
            path = root / from_file
            if not path.exists():
                from src.data_collector.seed import seed_all
                seed_all(root / "data", [slug])
            raw = json.loads((root / from_file).read_text())
            report = analyze_report(raw, company_name=name, use_llm=not no_llm)
        else:
            report = analyze_company(name, ticker=ticker, use_llm=not no_llm)

        reports_by_key[slug] = report
        html_p = out_dir / f"{slug}.html"
        render_report(report, fmt="html", path=html_p)
        (out_dir / f"{slug}.json").write_text(report.to_json(indent=2), encoding="utf-8")
        written.append(html_p)
        entries.append({
            "name": name,
            "html": html_p.name,
            "confidence": report.confidence,
            "gaps": len(report.gaps),
            "type": "report",
        })

    for key_a, key_b in load_compare_pairs():
        if key_a in reports_by_key and key_b in reports_by_key:
            cmp = f"compare_{key_a}_{key_b}.html"
            render_compare(
                reports_by_key[key_a],
                reports_by_key[key_b],
                dashboard=False,
                html_path=out_dir / cmp,
            )
            written.append(out_dir / cmp)
            entries.append({
                "name": f"{reports_by_key[key_a].company_name} vs {reports_by_key[key_b].company_name}",
                "html": cmp,
                "confidence": "—",
                "gaps": "—",
                "type": "compare",
            })

    write_index(out_dir, entries)
    written.append(out_dir / "index.html")
    return written
