"""마우스 휠 클릭 트리거 서비스."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Protocol

logger = logging.getLogger("quickpaste.mouse")


class MouseTriggerService(Protocol):
    def start(self, callback: Callable[[], None]) -> bool: ...
    def stop(self) -> None: ...


class StubMouseTriggerService:
    """TODO: pynput 또는 Win32 저수준 훅 기반 실제 구현으로 교체."""

    def __init__(self) -> None:
        self._callback: Callable[[], None] | None = None

    def start(self, callback: Callable[[], None]) -> bool:
        self._callback = callback
        logger.warning(
            "MouseTriggerService: 휠 클릭 트리거 시작 요청 — 저수준 훅 구현 TODO"
        )
        return False

    def stop(self) -> None:
        self._callback = None
        logger.debug("MouseTriggerService: 중지 (stub)")


def create_mouse_trigger_service() -> MouseTriggerService:
    return StubMouseTriggerService()
