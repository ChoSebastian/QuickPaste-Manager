"""QuickPaste Manager 진입점."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from src.app.app_controller import AppController
from src.utils.icons import load_app_icon
from src.utils.single_instance import SingleInstanceGuard


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("QuickPaste Manager")
    app.setOrganizationName("QuickPaste")
    try:
        app.setWindowIcon(load_app_icon())
    except Exception:
        pass

    if not _check_tray_available():
        return 1

    controller_holder: list[AppController] = []

    def on_second_instance() -> None:
        if controller_holder:
            controller_holder[0].open_popup()

    guard = SingleInstanceGuard(on_activate=on_second_instance, parent=app)
    if not guard.is_primary:
        QMessageBox.information(
            None,
            "QuickPaste Manager",
            "이미 실행 중입니다.\n"
            "알림 영역(트레이)의 QuickPaste 아이콘을 확인하세요.",
        )
        return 0

    controller = AppController(app)
    controller_holder.append(controller)
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
