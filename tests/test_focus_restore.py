"""restore_foreground_window 테스트."""

from __future__ import annotations

import sys
from unittest.mock import patch

from src.utils.input_injection import restore_foreground_window


def test_restore_skips_invalid_hwnd():
    with patch.object(sys, "platform", "win32"):
        assert restore_foreground_window(0) is False
        assert restore_foreground_window(None) is False


def test_restore_non_windows():
    with patch.object(sys, "platform", "linux"):
        assert restore_foreground_window(12345) is False
