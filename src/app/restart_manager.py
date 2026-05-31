"""프로세스 재시작 관리."""

from __future__ import annotations

import logging
import os
import sys
from typing import Final

logger = logging.getLogger("quickpaste.restart")

_MAX_RESTART_ATTEMPTS: Final[int] = 3
_restart_count = 0


def get_restart_count() -> int:
    return _restart_count


def can_restart() -> bool:
    return _restart_count < _MAX_RESTART_ATTEMPTS


def request_restart(reason: str) -> bool:
    """안전 조건에서만 프로세스 재시작을 시도한다."""
    global _restart_count

    if not can_restart():
        logger.error("재시작 한도 초과 (%s): %s", _MAX_RESTART_ATTEMPTS, reason)
        return False

    _restart_count += 1
    logger.warning("프로세스 재시작 요청 (%d/%d): %s", _restart_count, _MAX_RESTART_ATTEMPTS, reason)

    # TODO: DB 쓰기 중 강제 종료 방지 — graceful shutdown 후 재시작
    try:
        python = sys.executable
        args = [python, "-m", "src.main", *sys.argv[1:]]
        os.execv(python, args)
    except Exception as exc:
        logger.exception("재시작 실패: %s", exc)
        return False

    return True
