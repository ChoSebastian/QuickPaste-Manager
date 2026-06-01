"""ClickableImageLabel 테스트."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

from src.ui.widgets.clickable_image_label import ClickableImageLabel


def test_click_opens_source_file(qtbot, tmp_path):
    img = tmp_path / "a.png"
    QPixmap(20, 20).save(str(img))
    label = ClickableImageLabel()
    qtbot.addWidget(label)
    label.set_preview(QPixmap(20, 20), img)
    with patch("src.ui.widgets.clickable_image_label.open_image_file") as open_fn:
        qtbot.mouseClick(label, Qt.MouseButton.LeftButton)
        open_fn.assert_called_once_with(img)


def test_click_without_source_does_nothing(qtbot):
    label = ClickableImageLabel()
    qtbot.addWidget(label)
    label.setPixmap(QPixmap(10, 10))
    with patch("src.ui.widgets.clickable_image_label.open_image_file") as open_fn:
        qtbot.mouseClick(label, Qt.MouseButton.LeftButton)
        open_fn.assert_not_called()
