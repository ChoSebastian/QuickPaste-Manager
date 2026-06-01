"""hotkey_parser 테스트."""

from __future__ import annotations

import pytest

from src.utils.hotkey_parser import MOD_CONTROL, MOD_SHIFT, parse_hotkey


def test_parse_ctrl_shift_v():
    modifiers, vk = parse_hotkey("Ctrl+Shift+V")
    assert modifiers == (MOD_CONTROL | MOD_SHIFT)
    assert vk == ord("V")


def test_parse_case_insensitive():
    modifiers, vk = parse_hotkey("ctrl+shift+v")
    assert modifiers == (MOD_CONTROL | MOD_SHIFT)
    assert vk == ord("V")


def test_parse_function_key():
    _, vk = parse_hotkey("Ctrl+F5")
    assert vk == 0x74  # F5


def test_parse_invalid_modifier():
    with pytest.raises(ValueError, match="수정키"):
        parse_hotkey("Foo+Bar")


def test_parse_invalid_format():
    with pytest.raises(ValueError):
        parse_hotkey("V")
