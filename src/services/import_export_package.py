"""Import/Export ZIP 패키지 직렬화·역직렬화."""

from __future__ import annotations

import json
import logging
import shutil
import sqlite3
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.repositories import asset_repository, category_repository, snippet_repository
from src.repositories.db import utc_now_iso
from src.services.asset_service import guess_mime_type, save_image_file
from src.utils.config import load_settings, save_settings
from src.utils.paths import get_assets_dir, get_settings_path

logger = logging.getLogger("quickpaste.import_export")

MANIFEST_VERSION = 1
MANIFEST_NAME = "manifest.json"
CATEGORIES_NAME = "categories.json"
SNIPPETS_NAME = "snippets.json"
SETTINGS_NAME = "settings.json"
ASSETS_DIR = "assets"


@dataclass(frozen=True, slots=True)
class ImportResult:
    ok: bool
    message: str
    categories_added: int = 0
    snippets_added: int = 0
    snippets_renamed: int = 0
    assets_copied: int = 0


def _category_to_dict(category) -> dict:  # noqa: ANN001
    return {
        "name": category.name,
        "sort_order": category.sort_order,
        "color": category.color,
    }


def _snippet_to_dict(snippet, *, category_name: str, asset_file: str | None) -> dict:
    return {
        "category_name": category_name,
        "title": snippet.title,
        "content_type": snippet.content_type,
        "body_text": snippet.body_text,
        "tags": snippet.tags,
        "pinned": snippet.pinned,
        "asset_file": asset_file,
    }


def _unique_title(conn: sqlite3.Connection, category_id: int, title: str) -> tuple[str, bool]:
    if not _title_exists(conn, category_id, title):
        return title, False
    base = title
    n = 2
    while n < 100:
        candidate = f"{base} ({n})"
        if not _title_exists(conn, category_id, candidate):
            return candidate, True
        n += 1
    return f"{base} ({datetime.now().strftime('%H%M%S')})", True


def _title_exists(conn: sqlite3.Connection, category_id: int, title: str) -> bool:
    row = conn.execute(
        """
        SELECT 1 FROM snippets
        WHERE category_id = ? AND title = ? AND active = 1
        LIMIT 1
        """,
        (category_id, title),
    ).fetchone()
    return row is not None


def _resolve_category_id(
    conn: sqlite3.Connection,
    name: str,
    *,
    sort_order: int,
    color: str,
) -> tuple[int | None, bool]:
    for cat in category_repository.list_active(conn):
        if cat.name == name:
            return cat.id, False
    for cat in category_repository.list_all(conn):
        if cat.name == name and not cat.active:
            category_repository.restore(conn, cat.id)
            return cat.id, False
    if category_repository.count_active(conn) >= category_repository.MAX_CATEGORIES:
        return None, False
    new_id = category_repository.create(
        conn,
        name=name,
        sort_order=sort_order,
        color=color,
    )
    return new_id, True


def export_package(conn: sqlite3.Connection, destination: Path) -> bool:
    """활성 카테고리·상용구·에셋을 ZIP으로보낸다."""
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        categories = category_repository.list_active(conn)
        cat_by_id = {c.id: c for c in categories}

        snippet_rows: list[dict] = []
        asset_files: dict[str, Path] = {}

        for cat in categories:
            for snippet in snippet_repository.list_by_category(conn, cat.id):
                asset_file: str | None = None
                if snippet.asset_id:
                    asset = asset_repository.get_by_id(conn, snippet.asset_id)
                    if asset:
                        src = Path(asset.stored_path)
                        if src.exists():
                            rel = f"{asset.sha256}{src.suffix}" if asset.sha256 else src.name
                            asset_file = f"{ASSETS_DIR}/{rel}"
                            asset_files[rel] = src
                snippet_rows.append(
                    _snippet_to_dict(
                        snippet,
                        category_name=cat.name,
                        asset_file=asset_file,
                    )
                )

        manifest = {
            "version": MANIFEST_VERSION,
            "exported_at": utc_now_iso(),
            "app": "QuickPaste Manager",
        }

        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False, indent=2))
            zf.writestr(
                CATEGORIES_NAME,
                json.dumps([_category_to_dict(c) for c in categories], ensure_ascii=False, indent=2),
            )
            zf.writestr(SNIPPETS_NAME, json.dumps(snippet_rows, ensure_ascii=False, indent=2))
            settings_path = get_settings_path()
            if settings_path.exists():
                zf.writestr(SETTINGS_NAME, settings_path.read_text(encoding="utf-8"))

            for rel, src in asset_files.items():
                zf.write(src, f"{ASSETS_DIR}/{rel}")

        logger.info(
            "보내기 완료: categories=%d snippets=%d assets=%d → %s",
            len(categories),
            len(snippet_rows),
            len(asset_files),
            destination,
        )
        return True
    except Exception as exc:
        logger.exception("보내기 실패: %s", exc)
        return False


