"""Windows 창 Z-order 유틸."""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger("quickpaste.win")


def raise_window_topmost(hwnd: int) -> None:
    """창을 HWND_TOPMOST로 올린다 (포커스는 빼앗지 않음)."""
    if sys.platform != "win32" or not hwnd:
        return
    try:
        import win32con
        import win32gui

        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE
            | win32con.SWP_NOSIZE
            | win32con.SWP_NOACTIVATE
            | win32con.SWP_SHOWWINDOW,
        )
    except Exception as exc:
        logger.debug("SetWindowPos TOPMOST 실패: %s", exc)
