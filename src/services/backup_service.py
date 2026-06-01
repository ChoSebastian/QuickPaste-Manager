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
    def run_backup(self, *, keep_count: int = 10) -> Path | None: ...


def prune_old_backups(backups_dir: Path, *, keep_count: int) -> int:
    """오래된 backup_* 폴더를 삭제하고 삭제 개수를 반환한다."""
    if keep_count < 1:
        return 0
    dirs = sorted(
        (
            p
            for p in backups_dir.iterdir()
            if p.is_dir() and p.name.startswith("backup_")
        ),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    removed = 0
    for old in dirs[keep_count:]:
        shutil.rmtree(old, ignore_errors=True)
        removed += 1
    return removed


class LocalBackupService:
    def run_backup(self, *, keep_count: int = 10) -> Path | None:
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
            removed = prune_old_backups(backups_dir, keep_count=keep_count)
            if removed:
                logger.info("오래된 백업 %d개 삭제", removed)
            logger.info("백업 완료: %s", backup_dir)
            return backup_dir
        except Exception as exc:
            logger.exception("백업 실패: %s", exc)
            return None


def create_backup_service() -> BackupService:
    return LocalBackupService()
