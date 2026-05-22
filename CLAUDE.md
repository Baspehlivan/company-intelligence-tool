# CIT — OpenClaude workspace guide

You own **analysis** (`src/analysis/`). Cursor owns **output** (`src/output/`, `src/cit/`).

## Your responsibilities

1. **Reframing engine** — gaps between Layer 1 (narrative) and Layer 2 (data)
2. **LLM synthesis** — `insights.py` via `src/analysis/llm.py` (OpenClaude, litellm, or templates)
3. **Data quality** — `edge_cases.py`, `reference.py` enrichment when live data is sparse
4. **Collectors** — `live_collector.py` (do not duplicate logic in `collect.py`)

## Run analysis

```bash
source .venv/bin/activate
python -m src.analysis "Rhenus" --from-file data/rhenus.json --no-llm --pretty
python -m src.analysis "Buynomics" --from-file data/buynomics.json --pretty
```

## Handoff from Cursor

Check `.openclaude/inbox/TASK.md` for the latest delegated task. When done, write results to `.openclaude/inbox/DONE.md`.

## Key files

| File | Purpose |
|------|---------|
| `src/analysis/gaps.py` | Heuristic + semantic gap detectors (27 total) |
| `src/analysis/insights.py` | Interview insight synthesis |
| `src/analysis/llm.py` | LLM backends (openclaude / litellm) |
| `src/analysis/report.py` | `GapReportOutput` dataclass + `build_report()` with EDGAR integration |
| `config/companies.yaml` | Company registry (30 companies) + 9 compare pairs |
| `src/data_collector/reference.py` | Curated snapshots (30 companies) |
| `src/data_collector/edgar.py` | SEC EDGAR XBRL financials (revenue, margins, ratios, 5-yr trends) |
| `src/data_collector/wikipedia.py` | Wikipedia API client (description, founded, HQ, employees, sector) |
| `src/data_collector/live_collector.py` | Orchestrates Wikipedia → Crunchbase → DuckDuckGo → EDGAR |
| `src/output/theme.py` | `CIT_CSS_V3` dark/light theme with professional financial sections |
| `src/output/html_report.py` | Professional HTML report with financial panels + executive summary + peer comparison |
| `src/data_collector/seed.py` | `python -m src.data_collector.seed` |

## Do not break

- `GapReportOutput` JSON shape in `report.py` (Cursor HTML/CLI depends on it)
- `./cit demo` must still produce `reports/demo/index.html`

## LLM via OpenClaude from Python

```bash
export CIT_LLM_BACKEND=openclaude
./cit report Rhenus -f data/rhenus.json --pretty
```

Or delegate: `./cit delegate "Improve gap detector for AI-native vs legacy"`
