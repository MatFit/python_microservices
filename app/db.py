import sqlite3
import threading
from pathlib import Path
from contextlib import contextmanager

# Create a ticker DB to not waste API usage
DB_FILE = Path("data/tickers.db")

class SQLitePool:
    def __init__(self, db_file):
        self.db_file = db_file
        self.pool_of_connections = []
        self.lock = threading.Lock()
    
    @contextmanager
    def get_connection(self):
        conn = None
        with self.lock:
            # Try to get a connection from pool
            while self.pool_of_connections:
                conn = self.pool_of_connections.pop()
                # Check if connection is still valid
                try:
                    conn.execute("SELECT 1")
                    break  # Connection is good
                except sqlite3.Error:
                    conn = None  # Connection is bad, create new one
            
            # Create new connection if needed
            if conn is None:
                conn = sqlite3.connect(self.db_file, check_same_thread=False)
                conn.row_factory = sqlite3.Row
        
        try:
            yield conn
        except Exception:
            # If there's an error, don't return connection to pool
            try:
                conn.close()
            except:
                pass
            raise
        else:
            # Only return to pool if no exception occurred
            with self.lock:
                # Double-check connection is still valid before returning to pool
                try:
                    conn.execute("SELECT 1")
                    self.pool_of_connections.append(conn)
                except sqlite3.Error:
                    # Connection is bad, close it
                    try:
                        conn.close()
                    except:
                        pass

# Initialize the database pool
db_pool = SQLitePool(str(DB_FILE))



class TickerDB:
    _instance = None

    def __new__(cls, db_pool=None, DB_FILE=None):
        if cls._instance is None:
            cls._instance = super(TickerDB, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db_pool, DB_FILE):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.db_pool = db_pool
            self.DB_FILE = DB_FILE

    def init_ticker_db(self):
        self.DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with self.db_pool.get_connection() as conn:
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
                conn.commit()
                print("SUCCESS IN MAKING TICKER TABLE")
            except Exception as e:
                print(f"ERROR IN MAKING TICKER TABLE: {e}")

    def search_tickers_db(self, query, limit=10):
        with self.db_pool.get_connection() as conn:
            cursor = conn.execute(
                "SELECT ticker, company_name, exchange FROM tickers WHERE ticker LIKE ? OR company_name LIKE ? LIMIT ?",
                (f"%{query}%", f"%{query}%", limit)
            )
            return cursor.fetchall()
    def get_ticker_db_connection():
        with db_pool.get_connection() as db:
            yield db
    



def get_ticker_db_connection():
    with db_pool.get_connection() as db:
        yield db

def init_ticker_db():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with db_pool.get_connection() as conn:
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
            conn.commit()
            print("SUCCESS IN MAKING TICKER TABLE")
        except Exception as e:
            print(f"ERROR IN MAKING TICKER TABLE: {e}")

def search_tickers_db(query, limit=10):
    with db_pool.get_connection() as conn:
        cursor = conn.execute(
            "SELECT ticker, company_name, exchange FROM tickers WHERE ticker LIKE ? OR company_name LIKE ? LIMIT ?",
            (f"%{query}%", f"%{query}%", limit)
        )
        return cursor.fetchall()

def get_ticker_count():
    with db_pool.get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM tickers")
        return cursor.fetchone()[0]
