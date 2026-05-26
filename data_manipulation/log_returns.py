from supabase import Client, create_client
import dotenv
import os
import numpy as np
import pandas as pd

env = dotenv.load_dotenv("././.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Invalid key and url")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'DYDX/USDT', 'SOL/USDT', 'AVAX/USDT',
    'BNB/USDT', 'SUI/USDT', 'LDO/USDT', 'LINK/USDT', 'GMX/USDT',
    'XRP/USDT', 'APT/USDT', 'AAVE/USDT', 'COMP/USDT', 'TRX/USDT',
    'UNI/USDT', 'DOT/USDT', 'ADA/USDT', 'TON/USDT', 'PENDLE/USDT',
    'NEAR/USDT', 'PYTH/USDT', 'JUP/USDT', 'ENA/USDT', 'ALGO/USDT',
    'LIT/USDT',
]

# Clean ticker labels (strip the /USDC:USDC suffix for readability)
TICKERS = [s.split('/')[0] for s in SYMBOLS]

BATCH_SIZE = 1000

def fetch_all_closes(symbol: str) -> tuple:
    timestamps, prices = [], []
    start = 0
    while True:
        batch = supabase.table("market_data") \
            .select("timestamp, close") \
            .eq("symbol", symbol) \
            .order("timestamp", desc=False) \
            .range(start, start + BATCH_SIZE - 1) \
            .execute()
        if not batch.data:
            break
        timestamps.extend(d["timestamp"] for d in batch.data)
        prices.extend(d["close"] for d in batch.data)
        if len(batch.data) < BATCH_SIZE:
            break
        start += BATCH_SIZE
    return timestamps, prices

def get_market_data():
    market_data = {}

    for symbol, ticker in zip(SYMBOLS, TICKERS):
        try:
            timestamps, prices = fetch_all_closes(symbol)
            if prices:
                series = pd.Series(prices, index=pd.to_datetime(timestamps, unit='ms', utc=True))
                log_returns = np.diff(np.log(series.values))
                market_data[ticker] = log_returns

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

    # Align all series to the same length (shortest available)
    min_len = min(len(v) for v in market_data.values())
    df = pd.DataFrame(
        {ticker: series[-min_len:] for ticker, series in market_data.items()}
    )

    return df  # Shape: (T, 33) — rows=time, cols=tickers


def get_price_levels():
    """Returns DataFrame of log prices (not returns): shape (T, 33)."""
    market_data = {}
    for symbol, ticker in zip(SYMBOLS, TICKERS):
        try:
            timestamps, prices = fetch_all_closes(symbol)
            if prices:
                series = pd.Series(prices, index=pd.to_datetime(timestamps, unit='ms', utc=True))
                market_data[ticker] = np.log(series.values)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
    min_len = min(len(v) for v in market_data.values())
    return pd.DataFrame({t: s[-min_len:] for t, s in market_data.items()})


if __name__ == "__main__":
    df = get_market_data()
    print(df.shape)
    print(df.head())