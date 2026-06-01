"""Win32 클립보드 동기화 테스트."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from src.utils.win_clipboard import get_unicode_text, set_unicode_text, wait_unicode_text

SAMPLE_KO = "안녕하세요 테스트"


def test_set_and_get_unicode_text():
    stored: dict[int, object] = {}

    mock_clip = MagicMock()
    mock_con = MagicMock()
    mock_con.CF_UNICODETEXT = 13
    mock_con.CF_TEXT = 1

    def set_data(fmt, data):
        stored[fmt] = data

    def get_data(fmt):
        raw = stored.get(fmt, b"")
        if fmt == mock_con.CF_UNICODETEXT:
            if isinstance(raw, str):
                return raw
            return raw.decode("utf-16-le").rstrip("\x00")  # type: ignore[union-attr]
        if fmt == mock_con.CF_TEXT:
            if isinstance(raw, bytes):
                return raw.rstrip(b"\x00").decode("mbcs")
            return str(raw)
        return ""

    mock_clip.IsClipboardFormatAvailable.return_value = True
    mock_clip.SetClipboardData = set_data
    mock_clip.GetClipboardData = get_data

    with (
        patch.object(sys, "platform", "win32"),
        patch.dict(sys.modules, {"win32clipboard": mock_clip, "win32con": mock_con}),
    ):
        assert set_unicode_text(SAMPLE_KO) is True
        assert get_unicode_text() == SAMPLE_KO
        assert wait_unicode_text(SAMPLE_KO) is True
        assert mock_con.CF_TEXT in stored
        assert mock_con.CF_UNICODETEXT in stored
        assert isinstance(stored[mock_con.CF_TEXT], bytes)
