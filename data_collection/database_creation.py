import sqlite3

def setup_database():
    # 1. Establish connection (creates the file if it doesn't exist)
    conn = sqlite3.connect('crypto_pairs.db')
    cursor = conn.cursor()

    # 2. Define the schema logic
    # Using 'IF NOT EXISTS' prevents errors if you run this script multiple times
    # 'timestamp' as INTEGER PRIMARY KEY ensures uniqueness and fast lookups
    create_sol_table = """
    CREATE TABLE IF NOT EXISTS solana (
        timestamp INTEGER PRIMARY KEY,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL
    );
    """

    create_kmno_table = """
    CREATE TABLE IF NOT EXISTS kamino (
        timestamp INTEGER PRIMARY KEY,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL
    );
    """

    # 3. Execute the commands
    cursor.execute(create_sol_table)
    cursor.execute(create_kmno_table)

    # 4. Commit the changes and close
    conn.commit()
    conn.close()
    print("Database and tables initialized successfully.")

if __name__ == "__main__":
    setup_database()