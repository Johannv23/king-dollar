# TDI Intern Project — Project Process - Johann Varghese
*Last updated: July 2, 2026*

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
*(Updated June 11, 2026)*

`fetch.py` structure finalized. All 18 series mapped and coded. Not yet run end-to-end.

### fetch.py Design Decisions

**Looped fetching instead of individual functions**
Both `fetch_yfinance()` and `fetch_fred()` use a dict mapping ticker/code → filename and iterate over it, rather than writing a separate download block per series. Reason: 12 yFinance tickers and 7 FRED series would have been ~80 lines of near-identical code. The loop is easier to extend (add a ticker to the dict, done) and easier to read.

**FRED series saved with `.to_frame(name=code)`**
`fred.get_series()` returns a pandas Series with no column name. Calling `.to_frame(name=code)` before `.to_csv()` gives the value column a proper header (e.g. `FEDFUNDS`), consistent with how yFinance CSVs are structured. Makes merging in `thesis.py` straightforward — no unnamed columns to deal with.

**`progress=False` on yFinance downloads**
Suppresses the tqdm progress bar per ticker, which would clutter the terminal across 12 downloads. Status is handled by the `print()` calls instead.

**All CSVs land in `data/raw/`**
Both functions call `os.makedirs("data/raw", exist_ok=True)` so the directory is created on first run regardless of which function runs first.

**`thesis.py` and `visualize.py` complete.** README and 10-minute presentation are the remaining pieces for the lower tier.

### thesis.py — What Was Built & Why

**Step 2 — Rate differential:** Computed two versions — `RATE_DIFF_10Y` (US10Y − ECB, market-forward) and `RATE_DIFF_POLICY` (Fed Funds − ECB, what was actually done). Used both because currency markets price off longer-term differentials, not just the overnight rate. Rolling 24-month correlation with DXY showed the 10Y version peaked at +0.81 in Feb 2025 then turned negative (-0.53) by mid-2025 — the mechanism broke down, likely due to tariff/policy uncertainty.

**Step 3 — EM stress:** Rolling 24-month correlations of DXY vs. EMB, EEM, BRL, TRY, INR. Expected negative — dollar up, EM down. EMB, EEM, TRY, INR all confirmed. BRL was a positive outlier (+0.81) — Brazil's commodity exports and aggressive rate hikes drove BRL independently of DXY.

**Step 4 — Safe haven:** Correlated DXY vs. VIX, Gold, Oil, S&P 500. Key finding: VIX near zero (0.05) — the dollar decline is not fear-driven, supporting the cyclical thesis. Gold (-0.69) and SP500 (-0.57) behaved as expected.

**Step 5 — Bear case trends:** Directional check only (no regression — FEDERAL_DEFICIT and CURRENT_ACCOUNT are quarterly/annual forward-filled, not suitable for month-over-month regression). Trade deficit spike in early 2025 was tariff front-running, now normalized. Foreign Treasury holdings rose ($8,528B → $9,248B) — foreigners are not dumping US assets. Bear case is structurally weak.

**Step 6 — Regression:** OLS on monthly DXY returns. R²=0.167. RATE_DIFF_CHG (+0.016, p=0.000) and SP500_RETURN (-0.188, p=0.000) are significant. VIX_CHG is noise (p=0.960). Used changes/returns (not levels) to avoid spurious correlation from trending series.

**Step 7 — Verdict:** Programmatic signal tally (5 bull, 4 bear checks). Confidence computed as bull/(bull+bear). Verdict: THESIS PARTIALLY SUPPORTED at moderate confidence.

### visualize.py — What Was Built & Why

Three charts saved to `charts/output/`:

**Chart 2 — DXY vs. rate differential (two-panel):** Top panel overlays DXY and the US10Y−ECB rate differential. Bottom panel shows the rolling 24-month correlation over time. Purpose: tells the core bull case story — the mechanism was strongly positive (+0.81) then broke down (-0.53), which is the central tension of the thesis.

**Chart 3 — EM stress correlations bar chart:** Latest rolling 24M correlation of DXY vs. EMB, EEM, BRL, TRY, INR. Red = negative (expected), green = positive (anomaly). Purpose: shows EM stress mechanism is broadly working, with BRL flagged as an outlier driven by local factors.

**Chart 4 — 2022 zoom, normalized to 100:** DXY, EEM, Gold, and Oil all indexed to 100 in Jan 2022 and plotted through year-end. Green shading marks strong dollar months using the same DXY +3%/90-day rule as the other charts. Purpose: makes the inverse relationship between DXY and the other assets visually obvious at the episode level.

*Note: An earlier Chart 1 (DXY full history with annotated macro events) was removed once Chart 4 superseded its storytelling role for the 2022 hike cycle.*

### Data Quality Notes (observed after fetch)

- **Missing early data** — EMB starts Dec 2007, EEM from Apr 2003, BRL/TRY from late 2003. DXY-vs-EMB correlation sample is effectively 2007–present (~18 years), not 2000. Report sample period explicitly in analysis.
- **FEDERAL_DEFICIT is sparse** — annual/quarterly figure forward-filled across months. Do not use in month-over-month regression. Use only for directional context (e.g. chart annotation).
- **Unnamed index column** — CSVs have a leading comma on row 1. Handled by `index_col=0` in the `load()` helper. Added `df.loc[:, ~df.columns.str.contains("^Unnamed")]` after `pd.concat()` as a cleanup safeguard.

