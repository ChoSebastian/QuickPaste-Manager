"""Top5 호버 시 주 팝업 우측 전체 내용 패널."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable

from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from src.models.snippet import Snippet
from src.ui.popup_flags import popup_window_flags
from src.ui.widgets.draggable_title_bar import DraggableTitleBar
from src.ui.widgets.snippet_content_view import (
    apply_snippet_full_content,
    build_image_preview_block,
)
from src.utils.win_window import raise_window_topmost

TOP5_DETAIL_HEADER = "Top 5 상용구 내용"


class SnippetDetailFlyout(QWidget):
    def __init__(
        self,
        conn: sqlite3.Connection,
        *,
        on_close: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent, popup_window_flags())
        self._conn = conn
        self._on_close = on_close
        self._panel_width = 300
        self._panel_height = 480
        self.setObjectName("SnippetDetailFlyout")
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._header = DraggableTitleBar(
            title=TOP5_DETAIL_HEADER,
            on_close=self._handle_close,
        )
        root.addWidget(self._header)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(8, 8, 8, 8)
        body_layout.setSpacing(6)

        self._snippet_title = QLabel()
        self._snippet_title.setObjectName("SectionTitle")
        self._snippet_title.setWordWrap(True)
        body_layout.addWidget(self._snippet_title)

        self._image_hint, self._image_scroll, self._image = build_image_preview_block(
            body,
            object_name="Top5ImagePreviewBlock",
        )
        body_layout.addWidget(self._image_hint)
        body_layout.addWidget(self._image_scroll, stretch=1)

        self._text = QTextEdit()
        self._text.setObjectName("PreviewText")
        self._text.setReadOnly(True)
        body_layout.addWidget(self._text, stretch=1)

        root.addWidget(body, stretch=1)

    def _handle_close(self) -> None:
        self.reset()
        if self._on_close is not None:
            self._on_close()

    def reset(self) -> None:
        """다음 호버를 위해 내용·표시 상태를 초기화한다."""
        self._snippet_title.clear()
        self._text.clear()
        self._image.clear_preview()
        self._image_scroll.hide()
        self._image_hint.hide()
        self._text.show()
        self.hide()

    def show_snippet(
        self,
        snippet: Snippet,
        *,
        global_x: int,
        global_y: int,
        panel_width: int,
        panel_height: int,
    ) -> None:
        self._panel_width = max(panel_width, 200)
        self._panel_height = max(panel_height, 200)
        self.setFixedSize(self._panel_width, self._panel_height)

        title = snippet.title or "(제목 없음)"
        if snippet.pinned:
            title = f"📌 {title}"
        self._snippet_title.setText(title)

        inner_w = self._panel_width - 48
        inner_h = self._panel_height - 120
        apply_snippet_full_content(
            self._conn,
            snippet,
            text_edit=self._text,
            image_label=self._image,
            image_scroll=self._image_scroll,
            image_hint=self._image_hint,
            max_width=inner_w,
            max_height=inner_h,
        )

        self.move(global_x, global_y)
        self.show()
        self.raise_()
        hwnd = int(self.winId())
        if hwnd:
            raise_window_topmost(hwnd)
