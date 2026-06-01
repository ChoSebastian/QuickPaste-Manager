"""전역 단축키 서비스 (RegisterHotKey)."""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from ctypes import wintypes
from typing import Protocol

from PySide6.QtCore import QAbstractNativeEventFilter, Qt
from PySide6.QtWidgets import QApplication, QWidget

logger = logging.getLogger("quickpaste.hotkey")

HOTKEY_ID = 0xB001
WM_HOTKEY = 0x0312


class HotkeyService(Protocol):
    def register(self, hotkey: str, callback: Callable[[], None]) -> bool: ...
    def unregister(self) -> None: ...
    def set_suppressed(self, suppressed: bool) -> None: ...
    def probe_available(self, hotkey: str) -> tuple[bool, str]: ...
    @property
    def active_hotkey(self) -> str | None: ...


class _HotkeyNativeFilter(QAbstractNativeEventFilter):
    def __init__(
        self,
        hotkey_id: int,
        callback: Callable[[], None],
        *,
        is_suppressed: Callable[[], bool],
    ) -> None:
        super().__init__()
        self._hotkey_id = hotkey_id
        self._callback = callback
        self._is_suppressed = is_suppressed

    def nativeEventFilter(self, event_type, message):  # noqa: ANN001
        if sys.platform != "win32":
            return False, 0

        expected = b"windows_generic_MSG"
        if event_type not in (expected, "windows_generic_MSG"):
            return False, 0

        try:
            msg = wintypes.MSG.from_address(int(message))
        except (TypeError, ValueError):
            return False, 0

        if msg.message == WM_HOTKEY and msg.wParam == self._hotkey_id:
            if not self._is_suppressed():
                self._callback()
            return True, 0
        return False, 0


class StubHotkeyService:
    def __init__(self) -> None:
        self._hotkey: str | None = None

    @property
    def active_hotkey(self) -> str | None:
        return self._hotkey

    def set_suppressed(self, suppressed: bool) -> None:
        pass

    def probe_available(self, hotkey: str) -> tuple[bool, str]:
        return True, ""

    def register(self, hotkey: str, callback: Callable[[], None]) -> bool:
        self._hotkey = hotkey
        logger.warning("HotkeyService stub: '%s' (Windows 전용)", hotkey)
        return False

    def unregister(self) -> None:
        self._hotkey = None


class Win32HotkeyService:
    """pywin32 RegisterHotKey + Qt native event filter."""

    def __init__(self, app: QApplication) -> None:
        self._app = app
        self._host = QWidget()
        self._host.setWindowFlags(Qt.WindowType.Tool)
        self._host.setFixedSize(1, 1)
        self._host.hide()

        self._hotkey: str | None = None
        self._callback: Callable[[], None] | None = None
        self._filter: _HotkeyNativeFilter | None = None
        self._registered = False
        self._suppressed = False

    @property
    def active_hotkey(self) -> str | None:
        return self._hotkey if self._registered else None

    def _hwnd(self) -> int:
        return int(self._host.winId())

    def set_suppressed(self, suppressed: bool) -> None:
        self._suppressed = suppressed

    def probe_available(self, hotkey: str) -> tuple[bool, str]:
        from src.utils.hotkey_parser import hotkeys_equal, parse_hotkey

        if self._registered and self._hotkey and hotkeys_equal(hotkey, self._hotkey):
            return True, ""

        saved_hotkey = self._hotkey
        saved_callback = self._callback
        was_registered = self._registered
        if was_registered:
            self.unregister()

        import pywintypes
        import win32gui

        try:
            modifiers, vk = parse_hotkey(hotkey)
        except ValueError as exc:
            return False, str(exc)

        hwnd = self._hwnd()
        try:
            win32gui.RegisterHotKey(hwnd, HOTKEY_ID, modifiers, vk)
            win32gui.UnregisterHotKey(hwnd, HOTKEY_ID)
            return True, ""
        except pywintypes.error as exc:
            code = exc.args[0] if exc.args else 0
            if code == 1409:
                msg = "다른 프로그램에서 이미 사용 중인 단축키입니다."
            else:
                msg = (
                    f"이 단축키를 등록할 수 없습니다. (오류 {code})\n"
                    "다른 조합을 선택해 주세요."
                )
            return False, msg
        finally:
            if was_registered and saved_hotkey and saved_callback:
                self.register(saved_hotkey, saved_callback)

    def _force_unregister(self) -> None:
        import win32gui

        try:
            win32gui.UnregisterHotKey(self._hwnd(), HOTKEY_ID)
        except Exception as exc:
            logger.debug("UnregisterHotKey 무시: %s", exc)
        self._registered = False

    def register(self, hotkey: str, callback: Callable[[], None]) -> bool:
        import pywintypes
        import win32gui

        from src.utils.hotkey_parser import parse_hotkey

        self.unregister()

        try:
            modifiers, vk = parse_hotkey(hotkey)
        except ValueError as exc:
            logger.error("단축키 파싱 실패: %s", exc)
            return False

        hwnd = self._hwnd()
        self._force_unregister()

        try:
            win32gui.RegisterHotKey(hwnd, HOTKEY_ID, modifiers, vk)
        except pywintypes.error as exc:
            logger.error(
                "RegisterHotKey 실패: %s — %s (코드 %s, 이미 사용 중일 수 있음)",
                hotkey,
                exc.args[2] if len(exc.args) > 2 else exc,
                exc.args[0] if exc.args else "?",
            )
            return False

        self._filter = _HotkeyNativeFilter(
            HOTKEY_ID,
            callback,
            is_suppressed=lambda: self._suppressed,
        )
        self._app.installNativeEventFilter(self._filter)

        self._hotkey = hotkey
        self._callback = callback
        self._registered = True
        logger.info("전역 단축키 등록: %s", hotkey)
        return True

    def unregister(self) -> None:
        if self._filter is not None:
            self._app.removeNativeEventFilter(self._filter)
            self._filter = None

        if self._registered:
            self._force_unregister()
            logger.debug("전역 단축키 해제: %s", self._hotkey)

        self._hotkey = None
        self._callback = None


def create_hotkey_service(app: QApplication | None = None) -> HotkeyService:
    if sys.platform == "win32" and app is not None:
        return Win32HotkeyService(app)
    return StubHotkeyService()
