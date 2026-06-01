"""Windows 클립보드 (Unicode + 레거시 ANSI 호환)."""

from __future__ import annotations

import logging
import sys
import time

logger = logging.getLogger("quickpaste.clipboard")


def get_unicode_text() -> str:
    if sys.platform != "win32":
        return ""
    try:
        import win32clipboard
        import win32con

        win32clipboard.OpenClipboard()
        try:
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                return data if isinstance(data, str) else str(data)
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
                raw = win32clipboard.GetClipboardData(win32con.CF_TEXT)
                if isinstance(raw, bytes):
                    return raw.decode("mbcs", errors="replace")
                return str(raw)
            return ""
        finally:
            win32clipboard.CloseClipboard()
    except Exception as exc:
        logger.debug("클립보드 읽기 실패: %s", exc)
        return ""


def set_unicode_text(text: str) -> bool:
    """Unicode + CF_TEXT(mbcs) 동시 등록 — 메모장 등 레거시 앱 호환."""
    if sys.platform != "win32":
        return False
    try:
        import win32clipboard
        import win32con

        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
            try:
                ansi = text.encode("mbcs", errors="replace") + b"\x00"
                win32clipboard.SetClipboardData(win32con.CF_TEXT, ansi)
            except UnicodeEncodeError:
                logger.debug("CF_TEXT(mbcs) 인코딩 생략")
        finally:
            win32clipboard.CloseClipboard()
        return True
    except Exception as exc:
        logger.exception("Win32 클립보드 등록 실패: %s", exc)
        return False


def wait_unicode_text(expected: str, *, timeout_ms: int = 300) -> bool:
    """클립보드에 expected 텍스트가 반영될 때까지 대기한다."""
    deadline = time.monotonic() + timeout_ms / 1000.0
    while time.monotonic() < deadline:
        if get_unicode_text() == expected:
            return True
        time.sleep(0.01)
    return get_unicode_text() == expected
