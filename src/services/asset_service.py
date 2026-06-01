"""에셋 파일 저장 서비스."""

from __future__ import annotations

import hashlib
import logging
import shutil
import sqlite3
from pathlib import Path

from PIL import Image
from PySide6.QtGui import QImage

from src.repositories import asset_repository
from src.utils.paths import get_assets_dir

logger = logging.getLogger("quickpaste.asset")

_MIME_BY_EXT: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
}


def guess_mime_type(path: Path) -> str:
    return _MIME_BY_EXT.get(path.suffix.lower(), "application/octet-stream")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _image_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        with Image.open(path) as img:
            return img.size
    except Exception as exc:
        logger.warning("이미지 크기 읽기 실패: %s", exc)
        return None, None


def save_image_file(
    conn: sqlite3.Connection,
    source_path: Path,
    *,
    mime_type: str | None = None,
) -> int:
    """이미지 파일을 assets 폴더에 복사하고 DB에 등록한다."""
    assets_dir = get_assets_dir()
    assets_dir.mkdir(parents=True, exist_ok=True)

    digest = _sha256_file(source_path)
    ext = source_path.suffix or ".png"
    stored_name = f"{digest}{ext}"
    stored_path = assets_dir / stored_name

    if not stored_path.exists():
        shutil.copy2(source_path, stored_path)

    width, height = _image_dimensions(stored_path)
    resolved_mime = mime_type or guess_mime_type(source_path)

    return asset_repository.create(
        conn,
        asset_type="image",
        original_name=source_path.name,
        stored_path=str(stored_path),
        mime_type=resolved_mime,
        file_size=stored_path.stat().st_size,
        sha256=digest,
        width=width,
        height=height,
    )


def save_qimage(
    conn: sqlite3.Connection,
    image: QImage,
    *,
    original_name: str = "clipboard.png",
) -> int:
    """QImage(클립보드 등)를 assets에 저장한다."""
    assets_dir = get_assets_dir()
    assets_dir.mkdir(parents=True, exist_ok=True)

    temp_path = assets_dir / f"_tmp_{original_name}"
    if not image.save(str(temp_path), "PNG"):
        raise RuntimeError("클립보드 이미지 저장 실패")

    try:
        return save_image_file(conn, temp_path, mime_type="image/png")
    finally:
        temp_path.unlink(missing_ok=True)

