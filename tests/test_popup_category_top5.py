"""카테고리 열림 시 Top5 호버가 보조 팝업을 침범하지 않는지 검증."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.repositories.db import initialize_database
from src.ui.popup_window import PopupWindow


@pytest.fixture
def popup(qtbot, tmp_path):
    conn = initialize_database(db_path=tmp_path / "test.db", seed_categories=True)
    paste = MagicMock()
    window = PopupWindow(conn, paste)
    qtbot.addWidget(window)
    window.show()
    yield window
    conn.close()


def test_top5_hover_ignored_when_category_flyout_active(popup):
    popup._selected_category_id = 1
    popup._flyout = MagicMock()
    popup._flyout.isVisible.return_value = True

    assert popup._category_panel_active() is True

    item = MagicMock()
    popup._on_top_item_entered(item)
    popup._flyout.hide_and_reset.assert_not_called()
