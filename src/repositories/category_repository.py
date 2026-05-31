"""Category repository."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from src.models.category import Category
from src.repositories.db import utc_now_iso


def _row_to_category(row: sqlite3.Row) -> Category:
    return Category(
        id=row["id"],
        name=row["name"],
        sort_order=row["sort_order"],
        color=row["color"],
        active=bool(row["active"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def list_active(conn: sqlite3.Connection) -> list[Category]:
    rows = conn.execute(
        """
        SELECT * FROM categories
        WHERE active = 1
        ORDER BY sort_order, name
        """
    ).fetchall()
    return [_row_to_category(r) for r in rows]


def list_all(conn: sqlite3.Connection) -> list[Category]:
    rows = conn.execute(
        "SELECT * FROM categories ORDER BY sort_order, name"
    ).fetchall()
    return [_row_to_category(r) for r in rows]


def get_by_id(conn: sqlite3.Connection, category_id: int) -> Category | None:
    row = conn.execute(
        "SELECT * FROM categories WHERE id = ?", (category_id,)
    ).fetchone()
    return _row_to_category(row) if row else None


def create(
    conn: sqlite3.Connection,
    *,
    name: str,
    sort_order: int = 0,
    color: str = "#4A90D9",
) -> int:
    now = utc_now_iso()
    cursor = conn.execute(
        """
        INSERT INTO categories (name, sort_order, color, active, created_at, updated_at)
        VALUES (?, ?, ?, 1, ?, ?)
        """,
        (name, sort_order, color, now, now),
    )
    return int(cursor.lastrowid)


def update_name(conn: sqlite3.Connection, category_id: int, name: str) -> None:
    conn.execute(
        "UPDATE categories SET name = ?, updated_at = ? WHERE id = ?",
        (name, utc_now_iso(), category_id),
    )


def soft_delete(conn: sqlite3.Connection, category_id: int) -> None:
    conn.execute(
        "UPDATE categories SET active = 0, updated_at = ? WHERE id = ?",
        (utc_now_iso(), category_id),
    )
