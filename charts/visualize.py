# visualize.py
# Generates 3 charts supporting the thesis: "The dollar's decline is cyclical, not structural."
# Reads from data/raw/merged.csv — run fetch.py first if CSVs are missing.
# Saves charts to charts/output/

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

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


# ── CHART 1: DXY PRICE HISTORY WITH ANNOTATED EVENTS ─────────────────────────
# Shows the full dollar cycle from 2000–present with key events marked.
# Tells the story: dollar has gone through cycles before — this decline fits the pattern.
fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(df.index, df["DXY"], color="#1f77b4", linewidth=1.5, label="DXY")
ax.fill_between(df.index, df["DXY"], alpha=0.08, color="#1f77b4")

# annotate key events
events = {
    "2008-09-01": ("GFC", "down"),
    "2014-07-01": ("Fed taper / USD surge", "up"),
    "2020-03-01": ("COVID crash", "down"),
    "2022-09-01": ("Fed hike cycle peak", "up"),
    "2025-01-01": ("2025 decline begins", "down"),
}

for date, (label, direction) in events.items():
    if date in df.index.strftime("%Y-%m-%d").tolist():
        x = pd.Timestamp(date)
        y = df.loc[x, "DXY"]
        offset = 4 if direction == "up" else -6
        ax.annotate(label, xy=(x, y), xytext=(x, y + offset),
                    fontsize=7.5, ha="center", color="gray",
                    arrowprops=dict(arrowstyle="-", color="gray", lw=0.8))

ax.set_title("DXY Dollar Index (2000–Present)", fontsize=13, fontweight="bold")
ax.set_ylabel("DXY Level")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.legend()
plt.tight_layout()
plt.savefig("charts/output/chart1_dxy_history.png", dpi=150)
plt.close()
print("Saved chart1_dxy_history.png")


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
from matplotlib.patches import Patch

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

print("\nAll charts saved to charts/output/")
