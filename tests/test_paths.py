"""경로 유틸리티 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.utils import paths


def test_get_app_data_root_name(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    root = paths.get_app_data_root()
    assert root == tmp_path / "QuickPasteManager"


def test_ensure_app_directories_creates_subdirs(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    base = tmp_path / "QuickPasteManager"
    result = paths.ensure_app_directories(base)

    assert result == base
    for name in ("assets", "logs", "exports", "backups"):
        assert (base / name).is_dir()


def test_get_db_and_settings_paths(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    base = paths.ensure_app_directories()
    assert paths.get_db_path(base) == base / "app.db"
    assert paths.get_settings_path(base) == base / "settings.json"


def test_iter_required_paths(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    base = paths.ensure_app_directories()
    required = list(paths.iter_required_paths(base))
    assert base in required
    assert paths.get_db_path(base) in required
