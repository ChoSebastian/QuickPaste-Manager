"""Snippet 데이터 모델."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Snippet:
    id: int
    category_id: int
    title: str
    content_type: str
    body_text: str | None
    asset_id: int | None
    tags: str
    use_count: int
    last_used_at: datetime | None
    pinned: bool
    active: bool
    created_at: datetime
    updated_at: datetime
