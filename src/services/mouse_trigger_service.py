"""마우스 가운데 버튼(휠 클릭) 전역 트리거 — Windows WH_MOUSE_LL."""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from ctypes import WINFUNCTYPE, Structure, c_int, c_long, windll
from ctypes import wintypes
from typing import Protocol

from PySide6.QtCore import QObject, QMetaObject, Qt, Slot
from PySide6.QtWidgets import QApplication

logger = logging.getLogger("quickpaste.mouse")

WH_MOUSE_LL = 14
WM_MBUTTONDOWN = 0x0207
HC_ACTION = 0


class MSLLHOOKSTRUCT(Structure):
    _fields_ = [
        ("pt", wintypes.POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", c_long),
    ]


class MouseTriggerService(Protocol):
    def start(self, callback: Callable[[], None]) -> bool: ...

    def stop(self) -> None: ...


class _TriggerBridge(QObject):
    """훅 스레드 → Qt 메인 스레드로 콜백 전달."""

    def __init__(self) -> None:
        super().__init__()
        self._callback: Callable[[], None] | None = None

    def set_callback(self, callback: Callable[[], None] | None) -> None:
        self._callback = callback

    @Slot()
    def fire(self) -> None:
        if self._callback is not None:
            self._callback()


class StubMouseTriggerService:
    def __init__(self) -> None:
        self._callback: Callable[[], None] | None = None

    def start(self, callback: Callable[[], None]) -> bool:
        self._callback = callback
        logger.warning("MouseTriggerService: Windows 전용 — 현재 플랫폼에서는 사용할 수 없습니다.")
        return False

    def stop(self) -> None:
        self._callback = None


class Win32MouseTriggerService:
    """SetWindowsHookEx(WH_MOUSE_LL) — 가운데 버튼 누름 시 팝업."""

    def __init__(self, app: QApplication) -> None:
        self._app = app
        self._bridge = _TriggerBridge()
        self._hook_id: int | None = None
        self._hook_proc = None

    def start(self, callback: Callable[[], None]) -> bool:
        if sys.platform != "win32":
            return False
        self.stop()
        self._bridge.set_callback(callback)

        user32 = windll.user32
        kernel32 = windll.kernel32

        @WINFUNCTYPE(c_long, c_int, wintypes.WPARAM, wintypes.LPARAM)
        def low_level_mouse_proc(n_code: int, w_param: int, l_param: int) -> int:
            if n_code == HC_ACTION and w_param == WM_MBUTTONDOWN:
                QMetaObject.invokeMethod(
                    self._bridge,
                    "fire",
                    Qt.ConnectionType.QueuedConnection,
                )
            return user32.CallNextHookEx(self._hook_id, n_code, w_param, l_param)

        self._hook_proc = low_level_mouse_proc
        module = kernel32.GetModuleHandleW(None)
        hook_id = user32.SetWindowsHookExW(
            WH_MOUSE_LL,
            self._hook_proc,
            module,
            0,
        )
        if not hook_id:
            logger.error("마우스 훅 등록 실패 (GetLastError=%s)", kernel32.GetLastError())
            self._hook_proc = None
            return False

        self._hook_id = hook_id
        logger.info("마우스 가운데 버튼 트리거 등록됨")
        return True

    def stop(self) -> None:
        if self._hook_id is not None:
            windll.user32.UnhookWindowsHookEx(self._hook_id)
            self._hook_id = None
        self._hook_proc = None
        self._bridge.set_callback(None)
        logger.debug("마우스 트리거 해제")


def create_mouse_trigger_service(
    app: QApplication | None = None,
) -> MouseTriggerService:
    if sys.platform == "win32" and app is not None:
        return Win32MouseTriggerService(app)
    return StubMouseTriggerService()
