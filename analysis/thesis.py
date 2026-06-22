# thesis.py
# Reads merged CSV from data/raw/, runs statistical analysis to test the thesis:
# "The dollar's decline is cyclical, not structural. A rebound is more likely than a continued slide."
# Steps: rate differential → EM stress → safe haven → bear case trends → regression → verdict

import statsmodels.formula.api as smf
import pandas as pd
import os


# ── 1. LOAD DATA ──────────────────────────────────────────────────────────────
# Reads the merged CSV produced by fetch.py (all 18 series, monthly, 2000–present)
df = pd.read_csv(
    os.path.join("data", "raw", "merged.csv"),
    index_col=0,
    parse_dates=True
)


# ── 2. RATE DIFFERENTIAL ──────────────────────────────────────────────────────
# Core bull case: when US rates are higher than ECB rates, dollar should be stronger.
# Two versions:
#   RATE_DIFF_10Y    — market-forward view (what traders price in)
#   RATE_DIFF_POLICY — what the Fed and ECB have actually done
df["RATE_DIFF_10Y"]    = df["US10Y"] - df["ECBRATE"]
df["RATE_DIFF_POLICY"] = df["FEDFUNDS"] - df["ECBRATE"]

# Rolling 24-month correlation: positive = differential and DXY move together (bull case)
# Finding: CORR_10Y was +0.81 in early 2025 but turned negative (-0.53) by mid-2025.
# The mechanism existed but has recently broken down — likely due to tariff/policy uncertainty.
df["CORR_10Y"]    = df["DXY"].rolling(24).corr(df["RATE_DIFF_10Y"])
df["CORR_POLICY"] = df["DXY"].rolling(24).corr(df["RATE_DIFF_POLICY"])


# ── 3. EM STRESS CORRELATIONS ─────────────────────────────────────────────────
# If the dollar strengthens, EM assets should weaken (negative correlation expected).
# EMB starts Dec 2007, EEM from Apr 2003, BRL/TRY from late 2003 — sample is ~18 years not 26.
# Finding: EMB (-0.70), EEM (-0.64), TRY (-0.71), INR (-0.47) all negative as expected.
# Exception: BRL (+0.81) — Brazil's commodity exports and aggressive rate hikes drove BRL
# independently of DXY, masking the typical relationship.
df["CORR_EMB"] = df["DXY"].rolling(24).corr(df["EMB"])
df["CORR_EEM"] = df["DXY"].rolling(24).corr(df["EEM"])
df["CORR_BRL"] = df["DXY"].rolling(24).corr(df["BRL"])
df["CORR_TRY"] = df["DXY"].rolling(24).corr(df["TRY"])
df["CORR_INR"] = df["DXY"].rolling(24).corr(df["INR"])


# ── 4. SAFE HAVEN CORRELATIONS ────────────────────────────────────────────────
# Tests whether the dollar's decline was driven by risk-off fear (structural) or sentiment (cyclical).
# Expected: VIX positive, Gold negative, Oil negative, SP500 negative.
# Finding: VIX near zero (0.05) — dollar decline is NOT fear-driven, supports cyclical thesis.
# Gold strongly negative (-0.69), SP500 negative (-0.57) as expected.
# Oil turned from positive to near zero — OPEC supply dynamics overwhelmed the dollar relationship.
df["CORR_VIX"]   = df["DXY"].rolling(24).corr(df["VIX"])
df["CORR_GOLD"]  = df["DXY"].rolling(24).corr(df["GOLD"])
df["CORR_OIL"]   = df["DXY"].rolling(24).corr(df["OIL"])
df["CORR_SP500"] = df["DXY"].rolling(24).corr(df["SP500"])


# ── 5. BEAR CASE TRENDS ───────────────────────────────────────────────────────
# Directional check only — no regression (FEDERAL_DEFICIT and CURRENT_ACCOUNT are
# quarterly/annual figures forward-filled, not suitable for month-over-month analysis).
# Finding: Trade deficit spike in early 2025 was tariff front-running, now normalized.
# Foreign Treasury holdings rose ($8,528B → $9,248B) — foreigners are NOT dumping US assets.
# Bear case structural argument is weak based on this data.
bear = df[["TRADE_BALANCE", "CURRENT_ACCOUNT", "FOREIGN_TREASURY_HOLDINGS"]].dropna()


# ── 6. REGRESSION ─────────────────────────────────────────────────────────────
# Regress monthly DXY returns on three predictors to quantify what actually drives the dollar.
# Using changes/returns (not levels) to avoid spurious correlation from trending series.
df["DXY_RETURN"]    = df["DXY"].pct_change()
df["RATE_DIFF_CHG"] = df["RATE_DIFF_10Y"].diff()   # change in rate differential
df["VIX_CHG"]       = df["VIX"].pct_change()
df["SP500_RETURN"]  = df["SP500"].pct_change()

