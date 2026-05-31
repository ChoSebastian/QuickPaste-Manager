"""UsageEvent 데이터 모델."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class UsageEvent:
    id: int
    snippet_id: int
    used_at: datetime
    target_window_title: str | None
    target_process: str | None
    success: bool
    error_code: str | None
