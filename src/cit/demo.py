"""Generate full portfolio demo bundle under reports/demo/."""

from __future__ import annotations

import json
from pathlib import Path

from src.analysis.engine import analyze_report
from src.output.render import render_report, render_compare
from src.output.index_page import write_index
from src.cit.companies import load_companies, load_compare_pairs, slug_for


def run_demo(
    out_dir: Path | None = None,
    *,
    no_llm: bool = True,
    keys: list[str] | None = None,
) -> Path:
    root = Path(__file__).resolve().parents[2]
    out = out_dir or root / "reports" / "demo"
    out.mkdir(parents=True, exist_ok=True)

    companies = load_companies()
    if keys:
        key_set = {k.lower() for k in keys}
        companies = [c for c in companies if c.get("key", "").lower() in key_set]

    entries = []
    reports_by_key: dict[str, object] = {}

    for c in companies:
        name = c["name"]
        slug = slug_for(c)
        json_path = root / c.get("from_file", f"data/{slug}.json")

        if not json_path.exists():
            from src.data_collector.seed import seed_all
            seed_all(root / "data", [slug])
            json_path = root / "data" / f"{slug}.json"

        if not json_path.exists():
            continue

        raw = json.loads(json_path.read_text())
        report = analyze_report(raw, company_name=name, use_llm=not no_llm)
        reports_by_key[slug] = report

        render_report(report, fmt="html", path=out / f"{slug}.html")
        (out / f"{slug}.json").write_text(report.to_json(indent=2), encoding="utf-8")
        render_report(report, fmt="md", path=out / f"{slug}.md")
        render_report(report, fmt="csv", path=out / f"{slug}_gaps.csv")

        entries.append({
            "name": name,
            "html": f"{slug}.html",
            "confidence": report.confidence,
            "gaps": len(report.gaps),
            "type": "report",
        })

    for key_a, key_b in load_compare_pairs():
        if key_a not in reports_by_key or key_b not in reports_by_key:
            continue
        ra = reports_by_key[key_a]
        rb = reports_by_key[key_b]
        cmp_name = f"compare_{key_a}_{key_b}.html"
        render_compare(ra, rb, dashboard=False, html_path=out / cmp_name)
        entries.append({
            "name": f"{ra.company_name} vs {rb.company_name}",
            "html": cmp_name,
            "confidence": "—",
            "gaps": len(ra.gaps) + len(rb.gaps),
            "type": "compare",
        })

    write_index(out, entries)
    return out
