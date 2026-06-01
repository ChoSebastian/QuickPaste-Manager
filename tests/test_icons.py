"""트레이 아이콘 생성 테스트."""

from __future__ import annotations

from src.utils.icons import ensure_tray_icon


def test_ensure_tray_icon_creates_png(tmp_path, monkeypatch):
    icons_dir = tmp_path / "icons"
    monkeypatch.setattr("src.utils.icons._ICON_DIR", icons_dir)
    monkeypatch.setattr("src.utils.icons._ICON_PATH", icons_dir / "app.png")

    path = ensure_tray_icon()
    assert path.exists()
    assert path.suffix == ".png"

    # 두 번째 호출은 재생성하지 않음
    path2 = ensure_tray_icon()
    assert path2 == path
