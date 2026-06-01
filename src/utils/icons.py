"""트레이/앱 아이콘 생성 및 로드."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon

from src.utils.paths import get_resources_dir

_ICON_DIR = get_resources_dir() / "icons"
_ICON_PATH = _ICON_DIR / "app.png"
_ICON_ICO_PATH = _ICON_DIR / "app.ico"
_ICON_VERSION = 2


def _draw_icon(size: int):
    from PIL import Image, ImageDraw

    scale = size / 256.0
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = int(28 * scale)
    r = int(36 * scale)
    # 그라데이션 느낌 — 상단 진한 파랑, 하단 청록
    for y in range(pad, size - pad):
        t = (y - pad) / max(size - 2 * pad, 1)
        col = (
            int(26 + t * 20),
            int(95 + t * 40),
            int(180 - t * 30),
            255,
        )
        draw.rounded_rectangle(
            (pad, y, size - pad, y + 1),
            radius=max(1, r // 8),
            fill=col,
        )
    draw.rounded_rectangle(
        (pad, pad, size - pad, size - pad),
        radius=r,
        fill=(30, 100, 190, 255),
    )

    # 클립보드 본체
    cx0 = int(72 * scale)
    cy0 = int(64 * scale)
    cx1 = int(184 * scale)
    cy1 = int(200 * scale)
    draw.rounded_rectangle(
        (cx0, cy0, cx1, cy1),
        radius=int(14 * scale),
        fill=(255, 255, 255, 245),
    )
    # 클립 상단
    clip_w = int(48 * scale)
    clip_h = int(28 * scale)
    clip_x = (size - clip_w) // 2
    draw.rounded_rectangle(
        (clip_x, cy0 - int(8 * scale), clip_x + clip_w, cy0 + clip_h),
        radius=int(8 * scale),
        fill=(220, 228, 240, 255),
    )
    draw.rectangle(
        (
            clip_x + int(10 * scale),
            cy0 + clip_h - int(4 * scale),
            clip_x + clip_w - int(10 * scale),
            cy0 + clip_h + int(6 * scale),
        ),
        fill=(255, 255, 255, 245),
    )

    # 텍스트 라인
    line_y = cy0 + int(36 * scale)
    line_h = int(10 * scale)
    gap = int(18 * scale)
    for i in range(3):
        y = line_y + i * gap
        w = cx1 - cx0 - int(40 * scale) - i * int(12 * scale)
        draw.rounded_rectangle(
            (cx0 + int(20 * scale), y, cx0 + int(20 * scale) + w, y + line_h),
            radius=int(4 * scale),
            fill=(180, 200, 230, 255),
        )

    # 붙여넣기 화살표 (우하단)
    ax = int(168 * scale)
    ay = int(168 * scale)
    draw.polygon(
        [
            (ax, ay + int(36 * scale)),
            (ax + int(28 * scale), ay + int(18 * scale)),
            (ax + int(18 * scale), ay + int(18 * scale)),
            (ax + int(18 * scale), ay),
            (ax - int(8 * scale), ay),
            (ax - int(8 * scale), ay + int(28 * scale)),
        ],
        fill=(46, 204, 113, 255),
    )

    return img


def _write_icon_assets() -> None:
    from PIL import Image

    _ICON_DIR.mkdir(parents=True, exist_ok=True)
    sizes = (16, 24, 32, 48, 64, 128, 256)
    images: list[Image.Image] = []
    for s in sizes:
        im = _draw_icon(s)
        im.save(_ICON_DIR / f"app_{s}.png", format="PNG")
        images.append(im)
    images[-1].save(_ICON_PATH, format="PNG")
    images[-1].save(
        _ICON_ICO_PATH,
        format="ICO",
        sizes=[(s, s) for s in sizes],
    )


def ensure_tray_icon() -> Path:
    """앱 아이콘 PNG/ICO를 생성하거나 기존 파일을 반환한다."""
    version_file = _ICON_DIR / ".icon_version"
    current = ""
    if version_file.exists():
        current = version_file.read_text(encoding="utf-8").strip()

    if not _ICON_PATH.exists() or current != str(_ICON_VERSION):
        _write_icon_assets()
        version_file.write_text(str(_ICON_VERSION), encoding="utf-8")
    return _ICON_PATH


def load_app_icon() -> QIcon:
    """다중 해상도 QIcon."""
    ensure_tray_icon()
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        path = _ICON_DIR / f"app_{size}.png"
        if path.exists():
            icon.addFile(str(path), QSize(size, size))
    if icon.isNull() and _ICON_PATH.exists():
        icon = QIcon(str(_ICON_PATH))
    if _ICON_ICO_PATH.exists():
        icon.addFile(str(_ICON_ICO_PATH))
    return icon
