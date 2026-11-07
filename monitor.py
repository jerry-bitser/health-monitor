import os
import sqlite3
import time
from datetime import datetime, timezone

import requests

DB_FILE = os.environ.get("DB_FILE", "monitor.db")

URLS = [
    "https://www.google.com",
    "https://github.com",
    "https://www.python.org",
    "https://httpbin.org/status/500",           # always returns an error
    "https://this-site-does-not-exist-12345.com",  # always fails
]


def init_db(conn):
    """Create the table that stores every check result."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            status_code INTEGER,
            response_ms REAL,
            is_up INTEGER NOT NULL,
            checked_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def check_url(url, timeout=5):
    """Send a GET request. Return (status_code, response_ms, is_up)."""
    start = time.time()
    try:
        response = requests.get(url, timeout=timeout)
        elapsed_ms = (time.time() - start) * 1000
        is_up = 1 if response.status_code < 400 else 0
        return response.status_code, elapsed_ms, is_up
    except requests.RequestException:
        # DNS failure, timeout, connection refused, etc.
        return None, None, 0


def save_result(conn, url, status_code, response_ms, is_up):
    """Insert one check result into the database."""
    conn.execute(
        "INSERT INTO checks (url, status_code, response_ms, is_up, checked_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (url, status_code, response_ms, is_up,
         datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()


def main():
    conn = sqlite3.connect(DB_FILE)
    init_db(conn)
    for url in URLS:
        status, ms, is_up = check_url(url)
        save_result(conn, url, status, ms, is_up)
        label = "UP  " if is_up else "DOWN"
        ms_text = f"{ms:.0f} ms" if ms is not None else "no response"
        print(f"{label} {url} -> {status} ({ms_text})")
    conn.close()


if __name__ == "__main__":
    main()
