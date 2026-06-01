"""snippet_list_item 유틸 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtGui import QPixmap

from src.ui.widgets.snippet_list_item import (
    SNIPPET_THUMB_PX,
    scaled_preview_pixmap,
    thumbnail_pixmap,
)


def test_thumbnail_pixmap_scales(tmp_path):
    src = tmp_path / "t.png"
    QPixmap(80, 40).save(str(src))
    thumb = thumbnail_pixmap(src, SNIPPET_THUMB_PX)
    assert not thumb.isNull()
    assert thumb.width() <= SNIPPET_THUMB_PX
    assert thumb.height() <= SNIPPET_THUMB_PX


def test_scaled_preview_pixmap():
    pix = QPixmap(400, 200)
    out = scaled_preview_pixmap(pix, max_width=100, max_height=100)
    assert out.width() <= 100
    assert out.height() <= 100
