# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
# Activate virtual environment (PowerShell)
& ".venv\Scripts\Activate.ps1"

# Activate virtual environment (bash/cmd)
.venv/Scripts/activate

# Run the dashboard
streamlit run app.py
# Opens at http://localhost:8501
```

## Architecture

This is a single-page Streamlit dashboard for analyzing Brazilian stock performance (Itaú ITUB4, Petrobras PETR4, Vale VALE3) from Jan/2025 to Mar/2026.

**Data flow:** `config.py` → `data_loader.py` → `charts.py` → `app.py`

- **`config.py`** — Single source of truth: ticker symbols (`.SA` suffix for B3/Bovespa), date range, and color palette. Change stocks or date range here only.
- **`data_loader.py`** — Fetches all tickers in one `yf.download()` call. Returns `dict[ticker → DataFrame]` with columns `Close`, `Volume`, `DailyReturn`, `CumulativeReturn`. Uses `@st.cache_data(ttl=3600)`. Handles yfinance MultiIndex columns (returned when fetching multiple tickers).
- **`charts.py`** — Pure functions: data in, `go.Figure` out. No Streamlit calls. Four charts: price, cumulative performance, daily returns, volume. All use `template="plotly_dark"` and `hovermode="x unified"`.
- **`app.py`** — Layout only: fetches data, renders sidebar checkboxes to filter tickers, passes filtered `metrics` dict to chart functions, renders `st.metric` footer.

## Key Conventions

- `CumulativeReturn` is always based on `Close.iloc[0]` (first trading day in dataset), not a hardcoded date.
- yfinance MultiIndex: access via `raw["Close"][ticker]` — flat DataFrame only when a single ticker is downloaded.
- Chart functions receive only the filtered `metrics` dict (already subset by sidebar selection).
