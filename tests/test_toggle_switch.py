"""토글 스위치 시각·상태 테스트."""

from __future__ import annotations

from PySide6.QtCore import Qt

from src.ui.widgets.toggle_switch import ToggleSwitch


def test_toggle_click_updates_checked_and_thumb(qtbot, qapp):
    sw = ToggleSwitch(checked=False)
    sw.show()
    qtbot.waitExposed(sw)

    assert not sw.isChecked()
    qtbot.mouseClick(sw, Qt.MouseButton.LeftButton)
    qtbot.wait(150)

    assert sw.isChecked()
    assert sw._thumb_pos > sw._PAD

    qtbot.mouseClick(sw, Qt.MouseButton.LeftButton)
    qtbot.wait(150)

    assert not sw.isChecked()
