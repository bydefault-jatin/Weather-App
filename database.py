# database.py - SQLite database management for Weather App

import sqlite3
import os

# On Vercel / serverless platforms, the root filesystem is read-only.
# We detect Vercel via environment variable and use '/tmp/weather.db' which is writable.
if os.environ.get("VERCEL") == "1":
    DB_NAME = "/tmp/weather.db"
else:
    DB_NAME = os.path.join(os.path.dirname(__file__), "weather.db")


def get_db_connection():
    """
    Opens a connection to the SQLite database.
    row_factory = sqlite3.Row allows accessing columns by name (like dictionaries).
    """
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Creates the 'searches' table if it does not already exist.
    """
    try:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    country TEXT,
                    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"Warning: Database initialization skipped: {e}")


def insert_search(city, country):
    """
    Inserts a newly searched city and country into the database.
    Uses '?' placeholders to safely pass values and avoid SQL injection.
    """
    try:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO searches (city, country)
                VALUES (?, ?)
            """, (city, country))
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"Warning: Could not save search to database: {e}")


def get_recent_searches(limit=5):
    """
    Retrieves the last unique recent searches up to the specified limit.
    Groups by city (case-insensitive) to prevent duplicate chips,
    ordered by the most recent timestamp.
    """
    try:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT city, country, MAX(searched_at) AS latest_searched_at
                FROM searches
                GROUP BY city COLLATE NOCASE
                ORDER BY latest_searched_at DESC
                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()
            recent = []
            for row in rows:
                recent.append({
                    "city": row["city"],
                    "country": row["country"]
                })
            return recent
        finally:
            conn.close()
    except Exception as e:
        print(f"Warning: Could not read searches from database: {e}")
        return []
