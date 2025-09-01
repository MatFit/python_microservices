import sqlite3
from pathlib import Path


# Create a ticker DB to not waste API usage
DB_FILE = Path("data/tickers.db")

def get_ticker_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_ticker_db():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = get_ticker_connection()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS tickers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        company_name TEXT,
        exchange TEXT
    );
    """
    try:
        conn.execute(create_table_sql)
        print("SUCCESS IN MAKING TICKER TABLE")
    except:
        print("ERROR IN MAKING TICKER TABLE")
    conn.commit()
    conn.close()