def import_package(conn: sqlite3.Connection, source: Path) -> ImportResult:
    """ZIP 패키지를 불러와 DB·assets에 병합한다."""
    if not source.is_file():
        return ImportResult(ok=False, message="파일을 찾을 수 없습니다.")

    try:
        with zipfile.ZipFile(source, "r") as zf:
            if MANIFEST_NAME not in zf.namelist():
                return ImportResult(ok=False, message="manifest.json이 없는 패키지입니다.")
            manifest = json.loads(zf.read(MANIFEST_NAME))
            if manifest.get("version") != MANIFEST_VERSION:
                return ImportResult(
                    ok=False,
                    message=f"지원하지 않는 패키지 버전입니다: {manifest.get('version')}",
                )

            categories_data = json.loads(zf.read(CATEGORIES_NAME))
            snippets_data = json.loads(zf.read(SNIPPETS_NAME))

            extract_root = get_assets_dir().parent / "_import_tmp"
            if extract_root.exists():
                shutil.rmtree(extract_root)
            extract_root.mkdir(parents=True, exist_ok=True)
            zf.extractall(extract_root)

        categories_added = 0
        snippets_added = 0
        snippets_renamed = 0
        assets_copied = 0

        category_id_by_name: dict[str, int] = {}
        for item in categories_data:
            name = str(item["name"])
            cid, created = _resolve_category_id(
                conn,
                name,
                sort_order=int(item.get("sort_order", 0)),
                color=str(item.get("color", "#4A90D9")),
            )
            if cid is None:
                continue
            category_id_by_name[name] = cid
            if created:
                categories_added += 1

        for item in snippets_data:
            cat_name = str(item["category_name"])
            cat_id = category_id_by_name.get(cat_name)
            if cat_id is None:
                cid, created = _resolve_category_id(
                    conn,
                    cat_name,
                    sort_order=category_repository.next_sort_order(conn),
                    color="#4A90D9",
                )
                if cid is None:
                    logger.warning("카테고리 생성 실패(한도): %s", cat_name)
                    continue
                cat_id = cid
                category_id_by_name[cat_name] = cat_id
                if created:
                    categories_added += 1

            title = str(item["title"])
            title, renamed = _unique_title(conn, cat_id, title)
            if renamed:
                snippets_renamed += 1

            content_type = str(item.get("content_type", "text"))
            tags = str(item.get("tags", ""))
            pinned = bool(item.get("pinned", False))

            if content_type == "image":
                asset_file = item.get("asset_file")
                if not asset_file:
                    continue
                src = extract_root / str(asset_file).replace("\\", "/")
                if not src.exists():
                    logger.warning("에셋 파일 누락: %s", asset_file)
                    continue
                asset_id = save_image_file(conn, src, mime_type=guess_mime_type(src))
                assets_copied += 1
                sid = snippet_repository.create_image(
                    conn,
                    category_id=cat_id,
                    title=title,
                    asset_id=asset_id,
                    tags=tags,
                )
            else:
                sid = snippet_repository.create_text(
                    conn,
                    category_id=cat_id,
                    title=title,
                    body_text=str(item.get("body_text") or ""),
                    tags=tags,
                )
            if pinned:
                snippet_repository.update(conn, sid, pinned=True)
            snippets_added += 1

        settings_file = extract_root / SETTINGS_NAME
        if settings_file.exists():
            imported_settings = json.loads(settings_file.read_text(encoding="utf-8"))
            current = load_settings()
            for key in ("hotkey", "popup_width", "popup_height", "popup_offset_px", "theme", "font_size"):
                if key in imported_settings:
                    current[key] = imported_settings[key]
            save_settings(current)

        shutil.rmtree(extract_root, ignore_errors=True)
        conn.commit()

        msg = (
            f"카테고리 {categories_added}개, 상용구 {snippets_added}개 추가"
            + (f" (제목 변경 {snippets_renamed}건)" if snippets_renamed else "")
        )
        return ImportResult(
            ok=True,
            message=msg,
            categories_added=categories_added,
            snippets_added=snippets_added,
            snippets_renamed=snippets_renamed,
            assets_copied=assets_copied,
        )
    except zipfile.BadZipFile:
        return ImportResult(ok=False, message="손상되었거나 ZIP 형식이 아닙니다.")
    except Exception as exc:
        logger.exception("불러오기 실패: %s", exc)
        return ImportResult(ok=False, message=f"불러오기 실패: {exc}")
