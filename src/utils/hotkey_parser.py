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


_DISPLAY_MODIFIERS = frozenset({"Ctrl", "Shift", "Alt", "Win"})
_MODIFIER_DISPLAY_ORDER = ("Ctrl", "Shift", "Alt", "Win")


def _canonical_display_part(part: str) -> str:
    normalized = _normalize_part(part)
    alias = _MODIFIER_ALIASES.get(normalized)
    if alias:
        return {"control": "Ctrl", "shift": "Shift", "alt": "Alt", "win": "Win"}[alias]
    if normalized in _SPECIAL_KEYS:
        return part.strip().title() if part.strip() else normalized.title()
    if normalized.startswith("f") and normalized[1:].isdigit():
        return f"F{int(normalized[1:])}"
    if len(part.strip()) == 1:
        return part.strip().upper()
    return part.strip()


def format_hotkey(parts: list[str]) -> str:
    """표시용 단축키 문자열."""
    if not is_valid_hotkey_parts(parts):
        raise ValueError("단축키는 2~3개 조합(수정키+키)이어야 합니다.")
    return "+".join(_canonical_display_part(p) for p in parts)


def is_valid_hotkey_parts(parts: list[str]) -> bool:
    if len(parts) < 2 or len(parts) > 3:
        return False
    display = [_canonical_display_part(p) for p in parts]
    mod_count = sum(1 for p in display if p in _DISPLAY_MODIFIERS)
    if mod_count < 1:
        return False
    if display[-1] in _DISPLAY_MODIFIERS:
        return False
    try:
        parse_hotkey("+".join(display))
    except ValueError:
        return False
    return True


def is_valid_hotkey_string(hotkey: str) -> bool:
    parts = [p for p in hotkey.split("+") if p.strip()]
    return is_valid_hotkey_parts(parts)


def normalize_hotkey_string(hotkey: str) -> str:
    """비교용 정규화 (대소문자·별칭·수정키 순서 통일)."""
    parts = [p for p in hotkey.split("+") if p.strip()]
    if not parts:
        return ""
    display = [_canonical_display_part(p) for p in parts]
    mods = [m for m in _MODIFIER_DISPLAY_ORDER if m in display]
    keys = [p for p in display if p not in _DISPLAY_MODIFIERS]
    return "+".join(mods + keys)


def hotkeys_equal(a: str, b: str) -> bool:
    return normalize_hotkey_string(a) == normalize_hotkey_string(b)


def parse_hotkey(hotkey: str) -> tuple[int, int]:
    """'Ctrl+Shift+Q' → (modifiers, virtual_key_code)."""
    parts = [_normalize_part(p) for p in hotkey.split("+") if p.strip()]
    if len(parts) < 2:
        raise ValueError(f"단축키 형식이 올바르지 않습니다: {hotkey}")
    if len(parts) > 3:
        raise ValueError(f"단축키는 최대 3개 조합까지 가능합니다: {hotkey}")

    key_part = parts[-1]
    modifier_parts = parts[:-1]

    modifiers = 0
    for part in modifier_parts:
        modifiers |= _parse_modifier(part)

    vk = _parse_key_vk(key_part)
    return modifiers, vk
