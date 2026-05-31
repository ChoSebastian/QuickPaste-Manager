"""에셋 파일 저장 서비스."""

from __future__ import annotations

import hashlib
import logging
import shutil
import sqlite3
from pathlib import Path

from src.repositories import asset_repository
from src.utils.paths import get_assets_dir

logger = logging.getLogger("quickpaste.asset")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_image_file(
    conn: sqlite3.Connection,
    source_path: Path,
    *,
    mime_type: str = "image/png",
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

    return asset_repository.create(
        conn,
        asset_type="image",
        original_name=source_path.name,
        stored_path=str(stored_path),
        mime_type=mime_type,
        file_size=stored_path.stat().st_size,
        sha256=digest,
    )
