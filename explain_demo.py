import random
import sqlite3
import time
from datetime import datetime, timedelta, timezone

DB = "seed.db"
conn = sqlite3.connect(DB)
conn.execute("DROP TABLE IF EXISTS checks")
conn.execute(
    """CREATE TABLE checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL, status_code INTEGER, response_ms REAL,
        is_up INTEGER NOT NULL, checked_at TEXT NOT NULL)"""
)

urls = [f"https://site{i}.example.com" for i in range(50)]
start = datetime(2026, 1, 1, tzinfo=timezone.utc)
rows = []
for i in range(300_000):
    t = (start + timedelta(seconds=i * 60)).isoformat()
    up = random.random() > 0.05
    rows.append((random.choice(urls), 200 if up else 500,
                 random.uniform(50, 900), int(up), t))
conn.executemany(
    "INSERT INTO checks (url, status_code, response_ms, is_up, checked_at) VALUES (?,?,?,?,?)",
    rows)
conn.commit()

QUERY = ("SELECT AVG(response_ms) FROM checks "
         "WHERE url = 'https://site7.example.com' AND checked_at >= '2026-06-01'")

def timed():
    t0 = time.perf_counter()
    for _ in range(20):
        conn.execute(QUERY).fetchone()
    return (time.perf_counter() - t0) / 20 * 1000

print("BEFORE INDEX")
for row in conn.execute("EXPLAIN QUERY PLAN " + QUERY):
    print("  plan:", row[3])
before = timed()
print(f"  avg time: {before:.2f} ms")

conn.execute("CREATE INDEX idx_checks_url_time ON checks (url, checked_at)")
conn.commit()

print("AFTER INDEX")
for row in conn.execute("EXPLAIN QUERY PLAN " + QUERY):
    print("  plan:", row[3])
after = timed()
print(f"  avg time: {after:.2f} ms")
print(f"Speedup: {before / after:.1f}x")
