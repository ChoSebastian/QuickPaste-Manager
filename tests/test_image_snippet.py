"""이미지 상용구 및 Top5 테스트."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from src.repositories import category_repository, snippet_repository
from src.repositories.db import initialize_database
from src.services.asset_service import guess_mime_type, save_image_file
from src.services.paste_service import DefaultPasteService


def test_guess_mime_type():
    assert guess_mime_type(Path("a.PNG")) == "image/png"
    assert guess_mime_type(Path("a.jpg")) == "image/jpeg"


def test_create_image_snippet(tmp_path):
    conn = initialize_database(db_path=tmp_path / "test.db", seed_categories=True)
    cat_id = category_repository.list_active(conn)[0].id

    img_path = tmp_path / "logo.png"
    Image.new("RGB", (8, 8), color=(255, 0, 0)).save(img_path)

    asset_id = save_image_file(conn, img_path)
    sid = snippet_repository.create_image(
        conn, category_id=cat_id, title="로고", asset_id=asset_id
    )
    conn.commit()

    snippet = snippet_repository.get_by_id(conn, sid)
    assert snippet is not None
    assert snippet.content_type == "image"
    assert snippet.asset_id == asset_id
    conn.close()


def test_top_snippets_prefers_pinned(tmp_path):
    conn = initialize_database(db_path=tmp_path / "test.db", seed_categories=True)
    cat_id = category_repository.list_active(conn)[0].id

    low = snippet_repository.create_text(
        conn, category_id=cat_id, title="low", body_text="a"
    )
    high = snippet_repository.create_text(
        conn, category_id=cat_id, title="high", body_text="b"
    )
    snippet_repository.update(conn, high, pinned=True)
    for _ in range(5):
        snippet_repository.record_usage(conn, low)
    conn.commit()

    top = snippet_repository.top_snippets(conn, limit=1)
    assert top[0].id == high
    conn.close()


def test_paste_image_success(tmp_path):
    conn = initialize_database(db_path=tmp_path / "test.db", seed_categories=True)
    cat_id = category_repository.list_active(conn)[0].id
    img_path = tmp_path / "img.png"
    Image.new("RGB", (4, 4), color=(0, 128, 255)).save(img_path)
    asset_id = save_image_file(conn, img_path)
    sid = snippet_repository.create_image(
        conn, category_id=cat_id, title="img", asset_id=asset_id
    )
    conn.commit()
    snippet = snippet_repository.get_by_id(conn, sid)
    assert snippet is not None

    clipboard = MagicMock()
    clipboard.set_image_from_path.return_value = True
    service = DefaultPasteService(clipboard, paste_delay_ms=0, restore_clipboard=False)

    with patch("src.services.paste_service.send_ctrl_v", return_value=True):
        assert service.paste_snippet(conn, snippet) is True

    conn.close()
