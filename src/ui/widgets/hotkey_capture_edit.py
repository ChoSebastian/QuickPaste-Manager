"""단축키 캡처 입력 (키 누름으로 조합)."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFocusEvent, QKeyEvent
from PySide6.QtWidgets import QLineEdit, QMessageBox

from src.utils.hotkey_parser import (
    format_hotkey,
    hotkeys_equal,
    is_valid_hotkey_string,
)

_MODIFIER_ORDER = ("Ctrl", "Shift", "Alt", "Win")
_QT_MODIFIER_MAP: tuple[tuple[Qt.KeyboardModifier, str], ...] = (
    (Qt.KeyboardModifier.ControlModifier, "Ctrl"),
    (Qt.KeyboardModifier.ShiftModifier, "Shift"),
    (Qt.KeyboardModifier.AltModifier, "Alt"),
    (Qt.KeyboardModifier.MetaModifier, "Win"),
)

_QT_MODIFIER_KEYS = frozenset(
    {
        Qt.Key.Key_Control,
        Qt.Key.Key_Shift,
        Qt.Key.Key_Alt,
        Qt.Key.Key_AltGr,
        Qt.Key.Key_Meta,
    }
)

_USER_FOCUS_REASONS = frozenset(
    {
        Qt.FocusReason.MouseFocusReason,
        Qt.FocusReason.TabFocusReason,
        Qt.FocusReason.BacktabFocusReason,
        Qt.FocusReason.ShortcutFocusReason,
    }
)


class HotkeyCaptureEdit(QLineEdit):
    """클릭·Tab 포커스 시에만 입력 모드. 창 열릴 때 값 유지."""

    hotkeyChanged = Signal(str)

    def __init__(
        self,
        parent=None,
        *,
        probe_fn: Callable[[str], tuple[bool, str]] | None = None,
    ) -> None:
        super().__init__(parent)
        self._probe_fn = probe_fn or (lambda _h: (True, ""))
        self.setReadOnly(True)
        self.setPlaceholderText("클릭 후 단축키 입력 (2~3키)")
        self.setClearButtonEnabled(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._parts: list[str] = []
        self._capturing = False
        self._baseline_hotkey = ""
        self._committed_hotkey = ""

    def setHotkey(self, hotkey: str) -> None:
        self._committed_hotkey = hotkey.strip()
        self._baseline_hotkey = self._committed_hotkey
        self._parts = []
        self._capturing = False
        self.setText(self._committed_hotkey)
        self.setPlaceholderText("클릭 후 단축키 입력 (2~3키)")

    def hotkey(self) -> str:
        text = self.text().strip()
        return text or self._committed_hotkey

    def _begin_capture(self) -> None:
        if self._capturing:
            return
        self._capturing = True
        self._baseline_hotkey = self._committed_hotkey
        self._parts = []
        self.setText("")
        self.setPlaceholderText("키를 누르세요… (Del: 지움, Esc: 취소)")

    def _end_capture(self, *, restore_display: bool) -> None:
        self._capturing = False
        self.setPlaceholderText("클릭 후 단축키 입력 (2~3키)")
        if restore_display:
            self.setText(self._committed_hotkey)

    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)
        if event.reason() in _USER_FOCUS_REASONS:
            self._begin_capture()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        was_capturing = self._capturing
        if was_capturing:
            self._capturing = False
        super().focusOutEvent(event)
        if was_capturing:
            self._finalize_on_blur()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if not self._capturing:
            super().keyPressEvent(event)
            return

        key = event.key()
        if key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            self._parts = []
            self.setText("")
            self.setPlaceholderText("키를 누르세요… (Del: 지움, Esc: 취소)")
            event.accept()
            return

        if key == Qt.Key.Key_Escape:
            self._committed_hotkey = self._baseline_hotkey
            self._end_capture(restore_display=True)
            self.clearFocus()
            event.accept()
            return

        if key in _QT_MODIFIER_KEYS:
            name = self._modifier_key_name(key)
            if name and name not in self._parts and len(self._parts) < 2:
                self._parts.append(name)
            self._refresh_display()
            event.accept()
            return

        key_name = self._event_key_name(key, event)
        if key_name is None:
            event.accept()
            return

        mods = self._modifiers_from_event(event)
        for name in self._parts:
            if name in _MODIFIER_ORDER and name not in mods:
                mods.append(name)
        mods = [m for m in _MODIFIER_ORDER if m in mods]
        self._parts = mods + [key_name]
        if len(self._parts) > 3:
            self._parts = self._parts[:3]
        self._refresh_display()
        event.accept()

    def _modifier_key_name(self, key: Qt.Key) -> str | None:
        mapping = {
            Qt.Key.Key_Control: "Ctrl",
            Qt.Key.Key_Shift: "Shift",
            Qt.Key.Key_Alt: "Alt",
            Qt.Key.Key_AltGr: "Alt",
            Qt.Key.Key_Meta: "Win",
        }
        return mapping.get(key)

    def _modifiers_from_event(self, event: QKeyEvent) -> list[str]:
        mods: list[str] = []
        for flag, name in _QT_MODIFIER_MAP:
            if event.modifiers() & flag and name not in mods:
                mods.append(name)
        return [m for m in _MODIFIER_ORDER if m in mods]

    def _event_key_name(self, key: Qt.Key, event: QKeyEvent) -> str | None:
        if key in _QT_MODIFIER_KEYS:
            return None
        if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            return chr(key).upper()
        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            return chr(key)
        if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F24:
            return f"F{key - Qt.Key.Key_F1 + 1}"
        special = {
            Qt.Key.Key_Space: "Space",
            Qt.Key.Key_Tab: "Tab",
            Qt.Key.Key_Return: "Enter",
            Qt.Key.Key_Enter: "Enter",
            Qt.Key.Key_Insert: "Insert",
            Qt.Key.Key_Delete: "Delete",
            Qt.Key.Key_Home: "Home",
            Qt.Key.Key_End: "End",
            Qt.Key.Key_PageUp: "PageUp",
            Qt.Key.Key_PageDown: "PageDown",
            Qt.Key.Key_Left: "Left",
            Qt.Key.Key_Up: "Up",
            Qt.Key.Key_Right: "Right",
            Qt.Key.Key_Down: "Down",
        }
        return special.get(key)

    def _refresh_display(self) -> None:
        if not self._parts:
            self.setText("")
            return
        try:
            self.setText(format_hotkey(self._parts))
        except ValueError:
            self.setText("+".join(self._parts))

    def _finalize_on_blur(self) -> None:
        text = self.text().strip()

        if not text or hotkeys_equal(text, self._baseline_hotkey):
            self._committed_hotkey = self._baseline_hotkey
            self._end_capture(restore_display=True)
            return

        if not is_valid_hotkey_string(text):
            QMessageBox.warning(
                self.window(),
                "단축키",
                "단축키는 수정키(Ctrl, Shift, Alt, Win)와 키 1개로\n"
                "2~3개 조합이어야 합니다.\n예: Ctrl+Shift+Q",
            )
            self._committed_hotkey = self._baseline_hotkey
            self._end_capture(restore_display=True)
            self.setFocus()
            return

        ok, message = self._probe_fn(text)
        if not ok:
            QMessageBox.warning(
                self.window(),
                "단축키 사용 불가",
                message + "\n\n다른 조합을 입력해 주세요.",
            )
            self._committed_hotkey = self._baseline_hotkey
            self._end_capture(restore_display=True)
            self.setFocus()
            return

        self._committed_hotkey = text
        self._baseline_hotkey = text
        self._end_capture(restore_display=True)
        self.hotkeyChanged.emit(text)
