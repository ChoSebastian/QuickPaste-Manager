"""앱 전체 컨트롤러."""

from __future__ import annotations

import logging
import sqlite3

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from src.app.restart_manager import request_restart
from src.app.tray_controller import TrayController
from src.repositories.db import initialize_database
from src.services.backup_service import create_backup_service
from src.services.clipboard_service import create_clipboard_service
from src.services.hotkey_service import create_hotkey_service
from src.services.import_export_service import create_import_export_service
from src.services.mouse_trigger_service import create_mouse_trigger_service
from src.services.paste_service import create_paste_service
from src.ui.manager_window import ManagerWindow
from src.ui.popup_window import PopupWindow
from src.ui.settings_window import SettingsWindow
from src.utils.config import load_settings, save_settings
from src.utils.logger import setup_logging
from src.utils.paths import ensure_app_directories, get_resources_dir

logger = logging.getLogger("quickpaste.app")


class AppController:
    def __init__(self, app: QApplication) -> None:
        self._app = app
        self._settings = load_settings()
        setup_logging()

        ensure_app_directories()
        self._conn = initialize_database(
            seed_categories=self._settings.get("seed_default_categories", True),
        )

        self._clipboard = create_clipboard_service(app)
        self._paste_service = create_paste_service(
            self._clipboard,
            paste_delay_ms=int(self._settings.get("paste_delay_ms", 50)),
        )
        self._hotkey_service = create_hotkey_service()
        self._mouse_service = create_mouse_trigger_service()
        self._import_export = create_import_export_service()
        self._backup = create_backup_service()

        self._popup: PopupWindow | None = None
        self._manager: ManagerWindow | None = None
        self._settings_window: SettingsWindow | None = None

        self._tray = TrayController(
            on_open_popup=self.open_popup,
            on_open_manager=self.open_manager,
            on_open_settings=self.open_settings,
            on_export=self.export_data,
            on_import=self.import_data,
            on_help=self.show_help,
            on_quit=self.quit,
            icon=self._load_icon(),
        )

        self._register_triggers()

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn

    @property
    def settings(self) -> dict:
        return self._settings

    def _load_icon(self) -> QIcon:
        icon_dir = get_resources_dir() / "icons"
        for name in ("app.ico", "app.png"):
            path = icon_dir / name
            if path.exists():
                return QIcon(str(path))
        return QIcon()

    def _register_triggers(self) -> None:
        hotkey = str(self._settings.get("hotkey", "Ctrl+Shift+V"))
        self._hotkey_service.register(hotkey, self.open_popup)

        if self._settings.get("mouse_wheel_trigger_enabled", False):
            self._mouse_service.start(self.open_popup)

    def start(self) -> None:
        self._tray.show()
        logger.info("QuickPaste Manager 시작")

    def open_popup(self) -> None:
        if self._popup is None:
            self._popup = PopupWindow(
                self._conn,
                self._paste_service,
                on_close=self._on_popup_closed,
            )
        self._popup.refresh()
        self._popup.show_near_cursor(
            offset_px=int(self._settings.get("popup_offset_px", 12)),
            width=int(self._settings.get("popup_width", 360)),
            height=int(self._settings.get("popup_height", 520)),
        )

    def _on_popup_closed(self) -> None:
        pass

    def open_manager(self) -> None:
        if self._manager is None:
            self._manager = ManagerWindow(self._conn)
        self._manager.refresh()
        self._manager.show()
        self._manager.raise_()
        self._manager.activateWindow()

    def open_settings(self) -> None:
        if self._settings_window is None:
            self._settings_window = SettingsWindow(
                self._settings,
                on_save=self._save_settings,
            )
        self._settings_window.load_settings(self._settings)
        self._settings_window.show()
        self._settings_window.raise_()
        self._settings_window.activateWindow()

    def _save_settings(self, new_settings: dict) -> None:
        self._settings = new_settings
        save_settings(self._settings)
        logger.info("설정 저장 완료")

    def export_data(self) -> None:
        from src.utils.paths import get_exports_dir

        dest = get_exports_dir() / "export.zip"
        if self._import_export.export_to_zip(dest):
            QMessageBox.information(
                None, "내보내기", f"내보내기 완료:\n{dest}"
            )
        else:
            QMessageBox.warning(
                None, "내보내기", "내보내기 기능은 아직 구현 중입니다."
            )

    def import_data(self) -> None:
        QMessageBox.information(
            None, "불러오기", "불러오기 기능은 아직 구현 중입니다."
        )

    def show_help(self) -> None:
        QMessageBox.information(
            None,
            "도움말",
            "QuickPaste Manager\n\n"
            "트레이 메뉴에서 팝업/관리/설정을 열 수 있습니다.\n"
            "전역 단축키는 Phase 4에서 구현 예정입니다.",
        )

    def quit(self) -> None:
        logger.info("앱 종료")
        self._hotkey_service.unregister()
        self._mouse_service.stop()
        self._conn.close()
        self._app.quit()

    def handle_fatal_error(self, message: str) -> None:
        logger.error("치명적 오류: %s", message)
        QMessageBox.critical(None, "오류", message)
        request_restart(message)
