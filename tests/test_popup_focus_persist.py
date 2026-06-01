"""연속 붙여넣기 모드에서 포커스 이탈 시 팝업 유지."""

from __future__ import annotations

from unittest.mock import MagicMock

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
