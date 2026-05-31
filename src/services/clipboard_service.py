"""클립보드 등록 서비스."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol

from PySide6.QtGui import QClipboard, QImage
from PySide6.QtWidgets import QApplication

logger = logging.getLogger("quickpaste.clipboard")


class ClipboardService(Protocol):
    def set_text(self, text: str) -> bool: ...
    def set_image_from_path(self, image_path: Path) -> bool: ...
    def get_text(self) -> str: ...


class QtClipboardService:
    """Qt 기반 클립보드 서비스. 이미지는 기본 구현만 제공."""

    def __init__(self, app: QApplication | None = None) -> None:
        self._app = app or QApplication.instance()

    def _clipboard(self) -> QClipboard:
        if self._app is None:
            raise RuntimeError("QApplication이 초기화되지 않았습니다.")
        return self._app.clipboard()

    def set_text(self, text: str) -> bool:
        try:
            self._clipboard().setText(text)
            return True
        except Exception as exc:
            logger.exception("텍스트 클립보드 등록 실패: %s", exc)
            return False

    def set_image_from_path(self, image_path: Path) -> bool:
        # TODO: Windows 표준 이미지 클립보드 형식(DIB/CF_BITMAP) 보조 구현
        try:
            image = QImage(str(image_path))
            if image.isNull():
                logger.error("이미지 로드 실패: %s", image_path)
                return False
            self._clipboard().setImage(image)
            return True
        except Exception as exc:
            logger.exception("이미지 클립보드 등록 실패: %s", exc)
            return False

    def get_text(self) -> str:
        return self._clipboard().text() or ""


def create_clipboard_service(app: QApplication | None = None) -> ClipboardService:
    return QtClipboardService(app)
