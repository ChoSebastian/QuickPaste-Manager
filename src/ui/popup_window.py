"""QuickPaste 팝업 창 — docs/기본ui-1.png, 기본ui-2.png 레이아웃."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable

from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QCursor, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.models.snippet import Snippet
from src.repositories import category_repository, snippet_repository
from src.services.paste_service import PasteService
from src.ui.widgets.snippet_list_item import (
    LIST_SUMMARY_PREVIEW_LEN,
    SNIPPET_THUMB_PX,
    configure_snippet_list,
    make_snippet_list_item,
)
from src.ui.widgets.draggable_title_bar import DraggableTitleBar
from src.ui.widgets.hover_zone import LEAVE_CHECK_MS, cursor_in_any, widget_global_rect
from src.ui.widgets.snippet_detail_flyout import TOP5_DETAIL_HEADER, SnippetDetailFlyout
from src.ui.widgets.snippet_flyout import SnippetFlyout
from src.ui.popup_flags import popup_window_flags
from src.utils.input_injection import capture_foreground_window, capture_window_at_cursor
from src.utils.paths import get_resources_dir
from src.utils.win_window import raise_window_topmost


def _load_popup_stylesheet() -> str:
    path = get_resources_dir() / "styles" / "popup.qss"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


class PopupWindow(QWidget):
    def __init__(
        self,
        conn: sqlite3.Connection,
        paste_service: PasteService,
        *,
        on_close: Callable[[], None] | None = None,
        on_help: Callable[[], None] | None = None,
        on_open_manager: Callable[[], None] | None = None,
        on_open_settings: Callable[[], None] | None = None,
        close_popup_after_paste: Callable[[], bool] | None = None,
    ) -> None:
        flags = popup_window_flags()
        super().__init__(None, flags)
        self.setObjectName("PopupRoot")
        self._conn = conn
        self._paste_service = paste_service
        self._on_close = on_close
        self._on_help = on_help
        self._on_open_manager = on_open_manager
        self._on_open_settings = on_open_settings
        self._close_popup_after_paste = close_popup_after_paste or (lambda: True)
        self._selected_category_id: int | None = None
        self._target_hwnd: int | None = None
        self._target_poll_timer: QTimer | None = None
        self._pasting = False
        self._panel_width = 300
        self._panel_height = 480

        sheet = _load_popup_stylesheet()
        if sheet:
            self.setStyleSheet(sheet)

        self._flyout: SnippetFlyout | None = None
        self._top_detail: SnippetDetailFlyout | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._title_bar = DraggableTitleBar(
            title="QuickPaste",
            on_close=self._close_popup,
            on_help=self._show_help,
        )
        layout.addWidget(self._title_bar)

        body = QVBoxLayout()
        body.setContentsMargins(8, 8, 8, 8)
        body.setSpacing(6)

        self._search = QLineEdit()
        self._search.setObjectName("SearchEdit")
        self._search.setPlaceholderText("검색")
        self._search.textChanged.connect(self._on_search_changed)
        body.addWidget(self._search)

        top_label = QLabel("Top 5")
        top_label.setObjectName("SectionTitle")
        body.addWidget(top_label)
        self._top_list = QListWidget()
        self._top_list.setObjectName("TopList")
        self._top_list.setMaximumHeight(110)
        configure_snippet_list(self._top_list)
        self._top_list.setMouseTracking(True)
        self._top_list.viewport().setMouseTracking(True)
        self._top_list.itemClicked.connect(self._on_top_item_selected)
        self._top_list.itemEntered.connect(self._on_top_item_entered)
        self._top_list.viewport().installEventFilter(self)
        body.addWidget(self._top_list)

        cat_label = QLabel("카테고리")
        cat_label.setObjectName("SectionTitle")
        body.addWidget(cat_label)
        self._category_list = QListWidget()
        self._category_list.setObjectName("CategoryList")
        self._category_list.setMaximumHeight(120)
        self._category_list.itemClicked.connect(self._on_category_clicked)
        body.addWidget(self._category_list)

        line = QFrame()
        line.setObjectName("SectionLine")
        line.setFrameShape(QFrame.Shape.HLine)
        body.addWidget(line)

        actions = QHBoxLayout()
        actions.setSpacing(6)
        self._btn_add = QPushButton("추가")
        self._btn_edit = QPushButton("수정")
        self._btn_delete = QPushButton("삭제")
        self._btn_settings = QPushButton("설정")
        for btn in (
            self._btn_add,
            self._btn_edit,
            self._btn_delete,
            self._btn_settings,
        ):
            btn.setObjectName("ActionBtn")
            actions.addWidget(btn)
        self._btn_add.clicked.connect(self._on_action_manager)
        self._btn_edit.clicked.connect(self._on_action_manager)
        self._btn_delete.clicked.connect(self._on_action_manager)
        self._btn_settings.clicked.connect(self._on_action_settings)
        body.addLayout(actions)

        layout.addLayout(body)

    def _ensure_top_detail(self) -> SnippetDetailFlyout:
        if self._top_detail is None:
            self._top_detail = SnippetDetailFlyout(
                self._conn,
                on_close=self._reset_top_detail,
            )
            sheet = _load_popup_stylesheet()
            if sheet:
                self._top_detail.setStyleSheet(sheet)
            self._top_detail.installEventFilter(self)
        return self._top_detail

    def _ensure_flyout(self) -> SnippetFlyout:
        if self._flyout is None:
            self._flyout = SnippetFlyout(
                self._conn,
                on_select=self._paste_snippet,
                on_close=self._hide_category_flyout,
            )
            sheet = _load_popup_stylesheet()
            if sheet:
                self._flyout.setStyleSheet(sheet)
        return self._flyout

    def _show_help(self) -> None:
        if self._on_help:
            self._on_help()

    def refresh(self) -> None:
        self._load_top5()
        self._load_categories()

    def show_near_cursor(
        self,
        *,
        offset_px: int = 12,
        width: int = 300,
        height: int = 480,
    ) -> None:
        self._target_hwnd = capture_foreground_window()
        self._reset_top_detail()
        self._hide_category_flyout()

        self._panel_width = width
        self._panel_height = height

        cursor_pos = QCursor.pos()
        screen = QGuiApplication.screenAt(cursor_pos)
        if screen is None:
            self.resize(width, height)
            self.move(cursor_pos.x() + offset_px, cursor_pos.y())
            self._present()
            return

        geo = screen.availableGeometry()
        x = cursor_pos.x() + offset_px
        y = cursor_pos.y()
        if x + width > geo.right():
            x = cursor_pos.x() - width - offset_px
        if y + height > geo.bottom():
            y = max(geo.top(), geo.bottom() - height)

        self.setGeometry(x, y, width, height)
        self._present()

    def _present(self) -> None:
        """즉시 표시 + 최상위 (포커스는 검색창)."""
        self.show()
        self.raise_()
        hwnd = int(self.winId())
        if hwnd:
            raise_window_topmost(hwnd)
        self.activateWindow()
        self._search.setFocus()
        self._update_target_poll_timer()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._update_target_poll_timer()

    def hideEvent(self, event) -> None:  # noqa: N802
        self._stop_target_poll_timer()
        super().hideEvent(event)

    def _update_target_poll_timer(self) -> None:
        if self._close_popup_after_paste():
            self._stop_target_poll_timer()
            return
        if self._target_poll_timer is None:
            self._target_poll_timer = QTimer(self)
            self._target_poll_timer.setInterval(100)
            self._target_poll_timer.timeout.connect(self._sync_external_target_hwnd)
        if self.isVisible():
            self._target_poll_timer.start()

    def _stop_target_poll_timer(self) -> None:
        if self._target_poll_timer is not None:
            self._target_poll_timer.stop()

    def moveEvent(self, event) -> None:  # noqa: N802
        super().moveEvent(event)
        rect = self.frameGeometry()
        if (
            self._flyout is not None
            and self._flyout.isVisible()
        ):
            self._flyout.reposition(rect.right() + 4, rect.top())
        if self._top_detail is not None and self._top_detail.isVisible():
            x, y, _, _ = self._top_detail_anchor()
            self._top_detail.move(x, y)

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self._close_popup()
            return
        super().keyPressEvent(event)

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        if event.type() == QEvent.Type.Leave:
            if obj is self._top_list.viewport():
                QTimer.singleShot(LEAVE_CHECK_MS, self._check_top5_zone)
            elif self._top_detail is not None and obj is self._top_detail:
                QTimer.singleShot(LEAVE_CHECK_MS, self._check_top5_zone)
        return super().eventFilter(obj, event)

    def _top5_zone_rects(self) -> list:
        rects = [widget_global_rect(self._top_list.viewport())]
        if self._top_detail is not None and self._top_detail.isVisible():
            rects.append(self._top_detail.frameGeometry())
        return rects

    def _check_top5_zone(self) -> None:
        if cursor_in_any(QCursor.pos(), self._top5_zone_rects()):
            return
        self._reset_top_detail()

    def _reset_top_detail(self) -> None:
        if self._top_detail is None:
            return
        self._top_detail.reset()
        self._top_list.clearSelection()

    def _on_action_manager(self) -> None:
        self._hide_category_flyout()
        self._reset_top_detail()
        self.hide()
        if self._on_open_manager:
            self._on_open_manager()

    def _on_action_settings(self) -> None:
        self._hide_category_flyout()
        self._reset_top_detail()
        self.hide()
        if self._on_open_settings:
            self._on_open_settings()

    def _hide_category_flyout(self) -> None:
        if self._flyout is not None:
            self._flyout.hide_and_reset()
        self._selected_category_id = None

    def event(self, event) -> bool:  # noqa: N802
        if (
            event.type() == QEvent.Type.WindowDeactivate
            and self.isVisible()
            and not self._pasting
        ):
            if self._close_popup_after_paste():
                QTimer.singleShot(150, self._close_if_focus_lost)
            else:
                self._sync_external_target_hwnd()
                QTimer.singleShot(50, self._sync_external_target_hwnd)
        return super().event(event)

    def _popup_hwnds(self) -> frozenset[int]:
        hwnds: set[int] = set()
        wid = self.winId()
        if wid:
            hwnds.add(int(wid))
        if self._flyout is not None and self._flyout.isVisible():
            fw = self._flyout.winId()
            if fw:
                hwnds.add(int(fw))
            hwnds.update(self._flyout.auxiliary_hwnds())
        if self._top_detail is not None and self._top_detail.isVisible():
            dw = self._top_detail.winId()
            if dw:
                hwnds.add(int(dw))
        return frozenset(hwnds)

    def _sync_external_target_hwnd(self) -> None:
        """팝업 유지 모드: 커서·전경이 우리 UI 밖이면 붙여넣기 대상 HWND 갱신."""
        if not self.isVisible() or self._pasting or self._close_popup_after_paste():
            return

        ours = self._popup_hwnds()
        pos = QCursor.pos()
        over_ours = self.frameGeometry().contains(pos) or self._auxiliary_windows_at(
            pos
        )

        if not over_ours:
            hwnd = capture_window_at_cursor()
            if hwnd and hwnd not in ours:
                self._target_hwnd = hwnd
                return

        hwnd = capture_foreground_window()
        if hwnd and hwnd not in ours:
            self._target_hwnd = hwnd

    def _category_panel_active(self) -> bool:
        return (
            self._selected_category_id is not None
            and self._flyout is not None
            and self._flyout.isVisible()
        )

    def _auxiliary_windows_at(self, pos) -> bool:
        if self._flyout is not None and self._flyout.isVisible():
            if self._flyout.frameGeometry().contains(pos):
                return True
            if self._flyout.auxiliary_contains(pos):
                return True
        if self._top_detail is not None and self._top_detail.isVisible():
            if self._top_detail.frameGeometry().contains(pos):
                return True
        return False

    def _close_if_focus_lost(self) -> None:
        if not self._close_popup_after_paste():
            return
        if not self.isVisible():
            return
        pos = QCursor.pos()
        if self.frameGeometry().contains(pos) or self._auxiliary_windows_at(pos):
            return
        focused = QApplication.focusWidget()
        if focused is not None:
            w = focused.window()
            cat_detail = (
                self._flyout.category_detail_widget()
                if self._flyout is not None
                else None
            )
            if w is self or (self._flyout and w is self._flyout) or (
                self._top_detail and w is self._top_detail
            ) or (cat_detail is not None and w is cat_detail):
                return
        self._close_popup()

    def _close_popup(self) -> None:
        self._stop_target_poll_timer()
        self._hide_category_flyout()
        self._reset_top_detail()
        self.close()
        if self._on_close:
            self._on_close()

    def _load_top5(self) -> None:
        self._top_list.clear()
        inner_w = max(self.width() - 16, self._panel_width - 16)
        for snippet in snippet_repository.top_snippets(self._conn, limit=5):
            self._top_list.addItem(
                make_snippet_list_item(
                    self._conn,
                    snippet,
                    thumb_px=SNIPPET_THUMB_PX,
                    text_preview_len=LIST_SUMMARY_PREVIEW_LEN,
                    panel_width=inner_w,
                )
            )

    def _load_categories(self) -> None:
        self._category_list.clear()
        for cat in category_repository.list_active(self._conn):
            item = QListWidgetItem(cat.name)
            item.setData(Qt.ItemDataRole.UserRole, cat.id)
            self._category_list.addItem(item)

    def _top_detail_anchor(self) -> tuple[int, int, int, int]:
        """Top5 상세 패널 위치·크기 (x, y, width, height)."""
        rect = self.frameGeometry()
        if self._category_panel_active() and self._flyout is not None:
            fly_rect = self._flyout.frameGeometry()
            return (
                fly_rect.right() + 4,
                fly_rect.top(),
                self._panel_width,
                self._panel_height,
            )
        return rect.right() + 4, rect.top(), rect.width(), rect.height()

    def _show_top_detail(self, snippet: Snippet) -> None:
        if self._category_panel_active() and self._flyout is not None:
            self._flyout.reset_detail_panel()
        global_x, global_y, panel_w, panel_h = self._top_detail_anchor()
        detail = self._ensure_top_detail()
        detail.set_header_title(TOP5_DETAIL_HEADER)
        detail.show_snippet(
            snippet,
            global_x=global_x,
            global_y=global_y,
            panel_width=panel_w,
            panel_height=panel_h,
        )
        detail.raise_()
        hwnd = int(detail.winId())
        if hwnd:
            raise_window_topmost(hwnd)

    def _on_top_item_entered(self, item: QListWidgetItem) -> None:
        snippet_id = item.data(Qt.ItemDataRole.UserRole)
        snippet = snippet_repository.get_by_id(self._conn, snippet_id)
        if snippet is not None:
            self._show_top_detail(snippet)

    def _on_category_clicked(self, item: QListWidgetItem) -> None:
        self._reset_top_detail()
        category_id = item.data(Qt.ItemDataRole.UserRole)
        self._selected_category_id = category_id
        self._show_category_flyout(category_id)

    def _show_category_flyout(self, category_id: int) -> None:
        flyout = self._ensure_flyout()
        rect = self.frameGeometry()
        flyout.show_for_category(
            category_id,
            global_x=rect.right() + 4,
            global_y=rect.top(),
            panel_width=rect.width(),
            panel_height=rect.height(),
        )

    def _on_search_changed(self, text: str) -> None:
        if not text.strip():
            self._load_top5()
            self._reset_top_detail()
            self._hide_category_flyout()
            return
        self._reset_top_detail()
        self._hide_category_flyout()
        self._top_list.clear()
        inner_w = max(self.width() - 16, self._panel_width - 16)
        for snippet in snippet_repository.search(self._conn, text.strip()):
            self._top_list.addItem(
                make_snippet_list_item(
                    self._conn,
                    snippet,
                    thumb_px=SNIPPET_THUMB_PX,
                    text_preview_len=LIST_SUMMARY_PREVIEW_LEN,
                    panel_width=inner_w,
                )
            )
        if self._flyout:
            self._flyout.hide_and_reset()

    def _on_top_item_selected(self, item: QListWidgetItem) -> None:
        snippet_id = item.data(Qt.ItemDataRole.UserRole)
        snippet = snippet_repository.get_by_id(self._conn, snippet_id)
        if snippet is not None:
            self._paste_snippet(snippet)

    def _paste_snippet(self, snippet: Snippet) -> None:
        if self._pasting:
            return

        self._sync_external_target_hwnd()
        target_hwnd = self._target_hwnd
        self._pasting = True
        self._set_lists_enabled(False)

        def _paste_then_close() -> None:
            ok = False
            try:
                ok = self._paste_service.paste_snippet(
                    self._conn,
                    snippet,
                    target_hwnd=target_hwnd,
                    show_warning=True,
                )
            finally:
                self._pasting = False
                self._set_lists_enabled(True)
            if ok:
                if self._close_popup_after_paste():
                    self._hide_category_flyout()
                    self._reset_top_detail()
                    self._close_popup()
                else:
                    hwnd = int(self.winId())
                    if hwnd:
                        raise_window_topmost(hwnd)
                    if self._flyout is not None and self._flyout.isVisible():
                        fly_hwnd = int(self._flyout.winId())
                        if fly_hwnd:
                            raise_window_topmost(fly_hwnd)

        QTimer.singleShot(30, _paste_then_close)

    def _set_lists_enabled(self, enabled: bool) -> None:
        self._top_list.setEnabled(enabled)
        self._category_list.setEnabled(enabled)
        self._search.setEnabled(enabled)
