import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
import ccxt


# 1. Load Environment Variables
# Conceptual Logic: Finding the file relative to the script itself

env_path = "././.env"
load_dotenv(dotenv_path=env_path)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Failsafe: Ensure keys actually exist before continuing
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials. Check your .env file location.")


# 2. Initialize Clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
exchange = ccxt.hyperliquid()

# Configuration
TIMEFRAME = "5m"
# Jan 1, 2026 00:00:00 UTC in milliseconds
START_OF_YEAR = 1767225600000 

# The 50 Symbols List
SYMBOLS = [
    'BTC/USDC:USDC', 'ETH/USDC:USDC', 'DYDX/USDC:USDC', 'SOL/USDC:USDC', 'AVAX/USDC:USDC', 
    'BNB/USDC:USDC', 'SUI/USDC:USDC', 'LDO/USDC:USDC', 'LINK/USDC:USDC', 'GMX/USDC:USDC', 
    'XRP/USDC:USDC', 'APT/USDC:USDC', 'AAVE/USDC:USDC', 'COMP/USDC:USDC', 'TRX/USDC:USDC', 
    'UNI/USDC:USDC', 'DOT/USDC:USDC', 'ADA/USDC:USDC', 'TON/USDC:USDC', 'PENDLE/USDC:USDC', 
    'NEAR/USDC:USDC', 'PYTH/USDC:USDC', 'JUP/USDC:USDC', 'ONDO/USDC:USDC', 'ENA/USDC:USDC', 
    'MNT/USDC:USDC', 'ALGO/USDC:USDC', 'HYPE/USDC:USDC', 'MORPHO/USDC:USDC', 'SKY/USDC:USDC', 
    'ASTER/USDC:USDC', 'APEX/USDC:USDC', 'LIT/USDC:USDC'
]
def get_latest_timestamp(symbol)->int:
    """Checks Supabase for the last recorded candle of a specific coin."""
    response = supabase.table("market_data") \
        .select("timestamp") \
        .eq("symbol", symbol) \
        .order("timestamp", desc=True) \
        .limit(1) \
        .execute()
    
    if response.data:
        return response.data[0]['timestamp']
    return START_OF_YEAR

def fetch_and_upload(symbol):
    """Fetches data from Hyperliquid and upserts to Supabase."""
    # Logic Check: Where did we leave off?
    since = get_latest_timestamp(symbol) + 1
    current_time = int(time.time() * 1000)
    
    all_rows = []
    print(f"Syncing {symbol} starting from {since}...")

    try:
        while since < current_time:
            # Hyperliquid fetch_ohlcv (limit is high, usually 5000)
            candles = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, since=since,)
            
            if not candles:
                break
            
            # Convert list of lists to list of dicts for Supabase
            for c in candles:
                all_rows.append({
                    "timestamp": c[0],
                    "symbol": symbol,
                    "open": c[1],
                    "high": c[2],
                    "low": c[3],
                    "close": c[4],
                    "volume": c[5]
                })
            
            since = candles[-1][0] + 1
            
            # Break if we've reached 'now'
            if len(candles) < 20: 
                break
                
            time.sleep(2)

        # Upsert in batches to Supabase (handles duplicates via Composite PK)
        if all_rows:
            # Supabase upsert automatically uses the Primary Key we defined in SQL
            supabase.table("market_data").upsert(all_rows).execute()
            print(f"Successfully synced {len(all_rows)} rows for {symbol}.")
        else:
            print(f"{symbol} is already up to date.")

    except Exception as e:
        print(f"FAILSAFE: Error syncing {symbol}. Skipping... (Error: {e})")


def main():
    print("Starting Global Sync...")
    for symbol in SYMBOLS:
        fetch_and_upload(symbol)
    print("All coins processed.")

'''
# Test main function
def main():
    print("Starting Smoke Test...")
    # Test with just one reliable coin first
    fetch_and_upload("BTC/USDC") 
    print("Smoke test complete.")
'''
if __name__ == "__main__":
    main()