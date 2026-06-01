"""이미지 붙여넣기 불가 대상·팝업 유지 관련 paste_service 테스트."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from src.repositories import category_repository, snippet_repository
from src.repositories.db import initialize_database
from src.services.asset_service import save_image_file
from src.services.paste_service import DefaultPasteService


def test_paste_image_blocked_target(tmp_path):
    conn = initialize_database(db_path=tmp_path / "test.db", seed_categories=True)
    cat_id = category_repository.list_active(conn)[0].id
    img_path = tmp_path / "x.png"
    Image.new("RGB", (2, 2)).save(img_path)
    asset_id = save_image_file(conn, img_path)
    sid = snippet_repository.create_image(
        conn, category_id=cat_id, title="img", asset_id=asset_id
    )
    conn.commit()
    snippet = snippet_repository.get_by_id(conn, sid)
    assert snippet is not None

    clipboard = MagicMock()
    service = DefaultPasteService(clipboard, paste_delay_ms=0, restore_clipboard=False)

    with patch(
        "src.services.paste_service.image_paste_blocked_reason",
        return_value="이 입력란에는 이미지를 붙여넣을 수 없습니다.",
    ), patch("src.services.paste_service.show_user_warning") as warn:
        assert service.paste_snippet(conn, snippet, target_hwnd=1, show_warning=True) is False
        warn.assert_called_once()
        clipboard.set_image_from_path.assert_not_called()

    conn.close()
