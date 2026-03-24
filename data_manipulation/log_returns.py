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
    'BTC/USDC:USDC', 'ETH/USDC:USDC', 'DYDX/USDC:USDC', 'SOL/USDC:USDC', 'AVAX/USDC:USDC', 
    'BNB/USDC:USDC', 'SUI/USDC:USDC', 'LDO/USDC:USDC', 'LINK/USDC:USDC', 'GMX/USDC:USDC', 
    'XRP/USDC:USDC', 'APT/USDC:USDC', 'AAVE/USDC:USDC', 'COMP/USDC:USDC', 'TRX/USDC:USDC', 
    'UNI/USDC:USDC', 'DOT/USDC:USDC', 'ADA/USDC:USDC', 'TON/USDC:USDC', 'PENDLE/USDC:USDC', 
    'NEAR/USDC:USDC', 'PYTH/USDC:USDC', 'JUP/USDC:USDC', 'ONDO/USDC:USDC', 'ENA/USDC:USDC', 
    'MNT/USDC:USDC', 'ALGO/USDC:USDC', 'HYPE/USDC:USDC', 'MORPHO/USDC:USDC', 'SKY/USDC:USDC', 
    'ASTER/USDC:USDC', 'APEX/USDC:USDC', 'LIT/USDC:USDC'
]

def get_market_data():

    for symbol in SYMBOLS:
        try:
            close_data = supabase.table("market_data")\
            .select("close")\
            .eq("symbol",symbol)\
            .order("timestamp",desc=False)\
            .range(0,10000)\
            .execute()
            if close_data:
                # Loop in loop. so for every value in the market data (e.g. {'close': 0.10892}, {'close': 0.10892},) 
                # Get the values in all of those dictionaries
                market_data.append([value for d in close_data.data for value in d.values()])
                
        except:
            print('An exception occurred')
    


    log_returns = [np.diff(l) for l in market_data]
    combined_matrix = np.vstack(log_returns)
    return combined_matrix




if __name__ == "__main__":
    get_market_data()
    
