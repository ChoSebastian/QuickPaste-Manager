"""카테고리 클릭 시 우측 상용구 목록 + 호버 시 목록 우측 전체 내용.

카테고리 목록 창은 헤더 닫기(×) 또는 주 팝업 닫기·검색 등으로만 닫힌다.
마우스가 창 밖으로 나가도 자동으로 닫히지 않는다.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable

from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from src.models.snippet import Snippet
from src.repositories import category_repository, snippet_repository
from src.ui.popup_flags import popup_window_flags
from src.ui.widgets.draggable_title_bar import DraggableTitleBar
from src.ui.widgets.hover_zone import LEAVE_CHECK_MS, cursor_in_any, widget_global_rect
from src.ui.widgets.snippet_detail_flyout import SnippetDetailFlyout
from src.ui.widgets.snippet_list_item import (
    LIST_SUMMARY_PREVIEW_LEN,
    SNIPPET_THUMB_PX,
    configure_snippet_list,
    make_snippet_list_item,
)
from src.utils.paths import get_resources_dir
from src.utils.win_window import raise_window_topmost

_OPEN_GUARD_MS = 200
_CATEGORY_DETAIL_HEADER = "상용구 전체 내용"
_DETAIL_GAP_PX = 4


def _load_popup_stylesheet() -> str:
    path = get_resources_dir() / "styles" / "popup.qss"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


class SnippetFlyout(QWidget):
    """주 팝업 우측: 축약 목록 + 호버 시 목록 우측 전체 내용 패널."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        *,
        on_select: Callable[[Snippet], None],
        on_close: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent, popup_window_flags())
        self._conn = conn
        self._on_select = on_select
        self._on_close = on_close
        self._panel_width = 300
        self._panel_height = 480
        self._category_id: int | None = None
        self._suppress_leave_check = False
        self._detail: SnippetDetailFlyout | None = None
        self._hover_timer = QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.setInterval(120)
        self._hover_timer.timeout.connect(self._show_full_content_for_hover)
        self._pending_snippet_id: int | None = None

        self.setObjectName("SnippetFlyout")
        self._build_ui()
        self._list.viewport().installEventFilter(self)

    def _build_ui(self) -> None:
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        self._header = DraggableTitleBar(
            title="상용구",
            on_close=self._handle_header_close,
        )
        self._root.addWidget(self._header)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(8, 8, 8, 8)
        body_layout.setSpacing(6)

        self._list = QListWidget()
        self._list.setObjectName("SnippetFlyoutList")
        configure_snippet_list(self._list)
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.itemEntered.connect(self._on_item_entered)
        self._list.setMouseTracking(True)
        self._list.viewport().setMouseTracking(True)
        body_layout.addWidget(self._list, stretch=1)
        self._root.addWidget(body, stretch=1)

    def _ensure_detail(self) -> SnippetDetailFlyout:
        if self._detail is None:
            self._detail = SnippetDetailFlyout(
                self._conn,
                on_close=self._reset_detail_panel,
            )
            sheet = _load_popup_stylesheet()
            if sheet:
                self._detail.setStyleSheet(sheet)
            self._detail.installEventFilter(self)
        return self._detail

    def auxiliary_hwnds(self) -> frozenset[int]:
        hwnds: set[int] = set()
        if self._detail is not None and self._detail.isVisible():
            wid = self._detail.winId()
            if wid:
                hwnds.add(int(wid))
        return frozenset(hwnds)

    def category_detail_widget(self) -> SnippetDetailFlyout | None:
        if self._detail is not None and self._detail.isVisible():
            return self._detail
        return None

    def auxiliary_contains(self, pos) -> bool:
        detail = self.category_detail_widget()
        if detail is not None and detail.frameGeometry().contains(pos):
            return True
        return False

    def _handle_header_close(self) -> None:
        self.hide_and_reset()
        if self._on_close is not None:
            self._on_close()

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        if self._suppress_leave_check:
            return super().eventFilter(obj, event)
        if event.type() == QEvent.Type.Leave:
            if obj is self._list.viewport() or (
                self._detail is not None and obj is self._detail
            ):
                QTimer.singleShot(LEAVE_CHECK_MS, self._check_list_detail_zone)
        return super().eventFilter(obj, event)

    def _list_detail_zone_rects(self) -> list:
        rects = [widget_global_rect(self._list.viewport())]
        if self._detail is not None and self._detail.isVisible():
            rects.append(self._detail.frameGeometry())
        return rects

    def _check_list_detail_zone(self) -> None:
        if self._suppress_leave_check:
            return
        if cursor_in_any(QCursor.pos(), self._list_detail_zone_rects()):
            return
        self._reset_detail_panel()

    def reset_detail_panel(self) -> None:
        """카테고리 상세 패널만 닫는다(목록 창은 유지)."""
        self._reset_detail_panel()

    def _reset_detail_panel(self) -> None:
        self._hover_timer.stop()
        self._pending_snippet_id = None
        if self._detail is not None:
            self._detail.reset()
        self._list.clearSelection()

    def hide_and_reset(self) -> None:
        self._reset_detail_panel()
        self._list.clear()
        self._category_id = None
        self.hide()

    def show_for_category(
        self,
        category_id: int,
        *,
        global_x: int,
        global_y: int,
        panel_width: int,
        panel_height: int,
    ) -> None:
        self._suppress_leave_check = True
        self._reset_detail_panel()
        self._category_id = category_id
        self._panel_width = max(panel_width, 200)
        self._panel_height = max(panel_height, 200)
        self.setFixedSize(self._panel_width, self._panel_height)

        category = category_repository.get_by_id(self._conn, category_id)
        cat_name = category.name if category is not None else "카테고리"
        self._header.set_title(f"{cat_name} 상용구")

        inner_w = self._panel_width - 16
        self._list.clear()
        snippets = snippet_repository.list_by_category(self._conn, category_id)
        for snippet in snippets:
            self._list.addItem(
                make_snippet_list_item(
                    self._conn,
                    snippet,
                    thumb_px=SNIPPET_THUMB_PX,
                    text_preview_len=LIST_SUMMARY_PREVIEW_LEN,
                    panel_width=inner_w,
                )
            )
        self._list.setCurrentRow(-1)

        self.reposition(global_x, global_y)
        self._present()
        QTimer.singleShot(_OPEN_GUARD_MS, self._end_open_guard)

    def _end_open_guard(self) -> None:
        self._suppress_leave_check = False

    def reposition(self, global_x: int, global_y: int) -> None:
        self.move(global_x, global_y)
        self._reposition_detail_panel()

    def moveEvent(self, event) -> None:  # noqa: N802
        super().moveEvent(event)
        self._reposition_detail_panel()

    def _reposition_detail_panel(self) -> None:
        if self._detail is None or not self._detail.isVisible():
            return
        rect = self.frameGeometry()
        self._detail.move(rect.right() + _DETAIL_GAP_PX, rect.top())

    def _present(self) -> None:
        self.show()
        self.raise_()
        hwnd = int(self.winId())
        if hwnd:
            raise_window_topmost(hwnd)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        snippet_id = item.data(Qt.ItemDataRole.UserRole)
        snippet = snippet_repository.get_by_id(self._conn, snippet_id)
        if snippet is not None:
            self._on_select(snippet)

    def _on_item_entered(self, item: QListWidgetItem) -> None:
        if self._suppress_leave_check:
            return
        self._pending_snippet_id = item.data(Qt.ItemDataRole.UserRole)
        self._hover_timer.start()

    def _show_full_content_for_hover(self) -> None:
        if self._pending_snippet_id is None:
            return
        snippet = snippet_repository.get_by_id(self._conn, self._pending_snippet_id)
        if snippet is None:
            return

        detail = self._ensure_detail()
        detail.set_header_title(_CATEGORY_DETAIL_HEADER)
        rect = self.frameGeometry()
        detail.show_snippet(
            snippet,
            global_x=rect.right() + _DETAIL_GAP_PX,
            global_y=rect.top(),
            panel_width=self._panel_width,
            panel_height=self._panel_height,
        )
