# visualize.py
# Generates 3 charts supporting the thesis: "The dollar's decline is cyclical, not structural."
# Reads from data/raw/merged.csv — run fetch.py first if CSVs are missing.
# Saves charts to charts/output/

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from matplotlib.patches import Patch


# ── SETUP ─────────────────────────────────────────────────────────────────────
os.makedirs("charts/output", exist_ok=True)

df = pd.read_csv(
    os.path.join("data", "raw", "merged.csv"),
    index_col=0,
    parse_dates=True
)

# recompute derived columns needed for charts
df["RATE_DIFF_10Y"] = df["US10Y"] - df["ECBRATE"]
df["CORR_10Y"]      = df["DXY"].rolling(24).corr(df["RATE_DIFF_10Y"])
df["CORR_EMB"]      = df["DXY"].rolling(24).corr(df["EMB"])
df["CORR_EEM"]      = df["DXY"].rolling(24).corr(df["EEM"])
df["CORR_BRL"]      = df["DXY"].rolling(24).corr(df["BRL"])
df["CORR_TRY"]      = df["DXY"].rolling(24).corr(df["TRY"])
df["CORR_INR"]      = df["DXY"].rolling(24).corr(df["INR"])
df["DXY_3M_RETURN"] = df["DXY"].pct_change(3) * 100
df["STRONG_DOLLAR"]  = df["DXY_3M_RETURN"] > 3


# ── CHART 2: DXY vs RATE DIFFERENTIAL + ROLLING CORRELATION ──────────────────
# Two-panel chart: top = DXY and rate differential levels, bottom = rolling correlation.
# Shows the mechanism working (positive correlation) then breaking down mid-2025.
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

# top panel — DXY and rate differential
ax1.plot(df.index, df["DXY"], color="#1f77b4", label="DXY", linewidth=1.5)
ax1_twin = ax1.twinx()
ax1_twin.plot(df.index, df["RATE_DIFF_10Y"], color="#ff7f0e",
              label="Rate Diff (US10Y − ECB)", linewidth=1.2, linestyle="--")
ax1.set_ylabel("DXY Level", color="#1f77b4")
ax1_twin.set_ylabel("Rate Differential (%)", color="#ff7f0e")
ax1.set_title("DXY vs. US–ECB Rate Differential", fontsize=13, fontweight="bold")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)
ax1.grid(axis="y", linestyle="--", alpha=0.4)

# bottom panel — rolling correlation
corr = df["CORR_10Y"].dropna()
ax2.plot(corr.index, corr, color="purple", linewidth=1.5, label="Rolling 24M Correlation")
ax2.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax2.fill_between(corr.index, corr, 0,
                 where=(corr > 0), color="green", alpha=0.15, label="Positive (bull)")
ax2.fill_between(corr.index, corr, 0,
                 where=(corr < 0), color="red", alpha=0.15, label="Negative (bear)")
ax2.set_ylabel("Correlation")
ax2.set_title("Rolling 24-Month Correlation: DXY vs. Rate Differential", fontsize=11)
ax2.legend(fontsize=8)
ax2.grid(axis="y", linestyle="--", alpha=0.4)
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax2.xaxis.set_major_locator(mdates.YearLocator(2))

plt.tight_layout()
plt.savefig("charts/output/chart2_rate_diff_correlation.png", dpi=150)
plt.close()
print("Saved chart2_rate_diff_correlation.png")


# ── CHART 3: EM STRESS CORRELATIONS BAR CHART ────────────────────────────────
# Latest rolling correlation of DXY vs each EM series.
# Negative = dollar strength hurts EM (expected). BRL positive = anomaly.

latest = {
    "EMB":  df["CORR_EMB"].dropna().iloc[-1],
    "EEM":  df["CORR_EEM"].dropna().iloc[-1],
    "BRL":  df["CORR_BRL"].dropna().iloc[-1],
    "TRY":  df["CORR_TRY"].dropna().iloc[-1],
    "INR":  df["CORR_INR"].dropna().iloc[-1],
}

