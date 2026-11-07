import sqlite3

import requests

import monitor


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code


def test_save_result_stores_row():
    conn = sqlite3.connect(":memory:")
    monitor.init_db(conn)
    monitor.save_result(conn, "https://example.com", 200, 12.5, 1)
    row = conn.execute("SELECT url, status_code, is_up FROM checks").fetchone()
    assert row == ("https://example.com", 200, 1)


def test_check_url_marks_200_as_up(monkeypatch):
    monkeypatch.setattr(monitor.requests, "get", lambda url, timeout: FakeResponse(200))
    status, ms, is_up = monitor.check_url("https://example.com")
    assert status == 200 and is_up == 1 and ms is not None


def test_check_url_marks_500_as_down(monkeypatch):
    monkeypatch.setattr(monitor.requests, "get", lambda url, timeout: FakeResponse(500))
    status, ms, is_up = monitor.check_url("https://example.com")
    assert status == 500 and is_up == 0


def test_check_url_handles_connection_error(monkeypatch):
    def boom(url, timeout):
        raise requests.ConnectionError()
    monkeypatch.setattr(monitor.requests, "get", boom)
    assert monitor.check_url("https://example.com") == (None, None, 0)
