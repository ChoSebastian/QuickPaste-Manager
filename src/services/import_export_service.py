"""Import / Export 서비스 (ZIP 패키지 인터페이스)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol

logger = logging.getLogger("quickpaste.import_export")


class ImportExportService(Protocol):
    def export_to_zip(self, destination: Path) -> bool: ...
    def import_from_zip(self, source: Path) -> bool: ...


class StubImportExportService:
    """TODO: manifest.json + snippets + categories + assets ZIP 구현."""

    def export_to_zip(self, destination: Path) -> bool:
        logger.warning("Export TODO: %s", destination)
        return False

    def import_from_zip(self, source: Path) -> bool:
        logger.warning("Import TODO: %s", source)
        return False


def create_import_export_service() -> ImportExportService:
    return StubImportExportService()
