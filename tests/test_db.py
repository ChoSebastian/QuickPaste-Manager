"""SQLite DB 초기화 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.repositories import category_repository, snippet_repository
from src.repositories.db import DEFAULT_CATEGORIES, initialize_database, initialize_schema


@pytest.fixture
def db_conn(tmp_path: Path):
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path=db_path, seed_categories=True)
    yield conn
    conn.close()


def test_schema_creates_tables(db_conn):
    tables = {
        row[0]
        for row in db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert {"categories", "snippets", "assets", "usage_events"}.issubset(tables)


def test_seed_default_categories(db_conn):
    categories = category_repository.list_active(db_conn)
    assert len(categories) == len(DEFAULT_CATEGORIES)
    names = {c.name for c in categories}
    assert "일반" in names
    assert "고객응대" in names


def test_seed_skips_when_categories_exist(tmp_path):
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path=db_path, seed_categories=True)
    count_first = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]

    from src.repositories.db import seed_default_categories

    inserted = seed_default_categories(conn)
    count_second = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]

    assert count_first == len(DEFAULT_CATEGORIES)
    assert inserted == 0
    assert count_second == count_first
    conn.close()


def test_snippet_crud(db_conn):
    categories = category_repository.list_active(db_conn)
    cat_id = categories[0].id

    snippet_id = snippet_repository.create_text(
        db_conn,
        category_id=cat_id,
        title="테스트",
        body_text="본문",
        tags="tag1",
    )
    db_conn.commit()

    snippet = snippet_repository.get_by_id(db_conn, snippet_id)
    assert snippet is not None
    assert snippet.title == "테스트"

    results = snippet_repository.search(db_conn, "테스트")
    assert any(s.id == snippet_id for s in results)
