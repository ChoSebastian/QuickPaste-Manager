"""휴지통 repository 테스트."""

from __future__ import annotations

from src.repositories import category_repository, snippet_repository
from src.repositories.db import initialize_database


def test_trash_restore_and_empty(tmp_path):
    conn = initialize_database(db_path=tmp_path / "test.db", seed_categories=True)
    cat_id = category_repository.list_active(conn)[0].id
    sid = snippet_repository.create_text(
        conn, category_id=cat_id, title="삭제 대상", body_text="x"
    )
    conn.commit()

    snippet_repository.soft_delete(conn, sid)
    conn.commit()
    assert snippet_repository.count_trash(conn) == 1
    assert len(snippet_repository.list_trash(conn)) == 1

    snippet_repository.restore(conn, sid)
    conn.commit()
    assert snippet_repository.count_trash(conn) == 0
    assert snippet_repository.get_by_id(conn, sid).active is True

    snippet_repository.soft_delete(conn, sid)
    conn.commit()
    removed = snippet_repository.empty_trash(conn)
    conn.commit()
    assert removed == 1
    assert snippet_repository.get_by_id(conn, sid) is None
    conn.close()
