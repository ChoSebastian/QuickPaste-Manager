"""상용구 전체 내용(텍스트·이미지) 표시 공통."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QScrollArea, QTextEdit, QVBoxLayout, QWidget

from src.models.snippet import Snippet
from src.repositories import asset_repository
from src.ui.widgets.clickable_image_label import ClickableImageLabel
from src.ui.widgets.snippet_list_item import scaled_preview_pixmap


def apply_snippet_full_content(
    conn: sqlite3.Connection,
    snippet: Snippet,
    *,
    text_edit: QTextEdit,
    image_label: ClickableImageLabel,
    image_scroll: QScrollArea,
    image_hint: QLabel | None,
    max_width: int,
    max_height: int,
) -> None:
    """텍스트는 전체 본문, 이미지는 스크롤 영역 안 미리보기(클릭 시 원본 열기)."""
    text_edit.hide()
    image_label.clear_preview()
    image_scroll.hide()
    if image_hint is not None:
        image_hint.hide()

    if snippet.content_type == "image" and snippet.asset_id:
        asset = asset_repository.get_by_id(conn, snippet.asset_id)
        if asset:
            source = Path(asset.stored_path)
            pix = QPixmap(str(source))
            if not pix.isNull():
                scaled = scaled_preview_pixmap(
                    pix,
                    max_width=max_width,
                    max_height=max_height,
                )
                image_label.set_preview(scaled, source)
                image_scroll.show()
                if image_hint is not None:
                    image_hint.show()
                return

    text_edit.setPlainText(snippet.body_text or "(내용 없음)")
    text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    text_edit.setMinimumHeight(min(max_height, 80))
    text_edit.setMaximumHeight(max_height)
    text_edit.show()


def build_image_preview_block(
    parent: QWidget,
    *,
    object_name: str = "ImagePreviewBlock",
) -> tuple[QLabel, QScrollArea, ClickableImageLabel]:
    """이미지 미리보기(힌트 + 스크롤 + 클릭 라벨) 블록."""
    block = QWidget(parent)
    block.setObjectName(object_name)
    layout = QVBoxLayout(block)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)

    hint = QLabel("클릭하면 원본 이미지가 열립니다.")
    hint.setObjectName("ImageOpenHint")
    hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
    hint.hide()
    layout.addWidget(hint)

    scroll = QScrollArea()
    scroll.setObjectName("ImagePreviewScroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.hide()

    holder = QWidget()
    holder.setObjectName("PreviewPanel")
    holder_layout = QVBoxLayout(holder)
    holder_layout.setContentsMargins(8, 8, 8, 8)
    holder_layout.addStretch()
    image_label = ClickableImageLabel()
    holder_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)
    holder_layout.addStretch()
    scroll.setWidget(holder)
    layout.addWidget(scroll, stretch=1)

    return hint, scroll, image_label
