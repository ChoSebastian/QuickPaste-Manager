"""드래그로 이동 가능한 타이틀 바."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class DraggableTitleBar(QWidget):
    """헤더 영역 드래그로 부모 창을 이동한다."""

    def __init__(
        self,
        *,
        title: str = "QuickPaste",
        on_close: Callable[[], None] | None = None,
        on_help: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self._drag_offset: QPoint | None = None
        self._on_close = on_close
        self._on_help = on_help

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 6, 6)
        layout.setSpacing(6)

        self._title = QLabel(title)
        self._title.setObjectName("TitleLabel")
        layout.addWidget(self._title)
        layout.addStretch()

        if on_help is not None:
            help_btn = QPushButton("?")
            help_btn.setObjectName("TitleBtn")
            help_btn.setToolTip("도움말")
            help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            help_btn.clicked.connect(on_help)
            layout.addWidget(help_btn)

        if on_close is not None:
            close_btn = QPushButton("✕")
            close_btn.setObjectName("TitleBtn")
            close_btn.setToolTip("닫기")
            close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            close_btn.clicked.connect(on_close)
            layout.addWidget(close_btn)

    def set_title(self, title: str) -> None:
        self._title.setText(title)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            self._drag_offset = event.globalPosition().toPoint() - window.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_offset is not None:
            window = self.window()
            window.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._drag_offset = None
        super().mouseReleaseEvent(event)
