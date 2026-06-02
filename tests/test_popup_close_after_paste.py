"""붙여넣기 후 팝업 닫기 설정 테스트."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.repositories import category_repository, snippet_repository
from src.repositories.db import initialize_database
from src.ui.popup_window import PopupWindow


@pytest.fixture
def snippet_conn(tmp_path):
    conn = initialize_database(db_path=tmp_path / "t.db", seed_categories=True)
    cat_id = category_repository.list_active(conn)[0].id
    sid = snippet_repository.create_text(
        conn, category_id=cat_id, title="t", body_text="body"
    )
    conn.commit()
    snippet = snippet_repository.get_by_id(conn, sid)
    yield conn, snippet
    conn.close()


def test_paste_closes_popup_when_setting_on(snippet_conn, qapp, qtbot):
    conn, snippet = snippet_conn
    paste = MagicMock()
    paste.paste_snippet.return_value = True
    window = PopupWindow(conn, paste, close_popup_after_paste=lambda: True)
    window.show()
    qtbot.waitExposed(window)
    window._paste_snippet(snippet)
    qtbot.wait(80)

    assert paste.paste_snippet.called
    assert not window.isVisible()


def test_paste_keeps_popup_when_setting_off(snippet_conn, qapp, qtbot):
    conn, snippet = snippet_conn
    paste = MagicMock()
    paste.paste_snippet.return_value = True
    window = PopupWindow(conn, paste, close_popup_after_paste=lambda: False)
    window.show()
    qtbot.waitExposed(window)

    with patch("src.ui.popup_window.capture_foreground_window", return_value=None):
        window._paste_snippet(snippet)
    qtbot.wait(80)

    assert paste.paste_snippet.called
    assert window.isVisible()


def test_paste_keeps_category_flyout_when_setting_off(snippet_conn, qapp, qtbot):
    conn, snippet = snippet_conn
    paste = MagicMock()
    paste.paste_snippet.return_value = True
    window = PopupWindow(conn, paste, close_popup_after_paste=lambda: False)
    window.show()
    qtbot.waitExposed(window)

    cat_id = snippet.category_id
    window._show_category_flyout(cat_id)
    flyout = window._ensure_flyout()
    qtbot.waitExposed(flyout)

    with patch("src.ui.popup_window.capture_foreground_window", return_value=None):
        window._paste_snippet(snippet)
    qtbot.wait(80)

    assert flyout.isVisible()


def test_category_flyout_not_closed_on_leave_event(snippet_conn, qapp, qtbot):
    from PySide6.QtCore import QEvent

    conn, _snippet = snippet_conn
    paste = MagicMock()
    window = PopupWindow(conn, paste, close_popup_after_paste=lambda: False)
    window.show()
    qtbot.waitExposed(window)

    cat_id = category_repository.list_active(conn)[0].id
    window._show_category_flyout(cat_id)
    flyout = window._ensure_flyout()
    qtbot.waitExposed(flyout)

    flyout.leaveEvent(QEvent(QEvent.Type.Leave))
    qtbot.wait(120)

    assert flyout.isVisible()
