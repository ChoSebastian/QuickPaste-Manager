"""AppData 및 프로젝트 경로 관리."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

APP_DIR_NAME = "QuickPasteManager"

_SUBDIRS = ("assets", "logs", "exports", "backups")


def get_app_data_root() -> Path:
    """%APPDATA%\\QuickPasteManager 경로를 반환한다."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA 환경 변수를 찾을 수 없습니다.")
    return Path(appdata) / APP_DIR_NAME


def get_project_root() -> Path:
    """프로젝트 루트 경로 (src 상위)를 반환한다."""
    return Path(__file__).resolve().parents[2]


def get_resources_dir() -> Path:
    return get_project_root() / "src" / "resources"


def get_db_path(root: Path | None = None) -> Path:
    base = root or get_app_data_root()
    return base / "app.db"


def get_settings_path(root: Path | None = None) -> Path:
    base = root or get_app_data_root()
    return base / "settings.json"


def get_logs_dir(root: Path | None = None) -> Path:
    base = root or get_app_data_root()
    return base / "logs"


def get_assets_dir(root: Path | None = None) -> Path:
    base = root or get_app_data_root()
    return base / "assets"


def get_exports_dir(root: Path | None = None) -> Path:
    base = root or get_app_data_root()
    return base / "exports"


def get_backups_dir(root: Path | None = None) -> Path:
    base = root or get_app_data_root()
    return base / "backups"


def ensure_app_directories(root: Path | None = None) -> Path:
    """AppData 루트 및 하위 디렉터리를 생성한다."""
    base = root or get_app_data_root()
    base.mkdir(parents=True, exist_ok=True)
    for name in _SUBDIRS:
        (base / name).mkdir(parents=True, exist_ok=True)
    return base


def iter_required_paths(root: Path | None = None) -> Iterable[Path]:
    """앱 실행에 필요한 주요 경로를 순회한다."""
    base = root or get_app_data_root()
    yield base
    yield get_db_path(base)
    yield get_settings_path(base)
    for name in _SUBDIRS:
        yield base / name
