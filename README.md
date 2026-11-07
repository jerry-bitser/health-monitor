# Health Monitor

A small Python tool that checks whether websites are up, stores every result in SQLite, and reports uptime and response times.

## What it does
- `monitor.py` checks a list of URLs and saves status code, response time and up/down result
- `report.py` summarizes uptime % and average response time per site using SQL
- `explain_demo.py` compares a query plan before and after adding an index on 300k synthetic rows
- `test_monitor.py` has pytest unit tests (network calls are mocked)
- `Dockerfile` packages the monitor as a container

## Run locally
    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python3 monitor.py
    python3 report.py

## Run tests
    pytest -v

## Run with Docker
    docker build -t health-monitor .
    mkdir -p data
    docker run --rm -v "$(pwd)/data:/app/data" -e DB_FILE=/app/data/monitor.db health-monitor

## SQL index experiment
Run `python3 explain_demo.py`. Results on my machine: full table scan 21.2 ms -> 1.5 ms with a composite index on (url, checked_at), about 14x faster on 300k synthetic rows
