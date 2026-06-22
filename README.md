# Dollar Rebound Thesis — TDI Intern Project
**Johann Varghese | June 2026**

---

## Thesis

> "The dollar's 2025 decline is cyclical, not structural. The conditions that drove dollar strength — rate differentials, capital flows, US economic dominance — remain intact. A rebound is more likely than a continued slide."

The DXY fell ~10% in 2025, hitting a 4-year low. Most major banks (Goldman, Deutsche Bank, Morgan Stanley) project continued weakness. This project takes the contrarian position and tests it with real data.

---

## What This Project Does

- Pulls 18 macroeconomic data series from yFinance and FRED (2000–present)
- Runs statistical analysis: rolling correlations, OLS regression, bear case trend analysis
- Generates 3 charts visualizing the results
- Outputs a data-driven verdict on the thesis

---

## Results

**Verdict: THESIS PARTIALLY SUPPORTED**

| Signal | Direction | Finding |
|---|---|---|
| Rate differential (10Y) | Bull | Statistically significant predictor of DXY (p=0.000) |
| Rate differential level | Bull | Still wide at 2.55% — conditions for rebound intact |
| Foreign Treasury holdings | Bull | Rising ($8,528B → $9,248B) — no de-dollarization |
| VIX correlation | Bull | Near zero — decline is sentiment-driven, not structural fear |
| EM stress mechanism | Bull | EMB, EEM, TRY, INR all negatively correlated as expected |
| Rate diff correlation | Bear | Turned negative (-0.53) mid-2025 — mechanism temporarily broken |
| Policy rate correlation | Bear | Consistently negative (-0.59) |
| Gold correlation | Bear | Strongly negative (-0.69) — dollar losing store-of-value bid |
| BRL decoupling | Bear | Positive correlation (+0.81) — EM transmission not universal |

The structural bear case is weak. Foreigners are buying Treasuries, the trade deficit normalized after tariff front-running, and VIX is calm. The rate differential mechanism has broken down recently — but this is consistent with a sentiment/policy-driven decline, not a structural shift. A rebound is more likely than a continued slide; the timeline is uncertain.

---

## Charts

| Chart | What It Shows |
|---|---|
| `chart1_dxy_history.png` | DXY from 2000–present with annotated macro events |
| `chart2_rate_diff_correlation.png` | DXY vs. rate differential + rolling 24M correlation |
| `chart3_em_correlations.png` | DXY vs. EM assets — latest rolling correlations |

---

## Setup & Usage

**Requirements**
```bash
pip install -r requirements.txt
```

**1. Fetch data**
```bash
python data/fetch.py
```
Pulls all 18 series from yFinance and FRED. Saves CSVs to `data/raw/`. Requires a FRED API key in a `.env` file:
```
FRED_API_KEY=your_key_here
```

**2. Run analysis**
```bash
python analysis/thesis.py
```
Loads the merged CSV, runs correlations and regression, prints the verdict.

**3. Generate charts**
```bash
python charts/visualize.py
```
Saves 3 PNGs to `charts/output/`.

---

## Project Structure

```
tdi-intern-project/
├── data/
│   ├── fetch.py           ← pulls from yFinance and FRED, saves CSVs
│   └── raw/               ← CSVs saved here (gitignored)
├── analysis/
│   └── thesis.py          ← statistical analysis + verdict
├── charts/
│   ├── visualize.py       ← chart generation
│   └── output/            ← PNG charts saved here
├── PROJECT_OVERVIEW.md    ← process log, design decisions, findings
├── requirements.txt
└── README.md
```

---

## Data Sources

| Series | Source | Ticker/Code |
|---|---|---|
| DXY Dollar Index | yFinance | `DX-Y.NYB` |
| EUR/USD | yFinance | `EURUSD=X` |
| JPY/USD | yFinance | `JPY=X` |
| EM Bond ETF | yFinance | `EMB` |
| EM Equity ETF | yFinance | `EEM` |
| Brazilian Real | yFinance | `BRL=X` |
| Turkish Lira | yFinance | `TRY=X` |
| Indian Rupee | yFinance | `INR=X` |
| S&P 500 | yFinance | `^GSPC` |
| VIX | yFinance | `^VIX` |
| Gold | yFinance | `GC=F` |
| Oil | yFinance | `CL=F` |
| Fed Funds Rate | FRED | `FEDFUNDS` |
| US 10Y Treasury Yield | FRED | `DGS10` |
| ECB Rate | FRED | `ECBDFR` |
| US Current Account | FRED | `NETFI` |
| Foreign Treasury Holdings | FRED | `FDHBFIN` |
| US Trade Balance | FRED | `BOPGSTB` |
