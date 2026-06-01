"""이미지 원본 파일 열기 (팝업 유지)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logger = logging.getLogger("quickpaste.image")


def open_image_file(path: Path) -> bool:
    """시스템 기본 뷰어로 이미지를 연다. 팝업은 닫지 않는다."""
    resolved = path.resolve()
    if not resolved.is_file():
        logger.warning("이미지 파일 없음: %s", resolved)
        return False
    try:
        if sys.platform == "win32":
            import os

            os.startfile(str(resolved))  # noqa: S606
            return True
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        return QDesktopServices.openUrl(QUrl.fromLocalFile(str(resolved)))
    except Exception as exc:
        logger.exception("이미지 열기 실패: %s", exc)
        return False
