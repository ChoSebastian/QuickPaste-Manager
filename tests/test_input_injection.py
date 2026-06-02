"""input_injection 테스트."""

from __future__ import annotations

import ctypes
import sys
from unittest.mock import patch

from src.utils.input_injection import (
    INPUT,
    capture_foreground_window,
    capture_window_at_cursor,
    send_ctrl_v,
)


def test_send_ctrl_v_non_windows_returns_false():
    with patch.object(sys, "platform", "linux"):
        assert send_ctrl_v() is False


def test_send_ctrl_v_success_on_windows():
    with (
        patch.object(sys, "platform", "win32"),
        patch("src.utils.input_injection._send_input_sequence", return_value=True),
        patch("src.utils.input_injection.restore_foreground_window", return_value=True),
    ):
        assert send_ctrl_v(target_hwnd=12345) is True


def test_send_ctrl_v_fallback_keybd_event():
    with (
        patch.object(sys, "platform", "win32"),
        patch("src.utils.input_injection._send_input_sequence", return_value=False),
        patch("src.utils.input_injection._send_ctrl_v_keybd_event", return_value=True),
        patch("src.utils.input_injection.time.sleep"),
    ):
        assert send_ctrl_v() is True


def test_input_struct_size_reasonable():
    size = ctypes.sizeof(INPUT)
    assert size in (28, 40)


def test_capture_foreground_non_windows():
    with patch.object(sys, "platform", "linux"):
        assert capture_foreground_window() is None


def test_capture_window_at_cursor_non_windows():
    with patch.object(sys, "platform", "linux"):
        assert capture_window_at_cursor() is None
