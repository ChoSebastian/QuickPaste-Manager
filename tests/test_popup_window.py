"""PopupWindow 초기화 테스트."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import Qt

from src.repositories.db import initialize_database
from src.ui.popup_window import PopupWindow


@pytest.fixture
def popup(qtbot, tmp_path):
    conn = initialize_database(db_path=tmp_path / "test.db", seed_categories=True)
    paste = MagicMock()
    window = PopupWindow(conn, paste)
    qtbot.addWidget(window)
    yield window
    conn.close()


def test_popup_window_can_be_created(popup):
    popup.show()
    assert popup.isVisible()


def test_popup_escape_closes(popup, qtbot):
    popup.show()
    qtbot.keyClick(popup, Qt.Key.Key_Escape)
    assert not popup.isVisible()
