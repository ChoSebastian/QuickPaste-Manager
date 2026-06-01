"""settings.json 로드/저장."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from src.utils.paths import ensure_app_directories, get_settings_path

DEFAULT_HOTKEY = "Ctrl+Shift+Q"

DEFAULT_SETTINGS: dict[str, Any] = {
    "version": 1,
    "hotkey": DEFAULT_HOTKEY,
    "mouse_wheel_trigger_enabled": False,  # deprecated, unused
    "startup_with_windows": True,
    "popup_offset_px": 12,
    "popup_width": 360,
    "popup_height": 520,
    "paste_delay_ms": 50,
    "restore_clipboard_after_paste": True,
    "close_popup_after_paste": False,
    "image_paste_mode": "clipboard",
    "auto_backup_interval_hours": 24,
    "auto_backup_keep_count": 10,
    "seed_default_categories": True,
    "seed_sample_snippets": False,
}


def default_settings() -> dict[str, Any]:
    return deepcopy(DEFAULT_SETTINGS)


def merge_settings(stored: dict[str, Any]) -> dict[str, Any]:
    """저장된 설정과 기본값을 병합한다."""
    merged = default_settings()
    merged.update(stored)
    return merged


def load_settings(path: Path | None = None) -> dict[str, Any]:
    """settings.json을 로드한다. 없으면 기본값을 생성·저장한다."""
    ensure_app_directories()
    settings_path = path or get_settings_path()
    if not settings_path.exists():
        settings = default_settings()
        save_settings(settings, settings_path)
        return settings

    raw = settings_path.read_text(encoding="utf-8")
    stored = json.loads(raw)
    return merge_settings(stored)


def save_settings(settings: dict[str, Any], path: Path | None = None) -> None:
    """settings.json을 저장한다."""
    ensure_app_directories()
    settings_path = path or get_settings_path()
    settings_path.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
