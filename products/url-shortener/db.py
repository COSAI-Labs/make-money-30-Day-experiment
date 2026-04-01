"""URL Shortener database module using SQLite."""
import sqlite3
import os
import string
import random
from datetime import datetime, timezone
from pathlib import Path

DB_DIR = Path(__file__).parent / "data"
DB_PATH = DB_DIR / "urls.db"


def get_db():
    DB_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            long_url TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            creator_ip TEXT,
            click_count INTEGER DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_short_code ON urls(short_code);

        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url_id INTEGER NOT NULL,
            clicked_at TEXT NOT NULL DEFAULT (datetime('now')),
            ip TEXT,
            user_agent TEXT,
            referer TEXT,
            country TEXT,
            FOREIGN KEY (url_id) REFERENCES urls(id)
        );
        CREATE INDEX IF NOT EXISTS idx_clicks_url ON clicks(url_id);
        CREATE INDEX IF NOT EXISTS idx_clicks_time ON clicks(clicked_at);
    """)
    conn.commit()
    conn.close()


def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def create_short_url(long_url, creator_ip=None, custom_code=None):
    conn = get_db()
    code = custom_code or generate_code()
    # Ensure uniqueness
    while True:
        existing = conn.execute("SELECT id FROM urls WHERE short_code = ?", (code,)).fetchone()
        if not existing:
            break
        code = generate_code()

    conn.execute(
        "INSERT INTO urls (short_code, long_url, creator_ip) VALUES (?, ?, ?)",
        (code, long_url, creator_ip),
    )
    conn.commit()
    conn.close()
    return code


def get_url(short_code):
    conn = get_db()
    row = conn.execute("SELECT * FROM urls WHERE short_code = ?", (short_code,)).fetchone()
    conn.close()
    return dict(row) if row else None


def record_click(url_id, ip=None, user_agent=None, referer=None):
    conn = get_db()
    conn.execute(
        "INSERT INTO clicks (url_id, ip, user_agent, referer) VALUES (?, ?, ?, ?)",
        (url_id, ip, user_agent, referer),
    )
    conn.execute("UPDATE urls SET click_count = click_count + 1 WHERE id = ?", (url_id,))
    conn.commit()
    conn.close()


def get_url_stats(short_code):
    conn = get_db()
    url = conn.execute("SELECT * FROM urls WHERE short_code = ?", (short_code,)).fetchone()
    if not url:
        conn.close()
        return None

    clicks = conn.execute(
        "SELECT clicked_at, referer, user_agent FROM clicks WHERE url_id = ? ORDER BY clicked_at DESC LIMIT 50",
        (url["id"],),
    ).fetchall()

    # Click counts by day (last 7 days)
    daily = conn.execute("""
        SELECT date(clicked_at) as day, COUNT(*) as count
        FROM clicks WHERE url_id = ? AND clicked_at > datetime('now', '-7 days')
        GROUP BY date(clicked_at) ORDER BY day
    """, (url["id"],)).fetchall()

    # Top referers
    referers = conn.execute("""
        SELECT referer, COUNT(*) as count FROM clicks
        WHERE url_id = ? AND referer IS NOT NULL AND referer != ''
        GROUP BY referer ORDER BY count DESC LIMIT 10
    """, (url["id"],)).fetchall()

    conn.close()
    return {
        "url": dict(url),
        "recent_clicks": [dict(c) for c in clicks],
        "daily_clicks": [dict(d) for d in daily],
        "top_referers": [dict(r) for r in referers],
    }


# Initialize on import
init_db()
