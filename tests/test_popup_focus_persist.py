"""연속 붙여넣기 모드에서 포커스 이탈 시 팝업 유지."""

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


def test_deactivate_does_not_schedule_close_when_persist_mode(
    snippet_conn, qapp, qtbot
):
    conn, _ = snippet_conn
    window = PopupWindow(
        conn, MagicMock(), close_popup_after_paste=lambda: False
    )
    window.show()
    qtbot.waitExposed(window)

    from PySide6.QtCore import QEvent

    app = qapp
    app.sendEvent(window, QEvent(QEvent.Type.WindowDeactivate))
    qtbot.wait(200)

    assert window.isVisible()


def test_sync_updates_from_cursor_when_outside_popup(snippet_conn, qapp, qtbot):
    conn, _ = snippet_conn
    window = PopupWindow(
        conn, MagicMock(), close_popup_after_paste=lambda: False
    )
    window._target_hwnd = 111
    window.show()
    qtbot.waitExposed(window)

    with (
        patch(
            "src.ui.popup_window.capture_window_at_cursor", return_value=222
        ),
        patch.object(window, "frameGeometry") as mock_rect,
        patch.object(window, "_auxiliary_windows_at", return_value=False),
    ):
        mock_rect.return_value.contains.return_value = False
        window._sync_external_target_hwnd()

    assert window._target_hwnd == 222


def test_sync_keeps_target_when_cursor_on_popup_and_fg_is_popup(
    snippet_conn, qapp, qtbot
):
    conn, _ = snippet_conn
    window = PopupWindow(
        conn, MagicMock(), close_popup_after_paste=lambda: False
    )
    window._target_hwnd = 111
    window.show()
    qtbot.waitExposed(window)
    popup_hwnd = int(window.winId())

    with (
        patch(
            "src.ui.popup_window.capture_window_at_cursor", return_value=popup_hwnd
        ),
        patch(
            "src.ui.popup_window.capture_foreground_window",
            return_value=popup_hwnd,
        ),
        patch.object(window, "frameGeometry") as mock_rect,
        patch.object(window, "_auxiliary_windows_at", return_value=False),
    ):
        mock_rect.return_value.contains.return_value = True
        window._sync_external_target_hwnd()

    assert window._target_hwnd == 111


def test_deactivate_triggers_sync(snippet_conn, qapp, qtbot):
    conn, _ = snippet_conn
    window = PopupWindow(
        conn, MagicMock(), close_popup_after_paste=lambda: False
    )
    window._target_hwnd = 111
    window.show()
    qtbot.waitExposed(window)

    with patch.object(window, "_sync_external_target_hwnd") as sync:
        from PySide6.QtCore import QEvent

        qapp.sendEvent(window, QEvent(QEvent.Type.WindowDeactivate))
        qtbot.wait(80)
        assert sync.call_count >= 1
