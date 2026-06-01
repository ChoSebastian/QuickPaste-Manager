"""클릭 시 원본 이미지 파일을 여는 미리보기 라벨."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

from src.utils.image_open import open_image_file


class ClickableImageLabel(QLabel):
    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)
        self.setObjectName("ClickableImagePreview")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("클릭하여 원본 이미지 열기")
        self._source_path: Path | None = None

    def clear_preview(self) -> None:
        self._source_path = None
        self.clear()
        self.hide()

    def set_preview(self, pixmap: QPixmap, source_path: Path) -> None:
        self._source_path = source_path
        self.setPixmap(pixmap)
        self.setFixedSize(pixmap.size())
        self.show()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self._source_path is not None
            and self.pixmap() is not None
            and not self.pixmap().isNull()
        ):
            open_image_file(self._source_path)
            event.accept()
            return
        super().mouseReleaseEvent(event)
