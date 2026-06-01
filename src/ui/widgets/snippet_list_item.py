"""상용구 목록 항목(텍스트·이미지 썸네일) 공통."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from src.models.snippet import Snippet
from src.repositories import asset_repository

SNIPPET_THUMB_PX = 44
LIST_SUMMARY_PREVIEW_LEN = 50


def configure_snippet_list(widget: QListWidget, *, thumb_px: int = SNIPPET_THUMB_PX) -> None:
    widget.setIconSize(QSize(thumb_px, thumb_px))


def thumbnail_pixmap(path: Path, size_px: int) -> QPixmap:
    pix = QPixmap(str(path))
    if pix.isNull():
        return QPixmap()
    return pix.scaled(
        size_px,
        size_px,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def scaled_preview_pixmap(pix: QPixmap, *, max_width: int, max_height: int) -> QPixmap:
    if pix.isNull():
        return pix
    return pix.scaled(
        max_width,
        max_height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def _image_asset_path(conn: sqlite3.Connection, snippet: Snippet) -> Path | None:
    if snippet.content_type != "image" or not snippet.asset_id:
        return None
    asset = asset_repository.get_by_id(conn, snippet.asset_id)
    if asset is None:
        return None
    path = Path(asset.stored_path)
    return path if path.exists() else None


def make_snippet_list_item(
    conn: sqlite3.Connection,
    snippet: Snippet,
    *,
    thumb_px: int = SNIPPET_THUMB_PX,
    text_preview_len: int = 50,
    panel_width: int | None = None,
) -> QListWidgetItem:
    """Top5·플라이아웃 공통 리스트 항목."""
    if snippet.content_type == "image":
        label = snippet.title or "이미지"
        asset_path = _image_asset_path(conn, snippet)
        if asset_path is not None:
            thumb = thumbnail_pixmap(asset_path, thumb_px)
            if not thumb.isNull():
                item = QListWidgetItem(QIcon(thumb), label)
                row_h = thumb_px + 12
                if panel_width:
                    item.setSizeHint(QSize(panel_width - 12, row_h))
                else:
                    item.setSizeHint(QSize(thumb_px + 120, row_h))
                item.setData(Qt.ItemDataRole.UserRole, snippet.id)
                if snippet.pinned:
                    item.setText(f"📌 {label}")
                return item
        label = f"🖼 {label}"
    else:
        body = (snippet.body_text or "").replace("\n", " ")
        preview = body[:text_preview_len] + ("..." if len(body) > text_preview_len else "")
        label = f"{snippet.title}\n{preview}" if preview else snippet.title

    if snippet.pinned:
        label = f"📌 {label}"

    item = QListWidgetItem(label)
    if panel_width:
        item.setSizeHint(QSize(panel_width - 12, 36 if "\n" not in label else 52))
    item.setData(Qt.ItemDataRole.UserRole, snippet.id)
    return item
