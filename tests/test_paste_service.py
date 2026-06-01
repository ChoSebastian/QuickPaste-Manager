"""paste_service 테스트."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.repositories import category_repository, snippet_repository
from src.repositories.db import initialize_database
from src.services.paste_service import DefaultPasteService


@pytest.fixture
def text_snippet(tmp_path):
    conn = initialize_database(db_path=tmp_path / "test.db", seed_categories=True)
    cat_id = category_repository.list_active(conn)[0].id
    sid = snippet_repository.create_text(
        conn, category_id=cat_id, title="t", body_text="hello"
    )
    conn.commit()
    snippet = snippet_repository.get_by_id(conn, sid)
    assert snippet is not None
    yield conn, snippet
    conn.close()


def test_paste_text_success(text_snippet):
    conn, snippet = text_snippet
    clipboard = MagicMock()
    clipboard.get_text.return_value = "prev"
    clipboard.set_text.return_value = True

    service = DefaultPasteService(clipboard, paste_delay_ms=0, restore_clipboard=False)

    with patch("src.services.paste_service.send_ctrl_v", return_value=True):
        assert service.paste_snippet(conn, snippet) is True

    clipboard.set_text.assert_called_once_with("hello")
    updated = snippet_repository.get_by_id(conn, snippet.id)
    assert updated is not None
    assert updated.use_count == 1


def test_paste_text_sendinput_failure(text_snippet):
    conn, snippet = text_snippet
    clipboard = MagicMock()
    clipboard.set_text.return_value = True
    service = DefaultPasteService(clipboard, paste_delay_ms=0, restore_clipboard=False)

    with patch("src.services.paste_service.send_ctrl_v", return_value=False):
        assert service.paste_snippet(conn, snippet) is False
