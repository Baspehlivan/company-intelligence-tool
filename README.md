# Company Intelligence Tool (CIT)

A reframing engine that takes a company name and produces a structured intelligence report. It systematically separates what a company says about itself (Layer 1) from what the data actually shows (Layer 2), then surfaces the gaps as actionable insight.

**Use cases:** competitive analysis, investment research, due diligence, sourcing, interview preparation.

## Core Logic: The Reframing Engine

- **Layer 1:** What does the company say about itself? (public statements, positioning, annual reports, mission)
- **Layer 2:** What do financials, growth, and market data actually show? (revenue trends, margins, employee efficiency, funding patterns)
- **Output:** The gap between these two — expressed as structured, diagnostic insight with 27+ heuristic detectors

The reframing is universal: it works for public companies with tickers (via yfinance + EDGAR XBRL), private companies with sparse web data (via DuckDuckGo extraction + curated references), and everything in between.

## Architecture

| Layer | Component | What it does |
|-------|-----------|-------------|
| Data | `src/data_collector/live_collector.py` | Live connector — two-path architecture |
| Analysis | `src/analysis/` | Reframing engine (heuristic + LLM synthesis) |
| Automation | Hermes cron jobs | Scheduled data collection per target company |
| Output | `src/output/` + `cit` CLI | HTML, dashboard, exports, compare, API |

### Live Data Connector — Two-Path Architecture

- **Public path** (has ticker): Uses `yfinance` for financial statements, key metrics, stock history, description
- **Private path** (no ticker): Uses web search (DuckDuckGo) + structured extraction for funding, employees, HQ

Both paths return the same normalized JSON schema. The analysis engine does not need to know which path was used.

### Reframing Engine — 27+ Gap Detectors

Each detector maps to a specific business judgment dimension:

| Detector | What it catches |
|----------|----------------|
| Revenue per Employee | Productivity gap — headcount vs output |
| Claim Consistency | Layer 1 vs Layer 2 contradiction |
| Funding Efficiency | Capital efficiency vs burn rate |
| ESG Posture | Sustainability claims vs disclosure depth |
| Customer Concentration | Whale dependency risk |
| Moat Analysis | Competitive advantage — genuine vs claimed |
| Market Timing | Sector tailwind vs execution quality |
| Complexity Denial | Product sprawl vs organizational maturity |
| Regulatory Posture | Compliance narrative vs actual footprint |

... plus 20 more spanning financial health, growth quality, management credibility, and competitive positioning.

## Usage

```bash
# Activate venv first
source .venv/bin/activate

# Auto-detect: tries public, falls back to private
python src/data_collector/live_collector.py "Rhenus" --pretty
python src/data_collector/live_collector.py "Buynomics" --pretty --output data/buynomics.json

# Explicit ticker (skip auto-detect)
python src/data_collector/live_collector.py "DHL" --ticker DHL --pretty
python src/data_collector/live_collector.py "Apple" --ticker AAPL --output data/apple.json

# Save to file
python src/data_collector/live_collector.py "Rhenus" --output data/rhenus.json
```

## Project Structure

```
cit/
├── README.md
├── .venv/                 # Python virtual environment
├── data/                  # Collected company reports (JSON)
│   ├── buynomics.json
│   └── rhenus.json
├── config/                # Company targets, schedules, API keys
├── cit                       # CLI launcher (./cit report …)
├── reports/                  # Generated HTML, JSON, exports
└── src/
    ├── data_collector/       # Live connector + reference snapshots
    │   ├── live_collector.py # Orchestrator: Wikipedia → Crunchbase → DDG → EDGAR
    │   ├── edgar.py          # SEC EDGAR XBRL financials
    │   ├── wikipedia.py      # Wikipedia API client
    │   ├── market.py         # Market data collection
    │   ├── reference.py      # Curated snapshots (30 companies)
    │   └── yfinance_financials.py  # yfinance financial extraction
    ├── analysis/             # Reframing engine
    │   ├── layers.py         # Layer 1 (narrative) + Layer 2 (data) extraction
    │   ├── gaps.py           # 27+ heuristic + semantic gap detectors
    │   ├── insights.py       # Interview insight synthesis
    │   ├── report.py         # GapReportOutput dataclass + build_report()
    │   ├── edge_cases.py     # Sparse data handling and fallback logic
    │   └── llm.py            # LLM backends (openclaude / litellm)
    ├── output/               # HTML, dashboard, exports, compare
    │   ├── html_report.py    # Professional HTML report with financial panels
    │   ├── theme.py          # Dark/light theme with financial visualization
    │   └── dashboard.py      # Terminal dashboard
    └── cit/                  # Unified CLI + FastAPI
        ├── cli.py            # CLI dispatcher
        └── companies.py      # Company registry management
```

