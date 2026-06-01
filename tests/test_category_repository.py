"""카테고리 repository 테스트."""

from __future__ import annotations

import pytest

from src.repositories import category_repository
from src.repositories.category_repository import MAX_CATEGORIES
from src.repositories.db import initialize_database


@pytest.fixture
def conn(tmp_path):
    db = initialize_database(db_path=tmp_path / "test.db", seed_categories=True)
    yield db
    db.close()


def test_count_active(conn):
    assert category_repository.count_active(conn) == 5


def test_create_respects_max(conn):
    existing = category_repository.count_active(conn)
    for i in range(MAX_CATEGORIES - existing):
        category_repository.create(
            conn, name=f"extra-{i}", sort_order=100 + i
        )
    assert category_repository.count_active(conn) == MAX_CATEGORIES


def test_soft_delete_and_restore(conn):
    cat_id = category_repository.list_active(conn)[0].id
    category_repository.soft_delete(conn, cat_id)
    conn.commit()
    assert category_repository.get_by_id(conn, cat_id).active is False

    category_repository.restore(conn, cat_id)
    conn.commit()
    assert category_repository.get_by_id(conn, cat_id).active is True


def test_update_name(conn):
    cat = category_repository.list_active(conn)[0]
    category_repository.update(conn, cat.id, name="변경됨")
    conn.commit()
    updated = category_repository.get_by_id(conn, cat.id)
    assert updated is not None
    assert updated.name == "변경됨"
