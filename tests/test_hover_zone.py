"""hover_zone 유틸 테스트."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect

from src.ui.widgets.hover_zone import cursor_in_any


def test_cursor_in_any():
    rects = [QRect(0, 0, 100, 100)]
    assert cursor_in_any(QPoint(50, 50), rects)
    assert not cursor_in_any(QPoint(200, 200), rects)
