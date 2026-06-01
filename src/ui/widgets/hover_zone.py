"""리스트·보조 패널 호버 영역 판별."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect
from PySide6.QtWidgets import QWidget

LEAVE_CHECK_MS = 80


def widget_global_rect(widget: QWidget) -> QRect:
    return QRect(widget.mapToGlobal(QPoint(0, 0)), widget.size())


def cursor_in_any(pos: QPoint, rects: list[QRect]) -> bool:
    return any(rect.isValid() and rect.contains(pos) for rect in rects)
