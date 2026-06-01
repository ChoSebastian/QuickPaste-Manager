"""붙여넣기 대상 창이 이미지를 받을 수 있는지 휴리스틱 판별."""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger("quickpaste.paste_target")

# 단순 텍스트 전용으로 보이는 클래스
_TEXT_ONLY_CLASSES = frozenset(
    {
        "Edit",
        "TEdit",
        "TMemo",
        "ConsoleWindowClass",
        "Notepad",
    }
)

# Notepad 11 등 (RichEdit 계열이지만 이미지 미지원)
_NOTEPAD_RICHEDIT_CLASSES = frozenset(
    {
        "RichEditD2DPT",
        "RichEdit20W",
        "RichEdit50W",
    }
)


def image_paste_blocked_reason(target_hwnd: int | None) -> str | None:
    """
    이미지 붙여넣기가 어렵거나 불가능해 보이면 안내 문구를 반환한다.
    판별 불가(None hwnd 등)이면 None을 반환해 시도는 허용한다.
    """
    if target_hwnd is None or sys.platform != "win32":
        return None
    try:
        import win32gui

        cls = win32gui.GetClassName(int(target_hwnd))
        if cls in _TEXT_ONLY_CLASSES:
            return "이 입력란에는 이미지를 붙여넣을 수 없습니다.\n텍스트만 붙여넣을 수 있는 창입니다."

        if cls in _NOTEPAD_RICHEDIT_CLASSES:
            title = win32gui.GetWindowText(int(target_hwnd)) or ""
            root = win32gui.GetAncestor(int(target_hwnd), 2)  # GA_ROOT
            root_title = win32gui.GetWindowText(root) if root else title
            combined = f"{title} {root_title}".lower()
            if "메모장" in combined or "notepad" in combined:
                return (
                    "메모장 등 텍스트 편집기에는 이미지를 붙여넣을 수 없습니다.\n"
                    "그림판, Word, PowerPoint 등을 사용해 주세요."
                )
    except Exception as exc:
        logger.debug("붙여넣기 대상 판별 실패: %s", exc)
    return None
