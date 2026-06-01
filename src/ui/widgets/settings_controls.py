"""환경설정 단일 화면용 공통 위젯."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.ui.widgets.toggle_switch import ToggleSwitch


class SettingSectionTitle(QLabel):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("SettingSectionTitle")
        self.setStyleSheet(
            "font-size: 13px; font-weight: 600; color: #1a5fb4; "
            "padding: 16px 0 6px 0;"
        )


class SettingDivider(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setStyleSheet("color: #e8e8e8; margin: 4px 0;")


class SettingToggle(QWidget):
    """설명 + Windows 스타일 켬/끔 토글."""

    def __init__(
        self,
        title: str,
        *,
        hint: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 13px; color: #222;")
        text_col.addWidget(title_lbl)
        if hint:
            hint_lbl = QLabel(hint)
            hint_lbl.setWordWrap(True)
            hint_lbl.setStyleSheet("font-size: 11px; color: #888;")
            text_col.addWidget(hint_lbl)
        layout.addLayout(text_col, stretch=1)

        self._switch = ToggleSwitch()
        layout.addWidget(self._switch, alignment=Qt.AlignmentFlag.AlignRight)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._switch.setChecked(not self._switch.isChecked())
            event.accept()
            return
        super().mousePressEvent(event)

    def isChecked(self) -> bool:
        return self._switch.isChecked()

    def setChecked(self, checked: bool) -> None:
        self._switch.setChecked(checked, animate=False)


class SettingSpinRow(QWidget):
    """숫자 입력 행."""

    def __init__(
        self,
        title: str,
        *,
        suffix: str = "",
        minimum: int = 0,
        maximum: int = 9999,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 13px; color: #222;")
        layout.addWidget(lbl, stretch=1)
        self.spin = QSpinBox()
        self.spin.setRange(minimum, maximum)
        if suffix:
            self.spin.setSuffix(suffix)
        self.spin.setMinimumWidth(110)
        layout.addWidget(self.spin)

    def value(self) -> int:
        return self.spin.value()

    def setValue(self, value: int) -> None:
        self.spin.setValue(value)
