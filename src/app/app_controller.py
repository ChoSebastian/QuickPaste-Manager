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
from src.utils.icons import ensure_tray_icon
from src.utils.paths import ensure_app_directories, get_resources_dir

logger = logging.getLogger("quickpaste.app")

FALLBACK_HOTKEYS: tuple[str, ...] = (
    "Ctrl+Shift+V",
    "Ctrl+Alt+V",
    "Ctrl+Shift+Insert",
    "Ctrl+Alt+P",
)


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
            restore_clipboard=bool(
                self._settings.get("restore_clipboard_after_paste", True)
            ),
        )
        self._hotkey_service = create_hotkey_service(app)
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
        try:
            path = ensure_tray_icon()
            return QIcon(str(path))
        except Exception as exc:
            logger.warning("트레이 아이콘 생성 실패: %s", exc)
            icon_dir = get_resources_dir() / "icons"
            for name in ("app.ico", "app.png"):
                path = icon_dir / name
                if path.exists():
                    return QIcon(str(path))
            return QIcon()

    def _register_triggers(self) -> None:
        primary = str(self._settings.get("hotkey", "Ctrl+Shift+V"))
        candidates = [primary, *(hk for hk in FALLBACK_HOTKEYS if hk != primary)]

        registered = False
        used_hotkey = primary
        for hotkey in candidates:
            if self._hotkey_service.register(hotkey, self.open_popup):
                registered = True
                used_hotkey = hotkey
                break

        if registered:
            if used_hotkey != primary:
                logger.info("대체 단축키 사용: %s (원래: %s)", used_hotkey, primary)
            return

        logger.warning("전역 단축키 등록 실패: %s", primary)
        QMessageBox.warning(
            None,
            "단축키 등록 실패",
            f"'{primary}' 및 대체 단축키 등록에 모두 실패했습니다.\n"
            "다른 프로그램이 단축키를 사용 중일 수 있습니다.\n"
            "트레이 메뉴에서 팝업을 열거나 환경설정에서 단축키를 변경하세요.",
        )

        if self._settings.get("mouse_wheel_trigger_enabled", False):
            self._mouse_service.start(self.open_popup)

    def _reregister_triggers(self) -> None:
        self._hotkey_service.unregister()
        self._mouse_service.stop()
        self._register_triggers()

    def start(self) -> None:
        self._tray.show()
        self._ensure_popup()
        logger.info("QuickPaste Manager 시작")

    def _ensure_popup(self) -> PopupWindow:
        if self._popup is None:
            self._popup = PopupWindow(
                self._conn,
                self._paste_service,
                on_close=self._on_popup_closed,
                on_help=self.show_help,
            )
            self._popup.refresh()
        return self._popup

    def open_popup(self) -> None:
        try:
            popup = self._ensure_popup()
            popup.show_near_cursor(
                offset_px=int(self._settings.get("popup_offset_px", 12)),
                width=int(self._settings.get("popup_width", 360)),
                height=int(self._settings.get("popup_height", 520)),
            )
            popup.refresh()
        except Exception as exc:
            logger.exception("팝업 열기 실패: %s", exc)
            self._popup = None
            QMessageBox.critical(
                None,
                "팝업 오류",
                f"팝업을 열 수 없습니다.\n\n{exc}",
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
        self._settings_window.load_settings(
            self._settings,
            hotkey_active=self._hotkey_service.active_hotkey,
        )
        self._settings_window.show()
        self._settings_window.raise_()
        self._settings_window.activateWindow()

    def _save_settings(self, new_settings: dict) -> None:
        self._settings = new_settings
        save_settings(self._settings)

        self._paste_service.set_paste_delay_ms(
            int(self._settings.get("paste_delay_ms", 50))
        )
        self._paste_service.set_restore_clipboard(
            bool(self._settings.get("restore_clipboard_after_paste", True))
        )
        self._reregister_triggers()
        logger.info("설정 저장 완료 — 단축키·붙여넣기 옵션 반영")

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
        hotkey = self._settings.get("hotkey", "Ctrl+Shift+V")
        QMessageBox.information(
            None,
            "도움말",
            "QuickPaste Manager\n\n"
            f"전역 단축키: {hotkey}\n"
            "트레이 메뉴에서도 팝업/관리/설정을 열 수 있습니다.\n"
            "상용구 선택 시 클립보드 등록 후 자동 붙여넣기를 시도합니다.",
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