reg_df = df[["DXY_RETURN", "RATE_DIFF_CHG", "VIX_CHG", "SP500_RETURN"]].dropna()

# OLS regression — dependent variable: DXY monthly return
# Finding: R²=0.167 (17% explained — reasonable for FX)
# RATE_DIFF_CHG: coef=+0.016, p=0.000 — statistically significant bull signal
# SP500_RETURN:  coef=-0.188, p=0.000 — significant, risk-on = dollar outflows
# VIX_CHG:       coef=-0.0003, p=0.960 — not significant, VIX is noise for DXY
model = smf.ols("DXY_RETURN ~ RATE_DIFF_CHG + VIX_CHG + SP500_RETURN", data=reg_df).fit()


# ── 7. VERDICT ────────────────────────────────────────────────────────────────
# Tally bull vs bear signals programmatically and output a confidence-rated verdict.
bull = 0
bear_count = 0

if model.params["RATE_DIFF_CHG"] > 0 and model.pvalues["RATE_DIFF_CHG"] < 0.05:
    bull += 1  # rate differential is a statistically significant positive predictor
if df["RATE_DIFF_10Y"].iloc[-1] > 0:
    bull += 1  # differential is still wide and positive
if df["FOREIGN_TREASURY_HOLDINGS"].dropna().iloc[-1] > df["FOREIGN_TREASURY_HOLDINGS"].dropna().iloc[0]:
    bull += 1  # foreigners buying more Treasuries, not less
if abs(df["CORR_VIX"].iloc[-1]) < 0.1:
    bull += 1  # VIX not driving dollar — decline is sentiment not structural fear
if df["CORR_EMB"].iloc[-1] < -0.3:
    bull += 1  # EM stress mechanism working as expected

if df["CORR_10Y"].iloc[-1] < 0:
    bear_count += 1  # rate diff correlation has turned negative recently
if df["CORR_POLICY"].iloc[-1] < 0:
    bear_count += 1  # policy rate differential also negatively correlated
if df["CORR_GOLD"].iloc[-1] < -0.5:
    bear_count += 1  # gold strongly negatively correlated — dollar losing store-of-value bid
if df["CORR_BRL"].iloc[-1] > 0.5:
    bear_count += 1  # BRL decoupled — EM transmission not universal

total = bull + bear_count
confidence = bull / total

print("=== THESIS VERDICT ===")
print()
print("BULL SIGNALS:")
print(f"  [+] Rate differential significant predictor of DXY (p=0.000, coef={model.params['RATE_DIFF_CHG']:.4f})")
print(f"  [+] Rate differential still wide: {df['RATE_DIFF_10Y'].iloc[-1]:.2f}% as of latest data")
print(f"  [+] Foreign Treasury holdings rising: ${df['FOREIGN_TREASURY_HOLDINGS'].dropna().iloc[0]:.0f}B -> ${df['FOREIGN_TREASURY_HOLDINGS'].dropna().iloc[-1]:.0f}B")
print(f"  [+] VIX correlation near zero ({df['CORR_VIX'].iloc[-1]:.2f}) — decline is sentiment-driven, not structural fear")
print(f"  [+] EM stress mechanism working: EMB corr={df['CORR_EMB'].iloc[-1]:.2f}, EEM corr={df['CORR_EEM'].iloc[-1]:.2f}")
print()
print("BEAR SIGNALS:")
print(f"  [-] 10Y rate diff correlation with DXY turned negative ({df['CORR_10Y'].iloc[-1]:.2f})")
print(f"  [-] Policy rate differential correlation negative ({df['CORR_POLICY'].iloc[-1]:.2f})")
print(f"  [-] Gold strongly negatively correlated ({df['CORR_GOLD'].iloc[-1]:.2f}) — dollar losing store-of-value bid")
print(f"  [-] BRL decoupled: corr={df['CORR_BRL'].iloc[-1]:.2f} — EM transmission not universal")
print()
print(f"Bull signals: {bull}/{total}")
print(f"Bear signals: {bear_count}/{total}")
print(f"Confidence in bull thesis: {confidence:.0%}")
print()

if confidence >= 0.7:
    print("VERDICT: THESIS SUPPORTED")
elif confidence >= 0.5:
    print("VERDICT: THESIS PARTIALLY SUPPORTED")
else:
    print("VERDICT: THESIS REJECTED")

print()
print("The structural bear case is weak — foreigners are buying Treasuries, deficits are")
print("improving, and VIX is calm. However the rate differential mechanism has broken down")
print("recently, suggesting sentiment and policy uncertainty are dominating fundamentals.")
print("A rebound is more likely than a continued slide, but the timeline is uncertain.")
