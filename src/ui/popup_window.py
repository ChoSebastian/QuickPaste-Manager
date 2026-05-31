"""QuickPaste 팝업 창 뼈대."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QGuiApplication
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.models.snippet import Snippet
from src.repositories import category_repository, snippet_repository
from src.services.paste_service import PasteService


class PopupWindow(QWidget):
    def __init__(
        self,
        conn: sqlite3.Connection,
        paste_service: PasteService,
        *,
        on_close: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(flags=Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self._conn = conn
        self._paste_service = paste_service
        self._on_close = on_close
        self._selected_category_id: int | None = None

        self.setWindowTitle("QuickPaste")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self._search = QLineEdit()
        self._search.setPlaceholderText("검색...")
        self._search.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search)

        top_label = QLabel("Top 5")
        top_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(top_label)
        self._top_list = QListWidget()
        self._top_list.setMaximumHeight(100)
        self._top_list.itemDoubleClicked.connect(self._on_item_selected)
        layout.addWidget(self._top_list)

        cat_label = QLabel("카테고리")
        cat_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(cat_label)
        self._category_list = QListWidget()
        self._category_list.setMaximumHeight(80)
        self._category_list.currentItemChanged.connect(self._on_category_changed)
        layout.addWidget(self._category_list)

        snippet_label = QLabel("상용구")
        snippet_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(snippet_label)
        self._snippet_list = QListWidget()
        self._snippet_list.itemDoubleClicked.connect(self._on_item_selected)
        layout.addWidget(self._snippet_list)

        actions = QHBoxLayout()
        for label in ("추가", "수정", "삭제", "설정"):
            btn = QPushButton(label)
            btn.setEnabled(False)  # TODO: 팝업 내 빠른 액션
            actions.addWidget(btn)
        layout.addLayout(actions)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line)

    def refresh(self) -> None:
        self._load_top5()
        self._load_categories()
        if self._selected_category_id:
            self._load_snippets(self._selected_category_id)

    def show_near_cursor(
        self,
        *,
        offset_px: int = 12,
        width: int = 360,
        height: int = 520,
    ) -> None:
        cursor_pos = QCursor.pos()
        screen = QGuiApplication.screenAt(cursor_pos)
        if screen is None:
            self.resize(width, height)
            self.move(cursor_pos.x() + offset_px, cursor_pos.y())
            self.show()
            return

        geo = screen.availableGeometry()
        x = cursor_pos.x() + offset_px
        y = cursor_pos.y()

        if x + width > geo.right():
            x = cursor_pos.x() - width - offset_px
        if y + height > geo.bottom():
            y = geo.bottom() - height

        self.setGeometry(x, y, width, height)
        self.show()
        self._search.setFocus()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            if self._on_close:
                self._on_close()
            return
        super().keyPressEvent(event)

    def _load_top5(self) -> None:
        self._top_list.clear()
        for snippet in snippet_repository.top_snippets(self._conn, limit=5):
            self._top_list.addItem(self._make_item(snippet))

    def _load_categories(self) -> None:
        self._category_list.clear()
        categories = category_repository.list_active(self._conn)
        for cat in categories:
            item = QListWidgetItem(cat.name)
            item.setData(Qt.ItemDataRole.UserRole, cat.id)
            self._category_list.addItem(item)
        if categories:
            self._category_list.setCurrentRow(0)

    def _load_snippets(self, category_id: int) -> None:
        self._snippet_list.clear()
        for snippet in snippet_repository.list_by_category(self._conn, category_id):
            self._snippet_list.addItem(self._make_item(snippet))

    def _make_item(self, snippet: Snippet) -> QListWidgetItem:
        preview = (snippet.body_text or "")[:60]
        label = f"{snippet.title}"
        if preview:
            label += f" — {preview}"
        item = QListWidgetItem(label)
        item.setData(Qt.ItemDataRole.UserRole, snippet.id)
        return item

    def _on_category_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if current is None:
            return
        category_id = current.data(Qt.ItemDataRole.UserRole)
        self._selected_category_id = category_id
        self._load_snippets(category_id)

    def _on_search_changed(self, text: str) -> None:
        self._snippet_list.clear()
        if not text.strip():
            if self._selected_category_id:
                self._load_snippets(self._selected_category_id)
            return
        for snippet in snippet_repository.search(self._conn, text.strip()):
            self._snippet_list.addItem(self._make_item(snippet))

    def _on_item_selected(self, item: QListWidgetItem) -> None:
        snippet_id = item.data(Qt.ItemDataRole.UserRole)
        snippet = snippet_repository.get_by_id(self._conn, snippet_id)
        if snippet is None:
            return
        self._paste_service.paste_snippet(self._conn, snippet)
        self.close()
        if self._on_close:
            self._on_close()
