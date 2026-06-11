# TDI Intern Project — Project Process - Johann Varghese
*Last updated: June 10, 2026*

---

## Purpose
Build an investment thesis, test it with real data, and deliver a verdict. Document everything along the way.

## Thesis
> "The dollar's 2026 decline is temporary, not permanent. A rebound is more likely than a continued spiral."

**Position:** Bullish on dollar recovery. No reversal.

The dollar (DXY) fell ~10% in 2025. Most major banks expect continued weakness. My thesis is contrarian.

## Deliverables
- **Lower tier (due June 20):** Python script + statistical analysis + 2–3 charts + 10-min presentation on GitHub with README
- **Higher tier (due July 6):** Interactive Streamlit app, live data, adjustable parameters
- **Aspirational target:** Bull agent / Bear agent / Judge agent + Q&A mode

## Tech Stack
- **Data:** yFinance, FRED, Alpha Vantage
- **UI:** Streamlit
- **Version control:** GitHub (commit every meaningful change)

## Project Structure
```
tdi-intern-project/
├── app.py                 ← Streamlit entry point
├── requirements.txt
├── data/
│   ├── fetch.py           ← pulls from APIs, saves CSVs
│   └── raw/               ← CSVs saved here
├── analysis/
│   └── thesis.py          ← stats + verdict
├── charts/
│   └── visualize.py       ← chart functions
└── agents/                ← bull/bear/judge (not yet built)
```

**Data flow:** `fetch.py` → CSVs → `thesis.py` → results → `visualize.py` → `app.py`

**Refresh pattern:** CSVs are cached locally. Date range selector filters in-memory (fast). Refresh button in Streamlit re-fetches from APIs.

## Data Sources (~18 series)

### Structural drivers (does the dollar's strength have legs?)
| Data | Source | Ticker/Code |
|---|---|---|
| DXY — Dollar Index | yFinance | `DX-Y.NYB` |
| Fed Funds Rate | FRED | `FEDFUNDS` |
| US 10-Year Treasury Yield | FRED | `DGS10` |
| ECB Rate | FRED | `ECBDFR` |
| EUR/USD | yFinance | `EURUSD=X` |
| JPY/USD | yFinance | `JPY=X` |

### EM damage (who gets hurt?)
| Data | Source | Ticker/Code |
|---|---|---|
| EM Bond ETF | yFinance | `EMB` |
| EM Equity ETF | yFinance | `EEM` |
| Brazilian Real | yFinance | `BRL=X` |
| Turkish Lira | yFinance | `TRY=X` |
| Indian Rupee | yFinance | `INR=X` |

### Bear case data (what cuts against the thesis?)
| Data | Source | Ticker/Code |
|---|---|---|
| US Current Account Balance | FRED | `NETFI` |
| Foreign Holdings of US Treasuries | FRED | `FDHBFIN` |
| US Federal Deficit | FRED | `FYFSD` |

### Supporting/contextual
| Data | Source | Ticker/Code |
|---|---|---|
| S&P 500 | yFinance | `^GSPC` |
| VIX | yFinance | `^VIX` |
| Gold | yFinance | `GC=F` |
| Oil | yFinance | `CL=F` |
| US Trade Balance | FRED | `BOPGSTB` |

> Bear case data is intentionally included. The goal is honest analysis, not a skewed output. If the data partially contradicts the thesis, the Judge agent weighs it. A partial confirmation is more credible than a clean sweep.

## Current Status
DXY data pulled (2000–2026, monthly). Project structure scaffolded. Remaining data not yet pulled.

**Next step:** Build out `fetch.py` — pull all remaining series from yFinance and FRED.

