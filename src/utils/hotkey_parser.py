"""단축키 문자열 파싱 (RegisterHotKey용)."""

from __future__ import annotations

# win32 MOD_* 상수 (RegisterHotKey)
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008

_MODIFIER_ALIASES: dict[str, str] = {
    "ctrl": "control",
    "control": "control",
    "shift": "shift",
    "alt": "alt",
    "win": "win",
    "super": "win",
    "meta": "win",
}

_SPECIAL_KEYS: dict[str, int] = {
    "space": 0x20,
    "tab": 0x09,
    "enter": 0x0D,
    "return": 0x0D,
    "escape": 0x1B,
    "esc": 0x1B,
    "backspace": 0x08,
    "delete": 0x2E,
    "insert": 0x2D,
    "home": 0x24,
    "end": 0x23,
    "pageup": 0x21,
    "pagedown": 0x22,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
}


def _normalize_part(part: str) -> str:
    return part.strip().lower()


def _parse_modifier(name: str) -> int:
    canonical = _MODIFIER_ALIASES.get(name)
    if canonical is None:
        raise ValueError(f"지원하지 않는 수정키: {name}")

    mapping = {
        "control": MOD_CONTROL,
        "shift": MOD_SHIFT,
        "alt": MOD_ALT,
        "win": MOD_WIN,
    }
    return mapping[canonical]


def _parse_key_vk(key: str) -> int:
    normalized = _normalize_part(key)
    if normalized in _SPECIAL_KEYS:
        return _SPECIAL_KEYS[normalized]

    if normalized.startswith("f") and normalized[1:].isdigit():
        fn = int(normalized[1:])
        if 1 <= fn <= 24:
            return 0x70 + (fn - 1)

    if len(key) == 1:
        return ord(key.upper())

    raise ValueError(f"지원하지 않는 키: {key}")


def parse_hotkey(hotkey: str) -> tuple[int, int]:
    """'Ctrl+Shift+V' → (modifiers, virtual_key_code)."""
    parts = [_normalize_part(p) for p in hotkey.split("+") if p.strip()]
    if len(parts) < 2:
        raise ValueError(f"단축키 형식이 올바르지 않습니다: {hotkey}")

    key_part = parts[-1]
    modifier_parts = parts[:-1]

    modifiers = 0
    for part in modifier_parts:
        modifiers |= _parse_modifier(part)

    vk = _parse_key_vk(key_part)
    return modifiers, vk
