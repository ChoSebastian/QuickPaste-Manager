"""카테고리 열림 시 Top5 호버·상세·붙여넣기 동작."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import QRect

from src.repositories.db import initialize_database
from src.ui.popup_window import PopupWindow
from src.ui.widgets.snippet_detail_flyout import TOP5_DETAIL_HEADER


@pytest.fixture
def popup(qtbot, tmp_path):
    conn = initialize_database(db_path=tmp_path / "test.db", seed_categories=True)
    paste = MagicMock()
    window = PopupWindow(conn, paste)
    qtbot.addWidget(window)
    window.show()
    yield window
    conn.close()


def test_top5_detail_anchor_right_of_category_flyout(popup):
    popup._panel_width = 300
    popup._panel_height = 480
    popup._selected_category_id = 1
    flyout = MagicMock()
    flyout.isVisible.return_value = True
    flyout.frameGeometry.return_value = QRect(400, 100, 300, 480)
    popup._flyout = flyout

    fly_rect = flyout.frameGeometry()
    x, y, w, h = popup._top_detail_anchor()

    assert x == fly_rect.right() + 4
    assert y == 100
    assert w == 300
    assert h == 480


def test_top5_hover_shows_detail_when_category_flyout_active(popup):
    popup._selected_category_id = 1
    flyout = MagicMock()
    flyout.isVisible.return_value = True
    flyout.frameGeometry.return_value = QRect(400, 100, 300, 480)
    flyout.reset_detail_panel = MagicMock()
    popup._flyout = flyout

    snippet = MagicMock()
    detail = MagicMock()
    with patch.object(popup, "_ensure_top_detail", return_value=detail):
        popup._show_top_detail(snippet)

    flyout.reset_detail_panel.assert_called_once()
    detail.set_header_title.assert_called_once_with(TOP5_DETAIL_HEADER)
    detail.show_snippet.assert_called_once()
    assert detail.show_snippet.call_args.kwargs["global_x"] == 703


def test_top5_entered_not_blocked_when_category_active(popup):
    popup._selected_category_id = 1
    popup._flyout = MagicMock()
    popup._flyout.isVisible.return_value = True

    snippet = MagicMock()
    item = MagicMock()
    item.data.return_value = 99
    with (
        patch(
            "src.ui.popup_window.snippet_repository.get_by_id",
            return_value=snippet,
        ),
        patch.object(popup, "_show_top_detail") as show_detail,
    ):
        popup._on_top_item_entered(item)
        show_detail.assert_called_once_with(snippet)
