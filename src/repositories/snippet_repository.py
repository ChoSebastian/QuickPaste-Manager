"""Snippet repository."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from src.models.snippet import Snippet
from src.repositories.db import utc_now_iso


def _row_to_snippet(row: sqlite3.Row) -> Snippet:
    last_used = row["last_used_at"]
    return Snippet(
        id=row["id"],
        category_id=row["category_id"],
        title=row["title"],
        content_type=row["content_type"],
        body_text=row["body_text"],
        asset_id=row["asset_id"],
        tags=row["tags"],
        use_count=row["use_count"],
        last_used_at=datetime.fromisoformat(last_used) if last_used else None,
        pinned=bool(row["pinned"]),
        active=bool(row["active"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def list_by_category(
    conn: sqlite3.Connection,
    category_id: int,
    *,
    include_inactive: bool = False,
) -> list[Snippet]:
    query = """
        SELECT * FROM snippets
        WHERE category_id = ?
    """
    params: tuple[int, ...] = (category_id,)
    if not include_inactive:
        query += " AND active = 1"
    query += " ORDER BY pinned DESC, title"
    rows = conn.execute(query, params).fetchall()
    return [_row_to_snippet(r) for r in rows]


def get_by_id(conn: sqlite3.Connection, snippet_id: int) -> Snippet | None:
    row = conn.execute(
        "SELECT * FROM snippets WHERE id = ?", (snippet_id,)
    ).fetchone()
    return _row_to_snippet(row) if row else None


def create_text(
    conn: sqlite3.Connection,
    *,
    category_id: int,
    title: str,
    body_text: str,
    tags: str = "",
) -> int:
    now = utc_now_iso()
    cursor = conn.execute(
        """
        INSERT INTO snippets (
            category_id, title, content_type, body_text, tags,
            use_count, pinned, active, created_at, updated_at
        ) VALUES (?, ?, 'text', ?, ?, 0, 0, 1, ?, ?)
        """,
        (category_id, title, body_text, tags, now, now),
    )
    return int(cursor.lastrowid)


def update(
    conn: sqlite3.Connection,
    snippet_id: int,
    *,
    title: str | None = None,
    body_text: str | None = None,
    category_id: int | None = None,
    tags: str | None = None,
    pinned: bool | None = None,
) -> None:
    snippet = get_by_id(conn, snippet_id)
    if snippet is None:
        raise ValueError(f"Snippet not found: {snippet_id}")

    conn.execute(
        """
        UPDATE snippets SET
            title = ?,
            body_text = ?,
            category_id = ?,
            tags = ?,
            pinned = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            title if title is not None else snippet.title,
            body_text if body_text is not None else snippet.body_text,
            category_id if category_id is not None else snippet.category_id,
            tags if tags is not None else snippet.tags,
            int(pinned) if pinned is not None else int(snippet.pinned),
            utc_now_iso(),
            snippet_id,
        ),
    )


def soft_delete(conn: sqlite3.Connection, snippet_id: int) -> None:
    conn.execute(
        "UPDATE snippets SET active = 0, updated_at = ? WHERE id = ?",
        (utc_now_iso(), snippet_id),
    )


def record_usage(conn: sqlite3.Connection, snippet_id: int) -> None:
    now = utc_now_iso()
    conn.execute(
        """
        UPDATE snippets
        SET use_count = use_count + 1, last_used_at = ?, updated_at = ?
        WHERE id = ?
        """,
        (now, now, snippet_id),
    )


def top_snippets(conn: sqlite3.Connection, limit: int = 5) -> list[Snippet]:
    """Top N 상용구 (간단 점수: use_count + pinned 가산)."""
    rows = conn.execute(
        """
        SELECT * FROM snippets
        WHERE active = 1
        ORDER BY pinned DESC, use_count DESC, last_used_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [_row_to_snippet(r) for r in rows]


def search(conn: sqlite3.Connection, keyword: str) -> list[Snippet]:
    pattern = f"%{keyword}%"
    rows = conn.execute(
        """
        SELECT * FROM snippets
        WHERE active = 1
          AND (title LIKE ? OR tags LIKE ? OR body_text LIKE ?)
        ORDER BY pinned DESC, use_count DESC
        LIMIT 50
        """,
        (pattern, pattern, pattern),
    ).fetchall()
    return [_row_to_snippet(r) for r in rows]
