import yfinance as yf
import pandas as pd

# ---------------------------------------------
# 1. Load NASDAQ tickers (via QQQ holdings)
# ---------------------------------------------
import requests
import pandas as pd

def get_nasdaq_tickers():
    url = "https://api.nasdaq.com/api/quote/list-type/nasdaq100"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    json_data = response.json()

    df = pd.DataFrame(json_data["data"]["data"]["rows"])
    tickers = df["symbol"].tolist()
    return tickers


# ---------------------------------------------
# 2. Download fundamentals via yfinance
# ---------------------------------------------
def get_fundamentals(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "ticker": ticker,
            "market_cap": info.get("marketCap", None),
            "sector": info.get("sector", None),
            "revenue_growth": info.get("revenueGrowth", None),
            "earnings_growth": info.get("earningsGrowth", None),
            "pe_ratio": info.get("trailingPE", None),
            "ev_to_ebitda": info.get("enterpriseToEbitda", None),
            "profit_margin": info.get("profitMargins", None),
            "debt_to_equity": info.get("debtToEquity", None)
        }

    except Exception as e:
        print(f"Error loading {ticker}: {e}")
        return None

# ---------------------------------------------
# 3. Apply mid-cap + tech + growth filters
# ---------------------------------------------
def passes_filters(data):
    if data is None:
        return False

    # Mid-cap definition: 2–10 billion USD
    mc = data["market_cap"]
    if mc is None or mc < 2e9 or mc > 10e11:
        return False

    # Sector filter
    if data["sector"] != "Technology":
        return False

    # Growth filters
    if data["revenue_growth"] is None or data["revenue_growth"] < 0.05:
        return False

    if data["earnings_growth"] is None or data["earnings_growth"] < 0.05:
        return False

    # Valuation sanity check
    pe = data["pe_ratio"]
    if pe is None or pe <= 0 or pe > 50:
        return False

    return True

# ---------------------------------------------
# 4. Run screen
# ---------------------------------------------
def run_screen():
    tickers = get_nasdaq_tickers()
    results = []

    for t in tickers:
        fundamentals = get_fundamentals(t)
        if passes_filters(fundamentals):
            results.append(fundamentals)

    df = pd.DataFrame(results)
    print("Columns:", df.columns)
    print(df.head())

    df = df.sort_values("market_cap")
    return df

# ---------------------------------------------
# 5. Execute
# ---------------------------------------------
if __name__ == "__main__":
    df = run_screen()
    print(df)
    
df.to_csv("nasdaq_midcap_screen.csv", index=False)

