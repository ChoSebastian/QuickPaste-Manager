"""Windows 클립보드 히스토리(Win+V) 제외 API 테스트."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from src.utils.win_clipboard import exclude_from_clipboard_history


def test_exclude_returns_false_on_non_windows():
    with patch.object(sys, "platform", "linux"):
        assert exclude_from_clipboard_history() is False


def test_exclude_calls_user32_on_windows():
    mock_fn = MagicMock(return_value=1)
    mock_user32 = MagicMock()
    mock_user32.ExcludeClipboardContentFromMonitorProcessing = mock_fn

    with (
        patch.object(sys, "platform", "win32"),
        patch("ctypes.windll.user32", mock_user32),
    ):
        assert exclude_from_clipboard_history() is True
        mock_fn.assert_called_once()
