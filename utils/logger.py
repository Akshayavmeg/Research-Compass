"""
utils/logger.py
================
Persistence layer for conversation logs and recommendations.

Two things are logged:
1. Every query + response turn (conversations table)
2. Every accepted recommendation (recommendations table)

Both are stored in SQLite so they can be queried later (e.g. by an
admin dashboard, or for auditing which recommendations were acted on).
"""

from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Optional

from config import settings

# --- Python-level logging (to file + rotated) ------------------------------

_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    logger = logging.getLogger("research_compass")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if not logger.handlers:
        log_file = settings.logs_dir / "app.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        logger.addHandler(file_handler)

    _logger = logger
    return logger


# --- SQLite persistence -----------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    mode TEXT,
    user_query TEXT NOT NULL,
    response_summary TEXT
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    kind TEXT NOT NULL,
    payload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    recipient TEXT,
    subject TEXT,
    body TEXT,
    sent INTEGER NOT NULL DEFAULT 0
);
"""


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(settings.sqlite_path))
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(_SCHEMA)


def log_conversation(user_query: str, mode: str, response_summary: str) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO conversations (timestamp, mode, user_query, response_summary) VALUES (?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), mode, user_query, response_summary),
        )
    get_logger().info("conversation logged | mode=%s | query=%s", mode, user_query)


def log_recommendation(kind: str, payload: dict[str, Any]) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO recommendations (timestamp, kind, payload) VALUES (?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), kind, json.dumps(payload, default=str)),
        )
    get_logger().info("recommendation logged | kind=%s", kind)


def log_email(recipient: str, subject: str, body: str, sent: bool) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO emails (timestamp, recipient, subject, body, sent) VALUES (?, ?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), recipient, subject, body, int(sent)),
        )
    get_logger().info("email logged | recipient=%s | sent=%s", recipient, sent)
