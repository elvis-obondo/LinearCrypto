from supabase import Client,create_client
import dotenv
import os
import numpy as np

env=dotenv.load_dotenv("././.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Invalid key and url")

supabase: Client = create_client(SUPABASE_URL,SUPABASE_KEY)

market_data = []
SYMBOLS = [
    'BTC/USDC', 'ETH/USDC', 'DYDX/USDC', 'SOL/USDC', 'AVAX/USDC', 
    'BNB/USDC', 'SUI/USDC', 'LDO/USDC', 'LINK/USDC', 'GMX/USDC', 
    'XRP/USDC', 'APT/USDC', 'AAVE/USDC', 'COMP/USDC', 'TRX/USDC', 
    'UNI/USDC', 'DOT/USDC', 'ADA/USDC', 'TON/USDC', 'PENDLE/USDC', 
    'NEAR/USDC', 'PYTH/USDC', 'JUP/USDC', 'ONDO/USDC', 'ENA/USDC', 
    'MNT/USDC', 'ALGO/USDC', 'HYPE/USDC', 'MORPHO/USDC', 'SKY/USDC', 
    'ASTER/USDC', 'APEX/USDC', 'LIT/USDC'
    ]

for symbol in SYMBOLS:
    try:
        close_data = supabase.table("market_data")\
        .select("close")\
        .eq("symbol",symbol)\
        .order("timestamp",desc=False)\
        .execute()
        if close_data:
            # Loop in loop. so for every value in the market data (e.g. {'close': 0.10892}, {'close': 0.10892},) 
            # Get the values in all of those dictionaries
            market_data.append([value for d in close_data.data for value in d.values()])
    except:
      print('An exception occurred')
    



#Gets the log returns of each list (coin) in the array of lists(market)
log_returns = [np.diff(coin) for coin in market_data]
print(len(market_data))
for i in range(34):
    print(market_data[i][0:5])





