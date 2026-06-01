"""클립보드 등록 서비스."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Protocol

from PySide6.QtGui import QClipboard, QImage
from PySide6.QtWidgets import QApplication

logger = logging.getLogger("quickpaste.clipboard")


class ClipboardService(Protocol):
    def set_text(self, text: str) -> bool: ...
    def set_image_from_path(self, image_path: Path) -> bool: ...
    def get_text(self) -> str: ...
    def get_image(self) -> QImage: ...
    def has_image(self) -> bool: ...


class QtClipboardService:
    """Windows: Win32 클립보드로 동기 등록. 그 외: Qt 클립보드."""

    def __init__(self, app: QApplication | None = None) -> None:
        self._app = app or QApplication.instance()

    def _clipboard(self) -> QClipboard:
        if self._app is None:
            raise RuntimeError("QApplication이 초기화되지 않았습니다.")
        return self._app.clipboard()

    def set_text(self, text: str) -> bool:
        try:
            if sys.platform == "win32":
                from src.utils.win_clipboard import set_unicode_text, wait_unicode_text

                if not set_unicode_text(text):
                    return False
                if self._app is not None:
                    self._app.processEvents()
                if not wait_unicode_text(text, timeout_ms=300):
                    logger.error("클립보드 검증 실패 — 내용이 반영되지 않았습니다.")
                    return False
                return True

            self._clipboard().setText(text)
            if self._app is not None:
                self._app.processEvents()
            return True
        except Exception as exc:
            logger.exception("텍스트 클립보드 등록 실패: %s", exc)
            return False

    def set_image_from_path(self, image_path: Path) -> bool:
        try:
            image = QImage(str(image_path))
            if image.isNull():
                logger.error("이미지 로드 실패: %s", image_path)
                return False
            self._clipboard().setImage(image)
            if self._app is not None:
                self._app.processEvents()
            return True
        except Exception as exc:
            logger.exception("이미지 클립보드 등록 실패: %s", exc)
            return False

    def get_text(self) -> str:
        if sys.platform == "win32":
            from src.utils.win_clipboard import get_unicode_text

            return get_unicode_text()
        return self._clipboard().text() or ""

    def get_image(self) -> QImage:
        return self._clipboard().image()

    def has_image(self) -> bool:
        return not self.get_image().isNull()


def create_clipboard_service(app: QApplication | None = None) -> ClipboardService:
    return QtClipboardService(app)
