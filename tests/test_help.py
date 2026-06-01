"""도움말 콘텐츠·창 테스트."""

from __future__ import annotations

from src.ui.help_content import build_help_html
from src.ui.help_window import HelpWindow


def test_build_help_html_includes_hotkey_and_sections():
    html = build_help_html(
        hotkey="Ctrl+Shift+Q",
        active_hotkey="Ctrl+Shift+Q",
    )
    assert "Ctrl+Shift+Q" in html
    assert "Top 5" in html
    assert "환경설정" in html
    assert "보내기" in html
    assert "붙여넣기 후 팝업 닫기" in html
    assert "클릭" in html


def test_build_help_html_hotkey_unregistered():
    html = build_help_html(
        hotkey="Ctrl+Shift+Q",
        active_hotkey=None,
    )
    assert "등록되지 않음" in html


def test_help_window_shows_content(qtbot, qapp):
    win = HelpWindow()
    win.show_help(
        hotkey="Ctrl+Alt+P",
        active_hotkey="Ctrl+Alt+P",
    )
    qtbot.waitExposed(win)
    assert "Ctrl+Alt+P" in win._browser.toPlainText()
    assert "QuickPaste" in win.windowTitle()
