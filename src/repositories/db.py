"""SQLite 연결 및 스키마 초기화."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator

from src.utils.paths import ensure_app_directories, get_db_path

DEFAULT_CATEGORIES: tuple[tuple[str, str], ...] = (
    ("일반", "#4A90D9"),
    ("고객응대", "#50C878"),
    ("이메일", "#F5A623"),
    ("계좌/연락처", "#BD10E0"),
    ("기타", "#9B9B9B"),
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    color TEXT NOT NULL DEFAULT '#4A90D9',
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_type TEXT NOT NULL,
    original_name TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    file_size INTEGER NOT NULL DEFAULT 0,
    sha256 TEXT NOT NULL DEFAULT '',
    width INTEGER,
    height INTEGER,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content_type TEXT NOT NULL DEFAULT 'text',
    body_text TEXT,
    asset_id INTEGER,
    tags TEXT NOT NULL DEFAULT '',
    use_count INTEGER NOT NULL DEFAULT 0,
    last_used_at TEXT,
    pinned INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);

CREATE TABLE IF NOT EXISTS usage_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snippet_id INTEGER NOT NULL,
    used_at TEXT NOT NULL,
    target_window_title TEXT,
    target_process TEXT,
    success INTEGER NOT NULL DEFAULT 1,
    error_code TEXT,
    FOREIGN KEY (snippet_id) REFERENCES snippets(id)
);

CREATE INDEX IF NOT EXISTS idx_snippets_category ON snippets(category_id);
CREATE INDEX IF NOT EXISTS idx_snippets_active ON snippets(active);
CREATE INDEX IF NOT EXISTS idx_usage_events_snippet ON usage_events(snippet_id);
"""


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(tzinfo=None).isoformat(timespec="seconds")


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    ensure_app_directories()
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db_session(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    conn = connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)


def seed_default_categories(conn: sqlite3.Connection) -> int:
    """기본 카테고리 5개를 생성한다. 이미 있으면 건너뛴다."""
    existing = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    if existing > 0:
        return 0

    now = utc_now_iso()
    inserted = 0
    for order, (name, color) in enumerate(DEFAULT_CATEGORIES):
        conn.execute(
            """
            INSERT INTO categories (name, sort_order, color, active, created_at, updated_at)
            VALUES (?, ?, ?, 1, ?, ?)
            """,
            (name, order, color, now, now),
        )
        inserted += 1
    return inserted


def initialize_database(
    *,
    db_path: Path | None = None,
    seed_categories: bool = True,
) -> sqlite3.Connection:
    """DB 스키마를 초기화하고 선택적으로 기본 카테고리를 생성한다."""
    conn = connect(db_path)
    initialize_schema(conn)
    if seed_categories:
        seed_default_categories(conn)
    conn.commit()
    return conn
