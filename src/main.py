"""QuickPaste Manager 진입점."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from src.app.app_controller import AppController


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("QuickPaste Manager")
    app.setOrganizationName("QuickPaste")

    if not _check_tray_available():
        return 1

    controller = AppController(app)
    controller.start()
    return app.exec()


def _check_tray_available() -> bool:
    from PySide6.QtWidgets import QSystemTrayIcon

    if QSystemTrayIcon.isSystemTrayAvailable():
        return True

    QMessageBox.critical(
        None,
        "QuickPaste Manager",
        "시스템 트레이를 사용할 수 없습니다.\n"
        "Windows 알림 영역 설정을 확인하세요.",
    )
    return False


if __name__ == "__main__":
    raise SystemExit(main())
