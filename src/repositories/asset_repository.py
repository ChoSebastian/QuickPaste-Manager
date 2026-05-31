"""Asset repository."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from src.models.asset import Asset
from src.repositories.db import utc_now_iso


def _row_to_asset(row: sqlite3.Row) -> Asset:
    return Asset(
        id=row["id"],
        asset_type=row["asset_type"],
        original_name=row["original_name"],
        stored_path=row["stored_path"],
        mime_type=row["mime_type"],
        file_size=row["file_size"],
        sha256=row["sha256"],
        width=row["width"],
        height=row["height"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def get_by_id(conn: sqlite3.Connection, asset_id: int) -> Asset | None:
    row = conn.execute(
        "SELECT * FROM assets WHERE id = ?", (asset_id,)
    ).fetchone()
    return _row_to_asset(row) if row else None


def create(
    conn: sqlite3.Connection,
    *,
    asset_type: str,
    original_name: str,
    stored_path: str,
    mime_type: str,
    file_size: int = 0,
    sha256: str = "",
    width: int | None = None,
    height: int | None = None,
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO assets (
            asset_type, original_name, stored_path, mime_type,
            file_size, sha256, width, height, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            asset_type,
            original_name,
            stored_path,
            mime_type,
            file_size,
            sha256,
            width,
            height,
            utc_now_iso(),
        ),
    )
    return int(cursor.lastrowid)
