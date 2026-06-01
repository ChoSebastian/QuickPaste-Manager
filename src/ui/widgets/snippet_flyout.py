"""카테고리 클릭 시 우측 상용구 목록(Top5형) + 호버 시 하단 전체 내용."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable

from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.models.snippet import Snippet
from src.repositories import category_repository, snippet_repository
from src.ui.popup_flags import popup_window_flags
from src.ui.widgets.draggable_title_bar import DraggableTitleBar
from src.ui.widgets.hover_zone import LEAVE_CHECK_MS, cursor_in_any, widget_global_rect
from src.ui.widgets.snippet_content_view import (
    apply_snippet_full_content,
    build_image_preview_block,
)
from src.ui.widgets.snippet_list_item import (
    LIST_SUMMARY_PREVIEW_LEN,
    SNIPPET_THUMB_PX,
    configure_snippet_list,
    make_snippet_list_item,
)
from src.utils.win_window import raise_window_topmost

_OPEN_GUARD_MS = 200


class SnippetFlyout(QWidget):
    """주 팝업 우측: Top5와 같은 축약 목록 + 호버 시 하단 전체 내용."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        *,
        on_select: Callable[[Snippet], None],
        main_popup: QWidget | None = None,
        on_dismissed: Callable[[], None] | None = None,
        on_close: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent, popup_window_flags())
        self._conn = conn
        self._on_select = on_select
        self._main_popup = main_popup
        self._on_dismissed = on_dismissed
        self._on_close = on_close
        self._panel_width = 300
        self._panel_height = 480
        self._category_id: int | None = None
        self._suppress_leave_check = False
        self._hover_timer = QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.setInterval(120)
        self._hover_timer.timeout.connect(self._show_full_content_for_hover)
        self._pending_snippet_id: int | None = None

        self.setObjectName("SnippetFlyout")
        self._build_ui()
        self._list.viewport().installEventFilter(self)
        self._content.installEventFilter(self)

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

        self._content = QWidget()
        self._content.setObjectName("PreviewPanel")
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(6, 6, 6, 6)
        content_layout.setSpacing(4)
        self._content_label = QLabel("내용")
        self._content_label.setObjectName("SectionTitle")
        content_layout.addWidget(self._content_label)
        self._image_hint, self._image_scroll, self._content_image = build_image_preview_block(
            self._content,
            object_name="CategoryImagePreviewBlock",
        )
        content_layout.addWidget(self._image_hint)
        content_layout.addWidget(self._image_scroll, stretch=1)
        self._content_text = QTextEdit()
        self._content_text.setObjectName("PreviewText")
        self._content_text.setReadOnly(True)
        content_layout.addWidget(self._content_text, stretch=1)
        self._content.hide()
        body_layout.addWidget(self._content, stretch=0)
        self._root.addWidget(body, stretch=1)
        self._sync_content_layout_stretch()

    def _handle_header_close(self) -> None:
        self.hide_and_reset()
        if self._on_close is not None:
            self._on_close()
        elif self._on_dismissed is not None:
            self._on_dismissed()

    def _sync_content_layout_stretch(self) -> None:
        """내용 패널 숨김 시 리스트가 전체 높이를 쓰도록 stretch 조정."""
        body = self._list.parentWidget()
        if body is None:
            return
        body_layout = body.layout()
        if body_layout is None:
            return
        list_idx = body_layout.indexOf(self._list)
        content_idx = body_layout.indexOf(self._content)
        if self._content.isVisible():
            body_layout.setStretch(list_idx, 1)
            body_layout.setStretch(content_idx, 1)
            list_cap = max(110, int(self._panel_height * 0.45))
            self._list.setMaximumHeight(list_cap)
        else:
            body_layout.setStretch(list_idx, 1)
            body_layout.setStretch(content_idx, 0)
            self._list.setMaximumHeight(16777215)

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        if self._suppress_leave_check:
            return super().eventFilter(obj, event)
        if event.type() == QEvent.Type.Leave:
            if obj is self._list.viewport() or obj is self._content:
                QTimer.singleShot(LEAVE_CHECK_MS, self._check_list_content_zone)
        return super().eventFilter(obj, event)

    def _list_content_zone_rects(self) -> list:
        rects = [widget_global_rect(self._list.viewport())]
        if self._content.isVisible():
            rects.append(widget_global_rect(self._content))
        return rects

    def _check_list_content_zone(self) -> None:
        if self._suppress_leave_check:
            return
        if cursor_in_any(QCursor.pos(), self._list_content_zone_rects()):
            return
        self.reset_content_panel()

    def _check_window_zone(self) -> None:
        if self._suppress_leave_check:
            return
        pos = QCursor.pos()
        if self.frameGeometry().contains(pos):
            return
        if self._main_popup is not None and self._main_popup.frameGeometry().contains(pos):
            return
        self.hide_and_reset()
        if self._on_dismissed is not None:
            self._on_dismissed()

    def reset_content_panel(self) -> None:
        self._hover_timer.stop()
        self._pending_snippet_id = None
        self._content.hide()
        self._content_text.clear()
        self._content_image.clear_preview()
        self._image_scroll.hide()
        self._image_hint.hide()
        self._content_text.show()
        self._list.clearSelection()
        self._sync_content_layout_stretch()

    def hide_and_reset(self) -> None:
        self.reset_content_panel()
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
        self.reset_content_panel()
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
        self._sync_content_layout_stretch()

        self.reposition(global_x, global_y)
        self._present()
        QTimer.singleShot(_OPEN_GUARD_MS, self._end_open_guard)

    def _end_open_guard(self) -> None:
        self._suppress_leave_check = False

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        if not self._suppress_leave_check:
            QTimer.singleShot(LEAVE_CHECK_MS, self._check_window_zone)

    def reposition(self, global_x: int, global_y: int) -> None:
        self.move(global_x, global_y)

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

    def _content_max_size(self) -> tuple[int, int]:
        inner_w = self._panel_width - 32
        list_cap = max(110, int(self._panel_height * 0.45))
        max_h = max(120, self._panel_height - list_cap - 80)
        return inner_w, max_h

    def _show_full_content_for_hover(self) -> None:
        if self._pending_snippet_id is None:
            return
        snippet = snippet_repository.get_by_id(self._conn, self._pending_snippet_id)
        if snippet is None:
            return

        max_w, max_h = self._content_max_size()
        self._content.setFixedWidth(self._panel_width - 16)
        self._content.show()
        self._sync_content_layout_stretch()
        apply_snippet_full_content(
            self._conn,
            snippet,
            text_edit=self._content_text,
            image_label=self._content_image,
            image_scroll=self._image_scroll,
            image_hint=self._image_hint,
            max_width=max_w,
            max_height=max_h,
        )
