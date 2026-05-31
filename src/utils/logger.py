"""Rotating file logger 설정."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.utils.paths import ensure_app_directories, get_logs_dir

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_BYTES = 2 * 1024 * 1024
BACKUP_COUNT = 5


def get_log_file_path(logs_dir: Path | None = None) -> Path:
    base = logs_dir or get_logs_dir()
    return base / "quickpaste.log"


def setup_logging(
    *,
    name: str = "quickpaste",
    level: int = logging.INFO,
    logs_dir: Path | None = None,
) -> logging.Logger:
    """루트 앱 로거를 구성한다."""
    ensure_app_directories()
    log_path = get_log_file_path(logs_dir)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.debug("로깅 초기화 완료: %s", log_path)
    return logger