labels = list(latest.keys())
values = list(latest.values())
# red = negative (expected — dollar strength hurts EM), green = positive (anomaly)
colors = ["#d62728" if v < 0 else "#2ca02c" for v in values]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(labels, values, color=colors, edgecolor="white", width=0.5)
ax.axhline(0, color="black", linewidth=0.8)

for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2,
            val + (0.02 if val >= 0 else -0.04),
            f"{val:.2f}", ha="center", va="bottom", fontsize=9)

ax.set_title("DXY vs. EM Assets — Rolling 24M Correlation (Latest)", fontsize=13, fontweight="bold")
ax.set_ylabel("Correlation with DXY")
ax.set_ylim(-1, 1)
ax.grid(axis="y", linestyle="--", alpha=0.4)

legend_elements = [Patch(color="#d62728", label="Negative — EM weakens as DXY rises (expected)"),
                   Patch(color="#2ca02c", label="Positive — anomaly (BRL driven by local factors)")]
ax.legend(handles=legend_elements, fontsize=8)

plt.tight_layout()
plt.savefig("charts/output/chart3_em_correlations.png", dpi=150)
plt.close()
print("Saved chart3_em_correlations.png")



# ── CHART 4: 2022 ZOOM — DXY vs EEM / GOLD / OIL (NORMALIZED TO 100) ─────────
zoom = df["2022":"2022"].copy()

# normalize each series so Jan 2022 = 100
base = zoom.iloc[0]
for col in ["DXY", "EEM", "GOLD", "OIL"]:
    zoom[col + "_N"] = zoom[col] / base[col] * 100

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(zoom.index, zoom["DXY_N"],  color="#1f77b4", linewidth=2,   label="DXY")
ax.plot(zoom.index, zoom["EEM_N"],  color="#d62728", linewidth=1.5,  label="EEM (EM Equities)", linestyle="--")
ax.plot(zoom.index, zoom["GOLD_N"], color="#ff7f0e", linewidth=1.5,  label="Gold",              linestyle="--")
ax.plot(zoom.index, zoom["OIL_N"],  color="#2ca02c", linewidth=1.5,  label="Oil (WTI)",         linestyle="--")

ax.axhline(100, color="black", linewidth=0.7, linestyle=":")

# shade strong dollar periods (same rule as Chart 1)
in_period = False
start = None
for date, row in zoom.iterrows():
    if row["STRONG_DOLLAR"] and not in_period:
        start = date
        in_period = True
    elif not row["STRONG_DOLLAR"] and in_period:
        ax.axvspan(start, date, color="green", alpha=0.15)
        in_period = False
if in_period:
    ax.axvspan(start, zoom.index[-1], color="green", alpha=0.15)

ax.set_title("2022: DXY vs. EEM, Gold & Oil — Normalized to 100 (Jan 2022)",
             fontsize=13, fontweight="bold")
ax.set_ylabel("Indexed Level (Jan 2022 = 100)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.xticks(rotation=45, ha="right")
ax.legend(handles=[
    plt.Line2D([0], [0], color="#1f77b4", linewidth=2,              label="DXY"),
    plt.Line2D([0], [0], color="#d62728", linewidth=1.5, linestyle="--", label="EEM (EM Equities)"),
    plt.Line2D([0], [0], color="#ff7f0e", linewidth=1.5, linestyle="--", label="Gold"),
    plt.Line2D([0], [0], color="#2ca02c", linewidth=1.5, linestyle="--", label="Oil (WTI)"),
    Patch(color="green", alpha=0.3, label="Strong dollar period (DXY +3% / 90 days)"),
], fontsize=9, loc="upper right")
ax.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig("charts/output/chart4_2022_normalized.png", dpi=150)
plt.close()
print("Saved chart4_2022_normalized.png")

print("\nAll charts saved to charts/output/")

