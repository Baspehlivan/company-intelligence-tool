"""
FastAPI server for CIT reports.

  GET /              — report index (from reports/ dir)
  GET /health
  GET /report/{company}
  GET /compare/{a}/{b}
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse

from src.analysis.engine import analyze_company, analyze_report
from src.output.html_report import to_html
from src.output.compare import compare_html
from src.output.models import report_from_dict
from src.output.index_page import write_index

ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "reports"

app = FastAPI(title="CIT API", description="Company Intelligence Tool", version="0.3.0")
_cache: dict[str, dict] = {}


def _slug(name: str) -> str:
    return name.lower().replace(" ", "-")


@app.get("/health")
def health():
    return {"status": "ok", "service": "cit", "version": "0.3.0"}


@app.get("/report/{company}")
def get_report(
    company: str,
    ticker: str | None = Query(None),
    format: str = Query("json", pattern="^(json|html)$"),
    no_llm: bool = Query(False),
    refresh: bool = Query(False),
    from_file: str | None = Query(None, description="Path to collector JSON under project root"),
):
    cache_key = f"{company}:{ticker}:{no_llm}:{from_file}"
    if not refresh and cache_key in _cache:
        data = _cache[cache_key]
    else:
        try:
            if from_file:
                import json
                raw = json.loads((ROOT / from_file).read_text())
                report = analyze_report(raw, company_name=company, use_llm=not no_llm)
            else:
                report = analyze_company(company, ticker=ticker, use_llm=not no_llm)
            data = report.to_dict()
            _cache[cache_key] = data
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    if format == "html":
        return HTMLResponse(content=to_html(report_from_dict(data)))

    return JSONResponse(content=data)


@app.get("/compare/{company_a}/{company_b}")
def get_compare(
    company_a: str,
    company_b: str,
    format: str = Query("html", pattern="^(html|json)$"),
    no_llm: bool = Query(False),
):
    try:
        ra = analyze_company(company_a, use_llm=not no_llm)
        rb = analyze_company(company_b, use_llm=not no_llm)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    if format == "json":
        return JSONResponse(content={
            "a": ra.to_dict(),
            "b": rb.to_dict(),
        })
    return HTMLResponse(content=compare_html(ra, rb))


@app.get("/")
def index():
    """Serve reports index or API map."""
    index_path = REPORTS_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    demo_index = REPORTS_DIR / "demo" / "index.html"
    if demo_index.exists():
        return FileResponse(demo_index, media_type="text/html")
    return {
        "message": "CIT API — run ./cit demo to generate reports",
        "endpoints": {
            "report_html": "/report/{company}?format=html",
            "compare_html": "/compare/{a}/{b}",
        },
    }


