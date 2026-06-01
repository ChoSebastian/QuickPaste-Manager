"""Windows 설정 스타일 켬/끔 토글."""

from __future__ import annotations

from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget


class ToggleSwitch(QWidget):
    """Windows 11 스타일 토글 스위치."""

    toggled = Signal(bool)

    _TRACK_W = 44
    _TRACK_H = 22
    _PAD = 2
    _THUMB = _TRACK_H - _PAD * 2

    def __init__(
        self,
        *,
        checked: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._checked = checked
        self._thumb_pos = float(self._thumb_x_on() if checked else self._thumb_x_off())
        self._anim: QPropertyAnimation | None = None
        self.setFixedSize(self._TRACK_W, self._TRACK_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _thumb_x_off(self) -> int:
        return self._PAD

    def _thumb_x_on(self) -> int:
        return self._TRACK_W - self._PAD - self._THUMB

    def isChecked(self) -> bool:
        return self._checked

    def getThumbPos(self) -> float:
        return self._thumb_pos

    def setThumbPos(self, value: float) -> None:
        self._thumb_pos = value
        self.update()

    thumbPos = Property(float, getThumbPos, setThumbPos)

    def setChecked(self, checked: bool, *, animate: bool = True) -> None:
        if self._checked == checked:
            return
        self._checked = checked
        target = float(self._thumb_x_on() if checked else self._thumb_x_off())

        if self._anim is not None:
            self._anim.stop()
            self._anim = None

        if animate:
            anim = QPropertyAnimation(self, b"thumbPos", self)
            anim.setDuration(120)
            anim.setStartValue(self._thumb_pos)
            anim.setEndValue(target)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.start()
            self._anim = anim
        else:
            self._thumb_pos = target

        self.update()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)
            event.accept()
            return
        super().mousePressEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.hasFocus():
            painter.setPen(QColor("#0067C0"))
        else:
            painter.setPen(Qt.PenStyle.NoPen)

        track = QColor("#0067C0" if self._checked else "#8A8A8A")
        if not self.isEnabled():
            track = QColor("#C4C4C4" if self._checked else "#E0E0E0")

        painter.setBrush(track)
        painter.drawRoundedRect(0, 0, self._TRACK_W, self._TRACK_H, 11, 11)

        thumb_x = int(self._thumb_pos)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawEllipse(
            QRect(thumb_x, self._PAD, self._THUMB, self._THUMB),
        )

    def sizeHint(self) -> QSize:
        return QSize(self._TRACK_W, self._TRACK_H)
