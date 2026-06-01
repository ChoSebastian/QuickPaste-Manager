"""HotkeyService.probe_available 동작."""

from __future__ import annotations

from src.services.hotkey_service import StubHotkeyService


def test_stub_probe_always_available():
    svc = StubHotkeyService()
    assert svc.probe_available("Ctrl+Shift+Q") == (True, "")


def test_stub_active_hotkey_after_register():
    svc = StubHotkeyService()
    svc.register("Ctrl+Shift+Q", lambda: None)
    assert svc.active_hotkey == "Ctrl+Shift+Q"
    assert svc.probe_available("Ctrl+Shift+Q") == (True, "")
