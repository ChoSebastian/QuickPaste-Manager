"""snippet_content_view 테스트."""

from __future__ import annotations

from datetime import datetime, timezone

from PySide6.QtWidgets import QLabel, QScrollArea, QTextEdit

from src.models.snippet import Snippet
from src.ui.widgets.clickable_image_label import ClickableImageLabel
from src.ui.widgets.snippet_content_view import apply_snippet_full_content

_NOW = datetime.now(timezone.utc)


def test_apply_text_snippet_full_body(qtbot):
    text = QTextEdit()
    image = ClickableImageLabel()
    scroll = QScrollArea()
    hint = QLabel()
    qtbot.addWidget(text)
    snippet = Snippet(
        id=1,
        category_id=1,
        title="t",
        content_type="text",
        body_text="전체\n본문\n내용",
        asset_id=None,
        tags="",
        use_count=0,
        last_used_at=None,
        pinned=False,
        active=True,
        created_at=_NOW,
        updated_at=_NOW,
    )
    apply_snippet_full_content(
        None,  # type: ignore[arg-type]
        snippet,
        text_edit=text,
        image_label=image,
        image_scroll=scroll,
        image_hint=hint,
        max_width=200,
        max_height=300,
    )
    assert text.isVisible()
    assert "전체" in text.toPlainText()
    assert not scroll.isVisible()
