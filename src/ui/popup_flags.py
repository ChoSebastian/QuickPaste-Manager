"""팝업·플라이아웃 공통 창 플래그."""

from __future__ import annotations

from PySide6.QtCore import Qt


def popup_window_flags() -> Qt.WindowType:
    return (
        Qt.WindowType.Tool
        | Qt.WindowType.FramelessWindowHint
        | Qt.WindowType.WindowStaysOnTopHint
    )
