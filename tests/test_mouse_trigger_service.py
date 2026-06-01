"""마우스 트리거 서비스 팩토리 테스트."""

from __future__ import annotations

import sys

from src.services.mouse_trigger_service import (
    StubMouseTriggerService,
    Win32MouseTriggerService,
    create_mouse_trigger_service,
)


def test_create_stub_without_app():
    svc = create_mouse_trigger_service(None)
    assert isinstance(svc, StubMouseTriggerService)
    assert svc.start(lambda: None) is False


def test_create_win32_on_windows(qapp):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    svc = create_mouse_trigger_service(app)
    if sys.platform == "win32":
        assert isinstance(svc, Win32MouseTriggerService)
    else:
        assert isinstance(svc, StubMouseTriggerService)
