"""이미지 원본 열기 테스트."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from PIL import Image

from src.utils.image_open import open_image_file


def test_open_image_file_windows(tmp_path):
    img = tmp_path / "photo.png"
    Image.new("RGB", (4, 4), "red").save(img)
    with patch("src.utils.image_open.sys.platform", "win32"), patch(
        "os.startfile"
    ) as startfile:
        assert open_image_file(img) is True
        startfile.assert_called_once()
