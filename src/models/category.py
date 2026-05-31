"""Category 데이터 모델."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Category:
    id: int
    name: str
    sort_order: int
    color: str
    active: bool
    created_at: datetime
    updated_at: datetime