## Analysis Engine

```bash
# Template-only (no API key)
python -m src.analysis "Rhenus" --from-file data/rhenus.json --pretty --no-llm

# Full pipeline with reference enrichment for sparse live data
python -m src.analysis "Rhenus" --from-file data/rhenus.json --pretty

# Live fetch + LLM synthesis (requires OPENAI_API_KEY or ANTHROPIC_API_KEY)
export OPENAI_API_KEY=sk-...
python -m src.analysis "Buynomics" --pretty -o reports/buynomics.json
```

| Flag | Effect |
|------|--------|
| `--no-llm` | Template insight synthesis (no API calls) |
| `--no-enrich` | Skip merging curated reference data when live data is sparse |
| `-f` / `--from-file` | Analyze existing collector JSON |

Environment: `CIT_LLM_BACKEND=auto|openclaude|litellm`, `CIT_LLM_MODEL`, API keys for litellm

## CIT CLI (output layer)

```bash
pip install -r requirements.txt

# List all companies
./cit companies

# Seed collector JSON from curated reference (offline)
python -m src.data_collector.seed
# Or one company: ./cit collect dhl --seed

# Live fetch (public tickers need network)
./cit collect apple --ticker AAPL

# One-shot demo — 7 companies + 3 compare pages
./cit demo --no-llm
# → open reports/demo/index.html

# Subset demo
./cit demo --no-llm --only rhenus,dhl,apple

# Terminal dashboard (default)
./cit report Rhenus --from-file data/rhenus.json --no-llm

# Auto-write HTML + JSON to reports/
./cit report Rhenus -f data/rhenus.json --no-llm --out-dir reports

# Explicit dashboard
./cit report Rhenus -f data/rhenus.json --no-llm --dashboard

# Export formats
./cit report Rhenus -f data/rhenus.json --no-llm \
  --html reports/rhenus.html \
  --md reports/rhenus.md \
  --csv reports/rhenus_gaps.csv \
  --pdf reports/rhenus.pdf \
  --json reports/rhenus.json

# Compare two companies
./cit compare Rhenus Buynomics \
  --from-files data/rhenus.json data/buynomics.json --no-llm \
  --html reports/compare.html

# Render saved analysis JSON
./cit view reports/rhenus.json --dashboard
./cit view reports/rhenus.json --html reports/rhenus.html

# Demo API (browser) — requires: pip install fastapi uvicorn
./cit serve --port 8000
# → http://127.0.0.1:8000/report/Rhenus?format=html&no_llm=true
```

| Command | Description |
|---------|-------------|
| `cit report` | Analyze + dashboard / exports |
| `cit companies` | List registry (`config/companies.yaml`) |
| `cit collect` | Fetch live or `--seed` reference into `data/` |
| `cit compare` | Side-by-side (use keys: `./cit compare rhenus dhl`) |
| `cit view` | Render existing JSON without re-fetch |
| `cit demo` | Full demo bundle under `reports/demo/` |
| `cit batch` | All companies in `config/targets.yaml` |
| `cit serve` | FastAPI + report index at `/` |

### HTML report features
- Executive scorecard (confidence, data quality, gap counts)
- Layer 1 ⟷ Layer 2 reframing bridge
- Filterable gaps (high / medium / low)
- 27+ diagnostic detectors with strong label categorization
- Copy interview insight · dark/light theme · print-ready

## Technology

- **Python** — core engine (pandas, yfinance, requests, beautifulsoup4)
- **SEC EDGAR XBRL** — direct financial statement extraction (no API key required)
- **Multi-agent split** — OpenClaude (analysis engine), Cursor (output layer), Hermes (automation)
- **Two-path data normalization** — same schema for public and private companies

## License

MIT
