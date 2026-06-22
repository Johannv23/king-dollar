# fetch.py
# Pulls data from yFinance and FRED, saves to data/raw/ as CSVs.
# Run this directly OR trigger via the Refresh button in app.py.
import yfinance as yf
from fredapi import Fred
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

fred = Fred(api_key = os.getenv("FRED_API_KEY"))

def fetch_yfinance():
    os.makedirs("data/raw", exist_ok=True)

    tickers = {
        "DX-Y.NYB": "dxy",
        "EURUSD=X": "eurusd",
        "JPY=X":    "jpyusd",
        "EMB":      "emb",
        "EEM":      "eem",
        "BRL=X":    "brl",
        "TRY=X":    "try",
        "INR=X":    "inr",
        "^GSPC":    "sp500",
        "^VIX":     "vix",
        "GC=F":     "gold",
        "CL=F":     "oil",
    }

    for ticker, name in tickers.items():
        print(f"Fetching {name} ({ticker})...")
        df = yf.download(ticker, start="2000-01-01", interval="1mo", progress=False)
        df = df[["Close"]]
        df.columns = [name.upper()]
        df.to_csv(f"data/raw/{name}.csv")
        print(f"  Saved {len(df)} rows to data/raw/{name}.csv")


def fetch_fred():
    os.makedirs("data/raw", exist_ok=True)

    series = {
        "FEDFUNDS": "fedfunds",
        "DGS10":    "us10y",
        "ECBDFR":   "ecbrate",
        "NETFI":    "current_account",
        "FDHBFIN":  "foreign_treasury_holdings",
        "FYFSD":    "federal_deficit",
        "BOPGSTB":  "trade_balance",
    }

    for code, name in series.items():
        print(f"Fetching {name} ({code})...")
        s = fred.get_series(code, observation_start="2000-01-01")
        s.to_frame(name=code).to_csv(f"data/raw/{name}.csv")
        print(f"  Saved {len(s)} rows to data/raw/{name}.csv")

def load(filename, col):
    df = pd.read_csv(f"data/raw/{filename}", index_col=0, parse_dates=True)
    df.columns = [col]
    return df

def merge():

    dxy     = load("dxy.csv",     "DXY")
    eurusd  = load("eurusd.csv",  "EURUSD")
    jpyusd  = load("jpyusd.csv",  "JPYUSD")
    emb     = load("emb.csv",     "EMB")
    eem     = load("eem.csv",     "EEM")
    brl     = load("brl.csv",     "BRL")
    try_    = load("try.csv",     "TRY")
    inr     = load("inr.csv",     "INR")
    sp500   = load("sp500.csv",   "SP500")
    vix     = load("vix.csv",     "VIX")
    gold    = load("gold.csv",    "GOLD")
    oil     = load("oil.csv",     "OIL")

    fedfunds  = load("fedfunds.csv",                 "FEDFUNDS")
    us10y     = load("us10y.csv",                    "US10Y")
    ecbrate   = load("ecbrate.csv",                  "ECBRATE")
    ca        = load("current_account.csv",          "CURRENT_ACCOUNT")
    fth       = load("foreign_treasury_holdings.csv","FOREIGN_TREASURY_HOLDINGS")
    deficit   = load("federal_deficit.csv",          "FEDERAL_DEFICIT")
    trade     = load("trade_balance.csv",            "TRADE_BALANCE")

    # merge everything on the date index
    df = pd.concat([
        dxy, eurusd, jpyusd, emb, eem, brl, try_, inr,
        sp500, vix, gold, oil,
        fedfunds, us10y, ecbrate, ca, fth, deficit, trade
    ], axis=1)

    # align to monthly frequency, forward-fill FRED quarterly series
    df = df.resample("MS").last().ffill()

    df.to_csv(f"data/raw/merged.csv")







if __name__ == "__main__":
    merge()



# TODO: pull DXY (DX-Y.NYB) from yFinance
# TODO: pull Fed Funds Rate from FRED
# TODO: pull EM bond spread proxy (EMB) from yFinance
# TODO: save each series as a CSV in data/raw/
