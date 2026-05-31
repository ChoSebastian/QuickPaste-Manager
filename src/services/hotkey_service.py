"""전역 단축키 서비스 (RegisterHotKey 추상화)."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Protocol

logger = logging.getLogger("quickpaste.hotkey")


class HotkeyService(Protocol):
    def register(self, hotkey: str, callback: Callable[[], None]) -> bool: ...
    def unregister(self) -> None: ...


class StubHotkeyService:
    """TODO: pywin32 RegisterHotKey 기반 실제 구현으로 교체."""

    def __init__(self) -> None:
        self._hotkey: str | None = None
        self._callback: Callable[[], None] | None = None

    def register(self, hotkey: str, callback: Callable[[], None]) -> bool:
        self._hotkey = hotkey
        self._callback = callback
        logger.warning(
            "HotkeyService: '%s' 등록 요청됨 — 실제 RegisterHotKey 구현 TODO",
            hotkey,
        )
        return False

    def unregister(self) -> None:
        self._hotkey = None
        self._callback = None
        logger.debug("HotkeyService: 등록 해제 (stub)")


def create_hotkey_service() -> HotkeyService:
    return StubHotkeyService()
