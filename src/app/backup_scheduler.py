"""자동 백업 QTimer 스케줄러."""

from __future__ import annotations

from PySide6.QtCore import QObject, QTimer

from src.services.backup_service import BackupService


class BackupScheduler(QObject):
    def __init__(
        self,
        backup_service: BackupService,
        *,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._backup = backup_service
        self._keep_count = 10
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timeout)

    def apply_settings(self, settings: dict) -> None:
        hours = max(1, int(settings.get("auto_backup_interval_hours", 24)))
        self._keep_count = max(1, int(settings.get("auto_backup_keep_count", 10)))
        self._timer.stop()
        self._timer.start(hours * 3_600_000)

    def run_now(self) -> None:
        self._backup.run_backup(keep_count=self._keep_count)

    def _on_timeout(self) -> None:
        self.run_now()

    def stop(self) -> None:
        self._timer.stop()
