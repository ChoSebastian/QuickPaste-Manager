"""Import/Export ZIP 패키지 테스트."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from src.repositories import category_repository, snippet_repository
from src.repositories.db import initialize_database
from src.services.import_export_package import (
    MANIFEST_NAME,
    SNIPPETS_NAME,
    export_package,
    import_package,
)


def test_export_import_text_roundtrip(tmp_path: Path) -> None:
    src_db = tmp_path / "src.db"
    conn = initialize_database(db_path=src_db, seed_categories=True)
    cat_id = category_repository.list_active(conn)[0].id
    snippet_repository.create_text(
        conn,
        category_id=cat_id,
        title="인사",
        body_text="안녕하세요",
        tags="greet",
    )
    conn.commit()

    zip_path = tmp_path / "pack.zip"
    assert export_package(conn, zip_path)
    conn.close()

    dest_db = tmp_path / "dest.db"
    dest_conn = initialize_database(db_path=dest_db, seed_categories=False)
    result = import_package(dest_conn, zip_path)
    assert result.ok, result.message
    assert result.snippets_added >= 1

    titles = [
        s.title
        for s in snippet_repository.list_by_category(
            dest_conn, category_repository.list_active(dest_conn)[0].id
        )
    ]
    assert "인사" in titles
    dest_conn.close()


def test_import_renames_duplicate_title(tmp_path: Path) -> None:
    db = tmp_path / "db.db"
    conn = initialize_database(db_path=db, seed_categories=True)
    cat_id = category_repository.list_active(conn)[0].id
    snippet_repository.create_text(
        conn, category_id=cat_id, title="중복", body_text="A"
    )
    conn.commit()

    zip_path = tmp_path / "dup.zip"
    export_package(conn, zip_path)
    conn.close()

    conn2 = initialize_database(db_path=db, seed_categories=True)
    result = import_package(conn2, zip_path)
    assert result.ok
    assert result.snippets_renamed >= 1
    snippets = snippet_repository.list_by_category(conn2, cat_id)
    titles = {s.title for s in snippets}
    assert "중복" in titles
    assert any(t.startswith("중복 (") for t in titles)
    conn2.close()


def test_export_zip_structure(tmp_path: Path) -> None:
    conn = initialize_database(db_path=tmp_path / "t.db", seed_categories=True)
    cat_id = category_repository.list_active(conn)[0].id
    snippet_repository.create_text(
        conn, category_id=cat_id, title="x", body_text="y"
    )
    conn.commit()

    zip_path = tmp_path / "out.zip"
    export_package(conn, zip_path)
    conn.close()

    with zipfile.ZipFile(zip_path) as zf:
        assert MANIFEST_NAME in zf.namelist()
        manifest = json.loads(zf.read(MANIFEST_NAME))
        assert manifest["version"] == 1
        snippets = json.loads(zf.read(SNIPPETS_NAME))
        assert any(s["title"] == "x" for s in snippets)
