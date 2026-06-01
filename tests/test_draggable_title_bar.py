"""DraggableTitleBar 드래그 이동 테스트."""

from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QWidget

from src.ui.widgets.draggable_title_bar import DraggableTitleBar


def test_title_bar_drag_moves_window(qtbot):
    host = QWidget()
    host.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    host.resize(200, 100)
    bar = DraggableTitleBar(parent=host)
    layout = host.layout() or None
    if layout is None:
        from PySide6.QtWidgets import QVBoxLayout

        layout = QVBoxLayout(host)
    layout.addWidget(bar)
    qtbot.addWidget(host)
    host.show()
    start = host.pos()
    global_start = host.mapToGlobal(QPoint(0, 0))
    qtbot.mousePress(bar, Qt.MouseButton.LeftButton, pos=QPoint(10, 10))
    qtbot.mouseMove(
        bar,
        pos=QPoint(60, 10),
        delay=10,
    )
    qtbot.mouseRelease(bar, Qt.MouseButton.LeftButton, pos=QPoint(60, 10))
    assert host.pos().x() > start.x() or host.mapToGlobal(QPoint(0, 0)).x() > global_start.x()
