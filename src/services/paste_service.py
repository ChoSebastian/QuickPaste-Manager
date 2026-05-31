"""붙여넣기 서비스."""

from __future__ import annotations

import logging
import sqlite3
import time
from typing import Protocol

from src.models.snippet import Snippet
from src.repositories import snippet_repository, usage_repository
from src.services.clipboard_service import ClipboardService
from src.utils.win_compat import open_folder_in_explorer, show_user_warning

logger = logging.getLogger("quickpaste.paste")


class PasteService(Protocol):
    def paste_snippet(self, conn: sqlite3.Connection, snippet: Snippet) -> bool: ...


class DefaultPasteService:
    """텍스트 붙여넣기 기본 흐름. 자동 Ctrl+V는 TODO."""

    def __init__(
        self,
        clipboard: ClipboardService,
        *,
        paste_delay_ms: int = 50,
    ) -> None:
        self._clipboard = clipboard
        self._paste_delay_ms = paste_delay_ms

    def paste_snippet(self, conn: sqlite3.Connection, snippet: Snippet) -> bool:
        if snippet.content_type == "text":
            return self._paste_text(conn, snippet)
        if snippet.content_type == "image":
            return self._paste_image(conn, snippet)
        logger.warning("지원하지 않는 content_type: %s", snippet.content_type)
        return False

    def _paste_text(self, conn: sqlite3.Connection, snippet: Snippet) -> bool:
        body = snippet.body_text or ""
        if not self._clipboard.set_text(body):
            self._record_failure(conn, snippet.id, "CLIPBOARD_TEXT_FAILED")
            show_user_warning(
                "붙여넣기 실패",
                "클립보드 등록에 실패했습니다. 프로그램을 다시 시작합니다.",
            )
            return False

        # TODO: SendInput 기반 Ctrl+V 자동 입력 구현
        time.sleep(self._paste_delay_ms / 1000.0)
        logger.info("텍스트 클립보드 등록 완료 — 자동 Ctrl+V는 TODO")

        snippet_repository.record_usage(conn, snippet.id)
        usage_repository.record(conn, snippet_id=snippet.id, success=True)
        conn.commit()
        return True

    def _paste_image(self, conn: sqlite3.Connection, snippet: Snippet) -> bool:
        # TODO: asset_id로 이미지 경로 조회 후 클립보드 등록 + SendInput
        logger.warning("이미지 붙여넣기 — asset 연동 및 SendInput TODO")
        self._record_failure(conn, snippet.id, "IMAGE_PASTE_NOT_IMPLEMENTED")
        show_user_warning(
            "이미지 붙여넣기",
            "이미지 붙여넣기는 아직 구현 중입니다.",
        )
        return False

    def _record_failure(
        self,
        conn: sqlite3.Connection,
        snippet_id: int,
        error_code: str,
    ) -> None:
        usage_repository.record(
            conn,
            snippet_id=snippet_id,
            success=False,
            error_code=error_code,
        )
        conn.commit()


def open_image_asset_folder(folder_path: str) -> None:
    """이미지 붙여넣기 실패 시 에셋 폴더를 연다."""
    from pathlib import Path

    open_folder_in_explorer(Path(folder_path))


def create_paste_service(
    clipboard: ClipboardService,
    *,
    paste_delay_ms: int = 50,
) -> PasteService:
    return DefaultPasteService(clipboard, paste_delay_ms=paste_delay_ms)
