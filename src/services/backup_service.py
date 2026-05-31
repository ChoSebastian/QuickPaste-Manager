"""자동 백업 서비스."""

from __future__ import annotations

import logging
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from src.utils.paths import get_backups_dir, get_db_path, get_settings_path

logger = logging.getLogger("quickpaste.backup")


class BackupService(Protocol):
    def run_backup(self) -> Path | None: ...


class LocalBackupService:
    """TODO: 주기적 자동 백업 스케줄러 연동."""

    def run_backup(self) -> Path | None:
        backups_dir = get_backups_dir()
        backups_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_dir = backups_dir / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        db_path = get_db_path()
        settings_path = get_settings_path()

        try:
            if db_path.exists():
                shutil.copy2(db_path, backup_dir / "app.db")
            if settings_path.exists():
                shutil.copy2(settings_path, backup_dir / "settings.json")
            logger.info("백업 완료: %s", backup_dir)
            return backup_dir
        except Exception as exc:
            logger.exception("백업 실패: %s", exc)
            return None


def create_backup_service() -> BackupService:
    return LocalBackupService()
