"""Usage event repository."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from src.models.usage_event import UsageEvent
from src.repositories.db import utc_now_iso


def _row_to_event(row: sqlite3.Row) -> UsageEvent:
    return UsageEvent(
        id=row["id"],
        snippet_id=row["snippet_id"],
        used_at=datetime.fromisoformat(row["used_at"]),
        target_window_title=row["target_window_title"],
        target_process=row["target_process"],
        success=bool(row["success"]),
        error_code=row["error_code"],
    )


def record(
    conn: sqlite3.Connection,
    *,
    snippet_id: int,
    success: bool = True,
    error_code: str | None = None,
    target_window_title: str | None = None,
    target_process: str | None = None,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO usage_events (
            snippet_id, used_at, target_window_title, target_process,
            success, error_code
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            snippet_id,
            utc_now_iso(),
            target_window_title,
            target_process,
            int(success),
            error_code,
        ),
    )
    return int(cursor.lastrowid)


def list_by_snippet(
    conn: sqlite3.Connection,
    snippet_id: int,
    *,
    limit: int = 100,
) -> list[UsageEvent]:
    rows = conn.execute(
        """
        SELECT * FROM usage_events
        WHERE snippet_id = ?
        ORDER BY used_at DESC
        LIMIT ?
        """,
        (snippet_id, limit),
    ).fetchall()
    return [_row_to_event(r) for r in rows]
