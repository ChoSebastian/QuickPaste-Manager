"""paste_target 테스트."""

from __future__ import annotations

from unittest.mock import patch

from src.utils.paste_target import image_paste_blocked_reason


def test_edit_control_blocks_image():
    with patch("src.utils.paste_target.sys.platform", "win32"), patch(
        "win32gui.GetClassName", return_value="Edit"
    ):
        reason = image_paste_blocked_reason(12345)
    assert reason is not None
    assert "이미지" in reason


def test_unknown_hwnd_allows_paste():
    assert image_paste_blocked_reason(None) is None
