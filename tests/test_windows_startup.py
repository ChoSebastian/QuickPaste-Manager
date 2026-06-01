"""Windows 시작 프로그램 유틸 테스트."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from src.utils import windows_startup


def test_get_launch_command_dev_mode():
    with patch.object(sys, "frozen", False, create=True):
        with patch.object(sys, "executable", r"C:\Python312\python.exe"):
            cmd = windows_startup.get_launch_command()
    assert "python.exe" in cmd
    assert "src.main" in cmd


def test_get_launch_command_frozen():
    with patch.object(sys, "frozen", True, create=True):
        with patch.object(sys, "executable", r"C:\App\QuickPasteManager.exe"):
            cmd = windows_startup.get_launch_command()
    assert cmd == r'"C:\App\QuickPasteManager.exe"'


def test_apply_startup_enabled(monkeypatch):
    if sys.platform != "win32":
        return
    mock_key = MagicMock()
    monkeypatch.setattr(windows_startup, "get_launch_command", lambda: '"C:\\app.exe"')
    with patch("winreg.OpenKey", return_value=mock_key):
        with patch("winreg.SetValueEx") as set_value:
            with patch("winreg.HKEY_CURRENT_USER", 1):
                with patch("winreg.KEY_SET_VALUE", 2):
                    with patch("winreg.KEY_READ", 4):
                        with patch("winreg.REG_SZ", 1):
                            ok, _ = windows_startup.apply_startup_setting(True)
    assert ok is True
    set_value.assert_called_once()


def test_is_startup_enabled_false_on_missing(monkeypatch):
    if sys.platform != "win32":
        monkeypatch.setattr(windows_startup, "is_startup_enabled", lambda: False)
        assert windows_startup.is_startup_enabled() is False
        return
    import winreg

    def raise_not_found(*_args, **_kwargs):
        raise FileNotFoundError

    with patch("winreg.OpenKey") as open_key:
        open_key.return_value.__enter__.return_value = MagicMock()
        with patch("winreg.QueryValueEx", side_effect=FileNotFoundError):
            assert windows_startup.is_startup_enabled() is False
