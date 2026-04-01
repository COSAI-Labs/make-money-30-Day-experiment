"""
PingPulse - Lightweight uptime monitoring service.
Stores check results in SQLite. Serves dashboard and API.
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx

DB_PATH = Path(__file__).parent / "data" / "monitors.db"


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS monitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            interval_seconds INTEGER DEFAULT 300,
            expected_status INTEGER DEFAULT 200,
            enabled INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monitor_id INTEGER NOT NULL,
            status_code INTEGER,
            response_time_ms INTEGER,
            is_up INTEGER NOT NULL,
            error TEXT,
            checked_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (monitor_id) REFERENCES monitors(id)
        );
        CREATE INDEX IF NOT EXISTS idx_checks_monitor ON checks(monitor_id, checked_at);
    """)
    conn.close()


async def check_url(url: str, expected_status: int = 200, timeout: int = 10):
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "PingPulse/1.0"})
        elapsed_ms = int((time.time() - start) * 1000)
        is_up = resp.status_code == expected_status
        return {
            "status_code": resp.status_code,
            "response_time_ms": elapsed_ms,
            "is_up": is_up,
            "error": None if is_up else f"Expected {expected_status}, got {resp.status_code}",
        }
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        return {
            "status_code": None,
            "response_time_ms": elapsed_ms,
            "is_up": False,
            "error": str(e),
        }


async def run_checks():
    """Run checks for all enabled monitors."""
    conn = get_db()
    monitors = conn.execute("SELECT * FROM monitors WHERE enabled = 1").fetchall()

    for mon in monitors:
        result = await check_url(mon["url"], mon["expected_status"])
        conn.execute(
            "INSERT INTO checks (monitor_id, status_code, response_time_ms, is_up, error) VALUES (?, ?, ?, ?, ?)",
            (mon["id"], result["status_code"], result["response_time_ms"], result["is_up"], result["error"]),
        )
    conn.commit()

    # Clean up old checks (keep last 30 days)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    conn.execute("DELETE FROM checks WHERE checked_at < ?", (cutoff,))
    conn.commit()
    conn.close()

    return len(monitors)


def get_monitor_stats(monitor_id: int, hours: int = 24):
    """Get uptime stats for a monitor over the last N hours."""
    conn = get_db()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

    checks = conn.execute(
        "SELECT * FROM checks WHERE monitor_id = ? AND checked_at >= ? ORDER BY checked_at DESC",
        (monitor_id, cutoff),
    ).fetchall()

    if not checks:
        return {"uptime_pct": None, "avg_response_ms": None, "total_checks": 0, "checks": []}

    up_count = sum(1 for c in checks if c["is_up"])
    total = len(checks)
    avg_resp = sum(c["response_time_ms"] for c in checks if c["response_time_ms"]) / max(total, 1)

    return {
        "uptime_pct": round(up_count / total * 100, 2),
        "avg_response_ms": round(avg_resp),
        "total_checks": total,
        "up_count": up_count,
        "down_count": total - up_count,
        "last_check": dict(checks[0]) if checks else None,
        "checks": [dict(c) for c in checks[:50]],
    }


# Initialize DB on import
init_db()
