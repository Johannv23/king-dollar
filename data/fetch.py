# fetch.py
# Pulls data from yFinance and FRED, saves to data/raw/ as CSVs.
# Run this directly OR trigger via the Refresh button in app.py.
import yfinance as yf
import pandas as pd
import os

def fetch_dxy():
    print("Fetching DXY...")
    df = yf.download("DX-Y.NYB", start="2000-01-01", interval="1mo")
    # interval options: "1d" (daily), "1wk" (weekly), "1mo" (monthly)
    # monthly is clean for macro thesis work — less noise
    
    df = df[["Close"]]  # we only need closing price
    df.columns = ["DXY"]
    
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/dxy.csv")
    print(f"Saved {len(df)} rows to data/raw/dxy.csv")

if __name__ == "__main__":
    fetch_dxy()


# TODO: pull DXY (DX-Y.NYB) from yFinance
# TODO: pull Fed Funds Rate from FRED
# TODO: pull EM bond spread proxy (EMB) from yFinance
# TODO: save each series as a CSV in data/raw/
