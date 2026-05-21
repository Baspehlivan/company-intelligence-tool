# Company Intelligence Tool (CIT)

A reframing engine that takes a company name and produces a structured intelligence report.  
**Purpose:** Interview preparation + portfolio project demonstrating econometric analysis skills.

## Core Logic: The Reframing Engine

- **Layer 1:** What does the company say about itself? (public statements, positioning, annual reports)
- **Layer 2:** What do financials and growth data actually show?
- **Output:** The gap between these two — expressed as interview-ready insight

## Architecture

| Layer | Component | What it does |
|-------|-----------|-------------|
| Data | `src/data_collector/live_collector.py` | Live connector — two-path architecture |
| Analysis | `src/analysis/` | Reframing engine (coming next) |
| Automation | Hermes cron jobs | Scheduled data collection per target company |
| Output | `data/` | Collected reports (JSON) |

### Live Data Connector — Two-Path Architecture

- **Public path** (has ticker): Uses `yfinance` for financial statements, key metrics, stock history, description
- **Private path** (no ticker): Uses web search (DuckDuckGo) + structured extraction for funding, employees, HQ

Both paths return the same normalized JSON schema. The analysis engine doesn't need to know which path was used.

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
└── src/
    ├── data_collector/
    │   └── live_collector.py   # Live data connector (public + private paths)
    └── analysis/               # Reframing engine (coming next)
```

## Team

- **Claude** — strategy & mapping, reframing logic design
- **Hermes** — persistent memory, automation, scheduled collection
- **Kiro** — spec-driven analysis engine
- **Cursor / Windsurf** — output modules

## Next

- Analysis reframing engine (the gap between Layer 1 and Layer 2)
- Scheduled cron jobs for target companies
- Interview-ready insight output module
