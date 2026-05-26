import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
import ccxt

load_dotenv(dotenv_path="././.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials. Check your .env file location.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
exchange = ccxt.binance()

TIMEFRAME = "1h"
START_TIMESTAMP = 1735689600000  # Jan 1, 2025 00:00 UTC

SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'DYDX/USDT', 'SOL/USDT', 'AVAX/USDT',
    'BNB/USDT', 'SUI/USDT', 'LDO/USDT', 'LINK/USDT', 'GMX/USDT',
    'XRP/USDT', 'APT/USDT', 'AAVE/USDT', 'COMP/USDT', 'TRX/USDT',
    'UNI/USDT', 'DOT/USDT', 'ADA/USDT', 'TON/USDT', 'PENDLE/USDT',
    'NEAR/USDT', 'PYTH/USDT', 'JUP/USDT', 'ENA/USDT', 'ALGO/USDT',
    'LIT/USDT',
]


def clear_database():
    print("Clearing existing data from Supabase...")
    for symbol in SYMBOLS:
        supabase.table("market_data").delete().eq("symbol", symbol).execute()
        print(f"  Cleared {symbol}")
    print("Database cleared.")


def backfill_symbol(symbol: str):
    since = START_TIMESTAMP
    current_time = int(time.time() * 1000)
    total = 0

    while since < current_time:
        candles = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, since=since, limit=1000)
        if not candles:
            break

        rows = [
            {"timestamp": c[0], "symbol": symbol, "open": c[1],
             "high": c[2], "low": c[3], "close": c[4], "volume": c[5]}
            for c in candles
        ]

        for i in range(0, len(rows), 500):
            supabase.table("market_data").upsert(rows[i:i + 500]).execute()

        total += len(rows)
        since = candles[-1][0] + 1

        if len(candles) < 1000:
            break

        time.sleep(0.2)

    print(f"  {symbol}: {total} rows inserted.")


def main():
    clear_database()
    print(f"\nBackfilling {len(SYMBOLS)} coins from Jan 1, 2025...\n")
    for i, symbol in enumerate(SYMBOLS, 1):
        print(f"[{i}/{len(SYMBOLS)}] {symbol}")
        try:
            backfill_symbol(symbol)
        except Exception as e:
            print(f"  FAILED {symbol}: {e}")
    print("\nBackfill complete.")


if __name__ == "__main__":
    main()
