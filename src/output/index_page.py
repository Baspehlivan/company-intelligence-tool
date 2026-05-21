"""Generate reports/index.html listing available reports."""

from __future__ import annotations

import html
from pathlib import Path
from datetime import datetime


def write_index(reports_dir: Path, entries: list[dict]) -> Path:
    """
    entries: [{"name", "html", "json", "confidence", "gaps", "type": "report"|"compare"}]
    """
    reports_dir.mkdir(parents=True, exist_ok=True)
    cards = ""
    for e in entries:
        link = e.get("html", "#")
        name = e.get("name", "Report")
        conf = e.get("confidence", "—")
        gaps = e.get("gaps", "—")
        typ = e.get("type", "report")
        badge = "compare" if typ == "compare" else conf
        cards += f"""
        <a class="card" href="{html.escape(link)}">
          <span class="badge">{html.escape(str(badge))}</span>
          <h2>{html.escape(name)}</h2>
          <p class="meta">{html.escape(typ)} · {gaps} gaps</p>
        </a>"""

    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>CIT Reports</title>
  <style>
    body {{ font-family: system-ui; background:#0c0f14; color:#eef2f7; padding:2rem; max-width:720px; margin:0 auto; }}
    h1 {{ margin-bottom:0.25rem; }}
    .sub {{ color:#8b9cb3; margin-bottom:2rem; font-size:0.9rem; }}
    .grid {{ display:grid; gap:1rem; }}
    .card {{
      display:block; text-decoration:none; color:inherit;
      background:#151b26; border:1px solid #2a3548; border-radius:12px;
      padding:1.25rem; transition: border-color 0.15s;
    }}
    .card:hover {{ border-color:#3b82f6; }}
    .card h2 {{ font-size:1.15rem; margin:0.5rem 0 0.25rem; }}
    .badge {{ font-size:0.7rem; text-transform:uppercase; color:#3b82f6; letter-spacing:0.06em; }}
    .meta {{ color:#8b9cb3; font-size:0.85rem; }}
  </style>
</head>
<body>
  <h1>CIT Reports</h1>
  <p class="sub">Portfolio demo · updated {html.escape(datetime.now().strftime('%Y-%m-%d %H:%M'))}</p>
  <div class="grid">{cards or '<p class="sub">No reports yet. Run: ./cit demo</p>'}</div>
</body>
</html>"""
    path = reports_dir / "index.html"
    path.write_text(content, encoding="utf-8")
    return path
