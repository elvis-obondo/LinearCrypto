import time
import sqlite3
import ccxt

# 1. Setup Exchange
okx = ccxt.okx()
timeframe = "5m"
# Jan 1, 2026 00:00:00 UTC in milliseconds
start_time = 1767225600000 
# Current time in milliseconds
current_time = int(time.time() * 1000)

def fetch_all_ohlcv(symbol, start_ts):
    all_data = []
    since = start_ts
    limit = 300  # OKX specific limit
    
    print(f"Starting fetch for {symbol}...")
    
    while since < current_time:
        try:
            # Fetching in batches of 300
            batch = okx.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
            
            if not batch:
                break
                
            all_data.extend(batch)
            
            # Update 'since' to the timestamp of the last candle + 1ms to get the next batch
            last_ts = batch[-1][0]
            since = last_ts + 1
            
            # If the last candle fetched is very close to 'now', we can stop
            if len(batch) < limit:
                break
                
            # Respect OKX rate limits (approx 20 requests per 2 seconds for history)
            time.sleep(okx.rateLimit / 1000)
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            break
            
    return all_data

# 2. Execute Fetching
solana_data = fetch_all_ohlcv("SOL/USDT", start_time)
kamino_data = fetch_all_ohlcv("KMNO/USDT", start_time)

# 3. Database Operation
conn = sqlite3.connect('crypto_pairs.db')
cursor = conn.cursor()

# We use INSERT OR IGNORE so this script is "idempotent" 
# (you can run it 100 times and it won't duplicate data)
insert_sol = "INSERT OR IGNORE INTO solana (timestamp, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?)"
insert_kmno = "INSERT OR IGNORE INTO kamino (timestamp, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?)"

cursor.executemany(insert_sol, solana_data)
cursor.executemany(insert_kmno, kamino_data)

conn.commit()
conn.close()

print(f"Done! Processed {len(solana_data)} SOL rows and {len(kamino_data)} KMNO rows.")