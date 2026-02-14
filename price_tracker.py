"""
SQLite-backed price history and deal detection.
"""

import sqlite3
import logging
from datetime import date, datetime
from statistics import median
from pathlib import Path
import config

log = logging.getLogger(__name__)


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            depart_date TEXT NOT NULL,
            return_date TEXT NOT NULL,
            total_price REAL NOT NULL,
            per_person_price REAL NOT NULL,
            checked_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts_sent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            depart_date TEXT NOT NULL,
            return_date TEXT NOT NULL,
            per_person_price REAL NOT NULL,
            sent_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def record_price(depart_date: date, return_date: date,
                 total_price: float, per_person_price: float):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO prices (depart_date, return_date, total_price, per_person_price, checked_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (depart_date.isoformat(), return_date.isoformat(),
         total_price, per_person_price, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_price_history(depart_date: date, return_date: date) -> list[float]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT per_person_price FROM prices "
        "WHERE depart_date = ? AND return_date = ? ORDER BY checked_at",
        (depart_date.isoformat(), return_date.isoformat()),
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


def is_deal(depart_date: date, return_date: date, per_person_price: float) -> tuple[bool, str]:
    """
    Check if a price qualifies as a deal.
    Returns (is_deal, reason_string).
    """
    # Absolute threshold
    if per_person_price < config.ABSOLUTE_THRESHOLD:
        return True, f"${per_person_price:.0f}/person is under ${config.ABSOLUTE_THRESHOLD} threshold"

    # Relative threshold (need enough history)
    history = get_price_history(depart_date, return_date)
    if len(history) >= config.MIN_DATA_POINTS:
        med = median(history)
        drop_target = med * (1 - config.RELATIVE_DROP_PCT)
        if per_person_price <= drop_target:
            return True, (
                f"${per_person_price:.0f}/person is {config.RELATIVE_DROP_PCT*100:.0f}%+ "
                f"below median ${med:.0f}"
            )

    return False, ""


def already_alerted_today(depart_date: date, return_date: date) -> bool:
    conn = _get_conn()
    today = date.today().isoformat()
    row = conn.execute(
        "SELECT COUNT(*) FROM alerts_sent "
        "WHERE depart_date = ? AND return_date = ? AND sent_at LIKE ?",
        (depart_date.isoformat(), return_date.isoformat(), f"{today}%"),
    ).fetchone()
    conn.close()
    return row[0] > 0


def mark_alerted(depart_date: date, return_date: date, per_person_price: float):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO alerts_sent (depart_date, return_date, per_person_price, sent_at) "
        "VALUES (?, ?, ?, ?)",
        (depart_date.isoformat(), return_date.isoformat(),
         per_person_price, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
