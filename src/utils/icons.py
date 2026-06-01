"""트레이/앱 아이콘 생성."""

from __future__ import annotations

from pathlib import Path

from src.utils.paths import get_resources_dir

_ICON_DIR = get_resources_dir() / "icons"
_ICON_PATH = _ICON_DIR / "app.png"


def ensure_tray_icon() -> Path:
    """기본 트레이 아이콘 PNG를 생성하거나 기존 파일을 반환한다."""
    _ICON_DIR.mkdir(parents=True, exist_ok=True)
    if _ICON_PATH.exists():
        return _ICON_PATH

    from PIL import Image, ImageDraw, ImageFont

    size = 64
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((4, 4, 60, 60), radius=12, fill=(74, 144, 217, 255))
    draw.rounded_rectangle((14, 18, 50, 46), radius=4, fill=(255, 255, 255, 230))

    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()

    draw.text((22, 22), "Q", fill=(74, 144, 217, 255), font=font)
    image.save(_ICON_PATH, format="PNG")
    return _ICON_PATH
