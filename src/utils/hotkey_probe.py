"""RegisterHotKey 사용 가능 여부 프로브."""

from __future__ import annotations

import sys

PROBE_HOTKEY_ID = 0xB002


def probe_hotkey_available(hotkey: str) -> tuple[bool, str]:
    """단축키 등록 가능 여부를 시험 등록으로 확인한다."""
    if sys.platform != "win32":
        return True, ""

    from src.utils.hotkey_parser import parse_hotkey

    try:
        modifiers, vk = parse_hotkey(hotkey)
    except ValueError as exc:
        return False, str(exc)

    import pywintypes
    import win32gui

    hwnd = win32gui.GetDesktopWindow()
    try:
        win32gui.RegisterHotKey(hwnd, PROBE_HOTKEY_ID, modifiers, vk)
        win32gui.UnregisterHotKey(hwnd, PROBE_HOTKEY_ID)
        return True, ""
    except pywintypes.error as exc:
        code = exc.args[0] if exc.args else 0
        if code == 1409:  # ERROR_HOTKEY_ALREADY_REGISTERED
            return False, "다른 프로그램에서 이미 사용 중인 단축키입니다."
        return False, (
            f"이 단축키를 등록할 수 없습니다. (오류 {code})\n"
            "다른 조합을 선택해 주세요."
        )
