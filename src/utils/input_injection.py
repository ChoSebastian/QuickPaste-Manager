"""Windows SendInput 키 입력 및 포커스 복원."""

from __future__ import annotations

import ctypes
import logging
import sys
import time
from ctypes import wintypes

logger = logging.getLogger("quickpaste.input")

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002

VK_CONTROL = 0x11
VK_V = 0x56
VK_MENU = 0x12  # Alt

ASFW_ANY = 0xFFFFFFFF

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("ii", INPUT_UNION)]


def _allow_set_foreground() -> None:
    try:
        ctypes.windll.user32.AllowSetForegroundWindow(ASFW_ANY)
    except Exception as exc:
        logger.debug("AllowSetForegroundWindow 실패: %s", exc)


def capture_foreground_window() -> int | None:
    """현재 전경 창 HWND를 저장한다."""
    if sys.platform != "win32":
        return None
    try:
        import win32gui

        hwnd = win32gui.GetForegroundWindow()
        return int(hwnd) if hwnd else None
    except Exception as exc:
        logger.debug("전경 창 캡처 실패: %s", exc)
        return None


def _alt_key_foreground_trick() -> None:
    """SetForegroundWindow 제한 완화용 Alt 키 탭 (입력 없음)."""
    alt_down = _make_key_input(VK_MENU)
    alt_up = _make_key_input(VK_MENU, key_up=True)
    _send_input_sequence((alt_down, alt_up))


def restore_foreground_window(hwnd: int | None) -> bool:
    """붙여넣기 전 대상 앱으로 포커스를 되돌린다."""
    if sys.platform != "win32" or not hwnd:
        return False

    try:
        import win32con
        import win32gui
        import win32process

        if not win32gui.IsWindow(hwnd):
            return False
        if win32gui.GetForegroundWindow() == hwnd:
            return True

        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        _allow_set_foreground()

        try:
            win32gui.SetForegroundWindow(hwnd)
            if win32gui.GetForegroundWindow() == hwnd:
                return True
        except Exception:
            pass

        fg_hwnd = win32gui.GetForegroundWindow()
        if fg_hwnd:
            fg_thread, _ = win32process.GetWindowThreadProcessId(fg_hwnd)
            target_thread, _ = win32process.GetWindowThreadProcessId(hwnd)

            if (
                fg_thread
                and target_thread
                and fg_thread != target_thread
            ):
                attached = False
                try:
                    win32process.AttachThreadInput(fg_thread, target_thread, True)
                    attached = True
                    win32gui.SetForegroundWindow(hwnd)
                    win32gui.BringWindowToTop(hwnd)
                except Exception as exc:
                    logger.debug("AttachThreadInput 실패: %s", exc)
                finally:
                    if attached:
                        try:
                            win32process.AttachThreadInput(
                                fg_thread, target_thread, False
                            )
                        except Exception:
                            pass

                if win32gui.GetForegroundWindow() == hwnd:
                    return True

        _alt_key_foreground_trick()
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass

        ok = win32gui.GetForegroundWindow() == hwnd
        if not ok:
            logger.debug("포커스 복원 미확인 (hwnd=%s)", hwnd)
        return ok
    except Exception as exc:
        logger.debug("포커스 복원 예외: %s", exc)
        return False


def _make_key_input(vk: int, *, key_up: bool = False) -> INPUT:
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.ii.ki.wVk = vk
    inp.ii.ki.dwFlags = KEYEVENTF_KEYUP if key_up else 0
    return inp


def _send_input_sequence(inputs: tuple[INPUT, ...]) -> bool:
    if not inputs:
        return True
    array = (INPUT * len(inputs))(*inputs)
    sent = ctypes.windll.user32.SendInput(
        len(inputs),
        ctypes.byref(array),
        ctypes.sizeof(INPUT),
    )
    return sent == len(inputs)


def _send_ctrl_v_keybd_event() -> bool:
    """SendInput 실패 시 pywin32 keybd_event 폴백."""
    try:
        import win32api
        import win32con

        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord("V"), 0, 0, 0)
        win32api.keybd_event(ord("V"), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        return True
    except Exception as exc:
        logger.error("keybd_event 폴백 실패: %s", exc)
        return False


def send_ctrl_v(*, target_hwnd: int | None = None, focus_delay_ms: int = 80) -> bool:
    """Ctrl+V — 대상 창 포커스 복원 후 SendInput (실패 시 keybd_event)."""
    if sys.platform != "win32":
        logger.warning("SendInput은 Windows에서만 지원됩니다.")
        return False

    if target_hwnd:
        restore_foreground_window(target_hwnd)
        time.sleep(focus_delay_ms / 1000.0)

    sequence = (
        _make_key_input(VK_CONTROL),
        _make_key_input(VK_V),
        _make_key_input(VK_V, key_up=True),
        _make_key_input(VK_CONTROL, key_up=True),
    )

    if _send_input_sequence(sequence):
        return True

    logger.warning("SendInput 실패 — keybd_event 폴백 시도")
    return _send_ctrl_v_keybd_event()
