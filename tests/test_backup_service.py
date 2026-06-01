"""자동 백업 서비스 테스트."""

from __future__ import annotations

import time
from pathlib import Path

from src.services.backup_service import LocalBackupService, prune_old_backups


def test_run_backup_copies_db_and_settings(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "appdata"
    root.mkdir()
    db = root / "app.db"
    settings = root / "settings.json"
    db.write_text("db", encoding="utf-8")
    settings.write_text("{}", encoding="utf-8")

    monkeypatch.setattr("src.services.backup_service.get_backups_dir", lambda: root / "backups")
    monkeypatch.setattr("src.services.backup_service.get_db_path", lambda: db)
    monkeypatch.setattr("src.services.backup_service.get_settings_path", lambda: settings)

    svc = LocalBackupService()
    backup_dir = svc.run_backup(keep_count=5)
    assert backup_dir is not None
    assert (backup_dir / "app.db").read_text(encoding="utf-8") == "db"
    assert (backup_dir / "settings.json").exists()


def test_prune_old_backups(tmp_path: Path) -> None:
    backups = tmp_path / "backups"
    backups.mkdir()
    for i in range(5):
        d = backups / f"backup_{i:02d}"
        d.mkdir()
        time.sleep(0.01)
    removed = prune_old_backups(backups, keep_count=2)
    assert removed == 3
    remaining = list(backups.iterdir())
    assert len(remaining) == 2
