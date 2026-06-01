"""도움말 창."""

from __future__ import annotations

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from src.ui.help_content import build_help_html


class HelpWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("QuickPaste Manager — 도움말")
        self.resize(560, 620)
        self.setMinimumSize(420, 400)
        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)

        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(True)
        self._browser.setReadOnly(True)
        layout.addWidget(self._browser)

        actions = QHBoxLayout()
        actions.addStretch()
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.close)
        actions.addWidget(close_btn)
        layout.addLayout(actions)

    def load_help(
        self,
        *,
        hotkey: str,
        active_hotkey: str | None,
        mouse_trigger_enabled: bool,
    ) -> None:
        self._browser.setHtml(
            build_help_html(
                hotkey=hotkey,
                active_hotkey=active_hotkey,
                mouse_trigger_enabled=mouse_trigger_enabled,
            )
        )
        self._browser.moveCursor(QTextCursor.MoveOperation.Start)

    def show_help(
        self,
        *,
        hotkey: str,
        active_hotkey: str | None,
        mouse_trigger_enabled: bool,
    ) -> None:
        self.load_help(
            hotkey=hotkey,
            active_hotkey=active_hotkey,
            mouse_trigger_enabled=mouse_trigger_enabled,
        )
        self.show()
        self.raise_()
        self.activateWindow()
