"""Import / Export 서비스 (ZIP 패키지)."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Protocol

from src.services.import_export_package import ImportResult, export_package, import_package

logger = logging.getLogger("quickpaste.import_export")


class ImportExportService(Protocol):
    def export_to_zip(self, destination: Path) -> bool: ...

    def import_from_zip(self, source: Path) -> ImportResult: ...


class ZipImportExportService:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def export_to_zip(self, destination: Path) -> bool:
        return export_package(self._conn, destination)

    def import_from_zip(self, source: Path) -> ImportResult:
        return import_package(self._conn, source)


def create_import_export_service(conn: sqlite3.Connection) -> ImportExportService:
    return ZipImportExportService(conn)
