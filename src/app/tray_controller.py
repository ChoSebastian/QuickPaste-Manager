"""시스템 트레이 컨트롤러."""

from __future__ import annotations

import logging
from collections.abc import Callable

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

logger = logging.getLogger("quickpaste.tray")


class TrayController:
    def __init__(
        self,
        *,
        on_open_popup: Callable[[], None],
        on_open_manager: Callable[[], None],
        on_open_settings: Callable[[], None],
        on_export: Callable[[], None],
        on_import: Callable[[], None],
        on_help: Callable[[], None],
        on_quit: Callable[[], None],
        icon: QIcon | None = None,
    ) -> None:
        self._on_open_popup = on_open_popup
        self._on_open_manager = on_open_manager
        self._on_open_settings = on_open_settings
        self._on_export = on_export
        self._on_import = on_import
        self._on_help = on_help
        self._on_quit = on_quit

        self._tray = QSystemTrayIcon(icon or QIcon())
        self._tray.setToolTip("QuickPaste Manager")
        self._tray.setContextMenu(self._build_menu())

    def _build_menu(self) -> QMenu:
        menu = QMenu()

        actions = [
            ("팝업 열기", self._on_open_popup),
            ("상용구 관리", self._on_open_manager),
            ("환경설정", self._on_open_settings),
            (None, None),
            ("내보내기", self._on_export),
            ("불러오기", self._on_import),
            (None, None),
            ("도움말", self._on_help),
            ("종료", self._on_quit),
        ]

        for label, handler in actions:
            if label is None:
                menu.addSeparator()
                continue
            action = QAction(label, menu)
            if handler is not None:
                action.triggered.connect(handler)
            menu.addAction(action)

        return menu

    def show(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.error("시스템 트레이를 사용할 수 없습니다.")
            return
        self._tray.show()
        logger.info("시스템 트레이 표시")

    def hide(self) -> None:
        self._tray.hide()
