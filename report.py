import sqlite3

conn = sqlite3.connect("monitor.db")
rows = conn.execute(
    """
    SELECT url,
           COUNT(*) AS total_checks,
           ROUND(AVG(response_ms), 1) AS avg_ms,
           ROUND(100.0 * SUM(is_up) / COUNT(*), 1) AS uptime_pct
    FROM checks
    GROUP BY url
    ORDER BY uptime_pct DESC
    """
).fetchall()

print(f"{'URL':45} {'Checks':>6} {'Avg ms':>8} {'Uptime %':>9}")
for url, total, avg_ms, uptime in rows:
    print(f"{url:45} {total:>6} {str(avg_ms):>8} {uptime:>9}")
conn.close()
