"""설정 로더 테스트."""

from __future__ import annotations

import json

from src.utils.config import (
    default_settings,
    load_settings,
    merge_settings,
    save_settings,
)


def test_default_settings_has_required_keys():
    settings = default_settings()
    assert "hotkey" in settings
    assert settings["hotkey"] == "Ctrl+Shift+Q"
    assert "paste_delay_ms" in settings
    assert "close_popup_after_paste" in settings
    assert settings["close_popup_after_paste"] is False
    assert settings["startup_with_windows"] is True
    assert settings["restore_clipboard_after_paste"] is True
    assert "theme" not in settings


def test_merge_settings_fills_missing_keys(tmp_path):
    partial = {"hotkey": "Ctrl+Alt+V"}
    merged = merge_settings(partial)
    assert merged["hotkey"] == "Ctrl+Alt+V"
    assert merged["startup_with_windows"] is True


def test_load_and_save_settings_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from src.utils.paths import get_settings_path

    loaded = load_settings()
    path = get_settings_path()
    assert path.exists()

    loaded["theme"] = "dark"
    save_settings(loaded, path)

    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["theme"] == "dark"


def test_load_settings_creates_file_when_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    from src.utils.paths import get_settings_path

    path = get_settings_path()
    assert not path.exists()

    settings = load_settings()
    assert path.exists()
    assert settings["version"] == 1
