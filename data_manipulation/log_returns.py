import sqlite3
import numpy as np

def get_market_data():
    # 1. Connect to the database
    conn = sqlite3.connect('crypto_pairs.db')
    cursor = conn.cursor()

    # 2. Extract Solana data
    # We order by timestamp to ensure the time-series is chronological
    cursor.execute("SELECT close FROM ethereum ORDER BY timestamp ASC")
    sol_list = cursor.fetchall() 

    # 3. Extract Kamino data
    cursor.execute("SELECT close FROM kamino ORDER BY timestamp ASC")
    kmno_list = cursor.fetchall()

    # 4. Cleanup
    conn.close()
    sol_log_price=np.log(sol_list).ravel()
    kmno_log_price=np.log(kmno_list).ravel()
    

    return np.diff(sol_log_price),np.diff(kmno_log_price)

if __name__ == "__main__":
    sol_data, kmno_data = get_market_data()
    
    # Print the first few rows to verify
    print(f"Retrieved {len(sol_data)} rows for SOL.")
    print(f"Sample SOL rows: {sol_data[0:2]}")