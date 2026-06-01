"""hotkey_parser 테스트."""

from __future__ import annotations

import pytest

from src.utils.hotkey_parser import (
    MOD_CONTROL,
    MOD_SHIFT,
    format_hotkey,
    hotkeys_equal,
    is_valid_hotkey_parts,
    is_valid_hotkey_string,
    normalize_hotkey_string,
    parse_hotkey,
)


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


def test_parse_rejects_four_parts():
    with pytest.raises(ValueError, match="3개"):
        parse_hotkey("Ctrl+Shift+Alt+Q")


def test_format_hotkey_parts():
    assert format_hotkey(["Ctrl", "Shift", "Q"]) == "Ctrl+Shift+Q"


def test_hotkeys_equal_ignores_case_and_order():
    assert hotkeys_equal("Ctrl+Shift+Q", "ctrl+shift+q")
    assert hotkeys_equal("Shift+Ctrl+Q", "Ctrl+Shift+Q")
    assert not hotkeys_equal("Ctrl+Shift+Q", "Ctrl+Shift+V")


def test_normalize_hotkey_string():
    assert normalize_hotkey_string("ctrl+shift+q") == "Ctrl+Shift+Q"


def test_is_valid_hotkey_parts():
    assert is_valid_hotkey_parts(["Ctrl", "Q"])
    assert is_valid_hotkey_parts(["Ctrl", "Shift", "V"])
    assert not is_valid_hotkey_parts(["Q"])
    assert not is_valid_hotkey_parts(["Ctrl", "Shift", "Alt", "Q"])
    assert is_valid_hotkey_string("Ctrl+Shift+Q")
