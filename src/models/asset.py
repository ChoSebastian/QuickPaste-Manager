"""Asset 데이터 모델."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Asset:
    id: int
    asset_type: str
    original_name: str
    stored_path: str
    mime_type: str
    file_size: int
    sha256: str
    width: int | None
    height: int | None
    created_at: datetime
